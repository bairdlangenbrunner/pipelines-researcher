# US gas stale-operating cohort: half the researched SegmentCost values don't survive primary sources

**Date:** 2026-09-04
**Batch:** `batches/united-states-gas/staging/deepsweep-tx-operating/` (45 operating
rows, Texas slice, last touched ≤2023)
**Status:** flagged, nothing changed. Every item below is staged as a `concern` on
`Gas_Validity`, or sits as an `UNRESOLVED` ref unit — no value was edited.

## The finding

16 `SegmentCost` cells were researched. **8 did not survive:**

| | count | what happened |
|---|---|---|
| Sourced and consistent | 8 | ref added, value corroborated |
| **Sourced but materially different** | **2** | P0257, P1297 |
| **No source found at all** | **6** | P0196, P0224, P0290, P0373, P0383, P2499 |

The disagreements are not rounding:

- **P0196 Gulf Crossing** — sheet $121M; Boardwalk Pipeline Partners' FY2006–08 10-Ks
  put actual/estimated cost at **$1.4–1.8bn**. Roughly 10–15×.
- **P0373 Corpus Christi** — sheet $500M; Cheniere's own S-4 and 10-Ks show
  $350–450M estimated, **$375.1–397.7M capitalized**.
- **P0290 Nueva Era** — sheet $500M; the only dated project-financing figure located
  (IJGlobal transaction 35133, Dec 2016) is **$353.4M**.
- **P0257 Sur de Texas-Tuxpan** — TC Energy's own page *and* Mexico's federal project
  database (proyectosmexico.gob.mx) both say **~US$2.1bn**.
- **P1297 Stratton Ridge** — the sheet's $200M appears to be total project cost
  (construction + BIG Pipeline acquisition/lease); PGJ independently reports **$94M**
  for the pipeline construction alone. A scope mismatch, not a wrong number.

## Proven scope — and the control that bounds it

**This is NOT a tracker-wide sourcing defect, and must not be swept as one.**

| scope | `SegmentCost` populated | carries a `[ref]` |
|---|---|---|
| GGIT gas, all countries | 1,359 | **53.3%** |
| US gas, all 529 rows | 263 | 37.3% |
| **this cohort (45 rows)** | 19 | **5.3%** (one cell) |
| *control:* `Capacity`, tracker-wide | 2,664 | 42.7% |

`SegmentCost` is **better** referenced tracker-wide than `Capacity` is, so the column
is not systematically unsourced. The cohort's 5.3% is substantially a **selection
effect**: these 45 rows were chosen precisely because they are operating rows last
touched ≤2023.

So the honest claim is narrow and still worth acting on: *among stale rows, when a
cost value is finally checked against primary sources, it fails about half the time.*
That is a prediction about the remaining ~4 batches of the 217-row stale cohort, not
a verdict on the column.

## What is owed

- These 8 are Update items, one row at a time — there is no blanket fix, and several
  (P1297) are scope questions rather than wrong figures.
- The 6 unsourceable ones must **not** be blanked. "No public source states this"
  is not "the value is wrong"; project costs are frequently never disclosed
  per-segment.
- Worth deciding: whether a `SegmentCost` that no source can corroborate should carry
  a `ResearcherNotes` marker so the next sweep doesn't re-research it from scratch.
