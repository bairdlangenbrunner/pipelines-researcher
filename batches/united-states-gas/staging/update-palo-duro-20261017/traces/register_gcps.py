"""Build a denser control-point file for map.jpg (gcps_v2.json).

The first pass used five town dots and one hand-picked border corner. This pass keeps the town dots
(centroids of the dark gray dot symbols, found automatically) and adds points along the Texas-Oklahoma
state line, which the map draws as a thick black line: the straight 100th meridian and the Red River.
The Census county file gives the true line; an affine fit is nudged until the drawn line and the true
line coincide, and the pixel position of each chosen boundary vertex is read from that fit.

Usage: python register_gcps.py map.jpg gcps.json <census county shp> gcps_v2.json
"""
import json, sys
import numpy as np
import geopandas as gpd
from PIL import Image
from scipy import ndimage, optimize
from shapely.geometry import box, LineString
from shapely.ops import unary_union

img, gcps_in, shp, out = sys.argv[1:5]
im = np.array(Image.open(img).convert("RGB")).astype(int)
R, G, B = im[..., 0], im[..., 1], im[..., 2]
H, W = R.shape

# --- the town dots: dark gray blobs of 10-30 px near the first-pass picks -------------------------
dg = (R < 120) & (G < 120) & (B < 120) & (abs(R - G) < 20) & (abs(G - B) < 20)
lab, n = ndimage.label(dg)
sizes = ndimage.sum(dg, lab, range(1, n + 1)); cents = ndimage.center_of_mass(dg, lab, range(1, n + 1))
blobs = [(c[1], c[0]) for s, c in zip(sizes, cents) if 10 <= s <= 30]
gcps = []
for g in json.load(open(gcps_in)):
    if g["name"] == "TX-OK corner":
        continue
    d = [np.hypot(bx - g["px"][0], by - g["px"][1]) for bx, by in blobs]
    j = int(np.argmin(d)); assert d[j] < 3, (g["name"], d[j])
    gcps.append({**g, "px": [round(blobs[j][0], 2), round(blobs[j][1], 2)],
                 "source_ref": g["source_ref"] + "; pixel = centroid of the map's town dot symbol"})

# --- the state line: thick black pixels east of x=295, north of the legend ------------------------
blk = (R < 70) & (G < 70) & (B < 70)
keep = np.zeros_like(blk); keep[0:420, 295:600] = True
keep[185:220, 465:570] = False            # the word OKLAHOMA
blk &= keep
dt = ndimage.distance_transform_edt(~blk)

# the true line: Texas's boundary with Oklahoma inside the map window
co = gpd.read_file(shp).to_crs(4326)
tx = unary_union(co[co.STATEFP == "48"].geometry.values)
ok = unary_union(co[co.STATEFP == "40"].geometry.values)
border = tx.boundary.intersection(ok.boundary.buffer(0.002)).intersection(box(-100.1, 34.0, -98.55, 37))
pts = []
for part in getattr(border, "geoms", [border]):
    if part.geom_type != "LineString":
        continue
    L = part.length
    for t in np.arange(0, L, 0.004):          # about every 400 m
        p = part.interpolate(t); pts.append((p.x, p.y))
pts = np.array(pts)

# initial affine lonlat -> px from the town dots
A = np.column_stack([np.array([g["lonlat"] for g in gcps]), np.ones(len(gcps))])
P = np.array([g["px"] for g in gcps])
p0 = np.concatenate([np.linalg.lstsq(A, P[:, 0], rcond=None)[0], np.linalg.lstsq(A, P[:, 1], rcond=None)[0]])

def project(p, ll):
    return np.column_stack([ll @ p[0:2] + p[2], ll @ p[3:5] + p[5]])

def resid(p):
    xy = project(p, pts)
    d = ndimage.map_coordinates(dt, [xy[:, 1], xy[:, 0]], order=1, mode="nearest")
    return np.minimum(d, 12.0)                 # a far point counts as 12 px, so no single vertex pulls the fit

r0 = resid(p0)
fit = optimize.least_squares(resid, p0, method="trf", x_scale="jac")
r1 = resid(fit.x)
print(f"state line: {len(pts)} true points; mean distance to drawn line {r0.mean():.2f} px before, {r1.mean():.2f} px after")

# control points along the line: the meridian-river corner and river vertices at least 25 px apart
proj = project(fit.x, pts)
on_line = r1 < 1.5
cands = [i for i in np.argsort(pts[:, 0]) if on_line[i]]
chosen = []
for i in cands:
    if all(np.hypot(*(proj[i] - proj[j])) >= 25 for j in chosen):
        chosen.append(i)
corner = int(np.argmin(np.hypot(pts[:, 0] + 100.0, pts[:, 1] - 34.56)))
for k, i in enumerate([corner] + [c for c in chosen if c != corner]):
    name = "TX-OK line: 100th meridian meets the Red River" if i == corner else f"TX-OK line, Red River vertex {k}"
    gcps.append({"name": name, "px": [round(float(proj[i, 0]), 2), round(float(proj[i, 1]), 2)],
                 "lonlat": [round(float(pts[i, 0]), 6), round(float(pts[i, 1]), 6)],
                 "source_ref": "Census cb_2018_us_county_500k, Texas-Oklahoma state line; pixel from fitting the map's drawn state line to the Census line (register_gcps.py)"})
json.dump(gcps, open(out, "w"), indent=1)
print(len(gcps), "control points written to", out)
