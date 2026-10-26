"""Extract the four colored segment lines from the 200 dpi renders (pg-17..20.png), thin to a one pixel
centerline, take the longest path, simplify, move into one shared mosaic frame, and write trace.json.
Mosaic frame = page 17 pixel frame. Offsets come from stitch_offsets.py (page B = page A + d)."""
import json, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
from skimage.measure import approximate_polygon
from collections import deque
COL={'17':(232,72,72),'18':(184,72,168),'19':(216,232,56),'20':(104,200,152)}
# page -> shift to add to page pixels to get mosaic (page17) frame
SH={'17':(0,0),'18':(-960,-173),'19':(-1604,-949),'20':(-1791,-2016)}
FR=(150,190,1560,2050)  # inside the map frame
def longest_path(sk):
    ys,xs=np.nonzero(sk); pts=set(zip(ys,xs))
    nb=[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    def bfs(s):
        d={s:0};par={s:None};q=deque([s]);last=s
        while q:
            u=q.popleft();last=u
            for dy,dx in nb:
                v=(u[0]+dy,u[1]+dx)
                if v in pts and v not in d: d[v]=d[u]+1;par[v]=u;q.append(v)
        return last,par
    s=next(iter(pts)); a,_=bfs(s); b,par=bfs(a)
    path=[];u=b
    while u is not None: path.append(u);u=par[u]
    return path  # (y,x)
out=[];res={}
for p,c in COL.items():
    a=np.asarray(Image.open(f'pg-{p}.png').convert('RGB')).astype(int)
    d=np.abs(a-np.array(c)).sum(2)
    m=d<70
    m[:FR[1]]=0;m[FR[3]:]=0;m[:,:FR[0]]=0;m[:,FR[2]:]=0
    m=ndi.binary_closing(m,iterations=(6 if p=='19' else 1))  # bridge the transmission line crossing on page 19
    lab,n=ndi.label(m,structure=np.ones((3,3)))
    sz=ndi.sum(m,lab,range(1,n+1))
    keep=np.argsort(-sz)[:1]+1
    mm=np.isin(lab,keep)
    mm=ndi.binary_fill_holes(mm)
    sk=skeletonize(mm)
    path=longest_path(sk)
    pts=np.array([(x,y) for y,x in path],float)
    # orientation: start at the south-east / south end
    if p=='17':
        if pts[0,0]<pts[-1,0]: pts=pts[::-1]
    else:
        if pts[0,1]<pts[-1,1]: pts=pts[::-1]
    s=approximate_polygon(pts,tolerance=1.2)
    res[p]=dict(page_px=s.tolist(),npix=len(pts),comp_px=int(sz[keep[0]-1]))
    sh=np.array(SH[p]); out.append((s+sh).tolist())
    print(p,len(pts),len(s),pts[0],pts[-1])
json.dump(res,open('trace_pages_px.json','w'))
json.dump({"image":"mosaic of pg-17..pg-20.png (200 dpi renders of PDF pages 17-20 of MPSC_order_U-21780.pdf) in the page 17 pixel frame; pages 18, 19, 20 shifted by (-960,-173), (-1604,-949), (-1791,-2016)","polylines":out,"notes":"One polyline per segment (1 to 4), colored line extracted by color mask, skeleton, longest path, simplified 1.2 px. Segment ends meet at the valve markers; gaps of a few pixels at the marker pins are left as is."},open('trace.json','w'))
