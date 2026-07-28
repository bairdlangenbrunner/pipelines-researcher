# Escalation — the `scm/y` / `scm/yr` capacity rows all compute to zero

**Date:** 2026-07-28 (ET) · **Tracker:** GGIT (gas) · **Scope:** tracker-wide (8 rows: 4 Libya, 4 Algeria)
**Origin:** Libya gas deep sweep + reconciliation pass, `batches/libya-gas/`
**Decision owner:** Baird · **Engine never auto-applies — this is a flag, not an edit.**

## The finding

Eight rows in GGIT carry a `CapacityUnits` of `scm/y` (7) or `scm/yr` (1). **All eight
produce a `CapacityBcm/y` of `0.00` or `--`**, so all eight contribute nothing to any
country or global gas-capacity total. Every other scm-family row in the tracker (123 of
them) uses `MMSCMD`, which converts correctly — these 8 are the entire exception.

| ProjectID | Country | Pipeline | Capacity | Units | CapacityBcm/y | CapacityBOEd |
|---|---|---|---|---|---|---|
| P1858 | Libya | Bu-Attifel-Intesar (34in) | 4,134,806 | scm/y | 0.00 | 66.64 |
| P6713 | Libya | Bahr Assalam–Mellitah (10in) | 465,166 | scm/y | 0.00 | 7.50 |
| P6714 | Libya | Bu-Attifel-Intesar (10in) | 258,425 | scm/y | 0.00 | 4.17 |
| P6709 | Libya | Bouri-Bahr Asslam (4in) | 37,213 | scm/yr | `--` | `--` |
| P6616 | Algeria | Sidi Arcine-Blida | 660 | scm/y | 0.00 | 0.01 |
| P6617 | Algeria | Skikda-Khroub | 528 | scm/y | 0.00 | 0.01 |
| P6618 | Algeria | Arzew-Sidi Bel abbès | 330 | scm/y | 0.00 | 0.01 |
| P6620 | Algeria | Skikda-Berrahal | 800 | scm/y | 0.00 | 0.01 |

Every one of the eight cites the **OPEC Annual Statistical Bulletin** (ASB2012 or
ASB2013) as its capacity source, and nothing else non-OPEC except two Algerian rows.

## It is TWO separate defects, and they need different fixes

**1. `scm/yr` is not a unit the conversion recognises at all.** P6709 is the only row
using the `/yr` spelling and it is the only one that returns `--` rather than `0.00` —
the formula converts `scm/y` and does not convert `scm/yr`. That one is a pure
vocabulary-consistency bug: normalise `scm/yr` → `scm/y` and P6709 starts computing.
Worth a controlled-vocab entry so it cannot recur.

**2. The Libya values are 1000× too small, because the ASB's column multiplier was
dropped at ingest.** OPEC ASB Table 4.10's capacity column header reads
**"(1,000 scm/yr)"** — the tabulated figure is *thousands* of standard cubic metres per
year. The rows took the raw cell and labelled it a bare `scm/yr`, losing the ×1000. The
conversion itself is then working correctly on a wrong input: 4,134,806 scm/y really is
0.0041 bcm/y, which rounds to 0.00.

Restoring the factor gives figures that are internally consistent **across three
different diameters**, which is the reason I think this reading is right rather than a
guess:

| PID | Diameter | as-entered | ×1000 → bcm/y | plausible for that diameter? |
|---|---|---|---|---|
| P1858 | 34in | 4,134,806 | **4.13** | yes |
| P6713 | 10in | 465,166 | **0.47** | yes |
| P6714 | 10in | 258,425 | **0.26** | yes |
| P6709 | 4in | 37,213 | **0.037** | yes |

A scaling error that lands every line in a sensible range for its own bore, unprompted,
is unlikely to be coincidence.

**The Algeria four do NOT fit this explanation and must not be fixed the same way.**
660 thousand scm/y is 0.00066 bcm/y — still absurd for a transmission line, so ×1000 is
not the missing factor there. Their ASB figures are either a different column, a
different unit (million scm/y would give 0.33–0.80 bcm/y, which *is* plausible), or not
capacities at all. **Do not apply a blanket ×1000 across all eight rows.** Algeria needs
its own look at the source table before anything is changed.

## Why this is escalated rather than staged as four fixes

It meets the standing gate "a whole class of GEM values looks systematically wrong
(schema misunderstanding, not a finding)". The rows are not individually mis-researched
— they are one ingest that read an ASB table's header wrong, and the same ingest touched
at least two countries. Patching Libya's four in this batch would leave Algeria's four
silently zero and would not stop the next ASB ingest repeating it.

## Recommended disposition

1. **Decide the ASB-multiplier question once** (Libya ×1000 confirmed; Algeria open),
   then correct `Capacity` values — not `CapacityUnits` alone, which would leave the
   magnitude wrong.
2. **Normalise `scm/yr` → `scm/y`** in the controlled vocabulary, or better, convert all
   eight to `MMSCMD` so they join the 123 rows that already work.
3. **Sweep for the sibling case:** any other row citing ASB Table 4.10 for capacity may
   carry the same dropped multiplier regardless of the unit string it ended up with.
4. Libya gas currently reports **303.35 bcm/y across 23 of 38 rows**; adding the four
   Libya rows at their ×1000 values would add ~4.9 bcm/y. Small in aggregate, but the
   four rows read as *zero-capacity pipelines* today, which is worse than a wrong number
   — it is an invisible one.

## The same table produced a second, independent defect

**`notes/escalation-2026-07-28-asb-libya-length-units.md`** — ASB2012 Table 4.10's
*length* column is headed "(miles)", but the Libya block is tabulated in **kilometres**.
The ingest converted anyway, leaving 14 Libya gas lengths 1.609× too long. Same table,
same ingest, adjacent column, opposite direction of error — which is the strongest
argument for treating the ASB ingest itself as the thing to review, not the individual
rows. P1858 appears in both lists. Note the scope difference: the length defect is
provably **Libya-only** (Qatar/Iraq/Saudi convert correctly), whereas this capacity
defect crosses at least Libya and Algeria.

## Related, same batch, separate memo-worthy items

- Three condensate lines are sitting in the **gas** tracker (P6705, P6709, P6713) with
  three different correct dispositions — see `batches/libya-gas/staging/redundancy/`.
- **P0484 Wafa-Mellitah** carries `LengthKnownKm = 5246` against a drawn route of 526 km
  — a live decimal shift in the published tracker.
