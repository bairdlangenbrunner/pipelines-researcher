#!/usr/bin/env python3
"""Append ROUTE_PARTIAL records for the Egypt gas rows that stay unresolvable.

A partial is a row we deliberately did NOT draw: at 'very low' the bar is a sourced
anchor PAIR, and these rows have at most one. Each carries the reason, so the packet
states its own coverage instead of leaving the row silently absent.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).parent
REASONS = json.loads((HERE / "partials.json").read_text())
REASONS.pop("P7326", None)  # oil; already carries a null placeholder in the routes repo

units = {u["project_id"]: u for u in json.loads((HERE / "worklist.json").read_text())["units"]}
staged = json.loads((HERE / "staged_resolutions.json").read_text())
have = {r["project_id"] for r in staged["resolutions"]}

added = 0
for pid, reason in REASONS.items():
    if pid in have:
        continue
    u = units.get(pid, {})
    staged["resolutions"].append({
        "project_id": pid,
        "sheet_row": str((u.get("sheet_rows") or [""])[0]),
        "pipeline_name": u.get("pipeline_name", ""),
        "segment_name": "; ".join(u.get("segment_names") or []),
        "ref_col": "__ROUTE__",
        "class_in": "ROUTE",
        "class_out": "ROUTE_PARTIAL",
        "value_cols": [], "primary_value_col": None, "values": {}, "primary_value": "",
        "current_ref": u.get("current_route_ref", ""),
        "method": "", "geometry_file": "",
        "source": {"name": "", "url": "", "license": "", "odbl": False, "fetched_utc": ""},
        "georef": None, "replacement": False, "geometry_signals": {}, "qc_passed": False,
        "packet": "",
        "length_km": None,
        "sheet_length_km": u.get("sheet_length_km"),
        "length_ratio": None,
        "current_route_accuracy": u.get("current_route_accuracy", "no route"),
        "suggested_route_accuracy": "",
        "start_name": "", "start_lon": None, "start_lat": None,
        "end_name": "", "end_lon": None, "end_lat": None,
        "proposed_refs": [], "verifications": [], "tier": "", "independent": False,
        "source_language": "en",
        "researcher_notes": "NOT DRAWN, and not for want of trying — " + reason,
    })
    added += 1

(HERE / "staged_resolutions.json").write_text(json.dumps(staged, indent=1) + "\n")
print(f"appended {added} ROUTE_PARTIAL records; total {len(staged['resolutions'])}")
