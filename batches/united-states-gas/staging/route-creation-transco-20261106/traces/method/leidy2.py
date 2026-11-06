import sys,json,subprocess,networkx as nx; sys.path.insert(0,'.')
from mpcut import *
from leidy import county
G,nodes,t=graph()
s520,_=snap(G,nodes,t,stpt(520))
d=nx.single_source_dijkstra_path_length(G,s520,cutoff=110000,weight='weight')
cand=[n for n in d if 41.1<n[1]<41.6 and n[0]<-77.25]
west=max(cand,key=lambda n:d[n]); print('west target',west,round(d[west]/1609,1),'mi from 520')
vias=[(-74.733,40.532),stpt(517),stpt(520),west]
path,cum,ch,sn=master(vias)
print('snaps',[round(x,2) for x in sn],'chain',[round(x,2) for x in ch])
k=(ch[2]-ch[0])/(157.52-0.11); print('k',k)
f=lambda mp: ch[0]+(mp-0.11)*k
print('517 MP',round(0.11+ch[1]/k,2))
s515,dd=snap(G,nodes,t,stpt(515)); 
import bisect
best=min(range(len(path)),key=lambda i:(path[i][0]-stpt(515)[0])**2+(path[i][1]-stpt(515)[1])**2)
print('515 nearest on path MP',round(0.11+cum[best]/k,2),path[best])
for mp in [0.11,6.9,13.62,18.25,17.7,23.0,30.29,36.56,33.19,39.28,57.5,69.0,134.57,138.30,178.49,183.13]:
    p=interp(path,cum,f(mp)); print(mp,p,county(p))
json.dump({'path':path,'cum':cum,'ch':ch,'k':k},open('leidy_master.json','w'))
