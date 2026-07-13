# Iraq

Crude export focus (Basra, Kirkuk–Ceyhan), plus domestic and gas. Deep-dive country;
GulfPub has a global oil file that covers Iraq — a good second country to prove the
engine is country-agnostic (Phase E validation target).

## Regulators / official data
- SOMO (State Oil Marketing Organization), Ministry of Oil, Basra Oil Company.

## Preferred sources (beyond the global roster)
- MEED, Rigzone, Reuters — Gulf project + tender coverage. Esta/Micoperi for the
  Grand Faw Port offshore work.
- **Iraq/Kurdistan press (verified, some Arabic/FA-only):** Iraq Oil Report, MEES,
  Rudaw (Arabic), Shafaq, `attaqa.net`, `al-mirbad.com`, Wattan News, thenewregion,
  kurdistan24. Cross-border lines (Iran/Turkey/Jordan/Syria) need non-English search.

## Reconciliation notes
- Oil: use `gulfpub.SDE.Oil_Pipelines_Global.geojson` filtered to Iraq for the
  country-agnostic validation run.
- Gas: the fuller Dec-2025 SDE gas scrape (`SDE.NG_Pipelines_Global.geojson`, incl. 31
  Iraq gas features) is now the `gulfpub` gas source — earlier gas file had no Iraq.

## Gotchas
- Kirkuk–Ceyhan and cross-border lines are multi-country (`CountriesOrAreas`
  includes Turkey) — block on *any-of* country overlap.
- A GulfPub gas "addition" for Iraq is often an **Iran** line mislabeled `country=Iraq`
  (all endpoints in Iran) — verify the `country`/endpoints before treating it as a miss.
- Recurring: GEM `ProposalYear = 2022` where sources say **2021** (seen on P4047, P4053).

## Open items — oil
- **Grand Faw Port third offshore pipeline** (Esta/Micoperi, contracted April 2025)
  — entered as a single new row; confirm length/diameter and route.
- **P0544 (Basra–Haditha)** — status review: listed `construction` but appeared
  still pre-construction/tender as of early 2026.

## Open items — gas (staged, NOT applied — 2026-07-05 deep sweep; candidates for review)
Status/spec changes:
- **P4053 Erbil–Duhok** → `operating` (inaugurated by PM Barzani 2025-10-28; Shafaq /
  thenewregion / kurdistan24). Diameter 52″ confirmed; ProposalYear 2022 likely 2021.
- **P7434 Mahmudiyah–Besmaya** → `operating` (2025-08; 43 km / 42″ / 800 MMcf/d corroborated).
- **P7435 & P5856** → operating → `construction`. **P1851** 24″ → 42″. **P5855** MMcf/d → MMcm/d.
- **P7477** "130 bcm/y" is physically impossible — re-derive capacity.
- **P5857 Zubair–Faw** → stale → `cancelled` (Presumed); only reached 2011 tender / 2014 CPECC
  award, no independent progress since ~2021.
Existence / duplicate / classification (the redundancy concern that drove the sweep):
- **National dry-gas trunk system appears duplicated under three naming families** —
  "Strategic-X", "Trans-Iraq(i)-X", and "National Gas Pipeline P4061"/"Eastern Iraq P4058".
  Likely relabels: **P1847↔P4062, P1852↔P4061, P4054↔P1845+P4066** (human de-dup pass).
- **P6007 West Qurna–Rumela** → existence/phantom concern: no independent source documents a
  distinct pipeline by this name; likely a relabel of BGC associated-gas gathering lines.
- **P7445 Nasiriyah** → reclassify transmission → gathering/feeder; ConstructionYear 2024 likely ~2022.
- **P4067 (Al-Ahdab–Al-Zubaydia)** is **crude oil → belongs in GOIT**, not GGIT.
- **P6824 (Shouibah–Khor Al-Zubair)** is **gasoil/diesel products → not gas**.
- **P4041 North Rumaila–Al-Najaf** conflates two schemes; "shelved" contradicted (near completion
  Jan 2021); the "258 MMSCMD" capacity looks mis-derived from the Iraq–Jordan (Basra–Aqaba) project.
Attribution:
- **P7436 / P7437 Artawi GMP** owner = the **GGIP consortium** (TotalEnergies 45% / Basrah Oil
  30% / QatarEnergy 25%), NOT "Iraq Ministry of Oil 100%"; Start 2027 likely 2028.
- **P2234** operator → **Basrah Gas Company** (Shell/SGC JV). **P7457** "Semel Oil Field" →
  **Summail Gas Field**.
Discovery (new-row candidates that cleared threshold): Chemchemal–Bazian (high), Iran–Iraq
Basra/Shalamcheh import (high), Iraq–Jordan Basra–Aqaba gas leg (high), Kurdistan–Turkey export
(medium), Halfaya–Kahla (medium). Monitors: Akkas–Syria, Al-Faw LNG–Abu Ghraib, Chemchemal–Erbil
industrial, Diyala gas fields, Miran export.

Ref-harvest re-pass (2026-07-07, staged in the newer `*_iraq-gas-operating_deepsweep.xlsx`):
completed the wiki-citation harvest — **68 refs added** (mostly yellow/single-source, chiefly the
OPEC Annual Statistical Bulletin gas-pipeline tables ASB2012 p.75 / ASB2017 Table 9.9, recovered
via Wayback since the live opec.org PDFs 302 to the homepage). Confirmed conflicts to route to
Update (`harvest_conflicts.json` in the staging dir): **P4067** Al-Ahdab is a **crude-oil** field
(Iraq Business News + BBC Arabic) and **P6824** is a **gas-oil/diesel** export line (al-mirbad) —
both wrong-tracker flags now source-backed. **P1841 capacity** "2.41 MMcf/d" is a unit mislabel —
OPEC gives 2.41 **bcm/y** (~100× off). **P2231** North Gas–Baiji already moved gas in 2011, so
`ConstructionYear=2012` is too late. Owner refs unstaged across the OPEC set: the tables name the
operator **OPC (Oil Pipelines Company)**, which doesn't confirm the backend "Iraq Ministry of Oil"
string.
