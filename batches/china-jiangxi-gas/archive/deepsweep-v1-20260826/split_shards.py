#!/usr/bin/env python3
"""Route the fan-out's per-BATCH shards to the per-PID files each merge step requires.

The fan-out writes one shard per subagent batch (`shards/batch_NN.json`, a
`{"batch": …, "resolutions": [...]}` doc covering ~4 PIDs). Three consumers read
shards, and no two of them agree on where to look:

  merge_ref_shards.py          globs  ref_shards/*.json   -> batch files would work
  harvest_sentinel_findings.py globs  ref_shards/P*.json  -> batch files are SKIPPED
  merge_deepsweep_shards.py    globs  rows/*.json         -> reads d["fills"] / d["validity"]

Two silent-loss traps follow, and this script exists to close both.

1. FILENAME. A `__VALIDITY__` / `__REDUNDANCY__` sentinel has no baseline ref record,
   so merge_ref_shards WARNs and drops it and only the harvester recovers it — and the
   harvester would never see a file named `batch_03.json`. Sentinels are the
   highest-value findings in a deep sweep (this batch's route-length divergences and the
   P4777 redundancy verdict among them). So: split by ProjectID, satisfying both globs.

2. SHAPE. A `kind: FILL` record on a blank-value row has no baseline ref unit either —
   correctly, since the no-orphan-refs rule means a blank value column emits no ref unit
   for the worklist to carry. So merge_ref_shards drops it for want of a key, and the
   harvester only rescues the two sentinels. **Fills fall through both scripts.** Harmless
   while a fill is UNRESOLVED (no value, no refs), but six in-scope rows have a blank
   `LengthKnown`, so a successfully sourced length would vanish with no warning. Fills are
   merge_deepsweep_shards' job, and it reads them from `rows/<PID>.json`.

Each record therefore goes to EXACTLY ONE destination, keyed on `kind`:

    ref_col starts "__"        ->  ref_shards/<PID>.json  (sentinel; harvester)
    kind == "FILL"             ->  rows/<PID>.json fills[] (merge_deepsweep_shards)
    (pid, ref_col) not owed    ->  rows/<PID>.json fills[] -- STRUCTURAL, see below
    everything else            ->  ref_shards/<PID>.json   (merge_ref_shards)

The third rule is the one that matters. Routing on the `kind` tag alone trusts the shard
to have labelled itself, and three of Jiangxi's batch-02 records did not: they say
"FILL target: LengthKnown is blank" in their own `researcher_notes` and carry `kind: null`,
so they were dropped with a WARN. If the worklist owes no unit at `(pid, ref_col)` then the
value column is blank and the record is a fill by construction, whatever it called itself.

Row identity (`pipeline_name`, `wiki`, `sheet_row`, `segment_name`) is not carried on a
fill record, so it is joined back from worklist.json — merge_deepsweep_shards stamps it
onto every merged row and would otherwise write blanks.

Idempotent: rewrites ref_shards/ and rows/ from shards/ every run.

    python split_shards.py     # then, IN THIS ORDER:
    #   merge_ref_shards.py -> merge_deepsweep_shards.py -> harvest_sentinel_findings.py
    # The harvester runs LAST: merge_deepsweep_shards' is_old_deepsweep() drops any record
    # whose ref_col is __VALIDITY__, which is exactly what the harvester writes. Harvesting
    # first zeroes the sentinels out (verified empirically: 2 -> 0).
"""
from __future__ import annotations

import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# merge_deepsweep_shards reads these off each fills[] entry; our shard records name the
# primary value column differently, so translate rather than write blanks.
FILL_ALIASES = {"primary_value_col": "value_col", "primary_value": "proposed_value"}


def _fill_record(r: dict, ident: dict) -> dict:
    """Reshape a shard FILL record into the fills[] entry merge_deepsweep_shards expects."""
    f = {
        "sheet_row": r.get("sheet_row", ident.get("sheet_row", "")),
        "segment_name": r.get("segment_name", ident.get("segment_name", "")),
        "ref_col": r.get("ref_col", ""),
        "value_cols": r.get("value_cols", []) or [],
        "values": r.get("values", {}) or {},
        "proposed_refs": r.get("proposed_refs", []) or [],
        "verifications": r.get("verifications", []) or [],
        "class_out": r.get("class_out", "UNRESOLVED"),
        "tier": r.get("tier", ""),
        "independent": r.get("independent", False),
        "source_language": r.get("source_language", "en"),
        "researcher_notes": r.get("researcher_notes", ""),
    }
    for dest, src in FILL_ALIASES.items():
        v = r.get(dest, r.get(src))
        f[dest] = "" if v is None else v
    return f


def main() -> None:
    ref_dir, rows_dir = HERE / "ref_shards", HERE / "rows"
    for d in (ref_dir, rows_dir):
        d.mkdir(exist_ok=True)
        for stale in d.glob("P*.json"):
            stale.unlink()

    # ProjectID -> row identity, from the worklist (fills don't carry it).
    ident_of: dict[str, dict] = {}
    wl = json.loads((HERE / "worklist.json").read_text())
    for u in wl.get("units", []) or []:
        ident_of.setdefault(u["project_id"], {
            "project_id": u["project_id"],
            "pipeline_name": u.get("pipeline_name", ""),
            "sheet_row": u.get("sheet_row", ""),
            "wiki": u.get("wiki", ""),
            "segment_name": u.get("segment_name", ""),
        })

    # (pid, ref_col) the worklist actually owes a ref cell for. Anything outside this set
    # has no baseline record for merge_ref_shards to match, by construction.
    owed = {(u["project_id"], u["ref_col"]) for u in wl.get("units", []) or []}

    refs_by_pid: dict[str, list] = collections.defaultdict(list)
    fills_by_pid: dict[str, list] = collections.defaultdict(list)
    no_pid, batches, unreadable, unknown_pid, inferred_fill = [], [], [], set(), []
    for f in sorted((HERE / "shards").glob("batch_*.json")):
        # A shard being written by a still-running subagent parses as truncated JSON. Never
        # let that kill the split (the repo's own merge_qc.iter_shards takes the same line):
        # WARN, skip, and re-run once the agent lands. Crashing here would also be misread as
        # "the shard is corrupt" when it is merely half-written.
        try:
            doc = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            unreadable.append((f.name, str(e)))
            continue
        batches.append(f.name)
        for r in doc.get("resolutions", []) or []:
            pid = (r.get("project_id") or "").strip()
            if not pid:
                no_pid.append(r)
                continue
            if pid not in ident_of:
                unknown_pid.add(pid)
            rc = r.get("ref_col") or ""
            if rc.startswith("__"):                      # sentinel -> harvester
                refs_by_pid[pid].append(r)
            elif (r.get("kind") or "").upper() == "FILL":
                fills_by_pid[pid].append(_fill_record(r, ident_of.get(pid, {})))
            elif (pid, rc) not in owed:
                # STRUCTURAL, not tag-based. If the worklist owes no unit at (pid, ref_col)
                # then the value column is blank, so this IS a fill whatever the shard called
                # it -- and routing it to ref_shards/ means merge_ref_shards drops it for want
                # of a baseline. Three of Jiangxi's batch-02 records landed here: they say
                # "FILL target: LengthKnown is blank" in their own notes and carry no `kind`.
                # Trusting the tag would have lost them the moment one of them succeeded.
                inferred_fill.append((pid, rc))
                fills_by_pid[pid].append(_fill_record(r, ident_of.get(pid, {})))
            else:
                refs_by_pid[pid].append(r)

    sentinels = collections.Counter()
    for pid, recs in sorted(refs_by_pid.items()):
        (ref_dir / f"{pid}.json").write_text(
            json.dumps({"project_id": pid, "resolutions": recs},
                       ensure_ascii=False, indent=1))
        for r in recs:
            if (r.get("ref_col") or "").startswith("__"):
                sentinels[r["ref_col"]] += 1

    for pid, fills in sorted(fills_by_pid.items()):
        ident = ident_of.get(pid, {"project_id": pid})
        (rows_dir / f"{pid}.json").write_text(json.dumps({
            "project_id": pid,
            "pipeline_name": ident.get("pipeline_name", ""),
            "sheet_row": ident.get("sheet_row", ""),
            "wiki": ident.get("wiki", ""),
            # Sentinels stay in ref_shards/ for the harvester: merge_deepsweep_shards'
            # own validity path hardcodes __VALIDITY__ and would not carry __REDUNDANCY__.
            "validity": [],
            "fills": fills,
        }, ensure_ascii=False, indent=1))

    print(f"read {len(batches)} batch shard(s): {', '.join(batches)}")
    print(f"wrote {len(refs_by_pid)} ref shard(s) -> ref_shards/   "
          f"({sum(len(v) for v in refs_by_pid.values())} resolutions)")
    for k, n in sorted(sentinels.items()):
        print(f"    {k}: {n}")
    print(f"wrote {len(fills_by_pid)} row shard(s) -> rows/        "
          f"({sum(len(v) for v in fills_by_pid.values())} fills)")
    for pid, fills in sorted(fills_by_pid.items()):
        for f in fills:
            has = "value" if f.get("values") else "no value"
            print(f"    {pid} {f['ref_col']}: {f['class_out']}, {has}, "
                  f"{len(f['proposed_refs'])} ref(s)")
    if inferred_fill:
        print(f"  note {len(inferred_fill)} record(s) routed to rows/ as fills on the WORKLIST "
              f"(no owed unit at that ref_col), not on a `kind` tag:")
        for pid, rc in inferred_fill:
            print(f"    {pid} {rc}")
    for name, err in unreadable:
        print(f"  WARN unreadable shard {name}: {err} — SKIPPED (still being written? re-run later)")
    if unknown_pid:
        print(f"  WARN pid(s) not in worklist.json, identity written blank: "
              f"{', '.join(sorted(unknown_pid))}")
    if no_pid:
        # Never silently drop a record for want of a key — that is the failure mode
        # this whole script exists to prevent.
        print(f"  WARN {len(no_pid)} resolution(s) carry no project_id and were NOT written")


if __name__ == "__main__":
    main()
