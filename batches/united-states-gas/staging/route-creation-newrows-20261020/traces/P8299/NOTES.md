# P8299 We Energies Lakeshore Lateral, traced route

The source is the Wisconsin Department of Agriculture, Trade and Consumer Protection Agricultural Impact Statement addendum for the Lakeshore Lateral project, Appendix A Figure 1, PDF page 19. The figure is a company overview map dated October 19, 2020. It is a raster image, so the line was traced by hand and not extracted as vector data.

The page was rendered at 300 dpi to pg-19.png. The pipeline is the thick black line. County and municipal boundaries are thinner black lines, so the line was followed on zoomed crops with a pixel grid and drawn over the image to check it. The trace is in trace.json and was built by make_trace.py.

The map starts at station 0+00 near the Town of LaGrange and runs to station 2398+00 at the east frame edge, about 45 miles of the 46 mile route. The trace follows the line through the SIG-04 and SIG-05 areas as drawn in black. The red change segments were not followed.

Fifteen ground control points are used, all from the US Census Bureau 2023 Gazetteer internal points for towns, a city and a village. Each pixel is the center of that place's printed label on the map. The points are spread from LaGrange in the west to Paris and Norway in the east, and from East Troy in the north to Wheatland in the south. The file is gcps.json and each point has its own source reference.

The first order fit gives a root mean square error of 1.36 km, with a leave one out error of 1.73 km and a worst point of 3.38 km at Town of East Troy. The limit was 5 km and the fit passed. No point was moved or dropped.

The traced length is 71.26 km, or 44.28 miles, against a stated 46 miles. That is a ratio of 0.96. The shortfall fits a map that stops a little before the east end.

The start is at about 42.797 N, 88.652 W, on the east edge of the Town of Whitewater area as expected. The end is at about 42.663 N, 87.959 W, which is about 2 km short of the Mount Pleasant regulator station near Interstate 94, because the frame ends there. check.py shows the line passes 0.7 km from Burlington city, 3.3 km from Elkhorn city and 3.7 km from Union Grove, which matches the map.

Doubts. Place labels are not exact centers, so the fit carries about 1 to 3 km of error and the route should be treated as low accuracy. The map ends before the true east end, so the last mile or two is missing. Near Burlington the thick line merges with municipal boundaries, so the path in the SIG-04 area is the least certain part. The image is a low resolution scan, so the line width is several pixels.
