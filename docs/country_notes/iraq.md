# Iraq

Crude export focus (Basra, Kirkuk–Ceyhan), plus domestic and gas. Deep-dive country;
GulfPub has a global oil file that covers Iraq — a good second country to prove the
engine is country-agnostic (Phase E validation target).

## Regulators / official data
- SOMO (State Oil Marketing Organization), Ministry of Oil, Basra Oil Company.

## Preferred sources (beyond the global roster)
- MEED, Rigzone, Reuters — Gulf project + tender coverage. Esta/Micoperi for the
  Grand Faw Port offshore work.

## Reconciliation notes
- Use `gulfpub.SDE.Oil_Pipelines_Global.geojson` (or the canonical global oil
  extract) filtered to Iraq for the country-agnostic validation run.

## Gotchas
- Kirkuk–Ceyhan and cross-border lines are multi-country (`CountriesOrAreas`
  includes Turkey) — block on *any-of* country overlap.

## Open items
- **Grand Faw Port third offshore pipeline** (Esta/Micoperi, contracted April 2025)
  — entered as a single new row; confirm length/diameter and route.
- **P0544 (Basra–Haditha)** — status review: listed `construction` but appeared
  still pre-construction/tender as of early 2026.
