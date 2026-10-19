# Palo Duro update, handoff (2026-10-17)

Started in a gem-desk session and moved here to finish. The new route files for P7861 and P7862 were merged into the routes repo on 2026-10-18 (ae67b0cb), and the matching route cells were written to the sheet the same day with Baird's go ahead (backup `notes/sheet-write-2026-10-18-united-states-palo-duro-route-replacements.csv`). The rest of the batch went to the sheet on 2026-10-18 with Baird's go ahead: the 11 changes to P7861 and P7862 (33 cells, backup `notes/sheet-write-2026-10-18-1013-review-app-push.csv`), the new row as P8330 (73 cells, backup `notes/sheet-write-2026-10-18-1014-append-new-rows-gas.csv`), and a repair of 8 ref links that an old push had broken with a stray space after a comma inside a text fragment (backup `notes/sheet-write-2026-10-18-1015-review-app-push.csv`).

## What Baird asked for

- P7861 (Residue Header): keep the row, make it gathering, remove the data center tag, and fix the length so the 275 miles is not counted twice.
- P7862 (Palo Duro line): operating.
- A third row, appended at the bottom of the gas tab, for the project that turns the existing pipe into interstate service.
- Trace both lines from the company map and show the result.

## What the sources say

The FERC order of March 19, 2026, for docket CP25-531 (`sources/ferc_order_CP25-531_2026-03-19.txt`, from https://www.ferc.gov/sites/default/files/2026-03/CP25-531-000.pdf) is the main source.

- The Header Pipeline is about 150 miles of 16 and 20 inch pipe from Washita County, Oklahoma, to Roberts County, Texas. It belongs to a gathering system of more than 3,000 miles owned and run by Palo Duro Pipelines (Texas Gathering).
- The Palo Duro line is about 275 miles of 16 inch pipe from Nolan County to Wheeler County, Texas. It operates today and gathers gas.
- The project gives interstate service on the northern 61 miles of the Palo Duro line plus 80,000 dekatherms a day of leased Header capacity. The December 2025 amendment keeps the southern part as gathering, to be sold to an affiliate.
- The companies accepted the certificates on April 7, 2026. A FERC eLibrary search on October 17, 2026, found no later tariff filing or start of service notice, so the new row is staged as proposed.

## Files here

- `staged_resolutions.json`: 11 changes to P7861 and P7862. Built by `build_store.py`, so edit that script and rerun it rather than editing the JSON by hand.
- `staged_new.json`: the new row, length 0 and route type "Capacity expansion only" so no pipe is counted twice.
- `traces/`: the company map (`map.jpg`, 600 by 805 pixels; the company serves no larger copy, and the open season PDF of June 2025 carries the same map at 647 by 867), the pixel traces (`trace_palo_duro_v2.json`, `trace_residue_header_v2.json`, written by `retrace.py`), the control points (`gcps_v3.json`, 78 points written by `register_counties.py`: 67 county corners found by fitting the map's drawn county lines to the Census county lines, and 11 points on the Red River state line; town dots kept as check points in `gcps_v3_checkpoints.json`), the georeferenced lines (`palo_duro_v3.geojson`, `residue_header_v3.geojson`, order 2 fit, error 0.17 km, leave one out 0.18 km), the overlays (`overlay_v2_*.png`), the comparison (`compare_routes.py`, `compare_routes.png`, `compare_routes_header.png`), and the cross check against the company's August 2025 asset map (`map_2025_assets_wayback20250822.jpg`, `check_2025_map.py`, `check_2025_map.png`). The older `gcps.json`, `gcps_v2.json` and `*_v2.geojson` files are kept for the record; the v2 fit put the Header about 4 km too far north. The first pass traces (dashed header, affine fit) were deleted on 2026-10-17.
- `../route-creation-palo-duro-20261017/`: the route candidates (`candidate_routes/P7861.geojson`, `P7862.geojson`, each stamped with where it came from by `stamp_provenance.py`), the staged route records, and the sheet plan `apply_route_replacements_plan.json`.
- Workbooks in `batches/united-states-gas/deliverables/`: `pipelines_batch_20261018_0917_ET_united-states_palo-duro_update.xlsx` and `pipelines_batch_20261018_0927_ET_united-states_palo-duro_newrow.xlsx`, rebuilt after Baird's decisions (the new row workbook again once the owner got its FERC ref). The older copies are in `archive/`.

## Route finding

The traces were redone on 2026-10-17. The Header is one continuous mainline (west end in Roberts County to east end in Washita County) with three branches: a 13 km spur running north near the Texas Oklahoma line, and two very short stubs (about 1.5 km each) that Baird pointed out. The Palo Duro line is traced down the center of the yellow line and shares its top vertex with the Header mainline, so the two lines join. Baird approved both traces.

The first georeference put the Header about 4 km north of the P7861 file. The cause was weak north-south control in the north of the map: the state line there is the straight 100th meridian, which fixes east-west position only, and the Pampa dot was the one other point. The map also draws county lines, so the fit was redone on the county corners the drawn lines confirm. That fit has an error of 0.17 km, and the Header now sits a median 0.47 km from the P7861 file (90th percentile 0.71 km), and the Palo Duro line a median 0.09 km from the P7862 file (90th percentile 0.30 km). One pixel of this map is about 0.55 km.

Both new files replace the old ones. The old P7861 file was eight separate pieces; the new one is one connected line with its branches. The candidate builder caps a map trace at medium accuracy, so P7861 is staged to go from high to medium, and P7862 stays medium. The P7861 trace is 218 km against the sheet's 442.6 km, which the routes QC flags; that is the doubled 275 miles that this batch corrects to 150 miles. The traced Palo Duro line is 377 km against FERC's 275 miles (443 km), so the map may not show its full southern end.

## Decisions (Baird, 2026-10-18)

1. P7862 stays one row, typed "both transmission and gathering".
2. P7861 owner is Palo Duro Pipelines (Texas Gathering) LP, the company FERC names as owner. Tailwater Capital is dropped and no parent is staged.
3. The new row is proposed, owned by Palo Duro Transmission LP, with no parent.
4. Proposal and start years are cleared on both old rows.
5. The data center tag comes off P7861, which drops about 443 km from the tagged total.

## Next steps here

1. The Beyond Carbon notes in gem-desk (`grants/beyond-carbon/`) were updated 2026-10-18 with the live data center stats: 41 tagged rows, 10,112 km.
2. Three owner and operator changes from the FERC order went to the sheet on 2026-10-19 with Baird's go ahead (the last three records in `build_store.py`; 8 cells, backup `notes/sheet-write-2026-10-19-0829-review-app-push.csv`). P7861 Operator goes from `Producers Midstream II, LLC` to `Palo Duro Pipelines (Texas Gathering) LP`. P7862 Owner1 goes from `Producers Midstream` to `Palo Duro Transmission LP`, and P7862's blank Operator becomes `Palo Duro Transmission LP`. Footnote 4 of the order says Producers Midstream II is the parent group, two steps above the companies that own and run the pipe. Each change replaces the old ref with the FERC order, and each stamps Researcher CB, since they are research changes, not spelling fixes. A spelling-only accept on the P7861 operator line was put on hold on 2026-10-18 when the line changed.
