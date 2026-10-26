"""Render page 685 beside the extracted route clipped to the page frame, same extent, for a shape comparison."""
import sys, fitz, numpy as np, geopandas as gpd
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from geopdf import PageGeoref
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from PIL import Image
from shapely.geometry import box
S, out = sys.argv[1], sys.argv[2]
doc = fitz.open(f"{S}/p8327/dl/march_rr1_10.pdf"); g = PageGeoref(doc, 685)
im = Image.open(f"{S}/p8327/fix/pages/p685_150-685.png"); sc = im.size[0] / g.page.rect.width
b = g.bbox; H = g.page.rect.height
crop = im.crop((int(b[0]*sc), int((H-b[3])*sc), int(b[2]*sc), int((H-b[1])*sc)))
lay = gpd.read_file(f"{S}/p8327/fix/p685_layers.geojson")
roads = gpd.pd.concat([gpd.read_file(f"{S}/tiger_dl/tl_2023_{f}_roads/tl_2023_{f}_roads.shp") for f in ("38045",)])
water = gpd.read_file(f"{S}/tiger_dl/tl_2023_38045_linearwater/tl_2023_38045_linearwater.shp")
# frame corners in lon/lat
corners = np.array([g.lonlat(b[0], H-b[1]), g.lonlat(b[2], H-b[1]), g.lonlat(b[2], H-b[3]), g.lonlat(b[0], H-b[3])])
x0, x1, y0, y1 = corners[:,0].min(), corners[:,0].max(), corners[:,1].min(), corners[:,1].max()
fig, axs = plt.subplots(1, 2, figsize=(16, 9.5))
axs[0].imshow(crop); axs[0].set_title("page 685 as rendered (frame only)"); axs[0].axis("off")
ax = axs[1]; bb = box(x0, y0, x1, y1)
rr = roads[roads.intersects(bb)]; rr.plot(ax=ax, color="#c8c8c8", lw=0.6)
ww = water[water.intersects(bb)]; ww.plot(ax=ax, color="#8fd0ff", lw=0.7)
lay[lay.drawing == 48].plot(ax=ax, color="gray", ls="--", lw=1)
lay[lay.drawing == 63].plot(ax=ax, color="#0070ff", lw=2)
lay[lay.drawing == 64].plot(ax=ax, color="#032dff", lw=1.5, ls="--")
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect(1/np.cos(np.radians((y0+y1)/2)))
ax.set_title("extracted drawings 63 (Alt 1) and 64 (preferred, dashed) over TIGER roads and water")
plt.tight_layout(); plt.savefig(out, dpi=100); print("wrote", out)
