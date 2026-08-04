"""Empirical accuracy of the ENTSOG SYSCAP 2026 traces over Egypt.

Compares the ENTSOG operational-line extraction (sources/entsog/) against every
Egypt gas route already in GOIT-GGIT-pipeline-routes at RouteAccuracy high /
very high / medium (independent, better-sourced geometry). For each such GEM
route, samples points every ~2 km and measures the lateral distance to the
nearest ENTSOG trace; a route counts as "drawn on the map" when >=60% of its
samples fall within 15 km. The offset distribution over covered routes is the
empirical accuracy of ENTSOG-derived candidate geometry for Egypt.

Run from the repo root:  python3 batches/egypt-gas/staging/route-creation-20260804/entsog_accuracy_check.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely.geometry import LineString, shape
from shapely.ops import transform as shp_transform
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from route_compare import load_gem_route, _featurecollection_to_geom  # noqa: E402

CSV = ROOT / "data/GGIT_gas_snapshot_20260804.csv"
ENTSOG = ROOT / "sources/entsog/ENTSOG_GIE_SYSCAP_2026_pipelines_operational_wgs84.geojson"

TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32636", always_xy=True).transform


def utm(geom):
    return shp_transform(TO_UTM, geom)


def main() -> None:
    df = pd.read_csv(CSV, header=2, low_memory=False)
    eg = df[(df["CountriesOrAreas"].fillna("").str.contains("Egypt"))
            & df["ProjectID"].notna()]
    good = eg[eg["RouteAccuracy"].isin(
        ["high", "very high (within meters)", "medium"])]

    ent = json.load(open(ENTSOG))
    # Egypt + Sinai window, generous margins
    lines = []
    for f in ent["features"]:
        g = shape(f["geometry"])
        x0, y0, x1, y1 = g.bounds
        if x1 < 24.0 or x0 > 37.5 or y1 < 21.0 or y0 > 32.5:
            continue
        lines.append(utm(g))
    tree = STRtree(lines)
    print(f"ENTSOG operational traces in the Egypt window: {len(lines)}")

    rows = []
    for _, r in good.iterrows():
        pid = r["ProjectID"]
        gj = load_gem_route(pid, "gas")
        if gj is None:
            continue
        geom = utm(shape(gj))
        n = max(int(geom.length // 2000), 2)
        pts = [geom.interpolate(i / n, normalized=True) for i in range(n + 1)]
        d = np.array([lines[tree.nearest(p)].distance(p) for p in pts]) / 1000.0
        cov = float((d <= 15.0).mean())
        rows.append({"pid": pid, "name": r["PipelineName"], "acc": r["RouteAccuracy"],
                     "km": round(geom.length / 1000, 1), "coverage": round(cov, 2),
                     "median_off_km": round(float(np.median(d[d <= 15.0])), 2) if cov else None,
                     "p90_off_km": round(float(np.quantile(d[d <= 15.0], 0.9)), 2) if cov else None})

    out = pd.DataFrame(rows).sort_values("coverage", ascending=False)
    print(out.to_string(index=False))
    covered = out[out["coverage"] >= 0.6]
    if len(covered):
        print(f"\ncovered routes (>=60% within 15 km): {len(covered)}/{len(out)}")
        print(f"median offset over covered routes: "
              f"{covered['median_off_km'].median():.2f} km; "
              f"p90 of the per-route p90s: {covered['p90_off_km'].quantile(0.9):.2f} km")


if __name__ == "__main__":
    main()
