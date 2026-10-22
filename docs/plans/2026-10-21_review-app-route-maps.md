# Review app: route maps, already-added routes, route provenance (plan, 2026-10-21)

Status: plan only, nothing built. Scope: the pipelines review page (artifact + loopback server) and the shared core in `../gem-review-app`. GOGPT gets the shared pieces and keeps its own point-location panes.

## What Baird asked for

1. Routes already go straight into `GOIT-GGIT-pipeline-routes` (per-batch §8 apply). The review app must detect a route candidate that has already been added and pushed and show it as already added instead of asking for a decision.
2. Every route card shows the candidate geometry on a map, with a toggle between an OSM-style basemap and satellite imagery.
3. A route update (a replacement for a route GEM already has) is staged like any other update: the old route and the new route side by side on maps.
4. The notes and record dropdown says plainly how the route was obtained (scraped from oilandgaswatch.org, traced from a georeferenced map, vectors pulled from a PDF, endpoints joined, and so on), and when a map was used, shows a snapshot of that map for visual comparison.
5. GOGPT will get lat/lon mapping too but will diverge; the backend split and the shared tools are my call.

## What is true today (checked 2026-10-21)

- **The artifact page carries no geometry at all.** `publish.py::geo_bundle` and `A.Store.showGeo` belong to the parked Google version (`trackers/pipelines/web/gas.js`). The static page built by `review_core/build_static.py` has no geo payload, so a route card's geometry link points at `/geo/<dir>/<file>`, which only the loopback server answers. In the artifact it is a dead link. Item 2 therefore starts with getting geometry into the page.
- **Nothing records an apply.** `apply_route_candidates.py --apply` writes the routes repo and the sheet columns but never writes an `applied` marker into the staged record (unlike `append_new_rows.py::mark_applied` and `push.py`, whose `applied.by` the page already understands). Across all route-creation dirs there are 237 `__ROUTE__` records and zero carry an applied marker.
- **Geometry equality is a reliable detector.** Comparing each candidate's coordinates (rounded to 6 decimals) with the routes-repo mirror file: `route-creation-ogw-20261015` 1 of 1 identical, `route-creation-p8318-20261020` 1 of 1, `route-creation-newrows-20261020` 29 of 30 identical and 1 not yet in the repo. The sheet snapshot for an applied row (P8318) shows `RouteType = Mapped route (at any accuracy)`, `RouteAccuracy = medium`, `RouteNotes` starting `CB: route from GIS source`, `RouteCreator = CB`, `Researcher = CB`, `LastUpdated = 2026-10-20`.
- **Replacement candidates exist and are small.** Five records carry `replacement = true` (Israel P0480, P2197; US P7861, P7862 Palo Duro; Libya P6715). The existing repo files for them are 0.3 KB to 8.6 KB. All candidate geojsons together are 436 KB (largest P8092 at 110 KB).
- **Map snapshots are large.** `route-creation-newrows-20261020/maps/` is 460 MB and `traces/` 102 MB; the page limit is 16 MB. Snapshots can never be inlined.
- **Provenance is already recorded, in three places.** The staged record has `method` (`gulfpub_sidecar`, `gis_vector`, `osm`, `digitized`, `endpoints_greatcircle`, `corridor_follow_osm`; 68 older records have none), `source` (name, url, license, fetched time), `georef` (order, GCP count, RMSE, residuals, pass, image path), `proposed_sheet.RouteNotes`, `researcher_notes`. The batch dir has `maps/<PID>/source.json` (document title, page, source URL, date read, fetch route, what the map shows, landmarks, legible) and `traces/<PID>/` (gcps.json, trace.json, georef_report.json, overlay_trace.png, NOTES.md). The OGW batches have `ogw_catalog.csv` and `ogw_crosswalk.csv` with the resolution grade.
- **The GOGPT ext already draws satellite patches** without any map library: Esri World Imagery tiles in a 2 by 2 grid with a crosshair (`trackers/gogpt/web/ext.js` lines 270 to 326, `tileXY`, `locPane`, `locationBlock`), plus a saved map render image and a control-point table. The pipelines ext has `routeBody` (lengths, accuracy, QC chip, geometry link) and hooks `firstRef`, `openRef`, `onCardClick` that send a route line's ref click to `showGeo`. The core exposes `lineBody` and `lineDetails` hooks, so a tracker can replace the body and the dropdown of a line without touching the core.

## Design

### 1. Already added: `applied` on route lines

Two layers, because the past applies left no marker and future ones should.

**Build-time detection** in `review_app/review_data.py::_line` for `kind == "route"`, through a new `review_app/route_state.py`:

- Load the candidate geojson and the routes-repo mirror file for the PID (`scripts/paths.py::gem_route_path`; the gas or liquid subdir by commodity). Compare coordinate lists rounded to 6 decimals. Result: `same`, `differs`, or `missing`.
- Read the newest snapshot row: `RouteType == Mapped route (at any accuracy)`, `RouteAccuracy` non-blank and not `no route`, `RouteNotes` contains `CB: route`, `RouteCreator == CB`.
- When the repo file is `same` and the sheet row is mapped: `line.applied = {"by": "routes_repo", "at": <commit date>, "commit": <short hash>, "sheet": true}`. The commit comes from `git log -1 --format=%H,%cs -- <file>` in the routes repo (read only). The line renders as already added (the same path the page uses for `applied.by == "push"` lines): no decision buttons, a chip reading `already added 2026-10-20`, and it never counts toward the undecided total.
- When the repo file is `same` but the sheet row is not mapped, or `differs` while the sheet says mapped with a CB stamp: the line is held and gets a chip `route and sheet disagree` with the detail in the dropdown. This is finding A of `audit_route_sync.py` surfacing on the card; the fix stays with `apply_route_candidates.py --backfill-route-type` or a re-apply, never with the page.
- `missing`: an ordinary decidable route line, as today.
- For a `replacement` candidate, `same` means the replacement landed; `differs` is the expected pre-apply state and is not a disagreement.

**Write-back at apply time** in `scripts/apply_route_candidates.py --apply`: after the sheet write verifies, write `applied = {"date", "by": "apply_route_candidates", "commit", "plan_token", "backup"}` into the staged record (mirror `append_new_rows.py::mark_applied`, atomic rewrite keeping the file's formatting), and record one machine decision per applied line through the ledger with a new origin `apply` (`review_app/ledger.py::ORIGINS`; the core `review_core/ledger.py` takes the origin from the tracker). The build-time detector keeps running regardless, because the marker is absent on everything applied before this lands. `apply_route_candidates.py --decisions` also skips a line the detector reports as applied, in addition to its existing `CB: route` double-append guard.

`clean_accepts.py` is unaffected: route lines stay held from auto-accept.

### 2. Geometry in the page, and the map

**Payload.** `review_data.py` attaches `line.geo = {"candidate": <FeatureCollection>, "current": <FeatureCollection or null>, "bbox": [w, s, e, n], "length_km", "current_length_km"}`. `current` is the routes-repo mirror geometry (`scripts/route_compare.py::load_gem_route`) whenever the repo has a file for the PID, so a replacement shows both and an already-added line shows what landed. The whole thing rides in the gzipped blob with the rest of the dataset. Budget: the page is 7.9 MB of a 16 MB limit and all candidates together are under half a megabyte, so no simplification is needed. `build_static.py` prints the geo bytes per page and refuses a page whose geo payload exceeds 3 MB, at which point the fallback is to publish the geometry as artifact `files` (`geo/<dir>/<pid>.geojson`) fetched on demand. The loopback server keeps `/geo/` as is.

**Rendering.** Leaflet 1.9.4 from cdnjs, loaded once and lazily the first time a route map scrolls into view (the page's rule that strips local `<script src>` allows `https:` ones; GOGPT already depends on external tile hosts at view time, so the artifact already assumes a network). A route map is a `div.rmap` inside the line body, drawn by a shared `routeMap(el, geo, opts)`:

- Basemap toggle, two buttons on the map, `map` and `satellite`. `map` is Esri World Street Map (CARTO Voyager was planned, but its tiles returned "API key required" when built on 2026-10-21). `satellite` is Esri World Imagery, the tile set and attribution GOGPT already uses. The choice is remembered in localStorage and applies to every map on the page. The OSM tile servers themselves are not used: their usage policy excludes apps like this one.
- The candidate in the tracker accent color, the current route in gray, start and end markers labeled with `start_name` and `end_name`, fit to `bbox` with padding, scroll-wheel zoom only after a click so the page still scrolls.
- If Leaflet fails to load (offline, blocked CDN) the div shows one line, `map did not load`, with the geometry download link, so the card still works.

The existing `showGeo` sketch in `gas.js` stays parked. The `/geo/` link on the card becomes `download geojson`.

### 3. Route updates: old and new side by side

For a line whose `geo.current` exists and whose candidate differs (`replacement = true`, or any candidate for a row the repo already maps), the body shows two panes, `now` and `proposed`, the way GOGPT shows its two satellite patches, each a `routeMap` with its own basemap toggle, views synchronized (moving one moves the other). A third button, `overlay`, collapses them to one map with both routes drawn. Below the panes: current length, candidate length, ratio, `RouteAccuracy` was and suggested, QC chip, exactly the facts `routeBody` shows today. Accepting records approval for the §8 apply with `--replace`, as now; the footer keeps saying it writes no cell.

### 4. How the route was obtained: provenance in the dropdown

**Data.** A `provenance` object on every route line, built by `review_data.py` and, going forward, stamped into the staged record by `build_route_candidate.py::_route_record` so the generator in the app is only a fallback for older records:

- `text`: one short paragraph in plain prose, one sentence per idea, no repo jargon. Written from `method` plus the record. Examples. For `gis_vector` from OGW: "The route was copied from the Oil and Gas Watch record for this pipeline, which the site publishes as a line layer. Oil and Gas Watch grades its own resolution for this line as Medium." For `digitized`: "The route was traced by hand from Figure 1-1 on page 9 of the McCloud Resource Report 1, a PDF filed with FERC in March 2026. The figure was georeferenced with 6 control points, with a fit error of 0.013 km. The trace follows the line as drawn on that figure, so it is only as good as the figure." For `gulfpub_sidecar`: "The route was taken from the Petroleum Economist World Energy Map data (GulfPub) that GEM licenses." For `endpoints_greatcircle`: "No route was found. The line joins the start point and the end point with a straight line and is a placeholder with very low accuracy." For `corridor_follow_osm`: name the OSM way and say what was followed.
- `facts`: a short label and value list the page renders as a table: method (in words), source document (title, page, date read), source URL (linked, the `Route [ref]`), fetch route (what worked, from `source.json`), georeferencing (order, control points, RMSE, pass or fail), OGW resolution grade, license, fetched time, QC result.
- `images`: `[{"role": "map" | "overlay" | "render", "caption", "url", "path", "width", "height", "source_url"}]`. The map is the snapshot the route was traced from (`georef.image`, or each `files[].file` in `maps/<PID>/source.json`); the overlay is `traces/<PID>/overlay_trace.png` where present, which shows the trace on top of the map and is the best single picture for visual comparison.
- `control_points`: from `traces/<PID>/gcps.json` and `georef_report.json`: name, pixel, lon and lat, source ref, residual km. Rendered as a table like GOGPT's.

**Rendering** through the `lineDetails` hook in the pipelines ext: the paragraph first, then the facts table, then the images (click to open full size in a lightbox; the map and the overlay side by side when both exist), then the control-point table, then the existing notes and record block. Prose rules apply: these notes are read by reviewers.

**Older records** with no `method` (68 of 237) get `text` = "How this route was produced was not recorded. The researcher notes say: ..." and the facts the record does have. No guessing.

### 5. Map snapshots as artifact assets

Snapshots never go in the page. A new shared module `review_core/assets.py` plus a thin `review_app/map_assets.py`:

- Collect every image a route line references. Downscale to a JPEG with the long edge at 1600 px, quality 80 (expect 100 to 400 KB each; a PNG overlay with a transparent trace becomes a flattened JPEG over white, or stays PNG under 1 MB). Write to `work/review_assets/<sha256 of the source file>.<ext>` (gitignored).
- `review_app/assets.json` (committed) maps source sha256 to `{"url", "artifact", "uploaded", "bytes"}`. The build fills `images[].url` from it and lists what is still missing.
- Upload is a step in the publish recipe, done with the Artifact tool from the work profile: `asset: true` with `file_paths` (up to 25 per call, 15 MB each) against the page's url, then the returned URLs go into `assets.json` and the page is rebuilt and published. The page must declare the `assets` capability on publish; load the `artifact-capabilities` skill at implementation time for the exact declaration and limits. A brand-new page is published once without images, then assets, then republished.
- `build_all.py --check` reports `assets missing: N` as a reason a page is not fresh; `build_all.py --assets NAME` prints the upload list for the next Artifact call.
- The loopback server serves the same files at `/asset/<sha>.<ext>` from `work/review_assets/` (core `server.py`, since GOGPT's `location_image` needs the same), and the page uses that path when `window.REVIEW_STATIC` is absent.

Expected volume: one to three images per digitized or traced line, none for OGW, GulfPub or endpoints lines, so tens of images per batch, not hundreds.

### 6. What is shared and what is per tracker

Shared, in `gem-review-app/review_core` (the core still names no tracker):

- `web/geo.js` (new, inlined like the other core scripts): tile templates and attributions for Esri World Street Map and Esri imagery, `tileXY` (moved from the GOGPT ext; it mirrors `scripts/geo.py::tile_xy`), the basemap preference, `loadLeaflet()` (one promise, injects the cdnjs script and stylesheet), `routeMap()`, `syncMaps()`, `imageBlock()` with the lightbox, `controlPointTable()`.
- `assets.py`: thumbnail, hash, manifest read and write, the missing-list report.
- `server.py`: the `/asset/` route.
- `docs/plan.md`: a geo section stating the two shared line fields, `line.applied` (any `by`, rendered as done) and `line.provenance.images[].url`, and the two tracker-shaped ones, `line.geo` (pipelines: line geometry) and `line.location` (GOGPT: points).

Per tracker:

- Pipelines ext: `routeBody` becomes the map (one pane or two) plus the facts; `lineDetails` adds the provenance block; chips for `already added` and `route and sheet disagree`.
- GOGPT ext: `locationBlock` keeps its static 2 by 2 satellite patches (a point does not need pan and zoom), imports `tileXY` and the image block from `geo.js`, and can adopt `loadLeaflet()` later for a pin map without any core change. Its `review_data.py` keeps building `location`; it only gains `images[].url` through the shared assets manifest when it wants map renders in the artifact.
- Backends stay in each researcher repo: `review_data.py` builds `geo` and `provenance` (pipelines) or `location` (GOGPT); `route_state.py` is pipelines only.

### 7. Tests

- `pipelines-researcher/tests`: `route_state` on fixtures (same, differs, missing, replacement; sheet mapped and not); provenance text for each method and for a record with no method; `map_assets` (hash, skip already uploaded, missing list); `review_data` route line carries `geo`, `applied`, `provenance` and the page refuses an oversize geo payload.
- `gem-review-app/tests`: `test_core_build.py` accepts the cdnjs Leaflet tag; `tests/js` exercises `tileXY` against known values, `routeMap` with a stubbed `L`, the basemap toggle persisting, and the `already added` rendering of a line with `applied.by = routes_repo`; `test_core_server.py` for `/asset/`.

### 8. Docs to update when built

`review_app/README.md` (route cards, the assets step in the publish recipe, `assets.json`), `docs/sops/route_creation.md` (the review flow section: applied detection, provenance stamped at candidate time, snapshot and overlay files are inputs to the page), `CLAUDE.md` router row for the review app (one line: route maps, already-added detection, assets upload), `gem-review-app/docs/plan.md` (geo section), `gem-review-app/docs/refresh.md` (assets missing as a staleness reason). The memory note "review page sync after push" extends to a §8 apply: an apply is followed by rebuild, publish and mark-published in the same turn.

## Order of work

1. **Geometry into the page and one map with the toggle** (core `geo.js`, blob payload, pipelines `routeBody`). Fixes the dead link in the artifact and is most of the visible win. About half a day.
2. **Already added** (`route_state.py`, `_line`, chips, `mark_applied` and the `apply` ledger origin in `apply_route_candidates.py`, `--decisions` skip). Half a day; the detector is already proven on 31 of 32 US candidates.
3. **Side by side for replacements** (`geo.current`, two panes, sync, overlay). A few hours on top of step 1.
4. **Provenance block and snapshot assets** (`provenance` in `_route_record` and `review_data`, `assets.py`, `map_assets.py`, `/asset/`, `assets.json`, `build_all.py --assets`, the upload step). About a day; the upload step needs the `artifact-capabilities` skill.
5. **GOGPT alignment and docs** (move `tileXY` and the tile constants into `geo.js` with no behavior change; docs above). An hour or two.

Steps 1, 2 and 4 are specified closely enough for a Sonnet subagent each once the shared contract in `docs/plan.md` is written; the contract, the page review and the first publish stay in the main loop.

## Calls made here, say if any should go the other way

- Leaflet from cdnjs rather than a dependency-free tile grid. Pipelines need pan and zoom; the artifact already needs a network for tiles. The fallback line keeps the card usable offline.
- Esri World Street Map as the street basemap. CARTO Voyager was the first pick (OSM-styled), but its keyless tiles now return "API key required" (2026-10-21); OSM's own tiles stay out (usage policy).
- A route-and-sheet disagreement is shown on the card and held, not auto-fixed.
- Snapshots are artifact assets keyed by content hash; the manifest is committed so a rebuild from any session reuses the uploads.
- Provenance prose is stamped at candidate-build time from now on, with the app's generator as the fallback for the 68 records that have no method.
