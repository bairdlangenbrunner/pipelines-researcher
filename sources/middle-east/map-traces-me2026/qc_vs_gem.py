#!/usr/bin/env python3
"""Independent accuracy check: extracted routes vs GEM's own high-accuracy routes.

The georeferencing residual (~1.9 km) measures how well the transform reproduces
the map's own projection, against Natural Earth. It does NOT say how faithfully
the cartographer drew the pipe. Comparing against GEM routes already carrying
RouteAccuracy high / very high gives that second, independent number.

Direction matters: distances are measured GEM -> ours. Our chaining splits at
junctions, so one extracted polyline can span several GEM lines; measuring
ours -> GEM would charge us for pipe GEM has not drawn.

Two views:
  (a) per named pair, against the specific GEM route
  (b) network-level, every high-accuracy ME GEM route vs our whole same-commodity
      network -- "does the map draw pipe where GEM says pipe is?"

GEM routes are a yardstick for OUR geometry only. Nothing is written anywhere and
GEM is never cited as a source.
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Geod
from scipy.spatial import cKDTree

GEOD = Geod(ellps="WGS84")
ROUTES = Path("/Users/baird/Dropbox/_git_ALL/_github-repos-gem/GOIT-GGIT-pipeline-routes")
REPO = Path("/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher")
ME = {"Saudi Arabia", "Iraq", "Iran", "United Arab Emirates", "Qatar", "Kuwait",
      "Oman", "Yemen", "Egypt", "Jordan", "Israel", "Syria", "Lebanon", "Bahrain"}

# The sheet's own footprint, from the fitted corners. A GEM route that leaves it
# (Iran-Pakistan-India, Dauletabad, Egypt west of ~34E) is not drawn here at all,
# so scoring it would measure the map's coverage, not its accuracy.
FOOTPRINT = (34.1, 12.2, 63.4, 39.9)     # lon0, lat0, lon1, lat1 (inset by ~0.15)
INSIDE_FRAC = 0.90


def inside_footprint(pts):
    lon0, lat0, lon1, lat1 = FOOTPRINT
    m = ((pts[:, 0] >= lon0) & (pts[:, 0] <= lon1)
         & (pts[:, 1] >= lat0) & (pts[:, 1] <= lat1))
    return m.mean()

# Verified against the 2026-07-31 snapshots: every PID below is RouteAccuracy
# high or very high, and names both sides clearly depict the same trunk line.
PAIRS = [
    ("Dolphin", "P0437", "gas"),
    ("IGAT 2", "P0442", "gas"),
    ("IGAT 3", "P0443", "gas"),
    ("IGAT 4", "P0444", "gas"),
    ("IGAT 7", "P0446", "gas"),
    ("Trans-Arabian Pipeline (Tapline) mothballed", "P0552", "oil"),
    ("Strategic Pipeline", "P0542", "oil"),
]


def load_gem(pid):
    hits = list(ROUTES.glob(f"data/**/{pid}.geojson"))
    if not hits:
        return None
    pts = []
    for f in json.load(open(hits[0])).get("features", []):
        geom = f.get("geometry") or {}
        if geom.get("type") == "LineString":
            pts.extend(geom["coordinates"])
        elif geom.get("type") == "MultiLineString":
            for part in geom["coordinates"]:
                pts.extend(part)
    return np.array(pts, float)[:, :2] if len(pts) > 1 else None


def densify(pts, step_km=2.0):
    out = []
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        _, _, d = GEOD.inv(x0, y0, x1, y1)
        n = max(1, min(400, int(d / 1000.0 / step_km)))
        for i in range(n):
            t = i / n
            out.append((x0 + t * (x1 - x0), y0 + t * (y1 - y0)))
    out.append(tuple(pts[-1]))
    return np.array(out)


def nn_km(a, b):
    _, idx = cKDTree(b).query(a)
    _, _, d = GEOD.inv(a[:, 0], a[:, 1], b[idx][:, 0], b[idx][:, 1])
    return d / 1000.0


def main():
    feats = json.load(open("me2026_pipelines.geojson"))["features"]
    best = {}
    for f in feats:
        n = f["properties"]["name"]
        if n and (n not in best
                  or f["properties"]["length_km"] > best[n]["properties"]["length_km"]):
            best[n] = f

    rows = []
    for name, pid, cm in PAIRS:
        f, gem = best.get(name), load_gem(pid)
        if f is None or gem is None:
            rows.append((name, pid, cm, None, None, None, "no geometry"))
            continue
        ours = densify(np.array(f["geometry"]["coordinates"], float))
        d = nn_km(densify(gem), ours)
        rows.append((name, pid, cm, len(gem), round(float(np.median(d)), 2),
                     round(float(np.percentile(d, 90)), 2), ""))
    df = pd.DataFrame(rows, columns=["extracted_name", "gem_pid", "commodity",
                                     "gem_pts", "median_km", "p90_km", "note"])
    print("(a) per named pair, GEM route -> our named route")
    print(df.to_string(index=False))
    ok = df["median_km"].dropna()
    if len(ok):
        print(f"    median of medians: {ok.median():.2f} km over {len(ok)} lines")

    # (b) network level
    net = {}
    for cm in ("gas", "oil"):
        pts = [np.array(f["geometry"]["coordinates"], float) for f in feats
               if f["properties"]["commodity"] == cm]
        net[cm] = np.vstack([densify(p) for p in pts if len(p) > 1])

    nrows = []
    for path, cm in ((sorted(glob.glob(str(REPO / "data/GGIT_gas_snapshot_*.csv")))[-1], "gas"),
                     (sorted(glob.glob(str(REPO / "data/GOIT_oil_ngl_snapshot_*.csv")))[-1], "oil")):
        df2 = pd.read_csv(path, header=2, low_memory=False)
        ctry = [c for c in df2.columns if c.lower().startswith("countries")][0]
        sel = df2[df2["RouteAccuracy"].isin(["high", "very high (within meters)"])
                  & df2[ctry].astype(str).apply(lambda s: any(c in s for c in ME))]
        for _, r in sel.iterrows():
            gem = load_gem(r["ProjectID"])
            if gem is None or len(gem) < 2:
                continue
            frac = inside_footprint(gem)
            d = nn_km(densify(gem), net[cm])
            nrows.append((cm, r["ProjectID"], str(r["PipelineName"])[:44],
                          round(float(np.median(d)), 2), round(float(frac), 2),
                          frac >= INSIDE_FRAC))
    nd = pd.DataFrame(nrows, columns=["commodity", "pid", "name", "median_km",
                                      "frac_in_footprint", "scored"])
    inb = nd[nd["scored"]]
    print(f"\n(b) network level: {len(nd)} GEM high-accuracy ME routes, "
          f"{len(inb)} inside the sheet footprint (the rest are not drawn here)")
    for cm, g in inb.groupby("commodity"):
        within = (g["median_km"] <= 5).mean() * 100
        print(f"    {cm}: n={len(g)}  median {g['median_km'].median():.2f} km  "
              f"{within:.0f}% within 5 km")
    out = nd[~nd["scored"]]
    if len(out):
        print(f"    excluded as outside coverage ({len(out)}): "
              + ", ".join(f"{r.pid}" for r in out.head(12).itertuples()))
    Path("georef").mkdir(exist_ok=True)
    df.to_csv("georef/qc_vs_gem_pairs.csv", index=False)
    nd.to_csv("georef/qc_vs_gem_network.csv", index=False)
    print("wrote georef/qc_vs_gem_pairs.csv, georef/qc_vs_gem_network.csv")


if __name__ == "__main__":
    main()
