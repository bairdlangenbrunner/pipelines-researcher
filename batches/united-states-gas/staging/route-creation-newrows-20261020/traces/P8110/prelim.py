"""Preview-only: rough city-dot fit, then draw Census parish outlines over the map to find corner vertices."""
import numpy as np, geopandas as gpd, json
from PIL import Image, ImageDraw
D='/private/tmp/claude-501/census_dl/'
pl=gpd.read_file(D+'place/cb_2023_22_place_500k.shp').to_crs(4326)
pts={'Monroe':(328,232),'Alexandria':(130,1053),'Lafayette':(397,1785),'Baton Rouge':(887,1627),'New Orleans':(1552,1947),'Slidell':(1722,1722),'Houma':(1173,2200)}
A=[];B=[]
for n,(x,y) in pts.items():
    r=pl[pl.NAME==n].iloc[0].geometry.centroid; print(n,r.x,r.y); A.append([x,y,1]);B.append([r.x,r.y])
A=np.array(A,float);B=np.array(B)
M,res,_,_=np.linalg.lstsq(A,B,rcond=None); np.save('prelim_M.npy',M)
Minv=np.linalg.lstsq(np.c_[B,np.ones(len(B))],np.array([[p[0],p[1]] for p in pts.values()],float),rcond=None)[0]
print('resid px',np.abs(A@M-B).max(axis=0))
cty=gpd.read_file(D+'county/cb_2023_us_county_500k.shp').to_crs(4326)
cty=cty[cty.STATEFP.isin(['22','28'])]
im=Image.open('map250.png').convert('RGB'); d=ImageDraw.Draw(im)
def topx(lon,lat): return tuple(np.array([lon,lat,1])@Minv)
for _,r in cty.iterrows():
    g=r.geometry; gs=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
    for p in gs:
        c=[topx(x,y) for x,y in p.exterior.coords]; d.line(c,fill=(255,0,255),width=1)
im.save('prelim_counties.png')
