"""Add county-corner control points to map.jpg (gcps_v3.json).

gcps_v2.json pins the map with four town dots and the Texas-Oklahoma state line. The state line is the
straight 100th meridian north of the Red River, so it pins east-west only, and in the north the one
north-south control is the Pampa dot. The header trace came out about 4 km north of the P7861 route
file, and the company's August 2025 map puts the line where the file is. The map also draws county
lines (1 px, light gray), so this pass fits the Census county lines to the drawn ones with an order 2
polynomial, starting from the gcps_v2 fit, and reads the pixel position of every county corner (a
point where three or more counties meet) that the drawn lines confirm.

Usage: python register_counties.py map.jpg gcps_v2.json <census county shp> gcps_v3.json
"""
import json, sys
from collections import Counter
import numpy as np
import geopandas as gpd
from PIL import Image
from scipy import ndimage, optimize
from shapely.geometry import box

img, gcps_in, shp, out = sys.argv[1:5]
a = np.array(Image.open(img).convert("RGB")).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
H, W = R.shape
lum = (R + G + B) / 3; sat = a.max(2) - a.min(2)

# drawn county lines: light gray, unsaturated; nothing near the pipelines, the legend, the title or the compass
gray = (lum > 140) & (lum < 222) & (sat < 12)
pipe = ((R - np.maximum(G, B)) > 25) | ((np.minimum(R, G) - B) > 40)
gray &= ~ndimage.binary_dilation(pipe, iterations=3)
for x0, y0, x1, y1 in [(400, 420, 580, 540), (410, 0, 600, 30), (0, 0, 40, 40)]:
    gray[y0:y1, x0:x1] = False
gray[:, :3] = gray[:, -3:] = gray[:3, :] = gray[-3:, :] = False   # the frame
dt = ndimage.distance_transform_edt(~gray)

gcps = json.load(open(gcps_in))
ll = np.array([g["lonlat"] for g in gcps]); px = np.array([g["px"] for g in gcps])


def terms(lonlat):
    x, y = lonlat[:, 0], lonlat[:, 1]
    return np.column_stack([np.ones_like(x), x, y, x * x, x * y, y * y])


# lonlat -> px, order 2, from the gcps_v2 points
p0 = np.concatenate([np.linalg.lstsq(terms(ll), px[:, 0], rcond=None)[0],
                     np.linalg.lstsq(terms(ll), px[:, 1], rcond=None)[0]])


def project(p, lonlat):
    T = terms(lonlat)
    return np.column_stack([T @ p[:6], T @ p[6:]])


# the true lines: every county boundary in Texas, Oklahoma and New Mexico inside the map
co = gpd.read_file(shp).to_crs(4326)
co = co[co.STATEFP.isin(["48", "40", "35"])].reset_index(drop=True)
inv = np.linalg.lstsq(np.column_stack([np.ones(len(px)), px]), ll, rcond=None)[0]
lon0, lat0 = (np.array([[1, 0, H], [1, W, 0]]) @ inv).min(0) - 0.2
lon1, lat1 = (np.array([[1, 0, H], [1, W, 0]]) @ inv).max(0) + 0.2
win = box(lon0, lat0, lon1, lat1)
co = co[co.intersects(win)].reset_index(drop=True)
pts = []
for g in co.geometry.boundary:
    for part in getattr(g, "geoms", [g]):
        for t in np.arange(0, part.length, 0.005):         # about every 500 m
            p = part.interpolate(t); pts.append((p.x, p.y))
pts = np.unique(np.round(np.array(pts), 5), axis=0)


def inside(xy, m=4):
    return (xy[:, 0] > m) & (xy[:, 0] < W - m) & (xy[:, 1] > m) & (xy[:, 1] < H - m)


def resid(p):
    xy = project(p, pts); ok = inside(xy)
    d = ndimage.map_coordinates(dt, [xy[:, 1], xy[:, 0]], order=1, mode="nearest")
    return np.where(ok, np.minimum(d, 5.0), 0.0)            # a far point counts as 5 px, so no single vertex pulls the fit


r0 = resid(p0)
fit = optimize.least_squares(resid, p0, method="trf", x_scale="jac", loss="soft_l1", f_scale=1.5)
r1 = resid(fit.x)
ok1 = inside(project(fit.x, pts))
print(f"county lines: {len(pts)} true points, {ok1.sum()} on the map; mean distance to a drawn line "
      f"{r0[ok1].mean():.2f} px before, {r1[ok1].mean():.2f} px after; within 1 px {np.mean(r1[ok1] < 1):.0%}")

# county corners: boundary vertices shared by three or more counties (state line corners included)
cnt = Counter()
for g in co.geometry:
    vs = set()
    for poly in getattr(g, "geoms", [g]):
        vs |= {(round(x, 5), round(y, 5)) for x, y in poly.exterior.coords}
    cnt.update(vs)
corners = np.array([v for v, n in cnt.items() if n >= 3])
cxy = project(fit.x, corners)
keep = inside(cxy, 8)
for x0, y0, x1, y1 in [(400, 420, 580, 540), (410, 0, 600, 30), (0, 0, 40, 40)]:
    keep &= ~((cxy[:, 0] > x0 - 5) & (cxy[:, 0] < x1 + 5) & (cxy[:, 1] > y0 - 5) & (cxy[:, 1] < y1 + 5))

# a corner counts only when the drawn lines sit on the fitted lines all around it: the boundary samples
# within 15 px of the corner must be mostly within 1 px of a drawn line, and well covered
pxy = project(fit.x, pts)
new = []
for i in np.nonzero(keep)[0]:
    near = np.hypot(pxy[:, 0] - cxy[i, 0], pxy[:, 1] - cxy[i, 1]) < 15
    if near.sum() < 12:
        continue
    if np.mean(r1[near] < 1.0) < 0.8 or np.median(r1[near]) > 0.7:
        continue
    lon, lat = corners[i]
    names = co[co.geometry.touches(gpd.points_from_xy([lon], [lat])[0]) | co.geometry.intersects(gpd.points_from_xy([lon], [lat])[0].buffer(1e-5))]
    label = " / ".join(sorted(f"{n} {'TX' if s == '48' else 'OK' if s == '40' else 'NM'}" for n, s in zip(names.NAME, names.STATEFP)))
    new.append({"name": f"county corner: {label}", "px": [round(float(cxy[i, 0]), 2), round(float(cxy[i, 1]), 2)],
                "lonlat": [round(float(lon), 6), round(float(lat), 6)],
                "source_ref": "Census cb_2018_us_county_500k, county corner; pixel from fitting the map's drawn county lines to the Census lines (register_counties.py)"})
print(f"{len(new)} county corners confirmed of {keep.sum()} on the map")

# the state line points stay where they carry both axes; the town dots move to check points,
# since Childress showed the dots can sit 7 km off
# but only where the line bends: on the straight 100th meridian (north of the Red River corner) the drawn
# line says nothing about north-south position, so those points' y pixels were only the old affine guess
state = [g for g in gcps if g["name"].startswith("TX-OK line")
         and not (abs(g["lonlat"][0] + 100.0) < 0.002 and g["lonlat"][1] > 34.57)]
print(f"state line: kept {len(state)} Red River points, dropped {sum(g['name'].startswith('TX-OK line') for g in gcps) - len(state)} on the straight meridian")
towns = [g for g in gcps if not g["name"].startswith("TX-OK line")]
try:
    towns += json.load(open(gcps_in.replace(".json", "_checkpoints.json")))
except FileNotFoundError:
    pass
json.dump(state + new, open(out, "w"), indent=1)
json.dump(towns, open(out.replace(".json", "_checkpoints.json"), "w"), indent=1)
print(f"{len(state) + len(new)} control points written to {out}; {len(towns)} town dots to the checkpoints file")
