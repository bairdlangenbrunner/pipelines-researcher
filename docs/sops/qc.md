# SOP — Quality control

Data-health audit of what's already in GOIT/GGIT. **QC detects; Update fixes** —
findings route to a follow-on Update batch. QC here produces a **workbook** (the
rebuild of `GOIT_oil_ngl_QC.xlsx`, and a GGIT equivalent), unlike LNG's memo-only QC.

## QC workbook sheets (`scripts/build_qc_workbook.py`)

Build **one sheet at a time** for large scopes (token/review budget). Diameter and
similar out-of-range checks are **review flags, not auto-rejections**.

| Sheet | Checks |
|---|---|
| `Status` | values ∈ the locked `Status` vocab; status↔date consistency (operating⇒StartYear; cancelled⇒CancelledYear/presumed) |
| `RouteAccuracy` | values ∈ the locked ladder (incl. `very high (within meters)`) |
| `OtherVocab` | `PipelineType`, `DelayType`, `ShelvedCancelledType`, `FIDStatus`, `Delayed`, `Opposition` casing |
| `Owner_format` | structure sanity — but `--` is valid, and commas/&/slashes/`[NN.%]` inside Owner are legitimate (don't flag) |
| `WikiLink_health` | `Wiki` column links resolve |
| `Geo_consistency` | start/end country fields vs `CountriesOrAreas`; cross-border sanity |
| `Name_uniqueness` | duplicate `PipelineName`/`SegmentName` within a grouping |
| `Date_logic` | year ordering (ProposalYear ≤ ConstructionYear ≤ StartYear1) |
| `Diameter_OutOfRange` | parsed diameter set values outside plausible bounds (flag) |
| `BroadSweep_Misc` | orphan `[ref]` (filled ref / blank value or vice-versa), missing required fields |

**Permanently dropped:** the route/WKT-format sheet (old Sheet 10) — do not rebuild.

## Pre-delivery quality checklist (any doer batch)
1. **URL spot-check** — fetch 3–5 `[ref]` URLs; confirm they resolve and contain the claim.
2. **Expansion length** — every expansion: new pipe? if not, length 0 / diameter blank.
3. **Ownership consistency** — divestiture touched all affected rows.
4. **Status logic** — 2y→shelved, 4y→cancelled; `ShelvedCancelledType` set right.
5. **Date consistency** — operating⇒StartYear; cancelled⇒CancelledYear/presumed.
6. **ResearcherNotes** — every changed row explains what/why/caveats.
7. **No GEM self-citation** — no `[ref]` is a gem.wiki/globalenergymonitor URL.
8. **Corroboration** — confidence tier recorded; single-source flagged medium/low;
   "corroboration" isn't the same story republished or circling back to GEM.

## Escalate
>10% of a spot-check sample unsupported, or a whole class of values looks
systematically wrong → stop and discuss (schema misunderstanding, not a finding).
