"""Cut a sub-route out of the P0271 Transco system geometry: shortest path along the
network between two points (each snapped to the nearest network vertex).
usage: cut.py lon,lat lon,lat out.geojson [--via lon,lat] ; prints snap distances + length."""
import json, sys, math, networkx as nx
from pyproj import Geod
G_ = Geod(ellps='WGS84')
SRC = '/Users/baird/Dropbox/_git_ALL/_github-repos-gem/GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines/P0271.geojson'
def key(c): return (round(c[0], 5), round(c[1], 5))
def keep(p):
    p = {k: v for k, v in p.items() if v not in (None, '')}
    if p.get('usage') == 'administrative' or any(k.startswith('tiger') for k in p): return False
    if 'Cardinal' in str(p.get('substance', '')): return False
    return True
def load():
    d = json.load(open(SRC)); G = nx.Graph()
    for f in d['features']:
        if not keep(f['properties']): continue
        g = f['geometry']; parts = g['coordinates'] if g['type'] == 'MultiLineString' else [g['coordinates']]
        for p in parts:
            for a, b in zip(p, p[1:]):
                ka, kb = key(a), key(b)
                if ka == kb: continue
                w = G_.inv(ka[0], ka[1], kb[0], kb[1])[2]
                G.add_edge(ka, kb, weight=w)
    # bridge tiny gaps (<60 m) between components so noding misses don't break paths
    import numpy as np
    from scipy.spatial import cKDTree
    nodes = list(G.nodes); arr = np.array([[n[0]*math.cos(math.radians(35)), n[1]] for n in nodes])
    t = cKDTree(arr); comp = {}
    for i, c in enumerate(nx.connected_components(G)):
        for n in c: comp[n] = i
    for i, j in t.query_pairs(60/111000):
        a, b = nodes[i], nodes[j]
        if comp[a] != comp[b] and not G.has_edge(a, b):
            G.add_edge(a, b, weight=G_.inv(a[0], a[1], b[0], b[1])[2], bridge=True)
    # T-junctions: join dangling ends to the nearest vertex of another line within 400 m
    nodes = list(G.nodes); arr = np.array([[n[0]*math.cos(math.radians(35)), n[1]] for n in nodes]); t = cKDTree(arr)
    idx = {n: i for i, n in enumerate(nodes)}
    for n in [n for n in nodes if G.degree(n) == 1]:
        near = nx.single_source_dijkstra_path_length(G, n, cutoff=1500, weight='weight')
        best = None
        for j in t.query_ball_point(arr[idx[n]], 400/111000):
            m = nodes[j]
            if m in near: continue
            dd = G_.inv(n[0], n[1], m[0], m[1])[2]
            if best is None or dd < best[0]: best = (dd, m)
        if best: G.add_edge(n, best[1], weight=best[0], bridge=True)
    nodes = list(G.nodes); t = cKDTree(np.array([[n[0]*math.cos(math.radians(35)), n[1]] for n in nodes]))
    return G, nodes, t
def snap(G, nodes, t, pt):
    d, i = t.query([pt[0]*math.cos(math.radians(35)), pt[1]])
    n = nodes[i]; return n, G_.inv(pt[0], pt[1], n[0], n[1])[2]/1000
if __name__ == '__main__':
    a = [float(x) for x in sys.argv[1].split(',')]; b = [float(x) for x in sys.argv[2].split(',')]; out = sys.argv[3]
    via = [[float(x) for x in v.split(',')] for v in sys.argv[4:] if ',' in v]
    G, nodes, t = load(); pts = [a] + via + [b]; path = []; snaps = []
    for p, q in zip(pts, pts[1:]):
        sp, ds = snap(G, nodes, t, p); sq, dq = snap(G, nodes, t, q); snaps += [ds, dq]
        seg = nx.shortest_path(G, sp, sq, weight='weight'); path += seg if not path else seg[1:]
    km = sum(G_.inv(u[0], u[1], v[0], v[1])[2] for u, v in zip(path, path[1:]))/1000
    json.dump({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "LineString", "coordinates": [list(p) for p in path]}}]}, open(out, 'w'))
    print(json.dumps({"km": round(km, 2), "mi": round(km/1.609344, 2), "snap_km": [round(x, 2) for x in snaps], "n": len(path)}))
