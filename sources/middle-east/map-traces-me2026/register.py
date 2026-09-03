#!/usr/bin/env python3
"""Fit a page-space -> lon/lat transform by registering the map's own coastline
vector to Natural Earth 10m coastline + lakes.

Stage 1: coarse grid search over an equirectangular model (lon0, lat0, sx, sy).
Stage 2: trimmed ICP refining a full affine (and optionally quadratic) fit.
Scoring/residuals are geodesic km via pyproj.Geod.
"""
from __future__ import annotations

import json
import numpy as np
from pathlib import Path
from scipy.spatial import cKDTree
import geopandas as gpd
from pyproj import Geod

NE = Path("/Users/baird/Dropbox/_gis-data/_natural_earth_data")
BBOX = (20.0, 8.0, 74.0, 47.0)          # lon0, lat0, lon1, lat1
INSET = (2020, 1740, 2520, 2370)        # Hormuz inset, page coords -> drop
NEATLINE = (42, 44, 2483, 2354)
GEOD = Geod(ellps="WGS84")


def ref_points(step_deg=0.02):
    """Densified reference coastline+lake vertices inside BBOX."""
    frames = []
    for name in ("ne_10m_coastline", "ne_10m_lakes"):
        g = gpd.read_file(NE / name / f"{name}.shp")
        g = g.clip(gpd.GeoSeries([__import__("shapely").geometry.box(*BBOX)], crs=g.crs).iloc[0])
        frames.append(g)
    pts = []
    for g in frames:
        for geom in g.geometry:
            if geom is None or geom.is_empty:
                continue
            parts = geom.geoms if hasattr(geom, "geoms") else [geom]
            for part in parts:
                coords = (list(part.exterior.coords) if part.geom_type == "Polygon"
                          else list(part.coords) if part.geom_type == "LineString" else [])
                if len(coords) >= 2:
                    pts.extend(_densify(coords, step_deg))
    return np.array(pts)


def _densify(coords, step):
    out = []
    for (x0, y0), (x1, y1) in zip(coords[:-1], coords[1:]):
        d = np.hypot(x1 - x0, y1 - y0)
        n = max(1, int(d / step))
        for i in range(n):
            t = i / n
            out.append((x0 + t * (x1 - x0), y0 + t * (y1 - y0)))
    out.append(coords[-1])
    return out


def map_points(max_pts=20000, min_len=8):
    g = json.load(open("traces/basemap_lines.json"))
    cyan = g["(0.0, 0.681, 0.938)"]
    pts = []
    for ln in cyan:
        if len(ln) < min_len:
            continue
        for x, y in ln:
            if INSET[0] <= x <= INSET[2] and INSET[1] <= y <= INSET[3]:
                continue
            if not (NEATLINE[0] <= x <= NEATLINE[2] and NEATLINE[1] <= y <= NEATLINE[3]):
                continue
            pts.append((x, y))
    pts = np.array(pts)
    if len(pts) > max_pts:
        idx = np.linspace(0, len(pts) - 1, max_pts).astype(int)
        pts = pts[idx]
    return pts


def coarse_search(mp, tree, ref):
    best = None
    sub = mp[np.linspace(0, len(mp) - 1, 800).astype(int)]
    x, y = sub[:, 0], sub[:, 1]
    for lon0 in np.arange(22.0, 36.01, 1.0):
        for sx in np.arange(0.0150, 0.02201, 0.0005):
            lon = lon0 + sx * (x - NEATLINE[0])
            for lat0 in np.arange(38.0, 48.01, 1.0):
                for sy in np.arange(0.0110, 0.01801, 0.0005):
                    lat = lat0 - sy * (y - NEATLINE[1])
                    d, _ = tree.query(np.column_stack([lon, lat]))
                    score = np.median(d)
                    if best is None or score < best[0]:
                        best = (score, lon0, sx, lat0, sy)
    return best


def apply_affine(coef, px):
    x, y = px[:, 0], px[:, 1]
    A = np.column_stack([np.ones_like(x), x, y])
    return np.column_stack([A @ coef[0], A @ coef[1]])


def apply_quad(coef, px):
    x, y = px[:, 0], px[:, 1]
    A = np.column_stack([np.ones_like(x), x, y, x * x, x * y, y * y])
    return np.column_stack([A @ coef[0], A @ coef[1]])


def icp(mp, tree, ref, coef, order=1, iters=60, trim=0.6):
    apply = apply_affine if order == 1 else apply_quad
    x, y = mp[:, 0], mp[:, 1]
    A = (np.column_stack([np.ones_like(x), x, y]) if order == 1
         else np.column_stack([np.ones_like(x), x, y, x * x, x * y, y * y]))
    for _ in range(iters):
        ll = apply(coef, mp)
        d, idx = tree.query(ll)
        keep = d <= np.quantile(d, trim)
        tgt = ref[idx[keep]]
        Ak = A[keep]
        coef = (np.linalg.lstsq(Ak, tgt[:, 0], rcond=None)[0],
                np.linalg.lstsq(Ak, tgt[:, 1], rcond=None)[0])
    return coef


def residual_km(mp, tree, ref, coef, order, trim=0.6):
    apply = apply_affine if order == 1 else apply_quad
    ll = apply(coef, mp)
    d, idx = tree.query(ll)
    keep = d <= np.quantile(d, trim)
    a, b = ll[keep], ref[idx[keep]]
    _, _, dist = GEOD.inv(a[:, 0], a[:, 1], b[:, 0], b[:, 1])
    dist = dist / 1000.0
    return dict(n=int(keep.sum()), median_km=float(np.median(dist)),
                mean_km=float(dist.mean()), p90_km=float(np.percentile(dist, 90)),
                rmse_km=float(np.sqrt((dist ** 2).mean())))


def main():
    print("loading reference…")
    ref = ref_points()
    tree = cKDTree(ref)
    print("  ref points:", len(ref))
    mp = map_points()
    print("  map coastline points:", len(mp))

    print("coarse search…")
    score, lon0, sx, lat0, sy = coarse_search(mp, tree, ref)
    print(f"  best equirect: lon0={lon0} sx={sx} lat0={lat0} sy={sy}  median_deg={score:.4f}")

    coef = (np.array([lon0 - sx * NEATLINE[0], sx, 0.0]),
            np.array([lat0 + sy * NEATLINE[1], 0.0, -sy]))
    out = {}
    for order in (1, 2):
        c = coef if order == 1 else (np.r_[c1[0], 0, 0, 0], np.r_[c1[1], 0, 0, 0])
        c = icp(mp, tree, ref, c, order=order)
        r = residual_km(mp, tree, ref, c, order)
        print(f"  order {order}: {r}")
        out[order] = (c, r)
        if order == 1:
            c1 = c
    np.save("georef/fit_order1.npy", np.array(out[1][0]))
    np.save("georef/fit_order2.npy", np.array(out[2][0]))
    json.dump({str(k): v[1] for k, v in out.items()}, open("georef/fit_report.json", "w"), indent=2)


if __name__ == "__main__":
    main()
