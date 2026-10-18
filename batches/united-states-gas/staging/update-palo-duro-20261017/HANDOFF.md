# Palo Duro update, handoff (2026-10-17)

Started in a gem-desk session and moved here to finish. The new route files for P7861 and P7862 were merged into the routes repo on 2026-10-18 (ae67b0cb), and the matching route cells were written to the sheet the same day with Baird's go ahead (backup `notes/sheet-write-2026-10-18-united-states-palo-duro-route-replacements.csv`). The other changes in this batch have not been written to the sheet.

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
- Workbooks in `batches/united-states-gas/deliverables/`: `pipelines_batch_20261017_1917_ET_united-states_palo-duro_update.xlsx` and `..._newrow.xlsx`.

## Route finding

The traces were redone on 2026-10-17. The Header is one continuous mainline (west end in Roberts County to east end in Washita County) with three branches: a 13 km spur running north near the Texas Oklahoma line, and two very short stubs (about 1.5 km each) that Baird pointed out. The Palo Duro line is traced down the center of the yellow line and shares its top vertex with the Header mainline, so the two lines join. Baird approved both traces.

The first georeference put the Header about 4 km north of the P7861 file. The cause was weak north-south control in the north of the map: the state line there is the straight 100th meridian, which fixes east-west position only, and the Pampa dot was the one other point. The map also draws county lines, so the fit was redone on the county corners the drawn lines confirm. That fit has an error of 0.17 km, and the Header now sits a median 0.47 km from the P7861 file (90th percentile 0.71 km), and the Palo Duro line a median 0.09 km from the P7862 file (90th percentile 0.30 km). One pixel of this map is about 0.55 km.

Both new files replace the old ones. The old P7861 file was eight separate pieces; the new one is one connected line with its branches. The candidate builder caps a map trace at medium accuracy, so P7861 is staged to go from high to medium, and P7862 stays medium. The P7861 trace is 218 km against the sheet's 442.6 km, which the routes QC flags; that is the doubled 275 miles that this batch corrects to 150 miles. The traced Palo Duro line is 377 km against FERC's 275 miles (443 km), so the map may not show its full southern end.

## Open decisions for Baird

1. P7862 pipeline type: staged as "both transmission and gathering". The other choice is to split the row into a northern 61 mile part and a southern 214 mile part.
2. P7861 owner: staged as Producers Midstream (existing entity) to match P7862, with Tailwater Capital as parent. The legal owner per FERC is Palo Duro Pipelines (Texas Gathering).
3. New row status: proposed. Owner Palo Duro Transmission L.P. is a new entity (entity_lookup found no match).
4. Proposal and start years cleared on both old rows, since they belonged to the interstate project. No build year was found for either line.
5. Data center totals: removing the 275 miles from P7861 drops about 443 km from the 10,554 km tagged total.

## Next steps here

1. Baird reviews the two workbooks and the decisions above.
2. On his go ahead for this batch only: apply the P7861 and P7862 changes, then `scripts/append_new_rows.py` for the new row (plan first, read only, then `--apply`).
3. Update the data center stats and the Beyond Carbon notes in gem-desk (`grants/beyond-carbon/`) once the sheet changes land.
