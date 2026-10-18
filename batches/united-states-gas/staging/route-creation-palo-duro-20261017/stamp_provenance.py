"""Stamp a provenance object onto each candidate_routes/<PID>.geojson, so the lineage travels with the
geometry into the routes repo. Re-run after build_route_candidate.py rewrites a candidate.

Usage: python stamp_provenance.py   (from this directory)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACES = "batches/united-states-gas/staging/update-palo-duro-20261017/traces"
MAP_URL = "https://producersmidstream.com/wp-content/uploads/2026/03/PD_Pipeline_and_Residue_Header.jpg"
ROOT = {
    "type": "raster map trace",
    "name": "Producers Midstream map of the Palo Duro pipeline and the Residue Header (PD_Pipeline_and_Residue_Header.jpg, 600 by 805 px)",
    "url": MAP_URL,
    "local_copy": f"{TRACES}/map.jpg",
    "fetched": "2026-10-17",
    "georeference": f"{TRACES}/gcps_v3.json: order 2 polynomial on 78 control points (67 county corners confirmed by fitting the map's drawn county lines to Census cb_2018 county lines, register_counties.py; 11 Red River points on the Texas-Oklahoma line); town dots held out as check points",
    "cross_check": f"company asset map of August 2025 (Wayback 2025-08-22, {TRACES}/map_2025_assets_wayback20250822.jpg, check_2025_map.py)",
    "disclaimer": "company map at about 0.55 km per pixel, so traced RouteAccuracy is capped at medium",
}
PER_PID = {
    "P7861": {"derived_from": f"{TRACES}/residue_header_v3.geojson <- {TRACES}/trace_residue_header_v2.json (retrace.py)",
              "shape": "one continuous mainline, a 13 km spur north near the Texas-Oklahoma line, two stubs of about 1.5 km; joins P7862 at its north end",
              "agreement_with_prior_file_km": {"median": 0.47, "p90": 0.71, "max": 0.98}},
    "P7862": {"derived_from": f"{TRACES}/palo_duro_v3.geojson <- {TRACES}/trace_palo_duro_v2.json (retrace.py)",
              "shape": "centerline of the drawn line; north end shares a vertex with the P7861 mainline",
              "agreement_with_prior_file_km": {"median": 0.09, "p90": 0.30, "max": 0.88}},
}
recs = {r["project_id"]: r for r in json.load(open(HERE / "staged_resolutions.json"))["resolutions"]}
for pid, extra in PER_PID.items():
    p = HERE / "candidate_routes" / f"{pid}.geojson"
    fc = json.load(open(p)); r = recs[pid]
    for f in fc["features"]:
        f["properties"] = {"ProjectID": pid, "provenance": {
            "produced_by": "pipelines-researcher route-creation SOP section 8",
            "batch": "united-states-gas / route-creation-palo-duro-20261017",
            "method": "digitized (map trace); replacement of the prior route file",
            **extra, "root_source": ROOT, "georef": r.get("georef"),
            "route_accuracy_cap": r["suggested_route_accuracy"], "length_km": r["length_km"],
            "sheet_length_km": r["sheet_length_km"], "replacement": True,
            "qc_gate": "PASS" if r.get("qc_passed") else "FAIL (length vs the sheet; see researcher_notes)",
            "tools": ["retrace.py", "register_counties.py", "georef.py", "build_route_candidate.py"],
            "researcher_notes": r["researcher_notes"], "generated": "2026-10-17"}}
    p.write_text(json.dumps(fc, indent=1))
    print(pid, "stamped")
