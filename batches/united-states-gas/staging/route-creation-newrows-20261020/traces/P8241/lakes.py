"""Find dark water blobs in the mosaic (frame coordinates) to compare with Census water polygon centroids."""
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
M=np.asarray(Image.open('mosaic.png')).astype(int)
ox,oy=-1800,-2000
valid=M.sum(2)>0
water=(M[...,0]<138)&(M[...,1]<142)&(M[...,2]<100)&valid
# remove colored overlays (red, purple, yellow, teal lines)
water=ndi.binary_opening(water,iterations=3)
water=ndi.binary_closing(water,iterations=3)
lab,n=ndi.label(water)
sz=ndi.sum(water,lab,range(1,n+1))
out=[]
for i in np.argsort(-sz)[:30]:
    ys,xs=np.nonzero(lab==i+1)
    out.append(dict(id=int(i+1),area=int(sz[i]),cx=float(xs.mean()+ox),cy=float(ys.mean()+oy),bbox=[int(xs.min()+ox),int(xs.max()+ox),int(ys.min()+oy),int(ys.max()+oy)]))
    print(out[-1])
json.dump(out,open('lake_blobs.json','w'))
Image.fromarray((np.stack([ (lab>0)*255]*3,2)).astype(np.uint8)).resize((850,1025)).save('water_mask_small.png')
