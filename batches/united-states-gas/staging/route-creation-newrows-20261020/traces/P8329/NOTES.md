# P8329 We Energies Rochester Lateral, trace notes

The map is the Public Service Commission of Wisconsin project map for docket 6630-CG-139, one page, file RochesterLateralMap-1.png (1650 by 1275 pixels), taken from RochesterLateralMap.pdf on the commission case page.

The map shows route alternatives, not the authorized route. The Commission authorized the applicant's preferred route on December 2, 2025. That route is a mix of Route A segments, Route B segments and Route C connectors, and the map does not show which segments.

I traced Route B, including the shared AB sections at the west and east ends, as a stand-in for the authorized route. I chose Route B because its class location mileage in the environmental assessment (15.8, 16.3 and 0.56 miles by class) is closest to the preferred route (15.7, 16.1 and 1.2 miles). The environmental assessment also says the preferred route takes segment B-6 over A-6, which is the long northeast run. Route B is 33.2 miles in the environmental assessment and the sheet says 33 miles.

The trace has three parts. One runs from Rochester Gate along State Highway 20 to the junction near State Highway 75. One is the trunk from that junction north and east to the Oak Creek campus on Lake Michigan. One is the south spur from the Lakeshore Lateral near State Highway 75 and the Racine-Kenosha county line up to the junction. The three parts meet at the junction.

The line was extracted from the magenta Route B pixels (and the dashed AB sections) by shortest path through a color mask with hand-placed waypoints, then simplified to about one pixel. I drew it over the map and checked the overlay by eye (overlay.png). The scripts are mask.py and trace_routeB.py.

Nine ground control points were used, all from US Census Bureau TIGERweb county and road geometry, never read off the map. They are county line crossings of US 45, State Highway 38, State Highway 75 and Interstate 41, plus road crossings of Interstate 41 with State Highways 20 and 11, US 45 with State Highway 11, and State Highway 75 with State Highway 11. Each has its source in gcps.json. The pixel positions were read from zoomed crops (gcp_crops.png and gcp_crops2.png). The candidate calculation is in geocode_candidates.py.

The first-order fit has a root mean square error of 0.021 km, leave-one-out 0.033 km, maximum 0.035 km, against a bound of 5 km.

The traced length is 50.5 km, which is 31.4 miles. That is 0.95 of the stated 33 miles. The shortfall is expected because the map draws the route with straight edges. The start is in Racine County near Rochester, the south spur starts in Kenosha County, and the east end is in Milwaukee County at Oak Creek. The check is in check.py.

Doubts. The authorized route differs from Route B in places, so this line is an approximation of the authorized route, not the route itself. Locally it may be off by a mile or more where the preferred route uses Route A or Route C segments, most likely near the junction and the northeast end. The application's Attachment 10 Preferred Route Map would fix this and was not found. The GCPs sit between x 463 and 1195 on the map, so the west branch (to x 160) and the east end (to x 1500) are extrapolated, though the fit is nearly exact, so the risk is small. The south spur end was stopped at the last drawn line pixel just above the valve symbol.
