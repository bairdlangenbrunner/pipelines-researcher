# fetch Census TIGERweb road centerlines (public Census Bureau data) for the map area, save for GCP geocoding
import json,subprocess,urllib.parse
out={}
for L in (6,8):
    p={'where':'1=1','geometry':'-80.45,40.58,-80.31,40.65','geometryType':'esriGeometryEnvelope','inSR':'4326','outSR':'4326','outFields':'NAME,MTFCC','returnGeometry':'true','f':'json','resultRecordCount':2000}
    r=subprocess.run(['curl','-s','-m','90','-G','https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Transportation/MapServer/%d/query'%L]+sum([['--data-urlencode','%s=%s'%kv] for kv in p.items()],[]),capture_output=True,text=True).stdout
    d=json.loads(r);out[L]=[(f['attributes']['NAME'],f['attributes']['MTFCC'],f['geometry']['paths']) for f in d.get('features',[])]
    print(L,len(out[L]),d.get('exceededTransferLimit'))
json.dump(out,open('tiger_roads.json','w'))
