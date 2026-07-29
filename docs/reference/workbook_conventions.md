# Output workbook conventions

Every deliverable is a reviewable Excel file the user applies to the live sheet
manually — the agent never writes the Google Sheet or the routes repo to apply a
batch. (Separately authorized one-off sheet fixes exist; they never come through
this path. See `CLAUDE.md`.)

## File naming and location

Written to the scope's `deliverables/` directory in the in-repo `batches/` tree:

```
batches/<country-slug>-<commodity>/deliverables/pipelines_batch_<YYYYMMDD>_<HHMM>_ET[_<scope>]_<mode>.xlsx
```

- `<mode>` (always present): `reconciliation` / `update` / `discovery` /
  `refsweep` / `deepsweep` / `annual-indev` / `qc` / `handoff` / `route-creation`.
- `<scope>` slug (lowercase, hyphenated): a country (`saudi-arabia`), region
  (`mena`), or `<source>-<country>` for reconciliation (`gulfpub-saudi-arabia`).
  Omit only for a genuinely global batch.
- Stamp the timestamp at build time: `TZ=America/New_York date "+%Y%m%d_%H%M_ET"`.
- **Never overwrite** an existing batch file — every (re)build gets a new
  timestamp. When a rebuild supersedes an older workbook (or a batch is applied to
  the sheet), move the old file to the scope's `archive/`; then regenerate
  `batches/INDEX.md` (`python scripts/staged_summary.py --index`). Triage produces
  a markdown memo, not an xlsx.

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

No generic builder yet — recent update batches (`batches/united-states-oil/staging/update-delaware-express/`,
`batches/united-states-oil/staging/update-permian-express/`) shipped via a per-batch `build_update_workbook.py`
staged alongside the JSON: a backend-mirror tab of the touched rows (current values
prefilled, changed cells overlaid tier-colored, per the sweep conventions below)
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

## Country Sweep workbook (mode = `refsweep` / `deepsweep` / `annual-indev`)

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
- **Finding tabs (deep preset):** `<Cmdty>_Validity`, `<Cmdty>_Fills`, and (routes/recon legs)
  `<Cmdty>_RouteSuggestions` plus **one tab per reconciled reference dataset** —
  `<Cmdty>_GulfPub`, `<Cmdty>_OSM`, and any source registered later (discovered by glob over
  `recon_*_crosswalk.json`, never named in the builder). Unmatched reference records are
  grouped **by disposition**, not as one "additions" block.
  The in-dev preset leads with `<Cmdty>_StatusReview`.
  The Fills tab's **`Target tab` column** says where each fill pastes: `tracker`, or
  `operators/owners` for Operator/Owner fills (record `tab="operators_owners"`; the SheetRow
  shown is the tracker locator, but the paste goes to the ProjectID-keyed oo tab).
- **Tier → cell color** (on `[ref]` cells): green = ≥2 independent working sources · yellow =
  single · red = low/none (an empty red cell = "needs a source", **not an error**) · blue =
  existing ref re-verified live.

## Route-creation workbook (mode = `route-creation`)

Built by `build_ref_workbook.py` from a `route-creation-<scope>` staging dir. A single
finding tab, `<Cmdty>_RouteCandidates`, renders the `ROUTE_CANDIDATE` records (drawn
`<PID>.geojson` candidate geometry; destination is the **ROUTES REPO via a human
branch+PR**, never the sheet — see `docs/sops/route_creation.md`).

- **Columns:** ProjectID, SheetRow, PipelineName, SegmentName, Current/Suggested
  RouteAccuracy, Method, Geometry file, Length km / Sheet km / Ratio, Source, **License**
  (ODbL flagged for OSM geometry), Georef RMSE km / GCPs, QC result, **Replacement?**,
  Route IoU / g_score, Packet?, Proposed ref(s), Verification status, Corroboration
  tier, Independent?, Source URL, ResearcherNotes.
- **Color semantics:** tier fill on the Corroboration-tier cell (as elsewhere);
  **yellow** on `Replacement?` when the candidate replaces an existing GEM route (reuses
  the route-replacement-candidate convention); **red** on `QC result` when the gate
  FAILed — a failed gate is listed loudly, never silently dropped. Never color empty
  cells. `Packet?` = yes when digitization couldn't register below the RMSE threshold
  and a `packets/<PID>/` was emitted.
- These records are `class_out="ROUTE_CANDIDATE"` and are split out of the shared route
  bucket (the `RouteSuggestions` tab keeps `ROUTE_SUGGESTED`/`ROUTE_PARTIAL`); a §6
  handoff carries them onto the same tab automatically.

## QC workbook (mode = `qc`)

Rebuild of `GOIT_oil_ngl_QC.xlsx` (and a GGIT equivalent). One sheet per check:
`Status`, `RouteAccuracy`, `OtherVocab`, `Owner_format`, `WikiLink_health`,
`Geo_consistency`, `Name_uniqueness`, `Date_logic`, `Diameter_OutOfRange`,
`BroadSweep_Misc`. **The route/WKT sheet (old Sheet 10) stays permanently dropped.**
Build one sheet at a time for large scopes (token/review budget). Diameter
out-of-range and similar are **review flags, not auto-rejections**.

## Handoff packet (build_ref_workbook, `staged_actions.json` present)

TWO workbooks per country+commodity (split adopted 2026-07-16; workflow recipe:
`docs/workflows.md` §6), derived from the passed `--output`
(`..._handoff.xlsx` → `..._handoff-actions.xlsx` + `..._handoff-evidence.xlsx`).
The split axis is **act vs audit**: everything the researcher must do is in the
actions file, grouped by destination (sheet paste / wiki edit / routes-repo PR /
open judgment calls); everything confirmed / known-staged / info-only is in the
evidence file. No row appears in both.

**`<stem>-actions.xlsx`** — tab order = work order:

`README` → **`<Cmdty>_Decisions`** (read FIRST — every OPEN validity concern for
the scope, carried + this packet's own Leg-3 findings, high-concern rows sorted
first; confirmed verdicts are NOT here) → `<Cmdty>_StatusChanges` (carried + own,
verdict ≠ confirm; confirms are counts-only) → **`<Cmdty>_AllFillsBackend`** (THE
one paste surface for the tracker tab: ALL corroborated fills AND all paste-ready
ref work — REFS_ADDED + DEAD_LINK, carried + own — unified on the full backend
mirror; **no leading `SheetRow` locator** — every column aligns 1:1 with the sheet
so cells copy-paste with no offset, rows located by ProjectID (unlike the sweep
`<Cmdty>_Backend` mirror, which keeps the locator); a tier-colored VALUE cell = a
proposed new value, a colored `[ref]` cell
with an untinted value = ref-only work) → `<Cmdty>_OperatorsOwners` (same, for the
oo tab; owner/operator fills AND refs) → `<Cmdty>_NewRows` / `<Cmdty>_NewRowRefs`
/ `<Cmdty>_MatchedExisting` → `<Cmdty>_WikiUpdates` (flag-severity WIKI_UPDATE
rows only — wiki link leftmost, stale wiki value red, Action column = the edit) →
`<Cmdty>_RouteSuggestions` (carried + own, one tab; routes-repo destination) →
`<Cmdty>_OpenFlags` (the open residue: uncovered mechanical flags, open route
flags, unparseable wiki pages, UNRESOLVED ref units — each with a suggested next
step) → `<Cmdty>_<Source>Actions`, one per reconciled reference dataset
(`<Cmdty>_GulfPubActions`, `<Cmdty>_OSMActions`, …): every unmatched reference
record, every ambiguous match, and only those overlaps where GEM and the dataset
actually **disagree**. A reference route is presumptively real pipe, so the
unmatched rows are proposed additions and proposed geometry — filing all of them
as evidence would be the same failure as the crosswalk being GulfPub-only: the
finding exists and nobody is asked to act on it. Clean overlaps stay in the
evidence file's full `<Cmdty>_<Source>` tab.

**`<stem>-evidence.xlsx`** — audit trail, no action required:

`README` → `<Cmdty>_ConfirmedAudit` (validity checks that cleared the row) →
`<Cmdty>_FillDetail` (per-fill verification detail behind the paste cells) →
`<Cmdty>_RefWorkDetail` (per-ref detail, all buckets, with a `Bucket` column) →
`<Cmdty>_WikiAlignment` (non-action diff context: SHEET_SUSPECT,
WIKI_STALE_VS_STAGED, info-severity) → `<Cmdty>_RouteIntegrity` (covered/info) →
`<Cmdty>_Flags` (covered only) → `<Cmdty>_MonitorList` → the per-source recon tabs
(`<Cmdty>_GulfPub`, `<Cmdty>_OSM`, …).

Empty tabs are omitted; carried rows carry a `Source packet` column (this
packet's own rows say `(this packet)`). Blue notes = already covered; red = open.
Each README names its companion file. Render inputs: `staged_resolutions.json` +
`staged_actions.json` + `qc_flags.json` sidecars (render only — apply from the
source dirs' canonical files; contract in `docs/reference/staged_json_schema.md`).
Legacy qc dirs **without** `staged_actions.json` still render the old
single-workbook layout (Concerns gatekeeper + per-leg tabs).
