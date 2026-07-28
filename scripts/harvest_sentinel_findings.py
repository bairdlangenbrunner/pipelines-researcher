#!/usr/bin/env python3
"""Fold research agents' `__REDUNDANCY__` / `__VALIDITY__` shard objects into the store.

    python scripts/harvest_sentinel_findings.py --staging <dir> [--staging <dir> ...]

`merge_ref_shards.py` matches each shard resolution to a baseline record by
(project_id, ref_col, sheet_row). A sentinel object — `ref_col` of
`__REDUNDANCY__` or `__VALIDITY__` — deliberately has no baseline record: it is
not a ref cell, it is the agent answering "is this row real / is it a
double-count?". So the merge WARNs and drops it, and the sourced verdict is
lost while the refs survive. That was worth a script rather than a manual copy:
these are the highest-value findings in the batch (three misplaced condensate
lines in Libya came from them), and losing them silently is the worst failure
mode available.

This appends each sentinel as a proper `__VALIDITY__` resolution — the same
shape `build_redundancy.py` writes — with `class_out: UNRESOLVED`, because a
validity record is read-and-flag only and never an applied edit. Idempotent:
re-running replaces previously harvested records rather than duplicating them.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SENTINELS = ("__REDUNDANCY__", "__VALIDITY__")
MARK = "harvested_from_shard"


def harvest(staging: Path) -> int:
    store_p = staging / "staged_resolutions.json"
    if not store_p.exists():
        print(f"  {staging.name}: no staged_resolutions.json — skipped")
        return 0
    store = json.loads(store_p.read_text())

    # Drop any prior harvest so a re-run is a replace, not an append.
    kept = [r for r in store["resolutions"] if not r.get(MARK)]
    dropped = len(store["resolutions"]) - len(kept)

    found = []
    for sf in sorted((staging / "ref_shards").glob("P*.json")):
        sh = json.loads(sf.read_text())
        for r in sh.get("resolutions", []):
            if r.get("ref_col") not in SENTINELS:
                continue
            found.append({
                "project_id": sh.get("project_id"),
                "sheet_row": r.get("sheet_row", 0),
                "pipeline_name": sh.get("pipeline_name", ""),
                "segment_name": "",
                "ref_col": "__VALIDITY__",
                "value_cols": [],
                "primary_value_col": "",
                "primary_value": "",
                "values": {},
                "current_ref": "",
                "class_in": "VALIDITY",
                # Read-and-flag only. An agent's redundancy verdict is evidence for
                # Baird's decision, never the decision itself.
                "class_out": "UNRESOLVED",
                "verdict": "concern",
                "concern_type": "redundancy"
                if r.get("ref_col") == "__REDUNDANCY__" else "validity",
                "recommendation": "Agent research verdict — see researcher_notes. "
                "Cross-check against the cluster-level recommendation in "
                "staging/redundancy/ before acting; where they differ, the cluster "
                "file is the adjudicated one.",
                "proposed_refs": r.get("proposed_refs", []),
                "verifications": r.get("verifications", []),
                "tier": r.get("tier", "n/a"),
                "independent": r.get("independent", False),
                "source_language": r.get("source_language", "en"),
                "researcher_notes": r.get("researcher_notes", ""),
                MARK: str(sf.name),
            })

    store["resolutions"] = kept + found
    store.setdefault("meta", {})["sentinel_findings_harvested"] = {
        "count": len(found),
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    store_p.write_text(json.dumps(store, indent=1) + "\n")
    note = f" (replaced {dropped})" if dropped else ""
    print(f"  {staging.name}: harvested {len(found)} sentinel finding(s){note} "
          f"-> {', '.join(sorted({f['project_id'] for f in found})) or '-'}")
    return len(found)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", action="append", required=True,
                    help="staging dir (repeatable)")
    args = ap.parse_args()
    total = sum(harvest(Path(s)) for s in args.staging)
    print(f"total: {total}")


if __name__ == "__main__":
    main()
