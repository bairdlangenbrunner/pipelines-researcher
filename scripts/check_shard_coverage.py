#!/usr/bin/env python3
"""Does a deep-sweep shard report on EVERY worklist unit assigned to its pipeline?

Called by each subagent before it finishes (the contract in
`.claude/workflows/critical-deep-sweep.js` blocks on it), and by the orchestrator with
`--all` to audit a whole staging dir before the merge.

The defect it exists to stop: a unit whose class is MISSING_REF — the sheet HAS a value and
its `[ref]` cell is EMPTY — being confirmed in prose and reported nowhere machine-readable.
`seed_resolutions_from_worklist.py` seeds a record for every MISSING_REF unit, so a dropped
one does not go missing downstream; it silently becomes UNRESOLVED with empty notes, which
is indistinguishable from "nobody looked". Measured at 26-45% of MISSING_REF units across
the four 2026-09 US gas batches (381 units / 72 rows) while MISSING_VALUE — the one class
the contract named and gate J counted — ran at 0-1%. Same agents, same runs: the variable
was whether the contract carried a per-unit emit rule.

    python scripts/check_shard_coverage.py --staging <dir> --pid P0187
    python scripts/check_shard_coverage.py --staging <dir> --all [--json]

Exit 0 = every unit has a record. Exit 1 = units left unreported (or the shard is missing
/ unparseable). Advisory elsewhere in this repo is deliberate; here it is a hard stop,
because the agent that would fix it is still running when this is called.
"""
from __future__ import annotations

import argparse
import collections
import itertools
import json
import sys
from pathlib import Path


def load_units(staging: Path) -> dict[str, list[dict]]:
    wl = json.loads((staging / "worklist.json").read_text())
    by_pid: dict[str, list[dict]] = collections.defaultdict(list)
    for u in wl.get("units") or []:
        by_pid[u.get("project_id")].append(u)
    return by_pid


def check(units: list[dict], shard: dict) -> tuple[list[dict], list[dict]]:
    """-> (unreported units, silent-UNRESOLVED fills).

    Matching is by ref_col, disambiguated by sheet_row ONLY where a pipeline carries several
    units on the same ref_col (multi-segment rows). Owner/Operator units are keyed to the
    separate operators-owners tab, so subagents report that tab's row rather than the
    tracker's — keying on sheet_row unconditionally would flag every one of them as missing
    (the same trap `merge_deepsweep_shards.py` works around).
    """
    fills = shard.get("fills") or []
    by_col: dict[str, list[dict]] = collections.defaultdict(list)
    for f in fills:
        by_col[f.get("ref_col")].append(f)

    unreported = []
    for ref_col, group in itertools.groupby(
        sorted(units, key=lambda u: str(u.get("ref_col"))), key=lambda u: str(u.get("ref_col"))
    ):
        group = list(group)
        got = by_col.get(ref_col, [])
        if len(group) == 1:
            if not got:
                unreported.append(group[0])
            continue
        rows_got = {f.get("sheet_row") for f in got}
        for u in group:                                  # multi-segment: match per row
            if u.get("sheet_row") not in rows_got:
                unreported.append(u)

    silent = [f for f in fills
              if f.get("class_out") == "UNRESOLVED"
              and not (f.get("researcher_notes") or "").strip()]
    return unreported, silent


def run_one(staging: Path, pid: str) -> dict:
    path = staging / "rows" / f"{pid}.json"
    units = load_units(staging).get(pid, [])
    if not path.exists():
        return {"pid": pid, "error": f"no shard at {path}", "units": len(units)}
    try:
        shard = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return {"pid": pid, "error": f"shard does not parse: {e}", "units": len(units)}
    unreported, silent = check(units, shard)
    return {
        "pid": pid, "units": len(units), "fills": len(shard.get("fills") or []),
        "unreported": [{"ref_col": u.get("ref_col"), "class": u.get("class"),
                        "sheet_row": u.get("sheet_row"),
                        "primary_value": u.get("primary_value")} for u in unreported],
        "silent_unresolved": [f.get("ref_col") for f in silent],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--pid", help="check one shard (what a subagent runs)")
    ap.add_argument("--all", action="store_true", help="check every shard in <staging>/rows/")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    staging = Path(a.staging)
    if not (a.pid or a.all):
        ap.error("pass --pid <PID> or --all")

    if a.all:
        pids = sorted(p.stem for p in (staging / "rows").glob("*.json"))
    else:
        pids = [a.pid]
    out = [run_one(staging, p) for p in pids]

    if a.json:
        print(json.dumps(out, indent=1))
    bad = [r for r in out if r.get("error") or r["unreported"] or r["silent_unresolved"]]
    if not a.json:
        for r in out:
            if r.get("error"):
                print(f"FAIL {r['pid']}: {r['error']}")
                continue
            if not r["unreported"] and not r["silent_unresolved"]:
                if not a.all:
                    print(f"OK — {r['pid']}: all {r['units']} worklist unit(s) reported "
                          f"({r['fills']} fills[] object(s)).")
                continue
            print(f"FAIL {r['pid']}: {len(r['unreported'])} of {r['units']} worklist unit(s) "
                  f"have NO fills[] object.")
            for u in r["unreported"]:
                val = u["primary_value"]
                hint = (f"sheet already has {val!r} — find the source that states it, "
                        f"emit REFS_ADDED" if u["class"] == "MISSING_REF"
                        else "blank cell — fill it or say what you searched")
                print(f"     {u['ref_col']:24s} [{u['class']}] {hint}")
            for c in r["silent_unresolved"]:
                print(f"     {c:24s} [UNRESOLVED with empty researcher_notes — say what you searched]")
        if a.all:
            n = sum(len(r.get("unreported") or []) for r in out)
            s = sum(len(r.get("silent_unresolved") or []) for r in out)
            print(f"\n{len(out)} shard(s): {len(bad)} with gaps — "
                  f"{n} unreported unit(s), {s} silent UNRESOLVED.")
            if not bad:
                print("OK — every worklist unit is reported on in every shard.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
