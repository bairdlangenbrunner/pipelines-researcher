# Controlled-vocabulary casing (locked)

Casing is **locked** and inconsistent across fields — some are lowercase, some
Title Case. Match it exactly. **When in doubt, pull a real row from the live sheet
and copy the exact string** (`scripts/refresh_csvs.sh`, then `pd.read_csv(path,
header=2)`); never assume Title Case or ALL CAPS for a dropdown field.

These vocabularies are the source of truth for `normalize.py`'s `status_map`
targets and for QC enum checks (`build_qc_workbook.py`). A reference dataset's own
status/type strings are mapped *into* these via its manifest `status_map`.

## lowercase fields

| Field | Allowed values |
|---|---|
| `Status` | `operating`, `proposed`, `construction`, `shelved`, `cancelled`, `idle`, `mothballed`, `retired` |
| `RouteAccuracy` | `high`, `medium`, `low`, `no route` — **plus** two parenthetical values written exactly like that: `very high (within meters)` and `very low (straight line/schematic)` |
| `PipelineType` | `transmission`, `gathering`, `distribution` |

## Title Case fields (the exceptions)

| Field | Allowed values | Notes |
|---|---|---|
| `DelayType` | `Presumed`, `Confirmed` | |
| `ShelvedCancelledType` | `Presumed`, `Confirmed` | `Presumed` for a GEM-rule-inferred status change (no fabricated URL); `Confirmed` when a source states it |
| `FIDStatus` | `Pre-FID`, `FID` | only populated when `Status = proposed` |
| `Delayed` | `Yes` | leave **blank** if not delayed — do **not** enter `No` |
| `Opposition` | `Yes`, `No` | |

## Cost units (all `*CostUnits` fields)

`ProjectLevelCostUnits` / `SegmentCostUnits` / `H2CostUnits` hold a **bare
currency code only** (`USD`, `EGP`, `EUR`, `RMB`, …) — **never a multiplier**
(`EGP million`, `USD (millions)`, `bn`). The magnitude lives in the cost number
itself: a "336 million EGP" source is staged as `ProjectLevelCost = 336000000`,
`ProjectLevelCostUnits = EGP`. The shard merges WARN on multiplier strings
(`merge_qc.bad_cost_units`) — fix the shard, don't hand-edit the merged JSON.

## Free-but-constrained fields

- `RouteType` — match the exact dropdown strings from the sheet, e.g.
  `Not mapped (but could be — route or endpoints are known)`,
  `Mapped route (at any accuracy)`, `Unavailable (cannot find route)`.
  Pull a live row to confirm the current exact strings before populating.
- `RouteLocation` — `Folder` when a GeoJSON has been uploaded to the routes repo;
  blank if not yet created.

## Status-logic conventions (from the research workflow)

- No development updates **2 years** post-proposal → `shelved`.
- No development updates **4+ years** post-proposal → `cancelled`.
- Confirmed cancelled by owner/news → `cancelled` + `ShelvedCancelledType = Confirmed`.
- Inferred by the GEM dormancy rule → `ShelvedCancelledType = Presumed` (no fabricated URL).
- Date consistency: `Status = operating` ⇒ a `StartYear1` should exist;
  `Status = cancelled` ⇒ a `CancelledYear` (or `StopYear = presumed` for the 4-year rule).

See `docs/reference/confidence_tiers.md` for the green/yellow/red confidence rubric
and `docs/reference/gem_schema.md` for the column-level schema.
