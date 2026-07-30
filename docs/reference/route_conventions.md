# Pipeline route data — reference

Pipeline route geometry is **not** in the main Google Sheet. It lives as GeoJSON in
a sibling repo and is pulled on demand. This file is the canonical pointer; it
supersedes the old top-level `ROUTE_DATA_REFERENCE.md`.

## Source of truth: public GitHub repo

`https://github.com/GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes`

Files are named `<ProjectID>.geojson` and partitioned by commodity:

```
data/individual-routes/
├── liquid-pipelines/    # oil + NGL   (~2,090 files)
├── gas-pipelines/       # gas         (~4,335 files)
└── hydrogen-pipelines/  # hydrogen    (~360 files)
```

**Local mirror** (Baird's machine, default the engine looks for):
`../GOIT-GGIT-pipeline-routes` (sibling of this repo). Override with
`GEM_ROUTES_REPO`. `scripts/paths.py` resolves it; `scripts/route_compare.py`
reads the mirror first and falls back to `scripts/fetch_route.sh <ProjectID>`
(GitHub code-search + raw download, `routes_cache/`) on a local miss.

### Fetch one route
```bash
./scripts/fetch_route.sh P5367            # -> P5367.geojson
curl -sL "https://raw.githubusercontent.com/GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes/main/{path}" -o route.geojson
```

## Conventions

- **CRS: EPSG:4326** (WGS84 lon/lat). Files may declare the OGC CRS84 URN — same
  thing, lon/lat order.
- Geometry: `LineString` or `MultiLineString`.
- **Geometry can be `null`** (or an empty feature list) — expansions with no new
  pipe, or routes not yet drawn (e.g. `P5367`). Treat null cleanly: no geometry
  signals, **no penalty** in matching.
- Per-file `properties` are inconsistent (`ProjectID`, or `id` + `Name`, or a full
  ESRI property bag) — read **geometry only**, ignore properties.
- **Length:** compute geodesically from the geometry (`pyproj.Geod`), not from any
  embedded projected shape-length field.

## In-sheet route columns

| Column | Meaning |
|---|---|
| `RouteType` | dropdown — match the exact sheet strings (see `controlled_vocab.md`) |
| `RouteAccuracy` | `high` / `medium` / `low` / `no route` / `very high (within meters)` / `very low (straight line/schematic)` |
| `RouteNotes` | map source, endpoint coords, link to the visual map used |
| `Route [ref]` | URL to the best available map source |

### RouteAccuracy assignment ladder
- `high` — digitally traced in GIS, or shapefile/GeoJSON from a reliable source.
- `medium` — not a straight line but not precisely traced (e.g. digitized from a
  press-release map).
- `low` — basic point-A-to-point-B from known endpoints.
- `very low (straight line/schematic)` — a straight line or a schematic trace: it says
  roughly *where* the pipe runs and nothing more.
- `no route` — none available, or a capacity expansion with no new pipe.
- `very high (within meters)` — survey-grade.

**`very low (straight line/schematic)` is the newest value and the largest weak bucket** —
GEM re-graded ~1,428 rows into it (911 gas + 517 oil), mostly from `low`, between the two
2026-07-28 pulls. Any weak-accuracy selector must include it: it was missing from
`build_route_worklist.ELIGIBLE_ACCURACY` and `build_qc_workbook.ROUTE_ACCURACY`, which
silently excluded those rows from route creation and flagged all of them as vocab
violations. Prefer an **allowlist of *good* values** (`route_compare.replacement_candidate`,
`route_integrity._MEDIUM_PLUS`) over a denylist of weak ones — a new weak value then
degrades safely instead of disappearing.

**WKT/route-format QC checks are permanently dropped — do not rebuild route-format
QC** (the QC workbook's old Sheet 10).

## Route reconciliation against scraped datasets (e.g. GulfPub)

A scraped reference dataset (GulfPub) often carries its **own** route geometry. The
reconciliation engine compares it spatially to the GEM route:

- GulfPub routes are treated as **more accurate than `low`/`medium`/`no route` GEM
  routes**. When the geometry is corroborated (buffer-IoU ≥ 0.5 or endpoint match
  ≥ 0.7) and the GEM route is low-accuracy, the engine flags the GEM route as a
  **route-replacement candidate** (surfaced in the `Routes_WKT` sheet + a
  `staged_route_replacements.json` template).
- This **never edits** the routes repo. Replacing a GeoJSON is a separate,
  human-initiated step (new branch + PR against `GOIT-GGIT-pipeline-routes`),
  done only after review.
- **OSM geometry is not interchangeable with GulfPub's here.** It needs a wider
  overlap buffer (10 km vs 2 km) and, being Tier 3, never justifies a replacement on
  its own. It also carries a **licensing** question GulfPub doesn't: ODbL is
  share-alike, so whether OSM-derived coordinates may ship in a GEM route is **Baird's
  call, surfaced end-to-end** (workbook License column) — never the agent's. Reading
  OSM to *corroborate* an attribute is not redistribution; copying its coordinates
  into a GEM route is.
- If the GEM route is already `high`/`very high` and the geometries disagree badly,
  that is a `Route_Conflicts` review item, **not** a replacement.

Spatial metrics and the flag logic: `docs/sops/reconciliation.md` + `route_compare.py`.

## Route suggestions from a deep sweep (weak `RouteAccuracy`)

A Country Sweep `routes` leg (`workflows.md §3`, on request) suggests routes for rows whose
`RouteAccuracy` is `no route` / `low` / `medium`. This is the one route work *in scope* for a
sweep — distinct from route geometry `[ref]` cells (media URLs), which stay out of scope.

- Depth is **corridor + endpoints**: named endpoints + **sourced** lat/lon + a corridor
  description — not a full traced geometry.
- Output is a **candidate** on the `<Cmdty>_RouteSuggestions` tab (staged as `routes[]` on the
  subagent shard; schema in `docs/sops/sweep.md`). It is delivered for a **human routes-repo
  branch + PR**; the agent **never edits `GOIT-GGIT-pipeline-routes`** and **never fabricates
  coordinates** — unsourced coords are null and flagged red.

## Candidate routes (§8 — drawn geometry)

The Route-creation workflow (`workflows.md §8` + `docs/sops/route_creation.md`) goes one
step further than a sweep suggestion: it produces an actual routes-repo-valid
`<ProjectID>.geojson`, walking a **source ladder** whose rung sets the `RouteAccuracy`
cap. Distinct from a sweep suggestion (corridor + endpoints prose, `ROUTE_SUGGESTED` /
`ROUTE_PARTIAL`), which it consumes as input.

- **Method → accuracy cap** (never suggest an accuracy the method can't earn):
  GulfPub sidecar → `high`; ArcGIS / OSM → `high`; digitized (GCP-traced) → `medium`;
  endpoints great-circle → `low`; corridor-only fallback stays `ROUTE_PARTIAL`.
- **Files:** `candidate_routes/<PID>.geojson` (one per PID; multi-segment networks
  merged into one `MultiLineString`); digitization `packets/<PID>/` when a map can't be
  registered below `rmse ≤ max(5 km, 2% of length)`; raw fetched layers in
  `fetched_layers/` (gitignored) each with a `.meta.json` provenance sidecar.
- **No fabricated coordinates** (standing rule 2): lon/lat only from a vector source, a
  fitted georeference transform, or a sourced endpoint. Traces are pixels; GCPs carry
  `source_ref`.
- **OSM/ODbL provenance** rides through to the workbook License column; ODbL
  acceptability is Baird's review call, never the agent's.
- **GOGET/GOGPT facility gazetteer** anchors endpoints internally only — never a
  `[ref]`, never a corroboration source (standing rule 1).
- **Replacement framing:** an existing GEM route → the candidate is flagged
  `replacement=true` (yellow fill); a `high`/`very high` GEM route disagreeing badly is a
  conflict/escalation, never a replacement. A route is **never auto-replaced** — a
  candidate lands in `GOIT-GGIT-pipeline-routes` via a human branch+PR, or via the
  agent only on explicit per-batch authorization (`workflows.md` §8 step 6:
  qc_routes gate + merge, then `scripts/apply_route_candidates.py` for the sheet
  columns); until then it stays staged in this repo. Staged as `ROUTE_CANDIDATE`
  records (schema: `docs/reference/staged_json_schema.md`); rendered on the
  `<Cmdty>_RouteCandidates` tab.
