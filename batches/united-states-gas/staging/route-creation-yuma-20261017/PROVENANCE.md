# Route genealogy — P8309 Yuma Pipeline

The candidate route `candidate_routes/P8309.geojson` traces back to one source: the Yuma Pipeline overview map that FERC posted on August 28, 2026 at https://www.ferc.gov/media/yuma-pipeline-overview-map (image `Updated Yuma Map 8-27-2026.jpg`, fetched 2026-10-17). The same lineage is stamped as a `provenance` property on the feature and in `route_provenance.json`.

| Step | File | What it is |
|---|---|---|
| Source map | `maps/Updated Yuma Map 8-27-2026.jpg` | FERC map, 3400 by 2200 pixels, scale 1 to 600,000 |
| Trace | `traces/trace.json`, `traces/trace_red.py` | red pipeline line pulled out by color and thinned to a one-pixel centerline (185 points after a 0.8 pixel simplification and the border cut), in pixels only, chained from milepost 0 at the northeast end across the milepost circles |
| Control points | `traces/gcps.json` | 9 points: 8 county corners and border points from the US Census 2023 county file, 1 highway interchange from OpenStreetMap; none read off the map |
| Georeference | `traces/georef_report.json`, `traces/P8309_georef_out.geojson` | `scripts/georef.py`, second-order fit, RMSE 0.098 km; `P8309_georef_out_unclipped.geojson` is the line before the border cut, `P8309_georef_out.geojson` after it |
| Checks | `traces/mileposts_px.json`, `traces/check_mp.py` | printed mileposts land every 9.7 to 10.2 miles; map border within about 160 m of the Census border |
| Candidate | `candidate_routes/P8309.geojson` | 220.8 km (137.2 mi) against 138 mi stated; RouteAccuracy medium. The raw trace ran about 650 m past the border because the map draws the line into its thick border symbol; the line is cut at the Natural Earth United States boundary (the routes repository checks endpoints against it), with the last point 20 m inside, about 250 m north of the Census border |

The first trace (6 pixel cells, 215.8 km) cut corners and was replaced on 2026-10-17 by the full-resolution skeleton trace. The trace scripts were run from a scratch folder, so their input and output paths point there; the copies here are the record of what was run.
