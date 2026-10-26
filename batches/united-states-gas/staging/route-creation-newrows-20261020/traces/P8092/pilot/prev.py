import json,numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize
from pyproj import Transformer
M='/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher/batches/united-states-gas/staging/route-creation-newrows-20261020/maps/P8092/map-02.png'
im=np.array(Image.open(M).convert('RGB')).astype(int)
r,g,b=im[...,0],im[...,1],im[...,2]
blue=(b>r+25)&(b>=g-5)&(g>r)   # blue/teal strokes
blue[830:]=False; blue[:90]=False
print('blue px',blue.sum())
dt=ndi.distance_transform_edt(~blue)
t=Transformer.from_crs(4326,32606,always_xy=True)
d=json.load(open('nhd2.json'))
P=[]
for f in d['features']:
    c=np.array([t.transform(*q) for q in f['geometry']['coordinates']])
    for a,bb in zip(c[:-1],c[1:]):
        n=max(2,int(np.hypot(*(bb-a))/20))
        for s in np.linspace(0,1,n): P.append(a+(bb-a)*s)
P=np.array(P)
def pix(a,P):
    s=a[0];th=a[1];tx=a[2];ty=a[3]
    # base: x=204+(578000-E)*.2228 ; y=432+(N-6890000)*.2228
    x=204+(578000-P[:,0])*.2228; y=432+(P[:,1]-6890000)*.2228
    x=x-1275;y=y-824
    c,sn=np.cos(th),np.sin(th)
    X=s*(c*x-sn*y)+1275+tx; Y=s*(sn*x+c*y)+824+ty
    return X,Y
def f(a):
    X,Y=pix(a,P); ok=(X>160)&(X<2400)&(Y>100)&(Y<820)
    xi=X[ok].astype(int);yi=Y[ok].astype(int)
    return np.minimum(dt[yi,xi],20).mean()-0.0*ok.sum()
best=None
for tx in range(-60,61,15):
  for ty in range(-60,61,15):
    v=f([1,0,tx,ty]); 
    if best is None or v<best[0]: best=(v,tx,ty)
print(best)
res=minimize(f,[1,0,best[1],best[2]],method='Nelder-Mead',options={'xatol':1e-5,'fatol':1e-5,'maxiter':3000}); print(res.fun,res.x)
np.save('prev_a.npy',res.x)
# overlay
from PIL import ImageDraw
o=Image.open(M).convert('RGB'); dr=ImageDraw.Draw(o)
X,Y=pix(res.x,P)
for x,y in zip(X,Y):
    if 160<x<2400 and 100<y<830: dr.ellipse((x-2,y-2,x+2,y+2),fill=(255,0,0))
o.save('prev_overlay.png')
