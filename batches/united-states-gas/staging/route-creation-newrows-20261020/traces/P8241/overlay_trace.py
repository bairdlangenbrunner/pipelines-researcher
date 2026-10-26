"""Draw the traced polylines (page 17 frame) on the mosaic, one color per segment, and save overlay_trace.png."""
import json
from PIL import Image, ImageDraw
im=Image.open('mosaic.png').convert('RGB'); d=ImageDraw.Draw(im)
cols=[(255,0,255),(0,255,255),(255,128,0),(0,0,255)]
for i,pl in enumerate(json.load(open('trace.json'))['polylines']):
    print(i,pl[0],pl[-1])
    d.line([(x+1800,y+2000) for x,y in pl],fill=cols[i],width=6)
im.thumbnail((1400,1400)); im.save('overlay_trace.png')
