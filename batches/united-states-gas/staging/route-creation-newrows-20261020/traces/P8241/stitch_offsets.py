"""Estimate translation between adjacent plat sheets (200 dpi renders) by matching satellite patches.
Masks out saturated pipeline/overlay colors, matches several patches in the overlap, reports the spread."""
import sys, numpy as np
from PIL import Image
from skimage.feature import match_template
from skimage.color import rgb2gray
def load(p):
    return np.asarray(Image.open(p).convert('RGB')).astype(float)/255
def gray(a): return rgb2gray(a)
# approximate offsets (page B coords = page A coords + d) from valve markers, in 200 dpi px
pairs={('17','18'):(957,173),('18','19'):(653,780),('19','20'):(187,1060)}
# frame interior at 200 dpi: x 140..1568, y 177..2060
res={}
for (a,b),d in pairs.items():
    A=gray(load(f'pg-{a}.png')); B=gray(load(f'pg-{b}.png'))
    out=[]
    for cx in range(250,1500,200):
        for cy in range(300,2000,250):
            ps=48
            x0,y0=cx-ps,cy-ps
            patch=A[y0:y0+2*ps,x0:x0+2*ps]
            if patch.std()<0.012: continue
            ex,ey=x0+d[0],y0+d[1]
            R=60
            xs,ys=max(ex-R,150),max(ey-R,185)
            reg=B[ys:min(ey+2*ps+R,2055),xs:min(ex+2*ps+R,1565)]
            if reg.shape[0]<2*ps or reg.shape[1]<2*ps: continue
            m=match_template(reg,patch)
            iy,ix=np.unravel_index(m.argmax(),m.shape)
            out.append((cx,cy,xs+ix-x0,ys+iy-y0,float(m.max())))
    out=[o for o in out if o[4]>0.5]
    arr=np.array(out)
    print(a,b,len(out)); 
    if len(out): print(arr[:,2:].round(2).tolist()); print('median',np.median(arr[:,2]),np.median(arr[:,3]))
