import json,numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize
from pyproj import Transformer
M='/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher/batches/united-states-gas/staging/route-creation-newrows-20261020/maps/P8092/map-12.png'
im=np.array(Image.open(M).convert('RGB')).astype(int)
r,g,b=im[...,0],im[...,1],im[...,2]
lake=(b>r+20)&(b>g)&(r<200)   # light blue fill
lake[830:]=False; lake[:90]=False; lake[:, :110]=False
lake=ndi.binary_opening(lake,iterations=2)
# edge of lake mask = outline
edge=lake&~ndi.binary_erosion(lake,iterations=2)
print(lake.sum(),edge.sum())
dt=ndi.distance_transform_edt(~edge)
t=Transformer.from_crs(4326,32606,always_xy=True)
P=[]
for f in json.load(open('w12.json'))['features']:
    g=f['geometry']; rings=g['coordinates'] if g['type']=='Polygon' else [r for p in g['coordinates'] for r in p]
    for rg in rings:
        c=np.array([t.transform(*q) for q in rg])
        for a,bb in zip(c[:-1],c[1:]):
            n=max(2,int(np.hypot(*(bb-a))/15))
            for s in np.linspace(0,1,n,endpoint=False): P.append(a+(bb-a)*s)
P=np.array(P); print(len(P))
def pix(a,P):
    s,th,tx,ty=a
    x=(488000-P[:,0])*.24; y=(P[:,1]-6866000)*.24
    c,sn=np.cos(th),np.sin(th)
    return 150+tx+s*(c*x-sn*y), 371+ty+s*(sn*x+c*y)
def f(a):
    X,Y=pix(a,P); ok=(X>115)&(X<2440)&(Y>95)&(Y<825)
    if ok.sum()<50: return 99
    return np.minimum(dt[Y[ok].astype(int),X[ok].astype(int)],25).mean()
best=None
for tx in range(-150,151,10):
  for ty in range(-150,151,10):
    v=f([1,0,tx,ty])
    if best is None or v<best[0]: best=(v,tx,ty)
print(best)
res=minimize(f,[1,0,best[1],best[2]],method='Nelder-Mead',options={'xatol':1e-6,'fatol':1e-6,'maxiter':4000}); print(res.fun,res.x)
np.save('a12.npy',res.x)
