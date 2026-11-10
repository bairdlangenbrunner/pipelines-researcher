# Route genealogy — P4457 Lowman Pipeline

The candidate route `candidate_routes/P4457.geojson` traces back to one source: the route map on the Lowman Pipeline project page, as saved by the Internet Archive on July 13, 2023, at https://web.archive.org/web/20230713140710/https://www.lowmanpipeline.com/project.html (map image `lowman-map.jpeg`, fetched 2026-11-05). The page is the project site of the line's owner, NextEra Energy Resources. The same lineage is in `route_provenance.json`.

| Step | File | What it is |
|---|---|---|
| Worklist | `worklist.json` | one row, P4457, no existing route, sheet length 86.9 km |
| Source map | `maps/lowman_company_map_20230713.jpg` | the 1008 by 417 pixel map; the left half is a county-level detail map that draws the line in blue from Choctaw County to the Lowman Energy Center in Washington County |
| Trace | `traces/trace.json`, `traces/trace_band.py` | the middle of the blue line, pulled out by color and thinned to a one-pixel line at four times the map's size; 128 points in pixels only, with the black plant dot's center added at the end |
| Control points | `traces/gcps.json` | 5 county corners and meeting points (two Choctaw County corners, the Choctaw, Washington and Clarke meeting point, where the Choctaw and Washington line meets the state line, and where the Washington County south line meets the river), taken from the US Census 2023 county boundary file; none read off the map as coordinates |
| Georeference | `traces/georef_report.json`, `traces/P4457_georef_out.geojson` | `scripts/georef.py`, first-order fit, RMSE 0.19 km, worst point 0.24 km, leave-one-out 0.54 km |
| Checks | `overlays/trace_on_source_map.png`, `overlays/candidate_on_counties.png` | the trace and control points drawn back on the map, and the georeferenced line on Census counties |
| Candidate | `candidate_routes/P4457.geojson` | 81.5 km against 54 miles (86.9 km) on the sheet, ratio 0.94; RouteAccuracy medium |

The map is small, one pixel is about 0.35 km, and the drawn line is about 5 pixels wide, so the line is good to roughly 1 to 2 km even though the fit error is small. The trace smooths small bends, which is why it is about 5 km shorter than the sheet.

The Alabama Public Service Commission notice in docket 32978 at https://www.pscpublicaccess.alabama.gov/pscpublicaccess/ViewFile.aspx?Id=551e03df-819c-494d-bbab-c36f60b16006 describes about 51 miles of 16 inch pipe from near Butler in Choctaw County to the Lowman Energy Center near Leroy in Washington County. It gives no coordinates, so it checks the endpoints in words only.

The plant end was checked against the federal power plant records for plant 56, shown at https://www.interconnection.fyi/eia/plant/56 (31.488, -87.911). The traced end is 0.46 km from that point. That location was not used as a control point.

The Choctaw County start is only what the company map shows, a join with existing gas pipelines near the Mississippi state line. No other source gives a coordinate for it.

The pipeline serves the Lowman Energy Center, owned by PowerSouth Energy Cooperative, in Washington County. I found nothing tying it to Alabama Power plants or to Mobile County.

An OpenStreetMap line for this pipeline (way 1282145901) was drawn in a comparison overlay once, as a sanity check only. The largest gap between it and the traced line is 1.5 km and the average is 0.2 km. Baird ruled on 2026-10-20 that OpenStreetMap is not a trusted source for this work, so it is not a source for the route, the notes, or the references, and nothing from it is staged. An earlier version of this candidate was built from it and was replaced on 2026-11-05.
