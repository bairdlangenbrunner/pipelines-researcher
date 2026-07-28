#!/usr/bin/env python3
"""Seed the cancelled-review staged store from its briefs, so merge_ref_shards can run.

    python batches/libya-gas/staging/cancelled-review/build_baseline.py
    python scripts/merge_ref_shards.py --staging batches/libya-gas/staging/cancelled-review

The operating sweep's baseline came from `worklist.json`, built by the sweep
engine. This dir was created by hand for the two `cancelled` rows the sweeps
never covered (P1728, P3985), so its baseline is seeded from the same briefs the
research agents worked from — one record per ref unit, all `UNRESOLVED` until the
shards are merged over the top.

Every unit is `class_in: MISSING_REF` because neither row carried a working ref
in any of its paired ref cells.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
BRIEFS = OUT / "ref_shards" / "_briefs"

resolutions, pids = [], []
for bf in sorted(BRIEFS.glob("P*.json")):
    b = json.loads(bf.read_text())
    pids.append(b["project_id"])
    for u in b["units"]:
        resolutions.append({
            "project_id": b["project_id"],
            "sheet_row": u["sheet_row"],
            "pipeline_name": b["pipeline_name"],
            "segment_name": u.get("segment_name", ""),
            "ref_col": u["ref_col"],
            "value_cols": u["value_cols"],
            "primary_value_col": (u["value_cols"] or [""])[0],
            "values": u["values"],
            "primary_value": u["primary_value"],
            "current_ref": u.get("current_ref", ""),
            "class_in": "HAS_REF" if u.get("current_ref") else "MISSING_REF",
            "class_out": "UNRESOLVED",
            "proposed_refs": [],
            "verifications": [],
            "tier": "",
            "independent": False,
            "source_language": "",
            "researcher_notes": "",
        })

meta = {
    "commodity": "gas",
    "scope": {
        "csv": "GGIT_gas_snapshot_20260728.csv",
        "country": "Libya",
        "tracker": "gas",
        "statuses": ["cancelled"],
        "rows": len(pids),
        "project_ids": len(pids),
    },
    "mode": "sweep",
    "leg": "status-review",
    "n_units": len(resolutions),
    "seeded_from": "ref_shards/_briefs",
    "note": "The two Libya gas rows with Status=cancelled, neither covered by the "
            "operating ref-sweep nor the in-dev sweep. Status is itself under review "
            "here — see RESEARCH_PROTOCOL.md: absence of news is not evidence of "
            "cancellation.",
    "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
}

(OUT / "staged_resolutions.json").write_text(
    json.dumps({"meta": meta, "resolutions": resolutions}, indent=1) + "\n")
print(f"seeded {len(resolutions)} units across {len(pids)} rows ({', '.join(pids)})")
