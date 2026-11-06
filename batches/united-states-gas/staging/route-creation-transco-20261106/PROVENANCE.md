# Route genealogy — Transco segments without routes

This batch draws routes for 13 Transco rows and Transco-linked laterals that had no route or only a low-accuracy one. Most Transco expansion projects are loops: new pipe laid beside the existing mainline in the same right of way. GEM already has the mainline route (P0271), so most loops can be cut out of it once the loop's mileposts are known. The same lineage, per row, is in `route_provenance.json`.

## How the source was chosen

- **Oil & Gas Watch first.** Three rows have Oil & Gas Watch records that were traced from FERC environmental assessments (P3201, P2574, P2600). Those were used as published vector data, and two of them replace an existing low-accuracy route.
- **OpenStreetMap for the rest.** OpenStreetMap is not trusted by default for US gas (rulings of 2026-10-02 and 2026-10-20). It is used here under the 2026-11-05 exception: each line is detailed (dozens to hundreds of points) and much better than the only other vector source, the EIA pipeline map, which Baird ruled a last resort on 2026-11-06. The EIA map has no line at all for the Dalton Lateral and only a generalized line for the others. No company system map or FERC GeoPDF with usable geometry was found for these rows.
- **EIA as a cross-check.** The EIA natural gas pipeline layer was pulled (`fetched_layers/eia_transco.geojson`, `eia_gulf_sc.geojson`, `eia_dalton.geojson`) and each candidate was measured against it. The table gives the gap from points along the candidate to the nearest EIA line of the same operator.

| Row | Points | Mean gap to EIA, km | 90th percentile, km | Largest, km |
|---|---|---|---|---|
| P8288 | 130 | 0.6 | 1.8 | 2.1 |
| P8287 | 92 | 0.9 | 2.1 | 2.5 |
| P8285 | 115 | 0.2 | 0.3 | 0.4 |
| P8281 | 72 | 0.2 | 0.5 | 0.7 |
| P8280 | 72 | 0.4 | 1.1 | 1.5 |
| P3199 | 4 | 0.4 | 0.4 | 0.4 |
| P8229 | 67 | 1.7 | 3.3 | 4.2 |
| P8284 | 864 | 0.3 | 0.6 | 1.3 |
| P4382 | 314 | 9.7 | 20.0 | 23.0 |
| P8279 | 607 | not on EIA map | | |

For P4382 the EIA line is the older Carolina Gas Transmission system, not this 2017 lateral, so the gap is expected. For P8279 the nearest EIA line is Southern Natural Gas, 11 km away on average.

## Loops cut from the mainline (P8288, P8287, P8285, P8281, P8280, P3199)

The mainline route in the routes repo (P0271) is built from OpenStreetMap ways tagged with Transco as operator and with line names such as Main Line A, B and C. The loops were cut along it at the mileposts in FERC documents.

- **Milepost placement.** A milepost was turned into a point by measuring along the mainline from compressor stations whose mileposts and locations are known. Station locations come from EPA facility records (`traces/method/stations.json`). On the southern mainline, Station 90 (milepost 811.26) to Station 165 (milepost 1413.0) gives a scale of 1.00175 mapped miles per milepost.
- **New Jersey.** The line north of Station 205 has a milepost equation, so it was scaled on two anchors instead: the Stirling Loop end at the Somerset and Morris county line (milepost 1793.92) and Station 240 in Bergen County (milepost 1825.8).
- **Leidy Line in Pennsylvania.** The scale runs from Centerville (milepost 0.11) to Station 520 (milepost 157.52). Dorrance and Benton loops are given in Leidy Loop Line mileposts, which were taken to count from Station 515. That assumption is flagged in both rows' notes.
- **Checks.** Every cut was checked against the counties and townships the FERC documents name, using the Census geocoder. The Lehigh River crossing at milepost 65.5 falls on the Monroe and Luzerne county line. Station 515 falls in Buck Township, the Dorrance start in Dorrance Township, the Benton end in Benton Township, and the Haneyville Loop in Grugan Township, Clinton County. All other stated counties match.
- **Files.** The cuts are in `traces/P####_loops.geojson`, one feature per loop with its mileposts. The scripts and the calibrated master paths are in `traces/method/`.

| Row | Loops | Cut length | Sheet length |
|---|---|---|---|
| P8288 Sundance | DeSoto, Summerville, Kings Mountain, Mooresville | 38.0 mi | 38 mi |
| P8287 SouthCoast | Loop E 42-inch, Loop E 48-inch, North Georgia Extension Loop | 44.2 mi | 44.3 mi |
| P8285 Momentum Phase I | Phase I loops, Mississippi to Georgia | 42.7 mi | 42.26 mi |
| P8281 Leidy Southeast | Skillman, Pleasant Run, Franklin, Dorrance | 29.7 mi | 29.8 mi |
| P8280 Leidy East | Haneyville, Williamsport, Benton, Allentown, Clinton, Stirling | 29.6 mi | 31 mi |
| P3199 Rivervale South to Market | Bergen Loop, mileposts 1825.80 to 1826.41 | 0.61 mi | 0.98 km |

All six are set to medium accuracy. The mainline line itself is detailed, but each loop end rests on a milepost placed by measurement, good to a few hundred meters.

## Standalone lines

- **P8279 Dalton Expansion.** OpenStreetMap ways tagged Dalton Lateral, Transco, 20 inch, start date 2017 (ways 1041497817, 1047098239, 1047695382 to 1047695386, 1071082593, 836132508). The line runs from Coweta County north to Murray County, Georgia, 114.5 miles against 115 on the sheet. A short branch near the north end is kept as a separate part. High, since the name, operator, diameter, date and length all match.
- **P4382 Transco to Charleston.** OpenStreetMap ways 1096994409, 1096994412 and 1096994413, operator Carolina Gas Transmission, from Moore in Spartanburg County to the Chappells area, 54.7 miles. The 2016 Federal Register notice calls this the Moore to Chappells Pipeline, about 55 miles of 12-inch pipe. The 5-mile Dillon Pipeline in the same project is not drawn. Medium, since the ways carry no name.
- **P8229 Pascagoula Supply Line.** OpenStreetMap ways 1070117869, 1182027895 and 257816887, operator Transco, from the Bayou Casotte area of Pascagoula, Mississippi east to Grand Bay, Alabama, 15.4 miles against 15.54. OpenStreetMap tags these ways as part of the Transco Gulf of Mexico mainline, so the match rests on the ends and the length. Medium.
- **P8284 Mobile Bay Lateral Expansion Phase 1.** The 30-inch segment from Station 82 near Coden across Mobile Bay to Mobile Block 822 is OpenStreetMap way 1256820051 (Transco, 30 inch, underwater), 18.1 miles. The 24-inch offshore segment to Main Pass Block 261 is BOEM pipeline segment 11467 (Transco, 24 inch, gas, active, right of way G18794), 57.3 miles, from the BOEM pipeline shapefile (US public domain), reprojected from NAD27. The BOEM segment starts where the OpenStreetMap way ends. BOEM's short 30-inch segment 11468 lies on top of the OpenStreetMap way and was not added. The 1997 Federal Register notice gives 19.08 and 56.58 miles. High.

## Oil & Gas Watch rows

- **P3201 Southeastern Trail Expansion.** Oil & Gas Watch record 3359, the Manassas loop in Prince William County, Virginia, 12.4 km against 12.9 km. High.
- **P2574 Northeast Supply Enhancement.** Oil & Gas Watch record 3340, 59.7 km. Replaces a low-accuracy route. High.
- **P2600 Regional Energy Access.** Oil & Gas Watch record 3353, 58.4 km against 54.7 km. Replaces a low-accuracy route. Medium.

## License

OpenStreetMap data carries the Open Database License, which asks for credit to OpenStreetMap contributors. Whether that is acceptable for the tracker is Baird's call. The BOEM segment is US government public domain.
