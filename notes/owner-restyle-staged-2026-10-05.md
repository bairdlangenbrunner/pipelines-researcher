# Owner and operator spellings in pending staged work, restyled 2026-10-05

Mode: APPLIED. Sheet snapshot: `GEM_operators_owners_snapshot_20261005.csv`.

Every pending staging dir was read. A proposed Owner or Operator value that differs from the sheet's current cell was run through the styler; the ones the policy allows (an exact gazetteer hit, a confirmed alias, a ruling, or a rules result with only mechanical flags) were rewritten, with the source's spelling kept in the researcher notes. The rest were left as they were and are listed below for a person.

- cells rewritten: 403 (201 in staged_resolutions.json files, the rest in shard rows)
- distinct re-spellings: 105
- cells left as they were (a judgment, not a spelling): 32 — acronym_not_initials 16, fuzzy_candidates 10, alias_candidate 6
- proposed values equal to the sheet (carried, not touched): 3654

## Rewritten, by staging dir

- `batches/india-gas/staging/qc`: 48
- `batches/united-states-gas/staging/deepsweep-gulf-operating`: 44
- `batches/united-states-gas/staging/deepsweep-remainder`: 38
- `batches/united-states-gas/staging/deepsweep-west-operating`: 37
- `batches/united-states-gas/staging/deepsweep-appalachian-operating`: 28
- `batches/united-states-gas/staging/deepsweep-s2-gulf-indev`: 24
- `batches/united-states-gas/staging/deepsweep-s2-tx-midcon-operating`: 23
- `batches/united-states-gas/staging/deepsweep-s2-west`: 22
- `batches/libya-gas/staging/qc`: 18
- `batches/united-states-gas/staging/deepsweep-s2-appalachian-indev`: 18
- `batches/united-states-gas/staging/deepsweep-s2-gulf-se-operating`: 18
- `batches/united-states-gas/staging/deepsweep-s2-northeast-alaska`: 18
- `batches/united-states-gas/staging/qc`: 18
- `batches/iran-gas/staging/ref-sweep-operating`: 15
- `batches/russia-gas/staging/deepsweep-r3-nw-indev`: 6
- `batches/iraq-gas/staging/ref-sweep-operating`: 5
- `batches/iran-gas/staging/annual`: 4
- `batches/saudi-arabia-gas/staging/ref-sweep-critical`: 3
- `batches/saudi-arabia-gas/staging/ref-sweep-operating`: 3
- `batches/egypt-gas/staging/qc`: 2
- `batches/egypt-gas/staging/ref-sweep-operating`: 2
- `batches/egypt-oil/staging/ref-sweep-all`: 2
- `batches/india-gas/staging/annual`: 2
- `batches/kazakhstan-gas/staging/cancelled-review`: 2
- `batches/malaysia-gas/staging/qc`: 2
- `batches/saudi-arabia-gas/staging/ref-sweep`: 1

## Re-spellings (cells)

- 'GAIL (India) Ltd' -> 'GAIL Ltd' (44)
- 'Energy Transfer' -> 'Energy Transfer LP' (22)
- 'Targa Resources' -> 'Targa Resources Corp' (20)
- 'Kinder Morgan' -> 'Kinder Morgan Inc' (14)
- 'Iran Ministry of Petroleum' -> 'Ministry of Petroleum (Iran)' (13)
- 'Mellitah Oil & Gas B.V.' -> 'Mellitah Oil & Gas BV' (10)
- 'Florida Gas Transmission Company, LLC' -> 'Florida Gas Transmission Company LLC' (10)
- 'Sirte Oil' -> 'Sirte Oil Co' (8)
- 'National Iranian Gas Company (NIGC)' -> 'National Iranian Gas Co' (6)
- 'Gazprom' -> 'Gazprom PJSC' (6)
- 'Enbridge Inc.' -> 'Enbridge Inc' (6)
- 'DT Midstream' -> 'DT Midstream Inc' (6)
- 'Florida Gas Transmission, LLC' -> 'Florida Gas Transmission LLC' (6)
- 'Tennessee Gas Pipeline Company, L.L.C.' -> 'Tennessee Gas Pipeline Company LLC' (6)
- 'Kinder Morgan, Inc.' -> 'Kinder Morgan Inc' (6)
- 'Columbia Gas of Ohio, Inc.' -> 'Columbia Gas of Ohio Inc' (6)
- 'Columbia Gulf Transmission, LLC' -> 'Columbia Gulf Transmission LLC' (6)
- 'TC Energy' -> 'TC Energy Corp' (6)
- 'Aramco' -> 'Saudi Arabian Oil Co' (5)
- 'Transcontinental Gas Pipe Line Company, LLC' -> 'Transcontinental Gas Pipe Line Company LLC' (5)
- 'Nile Valley Gas Company' -> 'Nile Valley Gas Co' (4)
- 'Iraq Ministry of Oil' -> 'Ministry of Oil (Iraq)' (4)
- 'Eastern Gas Transmission and Storage, Inc.' -> 'Eastern Gas Transmission and Storage Inc' (4)
- 'Enstor Pipeline Holdings, LLC' -> 'Enstor Pipeline Holdings LLC' (4)
- 'Mountain Valley Pipeline, LLC' -> 'Mountain Valley Pipeline LLC' (4)
- 'Sabine Crossing Pipeline, LLC' -> 'Sabine Crossing Pipeline LLC' (4)
- 'CE Pipeline, LLC' -> 'CE Pipeline LLC' (4)
- 'Gulf Run Transmission, LLC' -> 'Gulf Run Transmission LLC' (4)
- 'Texas Eastern Transmission, LP' -> 'Texas Eastern Transmission LP' (4)
- 'Great Basin Gas Transmission Company' -> 'Great Basin Gas Transmission Co' (4)
- 'Southwest Gas Corporation' -> 'Southwest Gas Corp' (4)
- 'EnLink Midstream' -> 'EnLink Midstream LLC' (3)
- 'Enbridge' -> 'Enbridge Inc' (3)
- 'WBI Energy Transmission, Inc.' -> 'WBI Energy Transmission Inc' (3)
- 'Valley Crossing Pipeline, LLC' -> 'Valley Crossing Pipeline LLC' (3)
- 'Petroleum Pipeline Company(PPC)' -> 'Petroleum Pipeline Co' (2)
- 'Oil and Natural Gas Corp Ltd (ONGC)' -> 'Oil and Natural Gas Corp Ltd' (2)
- 'ONGC Petro Additions Ltd' -> 'ONGC Petro additions Ltd' (2)
- 'GSPL India Gasnet Ltd (GIGL)' -> 'GSPL India Gasnet Ltd' (2)
- 'Uzbekneftegaz' -> 'Uzbekneftegaz JSC' (2)
- 'PETRONAS Carigali Sdn Bhd' -> 'Petronas Carigali Sdn Bhd' (2)
- 'Saudi Aramco' -> 'Saudi Arabian Oil Co' (2)
- 'Eastern Shore Natural Gas Company' -> 'Eastern Shore Natural Gas Co' (2)
- 'Iroquois Pipeline Operating Company' -> 'Iroquois Pipeline Operating Co' (2)
- 'TC Energy Corporation' -> 'TC Energy Corp' (2)
- 'Duke Energy Ohio' -> 'Duke Energy Ohio Inc' (2)
- 'New York State Electric and Gas Corporation' -> 'New York State Electric and Gas Corp' (2)
- 'Dominion Transmission, Inc.' -> 'Dominion Transmission Inc' (2)
- 'Vector Pipeline L.P.' -> 'Vector Pipeline LP' (2)
- 'Eastern Gas Transmission & Storage, Inc.' -> 'Eastern Gas Transmission & Storage Inc' (2)
- 'Chandeleur Pipe Line, LLC' -> 'Chandeleur Pipe Line LLC' (2)
- 'Third Coast Midstream, LLC' -> 'Third Coast Midstream LLC' (2)
- 'BBT Midla, LLC' -> 'BBT Midla LLC' (2)
- 'Gulfstream Natural Gas System, L.L.C.' -> 'Gulfstream Natural Gas System LLC' (2)
- 'Enterprise Products Partners' -> 'Enterprise Products Partners LP' (2)
- 'Natural Gas Pipeline Company of America, LLC' -> 'Natural Gas Pipeline Company of America LLC' (2)
- 'RIGS Haynesville Partnership Co.' -> 'RIGS Haynesville Partnership Co' (2)
- 'Kinetica Energy Express, LLC' -> 'Kinetica Energy Express LLC' (2)
- 'UGI Energy Services Inc.' -> 'UGI Energy Services Inc' (2)
- 'Capitol Energy Ventures Corp.' -> 'Capitol Energy Ventures Corp' (2)
- 'Williams Companies' -> 'Williams Companies Inc' (2)
- 'Nicor-Horizon, Inc.' -> 'Nicor-Horizon Inc' (2)
- 'Midwestern Gas Transmission Company' -> 'Midwestern Gas Transmission Co' (2)
- 'Ozark Gas Transmission, L.L.C.' -> 'Ozark Gas Transmission LLC' (2)
- 'Natural Gas Pipeline Co of America LLC (NGPL)' -> 'Natural Gas Pipeline Co of America LLC' (2)
- 'Natural Gas Pipeline Company of America LLC (NGPL)' -> 'Natural Gas Pipeline Company of America LLC' (2)
- 'Enable Gas Transmission, LLC' -> 'Enable Gas Transmission LLC' (2)
- 'El Paso Natural Gas Company, L.L.C.' -> 'El Paso Natural Gas Company LLC' (2)
- 'National Grid' -> 'National Grid PLC' (2)
- 'National Grid plc' -> 'National Grid PLC' (2)
- 'Venture Global Gator Express, LLC' -> 'Venture Global Gator Express LLC' (2)
- 'Cheniere Creole Trail Pipeline, L.P.' -> 'Cheniere Creole Trail Pipeline LP' (2)
- 'Cheniere Energy Partners, L.P.' -> 'Cheniere Energy Partners LP' (2)
- 'Venture Global Delta Express, LLC' -> 'Venture Global Delta Express LLC' (2)
- 'ArcLight Capital Partners' -> 'ArcLight Capital Partners LLC' (2)
- 'Brookfield Infrastructure Partners' -> 'Brookfield Infrastructure Partners LP' (2)
- 'Adelphia Gateway, LLC' -> 'Adelphia Gateway LLC' (2)
- 'Equitrans Midstream Corporation' -> 'Equitrans Midstream Corp' (2)
- 'Eversource' -> 'Eversource Energy' (2)
- 'Algonquin Gas Transmission, LLC' -> 'Algonquin Gas Transmission LLC' (2)
- 'Glenfarne Alaska LNG, LLC' -> 'Glenfarne Alaska LNG LLC' (2)
- 'Harvest Alaska, LLC' -> 'Harvest Alaska LLC' (2)
- 'Hilcorp Alaska, LLC' -> 'Hilcorp Alaska LLC' (2)
- 'Alliance Pipeline L.P.' -> 'Alliance Pipeline LP' (2)
- 'Trail West Pipeline, LLC' -> 'Trail West Pipeline LLC' (2)
- 'Pacific Gas and Electric Company' -> 'Pacific Gas and Electric Co' (2)
- 'PG&E Corporation' -> 'PG&E Corp' (2)
- 'Carlsbad Gateway, LLC' -> 'Carlsbad Gateway LLC' (2)
- 'WhiteWater Midstream, LLC' -> 'WhiteWater Midstream LLC' (2)
- 'Kern River Gas Transmission Company' -> 'Kern River Gas Transmission Co' (2)
- 'Mojave Pipeline Operating Company, LLC' -> 'Mojave Pipeline Operating Company LLC' (2)
- 'Ruby Pipeline, L.L.C.' -> 'Ruby Pipeline LLC' (2)
- 'Transwestern Pipeline Company, LLC' -> 'Transwestern Pipeline Company LLC' (2)
- 'Montana-Dakota Utilities Co.' -> 'Montana-Dakota Utilities Co' (2)
- 'Tallgrass Energy' -> 'Tallgrass Energy LP' (2)
- 'Northern Border Pipeline Company' -> 'Northern Border Pipeline Co' (2)
- 'Tallgrass NatGas Operator, LLC' -> 'Tallgrass NatGas Operator LLC' (2)
- 'Northwest Natural Gas Company' -> 'Northwest Natural Gas Co' (2)
- 'New Mexico Gas Company' -> 'New Mexico Gas Co' (2)
- 'Tuscarora Gas Transmission Company' -> 'Tuscarora Gas Transmission Co' (2)
- 'El Paso Natural Gas Company' -> 'El Paso Natural Gas Co' (2)
- 'Kurdistan Regional Government' -> 'Government of Kurdistan Region' (1)
- 'Rio Bravo Pipeline Company, LLC' -> 'Rio Bravo Pipeline Company LLC' (1)
- 'Roadrunner Gas Transmission, LLC' -> 'Roadrunner Gas Transmission LLC' (1)
- 'Freeport LNG Development, L.P.' -> 'Freeport LNG Development LP' (1)

## Left as they were (a person decides)

- 'H-Energy Private Limited' -> 'H-Energy Pvt Ltd'? fuzzy_candidates (4)
- 'Equitrans, L.P.' -> 'Equitrans LP'? alias_candidate (4)
- 'GASCO (Egyptian Natural Gas Company)' -> 'Egyptian Natural Gas Co'? acronym_not_initials (2)
- 'Egyptian Natural Gas Company (Gasco)' -> 'Egyptian Natural Gas Co'? acronym_not_initials (2)
- 'Egyptian Natural Gas Company (GASCO)' -> 'Egyptian Natural Gas Co'? acronym_not_initials (2)
- 'Pipeline Infrastructure Limited' -> 'Pipeline Infrastructure Ltd'? fuzzy_candidates (2)
- 'Indian Oil Corp (IOCL)' -> 'Indian Oil Corp'? acronym_not_initials (2)
- 'Brooklyn Union Gas Company d/b/a National Grid NY (KEDNY)' -> 'Brooklyn Union Gas Company d/b/a National Grid NY'? acronym_not_initials (2)
- 'National Fuel Gas Supply Corporation' -> 'National Fuel Gas Supply Corp'? alias_candidate (2)
- 'NextEra Energy, Inc. (affiliate)' -> 'NextEra Energy Inc'? acronym_not_initials (2)
- 'Con Edison Gas Pipeline and Storage, LLC (affiliate)' -> 'Con Edison Gas Pipeline and Storage LLC'? acronym_not_initials (2)
- 'AltaGas Ltd. / RGC Resources, Inc. (affiliates)' -> 'AltaGas Ltd. / RGC Resources Inc'? acronym_not_initials (2)
- 'ENSTAR Natural Gas Company' -> 'ENSTAR Natural Gas Co'? fuzzy_candidates (2)
- 'Southern California Gas Company' -> 'Southern California Gas Co'? fuzzy_candidates (2)

Next: the review app and the workbooks read these files on their next build; a decided line keeps its decision (the spelling moved, the entity did not).
