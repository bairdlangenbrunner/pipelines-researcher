#!/usr/bin/env python3
"""Split the Leg-3 worklist into four corridor briefs for the research fan-out.

    python batches/libya-gas/staging/qc/build_leg3_briefs.py

`build_qc_staging.py` emits `worklist.json` — 25 rows, 35 flags — as a flat list.
Dispatching 25 agents against it would be wasteful and would produce 25
independent answers to what are really four questions: who operates the Sirte
Basin grid, who operates the Mellitah/WLGP lines, when the Sirte lines were
commissioned, and which of (route, LengthKnownKm) is wrong on the coastal trunk.
Rows that share a source ladder are therefore briefed together, so one agent's
find on the corridor answers every row in it.

Each brief carries the row's flags verbatim plus the geometry measured in Leg 2
and the inline triage notes below, so the agent is answering a specific question
rather than re-deriving the flag.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BRIEFS = OUT / "rows" / "_briefs"

CLUSTERS = {
    "coastal-trunk": {
        "title": "Libya coastal gas trunk (Brega -> Benghazi / Khoms / Tripoli / Mellitah)",
        "pids": ["P0483", "P1789", "P1862", "P1863", "P1864", "P1865"],
        "context":
            "These rows are the western/coastal trunk. A separate redundancy pass "
            "(staging/redundancy, cluster A) has ALREADY flagged that P0483 'Libya "
            "Coastal Gas Pipeline' may be an aggregate that double-counts its member "
            "segments P1862/P1863/P1864/P1865, with P1789 a sixth overlapping row. "
            "Do NOT re-litigate that question — it is Baird's call and is already "
            "staged. Your job is narrower: the operator attribution and the "
            "route-vs-length disagreements. Note that four separate segments here "
            "have a drawn route 40-50% shorter than their stated length, which is a "
            "suspiciously consistent pattern: either the drawn routes are all "
            "straight-line schematics, or the stated lengths were derived from "
            "something other than the pipe. Find out which. The single most useful "
            "find would be a source giving the ACTUAL length of any one of these "
            "segments.",
    },
    "sirte-east": {
        "title": "Sirte Basin east — Intesar / Bu-Attifel / Waha / Farigh feeders",
        "pids": ["P1856", "P1857", "P1858", "P1860", "P1861"],
        "context":
            "Zueitina Oil Co, Mellitah Oil & Gas and Waha Oil Co operate here and the "
            "operators tab already names them for these rows — but with NO "
            "`Operator [ref]`. Two specific things to chase: (1) P1860 'Waha-Nasser' "
            "and P1861 'Farigh-Intesar' both carry LengthKnownKm = 177.00 exactly, "
            "with blank endpoints and RouteAccuracy=low on both — an identical length "
            "on two different pipelines reads as a copy-paste, so find each line's "
            "real length independently. (2) P1858's 131.96 km is SOURCED (OPEC ASB "
            "lists Bu-Attifel/Intesar 34in at that length) while its drawn route is a "
            "91 km straight line — that is a ROUTE problem, not a length problem, so "
            "do not propose changing the length; confirm the ASB figure and say so.",
    },
    "sirte-grid": {
        "title": "Sirte Basin grid — Sirte Oil Company lines around Brega",
        "pids": ["P1866", "P1867", "P1868", "P1869", "P1870", "P1871", "P1872", "P1873"],
        "context":
            "Eight Sirte-Basin rows, mostly needing a commissioning year and an "
            "operator. gem.wiki says 'Sirte Oil' for several — treat that as a lead "
            "and find an independent source (Sirte Oil Company's own site, NOC, OPEC "
            "ASB, trade press). Sirte Oil Company was formed in 1981 out of Esso "
            "Standard Libya, so a pipeline commissioned in the 1960s-70s was built by "
            "a predecessor and is OPERATED by Sirte Oil today — do not read a 1981 "
            "corporate date as a commissioning date. P1866 'Nasser-Brega' is already "
            "flagged separately (staging/redundancy cluster F) as sharing its "
            "identity with GOIT P0599 and as carrying a wrong 277 km length against a "
            "sourced ~172 km; its drawn route measures 174 km, which corroborates the "
            "~172. For P1866 you only need to nail the commissioning year and the "
            "length citation — the duplicate question is already staged.",
    },
    "mellitah-wlgp": {
        "title": "Mellitah complex / Western Libya Gas Project / Bahr Assalam offshore",
        "pids": ["P0482", "P0484", "P6713", "P6715", "P6716", "P7617"],
        "context":
            "Mellitah Oil & Gas (the NOC-Eni 50:50 JV) is the operator across this "
            "group; the operators tab is blank for all six. Three notes so you do not "
            "waste effort: (1) P0482's flag says 'sheet Capacity is blank but wiki "
            "shows 30/36 inches' — that wiki value is a DIAMETER string, not a "
            "capacity, so the flag is a wiki-parse artifact. Do not stage a capacity "
            "from it. If you can source P0482's real diameter and/or capacity, do "
            "that instead and say what you found. (2) P0484's LengthKnownKm of 5246 "
            "is a known decimal-shift error against a drawn route of 526 km and is "
            "already staged in staging/redundancy cluster B — you only need the "
            "operator. (3) P6716 and P7617 are two SEGMENTS of one DP3-DP4-Sabratha "
            "pipeline; the route file holds the whole line (66 km) while P6716's row "
            "is just the 8.5 km DP3-DP4 leg, so its length_ratio flag is a "
            "segment-vs-network granularity artifact, not an error. Confirm the "
            "segment lengths if you can, but do not 'fix' 8.5 km to 66 km.",
    },
}

# Inline triage from the drawn geometry (Leg 2 measured these; recomputed per part here).
GEOM = {
    "P0484": "drawn route 526.6 km, Wafa gas field (10.024E,28.889N) -> Mellitah (12.238E,32.854N)",
    "P1789": "drawn route 249.2 km, (15.041E,32.210N) -> (12.575E,32.787N) — i.e. the WHOLE "
             "Misrata/Khoms-to-Mellitah coast, ~= P1864 (105 km) + P1865 (117 km) end to end, "
             "against a stated 25 km",
    "P1856": "drawn route 223.0 km, Intesar (20.987E,28.926N) -> Brega (19.591E,30.409N)",
    "P1858": "drawn route 91.4 km, Bu-Attifel (22.068E,28.880N) -> Intesar (21.130E,28.885N) — "
             "essentially a straight line, i.e. a schematic",
    "P1860": "drawn route 69.9 km, Waha (19.923E,28.302N) -> Nasser (19.770E,28.916N)",
    "P1861": "drawn route only 13.3 km, (21.123E,28.887N) -> (20.994E,28.928N) — and its start "
             "point is within ~10 m of where P1858's route ENDS, so the drawn line is a stub "
             "between P1858's endpoint and Intesar, nowhere near the Farigh field",
    "P1862": "drawn route 225.9 km, Brega (19.597E,30.416N) -> Benghazi (20.056E,32.077N)",
    "P1864": "drawn route 105.2 km, Khoms (14.447E,32.518N) -> Tripoli (13.425E,32.766N)",
    "P1865": "drawn route 116.6 km, Tripoli (13.425E,32.766N) -> Mellitah (12.205E,32.876N)",
    "P1866": "drawn route 174.0 km, Nasser (19.770E,28.916N) -> Brega (19.609E,30.410N) — this "
             "corroborates the ~172 km figure, not the sheet's 277 km",
    "P6716": "route file covers the whole DP3-DP4-Sabratha line, 65.8 km "
             "(13.190E,32.860N -> 12.495E,32.806N); the row is only the DP3-DP4 segment",
}

FIELDS = ["PipelineName", "SegmentName", "Status", "StartYear1", "LengthKnownKm",
          "Diameter", "Capacity", "CapacityUnits", "StartLocation", "EndLocation",
          "Owner", "RouteAccuracy", "Wiki"]


def main() -> None:
    BRIEFS.mkdir(parents=True, exist_ok=True)
    wl = json.loads((OUT / "worklist.json").read_text())
    by_pid = {r["project_id"]: r for r in wl["rows"]}

    df = pd.read_csv(ROOT / "data/GGIT_gas_snapshot_20260728.csv", header=2,
                     low_memory=False)
    df = df[df["CountriesOrAreas"].astype(str).str.contains("Libya", na=False)]
    ops = pd.read_csv(ROOT / "data/GEM_operators_owners_snapshot_20260728.csv",
                      header=1, low_memory=False)
    ops = ops.set_index("ProjectID")

    assigned = set()
    for slug, spec in CLUSTERS.items():
        rows = []
        for pid in spec["pids"]:
            assigned.add(pid)
            wr = by_pid[pid]
            srow = df[df["ProjectID"] == pid].iloc[0]
            cur = {f: ("" if pd.isna(srow.get(f)) else str(srow.get(f)))
                   for f in FIELDS if f in df.columns}
            orow = ops.loc[pid] if pid in ops.index else None
            rows.append({
                "project_id": pid,
                "sheet_row": wr["sheet_row"],
                "pipeline_name": wr["pipeline_name"],
                "wiki": wr["wiki"],
                "status": wr["status"],
                "flags": wr["flags"],
                "current_sheet_values": cur,
                "current_operator": ("" if orow is None or pd.isna(orow.get("Operator"))
                                     else str(orow.get("Operator"))),
                "current_operator_ref": ("" if orow is None
                                         or pd.isna(orow.get("Operator [ref]"))
                                         else str(orow.get("Operator [ref]"))),
                "drawn_geometry": GEOM.get(pid, "no route drawn / not flagged"),
            })
        payload = {
            "cluster": slug,
            "title": spec["title"],
            "context": spec["context"],
            "protocol": "batches/libya-gas/staging/qc/RESEARCH_PROTOCOL.md",
            "write_shards_to": "batches/libya-gas/staging/qc/rows/<PID>.json",
            "n_rows": len(rows),
            "n_flags": sum(len(r["flags"]) for r in rows),
            "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "rows": rows,
        }
        (BRIEFS / f"{slug}.json").write_text(json.dumps(payload, indent=1) + "\n")
        print(f"  {slug}: {len(rows)} rows, {payload['n_flags']} flags")

    missing = set(by_pid) - assigned
    if missing:
        raise SystemExit(f"UNASSIGNED worklist rows: {sorted(missing)}")
    print(f"total: {len(assigned)} rows across {len(CLUSTERS)} briefs "
          f"(worklist has {len(by_pid)})")


if __name__ == "__main__":
    main()
