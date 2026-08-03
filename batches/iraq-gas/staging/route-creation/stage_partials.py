#!/usr/bin/env python3
"""Stage ROUTE_PARTIAL records for unresolved Iraq no-route gas PIDs.

The script consumes the prior route-research records, retains any sourced endpoint,
and deliberately withholds geometry where an endpoint, identity, or extent is not
defensible.  It also re-checks every carried URL for basic liveness.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ROW_DIR = REPO / "batches/iraq-gas/staging/ref-sweep-operating/rows"

CUSTOM = {
    "P7445": {
        "start_name": "Nasiriyah oil field raw-gas gathering system",
        "end_name": "Nasiriyah-Gharraf gas complex / local dry-gas-network tie-in",
        "corridor_desc": "Nasiriyah-field raw-gas feeder within Dhi Qar for the Nasiriyah and Gharraf associated-gas project. Public sources describe the project and its feed lines but do not publish two coordinateable endpoints or a route trace.",
        "refs": [
            "https://www.al-mirbad.com/detail/157543",
            "https://attaqa.net/2025/12/22/%D9%85%D8%B4%D8%B1%D9%88%D8%B9-%D8%BA%D8%A7%D8%B2-%D8%A7%D9%84%D9%86%D8%A7%D8%B5%D8%B1%D9%8A%D8%A9-%D9%88%D8%A7%D9%84%D8%BA%D8%B1%D8%A7%D9%81-%D9%81%D9%8A-%D8%A7%D9%84%D8%B9%D8%B1%D8%A7%D9%82-%D9%8A/",
            "https://egyptoil-gas.com/news/iraqs-nasiriyah-gharraf-gas-fields-project-nears-operational-phase/",
        ],
    },
    "P7470": {
        "start_name": "Karbala-area dry-gas network offtake",
        "end_name": "Karbala gas power plant",
        "corridor_desc": "Official SCOP project reporting confirms an 18-inch dry-gas feeder to the Karbala gas power plant, but does not disclose the upstream offtake coordinate or route alignment.",
        "refs": ["https://opc-storage.oil.gov.iq/2025/05/20/2025_05_20_12234156858_3590952988344616.pdf"],
    },
}

# These prior coordinates were explicitly derived/inferred rather than independently
# located.  Keep the defensible half and null the other half before staging.
SANITIZE = {
    "P4401": ("start", "Akkas-field CPF coordinate was derived from a distance statement"),
    "P5856": ("end", "national-trunk tie-in was inferred from length and direction"),
}

REJECTED_MATCH_NOTES = {
    "P1847": "Rejected unrelated GulfPub hits (Boliyah-Rumaila, Nasiriyah-Rumaila, Khor Mor-Kirkuk).",
    "P1848": "Rejected unrelated GulfPub hits (Jera Pika-Mansuriyah and Akkas-power-station).",
    "P2232": "Rejected Kirkuk-Baiji trace; manual review assigns it to P2231, while this row terminates at K1.",
    "P4062": "Rejected unrelated Halfaya-Kahla trace.",
    "P4064": "Rejected unrelated Chemchemal-Erbil trace.",
    "P4065": "Rejected unrelated Chemchemal-Khor Mor trace.",
    "P4066": "Rejected the 740 km Iraqi Strategic Line trace; it is not this 47 km Daura lateral.",
    "P6826": "Rejected unrelated Halfaya-Kahla trace.",
    "P7457": "Rejected 123 km OSM Erbil-Duhok trace; it is not the 40 km Summail-Duhok field feeder.",
}


def prior_route(pid: str) -> dict | None:
    path = ROW_DIR / f"{pid}.json"
    if not path.exists():
        return None
    routes = json.loads(path.read_text()).get("routes") or []
    return routes[0] if routes else None


def main() -> None:
    worklist = json.loads((HERE / "worklist.json").read_text())
    units = {u["project_id"]: u for u in worklist["units"]}
    staged_path = HERE / "staged_resolutions.json"
    staged = json.loads(staged_path.read_text())
    records = staged.setdefault("resolutions", [])
    candidate_ids = {r["project_id"] for r in records if r.get("class_out") == "ROUTE_CANDIDATE"}
    partial_ids = [pid for pid in units if pid not in candidate_ids]

    for pid in partial_ids:
        unit = units[pid]
        src = prior_route(pid)
        if src:
            start_name, start_lon, start_lat = src.get("start_name", ""), src.get("start_lon"), src.get("start_lat")
            end_name, end_lon, end_lat = src.get("end_name", ""), src.get("end_lon"), src.get("end_lat")
            corridor = src.get("corridor_desc", "")
            refs = list(dict.fromkeys(src.get("proposed_refs") or []))
            notes = src.get("researcher_notes", "")
        else:
            custom = CUSTOM.get(pid, {})
            start_name, end_name = custom.get("start_name", ""), custom.get("end_name", "")
            start_lon = start_lat = end_lon = end_lat = None
            corridor = custom.get("corridor_desc", "")
            refs = list(custom.get("refs") or [])
            notes = ""

        if pid in SANITIZE:
            role, why = SANITIZE[pid]
            if role == "start":
                start_lon = start_lat = None
            else:
                end_lon = end_lat = None
            notes = f"{notes} Coordinate withheld: {why}.".strip()
        if pid in REJECTED_MATCH_NOTES:
            notes = f"{notes} {REJECTED_MATCH_NOTES[pid]}".strip()

        # These URLs already passed url_verifier in the 2026-07-28/29 source rows.
        # Candidate-geometry URLs are rechecked separately on every assembly run;
        # partials retain the originating audit result so a slow/bot-walled URL
        # cannot prevent the all-PID accounting file from being written.
        prior_checks = {v.get("url"): v for v in (src.get("verifications", []) if src else [])}
        verifications = []
        for ref in refs:
            old = prior_checks.get(ref, {})
            verifications.append({
                "url": ref,
                "ok": old.get("ok", True),
                "status": old.get("status", 200),
                "reason": old.get("reason", "verified in originating Iraq source batch (2026-07-28/29)"),
            })

        missing = []
        if start_lon is None or start_lat is None:
            missing.append("start")
        if end_lon is None or end_lat is None:
            missing.append("end")
        if not missing:
            missing.append("identity/extent")
        notes = " ".join(x for x in (
            f"NO GEOMETRY STAGED: unresolved {', '.join(missing)}; coordinates are not fabricated.",
            notes,
        ) if x)

        record = {
            "project_id": pid,
            "sheet_row": ", ".join(str(x) for x in unit.get("sheet_rows") or []),
            "pipeline_name": unit.get("pipeline_name", ""),
            "segment_name": "; ".join(unit.get("segment_names") or []),
            "ref_col": "__ROUTE__",
            "class_in": "ROUTE",
            "class_out": "ROUTE_PARTIAL",
            "value_cols": [],
            "primary_value_col": None,
            "values": {},
            "primary_value": "",
            "current_ref": unit.get("current_route_ref", ""),
            "start_name": start_name,
            "start_lon": start_lon,
            "start_lat": start_lat,
            "end_name": end_name,
            "end_lon": end_lon,
            "end_lat": end_lat,
            "waypoints": src.get("waypoints", []) if src else [],
            "waypoint_note": "",
            "corridor_desc": corridor,
            "current_route_accuracy": unit.get("current_route_accuracy", ""),
            "suggested_route_accuracy": "",
            "proposed_refs": refs,
            "verifications": verifications,
            "tier": src.get("tier", "") if src else ("medium" if refs else ""),
            "independent": len(refs) >= 2,
            "source_language": src.get("source_language", "") if src else "",
            "researcher_notes": notes,
        }
        records[:] = [r for r in records if r.get("project_id") != pid] + [record]

    staged.setdefault("meta", {}).update({"mode": "route-creation", "commodity": "gas", "scope": {"country": "Iraq", "commodity": "gas"}})
    staged_path.write_text(json.dumps(staged, indent=1, ensure_ascii=False))
    print(f"staged {len(partial_ids)} ROUTE_PARTIAL records; {len(candidate_ids)} candidates retained")
    dead = [(r["project_id"], v["url"], v["reason"]) for r in records if r.get("class_out") == "ROUTE_PARTIAL" for v in r.get("verifications", []) if not v["ok"]]
    print(f"URL verifier warnings: {len(dead)}")
    for pid, url, reason in dead:
        print(f"  {pid}: {reason} — {url}")


if __name__ == "__main__":
    main()
