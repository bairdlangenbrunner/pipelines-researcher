# P8212 Northern Natural Gas Permian Basin Expansion Project, trace notes

The map is Figure 1-1, Project Overview Map, embedded in the FERC notice of scoping for docket CP26-534 (accession 20260708-3030). The image is maps/P8212/notice-of-scoping-image1.png, 1525 by 966 pixels, a raster at 1 to 60,000 with no vector layer, so the line was traced from pixels.

I traced the proposed pipeline, which the legend shows as red dashes over a purple permanent easement. The red dashes were pulled out with a color mask (about RGB 230, 77, 0) and chained with per-bin medians in trace_red.py. The staging boxes, access roads, survey boundary and the Plains recycle valve inset were left out. The overlay was checked by eye at the west end, the corner at the compressor station and the east end.

The traced line starts at the Hobbs-Plains bidirectional receiver, runs northeast about 1.1 miles to the Hobbs compressor station, then runs south and southeast along the main leg to the Gaines County Generating Station. The short diagonal matches the 1.1 miles of 16 inch pipe in the application and the main leg matches the 15.1 miles of 24 inch pipe. I treated the two as one connected line.

Nine ground control points were used, all from Census Bureau TIGER/Line 2023 road and county files, never read off the map. They are the junctions of US 62 with New Mexico 8, South Ryco Lane, South Asher Road, South Cecil Street and North Dal Paso Street, East Stanolind Road with South Dal Paso Street, East Stanolind Road and East Nadine Road where each meets the New Mexico and Texas state line, and Nadine Road with County Road 347. Each source reference is in gcps.json. The pixel positions were read from zoomed crops.

The first order fit has a root mean square error of 0.017 km, leave-one-out 0.027 km, and a maximum of 0.025 km. The bound was 5 km.

The traced length is 26.06 km or 16.19 miles against the stated 16.2 miles. About 15.6 miles fall in Lea County, New Mexico and 0.6 miles in Gaines County, Texas. The line starts near -103.284, 32.699 and ends near -103.060, 32.634. check_route.py reproduces these numbers.

Doubts. The application text says about 14.5 miles are in New Mexico and the rest in Texas, but the map puts the Gaines County generating station only about 0.5 km past the state line, so the traced Texas share is smaller than the text. The two disagree and I did not adjust the line. The east end hook near the generating station is a few pixels wide and the corner was cut slightly. The Cecil Street control point sits in a dense street grid and is the least certain, but it fits within 0.02 km. The line shows only the proposed pipeline, not the Plains recycle valve site in Yoakum County, which is about 29 miles away.
