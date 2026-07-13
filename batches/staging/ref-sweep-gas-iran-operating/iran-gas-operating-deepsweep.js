export const meta = {
  name: 'iran-gas-operating-deepsweep',
  description: 'Iran gas OPERATING deep sweep: per-pipeline critical re-audit (existence/classification/duplicate/attribution/spec) + ref confirmation + blank-value fills + corridor/endpoint route suggestions, with GulfPub PE World Map gas corroboration context. Read-and-stage only.',
  phases: [ { title: 'Audit', detail: 'one subagent per operating gas pipeline' } ],
}

const A = {
 "repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher",
 "staging": "batches/staging/ref-sweep-gas-iran-operating",
 "commodity": "gas",
 "country": "Iran",
 "pids": [
  "P5984",
  "P0749",
  "P0748",
  "P1639",
  "P0742",
  "P0459",
  "P0442",
  "P0443",
  "P5855",
  "P0444",
  "P6026",
  "P0449",
  "P3949",
  "P2015",
  "P0446",
  "P0440",
  "P0445",
  "P0447",
  "P3950",
  "P3951",
  "P3957",
  "P6009",
  "P6021",
  "P6022",
  "P6023",
  "P6024",
  "P6025",
  "P6027",
  "P6028",
  "P6029",
  "P6030"
 ],
 "roster": [
  "P5984 | Rasht-Chelavend Gas Pipeline | ?->? | len=150.0 dia=42 cap=5.5 | status=operating | updated=2025-07-23",
  "P0749 | Korpeje-Kordkuy Gas Pipeline | Korpeje->Golestan | len=197.0 dia=1000 cap=8.0 | status=operating | updated=2024-08-29",
  "P0748 | Hajiqabul–Astara–Abadan Gas Pipeline | Gazimammad->Khuzestan | len=1474.5 dia=1020, 1200 cap=10.0 | status=operating | updated=2024-09-20",
  "P1639 | Sarakhs-Sari Pipeline | Sarakhs->? | len=795.0 dia=30, 36 cap=12.0 | status=operating | updated=2023-09-19",
  "P0742 | Dauletabad-Sarakhs-Khangiran Gas Pipeline | Dauletabad->Khorasan Khorasan Province | len=182.0 dia=48 cap=12.5 | status=operating | updated=2025-06-30",
  "P0459 | Tabriz-Ankara Gas Pipeline | Tabriz->? | len=2577.0 dia=40, 46 cap=14.0 | status=operating | updated=2025-07-07",
  "P0442 | IGAT 2 Gas Pipeline | Kangan Refinery->Qazvin | len=680.0 dia=56 cap=32.85 | status=operating | updated=2022-07-18",
  "P0443 | IGAT 3 Gas Pipeline | Asaluyeh->Markazi | len=1195.0 dia=56 cap=32.85 | status=operating | updated=2022-07-18",
  "P5855 | Iran-Iraq Gas Pipeline | ?->Diyala | len=? dia=? cap=35.0 | status=operating | updated=2023-09-18",
  "P0444 | IGAT 4 Gas Pipeline | Asaluyeh->Markazi | len=1145.0 dia=? cap=40.15 | status=operating | updated=2022-07-18",
  "P6026 | North–Northeast Gas Pipeline | ?->Tehran | len=35.0 dia=48 cap=204.0 | status=operating | updated=2023-09-19",
  "P0449 | Iran-Armenia Gas Pipeline | Tabriz->? | len=141.0 dia=700 cap=222.5 | status=operating | updated=2025-07-25",
  "P3949 | Siri–Asaluyeh Gas Pipeline | ?->Bushehr | len=289.0 dia=32.00 cap=500.0 | status=operating | updated=2022-09-16",
  "P2015 | IGAT 7 Gas Pipeline | ?->? | len=290.0 dia=? cap=1100.0 | status=operating | updated=2025-07-15",
  "P0446 | IGAT 7 Gas Pipeline | Asaluyeh->Sistan-Baluchistan | len=907.0 dia=56 cap=1800.0 | status=operating | updated=2025-07-14",
  "P0440 | IGAT 10 Gas Pipeline | Kangan->? | len=632.0 dia=? cap=2472.03 | status=operating | updated=2022-07-17",
  "P0445 | IGAT 6 Gas Pipeline | Asaluyeh->Khūzestān | len=600.0 dia=56 cap=3884.6 | status=operating | updated=2025-07-28",
  "P0447 | IGAT 8 Gas Pipeline | Parsian Refinery->Qom | len=1000.0 dia=56 cap=3884.6 | status=operating | updated=2024-02-27",
  "P3950 | Salman–Siri Gas Pipeline | Lavan Island->Hormozgan | len=147.0 dia=30.00 cap=? | status=operating | updated=2022-09-16",
  "P3951 | Siri–Mobarak Gas Pipeline | ?->Hormozgan | len=66.0 dia=30.00 cap=? | status=operating | updated=2022-09-16",
  "P3957 | IGAT 1 Gas Pipeline | ?->Gilan | len=1104.0 dia=42 cap=? | status=operating | updated=2022-09-16",
  "P6009 | Dizbad-Torbat Heydariyeh Gas Pipeline | ?->Razavi Khorasan | len=50.0 dia=12, 30 cap=? | status=operating | updated=2025-07-23",
  "P6021 | Torbat Heydariyeh–Kashmar Gas Pipeline | ?->Razavi Khorasan | len=? dia=12 cap=? | status=operating | updated=2023-09-19",
  "P6022 | Esfarayen–Neqab–Joghatai Gas Pipeline | ?->Razavi Khorasan | len=48.0 dia=30 cap=? | status=operating | updated=2023-09-19",
  "P6023 | Esfarayen–Neqab–Joghatai Gas Pipeline | ?->Razavi Khorasan | len=35.0 dia=20 cap=? | status=operating | updated=2023-09-19",
  "P6024 | Esfarayen Gas Pipeline | ?->? | len=? dia=10 cap=? | status=operating | updated=2023-09-19",
  "P6025 | Sabzevar Steel Plant Gas Pipeline | ?->Razavi Khorasan | len=3.5 dia=12 cap=? | status=operating | updated=2023-09-19",
  "P6027 | Kuh Sefid–Charmshahr Gas Pipeline | ?->Tehran | len=45.0 dia=56 cap=? | status=operating | updated=2023-09-19",
  "P6028 | Zahedan–Zabol Gas Pipeline | Zahedan->Sistan and Baluchestan | len=250.0 dia=? cap=? | status=operating | updated=2023-09-19",
  "P6029 | Kuhdasht–Pol-e-Dokhtar Gas Pipeline | ?->Lorestan | len=50.0 dia=12 cap=? | status=operating | updated=2023-09-19",
  "P6030 | Zarand–Ravar Gas Pipeline | ?->Kerman | len=106.0 dia=12,10 cap=? | status=operating | updated=2023-09-19"
 ],
 "routes_context": {
  "P5984": {
   "route_accuracy": "medium",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "map was copied from an IGAT 1 map and shortened accordingly"
  },
  "P0749": {
   "route_accuracy": "high",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "NF 8/29/24: Mapped with QGIS."
  },
  "P0748": {
   "route_accuracy": "high",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "NF 9/20/24: Mapped with QGIS. Updated the end of the route in geojson to end in Abadan."
  },
  "P1639": {
   "route_accuracy": "high",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Oil_natural_gas_infrastructure.png?1596730264763"
  },
  "P0742": {
   "route_accuracy": "high",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "NF 8/29/24: Mapped with QGIS."
  },
  "P0459": {
   "route_accuracy": "high",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "https://www.loc.gov/resource/g7421h.ct002142/?ciw=467&clip=3098,948,3608,1474&rot=0, https://4.bp.blogspot.com/-KAD3oMTUVRI/Wd2jqC60akI/AAAAAAAAIzc/N_EydhsmatgWaoKqIi9qAOWkEzAv5FIHwCLcBGAs/s640/Pipeline_Turkey-pipelines_TEKMOR.png, https://www.turkey-japan.com/business/category5/category5_404b.pdf"
  },
  "P0442": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "https://upload.wikimedia.org/wikipedia/commons/a/ae/CIAIranKarteOelGas.jpg?1596728405705"
  },
  "P0443": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "https://upload.wikimedia.org/wikipedia/commons/a/ae/CIAIranKarteOelGas.jpg?1596728405705"
  },
  "P5855": {
   "route_accuracy": "no route",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P0444": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Oil_natural_gas_infrastructure.png?1596730264763"
  },
  "P6026": {
   "route_accuracy": "medium",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P0449": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "https://drive.google.com/file/d/15MlsJ2awq8Zfjia7b9SBhHYCQzkbaPc9/view?usp=sharing"
  },
  "P3949": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P2015": {
   "route_accuracy": "no route",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P0446": {
   "route_accuracy": "high",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P0440": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "https://upload.wikimedia.org/wikipedia/commons/c/ce/Oil_natural_gas_infrastructure.png?1596730264763"
  },
  "P0445": {
   "route_accuracy": "high",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P0447": {
   "route_accuracy": "medium",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P3950": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "https://www.offshore-technology.com/projects/salman-oil-and-gas-field-persian-gulf/"
  },
  "P3951": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P3957": {
   "route_accuracy": "high",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "AL: re-mapped to improve accuracy"
  },
  "P6009": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P6021": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P6022": {
   "route_accuracy": "medium",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P6023": {
   "route_accuracy": "medium",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P6024": {
   "route_accuracy": "no route",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P6025": {
   "route_accuracy": "no route",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P6027": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P6028": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P6029": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  },
  "P6030": {
   "route_accuracy": "low",
   "start": "Asia",
   "end": "Asia",
   "route_notes": "nan"
  }
 },
 "gulfpub_gas_iran": "  - Mubarak - Sirri Island Pipeline | Operating | International | Mubarak field, offshore United Arab Emirates -> Sirri Island, Iran | op=National Iranian Oil Company [NIOC] dia=30.0 len_km=41.0\n  - IGAT 2 extension | Operating | National | Qazvin, Iran -> Tabriz, Iran | op=National Iranian Oil Company [NIOC] dia=48.0 len_km=274.0\n  - IGAT 8 | Operating | National | Assaluyeh, Iran -> Qom, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=642.0\n  - Iran - Kuwait Offshore Pipeline | Non operational | International | Ganaveh, Iran -> Al Zour, Kuwait | op=National Iranian Oil Company [NIOC] dia=16.0 len_km=138.0\n  - Sarkhun - Kerman | Operating | National | Sarkhun Gas Refinery (Bandar Abbas), Iran -> Rafsanjan, Iran | op=National Iranian Gas Company (NIGC) dia=24.0 len_km=243.0\n  - Minab - Sirik Pipeline | Operating | National | Minab (IGAT 7 pipeline), Iran -> Sirik, Iran | op=National Iranian Oil Company [NIOC] dia=42.0 len_km=75.0\n  - Salman - Sirri Island Pipeline | Operating | National | Salman field, offshore Iran -> Sirri Island, Iran | op=National Iranian Oil Company [NIOC] dia=30.0 len_km=91.0\n  - Iranshahr to Chabahar Gas Pipeline | Operating | National | Iranshahr, Iran -> Chabahar, Iran | op=Mokran Gas Transmission Pipeline Company dia=56.0 len_km=180.0\n  - Salakh - Bandar Abbas Pipeline | Operating | National | Salakh field, Qeshm Island, Iran -> Bandar Abbas, Iran | op=National Iranian Oil Company [NIOC] dia=16.0 len_km=51.0\n  - Sirri D - Sirri Island Line | Operating | National | Sirri D field, offshore Iran -> Sirri Island, Iran | op=National Iranian Oil Company [NIOC] dia=16.0 len_km=20.0\n  - IGAT 7 | Operating | National | Assaluyeh, Iran -> Iranshahr, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=563.0\n  - IGAT 2 | Operating | National | Kangan NG Refinery, Iran -> Qazvin, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=640.0\n  - Sarakhs - Mashad - Neka  - Rasht | Operating | National | Sarakhs, Iran -> Rasht, Iran | op=National Iranian Oil Company [NIOC] dia=36.0 len_km=735.0\n  - IGAT 5 | Operating | National | Assaluyeh, Iran -> Aghajari, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=313.0\n  - Shiraz - Bid Boland Pipeline | Operating | National | Shiraz, Iran -> Bid Boland Refinery, Iran | op=National Iranian Oil Company [NIOC] dia=16.0 len_km=200.0\n  - IGAT 6 | Operating | National | Assaluyeh, Iran -> Khuzestan Province, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=311.0\n  - IGAT 4 | Operating | National | Assaluyeh, Iran -> Shiraz, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=720.0\n  - Parsi - Bandar-e-Mahshahr Pipeline | Operating | National | Parsi field, Iran -> Bandar-e-Mahshahr, Iran | op=National Iranian Oil Company [NIOC] dia=16.0 len_km=56.0\n  - Tabriz - Bazargan Pipeline  | Planned | National | Tabriz, Iran -> Bazargan, Iran | op=National Iranian Oil Company [NIOC] dia=40.0 len_km=157.0\n  - Dauletabad - Sarakhs Loop | Operating | National | Dauletabad - Sarakhs - Khangiram Pipeline -> Sarakhs - Mashad - Neka - Rasht Pipeline | op=National Iranian Oil Company [NIOC] dia=16.0 len_km=76.0\n  - Iran - Armenia | Operating | International | Tabriz, Iran -> Ararat, Armenia | op=National Iranian Oil Company [NIOC] dia=30.0 len_km=87.0\n  - Astara - Tabriz | Operating | National | Astara, Iran -> Tabriz, Iran | op=National Iranian Oil Company [NIOC] dia=30.0 len_km=172.0\n  - Dauletabad - Sarakhs - Khangiram | Operating | International | Dauletabad field, Turkmenistan -> Khangiram, Iran | op=Turkmengaz dia=48.0 len_km=113.0\n  - IGAT 9 | Operating | National | Ahwaz, Iran -> Bazargan, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=775.0\n  - Bandar Mahshahr - Abadan Pipeline | Operating | National | Bandar-e-Mahshahr, Iran -> Abadan, Iran | op=National Iranian Oil Company [NIOC] dia=16.0 len_km=60.0\n  - Southwest Ramhormoz Pipeline | Operating | National | Southwest Ramhormoz -> near Ahwaz - Bid Boland Pipeline | op=National Iranian Oil Company [NIOC] dia=16.0 len_km=6.0\n  - Hamadan - Arak Pipeline | Operating | National | Hamadan, Iran -> Arak, Iran | op=National Iranian Oil Company [NIOC] dia=30.0 len_km=171.0\n  - Malayer - Kermanshah | Operating | National | Malayer, Iran -> Kermanshah, Iran | op=National Iranian Oil Company [NIOC] dia=20.0 len_km=160.0\n  - Kish - IGAT 7 | Operating | National | Kish field, offshore Iran -> IGAT 7 Pipeline | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=58.0\n  - Sirri Island - Bandar Abbas Pipeline | Planned | National | Sirri Island, Iran -> Bandar Abbas, Iran | op=National Iranian Oil Company [NIOC] dia=16.0 len_km=138.0\n  - Iranshahr - Zahedan Gas Pipeline | Operating | National | Iranshahr, Iran -> Zahedan, Iran | op=National Iranian Gas Company (NIGC) dia=36.0 len_km=174.0\n  - Ahwaz - Bid Boland Pipeline | Operating | National | Ahwaz, Iran -> Bid Boland Refinery, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=73.0\n  - Saveh - Shahtyar | Operating | National | Saveh, Iran -> Shahtyar, Iran | op=National Iranian Oil Company [NIOC] dia=48.0 len_km=53.0\n  - IGAT 1 | Operating | National | Bid Boland Refinery, Iran -> Astara, Iran | op=National Iranian Oil Company [NIOC] dia=42.0 len_km=685.0\n  - IGAT 1 | Operating | National | Qazvin, Iran -> Astara, Iran | op=National Iranian Oil Company [NIOC] dia=42.0 len_km=250.0\n  - IGAT 4 | Operating | National | Assaluyeh, Iran -> Esfahan, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=720.0\n  - IGAT 3 | Operating | National | Assaluyeh, Iran -> Saveh, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=573.0\n  - Tabriz - Bazargan Pipeline  | Operating | National | Tabriz, Iran -> Bazargan, Iran | op=National Iranian Oil Company [NIOC] dia=40.0 len_km=157.0\n  - Hamadan - Sanandaj | Operating | National | Hamadan, Iran -> Sanandaj, Iran | op=National Iranian Oil Company [NIOC] dia=20.0 len_km=101.0\n  - Neka - Damghan | Operating | National | Neka, Iran -> Damghan, Iran | op=National Iranian Oil Company [NIOC] dia=16.0 len_km=65.0\n  - Korpezhe - Kord Kuy | Operating | International | Korpezhe, Turkmenistan -> Kord Kuy, Iran | op=Turkmengaz dia=40.0 len_km=120.0\n  - IGAT 10 | Operating | National | Bushehr Province, Iran -> \tSaveh, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=393.0\n  - IGAT 11 | Under construction | National | Assaluyeh, Iran -> Bazargan, Iran | op=National Iranian Oil Company [NIOC] dia=56.0 len_km=748.0\n  - Iran - Oman Gas Project | Planned | International | Kuh Mobarak, Iran -> Sohar, Oman | op=National Iranian Oil Company [NIOC] dia=16.0 len_km=112.0\n  - Sirik - Kuh Mobarak Pipeline | Under construction | National | Sirik, Iran -> Kuh Mobarek, Iran | op=National Iranian Oil Company [NIOC] dia=42.0 len_km=50.0\n  - Iranshahr to Chabahar Gas Pipeline [Spur] | Operating | National | Chabahar, Iran -> Konarak, Iran | op=Mokran Gas Transmission Pipeline Company dia=20.0 len_km=12.0\n  - Southern Arm (Sistan & Baluchestan Supply) Pakistan Link | Non operational | National | Zahedan, Iran -> Border, Pakistan | op=National Iranian Gas Company (NIGC) dia=36.0 len_km=30.0\n  - Sarkhun - Kerman | Operating | National | Rafsanjan, Iran -> Kerman, Iran | op=National Iranian Gas Company (NIGC) dia=14.0 len_km=50.0\n  - Sarkhun - Kerman | Operating | National | Rafsanjan, Iran -> Anar, Iran | op=National Iranian Gas Company (NIGC) dia=12.0 len_km=60.0",
 "gulfpub_note": "GulfPub PE World Map (SDE Dec-2025 scrape) DOES cover Iran gas (49 features incl. IGAT 1-9, cross-border, offshore). Use it to corroborate specs AND catch duplicates/relabels/misclassification. Name-matching in pid_crosswalk is fuzzy (e.g. IGAT numbers cross-paired) — treat as a lead, verify. Capacity_mmcfd is a constant 300 placeholder, NEVER a real capacity.",
 "gulfpub_status_conflicts": [
  {
   "gem_name": "IGAT 9 Gas Pipeline",
   "gem_status": "construction",
   "gulfpub_name": "IGAT 8",
   "gp_status": "operating"
  },
  {
   "gem_name": "IGAT 7 Gas Pipeline",
   "gem_status": "operating",
   "gulfpub_name": "Tabriz - Bazargan Pipeline",
   "gp_status": "proposed"
  },
  {
   "gem_name": "Dauletabad-Sarakhs-Khangiran Gas Pipeline",
   "gem_status": "proposed",
   "gulfpub_name": "Dauletabad - Sarakhs Loop",
   "gp_status": "operating"
  },
  {
   "gem_name": "IGAT 9 Gas Pipeline",
   "gem_status": "construction",
   "gulfpub_name": "IGAT 9",
   "gp_status": "operating"
  },
  {
   "gem_name": "Iran-Iraq Gas Pipeline",
   "gem_status": "operating",
   "gulfpub_name": "Sirri Island - Bandar Abbas Pipeline",
   "gp_status": "proposed"
  },
  {
   "gem_name": "IGAT 9 Gas Pipeline",
   "gem_status": "construction",
   "gulfpub_name": "IGAT 4",
   "gp_status": "operating"
  },
  {
   "gem_name": "Iran-Iraq Gas Pipeline",
   "gem_status": "operating",
   "gulfpub_name": "Sirik - Kuh Mobarak Pipeline",
   "gp_status": "construction"
  }
 ],
 "pid_crosswalk": {
  "P2015": [
   {
    "gulfpub_name": "IGAT 2 extension",
    "gp_status": "operating",
    "gp_dia": "48.0",
    "gp_len_km": 274.0,
    "gp_start": "Qazvin, Iran",
    "gp_end": "Tabriz, Iran",
    "confidence": "yellow",
    "composite": 0.5882,
    "reason": "name 0.56; length 0.67"
   },
   {
    "gulfpub_name": "Sarkhun - Kerman",
    "gp_status": "operating",
    "gp_dia": "24.0",
    "gp_len_km": 243.0,
    "gp_start": "Sarkhun Gas Refinery (Bandar Abbas), Iran",
    "gp_end": "Rafsanjan, Iran",
    "confidence": "yellow",
    "composite": 0.5135,
    "reason": "name 0.43; length 0.75"
   },
   {
    "gulfpub_name": "Iranshahr to Chabahar Gas Pipeline",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 180.0,
    "gp_start": "Iranshahr, Iran",
    "gp_end": "Chabahar, Iran",
    "confidence": "green",
    "composite": 0.8083,
    "reason": "name 0.77; length 0.91"
   },
   {
    "gulfpub_name": "IGAT 7",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 563.0,
    "gp_start": "Assaluyeh, Iran",
    "gp_end": "Iranshahr, Iran",
    "confidence": "green",
    "composite": 0.8332,
    "reason": "name 1.00; length 0.33"
   },
   {
    "gulfpub_name": "IGAT 5",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 313.0,
    "gp_start": "Assaluyeh, Iran",
    "gp_end": "Aghajari, Iran",
    "confidence": "green",
    "composite": 0.7535,
    "reason": "name 0.80; length 0.61"
   },
   {
    "gulfpub_name": "Shiraz - Bid Boland Pipeline",
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 200.0,
    "gp_start": "Shiraz, Iran",
    "gp_end": "Bid Boland Refinery, Iran",
    "confidence": "yellow",
    "composite": 0.7127,
    "reason": "name 0.62; length 0.98"
   },
   {
    "gulfpub_name": "IGAT 6",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 311.0,
    "gp_start": "Assaluyeh, Iran",
    "gp_end": "Khuzestan Province, Iran",
    "confidence": "green",
    "composite": 0.767,
    "reason": "name 0.80; length 0.67"
   },
   {
    "gulfpub_name": "IGAT 4",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 720.0,
    "gp_start": "Assaluyeh, Iran",
    "gp_end": "Shiraz, Iran",
    "confidence": "green",
    "composite": 0.8427,
    "reason": "name 0.80; length 0.97"
   },
   {
    "gulfpub_name": "Tabriz - Bazargan Pipeline",
    "gp_status": "proposed",
    "gp_dia": "40.0",
    "gp_len_km": 157.0,
    "gp_start": "Tabriz, Iran",
    "gp_end": "Bazargan, Iran",
    "confidence": "yellow",
    "composite": 0.673,
    "reason": "name 0.60; length 0.88"
   },
   {
    "gulfpub_name": "Astara - Tabriz",
    "gp_status": "operating",
    "gp_dia": "30.0",
    "gp_len_km": 172.0,
    "gp_start": "Astara, Iran",
    "gp_end": "Tabriz, Iran",
    "confidence": "yellow",
    "composite": 0.5792,
    "reason": "name 0.48; length 0.86"
   },
   {
    "gulfpub_name": "Malayer - Kermanshah",
    "gp_status": "operating",
    "gp_dia": "20.0",
    "gp_len_km": 160.0,
    "gp_start": "Malayer, Iran",
    "gp_end": "Kermanshah, Iran",
    "confidence": "yellow",
    "composite": 0.455,
    "reason": "name 0.32; length 0.85"
   },
   {
    "gulfpub_name": "Kish - IGAT 7",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 58.0,
    "gp_start": "Kish field, offshore Iran",
    "gp_end": "IGAT 7 Pipeline",
    "confidence": "yellow",
    "composite": 0.566,
    "reason": "name 0.71; length 0.15"
   },
   {
    "gulfpub_name": "Iranshahr - Zahedan Gas Pipeline",
    "gp_status": "operating",
    "gp_dia": "36.0",
    "gp_len_km": 174.0,
    "gp_start": "Iranshahr, Iran",
    "gp_end": "Zahedan, Iran",
    "confidence": "green",
    "composite": 0.826,
    "reason": "name 0.77; length 0.98"
   },
   {
    "gulfpub_name": "IGAT 1",
    "gp_status": "operating",
    "gp_dia": "42.0",
    "gp_len_km": 250.0,
    "gp_start": "Qazvin, Iran",
    "gp_end": "Astara, Iran",
    "confidence": "green",
    "composite": 0.8265,
    "reason": "name 0.80; length 0.91"
   },
   {
    "gulfpub_name": "Tabriz - Bazargan Pipeline",
    "gp_status": "operating",
    "gp_dia": "40.0",
    "gp_len_km": 157.0,
    "gp_start": "Tabriz, Iran",
    "gp_end": "Bazargan, Iran",
    "confidence": "yellow",
    "composite": 0.6732,
    "reason": "name 0.60; length 0.88"
   }
  ],
  "P0448": [
   {
    "gulfpub_name": "IGAT 8",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 642.0,
    "gp_start": "Assaluyeh, Iran",
    "gp_end": "Qom, Iran",
    "confidence": "yellow",
    "composite": 0.7276,
    "reason": "name 0.80; endpoints 0.55; diameter ✓; length 0.54"
   },
   {
    "gulfpub_name": "IGAT 9",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 775.0,
    "gp_start": "Ahwaz, Iran",
    "gp_end": "Bazargan, Iran",
    "confidence": "yellow",
    "composite": 0.6814,
    "reason": "name 1.00; endpoints 0.61; diameter ✓; length 0.63; route IoU 0.009"
   },
   {
    "gulfpub_name": "IGAT 4",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 720.0,
    "gp_start": "Assaluyeh, Iran",
    "gp_end": "Esfahan, Iran",
    "confidence": "yellow",
    "composite": 0.7486,
    "reason": "name 0.80; endpoints 0.61; diameter ✓; length 0.55"
   }
  ],
  "P5855": [
   {
    "gulfpub_name": "Minab - Sirik Pipeline",
    "gp_status": "operating",
    "gp_dia": "42.0",
    "gp_len_km": 75.0,
    "gp_start": "Minab (IGAT 7 pipeline), Iran",
    "gp_end": "Sirik, Iran",
    "confidence": "yellow",
    "composite": 0.667,
    "reason": "name 0.67"
   },
   {
    "gulfpub_name": "Salakh - Bandar Abbas Pipeline",
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 51.0,
    "gp_start": "Salakh field, Qeshm Island, Iran",
    "gp_end": "Bandar Abbas, Iran",
    "confidence": "yellow",
    "composite": 0.64,
    "reason": "name 0.64"
   },
   {
    "gulfpub_name": "Parsi - Bandar-e-Mahshahr Pipeline",
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 56.0,
    "gp_start": "Parsi field, Iran",
    "gp_end": "Bandar-e-Mahshahr, Iran",
    "confidence": "yellow",
    "composite": 0.533,
    "reason": "name 0.53"
   },
   {
    "gulfpub_name": "Bandar Mahshahr - Abadan Pipeline",
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 60.0,
    "gp_start": "Bandar-e-Mahshahr, Iran",
    "gp_end": "Abadan, Iran",
    "confidence": "yellow",
    "composite": 0.566,
    "reason": "name 0.57"
   },
   {
    "gulfpub_name": "Southwest Ramhormoz Pipeline",
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 6.0,
    "gp_start": "Southwest Ramhormoz",
    "gp_end": "near Ahwaz - Bid Boland Pipeline",
    "confidence": "yellow",
    "composite": 0.533,
    "reason": "name 0.53"
   },
   {
    "gulfpub_name": "Hamadan - Arak Pipeline",
    "gp_status": "operating",
    "gp_dia": "30.0",
    "gp_len_km": 171.0,
    "gp_start": "Hamadan, Iran",
    "gp_end": "Arak, Iran",
    "confidence": "yellow",
    "composite": 0.651,
    "reason": "name 0.65"
   },
   {
    "gulfpub_name": "Sirri Island - Bandar Abbas Pipeline",
    "gp_status": "proposed",
    "gp_dia": "16.0",
    "gp_len_km": 138.0,
    "gp_start": "Sirri Island, Iran",
    "gp_end": "Bandar Abbas, Iran",
    "confidence": "yellow",
    "composite": 0.643,
    "reason": "name 0.64"
   },
   {
    "gulfpub_name": "Ahwaz - Bid Boland Pipeline",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 73.0,
    "gp_start": "Ahwaz, Iran",
    "gp_end": "Bid Boland Refinery, Iran",
    "confidence": "yellow",
    "composite": 0.596,
    "reason": "name 0.60"
   },
   {
    "gulfpub_name": "Sirik - Kuh Mobarak Pipeline",
    "gp_status": "construction",
    "gp_dia": "42.0",
    "gp_len_km": 50.0,
    "gp_start": "Sirik, Iran",
    "gp_end": "Kuh Mobarek, Iran",
    "confidence": "yellow",
    "composite": 0.625,
    "reason": "name 0.62"
   },
   {
    "gulfpub_name": "Iranshahr to Chabahar Gas Pipeline [Spur]",
    "gp_status": "operating",
    "gp_dia": "20.0",
    "gp_len_km": 12.0,
    "gp_start": "Chabahar, Iran",
    "gp_end": "Konarak, Iran",
    "confidence": "yellow",
    "composite": 0.706,
    "reason": "name 0.71"
   }
  ],
  "P3950": [
   {
    "gulfpub_name": "Salman - Sirri Island Pipeline",
    "gp_status": "operating",
    "gp_dia": "30.0",
    "gp_len_km": 91.0,
    "gp_start": "Salman field, offshore Iran",
    "gp_end": "Sirri Island, Iran",
    "confidence": "yellow",
    "composite": 0.6703,
    "reason": "name 0.85; endpoints 0.60; diameter ✓; length 0.96; route IoU 0.005"
   }
  ],
  "P0442": [
   {
    "gulfpub_name": "IGAT 2",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 640.0,
    "gp_start": "Kangan NG Refinery, Iran",
    "gp_end": "Qazvin, Iran",
    "confidence": "green",
    "composite": 0.7794,
    "reason": "name 1.00; endpoints 1.00; diameter ✓; length 0.63; route IoU 0.014"
   },
   {
    "gulfpub_name": "IGAT 10",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 393.0,
    "gp_start": "Bushehr Province, Iran",
    "gp_end": "Saveh, Iran",
    "confidence": "yellow",
    "composite": 0.6787,
    "reason": "name 0.73; endpoints 0.32; diameter ✓; length 0.95"
   }
  ],
  "P1639": [
   {
    "gulfpub_name": "Sarakhs - Mashad - Neka  - Rasht",
    "gp_status": "operating",
    "gp_dia": "36.0",
    "gp_len_km": 735.0,
    "gp_start": "Sarakhs, Iran",
    "gp_end": "Rasht, Iran",
    "confidence": "yellow",
    "composite": 0.5501,
    "reason": "name 0.52; endpoints 0.64; diameter ✓; length 0.67; route IoU 0.022"
   }
  ],
  "P6848": [
   {
    "gulfpub_name": "Dauletabad - Sarakhs Loop",
    "gp_status": "operating",
    "gp_dia": "16.0",
    "gp_len_km": 76.0,
    "gp_start": "Dauletabad - Sarakhs - Khangiram Pipeline",
    "gp_end": "Sarakhs - Mashad - Neka - Rasht Pipeline",
    "confidence": "yellow",
    "composite": 0.6016,
    "reason": "name 0.88; endpoints 0.64; length 0.79; route IoU 0.0"
   }
  ],
  "P3957": [
   {
    "gulfpub_name": "IGAT 1",
    "gp_status": "operating",
    "gp_dia": "42.0",
    "gp_len_km": 685.0,
    "gp_start": "Bid Boland Refinery, Iran",
    "gp_end": "Astara, Iran",
    "confidence": "green",
    "composite": 0.7581,
    "reason": "name 1.00; diameter ✓; length 0.97; route IoU 0.054"
   }
  ],
  "P0443": [
   {
    "gulfpub_name": "IGAT 3",
    "gp_status": "operating",
    "gp_dia": "56.0",
    "gp_len_km": 573.0,
    "gp_start": "Assaluyeh, Iran",
    "gp_end": "Saveh, Iran",
    "confidence": "green",
    "composite": 0.7716,
    "reason": "name 1.00; endpoints 0.86; diameter ✓; length 0.85; route IoU 0.03"
   }
  ],
  "P0441": [
   {
    "gulfpub_name": "IGAT 11",
    "gp_status": "construction",
    "gp_dia": "56.0",
    "gp_len_km": 748.0,
    "gp_start": "Assaluyeh, Iran",
    "gp_end": "Bazargan, Iran",
    "confidence": "green",
    "composite": 0.7638,
    "reason": "name 1.00; endpoints 0.86; diameter ✓; length 0.67; route IoU 0.018"
   }
  ]
 }
}

const REPO = A.repo
const STAGING = A.staging
const COMMODITY = A.commodity || 'gas'
const COUNTRY = A.country || 'Iran'
const PIDS = A.pids
const ROSTER = (A.roster || []).join("\n")
const RC = A.routes_context || {}
const GULFPUB_GAS = A.gulfpub_gas_iran || ''
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
- Roster of ALL ${PIDS.length} in-scope Iran gas operating pipelines (duplicate/relabel detection —
  does ${pid} look like the same physical pipe as another row?):
${ROSTER}
- GulfPub PE World Map INDEPENDENT gas record for Iran (Dec-2025 SDE scrape; use it to CORROBORATE
  specs/endpoints/operator AND to catch duplicates/relabels/misclassification). ${GULFPUB_NOTE}
  Auto-computed candidate match(es) for THIS row (fuzzy — verify, don't trust blindly):
${xw}
  Full GulfPub Iran gas roster (search it for the real counterpart of this pipeline):
${GULFPUB_GAS}
- GEM-vs-GulfPub status disagreements auto-flagged in this country (fuzzy matches; adjudicate):
${XCONF}

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, A Barrel Full / any wikidot.com page.
   Read for leads only; url_verifier rejects them.
2. NEVER fabricate a URL or a coordinate. If you cannot verify, say so in researcher_notes.
3. Run EVERY url through the verifier before citing:
   \`python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"]\` -> cite only if OK/200
   AND contains the expected token(s). Use distinctive tokens (numbers, place names, Persian forms).
4. Corroborate with >=2 INDEPENDENT sources (separate origins; not one wire story reprinted, not two
   pages tracing to GEM). tier: high = >=2 independent working+value-present; medium = 1 strong;
   low = 1 weak/partial/conflicting. Search Persian/Farsi sources too (Shana, Mehr, Tehran Times, NIGC,
   NIOC). Watch sanctions-era renaming and republished wire copy (not independent).

## What to do, IN PRIORITY ORDER (existence + classification FIRST)
1. EXISTENCE — is this pipeline real? Independent evidence it physically exists. If the only traces are
   GEM-derived, or the cited source doesn't name it, or no independent confirmation -> verdict="concern",
   concern_type="existence".
2. CLASSIFICATION — correctly a GAS TRANSMISSION trunk (not gathering/process/feeder; not actually an
   oil/NGL/condensate line; not a plant-internal line)? Wrong -> concern_type="classification".
3. DUPLICATE — compare vs the roster AND the GulfPub list; if ${pid} is very likely the same physical
   pipe as another ProjectID (relabel / segment double-count; e.g. IGAT trunk segments), flag
   concern_type="duplicate" and NAME the other PID. Iran's IGAT trunk series is prone to this.
4. ATTRIBUTION — owner/operator (NIGC vs NIOC vs a subsidiary), FuelSource, province, endpoints.
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
      "independent": true, "source_language": "en|fa" }
  ],
  "fills": [
    { "segment_name": "<or empty>", "sheet_row": <int>, "ref_col": "Capacity [ref]",
      "value_cols": ["Capacity"], "primary_value_col": "Capacity", "values": {"Capacity": "<val>"},
      "primary_value": "<val>", "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
      "class_out": "REFS_ADDED|UNRESOLVED", "tier": "high|medium|low", "independent": true,
      "source_language": "en|fa", "researcher_notes": "<why this value / source>" }
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
      "tier": "high|medium|low", "source_language": "en|fa",
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
  agent(contract(pid), { label: `audit:${pid}`, phase: 'Audit', agentType: 'general-purpose' })
))
const done = results.filter(Boolean).length
log(`Audit complete: ${done}/${PIDS.length} subagents returned. Shards in ${STAGING}/rows/`)
