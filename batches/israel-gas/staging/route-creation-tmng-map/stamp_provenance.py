#!/usr/bin/env python3
"""Stamp route genealogy onto every produced geojson + emit a provenance ledger.

Each candidate route in this batch is traceable to a root source:
  - a *trace* of the INGL transmission raster map (maps/ingl_big_map_fullres.jpg),
    georeferenced via georef_params.json (ITM EPSG:2039 comb fit, ~92.5 m/px), or
  - an *extraction* from an existing high-accuracy routes-repo geometry.

This script writes that lineage in two forms so it can never be lost:
  1. a `provenance` object injected into each candidate_routes/<PID>.geojson
     feature's properties (travels WITH the geometry into any PR); and
  2. route_provenance.json — one machine-readable ledger for the whole batch.

Idempotent: re-running overwrites the provenance block in place. Run after any
rebuild of the candidate geometry.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
GENERATED = "2026-07-23"

MAP_ROOT = {
    "type": "raster map trace",
    "name": "INGL national natural-gas transmission map (\"big-map.jpg\")",
    "url": "https://www.ingl.co.il/wp-content/uploads/2024/04/big-map.jpg",
    "page": "https://www.ingl.co.il/en/holancha/",
    "local_copy": "maps/ingl_big_map_fullres.jpg",
    "fetched": "2026-07-23",
    "basemap_credit": "base map © Survey of Israel 2018",
    "disclaimer": "map is schematic → traced RouteAccuracy capped at medium",
    "georeference": "georef_params.json (ITM EPSG:2039, comb fit, ~92.5 m/px)",
    "centerline_correction": "offshore white-band traces are recentered off the dark "
                             "outline edge onto the band's bright-fill midpoint "
                             "(recenter_traces.py); the raw BFS trace hugged the edge "
                             "(~4px / ~415 m offset). Onshore lines on the topo basemap "
                             "(e.g. P0480) are not amenable and stay human-review candidates.",
    "digitization_scheme": "legend.md — the map's key (מקרא) is transcribed and its "
                           "point symbols are used as trace anchors: routes pass "
                           "dead-through each ⊕ well-marker / ○ marine-receiving-station "
                           "centre (point-symmetry detection), stay straight through "
                           "crossings, and follow the gas-suppliers white band centerline.",
}

# per-candidate lineage: the immediate parent artifact + which root it descends from
LINEAGE = {
    "P7602": {
        "derived_from": "traces/trace_leviathan_centerline.geojson",
        "root": "map",
        "method": "digitized (map trace, band-centerline corrected)",
        "tools": ["extract_offshore_lines.py", "recenter_traces.py",
                  "build_route_candidate.py", "validate_route_candidate.py"],
        "route_accuracy_cap": "medium",
    },
    "P7603": {
        "derived_from": "traces/trace_leviathan_centerline.geojson",
        "root": "map",
        "method": "digitized (map trace, band-centerline corrected; shares P7602 corridor)",
        "tools": ["extract_offshore_lines.py", "recenter_traces.py",
                  "build_route_candidate.py", "validate_route_candidate.py"],
        "route_accuracy_cap": "medium",
    },
    "P0480": {
        "derived_from": "traces/trace_p0480.geojson",
        "root": "map",
        "method": "digitized (map trace); replacement of prior chord",
        "tools": ["extract_offshore_lines.py", "build_route_candidate.py",
                  "validate_route_candidate.py"],
        "route_accuracy_cap": "low",
    },
    "P8003": {
        "derived_from": "traces/trace_karish_centerline.geojson",
        "root": "map",
        "method": ("digitized (map trace, band-centerline corrected); re-traced through "
                   "the map's legend point-anchors Tanin well-marker (⊕) → Karish/Energean "
                   "FPSO well-marker (⊕) → Dor INGL OOAT marine-receiving-station (○), each "
                   "hit dead-centre; NEW discovery row, no prior GEM route. FULL DRAWN "
                   "EXTENT ~129 km — the Tanin→Karish leg is a drawn FUTURE line (קו עתידי, "
                   "field tieback), Karish→OOAT is the operating export line; trim is a "
                   "human decision at apply time."),
        "tools": ["extract_offshore_lines.py", "recenter_traces.py",
                  "retrace_karish_tanin.py", "build_route_candidate.py",
                  "validate_route_candidate.py"],
        "route_accuracy_cap": "medium",
    },
    "P2197": {
        "derived_from": "traces/extract_p2197.geojson",
        "root": "gem_geometry",
        "root_detail": {
            "type": "extraction from existing GEM route geometry",
            "name": "P3658 INGL-network route (routes repo, RouteAccuracy high)",
            "source_repo": "GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes",
            "source_file": "data/individual-routes/gas-pipelines/P3658.geojson",
            "note": "Elyakim↔Ramle eastern trunk the network already contains; "
                    "NOT a fresh map trace. Map used only to confirm the corridor.",
        },
        "method": "extracted from P3658 network geometry; replacement of 2-pt chord",
        "tools": ["build_route_candidate.py", "validate_route_candidate.py"],
        "route_accuracy_cap": "medium",
    },
}


def main() -> None:
    reso = {r["project_id"]: r
            for r in json.loads((HERE / "staged_resolutions.json").read_text())["resolutions"]}
    ledger = {"batch": "israel-gas / route-creation-tmng-map",
              "generated": GENERATED,
              "roots": {"map": MAP_ROOT},
              "routes": []}

    for pid, lin in LINEAGE.items():
        gpath = HERE / "candidate_routes" / f"{pid}.geojson"
        if not gpath.exists():
            print(f"  skip {pid}: no geometry file")
            continue
        r = reso.get(pid, {})
        root = dict(MAP_ROOT) if lin["root"] == "map" else dict(lin["root_detail"])
        prov = {
            "produced_by": "pipelines-researcher route-creation SOP §8",
            "batch": "israel-gas / route-creation-tmng-map",
            "method": lin["method"],
            "derived_from": lin["derived_from"],
            "root_source": root,
            "route_accuracy_cap": lin["route_accuracy_cap"],
            "length_km": r.get("length_km"),
            "sheet_length_km": r.get("sheet_length_km"),
            "replacement": r.get("replacement"),
            "qc_gate": "PASS" if r.get("qc_passed") else "FAIL (documented, non-blocking)",
            "tools": lin["tools"],
            "researcher_notes": r.get("researcher_notes"),
            "generated": GENERATED,
        }
        gj = json.loads(gpath.read_text())
        for f in gj.get("features", []):
            f.setdefault("properties", {})["provenance"] = prov
        gpath.write_text(json.dumps(gj, ensure_ascii=False))
        ledger["routes"].append({"project_id": pid, **prov})
        print(f"  stamped {pid} ({lin['root']} root, {lin['method']})")

    (HERE / "route_provenance.json").write_text(
        json.dumps(ledger, indent=2, ensure_ascii=False))
    print(f"wrote route_provenance.json ({len(ledger['routes'])} routes)")


if __name__ == "__main__":
    main()
