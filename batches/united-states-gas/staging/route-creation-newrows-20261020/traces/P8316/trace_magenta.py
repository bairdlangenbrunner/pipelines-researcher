"""Extract the magenta pipeline centerline from the figure as pixel polylines (P8316 McCloud Lateral).
Color mask -> closing -> skeleton -> longest path through the skeleton graph -> simplify ~1 px."""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize, binary_closing, disk
from skimage.measure import approximate_polygon
import networkx as nx
R='batches/united-states-gas/staging/route-creation-newrows-20261020/'
img=Image.open(R+'maps/P8316/mccloud-fig1-1-p9-009.png').convert('RGB')
a=np.array(img).astype(int)
r,g,b=a[...,0],a[...,1],a[...,2]
mask=(r>120)&(r-g>70)&(b-g>35)&(r-b>5)&(r-b<90)
mask[:200]=False; mask[868:]=False; mask[:,:172]=False; mask[:,1478:]=False
# drop the meter-station fill: it is a larger solid blob, handled below by opening test
m=binary_closing(mask,disk(2))
lab,n=ndi.label(m,structure=np.ones((3,3)))
sizes=ndi.sum(m,lab,range(1,n+1))
keep=[i+1 for i,s in enumerate(sizes) if s>150]
m=np.isin(lab,keep)
Image.fromarray((m*255).astype('uint8')).save(R+'traces/P8316/mask.png')
sk=skeletonize(m)
ys,xs=np.nonzero(sk)
G=nx.Graph()
S=set(zip(xs,ys))
for (x,y) in S:
    for dx in (-1,0,1):
        for dy in (-1,0,1):
            if (dx or dy) and (x+dx,y+dy) in S:
                G.add_edge((x,y),(x+dx,y+dy),weight=(dx*dx+dy*dy)**.5)
comps=sorted(nx.connected_components(G),key=len,reverse=True)
print('components',[len(c) for c in comps][:8])
# bridge gaps (places where the magenta is hidden by the black limit-of-disturbance outline):
# join each component to the nearest other one by the closest pair of skeleton pixels, if under 80 px
from scipy.spatial import cKDTree
big=[c for c in comps if len(c)>40]
import itertools
while len(big)>1:
    best=None
    for ca,cb in itertools.combinations(range(len(big)),2):
        A=np.array(list(big[ca])); B=np.array(list(big[cb]))
        t=cKDTree(B); d,i=t.query(A); k=int(np.argmin(d))
        if best is None or d[k]<best[0]: best=(d[k],ca,cb,tuple(A[k]),tuple(B[i[k]]))
    d,ca,cb,pa,pb=best
    print('bridge',pa,pb,round(d,1))
    assert d<80
    G.add_edge(pa,pb,weight=float(d))
    big[ca]=big[ca]|big[cb]; del big[cb]
comps=[big[0]]
out=[]
for c in comps[:1]:
    H=G.subgraph(c)
    u=next(iter(c)); d=nx.single_source_dijkstra_path_length(H,u); a0=max(d,key=d.get)
    d=nx.single_source_dijkstra_path_length(H,a0); b0=max(d,key=d.get)
    path=nx.dijkstra_path(H,a0,b0)
    print('endpoints',a0,b0,'len px',d[b0])
    pl=approximate_polygon(np.array(path,float),1.0)
    out.append(pl.tolist())
json.dump({"image":"maps/P8316/mccloud-fig1-1-p9-009.png","polylines":out,"notes":"magenta centerline by color mask and skeleton; see trace_magenta.py"},open(R+'traces/P8316/trace.json','w'))
# overlay
ov=img.copy()
from PIL import ImageDraw
dr=ImageDraw.Draw(ov)
for pl in out:
    dr.line([tuple(p) for p in pl],fill=(0,255,0),width=1)
ov.save(R+'traces/P8316/overlay_trace.png')
