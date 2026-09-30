#!/usr/bin/env python3
"""Does a Leg-3 shard report on EVERY flag the handoff worklist raised for its row?

The handoff packet's `worklist.json` is FLAG-shaped (`rows[].flags[]`), not UNIT-shaped
(`units[]`), so `scripts/check_shard_coverage.py` — which keys on `units` — passes
vacuously here and checks nothing. This is its analogue for a QC Leg-3 fan-out, and it
exists for the same defect rule 4(e) names: a flagged disagreement resolved in prose and
reported nowhere machine-readable is indistinguishable from nobody having looked.

A flag on field X is satisfied by either
  * a `fills[]` record whose `value_cols` contains X, or whose `ref_col` is `X [ref]`, or
  * a `validity[]` record whose `fields` array names X — the judgement shape, used when the
    honest answer has no single cell to fill (a granularity ruling, a partial-route call).
`fields` is a gate-only key; `merge_deepsweep_shards.py` selects the keys it carries and
drops the rest, so it never reaches the deliverable.

    python3 batches/united-states-gas/staging/qc/check_flag_coverage.py --pid P0271
    python3 batches/united-states-gas/staging/qc/check_flag_coverage.py --all [--json]

Exit 0 = every flag has a record. Exit 1 = flags left unreported, or the shard is missing
or unparseable. Blocking, per shard, before a subagent finishes — the agent that would fix
it is still running when this is called.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALID_CLASS_OUT = {"REFS_ADDED", "REVERIFIED", "UNRESOLVED", "DEAD_LINK"}


def flags_by_pid() -> dict[str, list[dict]]:
    """The FAN-OUT's scope, not the packet's full record.

    `worklist.json` holds all 209 flagged rows and stays the packet's record;
    `worklist_leg3.json` holds the 91-row B/D/E cut Baird chose at the gate
    (2026-09-16). A row in the cut usually ALSO carries a class-A multi-segment-union
    flag that ships as a `Gas_Decisions` granularity ruling rather than as research, so
    checking against the full worklist would demand a record nobody was asked to write.
    """
    for name in ("worklist_leg3.json", "worklist.json"):
        fp = HERE / name
        if fp.exists():
            return {r["project_id"]: r.get("flags", []) for r in json.loads(fp.read_text())["rows"]}
    raise SystemExit(f"no worklist_leg3.json / worklist.json in {HERE}")


def covered_fields(shard: dict) -> set[str]:
    got: set[str] = set()
    for f in shard.get("fills") or []:
        got.update(f.get("value_cols") or [])
        rc = (f.get("ref_col") or "").strip()
        if rc.endswith(" [ref]"):
            got.add(rc[:-6].strip())
    for v in shard.get("validity") or []:
        got.update(v.get("fields") or [])
    return got


def check(pid: str, want: list[dict]) -> list[str]:
    fp = HERE / "rows" / f"{pid}.json"
    if not fp.exists():
        return [f"{pid}: NO SHARD — write rows/{pid}.json even if everything is UNRESOLVED"]
    try:
        shard = json.loads(fp.read_text())
    except Exception as e:                                    # noqa: BLE001
        return [f"{pid}: shard does not parse — {e}"]

    out = []
    got = covered_fields(shard)
    for fl in want:
        field = fl.get("field")
        if field not in got:
            out.append(f"{pid}: flag '{field}' ({fl.get('source')}) has no fills[] or "
                       f"validity[] record — {str(fl.get('detail'))[:110]}")

    for f in shard.get("fills") or []:
        cls = f.get("class_out")
        if cls not in VALID_CLASS_OUT:
            out.append(f"{pid}: fills[] class_out={cls!r} is outside "
                       f"{sorted(VALID_CLASS_OUT)} — the merge drops it silently")
        if not (f.get("ref_col") or "").strip():
            out.append(f"{pid}: a fills[] record has no ref_col to key on — it will vanish")
        if cls == "UNRESOLVED" and not (f.get("researcher_notes") or "").strip():
            out.append(f"{pid}: UNRESOLVED on {f.get('ref_col')!r} with empty "
                       f"researcher_notes — say what you searched")
    for v in shard.get("validity") or []:
        if not (v.get("recommendation") or "").strip():
            out.append(f"{pid}: a validity[] record has no recommendation — "
                       f"state the ACTION a human should take, not a summary")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--pid")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    want = flags_by_pid()
    pids = sorted(want) if args.all else [args.pid]
    problems: list[str] = []
    for p in pids:
        if p not in want:
            problems.append(f"{p}: not on the worklist — check the PID")
            continue
        problems += check(p, want[p])

    if args.json:
        print(json.dumps({"checked": len(pids), "problems": problems}, indent=1))
    else:
        for line in problems:
            print(line)
        n = len(pids)
        print(f"{'FAIL' if problems else 'OK'}: {n} shard(s), {len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
