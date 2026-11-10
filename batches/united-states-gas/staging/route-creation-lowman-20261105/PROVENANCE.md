# Route genealogy — P4457 Lowman Pipeline

The candidate route `candidate_routes/P4457.geojson` comes from OpenStreetMap way 1282145901 (https://www.openstreetmap.org/way/1282145901), tagged as the Lowman Pipeline, 16 inch gas, operator NextEra Energy Pipeline Holdings (Lowman), Inc. It was pulled with Overpass on 2026-11-05 (`fetched_layers/osm_lowman.geojson`) and the one way was split out to `fetched_layers/osm_lowman_way1282145901.geojson`. The same lineage is in `route_provenance.json`.

The line has 555 points and is 87.1 km long, against 54 miles (86.9 km) on the sheet. RouteAccuracy is high.

OpenStreetMap is normally not used for US gas routes (ruling of 2026-10-20). Baird made an exception on 2026-11-05: an OpenStreetMap line may be used when it is clearly detailed and much better than the other options. Here it was checked against a trace of the route map on the company's project page, as saved by the Internet Archive on July 13, 2023. The two lines are 0.2 km apart on average, 0.7 km at the 90th percentile, and 1.5 km at most. The company map is small, with one pixel about 0.35 km, so the trace is good to only 1 to 2 km. The trace and its files are kept in `superseded_trace/`, `traces/`, `maps/`, and `overlays/`.

The Alabama Public Service Commission notice in docket 32978 (https://www.pscpublicaccess.alabama.gov/pscpublicaccess/ViewFile.aspx?Id=551e03df-819c-494d-bbab-c36f60b16006) describes about 51 miles of 16 inch pipe from near Butler in Choctaw County to the Lowman Energy Center near Leroy in Washington County. The plant end of the line is within 0.5 km of the federal power plant record for plant 56 (https://www.interconnection.fyi/eia/plant/56).

OpenStreetMap data carries the Open Database License, which asks for credit to OpenStreetMap contributors.
