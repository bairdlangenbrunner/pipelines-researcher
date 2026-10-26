"""Paste pages 17-20 (200 dpi) into one mosaic in the page 17 pixel frame. Writes mosaic.png and mosaic_origin.json (mosaic px = frame px - origin)."""
import json, numpy as np
from PIL import Image
SH={'17':(0,0),'18':(-960,-173),'19':(-1604,-949),'20':(-1791,-2016)}
FR=(142,180,1566,2058)
W0,H0,W1,H1=-1800,-2000,1600,2100
ox,oy=W0,H0
M=np.zeros((H1-H0,W1-W0,3),np.uint8)
for p in ['20','19','18','17']:
    a=np.asarray(Image.open(f'pg-{p}.png').convert('RGB'))[FR[1]:FR[3],FR[0]:FR[2]]
    sx,sy=SH[p]
    X=FR[0]+sx-ox;Y=FR[1]+sy-oy
    M[Y:Y+a.shape[0],X:X+a.shape[1]]=a
Image.fromarray(M).save('mosaic.png')
json.dump({'origin':[ox,oy]},open('mosaic_origin.json','w'))
print(M.shape)
