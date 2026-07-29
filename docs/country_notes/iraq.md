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
- **OSM is registered for both commodities** (`osm/gas_iq` 52 features, `osm/oil_iq` 246)
  and runs by default in the `deep` preset. Both carry a per-dataset
  `geoarea_weight: 0.30`: Iraq's OSM features are essentially unnamed and 34 of 54 GEM gas
  rows have no drawn route, so name and geometry are both dead and the admin-area signal
  is the only live axis. Without it the gas run scored **0 overlaps from 52 features** —
  top composite 0.438 against a 0.45 threshold — and that null passed as a finding.
  Detail: `sources/osm/NOTES.md`.

### Reference-dataset re-run, 2026-07-28 (staged, nothing applied)

| Scope · source | Overlaps | Unmatched (by disposition) | Deliverable |
|---|---|---|---|
| gas · OSM | 8 (5 `partial`) | 44 — ROUTE_FOR_EXISTING 30, DISCOVERY 10, NEAR_MISS 2, FRAGMENT 2 | `Gas_OSMActions` / `Gas_OSM` in the handoff packet |
| gas · GulfPub | 39 (4 green) | 8 — NEAR_MISS 7, DISCOVERY 1; 13 status conflicts | `Gas_GulfPubActions` / `Gas_GulfPub` |
| oil · OSM | 71 | 175 — DISCOVERY 84, FRAGMENT 61, ROUTE_FOR_EXISTING 21, NEAR_MISS 9 | `…_1804_ET_iraq-oil_osm-reconciliation.xlsx` |
| oil · GulfPub | 20 (2 green) | 1 NEAR_MISS; 8 status conflicts | `…_1804_ET_iraq-oil_gulfpub-reconciliation.xlsx` |

**GulfPub gas re-run 2026-07-29 — the packet's `Gas_GulfPub` tab has a bad length column.**
The gas `Length` unit was miles read as km, so every `Ref Length (km)` cell in the 07-28
packet is ~38% short (display only; matching scores on `geodesic_km`, and the re-run
reproduces the same 39 overlaps / 8 unmatched / 13 status conflicts). Corrected standalone
workbook: `…_20260729_0941_ET_iraq-gas_reconciliation-gulfpub.xlsx` (`--commodity both`, so
it also carries the oil tabs). Use it for any length comparison; everything else in the
packet's recon tabs still stands. `notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`.

What to look at first:

- **Gas, route candidates.** [OSM way/1494626715](https://www.openstreetmap.org/way/1494626715)
  (116.6 km, Iraq/Diyala → Iran/Kermanshah) and way/301655831 (42.6 km) are both candidate
  geometry for **P5855 Iran-Iraq Gas Pipeline**, which currently has `no route`, blank
  Diameter and `LengthKnownKm='--'`. Filed ROUTE_FOR_EXISTING at composite 0.4324 — under
  threshold deliberately, because nothing physical corroborates the identification. Also
  way/1526522308_1526522309 (1.7 km) → **P7459**. The other 27 ROUTE_FOR_EXISTING traces
  are sub-kilometre stubs clustered on P7445 (17) and P7459 (10).
- **Gas, status conflict.** Five OSM stubs along the Zubair–Faw corridor are mapped
  `operating`; GEM has **P5857** as `shelved`. Tier 3, so a lead rather than evidence — but
  a lead on the row's whole premise.
- **Oil, the big unmatched traces.** 80.9 km in Arbil near **P0548** and 52.3 km in
  At-Ta'mim near **P0577** (both FRAGMENT_OF_EXISTING); 86.1 km across
  Al-Muthannia/Dhi-Qar as candidate geometry for **P6255**; 80.3 + 53.6 km in Al-Anbar
  scoring just under threshold against **P7898**. The 84 DISCOVERY_CANDIDATE traces
  (366 km total, largest 26.5 km in At-Ta'mim) are **untriaged** — each needs the
  match-to-an-existing-row-under-another-name check before any of it reaches Discovery.
- **Coverage guard.** 5 of the 8 gas overlaps are `partial`: a 0.1–0.5 km OSM stub matched
  to a 100 km GEM row corroborates *location* only, never length, capacity or extent.

## Gotchas
- Kirkuk–Ceyhan and cross-border lines are multi-country (`CountriesOrAreas`
  includes Turkey) — block on *any-of* country overlap.
- A GulfPub gas "addition" for Iraq is often an **Iran** line mislabeled `country=Iraq`
  (all endpoints in Iran) — verify the `country`/endpoints before treating it as a miss.
- Recurring: GEM `ProposalYear = 2022` where sources say **2021** (seen on P4047, P4053).
- **Arabic false friends.** `زيت الغاز` ("gas oil") = **diesel**, NOT natural gas — natural gas is
  `غاز طبيعي`, dry gas `الغاز الجاف`. Reading `الغاز` out of the phrase is how a diesel line
  (P6824) entered GGIT. Separately, **`عقدة` means "inch"** in Iraqi pipe-sizing usage; machine
  translation renders it "knot" (seen on iina.news for P7434's 42″).
- **Never infer a pipeline's fluid from its origin field's principal product.** An oil field
  produces associated gas, and an oil-field→power-station gas line is the most ordinary object in
  Iraq's gas network. This invalid inference produced the retracted P4067 finding; key on what the
  source says the pipe **carries**.
- **OPEC ASB Iraq blocks are tabulated in KILOMETRES** despite the column header reading
  "(miles)", and the ASB tables are **per-pipeline** ("Connection from/to"), not country
  aggregates — so an ASB-only citation is not evidence of a phantom row.
- `mnr.krg.org` intermittently ConnectTimeouts while genuinely reachable — cite the Wayback
  snapshot for stability.

## Open items — oil
- **Grand Faw Port third offshore pipeline** (Esta/Micoperi, contracted April 2025)
  — entered as a single new row; confirm length/diameter and route.
- **P0544 (Basra–Haditha)** — status review: listed `construction` but appeared
  still pre-construction/tender as of early 2026.

## Open items — gas (full pass 2026-07-28; ALL staged, NOTHING applied)

**Work from the ACTIONS file, not the per-leg workbooks:**
`batches/iraq-gas/deliverables/pipelines_batch_20260728_1804_ET_iraq-gas_handoff-actions.xlsx`
(100 open decisions · 9 status changes · 265 backend paste units · 27 operator/owner units ·
5 new rows · 114 wiki updates · 36 route suggestions · 171 open flags · **104 recon rows needing a
decision** on the new `Gas_GulfPubActions` + `Gas_OSMActions` tabs), with the audit trail in
the companion `…_handoff-evidence.xlsx` (37 confirmed audits · 118 fill detail · 339 ref detail ·
150 re-verified · the full 115-row `Gas_GulfPub` / `Gas_OSM` cross-comparisons). Legs: refs sweep ·
cancelled review (4 rows) · redundancy/duplicate clusters · GulfPub crosswalk · OSM recon ·
wiki alignment (158 diffs) · route integrity (13 rows) · ref-gap re-pass · Leg-3 targeted research
(15 rows). The 1704 packet is superseded (archived) — it predates the recon tabs. Live counts:
`python scripts/staged_summary.py --country Iraq --commodity gas`.

### Twelve escalations awaiting a ruling
Full list + memo paths: `batches/iraq-gas/staging/qc/escalations.json` (rendered as the
ESCALATIONS row in both workbook READMEs). The structural ones:
- **ASB length mi→km, 19 rows — TWO families, TWO different one-cell fixes.** OPEC's ASB length
  column is headed "(miles)" but the Iraq block is tabulated in **km**, and the ingest converted
  anyway. 13 rows (P18xx/P22xx) hold the converted km → fix the **number**; 6 rows (P40xx) hold
  the ASB integer verbatim with units `mi` → fix **only the unit label**. Route geometry arbitrates
  6–0 for the raw figure. `notes/escalation-2026-07-28-asb-iraq-length-units.md`.
- **CapacityUnits mislabelled on 3 rows** (P4041 `MMSCMD`→`MMcf/d`; P7477 `bcm/y`→`MMcf/d`,
  number stays 130) — and the screen suggests it is tracker-wide.
  `notes/escalation-2026-07-28-iraq-capacity-units.md`.
- **P6824 (Shouibah–Khor Al-Zubair) is a DIESEL line in GGIT** — its own al-Mirbad source says
  `زيت الغاز` ("gas oil" = diesel), 46 km / 8–10″ to an oil port. Remove from GGIT, refer to GOIT.
  Second country with this class after Libya's three condensate lines.
  `notes/escalation-2026-07-28-iraq-gasoil-misfiled.md`.
- **ASB provenance ruling — 12 of 16 duplicate/existence flags WITHDRAWN.** ASB Table 4.10/9.9 is
  a **per-pipeline** table ("Connection from/to"), not a country aggregate, so rows citing it are
  faithful 1:1 transcriptions, not phantoms. My own earlier legs were wrong.
  `notes/escalation-2026-07-28-asb-iraq-provenance.md`.
- **Cluster C — P4061 (600 km national 42″ trunk) vs P1852: a 600 km double count**, and
  **Cluster B — P4054 is a third naming of P4066** (the one confirmed duplicate).
  `batches/iraq-gas/staging/redundancy/`.
- **P7457 LengthKnown was populated from a "X km from" DISTANCE statement** — a second
  length-provenance defect class, distinct from the units one.
- **P7436/P7437 owner is TotalEnergies' project (GGIP: TotalEnergies 45% / Basrah Oil 30% /
  QatarEnergy 25%), not "Iraq Ministry of Oil 100%"** — the contractor/operator-vs-owner
  confusion, which also produced three wrong wiki operator values this pass (P6832, P6827, P4041).
- **GulfPub↔GEM matching is unreliable for Iraq — do NOT act on its conflict list.**
  `notes/escalation-2026-07-28-gulfpub-iraq-match-quality.md`.
- **`url_verifier.py` false negatives cost 33 of 41 "dead" refs** — six families now, two new
  (CAPTCHA interstitials returning HTTP 200; JS-gated stubs). A token FAIL on a large PDF is not
  evidence the source lacks the value.

### Three retractions — do NOT act on these older findings
- **P4067 (Al-Ahdab–Al-Zubaydia) is NOT a crude line misfiled in GGIT.** The 2026-07-07 harvest
  concluded "crude oil → belongs in GOIT" from Al-Ahdab being a crude-oil *field*. Invalid: an oil
  field produces associated gas, the destination is a **power station**, and ASB2017 lists the
  corridor's gas line (Table 9.9) and crude lines (Table 6.9) as **separate rows**. **P4067 stays
  in GGIT.** Al-Jibawi's genuinely new 16″/76 km Ahdab→Zubaidiya **crude** line is a separate
  **GOIT discovery candidate**. General rule: key on what the source says the pipe **carries**,
  never on what its origin field produces.
- **"Status is stale forward" on P7435 and P6826 is retracted** — Al-Jibawi refutes both; GEM was
  right. (P7435 stays `operating`, not `construction`.)
- **P6007 West Qurna–Rumela is not a phantom.** The existence concern is resolved: OGJ (2016-03-07,
  operational by mid-2015, 80 MMcfd from DS-7/DS-8), BGC's own operations page and MEES
  (2025-10-24) document it → `operating`, StartYear1 2015, Diameter 40″. Only its **drawn route**
  is still flagged (87 km drawn vs 50 km attribute).

### Status changes staged (9, one per row)
- **P4053 Erbil–Duhok** → `operating`, StartYear1 2025-10 (inaugurated by PM Barzani 2025-10-28;
  four independent outlets). **LengthKnown 198 km** (Shafaq + Kurdistan24 attribute 198 to the
  Erbil–Duhok leg alone; The New Region's 192 is the outlier) vs GEM's route-derived 117.42 km —
  so the `low`-accuracy route likely needs a redraw. Diameter 52″ doubly sourced;
  ProposalYear 2022 likely **2021**.
- **P7434 Mahmudiyah–Besmaya** → `operating`, StartYear1 2025 (Oil Minister 2025-07-20 "completed
  in full"; attaqa 2025-08-11). Specs 43 km / 42″ / 800 MMcf/d confirmed a second time by
  Al-Jibawi. *A mid-pass reading of "confirm construction" off Al-Jibawi (June 2025) was withdrawn
  — a source describing construction dates the construction, it does not bound completion.*
- **P6007** → `operating` 2015 · **P5857 Zubair–Faw** → `cancelled` + `ShelvedCancelledType=
  Presumed`, **no CancelledYear** (nothing dates a cancellation; CPECC contract PRJ-11-4226's
  execution window lapsed April 2016 and the line is absent from GulfPub's map) · **P7436 Artawi**
  → `construction` · **P7470 Karbla** → `operating` · **P0450**, **P0481** → `cancelled` +
  Presumed (stale) · **P4041** → `unclear`.
- Sourced spec defects: **P6832** 70→60 km · **P6827** StartYear1 1980→2023 (month 11) ·
  **P7459** blank→100 km · **P1851** 24″→42″ · **P5855** MMcf/d→MMcm/d ·
  **P7445 Nasiriyah** reclassify transmission → gathering/feeder, ConstructionYear 2024 → ~2022.

### Still open after this pass
- The three cluster rulings (B/C and the national-trunk naming families "Strategic-X" /
  "Trans-Iraq(i)-X" / P4061 / P4058) need a human de-dup decision — `P1847↔P4062` and
  `P1852↔P4061` were **cleared** by the ASB provenance ruling; `P4054↔P4066` is the one
  confirmed duplicate.
- **P4058 "Eastern Iraq Gas Pipeline"** — not a duplicate, but not a sourceable entity either
  (no ASB, Al-Jibawi, GulfPub or OSM match). Reads like a descriptive grouping. Not escalated as
  a deletion; the 48″/350 MMcf/d specifics suggest something real under a different name.
- **P4041 North Rumaila–Al-Najaf** conflates two schemes (the SCOP 28″ gas twin vs the revived
  crude Basra–Aqaba); cross-tracker inconsistency with GOIT **P0544**, which reads `construction`.
- Discovery candidates that cleared threshold: Chemchemal–Bazian (high), Iran–Iraq
  Basra/Shalamcheh import (high), Iraq–Jordan Basra–Aqaba gas leg (high), Kurdistan–Turkey export
  (medium), Halfaya–Kahla (medium). Monitors: Akkas–Syria, Al-Faw LNG–Abu Ghraib, Chemchemal–Erbil
  industrial, Diyala gas fields, Miran export.
- 36 route suggestions staged for a separate human routes-repo PR (never auto-replaced).
- **The OSM recon findings are new and untriaged** (see the section below) — 44 unmatched
  traces, 30 of them candidate geometry for routeless GEM rows.

### Prior gas work folded into the above
2026-07-05 deep sweep and the 2026-07-07 ref-harvest re-pass (68 refs added, chiefly ASB2012 p.75
/ ASB2017 Table 9.9 recovered via Wayback since live opec.org PDFs 302 to the homepage). Findings
that still stand from that harvest: **P1841 capacity** "2.41 MMcf/d" is a unit mislabel — OPEC
gives 2.41 **bcm/y** (~100× off); **P2231** North Gas–Baiji already moved gas in 2011, so
`ConstructionYear=2012` is too late; the ASB tables name the operator **OPC (Oil Pipelines
Company)**, which does not confirm the backend "Iraq Ministry of Oil" string. Its **P4067**
conclusion is retracted above.
