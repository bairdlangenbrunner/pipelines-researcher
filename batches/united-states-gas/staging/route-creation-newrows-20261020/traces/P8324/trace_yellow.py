import json, numpy as np
from PIL import Image, ImageDraw
from skimage.morphology import skeletonize
from scipy import ndimage as ndi
im=np.array(Image.open('p31-031.png').convert('RGB')).astype(int)
r,g,b=im[...,0],im[...,1],im[...,2]
mask=(r>230)&(g>220)&(b<80)
# restrict to project area window
win=np.zeros_like(mask);win[700:1400,1350:1800]=True
mask&=win
lab,n=ndi.label(mask,structure=np.ones((3,3)))
sizes=ndi.sum(mask,lab,range(1,n+1));print(n,sizes)
big=np.argmax(sizes)+1
m=lab==big
sk=skeletonize(m)
ys,xs=np.nonzero(sk);print(len(xs))
np.save('skel.npy',np.c_[xs,ys]);np.save('mask.npy',m)
Image.fromarray((m*255).astype('uint8')).save('mask.png')
