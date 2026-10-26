# Extract the orange "PROPOSED PIPELINE" line from each sheet by color mask -> skeleton -> longest chain -> simplify.
import numpy as np, json
from PIL import Image
from skimage.morphology import skeletonize, remove_small_objects
from skimage.measure import approximate_polygon
from collections import deque
M='../../maps/P8317/pagwis-fig1-%d.png'
out={}
for k in range(1,6):
    im=np.asarray(Image.open(M%k).convert('RGB')).astype(int)
    R,G,B=im[...,0],im[...,1],im[...,2]
    m=(R>225)&(G>135)&(G<200)&(B<70)
    m[:70,:]=False; m[2290:,:]=False; m[:,:40]=False; m[:,1620:]=False
    m[1950:,1270:]=False   # legend
    from skimage.morphology import binary_closing, disk
    m=binary_closing(m,disk(7)); m=remove_small_objects(m,60)
    sk=skeletonize(m)
    ys,xs=np.nonzero(sk); pts=set(zip(xs.tolist(),ys.tolist()))
    def nb(p):
        for dx in(-1,0,1):
            for dy in(-1,0,1):
                if (dx or dy) and (p[0]+dx,p[1]+dy) in pts: yield (p[0]+dx,p[1]+dy)
    def bfs(s):
        d={s:0};prev={s:None};q=deque([s])
        while q:
            u=q.popleft()
            for v in nb(u):
                if v not in d: d[v]=d[u]+1;prev[v]=u;q.append(v)
        return d,prev
    # components
    seen=set();comps=[]
    for p in pts:
        if p in seen: continue
        d,_=bfs(p); seen|=set(d); comps.append(list(d))
    comps.sort(key=len,reverse=True)
    print('sheet',k,'skeleton px',len(pts),'components',[len(c) for c in comps[:5]])
    polys=[]
    for c in comps:
        if len(c)<80: continue
        s=c[0]; d,_=bfs(s); a=max(d,key=d.get); d,prev=bfs(a); b=max(d,key=d.get)
        path=[];u=b
        while u is not None: path.append(u);u=prev[u]
        arr=np.array(path,float)
        simp=approximate_polygon(arr,tolerance=1.0)
        polys.append(simp.tolist()); print('  chain',len(path),'simplified',len(simp),'ends',path[0],path[-1])
    out[k]=polys
    Image.fromarray((m*255).astype(np.uint8)).save('/private/tmp/claude-501/mask%d.png'%k)
json.dump(out,open('orange_by_sheet.json','w'))
