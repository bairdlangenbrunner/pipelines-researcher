# Computes independent lon/lat candidates from Census TIGERweb county and road geometry.
import json, itertools
from shapely.geometry import shape, Point, MultiPoint
from shapely.ops import unary_union
g=lambda f:[(x['properties']['NAME'],shape(x['geometry'])) for x in json.load(open(f))['features']]
cty=dict(g('geo/counties.geojson'))
roads=g('geo/roads_2.geojson')+g('geo/roads_5.geojson')+g('geo/roads_6.geojson')
def rd(name):
    return unary_union([s for n,s in roads if n and name.lower() in n.lower()])
def pts(x):
    if x.is_empty: return []
    return [ (round(p.x,5),round(p.y,5)) for p in (x.geoms if hasattr(x,'geoms') else [x])]
names=list(cty)
print('county tripoints')
for a,b,c in itertools.combinations(names,3):
    print(a,b,c,[pts(cty[a].boundary.intersection(cty[b].boundary).intersection(cty[c].boundary))])
r=cty['Racine County'];m=cty['Milwaukee County'];k=cty['Kenosha County']
for nm in ['I- 41','US Hwy 41','State Hwy 20','State Hwy 11','State Hwy 75','US Hwy 45','State Hwy 38','State Hwy 32','State Hwy 31','State Hwy 36','Co Hwy K','Co Hwy G']:
    R=rd(nm); print(nm, 'x Racine/Milw line', pts(R.intersection(r.boundary.intersection(m.boundary))), 'x Racine/Kenosha', pts(R.intersection(r.boundary.intersection(k.boundary))))
import sys
roadsets=['I- 41','State Hwy 20','State Hwy 11','State Hwy 75','US Hwy 45','State Hwy 38','State Hwy 32','State Hwy 31','State Hwy 36']
for a,b in itertools.combinations(roadsets,2):
    p=pts(rd(a).intersection(rd(b)))
    if p: print(a,'x',b,p)
