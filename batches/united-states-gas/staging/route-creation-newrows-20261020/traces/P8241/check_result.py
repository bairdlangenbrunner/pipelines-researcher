"""Sanity checks for P8241: geodesic length, endpoints vs Census roads/places, counties crossed, overlay of final line on the mosaic with TIGER roads."""
import json, glob, numpy as np, geopandas as g
from pyproj import Geod
from shapely.geometry import shape, Point
DL=glob.glob('/private/tmp/claude-501/*/b8a48c22*/scratchpad/p8241_dl')[0]
f=json.load(open('../../fetched_layers/P8241_traced.geojson'))['features'][0]
geom=shape(f['geometry']); geo=Geod(ellps='WGS84')
parts=list(geom.geoms) if geom.geom_type=='MultiLineString' else [geom]
L=sum(geo.geometry_length(p) for p in parts)/1000
print('parts',len(parts),'length km',round(L,2),'mi',round(L/1.609344,2),'ratio to 30 mi',round(L/1.609344/30,3))
pts=[c for p in parts for c in p.coords]
s,e=pts[0],pts[-1]; print('start',s,'end',e)
r=g.read_file(f'{DL}/tl_2023_26013_roads/tl_2023_26013_roads.shp')
for nm in ['State Hwy M38','Grist Mill Rd','Krolik Rd','US Hwy 41','Old US Hwy 41']:
    sub=r[r.FULLNAME==nm]
    dd=[(geo.inv(e[0],e[1],*x.geometry.interpolate(x.geometry.project(Point(e))).coords[0])[2],x.LINEARID) for x in sub.itertuples()]
    print('end to',nm,round(min(dd)[0]),'m')
c=g.read_file(f'{DL}/tl_2023_us_county/tl_2023_us_county.shp',bbox=(-88.9,46.4,-88.0,47.0)); c=c[c.STATEFP=='26']
order=[]
for p in pts:
    for x in c.itertuples():
        if x.geometry.contains(Point(p)):
            if not order or order[-1]!=x.NAME: order.append(x.NAME)
print('counties in order',order)
# distance from line to US 41 at the start and to the Three Lakes place
pl=g.read_file(f'{DL}/tl_2023_26_place/tl_2023_26_place.shp')
pl=pl.to_crs(4326)
ctr=pl.geometry.representative_point()
for nm in ['Baraga','L\'Anse','Three Lakes']:
    m=pl[pl.NAME==nm]
    for x in m.itertuples():
        d=min(geo.inv(x.geometry.representative_point().x,x.geometry.representative_point().y,*p)[2] for p in pts)
        print('place',nm,'nearest line vertex m',round(d))
