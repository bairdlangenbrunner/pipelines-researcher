"""Candidate GCP vertices: Census 2023 county-boundary vertices with straight edges of 3.5 km or more on both sides and a sharp turn (>=50 deg), plus tri-junctions."""
import numpy as np, geopandas as gpd, json
from pyproj import Geod
from PIL import Image, ImageDraw
g=Geod(ellps='WGS84')
D='/private/tmp/claude-501/census_dl/'
M=np.load('prelim_M.npy'); L=M[:2].T; t=M[2]
cty=gpd.read_file(D+'county/cb_2023_us_county_500k.shp').to_crs(4326)
cty=cty[cty.STATEFP.isin(['22','28'])]
out=[]
for _,r in cty.iterrows():
    gg=r.geometry; gs=list(gg.geoms) if gg.geom_type=='MultiPolygon' else [gg]
    for p in gs:
        c=list(p.exterior.coords)[:-1]; n=len(c)
        for i in range(n):
            a,b,d=c[i-1],c[i],c[(i+1)%n]
            _,_,l1=g.inv(a[0],a[1],b[0],b[1]); _,_,l2=g.inv(b[0],b[1],d[0],d[1])
            if l1<3500 or l2<3500: continue
            a1,_,_=g.inv(a[0],a[1],b[0],b[1]); a2,_,_=g.inv(b[0],b[1],d[0],d[1])
            turn=abs((a2-a1+180)%360-180)
            if turn<60: continue
            px=np.linalg.solve(L,np.array(b)-t)
            if 60<px[0]<2100 and 60<px[1]<2370: out.append({'name':r.NAME,'st':r.STATEFP,'lonlat':[b[0],b[1]],'px0':px.tolist(),'turn':round(turn),'l1km':round(l1/1000,1),'l2km':round(l2/1000,1)})
for i,o in enumerate(out): o['id']=i
json.dump(out,open('corner_candidates.json','w'))
im=Image.open('map250.png').convert('RGB'); d=ImageDraw.Draw(im)
for o in out:
    x,y=o['px0']; d.ellipse([x-4,y-4,x+4,y+4],outline=(255,0,255),width=2); d.text((x+6,y-6),str(o['id']),fill=(255,0,255))
im.save('corners.png'); print(len(out))
