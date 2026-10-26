# P8327 candidate verification, 2026-10-20

The candidate in candidate_routes/P8327.geojson was challenged as a bad route. It was re-checked against every map in the March 13, 2026 FERC draft (accession 20260313-5242) and against Census TIGER roads, water, county and place boundaries. The geometry was not changed. These files are the evidence.

Scripts (run with python3 -I from outside the download directory; they take the scratchpad path and the full 686 page PDF):
- verify_geopdf.py: reads a page's /VP /Measure georeferencing and converts drawing coordinates to lon/lat.
- verify_route.py: length, milepost circles, county crossings, endpoint checks, segment statistics.
- verify_extrapolation.py: tests the affine extrapolation outside the page frame against Census county lines and compares the mainline vertex count across pages 681, 683, 684 and 686.
- verify_side_by_side.py: renders page 685 beside the extracted layers.
- verify_overlays.py: eight review panels (verify_overlays.png).

Results: length 81.62 mi (filing 81.6). Milepost circles 45 to 54 on page 685 sit at 45.0 to 54.0 mi along the line, 0.1 to 0.7 m off it. County lines crossed at 29.98 mi (filing 29.7) and 62.11 mi (filing 62.1). North end 1.1 m from the mainline drawn inside page 684's frame, at mainline milepost 294.32 (filing 294.3). South end 2.1 km north of the Ellendale place boundary. Off-frame county lines on pages 684 and 685 match Census lines within 0.4 m median and 3.1 m max, so extrapolation is exact. Mainline vertex count is the same on four pages at four scales, so the drawn lines are not generalized. The stair-step shape is the real section-line alignment.

Page cut-outs: the p684 file and the p685-with-vp file carry the /VP georeferencing dictionary copied from the source page (the original p685 cut-out already had it).
