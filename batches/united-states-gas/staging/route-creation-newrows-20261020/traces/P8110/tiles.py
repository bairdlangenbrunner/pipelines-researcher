"""Make zoomed tiles (4x, 10 px grid) around candidate vertices to read the gray-outline corner pixel precisely."""
import json,numpy as np,sys
from PIL import Image, ImageDraw
A=np.load('icp_A.npy'); T={('t%d'%t['id']):t for t in json.load(open('tri_refined.json'))}
C={('c%d'%c['id']):c for c in json.load(open('corner_candidates.json'))}
ids=sys.argv[2:]; out=sys.argv[1]
im=Image.open('map250.png').convert('RGB')
R=48; Z=6; tiles=[]
for i in ids:
    o=T.get(i) or C[i]; px=o['px1']; cx,cy=int(round(px[0])),int(round(px[1]))
    x0,y0=cx-R,cy-R
    t=im.crop((x0,y0,x0+2*R,y0+2*R)).resize((2*R*Z,2*R*Z),Image.NEAREST); d=ImageDraw.Draw(t)
    for g in range(0,2*R,12):
        d.line([(g*Z,0),(g*Z,2*R*Z)],fill=(0,160,255),width=1); d.line([(0,g*Z),(2*R*Z,g*Z)],fill=(0,160,255),width=1)
        d.text((g*Z+2,2),str(x0+g),fill=(0,0,255)); d.text((2,g*Z+2),str(y0+g),fill=(0,0,255))
    d.ellipse([R*Z-6,R*Z-6,R*Z+6,R*Z+6],outline=(255,0,255),width=2)
    d.text((R*Z+8,R*Z+8),i,fill=(255,0,255)); tiles.append(t)
W=Image.new('RGB',(3*2*R*Z,((len(tiles)+2)//3)*2*R*Z),'white')
for k,t in enumerate(tiles): W.paste(t,((k%3)*2*R*Z,(k//3)*2*R*Z))
W.save(out)
