"""ENTSOG SYSCAP 2026 network matcher for the Egypt gas §8 pass (2026-08-07).

Builds a routable graph from the ENTSOG operational traces over the
Egypt/Sinai/AGP window and, for every worklist PID with usable endpoints
(researched endpoints from research_results_*.json — every PID in this batch is
a no-route row, so there is no existing route to borrow endpoints from), finds the shortest network path between them.
Emits a per-PID report (entsog_match_report.json) and an overlay PNG per PID
(overlays/) for human adjudication. NOTHING here writes a candidate — the
adjudicated PIDs are assembled one by one with build_route_candidate.py.

Run from the repo root:
  python3 batches/egypt-gas/staging/route-creation-20260807/entsog_match.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from pyproj import Geod, Transformer
from shapely.geometry import LineString, Point, shape
from shapely.ops import substring, transform as shp_transform, unary_union
from shapely.strtree import STRtree

STAGING = Path(__file__).resolve().parent
ROOT = STAGING.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from route_compare import load_gem_route  # noqa: E402

ENTSOG_DIR = ROOT / "sources/entsog"
GEOD = Geod(ellps="WGS84")
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32636", always_xy=True).transform
TO_LL = Transformer.from_crs("EPSG:32636", "EPSG:4326", always_xy=True).transform

# Egypt + Sinai + AGP-into-Jordan window
WINDOW = (24.0, 21.0, 37.0, 33.5)  # lon0, lat0, lon1, lat1
NODE_SNAP_M = 4000        # merge trace endpoints within this radius into one node
ENDPOINT_SNAP_M = 20000   # max distance from a query endpoint to the network


def utm(geom):
    return shp_transform(TO_UTM, geom)


def load_entsog_lines():
    feats = []
    for status in ("operational", "project"):
        fc = json.load(open(ENTSOG_DIR /
                            f"ENTSOG_GIE_SYSCAP_2026_pipelines_{status}_wgs84.geojson"))
        for f in fc["features"]:
            g = shape(f["geometry"])
            x0, y0, x1, y1 = g.bounds
            if x1 < WINDOW[0] or x0 > WINDOW[2] or y1 < WINDOW[1] or y0 > WINDOW[3]:
                continue
            feats.append((f["properties"], g))
    return feats


def node_network(feats):
    """Snap-bridge nearby stroke endpoints onto other strokes, then unary_union to
    node the network at every crossing. Returns the noded UTM LineStrings."""
    lines = []
    for props, g in feats:
        parts = [g] if g.geom_type == "LineString" else list(g.geoms)
        for ln in parts:
            lu = utm(ln).simplify(50)
            if lu.length > 100:
                lines.append(lu)
    tree = STRtree(lines)
    bridges = []
    for i, ln in enumerate(lines):
        for end in (Point(ln.coords[0]), Point(ln.coords[-1])):
            best, bd = None, NODE_SNAP_M
            for j in tree.query(end.buffer(NODE_SNAP_M)):
                if j == i:
                    continue
                d = lines[j].distance(end)
                if 1.0 < d < bd:
                    bd, best = d, j
            if best is not None:
                p = lines[best].interpolate(lines[best].project(end))
                bridges.append(LineString([end, p]))
    merged = unary_union(lines + bridges)
    segs = list(merged.geoms) if merged.geom_type == "MultiLineString" else [merged]
    return [s for s in segs if s.length > 1]


def build_graph(segs):
    """MultiGraph over the noded segments; nodes keyed by 10 m-rounded coords."""
    G = nx.MultiGraph()

    def nid(c):
        return (round(c[0], -1), round(c[1], -1))

    for s in segs:
        a, b = nid(s.coords[0]), nid(s.coords[-1])
        if a == b and s.length < 100:
            continue
        G.add_edge(a, b, weight=s.length, line=s)
    return G


def insert_point(G, pt_utm, label):
    """Split the nearest edge at pt's projection and add a node there.
    Returns (node_id, snap_distance_m) or (None, dist)."""
    edges = [(u, v, k, d["line"]) for u, v, k, d in G.edges(keys=True, data=True)]
    tree = STRtree([e[3] for e in edges])
    j = int(tree.nearest(pt_utm))
    u, v, k, ln = edges[j]
    # MultiGraph iteration may return (u, v) reversed vs the stored geometry
    if node_point(G, u).distance(Point(ln.coords[0])) > \
       node_point(G, u).distance(Point(ln.coords[-1])):
        u, v = v, u
    d = ln.distance(pt_utm)
    if d > ENDPOINT_SNAP_M:
        return None, d
    t = ln.project(pt_utm)
    node = ("q", label)
    if t < 1 or t > ln.length - 1:
        # projection lands on an existing node
        end = u if t < 1 else v
        # orient: u is the coords[0] end by construction in build_graph
        return end, d
    G.remove_edge(u, v, key=k)
    s1, s2 = substring(ln, 0, t), substring(ln, t, ln.length)
    G.add_node(node, pt=ln.interpolate(t))
    G.add_edge(u, node, weight=s1.length, line=s1)
    G.add_edge(node, v, weight=s2.length, line=s2)
    return node, d


def node_point(G, n):
    p = G.nodes[n].get("pt")
    return p if p is not None else Point(n)


def path_geometry(G, path):
    """Stitch edge geometries along a node path into one UTM LineString."""
    coords: list = []
    for a, b in zip(path, path[1:]):
        best = min(G[a][b].values(), key=lambda d: d["weight"])
        seg = list(best["line"].coords)
        pa = node_point(G, a)
        if Point(seg[0]).distance(pa) > Point(seg[-1]).distance(pa):
            seg = seg[::-1]
        coords += seg
    return LineString(coords).simplify(10)


def main() -> None:
    feats = load_entsog_lines()
    print(f"ENTSOG features in window: {len(feats)}")
    segs = node_network(feats)
    G0 = build_graph(segs)
    print(f"noded graph: {G0.number_of_nodes()} nodes, {G0.number_of_edges()} edges, "
          f"{nx.number_connected_components(G0)} components; "
          f"largest component {max(len(c) for c in nx.connected_components(G0))} nodes")

    wl = json.load(open(STAGING / "worklist.json"))["units"]
    all_lines = [utm(g) for _, g in feats]

    # researched endpoints: research_results_<group>.json, one object per PID
    research = {}
    for f in sorted(STAGING.glob("research_results_*.json")):
        for rec in json.load(open(f)):
            research[rec["project_id"]] = rec

    (STAGING / "overlays").mkdir(exist_ok=True)
    report = []
    for u in wl:
        pid = u["project_id"]
        gj = load_gem_route(pid, "gas")   # expected None for every PID in this batch
        r = research.get(pid) or {}
        s, e = r.get("start") or {}, r.get("end") or {}
        eps, src = None, None
        if s.get("lon") is not None and e.get("lon") is not None:
            eps = (Point(s["lon"], s["lat"]), Point(e["lon"], e["lat"]))
            src = "researched"
        if eps is None:
            report.append({"pid": pid, "name": u["pipeline_name"],
                           "status": "NO_ENDPOINTS",
                           "resolved": bool(r.get("resolved"))})
            continue

        a_utm, b_utm = utm(eps[0]), utm(eps[1])
        G = G0.copy()
        na, da = insert_point(G, a_utm, f"{pid}_a")
        nb, db = insert_point(G, b_utm, f"{pid}_b")
        rec = {"pid": pid, "name": u["pipeline_name"], "endpoint_source": src,
               "sheet_km": u.get("sheet_length_km"),
               "snap_start_km": round(da / 1000, 1), "snap_end_km": round(db / 1000, 1)}
        if na is None or nb is None or na == nb:
            rec["status"] = "NO_NETWORK_MATCH"
            report.append(rec)
            continue
        try:
            path = nx.shortest_path(G, na, nb, weight="weight")
        except nx.NetworkXNoPath:
            rec["status"] = "DISCONNECTED"
            report.append(rec)
            continue
        pg = path_geometry(G, path)
        path_km = pg.length / 1000
        rec.update({"status": "PATH", "path_km": round(path_km, 1),
                    "ratio_vs_sheet": round(path_km / u["sheet_length_km"], 3)
                    if u.get("sheet_length_km") else None,
                    "n_edges": len(path) - 1})
        # offset of existing straight line vs path (info)
        if src == "existing_route":
            ex = utm(shape(gj))
            samples = [pg.interpolate(t, normalized=True) for t in np.linspace(0, 1, 60)]
            rec["mean_offset_km"] = round(float(np.mean([ex.distance(p) for p in samples])) / 1000, 1)
        # write path geojson (raw, pre-assembly) for adjudication
        ll = shp_transform(TO_LL, pg)
        (STAGING / "overlays" / f"{pid}_entsog_path.geojson").write_text(json.dumps({
            "type": "Feature", "properties": {"pid": pid, "path_km": round(path_km, 1)},
            "geometry": {"type": "LineString",
                         "coordinates": [[round(x, 6), round(y, 6)] for x, y in ll.coords]}}))
        report.append(rec)

        # overlay PNG
        fig, ax = plt.subplots(figsize=(7, 7))
        for lu in all_lines:
            xs, ys = lu.xy
            ax.plot(xs, ys, color="#9ecae1", lw=0.6, zorder=1)
        if src == "existing_route":
            exl = utm(shape(gj))
            geoms = [exl] if exl.geom_type == "LineString" else list(exl.geoms)
            for g2 in geoms:
                ax.plot(*g2.xy, color="#888888", lw=1.2, ls="--", zorder=2, label="existing")
        ax.plot(*pg.xy, color="#d62728", lw=1.6, zorder=3, label="ENTSOG path")
        ax.scatter([a_utm.x, b_utm.x], [a_utm.y, b_utm.y], c="k", s=18, zorder=4)
        pad = 40000
        xs = [a_utm.x, b_utm.x] + list(pg.xy[0])
        ys = [a_utm.y, b_utm.y] + list(pg.xy[1])
        ax.set_xlim(min(xs) - pad, max(xs) + pad)
        ax.set_ylim(min(ys) - pad, max(ys) + pad)
        ax.set_title(f"{pid} {u['pipeline_name'][:45]}\n"
                     f"path {path_km:.0f} km vs sheet {u.get('sheet_length_km')} km; "
                     f"snaps {da/1000:.1f}/{db/1000:.1f} km")
        ax.set_aspect("equal"); ax.legend(fontsize=7); ax.tick_params(labelsize=6)
        fig.savefig(STAGING / "overlays" / f"{pid}.png", dpi=110, bbox_inches="tight")
        plt.close(fig)

    (STAGING / "entsog_match_report.json").write_text(
        json.dumps(report, indent=1, ensure_ascii=False))
    ok = [r for r in report if r.get("status") == "PATH"]
    print(f"\n{len(ok)} PATH / {sum(r.get('status')=='NO_NETWORK_MATCH' for r in report)} "
          f"NO_NETWORK_MATCH / {sum(r.get('status')=='DISCONNECTED' for r in report)} DISCONNECTED / "
          f"{sum(r.get('status')=='NO_ENDPOINTS' for r in report)} NO_ENDPOINTS")
    for r in sorted(ok, key=lambda r: abs(1 - (r.get('ratio_vs_sheet') or 9))):
        print(f"  {r['pid']} ratio={r.get('ratio_vs_sheet')} path={r['path_km']}km "
              f"snaps={r['snap_start_km']}/{r['snap_end_km']}km off={r.get('mean_offset_km','-')}km "
              f"| {r['name'][:40]}")


if __name__ == "__main__":
    main()
