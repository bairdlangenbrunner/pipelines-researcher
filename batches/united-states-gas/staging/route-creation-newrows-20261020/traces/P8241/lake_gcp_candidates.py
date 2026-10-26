"""Candidate lake GCPs: for each Census TIGER 2023 water polygon, projected into the mosaic with a rough affine,
find the dark water pixels inside the polygon grown by 20 px and compare the pixel centroid with the polygon centroid.
The lon/lat of a GCP is the Census polygon centroid (independent); the pixel is the dark-water centroid in the image."""
import glob, json, numpy as np, geopandas as g
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
DL=glob.glob('/private/tmp/claude-501/*/b8a48c22*/scratchpad/p8241_dl')[0]
co=np.array(json.load(open('prelim_affine.json'))); A=co[:2].T; b=co[2]; Ai=np.linalg.inv(A)
tp=lambda lon,lat: Ai@(np.array([lon,lat])-b)
M=np.asarray(Image.open('mosaic.png')).astype(int); ox,oy=-1800,-2000
valid=M.sum(2)>0
dark=(M[...,0]<140)&(M[...,1]<145)&(M[...,2]<105)&valid
H,W=dark.shape
cands=[]
w=g.read_file(f'{DL}/tl_2023_26013_areawater/tl_2023_26013_areawater.shp')
from shapely.ops import transform
for r in w.itertuples():
    if r.AWATER<120000 or r.AWATER>3.5e6: continue
    if r.geometry.geom_type!='Polygon': continue
    pts=[tp(*c[:2])-np.array([ox,oy]) for c in r.geometry.exterior.coords]
    pts=np.array(pts)
    if pts[:,0].min()<30 or pts[:,1].min()<30 or pts[:,0].max()>W-30 or pts[:,1].max()>H-30: continue
    cx,cy=tp(*r.geometry.centroid.coords[0])-np.array([ox,oy])
    x0,x1,y0,y1=int(pts[:,0].min()-30),int(pts[:,0].max()+30),int(pts[:,1].min()-30),int(pts[:,1].max()+30)
    # require imagery for the whole box
    if not valid[y0:y1,x0:x1].all(): continue
    im=Image.new('L',(x1-x0,y1-y0),0); ImageDraw.Draw(im).polygon([tuple(p-np.array([x0,y0])) for p in pts],fill=1)
    pm=np.array(im).astype(bool); grown=ndi.binary_dilation(pm,iterations=20)
    d=dark[y0:y1,x0:x1]&grown
    d=ndi.binary_opening(d,iterations=2); d=ndi.binary_closing(d,iterations=3)
    lab,n=ndi.label(d)
    if n==0: continue
    sz=ndi.sum(d,lab,range(1,n+1)); k=np.argmax(sz)+1
    ys,xs=np.nonzero(lab==k)
    ratio=sz[k-1]/pm.sum()
    mx,my=xs.mean()+x0,ys.mean()+y0
    cands.append(dict(name=r.FULLNAME,id=r.HYDROID,awater=int(r.AWATER),lon=r.geometry.centroid.x,lat=r.geometry.centroid.y,
        px=[float(mx+ox),float(my+oy)],poly_px=[float(cx+ox),float(cy+oy)],dpx=float(np.hypot(mx-cx,my-cy)),ratio=float(ratio),n_blobs=int(n)))
cands.sort(key=lambda c:c['dpx'])
for c in cands: print(c['name'],c['id'],c['awater'],[round(v,1) for v in c['px']],'diff',round(c['dpx'],1),'ratio',round(c['ratio'],2))
json.dump(cands,open('lake_gcp_candidates.json','w'),indent=1)
