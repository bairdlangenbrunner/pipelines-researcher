#!/usr/bin/env python3
"""SUPERSEDED 2026-09-03 by scripts/build_leg3_briefs.py (generic --staging/--groups
emitter). This copy uses the older CLUSTERS/FIELDS/GEOM shape, which does NOT load
through the promoted script. Kept for the run record only.

Split the Leg-3 worklist into ten corridor briefs for the research fan-out.

    python batches/pakistan-gas/staging/qc/build_leg3_briefs.py

`build_qc_staging.py` emits `worklist.json` — 50 rows, 50 flags — as a flat list,
but the flags collapse into three questions, not fifty: 35 rows want a
commissioning year, 13 have a drawn route that disagrees with `LengthKnown`, and 2
are transnational routes whose endpoint lands outside the row's start/end
countries. The 35 commissioning-year rows in particular are ONE research question
(when did SNGPL/SSGC commission its transmission lines?) with one source ladder —
the escalation memo on the July-2023 map bulk-load is explicit that dispatching an
agent per row is what fails here. Rows that share a source ladder are therefore
briefed together, so one agent's find on the corridor answers every row in it.

Each brief carries the row's flags verbatim plus its current sheet values and the
geometry measured in Leg 2, so the agent answers a specific question rather than
re-deriving the flag.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BRIEFS = OUT / "rows" / "_briefs"

_MAP_COHORT = (
    "Every row in this cluster is part of the July-2023 map bulk-load: its only refs "
    "are SNGPL's transmission-map JPG and PEPL's Energy-Map PDF, neither of which "
    "carries commissioning dates. So the sheet's own citation cannot answer your "
    "question and you must find a NEW source. Annual reports are the ladder: SNGPL "
    "publishes transmission additions FY-by-FY, and OGRA's licence and State of the "
    "Industry reports name segments."
)

CLUSTERS = {
    "ssgc-sindh": {
        "title": "SSGC Sindh transmission — Kadanwari/Jamshoro/Dadu to Karachi",
        "pids": ["P4015", "P4016", "P4020"],
        "context":
            "The three SSGC-owned rows needing a commissioning year. SSGC (Sui Southern "
            "Gas Company) publishes annual reports and an OGRA-regulated transmission "
            "network description; its Karachi-bound trunk from the Sindh fields is much "
            "better documented than SNGPL's Punjab distribution-region lines. The "
            "Kadanwari and Bajara/Dadu lines tie to specific field-development dates — "
            "but remember a FIELD's first-production year is not automatically the "
            "PIPELINE's commissioning year. P4016 is a LOOPLINE (Sindh University to "
            "FJFC offtake), so its date is a capacity-expansion date, likely much later "
            "than the original line it parallels.",
    },
    "sngpl-sindh-feeders": {
        "title": "SNGPL Sindh/Balochistan feeders — Sawan, Qadirpur, Sui, Kot Addu",
        "pids": ["P4079", "P4087", "P4090", "P4101", "P4102"],
        "context":
            "These are the SNGPL lines that pick gas up from the big Sindh fields and "
            "carry it north. Unlike the Punjab distribution lines these ARE documented: "
            "Sawan (OMV, on stream 2003), Qadirpur (OGDCL) and Sui (PPL) all have "
            "well-reported development histories, and the Sui-Multan line (P4090) is "
            "one of the oldest and most-cited pipelines in Pakistan — the sweep already "
            "confirmed its existence off SNGPL's own province-wise transmission "
            "breakdown, so chase that same document for a date. P4101 'SV1-QV1' and "
            "P4079 'Sawan-Qadirpur' share both endpoints (Sawan -> Qadirpur) and may be "
            "the same physical line under a valve-station label vs a place label; if "
            "your sources say so, raise it as validity concern_type=duplicate rather "
            "than forcing two separate dates.",
    },
    "rlng-punjab": {
        "title": "SNGPL RLNG project lines — Qadirpur Ran / Mian Channu / Sahiwal",
        "pids": ["P4099", "P4100", "P4105"],
        "context":
            "The best-documented cluster in this leg. These are the 42-inch RLNG "
            "(re-gasified LNG) transmission lines SNGPL built to move imported LNG from "
            "the Karachi terminals up-country — a major national project with ECNEC "
            "approvals, contract awards and completion reporting in Business Recorder, "
            "Dawn and The News, plus SNGPL annual-report coverage. Dates should be "
            "findable to the year and possibly the month. NOTE: the deep sweep already "
            "flagged P4105 'AV29-Sahiwal' as very likely the SAME pipe as P4099 "
            "'AV29-N2' + P4100 'N2-Sahiwal' (Qadirpur Ran -> Mian Channu -> Sahiwal, "
            "i.e. an end-to-end row sitting alongside its own two segments). Do NOT "
            "re-litigate that — it is staged. But if your sources happen to settle it, "
            "note it, and be careful not to give the aggregate row a date that really "
            "belongs to one segment.",
    },
    "punjab-central": {
        "title": "SNGPL central Punjab — Sidhnai/Faisalabad/Sahiwal/Lahore corridor",
        "pids": ["P4106", "P4107", "P4108", "P4124", "P4133", "P4174"],
        "context":
            _MAP_COHORT +
            " P4106 and P4107 are 'Sidhnai-Faisalabad Gas Pipeline' and '... II' — same "
            "endpoints, so II is a loop/second line and its date must be LATER than I's; "
            "if you can only date one, say which and reason about the other rather than "
            "copying the year across. Same pattern for P4108 'Sahiwal-Lahore I'. The "
            "sweep flagged P4106 and P4124 concern_type=existence purely because no text "
            "source names them — treat that as 'undocumented', not 'fake', and do not "
            "stage a deletion.",
    },
    "punjab-north": {
        "title": "SNGPL northern Punjab — Faisalabad/Shahdara/Sheikhupura/Gujranwala/Gujrat",
        "pids": ["P4135", "P4136", "P4137", "P4138", "P4139", "P4141", "P4158", "P4159"],
        "context":
            _MAP_COHORT +
            " The densest and least-documented part of the cohort — five of these eight "
            "rows carry an existence flag from the sweep for exactly that reason. Two "
            "leads that are more promising than generic search: (1) P4138 feeds the "
            "**Nandipur Power Plant**, a heavily-reported public project with its own "
            "conversion-to-gas history, so the pipeline serving it should be datable "
            "from power-sector reporting; (2) 'MP 59.91' in P4138/P4141 is an SNGPL "
            "milepost reference, which means these rows came off an engineering "
            "document — if you can find that document class (SNGPL tender, OGRA licence "
            "schedule), it likely names several of these lines at once. That find would "
            "be worth more than any individual date.",
    },
    "potohar-kp": {
        "title": "SNGPL Potohar + Khyber Pakhtunkhwa — Dandot/Dhulian/Kohat/Nowshera/Swat",
        "pids": ["P4161", "P4162", "P4164", "P4165", "P4176", "P4177", "P4178",
                 "P4179", "P4181", "P4182"],
        "context":
            _MAP_COHORT +
            " The northern extremity of SNGPL's system, tied to the old Potohar-basin "
            "fields (Dhulian, Meyal, Dakhni) — some of the OLDEST gas infrastructure in "
            "Pakistan, which cuts both ways: the fields are historically documented "
            "(Dhulian dates to the 1930s-40s as an OIL field), but a field's age tells "
            "you nothing about when SNGPL laid a gas line to it. Be strict about that "
            "distinction; the sweep already flagged P4164 for exactly this confusion. "
            "P4161/P4162 are 'Dandot-Gali Jagir-Wah I' and 'II' (same endpoints, so II "
            "is later). P4181 'Sakhakot-Swat' is flagged as a possible duplicate of "
            "P5486 'Mardan-Swat' and P4179 covers Nowshera-Mardan-Takht Bhai-Sakhakot — "
            "i.e. three rows over one Nowshera->Swat corridor. Gas supply to Swat/Malakand "
            "was a politically-reported development project, so news archives may date it.",
    },
    "length-sindh": {
        "title": "Length-vs-route disagreements — Sindh trunk + Iran-Pakistan",
        "pids": ["P0452", "P4014", "P4017", "P4021", "P4074"],
        "context":
            "Five rows where the drawn route is SHORTER than the stated length (ratios "
            "0.33-0.74). Pakistan's routes are overwhelmingly RouteAccuracy='very low "
            "(straight line/schematic)', so the default explanation is a schematic line "
            "that undershoots real pipe, NOT a wrong length — your job is to find the "
            "SOURCED length and say which side the evidence supports. Specifics: "
            "P0452 Iran-Pakistan is the IP/'Peace' pipeline, extensively reported, and "
            "the 2775 km figure is likely the WHOLE Iran+Pakistan project while the "
            "drawn 1781 km may be only part — check what extent GEM's row covers. "
            "P4074 Kandhkot has the worst ratio (18 km drawn vs 55.23 km stated) and "
            "the sweep separately flagged its Owner as questionable (SSGC vs PPL). "
            "P4017 HQ2-Tando Adam already has two independent official documents "
            "disagreeing with GEM's length — find them and resolve, don't re-derive.",
    },
    "length-qadirpur": {
        "title": "Length-vs-route — Qadirpur loops and Dhodak-Kot Addu",
        "pids": ["P4088", "P4089", "P4104"],
        "context":
            "P4088 'Qadirpur Gas Loopline' and P4089 'Qadirpur Gas Pipeline (LNG Phase "
            "II)' BOTH carry LengthKnown = 53.14 km exactly while their drawn routes "
            "measure 93 km and 107 km — an identical length on two different rows is a "
            "copy-paste signature, and both routes overshooting it in the same direction "
            "says the 53.14 is the suspect number, not the geometry. Find each line's "
            "real length independently. The sweep separately found an independent "
            "technical source giving P4088 as 44 MILES (~71 km) — chase that. P4104 "
            "Dhodak-Kot Addu is the reverse case (49 km drawn vs 77.79 km stated) and "
            "the sweep wants its Diameter changed from '16' to a mixed '12, 16'; "
            "confirm or refute that while you are in the sources.",
    },
    "length-punjab-kp": {
        "title": "Length-vs-route — Punjab and KP segments",
        "pids": ["P4129", "P4140", "P4170", "P4175", "P5486"],
        "context":
            "Mixed directions here, which matters. P4129 (122 km drawn vs 90.82 stated), "
            "P4140 (152 vs 76.67) and P4170 (73 vs 50.41) all have routes LONGER than "
            "the stated length — the classic signature of a geojson that covers a whole "
            "line while the row is one segment of it. Check whether each row is a "
            "segment of a longer named line before proposing any length change; that is "
            "a granularity artifact, not an error. P4175 Haripur-Mansehra (46 vs 70.53) "
            "and P5486 Mardan-Swat (73 vs 104.89) run the other way. P5486 is also "
            "flagged as a possible duplicate of P4181 Sakhakot-Swat — do not re-litigate "
            "that, but a sourced as-built length would help settle it.",
    },
    "transnational-endpoints": {
        "title": "Transnational routes whose endpoint lands outside the row's countries",
        "pids": ["P0451", "P0766"],
        "context":
            "Two megaproject rows, both CANCELLED or in-development and both already "
            "researched in the annual/cancelled-review packets — so do NOT re-research "
            "their status, ownership or cost. The narrow question is geometric extent. "
            "P0451 Iran-Pakistan-India: start/end columns say Iran -> India, but the "
            "drawn route ends at Karachi (24.916, 67.039). P0766 TAPI: the route ends in "
            "Afghanistan though the row is not an Afghanistan-terminating line. In both "
            "cases the likely answer is that the drawn geometry covers a different extent "
            "than GEM's start/end columns claim — decide which is wrong and recommend "
            "the fix as a validity finding. Do NOT propose new coordinates and do not "
            "touch the routes repo.",
    },
}

FIELDS = ["PipelineName", "SegmentName", "Status", "StartYear1", "LengthKnown",
          "Diameter", "Capacity", "CapacityUnits", "StartLocation", "EndLocation",
          "StartCountryOrArea", "EndCountryOrArea", "Owner", "RouteAccuracy",
          "RouteType", "Wiki"]


def main() -> None:
    BRIEFS.mkdir(parents=True, exist_ok=True)
    wl = json.loads((OUT / "worklist.json").read_text())
    by_pid = {r["project_id"]: r for r in wl["rows"]}

    import glob
    csv = sorted(glob.glob(str(ROOT / "data/GGIT_gas_snapshot_*.csv")))[-1]
    df = pd.read_csv(csv, header=2, low_memory=False)
    df = df[df["CountriesOrAreas"].astype(str).str.contains("Pakistan", na=False)]

    assigned = set()
    for slug, spec in CLUSTERS.items():
        rows = []
        for pid in spec["pids"]:
            assigned.add(pid)
            wr = by_pid[pid]
            srow = df[df["ProjectID"] == pid].iloc[0]
            cur = {f: ("" if pd.isna(srow.get(f)) else str(srow.get(f)))
                   for f in FIELDS if f in df.columns}
            rows.append({
                "project_id": pid,
                "sheet_row": wr["sheet_row"],
                "pipeline_name": wr["pipeline_name"],
                "wiki": wr["wiki"],
                "status": wr["status"],
                "flags": wr["flags"],
                "current_sheet_values": cur,
            })
        payload = {
            "cluster": slug,
            "title": spec["title"],
            "context": spec["context"],
            "protocol": "batches/pakistan-gas/staging/qc/RESEARCH_PROTOCOL.md",
            "write_shards_to": "batches/pakistan-gas/staging/qc/rows/<PID>.json",
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
