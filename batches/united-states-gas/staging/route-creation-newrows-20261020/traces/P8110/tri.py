"""List county tri-junction vertices (shared by 3+ counties/state) from Census 2023 500k, with preliminary pixel for picking."""
import numpy as np, geopandas as gpd, json
from collections import defaultdict
from PIL import Image, ImageDraw
D='/private/tmp/claude-501/census_dl/'
M=np.load('prelim_M.npy')
cty=gpd.read_file(D+'county/cb_2023_us_county_500k.shp').to_crs(4326)
cty=cty[cty.STATEFP.isin(['22','28'])]
V=defaultdict(set)
for _,r in cty.iterrows():
    g=r.geometry; gs=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
    for p in gs:
        for x,y in p.exterior.coords: V[(round(x,6),round(y,6))].add(r.NAME+','+r.STATEFP)
tri={k:v for k,v in V.items() if len(v)>=3}
Minv=np.linalg.lstsq(np.c_[M.T@np.eye(2)*0,np.ones(0)] if False else np.eye(3),np.eye(3),rcond=None)[0]
# invert affine: pixel = solve
A=np.c_[M[:2],]  # 2x2 from lonlat? M maps [x,y,1]->lonlat
L=M[:2].T; t=M[2]
out=[]
im=Image.open('map250.png').convert('RGB'); d=ImageDraw.Draw(im)
for i,(k,v) in enumerate(sorted(tri.items(), key=lambda kv:-kv[0][1])):
    px=np.linalg.solve(L,np.array(k)-t)
    if 60<px[0]<2100 and 60<px[1]<2370:
        out.append((i,k,px.tolist(),sorted(v))); d.ellipse([px[0]-3,px[1]-3,px[0]+3,px[1]+3],outline=(0,0,255)); d.text((px[0]+4,px[1]-4),str(i),fill=(0,0,255))
json.dump(out,open('tri_candidates.json','w'))
im.save('tri.png'); print(len(out))
