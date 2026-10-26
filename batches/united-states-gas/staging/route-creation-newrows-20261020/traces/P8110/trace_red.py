"""Extract the red Cloud Connector line from map250.png as a pixel polyline (pixels only)."""
import json, numpy as np, sys
from PIL import Image
from skimage.morphology import skeletonize
from scipy import ndimage as ndi
im = np.array(Image.open('map250.png').convert('RGB')).astype(int)
r,g,b = im[...,0],im[...,1],im[...,2]
mask = (r>200)&(g<60)&(b<60)
mask[2370:,:]=False   # legend and title block
mask[:, :70]=False
print(mask.sum())
lab,n = ndi.label(mask, structure=np.ones((3,3)))
sizes = ndi.sum(mask,lab,range(1,n+1))
print(n, sorted(sizes)[-8:])
# keep components larger than 150 px
keep = np.zeros_like(mask)
for i,s in enumerate(sizes,1):
    if s>25: keep|=lab==i
sk = skeletonize(keep)
ys,xs = np.nonzero(sk)
print(len(xs))
np.save('skel.npy', np.stack([xs,ys],1))
Image.fromarray((keep*255).astype('uint8')).save('mask.png')
