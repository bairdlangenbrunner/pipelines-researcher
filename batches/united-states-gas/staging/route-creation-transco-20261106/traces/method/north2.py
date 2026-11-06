import sys,json,urllib.request; sys.path.insert(0,'.')
from mpcut import *
def county(p):
    u=f"https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x={p[0]}&y={p[1]}&benchmark=Public_AR_Current&vintage=Current_Current&layers=Counties&format=json"
    try:
        d=json.load(urllib.request.urlopen(u,timeout=30)); c=d['result']['geographies']['Counties'][0]; return c['NAME']+' '+c['STATE']
    except Exception as e: return 'ERR'
src=json.load(open('/Users/baird/Dropbox/_git_ALL/_github-repos-gem/GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines/P0271.geojson'))
F=src['features']
mid=lambda i,fr=0.5: tuple(F[i]['geometry']['coordinates'][int(len(F[i]['geometry']['coordinates'])*fr)])
V=sys.argv[1] if len(sys.argv)>1 else 'a'
north={'a':[(-74.72898,40.33538),(-74.52747,40.65294),(-74.32889,40.82386),(-74.124422,40.949643),(-74.02588,40.98588)],
       'b':[(-74.72898,40.33538),(-74.52747,40.65294),(-74.32889,40.82386),(-74.05839,40.9265),(-74.02588,40.98588)]}[V]
vias=[stpt(n) for n in [160,165,170,175,180,185,190,195,200]]+[mid(146)]+north
path,cum,ch,sn=master(vias)
c165=ch[1]
print('snaps km',[round(x,2) for x in sn]); print('via MP',[round(1413+c-c165,1) for c in ch])
for mp in [1773.3,1776.8,1783,1789.6,1791.8,1793.92,1800,1810,1820,1825.8,1826.41]:
    p=interp(path,cum,c165+mp-1413.0); print(mp,p,county(p))
json.dump({'path':path,'cum':cum,'c165':c165},open(f'north_master_{V}.json','w'))
