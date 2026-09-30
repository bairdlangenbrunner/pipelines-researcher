# Russia

Gas (GGIT): 285 rows (227 Russia-only + 58 transit/export trunks), the world's largest
trunk system under one operator (Gazprom). Oil (GOIT) not in the current cycle.
**Campaign started 2026-09-14** — plan, rulings and batch plan in
`notes/triage-2026-09-14-russia-gas-campaign.md` (§7 rulings, §9 audit + recon results). Shape: 8
regional deep-sweep batches (all statuses, `--status-review` on, one pass per row), sliced by
federal district from the state audit in `batches/russia-gas/staging/state-audit-20260914/`
(`batch_plan.csv`; per-batch `include_pids.txt`/`exclude_pids.txt`). Order R1 Far Eastern (pilot) →
R2 NW operating → R3 NW in-dev → R4a Urals-YaNAO → R4b Urals-south → R5 Volga → R6 Siberia → R7
Central+South. **From R5 on, batches run as lean passes** (`docs/sops/lean_pass.md`; Baird
2026-09-16, weekly token budget): R5 Volga is the pilot — plan in
`batches/russia-gas/staging/deepsweep-r5-volga/PLAN.md` — then R4a, R4b, R6, R7 (all delivered — the regional pass is complete). Each lean batch's
deferred fills/second sources accumulate in its `deferred_units.json` for one later
campaign-wide fills pass. Oil out of scope this cycle. Later: sliced discovery by district, maybe §8 routes,
and a Russian-side re-look at the 33 carried rows as a §5 Update.

## Batches
- **R1 `deepsweep-r1-fareast`** (32 rows / 484 units) — delivered 2026-09-15, staged not applied:
  `deliverables/pipelines_batch_20260915_1851_ET_russia-gas_deepsweep-r1-fareast.xlsx`. 213 fills,
  257 refs added, 102 validity records (60 open concerns), 31 status reviews (22 confirm / 7 change /
  1 stale / 1 unresolved), 22 reverified, 18 dead links, 17 UNRESOLVED. Gates J and L PASS.
  Results + the two engine defects the pilot found: campaign memo §10. **Rebuilt at `_1851_ET`**
  for the three workbook defects in §11 (UNRESOLVED was 38 before the phantom-stub fix — no research
  changed); the `_1240_ET` and `_1844_ET` builds are in `archive/`.
- **R2 `deepsweep-r2-nw-operating`** (28 rows) — delivered 2026-09-15, staged not applied:
  `deliverables/pipelines_batch_20260915_1851_ET_russia-gas_deepsweep-r2-nw-operating.xlsx`. 190 fills,
  225 refs added, 58 validity records (25 open concerns), 28 status reviews (26 confirm / 1 change /
  1 unresolved), 4 reverified, 27 dead links (10 of them `link_live` — re-read, not delete),
  12 UNRESOLVED. Gates J and L PASS; I=2 (both P5540, honest residue). Results + the three workbook
  defects this packet exposed: campaign memo §11.
- **R3 `deepsweep-r3-nw-indev`** (27 rows / 413 units) — delivered 2026-09-15, staged not applied:
  `deliverables/pipelines_batch_20260915_2130_ET_russia-gas_deepsweep-r3-nw-indev.xlsx`. 222 fills,
  174 refs added, 62 validity records (30 open concerns), 27 status reviews (17 confirm / 7 change /
  3 unclear), 2 reverified, 5 dead links, 39 UNRESOLVED. Gates J, L, M and I' all PASS; advisory
  A=3 (Pskov отводы sourced only to `gazprommap.ru`), C=33 (decrees 816-р and 3302-р carry a third
  of the batch), I=2, K=106. The NW in-development slice: 16 of 27 rows are `PipelineType =
  distribution`, and 141 of the 172 owed blanks sit on `proposed` rows. Results + the two
  status-contract engine defects this batch found: campaign memo §12. The `_2128_ET` build, made
  before those fixes, is in `archive/`.
- **R5 `deepsweep-r5-volga`** (31 rows / 275 owed units of 467 — the LEAN-PASS PILOT,
  `docs/sops/lean_pass.md`) — delivered 2026-09-16, staged not applied:
  `deliverables/pipelines_batch_20260916_1902_ET_russia-gas_deepsweep-r5-volga.xlsx`. 42 fills
  (21 sourced, 21 unresolved), 236 refs added (215 on the tab after 21 baselines folded into sourced
  fills; 66 unique URLs), 39 validity records (22 open: 21 concern + 1 contested, on 17 rows),
  31 status reviews (29 confirm / 2 unclear / 0 change), 1 dead link (`link_live`), 59 UNRESOLVED
  with notes. **192 units deferred** to `staging/deepsweep-r5-volga/deferred_units.json` (fills 185,
  cleared refs 6, access-blocked 1) — owed to a later fills pass. Cost 1.18 M subagent tokens,
  **~38 k/row vs R3's ~184 k**, 39 min wall, Sonnet agents. Gates E/F/I/I'/L/M PASS, J skipped (lean);
  advisory A=1 (P2342 all on `saratov-tr.gazprom.ru`), C=43 (a uCoz free-hosted
  `ulianovsk-8422.my1.ru` page carries 19 units on P2286/P2430 — second source deferred), K=112.
  One engine defect logged, not fixed (`staging/deepsweep-r5-volga/DEFECTS.md`): validity records in
  the `contested`/`notes` shape lose their text at merge, so P2390 and P2435 show a blank Finding —
  read their shards. Full numbers: `staging/deepsweep-r5-volga/RUN.txt`; results memo §13.
- **R4a `deepsweep-r4a-urals-yanao`** (30 rows / 183 owed units of 453 — lean pass; 23 operating,
  7 in-development) — delivered 2026-09-21, staged not applied:
  `deliverables/pipelines_batch_20260921_1439_ET_russia-gas_deepsweep-r4a-urals-yanao.xlsx`. 24 fills
  (13 sourced, 11 unresolved), 165 refs added (152 on the tab after folding; 68 unique URLs),
  50 validity records (19 concern open on 16 rows), 30 status reviews (27 confirm / 2 unclear /
  **1 change: P5404 Bovanenkovo–Ukhta VI construction → proposed**), 8 dead links, 22 UNRESOLVED with
  notes. **Lean pass: 270 units deferred** to `staging/deepsweep-r4a-urals-yanao/deferred_units.json`
  (fills 146, access-blocked refs 82 — mostly `*.gazprom.ru` timeouts, cleared refs 42) — owed to a
  later fills pass. Cost 1.36 M subagent tokens, **~45 k/row vs R3's ~184 k** (R5 ~38 k), 57 min
  wall, Sonnet agents. Gates E/F/I/I'/L/M PASS, J skipped (lean); advisory C=15, D=3, K=83. Gate I
  was 4 until the P3507/P5612 Шемордан ЛПУ refs were hand-stamped (the page names «Уренгой-Центр 1, 2»;
  the matcher misses the sheet's spaced-hyphen alias — `staging/deepsweep-r4a-urals-yanao/DEFECTS.md`).
  R5's merge defect was fixed this session (R5 workbook rebuild still owed). Full numbers:
  `staging/deepsweep-r4a-urals-yanao/RUN.txt`; results memo §14.
- **R4b `deepsweep-r4b-urals-south`** (23 rows / 156 owed units of 345 — lean pass) — delivered
  2026-09-22, staged not applied:
  `deliverables/pipelines_batch_20260922_1611_ET_russia-gas_deepsweep-r4b-urals-south.xlsx`. 28 fills,
  115 refs added (47 unique URLs on 22 rows), 31 validity records (13 concern open on 11 rows),
  23 status reviews (20 confirm / 2 unclear / **1 change: P3977 Shumikha–Almenevo proposed →
  operating**), 37 UNRESOLVED with notes. **189 units deferred** to
  `staging/deepsweep-r4b-urals-south/deferred_units.json` (fills 143, access-blocked refs 32, cleared
  14). Cost 1.25 M subagent tokens, **~54.5 k/row** (16 of 23 rows were fully uncited), 46 min wall.
  Gates exit 0; I=1 (P2315 Owner ref, tier cut to low), advisory A=2, K=60. Three engine defects logged
  in the batch's `DEFECTS.md` (one fixed). Full numbers: `RUN.txt`; results memo §15.
- **R6 `deepsweep-r6-siberia`** (32 rows / 180 owed units of 483 — lean pass) — delivered
  2026-09-22, staged not applied:
  `deliverables/pipelines_batch_20260922_1723_ET_russia-gas_deepsweep-r6-siberia.xlsx`. 60 fills,
  78 refs added (48 unique URLs on 27 rows), 42 validity records (27 concern open on 22 rows),
  32 status reviews (20 confirm / 8 unclear / **4 change: P3980, P3981 proposed → operating, P3982
  construction → operating (Omsk отводы), P4056 proposed → construction**), 95 UNRESOLVED with notes.
  **303 units deferred** to `staging/deepsweep-r6-siberia/deferred_units.json` (fills 183,
  access-blocked refs 46, cleared 74). Cost 1.16 M subagent tokens, **~36.3 k/row** (lowest lean batch),
  32 min wall. Gates exit 0; I=5 (P4056, refs name the отвод к ГРС «Прокопьевск»), I'=1 (P5510), advisory
  A=7, K=46. Five engine defects logged in the batch's `DEFECTS.md` (two repeat R4b's). Full numbers:
  `RUN.txt`; results memo §16.
- **R7 `deepsweep-r7-central-south`** (49 rows / 408 owed units of 732 — lean pass; Central + Southern +
  North Caucasus districts + the export trunks starting there) — delivered 2026-09-30, staged not applied:
  `deliverables/pipelines_batch_20260930_1321_ET_russia-gas_deepsweep-r7-central-south.xlsx`. 19 fills,
  301 refs added (126 unique URLs on 48 rows), 55 validity records (32 concern open), 49 status reviews
  (36 confirm / 4 unclear / **9 change: P3973, P3974, P3996, P3997, P4013 proposed → operating, P4130
  construction → operating, P3971, P4142 proposed → construction, P2227 mothballed → operating (contested —
  BOTAS-only evidence for the Turkish section)**), 107 UNRESOLVED with notes. Duplicates flagged: P3997/P3996,
  P4143 = stage 2 of P4142; P2381/P5665 StartState Yaroslavl → Rostov. **324 units deferred** to
  `staging/deepsweep-r7-central-south/deferred_units.json`. Cost 1.66 M subagent tokens, **~33.9 k/row**
  (lowest lean batch), 20 min wall. Gates exit 0; advisory A=14, C=4, K=112. Full numbers: `RUN.txt`.
- **GulfPub recon** (standalone §2, full 285-row roster):
  `deliverables/pipelines_batch_20260914_1648_ET_russia-gas_reconciliation.xlsx` — 739 features,
  546 overlaps, 193 additions (190 NEAR_MISS, 2 DISCOVERY_CANDIDATE, 1 FRAGMENT), 142 GEM-only, 113
  status conflicts (71 GEM `proposed` vs GulfPub `operating` — a lead, not a verdict), 1
  route-replacement candidate; health clean. Not picked up by a handoff packet.
- **OSM recon** (standalone §2, dataset `gas_ru`, full 285-row roster, 2026-09-30):
  `deliverables/pipelines_batch_20260930_1504_ET_russia-gas_reconciliation-osm.xlsx` — 5,520 features,
  135 overlaps, 5,385 additions (3,078 DISCOVERY_CANDIDATE, 2,249 FRAGMENT, 58 NEAR_MISS), 224 GEM-only,
  8 status conflicts, 4 route-replacement candidates. **Health: `MATCH_CONCENTRATION`** — routeless
  capacity-expansion row P3894 is the nearest row for 1,822 records (33%) on length/diameter alone, so
  read every "nearest PID" as arithmetic, not geography; dispositions are geometry-based and unaffected
  (P3894 has 0 overlaps). Only 32.9% of features are named. Staging `staging/recon-osm-20260930/`. Not
  picked up by a handoff packet.
- **Discovery seeds (Step 0)** `staging/discovery-seeds-20260930/` — `seeds_by_district.{csv,json}` +
  `SUMMARY.md`: 88 seeds + 3 length-unknown store leads, 148 monitor, 53 already tracked; per slice D1–D6
  in the summary. Triage memo: `notes/triage-2026-09-30-russia-gas-discovery.md` → Step 0 results.


## Regulators / official data
- **Gazprom PJSC** (`gazprom.ru`) — project pages, annual + sustainability reports, IFRS,
  investor presentations. The 17 **Gazprom Transgaz** regional subsidiaries each publish the
  trunk lines, compressor stations, diameters and pressures they operate — the primary
  source for operating rows. **Gazprom Mezhregiongaz** + the regional gasification programmes
  (`программа развития газоснабжения и газификации <subject> до 2025/2030`) for branch lines.
- **Minenergo** — energy strategy to 2035/2050, general scheme for gas industry development.
- **FAS** tariff orders — list trunk pipelines by name for transport tariffs.
- **Glavgosexpertiza** — per-project approvals naming diameter, length, pressure (strong
  Construction/Start source).
- Regional governments' gasification decrees and press services.

## Key operators / owners
- Gazprom PJSC (near-monopoly trunk owner); Gazprom Transgaz <region> LLCs as operators.
- Independents with own lines: Novatek (Yamal), Rosneft/Sakhalin, Yakutia's Sakhatransneftegaz
  (the Srednevilyuyskoye–Yakutsk family), Norilsk's Norilskgazprom (Messoyakha–Norilsk).
- Export JV counterparts: BOTAŞ (TurkStream/Blue Stream), CNPC (Power of Siberia), Nord Stream AG.

## Preferred sources (beyond the global roster)
- Interfax, TASS, Kommersant, Vedomosti, RBC, neftegaz.ru, OGJ Russia; IEA/OIES for
  export-line analysis; Reuters/Bloomberg for export and sanctions context.
- energybase.ru **geoblocks non-Russian IPs** with a 200 block page (the 2026-08-12
  `url_verifier` false-positive case) — verifier catches it now; add a Wayback snapshot
  alongside, never swap.

## Routing / GIS tips
- 284 of 285 rows already have routes-repo geometry (only P8087 Ishim–Astana missing);
  66 rows are `very low`/`low`/`no route`. Natural Earth admin-1 carries the **federal district**
  as `region` for RU — slice batches on a spatial join of route termini, never on the sheet's
  `Start/EndState/Province` (inconsistent spellings, 26–29 blanks).
- **Tyumen Oblast legally contains KhMAO and YaNAO** (Arkhangelsk contains NAO): a sheet
  `Tyumen region` vs a geometry starting in Khanty-Mansi is vocabulary, not a mismatch.

## Reconciliation notes
- GulfPub gas extract: **739 Russia features** vs 285 rows — viable, will trip the >30
  Additions gate; triage by `disposition`. Features are Latin-transliterated.
- OSM: RU gas extract fetched 2026-09-14 and registered as `gas_ru` in `sources/osm/manifest.yml`
  (`sources/osm/data/osm-ru-gas.geojson`): 5,520 features / ~109,900 km, all lifecycle=operating,
  the largest and richest extract in the registry — the UGSS trunks are drawn end to end (top eight
  ~19,200 km, e.g. Уренгой — Ужгород 3,313 km DN1420) and 1,816 are named (1,798 Cyrillic), 1,611
  carry a diameter, 2,002 an operator (Gazprom transgaz subsidiaries by name). 62% are sub-1 km
  stubs, so the additions pile will be distribution fragments. Ingest smoke-tested (5,520 records,
  all with geometry). Usable as a route source now; the §2 OSM recon is a later campaign step.
- GulfPub recon ran 2026-09-14 (see Batches). P6540 Tambeyskoye–Bovanenkovo absorbed 76 reference
  features (10.3%) — check it is not a catch-all on the Yamal cluster before trusting its overlap.
- **33 PIDs are carried from other scopes' pending staged work** (Ukraine 20, Kazakhstan 15,
  Uzbekistan 7, Iran 1, China 2): `batches/russia-gas/carried_from_others.txt` — research
  legs exclude them, recon keeps them.

## Gotchas
- **Occupied Ukraine is Ukraine, not Russia** (GEM naming-conventions sheet,
  `docs/reference/gem_naming_conventions/`): a line into Crimea/Sevastopol/Donbas is a
  Russia–Ukraine cross-border line, its terminus state a `UKR` subdivision. GGIT has no such row yet.
- Diameters are metric (`1420` = mm, 56 in); capacities bcm/y; pressures MPa (7.5 / 9.8 /
  11.8 classes). `Pressure` is blank on 284 rows and is exactly what a Transgaz page states.
- The I/II/III **string convention** is the dominant row model (49 segment families; up to 8
  rows per family). A system figure restated on a string row is a `spec` concern, not a ref.
- Post-2022 status: Nord Stream 1/2 mothballed (NS1 A+B destroyed 2022-09, NS2 line B intact),
  Yamal–Europe idle since 2022-05, Ukraine transit stopped 2025-01-01, TurkStream the only
  Europe route, Power of Siberia 2 memorandum 2025-09-02 with price unsettled.
- Sanctions-era disclosure thinning: a 2021 Gazprom report may be the last primary source for
  a value — `medium` with the date noted, not `UNRESOLVED`.
- 46 rows are `PipelineType = distribution` (regional gasification branch lines) and 14 are
  blank — a classification question for the validity leg, flag not reclassify.
- State-column vocabulary: `Yamalo-Nenets Autonomus Okrug` (18 rows, typo) vs `…Autonomous`
  (14); `Republic of Komi`/`Komi Republic`; `Sakha Republic`/`Republic of Sakha (Yakutia)`;
  `<X> region` vs `<X> Oblast`; `Reublic of Adygea`; bare `Rostov`/`Orenburg`/`Leningrad`.
  These become `Location [ref]` fills on the shards, as in US batch 5; the state audit's
  `region_audit.csv` (`typos`, `verdict`) lists them per row.
- **gazprom.ru / gazprom.com connect-time-out from a US IP** (measured 2026-09-14; fas.gov.ru
  and rosneft.ru too). Wayback has captures of the project pages — cite the live URL with the
  Wayback capture alongside once the capture is read; the block is an access failure, never a
  reason to drop or skip a Gazprom ref.
- **A Russian-language page and an English GEM name did not match until 2026-09-15.**
  `url_verifier` now romanizes a Cyrillic page (`normalize.translit_cyrillic`) and requires only a
  name's DISTINCTIVE tokens, so `Средневилюйское` matches `Srednevilyuyskoye`. A **translated**
  name still will not (`Сила Сибири` is not `Power of Siberia`), so pass the `OtherLanguage*` form
  as a `name=` variant and never call a Russian page irrelevant off a Latin-name miss. When the
  matcher itself changes, re-check with `backfill_name_found.py --recheck-false`.

## Open items
- **R6 Siberia leads (2026-09-22):** P7615 Capacity 4.10 kept (NF's split; rules with P2350) — new:
  string II's StartYear1 2012 is the Yurga stretch only, the Novokuznetsk stretch was still being built
  in Oct 2025, and StartLocation Vertikos looks like segment I's; existence questions on P3367
  Barnaul–Shakhi (= P3368's Shakhov–Rebrikha отвод?), P2703 Achinsk–Abakan, P2705 Ust-Kamovskaya–Achinsk,
  P4110 Karasuk–…–Chany; P3604 Angarskaya looks like the Kovykta trunk (P2327/P5510); P5091 vs P0734
  PoS-2; P6535 Owner1 Sonatrach is wrong and 28.50 bcm/y is the whole Eastern system's; P5510's sudact.ru
  ref never names the line (Capacity 0.00 = placeholder); Omsk отводы P3980–P3982, P3368, P4056 recorded
  `distribution` but sourced as отвод-to-GRS (P5517 the reverse); P2283 Diameter 16 in vs 720 mm (PDF
  unfetchable); P6683/P6684 1.80 per-string vs combined; P6674 operator may not be Transgaz Tomsk.
- **R4b Urals-south leads (2026-09-22):** P2378 Punga–Vuktyl–Ukhta I carries line II's 1420 mm / 1976
  (line I = 1220 mm / 1977 — staged as fills); P2350 Capacity — the row's own ref states 8.2 bcm/y for
  the whole line and string II was built piecemeal, against NF's documented 4.10 even split (ruling
  for NF/Baird; P7615 moves with it, and sits in R6); P2320 carries «2-ая нитка» but is нитка I;
  Kurgan P3975/P3977/P3978/P3979 are отвод-to-ГРС objects (classification flag); P3975's 84 km belongs
  to the Shumikha–Mishkino–Yurgamysh segment; P2429 may be a segment of Bukhara–Ural I; P5686 sourced as
  its own 1020 mm line, not a looping; P2357/P5745 SRTO–Ural I/II share 1986 km and one energybase slug;
  `Gazrpom Transgaz Tomsk LLC` is a typo'd entity string on the owners tab (3 rows).
- **R4a Urals-YaNAO leads (2026-09-21):** P5402/P5403/P5404 Bovanenkovo–Ukhta IV/V/VI LengthKnown
  1158.60 km is String III's (P2287) figure — the cited severgazprom PDF never names IV/V/VI;
  P2348/P4145/P4146 Nadym–Punga I/II/III geometry measures ~60/60/50 km against 696/605/566 km at
  `RouteAccuracy = high` (§8 candidates), and P4146's Length ref (aup.ru) states a 1238 km combined
  figure; P4311 Yamburg–Tula II LengthKnown 3113 vs 2146 km in the ЭРТА table that matches string I
  exactly; P2450 (string I) carries P4311's «…вторая нитка» Russian name, and the two rows' route
  files look like one trace; P0737/P0738 SegmentCost $20 B each is an even split of a two-line
  aggregate; P7546 Medvezhye–Nadym I LengthKnown 118 vs 57 km (one source — no change), and
  P7546/P7547 status `unclear` (no post-2023 source names the line); P3506's gem.wiki-cited TPU thesis
  belongs to P5612 Urengoy–Center 2.
- **R5 Volga leads (2026-09-16):** P2340 vs P5744 Minnibaevo–Kazan — which of the 1954/1963 lines was
  converted to the ethane pipeline (kazan-tr.gazprom.ru and Wayback both unreachable in-session);
  P4063 Zorkino–Balakovo existence (both gem.wiki citations dead) and P4063/P4112 recorded
  `distribution` though sourced as газопровод-отвод to a GRS; P2383 Saratov–Gorky — the operator's
  own history calls the corridor распределительный; P2430 LengthKnown 263 → 152 km staged;
  P1466/P5656 Petrovsk–Elets 16.4 bcm/y is a two-pipe system total carried on both rows; P2425
  SegmentCost 53.12 bn RUB unsourced; P5714 geometry traces Perm–Gorky, not Nizhnyaya Tura–Perm
  (§8 candidate); P2390 Diameter 377 vs 530 mm and P2435 325 vs 300 mm (text in the shards only).
- Duplicate suspects for the validity leg: P0758 vs P2027 (Sakhalin–Khabarovsk–Vladivostok);
  P0734 vs P5409 (Power of Siberia 2 / Soyuz Vostok); P2327/P5510 (Kovykta–Sayansk–Irkutsk,
  both proposed, no segment names); P7538 "I" vs P5540 "II" (Vuktyl–Ukhta); P0765/P1368
  TurkStream strings.
- P8087 Ishim–Astana: the one row with no geometry.
- **P5539 Punga–Ukhta–Gryazovets IV — route fragment (R2).** The routes-repo geometry is 1 of the 13
  OSM member ways of relation 17195756: ~135 of ~943 km, ending deep in Komi, nowhere near
  Gryazovets, while the row recorded `RouteAccuracy = high`. R2 stages the downgrade to
  `low (subnational, imprecise, or unranked)`; `RouteType` stays `Mapped route (at any accuracy)`
  (a fragment is still mapped). **Owed: a §8 redigitization of the full relation.** Same row also
  carries a misattributed `zaogsp.ru/istoriya/punga` citation (a different, Punga-end 1976 object
  under Transgaz Yugorsk — already removed from Fuel/PipelineType/Status), a contested
  `FuelSource` (Medvezhye vs Urengoy), and a three-way ordinal disagreement (OSM "4" / company
  newspaper "III" / siyanie-severa "Уренгой — Ухта — Грязовец") logged as informational.
- **P7560 Volkhov–Petrozavodsk–Kondopoga: status UNRESOLVED (R2)** — the one row in the batch whose
  status the pass could not settle.
- **Sakhatransneftegaz StartYear1 is one family question, not four cells**: P3364/P6691 carry an
  unsourced 1982; P3365/P6695 (530 mm strings I/II) carry 2014 while the operator's own commissioning
  table and a government press release put String I at 1967. Decide the family together (R1 validity).
- **P7537 Ukhta–Torzhok IV carries the WRONG Cyrillic name (R3).** `OtherLanguageName` /
  `OtherLanguageAlias` read `Газопровод Ухта - Торжок - 3 (III) (Ямал)` — that is the III нитка,
  which is P2707. Directive 3302-р (16.11.2024) lists `Ухта - Торжок. III нитка (Ямал)` (item 10)
  and `IV нитка (Ямал)` (item 13) as two separate designated objects, mirroring Bovanenkovo–Ukhta
  III/IV at items 8/12, so the pre-batch **P2707/P7537 duplicate suspect is SETTLED: not a
  duplicate**. The name should read `4 (IV)`. Its recorded 972.60 km is the same miscitation —
  the cited PDF says `Магистральный газопровод Ухта-Торжок - 3 … 972,6 км`, twice, never IV — so
  P7537's length is unsourced until a IV-specific figure is found. Fix the name; delete neither row.
- **The Karelia 40 bcm/y cluster: P4094 / P4095 / P4096 restate one corridor figure (R3).**
  Decree 816-р item #388 covers the whole Volkhov–Segezha–Kostomuksha corridor with no per-stage
  breakdown, and 40.00 bcm/y (plus 1400 mm) has been copied onto all three stage rows. Separately,
  **P4094 `SegmentCost = 49,980,000` is a magnitude error** — 49.98 bn ₽ is Gazprom's commitment for
  the entire 2021–2025 Karelia gasification programme, not this segment. The three rows' merger
  (Interfax, Mar-2024) vs re-separation (decree, Nov-2024) history is left unresolved.
- **P4092 Kuznechnoe length 114.5 vs 111.3 km (R3)** — the sheet's 114.5 km comes from the
  as-designed engineering survey with full PK chainage (`kuznechnoe.lenobl.ru tom_1.pdf`); 111.3 km
  is the operator's Apr-2023 press release and its two republications, i.e. ONE origin.
  Preliminary-vs-as-designed, not an error, but unresolved; status left `unclear` for the same reason.
- **P4150 Bezhanitsy-area existence (R3)** — both of the row's only harvested citations fail to
  support this specific pipeline. A dormancy candidate the pass would not infer without evidence.
- **P5584 Belousovo (R3)** — the parent trunk is confirmed real and operating, but `Capacity =
  7.00 bcm/y` rests solely on an access-gated `consultant.ru` document, and the row's geography
  reads Leningrad where the sources put it in Kaluga.
- **12 classification concerns on the отвод-vs-межпоселковый line (R3)** — flagged row by row, never
  reclassified: a `газопровод-отвод` is transmission (transgaz-operated, terminates AT a ГРС),
  `межпоселковый` is distribution (Gazprom Gazoraspredeleniye, downstream of the ГРС).
- **Ukraine / Kazakhstan / Uzbekistan relevance stamped 2026-09-15 — DONE, workbooks NOT rebuilt.**
  Those three were swept under the broken Cyrillic matcher (delivered 2026-08), but the premise was
  wrong in one way worth recording: their stores carried **no `name_found` stamps at all**, true or
  false — the field postdates them — so `--recheck-false` had nothing to re-check. A plain
  `backfill_name_found.py --staging <dir> --shards store --apply` over all 13 staging dirs stamped
  **1,440 verifications from evidence under the fixed matcher: 907 name the pipeline (63%), 533 do
  not**. Per country: Ukraine 495 (248/247), Kazakhstan 682 (455/227), Uzbekistan 263 (204/59).
  The 533 cap at `low` downstream whenever those countries' workbooks are next rebuilt — that
  rebuild is deliberately deferred (Baird 2026-09-15, finish Russia first) and wants doing in the
  same per-country pass as the `repair_independence` and phantom-stub items in
  `docs/research_backlog.md` §2. 13 refs stayed UNKNOWN rather than be stamped false: **8 confirmed
  404s on `eegas.com`** (`ukr_090115e.htm`, `ukr_090115r.htm`, `belarus1.htm` — real dead links in
  Ukraine's `qc` + `ref-sweep-operating`, the one class that may drop a ref), one `rg.ru` 401, two
  scanned Kazakh PDFs with no text layer (`cnpc-amg.kz`, `zhylyoigas.kz`) and two `доступ ограничен`
  interstitials (`online.zakon.kz`, `prg.kz` — keep the ref, add Wayback alongside). Wayback
  `ConnectionError`s on the first pass were rate, not ban: a retry at `--sleep 1.5` recovered all 14.
