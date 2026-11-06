import json,sys
from pyproj import Geod
G=Geod(ellps='WGS84')
F=json.load(open('/Users/baird/Dropbox/_git_ALL/_github-repos-gem/GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines/P0271.geojson'))['features']
c=F[101]['geometry']['coordinates']; cum=[0.0]
for a,b in zip(c,c[1:]): cum.append(cum[-1]+G.inv(a[0],a[1],b[0],b[1])[2]/1609.344)
def at(m):
    import bisect
    i=bisect.bisect_left(cum,m); i=min(max(i,1),len(c)-1); u,v=c[i-1],c[i]; t=(m-cum[i-1])/((cum[i]-cum[i-1]) or 1)
    return [round(u[0]+t*(v[0]-u[0]),6),round(u[1]+t*(v[1]-u[1]),6)]
def sub(m0,m1):
    import bisect
    i0=bisect.bisect_right(cum,m0); i1=bisect.bisect_left(cum,m1)
    return [at(m0)]+[list(p) for p in c[i0:i1]]+[at(m1)]
