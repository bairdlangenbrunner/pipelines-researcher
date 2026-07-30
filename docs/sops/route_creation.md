# SOP — Route creation (candidate geometry, §8)

Produce candidate route **geometry** — a routes-repo-valid `<ProjectID>.geojson` — for
a pipeline (single PID) or every weak-`RouteAccuracy` row in a country, by walking a
**source ladder** and staging the result for a human branch+PR against
`GOIT-GGIT-pipeline-routes`. The agent **never writes the routes repo or the live
sheet by default** — both happen only on explicit per-batch authorization from Baird
(the agent-apply path in "Review flow" below + `workflows.md` §8 step 6); **no
coordinate is ever fabricated** — every lon/lat exits a vector source, a fitted
georeference transform, or an independently sourced endpoint.

This is distinct from the Country Sweep `routes` leg, which it *consumes*: that leg
suggests **corridor + endpoints prose** (`__ROUTE__` / `ROUTE_SUGGESTED` /
`ROUTE_PARTIAL`); this workflow turns endpoints/corridors into actual drawn geometry
(`ROUTE_CANDIDATE`). A prior sweep suggestion for the PID donates its sourced
endpoints to the endpoints/traced rungs.

## Inputs

- A fresh tracker snapshot (`header=2`) — never work from stale CSVs.
- Scope: `--country <C>` (all weak-`RouteAccuracy` rows) or `--pids P####[,…]`.
- The routes-repo mirror (`../GOIT-GGIT-pipeline-routes`) for the format validator +
  existing-route collision check.
- `data/boundaries/ne_50m_admin_0_countries.shp` (Natural Earth) for the integrity leg.
- The facility gazetteer (GOGET/GOGPT snapshots in `data/`) — endpoint anchors only.
- Optional: GulfPub recon sidecars (`batches/*/staging/recon-*/`) for the rung-1 shortcut.

## The source ladder (the heart)

Try rungs top-down per PID; take the highest rung that yields validated geometry. The
rung sets the **`RouteAccuracy` cap** — never suggest an accuracy the method can't earn.

| Rung | Method (`--method`) | Geometry from | RouteAccuracy cap |
|---|---|---|---|
| 1 | `sidecar` | GulfPub recon `geometry_sidecar.json` (keyed `gulfpub:<cmdty>:<OID>`, matched via that run's `match_diff.json`) | `high` |
| 2 | `gis` / `osm` | ArcGIS-REST FeatureServer/MapServer (`fetch_arcgis.py`) or OSM Overpass (`fetch_overpass.py`) | `high` |
| 3 | `traced` | agent digitization of a published map — GCP-fitted transform of hand-traced pixel polylines (`georef.py`) | `medium` |
| 4 | `endpoints` | great-circle densified line between two **sourced** endpoints | `low` |
| — | (fall back) | if even endpoints can't both be coordinated → leave the sweep's corridor-only `ROUTE_PARTIAL` suggestion, no geometry | — |

**GCP rules (rung 3).** Pick ≥4 ground-control points that are independently
geocodable (labeled cities, junctions, coastline crossings) — the lon/lat comes from
**geocoding the named place, never read off the map image**. Every GCP carries a
`source_ref`. Trace the pipeline as **pixel** polylines only; lon/lat is produced by
the fitted transform, never hand-typed. `georef.py` reports RMSE + leave-one-out
residuals + a condition-number check that refuses collinear/clustered GCPs.

**Registration threshold:** `rmse ≤ max(5 km, 2% of pipeline length)`. Above it, the
transform is not trusted — emit whatever partial geometry is possible AND a
**digitization packet** `packets/<PID>/` (the map file, a README, `gcps.json`
suggestions, the verified refs, the endpoints) so the map can be finished by hand in
QGIS. Registration failure is productive, not a dead end.

**OSM / ODbL.** Every OSM feature carries `{source: "OSM", license: "ODbL",
attribution: "© OpenStreetMap contributors", osm_ids}` end-to-end into the workbook's
License column. Whether ODbL is acceptable for a GEM tracker is **Baird's call at
review** — the workflow surfaces it, never decides it. Disconnected OSM ways stay
separate `MultiLineString` parts — **gaps are never bridged**.

**Facility gazetteer (GOGET/GOGPT) — internal, never citable.** Resolves named
start/end facilities to coordinates (sourced endpoints for the great-circle rung),
supplies snap targets for traced/fetched endpoints, and notes the extraction area /
plant a corridor plausibly serves. These are **GEM databases**: they drive geometry
internally only — **never written to a `[ref]` cell, never counted toward the
2-independent-source corroboration tier** (standing rule 1). Each anchored endpoint
still needs its own independent public `[ref]`. Every gazetteer hit is flagged
`citable: false` and recorded in the candidate's `facility_anchors` block as
provenance/audit, not a citation.

## Sequence (per PID)

1. **Fresh pull**, then build the worklist:
   `build_route_worklist.py --csv … --country … --commodity … --staging …`
   — groups scope by ProjectID (routes-repo files are per-PID; a multi-segment network
   becomes one merged candidate), and gathers existing-route presence + geodesic km,
   prior `__ROUTE__` suggestions, GulfPub sidecar hits, and facility anchors.
2. **Agent map/portal research** (non-script, for rungs 2–3): find the best public GIS
   layer or published map. **Every URL through `scripts/url_verifier.py`** (even ones
   that worked before; GEM URLs rejected). New GIS endpoints get appended to
   `sources/gis_endpoints.yml` + a `source_roster.md` line.
3. **Fetch / trace** per the chosen rung: `fetch_arcgis.py` / `fetch_overpass.py` write
   to `fetched_layers/` (gitignored) with a `.meta.json` provenance sidecar; `georef.py`
   fits the transform and reports RMSE.
4. **Assemble:** `build_route_candidate.py --pid … --method … <inputs>` normalizes the
   geometry (merge → linemerge → strip Z → 6 dp), optionally snaps an endpoint to an
   anchor (refused beyond `--snap-max-km`), writes `candidate_routes/<PID>.geojson`,
   runs the **validation gate**, computes replacement framing + `geometry_signals` vs
   any existing GEM route, and upserts a `ROUTE_CANDIDATE` record into `candidates.json`
   + `staged_resolutions.json`. Each candidate also stages **paste-ready APPEND values**
   for the sheet's route provenance columns (rendered as `Proposed RouteCreator` /
   `Proposed RouteNotes` / `Proposed Route [ref]` on the RouteCandidates tab — Baird
   2026-07-30): `RouteCreator` gets `CB`, `RouteNotes` a per-method stamp ("CB: route
   from gulfpub" / "CB: route guessed from endpoints", override with `--routenote`),
   and `Route [ref]` every verified link that informed the route (`--route-ref`,
   repeatable, plus the endpoint refs) — current cell content is always preserved,
   never overwritten. `--accuracy` accepts the sheet's
   `very low (straight line/schematic)` for pure two-point endpoint lines (below the
   endpoints rung's `low` cap).
5. **Workbook + recalc:** `build_ref_workbook.py --staging … --output …` renders the
   `<Cmdty>_RouteCandidates` tab; then `recalc.py`.

## The validation gate (`validate_route_candidate.py`)

Three legs, on every candidate before delivery. `errors` ⇒ FAIL (red QC cell, listed
not dropped); `warnings` are surfaced but pass.

- **format** — the routes repo's OWN `validate_geojson.validate_file` (imported
  read-only, vendored minimal fallback if the mirror is absent), so a candidate that
  passes here passes the repo's CI: filename `P####.geojson`, valid JSON, single
  Feature or FeatureCollection, WGS84.
- **integrity** — geodesic length vs summed segment `LengthKnownKm`/`LengthMergedKm`
  within `[0.75, 1.33]`; landfall countries ⊆ `CountriesOrAreas ∪ {start, end}`
  (Natural Earth, offshore-lenient); both endpoints inside start/end. **Method-aware:**
  an `endpoints_greatcircle` candidate can't know true routed length or transit
  countries, so length-ratio and unlisted-landfall become **warnings** there, not FAILs.
- **collision** — if GEM already has a route for the PID, the candidate must be flagged
  `replacement=true` (`--replace`); otherwise FAIL (never silently overwrite).

## Output

```
batches/<scope>/staging/route-creation[-<qualifier>]/   # e.g. batches/egypt-gas/staging/route-creation, batches/israel-gas/staging/route-creation-p3620-p3657
  worklist.json
  fetched_layers/                # raw fetched GIS layers + .meta.json (gitignored)
  candidate_routes/<PID>.geojson # THE deliverable — routes-repo-valid (committed)
  packets/<PID>/                 # digitization packets when RMSE fails (committed)
  candidates.json                # rich per-candidate metadata (workbook render input)
  staged_resolutions.json        # ROUTE_CANDIDATE records, meta.mode="route-creation"
```

Workbook: `batches/<scope>/deliverables/pipelines_batch_<stamp>_<scope>_route-creation.xlsx`
(`<stamp>` = `TZ=America/New_York date "+%Y%m%d_%H%M_ET"`; never overwrite).

## Standing rules (echoed)

- **Never write the routes repo or the live sheet without per-batch authorization** —
  candidate geometry is staged in THIS repo; by default the researcher opens the
  branch+PR, and the agent applies only when Baird explicitly authorizes that
  specific batch (see "Review flow" below).
- **Never fabricate coordinates** (rule 2): lon/lat only from a vector source, a fitted
  transform, or a sourced endpoint. Traces are pixels; GCPs carry `source_ref`; never
  hand-adjust output coordinates.
- **A route is never auto-replaced.** An existing GEM route → the candidate is framed as
  a replacement (yellow fill); a `high`/`very high` GEM route disagreeing badly is an
  escalation/**conflict**, never a replacement (mirrors `replacement_candidate()`).
- **GOGET/GOGPT drive geometry internally only** — never a `[ref]`, never a
  corroboration source.
- **OSM/ODbL** provenance rides through end-to-end; the licensing acceptability call is
  Baird's at review.
- **Multi-segment PIDs → one merged file.** Never point a deep-sweep merge
  (`merge_deepsweep_shards.py`) at a route-creation staging dir — it drops `__ROUTE__`
  records on re-merge.

## Pre-delivery checks

Gate clean (or FAILs explicitly listed with red QC cells + a next step); every
candidate geojson passes the routes-repo `validate_geojson.py`; spot-open 2 candidates
in geojson.io / QGIS; optional dress-rehearsal with the routes-repo `qc_routes.py`
(REPORT mode) on `candidate_routes/`; README present; every endpoint `[ref]` verified
and GEM-free. Full checklist: `docs/sops/qc.md`.

## Escalation gates

Stop and report rather than mass-producing weak geometry if: **>30%** of a batch lands
on rung 3/4 (weak sourcing across the country); a candidate is **ODbL-only** geometry
(licensing decision); a replacement is proposed **against a `high`/`very high` GEM
route** (conflict, not replacement); or a whole class of length ratios looks
systematically off (likely a segment-vs-network granularity misread, not a finding).

## Review flow (Baird, after delivery)

**Default (human path):** open candidates in geojson.io / QGIS → branch on
`GOIT-GGIT-pipeline-routes` → run its `qc_routes.py --copy` → PR → then the
sheet-side `RouteAccuracy` / `RouteNotes` / `Route [ref]` land via a separate
§5 Update batch.

**Authorized agent apply (per-batch only; the CLAUDE.md sheet-write carve-out):**
when Baird explicitly authorizes it for a specific batch, the agent runs both
halves itself — routes repo first (qc_routes gate REPORT → `--copy`, WARNs need
an explicit `--include`, positional targets before flags; branch → commit →
`merge --no-ff` → push), then the sheet columns via
`scripts/apply_route_candidates.py` (plan phase → Baird reviews the plan +
backup CSV → `--apply` with readback verification). Appends never overwrite:
RouteNotes gets the CB stamp + " — " + researcher notes, RouteCreator gains
`CB` (gas tab only — the oil tab has no RouteCreator column), Route [ref]
gains only URLs not already present; RouteAccuracy must currently be
`no route`. Authorization never carries to the next batch. Recipe:
`docs/workflows.md` §8 step 6; first use Egypt gas 2026-07-30.

## Iterate

Expect Baird to challenge specific candidates. Acknowledge, re-source, regenerate —
**do not defend** wrong geometry (standing rule 3).
