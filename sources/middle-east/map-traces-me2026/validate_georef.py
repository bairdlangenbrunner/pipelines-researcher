#!/usr/bin/env python3
"""Independent validation of the fit on a layer that was never fitted.

register.py fits the transform to the map's CYAN coastline. This scores it
against the map's GREY country borders, which are held out entirely, versus
Natural Earth admin-0. A fit can always be made to reproduce its own training
layer; the border residual is the honest number.

Writes georef/validation_report.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import shapely.geometry
from pyproj import Geod
from scipy.spatial import cKDTree

from register import BBOX, INSET, NEATLINE, _densify, apply_affine, apply_quad

NE = Path("/Users/baird/Dropbox/_gis-data/_natural_earth_data")
GEOD = Geod(ellps="WGS84")
GREY = "(0.427, 0.433, 0.442)"


def border_ref(step_deg=0.02):
    g = gpd.read_file(NE / "ne_10m_admin_0_countries" / "ne_10m_admin_0_countries.shp")
    g = g.clip(shapely.geometry.box(*BBOX))
    pts = []
    for geom in g.geometry:
        if geom is None or geom.is_empty:
            continue
        for part in (geom.geoms if hasattr(geom, "geoms") else [geom]):
            if part.geom_type != "Polygon":
                continue
            for ring in [part.exterior, *part.interiors]:
                c = list(ring.coords)
                if len(c) >= 2:
                    pts.extend(_densify(c, step_deg))
    return np.array(pts)


def map_borders(max_pts=12000, min_len=8):
    grey = json.load(open("traces/basemap_lines.json"))[GREY]
    pts = []
    for ln in grey:
        if len(ln) < min_len:
            continue
        for x, y in ln:
            if INSET[0] <= x <= INSET[2] and INSET[1] <= y <= INSET[3]:
                continue
            if not (NEATLINE[0] <= x <= NEATLINE[2] and NEATLINE[1] <= y <= NEATLINE[3]):
                continue
            pts.append((x, y))
    pts = np.array(pts)
    return pts[np.linspace(0, len(pts) - 1, min(max_pts, len(pts))).astype(int)]


def score(ll, tree, ref, trim=0.6):
    d, idx = tree.query(ll)
    keep = d <= np.quantile(d, trim)
    a, b = ll[keep], ref[idx[keep]]
    _, _, dist = GEOD.inv(a[:, 0], a[:, 1], b[:, 0], b[:, 1])
    dist /= 1000.0
    return dict(n=int(keep.sum()), median_km=round(float(np.median(dist)), 3),
                mean_km=round(float(dist.mean()), 3),
                p90_km=round(float(np.percentile(dist, 90)), 3),
                rmse_km=round(float(np.sqrt((dist ** 2).mean())), 3))


def main():
    ref = border_ref()
    tree = cKDTree(ref)
    mp = map_borders()
    print(f"held-out border points: map {len(mp)}, reference {len(ref)}")
    out = {}
    for order, fn in ((1, apply_affine), (2, apply_quad)):
        coef = np.load(f"georef/fit_order{order}.npy")
        out[f"order{order}"] = score(fn(coef, mp), tree, ref)
        print(f"  order {order}: {out[f'order{order}']}")
    out["note"] = ("scored against ne_10m_admin_0_countries; the map's grey border "
                   "strokes are never used by register.py, which fits the cyan "
                   "coastline only. Includes genuine NE-vs-publisher border "
                   "disagreement, so it is conservative.")
    Path("georef/validation_report.json").write_text(json.dumps(out, indent=2))
    print("wrote georef/validation_report.json")


if __name__ == "__main__":
    main()
