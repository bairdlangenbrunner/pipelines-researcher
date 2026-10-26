# P8320 Licking County Pipeline, trace notes

The map is the one-page project map dated March 26, 2026, from The Energy Cooperative, in maps/P8320/2026.03.26_Licking_County_Pipeline_Project_Map.pdf. The page is a single embedded raster image, not a vector file, so there was no path to extract. The image was pulled out with pdfimages at its native 3400 by 2200 pixels (img-000.png).

Both drawn phases were traced: Phase 1 in blue and Phase 2 in orange. The line is a flat saturated color, so extract_trace.py selected it with a color mask, thinned it to a one pixel skeleton, chained the pixels from west to east, and simplified it to 1.5 pixels. The two phases meet at one point and were joined into one line. The result is in trace.json and overlay_small.png shows it drawn over the map. It follows the colored line everywhere, with a tiny stub at the northwest end that is part of the drawn line.

Ten ground control points are in gcps.json. Eight are crossings of named roads (US 40, Interstate 70, State Routes 37, 79, 158, 161, 310 and 16), with longitude and latitude taken from the US Census Bureau TIGER/Line 2023 road file for Licking County, Ohio (tl_2023_39089_roads.zip). Two are corners of the Franklin and Licking county line, taken from the TIGER/Line 2023 county boundary file. No coordinate was read off the map image. The pixel for each point was located by zooming into native resolution crops (crop.py). The points cover the west, middle, east and south of the traced extent, but none lie north of the pipeline's upper half.

The first order (affine) fit passed with a root mean square error of 0.057 km, a leave-one-out error of 0.142 km, and a worst point of 0.149 km. The limit was 5 km. The full report is in georef_report.json.

The traced line is 36.35 km, or 22.59 miles, against a stated length of 24 miles, a ratio of 0.94. check_route.py confirms the whole line lies in Licking County, Ohio, and that the Phase 1 section lies on top of State Route 161. The start is near New Albany and the end is just north of US 40 east of Hebron, which matches the map.

Doubts: the pixel for the State Route 161 and State Route 310 crossing is uncertain by about 10 pixels, because the blue line covers the road there. The 24 mile stated length is a little longer than the drawn line, which is normal since the map shows a simple route and the real centerline may differ. The map is a proposed route and the final centerline may change. The May 2026 web map shows Phase 2 only as a wide study corridor, so it was not used for tracing.

Data downloads used for geocoding (all from www2.census.gov/geo/tiger/TIGER2023): ROADS/tl_2023_39089_roads.zip, ROADS/tl_2023_39045_roads.zip and COUNTY/tl_2023_us_county.zip. They were kept in the session scratch folder, not in the repository.
