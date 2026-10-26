"""Write gcps.json: Census TIGER/Line 2023 lake centroids (pixel = dark-water centroid in the image, from lake_gcp_candidates.py)
plus three hand-located points (Houghton County corner, Assinins shore spit tip, US 41 / US 141 / M-28 junction at Alberta)."""
import json
c={(x['name'],x['id']):x for x in json.load(open('lake_gcp_candidates.json'))}
use=[('Summit Lk','1101561182431'),('Kontio Lk','1101561182422'),('Petticoat Lk','1101561182459'),('Heart Lk','1101561182399'),
('Parent Lk','1101561182426'),('Dommer Lk','1101561182414'),('Lk Ruth','1101561182385'),('King Lk','1101561182381'),('Teddy Lk','1101561182407')]
out=[]
for n,i in use:
    x=[v for k,v in c.items() if k[0]==n and str(k[1])==i][0]
    out.append({"px":[round(x['px'][0],1),round(x['px'][1],1)],"lonlat":[round(x['lon'],6),round(x['lat'],6)],"name":f"{n} centroid",
     "source_ref":f"US Census Bureau TIGER/Line 2023 area water, Baraga County (tl_2023_26013_areawater), HYDROID {i}, {n}; lon/lat is the polygon centroid. Pixel is the centroid of the dark water pixels in the plat image."})
out.append({"px":[-901.5,-1551.8],"lonlat":[-88.55194,46.8518],"name":"Houghton County line southeast corner",
 "source_ref":"US Census Bureau TIGER/Line 2023 county boundaries (tl_2023_us_county), vertex where the Baraga and Houghton county line turns from east-west to north at 46.8518 N; pixel is the dashed county line corner on plat sheet 4."})
out.append({"px":[-318.5,-916.3],"lonlat":[-88.462237,46.788614],"name":"Assinins shore spit tip, Keweenaw Bay",
 "source_ref":"US Census Bureau TIGER/Line 2023 area water, Baraga County, Lake Superior polygon (HYDROID of the Lake Superior feature), east-most vertex of the small spit; pixel is the tip of the spit on plat sheet 4."})
out.append({"px":[-461,1073],"lonlat":[-88.472259,46.585275],"name":"US 41 / US 141 / M-28 junction at Alberta",
 "source_ref":"US Census Bureau TIGER/Line 2023 roads, Baraga County (tl_2023_26013_roads), end vertex of US Hwy 141 (LINEARID 1101561175871) where it meets US Hwy 41; pixel is where the three roads meet under the M-28 shield on plat sheets 2 and 3."})
json.dump(out,open('gcps.json','w'),indent=1); print(len(out))
