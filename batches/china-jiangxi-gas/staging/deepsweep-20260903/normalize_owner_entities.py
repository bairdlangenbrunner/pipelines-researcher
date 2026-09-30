#!/usr/bin/env python3
"""Normalize the Jiangxi Phase I owner/operator entity strings across shards.

WHY THIS EXISTS
Ten shards independently researched the same JV and wrote its 46% holder six different
ways -- precise, the PipeChina parent, a fabricated compound with two 有限公司, and three
English renderings. The primary source (SSE bond report 242696_20250403_SXBW.pdf,
footnote 5, verified by hand 2026-09-10) says:

    天然气集团持有天然气管道公司 54%的股权，剩余 46%股权由国家管网集团东部原油储运有限公司
    （原"中国石化管道储运有限公司"）持有。

That PDF is already the sheet's own `Operator [ref]`, so the sheet's generic parent name is
a rollup of what its own citation states -- unsupported under rule 4(e). This normalizes the
string; it NEVER assigns a phase (see --deny and the 54/46 gate below).

MUST RUN BEFORE split_shards.py, which globs shards/*.json.

BOTH TARGETS VERIFIED AGAINST THE LIVE TAB 2026-09-10 (snapshot 20260910):
  * projco model: the Jiangsu precedent is real -- P4650/P4651/P4652 all record
    `Jiangsu Natural Gas Co Ltd` at `100.00%`, the project company, NOT its
    shareholders. Jiangxi's JV is the same shape, so Owner1 = the projco.
  * QCCOwner house form for a JV is `Entity [NN%]; Entity [NN%]` (149 of 923
    non-empty cells; e.g. the Jiangsu row's
    `江苏省国信集团有限公司 [51%]; 国家管网集团东部原油储运有限公司 [49%]`), and
    `国家管网集团东部原油储运有限公司` ALREADY EXISTS in that column -- so the 46%
    target is the house-registered spelling, not a new entity.
  * The live tab currently carries the DEFECT this fixes:
    `江西省天然气集团有限公司 [54%]; 国家石油天然气管网集团有限公司 [46%]` -- the
    parent where its own cited footnote says the subsidiary.
  * entity_lookup.py --tracker gas finds no existing Jiangxi owner entity (the
    28 "Jiangxi Natural Gas Pipeline Network" hits are PipelineName/Wiki, not
    owners). Nearest match is `Guangxi Natural Gas Pipeline Co Ltd` at 94% -- a
    DIFFERENT PROVINCE; do not reuse it.

Ruling recorded in orchestrator_notes.md -> "BATCH-LEVEL RULING 2026-09-10".
"""
import argparse, json, pathlib, re, sys, collections

HERE = pathlib.Path(__file__).resolve().parent

CN_GROUP   = "江西省天然气集团有限公司"
CN_EAST    = "国家管网集团东部原油储运有限公司"
CN_PROJCO  = "江西省天然气管道有限公司"
EN_PROJCO  = "Jiangxi Natural Gas Pipeline Co Ltd"
EN_GROUP   = "Jiangxi Natural Gas Group Co Ltd"
EN_EAST    = "PipeChina Eastern Crude Oil Storage and Transportation Co Ltd"
QCC_CANON  = f"{CN_GROUP} [54%]; {CN_EAST} [46%]"

# Rows whose ownership is genuinely a different shareholder set. The 54/46 gate below would
# already spare most of them; the deny list makes the intent explicit and survives a shard
# being rewritten later.
DENY = {
    "P4649": "川气东送: 国家石油天然气管网集团 50% / 中国人寿 43.86% / 国投交通控股 6.14%",
    "P4657": "川气东送: same 50/43.86/6.14 shareholder set",
    "P4661": "川气东送二线: 100% parent",
    "P4797": "WEP2 -- 西气东输分公司 is a branch OF the parent; separate cohort ruling",
    "P4944": "WEP2 branch -- ditto",
    "P4946": "WEP2 branch -- ditto",
    "P4947": "WEP2 trunk -- ditto",
}

FABRICATED = "国家石油天然气管网集团有限公司东部原油储运有限公司"   # two 有限公司; no such registrant

def has_5446(rec) -> bool:
    """Only touch a record that actually expresses the Phase I 54/46 split.

    This is the phase guard. P5860 replaced the split with 100% Group on segment-naming
    evidence because it is a Phase II row -- it must come through here untouched.
    """
    blob = json.dumps(rec.get("values") or {}, ensure_ascii=False)
    return ("54" in blob and "46" in blob)

def norm_operator(vals, changes):
    for k in list(vals):
        if k.startswith("QCCOwner") or k.startswith("QCCOperator"):
            if vals[k] != QCC_CANON:
                changes.append(f"{k}: {vals[k]!r} -> {QCC_CANON!r}")
                vals[k] = QCC_CANON

def norm_owner(vals, changes, model):
    if model == "projco":
        want = collections.OrderedDict([("Owner1", EN_PROJCO), ("Owner1%", "100.00%")])
    else:  # "split" -- the reviewer's alternative
        want = collections.OrderedDict([
            ("Owner1", EN_GROUP), ("Owner1%", "54.00%"),
            ("Owner2", EN_EAST),  ("Owner2%", "46.00%"),
        ])
    before = {k: v for k, v in vals.items() if re.fullmatch(r"Owner\d+%?", k)}
    if before == dict(want):
        return
    for k in list(vals):
        if re.fullmatch(r"Owner\d+%?", k):
            del vals[k]
    # keep Owner keys leading, in order
    rest = [(k, v) for k, v in vals.items()]
    vals.clear(); vals.update(want); vals.update(rest)
    changes.append(f"Owner cols: {json.dumps(before,ensure_ascii=False)} -> "
                   f"{json.dumps(dict(want),ensure_ascii=False)}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write; default is a dry run")
    ap.add_argument("--dir", default="shards", metavar="SUBDIR",
                    help="shard subdir to normalize (default shards/). A recovery pass's "
                         "output lands in ref_shards_recovery/, which split_shards.py never "
                         "regenerates, so the shards/ glob never reaches it -- run this a "
                         "second time with --dir ref_shards_recovery. The record shape is "
                         "identical (a `resolutions` list); only the file set differs.")
    ap.add_argument("--model", choices=["projco", "split"], default="projco",
                    help="projco (default, matches the Jiangsu P4650/P4651/P4652 precedent): "
                         "Owner1 = the project company at 100%%, JV split stays in QCCOwner. "
                         "split: put 54/46 in Owner1/Owner2 instead.")
    a = ap.parse_args()

    files = sorted((HERE / a.dir).glob("*.json"))
    if not files:
        sys.exit("no shards/ found")
    total, touched_rows, fab = 0, [], []
    for f in files:
        d = json.load(open(f), object_pairs_hook=collections.OrderedDict)
        dirty = False
        for rec in d.get("resolutions") or []:
            pid = rec.get("project_id") or f.stem
            if pid in DENY or rec.get("ref_col") not in ("Owner [ref]", "Operator [ref]"):
                continue
            if rec.get("class_out") not in ("REFS_ADDED", "REVERIFIED"):
                continue   # UNRESOLVED echoes the sheet; it proposes nothing to normalize
            if not has_5446(rec):
                continue
            vals = rec.get("values")
            if not isinstance(vals, dict):
                continue
            if FABRICATED in json.dumps(vals, ensure_ascii=False):
                fab.append(f"{pid} {rec['ref_col']}")
            changes = []
            if rec["ref_col"] == "Operator [ref]":
                norm_operator(vals, changes)
            else:
                norm_owner(vals, changes, a.model)
            if changes:
                # `value_cols` is what the workbook builder reads. This pass adds and
                # DELETES Owner keys, so a stale declaration would silently drop a value
                # (or declare a key that no longer exists). Re-sync it here rather than
                # leaning on a later normalizer -- each pass leaves a conformant record.
                keys = list(vals.keys())
                if list(rec.get("value_cols") or []) != keys:
                    changes.append(f"value_cols -> {keys}")
                    rec["value_cols"] = keys
                dirty = True; total += len(changes)
                touched_rows.append((pid, rec["ref_col"], changes))
                rec["researcher_notes"] = (rec.get("researcher_notes") or "").rstrip() + (
                    "  [ENTITY NORMALIZED at merge 2026-09-10, orchestrator: "
                    + "; ".join(changes)
                    + f". Per the batch-level ruling in orchestrator_notes.md: the 46% holder is "
                      f"{CN_EAST} (SSE bond report 242696_20250403_SXBW.pdf footnote 5, the sheet's "
                      f"own Operator [ref]), not the PipeChina parent; "
                      f"model={a.model}. Research finding unchanged -- string/shape only.]")
        if dirty and a.apply:
            json.dump(d, open(f, "w"), ensure_ascii=False, indent=1)

    for pid, col, ch in touched_rows:
        print(f"{pid:7} {col:16} " + " | ".join(ch)[:150])
    print(f"\n{'APPLIED' if a.apply else 'DRY RUN'}: {total} change(s) over "
          f"{len({p for p,_,_ in touched_rows})} row(s); model={a.model}; "
          f"{len(DENY)} PID(s) denied by scope")
    if fab:
        print("fabricated compound name found and rewritten on: " + ", ".join(fab))

if __name__ == "__main__":
    main()
