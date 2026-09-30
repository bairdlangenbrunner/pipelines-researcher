#!/usr/bin/env python3
"""P4944's start location: revert the refs-leg values, rule on the __VALIDITY__ concern.

THE FINDING (unchanged and well-evidenced). P4944's `Location [ref]` record is
REFS_ADDED at tier `high` with three verified segment-naming refs, and its own notes
plus its companion `__VALIDITY__` concern (also tier high) say those refs place the
origin station 南昌分输压气站 in 大城镇, 高安市 (Yichun prefecture), NOT in the recorded
东阳镇, 安义县 (Nanchang prefecture) -- "No source was found placing any facility of
this branch in 安义县". PipeChina's own 2026 公平开放 facility workbook (read on P5861)
independently lists 高安 as the start of the 南昌-上海支干线: a fourth publisher in a
different document class. Gao'an and Anyi are adjacent counties either side of the
Nanchang/Yichun prefecture line, so it reads as a place-name slip, not a different
pipeline. Two cells are wrong: StartLocation and StartPrefecture/District.

WHY THIS SCRIPT NO LONGER WRITES THE CORRECTED VALUE. My first pass wrote it onto the
`Location [ref]` record's `values`. That reached `ref_shards/` and stopped there:
`merge_ref_shards.py` writes `class_out`, `proposed_refs`, `verifications`, `tier`,
`independent` and notes onto a seeded record and NEVER its `values` --

    vals = ...            # set only when APPENDING an unseeded MISSING_VALUE unit
    r["class_out"] = cls; r["proposed_refs"] = refs; ...   # seeded record: no values

-- so the store and the workbook kept the sheet's values while the shard disagreed
with both, silently. That is by design, not a bug: **the refs leg does not change
values.** It carries a value only for an owed BLANK (a `MISSING_VALUE` unit appended
as a FILL). A non-blank cell that is simply wrong has exactly one channel that
reaches the deliverable -- the `__VALIDITY__` concern -- which is "QC detects, Update
fixes" working as intended, and it means the agent's original choice to stage this as
a concern "rather than a silent change" was right for a structural reason on top of
the conservative one.

So this script now does two things:
  1. Reverts the two cells on the `Location [ref]` record to the sheet's values, so
     shards/, ref_shards/ and the store agree again. A divergence that changes no
     output is worse than either alternative.
  2. Sets an explicit `recommendation` on the start-location `__VALIDITY__` concern.
     `harvest_sentinel_findings.py` hard-coded one boilerplate line for all 99
     sentinel findings ("Agent research verdict -- see researcher_notes"); it now
     honours a per-record `recommendation`, so the actual actionable change lands in
     the column a reviewer scans instead of being buried in a 1,400-character note.
     The default still fires for every record that does not set one.

Not touched: StartState/Province (Jiangxi) and StartCountryOrArea (China) are true of
Gao'an too; the whole End side is corroborated by all three refs. `StartYear1` is a
separate first-gas-vs-full-line convention question and keeps its own concern record.

Runs at merge-chain step 0e7 -- BEFORE split_shards.py, which regenerates rows/ and
ref_shards/ from shards/ on every run. Re-run with --dir ref_shards_recovery for
symmetry with the other normalizers (P4944 has no recovery shard today).
"""
import argparse, json
from pathlib import Path

HERE = Path(__file__).resolve().parent

PID = "P4944"
REF_COL = "Location [ref]"
# The sheet's values -- what the record must carry, since the refs leg cannot propose
# a change to a non-blank cell.
SHEET = {
    "StartLocation": "Dongyang Town, Anyi County",
    "StartPrefecture/District": "Nanchang",
}
# What my earlier pass wrote, and what has to come back out.
STAGED = {
    "StartLocation": "Dacheng Town, Gao'an City",
    "StartPrefecture/District": "Yichun",
}
STAMP_KEY = "VALUE CORRECTED at merge"

RECOMMENDATION = (
    "CHANGE 2 CELLS: StartLocation 'Dongyang Town, Anyi County' -> \"Dacheng Town, "
    "Gao'an City\", and StartPrefecture/District 'Nanchang' -> 'Yichun'. Gao'an City is "
    "a county-level city under YICHUN prefecture, so both cells move together or the row "
    "becomes internally inconsistent. Evidence: three branch-naming sources on three "
    "hosts put the origin station 南昌分输压气站 in 大城镇, 高安市, and PipeChina's own 2026 "
    "公平开放 facility workbook independently lists 高安 as the start of the 南昌-上海支干线 "
    "(a fourth publisher, different document class); no source places any facility of "
    "this branch in 安义县. Gao'an and Anyi are adjacent counties across the "
    "Nanchang/Yichun prefecture line, so this is a place-name slip, not a different "
    "pipeline. LEAVE StartState/Province (Jiangxi) and StartCountryOrArea (China) -- "
    "true of Gao'an as well -- and the whole End side, which all three refs corroborate. "
    "Not staged as a value on the Location [ref] record because the refs leg cannot "
    "propose a change to a non-blank cell (merge_ref_shards.py writes refs and tier onto "
    "a seeded record, never its values); this concern is the channel. Orchestrator "
    "ruling 2026-09-10."
)


def revert_values(d, subdir):
    changed = 0
    for i, r in enumerate(d.get("resolutions") or []):
        if (r.get("ref_col") or "").strip() != REF_COL:
            continue
        vals = r.get("values") or {}
        moved = []
        for col, sheet_val in SHEET.items():
            cur = vals.get(col)
            if cur == sheet_val:
                continue
            if cur != STAGED[col]:
                print(f"  {subdir}/{PID} #{i} {col}: expected {STAGED[col]!r} or "
                      f"{sheet_val!r}, found {cur!r} -- NOT touched, re-check by hand")
                continue
            vals[col] = sheet_val
            moved.append(f"{col} {cur!r} -> {sheet_val!r} (reverted)")
        if not moved:
            continue
        r["values"] = vals
        note = (r.get("researcher_notes") or "")
        if STAMP_KEY in note:
            # Drop the whole stamp my earlier pass appended -- it describes a change
            # that is no longer being made, and a stale stamp is worse than none.
            note = note[:note.index("  [" + STAMP_KEY)].rstrip()
            r["researcher_notes"] = note + (
                "  [VALUE CHANGE WITHDRAWN FROM THIS RECORD at merge 2026-09-10, "
                "orchestrator: the start-location correction was briefly staged here and "
                "has been reverted to the sheet's values. merge_ref_shards.py never writes "
                "`values` onto a seeded record, so a refs-leg record cannot propose a "
                "change to a non-blank cell -- it reached ref_shards/ and no further. The "
                "correction now carries an explicit `recommendation` on this row's "
                "start-location __VALIDITY__ concern, which is the channel that reaches "
                "the deliverable. The finding itself is unchanged and still tier high.]")
        changed += 1
        for m in moved:
            print(f"  {subdir}/{PID} #{i} {REF_COL}: {m}")
    return changed


def set_recommendation(d, subdir):
    changed = 0
    for i, r in enumerate(d.get("resolutions") or []):
        rc = (r.get("ref_col") or r.get("sentinel") or "").strip()
        if rc != "__VALIDITY__":
            continue
        # Pick the start-location concern, not the StartYear1 one. Match on the finding
        # text rather than on list position -- the order is not a contract.
        note = r.get("researcher_notes") or ""
        if "START LOCATION" not in note:
            continue
        if (r.get("recommendation") or "").strip() == RECOMMENDATION:
            print(f"  {subdir}/{PID} #{i} __VALIDITY__: recommendation already set, skipped")
            continue
        r["recommendation"] = RECOMMENDATION
        changed += 1
        print(f"  {subdir}/{PID} #{i} __VALIDITY__: recommendation set "
              f"({len(RECOMMENDATION)} chars, start-location concern)")
    return changed


def main(apply=False, subdir="shards"):
    path = HERE / subdir / f"{PID}.json"
    if not path.exists():
        print(f"  {subdir}/{PID}.json: absent, nothing to do")
        return 0
    d = json.loads(path.read_text())
    changed = revert_values(d, subdir) + set_recommendation(d, subdir)
    if changed and apply:
        path.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
        print(f"  wrote {path.relative_to(HERE)}")
    elif changed:
        print("  DRY RUN -- pass --apply to write")
    return changed


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dir", default="shards")
    a = ap.parse_args()
    n = main(apply=a.apply, subdir=a.dir)
    print(f"{n} change(s) {'applied' if a.apply else 'to apply'}")
