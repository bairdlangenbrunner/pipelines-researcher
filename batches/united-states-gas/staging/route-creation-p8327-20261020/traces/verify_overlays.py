"""Overlay panels for a person to look at: the P8327 candidate over Census counties and places, TIGER roads and
water, the Bakken East mainline and milepost circles read from page 684 inside its frame, and milepost
circles 45-54 from page 685. usage: python3 -I final_overlays.py <S> <candidate.geojson> <out.png>"""
import sys, fitz, numpy as np, geopandas as gpd
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from geopdf import PageGeoref, drawing_polylines
from shapely.geometry import box, LineString, Point
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
S, cand, out = sys.argv[1:4]
cty = gpd.read_file(f"{S}/census/cb_2018_us_county_500k.shp"); cty = cty[cty.STATEFP == "38"]
pl = gpd.read_file(f"{S}/census/cb_2018_38_place_500k.shp")
roads = gpd.pd.concat([gpd.read_file(f"{S}/tiger_dl/tl_2023_{f}_roads/tl_2023_{f}_roads.shp") for f in ("38003", "38045", "38021", "38093")])
water = gpd.pd.concat([gpd.read_file(f"{S}/tiger_dl/tl_2023_{f}_linearwater/tl_2023_{f}_linearwater.shp") for f in ("38003", "38045", "38021")])
route = gpd.read_file(cand); route = route[route.get("drawing", gpd.pd.Series([64]*len(route))) == 64] if "drawing" in route else route
doc = fitz.open(f"{S}/p8327/dl/march_rr1_10.pdf")
g4 = PageGeoref(doc, 684); d4 = g4.page.get_drawings()
main = [LineString([g4.lonlat(*p) for p in pl_ if g4.inside_frame(*p)]) for pl_ in drawing_polylines(d4[1088]) if sum(g4.inside_frame(*p) for p in pl_) > 1]
main = gpd.GeoSeries(main, crs=4326)
mp4 = []
for i, d in enumerate(d4):
    r = d["rect"]
    if d.get("color") and [round(v, 2) for v in d["color"]] == [0.99, 0.14, 0.03] and d.get("fill") and len(d["items"]) == 7 and g4.inside_frame((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2):
        mp4.append(g4.lonlat((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))
mp4.sort(); labels4 = list(range(293, 293 + len(mp4)))
g5 = PageGeoref(doc, 685); d5 = g5.page.get_drawings(); mp5 = []
for i, d in enumerate(d5):
    r = d["rect"]
    if d.get("color") and [round(v, 2) for v in d["color"]] == [0.01, 0.18, 1.0] and d.get("fill") and len(d["items"]) == 7 and r.width < 6 and g5.inside_frame((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2):
        mp5.append(g5.lonlat((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))
line = list(route.geometry.iloc[0].coords)
if line[0][1] < line[-1][1]: line = line[::-1]
from pyproj import Geod; geod = Geod(ellps="WGS84"); cum = [0.0]
for a, b in zip(line, line[1:]): cum.append(cum[-1] + geod.inv(a[0], a[1], b[0], b[1])[2] / 1609.344)
def at_mile(m):
    for i in range(len(cum) - 1):
        if cum[i] <= m <= cum[i + 1]:
            f = (m - cum[i]) / (cum[i + 1] - cum[i]); return (line[i][0] + f * (line[i + 1][0] - line[i][0]), line[i][1] + f * (line[i + 1][1] - line[i][1]))
    return line[-1]
def panel(ax, bb, title, show_roads=True, pts=True):
    b = box(*bb)
    cty.boundary.plot(ax=ax, color="dimgray", lw=1.2, ls="--")
    if show_roads:
        rr = roads[roads.intersects(b)]
        if len(rr): rr.plot(ax=ax, color="#bdbdbd", lw=0.5)
        ww = water[water.intersects(b)]
        if len(ww): ww.plot(ax=ax, color="#8fd0ff", lw=0.7)
    pp = pl[pl.intersects(b)]
    if len(pp):
        pp.plot(ax=ax, color="#ffd080", alpha=0.7)
        for _, r in pp.iterrows():
            c = r.geometry.representative_point(); ax.text(c.x, c.y, r.NAME, fontsize=7, ha="center", va="bottom", color="#7a4b00")
    main.plot(ax=ax, color="red", lw=2)
    for (x, y), lab in zip(mp4, labels4):
        if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3]: ax.plot(x, y, "o", mfc="white", mec="red", ms=6); ax.text(x, y, f" ML {lab}", fontsize=7, color="red", va="bottom")
    route.plot(ax=ax, color="black", lw=1.4)
    if pts:
        xs, ys = route.geometry.iloc[0].xy; ax.plot(xs, ys, ".", color="magenta", ms=3)
    for x, y in mp5:
        if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3]: ax.plot(x, y, "o", mfc="white", mec="blue", ms=5)
    for m in (10, 20, 30, 40, 50, 60, 70, 80):
        x, y = at_mile(m)
        if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3]: ax.plot(x, y, "s", color="green", ms=5); ax.text(x, y, f" MP {m}", fontsize=7, color="green", va="top")
    ax.set_xlim(bb[0], bb[2]); ax.set_ylim(bb[1], bb[3]); ax.set_title(title, fontsize=9); ax.set_aspect(1 / np.cos(np.radians((bb[1] + bb[3]) / 2)))
n = line[0]; s = line[-1]
fig, axs = plt.subplots(2, 4, figsize=(24, 13))
panel(axs[0, 0], (-98.95, 45.92, -97.75, 47.12), "overview: candidate (black), county lines (dashed), mainline from page 684 (red), green = computed mileposts", show_roads=False, pts=False)
panel(axs[0, 1], (n[0] - 0.05, n[1] - 0.035, n[0] + 0.05, n[1] + 0.035), "north end: tie-in on the mainline, 0.32 mi east of mainline MP 294 (filing: MP 294.3)")
m12 = at_mile(12.1); panel(axs[0, 2], (m12[0] - 0.08, m12[1] - 0.06, m12[0] + 0.08, m12[1] + 0.06), "around MP 12 (MLV02_EL at 12.1), Barnes County")
m30 = at_mile(29.9); panel(axs[0, 3], (m30[0] - 0.08, m30[1] - 0.06, m30[0] + 0.08, m30[1] + 0.06), "Barnes/LaMoure line: crossed at 29.98 mi (filing 29.7)")
panel(axs[1, 0], (-98.45, 46.37, -98.30, 46.47), "page 685 frame: blue circles = the figure's MP 45-54 markers")
m62 = at_mile(62.1); panel(axs[1, 1], (m62[0] - 0.08, m62[1] - 0.06, m62[0] + 0.08, m62[1] + 0.06), "LaMoure/Dickey line: crossed at 62.11 mi (filing 62.1)")
m70 = at_mile(72); panel(axs[1, 2], (m70[0] - 0.08, m70[1] - 0.06, m70[0] + 0.08, m70[1] + 0.06), "around MP 72, Dickey County")
panel(axs[1, 3], (s[0] - 0.07, s[1] - 0.05, s[0] + 0.07, s[1] + 0.05), "south end: MP 81.6 about 2 km north of Ellendale")
plt.tight_layout(); plt.savefig(out, dpi=100); print("wrote", out)
