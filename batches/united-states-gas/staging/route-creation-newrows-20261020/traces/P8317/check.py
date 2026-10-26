# sanity check: geodesic length, endpoints, and named TIGER roads the traced line crosses, in order from the north end
import json, geopandas as gpd
from shapely.geometry import shape
from pyproj import Geod
f=json.load(open('../../fetched_layers/P8317_traced.geojson'))['features'][0]
g=shape(f['geometry']); geod=Geod(ellps='WGS84')
parts=[g] if g.geom_type=='LineString' else list(g.geoms)
L=sum(geod.geometry_length(p) for p in parts)/1000
print('parts',len(parts),'length km %.3f mi %.3f (stated 5.8 mi, ratio %.3f)'%(L,L/1.609344,L/1.609344/5.8))
c=list(parts[0].coords); e=list(parts[-1].coords)
print('start',c[0],'end',e[-1])
roads=gpd.read_file('/private/tmp/claude-501/tiger63/tl_2023_42063_roads.shp')
b=g.buffer(0.0004)
near=roads[roads.intersects(b)]
res=[]
for i,r in near.iterrows():
    if r.FULLNAME is None: continue
    x=r.geometry.intersection(g.buffer(0.00005))
    if x.is_empty: continue
    pt=x.representative_point(); res.append((-pt.y,r.FULLNAME,round(pt.x,5),round(pt.y,5)))
seen=set()
for t in sorted(res):
    if t[1] in seen: continue
    seen.add(t[1]); print(t[1],t[2],t[3])
# county / state
import shapely
