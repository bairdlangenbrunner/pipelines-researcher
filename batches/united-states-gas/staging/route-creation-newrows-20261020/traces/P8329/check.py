import json
from shapely.geometry import shape, Point
from pyproj import Geod
f=json.load(open('../../fetched_layers/P8329_traced.geojson'))['features'][0]['geometry']
g=shape(f); geod=Geod(ellps='WGS84')
L=sum(geod.geometry_length(l) for l in (g.geoms if hasattr(g,'geoms') else [g]))/1000
print('km',L,'mi',L/1.609344,'ratio to 33 mi',L/1.609344/33)
cty={x['properties']['NAME']:shape(x['geometry']) for x in json.load(open('geo/counties.geojson'))['features']}
parts=list(g.geoms) if hasattr(g,'geoms') else [g]
for i,p in enumerate(parts):
    for lab,c in (('start',p.coords[0]),('end',p.coords[-1])):
        print(i,lab,[round(v,4) for v in c],[n for n,s in cty.items() if s.contains(Point(c))])
for n,s in cty.items(): print(n,'km inside',sum(geod.geometry_length(p.intersection(s)) for p in parts)/1000)
