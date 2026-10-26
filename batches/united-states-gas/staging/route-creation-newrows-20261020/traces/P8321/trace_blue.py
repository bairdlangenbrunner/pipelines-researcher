# extract the blue Line N Lateral from the USGS project location map by color mask, skeletonize, chain, simplify
import json,sys,numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
IMG='../../maps/P8321/appxA-usgs-p4-04.png'
im=np.array(Image.open(IMG).convert('RGB')).astype(int)
r,g,b=im[...,0],im[...,1],im[...,2]
m=(b>180)&(r<60)&(g>80)&(g<150); m[1300:]=False
m=ndi.binary_closing(m,iterations=2); m=ndi.binary_dilation(m,iterations=3)
lab,n=ndi.label(m,structure=np.ones((3,3)))
sizes=ndi.sum(m,lab,range(1,n+1)); print('components',sorted(sizes)[-5:])
m=lab==(1+int(np.argmax(sizes)))
sk=skeletonize(m)
pts=set(map(tuple,np.argwhere(sk)))
nb=lambda p:[(p[0]+i,p[1]+j) for i in(-1,0,1) for j in(-1,0,1) if (i or j) and (p[0]+i,p[1]+j) in pts]
ends=[p for p in pts if len(nb(p))==1]
print('endpoints (y,x)',ends)
# longest path via two BFS
from collections import deque
def bfs(s):
    d={s:0};par={s:None};q=deque([s]);last=s
    while q:
        u=q.popleft();last=u
        for v in nb(u):
            if v not in d:d[v]=d[u]+1;par[v]=u;q.append(v)
    return last,par
a,_=bfs(next(iter(pts)));b2,par=bfs(a)
path=[];p=b2
while p:path.append(p);p=par[p]
path=[(x,y) for y,x in path]
# order from NW (start) to SE
if path[0][0]>path[-1][0]:path=path[::-1]
def rdp(P,e):
    P=np.array(P,float)
    if len(P)<3:return P.tolist()
    s,t=P[0],P[-1];d=t-s;L=np.hypot(*d)
    dist=np.abs(np.cross(d,P-s))/L if L else np.hypot(*(P-s).T)
    i=int(np.argmax(dist))
    if dist[i]>e:return rdp(P[:i+1],e)[:-1]+rdp(P[i:],e)
    return [P[0].tolist(),P[-1].tolist()]
poly=[[round(x,1),round(y,1)] for x,y in rdp(path,1.0)]
print(len(path),len(poly),poly[0],poly[-1])
json.dump({"image":"maps/P8321/appxA-usgs-p4-04.png","polylines":[poly],"notes":"blue Line N Lateral extracted by color mask and skeleton; sheet 1 of 3 of Appendix A. The line end near Service Creek Tie is where the blue line ends before the green tie symbol."},open('trace.json','w'))
