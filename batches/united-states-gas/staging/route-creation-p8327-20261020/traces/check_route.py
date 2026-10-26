"""Checks on the extracted Ellendale Lateral: endpoints, milepost circles vs distance along the line,
county-line crossings vs the filing's county table (Barnes 0-29.7, LaMoure 29.7-62.1, Dickey 62.1-81.6).
usage: python3 -I check_route.py ellendale_alt2.geojson ellendale_alt2.report.json <county shp> <nd place shp>"""
import json, sys
import geopandas as gpd
from shapely.geometry import LineString, Point
from pyproj import Geod
g = Geod(ellps="WGS84")
line = json.load(open(sys.argv[1]))["features"][0]["geometry"]["coordinates"]
rep = json.load(open(sys.argv[2]))
cty = gpd.read_file(sys.argv[3]); cty = cty[cty.STATEFP == "38"].to_crs(4326)
plc = gpd.read_file(sys.argv[4]).to_crs(4326)
# orient north to south (MP 0 at the mainline)
if line[0][1] < line[-1][1]:
    line = line[::-1]
cum = [0.0]
for a, b in zip(line, line[1:]):
    cum.append(cum[-1] + g.inv(a[0], a[1], b[0], b[1])[2] / 1609.344)
L = LineString(line)
print(f"north end {line[0]}  south end {line[-1]}  total {cum[-1]:.2f} mi")
for name in ("Valley City", "Ellendale", "Grand Rapids"):
    r = plc[plc.NAME == name]
    if len(r):
        c = r.geometry.iloc[0]
        for lab, p in (("north end", line[0]), ("south end", line[-1])):
            print(f"  {lab} to {name} boundary: {g.inv(p[0], p[1], c.representative_point().x, c.representative_point().y)[2]/1000:.1f} km to its center; distance to place polygon {c.distance(Point(p))*111:.2f} km approx")
def mile_at(pt):
    d = L.project(Point(pt)); acc = 0
    # convert projected planar fraction to miles via cumulative
    import numpy as np
    seg = 0; run = 0.0
    for i, (a, b) in enumerate(zip(line, line[1:])):
        s = LineString([a, b]).length
        if run + s >= d:
            f = (d - run) / s if s else 0
            return cum[i] + f * (cum[i+1] - cum[i]), Point(pt).distance(L) * 111000
        run += s
    return cum[-1], 0
print("milepost circles (drawings 65 to 74 are labeled 45 to 54 on the map):")
for k, m in enumerate(rep["milepost_circles"][:10]):
    mi, off = mile_at(m["lonlat"])
    print(f"  MP {45+k}: {mi:6.2f} mi along the line, {off:5.0f} m off it")
# county segments
print("county crossings:")
prev = None
for i, p in enumerate(line):
    hit = cty[cty.contains(Point(p))]
    n = hit.NAME.iloc[0] if len(hit) else "?"
    if n != prev:
        print(f"  {cum[i]:6.2f} mi  enters {n}")
        prev = n
