Registration was not attempted. See packets/P8092/README.md for why: 24 separate scanned sheets, no vector path, and the printed grid is not an independent source of control points.

## Cheap georeference pilot, 2026-10-21 (sheets 2 and 12), stopped

The idea was to fit sheets from public vector data: USGS National Hydrography streams and lakes, and Census roads. The scripts and overlay pictures are in pilot/. The printed grid labels were used only to place the vector data for a rough preview, never as control points.

Sheet 2 is flat tundra with a straight line and few drawn features. The preview overlay put Moose Creek in about the right place, but the other streams on the sheet do not match the national stream data, so no junction could be paired with confidence.

Sheet 12 has a topographic base with lakes and the Glenn Highway. A computer search for the best fit of the national lake outlines onto the sheet did not converge. The best fit left the two Startup Lakes about 400 meters off and with different shapes, so the sheet's base map and the national data were drawn from different sources. The Census road layers returned no Glenn Highway line for this area in the layers tried.

Result: no control point was accepted, because each pairing of a sheet feature with a national data feature would have been a guess. The error limit of 5 km would pass a loose fit, but the accuracy would be low and the control points would not be independent in any real sense. Next best route is a Glenn Highway corridor line or a shapefile request to the state pipeline office.

## Corridor proxy line (2026-10-21)
- What it is: the Glenn Highway centerline from US Census TIGERweb roads (layer 6, features named Glenn Hwy and AK Rte 1), merged into one line. It starts at the Glenn and Richardson Highway junction near Glennallen (-145.475, 62.108) and ends where the Glenn Highway forks near Palmer (-149.249, 61.553). It is 145.5 miles, close to the 148 miles the lease application states.
- What it is not: the surveyed pipeline alignment. The sources say the first 15 miles are on Ahtna land and the route crosses Chitna Pass on an RS-2477 right of way, so the real line leaves the highway in both places. Sheet 12 of the 2005 map shows the pipeline about 1 km from the highway where they run together.
- Accuracy: very low. The line is a stand-in until Alaska DNR supplies the lease alignment for ADL 229297.
- Line file: `glenn_hwy_tiger.geojson` in this folder. Candidate: `candidate_routes/P8092.geojson`, validation gate passed.
