"""Register the Aug-2025 asset map (county lines) to Census counties in its NE quadrant, then draw the
P7861 route file and the 2026-map trace on it to see which sits on the tan residue line.

Usage: python check_2025_map.py <census county shp> <routes repo P7861.geojson> residue_header_v2.geojson
The map is the Wayback copy (20250822154545) of producersmidstream.com/wp-content/uploads/2025/08/main-map-updated-1-1.jpg."""
import json, sys
import numpy as np, geopandas as gpd
from PIL import Image, ImageDraw
from scipy import ndimage, optimize
from shapely.geometry import box, shape
from shapely.ops import unary_union
im = Image.open("map_2025_assets_wayback20250822.jpg").convert("RGB"); a = np.array(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]; lum = (R + G + B) / 3
gray = (np.max(a, 2) - np.min(a, 2) < 14) & (lum > 120) & (lum < 232)
win = np.zeros_like(gray); win[0:1000, 1000:2048] = True; gray &= win
dt = ndimage.distance_transform_edt(~gray)
co = gpd.read_file(sys.argv[1]).to_crs(4326)
co = co[co.STATEFP.isin(["48", "40"])]
lines = unary_union(co.geometry.boundary.values).intersection(box(-101.6, 34.5, -98.5, 36.6))
pts = []
for part in getattr(lines, "geoms", [lines]):
    for t in np.arange(0, part.length, 0.01):
        p = part.interpolate(t); pts.append((p.x, p.y))
pts = np.array(pts); print(len(pts), "county-line points")
# initial affine from the small-image read: lon -103.04 -> x 490, lon -100 -> x 1594; lat 36.5 -> y 146, lat 34.56 -> y 800
sx = (1596 - 500) / 3.04
def project(p, ll): return np.column_stack([ll @ p[0:2] + p[2], ll @ p[3:5] + p[5]])
def resid(p):
    xy = project(p, pts); return np.minimum(ndimage.map_coordinates(dt, [xy[:, 1], xy[:, 0]], order=1, mode="nearest"), 15.0)
best = None
for sy0 in [-300, -330, -360, -400, -443]:
    p0 = np.array([sx, 0, 1596 + 100 * sx, 0, sy0, 787 - 34.56 * sy0], float)
    fit = optimize.least_squares(resid, p0, method="trf", x_scale="jac"); r = resid(fit.x)
    print("y-scale %d: before %.2f px, after %.2f px; share within 2 px: %.2f" % (sy0, resid(p0).mean(), r.mean(), (r < 2).mean()))
    if best is None or r.mean() < best[0]: best = (r.mean(), fit)
fit = best[1]
P = fit.x
def geo_lines(path):
    d = json.load(open(path)); fs = d["features"] if "features" in d else [d]; out = []
    for f in fs:
        g = shape(f["geometry"]); out += list(g.geoms) if hasattr(g, "geoms") else [g]
    return out
crop = (1200, 150, 2048, 650)
z = im.crop(crop).resize(((crop[2] - crop[0]) * 2, (crop[3] - crop[1]) * 2), Image.LANCZOS); d = ImageDraw.Draw(z)
for path, col in [(sys.argv[2], (255, 0, 0)), (sys.argv[3], (0, 0, 255))]:
    for l in geo_lines(path):
        xy = project(P, np.array(l.coords))
        d.line([((x - crop[0]) * 2, (y - crop[1]) * 2) for x, y in xy], fill=col, width=2)
z.save("check_2025_map.png"); print("wrote check_2025_map.png (red = P7861 route file, blue = 2026-map trace)")
# also the county-line points after the fit, to see the registration quality
z2 = im.crop(crop).copy(); d2 = ImageDraw.Draw(z2)
for x, y in project(P, pts): d2.point((x - crop[0], y - crop[1]), fill=(255, 0, 255))
z2.save("check_2025_map_fit.png")
