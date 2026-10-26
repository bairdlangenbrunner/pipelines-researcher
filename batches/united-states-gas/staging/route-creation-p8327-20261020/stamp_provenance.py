"""Stamp a provenance object onto candidate_routes/P8327.geojson, so the lineage travels with the
geometry into the routes repo. Re-run after build_route_candidate.py rewrites the candidate.

Usage: python stamp_provenance.py   (from this directory)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACES = "batches/united-states-gas/staging/route-creation-p8327-20261020/traces"
MAR = "https://elibrary.ferc.gov/eLibrary/filedownload?fileid=D5DC66BB-2D81-CDC1-9DA6-9CE8E2400000"
ROOT = {
    "type": "GeoPDF vector path",
    "name": "WBI Energy, Bakken East Pipeline Project draft Resource Reports 1 and 10, FERC docket PF26-4, accession 20260313-5242, filed 2026-03-13; Figure 10.6.1-5 James River Ellendale Lateral Route Alternatives (1:43,290, dated 2026-02-20), PDF page 685",
    "url": MAR,
    "local_copy": f"{TRACES}/wbi-bakken-east-rr10-march2026-fig-10.6.1-5-p685.pdf",
    "fetched": "2026-10-20",
    "georeference": "the page's own /VP /Measure dictionary (GPTS corners, NAD 1983 StatePlane North Dakota South FIPS 3302 Feet); affine fit of the PDF frame to the four corners, residual 0.424 ft",
    "drawing": "page drawing 64, the dashed line (proposed Ellendale Lateral with Alternative 2 incorporated); drawing 63, Alternative 1, not used",
}
p = HERE / "candidate_routes" / "P8327.geojson"
r = {x["project_id"]: x for x in json.load(open(HERE / "staged_resolutions.json"))["resolutions"]}["P8327"]
fc = json.load(open(p))
for f in fc["features"]:
    f["properties"] = {"ProjectID": "P8327", "provenance": {
        "produced_by": "pipelines-researcher route-creation SOP section 8",
        "batch": "united-states-gas / route-creation-p8327-20261020",
        "method": "vector path read from the sponsor's GeoPDF (no hand tracing)",
        "derived_from": f"{TRACES}/ellendale_alt2.geojson <- {TRACES}/extract_geopdf.py (page 685, drawing 64)",
        "checks": {"length_mi": 81.62, "filing_length_mi": 81.6,
                   "milepost_circles_45_to_54_offset_m": "0 to 1",
                   "county_line_crossings_mi": {"LaMoure": [29.98, 29.7], "Dickey": [62.11, 62.1]},
                   "script": f"{TRACES}/check_route.py"},
        "root_source": ROOT, "route_accuracy_cap": r["suggested_route_accuracy"], "length_km": r["length_km"],
        "sheet_length_km": r["sheet_length_km"], "replacement": False,
        "qc_gate": "PASS" if r.get("qc_passed") else "FAIL",
        "planned_route": "planned alignment of a lateral dropped from the project in April 2026; never built",
        "tools": ["extract_geopdf.py", "check_route.py", "build_route_candidate.py"],
        "researcher_notes": r["researcher_notes"], "generated": "2026-10-20"}}
p.write_text(json.dumps(fc, indent=1))
print("P8327 stamped")
