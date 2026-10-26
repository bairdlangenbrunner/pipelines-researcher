# where TIGER road centerlines cross the USGS 7.5-minute quadrangle boundaries (lat 40.625 N, lon -80.375 W)
import json
from shapely.geometry import LineString
R=json.load(open('tiger_roads.json'))
H=LineString([(-80.50,40.625),(-80.25,40.625)]);V=LineString([(-80.375,40.5),(-80.375,40.75)])
out=[]
for L in R:
    for nm,mt,paths in R[L]:
        for p in paths:
            g=LineString(p)
            for k,ln in (('H',H),('V',V)):
                x=g.intersection(ln)
                for q in ([x] if x.geom_type=='Point' else list(getattr(x,'geoms',[]))):
                    if q.geom_type=='Point':out.append({'kind':k,'name':nm,'mtfcc':mt,'lon':q.x,'lat':q.y})
json.dump(out,open('quad_crossings.json','w'),indent=0)
import sys
sys.path.insert(0,'.')
from prelim_roads import px
for i,o in enumerate(out):
    x,y=px(o['lon'],o['lat']);print(i,o['kind'],o['name'],o['mtfcc'],round(o['lon'],5),round(o['lat'],5),round(x),round(y))
