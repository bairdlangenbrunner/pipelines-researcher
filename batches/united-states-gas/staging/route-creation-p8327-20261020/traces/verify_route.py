"""Verification of the P8327 Ellendale Lateral candidate against the filing's own anchors.
usage: python3 -I verify_route.py <march pdf> <candidate or layer geojson> <census county shp> <nd place shp> <ogw P8096 geojson> [out.json]
Checks: length vs 81.6 mi; milepost circles 45-54 (page 685) at their stated distance from MP 0; county line
crossings vs 29.7 / 62.1; north end on the mainline drawn inside page 684's frame and 0.3 mi east of its MP 294
circle (tie-in at mainline MP 294.3); south end near Ellendale; the page's off-frame county line vs Census."""
import json, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import fitz, numpy as np, geopandas as gpd
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from pyproj import Geod
from geopdf import PageGeoref, drawing_polylines
pdf, cand, ctyshp, plshp, ogwf = sys.argv[1:6]; outp = sys.argv[6] if len(sys.argv) > 6 else None
geod = Geod(ellps="WGS84"); M = "EPSG:26914"; res = {}
fc = json.load(open(cand))
feats = [f for f in fc["features"] if f["properties"].get("drawing", 64) == 64]
line = feats[0]["geometry"]["coordinates"]
if line[0][1] < line[-1][1]: line = line[::-1]
cum = [0.0]
for a, b in zip(line, line[1:]): cum.append(cum[-1] + geod.inv(a[0], a[1], b[0], b[1])[2] / 1609.344)
res["length_mi"] = round(cum[-1], 2); res["filing_length_mi"] = 81.6; res["vertices"] = len(line)
L = gpd.GeoSeries([LineString(line)], crs=4326).to_crs(M).iloc[0]
def to_m(p): return gpd.GeoSeries([Point(p)], crs=4326).to_crs(M).iloc[0]
def mile_at(p):
    pm = to_m(p); d = L.project(pm); return d / L.length * cum[-1], pm.distance(L)
doc = fitz.open(pdf)
g5 = PageGeoref(doc, 685); drs = g5.page.get_drawings()
circ = [i for i, d in enumerate(drs) if d.get("color") and [round(v, 2) for v in d["color"]] == [0.01, 0.18, 1.0] and d.get("fill") and len(d["items"]) == 7 and d["rect"].width < 6 and g5.inside_frame((d["rect"].x0 + d["rect"].x1) / 2, (d["rect"].y0 + d["rect"].y1) / 2)]
# the ten circles are labeled 45..54 on the map, in route order from the north; sort by distance along the line
mps = []
for i in circ:
    r = drs[i]["rect"]; ll = g5.lonlat((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2); mi, off = mile_at(ll); mps.append((mi, off, i))
mps.sort()
res["milepost_circles_p685"] = [{"label": 45 + k, "mi_along": round(mi, 2), "off_m": round(off, 1)} for k, (mi, off, i) in enumerate(mps)]
cty = gpd.read_file(ctyshp); cty = cty[cty.STATEFP == "38"].to_crs(4326)
prev = None; cross = []
for i, p in enumerate(line):
    hit = cty[cty.contains(Point(p))]; n = hit.NAME.iloc[0] if len(hit) else "?"
    if n != prev: cross.append({"mi": round(cum[i], 2), "enters": n}); prev = n
res["county_crossings"] = cross; res["filing_county_crossings_mi"] = {"LaMoure": 29.7, "Dickey": 62.1}
# page 684 mainline and milepost circles
g4 = PageGeoref(doc, 684); d4 = g4.page.get_drawings()
mainpl = [pl for pl in drawing_polylines(d4[1088])]
main_in = [[g4.lonlat(*p) for p in pl if g4.inside_frame(*p)] for pl in mainpl]
main_in = [pl for pl in main_in if len(pl) > 1]
mu = unary_union([gpd.GeoSeries([LineString(pl)], crs=4326).to_crs(M).iloc[0] for pl in main_in])
north = line[0]; south = line[-1]
res["north_end"] = {"lonlat": [round(v, 6) for v in north], "distance_to_p684_mainline_m": round(mu.distance(to_m(north)), 1)}
red = sorted([(d["rect"].x0, i) for i, d in enumerate(d4) if d.get("color") and [round(v, 2) for v in d["color"]] == [0.99, 0.14, 0.03] and d.get("fill") and len(d["items"]) == 7 and g4.inside_frame((d["rect"].x0 + d["rect"].x1) / 2, (d["rect"].y0 + d["rect"].y1) / 2)])
mp294 = d4[red[1][1]]["rect"]; mp295 = d4[red[2][1]]["rect"]
p294 = g4.lonlat((mp294.x0 + mp294.x1) / 2, (mp294.y0 + mp294.y1) / 2); p295 = g4.lonlat((mp295.x0 + mp295.x1) / 2, (mp295.y0 + mp295.y1) / 2)
# distance along the drawn mainline from MP 294 circle to the lateral's north end
mline = max(main_in, key=len); ML = gpd.GeoSeries([LineString(mline)], crs=4326).to_crs(M).iloc[0]
a = ML.project(to_m(p294)); b = ML.project(to_m(north)); c = ML.project(to_m(p295))
res["north_end"]["mainline_mp_from_p684_circles"] = round(294 + (b - a) / (c - a), 2)
res["north_end"]["filing_tie_in_mainline_mp"] = 294.3
res["north_end"]["mp294_circle_offset_from_mainline_m"] = round(ML.distance(to_m(p294)), 1)
pl = gpd.read_file(plshp).to_crs(M); ell = pl[pl.NAME == "Ellendale"].geometry.iloc[0]
res["south_end"] = {"lonlat": [round(v, 6) for v in south], "distance_to_Ellendale_place_polygon_m": round(ell.distance(to_m(south))), "distance_to_Ellendale_centroid_m": round(ell.centroid.distance(to_m(south)))}
# extrapolation tests: county line drawn on each page vs Census
ctym = cty.to_crs(M); bnd = unary_union([x.boundary for x in ctym.geometry])
for pno, idx in ((685, 48), (684, 56)):
    g = PageGeoref(doc, pno); d = g.page.get_drawings()[idx]
    pts = [g.lonlat(*p) for pl in drawing_polylines(d) for p in pl]
    dd = np.array([bnd.distance(to_m(p)) for p in pts]); inside = sum(g.inside_frame(*p) for pl in drawing_polylines(d) for p in pl)
    res[f"p{pno}_drawn_county_line_vs_census_m"] = {"vertices": len(pts), "inside_frame": int(inside), "median": round(float(np.median(dd)), 1), "max": round(float(dd.max()), 1), "corner_fit_resid_ft": round(float(g.resid_ft.max()), 3)}
ogw = gpd.read_file(ogwf).to_crs(M); ou = unary_union(ogw.geometry)
res["north_end"]["distance_to_ogw_mainline_m"] = round(ou.distance(to_m(north)))
print(json.dumps(res, indent=1))
if outp: json.dump(res, open(outp, "w"), indent=1)
