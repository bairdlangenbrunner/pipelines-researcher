"""Extract the red 'Proposed Route' line from the FERC Yuma overview map into an ordered pixel polyline.

Full-resolution version (2026-10-17, replaces the 6 px cell tracer, which cut corners): the red mask is
thinned to a one-pixel skeleton, each skeleton component is ordered along its longest path, the pieces
are chained from milepost 0 (northeast end) across the gaps where milepost circles and labels cover the
line, and the pixel staircase is simplified with a 0.8 px tolerance so corners survive.

usage: python trace_red.py <map.jpg> <out trace.json> [mileposts_px.json]
"""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path, connected_components
from skimage.morphology import skeletonize
from shapely.geometry import LineString

img, out = sys.argv[1], sys.argv[2]
mp_file = sys.argv[3] if len(sys.argv) > 3 else None
a = np.asarray(Image.open(img).convert('RGB')).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
m = (r > 150) & (g < 100) & (b < 100) & (r - g > 90)
m[1880:, :] = False                       # drop legend panel
m = ndimage.binary_closing(m, structure=np.ones((3, 3)))
lab, n = ndimage.label(m, structure=np.ones((3, 3)))
sizes = ndimage.sum(m, lab, range(1, n + 1))
m = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= 40])
sk = skeletonize(m)
ys, xs = np.nonzero(sk)
pts = np.column_stack([xs, ys]).astype(float)
idx = {(int(x), int(y)): i for i, (x, y) in enumerate(pts)}
rows, cols, w = [], [], []
for (x, y), i in idx.items():
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            j = idx.get((x + dx, y + dy))
            if j is not None and j != i:
                rows.append(i); cols.append(j); w.append(float(np.hypot(dx, dy)))
G = csr_matrix((w, (rows, cols)), shape=(len(pts), len(pts)))
nc, comp = connected_components(G, directed=False)
segs = []
for c in range(nc):
    ids = np.nonzero(comp == c)[0]
    if len(ids) < 3:
        continue
    sub = G[ids][:, ids]
    d0 = shortest_path(sub, indices=0)
    a_ = int(np.argmax(np.where(np.isinf(d0), -1, d0)))
    da, pred = shortest_path(sub, indices=a_, return_predecessors=True)
    b_ = int(np.argmax(np.where(np.isinf(da), -1, da)))
    path = [b_]
    while path[-1] != a_:
        path.append(pred[path[-1]])
    segs.append(pts[ids[path]])
# chain components, starting at the NE end (milepost 0 = max x)
start = max(range(len(segs)), key=lambda i: max(segs[i][0][0], segs[i][-1][0]))
s = segs.pop(start)
if s[0][0] < s[-1][0]:
    s = s[::-1]
line = [s]; gaps = []
while segs:
    tail = line[-1][-1]
    best = min([(np.hypot(*(tail - sg[0])), i, False) for i, sg in enumerate(segs)] +
               [(np.hypot(*(tail - sg[-1])), i, True) for i, sg in enumerate(segs)])
    dist, i, rev = best
    sg = segs.pop(i)
    if rev:
        sg = sg[::-1]
    gaps.append(round(float(dist), 1))
    line.append(sg)
poly = np.vstack(line)
if mp_file:                               # the line starts at the centre of the milepost 0 marker
    mp0 = json.load(open(mp_file))["0"]
    if np.hypot(*(poly[0] - mp0)) < 20:
        poly = np.vstack([[mp0], poly])
simp = np.array(LineString(poly).simplify(0.8, preserve_topology=False).coords)
poly_out = [[round(float(x), 1), round(float(y), 1)] for x, y in simp]
json.dump({"image": "Updated Yuma Map 8-27-2026.jpg", "polylines": [poly_out],
           "notes": "Pixel centerline of the red 'Proposed Route' symbol from the 3400x2200 FERC map image: color mask (R>150, G<100, B<100, R-G>90), legend panel excluded, thinned to a one-pixel skeleton, ordered along each piece's longest path and chained from milepost 0 (northeast end). Gaps where milepost circles and labels sit on the line are bridged straight; the published line runs continuously under them. The start is extended to the centre of the milepost 0 marker. Simplified at 0.8 px so the pixel staircase drops out and corners stay."},
          open(out, 'w'))
print('skeleton px', len(pts), 'components', len(line), 'raw points', len(poly), 'simplified', len(poly_out),
      'bridged gaps px', sorted(gaps)[-8:], 'n gaps', len(gaps))
