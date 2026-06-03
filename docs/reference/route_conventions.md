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
| `RouteLocation` | `Folder` if a GeoJSON is uploaded; blank if not yet created |
| `RouteAccuracy` | `high` / `medium` / `low` / `no route` / `very high (within meters)` |
| `RouteNotes` | map source, endpoint coords, link to the visual map used |
| `Route [ref]` | URL to the best available map source |

### RouteAccuracy assignment ladder
- `high` — digitally traced in GIS, or shapefile/GeoJSON from a reliable source.
- `medium` — not a straight line but not precisely traced (e.g. digitized from a
  press-release map).
- `low` — basic point-A-to-point-B from known endpoints.
- `no route` — none available, or a capacity expansion with no new pipe.
- `very high (within meters)` — survey-grade.

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
- If the GEM route is already `high`/`very high` and the geometries disagree badly,
  that is a `Route_Conflicts` review item, **not** a replacement.

Spatial metrics and the flag logic: `docs/sops/reconciliation.md` + `route_compare.py`.
