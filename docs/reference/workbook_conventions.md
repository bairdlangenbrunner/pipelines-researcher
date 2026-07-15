# Output workbook conventions

Every deliverable is a reviewable Excel file the user applies to the live sheet
manually. The agent never writes to the Google Sheet or the routes repo.

## File naming and location

Written to the in-repo `batches/` directory:

```
batches/pipelines_batch_<YYYYMMDD>_<HHMM>_ET[_<scope>]_<mode>.xlsx
```

- `<mode>` (always present): `reconciliation` / `update` / `discovery` / `qc`.
- `<scope>` slug (lowercase, hyphenated): a country (`saudi-arabia`), region
  (`mena`), or `<source>-<country>` for reconciliation (`gulfpub-saudi-arabia`).
  Omit only for a genuinely global batch.
- Stamp the timestamp at build time: `TZ=America/New_York date "+%Y%m%d_%H%M_ET"`.
- **Never overwrite** an existing batch file — every (re)build gets a new
  timestamp. The user prunes old ones. Triage produces a markdown memo, not an xlsx.

## Universal formatting

- Header row: blue fill `4472C4`, white bold, center-aligned, wrap text.
- **Freeze panes at row 2** (below headers).
- Multiple URLs in a `[ref]` cell: separated by `, ` (comma + space).
- Key columns widened: `PipelineName` 45, `SegmentName` 50, `Status [ref]` 55,
  `Owner` 55, `ResearcherNotes` 55.
- **README sheet always present** with batch params + **per-sheet definitions for
  every other tab** (so the file is self-describing) + input-summary counts +
  any escalation-gate trips. Empty sheets are omitted.

## Color semantics (per cell, not per row)

Standard cells (`Updated`, `New`, reconciliation `Overlaps` Confidence):

- **green** — high confidence (primary/regulatory source or 2+ corroborations)
- **yellow** — entity confirmed but value implied/contested/single non-primary
- **red** — single weak source (prefer blank + a note) **or** a changed cell in an
  update sheet (`FFCCCC` fill / `CC0000` font marks what changed)
- **green tint** `E2EFDA` — a whole discovery/Addition row (new to GEM)
- **blue** `4472C4` — value unchanged but re-verified this batch
- **yellow fill** — a route-replacement-candidate cell

**Never colour an empty cell.** A fill (green tint / tier colour / re-verified blue)
means "this cell holds a value/ref I staged". If a value was searched for and not found,
leave the cell **blank and white** — an empty coloured cell is always a builder bug.
Corollary rules the builders enforce, not just style:
- **A researched value and its `[ref]` travel together** — never a value with no `[ref]`,
  never a `[ref]` with no value (both directions of the no-orphan rule).
- **Links go only in `[ref]` or notes columns — never in a value column.** A URL in
  `Owner`/`Status`/etc. is an error (usually a ref key mis-named without the ` [ref]`
  suffix). Owner/Parent/Operator refs have no main-tracker column → they go on the
  operators/owners tab (`[ref]` precedes its value), not into the value cell.
- **Never emit placeholder strings** like `SYSTEM/NETWORK INFO` into any cell.

See `docs/reference/confidence_tiers.md` for what earns each color.

## Reconciliation workbook (mode = `reconciliation`)

Generalizes `working_files/GOIT_SaudiArabia_Gulfpub_Comparison.xlsx` to any
source / country / commodity. Sheets are per-commodity-prefixed (`Oil_`, `Gas_`):

| Sheet | Contents |
|---|---|
| `README` | params, source + scrape date, color key, per-sheet defs, counts |
| `<Cmdty>_Overlaps` | matched pairs: `Confidence`, `Match reason / notes`, all reference cols (OID, Name, Status, Start, End, Diameter, Length, **Geodesic km (computed)**, Capacity, Operator, StartYear, Description), all matched GEM cols (ProjectID, PipelineName, SegmentName, Status, Diameter, Length, Start/End, Owner, StartYear1, RouteAccuracy, Wiki, `Route present?`), plus `GEM segments` (network-match member list), `Route IoU`, `Route replacement candidate?` |
| `<Cmdty>_Additions` | reference-only rows → **discovery candidates** (GEM cols blank); default red until reviewed |
| `<Cmdty>_GEM_only` | GEM rows in scope with no reference match (ProjectID, names, Status, Fuel, Country, Owner, Diameter, Length, Start/End, StartYear1, Wiki, `Note`) |
| `Status_Conflicts` | status disagreements: ref vs GEM status + `Recommendation` (verify true status — never auto-flip) |
| `Routes_WKT` | reference route geometry as WKT + `Matched GEM ProjectID` + GEM `RouteAccuracy` + `Route IoU` + `Replacement candidate?` |
| `Ambiguous_Clusters` | many-to-many / within-10% ties needing human resolution |

Confidence color is on the `Confidence` cell; route-replacement candidates get a
yellow `Route replacement candidate?` cell. **Findings are candidates, never
auto-applied** — `Additions` route to Discovery, value/status disagreements route
to Update.

## Update workbook (mode = `update`)

No generic builder yet — recent update batches (`batches/staging/delaware-express/`,
`batches/staging/permian-express/`) shipped via a per-batch `build_update_workbook.py`
staged alongside the JSON: a backend-mirror tab of the touched rows (current values
prefilled, changed cells overlaid tier-colored, per the deep-sweep conventions below)
plus an operators/owners tab. If the pattern recurs, promote a generic
`scripts/build_update_workbook.py`.

## Discovery workbook (mode = `discovery`)

Built by `scripts/build_discovery_workbook.py` from merged discovery shards:

1. **`<Cmdty>_NewRows`** — one paste-ready backend-format row per vetted new pipeline;
   verified `[ref]` on every data point (a candidate with zero surviving refs is
   downgraded to the monitor list, never staged as a row).
2. **`<Cmdty>_OperatorsOwners`** — operator/owner refs for the new rows.
3. **`<Cmdty>_MonitorList`** — below-threshold candidates to re-check later.
4. **`<Cmdty>_MatchedExisting`** — candidates matched to an existing GEM row
   (→ `OtherEnglishNames`), not added.

## Ref-sweep / deep-sweep workbook (mode = `refsweep` / `deepsweep`)

Built by `scripts/build_ref_workbook.py`. Two paste-ready tabs lead; bucket/finding tabs follow.

- **`<Cmdty>_Backend` — a 1:1 mirror of the GEM tracker backend, NOT a diff view.** Reproduce
  the **entire backend column set in exact sheet order** (every column, *including* computed/
  formula ones: CapacityBcm/y, LengthKnownKm, DiameterInMm, StartRegion/SubRegion, CostUSD,
  per-km costs, …), **one row per in-scope segment, with the current value prefilled in every
  cell** from the snapshot CSV. Overlay only on *touched* cells: proposed ref(s) on the `[ref]`
  cell (tier-colored) and any proposed value on its value cell. Prepend a single **`SheetRow`**
  locator column (the tracker's row number, not a backend field) and freeze through `ProjectID`.
  - Loaded by `_backend_snapshot(meta)` (full header at CSV row index 2; data rows keyed by the
    composite **`(ProjectID, SheetRow)`**, since a multi-segment ProjectID has >1 row and
    `SheetRow = CSV data-row index + 4`), rendered by `_backend_view`.
  - **Paste-back caveat:** the computed/formula columns hold *snapshot-computed* values — **never
    paste them back over the live-sheet formulas.** Paste only the touched (colored) cells.
  - History: this replaced an earlier touched-columns-only mirror (Iraq `Gas_Backend` had 43 of
    131 cols) after Baird required an exact, full reproduction of the backend.
- **`<Cmdty>_OperatorsOwners`** — mirror of the ProjectID-keyed operators/owners tab (GID
  `1489950650`); `[ref]` column **precedes** its values; paste back by ProjectID, not onto a
  tracker row.
- **Deep-sweep finding tabs:** `<Cmdty>_Validity`, `<Cmdty>_Fills`, and (route/GulfPub legs)
  `<Cmdty>_RouteSuggestions`, `<Cmdty>_GulfPub`. Annual mode leads with `<Cmdty>_StatusReview`.
- **Tier → cell color** (on `[ref]` cells): green = ≥2 independent working sources · yellow =
  single · red = low/none (an empty red cell = "needs a source", **not an error**) · blue =
  existing ref re-verified live.

## QC workbook (mode = `qc`)

Rebuild of `GOIT_oil_ngl_QC.xlsx` (and a GGIT equivalent). One sheet per check:
`Status`, `RouteAccuracy`, `OtherVocab`, `Owner_format`, `WikiLink_health`,
`Geo_consistency`, `Name_uniqueness`, `Date_logic`, `Diameter_OutOfRange`,
`BroadSweep_Misc`. **The route/WKT sheet (old Sheet 10) stays permanently dropped.**
Build one sheet at a time for large scopes (token/review budget). Diameter
out-of-range and similar are **review flags, not auto-rejections**.
