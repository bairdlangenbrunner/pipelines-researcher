"""Calibrated milepost cutter on the P0271 network.
master path through stations in order; MP(chain) anchored at known station mileposts (piecewise linear)."""
import json, sys, bisect, networkx as nx
sys.path.insert(0, '.')
from cut import load, snap, G_
ST = json.load(open('echo/stations.json'))
def stpt(n):
    r = [x for x in ST.get(str(n), []) if x.get('lat')]
    return (r[0]['lon'], r[0]['lat']) if r else None
_G = None
def graph():
    global _G
    if _G is None: _G = load()
    return _G
def master(pts):
    G, nodes, t = graph(); path = []; idx = []; snaps = []
    sn = [snap(G, nodes, t, p) for p in pts]
    for (a, da), (b, db) in zip(sn, sn[1:]):
        seg = nx.shortest_path(G, a, b, weight='weight')
        if not path: path = seg; idx.append(0)
        else: path += seg[1:]
        idx.append(len(path) - 1)
    cum = [0.0]
    for u, v in zip(path, path[1:]): cum.append(cum[-1] + G_.inv(u[0], u[1], v[0], v[1])[2]/1609.344)
    return path, cum, [cum[i] for i in idx], [d for _, d in sn]
def calib(anchors):  # anchors: list of (chain, mp) sorted
    def f(mp):
        a = anchors
        if mp <= a[0][1]: (c0, m0), (c1, m1) = a[0], a[1]
        elif mp >= a[-1][1]: (c0, m0), (c1, m1) = a[-2], a[-1]
        else:
            i = max(j for j in range(len(a)) if a[j][1] <= mp); (c0, m0), (c1, m1) = a[i], a[i+1]
        return c0 + (mp - m0) * (c1 - c0) / (m1 - m0)
    return f
def interp(path, cum, c):
    i = bisect.bisect_left(cum, c)
    if i <= 0: return list(path[0])
    if i >= len(cum): return list(path[-1])
    u, v = path[i-1], path[i]; t = (c - cum[i-1]) / (cum[i] - cum[i-1] or 1)
    return [round(u[0] + t*(v[0]-u[0]), 6), round(u[1] + t*(v[1]-u[1]), 6)]
def sub(path, cum, c0, c1):
    i0 = bisect.bisect_right(cum, c0); i1 = bisect.bisect_left(cum, c1)
    return [interp(path, cum, c0)] + [list(p) for p in path[i0:i1]] + [interp(path, cum, c1)]
