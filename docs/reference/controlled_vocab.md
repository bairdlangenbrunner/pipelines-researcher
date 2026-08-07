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
| `RouteAccuracy` | `high`, `medium`, `low`, `no route` — **plus** two parenthetical values written exactly like that: `very high (within meters)` and `very low (straight line/schematic)`. **Unbuilt rows cap at `medium`** — see below |
| `PipelineType` | `transmission`, `gathering`, `distribution` |

## The remaining vocab fields

**Corrected 2026-08-07.** This table previously called these "Title Case fields" and
gave `Presumed` / `Confirmed` / `Yes`. That was wrong on both counts — re-derived from
the live gas and oil tabs, the columns are lowercase, and the shelved/cancelled value is
the word **`inferred`**, not `Presumed`, which appears nowhere in either tracker.
`FIDStatus` is the only genuinely capitalized one.

| Field | Allowed values | Notes |
|---|---|---|
| `DelayType` | `inferred`, `confirmed` | live counts: 114/138 gas, 37/41 oil (one stray `Assumed` in gas is a data error) |
| `ShelvedCancelledType` | `inferred`, `confirmed` | `inferred` for a GEM-rule dormancy change (no fabricated URL); `confirmed` when a source states it. Live: 84/83 gas, 63/52 oil |
| `FIDStatus` | `Pre-FID`, `FID` | only populated when `Status = proposed`; genuinely capitalized like this |
| `Delayed` | `yes` | leave **blank** if not delayed — do **not** enter `no`. Live: 254 gas / 78 oil, all lowercase |
| `Opposition` | `yes`, `no` | **the sheet is genuinely inconsistent here** — gas holds `no` 66 / `Yes` 46 / `yes` 29 / `No` 26, oil is uniformly lowercase. Write lowercase; do not mass-restyle existing cells without Baird's say-so |

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
- `RouteLocation` — REMOVED from both tabs (2026-07-30): a repo geojson is the
  source of truth; don't stage values for it.

## RouteAccuracy: the unbuilt cap (Baird 2026-08-06)

`high` and `very high (within meters)` are reserved for **pipe that is built, or
whose construction can be traced from satellite imagery**. Any row whose `Status`
is `proposed`, `shelved`, `cancelled`, or `construction` caps at **`medium`**, no
matter how cleanly the route was traced or how authoritative the shapefile was. A
planned or in-progress alignment is not an as-built, so tracing quality can't raise
it above `medium`.

- **In scope of the cap:** `proposed`, `shelved`, `cancelled`, `construction` — all
  four are a mechanical sweep, no per-row judgment.
- **Not in scope:** `operating`, `mothballed`, `idle` (built pipe), and `retired`
  (was built — a traced route stays legitimate).
- **Not in scope:** network-level rows with a blank or `mixed status` `Status`
  (they aggregate operating segments).
- The cap only moves `RouteAccuracy`. It never touches `RouteType` — a downgraded
  row keeps `Mapped route (at any accuracy)`, so the three-way sync rule
  (`docs/sops/route_creation.md`) is unaffected.
- Applied tracker-wide 2026-08-06 in two passes: 268 cells for
  proposed/shelved/cancelled (51 oil, 217 gas) plus 90 cells for `construction`
  (16 oil, 74 gas) = **358 cells**. Backups
  `notes/routeaccuracy-downgrade-20260806-backup.csv` and
  `…-20260806-construction-backup.csv`. The rule is also documented upstream in the
  GOIT/GGIT pipelines manual (RouteAccuracy bullet) and in all three
  `Data dictionary - *` tabs of the backend sheet.
- **Hydrogen is untouched**: the `Hydrogen pipelines` tab had 143 rows matching the
  same pattern as of 2026-08-06 — out of this project's scope, not swept.

## Status-logic conventions (from the research workflow)

- No development updates **2 years** post-proposal → `shelved`.
- No development updates **4+ years** post-proposal → `cancelled`.
- Confirmed cancelled by owner/news → `cancelled` + `ShelvedCancelledType = confirmed`.
- Inferred by the GEM dormancy rule → `ShelvedCancelledType = inferred` (no fabricated URL).
- Date consistency: `Status = operating` ⇒ a `StartYear1` should exist;
  `Status = cancelled` ⇒ a `CancelledYear` (or `StopYear = presumed` for the 4-year rule).

See `docs/reference/confidence_tiers.md` for the green/yellow/red confidence rubric
and `docs/reference/gem_schema.md` for the column-level schema.
