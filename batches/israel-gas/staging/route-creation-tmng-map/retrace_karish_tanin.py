#!/usr/bin/env python3
"""Re-trace the Karish–Tanin gas-suppliers line through its legend point-anchors.

Per the map legend, the white blue-white-blue band is a "gas suppliers line"
(קו מספקי גז) and the ⊕ symbol is a "well location" (מיקום הקידוח). The drawn line
runs Tanin ⊕ → Karish ⊕ (FPSO) → Dor marine receiving station (תחנת קבלה ימית,
cyan circle-R). It must pass through the CENTRE of each point-anchor.

This script, per segment between consecutive anchors:
  1. BFS-shortest-paths the white band between two points just outside each circle
     (bright-over-sea mask, dilated for connectivity — same as extract_offshore_lines);
  2. recenters every path point onto the band's bright-fill midpoint along the local
     perpendicular (same routine as recenter_traces.py), tapering to the band ends;
then stitches: [Tanin_ctr, segA…, Karish_ctr, segB…, Dor_ctr] with the anchor centres
pinned exactly, so the route passes dead-through each ⊕/○ marker. Writes
traces/trace_karish_centerline.geojson (overwrites) + overlays/retrace_karish.png.
"""
import json
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance
from pyproj import Transformer
from scipy import ndimage
from shapely.geometry import LineString

HERE = Path(__file__).parent
P = json.load(open(HERE / "georef_params.json"))
base = Image.open(HERE / "maps" / "ingl_big_map_fullres.jpg").convert("RGB")
a = np.asarray(base, dtype=np.int16)
H, W = a.shape[:2]

# --- masks -----------------------------------------------------------------
sea = (np.abs(a - np.array([102, 165, 244])).sum(axis=2) < 60)
sea_wide = ndimage.binary_dilation(sea, iterations=12)
bright = (a[..., 0] > 190) & (a[..., 1] > 215) & (a[..., 2] > 225)
BFS_MASK = ndimage.binary_dilation(bright & sea_wide, iterations=3)
FILL = (a[..., 0] > 180) & (a[..., 1] > 205) & (a[..., 2] > 200)  # centerline recenter

# TAPER kept minimal: segment ends are replaced by pinned anchor centres, so the band
# should stay centered right up to each circle (a large taper would revert to the dark
# edge near the anchor and notch the join).
WINDOW, STEP, TANGENT_K, SMOOTH_K, TAPER = 16.0, 0.5, 3, 9, 1
MAX_RUN_PX = 11.0   # a fill run wider than this = a crossing/merge → don't recenter (stay straight)
MAX_OFFSET_PX = 9.0  # never shift a point more than this (crossings/clutter guard)

# --- anchor centres (px), symmetry-detected --------------------------------
ANCHORS = {"Tanin": (415, 375), "Karish": (816, 256), "Dor": (1399, 995)}
# band points just OUTSIDE each circle, on the band toward the neighbour anchor
SEG_ENDS = {
    "A": [(429, 371), (802, 260)],   # Tanin-side  -> Karish-side (future leg)
    "B": [(829, 269), (1390, 984)],  # Karish-side -> Dor-side (operating export)
}


def snap(x, y, r=40):
    ys, xs = np.nonzero(BFS_MASK[max(0, y - r):y + r, max(0, x - r):x + r])
    if not len(xs):
        raise SystemExit(f"no band pixel near ({x},{y})")
    d = (xs + max(0, x - r) - x) ** 2 + (ys + max(0, y - r) - y) ** 2
    i = d.argmin()
    return int(xs[i] + max(0, x - r)), int(ys[i] + max(0, y - r))


def bfs(p0, p1):
    sx, sy = snap(*p0); ex, ey = snap(*p1)
    prev = np.full((H, W), -1, dtype=np.int64)
    q = deque([(sx, sy)]); prev[sy, sx] = sy * W + sx
    steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    while q:
        x, y = q.popleft()
        if (x, y) == (ex, ey):
            break
        for dy, dx in steps:
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H and BFS_MASK[ny, nx] and prev[ny, nx] < 0:
                prev[ny, nx] = y * W + x; q.append((nx, ny))
    else:
        raise SystemExit(f"no path {p0}->{p1}")
    path = [(ex, ey)]
    while path[-1] != (sx, sy):
        p_ = prev[path[-1][1], path[-1][0]]; path.append((int(p_ % W), int(p_ // W)))
    path.reverse()
    return [tuple(c) for c in LineString(path).simplify(2.0).coords]


def densify(pts, step=1.5):
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = max(1, int(np.hypot(x1 - x0, y1 - y0) / step))
        for i in range(1, n + 1):
            t = i / n; out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return out


def fill_at(x, y):
    xi, yi = int(round(x)), int(round(y))
    return 0 <= xi < W and 0 <= yi < H and FILL[yi, xi]


def recenter(px_path):
    arr = np.array(densify(px_path)); n = len(arr)
    ts = np.arange(-WINDOW, WINDOW + 1e-9, STEP); offs = np.zeros(n)
    for i in range(n):
        j0, j1 = max(0, i - TANGENT_K), min(n - 1, i + TANGENT_K)
        tx, ty = arr[j1] - arr[j0]; nrm = np.hypot(tx, ty)
        if nrm < 1e-6:
            continue
        perp = np.array([-ty, tx]) / nrm; x, y = arr[i]
        hits = np.array([fill_at(x + t * perp[0], y + t * perp[1]) for t in ts])
        if not hits.any():
            continue
        runs, s = [], None
        for k, h in enumerate(hits):
            if h and s is None:
                s = k
            elif not h and s is not None:
                runs.append((s, k - 1)); s = None
        if s is not None:
            runs.append((s, len(hits) - 1))
        b = min(runs, key=lambda r: abs((ts[r[0]] + ts[r[1]]) / 2))
        run_w = ts[b[1]] - ts[b[0]]
        if run_w > MAX_RUN_PX:      # crossing/merge — keep the straight guide point
            continue
        o = (ts[b[0]] + ts[b[1]]) / 2
        offs[i] = max(-MAX_OFFSET_PX, min(MAX_OFFSET_PX, o))
    if n >= SMOOTH_K:
        offs = np.convolve(offs, np.ones(SMOOTH_K) / SMOOTH_K, mode="same")
    ramp = np.array([min(1.0, i / TAPER, (n - 1 - i) / TAPER) for i in range(n)])
    offs *= ramp
    out = arr.astype(float).copy()
    for i in range(n):
        j0, j1 = max(0, i - TANGENT_K), min(n - 1, i + TANGENT_K)
        tx, ty = arr[j1] - arr[j0]; nrm = np.hypot(tx, ty)
        if nrm < 1e-6:
            continue
        perp = np.array([-ty, tx]) / nrm; out[i] = arr[i] + offs[i] * perp
    return [tuple(p) for p in out]


def main():
    segA = recenter(bfs(*SEG_ENDS["A"]))
    segB = recenter(bfs(*SEG_ENDS["B"]))
    px = [ANCHORS["Tanin"]] + segA + [ANCHORS["Karish"]] + segB + [ANCHORS["Dor"]]

    to_wgs = Transformer.from_crs(2039, 4326, always_xy=True)
    to_itm = Transformer.from_crs(4326, 2039, always_xy=True)
    cc = []
    for x, y in px:
        E = P["e_per_px"] * x + P["e_intercept"]; N = P["n_per_px"] * y + P["n_intercept"]
        lon, lat = to_wgs.transform(E, N); cc.append([round(lon, 6), round(lat, 6)])
    ls = LineString(cc).simplify(0.00015)
    cc = [[round(a_, 6), round(b_, 6)] for a_, b_ in ls.coords]
    # re-pin the three anchor centres exactly (simplify may nudge endpoints/joins)
    anc_wgs = {}
    for tag, (x, y) in ANCHORS.items():
        E = P["e_per_px"] * x + P["e_intercept"]; N = P["n_per_px"] * y + P["n_intercept"]
        lon, lat = to_wgs.transform(E, N); anc_wgs[tag] = [round(lon, 6), round(lat, 6)]
    cc[0], cc[-1] = anc_wgs["Tanin"], anc_wgs["Dor"]

    itm = [to_itm.transform(*c) for c in cc]
    length_km = LineString(itm).length / 1000
    print(f"karish/tanin: {len(cc)} verts, length {length_km:.1f} km "
          f"(Tanin→Karish future leg + Karish→Dor export)")

    gj = {"type": "FeatureCollection", "name": "karish_tanin_centerline", "crs": None,
          "features": [{"type": "Feature", "properties": {
              "name": "karish_tanin_centerline",
              "source": "trace of INGL transmission map (ingl.co.il), gas-suppliers band "
                        "centerline; routed through legend point-anchors "
                        "Tanin ⊕ → Karish ⊕ (FPSO) → Dor ○ (marine receiving station)",
              "anchors": anc_wgs,
              "note": "Tanin→Karish leg is drawn as a FUTURE line (קו עתידי); "
                      "Karish→Dor is the operating export line.",
              "length_km": round(length_km, 1)},
              "geometry": {"type": "LineString", "coordinates": cc}}]}
    out = HERE / "traces" / "trace_karish_centerline.geojson"
    out.write_text(json.dumps(gj, ensure_ascii=False))
    print(f"wrote {out.name}")

    viz = ImageEnhance.Brightness(base).enhance(0.6); dr = ImageDraw.Draw(viz)
    dr.line([tuple(p) for p in px], fill=(0, 220, 255), width=2)
    for tag, (x, y) in ANCHORS.items():
        dr.ellipse([x - 11, y - 11, x + 11, y + 11], outline=(255, 60, 60), width=2)
    xs = [p[0] for p in px]; ys = [p[1] for p in px]
    crop = viz.crop((int(max(0, min(xs) - 80)), int(max(0, min(ys) - 80)),
                     int(min(W, max(xs) + 80)), int(min(H, max(ys) + 80))))
    if max(crop.size) > 1600:
        r = 1600 / max(crop.size); crop = crop.resize((int(crop.width * r), int(crop.height * r)))
    crop.save(HERE / "overlays" / "retrace_karish.png")
    print("wrote overlays/retrace_karish.png")


if __name__ == "__main__":
    main()
