export const meta = {
  name: 'egypt-gas-operating-deepsweep',
  description: 'Egypt gas OPERATING deep sweep: per-pipeline critical re-audit (existence/classification/duplicate/attribution/spec) + ref confirmation + blank-value fills + corridor/endpoint route suggestions, with GulfPub PE World Map gas corroboration context (95 Egypt features). Read-and-stage only.',
  phases: [ { title: 'Audit', detail: 'one subagent per operating gas pipeline' } ],
}

const A = {
 "repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher",
 "staging": "batches/staging/ref-sweep-gas-egypt-operating",
 "commodity": "gas",
 "country": "Egypt",
 "pids": [
  "P6035",
  "P0462",
  "P0436",
  "P7482",
  "P0477",
  "P3928",
  "P3935",
  "P7589",
  "P3939",
  "P3938",
  "P3937",
  "P0476",
  "P6688",
  "P6693",
  "P3936",
  "P6692",
  "P6703",
  "P6687",
  "P7577",
  "P7578",
  "P0474",
  "P3932",
  "P6037",
  "P3934",
  "P3343",
  "P3346",
  "P3366",
  "P3659",
  "P3929",
  "P3930",
  "P3931",
  "P5132",
  "P6032",
  "P6033",
  "P6034",
  "P6036",
  "P6689",
  "P6697",
  "P6698",
  "P6699",
  "P6700",
  "P6701",
  "P6702",
  "P6704",
  "P7447",
  "P7567",
  "P7572",
  "P7574",
  "P7580",
  "P7588"
 ],
 "roster": [
  "P6035 | Gamasa\u2013Veunsa Gas Pipeline | ?->? | len=34.0 dia=42 cap=6.8 | status=operating | updated=2025-08-13",
  "P0462 | Arish\u2013Ashkelon Pipeline | Ashkelon->North Sinai | len=90.0 dia=? cap=7.0 | status=operating | updated=2023-09-21",
  "P0436 | Arab Gas Pipeline | Arish->South Sinai | len=250.0 dia=36 cap=10.3 | status=operating | updated=2025-08-06",
  "P7482 | Arab Gas Pipeline | Taba->Aqaba | len=18.0 dia=26 cap=10.3 | status=operating | updated=2025-07-27",
  "P0477 | South Valley Gas Pipeline | Dahshour->Aswan | len=930.0 dia=36, 32, 32,32,32,30 cap=12.0 | status=operating | updated=2024-08-01",
  "P3928 | Nubaria\u2013Sadat Gas Pipeline | El Noubareya->Monufia | len=73.0 dia=36.00 cap=12.0 | status=operating | updated=2025-08-14",
  "P3935 | Salam\u2013Matruh Terminal Gas Pipeline | Salam->Matruh | len=75.0 dia=10.00 cap=22.0 | status=operating | updated=2022-09-16",
  "P7589 | Framid Field Gas Pipeline | ?->Western Desert | len=38.0 dia=10 cap=25.0 | status=operating | updated=2025-08-14",
  "P3939 | Abu Gharadig\u2013Dahshour (1) Gas Pipeline | Abu Gharadig->Giza | len=290.0 dia=24.00 cap=120.0 | status=operating | updated=2024-07-30",
  "P3938 | Badr El Din Spur Gas Pipelines | Badr El Din Field->Matruh | len=130.0 dia=16.00 cap=150.0 | status=operating | updated=2022-09-16",
  "P3937 | Badr El Din Spur Gas Pipelines | Badr El Din Field->Matruh | len=130.0 dia=20.00 cap=180.0 | status=operating | updated=2022-09-16",
  "P0476 | Salam-Abu Gharadig Southern Gas Pipeline | Salam gas field->Matruh | len=212.0 dia=18.00 cap=187.0 | status=operating | updated=2022-07-13",
  "P6688 | Shams-Obaiyed Gas Pipeline | Shams->Matruh | len=42.0 dia=18 cap=240.0 | status=operating | updated=2024-07-30",
  "P6693 | Salam Spurline Gas Pipeline | Salam->Matruh | len=35.0 dia=22 cap=250.0 | status=operating | updated=2024-07-30",
  "P3936 | BED/AS\u2013Ameryia Gas Pipeline | Abu Sennan->Alexandria | len=160.0 dia=24.00 cap=350.0 | status=operating | updated=2025-08-12",
  "P6692 | Qasr-Shams Gas Pipeline | Qasr->Matruh | len=40.0 dia=24 cap=350.0 | status=operating | updated=2024-07-30",
  "P6703 | Raven-Western Desert Cmplex Gas Pipeline | Rashid->? | len=70.0 dia=30 cap=350.0 | status=operating | updated=2025-08-14",
  "P6687 | Obaiyed-Amreya Northern Gas Pipeline | Obaiyed->Alexandria | len=41.5 dia=26 cap=480.0 | status=operating | updated=2024-07-30",
  "P7577 | Baltim Field Gas Pipelines | ?->? | len=18.0 dia=26 cap=500.0 | status=operating | updated=2025-08-13",
  "P7578 | Baltim Field Gas Pipelines | ?->? | len=25.0 dia=26 cap=500.0 | status=operating | updated=2025-08-13",
  "P0474 | Obaiyed-Amreya Northern Gas Pipeline | Obaiyed gas field->Alexandria | len=49.5 dia=32 cap=600.0 | status=operating | updated=2024-07-30",
  "P3932 | Nooros\u2013Abu Madi\u2013El Gamil Gas Pipline | Noors->Port Said | len=130.0 dia=24, 32 cap=700.0 | status=operating | updated=2025-08-13",
  "P6037 | Al Gamil\u2013Damietta Gas Pipeline | Al Gamil->Damietta | len=50.0 dia=42 cap=750.0 | status=operating | updated=2023-09-21",
  "P3934 | Obaiyed-Amreya Northern Gas Pipeline | ?->Alexandria | len=231.0 dia=34.00 cap=950.0 | status=operating | updated=2024-08-01",
  "P3343 | El Tina Gas Pipeline | El Tina->Al Qalyubia | len=170.0 dia=42 cap=? | status=operating | updated=2024-07-29",
  "P3346 | El Noubareya Gas Pipeline | El Noubareya->Al Qalyubia | len=66.0 dia=32, 42 cap=? | status=operating | updated=2025-08-12",
  "P3366 | El Tina- Abu Sultan- New Administrative Capital Gas Pipeline | El Tina Abou Sultan->Cairo | len=165.0 dia=42.00 cap=? | status=operating | updated=2022-07-13",
  "P3659 | Port Said - Arish Gas Pipeline | El Gamil->Northern Sinai | len=235.0 dia=36, 42 cap=? | status=operating | updated=2022-07-13",
  "P3929 | El Wasta\u2013Beni Suef Gas Pipeline | El Wasta->Beni Suef | len=65.0 dia=36.00 cap=? | status=operating | updated=2025-08-12",
  "P3930 | New Administrative Capital\u2013Dahshur Gas Pipeline | New Administrative Capital->Giza | len=70.0 dia=32.00 cap=? | status=operating | updated=2022-09-15",
  "P3931 | Amriya\u2013El Alamein Gas Pipeline | Amriya->Matruh | len=130.0 dia=32.00 cap=? | status=operating | updated=2025-08-14",
  "P5132 | Zohr\u2013Al Gamil Pipelines | Shorouk concession->Port Said | len=216.0 dia=30 cap=? | status=operating | updated=2024-07-31",
  "P6032 | Borg El Arab\u2013Midor Gas pipeline | Borg El Arab->Alexandria | len=10.0 dia=24 cap=? | status=operating | updated=2023-09-20",
  "P6033 | Damietta\u2013SEGAS Pipeline | Damietta->Damietta | len=12.0 dia=42 cap=? | status=operating | updated=2023-09-20",
  "P6034 | Hurghada\u2013Safaga Gas Pipeline | Hurghada->Red Sea Governorate | len=38.5 dia=24 cap=? | status=operating | updated=2023-09-20",
  "P6036 | Zohr\u2013Al Gamil Pipelines | Shorouk concession->Port Said | len=210.0 dia=30 cap=? | status=operating | updated=2024-07-31",
  "P6689 | Abu Sennan Spur Gas Pipeline | Abu Sennan->Matruh | len=45.0 dia=14 cap=? | status=operating | updated=2024-07-30",
  "P6697 | South Valley Gas Pipeline | Dahshour->Giza | len=90.0 dia=36 cap=? | status=operating | updated=2024-08-01",
  "P6698 | South Valley Gas Pipeline | Al Kurimat->Beni Suef | len=30.0 dia=32 cap=? | status=operating | updated=2024-08-01",
  "P6699 | South Valley Gas Pipeline | Beni Suef->Minya | len=150.0 dia=32 cap=? | status=operating | updated=2024-08-01",
  "P6700 | South Valley Gas Pipeline | Abu qurqas->Asyut | len=147.0 dia=32 cap=? | status=operating | updated=2024-08-01",
  "P6701 | South Valley Gas Pipeline | Asyut->Sohag | len=121.0 dia=32 cap=? | status=operating | updated=2024-08-01",
  "P6702 | South Valley Gas Pipeline | Girga->Aswan | len=390.0 dia=30 cap=? | status=operating | updated=2024-08-01",
  "P6704 | Raven-Al Ameryia Gas Pipeline | Rashid->Alexandria | len=5.0 dia=18 cap=? | status=operating | updated=2025-08-14",
  "P7447 | Denise Gas Pipeline | ?->? | len=405.0 dia=16 cap=? | status=operating | updated=2024-08-13",
  "P7567 | Idku-Abu Hummus Gas Pipeline | ?->Beheira | len=30.0 dia=42 cap=? | status=operating | updated=2025-08-12",
  "P7572 | Qarun Gas Pipeline | ?->? | len=206.0 dia=10 cap=? | status=operating | updated=2025-08-13",
  "P7574 | New Administration Capital PS Gas Pipeline | ?->? | len=63.0 dia=32 cap=? | status=operating | updated=2025-08-13",
  "P7580 | Mahmoudiah PS Gas Pipeline | ?->? | len=52.0 dia=? cap=? | status=operating | updated=2025-08-13",
  "P7588 | Edfu Gas Pipeline | Edfu->Aswan | len=37.0 dia=12 cap=? | status=operating | updated=2025-08-14"
 ],
 "routes_context": {
  "P6035": {
   "route_accuracy": "no route",
   "start": "nan",
   "end": "nan",
   "route_notes": "nan"
  },
  "P0462": {
   "route_accuracy": "low",
   "start": "Ashkelon",
   "end": "Arish",
   "route_notes": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Arab_Gas_Pipeline.svg/440px-Arab_Gas_Pipeline.svg.png, https://www.ingl.co.il/wp-content/uploads/2020/06/Natgaz_GeneralMap_Feb2020_ENG_FINAL.pdf"
  },
  "P0436": {
   "route_accuracy": "low",
   "start": "Arish",
   "end": "Taba",
   "route_notes": "IM: updated 2025 to reflect individual segment"
  },
  "P7482": {
   "route_accuracy": "low",
   "start": "Taba",
   "end": "Aqaba",
   "route_notes": "IM: updated 2025 to reflect individual segment"
  },
  "P0477": {
   "route_accuracy": "high",
   "start": "Dahshour",
   "end": "Aswan",
   "route_notes": "https://www.almasryalyoum.com/news/details/103848"
  },
  "P3928": {
   "route_accuracy": "low",
   "start": "El Noubareya",
   "end": "nan",
   "route_notes": "https://almalnews.com/%D8%A5%D8%AA%D9%85%D8%A7%D9%85-%D8%AE%D8%B7%D9%8A-%D8%A3%D9%86%D8%A7%D8%A8%D9%8A%D8%A8-%D9%86%D9%82%D9%84-%D8%A7%D9%84%D8%BA%D8%A7%D8%B2-%D8%A7%D9%84%D9%86%D9%88%D8%A8%D8%A7%D8%B1%D9%8A%D8%A9-%D8%A7/"
  },
  "P3935": {
   "route_accuracy": "low",
   "start": "Salam",
   "end": "nan",
   "route_notes": "https://egyptoil-gas.com/wp-content/uploads/2020/03/The-Western-Desert-Egypt%E2%80%99s-Giant-Petroleum-Reservoir-.pdf"
  },
  "P7589": {
   "route_accuracy": "no route",
   "start": "nan",
   "end": "nan",
   "route_notes": "nan"
  },
  "P3939": {
   "route_accuracy": "low",
   "start": "Abu Gharadig",
   "end": "nan",
   "route_notes": "https://egyptoil-gas.com/wp-content/uploads/2020/03/The-Western-Desert-Egypt%E2%80%99s-Giant-Petroleum-Reservoir-.pdf"
  },
  "P3938": {
   "route_accuracy": "no route",
   "start": "Badr El Din Field",
   "end": "nan",
   "route_notes": "https://www.wepco-eg.com/ar/%D8%A7%D9%84%D8%B9%D9%85%D9%84%D9%8A%D8%A7%D8%AA/%D8%AD%D9%82%D9%84-%D8%A8%D8%AF%D8%B1/"
  },
  "P3937": {
   "route_accuracy": "no route",
   "start": "Badr El Din Field",
   "end": "nan",
   "route_notes": "https://www.wepco-eg.com/ar/%D8%A7%D9%84%D8%B9%D9%85%D9%84%D9%8A%D8%A7%D8%AA/%D8%AD%D9%82%D9%84-%D8%A8%D8%AF%D8%B1/"
  },
  "P0476": {
   "route_accuracy": "high",
   "start": "Salam gas field",
   "end": "Abu Gharadig oilfield",
   "route_notes": "nan"
  },
  "P6688": {
   "route_accuracy": "no route",
   "start": "Shams",
   "end": "Obaiyed",
   "route_notes": "nan"
  },
  "P6693": {
   "route_accuracy": "no route",
   "start": "Salam",
   "end": "Salam",
   "route_notes": "nan"
  },
  "P3936": {
   "route_accuracy": "low",
   "start": "Abu Sennan",
   "end": "nan",
   "route_notes": "https://egyptoil-gas.com/wp-content/uploads/2020/03/The-Western-Desert-Egypt%E2%80%99s-Giant-Petroleum-Reservoir-.pdf"
  },
  "P6692": {
   "route_accuracy": "no route",
   "start": "Qasr",
   "end": "Shams",
   "route_notes": "nan"
  },
  "P6703": {
   "route_accuracy": "low",
   "start": "Rashid",
   "end": "nan",
   "route_notes": "nan"
  },
  "P6687": {
   "route_accuracy": "no route",
   "start": "Obaiyed",
   "end": "Amreya",
   "route_notes": "nan"
  },
  "P7577": {
   "route_accuracy": "no route",
   "start": "nan",
   "end": "nan",
   "route_notes": "nan"
  },
  "P7578": {
   "route_accuracy": "no route",
   "start": "nan",
   "end": "nan",
   "route_notes": "nan"
  },
  "P0474": {
   "route_accuracy": "high",
   "start": "Obaiyed gas field",
   "end": "Amreya oil & gas plant",
   "route_notes": "nan"
  },
  "P3932": {
   "route_accuracy": "medium",
   "start": "Noors",
   "end": "nan",
   "route_notes": "https://petrojeteg.com/?project=2207"
  },
  "P6037": {
   "route_accuracy": "low",
   "start": "Al Gamil",
   "end": "Damietta",
   "route_notes": "nan"
  },
  "P3934": {
   "route_accuracy": "no route",
   "start": "nan",
   "end": "nan",
   "route_notes": "nan"
  },
  "P3343": {
   "route_accuracy": "medium",
   "start": "El Tina",
   "end": "Mit Nema",
   "route_notes": "nan"
  },
  "P3346": {
   "route_accuracy": "high",
   "start": "El Noubareya",
   "end": "Mit Nema",
   "route_notes": "https://www.google.com/maps/place/30%C2%B008'43.0%22N+31%C2%B014'04.0%22E/@30.145278,31.2322553,17z/data=!3m1!4b1!4m5!3m4!1s0x0:0xf9ed88774fe03b3e!8m2!3d30.145278!4d31.234444, https://m.akhbarelyom.com/news/NewDetails/2916710/1/%D9%85%D8%AD%D8%A7%D9%81%D8%B8-%D8%A7%D9%84%D9%82%D9%84%D9%8A%D9%88%D8%A"
  },
  "P3366": {
   "route_accuracy": "medium",
   "start": "El Tina Abou Sultan",
   "end": "New Administrative Capital",
   "route_notes": "nan"
  },
  "P3659": {
   "route_accuracy": "high",
   "start": "El Gamil",
   "end": "nan",
   "route_notes": "https://www.youm7.com/story/2011/2/5/%D8%A8%D8%A7%D9%84%D8%B5%D9%88%D8%B1-%D8%A7%D9%84%D8%AA%D9%81%D8%A7%D8%B5%D9%8A%D9%84-%D8%A7%D9%84%D9%83%D8%A7%D9%85%D9%84%D8%A9-%D9%84%D9%85%D8%B3%D8%A7%D8%B1-%D8%AE%D8%B7%D9%89-%D8%A7%D9%84%D8%BA%D8%A7%D8%B2-%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%89-%D9%88%D8%A7%D9%"
  },
  "P3929": {
   "route_accuracy": "low",
   "start": "El Wasta",
   "end": "nan",
   "route_notes": "nan"
  },
  "P3930": {
   "route_accuracy": "low",
   "start": "New Administrative Capital",
   "end": "nan",
   "route_notes": "https://gate.ahram.org.eg/News/1367155.aspx"
  },
  "P3931": {
   "route_accuracy": "medium",
   "start": "Amriya",
   "end": "nan",
   "route_notes": "https://www.masrawy.com/news/news_economy/details/2021/3/6/1982248/%D9%88%D8%B2%D9%8A%D8%B1-%D8%A7%D9%84%D8%A8%D8%AA%D8%B1%D9%88%D9%84-%D9%8A%D8%AA%D9%81%D9%82%D8%AF-%D9%85%D8%B4%D8%B1%D9%88%D8%B9-%D8%A5%D9%86%D8%B4%D8%A7%D8%A1-%D8%AE%D8%B7-%D8%BA%D8%A7%D8%B2-%D9%85%D8%AF%D9%8A%D9%86%D8%A9-%D8%A7%D9"
  },
  "P5132": {
   "route_accuracy": "low",
   "start": "Shorouk concession",
   "end": "Al Gamil",
   "route_notes": "nan"
  },
  "P6032": {
   "route_accuracy": "low",
   "start": "Borg El Arab",
   "end": "Al ameryia",
   "route_notes": "nan"
  },
  "P6033": {
   "route_accuracy": "no route",
   "start": "Damietta",
   "end": "Damietta",
   "route_notes": "nan"
  },
  "P6034": {
   "route_accuracy": "low",
   "start": "Hurghada",
   "end": "Safaga",
   "route_notes": "nan"
  },
  "P6036": {
   "route_accuracy": "low",
   "start": "Shorouk concession",
   "end": "Al Gamil",
   "route_notes": "nan"
  },
  "P6689": {
   "route_accuracy": "no route",
   "start": "Abu Sennan",
   "end": "Abu Sennan",
   "route_notes": "nan"
  },
  "P6697": {
   "route_accuracy": "no route",
   "start": "Dahshour",
   "end": "Al Kurimat",
   "route_notes": " Nagwa: This is the full rout of the pipeline which includes six segments"
  },
  "P6698": {
   "route_accuracy": "no route",
   "start": "Al Kurimat",
   "end": "Beni Suef",
   "route_notes": " Nagwa: This is the full rout of the pipeline which includes six segments"
  },
  "P6699": {
   "route_accuracy": "no route",
   "start": "Beni Suef",
   "end": "Abu qurqas",
   "route_notes": " Nagwa: This is the full rout of the pipeline which includes six segments"
  },
  "P6700": {
   "route_accuracy": "no route",
   "start": "Abu qurqas",
   "end": "Asyut",
   "route_notes": " Nagwa: This is the full rout of the pipeline which includes six segments"
  },
  "P6701": {
   "route_accuracy": "no route",
   "start": "Asyut",
   "end": "Girga",
   "route_notes": " Nagwa: This is the full rout of the pipeline which includes six segments"
  },
  "P6702": {
   "route_accuracy": "no route",
   "start": "Girga",
   "end": "Aswan",
   "route_notes": " Nagwa: This is the full rout of the pipeline which includes six segments"
  },
  "P6704": {
   "route_accuracy": "no route",
   "start": "Rashid",
   "end": "Ameriya",
   "route_notes": "nan"
  },
  "P7447": {
   "route_accuracy": "no route",
   "start": "nan",
   "end": "nan",
   "route_notes": "nan"
  },
  "P7567": {
   "route_accuracy": "no route",
   "start": "nan",
   "end": "nan",
   "route_notes": "nan"
  },
  "P7572": {
   "route_accuracy": "no route",
   "start": "nan",
   "end": "nan",
   "route_notes": "nan"
  },
  "P7574": {
   "route_accuracy": "no route",
   "start": "nan",
   "end": "nan",
   "route_notes": "nan"
  },
  "P7580": {
   "route_accuracy": "no route",
   "start": "nan",
   "end": "nan",
   "route_notes": "nan"
  },
  "P7588": {
   "route_accuracy": "no route",
   "start": "Edfu",
   "end": "nan",
   "route_notes": "nan"
  }
 },
 "gulfpub_gas_eg": "  - Aphrodite Export Pipeline | proposed | Aphrodite field, offshore Cyprus -> Idku LNG facility, offshore Egypt | op=Chevron dia=32.0 len_km=193.0 start_year=2025\n  - Denise - Port Said Pipeline | operating | Denise field, offshore Egypt -> Port Said, Egypt | op=Eni dia=16.0 len_km=46.0 start_year=2012\n  - El King - Abu Sir /Ameriya Lateral | proposed | El King field, offshore Egypt -> Abu Sir - Ameriya Pipeline | op=Egyptian Natural Gas Company [Gasco] dia=12.0 len_km=6.0 start_year=2026\n  - Al Bahig - Abu Sir /Ameriya Lateral | proposed | Al Bahig field, offshore Egypt -> Abu Sir - Ameriya Pipeline | op=Egyptian Natural Gas Company [Gasco] dia=12.0 len_km=8.0 start_year=2026\n  - Simian/Sienna - Idku Pipeline | operating | Simian/Sienna fields, offshore Egypt -> Idku, Egypt | op=Burullus Gas Company dia=26.0 len_km=63.0 start_year=?\n  - Raven - Idku Pipeline | operating | Raven field, offshore Egypt -> Idku, Egypt | op=bp dia=16.0 len_km=46.0 start_year=2021\n  - Qarun West - WDGP-S | operating | Qarun West field, Egypt -> Western Desert Gas Project - South Line Pipeline | op=Shell dia=16.0 len_km=10.0 start_year=?\n  - Assad - Barboni Pipeline | proposed | Assad field, offshore Egypt -> Barboni field, offshore Egypt | op=Eni dia=16.0 len_km=14.0 start_year=2026\n  - Tulip - Abu Monkar Pipeline | proposed | Tulip field, Egypt -> Abu Monkar field, Egypt | op=Dana Gas dia=16.0 len_km=10.0 start_year=2027\n  - Ashkelon - Arish Pipeline | operating | Ashkelon, Israel -> Arish, Egypt | op=East Mediterranean Gas Company (EMGC) dia=16.0 len_km=62.0 start_year=2015\n  - Arab Gas Pipeline | operating | El Arish, Egypt -> Aqaba, Jordan | op=East Mediterranean Gas Company dia=36.0 len_km=169.0 start_year=2003\n  - Taba - Sharma el Sheikh | operating | Taba, Egypt -> Sharma el Sheikh, Egypt | op=Egyptian Natural Gas Company [Gasco] dia=20.0 len_km=137.0 start_year=2007\n  - Suez - Dahshour Pipeline | operating | Suez, Egypt -> Dahshour, Egypt | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=88.0 start_year=?\n  - Abu Sultan - Dahshour Pipeline | operating | Abu Sultan, Egypt -> Dahshour, Egypt | op=Egyptian Natural Gas Company [Gasco] dia=32.0 len_km=81.0 start_year=?\n  - Media - Idku/Tanta Pipeline | operating | Meadia (Abu Qir) GP, Egypt -> Idku - Tanta Pipeline | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=32.0 start_year=?\n  - Idku - Damietta | operating | Idku, Egypt -> Damietta, Egypt | op=EGAS dia=32.0 len_km=103.0 start_year=?\n  - Seth - Ha'py Lateral | operating | Seth field, offshore Egypt -> Ha'py - Shore Pipeline | op=Eni dia=16.0 len_km=5.0 start_year=2012\n  - Akhen - Denise Pipeline | operating | Akhen field, offshore Egypt -> Denise field, offshore Egypt | op=Eni dia=16.0 len_km=11.0 start_year=?\n  - Zohr Gas Export Pipeline II | operating | Zohr field, offshore Egypt -> Denise field, offshore Egypt | op=Eni dia=30.0 len_km=80.0 start_year=2020\n  - Qantara  - Suez Lateral | operating | Qantara field, Egypt -> Suez - Port Said Pipeline | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=5.0 start_year=?\n  - Tao - Port Said/El Arish Pipeline | operating | Tao field, offshore Egypt -> Port Said - El Arish Pipeline | op=Perenco dia=20.0 len_km=31.0 start_year=?\n  - Port Faoud - Baracuda Pipeline | operating | Port Faoud fields, offshore Egypt -> Baracuda fields, offshore Egypt | op=Eni dia=16.0 len_km=18.0 start_year=?\n  - Darfeel - El Gamil Pipeline | operating | Darfeel field, offshore Egypt -> El Gamil, Egypt | op=Eni dia=36.0 len_km=35.0 start_year=1997\n  - Port Fouad Marine - El Gamil Pipeline | operating | Port Fouad Marine field, offshore Egypt -> Damietta - Port Said Pipeline | op=IEOC dia=48.0 len_km=38.0 start_year=?\n  - Segan - Darfeel/Shore Pipeline | operating | Segan field, offshore Egypt -> Darfeel - El Gamil Pipeline | op=Eni dia=16.0 len_km=13.0 start_year=?\n  - Denise - Wakar Pipeline | operating | Denise field, offshore Egypt -> Segan - Darfeel/Shore Pipeline | op=IEOC dia=16.0 len_km=15.0 start_year=?\n  - Karous - Segan Line | operating | Karous field, offshore Egypt -> Segan tie in | op=Eni dia=16.0 len_km=2.0 start_year=?\n  - Port Said - El Arish Pipeline | operating | Port Said, Egypt -> El Arish, Egypt | op=EGAS dia=36.0 len_km=147.0 start_year=?\n  - El Fayrouz - Suez/Port Said Pipeline | operating | El Fayrouz field, Egypt -> Suez - Port Said Pipeline | op=IEOC dia=16.0 len_km=49.0 start_year=2008\n  - Abu Madi - Tanta Pipeline | operating | Abu Madi field, Egypt -> Tanta, Egypt | op=IEOC dia=8.0 len_km=50.0 start_year=?\n  - Baltim East - Abu Madi Pipeline | operating | Baltim East field, offshore Egypt -> Abu Madi field, Egypt | op=IEOC dia=16.0 len_km=18.0 start_year=?\n  - Nidoco - Abu Madi | operating | Nidoco field, offshore Egypt -> Abu Madi field, Egypt | op=IEOC dia=16.0 len_km=6.0 start_year=2020\n  - Abu Madi - Tanta | operating | Abu Madi field, Egypt -> Tanta, Egypt | op=IEOC dia=22.0 len_km=52.0 start_year=?\n  - North Mansoura Pipeline | operating | Northern Mansoura gas field -> Northwestern Mansoura gas field | op=IEOC dia=16.0 len_km=14.0 start_year=?\n  - Abu Madi - El Mansura Pipeline | operating | Abu Madi field, Egypt -> El Mansura area, Egypt | op=IEOC dia=16.0 len_km=24.0 start_year=?\n  - Delta East - Abu Madi Pipeline | operating | Delta East field, Egypt -> Abu Madi field, Egypt | op=IEOC dia=16.0 len_km=17.0 start_year=?\n  - Rashid - Idku Pipeline | operating | Rashid fields, offshore Egypt -> Idku, Egypt | op=Rashpetco dia=16.0 len_km=46.0 start_year=?\n  - Scarab/Saffron - Idku Pipeline | operating | Scarab / Saffron fields, offhore Egypt -> Idku, Egypt | op=Burullus Gas Company dia=36.0 len_km=61.0 start_year=2003\n  - Abu Qir - Meadia Pipeline | operating | Abu Qir field, offshore Egypt -> Meadia (Abu Qir) GP, Egypt | op=Energean Oil & Gas dia=16.0 len_km=23.0 start_year=?\n  - Taurus/Sapphire - Scarab/Saffron Pipeline | operating | Taurus / Sapphire fields, offshore Egypt -> Scarab/Saffron Pipeline | op=bp dia=16.0 len_km=29.0 start_year=2017\n  - Myas - Abu Seif Pipeline | operating | Myas field, offshore Egypt -> Abu Seif field, offshore Egypt | op=Eni dia=16.0 len_km=10.0 start_year=?\n  - Barboni - Baracuda Pipeline | operating | Barboni field, offshore Egypt -> Baracuda fields, offshore Egypt | op=Eni dia=16.0 len_km=7.0 start_year=?\n  - Thekah - Darfeel Pipeline | operating | Thekah field, offshore Egypt -> Darfeel field, offshore Egypt | op=Eni dia=16.0 len_km=29.0 start_year=?\n  - Abu El Naga - Baltim/Abu Madi Pipeline | operating | Abu El Naga fields, Egypt -> Baltim - Abu Madi Pipeline | op=Egyptian Natural Gas Company [Gasco] dia=28.0 len_km=45.0 start_year=?\n  - Abu Monkar - Sondos Pipeline | operating | Abu Monkar field, Egypt -> Sondos field, Egypt | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=17.0 start_year=?\n  - Abu Monkar - Sherbean Pipeline | operating | Abu Monkar field, Egypt -> Sherbean field, Egypt | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=4.0 start_year=?\n  - Ras Shukheir - Suez Pipeline | operating | Ras Shukheir, Egypt -> Suez, Egypt | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=154.0 start_year=?\n  - BAPETCO Pipeline | operating | Alam El Shawish, Egypt -> Ameriya Refinery, Egypt | op=Badr El Din Petroleum Company (BAPETCO) dia=24.0 len_km=97.0 start_year=?\n  - Western Desert Gas Project - South Line | operating | Abu El-Gharadiq field, Egypt -> Dahshour, Egypt | op=Badr El Din Petroleum Company (BAPETCO) dia=24.0 len_km=180.0 start_year=1974\n  - Western Desert Gas Project - Tarek Spur | operating | Ras Kanayes 4 field, Egypt -> Tarek field, Egypt | op=Khalda Petroleum Company (KPC) dia=10.0 len_km=14.0 start_year=?\n  - Western Desert Gas Project - North Line | operating | Obaiyed field, Egypt -> Ameriya Refinery, Egypt | op=Badr El Din Petroleum Company (BAPETCO) dia=34.0 len_km=196.0 start_year=1999\n  - Salam - WDGP-N | operating | Salam field, Egypt -> Western Desert Gas Project - North Line, Egypt | op=Khalda Petroleum Co dia=22.0 len_km=23.0 start_year=?\n  - Badr el Din 2 - Badr el Din Pipeline | operating | Badr el Din 2 field, Egypt -> Badr el Din GP, Egypt | op=Cheiron/Capricorn Energy dia=16.0 len_km=19.0 start_year=?\n  - Western Desert Gas Project - South Line | operating | Salam field, Egypt -> Abu Gharadiq GP, Egypt | op=Badr El Din Petroleum Company (BAPETCO) dia=18.0 len_km=296.0 start_year=?\n  - Shams - Obaiyed Pipeline | operating | Shams field, Egypt -> Obaiyed field, Egypt | op=Khalda Petroleum Co dia=20.0 len_km=28.0 start_year=?\n  - South Valley Gas Pipeline | operating | Beni Suef, Egypt -> Abu Qurqus, Egypt | op=Nile Valley Gas Company dia=32.0 len_km=93.0 start_year=2007\n  - Abu Sir - Ameriya Pipeline | proposed | Abu Sir field, offshore Egypt -> Ameriya Refinery, Egypt | op=Egyptian Natural Gas Company [Gasco] dia=12.0 len_km=50.0 start_year=2026\n  - Meleiha - Marsa Matruh Pipeline | operating | Meleiha field, Egypt -> Marsa Matruh, Egypt | op=Khalda Petroleum Company (KPC) dia=10.0 len_km=48.0 start_year=?\n  - Khepri - Salam Pipeline | operating | Khepri field, Egypt -> Salam field, Egypt | op=Khalda Petroleum Company (KPC) dia=12.0 len_km=41.0 start_year=?\n  - Shams - WDGP-N | operating | Salam field, Egypt -> Western Desert Gas Project - North Line, Egypt | op=Khalda Petroleum Company (KPC) dia=16.0 len_km=63.0 start_year=?\n  - Qasr GP - Shams Pipeline | operating | Qasr GP, Egypt -> Shams field, Egypt | op=Khalda Petroleum Company (KPC) dia=24.0 len_km=24.0 start_year=?\n  - Abu Sennan Spur | operating | GPT field, Egypt -> Pipeline T junction | op=EGPC dia=14.0 len_km=33.0 start_year=?\n  - Badr el Din Field - Alam El Shawish Pipeline | operating | Badr el Din fields, Egypt -> Alam El Shawish, Egypt | op=Shell dia=20.0 len_km=63.0 start_year=?\n  - BAPETCO - Idku Pipeline | operating | BAPETCO Pipeline -> Idku - Tanta Pipeline | op=Badr El Din Petroleum Company (BAPETCO) dia=16.0 len_km=40.0 start_year=?\n  - Dahshour - Mostorod Pipeline | operating | Dahshour, Egypt -> Mostorod (Cairo), Egypt | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=25.0 start_year=?\n  - South Valley Gas Pipeline | operating | Gerga, Egypt -> Aswan, Egypt | op=Nile Valley Gas Company dia=30.0 len_km=242.0 start_year=2008\n  - South Valley Gas Pipeline | operating | Asyut, Egypt -> Gerga, Egypt | op=Nile Valley Gas Company dia=32.0 len_km=75.0 start_year=2008\n  - South Valley Gas Pipeline | operating | Abu Qurqus, Egypt -> Asyut, Egypt | op=Nile Valley Gas Company dia=32.0 len_km=91.0 start_year=2007\n  - South Valley Gas Pipeline | operating | El-Koraimet, Egypt -> Beni Suef, Egypt | op=Nile Valley Gas Company dia=32.0 len_km=19.0 start_year=2007\n  - South Valley Gas Pipeline | operating | Dahsour, Egypt -> El-Koraimet, Egypt | op=Nile Valley Gas Company dia=36.0 len_km=56.0 start_year=2007\n  - Ras Shukheir - Hurghada | operating | Ras Shukheir, Egypt -> Hurghada, Egypt | op=Egyptian Natural Gas Company [Gasco] dia=24.0 len_km=79.0 start_year=2007\n  - Hurghada - Port Safaga Pipeline | operating | Hurghada, Egypt -> Port Safaga | op=Egyptian Natural Gas Company [Gasco] dia=24.0 len_km=40.0 start_year=?\n  - Zeit Bay - Ras Shukheir Line | operating | Zeit Bay field, offshore Egypt -> Ras Shukheir - Hurghada Pipeline | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=2.0 start_year=?\n  - Suez - Port Said Pipeline | operating | Suez, Egypt -> Port Said, Egypt | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=117.0 start_year=?\n  - Tanta - Mostorod Pipeline | operating | Tanta, Egypt -> Mostorod (Cairo), Egypt | op=Egyptian Natural Gas Company [Gasco] dia=28.0 len_km=63.0 start_year=?\n  - Idku - Tanta Pipeline | operating | Idku, Egypt -> Tanta, Egypt | op=Egyptian Natural Gas Company [Gasco] dia=28.0 len_km=79.0 start_year=?\n  - Ha'py - Damietta Pipeline | operating | Ha'py field, offshore Egypt -> Damietta - Port Said Pipeline | op=IEOC dia=16.0 len_km=38.0 start_year=2000\n  - Abu Qir West - Abu Qir Line | operating | Abu Qir West field, offshore Egypt -> Abu Qir field, offshore Egypt | op=Edison dia=6.0 len_km=7.0 start_year=2022\n  - Abu Qir North - Abu Qir Pipeline | operating | Abu Qir North field, offshore Egypt -> Abu Qir field, offshore Egypt | op=Edison dia=16.0 len_km=13.0 start_year=?\n  - Fayoum - Idku Pipeline | operating | Fayoum field, offshore Egypt -> Idku, Egypt | op=bp dia=16.0 len_km=52.0 start_year=2022\n  - Baltim North - Abu Madi Pipeline | operating | Baltim North field, offshore Egypt -> Abu Madi field, Egypt | op=Eni dia=16.0 len_km=31.0 start_year=?\n  - Damietta - Port Said Pipeline | operating | Damietta, Egypt -> Port Said, Egypt | op=PetroGas dia=32.0 len_km=112.0 start_year=?\n  - Nouras - Darfeel Line | operating | Nouras field, offshore Egypt -> Darfeel field, offshore Egypt | op=Eni dia=16.0 len_km=5.0 start_year=?\n  - Baracuda - Darfeel Pipeline | operating | Baracuda fields, offshore Egypt -> Darfeel field, offshore Egypt | op=Eni dia=16.0 len_km=12.0 start_year=?\n  - Baracuda - Wakar Line | operating | Baracuda fields, offshore Egypt -> Wakar field, offshore Egypt | op=Eni dia=16.0 len_km=6.0 start_year=?\n  - Tuna - Denise Pipeline | operating | Tuna field, offshore Egypt -> Denise field, offshore Egypt | op=Petrobel dia=24.0 len_km=8.0 start_year=?\n  - Gasco Pipeline | operating | Offshore fields, Egypt -> Shore | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=31.0 start_year=2007\n  - Amal - Shore Pipeline | operating | Amal field, offshore Egypt -> Shore | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=12.0 start_year=2007\n  - Belayim - Ras Shukheir/Suez Pipeline | operating | Belayim field -> Ras Shukheir - Suez pipeline | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=60.0 start_year=?\n  - Belayim/Ras Shukheir/Suez - Jabal Thal Pipeline | operating | Belayim - Ras Shukheir/Suez pipeline -> Jabal Thal area | op=Egyptian Natural Gas Company [Gasco] dia=16.0 len_km=27.0 start_year=?\n  - Denise - El Gamil Pipeline | operating | Denise field, offshore Egypt -> El Gamil, Egypt | op=Eni dia=16.0 len_km=41.0 start_year=?\n  - Zohr Gas Export Pipeline | operating | Zohr field, offshore Egypt -> Denise field, offshore Egypt | op=Eni dia=26.0 len_km=80.0 start_year=2017\n  - Salam - Matruh | operating | Salam field, Egypt -> Matrouh, Egypt | op=Khalda Petroleum Company (KPC) dia=16.0 len_km=52.0 start_year=1991\n  - GPT - Abu Sennan Spur | operating | GPT field, Egypt -> Alam El Shawish, Egypt | op=EGPC dia=14.0 len_km=13.0 start_year=?\n  - Qasr - Salam | operating | Qasr field, Egypt -> Salam field, Egypt | op=Khalda Petroleum Company (KPC) dia=6.0 len_km=19.0 start_year=?",
 "gulfpub_note": "GulfPub PE World Map (SDE Dec-2025 scrape) covers Egypt gas (95 features incl. cross-border). Use it to corroborate specs/endpoints/operator AND to catch duplicates/relabels/misclassification. pid_crosswalk matching is fuzzy - treat as a lead, verify. Capacity_mmcfd=300 is a PLACEHOLDER, never a capacity. GulfPub is Tier-2: one source in a conflict, never automatically authoritative.",
 "gulfpub_status_conflicts": [
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Denise - Port Said Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Raven - Idku Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Denise Gas Pipeline",
   "gem_status": "operating",
   "gulfpub_name": "Assad - Barboni Pipeline",
   "gp_status": "proposed"
  },
  {
   "gem_name": "Denise Gas Pipeline",
   "gem_status": "operating",
   "gulfpub_name": "Tulip - Abu Monkar Pipeline",
   "gp_status": "proposed"
  },
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Zohr Gas Export Pipeline II",
   "gp_status": "operating"
  },
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Tao - Port Said/El Arish Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Nitzana Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Darfeel - El Gamil Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Port Said - El Arish Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "El Fayrouz - Suez/Port Said Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Abu Madi - Tanta Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Nitzana Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Scarab/Saffron - Idku Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "BAPETCO Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Mahmoudiah PS Gas Pipeline",
   "gem_status": "operating",
   "gulfpub_name": "Abu Sir - Ameriya Pipeline",
   "gp_status": "proposed"
  },
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Suez - Port Said Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Tanta - Mostorod Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Idku - Tanta Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "New Fayoum Gas Pipeline",
   "gem_status": "construction",
   "gulfpub_name": "Fayoum - Idku Pipeline",
   "gp_status": "operating"
  },
  {
   "gem_name": "Cronos-Port Said Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Damietta - Port Said Pipeline",
   "gp_status": "operating"
  }
 ],
 "pid_crosswalk": {
  "P7597": [
   {
    "gulfpub_name": "Denise - Port Said Pipeline",
    "confidence": "green",
    "composite": 0.8365,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 46.0,
    "gp_start": "Denise field, offshore Egypt",
    "gp_end": "Port Said, Egypt",
    "reason": "overlap green 0.8365; status_conflict=CONFLICT diam=- len=DELTA 49%"
   },
   {
    "gulfpub_name": "Raven - Idku Pipeline",
    "confidence": "yellow",
    "composite": 0.6515,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 46.0,
    "gp_start": "Raven field, offshore Egypt",
    "gp_end": "Idku, Egypt",
    "reason": "overlap yellow 0.6515; status_conflict=CONFLICT diam=- len=DELTA 49%"
   },
   {
    "gulfpub_name": "Zohr Gas Export Pipeline II",
    "confidence": "yellow",
    "composite": 0.6845,
    "gp_status": "operating",
    "gp_dia": "30.0",
    "gp_len_km": 80.0,
    "gp_start": "Zohr field, offshore Egypt",
    "gp_end": "Denise field, offshore Egypt",
    "reason": "overlap yellow 0.6845; status_conflict=CONFLICT diam=- len=DELTA 11%"
   },
   {
    "gulfpub_name": "Tao - Port Said/El Arish Pipeline",
    "confidence": "green",
    "composite": 0.7622,
    "gp_status": "operating",
    "gp_dia": "20.0",
    "gp_len_km": 31.0,
    "gp_start": "Tao field, offshore Egypt",
    "gp_end": "Port Said - El Arish Pipeline",
    "reason": "overlap green 0.7622; status_conflict=CONFLICT diam=- len=DELTA 66%"
   },
   {
    "gulfpub_name": "Port Said - El Arish Pipeline",
    "confidence": "yellow",
    "composite": 0.7265,
    "gp_status": "operating",
    "gp_dia": "36.0",
    "gp_len_km": 147.0,
    "gp_start": "Port Said, Egypt",
    "gp_end": "El Arish, Egypt",
    "reason": "overlap yellow 0.7265; status_conflict=CONFLICT diam=- len=DELTA 39%"
   },
   {
    "gulfpub_name": "El Fayrouz - Suez/Port Said Pipeline",
    "confidence": "green",
    "composite": 0.7913,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 49.0,
    "gp_start": "El Fayrouz field, Egypt",
    "gp_end": "Suez - Port Said Pipeline",
    "reason": "overlap green 0.7913; status_conflict=CONFLICT diam=- len=DELTA 46%"
   },
   {
    "gulfpub_name": "Abu Madi - Tanta Pipeline",
    "confidence": "yellow",
    "composite": 0.6477,
    "gp_status": "operating",
    "gp_dia": "8.0",
    "gp_len_km": 50.0,
    "gp_start": "Abu Madi field, Egypt",
    "gp_end": "Tanta, Egypt",
    "reason": "overlap yellow 0.6477; status_conflict=CONFLICT diam=- len=DELTA 44%"
   },
   {
    "gulfpub_name": "BAPETCO Pipeline",
    "confidence": "yellow",
    "composite": 0.627,
    "gp_status": "operating",
    "gp_dia": "24.0",
    "gp_len_km": 97.0,
    "gp_start": "Alam El Shawish, Egypt",
    "gp_end": "Ameriya Refinery, Egypt",
    "reason": "overlap yellow 0.627; status_conflict=CONFLICT diam=- len=ok"
   },
   {
    "gulfpub_name": "Suez - Port Said Pipeline",
    "confidence": "green",
    "composite": 0.7972,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 117.0,
    "gp_start": "Suez, Egypt",
    "gp_end": "Port Said, Egypt",
    "reason": "overlap green 0.7972; status_conflict=CONFLICT diam=- len=DELTA 23%"
   },
   {
    "gulfpub_name": "Tanta - Mostorod Pipeline",
    "confidence": "yellow",
    "composite": 0.675,
    "gp_status": "operating",
    "gp_dia": "28.0",
    "gp_len_km": 63.0,
    "gp_start": "Tanta, Egypt",
    "gp_end": "Mostorod (Cairo), Egypt",
    "reason": "overlap yellow 0.675; status_conflict=CONFLICT diam=- len=DELTA 30%"
   },
   {
    "gulfpub_name": "Idku - Tanta Pipeline",
    "confidence": "yellow",
    "composite": 0.6522,
    "gp_status": "operating",
    "gp_dia": "28.0",
    "gp_len_km": 79.0,
    "gp_start": "Idku, Egypt",
    "gp_end": "Tanta, Egypt",
    "reason": "overlap yellow 0.6522; status_conflict=CONFLICT diam=- len=DELTA 12%"
   },
   {
    "gulfpub_name": "Damietta - Port Said Pipeline",
    "confidence": "green",
    "composite": 0.7637,
    "gp_status": "operating",
    "gp_dia": "32.0",
    "gp_len_km": 112.0,
    "gp_start": "Damietta, Egypt",
    "gp_end": "Port Said, Egypt",
    "reason": "overlap green 0.7637; status_conflict=CONFLICT diam=- len=DELTA 20%"
   }
  ],
  "P7577;P7578": [
   {
    "gulfpub_name": "Simian/Sienna - Idku Pipeline",
    "confidence": "yellow",
    "composite": 0.7142,
    "gp_status": "operating",
    "gp_dia": "26.0",
    "gp_len_km": 63.0,
    "gp_start": "Simian/Sienna fields, offshore Egypt",
    "gp_end": "Idku, Egypt",
    "reason": "overlap yellow 0.7142; status_conflict= diam=ok len=DELTA 32%"
   },
   {
    "gulfpub_name": "Zohr Gas Export Pipeline",
    "confidence": "yellow",
    "composite": 0.6978,
    "gp_status": "operating",
    "gp_dia": "26.0",
    "gp_len_km": 80.0,
    "gp_start": "Zohr field, offshore Egypt",
    "gp_end": "Denise field, offshore Egypt",
    "reason": "overlap yellow 0.6978; status_conflict= diam=ok len=DELTA 46%"
   }
  ],
  "P3938;P3937": [
   {
    "gulfpub_name": "Qarun West - WDGP-S",
    "confidence": "yellow",
    "composite": 0.5042,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 10.0,
    "gp_start": "Qarun West field, Egypt",
    "gp_end": "Western Desert Gas Project - South Line Pipeline",
    "reason": "overlap yellow 0.5042; status_conflict= diam=ok len=DELTA 96%"
   },
   {
    "gulfpub_name": "Taba - Sharma el Sheikh",
    "confidence": "yellow",
    "composite": 0.64,
    "gp_status": "operating",
    "gp_dia": "20.0",
    "gp_len_km": 137.0,
    "gp_start": "Taba, Egypt",
    "gp_end": "Sharma el Sheikh, Egypt",
    "reason": "overlap yellow 0.64; status_conflict= diam=DELTA 20% len=DELTA 47%"
   },
   {
    "gulfpub_name": "Suez - Dahshour Pipeline",
    "confidence": "yellow",
    "composite": 0.6824,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 88.0,
    "gp_start": "Suez, Egypt",
    "gp_end": "Dahshour, Egypt",
    "reason": "overlap yellow 0.6824; status_conflict= diam=ok len=DELTA 66%"
   },
   {
    "gulfpub_name": "Seth - Ha'py Lateral",
    "confidence": "yellow",
    "composite": 0.4602,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 5.0,
    "gp_start": "Seth field, offshore Egypt",
    "gp_end": "Ha'py - Shore Pipeline",
    "reason": "overlap yellow 0.4602; status_conflict= diam=ok len=DELTA 98%"
   },
   {
    "gulfpub_name": "Qantara  - Suez Lateral",
    "confidence": "yellow",
    "composite": 0.4787,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 5.0,
    "gp_start": "Qantara field, Egypt",
    "gp_end": "Suez - Port Said Pipeline",
    "reason": "overlap yellow 0.4787; status_conflict= diam=ok len=DELTA 98%"
   },
   {
    "gulfpub_name": "Port Faoud - Baracuda Pipeline",
    "confidence": "yellow",
    "composite": 0.632,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 18.0,
    "gp_start": "Port Faoud fields, offshore Egypt",
    "gp_end": "Baracuda fields, offshore Egypt",
    "reason": "overlap yellow 0.632; status_conflict= diam=ok len=DELTA 93%"
   },
   {
    "gulfpub_name": "Karous - Segan Line",
    "confidence": "yellow",
    "composite": 0.5245,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 2.0,
    "gp_start": "Karous field, offshore Egypt",
    "gp_end": "Segan tie in",
    "reason": "overlap yellow 0.5245; status_conflict= diam=ok len=DELTA 99%"
   },
   {
    "gulfpub_name": "Abu Madi - El Mansura Pipeline",
    "confidence": "yellow",
    "composite": 0.6562,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 24.0,
    "gp_start": "Abu Madi field, Egypt",
    "gp_end": "El Mansura area, Egypt",
    "reason": "overlap yellow 0.6562; status_conflict= diam=ok len=DELTA 91%"
   },
   {
    "gulfpub_name": "Delta East - Abu Madi Pipeline",
    "confidence": "yellow",
    "composite": 0.6107,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 17.0,
    "gp_start": "Delta East field, Egypt",
    "gp_end": "Abu Madi field, Egypt",
    "reason": "overlap yellow 0.6107; status_conflict= diam=ok len=DELTA 93%"
   },
   {
    "gulfpub_name": "Badr el Din 2 - Badr el Din Pipeline",
    "confidence": "yellow",
    "composite": 0.7491,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 19.0,
    "gp_start": "Badr el Din 2 field, Egypt",
    "gp_end": "Badr el Din GP, Egypt",
    "reason": "overlap yellow 0.7491; status_conflict= diam=ok len=DELTA 93%"
   },
   {
    "gulfpub_name": "Badr el Din Field - Alam El Shawish Pipeline",
    "confidence": "yellow",
    "composite": 0.7356,
    "gp_status": "operating",
    "gp_dia": "20.0",
    "gp_len_km": 63.0,
    "gp_start": "Badr el Din fields, Egypt",
    "gp_end": "Alam El Shawish, Egypt",
    "reason": "overlap yellow 0.7356; status_conflict= diam=DELTA 20% len=DELTA 76%"
   },
   {
    "gulfpub_name": "Zeit Bay - Ras Shukheir Line",
    "confidence": "yellow",
    "composite": 0.5278,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 2.0,
    "gp_start": "Zeit Bay field, offshore Egypt",
    "gp_end": "Ras Shukheir - Hurghada Pipeline",
    "reason": "overlap yellow 0.5278; status_conflict= diam=ok len=DELTA 99%"
   },
   {
    "gulfpub_name": "Nouras - Darfeel Line",
    "confidence": "yellow",
    "composite": 0.5453,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 5.0,
    "gp_start": "Nouras field, offshore Egypt",
    "gp_end": "Darfeel field, offshore Egypt",
    "reason": "overlap yellow 0.5453; status_conflict= diam=ok len=DELTA 98%"
   },
   {
    "gulfpub_name": "Baracuda - Wakar Line",
    "confidence": "yellow",
    "composite": 0.5465,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 6.0,
    "gp_start": "Baracuda fields, offshore Egypt",
    "gp_end": "Wakar field, offshore Egypt",
    "reason": "overlap yellow 0.5465; status_conflict= diam=ok len=DELTA 98%"
   },
   {
    "gulfpub_name": "Belayim - Ras Shukheir/Suez Pipeline",
    "confidence": "yellow",
    "composite": 0.638,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 60.0,
    "gp_start": "Belayim field",
    "gp_end": "Ras Shukheir - Suez pipeline",
    "reason": "overlap yellow 0.638; status_conflict= diam=ok len=DELTA 77%"
   }
  ],
  "P7447": [
   {
    "gulfpub_name": "Assad - Barboni Pipeline",
    "confidence": "yellow",
    "composite": 0.6064,
    "gp_status": "proposed",
    "gp_dia": "16.0",
    "gp_len_km": 14.0,
    "gp_start": "Assad field, offshore Egypt",
    "gp_end": "Barboni field, offshore Egypt",
    "reason": "overlap yellow 0.6064; status_conflict=CONFLICT diam=ok len=DELTA 97%"
   },
   {
    "gulfpub_name": "Tulip - Abu Monkar Pipeline",
    "confidence": "yellow",
    "composite": 0.6035,
    "gp_status": "proposed",
    "gp_dia": "16.0",
    "gp_len_km": 10.0,
    "gp_start": "Tulip field, Egypt",
    "gp_end": "Abu Monkar field, Egypt",
    "reason": "overlap yellow 0.6035; status_conflict=CONFLICT diam=ok len=DELTA 98%"
   },
   {
    "gulfpub_name": "Akhen - Denise Pipeline",
    "confidence": "green",
    "composite": 0.7615,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 11.0,
    "gp_start": "Akhen field, offshore Egypt",
    "gp_end": "Denise field, offshore Egypt",
    "reason": "overlap green 0.7615; status_conflict= diam=ok len=DELTA 97%"
   },
   {
    "gulfpub_name": "Segan - Darfeel/Shore Pipeline",
    "confidence": "yellow",
    "composite": 0.6538,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 13.0,
    "gp_start": "Segan field, offshore Egypt",
    "gp_end": "Darfeel - El Gamil Pipeline",
    "reason": "overlap yellow 0.6538; status_conflict= diam=ok len=DELTA 97%"
   },
   {
    "gulfpub_name": "Denise - Wakar Pipeline",
    "confidence": "green",
    "composite": 0.7644,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 15.0,
    "gp_start": "Denise field, offshore Egypt",
    "gp_end": "Segan - Darfeel/Shore Pipeline",
    "reason": "overlap green 0.7644; status_conflict= diam=ok len=DELTA 96%"
   },
   {
    "gulfpub_name": "Baltim East - Abu Madi Pipeline",
    "confidence": "yellow",
    "composite": 0.6104,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 18.0,
    "gp_start": "Baltim East field, offshore Egypt",
    "gp_end": "Abu Madi field, Egypt",
    "reason": "overlap yellow 0.6104; status_conflict= diam=ok len=DELTA 96%"
   },
   {
    "gulfpub_name": "North Mansoura Pipeline",
    "confidence": "yellow",
    "composite": 0.6053,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 14.0,
    "gp_start": "Northern Mansoura gas field",
    "gp_end": "Northwestern Mansoura gas field",
    "reason": "overlap yellow 0.6053; status_conflict= diam=ok len=DELTA 97%"
   },
   {
    "gulfpub_name": "Rashid - Idku Pipeline",
    "confidence": "yellow",
    "composite": 0.6695,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 46.0,
    "gp_start": "Rashid fields, offshore Egypt",
    "gp_end": "Idku, Egypt",
    "reason": "overlap yellow 0.6695; status_conflict= diam=ok len=DELTA 89%"
   },
   {
    "gulfpub_name": "Taurus/Sapphire - Scarab/Saffron Pipeline",
    "confidence": "yellow",
    "composite": 0.6164,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 29.0,
    "gp_start": "Taurus / Sapphire fields, offshore Egypt",
    "gp_end": "Scarab/Saffron Pipeline",
    "reason": "overlap yellow 0.6164; status_conflict= diam=ok len=DELTA 93%"
   },
   {
    "gulfpub_name": "Myas - Abu Seif Pipeline",
    "confidence": "yellow",
    "composite": 0.6031,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 10.0,
    "gp_start": "Myas field, offshore Egypt",
    "gp_end": "Abu Seif field, offshore Egypt",
    "reason": "overlap yellow 0.6031; status_conflict= diam=ok len=DELTA 98%"
   },
   {
    "gulfpub_name": "Barboni - Baracuda Pipeline",
    "confidence": "yellow",
    "composite": 0.6007,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 7.0,
    "gp_start": "Barboni field, offshore Egypt",
    "gp_end": "Baracuda fields, offshore Egypt",
    "reason": "overlap yellow 0.6007; status_conflict= diam=ok len=DELTA 98%"
   },
   {
    "gulfpub_name": "Thekah - Darfeel Pipeline",
    "confidence": "yellow",
    "composite": 0.6573,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 29.0,
    "gp_start": "Thekah field, offshore Egypt",
    "gp_end": "Darfeel field, offshore Egypt",
    "reason": "overlap yellow 0.6573; status_conflict= diam=ok len=DELTA 93%"
   },
   {
    "gulfpub_name": "Abu Monkar - Sondos Pipeline",
    "confidence": "yellow",
    "composite": 0.6065,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 17.0,
    "gp_start": "Abu Monkar field, Egypt",
    "gp_end": "Sondos field, Egypt",
    "reason": "overlap yellow 0.6065; status_conflict= diam=ok len=DELTA 96%"
   },
   {
    "gulfpub_name": "Abu Monkar - Sherbean Pipeline",
    "confidence": "yellow",
    "composite": 0.5989,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 4.0,
    "gp_start": "Abu Monkar field, Egypt",
    "gp_end": "Sherbean field, Egypt",
    "reason": "overlap yellow 0.5989; status_conflict= diam=ok len=DELTA 99%"
   },
   {
    "gulfpub_name": "Ras Shukheir - Suez Pipeline",
    "confidence": "yellow",
    "composite": 0.7067,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 154.0,
    "gp_start": "Ras Shukheir, Egypt",
    "gp_end": "Suez, Egypt",
    "reason": "overlap yellow 0.7067; status_conflict= diam=ok len=DELTA 62%"
   },
   {
    "gulfpub_name": "Shams - WDGP-N",
    "confidence": "yellow",
    "composite": 0.5124,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 63.0,
    "gp_start": "Salam field, Egypt",
    "gp_end": "Western Desert Gas Project - North Line, Egypt",
    "reason": "overlap yellow 0.5124; status_conflict= diam=ok len=DELTA 84%"
   },
   {
    "gulfpub_name": "Abu Qir North - Abu Qir Pipeline",
    "confidence": "yellow",
    "composite": 0.6056,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 13.0,
    "gp_start": "Abu Qir North field, offshore Egypt",
    "gp_end": "Abu Qir field, offshore Egypt",
    "reason": "overlap yellow 0.6056; status_conflict= diam=ok len=DELTA 97%"
   },
   {
    "gulfpub_name": "Baracuda - Darfeel Pipeline",
    "confidence": "yellow",
    "composite": 0.6036,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 12.0,
    "gp_start": "Baracuda fields, offshore Egypt",
    "gp_end": "Darfeel field, offshore Egypt",
    "reason": "overlap yellow 0.6036; status_conflict= diam=ok len=DELTA 97%"
   },
   {
    "gulfpub_name": "Amal - Shore Pipeline",
    "confidence": "yellow",
    "composite": 0.6036,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 12.0,
    "gp_start": "Amal field, offshore Egypt",
    "gp_end": "Shore",
    "reason": "overlap yellow 0.6036; status_conflict= diam=ok len=DELTA 97%"
   },
   {
    "gulfpub_name": "Belayim/Ras Shukheir/Suez - Jabal Thal Pipeline",
    "confidence": "yellow",
    "composite": 0.6133,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 27.0,
    "gp_start": "Belayim - Ras Shukheir/Suez pipeline",
    "gp_end": "Jabal Thal area",
    "reason": "overlap yellow 0.6133; status_conflict= diam=ok len=DELTA 93%"
   },
   {
    "gulfpub_name": "Denise - El Gamil Pipeline",
    "confidence": "green",
    "composite": 0.7831,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 41.0,
    "gp_start": "Denise field, offshore Egypt",
    "gp_end": "El Gamil, Egypt",
    "reason": "overlap green 0.7831; status_conflict= diam=ok len=DELTA 90%"
   }
  ],
  "P6700": [
   {
    "gulfpub_name": "Abu Sultan - Dahshour Pipeline",
    "confidence": "yellow",
    "composite": 0.6986,
    "gp_status": "operating",
    "gp_dia": "32.0",
    "gp_len_km": 81.0,
    "gp_start": "Abu Sultan, Egypt",
    "gp_end": "Dahshour, Egypt",
    "reason": "overlap yellow 0.6986; status_conflict= diam=ok len=DELTA 45%"
   },
   {
    "gulfpub_name": "South Valley Gas Pipeline",
    "confidence": "green",
    "composite": 0.9385,
    "gp_status": "operating",
    "gp_dia": "32.0",
    "gp_len_km": 91.0,
    "gp_start": "Abu Qurqus, Egypt",
    "gp_end": "Asyut, Egypt",
    "reason": "overlap green 0.9385; status_conflict= diam=ok len=DELTA 38%"
   }
  ],
  "P7580": [
   {
    "gulfpub_name": "Media - Idku/Tanta Pipeline",
    "confidence": "yellow",
    "composite": 0.686,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 32.0,
    "gp_start": "Meadia (Abu Qir) GP, Egypt",
    "gp_end": "Idku - Tanta Pipeline",
    "reason": "overlap yellow 0.686; status_conflict= diam=- len=DELTA 38%"
   },
   {
    "gulfpub_name": "Port Fouad Marine - El Gamil Pipeline",
    "confidence": "yellow",
    "composite": 0.661,
    "gp_status": "operating",
    "gp_dia": "48.0",
    "gp_len_km": 38.0,
    "gp_start": "Port Fouad Marine field, offshore Egypt",
    "gp_end": "Damietta - Port Said Pipeline",
    "reason": "overlap yellow 0.661; status_conflict= diam=- len=DELTA 27%"
   },
   {
    "gulfpub_name": "Abu Madi - Tanta",
    "confidence": "yellow",
    "composite": 0.4565,
    "gp_status": "operating",
    "gp_dia": "22.0",
    "gp_len_km": 52.0,
    "gp_start": "Abu Madi field, Egypt",
    "gp_end": "Tanta, Egypt",
    "reason": "overlap yellow 0.4565; status_conflict= diam=- len=ok"
   },
   {
    "gulfpub_name": "Abu Qir - Meadia Pipeline",
    "confidence": "yellow",
    "composite": 0.6705,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 23.0,
    "gp_start": "Abu Qir field, offshore Egypt",
    "gp_end": "Meadia (Abu Qir) GP, Egypt",
    "reason": "overlap yellow 0.6705; status_conflict= diam=- len=DELTA 56%"
   },
   {
    "gulfpub_name": "Abu El Naga - Baltim/Abu Madi Pipeline",
    "confidence": "yellow",
    "composite": 0.6227,
    "gp_status": "operating",
    "gp_dia": "28.0",
    "gp_len_km": 45.0,
    "gp_start": "Abu El Naga fields, Egypt",
    "gp_end": "Baltim - Abu Madi Pipeline",
    "reason": "overlap yellow 0.6227; status_conflict= diam=- len=DELTA 13%"
   },
   {
    "gulfpub_name": "Abu Sir - Ameriya Pipeline",
    "confidence": "green",
    "composite": 0.7555,
    "gp_status": "proposed",
    "gp_dia": "12.0",
    "gp_len_km": 50.0,
    "gp_start": "Abu Sir field, offshore Egypt",
    "gp_end": "Ameriya Refinery, Egypt",
    "reason": "overlap green 0.7555; status_conflict=CONFLICT diam=- len=ok"
   },
   {
    "gulfpub_name": "Meleiha - Marsa Matruh Pipeline",
    "confidence": "yellow",
    "composite": 0.6817,
    "gp_status": "operating",
    "gp_dia": "10.0",
    "gp_len_km": 48.0,
    "gp_start": "Meleiha field, Egypt",
    "gp_end": "Marsa Matruh, Egypt",
    "reason": "overlap yellow 0.6817; status_conflict= diam=- len=ok"
   },
   {
    "gulfpub_name": "Khepri - Salam Pipeline",
    "confidence": "yellow",
    "composite": 0.6208,
    "gp_status": "operating",
    "gp_dia": "12.0",
    "gp_len_km": 41.0,
    "gp_start": "Khepri field, Egypt",
    "gp_end": "Salam field, Egypt",
    "reason": "overlap yellow 0.6208; status_conflict= diam=- len=DELTA 21%"
   },
   {
    "gulfpub_name": "BAPETCO - Idku Pipeline",
    "confidence": "yellow",
    "composite": 0.6582,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 40.0,
    "gp_start": "BAPETCO Pipeline",
    "gp_end": "Idku - Tanta Pipeline",
    "reason": "overlap yellow 0.6582; status_conflict= diam=- len=DELTA 23%"
   },
   {
    "gulfpub_name": "Dahshour - Mostorod Pipeline",
    "confidence": "yellow",
    "composite": 0.6272,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 25.0,
    "gp_start": "Dahshour, Egypt",
    "gp_end": "Mostorod (Cairo), Egypt",
    "reason": "overlap yellow 0.6272; status_conflict= diam=- len=DELTA 52%"
   },
   {
    "gulfpub_name": "Ha'py - Damietta Pipeline",
    "confidence": "yellow",
    "composite": 0.6717,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 38.0,
    "gp_start": "Ha'py field, offshore Egypt",
    "gp_end": "Damietta - Port Said Pipeline",
    "reason": "overlap yellow 0.6717; status_conflict= diam=- len=DELTA 27%"
   },
   {
    "gulfpub_name": "Baltim North - Abu Madi Pipeline",
    "confidence": "yellow",
    "composite": 0.6437,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 31.0,
    "gp_start": "Baltim North field, offshore Egypt",
    "gp_end": "Abu Madi field, Egypt",
    "reason": "overlap yellow 0.6437; status_conflict= diam=- len=DELTA 40%"
   },
   {
    "gulfpub_name": "Gasco Pipeline",
    "confidence": "green",
    "composite": 0.7612,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 31.0,
    "gp_start": "Offshore fields, Egypt",
    "gp_end": "Shore",
    "reason": "overlap green 0.7612; status_conflict= diam=- len=DELTA 40%"
   }
  ],
  "P7574": [
   {
    "gulfpub_name": "Idku - Damietta",
    "confidence": "yellow",
    "composite": 0.5075,
    "gp_status": "operating",
    "gp_dia": "32.0",
    "gp_len_km": 103.0,
    "gp_start": "Idku, Egypt",
    "gp_end": "Damietta, Egypt",
    "reason": "overlap yellow 0.5075; status_conflict= diam=ok len=DELTA 39%"
   }
  ],
  "P7864": [
   {
    "gulfpub_name": "Darfeel - El Gamil Pipeline",
    "confidence": "green",
    "composite": 0.794,
    "gp_status": "operating",
    "gp_dia": "36.0",
    "gp_len_km": 35.0,
    "gp_start": "Darfeel field, offshore Egypt",
    "gp_end": "El Gamil, Egypt",
    "reason": "overlap green 0.794; status_conflict=CONFLICT diam=ok len=DELTA 46%"
   },
   {
    "gulfpub_name": "Scarab/Saffron - Idku Pipeline",
    "confidence": "green",
    "composite": 0.7575,
    "gp_status": "operating",
    "gp_dia": "36.0",
    "gp_len_km": 61.0,
    "gp_start": "Scarab / Saffron fields, offhore Egypt",
    "gp_end": "Idku, Egypt",
    "reason": "overlap green 0.7575; status_conflict=CONFLICT diam=ok len=ok"
   }
  ],
  "P6692": [
   {
    "gulfpub_name": "Western Desert Gas Project - South Line",
    "confidence": "yellow",
    "composite": 0.4649,
    "gp_status": "operating",
    "gp_dia": "24.0",
    "gp_len_km": 180.0,
    "gp_start": "Abu El-Gharadiq field, Egypt",
    "gp_end": "Dahshour, Egypt",
    "reason": "overlap yellow 0.4649; status_conflict= diam=ok len=DELTA 78%"
   },
   {
    "gulfpub_name": "Qasr GP - Shams Pipeline",
    "confidence": "green",
    "composite": 0.9688,
    "gp_status": "operating",
    "gp_dia": "24.0",
    "gp_len_km": 24.0,
    "gp_start": "Qasr GP, Egypt",
    "gp_end": "Shams field, Egypt",
    "reason": "overlap green 0.9688; status_conflict= diam=ok len=DELTA 40%"
   }
  ],
  "P7589": [
   {
    "gulfpub_name": "Western Desert Gas Project - Tarek Spur",
    "confidence": "yellow",
    "composite": 0.5522,
    "gp_status": "operating",
    "gp_dia": "10.0",
    "gp_len_km": 14.0,
    "gp_start": "Ras Kanayes 4 field, Egypt",
    "gp_end": "Tarek field, Egypt",
    "reason": "overlap yellow 0.5522; status_conflict= diam=ok len=DELTA 63%"
   }
  ],
  "P6687;P0474;P3934": [
   {
    "gulfpub_name": "Western Desert Gas Project - North Line",
    "confidence": "yellow",
    "composite": 0.6821,
    "gp_status": "operating",
    "gp_dia": "34.0",
    "gp_len_km": 196.0,
    "gp_start": "Obaiyed field, Egypt",
    "gp_end": "Ameriya Refinery, Egypt",
    "reason": "overlap yellow 0.6821; status_conflict= diam=DELTA 24% len=DELTA 39%"
   }
  ],
  "P6693": [
   {
    "gulfpub_name": "Salam - WDGP-N",
    "confidence": "yellow",
    "composite": 0.7027,
    "gp_status": "operating",
    "gp_dia": "22.0",
    "gp_len_km": 23.0,
    "gp_start": "Salam field, Egypt",
    "gp_end": "Western Desert Gas Project - North Line, Egypt",
    "reason": "overlap yellow 0.7027; status_conflict= diam=ok len=DELTA 34%"
   },
   {
    "gulfpub_name": "Qasr - Salam",
    "confidence": "yellow",
    "composite": 0.5428,
    "gp_status": "operating",
    "gp_dia": "6.0",
    "gp_len_km": 19.0,
    "gp_start": "Qasr field, Egypt",
    "gp_end": "Salam field, Egypt",
    "reason": "overlap yellow 0.5428; status_conflict= diam=DELTA 73% len=DELTA 46%"
   }
  ],
  "P0476": [
   {
    "gulfpub_name": "Western Desert Gas Project - South Line",
    "confidence": "green",
    "composite": 0.7616,
    "gp_status": "operating",
    "gp_dia": "18.0",
    "gp_len_km": 296.0,
    "gp_start": "Salam field, Egypt",
    "gp_end": "Abu Gharadiq GP, Egypt",
    "reason": "overlap green 0.7616; status_conflict= diam=ok len=DELTA 28%"
   }
  ],
  "P6688": [
   {
    "gulfpub_name": "Shams - Obaiyed Pipeline",
    "confidence": "green",
    "composite": 0.811,
    "gp_status": "operating",
    "gp_dia": "20.0",
    "gp_len_km": 28.0,
    "gp_start": "Shams field, Egypt",
    "gp_end": "Obaiyed field, Egypt",
    "reason": "overlap green 0.811; status_conflict= diam=DELTA 10% len=DELTA 33%"
   }
  ],
  "P6699": [
   {
    "gulfpub_name": "South Valley Gas Pipeline",
    "confidence": "green",
    "composite": 0.9355,
    "gp_status": "operating",
    "gp_dia": "32.0",
    "gp_len_km": 93.0,
    "gp_start": "Beni Suef, Egypt",
    "gp_end": "Abu Qurqus, Egypt",
    "reason": "overlap green 0.9355; status_conflict= diam=ok len=DELTA 38%"
   }
  ],
  "P6689": [
   {
    "gulfpub_name": "Abu Sennan Spur",
    "confidence": "yellow",
    "composite": 0.734,
    "gp_status": "operating",
    "gp_dia": "14.0",
    "gp_len_km": 33.0,
    "gp_start": "GPT field, Egypt",
    "gp_end": "Pipeline T junction",
    "reason": "overlap yellow 0.734; status_conflict= diam=ok len=DELTA 27%"
   },
   {
    "gulfpub_name": "GPT - Abu Sennan Spur",
    "confidence": "yellow",
    "composite": 0.6406,
    "gp_status": "operating",
    "gp_dia": "14.0",
    "gp_len_km": 13.0,
    "gp_start": "GPT field, Egypt",
    "gp_end": "Alam El Shawish, Egypt",
    "reason": "overlap yellow 0.6406; status_conflict= diam=ok len=DELTA 71%"
   }
  ],
  "P6702": [
   {
    "gulfpub_name": "South Valley Gas Pipeline",
    "confidence": "green",
    "composite": 0.9099,
    "gp_status": "operating",
    "gp_dia": "30.0",
    "gp_len_km": 242.0,
    "gp_start": "Gerga, Egypt",
    "gp_end": "Aswan, Egypt",
    "reason": "overlap green 0.9099; status_conflict= diam=ok len=DELTA 38%"
   }
  ],
  "P6701": [
   {
    "gulfpub_name": "South Valley Gas Pipeline",
    "confidence": "green",
    "composite": 0.9209,
    "gp_status": "operating",
    "gp_dia": "32.0",
    "gp_len_km": 75.0,
    "gp_start": "Asyut, Egypt",
    "gp_end": "Gerga, Egypt",
    "reason": "overlap green 0.9209; status_conflict= diam=ok len=DELTA 38%"
   }
  ],
  "P6698": [
   {
    "gulfpub_name": "South Valley Gas Pipeline",
    "confidence": "green",
    "composite": 0.9138,
    "gp_status": "operating",
    "gp_dia": "32.0",
    "gp_len_km": 19.0,
    "gp_start": "El-Koraimet, Egypt",
    "gp_end": "Beni Suef, Egypt",
    "reason": "overlap green 0.9138; status_conflict= diam=ok len=DELTA 37%"
   }
  ],
  "P6697": [
   {
    "gulfpub_name": "South Valley Gas Pipeline",
    "confidence": "green",
    "composite": 0.8334,
    "gp_status": "operating",
    "gp_dia": "36.0",
    "gp_len_km": 56.0,
    "gp_start": "Dahsour, Egypt",
    "gp_end": "El-Koraimet, Egypt",
    "reason": "overlap green 0.8334; status_conflict= diam=ok len=DELTA 38%"
   }
  ],
  "P6034": [
   {
    "gulfpub_name": "Ras Shukheir - Hurghada",
    "confidence": "yellow",
    "composite": 0.505,
    "gp_status": "operating",
    "gp_dia": "24.0",
    "gp_len_km": 79.0,
    "gp_start": "Ras Shukheir, Egypt",
    "gp_end": "Hurghada, Egypt",
    "reason": "overlap yellow 0.505; status_conflict= diam=ok len=DELTA 51%"
   },
   {
    "gulfpub_name": "Hurghada - Port Safaga Pipeline",
    "confidence": "green",
    "composite": 0.8497,
    "gp_status": "operating",
    "gp_dia": "24.0",
    "gp_len_km": 40.0,
    "gp_start": "Hurghada, Egypt",
    "gp_end": "Port Safaga",
    "reason": "overlap green 0.8497; status_conflict= diam=ok len=ok"
   }
  ],
  "P6686": [
   {
    "gulfpub_name": "Fayoum - Idku Pipeline",
    "confidence": "yellow",
    "composite": 0.669,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 52.0,
    "gp_start": "Fayoum field, offshore Egypt",
    "gp_end": "Idku, Egypt",
    "reason": "overlap yellow 0.669; status_conflict=CONFLICT diam=DELTA 99% len=DELTA 23%"
   }
  ],
  "P7577": [
   {
    "gulfpub_name": "Tuna - Denise Pipeline",
    "confidence": "yellow",
    "composite": 0.4958,
    "gp_status": "operating",
    "gp_dia": "24.0",
    "gp_len_km": 8.0,
    "gp_start": "Tuna field, offshore Egypt",
    "gp_end": "Denise field, offshore Egypt",
    "reason": "overlap yellow 0.4958; status_conflict= diam=DELTA 8% len=DELTA 56%"
   }
  ],
  "P3935": [
   {
    "gulfpub_name": "Salam - Matruh",
    "confidence": "yellow",
    "composite": 0.5172,
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 52.0,
    "gp_start": "Salam field, Egypt",
    "gp_end": "Matrouh, Egypt",
    "reason": "overlap yellow 0.5172; status_conflict= diam=DELTA 38% len=DELTA 31%"
   }
  ]
 }
}

const REPO = A.repo
const STAGING = A.staging
const COMMODITY = A.commodity || 'gas'
const COUNTRY = A.country || 'Egypt'
// Resume 2026-07-13: only the PIDs whose rows/<PID>.json shard is not yet on disk (20/50 done previously).
const REMAINING = new Set(["P0474","P3932","P6037","P3934","P3343","P3346","P3366","P3659","P3929","P3930","P3931","P5132","P6032","P6033","P6034","P6036","P6689","P6697","P6698","P6699","P6700","P6701","P6702","P6704","P7447","P7567","P7572","P7574","P7580","P7588"])
const PIDS = A.pids.filter(p => REMAINING.has(p))
const ROSTER = (A.roster || []).join("\n")
const RC = A.routes_context || {}
const GULFPUB_GAS = A.gulfpub_gas_eg || ''
const GULFPUB_NOTE = A.gulfpub_note || ''
const XCONF = (A.gulfpub_status_conflicts || []).map(c => `  - GEM "${c.gem_name}" (${c.gem_status}) vs GulfPub "${c.gulfpub_name}" (${c.gp_status})`).join("\n")
const XWALK = A.pid_crosswalk || {}

const contract = (pid) => {
  const rc = RC[pid] || {}
  const xw = (XWALK[pid] || []).map(e => `    GulfPub "${e.gulfpub_name}" [${e.confidence} ${e.composite}] status=${e.gp_status} dia=${e.gp_dia} len_km=${e.gp_len_km} ${e.gp_start}->${e.gp_end} (${e.reason})`).join("\n") || "    (no confident GulfPub match auto-computed — search the GulfPub roster above yourself)"
  const routeBlock = `
## ROUTE (corridor + endpoints — REQUIRED for this row; RouteAccuracy = "${rc.route_accuracy || '?'}")
${(rc.route_accuracy==='high') ? 'This row already has a high-accuracy route; still confirm the named endpoints and note if GulfPub/independent sources disagree, but a full corridor re-derivation is optional.' : 'This row\'s geometry is weak (no route / low / medium). Do NOT edit any Route [ref] cell and do NOT touch the routes repo — instead RESEARCH and PROPOSE a corridor for a later human routes-repo branch.'}
Current sheet endpoints: start="${rc.start || ''}" end="${rc.end || ''}". RouteNotes="${(rc.route_notes||'').slice(0,200)}".
Establish the REAL endpoints (named facilities/fields/cities) and the corridor the line follows, with
independent sources. Give approximate lat/lon (decimal degrees, EPSG:4326) for each endpoint and any
key waypoint you can source. If you can only bound it loosely, say so and give the tightest corridor you
can defend. NEVER fabricate coordinates — leave lat/lon null and describe in words if unsourced.
Emit a "routes" array in the shard (schema below). This is a suggestion set, never an auto-applied route.`

  return `You are a meticulous, skeptical GEM pipeline researcher. Critically RE-AUDIT one ${COUNTRY}
${COMMODITY} OPERATING pipeline: ProjectID ${pid}. This is a deep-sweep validity pass — CONFIRM the
existing data and EXPOSE anything wrong, not rubber-stamp it. Baird expects some data to be wrong, some
pipelines to not exist, some to be duplicates or misclassified. Find those.

cd ${REPO} first.

## Inputs (ALWAYS START FROM THE SOURCES THE SHEET ALREADY CITES)
- Current GEM values + existing refs: \`${STAGING}/worklist.json\` -> load it, filter \`units\` to
  \`project_id == "${pid}"\`. Each unit has ref_col, value_cols, values, primary_value, current_ref,
  sheet_row, segment_name, pipeline_name, wiki.
- gem.wiki outbound citations for this row: \`${STAGING}/wiki_citations.json\` (STARTING POINT; verify
  each — many rot; READ gem.wiki for leads but NEVER cite it). A row whose only support is a generic
  citation not naming this pipeline is itself an existence flag.
- Roster of ALL ${PIDS.length} in-scope Egypt gas operating pipelines (duplicate/relabel detection —
  does ${pid} look like the same physical pipe as another row?):
${ROSTER}
- GulfPub PE World Map INDEPENDENT gas record for Egypt (Dec-2025 SDE scrape; use it to CORROBORATE
  specs/endpoints/operator AND to catch duplicates/relabels/misclassification). ${GULFPUB_NOTE}
  Auto-computed candidate match(es) for THIS row (fuzzy — verify, don't trust blindly):
${xw}
  Full GulfPub Saudi Arabia gas roster (search it for the real counterpart of this pipeline):
${GULFPUB_GAS}
- GEM-vs-GulfPub status disagreements auto-flagged in this country (fuzzy matches; adjudicate):
${XCONF}

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, A Barrel Full / any wikidot.com page.
   Read for leads only; url_verifier rejects them.
2. NEVER fabricate a URL or a coordinate. If you cannot verify, say so in researcher_notes.
3. Run EVERY url through the verifier before citing:
   \`python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"]\` -> cite only if OK/200
   AND contains the expected token(s). Use distinctive tokens (numbers, place names, Arabic forms).
4. Corroborate with >=2 INDEPENDENT sources (separate origins; not one wire story reprinted, not two
   pages tracing to GEM). tier: high = >=2 independent working+value-present; medium = 1 strong;
   low = 1 weak/partial/conflicting. Search Arabic + trade sources too (Egypt Oil & Gas / egyptoil-gas.com, Enterprise Press, MEES, Zawya, Al-Ahram, Daily News Egypt, Egypt Today, Offshore Technology/NS Energy, and official GASCO / EGAS / Petroleum Ministry pages). Watch ministry/operator press-release copy republished across outlets (not independent) and contractor-PR restatements.

## What to do, IN PRIORITY ORDER (existence + classification FIRST)
1. EXISTENCE — is this pipeline real? Independent evidence it physically exists. If the only traces are
   GEM-derived, or the cited source doesn't name it, or no independent confirmation -> verdict="concern",
   concern_type="existence".
2. CLASSIFICATION — correctly a GAS TRANSMISSION trunk (not gathering/process/feeder; not actually an
   oil/NGL/condensate line; not a plant-internal line)? Wrong -> concern_type="classification".
3. DUPLICATE — compare vs the roster AND the GulfPub list; if ${pid} is very likely the same physical
   pipe as another ProjectID (relabel / segment double-count; e.g. IGAT trunk segments), flag
   concern_type="duplicate" and NAME the other PID. Egypt's GASCO national-grid trunklines (Nile Delta,
   Western Desert, Cairo ring), Arab Gas Pipeline segments, and offshore field-to-shore lines entered
   under both field and landing names are prone to this.
4. ATTRIBUTION — owner/operator (GASCO vs EGAS vs the field-operator JV, e.g. Pharaonic/Petrobel/Burullus; note operator vs owner), FuelSource, governorate, endpoints.
   Wrong -> concern_type="attribution".
5. SPEC — length, diameter, capacity, dates. CRITICALLY confirm each vs >=2 independent sources; a page
   merely mentioning the line is NOT enough — sources must AGREE with the GEM number. GulfPub corroborates
   here (but its Capacity_mmcfd=300 is a placeholder, never a capacity). Material disagreement ->
   concern_type="spec", verdict="concern" (never silently pass).
Also DEEP-FILL genuinely blank value fields with a paired, verified ref (best-effort; don't force a
number on weak fields like Capacity).
${routeBlock}

A pipeline that is real and correctly classified but has a lesser caveat -> verdict="confirmed (caveat)".
Only open existence/duplicate/classification doubt -> verdict="concern".

## Output — write a shard, then return a summary
Write \`${STAGING}/rows/${pid}.json\` = a single JSON object EXACTLY shaped like:
{
  "project_id": "${pid}",
  "pipeline_name": "<from worklist>",
  "sheet_row": <int from worklist>,
  "wiki": "<gem.wiki url from worklist>",
  "validity": [
    { "segment_name": "<or empty>", "verdict": "confirmed (caveat)|concern",
      "concern_type": "existence|duplicate|classification|attribution|spec|none",
      "recommendation": "<short human next step>",
      "researcher_notes": "<full finding — what you checked, what the sheet's own sources say, what independent sources + GulfPub say vs GEM, your reasoning>",
      "proposed_refs": ["https://...verified..."], "tier": "high|medium|low",
      "independent": true, "source_language": "en|ar" }
  ],
  "fills": [
    { "segment_name": "<or empty>", "sheet_row": <int>, "ref_col": "Capacity [ref]",
      "value_cols": ["Capacity"], "primary_value_col": "Capacity", "values": {"Capacity": "<val>"},
      "primary_value": "<val>", "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
      "class_out": "REFS_ADDED|UNRESOLVED", "tier": "high|medium|low", "independent": true,
      "source_language": "en|ar", "researcher_notes": "<why this value / source>" }
  ],
  "routes": [
    { "segment_name": "<or empty>",
      "start_name": "<named start facility/field/city>", "start_lat": <dd or null>, "start_lon": <dd or null>,
      "end_name": "<named end facility/city>", "end_lat": <dd or null>, "end_lon": <dd or null>,
      "waypoints": [ {"name":"<place>", "lat": <dd or null>, "lon": <dd or null>} ],
      "corridor_desc": "<prose corridor: provinces/towns/features it passes, and how tight the bound is>",
      "current_route_accuracy": "${rc.route_accuracy || ''}",
      "suggested_route_accuracy": "high|medium|low (what the sourced corridor supports)",
      "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
      "tier": "high|medium|low", "source_language": "en|ar",
      "researcher_notes": "<how you established endpoints + corridor; note any fabrication avoided>" }
  ],
  "summary": "<one line>"
}
Emit >=1 validity object (use verdict="confirmed (caveat)", concern_type="none" if nothing wrong,
summarizing what you confirmed) and >=1 routes object (endpoints at minimum). All proposed_refs must have
passed url_verifier. Coordinates must be real (sourced or defensible from a named place), never invented —
null if unknown. Before finishing, run
\`python -c "import json; json.load(open('${STAGING}/rows/${pid}.json'))"\` to confirm it parses.
Return ONLY a 2-line summary: verdict/concern_types staged + suggested route accuracy, and any UNRESOLVED.
Your shard file is the deliverable, not your message.`
}

phase('Audit')
log(`Auditing ${PIDS.length} ${COUNTRY} ${COMMODITY} operating pipelines (existence+classification first, + corridor routes, + GulfPub gas corroboration), one subagent each.`)
const results = await parallel(PIDS.map(pid => () =>
  agent(contract(pid), { label: `audit:${pid}`, phase: 'Audit', agentType: 'general-purpose', model: 'sonnet' })
))
const done = results.filter(Boolean).length
log(`Audit complete: ${done}/${PIDS.length} subagents returned. Shards in ${STAGING}/rows/`)
