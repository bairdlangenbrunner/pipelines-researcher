# Escalation — `route_integrity.py`'s length_ratio check reported the accuracy tier, not a defect

**Date:** 2026-08-12
**Found in:** Malaysia gas §6 handoff, Leg 2 (3 of 4 routed rows flagged `length_ratio`)
**Fixed in:** `scripts/route_integrity.py` (`_RATIO_BANDS`), same day
**Blast radius:** every country's Leg-2 output to date — see "What is NOT re-run" below

## The defect

`length_ratio` compared a row's geodesic route length to its `LengthKnownKm` and flagged
anything outside a **flat `[0.75, 1.33]`** band, with the detail text *"wrong route, wrong
length value, or a partial segment drawn"*.

A schematic route is **shorter than its pipe by construction**. A straight line between two
endpoints cannot reproduce a corridor's bends, so on a `very low (straight line/schematic)`
row a ratio of 0.6 is the drawing convention doing exactly what it says on the tin — not one
of the three defects the message named.

## The measurement

Over **5,569 routed GGIT gas + GOIT oil rows** that have both a local GeoJSON and a
`LengthKnownKm` (2026-08-12 snapshots against the routes-repo mirror):

| `RouteAccuracy` | n | p10 | median | p90 | flagged by the flat band |
|---|---|---|---|---|---|
| very high (within meters) | 295 | 0.89 | 1.00 | 1.18 | **12%** |
| high | 1,217 | 0.73 | 0.98 | 1.38 | 22% |
| medium | 1,383 | 0.69 | 0.97 | 1.37 | 25% |
| low | 572 | 0.62 | 0.93 | 1.37 | 32% |
| very low (straight line/schematic) | 1,401 | 0.51 | 0.87 | 1.63 | **48%** |

The band was calibrated for survey-grade geometry and applied to everything. It fired on
**half of all `very low` rows** — a check meant to isolate errors was instead reproducing
the `RouteAccuracy` column. Of the 99 `length_ratio` flags across the seven committed Leg-2
runs, **52 (53%) sit on `low` / `very low` rows**.

## The fix

The band is now conditioned on `RouteAccuracy`, each tier taking its own rounded p10/p90, so
every tier flags its ~20% tails and the check means the same thing everywhere:

| tier | band |
|---|---|
| very high (within meters) | 0.85 – 1.20 |
| high | 0.72 – 1.40 |
| medium | 0.68 – 1.40 |
| low | 0.60 – 1.40 |
| very low (straight line/schematic) | 0.50 – 1.65 |

Blank/unknown accuracy keeps the old `[0.75, 1.33]`. The flag text now names the tier and
its band instead of asserting a defect.

Malaysia re-run: **3 flags → 2**. P1068 (ratio 0.65, `very low`) was a false positive and is
gone. P1067 (0.57, `low`) and P1065 (0.47, `very high`) survive and are real questions — the
fix does not launder them.

## What is NOT re-run, and why

The seven prior batches' `route_integrity.json` files were left as they are. Re-running them
would desync each country's staged JSON from its **already-delivered** workbook, which the
researcher is working from — a worse failure than a known-stale flag. When any of those
countries is next rebuilt, Leg 2 picks up the new bands automatically.

Until then, treat a `length_ratio` flag in a pre-2026-08-12 packet as **needing its
`RouteAccuracy` checked first**: on a `low` or `very low` row it is more likely the tier than
a defect. Flags sitting on low / very-low rows, per delivered packet:

| batch | suspect | of total |
|---|---|---|
| pakistan-gas | **12** | 13 |
| iraq-gas | **9** | 12 |
| india-gas | **20** | 37 |
| egypt-gas | 6 | 13 |
| kazakhstan-gas | 2 | 10 |
| libya-gas | 1 | 11 |

Pakistan and Iraq are the ones to be careful with — nearly every `length_ratio` flag in
those two packets is on a schematic route. India's twenty matter too: that packet's Leg-3
briefs treated `length_ratio` as one of its two headline questions across 37 rows, so
roughly half of that question was the tolerance band rather than the data. India's own
resolution ladder (the PNGRB register's authorised lengths) is unaffected — a register
length is checked against the sheet, not against the drawn route — so the Leg-3 *answers*
stand; it is the *flag population* that was inflated.
