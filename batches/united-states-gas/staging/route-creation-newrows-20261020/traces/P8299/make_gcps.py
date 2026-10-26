import json
G='US Census Bureau 2023 Gazetteer, county subdivisions file (2023_Gaz_cousubs_national.txt), INTPTLAT/INTPTLONG for GEOID %s. Pixel is the center of the printed "%s" label on the map, which the map places at the subdivision center.'
P='US Census Bureau 2023 Gazetteer, places file (2023_Gaz_place_national.txt), INTPTLAT/INTPTLONG for GEOID %s. Pixel is the center of the printed "%s" label.'
rows=[
("Town of LaGrange",(729,783),42.792955,-88.594484,G%("5512741050","Town of LaGrange")),
("Town of Sugar Creek",(630,1285),42.716635,-88.605975,G%("5512778100","Town of Sugar Creek")),
("Town of Lafayette",(1066,1226),42.714176,-88.480931,G%("5512740950","Town of Lafayette")),
("Town of Spring Prairie",(1539,1258),42.708654,-88.368132,G%("5512776175","Town of Spring Prairie")),
("Town of Troy",(1098,810),42.802061,-88.478509,G%("5512780875","Town of Troy")),
("Town of East Troy",(1558,734),42.772187,-88.337209,G%("5512722125","Town of East Troy")),
("Town of Lyons",(1560,1670),42.628118,-88.363091,G%("5512746725","Town of Lyons")),
("Town of Burlington",(2060,1442),42.653301,-88.239051,G%("5510111225","Town of Burlington")),
("Town of Dover",(2410,1214),42.720097,-88.120628,G%("5510120625","Town of Dover")),
("Town of Norway",(2404,780),42.796831,-88.122754,G%("5510158600","Town of Norway")),
("Town of Brighton",(2425,1650),42.62745,-88.135197,G%("5505909635","Town of Brighton")),
("Town of Paris",(2859,1641),42.616626,-88.013223,G%("5505961175","Town of Paris")),
("Town of Wheatland",(1998,1900),42.583444,-88.247459,G%("5505986500","Town of Wheatland")),
("Village of Rochester",(1974,1120),42.732913,-88.250323,P%("5568550","Village of Rochester")),
("City of Elkhorn",(913,1434),42.671601,-88.536256,P%("5523300","City of Elkhorn")),
]
json.dump([{"px":list(p),"lonlat":[lo,la],"name":n,"source_ref":s} for n,p,la,lo,s in rows],open('gcps.json','w'),indent=1)
