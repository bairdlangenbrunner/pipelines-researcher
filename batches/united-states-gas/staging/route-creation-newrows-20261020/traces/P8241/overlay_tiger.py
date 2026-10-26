"""Draw Census TIGER 2023 roads, water edges, county line on the mosaic using a given affine (lonlat->frame px) to find/verify GCPs.
usage: overlay_tiger.py x0 y0 x1 y1 out.png   (frame coords)"""
import sys, glob, json, numpy as np, geopandas as g
from PIL import Image, ImageDraw
DL=glob.glob('/private/tmp/claude-501/*/b8a48c22*/scratchpad/p8241_dl')[0]
co=np.array(json.load(open('prelim_affine.json')))   # px->lonlat 3x2
# invert
A=co[:2].T  # 2x2: [lon,lat]=A@[x,y]+b
b=co[2]; Ai=np.linalg.inv(A)
def tp(lon,lat): return Ai@(np.array([lon,lat])-b)
x0,y0,x1,y1=map(int,sys.argv[1:5]); out=sys.argv[5]
M=Image.open('mosaic.png').convert('RGB'); ox,oy=-1800,-2000
crop=M.crop((x0-ox,y0-oy,x1-ox,y1-oy)); d=ImageDraw.Draw(crop)
def draw(geom,col):
    gs=geom.geoms if hasattr(geom,'geoms') else [geom]
    for s in gs:
        if s.geom_type=='Polygon': draw(s.exterior,col); continue
        pts=[tuple(tp(*c[:2])-np.array([x0,y0])) for c in s.coords]
        d.line(pts,fill=col,width=2)
for cty in ['26013','26061']:
    r=g.read_file(f'{DL}/tl_2023_{cty}_roads/tl_2023_{cty}_roads.shp')
    for x in r.itertuples():
        if x.FULLNAME and ('Hwy' in x.FULLNAME or 'Rd' in x.FULLNAME or 'Highway' in x.FULLNAME): draw(x.geometry,(0,255,255))
    w=g.read_file(f'{DL}/tl_2023_{cty}_areawater/tl_2023_{cty}_areawater.shp')
    for x in w.itertuples():
        if x.AWATER>150000: draw(x.geometry,(255,0,255))
c=g.read_file(f'{DL}/tl_2023_us_county/tl_2023_us_county.shp',bbox=(-88.9,46.4,-88.0,47.0))
for x in c.itertuples(): draw(x.geometry.boundary,(255,255,255))
crop.save(out)
