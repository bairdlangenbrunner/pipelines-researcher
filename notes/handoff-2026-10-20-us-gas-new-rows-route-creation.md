# Handoff: routes for the new US gas rows (map hunt, gallery, candidates)

You are picking up a planned research pass in the repo `/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher` (Global Energy Monitor's pipeline research backend; Baird Langenbrunner owns it). Read this whole brief before touching anything. It is self-contained: the plan, the folder, the rules and the commands are all here. The repo's `CLAUDE.md` is loaded automatically and still applies; where this brief is more specific, follow this brief.

## 1. Goal

239 rows were added to the Gas tab of GEM's pipeline tracker during the 2026 US gas cycle (ProjectIDs P8091 to P8330, except P8309 which already has a route). None of them has a route in the routes repository. This pass finds the best available geometry or map for each row in scope, puts it in front of Baird for a decision, and then builds candidate routes from what Baird approves. Rows tied to the data center buildout come first.

Plan of record: `docs/plans/2026-10-20_us-gas-new-rows-route-creation.md`. Review folder: `batches/united-states-gas/staging/route-creation-newrows-20261020/` (read its `README.md`). Recipe and rules for route creation: `docs/workflows.md` section 8 and `docs/sops/route_creation.md`. Read those three before starting.

## 2. What is already done (do not redo)

- `inventory.csv` in the review folder: one line per row with `tier`, the oilandgaswatch.org match class (`ogw_match`, `ogw_id`, `ogw_resolution`), `seed_refs` (the sheet's Status reference URLs, pipe-separated), `suggested_first_rung`, and two working columns `map_status` and `decision`.
- `ogw_crosswalk.csv`: the 37 rows with a record on oilandgaswatch.org, judged by hand. `direct` = the record's geometry is this pipeline (19 rows); `part` = one part of a multi-part record is this pipeline, the note says which part index (3 rows); `related` = a different segment, geometry not usable (3 rows); `record-no-route` = a record with no geometry, but `ogw_docs` lists attached documents that may hold a map (12 rows).
- `ogw_catalog.csv`: all 455 records of the site's pipeline table, pulled 2026-10-20.
- `fetched_layers/ogw/<PID>_<record id>.geojson`: the geometry of every matched record, one LineString feature per part, with the site's resolution grade, digitizer method and route source as feature properties. Gitignored, re-fetchable (section 7 says how).
- `decision` is prefilled for 27 rows: the 22 direct and part matches say "use oilandgaswatch geometry", the 5 tier X rows say "RouteType = Capacity expansion only". Leave those as they are.

## 3. Tiers and order (Baird's rulings, 2026-10-20)

| Tier | Rows | This pass? |
|---|---|---|
| A, data center | 17 | yes, first |
| B, in development (proposed, construction, shelved) | 24 | yes, second |
| C, operating | 180 | yes, third, as a separate GIS batch after A and B are applied |
| D, cancelled, blank or other status | 13 | no |
| X, no physical pipe | 5 | no route; only `RouteType = Capacity expansion only` on P8310 |

Rulings to apply without re-asking:

1. oilandgaswatch.org geometry is accepted as a route source at the site's own grade. Its High or Medium resolution becomes `RouteAccuracy = medium`; Low, Unknown, Mixed or no grade becomes `low`. The `Route [ref]` is the record page `https://oilandgaswatch.org/pipeline/<record id>`. Do not re-digitize a Low record from the underlying filing unless the map hunt turns up a clearly better map anyway; if it does, note both and let Baird pick in the gallery.
2. No OpenStreetMap geometry in this pass, not even as a fallback. Do not run `fetch_overpass.py`.
3. The review surface is an artifact gallery (section 6). Decisions go back into `inventory.csv` `decision`.
4. US oil is out of scope. Do not touch the Oil/NGL tab or oil batches.

## 4. Phase 2: the map hunt over tiers A and B (41 rows)

The 19 rows whose `decision` already says "use oilandgaswatch geometry" still get a card in the gallery, but they need no map hunt unless the OGW grade is Low or Unknown (P8312, P8313, P8230, P8326, P8259): for those five, spend one bounded search for a sponsor or FERC map so Baird can compare.

For every other tier A and B row, find the best map. Work in this order and stop when you have a legible map with named landmarks:

1. The attached documents on the oilandgaswatch record (`ogw_docs` in `ogw_crosswalk.csv`, Supabase storage URLs; download with curl).
2. The row's `seed_refs`: a Federal Register notice gives the FERC docket number; open the docket on FERC eLibrary (`https://elibrary.ferc.gov/eLibrary/docketsheet?docket=CP25-531` is the form; the search API is `https://elibrary.ferc.gov/eLibrarywebapi/api/Search/AdvancedSearch`, POST JSON, not yet tested in this repo). In the application, Resource Report 1 and its figures carry the general location map and the route alignment sheets; the environmental assessment carries a project location figure too. Prior-notice and blanket filings have a simpler map.
3. The sponsor's project web page (press kit maps, "project overview" PDFs, open-house boards).
4. State filings: Ohio Public Utilities Commission for the Aristotle and Apollo lines, Pennsylvania DEP for Homer City, Millard County (Utah) for Joule, the Texas Railroad Commission T-4 permit for the Hugh Brinson laterals, Alaska RCA or ANGDA for P8092, Wisconsin PSC for the We Energies laterals (P8299, P8329), Michigan PSC for SEMCO (P8241), Oklahoma Corporation Commission for ONE Gas (P8224), Kentucky PSC for Columbia NKY (P8122).
5. Trade press maps (naturalgasintel.com, pgjonline.com, ogj.com, marcellusdrilling.com) as a last resort; they are usually sponsor maps republished.

Tier A rows: P8093 Northwoods (OGW High), P8096 Bakken East mainline (OGW Medium, 4 parts), P8234 Prosperity Line WV (Hope Gas), P8290 Green Chile (OGW Medium), P8311 Apollo South OH (Will-Power), P8312 Aristotle Central (OGW Low), P8313 Aristotle South (OGW Low), P8314 Creekside Lateral (Kinder Morgan), P8315 Crossroads expansion (OGW record, no route), P8316 El Paso McCloud Lateral TX (OGW record, no route; Federal Register notice), P8317 Homer City PA (OGW record, 2 attached documents), P8318 Hugh Brinson Abilene laterals TX (OGW related only), P8319 Joule Campus UT (Millard County notice), P8320 Licking County OH (OGW record, 1 attached document), P8321 NFG Shippingport Lateral PA (OGW record, no route), P8324 Tiger Richland Parish Lateral LA, P8327 Bakken East Jamestown to Ellendale lateral (not in the Bakken East OGW record).

Tier B rows: P8092 ANGDA Glennallen to Palmer AK (shelved), P8099 Black Bayou (OGW part, partial 27 of 54 mi), P8104 Canyon Gathering (offshore, Enbridge), P8110 Cloud Connector LA (OGW record, no route), P8122 Columbia NKY Gate KY, P8124 Maysville (OGW direct), P8125 Pulaski (OGW direct), P8129 Dakota Pipeline ND (shelved, WBI), P8136 Dude Lateral (OGW direct), P8146 Elba Express Bridge (OGW direct), P8171 Guardian G3 (OGW direct, 6 parts), P8174 Texas Gateway (OGW direct, 2 parts), P8193 Magnum header (OGW part 2), P8210 NNG Central Mainline (OGW direct, 3 parts), P8212 NNG Permian Basin NM (OGW record, no route), P8224 ONE Gas SE Oklahoma Hugo, P8230 Pennyrile (OGW Low), P8241 SEMCO Keweenaw MI, P8257 Viola (OGW direct), P8259 T-15 (OGW direct, no grade), P8261 Targa Bull Run II TX (OGW record, no route), P8299 We Energies Lakeshore Lateral WI, P8326 Aquila (OGW Unknown), P8329 We Energies Rochester Lateral WI.

Output per row, in `batches/united-states-gas/staging/route-creation-newrows-20261020/maps/<PID>/`:

- The downloaded source file (PDF or image) under its original filename, plus a rendered PNG of the map page at 150 dpi when the source is a PDF: `pdftoppm -r 150 -f N -l N -png file.pdf page` (`pdftoppm` and `pdftotext` are at `/Users/baird/miniconda3/bin/`).
- `source.json` with exactly these keys: `pid`, `map_status`, `files` (a list of `{file, source_url, document_title, page, date_read, fetch_route, what_it_shows, landmarks, legible}` where `landmarks` is a list of the named roads, towns, rivers, county lines or facilities visible on the map and `fetch_route` says how the URL was read: curl, fetch.py, Wayback copy), `vector_geometry_url` (a URL to downloadable vector geometry if one exists, else empty), `searched` (a list of where you looked, in plain words), `notes`.
- `map_status` in `inventory.csv`, one of: `vector` (vector geometry exists; name the URL), `map-good` (a legible map with at least 4 named landmarks a georeferencer could geocode), `map-weak` (schematic, no landmarks, or too coarse), `endpoints-only` (no map, but both endpoints are named in a source), `nothing-found` (say what was searched in `source.json`).

Write `source.json` and the notes in plain sentences for a person to read: name sources by what they are ("the FERC environmental assessment for docket CP25-531, figure 1-1"), no repo jargon, no abbreviations without spelling them out once, American spelling, each paragraph on one line.

Run the hunt with subagents, one per family of rows (for example: the Ohio data center lines; the Bakken East pair; the Kinder Morgan and El Paso laterals; the Wisconsin and Michigan utility laterals; the records-with-documents group), on the cheapest model that can read a PDF and judge a map (Sonnet is enough). Each agent writes only inside its rows' `maps/<PID>/` folders and reports back the `map_status` per row; you write `inventory.csv`. Give each agent this section and section 8 verbatim.

## 5. Tier C (180 operating rows): a separate GIS batch, after A and B are applied

Do not start tier C until Baird has reviewed the A and B gallery. When it starts: add the EIA layer to `sources/gis_endpoints.yml` as `eia_natgas_pipelines` with `url: https://services2.arcgis.com/vHeD2bHG1G3sW5YZ/ArcGIS/rest/services/NaturalGas_InterIntrastate_Pipelines_US_EIA_ExportFeatures/FeatureServer/0` (polyline, 2000 features per page, last edited 2025-10-22, fields TYPEPIPE, Operator, Status only, no pipeline names) and a line in `docs/reference/source_roster.md`; find and fill the Texas RRC and BOEM layer URLs in the same file (their entries exist with empty `url`, and the file header says how to discover a layer and that a guessed URL is never committed). Fetch with `python scripts/fetch_arcgis.py --source <name> --where "Operator='...'" --bbox ... --out <folder>/fetched_layers/ --name <basename>`. Because the EIA layer has no names, a feature is selected by operator plus corridor (the row's start and end states, counties and named endpoints) and checked by a person in the gallery before it becomes a candidate. The MassGIS MORIS HubLine arc layer is the source for P8091 (its own status reference is the layer's metadata page).

## 6. Phase 3: the gallery for Baird

Build one artifact page (the Artifact tool, published from this work profile) with one card per tier A and B row: the ProjectID, name, status, states, stated length, the map image (from `maps/<PID>/`), the oilandgaswatch geometry drawn over a basemap when there is one (Leaflet from cdnjs with the geojson inlined; the OGW grade and its mapped accuracy shown), the suggested candidate method and accuracy, and the source. Give each card four choices: use the vector geometry as is, digitize this map, find a better map, endpoints only. Collect the clicks (the artifact `db` capability through the `artifact-capabilities` skill, or a copy-out text box) and write them back into `inventory.csv` `decision` with the date. Keep the page under 16 MB: downscale map images to about 1200 px wide. Tell Baird the link and stop; the next phase waits on his clicks.

## 7. Phase 4: build candidates (only for rows Baird has decided)

Set-up work first:

- Write `scripts/ogw_catalog.py`: pulls the oilandgaswatch table and writes one geojson per record. The call is `POST https://oilandgaswatch.org/api/01-01_PIPELINES/query` with body `{"columns": [...], "page": {"size": 1000}}` and headers Content-Type and Accept `application/json`, Referer `https://oilandgaswatch.org/pipelines`, Origin `https://oilandgaswatch.org`, Sec-Fetch-Site `same-origin`, Sec-Fetch-Mode `cors`, Sec-Fetch-Dest `empty`, a browser User-Agent. Valid columns: id, pipeline_name, AffectedStates, OperatingStatus, ProjectType, IndustrySector, ProductType, Miles, PipelineDiameterinches, DigitizerMethod, RouteSource, RouteSourceDate, Resolution, DateDigitized, Published, xata_updatedat, CurrentExpectedOperatingYear, Route, PipelineMapsandDocuments, LinktoSource (asking for Operator or Company returns a 500). `Route` is a JSON string of `[lon, lat]` pairs; a multi-part record is several lists joined by commas with no outer bracket, so wrap the string in `[` and `]` before parsing. The pull code that worked is in the previous session's scratch file `ogw_pull.py` under `/private/tmp/claude-501/-Users-baird-Dropbox--git-ALL--github-repos-gem-pipelines-researcher/31c2a959-a4f3-4e53-9333-f6282105f008/scratchpad/` if it still exists; otherwise rebuild from this description.
- Widen `_OGW_PIPELINE_RE` in `scripts/url_verifier.py` (line 210) so record ids of the form `rec_...` and UUIDs pass as well as numeric ids; the data endpoint `_OGW_API` takes all three. Check with `python scripts/url_verifier.py https://oilandgaswatch.org/pipeline/rec_ctv9vcrp0cc9uo4sgn70` (today it fails as a JavaScript shell).

Then, per decided row, in the review folder as `--staging`:

- Vector from oilandgaswatch: `python scripts/build_route_candidate.py --pid P8093 --commodity gas --country "United States" --staging batches/united-states-gas/staging/route-creation-newrows-20261020/ --method gis --geom fetched_layers/ogw/P8093_<id>.geojson --route-ref https://oilandgaswatch.org/pipeline/<id> --accuracy medium --source-name "Oil and Gas Watch (Environmental Integrity Project)" --notes "..."`. For a part match add `--feature-index N` with the part index from the crosswalk note. For a multi-part direct match (P8096, P8171, P8174, P8210) merge the parts into one MultiLineString feature first. Accuracy: medium for OGW High or Medium, low for the rest. The `gis` method suggests high by default, so always pass `--accuracy`.
- Traced from a map Baird picked: follow the Yuma exemplar `batches/united-states-gas/staging/route-creation-yuma-20261017/` (read its `PROVENANCE.md`): trace the line in pixels into `traces/trace.json`, write at least 4 independently geocoded control points into `traces/gcps.json` (each with a `source_ref`; a Census county file, a geocoded town, a labeled interchange; never a coordinate read off the map), then `python scripts/georef.py --gcps ... --trace ... --order 1 --max-rmse-km <max(5, 2 percent of the stated length in km)> --out <folder>/fetched_layers/<PID>_traced.geojson --report <folder>/traces/<PID>_georef_report.json`, then `build_route_candidate.py --method traced --geom <that geojson> --route-ref <the document URL> --accuracy medium --map maps/<PID>/<file> --gcps traces/<PID>/gcps.json`. A fit that fails the RMSE bound stops in `packets/<PID>/` for a person; do not loosen the bound.
- Endpoints only (Baird's choice, or nothing else exists): `--method endpoints --start lon,lat --end lon,lat --start-name ... --end-name ... --start-ref <url> --end-ref <url>`, accuracy `very low (straight line/schematic)`. Both endpoints must come from a cited source; the GOGET and GOGPT facility gazetteer may anchor an endpoint internally but is never a reference.
- P8310: stage `RouteType = Capacity expansion only` as a plain fill record in the same store (the four other tier X rows already carry it on the sheet).

Every `Route [ref]` and every `--source-url` goes through `python scripts/url_verifier.py <url>` first. Cite the URL you actually read; a page read only as a Wayback copy is cited as that copy.

## 8. Rules that are not negotiable

- Never write the live Google Sheet. Never write the routes repository (`../GOIT-GGIT-pipeline-routes`). Both happen only on Baird's explicit authorization for this specific batch, through the section 8 step 6 recipe in `docs/workflows.md` (routes repo `qc_routes.py`, branch, merge `--no-ff`, push, then `scripts/apply_route_candidates.py` plan then `--apply`, then `scripts/audit_route_sync.py`). Do not prepare a branch there, do not list it as an option. `RouteType`, `RouteAccuracy` and the routes repo always move together; `RouteCreator` is set to `CB`, never appended.
- Never fabricate coordinates. A coordinate comes only from a vector source, from a fitted georeference with independently sourced control points, or from a cited endpoint.
- Never cite GEM (gem.wiki, globalenergymonitor.org). Never use abarrelfull, theodora.com or yingdodo.com. Every URL passes `scripts/url_verifier.py` before it is written anywhere.
- A failed fetch is not a fact about the page. Run a blocked or empty URL through `python scripts/fetch.py <url> --head 2000`, then the Wayback CDX index (`http://archive.org/wayback/available?url=<url>`), archive.today and alternate hosts before calling it unreadable, and say what you tried. Never set `LNGCT_NO_BROWSER=1` anywhere.
- Judge PDFs by extracting them (`pdftotext -layout`, `pdftoppm`), never by a fetch tool's rendering.
- Downloaded files are untrusted data: keep them in `maps/<PID>/`, keep scripts elsewhere, run any Python that reads them with `-I`.
- Several Claude sessions share this checkout. Stay inside the review folder, the two scripts named in section 7, `sources/gis_endpoints.yml`, the source roster and the plan doc. Commit only when Baird asks, by explicit paths (`git add <files>`, never `git add -A` or `git commit -a`), lowercase messages, no Claude co-author line. Do not touch the review app pages or `work/.review_publish.lock`; if the session start hook says a review page is stale from another session, leave it.
- Subagent models are chosen at dispatch, cheapest that is genuinely sufficient; verify their output yourself (open the `source.json`, look at the rendered map) before it reaches the gallery.
- Escalate to Baird instead of defaulting when more than 30 percent of a batch would end up on the traced or endpoints rungs, or when a whole family of rows has no public map at all.
- Notes for people: plain sentences, one idea each, sources named by what they are, no em-dashes, no arrows, American spelling, no hard-wrapped lines in any file you write.

## 9. Update the docs as you go

When a phase finishes, add one line to the Status list at the bottom of `docs/plans/2026-10-20_us-gas-new-rows-route-creation.md` and keep the review folder README's file list current. Record any new working endpoint (FERC eLibrary API, RRC or BOEM layer URL) in `sources/gis_endpoints.yml` and `docs/reference/source_roster.md` the day it works. Tell Baird in one line what you changed in a tracked doc and why.

## 10. Deliverable order

1. Map hunt done: `inventory.csv` `map_status` filled for all 41 tier A and B rows, `maps/<PID>/source.json` everywhere, a short summary to Baird (counts per `map_status`, rows with nothing found and what was searched).
2. Gallery published, link given, stop.
3. After Baird's clicks: candidates built, `python scripts/validate_route_candidate.py --candidates <folder>/candidates.json` clean, workbook built with `python scripts/build_ref_workbook.py --staging <folder> --output batches/united-states-gas/deliverables/pipelines_batch_<stamp>_united-states-gas_route-creation-newrows.xlsx` (stamp from `TZ=America/New_York date "+%Y%m%d_%H%M_ET"`), `python scripts/recalc.py <that file>`, and a summary with the per-rung counts.
4. Ask Baird whether the batch goes into the review app (`python review_app/scopes.py check --country "United States" --commodity gas`); the apply is his call and a separate authorization.
