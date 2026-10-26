# P8316 McCloud Lateral, trace notes

The source is Figure 1.1-1, the Project Overview Map, on page 9 of the PDF (printed page 1-2) of Resource Report 1 for the McCloud Lateral Project, Federal Energy Regulatory Commission docket CP26-558. The map is a raster image at about 1 to 20,000 on an Open Street Map basemap. The image used is maps/P8316/mccloud-fig1-1-p9-009.png.

The pipeline centerline is a distinct magenta line, so it was extracted by color mask, morphological closing, skeletonizing and a longest-path walk through the skeleton, then simplified to about 1 pixel (trace_magenta.py). The overlay (overlay_trace.png, and zoomed crops viewed during review) shows the trace sitting on the magenta line along its whole length. Only the lateral was traced, from the El Paso Compressor Station in the southwest to the McCloud Meter Station in the northeast.

Three small gaps in the color mask were bridged automatically by joining the nearest skeleton pixels. Two of them were 3 pixels wide. The third was 57 pixels long, where a black limit-of-disturbance spur hides part of the magenta line just north of Stan Roberts Sr Avenue. The magenta line is visible and straight there in the zoomed crop, so the bridge follows it.

Six ground control points were used, all geocoded from US Census Bureau TIGER/Line 2023 files and none read off the map. They are the Doña Ana, Otero and El Paso county tripoint on the state line, McCombs Street at the state line, McCombs Street at Stan Roberts Sr Avenue, McCombs Street at FM 2637, Stan Roberts Sr Avenue at the center of the US 54 median, and the east end of Stan Roberts Sr Avenue at the railroad. Each has its source in gcps.json. They span the whole map in both directions, although three of them lie along McCombs Street on the west side.

The first order fit has a root mean square error of 0.013 km, with a leave-one-out error of 0.027 km and a maximum of 0.019 km, against the allowed 5 km. The fit passed on the first try with no GCP changed.

The traced line is 9.359 km, or 5.816 miles, against the stated 5.8 miles, a ratio of 1.003. Both ends and the whole line fall inside the Census El Paso County, Texas polygon. The line crosses Stan Roberts Sr Avenue at longitude -106.3746, between McCombs Street and the US 54 freeway, as the map shows (check_p8316.py).

Doubts are small. The two end points are the ends of the magenta line, so the exact position at the stations is only good to a few pixels, about 20 to 30 meters. The pixel positions of the GCPs were located by eye on 8 to 10 times zooms and are good to about 3 pixels. The map shows the lateral entering the meter station at the corner of its fill, and the trace stops at the skeleton end just short of the fill. The 120 foot access road in Otero County, New Mexico, that the report mentions is not part of the traced line.
