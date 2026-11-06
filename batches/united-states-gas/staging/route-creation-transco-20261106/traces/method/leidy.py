import sys,json,subprocess,networkx as nx; sys.path.insert(0,'.')
from mpcut import *
def county(p):
    u=f'https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x={p[0]}&y={p[1]}&benchmark=Public_AR_Current&vintage=Current_Current&layers=Counties&format=json'
    try:
        r=json.loads(subprocess.run(['curl','-s',u],capture_output=True,text=True,timeout=60).stdout)['result']['geographies']['Counties'][0]; return r['NAME']
    except: return '?'
G,nodes,t=graph()
s520,_=snap(G,nodes,t,stpt(520))
d=nx.single_source_dijkstra_path_length(G,s520,weight='weight')
west=min(d,key=lambda n:n[0]); print('westmost reachable',west,round(d[west]/1609,1),'mi')
far=[n for n in d if n[0]<-77.3]; print('nodes west of -77.3:',len(far))
vias=[(-74.733,40.532),stpt(515),stpt(517),stpt(520),west]
path,cum,ch,sn=master(vias)
print('snaps',[round(x,2) for x in sn],'chain',[round(x,2) for x in ch])
k=(ch[3]-ch[1])/(157.52-68.95); print('k',k)
f=lambda mp: ch[1]+(mp-68.95)*k
print('MP at 505-end via', round(68.95+(ch[0]-ch[1])/k,2))
for mp in [0.11,6.9,13.62,18.25,30.29,36.56,33.19,39.28,17.7,23.0,57.5,69.0,134.57,138.30,178.49,183.13]:
    p=interp(path,cum,f(mp)); print(mp,p,county(p))
json.dump({'path':path,'cum':cum,'ch':ch,'k':k},open('leidy_master.json','w'))
