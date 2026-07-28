# GEM pipeline schema (GOIT oil/NGL + GGIT gas)

How the two live tracker tabs are shaped, and the gotchas that bite every batch.
The column **order** is unreliable — re-derive the column→index map from the fresh
header row every run; never hard-code offsets (the schema drifts).

## The tabs

Backend Google Sheet `1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek`
("Anyone with link can view"). Pull via `scripts/refresh_csvs.sh` (curl).

| Tab | Commodity | GID | Cols | Rows (approx) | Header row |
|---|---|---|---|---|---|
| GOIT (oil/NGL tracker) | crude oil + NGL | `456134080` | 107 | ~2,200 | index 2 |
| GGIT (gas tracker) | gas | `1020144097` | ~140 | ~4,270 | index 2 |
| Pipeline operators/owners | oil **and** gas | `1489950650` | 44 | ~6,466 | **index 1** |

- The two **tracker** tabs: **header at CSV row index 2** (rows 0–1 are metadata);
  load with `pd.read_csv(path, header=2, low_memory=False)`. `SheetRow = CSV index + 4`.
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
- Do **not** use Drive MCP `download_file_content` (first tab only) or
  `read_file_content` (lossy/truncates). curl the CSV export — it is the only
  lossless path.

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
- Length lives in `LengthKnown` / `LengthKnownUnits` (and a km-normalized column).
  For a capacity expansion with **no new physical pipe**: `LengthKnown = 0`,
  `Diameter = blank` (see `docs/sops/update.md`).

## Key column groups (both sheets, names as in the sheet)

Identity: `ProjectID`, `PipelineName`, `SegmentName`, `PipelineNetworkGrouping`,
`OtherEnglishNames`, `Wiki`, `Researcher`, `LastUpdated`.
Classification: `Fuel`, `PipelineType`, `CountriesOrAreas`, `Status`, `Disrupted`.
Physical: `Diameter`, `LengthKnown`, `Capacity` (+ units + `[ref]` each).
Endpoints: `StartLocation` / `StartState/Province` / `StartCountryOrArea`,
`EndLocation` / `EndState/Province` / `EndCountryOrArea` (+ `[ref]`).
Lifecycle/finance: `ProposalYear`, `ConstructionYear`, `StartYear1`, `Cost`,
`FIDStatus`, `FIDYear`, `Opposition`, `Delayed`, `ShelvedCancelledType`.
Route: `RouteType`, `RouteLocation`, `RouteAccuracy`, `RouteNotes`, `Route [ref]`
(geometry itself lives in the routes repo, not the sheet — see
`docs/reference/route_conventions.md`).
Notes: `ResearcherNotes`, `Background` (+ `[ref]`).

The gas sheet mirrors this with gas-specific extras. Re-derive the exact column
list from the fresh header each run.

### Gotcha — `FuelSource` (gas sheet) is the upstream field/plant, not a fuel type
`FuelSource` (+ `[ref]`) names the **upstream gas source feeding the line** — a field,
plant, or facility (e.g. `Abqaiq`, `Haradh`, `Berri Gas Plant`, `Hasbah Gas Field`,
`Safianayh`). It is **not** the commodity/fuel type, so **never fill it with "Natural
Gas"** (that's what `Fuel` already encodes). When researching `FuelSource`, find the
named origin field/facility; if you can't attribute one, leave it blank and note why —
do not default it. (Bit the first wave of the Saudi gas deep sweep; 12 "Natural Gas"
fills had to be dropped.)
