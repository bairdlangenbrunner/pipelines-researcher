#!/usr/bin/env python3
"""Georeference the extracted GASCO-2007 page-space traces -> WGS84 GeoJSON.

The transform comes from the map's OWN printed 1-degree graticule, read out of
the vector art (gcps/gcps_gasco2007.json, 70 intersections). Identification of
which drawn line is which degree was established independently, by first fitting
23 OSM-geocoded place markers (gcps/validation_places_gasco2007.json) and reading
the graticule under that fit: every parallel came out within 0.08 deg of an
integer latitude and every meridian within 0.15 deg of an integer longitude.
Those place markers are then held out as the validation set -- their offsets
measure how schematically GASCO drew the features, NOT the registration error.

Writes gasco2007_gas_network.geojson + georef/georef_report_gasco2007.json.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
from pyproj import Geod

HERE = Path(__file__).parent
REPO = HERE.parents[3]
ORDER = 2                     # chosen on leave-one-out RMSE (order 1 -> 6.6 km)

# The only non-Egyptian geometry on this page runs northeast into Israel/Jordan
# (the EMG marine line and the Fajr/Arab Gas line). Egypt's border with Israel is
# effectively the straight Rafah -> Taba line, so a half-plane separates them.
RAFAH, TABA = (34.25, 31.29), (34.90, 29.49)


def _georef():
    spec = importlib.util.spec_from_file_location("georef", REPO / "scripts" / "georef.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _inside_egypt(pts) -> bool:
    """Approximate: majority of vertices west of the Rafah-Taba border line."""
    (ax, ay), (bx, by) = RAFAH, TABA
    side = [(bx - ax) * (lat - ay) - (by - ay) * (lon - ax) for lon, lat in pts]
    return sum(1 for s in side if s < 0) >= len(side) / 2


def main() -> None:
    m = _georef()
    geod = Geod(ellps="WGS84")
    gcps = json.loads((HERE / "gcps" / "gcps_gasco2007.json").read_text())
    val = json.loads((HERE / "gcps" / "validation_places_gasco2007.json").read_text())
    g = m.fit_transform(gcps, ORDER)

    voff = []
    for c in val:
        p = g.apply([c["px"]])[0]
        voff.append((geod.inv(p[0], p[1], *c["lonlat"])[2] / 1000.0, c["name"]))
    voff.sort(reverse=True)
    vkm = [d for d, _ in voff]

    src = json.loads((HERE / "traces" / "gasco2007_paths.json").read_text())
    feats = []
    for f in src["features"]:
        coords = g.apply(f["points"])
        lens = geod.line_length([c[0] for c in coords], [c[1] for c in coords]) / 1000.0
        feats.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "source_map": "gasco2007",
                "source_file": "maps/source_mashreq_gas_initiative_2008.pdf",
                "source_page": 15,
                "source_title": "GASCO, Natural Gas Network, Nov. 2007",
                "legend_class": f["legend_class"],
                "path_id": f["path_id"],
                "stroke_rgb": f["stroke_rgb"],
                "dashed": f["dashed"],
                "geometry_source": f["geometry_source"],
                "length_km": round(lens, 2),
                "georef_order": ORDER,
                "georef_source": "printed 1-degree graticule",
                "georef_loo_rmse_km": g.loo_rmse_km,
                "drawn_feature_offset_median_km": round(float(np.median(vkm)), 1),
                "accuracy_tier": "low",
                "inside_egypt": _inside_egypt(coords),
            },
        })

    out = HERE / "gasco2007_gas_network.geojson"
    out.write_text(json.dumps({"type": "FeatureCollection", "features": feats}) + "\n")

    rep = {
        "map": "gasco2007",
        "order": ORDER,
        "n_gcps": g.n_gcps,
        "gcp_source": "1-degree graticule printed on the source map (70 intersections)",
        "condition": g.condition,
        "rmse_km": g.rmse_km,
        "max_residual_km": g.max_residual_km,
        "loo_rmse_km": g.loo_rmse_km,
        "registration_gate": {"threshold_km": 5.0, "pass": g.loo_rmse_km <= 5.0},
        "validation_places": {
            "n": len(val),
            "note": "OSM-geocoded settlements NOT used in the fit; their offsets "
                    "measure how schematically GASCO drew the features, not the "
                    "registration error",
            "rmse_km": round(float(np.sqrt(np.mean(np.square(vkm)))), 1),
            "median_km": round(float(np.median(vkm)), 1),
            "max_km": round(max(vkm), 1),
            "worst": [{"name": n, "offset_km": round(d, 1)} for d, n in voff[:8]],
        },
        "alternatives_tested": {
            "graticule_order_1_loo_km": 6.634,
            "places_affine_order_1_loo_km": 19.956,
            "places_affine_order_2_loo_km": 23.546,
            "places_tps_best_loo_km": 18.99,
            "graticule_plus_tps_place_correction_best_loo_km": 17.9,
            "note": "rubber-sheeting toward the place markers did not generalize, "
                    "so the drawing is reproduced as drawn under the map's own "
                    "projection; scripts/georef.py is unchanged",
        },
        "features": len(feats),
        "features_outside_egypt": sum(1 for f in feats if not f["properties"]["inside_egypt"]),
        "total_length_km": round(sum(f["properties"]["length_km"] for f in feats), 1),
    }
    (HERE / "georef").mkdir(exist_ok=True)
    (HERE / "georef" / "georef_report_gasco2007.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
