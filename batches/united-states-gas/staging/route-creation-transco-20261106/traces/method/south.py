import sys, json, subprocess; sys.path.insert(0,'.')
from mpcut import *
G,nodes,t=graph()
s,_=snap(G,nodes,t,stpt(70))
d=nx.single_source_dijkstra_path_length(G,s,cutoff=40*1609.344,weight='weight')
west=max((n for n,w in d.items() if n[0]<-90.2), key=lambda n:d[n])
order=['W',70,85,90,95,110,120,125,135,145,150,155,160,165]
pts=[west]+[stpt(n) for n in order[1:]]
path,cum,ch,sn=master(pts)
c90=ch[order.index(90)]; c165=ch[order.index(165)]
k=(c165-c90)/(1413.0-811.26)
ch_of=lambda mp: c90+(mp-811.26)*k
LOOPS={'P8288':[('DeSoto loop',772.81,784.84),('Summerville loop',851.46,860.82),('Kings Mountain loop',1247.03,1256.00),('Mooresville loop',1287.11,1294.78)],
 'P8287':[('Loop E 42-inch',799.95,811.26),('Loop E 48-inch',837.52,851.46)],
 'P8285':[('Magnolia Loop',632.89,634.85),('Jones Loop',860.78,885.97),('Kellyton Loop Phase I',926.87,935.04),('Bowman Loop',1124.74,1132.23)]}
def county(p):
    u=f'https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x={p[0]}&y={p[1]}&benchmark=Public_AR_Current&vintage=Current_Current&layers=Counties&format=json'
    try:
        r=json.loads(subprocess.run(['curl','-s',u],capture_output=True,text=True,timeout=60).stdout)['result']['geographies']['Counties'][0]
        return r['NAME']
    except Exception as e: return '?'
res={}
for pid,ls in LOOPS.items():
    parts=[]
    for nm,a,b in ls:
        seg=sub(path,cum,ch_of(a),ch_of(b))
        km=sum(G_.inv(u[0],u[1],v[0],v[1])[2] for u,v in zip(seg,seg[1:]))/1000
        print(pid,nm,a,b,'mi',round(km/1.609344,2),'vs',round(b-a,2),'|',county(seg[0]),'->',county(seg[-1]),flush=True)
        parts.append((nm,a,b,seg))
    res[pid]=parts
    fc={"type":"FeatureCollection","features":[{"type":"Feature","properties":{"name":nm,"mp_start":a,"mp_end":b},"geometry":{"type":"LineString","coordinates":seg}} for nm,a,b,seg in parts]}
    json.dump(fc,open(f'cuts/{pid}_loops.geojson','w'))
