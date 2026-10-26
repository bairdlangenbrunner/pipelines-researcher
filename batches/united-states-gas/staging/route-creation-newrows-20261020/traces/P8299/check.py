import json
from pyproj import Geod
g=Geod(ellps='WGS84')
c=json.load(open('../../fetched_layers/P8299_traced.geojson'))['features'][0]['geometry']['coordinates']
L=sum(g.inv(*c[i],*c[i+1])[2] for i in range(len(c)-1))/1000
print('length km',round(L,2),'mi',round(L/1.609344,2),'ratio to 46 mi',round(L/1.609344/46,3))
print('start',c[0],'end',c[-1])
# distance of named places (Census internal points, not used as GCPs) to the line, densified
import numpy as np
pts=[]
for i in range(len(c)-1):
    n=max(2,int(g.inv(*c[i],*c[i+1])[2]/100))
    for t in np.linspace(0,1,n): pts.append((c[i][0]+t*(c[i+1][0]-c[i][0]),c[i][1]+t*(c[i+1][1]-c[i][1])))
for name,lo,la in [("Elkhorn city",-88.536256,42.671601),("Burlington city",-88.307489,42.664897),("Union Grove village",-88.049539,42.686397),("Rochester village",-88.250323,42.732913),("Geneva town",-88.48205,42.629891)]:
    print(name,round(min(g.inv(lo,la,p[0],p[1])[2] for p in pts)/1000,2),'km from line')
