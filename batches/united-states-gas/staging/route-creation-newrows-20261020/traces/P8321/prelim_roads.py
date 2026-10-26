import json,math,sys
from PIL import Image,ImageDraw
A=(1162.7,283.0);LON0,LAT0=-80.375,40.625;m=4.84;th=math.radians(2.4)
def px(lon,lat):
    e=(lon-LON0)*111320*math.cos(math.radians(LAT0));n=(lat-LAT0)*110574
    x=e/m;y=-n/m
    return A[0]+x*math.cos(th)-y*math.sin(th), A[1]+x*math.sin(th)+y*math.cos(th)
if __name__=='__main__':
    im=Image.open('../../maps/P8321/appxA-usgs-p4-04.png').convert('RGB');d=ImageDraw.Draw(im)
    R=json.load(open('tiger_roads.json'))
    for L in R:
        for nm,mt,paths in R[L]:
            for p in paths:
                pts=[px(*q) for q in p];d.line(pts,fill=(255,0,255),width=1)
                if nm and len(pts)>2:d.text(pts[len(pts)//2],nm[:18],fill=(200,0,0))
    im.crop(tuple(map(int,sys.argv[1:5]))).save(sys.argv[5])
