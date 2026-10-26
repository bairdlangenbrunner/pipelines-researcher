"""Extract the red dashed proposed-pipeline pixels from Figure 1-1 and chain them into a pixel polyline.
Color mask, then per-segment median of the mask pixels (x-binned for east-west parts, y-binned for the vertical part)."""
import json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
IMG='/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher/batches/united-states-gas/staging/route-creation-newrows-20261020/maps/P8212/notice-of-scoping-image1.png'
im=np.array(Image.open(IMG).convert('RGB')).astype(int)
m=np.abs(im-np.array([230,77,0])).sum(2)<90
m[870:,:]=False; m[:320,1040:]=False; m[535:870,:445]=False
ys,xs=np.nonzero(m)
def xbin(x0,x1,ylo=0,yhi=999,step=3):
    pts=[]
    for x in range(x0,x1+1,step):
        sel=(abs(xs-x)<=step//2+1)&(ys>=ylo)&(ys<=yhi)
        if sel.sum(): pts.append([x,float(np.median(ys[sel]))])
    return pts
def ybin(y0,y1,xlo,xhi,step=3):
    pts=[]
    for y in range(y0,y1+1,step):
        sel=(abs(ys-y)<=step//2+1)&(xs>=xlo)&(xs<=xhi)
        if sel.sum(): pts.append([float(np.median(xs[sel])),y])
    return pts
S1=xbin(131,218,170,240)            # receiver to compressor diagonal
S2=ybin(186,300,212,222)            # vertical leg
S3=xbin(222,1415,300,660)           # main leg
json.dump({'S1':S1,'S2':S2,'S3':S3},open('segments_raw.json','w'))
print(len(S1),len(S2),len(S3), S1[:2],S1[-2:],S2[:2],S2[-2:],S3[:2],S3[-2:])

# ---- cleaned chain ----
from scipy.signal import medfilt
def clean(pts,k=15,tol=4):
    a=np.array(pts); med=medfilt(a[:,1],k)
    keep=np.abs(a[:,1]-med)<=tol
    return a[keep].tolist()
S1=xbin(131,212,170,240,step=2)
S3=clean(xbin(222,1406,300,660,step=3))
S4=ybin(624,652,1406,1422,step=2)
# join: S1 ends at the compressor corner, S2 runs down, S3 runs east, S4 the end hook
S1=[p for p in S1]
line=[]
line+=S1
line+=[[217.5,186]]  # junction of diagonal with vertical leg (visual: where the two red runs meet)
line+=[p for p in S2 if p[1]>188]
line+=S3
line+=S4
json.dump({'image':'notice-of-scoping-image1.png','polylines':[line],'notes':'proposed pipeline red dashes, colour mask (230,77,0), per-bin median; see NOTES.md'},open('trace_try.json','w'))
print(len(line))
