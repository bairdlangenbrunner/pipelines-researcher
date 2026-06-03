# GulfPub — source notes

## Data files (machine-specific symlinks under `data/`, gitignored)

| Dataset | symlink `data/…` | points at | features | scraped |
|---|---|---|---|---|
| oil | `gulfpub-oil-global.geojson` | `_gem-docs/mapping/2026-oil/iraq/2026Q1/gulfpub.SDE.Oil_Pipelines_Global.geojson` | 1,645 | 2026-02 |
| gas | `gulfpub-gas-global.geojson` | `GOIT-GGIT-scraping/scraping/pe-world-map/pe-world-map-gas-pipelines-global.geojson` | 1,000 | 2024-05 |

Recreate the symlinks on a new machine (or set the `path:` in `manifest.yml` to
wherever the files live):

```bash
ln -sf /abs/path/gulfpub.SDE.Oil_Pipelines_Global.geojson        sources/gulfpub/data/gulfpub-oil-global.geojson
ln -sf /abs/path/pe-world-map-gas-pipelines-global.geojson       sources/gulfpub/data/gulfpub-gas-global.geojson
```

## Caveats (these drove the manifest)

- **`Shape_STLe` is NOT a length.** Its ratio to the attribute `length` ranges
  0.07–1713 (it's an ESRI projected shape-length in junk units). It's in
  `ignore_garbage_fields`. Real length = the `length`/`Length` attribute; the
  reliable length is `geodesic_km`, computed from the geometry by the engine.
- **Oil length is in MILES** (`units.length_units: mi`); gas appears to be km. The
  geometry-derived `geodesic_km` is the cross-check the matcher prefers, so a wrong
  unit guess degrades gracefully. Re-confirm the gas unit if a fuller gas scrape lands.
- **Oil vs gas schemas differ** (`project_na`/`Project`, `start`/`Start`,
  `start_date`/`Comm_1`, lowercase vs Title-case status) — absorbed by the two
  per-dataset `column_map`s + `status_map`s. This is exactly why the manifest exists.
- **Gas coverage is capped at 1,000 features** (a render/export cap on the May-2024
  pe-world-map file). No fuller gas extract exists on disk (`all-geojsons.zip` holds
  the same files; `query.json` is an unrelated ESRI polygon layer). When a complete
  gas scrape arrives, repoint `datasets[name=gas].path` — the only change needed.
- **OID instability:** `OBJECTID_1` is an ESRI OID that can renumber across scrapes,
  so `oid_stability: unstable`. `ref_id` is `gulfpub:<ds>:<OID>` and is stable
  *within* a scrape; cross-scrape identity should be re-confirmed (a documented
  follow-up, not silently assumed). Records with a blank OID fall back to a content
  hash (`gulfpub:<ds>:h<hash>`).
- **No adapter needed.** GulfPub is fully declarative — owner `(NN%)` strings parse
  via the generic owner parser, capacity comes from the numeric `Capacity_Mbpd` /
  `Capacity_mmcfd` columns, and junk fields are dropped by `ignore_garbage_fields`.
  It's the reference example of the manifest-only common case.

## Validation anchors (Saudi Arabia)
GEM ProjectIDs to eyeball after a Saudi run (from the POC workbook): P0637 (AB-4),
P1972 (Abqaiq Plants–Qatif Junction), P3966 (East–West Gas), P6734 (MGS III).
Status conflicts to expect: P2702 (Al Khafji), P0545 (IPSA).
