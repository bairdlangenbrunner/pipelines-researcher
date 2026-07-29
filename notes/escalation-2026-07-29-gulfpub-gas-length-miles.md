# RESOLVED — the GulfPub **gas** `Length` column is MILES, not km (manifest said km)

**Date:** 2026-07-29 (ET) · **Source:** `sources/gulfpub`, dataset `gas`
(`data/SDE.NG_Pipelines_Global.geojson`, Dec-2025 SDE scrape, 5,346 features)
**Status: FIXED AND RE-RUN, 2026-07-29.** The manifest now reads `length_units: mi` with a
per-country `Canada: km` override, the engine supports that override, and all five affected
countries' gulfpub gas legs were re-run and their workbooks rebuilt. Kept as the record of
what was wrong, what the evidence was, and what shipped wrong in the meantime.

**Origin:** Egypt gas §2 reconciliation, 2026-07-29 — the required 5-record ingest
spot-check (`workflows.md` §2 step 3) showed `geodesic_km ÷ length_km ≈ 1.6` on all five.

## The finding

`sources/gulfpub/manifest.yml`, `datasets[name=gas].units.length_units` was set to `km`:

```yaml
length_units: km                 # gas 'Length' appears km; geodesic from geometry is the cross-check
```

It is miles. `sources/gulfpub/NOTES.md` already recorded this value as a **guess** and told
us what to do about it:

> **Oil length is in MILES** (`units.length_units: mi`); gas appears to be km. […]
> **Re-confirm the gas unit if a fuller gas scrape lands.**

A fuller gas scrape *did* land — the Dec-2025 SDE repoint from 1,000 → 5,346 features — and
the re-confirmation was never done. The oil dataset was already correct (`length_units: mi`);
gas has the same convention.

## Evidence 1 — the global ratio is the miles constant

`geodesic_km` is computed by the engine from each feature's own geometry, so
`geodesic_km ÷ Length` is an independent test of the unit. Across all 5,345 gas features
with a usable length and geometry:

| statistic | value |
|---|---|
| median ratio `geodesic_km ÷ Length` | **1.595** |
| share within 10% of 1.609344 (miles) | **73.7%** |
| share within 10% of 1.000 (km) | **3.1%** |

Per-country medians — the constant reappears independently in country after country, on
separate blocks of the file:

| country | n | median | ~1.6 | ~1.0 |
|---|---|---|---|---|
| Russian Federation | 681 | 1.612 | 90% | 0% |
| United Kingdom | 501 | 1.591 | 77% | 1% |
| France | 290 | 1.588 | 95% | 0% |
| **Canada** | **204** | **0.938** | **10%** | **46%** |
| Netherlands | 196 | 1.603 | 87% | 1% |
| Italy | 194 | 1.595 | 95% | 1% |
| India | 158 | 1.527 | 49% | 5% |
| Australia | 148 | 1.595 | 70% | 1% |
| Nigeria | 131 | 1.601 | 72% | 1% |
| Mexico | 127 | 1.501 | 58% | 1% |
| Egypt | 92 | 1.553 | 60% | 2% |

**Canada is the only country in the file where km beats miles** — swept every country with
n≥5 and no other favours km. India (1.527), Mexico (1.501) and Spain (1.517) sit slightly low
and are probably mixed blocks; miles is still the better reading for them.

## Evidence 2 — reading it as miles makes GEM and GulfPub agree

On the 52 Egypt gas overlaps, comparing `Ref Length` to `GEM Length (km)`:

| reading | agree ±10% | agree ±20% |
|---|---|---|
| as km (old manifest) | **2/52 (4%)** | 5/52 (10%) |
| as miles ×1.609344 (fixed) | **15/52 (29%)** | 21/52 (40%) |

Eight land within 3% — arithmetic, not resemblance:

| ref raw | ×1.609344 | GEM sheet |
|---|---|---|
| 242 | 389.5 | **390.0** |
| 196 | 315.4 | 322.0 |
| 147 | 236.6 | 235.0 |
| 93 | 149.7 | **150.0** |
| 91 | 146.5 | **147.0** |
| 75 | 120.7 | **121.0** |
| 56 | 90.1 | **90.0** |
| 19 | 30.6 | 30.0 |

The stronger check is internal and needs no GEM row at all: post-fix, `Ref Length (km)` now
tracks the geometry-derived `Ref Geodesic (km)` column (Egypt: 74.0/75.2, 101.4/100.7,
141.6/135.8, 130.4/129.3). Pre-fix those two columns disagreed by a constant 1.609×.

## The fix that shipped

1. **Engine** — `scripts/adapter_base.py` resolves `units.length_units_by_country` per record
   before parsing length, keyed on the *normalized* country so a manifest may use any alias.
   Added to `sources/_schema/manifest.schema.json`. This is the general mechanism for a source
   that tabulates one country's block in different units than its column header claims (same
   shape as the OPEC ASB Libya case, `escalation-2026-07-28-asb-libya-length-units.md`) —
   reach for it instead of accepting a known-bad country.
2. **Manifest** — gas `length_units: mi` + `length_units_by_country: {Canada: km}`.
   `length_commodity_quirk` is now `false` on both datasets: oil and gas are both miles, so
   there is no commodity quirk left to flag.
3. **Re-ran all five affected countries** (Egypt, Libya, Iraq, Saudi Arabia, Iran) into
   `batches/<scope>/staging/recon-gulfpub-20260729/`, rebuilt each `…_reconciliation-gulfpub.xlsx`
   at stamp `20260729_0941_ET`, refreshed each `recon_gulfpub_crosswalk.json`, and moved the
   pre-fix runs to `archive/…-prefix-gulfpub-gas-miles/`.

## What was actually affected — narrower than first written

The first version of this memo claimed *"the matcher's length signal has been comparing km
against miles"*. **That was wrong.** `match.py:278` scores length on
`ref.get("geodesic_km") or ref.get("length_km")` — geodesic wins whenever geometry exists, and
only **1 of 5,346** gulfpub gas features has no geometry. So the length signal was computed
from geometry all along and no match was ever mis-scored by this defect. Verified empirically:
re-running Egypt against the same GEM snapshot changed `length_km` on 52/52 overlaps and
`s_length` on **0**, with identical overlap/addition/ambiguous counts (52/40/12).

- **The defect was display-only**: every `Ref Length (km)` cell in a shipped GulfPub *gas*
  workbook read ~38% short. Anyone comparing that column to GEM saw a false disagreement.
  `Ref Geodesic (km)` was always right.
- **GulfPub oil was never affected** (`length_units: mi` from the start), so the Iraq oil and
  Saudi oil reconciliations needed no re-run.
- **No GEM cell is wrong because of this**, and nothing was pasted from it — the defect was in
  the reference dataset's ingest, so there is nothing to un-paste.
- Iran and Saudi Arabia's re-runs *do* show large match churn, but that is **not** from this
  fix — their pre-fix runs date from 2026-07-05/07-06 and predate the admin-area geo signal,
  the per-dataset matching overrides, and the 'very low' route-accuracy re-grade. Libya's three
  yellow→green shifts are one day of GEM drift (07-28 → 07-29 snapshot). Treat both countries'
  new numbers as a fresh run, not a delta.

## The process failure worth keeping

`NOTES.md` recorded the unit as a **guess** and named the exact trigger for re-checking it
("if a fuller gas scrape lands"). The scrape landed, the manifest was repointed on the same
day, and the guess was carried forward unchallenged into four countries' workbooks. A
`column_map`/`units` value marked as unverified is a **blocking** item on any repoint of that
dataset, not a footnote. When the ingest spot-check does surface it, the fix is a manifest
change plus a re-run — not a memo.
