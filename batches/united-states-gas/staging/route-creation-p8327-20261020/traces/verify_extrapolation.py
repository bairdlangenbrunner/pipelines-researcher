"""Test whether page 685's off-frame vector content is faithful: compare the drawn county boundary
(drawing 48) and the James River (49/50) with Census county lines and TIGER linear water, and plot
the dashed route (64) over TIGER roads at several zooms."""
import json, sys
import geopandas as gpd, numpy as np
from shapely.geometry import LineString, shape, box, Point
from shapely.ops import unary_union, nearest_points
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
S = sys.argv[1]; out = sys.argv[2]; ogw = sys.argv[3]
lay = gpd.read_file(f"{S}/p8327/fix/p685_layers.geojson")
cty = gpd.read_file(f"{S}/census/cb_2018_us_county_500k.shp"); cty = cty[cty.STATEFP == "38"]
pl = gpd.read_file(f"{S}/census/cb_2018_38_place_500k.shp")
roads = gpd.pd.concat([gpd.read_file(f"{S}/tiger_dl/tl_2023_{f}_roads/tl_2023_{f}_roads.shp") for f in ("38003", "38045", "38021")])
water = gpd.pd.concat([gpd.read_file(f"{S}/tiger_dl/tl_2023_{f}_linearwater/tl_2023_{f}_linearwater.shp") for f in ("38003", "38045", "38021")])
main = gpd.read_file(ogw)
route = lay[lay.drawing == 64]; ctyline = lay[lay.drawing == 48]; river = lay[lay.drawing.isin([49, 50])]
# metric CRS for distances
M = "EPSG:26914"
cty_m = cty.to_crs(M); bnd = unary_union([g.boundary for g in cty_m.geometry])
ctyline_m = ctyline.to_crs(M)
d = []
for g in ctyline_m.geometry:
    for x, y in g.coords:
        d.append(bnd.distance(Point(x, y)))
d = np.array(d)
print("drawn county line vertices:", len(d), "dist to Census county boundary m: median", round(np.median(d)), "p90", round(np.percentile(d, 90)), "max", round(d.max()))
rt = unary_union(route.to_crs(M).geometry)
# where is drawn county line relative to frame
frame_in = ctyline[ctyline.all_inside]; print("county-line parts fully inside frame", len(frame_in), "of", len(ctyline))
for _, r in ctyline_m.iterrows():
    dd = [bnd.distance(Point(x, y)) for x, y in r.geometry.coords]
    print(f"  part {r.part} n={r.n} inside={r.any_inside} median={np.median(dd):.0f} m max={max(dd):.0f} m len={r.geometry.length/1000:.1f} km")
river_m = river.to_crs(M); wat_m = water.to_crs(M); watu = unary_union(wat_m.geometry)
dr = np.array([watu.distance(Point(x, y)) for g in river_m.geometry for x, y in g.coords])
print("drawn river vertices", len(dr), "dist to TIGER water m: median", round(np.median(dr)), "p90", round(np.percentile(dr, 90)))
# route vs mainline at north end
rtl = unary_union(route.geometry); coords = list(route.geometry.iloc[0].coords)
north = Point(coords[0]) if coords[0][1] > coords[-1][1] else Point(coords[-1])
south = Point(coords[-1]) if coords[0][1] > coords[-1][1] else Point(coords[0])
mm = main.to_crs(M); mu = unary_union(mm.geometry)
nm = gpd.GeoSeries([north], crs=4326).to_crs(M).iloc[0]
print("north end", north, "distance to OGW mainline m", round(mu.distance(nm)))
ell = pl[pl.NAME == "Ellendale"].to_crs(M).geometry.iloc[0]
sm = gpd.GeoSeries([south], crs=4326).to_crs(M).iloc[0]
print("south end", south, "distance to Ellendale place polygon m", round(ell.distance(sm)))
# segment bearing stats of the route
xy = np.array(gpd.GeoSeries([LineString(coords)], crs=4326).to_crs(M).iloc[0].coords)
seg = np.diff(xy, axis=0); L = np.hypot(seg[:, 0], seg[:, 1]); ang = np.degrees(np.arctan2(seg[:, 1], seg[:, 0])) % 90
print("route segments", len(L), "len m: median", round(np.median(L)), "max", round(L.max()), "; share within 3 deg of N-S/E-W grid:", round(np.mean((ang < 3) | (ang > 87)), 2))
# plots
def panel(ax, bb, title, show_roads=True):
    b = box(*bb)
    cty.boundary.plot(ax=ax, color="gray", lw=1)
    if show_roads:
        rr = roads[roads.intersects(b)]
        if len(rr): rr.plot(ax=ax, color="#bbbbbb", lw=0.5)
        ww = water[water.intersects(b)]
        if len(ww): ww.plot(ax=ax, color="#8fd0ff", lw=0.6)
    pp = pl[pl.intersects(b)]
    if len(pp): pp.plot(ax=ax, color="#ffd080", alpha=0.6)
    main.plot(ax=ax, color="red", lw=1.5)
    river.plot(ax=ax, color="blue", lw=0.8, alpha=0.6)
    ctyline.plot(ax=ax, color="green", lw=1, ls="--")
    route.plot(ax=ax, color="black", lw=1.2)
    for g in route.geometry:
        xs, ys = g.xy; ax.plot(xs, ys, ".", color="magenta", ms=3)
    ax.set_xlim(bb[0], bb[2]); ax.set_ylim(bb[1], bb[3]); ax.set_title(title, fontsize=8); ax.set_aspect(1 / np.cos(np.radians((bb[1] + bb[3]) / 2)))
fig, axs = plt.subplots(2, 3, figsize=(18, 13))
panel(axs[0, 0], (-98.9, 45.9, -97.8, 47.15), "overview: route (black), drawn county line (green dashed), OGW mainline (red)", show_roads=False)
panel(axs[0, 1], (north.x - 0.08, north.y - 0.06, north.x + 0.08, north.y + 0.06), "north end vs mainline + TIGER roads")
panel(axs[0, 2], (south.x - 0.08, south.y - 0.06, south.x + 0.08, south.y + 0.06), "south end near Ellendale")
panel(axs[1, 0], (-98.45, 46.60, -98.25, 46.76), "around MP 29.7 county line (Barnes/LaMoure)")
panel(axs[1, 1], (-98.45, 46.37, -98.30, 46.47), "inside the page 685 frame")
panel(axs[1, 2], (-98.60, 46.22, -98.40, 46.40), "around MP 62.1 county line (LaMoure/Dickey)")
plt.tight_layout(); plt.savefig(out, dpi=110); print("wrote", out)
