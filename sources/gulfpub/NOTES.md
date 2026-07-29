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
- **Length is in MILES for BOTH oil and gas.** Oil is configured correctly
  (`units.length_units: mi`). **Gas is still configured as `km` and that is WRONG** —
  re-confirmed 2026-07-29 on the Dec-2025 SDE scrape: median `geodesic_km ÷ Length` is
  1.595 over 5,284 features, 74.5% within 10% of 1.609344 and only 3.2% near 1.0, and
  reading Egypt's overlaps as miles lifts GEM agreement from 4% to 29% (±10%) with eight
  hits inside 3%. **Canada is the exception** (median 0.943 — its block really is km), and
  `length_units` is per-dataset with no per-country override, which is why the fix is a
  decision and not yet applied. Full writeup, options and blast radius:
  `notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`. Until it is settled, use the
  `Ref Geodesic (km)` column (computed from geometry, unaffected) and treat every
  `Ref Length` cell in a shipped gas workbook as ~38% short.
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
