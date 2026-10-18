"""Trace the two lines on the Producers Midstream asset map into pixel polylines (second pass).

The first pass thresholded the JPEG and skeletonized it, which broke the Residue Header into pieces and
left the Palo Duro line a little off center. This pass works on a 4x enlargement with soft color scores:

- Palo Duro (yellow, nearly north-south): one vertex per image row at the yellow-weighted center of
  that row, so the line follows the drawn centerline.
- Residue Header (dark red): skeleton of the red score, spurs dropped, gaps bridged, each vertex moved
  to the local red-weighted center. The longest path through the skeleton is the mainline; every other
  chain is a branch that starts at its junction vertex on the mainline.
- The top of the Palo Duro line is snapped onto the header mainline and that point is inserted into
  the mainline, so the two lines share a vertex.

Usage: python retrace.py map.jpg
Writes trace_palo_duro_v2.json, trace_residue_header_v2.json (pixel coordinates of the ORIGINAL
image) and overlay_v2.png.
"""
import json, sys
import numpy as np
import networkx as nx
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely.geometry import LineString, Point
from skimage.morphology import skeletonize, remove_small_objects

S = 4
img = sys.argv[1]
src = Image.open(img).convert("RGB")
big = src.resize((src.width * S, src.height * S), Image.LANCZOS)
im = np.array(big).astype(float)
R, G, B = im[..., 0], im[..., 1], im[..., 2]
H, W = R.shape
legend = np.zeros((H, W), bool); legend[420 * S:540 * S, 400 * S:580 * S] = True

lum = (R + G + B) / 3
# dark and reddish: the maroon line is the only dark red thing on the map; the header sits above row 180
red_score = np.clip((200 - lum) / 60, 0, 1) * np.clip((R - np.maximum(G, B) - 5) / 25, 0, 1) * ~legend
red_score[180 * S:] = 0
yel_score = np.clip((np.minimum(R, G) - B - 40) / 60, 0, 1) * (R > 160) * (G > 130) * ~legend

NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def centroid_refine(score, pts, rad=7):
    """Move each (x, y) to the score-weighted center of a (2 rad + 1) window around it."""
    out = []
    for x, y in pts:
        x0, x1 = max(0, x - rad), min(W, x + rad + 1); y0, y1 = max(0, y - rad), min(H, y + rad + 1)
        w = score[y0:y1, x0:x1]
        if w.sum() < 1e-6:
            out.append((float(x), float(y))); continue
        yy, xx = np.mgrid[y0:y1, x0:x1]
        out.append((float((w * xx).sum() / w.sum()), float((w * yy).sum() / w.sum())))
    return out


def smooth(pts, k=5):
    if len(pts) < k:
        return pts
    a = np.array(pts); ker = np.ones(k) / k
    xs = np.convolve(np.pad(a[:, 0], (k // 2, k // 2), mode="edge"), ker, "valid")
    ys = np.convolve(np.pad(a[:, 1], (k // 2, k // 2), mode="edge"), ker, "valid")
    xs[0], ys[0], xs[-1], ys[-1] = a[0, 0], a[0, 1], a[-1, 0], a[-1, 1]
    return list(zip(xs, ys))


# ---------------------------------------------------------------- Palo Duro: one vertex per row
ym = yel_score > 0.5
ym = remove_small_objects(ym, max_size=200)
rows = np.nonzero(ym.any(1))[0]
pd_pts = []
for y in range(rows.min(), rows.max() + 1):
    w = yel_score[y]
    if w.sum() < 0.5:
        continue
    pd_pts.append((float((w * np.arange(W)).sum() / w.sum()), float(y)))
pd_pts = smooth(pd_pts, 9)

# ---------------------------------------------------------------- Residue Header: skeleton graph
rm = ndimage.binary_closing(red_score > 0.5, iterations=3)
rm = remove_small_objects(rm, max_size=60)
sk = skeletonize(rm)
pts = set(zip(*np.nonzero(sk)))


def nbrs(p):
    return [(p[0] + a, p[1] + b) for a, b in NB if (p[0] + a, p[1] + b) in pts]


deg = {p: len(nbrs(p)) for p in pts}
nodes = {p for p in pts if deg[p] != 2}
seen = set(); chains = []
for n in nodes:
    for q in nbrs(n):
        if (n, q) in seen:
            continue
        path = [n, q]; seen.add((n, q)); seen.add((q, n))
        prev, cur = n, q
        while cur not in nodes:
            nx_ = [r for r in nbrs(cur) if r != prev and r not in path[-3:]]
            if not nx_:
                break
            prev, cur = cur, nx_[0]; path.append(cur)
            seen.add((prev, cur)); seen.add((cur, prev))
        chains.append(path)

# graph of chains; drop spurs shorter than 6 original px that end free, repeat until stable
Gr = nx.Graph()
for c in chains:
    Gr.add_edge(c[0], c[-1], pts=c, length=len(c))
changed = True
while changed:
    changed = False
    for u, v, d in list(Gr.edges(data=True)):
        if d["length"] < 6 * S and (Gr.degree(u) == 1 or Gr.degree(v) == 1) and not (Gr.degree(u) == 1 and Gr.degree(v) == 1):
            Gr.remove_edge(u, v); changed = True
    Gr.remove_nodes_from([n for n in list(Gr.nodes) if Gr.degree(n) == 0])

# bridge gaps: a free end within 12 original px of a point on another component joins it
comps = list(nx.connected_components(Gr))
print(f"header skeleton: {len(chains)} chains, {Gr.number_of_edges()} after pruning, {len(comps)} components")
while len(comps) > 1:
    best = None
    for ci in comps:
        ends = [n for n in ci if Gr.degree(n) == 1]
        for e in ends:
            for cj in comps:
                if cj is ci:
                    continue
                for u, v, d in Gr.subgraph(cj).edges(data=True):
                    arr = np.array(d["pts"])
                    dist = np.hypot(arr[:, 0] - e[0], arr[:, 1] - e[1]); k = int(dist.argmin())
                    if best is None or dist[k] < best[0]:
                        best = (dist[k], e, (u, v), k)
    if best is None or best[0] > 12 * S:
        # what is left apart is a stray blob, not line: keep the largest component and say what was dropped
        sizes = sorted(comps, key=lambda c: sum(d["length"] for _, _, d in Gr.subgraph(c).edges(data=True)), reverse=True)
        for c in sizes[1:]:
            xs = [n[1] / S for n in c]; ys = [n[0] / S for n in c]
            print(f"dropped a stray component of {len(c)} nodes near ({np.mean(xs):.0f}, {np.mean(ys):.0f}), {best[0] / S:.1f} px from the line")
            Gr.remove_nodes_from(c)
        break
    dist, e, (u, v), k = best
    d = Gr.edges[u, v]; c = d["pts"]; m = c[k]
    Gr.remove_edge(u, v)
    Gr.add_edge(u, m, pts=c[:k + 1], length=k + 1); Gr.add_edge(m, v, pts=c[k:], length=len(c) - k)
    Gr.add_edge(e, m, pts=[e, m], length=int(dist))
    print(f"bridged a {dist / S:.1f} px gap at ({m[1] / S:.0f}, {m[0] / S:.0f})")
    comps = list(nx.connected_components(Gr))

# merge degree-2 nodes left by pruning so chains are maximal
for n in [n for n in list(Gr.nodes) if Gr.degree(n) == 2]:
    nb = [(v, Gr.edges[n, v]) for v in Gr.neighbors(n)]
    if len(nb) != 2 or n not in Gr:
        continue
    (a, da), (b, db) = nb
    pa = da["pts"] if da["pts"][-1] == n else da["pts"][::-1]
    pb = db["pts"] if db["pts"][0] == n else db["pts"][::-1]
    Gr.remove_node(n); Gr.add_edge(a, b, pts=pa + pb[1:], length=len(pa) + len(pb) - 1)

# mainline = longest path between leaves (by pixel length)
leaves = [n for n in Gr.nodes if Gr.degree(n) == 1]
best = (0, None)
for i, a in enumerate(leaves):
    for b in leaves[i + 1:]:
        L = nx.shortest_path_length(Gr, a, b, weight="length")
        if L > best[0]:
            best = (L, (a, b))
main_nodes = nx.shortest_path(Gr, *best[1], weight="length")


def chain_pts(a, b):
    c = Gr.edges[a, b]["pts"]
    return c if c[0] == a else c[::-1]


main = []
for a, b in zip(main_nodes, main_nodes[1:]):
    c = chain_pts(a, b); main += c if not main else c[1:]
main_set = set(main_nodes)
branches = []
for u, v, d in Gr.edges(data=True):
    if u in main_set and v in main_set and main_nodes.index(u) + 1 == main_nodes.index(v) or \
       u in main_set and v in main_set and main_nodes.index(v) + 1 == main_nodes.index(u):
        continue
    if u in main_set:
        branches.append(chain_pts(u, v))
    elif v in main_set:
        branches.append(chain_pts(v, u))
    else:
        branches.append(d["pts"])
# skeleton stubs at junctions and bends are not branches: a branch is at least 6 original px long
branches = [b for b in branches if LineString([(c, r) for r, c in b]).length >= 6 * S]
print(f"header: mainline {len(main)} skeleton px, {len(branches)} branches of {[len(b) for b in branches]} px")

# (row, col) -> (x, y), refine to the red-weighted center, smooth
def finish(chain, score):
    xy = [(c, r) for r, c in chain]
    xy = centroid_refine(score, [(int(x), int(y)) for x, y in xy])
    return smooth(xy, 7)

main_xy = finish(main, red_score)
branch_xy = [finish(b, red_score) for b in branches]
pd_xy = pd_pts

# ---------------------------------------------------------------- snap Palo Duro onto the header
ml = LineString(main_xy)
top = Point(pd_xy[0]) if pd_xy[0][1] < pd_xy[-1][1] else Point(pd_xy[-1])
snap = ml.interpolate(ml.project(top))
snap_xy = (snap.x, snap.y)
# insert the shared vertex into the mainline at its position along the line
d_along = ml.project(top); acc = 0; ins = len(main_xy)
for i in range(1, len(main_xy)):
    acc += Point(main_xy[i - 1]).distance(Point(main_xy[i]))
    if acc >= d_along:
        ins = i; break
main_xy = main_xy[:ins] + [snap_xy] + main_xy[ins:]
if pd_xy[0][1] < pd_xy[-1][1]:
    pd_xy = [snap_xy] + pd_xy[1:]
else:
    pd_xy = pd_xy[:-1] + [snap_xy]
print(f"Palo Duro top snapped to the header at ({snap_xy[0] / S:.1f}, {snap_xy[1] / S:.1f}), moved {top.distance(snap) / S:.1f} px")
# branches whose first vertex sits on the mainline share that vertex exactly
for b in branch_xy:
    p = Point(b[0]); q = ml.interpolate(ml.project(p))
    if p.distance(q) < 2 * S:
        b[0] = (q.x, q.y)


# tiny laterals (1-3 px nubs) that the spur pruning cannot tell from junction stubs: Baird pointed at two,
# at about (354, 90) and (384, 124) in original pixels. Each is read from the red pixels there: the red
# that sticks out past the line's own half-width (5 px at 4x) within 8 px of the spot, tip = farthest such
# pixel from the mainline, junction = its foot on the mainline. No red sticking out = no branch, and a note.
NUBS = [(354, 90), (384, 124)]
for nx0, ny0 in NUBS:
    ys, xs = np.nonzero(red_score[(ny0 - 8) * S:(ny0 + 8) * S, (nx0 - 8) * S:(nx0 + 8) * S] > 0.5)
    cand = [(x + (nx0 - 8) * S, y + (ny0 - 8) * S) for x, y in zip(xs, ys)]
    far = [(ml.distance(Point(c)), c) for c in cand if ml.distance(Point(c)) > 5]
    if not far:
        print(f"nub near ({nx0}, {ny0}): no red beyond the line width, nothing traced"); continue
    dmax, tip = max(far)
    # a few pixels at the tip average out jpeg noise; keep only the ones on the tip's side of the line
    tip_pts = [c for d, c in far if d > dmax - 2 * 1.0]
    tip = (float(np.mean([c[0] for c in tip_pts])), float(np.mean([c[1] for c in tip_pts])))
    foot = ml.interpolate(ml.project(Point(tip)))
    branch_xy.append([(foot.x, foot.y), tip])
    print(f"nub near ({nx0}, {ny0}): {len(far)} red px beyond the line width, tip ({tip[0] / S:.1f}, {tip[1] / S:.1f}), "
          f"{dmax / S:.1f} px from the mainline, {len(tip_pts)} px averaged at the tip")


def simplify(xy, tol=0.6):
    return [list(c) for c in LineString(xy).simplify(tol, preserve_topology=False).coords]


def to_orig(xy):
    return [[round(x / S, 2), round(y / S, 2)] for x, y in xy]


pd_out = to_orig(simplify(pd_xy))
hdr_out = [to_orig(simplify(main_xy))] + [to_orig(simplify(b)) for b in branch_xy]
json.dump({"image": img, "polylines": [pd_out],
           "notes": f"Palo Duro Pipeline (yellow): yellow-weighted row centers on a {S}x enlargement, top vertex shared with the Residue Header mainline; {len(pd_out)} vertices after simplification (retrace.py)"},
          open("trace_palo_duro_v2.json", "w"), indent=1)
json.dump({"image": img, "polylines": hdr_out,
           "notes": f"PDM Residue Header (dark red): skeleton on a {S}x enlargement, vertices moved to the red-weighted center; polyline 0 is the mainline (west end to east end, {len(hdr_out[0])} vertices), the rest are branches starting at their junction on the mainline; the last {len(NUBS)} are the tiny laterals Baird pointed at, read as junction and tip only (retrace.py)"},
          open("trace_residue_header_v2.json", "w"), indent=1)

# overlay on the enlarged image, header area and whole map
ov = big.copy(); dr = ImageDraw.Draw(ov)
dr.line([(x * S, y * S) for x, y in pd_out], fill=(0, 90, 255), width=2)
dr.line([(x * S, y * S) for x, y in hdr_out[0]], fill=(0, 170, 0), width=2)
for b in hdr_out[1:]:
    dr.line([(x * S, y * S) for x, y in b], fill=(255, 0, 255), width=2)
for x, y in hdr_out[0]:
    dr.ellipse([x * S - 2, y * S - 2, x * S + 2, y * S + 2], outline=(0, 100, 0))
ov.crop((150 * S, 30 * S, 440 * S, 170 * S)).save("overlay_v2_header.png")
for i, (nx0, ny0) in enumerate(NUBS):
    ov.crop(((nx0 - 10) * S, (ny0 - 10) * S, (nx0 + 10) * S, (ny0 + 10) * S)).resize((400, 400), Image.NEAREST).save(f"overlay_v2_nub{i + 1}.png")
ov.crop((230 * S, 110 * S, 310 * S, 760 * S)).resize((80 * 2, 650 * 2)).save("overlay_v2_palo_duro.png")
print("wrote trace_*_v2.json, overlay_v2_header.png, overlay_v2_palo_duro.png")
