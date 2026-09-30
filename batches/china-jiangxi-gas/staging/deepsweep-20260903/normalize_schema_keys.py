#!/usr/bin/env python3
"""Mechanical schema conformance for shards/ — wrong tab, invented column keys, percent format.

NOT adjudication. Every rewrite here is a column name or a format, verified against the live
header of the tab the record claims. No research finding changes. Run it on any batch.

Found by scanning every value key in every record against the two live tabs' real headers:

  1. `tab` absent on an Owner/Operator record. Absent means the GAS tracker tab, where
     Owner1/QCCOwner do not exist -- the workbook builder would drop the record silently.
     9 records / 8 PIDs in this run.
  2. Invented column keys, each mapped to its real home:
       Operator1                  -> Operator                 (P4785)
       QCCOperator(施工/运营单位)   -> OperatorLocalLanguage    (P4946; value is CJK, and the
                                     English `Operator` stays unset rather than machine-
                                     translated -- it is owed by the WEP cohort ruling)
       Owner<N>LocalLanguage      -> folded into QCCOwner(业主单位)  (P5865, P5886; the tab has
                                     no per-owner CJK column, only OperatorLocalLanguage)
       StartCountry/EndCountry    -> StartCountryOrArea/EndCountryOrArea  (P4777, gas tab)
  4. `value_cols` out of sync with the keys of `values` -- a renamed key left the declaration
     pointing at the old name (P4785, P4946), a sourced record declared no columns at all
     (P4781, P4782), or a folded key was never declared (P5865, P5886). The workbook builder
     reads `value_cols`, so a stale list silently drops the value. Sentinels are exempt:
     their `values` hold diagnostic keys, not sheet columns.
  5. Record-shape conformance against BRIEF.md's allowed class set
     (`REFS_ADDED | REVERIFIED | UNRESOLVED | DEAD_LINK`, plus `CONFIRMED` on a sentinel):
       - `class_out: "CONCERN"` (11 records) and `class_out: "VALIDITY"` (2 carried-v2
         records, which repeated the ref_col in the class slot) are not in the set at all,
         so they degrade to UNRESOLVED downstream -- which would read as "nothing found"
         on sentinels that in fact confirm a real problem. Map both to `CONFIRMED`,
         which is how every conforming shard in this run writes the same verdict
         (see P4934's note: "used CONFIRMED, not P4947's non-conformant CONCERN").
         CONFIRMED does not imply refs: 11 sentinels here are CONFIRMED with
         `proposed_refs` empty, the class being about the FINDING, not its sourcing.
       - `sentinel` set but `ref_col` missing (P5887 #15/#16) -- the unit key is `ref_col`,
         so these two collided into one AMBIGUOUS duplicate unit whose winner was decided by
         filename order. Set `ref_col` from `sentinel`.
  6. `cross_row_leads[]` off-contract. The contract is `{project_id, url, facts}` (131 leads
     use it); P4794 wrote `{target_pid, from_pid, note, url}`, P5886 wrote
     `{target_project_id, source_project_id, note, url}`, and P5862 wrote
     `{target_project_id, from_project_id, claim, note, verified, url}` -- whose
     `claim` holds the substance and `note` only the caveat. The harvester keys on `project_id`,
     so an off-contract lead is invisible -- the finding is researched and then silently lost.
  3. `Owner<N>%` written bare ("54", "100"). All 5,476 non-empty Owner1% values on the live
     tab are `NN.NN%`; normalize to match.

ORDER: run this AFTER normalize_independence.py and normalize_owner_entities.py, and
BEFORE split_shards.py (which rewrites ref_shards/ and rows/ from shards/ every run).
It is the last conformance gate, so it also catches anything an earlier pass left
off-contract. (normalize_owner_entities.py now re-syncs its own `value_cols`, so the
order between those two no longer changes the OUTCOME -- but this one still runs last.)
"""
import argparse, collections, glob, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
OO_COLS_RENAME = {"Operator1": "Operator", "QCCOperator(施工/运营单位)": "OperatorLocalLanguage"}
GAS_RENAME     = {"StartCountry": "StartCountryOrArea", "EndCountry": "EndCountryOrArea"}
OWNER_REFCOLS  = ("Owner [ref]", "Operator [ref]")
# Sentinel class_out values that are NOT in BRIEF.md's set, so they degrade to
# UNRESOLVED downstream ("nothing found") on sentinels that in fact assert a real
# finding. `CONCERN` is how P4947 wrote it; `VALIDITY` is how two carried-v2
# records wrote it (they repeat the ref_col in the class slot). Both map to
# CONFIRMED -- the class does NOT require refs (11 sentinels in this run are
# CONFIRMED with proposed_refs empty), it means the finding is established.
OFF_SET_SENTINEL_CLASSES = {"CONCERN", "VALIDITY"}

def fix_pct(v):
    """54 -> 54.00%, 54% -> 54.00%, 100.00% -> unchanged."""
    s = str(v).strip()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*%?", s)
    return f"{float(m.group(1)):.2f}%" if m else s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write; default is a dry run")
    ap.add_argument("--dir", default="shards", metavar="SUBDIR",
                    help="shard subdir to normalize (default shards/). A recovery pass's "
                         "output lands in ref_shards_recovery/, which split_shards.py never "
                         "regenerates, so the shards/ glob never reaches it -- run this a "
                         "second time with --dir ref_shards_recovery. The record shape is "
                         "identical (a `resolutions` list); only the file set differs.")
    a = ap.parse_args()
    log = []
    for f in sorted((HERE / a.dir).glob("*.json")):
        d = json.load(open(f), object_pairs_hook=collections.OrderedDict)
        dirty = False
        for rec in d.get("resolutions") or []:
            pid, rc = rec.get("project_id") or f.stem, rec.get("ref_col") or ""
            ch = []
            # 1. tab routing
            if rc in OWNER_REFCOLS and rec.get("tab") != "operators_owners":
                ch.append(f"tab {rec.get('tab')!r} -> 'operators_owners'")
                rec["tab"] = "operators_owners"
            # 5. record-shape conformance
            if not rc and rec.get("sentinel"):
                ch.append(f"ref_col missing -> {rec['sentinel']!r} (was colliding as a dup unit)")
                rec["ref_col"] = rc = rec["sentinel"]
            if rc.startswith("__") and rec.get("class_out") in OFF_SET_SENTINEL_CLASSES:
                was = rec["class_out"]
                ch.append(f"class_out {was!r} -> 'CONFIRMED' ({was} is not in BRIEF's set)")
                rec["class_out"] = "CONFIRMED"
            oo = rec.get("tab") == "operators_owners"
            for src in ("values", "current_values"):
                vals = rec.get(src)
                if not isinstance(vals, dict):
                    continue
                ren = OO_COLS_RENAME if oo else GAS_RENAME
                # 2a. straight renames (preserve key order)
                if any(k in vals for k in ren):
                    items = [(ren.get(k, k), v) for k, v in vals.items()]
                    ch += [f"{src}.{k} -> {ren[k]}" for k in vals if k in ren]
                    vals.clear(); vals.update(items)
                # 2b. Owner<N>LocalLanguage -> QCCOwner(业主单位)
                if oo:
                    ll = {int(m.group(1)): vals.pop(k)
                          for k in list(vals)
                          for m in [re.fullmatch(r"Owner(\d+)LocalLanguage", k)] if m}
                    if ll:
                        parts = []
                        for n in sorted(ll):
                            pct = str(vals.get(f"Owner{n}%", "")).strip().rstrip("%")
                            parts.append(f"{ll[n]} [{pct}%]" if pct else ll[n])
                        qcc = "; ".join(parts)
                        ch.append(f"{src}.Owner*LocalLanguage ({len(ll)}) -> QCCOwner(业主单位)={qcc}")
                        vals["QCCOwner(业主单位)"] = qcc
                # 3. percent format
                for k in list(vals):
                    if re.fullmatch(r"Owner\d+%", k):
                        new = fix_pct(vals[k])
                        if new != str(vals[k]):
                            ch.append(f"{src}.{k} {vals[k]!r} -> {new!r}")
                            vals[k] = new
            # 4. value_cols must equal the keys of values (non-sentinels only)
            if not rc.startswith("__"):
                keys = list((rec.get("values") or {}).keys())
                if keys and list(rec.get("value_cols") or []) != keys:
                    ch.append(f"value_cols {rec.get('value_cols')} -> {keys}")
                    rec["value_cols"] = keys
            if ch:
                dirty = True
                log.append((pid, rc, ch))
                rec["researcher_notes"] = (rec.get("researcher_notes") or "").rstrip() + (
                    "  [SCHEMA NORMALIZED at merge 2026-09-10, orchestrator: " + "; ".join(ch)
                    + ". Column names/format only, checked against the live tab header; "
                      "no research finding altered.]")
        # 6. cross_row_leads contract
        for j, ld in enumerate(d.get("cross_row_leads") or []):
            if not isinstance(ld, dict):
                continue
            lch = []
            for alias in ("target_pid", "target_project_id"):
                if alias in ld and not ld.get("project_id"):
                    ld["project_id"] = ld.pop(alias); lch.append(f"{alias} -> project_id")
            # `facts` is the slot the harvester reads. P5862 split its leads into a
            # substantive `claim` (the quoted source content) plus a `note` (the
            # caveat for the receiving row). Mapping `note` alone would put the
            # CAVEAT in the fact slot and leave the substance invisible, so when
            # both are present they are joined, labelled, in that order.
            if not ld.get("facts") and ld.get("claim") and ld.get("note"):
                ld["facts"] = f"{ld.pop('claim').rstrip()}  CAVEAT: {ld.pop('note').lstrip()}"
                lch.append("claim + note -> facts (joined; claim first)")
            for alias in ("claim", "note", "facts_note"):
                if alias in ld and not ld.get("facts"):
                    ld["facts"] = ld.pop(alias); lch.append(f"{alias} -> facts")
            for alias in ("from_pid", "source_project_id", "from_project_id"):
                if alias in ld:
                    ld["from_pid"] = ld.pop(alias)          # keep provenance, off-contract key ok
            if lch:
                dirty = True
                log.append((ld.get("project_id", "?"), f"lead#{j}", lch))
        if dirty and a.apply:
            json.dump(d, open(f, "w"), ensure_ascii=False, indent=1)
    for pid, rc, ch in log:
        for c in ch:
            print(f"{pid:7} {rc:16} {c}")
    print(f"\n{'APPLIED' if a.apply else 'DRY RUN'}: {sum(len(c) for _,_,c in log)} fix(es) "
          f"over {len({p for p,_,_ in log})} row(s)")

if __name__ == "__main__":
    main()
