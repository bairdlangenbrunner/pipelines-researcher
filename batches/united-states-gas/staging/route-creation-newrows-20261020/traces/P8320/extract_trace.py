"""Extract the blue (Phase 1) and orange (Phase 2) pipeline lines from the map image by color mask, skeletonize, chain, simplify."""
import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
a=np.array(Image.open('img-000.png').convert('RGB')).astype(int)
r,g,b=a[...,0],a[...,1],a[...,2]
blue=(b>120)&(r<60)&(g<110)&(b-r>90)
org=(r>230)&(g>130)&(g<190)&(b<60)
def largest(m):
    m=ndi.binary_closing(m,iterations=2)
    l,n=ndi.label(m,structure=np.ones((3,3)))
    s=ndi.sum(m,l,range(1,n+1)); print('components',sorted(s)[-3:])
    return l==(1+int(np.argmax(s)))
def chain(sk):
    ys,xs=np.nonzero(sk); pts=set(zip(xs,ys))
    nb=lambda p:[(p[0]+dx,p[1]+dy) for dx in(-1,0,1) for dy in(-1,0,1) if(dx or dy) and (p[0]+dx,p[1]+dy) in pts]
    ends=[p for p in pts if len(nb(p))==1]
    # longest path via BFS from an end, twice (tree diameter)
    def bfs(s):
        prev={s:None};q=[s]
        for p in q:
            for n in nb(p):
                if n not in prev: prev[n]=p;q.append(n)
        return q[-1],prev
    s=ends[0] if ends else next(iter(pts))
    e,_=bfs(s); f,prev=bfs(e)
    path=[];p=f
    while p: path.append(p);p=prev[p]
    return path[::-1]
def simplify(path,tol=1.5):
    from shapely.geometry import LineString
    return [list(map(float,c)) for c in LineString(path).simplify(tol).coords]
out={}
for n,m in(('blue',blue),('org',org)):
    sk=skeletonize(largest(m)); p=chain(sk); out[n]=simplify(p); print(n,len(p),len(out[n]),p[0],p[-1])
json.dump(out,open('raw_lines.json','w'))
