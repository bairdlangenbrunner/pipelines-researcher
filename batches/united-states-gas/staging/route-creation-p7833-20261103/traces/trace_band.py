"""Dense centerline of the magenta 'S Mississippi Project' band (dark dashes plus the pale pink outline
around the gaps) on page 1 of Energy Transfer's binding open season notice (map dated 10/9/2026).
Pixels only; lon/lat come from georef.py.

1. Upsample the window x 520-670, y 565-665 by 4 (bicubic) so the thinned line is smooth.
2. Mask every magenta-ish pixel, (r+b)/2 - g > 28 with r,b > g; close small gaps, fill holes
   (the white centers of the outlined gaps), and keep the component that holds the dark dashes.
   The label text is a separate component and drops out.
3. Thin to a one-pixel skeleton and take the longest path through it (graph diameter),
   which runs from the Perryville star rim to the arrowhead tip; short side spurs drop out.
4. Smooth along the path (Gaussian, sigma 2 px of arc) to drop dash jitter, prepend the star
   center (blue fill), simplify at 0.15 original pixels, write in original pixels.
Usage: python -I trace_band.py <map.jpg> <trace.json>"""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize
import networkx as nx
from shapely.geometry import LineString

img, out = sys.argv[1], sys.argv[2]
X0, Y0, X1, Y1, S = 520, 565, 670, 665, 4
full = Image.open(img).convert("RGB")
a = np.array(full.crop((X0, Y0, X1, Y1)).resize(((X1 - X0) * S, (Y1 - Y0) * S), Image.BICUBIC)).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
m = ((r + b) / 2 - g > 28) & (r > g) & (b > g)
dark = (r > 120) & (b > 140) & (g < 90)
m = ndimage.binary_closing(m, structure=np.ones((5, 5)))
m = ndimage.binary_fill_holes(m)
lab, n = ndimage.label(m, structure=np.ones((3, 3)))
sizes = ndimage.sum(dark, lab, range(1, n + 1))
keep = 1 + int(np.argmax(sizes))
band = lab == keep
sk = skeletonize(band)
ys, xs = np.nonzero(sk)
G = nx.Graph()
idx = {(y, x) for y, x in zip(ys, xs)}
for y, x in idx:
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if (dy or dx) and (y + dy, x + dx) in idx:
                G.add_edge((y, x), (y + dy, x + dx), weight=(dy * dy + dx * dx) ** 0.5)
# graph diameter via two Dijkstra sweeps
s0 = next(iter(G.nodes))
d = nx.single_source_dijkstra_path_length(G, s0); u = max(d, key=d.get)
d, paths = nx.single_source_dijkstra(G, u); v = max(d, key=d.get)
path = paths[v]
if path[0][1] > path[-1][1]:  # start at the west (star) end
    path = path[::-1]
P = np.array([(X0 + (x + 0.5) / S - 0.5, Y0 + (y + 0.5) / S - 0.5) for y, x in path])
# Smooth along the path (Gaussian, sigma 2 original pixels of arc length) to remove the dash-by-dash
# jitter of the JPEG blobs while keeping the bends; the two ends are held fixed.
step = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
SIG = 2.0
Q = P.copy()
for i in range(1, len(P) - 1):
    w = np.exp(-0.5 * ((step - step[i]) / SIG) ** 2)
    Q[i] = (w[:, None] * P).sum(0) / w.sum()
pts = [tuple(q) for q in Q]
fa = np.array(full).astype(int)
fr, fg, fb = fa[..., 0], fa[..., 1], fa[..., 2]
sb = (fb > 180) & (fr < 80) & (fg < 120); sw = np.zeros_like(sb); sw[570:595, 522:548] = True
sy, sx = np.nonzero(sb & sw)
star = (float(sx.mean()), float(sy.mean()))
ls = LineString([star] + pts).simplify(0.15)
line = [[round(x, 2), round(y, 2)] for x, y in ls.coords]
json.dump({"image": "maps/et_binding_open_season_20261028_p1_map.jpg", "polylines": [line],
           "notes": "Centerline of the whole magenta band (dashes and the pale outline around the gaps), thinned at 4x upsampling, longest skeleton path from the Perryville star rim to the arrowhead tip, star center prepended, smoothed along the path (sigma 2 px), simplified at 0.15 px."},
          open(out, "w"), indent=1)
print(len(line), "points; skeleton path", len(path), "px; band px", int(band.sum()))
