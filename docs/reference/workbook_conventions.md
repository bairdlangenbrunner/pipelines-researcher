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

## Research workbook (mode = `update` / `discovery`)

Three sheets matching the GEM column structure:

1. **Updated Existing Pipelines** — one row per changed pipeline; carry forward
   unchanged columns; highlight changed/new cells red (`FFCCCC`/`CC0000`).
2. **New Pipelines (Discovery)** — one row per discovery; all populated cells green
   (`E2EFDA`); verified `[ref]` on every data point.
3. **Status Changes Summary** — Pipeline, Segment, Current Status, Recommended
   Status, Key Evidence, Source URL; recommended status highlighted red.

## QC workbook (mode = `qc`)

Rebuild of `GOIT_oil_ngl_QC.xlsx` (and a GGIT equivalent). One sheet per check:
`Status`, `RouteAccuracy`, `OtherVocab`, `Owner_format`, `WikiLink_health`,
`Geo_consistency`, `Name_uniqueness`, `Date_logic`, `Diameter_OutOfRange`,
`BroadSweep_Misc`. **The route/WKT sheet (old Sheet 10) stays permanently dropped.**
Build one sheet at a time for large scopes (token/review budget). Diameter
out-of-range and similar are **review flags, not auto-rejections**.
