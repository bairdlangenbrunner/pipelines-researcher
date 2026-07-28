#!/usr/bin/env python3
"""Recenter an edge-hugging offshore trace onto the band's bright-fill CENTERLINE.

The BFS extraction (extract_offshore_lines.py) masks near-white pixels and walks a
shortest path — which hugs the DARK OUTLINE edge of each drawn pipeline band, not the
light fill running down its middle. This post-processor takes such a trace, and for
every point samples the perpendicular across the band, finds the bright-fill run
(r>180 & g>205 & b>200 — sea fails on r, dark edges fail on r), and shifts the point to
that run's midpoint. The offset is smoothed and tapered to zero at both ends so the
sourced endpoint anchors (the trace tips) do not move.

Usage: python recenter_traces.py <key>              # e.g. leviathan, karish
Reads  traces/trace_<key>.geojson  -> writes traces/trace_<key>_centerline.geojson
       + overlays/recenter_<key>.png (original vs corrected, for visual QC)
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
from pyproj import Transformer
from shapely.geometry import LineString

HERE = Path(__file__).parent
P = json.load(open(HERE / "georef_params.json"))
base = Image.open(HERE / "maps" / "ingl_big_map_fullres.jpg").convert("RGB")
a = np.asarray(base, dtype=np.int16)
H, W = a.shape[:2]

# bright fill of the band centre (excludes sea, which fails r>180, and dark edges)
FILL = (a[..., 0] > 180) & (a[..., 1] > 205) & (a[..., 2] > 200)

WINDOW = 16.0   # +/- px sampled across the band perpendicular
STEP = 0.5      # perpendicular sampling step (px)
TANGENT_K = 3   # neighbours each side used for the local tangent
SMOOTH_K = 9    # moving-average window over the per-point offset
TAPER = 40      # samples over which the offset ramps 0->1 at each end


def to_px(lon, lat, to_itm):
    E, N = to_itm.transform(lon, lat)
    return (E - P["e_intercept"]) / P["e_per_px"], (N - P["n_intercept"]) / P["n_per_px"]


def fill_at(x, y):
    xi, yi = int(round(x)), int(round(y))
    return 0 <= xi < W and 0 <= yi < H and FILL[yi, xi]


def densify(pts, step=1.5):
    """Resample a pixel polyline at ~step px spacing."""
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        seg = np.hypot(x1 - x0, y1 - y0)
        n = max(1, int(seg / step))
        for i in range(1, n + 1):
            t = i / n
            out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return out


def recenter(key):
    d = json.load(open(HERE / "traces" / f"trace_{key}.geojson"))
    coords = d["features"][0]["geometry"]["coordinates"]
    to_itm = Transformer.from_crs(4326, 2039, always_xy=True)
    to_wgs = Transformer.from_crs(2039, 4326, always_xy=True)

    px = [to_px(lon, lat, to_itm) for lon, lat in coords]
    dp = densify(px)
    n = len(dp)
    arr = np.array(dp)

    offsets = np.zeros(n)
    ts = np.arange(-WINDOW, WINDOW + 1e-9, STEP)
    for i in range(n):
        j0, j1 = max(0, i - TANGENT_K), min(n - 1, i + TANGENT_K)
        tx, ty = arr[j1] - arr[j0]
        norm = np.hypot(tx, ty)
        if norm < 1e-6:
            continue
        perp = np.array([-ty, tx]) / norm  # unit perpendicular
        x, y = arr[i]
        hits = np.array([fill_at(x + t * perp[0], y + t * perp[1]) for t in ts])
        if not hits.any():
            continue
        # contiguous runs of fill; pick the one nearest (or containing) t=0
        runs, start = [], None
        for k, h in enumerate(hits):
            if h and start is None:
                start = k
            elif not h and start is not None:
                runs.append((start, k - 1)); start = None
        if start is not None:
            runs.append((start, len(hits) - 1))
        best = min(runs, key=lambda r: abs((ts[r[0]] + ts[r[1]]) / 2))
        offsets[i] = (ts[best[0]] + ts[best[1]]) / 2

    # smooth, then taper to zero at both ends (keep sourced tips fixed)
    if n >= SMOOTH_K:
        kern = np.ones(SMOOTH_K) / SMOOTH_K
        offsets = np.convolve(offsets, kern, mode="same")
    ramp = np.ones(n)
    for i in range(n):
        ramp[i] = min(1.0, i / TAPER, (n - 1 - i) / TAPER)
    offsets *= ramp

    corr = arr.copy().astype(float)
    for i in range(n):
        j0, j1 = max(0, i - TANGENT_K), min(n - 1, i + TANGENT_K)
        tx, ty = arr[j1] - arr[j0]
        norm = np.hypot(tx, ty)
        if norm < 1e-6:
            continue
        perp = np.array([-ty, tx]) / norm
        corr[i] = arr[i] + offsets[i] * perp

    # reproject, simplify
    cc = []
    for x, y in corr:
        E = P["e_per_px"] * x + P["e_intercept"]
        N = P["n_per_px"] * y + P["n_intercept"]
        lon, lat = to_wgs.transform(E, N)
        cc.append([round(lon, 6), round(lat, 6)])
    ls = LineString(cc).simplify(0.0002)  # ~20 m in degrees
    cc = [[round(a_, 6), round(b_, 6)] for a_, b_ in ls.coords]
    # hard-pin the endpoints back to the original sourced tips
    cc[0], cc[-1] = coords[0], coords[-1]

    itm = [to_itm.transform(*c) for c in cc]
    length_km = LineString(itm).length / 1000
    med = float(np.median(np.abs(offsets[TAPER:n - TAPER]))) if n > 2 * TAPER else float(np.median(np.abs(offsets)))
    print(f"{key}: {n} densified pts, {len(cc)} out verts, median |offset|={med:.1f}px, length={length_km:.1f} km")

    gj = {"type": "FeatureCollection", "name": f"{key}_centerline", "crs": None, "features": [{
        "type": "Feature",
        "properties": {"name": f"{key}_centerline",
                       "source": "trace of INGL transmission map (ingl.co.il), band-centerline corrected",
                       "correction": "recenter_traces.py: edge->bright-fill midpoint, perpendicular resample, "
                                      f"median shift {med:.1f}px (~{med*P['e_per_px']:.0f} m)",
                       "length_km": round(length_km, 1)},
        "geometry": {"type": "LineString", "coordinates": cc}}]}
    out = HERE / "traces" / f"trace_{key}_centerline.geojson"
    out.write_text(json.dumps(gj))
    print(f"wrote {out.name}")

    # overlay: original (magenta) vs corrected (cyan)
    viz = ImageEnhance.Brightness(base).enhance(0.6)
    dr = ImageDraw.Draw(viz)
    dr.line([tuple(p) for p in px], fill=(255, 0, 200), width=2)
    dr.line([tuple(p) for p in corr], fill=(0, 220, 255), width=2)
    xs = [p[0] for p in corr] + [p[0] for p in px]
    ys = [p[1] for p in corr] + [p[1] for p in px]
    crop = viz.crop((int(max(0, min(xs) - 80)), int(max(0, min(ys) - 80)),
                     int(min(W, max(xs) + 80)), int(min(H, max(ys) + 80))))
    if max(crop.size) > 1500:
        r = 1500 / max(crop.size)
        crop = crop.resize((int(crop.width * r), int(crop.height * r)))
    crop.save(HERE / "overlays" / f"recenter_{key}.png")
    print(f"wrote overlays/recenter_{key}.png")


if __name__ == "__main__":
    recenter(sys.argv[1])
