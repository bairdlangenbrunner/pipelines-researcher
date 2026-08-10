"""Plot + measure GulfPub sidecar hits for the rung-1 candidate PIDs (Egypt gas
§8 pass 2026-08-04). Output: per-PID PNG in overlays/ (gp_<PID>.png) + a summary
table on stdout. Adjudication is human; assembly happens per-PID afterwards.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform as shp_transform

STAGING = Path(__file__).resolve().parent
ROOT = STAGING.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from route_compare import load_gem_route  # noqa: E402

TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32636", always_xy=True).transform
PIDS = ["P3935", "P6034", "P8015", "P5132", "P6036", "P6037", "P7572",
        "P6686", "P8012", "P7577", "P7578", "P7589", "P7597"]


def utm(g):
    return shp_transform(TO_UTM, g)


def main() -> None:
    wl = json.load(open(STAGING / "worklist.json"))["units"]
    ent = json.load(open(ROOT / "sources/entsog/"
                         "ENTSOG_GIE_SYSCAP_2026_pipelines_operational_wgs84.geojson"))
    ent_utm = [utm(shape(f["geometry"])) for f in ent["features"]
               if 24 < shape(f["geometry"]).bounds[0] < 37]

    sidecars = {}
    for u in wl:
        for h in (u.get("gulfpub_hits") or []):
            d = h["recon_dir"]
            if d not in sidecars:
                sidecars[d] = json.load(
                    open(ROOT / "batches" / d.split("/")[0] / "staging" /
                         d.split("/", 1)[1] / "geometry_sidecar.json"))
    print("loaded sidecars:", {k: len(v) for k, v in sidecars.items()})

    for pid in PIDS:
        u = next(x for x in wl if x["project_id"] == pid)
        fig, ax = plt.subplots(figsize=(7, 6))
        for ln in ent_utm:
            ax.plot(*ln.xy, color="#c6dbef", lw=0.5, zorder=1)
        gj = load_gem_route(pid, "gas")
        xs, ys = [], []
        if gj is not None:
            ex = utm(shape(gj))
            for g in ([ex] if ex.geom_type == "LineString" else ex.geoms):
                ax.plot(*g.xy, color="#555555", lw=1.2, ls="--", zorder=2)
                xs += list(g.xy[0]); ys += list(g.xy[1])
        rows = []
        for i, h in enumerate(u.get("gulfpub_hits") or []):
            sc = sidecars[h["recon_dir"]]
            geom = sc.get(h["ref_id"])
            if geom is None:
                rows.append((h["ref_id"], h["ref_name"], None))
                continue
            g = shape(geom["geometry"] if "geometry" in geom else geom)
            gu = utm(g)
            km = gu.length / 1000
            rows.append((h["ref_id"], h["ref_name"], round(km, 1)))
            color = plt.cm.tab10(i % 10)
            for part in ([gu] if gu.geom_type == "LineString" else gu.geoms):
                ax.plot(*part.xy, color=color, lw=1.6, zorder=3,
                        label=f'{h["ref_name"][:32]} {km:.0f}km')
                xs += list(part.xy[0]); ys += list(part.xy[1])
        if xs:
            pad = 40000
            ax.set_xlim(min(xs) - pad, max(xs) + pad)
            ax.set_ylim(min(ys) - pad, max(ys) + pad)
        ax.set_title(f"{pid} {u['pipeline_name'][:45]} — sheet {u.get('sheet_length_km')} km "
                     f"(grey dash = existing GEM)")
        ax.set_aspect("equal"); ax.tick_params(labelsize=6)
        if rows:
            ax.legend(fontsize=6)
        fig.savefig(STAGING / "overlays" / f"gp_{pid}.png", dpi=110, bbox_inches="tight")
        plt.close(fig)
        print(f"{pid} sheet={u.get('sheet_length_km')}km "
              f"acc={u['current_route_accuracy'] or 'no route'}")
        for r in rows:
            print(f"   {r[0]:22} {str(r[2]):>7} km  {r[1]}")


if __name__ == "__main__":
    main()
