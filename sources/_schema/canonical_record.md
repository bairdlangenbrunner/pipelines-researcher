# Canonical record schema

`ingest.py` maps every source (any dataset, any commodity) into a uniform
`CanonicalSegment`. This is what `match.py` consumes. It is GEM-aligned (so the diff
is column-comparable) plus provenance and geometry. Records serialize to
`canonical_records.json` (one array); geometry lives in a separate
`geometry_sidecar.json` keyed by `ref_id` (keeps the records diffable and free of
bulky coordinates).

| Field | Type | Units / vocab | Notes |
|---|---|---|---|
| `ref_id` | str | — | stable id, `"<source>:<dataset>:<oid>"` (e.g. `gulfpub:oil:391`). The dedup key. Falls back to a content hash when the source OID is unstable. |
| `source` | str | — | registry folder name (`gulfpub`) |
| `dataset` | str | — | dataset name within the manifest (`oil` / `gas`) |
| `source_tier` | int | 1–4 | from the manifest; caps confidence (Tier ≥2 can't reach green alone) |
| `commodity` | enum | `oil` `ngl` `gas` `hydrogen` | selects which GEM sheet to match against |
| `country` | str | normalized | via `normalize.normalize_country` |
| `country_raw` | str | — | preserved for display |
| `name` | str | — | source project name |
| `name_norm` | str | — | lowercased, suffix-stripped, diacritic-folded (matching only) |
| `aliases` | list[str] | — | alternate names the source carries (often empty) |
| `status` | enum | GEM lowercase `Status` vocab | mapped via the manifest `status_map` |
| `status_raw` | str | — | the source's original status string |
| `start_loc` | str | — | source start-endpoint string |
| `end_loc` | str | — | source end-endpoint string |
| `start_pt` | [lon,lat] \| null | EPSG:4326 | first vertex of the geometry, when present |
| `end_pt` | [lon,lat] \| null | EPSG:4326 | last vertex of the geometry |
| `diameter_in` | list[float] | inches | parsed multi-value set, unit-converted |
| `diameter_raw` | str | — | preserved |
| `length_km` | float \| null | km | **attribute** length, unit-converted (e.g. miles→km) |
| `length_raw` | str | — | preserved (provenance of the unit quirk) |
| `geodesic_km` | float \| null | km | **computed from geometry** (`pyproj.Geod`), never from a projected shape-length field |
| `capacity` | float \| null | source-native | NOT cross-commodity normalized; display only |
| `capacity_units` | str | — | e.g. `bpd`, `MMcf/d` |
| `capacity_raw` | str | — | preserved |
| `operator` | str | — | source operator string |
| `owners` | list[str] | — | parsed owner list (entity-normalized for matching) |
| `start_year` | int \| null | — | |
| `description` | str | — | source description/scope/notes |
| `has_geometry` | bool | — | true iff a non-null LineString/MultiLineString was loaded |
| `geometry_ref` | str | — | key into `geometry_sidecar.json` (WGS84 GeoJSON geometry) |
| `source_url` | str \| null | — | the source's own link, if any — **never** a GEM URL |
| `report_citation` | str | — | non-URL citation, e.g. `"GulfPub PE World Map, oil, scraped 2024-05-16"` |
| `_raw` | dict | — | the untouched source properties (audit / debugging) |

**Commodity uniformity:** the record is commodity-tagged but otherwise identical
across oil/gas. `capacity` deliberately stays source-native (oil bpd and gas MMcf/d
aren't comparable), while `diameter_in`/`length_km`/`geodesic_km` are normalized to
common units so the matcher never branches on commodity except to pick the GEM
sheet. All per-commodity field-name and unit differences are absorbed by the
manifest, not the engine.
