#!/usr/bin/env python3
"""Semi-automatic extraction of the white offshore supplier lines from the INGL map.

Mask = bright (near-white) pixels over/near sea; per-line, BFS shortest path
between operator-supplied endpoint pixels (snapped to nearest mask pixel),
Douglas-Peucker simplify (shapely), pixel -> ITM (georef_params.json) -> WGS84.
Writes traces/trace_<key>.geojson + overlays/trace_<key>.png for QC.

Usage: python extract_offshore_lines.py <key> x0 y0 x1 y1 [dilate_px]
       python extract_offshore_lines.py --mask     (just write the mask viz)
"""
import json
import sys
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

# sea (or sea-adjacent) so land clutter is excluded; dilate sea generously so the
# mask survives right up to the landfall symbols
sea = (np.abs(a - np.array([102, 165, 244])).sum(axis=2) < 60)
sea_wide = ndimage.binary_dilation(sea, iterations=12)

bright = (a[..., 0] > 190) & (a[..., 1] > 215) & (a[..., 2] > 225)
mask = bright & sea_wide

if "--mask" in sys.argv:
    viz = ImageEnhance.Brightness(base).enhance(0.35)
    va = np.asarray(viz).copy()
    va[mask] = (255, 60, 60)
    Image.fromarray(va).resize((W // 2, H // 2)).save(HERE / "overlays" / "offshore_mask_half.png")
    print("wrote overlays/offshore_mask_half.png")
    sys.exit(0)

key, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6])
dil = int(sys.argv[6]) if len(sys.argv) > 6 else 3
m = ndimage.binary_dilation(mask, iterations=dil)


def snap(x, y):
    ys, xs = np.nonzero(m[max(0, y - 40):y + 40, max(0, x - 40):x + 40])
    if not len(xs):
        raise SystemExit(f"no mask pixel near ({x},{y})")
    d = (xs + max(0, x - 40) - x) ** 2 + (ys + max(0, y - 40) - y) ** 2
    i = d.argmin()
    return int(xs[i] + max(0, x - 40)), int(ys[i] + max(0, y - 40))


sx, sy = snap(x0, y0)
ex, ey = snap(x1, y1)
print(f"snapped: ({sx},{sy}) -> ({ex},{ey})")

# BFS shortest path on the dilated mask
prev = np.full((H, W), -1, dtype=np.int64)
q = deque([(sx, sy)])
prev[sy, sx] = sy * W + sx
steps = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
found = False
while q:
    x, y = q.popleft()
    if (x, y) == (ex, ey):
        found = True
        break
    for dy, dx in steps:
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H and m[ny, nx] and prev[ny, nx] < 0:
            prev[ny, nx] = y * W + x
            q.append((nx, ny))
if not found:
    raise SystemExit("no path — endpoints not connected on mask (try higher dilate)")

path = [(ex, ey)]
while path[-1] != (sx, sy):
    p_ = prev[path[-1][1], path[-1][0]]
    path.append((int(p_ % W), int(p_ // W)))
path.reverse()
print(f"raw path: {len(path)} px")

ls = LineString(path).simplify(2.0)
px_pts = list(ls.coords)
print(f"simplified: {len(px_pts)} vertices")

to_wgs = Transformer.from_crs(2039, 4326, always_xy=True)
coords = []
for x, y in px_pts:
    E = P["e_per_px"] * x + P["e_intercept"]
    N = P["n_per_px"] * y + P["n_intercept"]
    lon, lat = to_wgs.transform(E, N)
    coords.append([round(lon, 6), round(lat, 6)])

km = LineString([(c[0], c[1]) for c in coords])
# rough length: project to ITM meters
to_itm = Transformer.from_crs(4326, 2039, always_xy=True)
itm = [to_itm.transform(*c) for c in coords]
length_km = LineString(itm).length / 1000
print(f"length: {length_km:.1f} km")

gj = {"type": "FeatureCollection", "name": key, "crs": None, "features": [{
    "type": "Feature",
    "properties": {"name": key, "source": "trace of INGL transmission map (ingl.co.il)",
                   "length_km": round(length_km, 1)},
    "geometry": {"type": "LineString", "coordinates": coords}}]}
out = HERE / "traces" / f"trace_{key}.geojson"
out.write_text(json.dumps(gj))
print(f"wrote {out.name}")

viz = ImageEnhance.Brightness(base).enhance(0.55)
d = ImageDraw.Draw(viz)
d.line([(x, y) for x, y in px_pts], fill=(255, 0, 200), width=4)
xs = [p[0] for p in px_pts]; ys = [p[1] for p in px_pts]
c = viz.crop((int(max(0, min(xs) - 100)), int(max(0, min(ys) - 100)),
              int(min(W, max(xs) + 100)), int(min(H, max(ys) + 100))))
if max(c.size) > 1400:
    r = 1400 / max(c.size)
    c = c.resize((int(c.width * r), int(c.height * r)))
c.save(HERE / "overlays" / f"trace_{key}.png")
print(f"wrote overlays/trace_{key}.png")
