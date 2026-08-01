#!/usr/bin/env python3
"""Independent accuracy check: georeferenced GASCO traces vs GEM's own Egypt gas
routes at high/medium RouteAccuracy.

For every vertex of a GEM reference route, measure the distance to the nearest
GASCO trace. This is a one-way, nearest-neighbour statistic over pipe GASCO
actually drew -- GEM tracks routes the 2007 map does not show, so the tail is
expected and only the low percentiles are informative.

Writes overlays/qc_gasco2007_vs_gem_routes.png and prints the distance table.
"""
from __future__ import annotations

import glob
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from shapely.geometry import shape
from shapely.ops import unary_union

HERE = Path(__file__).parent
REPO = HERE.parents[3]
ROUTES = REPO.parent / "GOIT-GGIT-pipeline-routes" / "data" / "individual-routes" / "gas-pipelines"
SNAP = sorted(glob.glob(str(REPO / "data" / "GGIT_gas_snapshot_*.csv")))[-1]
GOOD = {"high", "medium", "very high (within meters)"}


def _to_km(geom, lat0):
    """Equirectangular metres-ish scaling about lat0 so shapely distances are km."""
    kx = 111.320 * math.cos(math.radians(lat0))
    from shapely.ops import transform
    return transform(lambda x, y, z=None: (x * kx, y * 110.574), geom)


def main() -> None:
    df = pd.read_csv(SNAP, header=2, low_memory=False)
    e = df[df["CountriesOrAreas"].astype(str).str.contains("Egypt", na=False)]
    pids = sorted(e[e["RouteAccuracy"].astype(str).str.strip().isin(GOOD)]["ProjectID"])

    gasco = json.loads((HERE / "gasco2007_gas_network.geojson").read_text())
    lat0 = 28.0
    traces = unary_union([_to_km(shape(f["geometry"]), lat0) for f in gasco["features"]])

    rows, missing = [], []
    for pid in pids:
        p = ROUTES / f"{pid}.geojson"
        if not p.exists():
            missing.append(pid)
            continue
        gj = json.loads(p.read_text())
        geoms = [shape(f["geometry"]) for f in gj.get("features", [])] if "features" in gj \
            else [shape(gj)]
        pts = []
        for g in geoms:
            for ls in (g.geoms if g.geom_type.startswith("Multi") else [g]):
                pts.extend(list(ls.coords))
        if not pts:
            continue
        from shapely.geometry import Point
        d = [traces.distance(_to_km(Point(x, y), lat0)) for x, y in pts]
        rows.append((pid, len(pts), float(np.median(d)), float(np.percentile(d, 90))))

    rows.sort(key=lambda r: r[2])
    print(f"{len(rows)} GEM high/medium Egypt gas routes vs GASCO-2007 traces"
          f"{f' (missing geojson: {missing})' if missing else ''}")
    print("  PID     verts  median_km  p90_km")
    for pid, n, med, p90 in rows:
        print("  %-7s %5d  %8.1f  %6.1f" % (pid, n, med, p90))
    med = np.array([r[2] for r in rows])
    print("\n  across routes: min %.1f  p25 %.1f  median %.1f  p75 %.1f  max %.1f km"
          % (med.min(), np.percentile(med, 25), np.median(med),
             np.percentile(med, 75), med.max()))
    print("  routes whose median offset is < 10 km: %d/%d" % ((med < 10).sum(), len(med)))

    # ---- overlay -----------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(11, 12))
    col = {"existing_pl": "#009900", "under_construction_pl": "#3333ff",
           "under_study_pl": "#ff0000"}
    for f in gasco["features"]:
        c = np.array(f["geometry"]["coordinates"])
        ax.plot(c[:, 0], c[:, 1], color=col[f["properties"]["legend_class"]],
                lw=1.0, alpha=0.8, zorder=1)
    for pid in pids:
        p = ROUTES / f"{pid}.geojson"
        if not p.exists():
            continue
        gj = json.loads(p.read_text())
        geoms = [shape(f["geometry"]) for f in gj.get("features", [])] if "features" in gj \
            else [shape(gj)]
        for g in geoms:
            for ls in (g.geoms if g.geom_type.startswith("Multi") else [g]):
                c = np.array(ls.coords)
                ax.plot(c[:, 0], c[:, 1], color="k", lw=2.0, alpha=0.55, zorder=2)
    ax.set_aspect(1 / math.cos(math.radians(lat0)))
    ax.set_title("GASCO 2007 traces (colour, by legend class) vs GEM high/medium\n"
                 "Egypt gas routes (black)")
    ax.set_xlabel("lon"); ax.set_ylabel("lat"); ax.grid(alpha=.25)
    (HERE / "overlays").mkdir(exist_ok=True)
    fig.savefig(HERE / "overlays" / "qc_gasco2007_vs_gem_routes.png", dpi=140,
                bbox_inches="tight")
    print("\n  -> overlays/qc_gasco2007_vs_gem_routes.png")


if __name__ == "__main__":
    main()
