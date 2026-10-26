"""Preview-only refinement: fit an affine so Census parish outlines sit on the map's gray outlines (chamfer). Used only to place candidate vertices for hand-picking GCP pixels; the final georeferencing uses only the picked GCPs."""
import numpy as np, geopandas as gpd
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import minimize
D='/private/tmp/claude-501/census_dl/'
im=np.array(Image.open('map250.png').convert('RGB')).astype(int)
r,g,b=im[...,0],im[...,1],im[...,2]
gray=(abs(r-g)<6)&(abs(g-b)<6)&(r>105)&(r<150)
gray[2370:]=False
dt=ndi.distance_transform_edt(~gray)
M=np.load('prelim_M.npy'); L=M[:2].T; t=M[2]
cty=gpd.read_file(D+'county/cb_2023_us_county_500k.shp').to_crs(4326)
cty=cty[cty.STATEFP.isin(['22','28'])]
pts=[]
from shapely.geometry import LineString
for _,rw in cty.iterrows():
    gg=rw.geometry; gs=list(gg.geoms) if gg.geom_type=='MultiPolygon' else [gg]
    for p in gs:
        ls=LineString(p.exterior.coords)
        for d in np.arange(0,ls.length,0.004): 
            q=ls.interpolate(d); pts.append((q.x,q.y))
pts=np.array(pts)
px0=np.linalg.solve(L,(pts-t).T).T
ok=(px0[:,0]>150)&(px0[:,0]<900)&(px0[:,1]>150)&(px0[:,1]<2250)
# route corridor: stay near the red line (within 250 px)
tr=np.array(__import__('json').load(open('trace.json'))['polylines'][0])
from scipy.spatial import cKDTree
kd=cKDTree(tr); dd,_=kd.query(px0); ok&=dd<220
P=pts[ok]; print(len(P))
def apply(a,P):
    A=np.array(a[:6]).reshape(2,3)
    ll=np.c_[P,np.ones(len(P))]
    return None
def f(a):
    # pixel = initial pixel + affine correction
    A=np.array([[1+a[0],a[1],a[2]],[a[3],1+a[4],a[5]]])
    q=px0[ok]@A[:,:2].T+A[:,2]
    xi=np.clip(q[:,0].round().astype(int),0,2124); yi=np.clip(q[:,1].round().astype(int),0,2749)
    return np.minimum(dt[yi,xi],25).mean()
best=None
for sx in range(-40,41,10):
  for sy in range(-40,41,10):
    v=f([0,0,sx,0,0,sy])
    if best is None or v<best[0]: best=(v,sx,sy)
print(best)
res=minimize(f,[0,0,best[1],0,0,best[2]],method='Nelder-Mead',options={'xatol':1e-4,'fatol':1e-4,'maxiter':4000})
print(res.fun,res.x)
a=res.x; A=np.array([[1+a[0],a[1],a[2]],[a[3],1+a[4],a[5]]]); np.save('icp_A.npy',A)
