# P8311 Apollo South Pipeline endpoints

Result: end PASS, start PARTIAL (place sourced, coordinate is a proxy).

## End
- Place: Apollo Power Generation Facility, on 147 acres at the northeast corner of Ohio 582 and Mercer Road, Middleton Township, Wood County. The Bowling Green Independent Media seed article says the line ends at the plant on Mercer Road just east of the Meta data center.
- Sources opened: https://bgindependentmedia.org/residents-on-pipeline-route-for-data-center-worry-about-safety-property-values-and-lack-of-transparency/ and https://bgindependentmedia.org/?p=115392 (plant site description).
- Coordinate: -83.62897, 41.45809. It is the intersection of State Rte 582 and Mercer Rd from US Census TIGERweb road lines. The plant sits at the northeast corner, so the true end is within about 0.5 km of this point.

## Start
- Place: Rover Pipeline interconnect in southern Wood County, just north of Cygnet Road. The line then runs through Henry, Liberty, Plain and Middleton townships (seed article).
- Coordinate used: -83.72717, 41.24098, from the US Census Geocoder for Cygnet Rd and Wingston Rd. Wingston Road is named in the article. This is a point on Cygnet Road, not the Rover crossing itself. The real interconnect is north of it and could be several km east or west.
- Why not better: no source read gives the Rover crossing point. The Ohio Power Siting Board case record (dis.puc.state.oh.us, case 26-0624-GA-BLN) returned "Request Rejected" through curl and scripts/fetch.py. The EIA pipeline layer on ArcGIS (services2.arcgis.com, NaturalGas_InterIntrastate_Pipelines_US_EIA_ExportFeatures) draws Rover as a coarse line that puts it in Liberty Township, which conflicts with other reports that Rover crosses Henry Township here, so it was not used.

## Length
- 23.5 miles of 20 inch pipe in Wood County, from a Teamsters National Pipeline job notice dated 2026-09-21 for contractor WHM Construction (clearing and mat setting, start 2026-10-03): https://www.teamsterspipeline.com/find-work/ohio/whm-construction-inc-2/. One source. The Williams page gives no length. Straight-line distance between the two points is about 16 miles, which fits a 23.5 mile routed line.

## Maps and filings
- No route map was found. The seed article mentions a Plain Township route map that residents said was too small, but it is not online there. The OPSB case 26-0624-GA-BLN letter of notification (listed on https://www.williams.com/expansion-project/apollo-power-generation-project/) almost certainly holds the map and exact route. Someone with browser access to https://dis.puc.state.oh.us/CaseRecord.aspx?CaseNo=26-0624-GA-BLN should pull it.
- The Williams fact sheet PDF was read and has no map.
