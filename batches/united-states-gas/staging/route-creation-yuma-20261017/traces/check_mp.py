import numpy as np, json, sys
import geopandas as gpd
from pyproj import Geod
from shapely.geometry import Point, LineString
geod=Geod(ellps='WGS84')
T=np.array(json.load(open('trace.json'))['polylines'][0])
mp={int(k):v for k,v in json.load(open('mileposts_px.json')).items()}
nat=gpd.read_file('../tiger/nation.zip').geometry.iloc[0].boundary
for f in sys.argv[1:]:
    C=np.array(json.load(open(f))['features'][0]['geometry']['coordinates'])
    assert len(C)==len(T), (len(C),len(T))
    seg=[geod.inv(*C[i],*C[i+1])[2] for i in range(len(C)-1)]; cum=np.r_[0,np.cumsum(seg)]/1609.344
    ch={}
    for k,(x,y) in mp.items():
        # project onto pixel polyline: nearest segment param
        best=None
        for i in range(len(T)-1):
            p,q=T[i],T[i+1]; d=q-p; t=np.clip(np.dot([x,y]-p,d)/max(np.dot(d,d),1e-9),0,1); r=np.hypot(*([x,y]-(p+t*d)))
            if best is None or r<best[0]: best=(r,i,t)
        r,i,t=best; ch[k]=cum[i]+t*(cum[i+1]-cum[i])
    ks=sorted(ch); diffs=[round(ch[ks[j+1]]-ch[ks[j]],2) for j in range(len(ks)-1)]
    end=Point(*C[-1]); dist_border=geod.inv(*C[-1],*np.array(nat.interpolate(nat.project(end)).coords[0]))[2]
    print(f, 'total %.1f mi'%cum[-1], 'MP0 at %.2f'%ch[0], 'MP130 at %.2f'%ch[130])
    print('  10-mi intervals', diffs, 'mean %.2f sd %.2f'%(np.mean(diffs),np.std(diffs)))
    print('  SW end', np.round(C[-1],5),'distance to US-Mexico border %.0f m'%dist_border)
