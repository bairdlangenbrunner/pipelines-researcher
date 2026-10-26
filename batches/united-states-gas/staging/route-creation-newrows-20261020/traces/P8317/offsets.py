# Translation between consecutive sheets (same scale, north-up) by template matching.
# Template = bottom strip of sheet k (inside map frame), searched in the upper part of sheet k+1.
# offset[k] = (dx,dy): sheet k pixel (x,y) corresponds to sheet k+1 pixel (x+dx, y+dy).
import numpy as np, json
from PIL import Image
from skimage.feature import match_template
M='../../maps/P8317/pagwis-fig1-%d.png'
def g(i): return np.asarray(Image.open(M%i).convert('L'),dtype=np.float32)
out={}
for k in range(1,5):
    a,b=g(k),g(k+1)
    for h in (60,120,200):
        ty0,ty1=2282-h,2282; tx0,tx1=50,1500
        t=a[ty0:ty1,tx0:tx1]
        sb=b[60:900,:]
        r=match_template(sb,t)
        iy,ix=np.unravel_index(r.argmax(),r.shape)
        print(k,h,round(float(r.max()),3),'dx',int(ix-tx0),'dy',int(iy+60-ty0))
        out[f'{k}_{h}']=[int(ix-tx0),int(iy+60-ty0),float(r.max())]
json.dump(out,open('offsets_raw.json','w'))
