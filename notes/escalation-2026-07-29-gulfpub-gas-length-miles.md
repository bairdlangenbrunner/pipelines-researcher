# Escalation — the GulfPub **gas** `Length` column is MILES, not km (manifest says km)

**Date:** 2026-07-29 (ET) · **Source:** `sources/gulfpub`, dataset `gas`
(`data/SDE.NG_Pipelines_Global.geojson`, Dec-2025 SDE scrape, 5,346 features)
**Scope:** the whole gas dataset — **not one country**. Affects every GulfPub gas
reconciliation shipped to date (Egypt, Libya, Iraq, Saudi Arabia).
**Origin:** Egypt gas §2 reconciliation, 2026-07-29 — the required 5-record ingest
spot-check (`workflows.md` §2 step 3) showed `geodesic_km ÷ length_km ≈ 1.6` on all five.
**Decision owner:** Baird · **Nothing was changed — the manifest is untouched and this is a
flag, not an edit.**

## The finding

`sources/gulfpub/manifest.yml`, `datasets[name=gas].units.length_units` is set to `km`:

```yaml
length_units: km                 # gas 'Length' appears km; geodesic from geometry is the cross-check
```

It is miles. `sources/gulfpub/NOTES.md` already recorded this value as a **guess** and told
us what to do about it:

> **Oil length is in MILES** (`units.length_units: mi`); gas appears to be km. […]
> **Re-confirm the gas unit if a fuller gas scrape lands.**

A fuller gas scrape *did* land — the Dec-2025 SDE repoint from 1,000 → 5,346 features — and
the re-confirmation was never done. This memo is that re-confirmation, and the guess was wrong.
The oil dataset is already correct (`length_units: mi`); gas has the same convention.

## Evidence 1 — the global ratio is the miles constant

`geodesic_km` is computed by the engine from each feature's own geometry, so
`geodesic_km ÷ Length` is an independent test of the unit. Across all 5,284 gas features
with a usable length and geometry:

| statistic | value |
|---|---|
| median ratio `geodesic_km ÷ Length` | **1.595** |
| share within 10% of 1.609344 (miles) | **74.5%** |
| share within 10% of 1.000 (km) | **3.2%** |

Per-country medians — the constant reappears independently in country after country, on
separate blocks of the file:

| country | n | median | ~1.6 | ~1.0 |
|---|---|---|---|---|
| Russian Federation | 676 | 1.612 | 91% | 0% |
| United Kingdom | 497 | 1.592 | 78% | 1% |
| France | 290 | 1.588 | 95% | 0% |
| Netherlands | 196 | 1.603 | 87% | 1% |
| Italy | 194 | 1.595 | 95% | 1% |
| **Canada** | **193** | **0.943** | **10%** | **48%** |
| Australia | 145 | 1.595 | 72% | 1% |
| Nigeria | 131 | 1.601 | 72% | 1% |
| Ukraine | 111 | 1.603 | 89% | 0% |
| Turkey | 84 | 1.597 | 92% | 0% |
| Norway | 62 | 1.591 | 90% | 0% |
| Egypt | 92 | 1.553 | 60% | 2% |

## Evidence 2 — reading it as miles makes GEM and GulfPub agree

On the 52 Egypt gas overlaps just produced, comparing `Ref Length` to `GEM Length (km)`:

| reading | agree ±10% | agree ±20% |
|---|---|---|
| as km (current manifest) | **2/52 (4%)** | 5/52 (10%) |
| as miles ×1.609344 | **15/52 (29%)** | 21/52 (40%) |

Eight of them land within 3% — that is arithmetic, not resemblance:

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

## The complication — Canada is genuinely kilometres

Canada is the one clear exception: median 0.943, 48% of its 193 records within 10% of 1.0 and
only 10% near 1.6. Its block really is in km, exactly mirroring the OPEC ASB Libya case
(`escalation-2026-07-28-asb-libya-length-units.md`), where one country's block was tabulated in
different units than the column header claimed. India (1.543), Mexico (1.503), Spain (1.517)
and Brazil (1.556) sit slightly low and are probably mixed blocks.

**This is why the memo does not ship a fix.** `units.length_units` is per-*dataset*; the
manifest schema has no per-country override, so flipping gas to `mi` corrects ~75% of the file
and breaks Canada's 193 records by the same 1.609×. The options are a real decision:

1. **Flip to `mi` and accept Canada wrong** — one-line manifest change, correct for the large
   majority, known-bad for Canada (no Canada recon has ever run, so nothing shipped regresses).
2. **Add per-country unit overrides to the manifest schema** — engine + schema change
   (`sources/_schema/manifest.schema.json` and `ingest.py`), correct everywhere, more work.
3. **Leave it and lean on `geodesic_km`** — status quo; every length comparison in every
   GulfPub gas workbook stays biased ~38% short.

## Blast radius

- **Shipped workbooks understate GulfPub gas lengths by ~38%.** Every `Ref Length (km)` cell in
  the `Gas_Overlaps` / `Gas_Additions` tabs of the Egypt (2026-07-29), Libya and Iraq
  (2026-07-28) reconciliations is affected. **`Ref Geodesic (km)`, in the adjacent column, is
  computed from geometry and is unaffected — use it.**
- **The matcher's length signal has been comparing km against miles.** `length_weight` is 0.10
  for gulfpub, so this suppressed rather than destroyed matches, but some real pairs were pushed
  under threshold and are sitting in `Gas_Additions` / `Ambiguous_Clusters` as false negatives.
  Re-running after a fix will move overlap/addition counts in Egypt, Libya, Iraq and Saudi.
- **No GEM cell is wrong because of this.** The defect is in the reference dataset's ingest, not
  in the tracker, so there is nothing to un-paste. It only ever mis-*informed* a comparison.
- Do **not** treat any length disagreement in a GulfPub gas workbook as a finding until this is
  settled.

## Recommendation

Take option 1 now (one line, `length_units: km` → `mi`, plus a Canada caveat in `NOTES.md`)
and re-run the four affected countries' gulfpub legs; take option 2 only if a Canada or
India/Mexico/Spain/Brazil recon is actually on the roadmap. Either way the stale
"gas appears to be km / re-confirm" line in `NOTES.md` should be replaced with this finding
so the guess is not re-inherited a third time.
