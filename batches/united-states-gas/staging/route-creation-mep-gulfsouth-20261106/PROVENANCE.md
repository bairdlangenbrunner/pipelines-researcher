# Route genealogy — P0213 Midcontinent Express and P5926 Gulf South Southeast Expansion

Both candidates replace existing routes in the routes repo. Both were applied on 2026-11-06 on Baird's authorization: routes repo merge f227f9d0, and the sheet route columns on rows 663 and 3564 (backup in `notes/sheet-write-2026-11-06-united-states-gas-route-replacements.csv`). `audit_route_sync.py` shows both rows in sync. The same lineage is in `route_provenance.json`.

## How the source was chosen

The US Energy Information Administration (EIA) pipeline map was pulled first (`fetched_layers/eia_mep.geojson`, `fetched_layers/eia_gulfsouth.geojson`). It is too generalized to use, with 21 points over 487 miles for MEP, and Baird ruled on 2026-11-06 that it is a last resort. Kinder Morgan's June 2025 segment map for MEP was found next (`maps/MEP_SEGMENT_PIN_MAP-20250410092236.pdf`, from https://pipeline2.kindermorgan.com/Documents/MEP/MEP_SEGMENT_PIN_MAP-20250410092236.pdf). It is a vector PDF with no geographic reference, so it would have to be traced. OpenStreetMap was then pulled with Overpass on 2026-11-06 (`fetched_layers/osm_mep_gulfsouth.json`). It has both lines in detail, tagged with each operator's own line number, so OpenStreetMap was used under Baird's 2026-11-05 exception for lines that are clearly detailed and much better than the other options. The Kinder Morgan map and the EIA line serve as checks.

## P0213 Midcontinent Express Pipeline

The candidate `candidate_routes/P0213.geojson` joins five OpenStreetMap ways, in order from west to east:

- https://www.openstreetmap.org/way/1105967095
- https://www.openstreetmap.org/way/1105967099
- https://www.openstreetmap.org/way/13426782
- https://www.openstreetmap.org/way/1105967084
- https://www.openstreetmap.org/way/256619214

All five are named Midcontinent Express Pipeline, with operator Midcontinent Express Pipeline LLC, line number MEP 0180010000, a start date of 2009, and 42 inch pipe west of Delhi, Louisiana and 36 inch pipe east of it. The joined line (`fetched_layers/osm_P0213.geojson`) has 1,907 points.

- Length: 823.8 km (511.9 miles), against 507.3 miles (816.4 km) on the sheet, a ratio of 1.009.
- Start: Bryan County, Oklahoma, near Bennington (33.933, -96.071).
- End: Transco Station 85 near Butler, Choctaw County, Alabama (32.057, -88.362).
- The current route in the routes repo has 4 points. The new line is 9.3 km from it on average and 23.3 km at most.
- The EIA line is a separate, generalized drawing. The new line is 2.5 km from it on average and 11.9 km at most.
- The Kinder Morgan map was compared by eye (`overlays/mep_gulfsouth_overlay.png` beside `maps/mep_pin_map.png`). It has the same shape: the line runs from Bryan County through Lamar, Red River, Titus, Morris and Cass counties in Texas, bends near Perryville in Lincoln and Ouachita parishes, and crosses Mississippi through Hinds, Rankin, Simpson, Smith, Jasper and Clarke counties to Choctaw County. OpenStreetMap also has short MEP-tagged laterals at the Perryville and Delhi interconnects, which match the delivery points on that map. The laterals are not part of the candidate.

Route references staged (added to the existing Kinder Morgan portal link, which stays): the five way links and the Kinder Morgan segment map.

## P5926 Gulf South Southeast Expansion

The candidate `candidate_routes/P5926.geojson` joins two OpenStreetMap ways:

- https://www.openstreetmap.org/way/834013474
- https://www.openstreetmap.org/way/1107120399

Both are named "Harrisville, MS to Transco Compressor Station", with operator Gulf South Pipeline Company, LLC, line number 818 and a start date of 2008. The joined line (`fetched_layers/osm_P5926.geojson`) has 547 points.

- Length: 178.1 km (110.7 miles), against 111 miles (178.6 km) on the sheet, a ratio of 0.997.
- Start: near Harrisville, Simpson County, Mississippi (32.028, -90.146).
- End: Transco Station 85, Choctaw County, Alabama (32.057, -88.361). This is within about 0.2 km of where the MEP line ends.
- The current route is a straight line with 2 points. The new line is 11.9 km from it on average and 23.3 km at most.
- Boardwalk Pipeline Partners' 2007 annual report (https://www.annualreports.com/HostedData/AnnualReportArchive/b/NYSE_BWP_2007.pdf, already the row's route reference) says the Southeast Expansion starts near Harrisville, Mississippi and ends at an interconnect with Transco Station 85 in Choctaw County, Alabama, and is about 112 miles of 42 inch pipe. FERC approved it on September 28, 2007.

The OpenStreetMap ways do not give a diameter. No company map of this line was found in this pass.

Route references staged (added to the existing annual report link): the two way links.

## Checks and limits

- `validate_route_candidate.py` passed for both. The batch has no worklist, so the gate skipped the length check. The lengths above were checked by hand.
- RouteAccuracy suggested: high for both.
- OpenStreetMap data carries the Open Database License, which asks for credit to OpenStreetMap contributors.
- Applied together, the routes repo and the sheet route columns, per `workflows.md` §8 step 6.
