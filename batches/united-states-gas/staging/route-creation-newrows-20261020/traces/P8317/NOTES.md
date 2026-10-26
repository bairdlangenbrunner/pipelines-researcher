# P8317 Homer City Generating Station Gas Pipeline: trace notes

The map is the Pennsylvania Department of Environmental Protection permit application PAD320011 water well map, Figure 1, sheets 1A to 1E (pages 1 to 5 of PAGWIS_Water_Wells_Fig1.pdf), drawn by Civil and Environmental Consultants on May 28, 2026. The sheets are aerial photos at 1 inch to 500 feet with the proposed pipeline as an orange line. The PDF is an image-only file, so the line was extracted from the rendered pages and not from vector paths.

The orange line was pulled from each sheet with a color mask, thinned to a one pixel skeleton, chained into one path and simplified to about 1 pixel (trace_orange.py). The other overlays on the sheets (red limit of disturbance, pink buffer) were not traced. The line runs from the Homer City Generating Station end on sheet 1A to a dead end in the woods near Campbells Mill Road on sheet 1E.

The five sheets are not true overlaps. Each frame meets the next at its edge, so the sheets were placed in one pixel frame by where the orange line crosses each shared frame edge (stitch.py). Sheets 1A to 1B, 1B to 1C and 1D to 1E join top to bottom. Sheet 1C joins sheet 1D at the left edge of 1C and the right edge of 1D. The offsets are in sheet_offsets_stitch.json.

There are 10 ground control points, all intersections of named road centerlines in the US Census Bureau TIGER/Line 2023 roads file for Indiana County, Pennsylvania. The longitude and latitude come from that file and the pixel is where the same junction sits on the map. They are Coal Road with Bruner Road, Coal Road with Power Plant Road, Dickey Road with Mahan School Road, Black Lick Road with Ash Road, Dunlap Drive and McConnell Road, Black Lick Road with Thompson Road, Muddy Run Road with Thompson Road, and Campbells Mill Road with Pine Lane and with Falling Run Road. They are spread over all five sheets. Each has its source reference in gcps.json.

The first order fit has a root mean square error of 0.037 km, leave-one-out 0.049 km and maximum 0.062 km, well inside the 5 km limit. The stitching by line crossings and the geocoded points were made independently, so this agreement is a real check on both.

The traced length is 9.313 km, which is 5.79 miles, against 5.8 miles stated, a ratio of 0.998. The start is at about -79.2057, 40.5198 and the end at about -79.2452, 40.4568. Crossing the output with TIGER roads gives Power Plant Road, Dickey Road, Black Lick Road, McConnell Road and Falling Run Road in that order from the north, matching the order in the Department fact sheet (check.py).

One candidate point was dropped: Mine Road with Mahan School Road on sheet 1B. It sat about 110 meters out of line with the other points and the stitching, and the Dickey Road junction on the same sheet agreed. Falling Run Road with Campbells Mill Road is a little uncertain because the map junction and the TIGER junction differ by roughly 50 meters. It stays in because the fit is far inside the limit.

The fact sheet overview map was not used, since it appears to show a different line. The south end of the orange line on sheet 1E is a short dog-leg that stops in woods near Campbells Mill Road. The sheet 1E overlay is in overlay_sheet5.png.
