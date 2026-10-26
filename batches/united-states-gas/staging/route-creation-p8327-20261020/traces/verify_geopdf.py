"""Georeference helpers for the WBI Energy GeoPDF figure pages (ArcGIS Pro exports with a /VP /Measure dict).
Reads the page's own GPTS/LPTS/BBox/WKT and fits an affine page->projected transform; exposes lonlat().
Also dumps selected drawings as WGS84 geojson. usage: python3 -I geopdf.py <pdf> <page1based> <out.geojson> <drawing_idx>[,idx...]"""
import json, re, sys
import fitz, numpy as np
from pyproj import CRS, Transformer

class PageGeoref:
    def __init__(self, doc, pno):
        self.page = doc[pno - 1]; self.H = self.page.rect.height
        obj = doc.xref_object(self.page.xref)
        self.bbox = [float(v) for v in re.search(r"/BBox \[([^\]]+)\]", obj).group(1).split()]
        self.gpts = [float(v) for v in re.search(r"/GPTS \[([^\]]+)\]", obj).group(1).split()]
        lpts = [float(v) for v in re.search(r"/LPTS \[([^\]]+)\]", obj).group(1).split()]
        wkt = re.search(r"/WKT \((.*?)\)\s*>>", obj, re.S).group(1).replace("\\(", "(").replace("\\)", ")")
        self.proj = CRS.from_wkt(wkt.split(",VERTCS")[0] + "]" if "VERTCS" in wkt else wkt)
        self.to_xy = Transformer.from_crs("EPSG:4269", self.proj, always_xy=True)
        self.to_ll = Transformer.from_crs(self.proj, "EPSG:4326", always_xy=True)
        ll = np.array(self.gpts).reshape(-1, 2)
        xy = np.array([self.to_xy.transform(lon, lat) for lat, lon in ll])
        uv = np.array(lpts).reshape(-1, 2)
        b = self.bbox
        pdfxy = np.column_stack([b[0] + uv[:, 0] * (b[2] - b[0]), b[1] + uv[:, 1] * (b[3] - b[1])])
        A = np.column_stack([pdfxy, np.ones(len(pdfxy))])
        self.cx, *_ = np.linalg.lstsq(A, xy[:, 0], rcond=None); self.cy, *_ = np.linalg.lstsq(A, xy[:, 1], rcond=None)
        self.resid_ft = np.hypot(A @ self.cx - xy[:, 0], A @ self.cy - xy[:, 1])
        # scale: projected feet per PDF point
        self.ft_per_pt = float(np.hypot(self.cx[0], self.cy[0]))
    def xy(self, px, py_down):
        X, Y = px, self.H - py_down
        return self.cx @ [X, Y, 1], self.cy @ [X, Y, 1]
    def lonlat(self, px, py_down):
        return self.to_ll.transform(*self.xy(px, py_down))
    def inside_frame(self, px, py_down):
        b = self.bbox; Y = self.H - py_down
        return b[0] <= px <= b[2] and b[1] <= Y <= b[3]

def drawing_polylines(dr):
    segs = [(tuple(it[1]), tuple(it[2])) for it in dr["items"] if it[0] == "l"]
    lines, cur = [], [segs[0][0], segs[0][1]]
    for a, b in segs[1:]:
        if abs(a[0] - cur[-1][0]) < 1e-3 and abs(a[1] - cur[-1][1]) < 1e-3:
            cur.append(b)
        else:
            lines.append(cur); cur = [a, b]
    lines.append(cur)
    return lines

if __name__ == "__main__":
    doc = fitz.open(sys.argv[1]); pno = int(sys.argv[2]); out = sys.argv[3]
    idxs = [int(v) for v in sys.argv[4].split(",")]
    g = PageGeoref(doc, pno)
    print("page", pno, "bbox", g.bbox, "corner resid ft", [round(v, 3) for v in g.resid_ft], "ft/pt", round(g.ft_per_pt, 3), "scale 1:", round(g.ft_per_pt * 72 * 12))
    drs = g.page.get_drawings(); feats = []
    for i in idxs:
        for k, pl in enumerate(drawing_polylines(drs[i])):
            coords = [[round(v, 7) for v in g.lonlat(*p)] for p in pl]
            inside = [g.inside_frame(*p) for p in pl]
            feats.append({"type": "Feature", "properties": {"drawing": i, "part": k, "n": len(pl), "all_inside": all(inside), "any_inside": any(inside)}, "geometry": {"type": "LineString", "coordinates": coords}})
    json.dump({"type": "FeatureCollection", "features": feats}, open(out, "w"))
    print("wrote", out, len(feats), "features")
