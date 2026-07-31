# Route three-way sync drift — rows NOT from our batches (2026-07-31)

Standing audit: `python scripts/audit_route_sync.py` (findings A–D; see
`docs/sops/route_creation.md` → "The three-way sync rule").

**Context.** The cardinal rule (Baird 2026-07-31) is that `RouteType`,
`RouteAccuracy` and the geometry in `GOIT-GGIT-pipeline-routes` must always
agree. Our own violations were repaired the same day: Egypt gas was already
clean (Baird fixed all 40), **China gas 2026-07-30 had 79 rows with merged
geometry and a stale `RouteType`** — backfilled and verified (backup
`notes/sheet-write-2026-07-31-china-gas-route-type-backfill.csv`).

This memo covers the **26 remaining rows, none of them ours** — other
researchers' work, older imports, and two genuine repo-side problems. Nothing
here has been written. Every row below is a **proposal awaiting Baird**, and
several are not a sync defect at all but a real data conflict that the sync
audit merely surfaced.

Length ratios are geodesic repo length ÷ sheet `LengthKnown` (unit-converted);
the route-integrity gate is [0.75, 1.33].

---

## Group 1 — `RouteType` stale, geometry corroborates the row (11 rows)

Same defect class as our China batch: real geometry is live in the repo,
`RouteAccuracy` is already a real tier, only `RouteType` was never flipped.
**Proposal: set `RouteType = 'Mapped route (at any accuracy)'`.** Mechanical —
no research needed, no other column moves.

| PID | Pipeline | Country | Current RouteType | RouteAccuracy | ratio |
|---|---|---|---|---|---|
| P1012 | Joso Gas Pipeline | Japan | Unavailable (cannot find route) | high | 0.94 |
| P4939 | West-East Gas Pipeline 2 | China | Not mapped | very low | 0.97 |
| P5497 | Brittany South Gas Pipeline | France | Not mapped | high | 0.99 |
| P7099 | Gulf of Guinea Gas Pipeline | Nigeria, Eq. Guinea | Not mapped | very low | 0.91 |
| P7819 | Karachaganak-Uralsk Gas Pipeline | Kazakhstan | Not mapped | very low | 0.92 |
| P6535 | Volodino-Krasnoyarsk Gas Pipeline | Russia | Not mapped | very low | 0.80 |
| P7102 | Nigeria–Libya Gas Pipeline | Nigeria, Niger, Libya | Not mapped | very low | no sheet length |
| P7817 | Taganrog-Mariupol-Berdyansk | Russia, Ukraine | Not mapped | very low | no sheet length |
| P7818 | Taganrog-Mariupol-Berdyansk | Russia, Ukraine | Not mapped | very low | no sheet length |
| P7300 | Ohanet-Gassi Touil LPG (oil) | Algeria | Not mapped | medium | 1.13 |

P1012 is the clearest: `Unavailable (cannot find route)` on a row whose route
*is* in the repo and matches its length to 6%.

## Group 2 — `RouteType` stale AND four rows share one trace (4 rows)

**P4001 / P4002 / P4003 / P4004 — AKG-Ras Laffan Gas Pipeline, Qatar.**
All four are `Not mapped` + `very low (straight line/schematic)`, and all four
geojsons are the **same 51.1 km two-point line**. `RouteType` is wrong on all
four by the same logic as Group 1, but writing `Mapped` four times over one
copied trace states four mapped routes where one schematic line exists.
Sheet `LengthKnown` is blank on all four, so there is no ratio to test against.

**Proposal:** flip `RouteType` on all four (the geometry is genuinely there and
`very low` already tells the truth about its quality), **and** open a separate
segment-vs-network question — are these four real segments that each need their
own trace, or one pipeline over-split in GEM? Do not resolve that here.

## Group 3 — geometry live but `RouteAccuracy` still `no route` (4 rows)

Both route columns are wrong. Setting `RouteType` alone would leave the row
half-synced, and the accuracy tier is a research judgment, not mechanical.

- **P3185 Alliance Gas Pipeline (US)** — ratio 0.98 on a 4.5 km trace, 9
  vertices. Geometry clearly belongs to the row. Proposal: `Mapped` + a real
  tier (looks `medium`/`high`; needs an eyes-on check of the trace).
- **P6531 DeLa Express Pipeline (US, proposed)** — ratio 1.17, **3,068
  vertices**. A detailed, real route sitting on a row that claims `no route`.
  Proposal: `Mapped` + likely `high`. Worth checking provenance first: a
  proposed pipeline with a 3k-vertex trace usually came from a filed FERC/permit
  alignment, which would justify `high`.
- **P2995 Flanders Artery Pipeline (Belgium)** — ratio **0.29** (75.5 km sheet
  vs 21.6 km repo, 151 vertices). The trace is real but covers roughly a
  quarter of the line. This is a **fragment, not a route**. Proposal: do NOT
  flip to `Mapped` — either the repo trace is partial (extend it) or the sheet
  length covers a longer system than this row. Route-integrity call, escalate.
- **P6623 Bordj Ménail-Algiers Gas Pipeline (Algeria)** — ratio **3.95** (58.3
  km sheet vs 230.4 km repo). See Group 4; the geometry is too long to be this
  row's.

## Group 4 — length conflicts: geometry probably does not belong to the row (5 rows)

These fail the ratio gate badly enough that flipping `RouteType` would assert a
mapped route that the evidence does not support. **Proposal: change nothing;
route these to a §5 Update as route-correctness conflicts.**

| PID | Pipeline | sheet | repo | ratio | read |
|---|---|---|---|---|---|
| P5970 | BC Gas Pipeline (Canada) | 39 km | 1,553 km | **39.8×** | the geojson is almost certainly a different (trunk) pipeline, or the row is one spur of a system whose whole trace got attached. Worst offender in the tracker. |
| P6623 | Bordj Ménail-Algiers (Algeria) | 58.3 km | 230.4 km | 3.95× | geometry ~4× the row |
| P7297 | Hassi R'Mel-Arzew LPG I (oil) | 503 km | 777.8 km | 1.55× | — |
| P7298 | Hassi R'Mel-Arzew LPG II (oil) | 492 km | 777.9 km | 1.58× | **P7297 and P7298 carry near-identical geometry** (777.8 / 777.9 km): one trace copied onto both parallel lines. |
| P7299 | Alrar-Hassi R'Mel LPG (oil) | 989 km | 610.1 km | 0.62× | trace covers ~2/3 of the row |
| P7338 | Dekhela-Wadi Al Qamar LPG (Egypt, oil) | 7 km | 4.1 km | 0.59× | 3-vertex sketch on a 7 km line; `RouteType` says `Unavailable` while a trace exists. Low stakes — the ratio miss is ~3 km. Probably a Group-1 flip, but it fails the gate, so flagging rather than assuming. |

Note the Algerian LPG cluster (P7297/P7298/P7299/P7300) came in as one batch and
three of its four rows fail the gate — likely one systematic import problem, not
four independent errors.

## Group 5 — sheet claims a route the repo deliberately does not have (3 rows)

The repo is **right** here and the sheet is stale. Routes repo commit
`dedc8b89` "null p1000 and p1406 routes carrying other projects' geometry
(dabhol-bangalore sketch, telfer trace)" — someone found these two rows holding
*other pipelines'* geometry and correctly nulled them; the sheet's
`RouteType = Mapped` was never walked back. `2163be2c` did the same for P7999.

- **P1000 Fukunan Gas Pipeline (Japan, cancelled)** — `Mapped` + `no route`.
  Proposal: `RouteType` → `Not mapped (but could be…)` or `Unavailable`.
- **P1406 Dongjiakou–Weifang–Luzhong (China, oil)** — same. Proposal: same.
- **P7999 Columbia Gas Transmission (US, proposed)** — `Mapped` + `no route`,
  null route added deliberately. Proposal: same.

`RouteAccuracy` is already `no route` on all three, so this is a one-cell fix
each — but which replacement value is right (`Not mapped` vs `Unavailable`)
depends on whether the route is findable, so it is Baird's call per row.

## Group 6 — two genuine repo-side problems (2 rows)

Not sheet defects. These need a routes-repo action, not a sheet write.

- **P7274 Longhorn Oil Pipeline (US)** — sheet says `Mapped` + **`high`**, but
  the repo file is an **empty placeholder** (commit `561409b7` "adding empty no
  route rows", 142 bytes). The sheet asserts a high-accuracy route that the repo
  has never held. Either a real trace was lost/never uploaded, or the sheet
  attributes an accuracy nobody earned. **A 270-mile US crude line claiming
  `high` accuracy with no geometry is the highest-value row in this memo** —
  recommend resolving it first.
- **P2041 Taproot Baja Pipeline System (US)** — **not a drift finding, a
  filing bug.** The row is on the OIL tab, but its geojson sits in
  `data/individual-routes/gas-pipelines/P2041.geojson` (real 2-point geometry,
  consistent with the sheet's `low`). Separately, **ProjectID P2041 appears on
  BOTH the gas and oil tabs** — that is an identity problem worth its own look.
  Proposal: leave both sheets alone; move/copy the geojson to
  `liquid-pipelines/` in a routes-repo PR, and triage the duplicate ProjectID.

## Group 7 — row never got its route columns filled (1 row)

- **P8030 IGAT 5 Gas Pipeline (Iran)** — `RouteType` and `RouteAccuracy` are
  **both blank**, while the repo holds a 293-vertex trace added by someone else
  from a Drive upload (`87da34fd`). Ratio 0.92 — the geometry fits the row.
  Proposal: `Mapped route (at any accuracy)` + a tier (the vertex count and
  ratio support `high`, pending an eyes-on check). Folds naturally into the
  open Iran gas work (`docs/country_notes/iran.md`).

---

## Recommended order

1. **P7274** (Longhorn) — a `high` claim with no geometry, biggest exposure.
2. **P5970** (BC Gas, 39.8× length) — near-certain wrong-pipeline geometry.
3. **Group 1 + P8030** — 12 mechanical `RouteType` flips, no research.
4. **Group 5** — 3 one-cell corrections, pending Baird's `Not mapped` vs
   `Unavailable` call per row.
5. **Group 3, 4, 6** — real research/repo work; route through §5 Update and a
   routes-repo PR respectively.

Steps 3 and 4 are ~15 cells and can go in one authorized batch via
`apply_route_candidates.py --backfill-route-type` (Group 1) plus a small
one-off for the Group 5 reversals. **Nothing is written without per-row
authorization** — these are other researchers' judgments.
