# Route genealogy — P7833 South Mississippi Project

The candidate route `candidate_routes/P7833.geojson` traces back to one source: the map on page 1 of the Energy Transfer binding open season notice for the South Mississippi Project, dated October 28, 2026, at https://pipelines.energytransfer.com/InfoPost/resources/documents/ET_Open_Season_Announcement_South_Mississippi_Project%2010_28_2026.pdf (linked from Florida Gas Transmission notice 74540, fetched 2026-11-03). The map itself is dated October 9, 2026. The same lineage is in `route_provenance.json`.

| Step | File | What it is |
|---|---|---|
| Source map | `maps/ET_Open_Season_Announcement_South_Mississippi_Project_10_28_2026.pdf`, `maps/et_binding_open_season_20261028_p1_map.jpg` | the notice, and its page 1 map cut out at 1091 by 900 pixels; the map covers much of the eastern United States and draws the project as a magenta dashed arrow |
| Trace | `traces/trace.json`, `traces/trace_magenta.py` | the magenta dashes pulled out by color, 16 points in pixels only; label letters dropped, the Perryville star center added at the start and the arrowhead tip at the end |
| Control points | `traces/gcps.json` | 6 state border corners and border points (Louisiana, Arkansas, Mississippi, Tennessee, Alabama) computed from the Natural Earth 10m states file; none read off the map as coordinates |
| Georeference | `traces/georef_report.json`, `traces/P7833_georef_out.geojson` | `scripts/georef.py`, first-order fit, RMSE 3.2 km, worst point 4.1 km |
| Checks | `overlays/trace_on_source_map.png`, `overlays/traced_route_counties_sesh.png` | the trace drawn back on the map, and the georeferenced line beside US Census 2023 counties and the Southeast Supply Header route (P0164) |
| Candidate | `candidate_routes/P7833.geojson` | 307.5 km against 215 miles (about 346 km) stated; RouteAccuracy very low. Starts in Richland Parish, Louisiana, and ends in Greene County, Mississippi, about 4 km from George County, which is inside the fit error |

The notice says most of the line will be built beside existing pipe. The trace runs near the Southeast Supply Header, but that corridor is a guess and is not drawn into the route. The trace script was run from a scratch folder, so its paths point there; the copy here is the record of what was run. The Census county files used for the check map are in `fetched_layers/` and are not committed.
