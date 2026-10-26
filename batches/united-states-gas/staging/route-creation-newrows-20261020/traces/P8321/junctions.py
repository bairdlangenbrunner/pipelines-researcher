# all intersections between different named TIGER road centerlines (public Census data); lon/lat exact from geometry
import json,itertools
from shapely.geometry import LineString
from shapely.strtree import STRtree
R=json.load(open('tiger_roads.json'))
segs=[]
for L in R:
    for nm,mt,paths in R[L]:
        for p in paths:
            if nm and len(p)>1:segs.append((nm,mt,LineString(p)))
tree=STRtree([s[2] for s in segs]);out=[]
for i,(n,m,g) in enumerate(segs):
    for j in tree.query(g):
        if j<=i:continue
        n2,m2,g2=segs[j]
        if n2==n:continue
        x=g.intersection(g2)
        pts=[x] if x.geom_type=='Point' else list(getattr(x,'geoms',[]))
        for q in pts:
            if q.geom_type=='Point':out.append({'lon':q.x,'lat':q.y,'roads':[n,n2],'mtfcc':[m,m2]})
json.dump(out,open('junctions.json','w'));print(len(out))
