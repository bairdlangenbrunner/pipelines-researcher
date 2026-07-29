# Iran

Crude, NGL, and gas; large domestic trunk network. Deep-dive country. Sanctions
complicate sourcing — lean on Iranian official/industry outlets plus independent
corroboration.

## Regulators / official data
- Shana (`shana.ir`) — Ministry of Petroleum news outlet; primary for project
  announcements and status.
- NIOC / NIGC / NIORDC — national oil, gas, and refining/distribution companies.

## Preferred sources (beyond the global roster)
- Tehran Times, Mehr News Agency, Interfax — corroborators for Shana reports
  (watch for the same wire being republished — not independent).

## Reconciliation notes
- **Fresh standalone GulfPub gas recon, 2026-07-29:**
  `…_20260729_0941_ET_iran-gas_reconciliation-gulfpub.xlsx` (43 refs → 25 overlaps,
  18 additions, 25 GEM-only, 3 status conflicts, 10 ambiguous; NEAR_MISS 14 /
  DISCOVERY_CANDIDATE 4). Produced by the gas length-units fix re-run
  (`notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`) and **not in any packet**.
  **Read it as a fresh run, not a delta.** The superseded 07-05 run predates the admin-area
  geo signal, the per-dataset matching overrides and the 'very low' route-accuracy re-grade;
  it had collapsed 20+ references onto two rows (P2015, P5855), which the current engine
  spreads across the IGAT series (P0440–P0459). The 07-05 packet's GulfPub content is stale.

## Gotchas
- Sanctions/force-majeure and frequent renaming; verify "operating" claims.
- Many segments belong to large network groupings (e.g. trunk gas lines IGAT
  series) — match at the network level, not just the segment.

## Open items
- **P6074 (Goureh–Persian Gulf Coast)** — verify before any duplicate/removal decision.
- **P5367 (Golpa–Moghanak)** — reclassify as a Neka–Ray segment rather than a
  standalone entry (its route GeoJSON is currently null/expansion-style — a good
  null-geometry test case for `route_compare`).

## Open items — gas (staged, NOT applied — 2026-07-05 full packet: in-dev sweep + discovery + operating deep sweep; candidates for review)
In-dev status verdicts (Leg A, 8 rows → 3 confirm / 4 change / 1 stale = 62.5% >30% gate):
- **P0452 Iran–Pakistan** → construction→`shelved` (ShelvedYear 2026; Pakistan formally
  conveyed a decision to shelve the IP line, Jan 2026, multiple independent outlets). Also:
  Owner "Iran Ministry of Petroleum 100%" overstates — split NIGC (Iran side) / ISGS (Pakistan side).
- **P2225 Iran–Oman** → construction→`proposed` (the defining subsea export line was never
  built; construction leg = Minab–Sirik / Sirik–Kuhmobarak — **overlaps the discovery candidate
  "Minab–Sirik–Kuhmobarak"**, reconcile before adding).
- **P6006 Behbahan–Gachsaran** → construction→`operating`, StartYear1 2025 (confirmed: Mehr
  2025-10-07 + Shana ~2026-02; length 61 not 62 km; owner NIGC/IGEDC not NIOC).
- **P7104 Russia–Iran** → construction→`proposed` (no pipeline yet; 2025 plan routes 55 bcm/y via
  Azerbaijan — clear ConstructionYear/Month).
- **P3174 "Off-Shore Gas Pipeline"** → `stale`→`shelved` (Presumed): a defunct Iran–Pakistan
  offshore/Gazprom proposal, all independent traces cluster 2017–2019; misleadingly generic name.
- Confirmed in construction/proposed: **P0441 IGAT 11**, **P0448 IGAT 9** (both construction);
  **P6848 Dauletabad–Sarakhs–Khangiran** (proposed 2024 swap deal — **note name-collision with the
  operating P0742 of the same name**; different projects).
- Spec caveats flagged (not applied): P0441 ProposalYear/StartYear/Bazargan-endpoint/SegmentCost
  contradictions; P0448 SegmentCost $8.5B vs 8.9B, Length 1800/1863 vs 1900 km; P6848 capacity
  19.5 bcm/y is a GEM derivation.
Operating deep sweep (Leg C, 31 rows → 32 confirmed-caveat / 37 concern):
- **Systematic class-wide attribution error** — Owner recorded as **NIOC (oil co.) where it should
  be NIGC / IGTC / IGEDC / regional gas cos** on ~27 of 31 operating rows. This is a whole-class
  fix, not row-by-row (escalation-gate: systematic wrong values).
- Duplicate / segmentation: **P0748 (IGAT-1) double-counts P3957 (IGAT-1)**; **P6022 / P6023 /
  P6024** are one Iran-Ertebat reinforcing project split three ways under near-identical names on a
  single now-dead source; **P6027 Kuh Sefid–Charmshahr** likely an IGAT/Tehran-feed segment
  mislabeled standalone. P0446 IGAT 7 vs **P2015** is a name-collision but NOT a true duplicate
  (P2015 = the Iranshahr–Chabahar–Konarak extension, operating Jun 2024 — rename it).
- Existence cluster: **P6024 Esfarayen, P6025 Sabzevar Steel Plant, P6027 Kuh Sefid–Charmshahr**
  all trace to one geoblocked/dead iranertebat EPC portfolio page with no independent corroboration.
- Status error: **P3951 Siri–Mobarak** "operating" is **wrong** — the NIOC–Crescent export line
  never commercially delivered (only a failed 2010 test; 2014 tribunal breach); also mislabeled
  domestic when it is an international Iran→UAE line.
- Units/spec errors: **P5855 Iran–Iraq** capacity 35 is MMcm/d not MMcf/d (~35× off);
  **P6026** capacity ~6× below sourced figure; **P5984** EndCountry Azerbaijan→Iran (Chelavend is
  in Gilan); **P0442 IGAT 2** length 680 km likely ~1,039 km and capacity copy-pasted from IGAT 3;
  several endpoint fixes (P0440 end city, P0443 end Rasht/Gilan, P0447 start Asaluyeh, P3950 start
  Salman field).
Discovery (Leg B, 10 candidates >5 gate → 9 new_row + 1 matched-existing): see the discovery
workbook. Notable: Minab–Sirik–Kuhmobarak (reconcile vs P2225 above), a 16-in Torbat
Heydariyeh–Kashmar reinforcement line (missing sibling of P6021).

Ref-harvest re-pass (2026-07-07, staged in the newer `*_iran-gas-operating_deepsweep.xlsx`):
completed the wiki-citation harvest — **35 refs added** (9 green / 26 yellow). Wins: **P5984**
Status=operating corroborated by **two independent sources → green**: Pipeline & Gas Journal
("50-mile section of the Rasht–Chelvand pipeline was also completed") **and** eurasianet
(turkmenistan-iran-azerbaijan-gas-swaps-surge: "work on expanding its Rasht-Chelavand gas pipeline
would be completed by the middle of this year, boosting the volume of gas it can transit to
Azerbaijan to an annual 5.5 billion cubic meters"). **Correction:** an earlier pass wrongly recorded
that eurasianet "does NOT name the line" — it does; that note came from a truncated/stub archive
fetch, not the article, and `operating` is a valid *inference* from the expansion/transit prose even
though the word never appears (a status doesn't need the literal token — see confidence_tiers.md).
eurasianet also independently corroborates the 5.5 bcm/y capacity. **P0749** (Korpeje–Kordkuy) and **P2015** (IGAT-7)
each got 2-independent greens on status/owner. New value conflicts to route to Update
(`harvest_conflicts.json` in the staging dir): **P0742** `StartMonth1=10` (Oct) contradicted — BBC /
RFE-RL / Press TV / ISNA all date the opening to **January 2010**; **P0459** Tabriz–Ankara capacity
14 bcm/y vs OGJ ≤10 / SHANA 8.5; **P2015** capacity 1100 MMcf/d vs OGJ ~1800; **P3949** capacity
500 vs 530 MMcf/d and length 289 vs 305–313 km; **P0749** cost 195 vs 190 M USD; **P0449**
Iran–Armenia cost 370 M vs a1plus ~210 M; **P0444** IGAT-4 end Fars/Isfahan vs backend Saveh/Markazi.
Owner harvest reinforces the class-wide NIOC→NIGC/IOOC fix (P3957 NIGC; P3949/P3951 IOOC; P0748
lists NIGC+SOCAR, backend NIORDC). pgjonline note: it trips `url_verifier` on an SSL cert-chain
error (a 3rd false-negative mode) — page is live, confirmed via curl before staging.
