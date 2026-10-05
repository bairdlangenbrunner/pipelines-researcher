# GEM pipeline schema (GOIT oil/NGL + GGIT gas)

How the two live tracker tabs are shaped, and the gotchas that bite every batch.
The column **order** is unreliable — re-derive the column→index map from the fresh
header row every run; never hard-code offsets (the schema drifts).

## The tabs

Backend Google Sheet `1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek` (work shared drive,
authenticated reads only). Pull via `scripts/refresh_csvs.sh`, which wraps the shared
engine in `../gem-db-ops` (`goit/pull.py`, `ggit/pull.py`).

| Tab | Commodity | GID | Cols | Rows (approx) | Header row |
|---|---|---|---|---|---|
| GOIT (oil/NGL tracker) | crude oil + NGL | `456134080` | 107 | ~2,200 | index 2 |
| GGIT (gas tracker) | gas | `1020144097` | ~140 | ~4,270 | index 2 |
| Pipeline operators/owners | oil **and** gas | `1489950650` | 44 | ~6,466 | **index 1** |

- The two **tracker** tabs: **header at CSV row index 2** (rows 0–1 are metadata);
  load with `pd.read_csv(path, header=2, low_memory=False)`. `SheetRow = CSV index + 4`.
- **Always pass `keep_default_na=False, na_values=[]`.** pandas' default NA list eats
  literal strings this tracker uses as data, and the damage is silent (2026-09-10):
  `Status = "N/A"` — the do-not-research exclusion marker (`controlled_vocab.md`) — read
  back as a blank status on 11 rows, and **`Researcher = "NA"`, Nagwa's initials, read
  back as unattributed on 765 rows across the two tabs** (416 gas + 349 oil), plus 302
  `RouteCreator` cells. A blanked initials cell is exactly the published false
  attribution the initials rule exists to prevent. The core loaders
  (`match.load_gem_df`, `build_ref_worklist._load_indexed`/`_load_owners`,
  `build_qc_staging`, `entity_lookup`) all pass it; so must any new reader.
- **`SheetRow` is positional, so it goes stale whenever the sheet is re-sorted — never
  trust a staged one.** GGIT gas was re-ordered between the 2026-07-04 and 2026-07-05
  pulls (pre-07-05 exports are ProjectID-ascending, starting `P0061`; from 07-05 on they
  start `P4458`), which silently invalidated every locator staged by an earlier leg —
  1,463 of them across two Iraq gas legs, found only because one PID rendered two
  different `SheetRow`s in the same workbook. Two ways it bites: the researcher is sent
  to the wrong row, and a `(ProjectID, SheetRow)` prefill lookup MISSES, so a backend
  mirror row renders identity-only — a paste surface of blanks over live data.
  **Always re-derive from the current CSV, keyed on ProjectID.** `build_ref_workbook.py`
  does this for every record at build time (`_restamp_sheet_rows`) and prints the count;
  any new consumer must do the same rather than reading `sheet_row` from staged JSON.
- **Buffer rows:** ~104 reserved/blank `ProjectID`s exist at the tail of each tracker
  tab. Exclude them from QC and matching (filter to rows with a real `PipelineName`/`Status`).
- **Pull it with `./scripts/refresh_csvs.sh`** (authenticated Sheets `values.get` per tab via
  `gws-gem`, implemented once in `../gem-db-ops/gem_sheets.py` — never re-implement it here).
  The anonymous CSV export died 2026-07-29 and anonymous access to these documents
  is being withdrawn deliberately — don't curl an export URL. Drive MCP is not a substitute
  either: `download_file_content` returns the first tab only and `read_file_content` is
  lossy/truncating. `FORMATTED_VALUE` per-tab reads are the lossless path.

### Pipeline operators/owners tab (GID `1489950650`)
Ownership/operator detail + their source refs, **ProjectID-keyed** (same `ProjectID`s as the
tracker tabs; one tab covers both oil and gas). The tracker tabs carry the `Owner`/`Parent`
*values* but **no `[ref]` column** — the actual reference cells live here.
- **Header at CSV row index 1** (row 0 is a "apply a filter view" banner) — load with `header=1`.
- Two ref-bearing data points, and here the **`[ref]` column PRECEDES its values** (opposite of
  the tracker tabs, where `X [ref]` follows `X`):
  - **`Operator [ref]`** → `Operator`, `OperatorLocalLanguage`, `QCCOwner(业主单位)`.
  - **`Owner [ref]`** → `Owner1`/`Owner1%` … `Owner11`/`Owner11%` (+ `AggregateOwners`,
    `Percentage Verification`).
- So a Ref-Sweep owner/operator candidate for ProjectID *P* is pasted into `Owner [ref]` /
  `Operator [ref]` on **this** tab's *P* row — not a tracker-tab cell, not `ResearcherNotes`.
  Because it's ProjectID-keyed, the ref is per-pipeline (no entity-level de-dup).
- **`Owner1` holds the SPV, not the parent** (Baird ruling 2026-09-15, tracker-wide). When a
  project is sponsored through a joint venture or project company — `Trail West Pipeline, LLC`,
  `Mountain Valley Pipeline, LLC`, a 50/50 JV vehicle — that **named entity** is what goes in
  `Owner1`, even when the sheet currently carries a parent (`Williams Companies`, `TC Energy`)
  and even when the parent is the name in the headlines. The parent relationship is not lost:
  the ownership team builds the parent tree **from** that SPV, which is exactly why the SPV has
  to be the thing recorded. Research stages the SPV and names the parents it found in
  `researcher_notes`; it never flattens the SPV up to its parent, and never invents a tree.
- **Owner names are written the ownership team's way** — full legal name, trailing short legal
  form, no punctuation, no trailing acronym (`Mountain Valley Pipeline LLC`, `Gazprom PJSC`,
  `Ministry of Oil (Iraq)`). Rules, adoption policy and the alias file:
  `docs/reference/owner_style.md`; `scripts/entity_style.py` applies them. Only `Owner1..11` and
  `Owner1%..11%` are data on this tab — `AggregateOwners` / `Percentage Verification` are formulas.
- **Columns A–E are FORMULAS, not data** — `PipelineNetworkContainer`, `PipelineName`,
  `SegmentName`, `Countries`, `Wiki` are each an `iferror(xlookup(F<row>, 'Gas pipelines'!F:F,
  …), xlookup(F<row>, 'Oil/NGL pipelines'!F:F, …))` keyed on `ProjectID` in column **F**, so
  they mirror whatever the tracker tabs hold. A CSV pull renders them as values and hides
  this. **Never write A–E** — fix the tracker-tab cell and the mirror follows. (Caught
  2026-08-05 by the FORMULA pre-read gate during the Wayback `/save/` repair, which found
  `E3392` mirroring Gas row 2437's `Wiki`.)

## Row granularity (matters for reconciliation)

Each row is a pipeline **segment**, not a whole pipeline:

- `PipelineNetworkGrouping` (+ `AltPipelineNetworkGrouping`) groups segments that
  form one physical system.
- `PipelineName` is the system/pipeline name; `SegmentName` distinguishes segments
  (`Pipeline 1`, `Pipeline 2`, …; blank or `--` for a single-segment pipeline).
- A single external-dataset pipeline routinely maps to **many** GEM segment rows
  under one `PipelineNetworkGrouping` (and occasionally the reverse). The matcher
  handles this with dual-level (segment + synthetic-network) matching — see
  `docs/sops/reconciliation.md`.
- **`ProjectID` is NOT unique per row** — a multi-segment pipeline repeats its
  ProjectID across rows (e.g. `P7445` has two segments). Any per-row join back to the
  sheet (the `_Backend` snapshot key, a route match, a status verdict) must key on the
  **composite `(ProjectID, SheetRow)`**, never ProjectID alone.
- **Multi-match length deltas are granularity, not error.** A GEM network row (e.g.
  `P2233`, 438 km) legitimately matches several shorter dataset segments (110/317/88/…);
  the reconcile engine flags these as conflicts/ambiguous, but a human must read them as
  segment-vs-network, not a data defect.

### The aggregate-corridor convention (an aggregate row is not automatically a duplicate)

An aggregate row sitting alongside its own member segments looks like a double-count and
often isn't. **The in-tracker convention** for representing a corridor at both levels
without double-counting is: the aggregate row carries a **blank `Status`** plus a
`PipelineNetworkGrouping` label, so status-filtered totals skip it while the member
segments keep their own status / length / capacity. Verified precedent rows (GGIT,
2026-07-28): `P3656` Moomba Sydney Pipeline System, `P3672` NSW Gas Network, `P3966`
East-West Gas Pipeline and `P5885` MGS III (both `Master Gas System`), `P7150` OQGN.

Two traps when adjudicating one of these clusters (Libya/Iraq redundancy passes):

- **`n/a` is not in the `Status` vocab, and `mixed status` is not a convention** — the one
  row using it (`P6249` Guizhou) is a non-vocab one-off. Don't copy either.
- **Resolve to precedent, not invention**, and cite the precedent rows in the staged
  recommendation. Whichever representation is dropped from an aggregate must be excluded
  from length/capacity totals explicitly, as a family-level decision — never fixed from
  one row's side. Procedure: `docs/sops/sweep.md` §"Two follow-on passes".

## `[ref]` pairing

Most data columns have a paired `X [ref]` source-URL column (`Status` / `Status
[ref]`, `Capacity` / `Capacity [ref]`, …). **Never fill a `[ref]` without a paired
data value, and never leave a researched data value without a `[ref]`** (orphan
rule). Multiple URLs in one `[ref]` cell are separated by `, ` (comma + space).
Every URL must pass `scripts/url_verifier.py` and must not be a GEM surface.
A Wayback ref must be a **snapshot** URL (`web.archive.org/web/<ts>/<url>`), never the
Save Page Now instruction endpoint `web.archive.org/save/<url>` — see the Wayback note in
`docs/reference/source_roster.md`.

## Oil-sheet gotchas

- Column order: **ask Baird to paste the header row** if unsure — the data
  dictionary's `OilOrderInSheet` is unreliable.
- Columns **absent from the data dictionary** (present in the sheet): `Disrupted`,
  `RMI`, `QCCOwner2025Update`, `OwnerEntityIDs`, `AlternateRouteProjectIDs`.
- Cost columns are `Cost`, `CostUnits`, `Cost [ref]` — **not** `ProjectLevelCost`.
- `OtherEnglishNames` — **semicolon-separated** list of alternate English names.
- `Owner` — `--` is a valid sentinel for unknown ownership. Commas / ampersands /
  slashes **inside** an Owner string are legitimate company-name separators (and
  ownership %s like `Saudi Aramco [100.%]`) — do not flag them as defects.
- `Diameter` — frequently **multi-valued and irregularly delimited**: `"46, 48"`,
  `"40/42/48"`, `"56,10,16"`, even `"30, 32, 46, 48, 30, 40, 42"`. Parse on
  `[,/;]`+whitespace into a set; compare by set membership, never equality.
  Diameter mismatches are **review flags, not auto-rejections**.
- Length lives in `LengthKnown` / `LengthKnownUnits` (and a km-normalized column, `LengthKnownKm`, which is computed).
  **Stage length and capacity in the source's own unit** (Baird 2026-10-02): a 1,750-mile source is `1750` + `mi`, not
  `2816.35` + `km`; change `*Units` with the number. Same for `Capacity` (`105.12` + `mill.Sm3/day`, not `38.37` + `bcm/y`).
  Conversion goes in the note only.
  For a capacity expansion with **no new physical pipe**: `LengthKnown = 0`,
  `Diameter = blank` (see `docs/sops/update.md`).

## Key column groups (both sheets, names as in the sheet)

Identity: `ProjectID`, `PipelineName`, `SegmentName`, `PipelineNetworkGrouping`,
`OtherEnglishNames`, `Wiki`, `Researcher`, `LastUpdated`.
Classification: `Fuel`, `PipelineType`, `CountriesOrAreas`, `Status`, `Disrupted`.
Physical: `Diameter`, `LengthKnown`, `Capacity` (+ units + `[ref]` each).
Endpoints: `StartLocation` / `StartState/Province` / `StartCountryOrArea`,
`EndLocation` / `EndState/Province` / `EndCountryOrArea` (+ `[ref]`).
Country / territory / subdivision names (incl. occupied or disputed territory — Crimea and the
Donbas are Ukraine): GEM's naming-conventions sheet, `docs/reference/gem_naming_conventions/`.
Lifecycle/finance: `ProposalYear`, `ConstructionYear`, `StartYear1`, `Cost`,
`FIDStatus`, `FIDYear`, `Opposition`, `Delayed`, `ShelvedCancelledType`.
Route: `RouteType`, `RouteAccuracy`, `RouteNotes`, `RouteCreator`, `Route [ref]`
(geometry itself lives in the routes repo, not the sheet — see
`docs/reference/route_conventions.md`).
Notes: `ResearcherNotes`, `Background` (+ `[ref]`).

The gas sheet mirrors this with gas-specific extras. Re-derive the exact column
list from the fresh header each run.

### Gotcha — `FIDYear` is a planned year too; a past one on a `Pre-FID` row is not a defect
`FIDYear` records the *planned or targeted* FID year as well as the year one was taken (Baird
2026-10-01). A `Pre-FID` row whose `FIDYear` is in the past (AKLNG: `Pre-FID`, `2025`) is a
missed target, not an error. Never raise a validity concern, blank it, or move it to another column
for being past-dated or "not a decision". Only the pairing is checkable: `FID` needs a `FIDYear`
that is the year it was taken, and a `FIDYear` that no source supports as either a target or a
decision is the one ordinary `spec` concern.

### Gotcha — `FuelSource` (gas sheet) is the upstream field/plant, not a fuel type
`FuelSource` (+ `[ref]`) names the **upstream gas source feeding the line** — a field,
plant, or facility (e.g. `Abqaiq`, `Haradh`, `Berri Gas Plant`, `Hasbah Gas Field`,
`Safianayh`). It is **not** the commodity/fuel type, so **never fill it with "Natural
Gas"** (that's what `Fuel` already encodes). When researching `FuelSource`, find the
named origin field/facility; if you can't attribute one, leave it blank and note why —
do not default it. (Bit the first wave of the Saudi gas deep sweep; 12 "Natural Gas"
fills had to be dropped.)
