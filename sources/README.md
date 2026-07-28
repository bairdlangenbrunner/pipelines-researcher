# Reference-dataset registry

Every scraped pipeline dataset that gets reconciled against GEM is registered here,
one folder per source:

```
sources/
├── _schema/
│   ├── manifest.schema.json     # JSON-Schema every manifest.yml is validated against
│   └── canonical_record.md      # the canonical intermediate schema (ingest output)
├── _template/                   # copy this to start a new source
│   ├── manifest.yml
│   └── adapter.py
├── gis_endpoints.yml            # public GIS layers for §8 route creation — NOT a reconciliation source
├── gulfpub/                     # a real source (tier 2, global extract)
│   ├── manifest.yml             # declarative mapping (column maps, units, status map, geometry)
│   ├── adapter.py               # OPTIONAL — only when the declarative loader isn't enough
│   ├── NOTES.md                 # quirks, scrape date, OID caveats
│   └── data/                    # the raw scrape (gitignored; usually symlinks to ../../GOIT-GGIT-scraping)
└── osm/                         # a real source (tier 3, per-country Overpass pulls; manifest-only)
    ├── manifest.yml
    ├── NOTES.md
    └── data/
```

`scripts/ingest.py` reads `sources/<name>/manifest.yml`, validates it against
`_schema/manifest.schema.json`, and emits **canonical records** (`canonical_record.md`)
that `match.py` / `route_compare.py` / `reconcile.py` consume. The engine is generic;
all per-source knowledge lives in the manifest (+ adapter).

## Config + adapter fallback

- **Manifest-only (the common case):** describe the source declaratively — point
  `path` at the file, map its columns to canonical fields, declare units and a
  status map. No code. The built-in `DeclarativeAdapter` handles it.
- **Adapter (the escape hatch):** add `adapter: adapter.py:MyAdapter` and a small
  `adapter.py` subclassing `AdapterBase` (from `scripts/adapter_base.py`) only when
  the source needs custom parsing — odd geometry joins, a sidecar attribute table,
  reconstructing an OID, parsing `"(NN%)"` owner strings, dropping junk ESRI fields.
  Override just the hooks you need; everything else falls back to declarative.

## Add a new source

1. `cp -r sources/_template sources/<name>` and edit `manifest.yml`.
2. Point `datasets[].path` at the raw file(s). Keep large raw data in
   `sources/<name>/data/` (gitignored) — a symlink to the scrape repo is fine.
   **If the source has no global extract** (e.g. OSM/Overpass), each `datasets[]`
   entry is one scoped pull produced *before* the run by a fetcher
   (`fetch_overpass.py`, `fetch_arcgis.py`) writing into `sources/<name>/data/`.
   Extending coverage to a new country is then one fetch + one `datasets[]` entry,
   still no code.
3. Map columns, set `units`, `status_map`, `source_tier`, `provenance`.
4. Validate + smoke-test: `python scripts/ingest.py --source <name> --commodity oil --out /tmp/<name>/`
   and spot-check `canonical_records.json` against the raw file.
5. Reconcile: `python scripts/reconcile.py --source <name> --country "<C>" --commodity both …`.
   **No engine code changes** — the workflow is identical to GulfPub.
6. Add the source to the registry table in `docs/reference/source_roster.md` with
   its tier, and note quirks in `sources/<name>/NOTES.md`.

A scraped dataset is cited by a non-URL `report_citation` (name + scrape date),
**never** by a GEM URL. A single Tier-2 dataset never reaches green confidence alone
(`docs/reference/confidence_tiers.md`).
