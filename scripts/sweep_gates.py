#!/usr/bin/env python3
"""Pre-delivery gates for any sweep staging dir. Read-only: reports, never edits.

Promoted 2026-09-03 from the Jiangxi-only `predelivery_checks.py` (deepsweep-20260902) so
every sweep runs the same gates instead of each batch re-deriving them. The lesson they
encode: a sweep that looks comprehensive by REF COUNT can be thin by ORIGIN COUNT — Jiangxi
v1 shipped 98 REFS_ADDED, three documents carried 71 of them, and 4 of 18 rows rested on a
single host — and the tier column is what a researcher trusts when deciding to paste.
MZ's 2026-09-03 feedback on v2 added the other two axes these gates now cover: RELEVANCE
(a ref must name the pipeline, not just contain its number) and COVERAGE OF BLANKS (a
blank value on an operating row is owed work, not a non-unit).

    python scripts/sweep_gates.py --staging batches/<scope>/staging/<run>/ [--json]
        [--dominant-min 15] [--pool harvest_screen.json]

Gates (all advisory; exit code is always 0 — they inform the delivery note):
  A  SOURCE DIVERSITY   -- a row whose sourced units all trace to <2 distinct hosts.
  B  FALSE HIGH         -- a `high` unit whose verified refs share one host or number <2
                           (a `__VALIDITY__` concern is counted over proposed_refs -- see
                           `evidence()`).
  C  DOMINANT DOCUMENT  -- one URL carrying >= --dominant-min units cannot be the second
                           source for a `high`: one origin restated is still one origin.
  D  INDEPENDENCE FLAG  -- `independent: true` on a unit with <2 verified refs.
  E  ORPHAN REFS        -- a ref with no paired value, or a sourced value with no ref.
  F  BANNED / GEM       -- gem.wiki, globalenergymonitor.org, abarrelfull anywhere.
  G  HARVEST COVERAGE   -- live pool URLs never opened on a row that still reports
                           UNRESOLVED (needs --pool, or harvest_screen.json in the dir).
  H  RECOVERED SPN      -- live origins behind Save-Page-Now citations, unopened on an
                           UNRESOLVED row (needs spn_recovered_origins.json; else skipped).
  I  RELEVANCE          -- a sourced unit none of whose verifications says name_found=true:
                           either the page does not name the pipeline (name_found=false)
                           or nobody checked (field absent). Both are listed, separately.
  J  BLANKS COVERAGE    -- worklist MISSING_VALUE units (--owe-fills) with no FILL record
                           of any class in the store: an owed blank nobody reported on.
  K  SINGLE-SOURCE UNITS -- REFS_ADDED units with exactly one verified ref (the 2-per-data-
                           point target unmet). Not a defect (medium is fillable) but the
                           count is the honest measure of how far the batch is from green.
  L  UNCITED VALUES NEVER WORKED -- worklist MISSING_REF units (the sheet HAS a value, its
                           [ref] cell is EMPTY) whose store record is still UNRESOLVED with
                           NO refs and NO researcher_notes: nobody reported on it. J's twin,
                           and the one that was missing. A dropped blank leaves no record at
                           all, so J catches it by absence; a dropped MISSING_REF unit IS
                           seeded by `seed_resolutions_from_worklist.py`, so it survives as
                           an empty record that reads exactly like honest failure. The split
                           against UNRESOLVED-with-notes is the whole point: notes = the
                           researcher looked and said so; no notes = silence.
  M  PROSE IN A PASTEABLE CELL -- a `values` (or validity `contested`) entry that is a RECOMMENDATION rather than the
                           cell content: "downgrade from 'high' to 'low ...' pending
                           redigitization -- staged geometry covers only ~14% ...". Every
                           `values` entry lands in a tier-colored backend cell the
                           researcher copies; prose there is pasted verbatim into the live
                           tracker. The rationale belongs in `researcher_notes` /
                           `recommendation`, which the cell comment already carries. First
                           seen on US gas batch 5 (fixed by hand, commit 7e75f26), again on
                           Russia R2 P5539 -- hence the gate.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from url_verifier import BLOCKLIST_HOSTS, GEM_HOSTS  # noqa: E402
from merge_qc import publisher_key  # noqa: E402

BANNED = tuple(GEM_HOSTS + BLOCKLIST_HOSTS)

# Columns whose content is legitimately narrative — never flagged by gate M.
PROSE_OK_COLS = {"ResearcherNotes", "Wiki", "OtherEnglishNames", "OtherLanguageNames",
                 "OtherLanguagePrimaryPipelineName", "ShelvedCancelledDescription"}
# Markers of a recommendation ABOUT a cell rather than the cell's content. A bare long
# value is fine (owner strings run long); it is the narrative that is the defect.
PROSE_MARKERS = (" -- ", " — ", " see ", "pending ", "do not ", "was blank",
                 "downgrade", "upgrade to", "instead of", "http://", "https://",
                 "(add ", "(remove", "n/a --", "per sourced")


def prose_value(col: str, val) -> str:
    """Is this `values` entry a recommendation instead of a pasteable cell value?"""
    if col in PROSE_OK_COLS or col.endswith(" [ref]") or col.endswith("Notes"):
        return ""
    v = str(val or "").strip()
    if len(v) < 40:
        return ""
    low = v.lower()
    for m in PROSE_MARKERS:
        if m in low:
            return m.strip()
    return "over 120 chars" if len(v) > 120 else ""

SOURCED = {"REFS_ADDED", "REVERIFIED", "CONFIRMED"}
SENTINEL_PREFIX = "__"


def host(u: str) -> str:
    """Publisher identity for the independence gates — delegated to
    `merge_qc.publisher_key` so the gates and the mergers can never drift. It
    unwraps Wayback captures to the origin AND collapses document-redistribution
    venues (exchange portals, corporate-data aggregators) into one bucket, since
    on those the host names the venue rather than the author."""
    return publisher_key(u)


def verified(r: dict) -> list[str]:
    """Refs the merge would actually KEEP: ok && contains_value. Counting proposed_refs
    instead would credit a row for URLs that get dropped at merge — which is precisely
    how a row ends up looking two-sourced in the workbook and single-sourced in fact.

    Strict, with no lenient branch: absent verifications yield zero refs. That differs
    deliberately from `merge_qc.verified_refs`, which host-filters only when handed no
    verifications -- see the asymmetry note in its docstring before writing a new
    consumer of either."""
    ok = {v.get("url") for v in (r.get("verifications") or [])
          if v.get("ok") and v.get("contains_value")}
    return [u for u in (r.get("proposed_refs") or []) if u in ok]


def evidence(r: dict) -> list[str]:
    """The refs a record's TIER and INDEPENDENCE claims are counted over (gates B/C/D).

    Identical to `verified()` except for one documented repo convention: a
    `__VALIDITY__` record carries NO `verifications` by convention (see the header
    of `audit_shard.py`, which counts a validity record's tier over `proposed_refs`
    for exactly this reason), and the merge carries a concern's `proposed_refs`
    through UNFILTERED — so counting a validity concern over ok+contains_value
    scores every one of them at zero and buries the real findings. Russia R1:
    33 of 33 gate-B flags and 49 of 49 gate-D flags were validity records that each
    carried 2+ proposed refs. A validity record that DOES carry verifications
    (agents sometimes write them) is judged strictly, like everything else."""
    if str(r.get("ref_col") or "") == "__VALIDITY__" and not (r.get("verifications") or []):
        return [u for u in (r.get("proposed_refs") or []) if u]
    return verified(r)


def _load(path: Path):
    return json.loads(path.read_text()) if path.exists() else None


def run(staging: Path, dominant_min: int = 15, pool_path: Path | None = None) -> dict:
    store = json.loads((staging / "staged_resolutions.json").read_text())
    res = store["resolutions"]
    wl = _load(staging / "worklist.json") or {}
    pool = _load(pool_path) if pool_path else _load(staging / "harvest_screen.json")
    spn = _load(staging / "spn_recovered_origins.json")

    by_pid = collections.defaultdict(list)
    for r in res:
        by_pid[r.get("project_id")].append(r)

    url_units = collections.Counter()
    for r in res:
        for u in set(verified(r)):
            url_units[u] += 1
    dominant = {u for u, n in url_units.items() if n >= dominant_min}

    # A sourced FILL replaces the value in its ref cell, so its refs ARE that unit's refs; the
    # carried HAS_REF/MISSING_REF record for the same cell documents the value being replaced.
    # Gate I judges the replacement, never the superseded sheet ref (US gas A1, 2026-09-11:
    # 21 carried EIA `data.php` refs failed I though every one had a FILL whose refs named
    # the pipeline).
    superseded = {(r.get("project_id"), str(r.get("sheet_row", "")), r.get("ref_col"))
                  for r in res if r.get("class_in") == "FILL"
                  and r.get("class_out") in SOURCED and verified(r)}

    A, B, C, D, E, F, G, H = [], [], [], [], [], [], [], []
    I_false, I_unchecked, J, K, L = [], [], [], [], []
    for pid, recs in sorted(by_pid.items()):
        hosts = {host(u) for r in recs if r.get("class_out") in SOURCED
                 for u in verified(r)} - {""}
        sourced_n = sum(1 for r in recs if r.get("class_out") in SOURCED)
        if sourced_n and len(hosts) < 2:
            A.append((pid, sourced_n, sorted(hosts)))
        for r in recs:
            vr = verified(r)
            ev = evidence(r)          # == vr except for the validity convention
            vh = {host(u) for u in ev} - {""}
            tier = (r.get("tier") or "").lower()
            col = r.get("ref_col")
            sentinel = str(col).startswith(SENTINEL_PREFIX)
            if tier == "high" and (len(ev) < 2 or len(vh) < 2):
                B.append((pid, col, len(ev), sorted(vh)))
            if tier == "high" and len(vh) == 2 and dominant & set(ev) and \
                    len([u for u in ev if u not in dominant]) < 2:
                C.append((pid, col, sorted(set(ev) & dominant)))
            if r.get("independent") and len(ev) < 2:
                D.append((pid, col, len(ev)))
            has_val = any(str(v).strip() for v in (r.get("values") or {}).values())
            # Only a SOURCED record's refs reach a `[ref]` cell (build_ref_workbook.py never
            # writes ref text for UNRESOLVED — see its "must never blank the prefilled current"
            # rule), so an UNRESOLVED carrying the evidence for WHY a blank is correct, or why a
            # recorded value is contested, is documentation, not an orphan.
            if vr and not has_val and not sentinel and r.get("class_out") in SOURCED:
                E.append((pid, col, "ref without a paired value"))
            # A few tracker value columns have no paired `[ref]` column at all
            # (OtherEnglishNames, the OtherLanguage* names), so such a record keys to no
            # ref cell and can orphan nothing — its corroboration lives in researcher_notes
            # by necessity (tx P0257's alias fix, 2026-09-09).
            if (has_val and not vr and r.get("class_out") in SOURCED and not sentinel
                    and str(col or "").strip()):
                E.append((pid, col, "value marked sourced with no verified ref"))
            for u in (r.get("proposed_refs") or []):
                if any(b in u.lower() for b in BANNED):
                    F.append((pid, col, u))
            replaced = (r.get("class_in") in ("HAS_REF", "MISSING_REF") and
                        (pid, str(r.get("sheet_row", "")), col) in superseded)
            if vr and not sentinel and r.get("class_out") in SOURCED and not replaced:
                okv = [v for v in (r.get("verifications") or []) if v.get("ok")]
                named = [v for v in okv if "name_found" in v]
                if named and not any(v.get("name_found") for v in named):
                    I_false.append((pid, col, vr[0]))
                elif not named:
                    I_unchecked.append((pid, col))
            if r.get("class_out") == "REFS_ADDED" and len(vr) == 1 and not sentinel:
                K.append((pid, col))

    # G — harvest coverage. Pool is a FLAT LIST of {ok, status, reason, url, project_ids}.
    if pool:
        live_by_pid = collections.defaultdict(set)
        for e in pool:
            if e.get("ok"):
                for p in e.get("project_ids") or []:
                    live_by_pid[p].add(e["url"])
        # "Opened" = cited OR verified: a URL read and REJECTED was still opened.
        opened = {u for r in res for u in (r.get("proposed_refs") or [])}
        opened |= {v.get("url") for r in res for v in (r.get("verifications") or []) if v.get("url")}
        for pid, recs in sorted(by_pid.items()):
            if not any(r.get("class_out") == "UNRESOLVED" for r in recs):
                continue
            unopened = live_by_pid.get(pid, set()) - opened
            if unopened:
                G.append((pid, len(unopened), len(live_by_pid.get(pid, set()))))
        if spn:
            spn_by_pid = collections.defaultdict(set)
            for e in spn:
                if e.get("ok"):
                    for p in e.get("project_ids") or []:
                        spn_by_pid[p].add(e["origin"])
            for pid, recs in sorted(by_pid.items()):
                if not any(r.get("class_out") == "UNRESOLVED" for r in recs):
                    continue
                unopened = spn_by_pid.get(pid, set()) - opened
                if unopened:
                    H.append((pid, len(unopened), sorted(unopened)[0]))

    # J — blanks coverage: every worklist MISSING_VALUE unit needs SOME record in the
    # store (a FILL of any class_out, or a ref record on the same cell). "No record" means
    # the owed blank was never reported on — the silent-skip MZ flagged.
    owed = [u for u in (wl.get("units") or []) if u.get("class") == "MISSING_VALUE"]
    if owed:
        have = {(r.get("project_id"), r.get("ref_col")) for r in res}
        for u in owed:
            key = (u.get("project_id"), u.get("ref_col"))
            if key not in have:
                J.append((u.get("project_id"), u.get("ref_col"), u.get("status", "")))

    # L — uncited values never worked: J's twin for MISSING_REF. The seeder gives every one
    # of these a record, so absence can't be the test; silence is. A record still UNRESOLVED
    # with no refs AND no notes was never reported on by any subagent.
    uncited = [u for u in (wl.get("units") or []) if u.get("class") == "MISSING_REF"]
    L_looked = 0
    if uncited:
        # Key on (pid, ref_col, sheet_row): a multi-segment pipeline carries one unit per
        # SEGMENT ROW on the same ref_col, and each is its own cell in the sheet — crediting
        # a whole pipeline because one of its segments was worked hides the other segments.
        # Fall back to (pid, ref_col) only where the pipeline has exactly one unit on that
        # column, which is also how owner/operator records (keyed to the operators-owners
        # tab's row, not the tracker's) find their seeded record.
        rec_by_key, rec_by_col = {}, {}
        for r in res:
            if str(r.get("ref_col", "")).startswith(SENTINEL_PREFIX):
                continue
            rec_by_key.setdefault(
                (r.get("project_id"), r.get("ref_col"), r.get("sheet_row")), []).append(r)
            rec_by_col.setdefault((r.get("project_id"), r.get("ref_col")), []).append(r)
        units_per_col = collections.Counter(
            (u.get("project_id"), u.get("ref_col")) for u in uncited)
        for u in uncited:
            col_key = (u.get("project_id"), u.get("ref_col"))
            recs = rec_by_key.get((*col_key, u.get("sheet_row")))
            worked = lambda rs: any(  # noqa: E731
                r.get("class_out") in SOURCED or (r.get("proposed_refs") or [])
                or (r.get("researcher_notes") or "").strip() for r in (rs or []))
            # An exact-row hit can return only ONE of several records on the same cell: the
            # seed, while the research landed on a sibling the fold failed to merge into it
            # (west P2573 Owner, 2026-09-09 — the deep leg disputed the recorded owner on a
            # separate FILL and the seed stayed blank). The unit WAS worked, so widen to the
            # column before calling it never worked; never narrow, so a genuinely untouched
            # cell on a multi-segment row still reports.
            if (not recs or not worked(recs)) and units_per_col[col_key] == 1:
                recs = rec_by_col.get(col_key) or recs
            if not recs:
                L.append((u.get("project_id"), u.get("ref_col"), u.get("primary_value", "")))
                continue
            if any(r.get("class_out") in SOURCED or (r.get("proposed_refs") or [])
                   or (r.get("researcher_notes") or "").strip() for r in recs):
                if not any(r.get("class_out") in SOURCED for r in recs):
                    L_looked += 1
                continue
            L.append((u.get("project_id"), u.get("ref_col"), u.get("primary_value", "")))

    # M -- prose where a pasteable value belongs (every `values` entry is a backend cell,
    # and so is every `contested` entry on a validity concern: it is the candidate value
    # the Backend tab marks orange -- R4b/R6 shipped prose there, fixed by hand)
    M = []
    for r in res:
        for field in ("values", "contested"):
            for col, val in (r.get(field) or {}).items():
                why = prose_value(col, val)
                if why:
                    M.append((r.get("project_id"), f"{r.get('ref_col')}/{field}:{col}",
                              str(val)[:110], why))

    return {
        "records": len(res), "rows": len(by_pid),
        "M_prose_in_value_cell": M,
        "A_single_host_rows": A, "B_false_high": B, "C_dominant_document": C,
        "D_independence_flag": D, "E_orphan_refs": E, "F_banned_sources": F,
        "G_unopened_pool_on_unresolved_rows": G,
        "H_recovered_spn_origins_unopened": H,
        "I_relevance_name_not_found": I_false,
        "I_relevance_unchecked": I_unchecked,
        "J_owed_blanks_unreported": J,
        "K_single_source_refs_added": K,
        "L_uncited_values_never_worked": L,
        "uncited_owed": len(uncited),
        "uncited_unresolved_but_worked": L_looked,
        "fills_owed": len(owed),
        "fills_staged": sum(1 for r in res if r.get("class_in") == "FILL"),
        "lean_fills_deferred": ((wl.get("summary") or {}).get("lean") or {}).get(
            "deferred_by_reason", {}).get("fills_deferred") if (wl.get("scope") or {}).get("lean") else None,
        "pool_present": bool(pool),
        "dominant_documents": sorted(((n, u) for u, n in url_units.items()
                                      if n >= dominant_min), reverse=True),
    }


def report(out: dict, dominant_min: int) -> None:
    def sec(k, rows, ok_msg, fmt, cap=40):
        print(f"\n{k}  ({len(rows)})")
        if not rows:
            print(f"    PASS — {ok_msg}")
        for r in rows[:cap]:
            print("    " + fmt(r))
        if len(rows) > cap:
            print(f"    … {len(rows) - cap} more")

    print(f"sweep gates — {out['records']} records, {out['rows']} rows")
    sec("A  source diversity (<2 distinct hosts on a sourced row)", out["A_single_host_rows"],
        "every sourced row rests on 2+ origins",
        lambda r: f"{r[0]}: {r[1]} sourced unit(s), hosts={r[2] or ['(none)']}")
    sec("B  tier `high` without 2 verified refs on 2 hosts", out["B_false_high"],
        "every high tier has 2+ independent origins",
        lambda r: f"{r[0]} {r[1]}: {r[2]} verified ref(s), hosts={r[3]}")
    sec(f"C  `high` leaning on a dominant document (>={dominant_min} units)", out["C_dominant_document"],
        "no high tier rests on one restated origin",
        lambda r: f"{r[0]} {r[1]}: dominant {r[2]}")
    sec("D  independent=true with <2 verified refs", out["D_independence_flag"],
        "the independence flag matches the rubric",
        lambda r: f"{r[0]} {r[1]}: {r[2]} verified ref(s)")
    sec("E  orphan refs / unsourced sourced-values", out["E_orphan_refs"],
        "no orphans in either direction", lambda r: f"{r[0]} {r[1]}: {r[2]}")
    sec("F  banned or GEM sources", out["F_banned_sources"], "0 GEM surfaces, 0 blocklisted",
        lambda r: f"{r[0]} {r[1]}: {r[2]}")
    if out["pool_present"]:
        sec("G  live pool URLs never opened on a row still UNRESOLVED",
            out["G_unopened_pool_on_unresolved_rows"], "the harvested pool was worked to exhaustion",
            lambda r: f"{r[0]}: {r[1]} of {r[2]} live pool URL(s) unopened")
        sec("H  live origins behind Save-Page-Now citations, unopened on an UNRESOLVED row",
            out["H_recovered_spn_origins_unopened"], "no recoverable SPN origin is left unread",
            lambda r: f"{r[0]}: {r[1]} unopened, e.g. {r[2][:78]}")
    else:
        print("\nG/H  skipped — no harvest_screen.json (pass --pool to enable)")
    sec("I  relevance: sourced unit whose refs do NOT name the pipeline (name_found=false)",
        out["I_relevance_name_not_found"], "every checked ref names the pipeline",
        lambda r: f"{r[0]} {r[1]}: {r[2][:80]}")
    sec("I' relevance UNCHECKED (no name_found on any ok verification)",
        out["I_relevance_unchecked"], "every sourced unit carries a relevance check",
        lambda r: f"{r[0]} {r[1]}", cap=15)
    if out["fills_owed"]:
        sec(f"J  owed blanks with no record at all (fills owed {out['fills_owed']}, "
            f"FILL records staged {out['fills_staged']})", out["J_owed_blanks_unreported"],
            "every owed blank was reported on (filled or honest UNRESOLVED)",
            lambda r: f"{r[0]} {r[1]} [{r[2]}]")
    elif out.get("lean_fills_deferred") is not None:
        print(f"\nJ  skipped — lean pass: {out['lean_fills_deferred']} blank-value units deferred to "
              f"deferred_units.json (owed to a later fills pass, docs/sops/lean_pass.md); "
              f"FILL records staged: {out['fills_staged']}")
    else:
        print(f"\nJ  skipped — worklist has no MISSING_VALUE units (built without --owe-fills); "
              f"FILL records staged: {out['fills_staged']}")
    if out["uncited_owed"]:
        sec(f"L  uncited values NEVER WORKED (MISSING_REF units owed {out['uncited_owed']}; "
            f"{out['uncited_unresolved_but_worked']} more unresolved but with notes)",
            out["L_uncited_values_never_worked"],
            "every value the sheet carries uncited was reported on (sourced or honest UNRESOLVED)",
            lambda r: f"{r[0]} {r[1]} — sheet has {str(r[2])[:30]!r}, no ref, no notes")
    else:
        print("\nL  skipped — worklist has no MISSING_REF units")
    sec("M  prose where a pasteable value belongs (values{} / contested{} entry)",
        out["M_prose_in_value_cell"],
        "every proposed value is cell content, not a recommendation",
        lambda r: f"{r[0]} {r[1]} [{r[3]}]: {r[2]!r}", cap=20)
    sec("K  REFS_ADDED on exactly one verified ref (2-per-data-point target unmet)",
        out["K_single_source_refs_added"], "every added ref is two-sourced",
        lambda r: f"{r[0]} {r[1]}", cap=10)
    if out["dominant_documents"]:
        print("\ndominant documents (one origin carrying many units):")
        for n, u in out["dominant_documents"]:
            print(f"    {n:3d}  {u[:100]}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--dominant-min", type=int, default=15)
    ap.add_argument("--pool", help="harvest_screen.json (flat list of screened pool URLs); "
                                   "default <staging>/harvest_screen.json if present")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    out = run(Path(a.staging), a.dominant_min, Path(a.pool) if a.pool else None)
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        report(out, a.dominant_min)


if __name__ == "__main__":
    main()
