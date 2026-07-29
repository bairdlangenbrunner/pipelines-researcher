# GulfPub — source notes

## Data files (machine-specific symlinks under `data/`, gitignored)

| Dataset | file `data/…` | source scrape | features | scraped |
|---|---|---|---|---|
| oil | `gulfpub-oil-global.geojson` (symlink) | `gulfpub.SDE.Oil_Pipelines_Global.geojson` | 1,645 | 2026-02 |
| gas | `SDE.NG_Pipelines_Global.geojson` (copied in) | fuller PE World Map SDE scrape (incl. Iraq) | 5,346 | 2025-12-11 |

Both are the December-2025 SDE (PE World Map / Petroleum Economist) scrape from the Esri
Open_Data endpoint. Recreate on a new machine (or set the `path:` in `manifest.yml` to
wherever the files live):

```bash
ln -sf /abs/path/gulfpub.SDE.Oil_Pipelines_Global.geojson   sources/gulfpub/data/gulfpub-oil-global.geojson
cp     /abs/path/SDE.NG_Pipelines_Global.geojson            sources/gulfpub/data/SDE.NG_Pipelines_Global.geojson
```

## Caveats (these drove the manifest)

- **`Shape_STLe` is NOT a length.** Its ratio to the attribute `length` ranges
  0.07–1713 (it's an ESRI projected shape-length in junk units). It's in
  `ignore_garbage_fields`. Real length = the `length`/`Length` attribute; the
  reliable length is `geodesic_km`, computed from the geometry by the engine.
- **Length is in MILES for BOTH oil and gas** — both datasets carry
  `units.length_units: mi`. Gas was misconfigured as `km` until **2026-07-29**; the
  re-confirmation on the Dec-2025 SDE scrape gives median `geodesic_km ÷ Length` = 1.595
  over 5,345 features, 73.7% within 10% of 1.609344 vs 3.1% near 1.0. **Canada is the only
  exception** (median 0.938, n=204 — its block really is km) and is handled by
  `units.length_units_by_country: {Canada: km}`, the per-country override added to the
  manifest schema for exactly this. Sweeping every country at n≥5, no other favours km.
  Do **not** "fix" a suspect length by lowering it back to km — check
  `geodesic_km ÷ Length` per country first. Fixed, re-run and blast radius:
  `notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`. Any gas workbook stamped
  **before 20260729_0941_ET** has `Ref Length (km)` ~38% short (display only — matching
  scores on `geodesic_km`, so no match was ever mis-scored); those five workbooks are
  rebuilt and the pre-fix runs are in `batches/<scope>/archive/…-prefix-gulfpub-gas-miles/`.
- **Oil vs gas schemas differ** (`project_na`/`Project`, `start`/`Start`,
  `start_date`/`Comm_1`, lowercase vs Title-case status) — absorbed by the two
  per-dataset `column_map`s + `status_map`s. This is exactly why the manifest exists.
- **Gas now uses the fuller Dec-2025 SDE scrape** (`SDE.NG_Pipelines_Global.geojson`,
  5,346 features incl. 31 Iraq gas). This replaced the old May-2024 `pe-world-map` file,
  which was capped at 1,000 features and had no Iraq coverage. The gas `column_map` already
  matched the SDE schema (same PE World Map fields), so the repoint was **path + scraped_date
  only**. If an even-newer scrape arrives, repoint `datasets[name=gas].path` again.
- **`Capacity_mmcfd` is a constant `300` placeholder** in the gas schema — it is **not** a real
  capacity and must never be used as a capacity corroboration (bit the Iraq gas sweep).
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
