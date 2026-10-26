import numpy as np, json
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation
from skimage.graph import route_through_array
mag=np.load('mag.npy'); org=np.load('org.npy')
H,W=mag.shape
m=mag.copy()
yy,xx=np.mgrid[:H,:W]
m|= org & (((xx>1395)&(yy<240))|((xx<445)&(yy>700)&(yy<730)))   # dashed AB sections only
cost=np.where(binary_dilation(m,iterations=2),1.0,80.0)
def chain(wps):
    pts=[]
    for a,b in zip(wps,wps[1:]):
        p,_=route_through_array(cost,(a[1],a[0]),(b[1],b[0]),fully_connected=True,geometric=True)
        pts+= [(c,r) for r,c in p]
    return pts
def simplify(pts,tol=1.0):
    from shapely.geometry import LineString
    return [list(map(float,c)) for c in LineString(pts).simplify(tol).coords]
west=[(160,717),(300,720),(440,722),(497,728)]
trunk=[(497,728),(497,648),(660,643),(665,533),(935,528),(993,440),(1040,352),(1118,348),(1120,312),(1150,310),(1150,293),(1300,295),(1412,297),(1413,205),(1500,176)]
south=[(462,1148),(462,1090),(483,1088),(500,1000),(498,868),(517,865),(517,735),(497,728)]
pl=[simplify(chain(w)) for w in (west,trunk,south)]
json.dump({"image":"maps/P8329/RochesterLateralMap-1.png","polylines":pl,"notes":"Route B (applicant alternative) incl. shared AB ends, traced by shortest path through a color mask of the magenta Route B line and the dashed AB sections, with hand-placed waypoints. Three parts: west branch from Rochester Gate, trunk to Oak Creek, south spur to Lakeshore Lateral."},open('trace.json','w'))
im=Image.open('../../maps/P8329/RochesterLateralMap-1.png').convert('RGB'); d=ImageDraw.Draw(im)
for p in pl: d.line([tuple(q) for q in p],fill=(0,160,0),width=3)
im.save('overlay.png')
import math
px=sum(math.dist(a,b) for p in pl for a,b in zip(p,p[1:])); print(px, px/73.75,'mi (scale 73.75 px/mi)', [len(p) for p in pl])
