"""Second matcher pass: route researched endpoints (research_results_*.json)
through the ENTSOG network for the no-route rows. Reuses entsog_match's graph.

  python3 batches/egypt-gas/staging/route-creation-20260804/noroute_match.py [group ...]
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Point
from shapely.ops import transform as shp_transform

STAGING = Path(__file__).resolve().parent
sys.path.insert(0, str(STAGING))
from entsog_match import (TO_LL, build_graph, insert_point, load_entsog_lines,  # noqa: E402
                          node_network, path_geometry, utm)


def main() -> None:
    groups = sys.argv[1:] or [p.stem.replace("research_results_", "")
                              for p in STAGING.glob("research_results_*.json")]
    feats = load_entsog_lines()
    segs = node_network(feats)
    G0 = build_graph(segs)
    all_lines = [utm(g) for _, g in feats]

    wl = {u["project_id"]: u for u in json.load(open(STAGING / "worklist.json"))["units"]}
    for grp in groups:
        fn = STAGING / f"research_results_{grp}.json"
        if not fn.exists():
            print(f"-- {grp}: no results file yet")
            continue
        for rec in json.load(open(fn)):
            pid = rec["project_id"]
            if not rec.get("resolved") or "start" not in rec or "end" not in rec:
                print(f"{pid}: unresolved — skip")
                continue
            a = utm(Point(rec["start"]["lon"], rec["start"]["lat"]))
            b = utm(Point(rec["end"]["lon"], rec["end"]["lat"]))
            G = G0.copy()
            na, da = insert_point(G, a, f"{pid}_a")
            nb, db = insert_point(G, b, f"{pid}_b")
            sheet = wl.get(pid, {}).get("sheet_length_km")
            if na is None or nb is None or na == nb:
                print(f"{pid}: NO_NETWORK_MATCH snaps={da/1000:.1f}/{db/1000:.1f} km")
                continue
            try:
                path = nx.shortest_path(G, na, nb, weight="weight")
            except nx.NetworkXNoPath:
                print(f"{pid}: DISCONNECTED")
                continue
            pg = path_geometry(G, path)
            km = pg.length / 1000
            ratio = round(km / sheet, 3) if sheet else None
            print(f"{pid}: PATH {km:.1f} km vs sheet {sheet} (ratio {ratio}) "
                  f"snaps={da/1000:.1f}/{db/1000:.1f} km")
            ll = shp_transform(TO_LL, pg)
            (STAGING / "overlays" / f"{pid}_entsog_path.geojson").write_text(json.dumps({
                "type": "Feature",
                "properties": {"pid": pid, "path_km": round(km, 1)},
                "geometry": {"type": "LineString",
                             "coordinates": [[round(x, 6), round(y, 6)]
                                             for x, y in ll.coords]}}))
            fig, ax = plt.subplots(figsize=(7, 6))
            for lu in all_lines:
                ax.plot(*lu.xy, color="#9ecae1", lw=0.6, zorder=1)
            ax.plot(*pg.xy, color="#d62728", lw=1.6, zorder=3)
            ax.scatter([a.x, b.x], [a.y, b.y], c="k", s=18, zorder=4)
            pad = 40000
            xs = [a.x, b.x] + list(pg.xy[0]); ys = [a.y, b.y] + list(pg.xy[1])
            ax.set_xlim(min(xs) - pad, max(xs) + pad)
            ax.set_ylim(min(ys) - pad, max(ys) + pad)
            ax.set_title(f"{pid} (no route) path {km:.0f} km vs sheet {sheet} km; "
                         f"snaps {da/1000:.1f}/{db/1000:.1f} km")
            ax.set_aspect("equal"); ax.tick_params(labelsize=6)
            fig.savefig(STAGING / "overlays" / f"nr_{pid}.png", dpi=110,
                        bbox_inches="tight")
            plt.close(fig)


if __name__ == "__main__":
    main()
