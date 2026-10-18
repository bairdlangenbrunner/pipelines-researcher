"""Plot the georeferenced map traces against the current P7861/P7862 route files and print how far apart they sit.

Usage: python compare_routes.py <traces dir> <routes dir> <states shp> compare_routes.png
"""
import json, sys
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import shape, Point
from shapely.ops import unary_union
from pyproj import Geod

stg, routes, states, out = sys.argv[1:5]
geod = Geod(ellps="WGS84")


def lines(p):
    d = json.load(open(p)); fs = d["features"] if "features" in d else [d]
    out = []
    for f in fs:
        g = shape(f["geometry"]); out += list(g.geoms) if hasattr(g, "geoms") else [g]
    return out


def offsets_km(a, b, step_km=1.0):
    """Distance from points every step_km along the lines of a to the nearest point on the lines of b."""
    ub = unary_union(b); out = []
    for l in a:
        n = max(2, int(geod.geometry_length(l) / 1000 / step_km))
        for t in np.linspace(0, 1, n):
            p = l.interpolate(t, normalized=True); q = ub.interpolate(ub.project(p))
            out.append(geod.inv(p.x, p.y, q.x, q.y)[2] / 1000)
    return np.array(out)


pairs = [("Palo Duro", f"{stg}/palo_duro_v3.geojson", f"{routes}/P7862.geojson"),
         ("Residue Header", f"{stg}/residue_header_v3.geojson", f"{routes}/P7861.geojson")]
for name, tr, rf in pairs:
    a, b = lines(tr), lines(rf)
    d1, d2 = offsets_km(a, b), offsets_km(b, a)
    print(f"{name}: trace {sum(geod.geometry_length(l) for l in a) / 1000:.0f} km in {len(a)} part(s), route file "
          f"{sum(geod.geometry_length(l) for l in b) / 1000:.0f} km in {len(b)} part(s); trace to file median {np.median(d1):.2f} km, "
          f"90th pct {np.percentile(d1, 90):.2f}, max {d1.max():.2f}; file to trace median {np.median(d2):.2f}, 90th pct {np.percentile(d2, 90):.2f}, max {d2.max():.2f}")

fig, ax = plt.subplots(figsize=(8, 10))
st = gpd.read_file(states); st[(st.iso_a2 == "US") & st.postal.isin(["TX", "OK", "NM"])].boundary.plot(ax=ax, color="#bbb", lw=0.8)
for p, c, lw, lab in [(f"{routes}/P7862.geojson", "#e0b000", 6, "P7862 route file (Palo Duro)"),
                      (f"{routes}/P7861.geojson", "#d08080", 6, "P7861 route file (Residue Header)"),
                      (f"{stg}/palo_duro_v3.geojson", "black", 1.2, "map trace, Palo Duro"),
                      (f"{stg}/residue_header_v3.geojson", "#7a0000", 1.2, "map trace, Residue Header")]:
    for i, g in enumerate(lines(p)):
        x, y = g.xy; ax.plot(x, y, color=c, lw=lw, alpha=0.6 if lw > 2 else 1, label=lab if i == 0 else None, solid_capstyle="round")
for n, (x, y) in {"Pampa": (-100.965, 35.548), "Amarillo": (-101.833, 35.198), "Childress": (-100.282, 34.435), "Sweetwater": (-100.409, 32.469), "Abilene": (-99.738, 32.455)}.items():
    ax.plot(x, y, "k^", ms=5); ax.annotate(n, (x, y), xytext=(4, 4), textcoords="offset points", fontsize=8)
ax.set_xlim(-102.2, -98.6); ax.set_ylim(31.8, 36.1); ax.set_aspect(1 / 0.83)
ax.legend(loc="lower left", fontsize=8); ax.set_title("Palo Duro and Residue Header: map traces vs current route files")
fig.tight_layout(); fig.savefig(out, dpi=130)
# a close-up of the header
fig.set_size_inches(10, 5.2); ax.set_xlim(-101.1, -99.2); ax.set_ylim(35.15, 35.9); ax.set_aspect(1 / 0.83); ax.set_title("Residue Header close-up"); fig.tight_layout()
fig.savefig(out.replace(".png", "_header.png"), dpi=130)
