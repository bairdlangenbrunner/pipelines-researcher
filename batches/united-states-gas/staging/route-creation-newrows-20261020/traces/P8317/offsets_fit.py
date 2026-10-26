import numpy as np, json
from pyproj import Transformer
from gcp_raw import G
S=1.006  # m per px, from the printed 1000 ft scale bar (303 px)
tr=Transformer.from_crs(4326,32617,always_xy=True)
off={}
for k in range(1,6):
    v=[]
    for s,n,x,y,lo,la,ref in G:
        if s!=k: continue
        E,N=tr.transform(lo,la); v.append((E/S-x,-N/S-y,n))
    print(k,[(round(a),round(b),n) for a,b,n in v])
    off[k]=(np.mean([a for a,b,n in v]),np.mean([b for a,b,n in v]))
for k in range(1,5):
    print('gcp-derived shift k->k+1 :',round(off[k+1][0]-off[k][0]),round(off[k+1][1]-off[k][1]))
