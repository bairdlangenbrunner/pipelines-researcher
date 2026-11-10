"""Trace the blue pipeline band on the Lowman Pipeline company map.
Usage: python trace_band.py <map.jpg> <out trace.json>
Colour-masks the blue band, thins it to a one-pixel line at 4x size, takes the longest path
end to end, simplifies it and smooths it. Output is pixels only."""
import sys, json, numpy as np, networkx as nx
from PIL import Image
from skimage.morphology import skeletonize
from scipy.ndimage import gaussian_filter1d
src, out = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert('RGB')).astype(int)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
mask = (b > 180) & (r < 120) & (g > 100) & (g < 210)
# drop the north-arrow icon area (top right of the detail map)
mask[:70, 600:] = False
mask[:, 640:] = False
big = np.kron(mask, np.ones((4, 4), bool))
sk = skeletonize(big)
ys, xs = np.nonzero(sk)
pts = set(zip(ys, xs))
G = nx.Graph()
for (y, x) in pts:
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if (dy or dx) and (y + dy, x + dx) in pts:
                G.add_edge((y, x), (y + dy, x + dx), weight=(dy * dy + dx * dx) ** .5)
comp = max(nx.connected_components(G), key=len)
G = G.subgraph(comp)
a = min(G.nodes, key=lambda p: (p[0], p[1]))
d1 = nx.single_source_dijkstra_path_length(G, a)
b_ = max(d1, key=d1.get)
d2 = nx.single_source_dijkstra_path_length(G, b_)
c_ = max(d2, key=d2.get)
path = nx.dijkstra_path(G, b_, c_)
P = np.array([[x / 4 + .375, y / 4 + .375] for y, x in path])
if P[0, 1] > P[-1, 1]:
    P = P[::-1]
# resample every 2 px then smooth
d = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
n = int(d[-1] / 2) + 1
t = np.linspace(0, d[-1], n)
Q = np.c_[np.interp(t, d, P[:, 0]), np.interp(t, d, P[:, 1])]
Qs = np.c_[gaussian_filter1d(Q[:, 0], 2, mode='nearest'), gaussian_filter1d(Q[:, 1], 2, mode='nearest')]
Qs[0], Qs[-1] = Q[0], Q[-1]
json.dump({"image": src.split('/')[-1], "polylines": [[[round(float(x), 2), round(float(y), 2)] for x, y in Qs]],
           "notes": "centerline of the blue band, pixels only"}, open(out, 'w'))
print(len(Qs), 'points; start', Qs[0], 'end', Qs[-1])
