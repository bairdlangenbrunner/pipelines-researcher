"""Read the Ellendale Lateral preferred route (dashed vector path) out of the March 13, 2026
FERC filing, page 685 (Figure 10.6.1-5, a GeoPDF), using the page's own /VP /Measure georeferencing.
usage: python3 -I extract_geopdf.py <march_rr1_10.pdf> <page1based> <drawing_index> <out_prefix>"""
import json, re, sys
import fitz, numpy as np
from pyproj import CRS, Transformer, Geod

pdf, pno, didx, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
doc = fitz.open(pdf); page = doc[pno - 1]; H = page.rect.height
obj = doc.xref_object(page.xref)
bbox = [float(v) for v in re.search(r"/BBox \[([^\]]+)\]", obj).group(1).split()]
gpts = [float(v) for v in re.search(r"/GPTS \[([^\]]+)\]", obj).group(1).split()]
lpts = [float(v) for v in re.search(r"/LPTS \[([^\]]+)\]", obj).group(1).split()]
wkt = re.search(r"/WKT \((.*?)\)\s*>>", obj, re.S).group(1).replace("\\(", "(").replace("\\)", ")")
# the WKT carries a trailing vertical datum (VERTCS); keep only the horizontal PROJCS
proj = CRS.from_wkt(wkt.split(",VERTCS")[0] + "]" if "VERTCS" in wkt else wkt)
to_xy = Transformer.from_crs("EPSG:4269", proj, always_xy=True)
to_ll = Transformer.from_crs(proj, "EPSG:4326", always_xy=True)
ll = np.array(gpts).reshape(-1, 2)  # lat, lon
xy = np.array([to_xy.transform(lon, lat) for lat, lon in ll])
uv = np.array(lpts).reshape(-1, 2)
pdfxy = np.column_stack([bbox[0] + uv[:, 0] * (bbox[2] - bbox[0]), bbox[1] + uv[:, 1] * (bbox[3] - bbox[1])])
A = np.column_stack([pdfxy, np.ones(len(pdfxy))])
cx, *_ = np.linalg.lstsq(A, xy[:, 0], rcond=None); cy, *_ = np.linalg.lstsq(A, xy[:, 1], rcond=None)
resid_ft = np.hypot(A @ cx - xy[:, 0], A @ cy - xy[:, 1])

def lonlat(px, py_down):
    X, Y = px, H - py_down
    e, n = cx @ [X, Y, 1], cy @ [X, Y, 1]
    return to_ll.transform(e, n)

dr = page.get_drawings()[didx]
segs = [(tuple(it[1]), tuple(it[2])) for it in dr["items"] if it[0] == "l"]
# chain consecutive segments into polylines
lines, cur = [], [segs[0][0], segs[0][1]]
for a, b in segs[1:]:
    if abs(a[0] - cur[-1][0]) < 1e-3 and abs(a[1] - cur[-1][1]) < 1e-3:
        cur.append(b)
    else:
        lines.append(cur); cur = [a, b]
lines.append(cur)
geod = Geod(ellps="WGS84")
polys = [[[round(v, 6) for v in lonlat(*p)] for p in ln] for ln in lines]
km = sum(geod.line_length([q[0] for q in pl], [q[1] for q in pl]) for pl in polys) / 1000
# milepost circles on this page (same blue, small closed curves)
mps = []
for i, x in enumerate(page.get_drawings()):
    c = x.get("color")
    if c and [round(v, 2) for v in c] == [0.01, 0.18, 1.0] and not x.get("dashes", "").strip("[] 0") and x["rect"].width < 6 and len(x["items"]) == 7:
        r = x["rect"]; mps.append({"drawing": i, "lonlat": [round(v, 6) for v in lonlat((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)]})
json.dump({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {"part": k, "n": len(p)}, "geometry": {"type": "LineString", "coordinates": p}} for k, p in enumerate(polys)]}, open(out + ".geojson", "w"))
json.dump({"bbox_pdf": bbox, "gpts": gpts, "corner_fit_resid_ft": [round(v, 3) for v in resid_ft], "parts": len(polys), "points": sum(map(len, polys)), "length_km": round(km, 2), "length_mi": round(km / 1.609344, 2), "milepost_circles": mps, "crs": proj.name}, open(out + ".report.json", "w"), indent=1)
print(json.dumps(json.load(open(out + ".report.json")), indent=1)[:2500])
