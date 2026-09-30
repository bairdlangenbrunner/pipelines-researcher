SCOPE: RUSSIA gas, batch R1 of 8 — FAR EASTERN FEDERAL DISTRICT (Sakhalin, Yakutia, Khabarovsk,
Primorye, Amur, Kamchatka, Chukotka, Buryatia) plus the district's cross-border lines into China,
Mongolia, Japan and Korea. 32 rows: 17 operating, 5 construction (P3175 Aykhal–Udachny Branch,
P4111 Bolshoy Kamen–Vrangel, P5521 Belogorsk–Khabarovsk, P6710 Srednetyungskoye–Nakyn, P7600
Tas-Yuryakhskoye–Verkhnevilyuchanskoye), 4 proposed (P3895 Dalnerechensk–Hulin, P3896
Kysyl-Syr–Amga–Ayan, P5409 Soyuz Vostok, P6682 Srednebotuobinskoye–Novolenskaya CHP), 2 shelved
(P1440 Trans-Korea, P4559 China-Russia Binhai-Jilin) and 4 cancelled (P0828 Sakhalin–Hokkaido,
P2706 Yakutsk–Aldan, P3208 Power of Siberia Phase I Expansion, P3603 Power of Siberia 2 Sayansk
Branch). The batch is dominated by three families: the Gazprom export/trunk system (Power of
Siberia I and II, Sakhalin–Khabarovsk–Vladivostok and its Far Eastern route to China), the
Sakhatransneftegaz Yakutia trunk (8 rows of the Srednevilyuyskoye–Yakutsk string family), and the
Alrosa-Gas / Sakhalin / Kamchatka / Chukotka regional lines. Baird chose 2026-09-14 to deep-sweep
every Russia row ONCE with status review ON, sliced by federal district — this is the ONLY pass
these rows get this cycle: do the status work and the data work together. This is the campaign's
PILOT batch; its defects set the calibration for R2–R7, so write your researcher_notes so the
orchestrator can see what worked and what did not.

CALIBRATION — 484 owed units over 32 rows: HAS_REF 233 / MISSING_REF 102 / MISSING_VALUE 149 (64 of them
operator/owner). The builder's up-front HTTP check on the 233 HAS_REF units found 150 all-live, 83
with a dead-or-missing link, and 139 live but NOT naming the pipeline in the verifier's Latin-name
fuzzy match (the Cyrillic-name relevance read is owed on every one of those). BUT read the 83 with
care: only 4 of their link checks are true 404s (aostng.ru x2, arcticpost.ru, sakhalinenergy.ru);
35 are ConnectTimeout on gazprom.com (19), krasnodar-dobycha.gazprom.ru (8), peretok.ru (5),
rostender.info (2), gazprom.ru (1); 8 are 403 (e-disclosure.ru x7, tass.ru); 4 are 401 (reuters
x2, rg.ru, rbc.ru). Every one of those 47 non-404s is an ACCESS FAILURE from this IP — read it
through Wayback or with a browser UA and grade it on content; DEAD_LINK is for the 4 confirmed
404s only. Fills owed: 149 (by column: Pressure 32, Proposal 24, SegmentCost 23, Construction 21,
Diameter 13, Operator 13, Start 8, Capacity 6, FuelSource 5, Length 3, Owner 1; by status:
operating 67, cancelled 31, construction 21, shelved 17, proposed 13). Pressure is blank on
every row — a Gazprom/Transgaz/Glavgosexpertiza page states it for the trunk lines; for the
small Yakutia and Chukotka lines a dated UNRESOLVED naming what was read is the honest answer.
Read UNRESOLVED the way India and Ukraine were read, NOT Pakistan: this is a well-documented
Gazprom-dominated district and a blank ref means nobody looked, so UNRESOLVED is unfinished work
unless the note names the documents that do not state the value. Harvested pool: 783 citations,
246 distinct URLs, 32 of 32 gem.wiki pages fetched (P4559 has 0 citations; the Sakhatransneftegaz
family rows share one 31-citation pool each — the same documents cover all 8 siblings).

THE LANGUAGE IS RUSSIAN. There is no FERC/EIA analogue; the primary record is Gazprom's, its
subsidiaries', the regional governments' and the Russian trade press's, almost all in Russian.
Search in Russian FIRST (the worklist's `OtherLanguageName` where present; otherwise transliterate
back: Сила Сибири, Сахалин – Хабаровск – Владивосток, Кысыл-Сыр – Мастах, Средневилюйское ГКМ –
Якутск, Таас-Юрях – Мирный – Айхал, Соболево – Петропавловск-Камчатский, Западно-Озерное –
Анадырь, Оха – Комсомольск-на-Амуре, Белогорск – Хабаровск, Большой Камень – Врангель,
Дальнереченск – Хулинь, Союз Восток). Vocabulary that finds the documents: `магистральный
газопровод`, `МГ`, `газопровод-отвод`, `протяжённость … км`, `диаметр 1420 мм` / `DN 1400`,
`рабочее давление … МПа`, `производительность … млрд куб. м в год`, `ввод в эксплуатацию`,
`Главгосэкспертиза`, `положительное заключение`, `компрессорная станция (КС)`. A page in
Russian that names the line in Cyrillic is `name_found: true` — read it, encode the match in the
verification `note` with the matched Cyrillic string; the verifier's fuzzy match on a Latin name
WILL miss Cyrillic. Never mark a Russian page "does not name the pipeline" off a Latin-name miss.

EVERY WORKLIST UNIT IS OWED A RECORD — INCLUDING THE ALREADY-CITED ONES. Almost half of this
batch's ref-bearing units already carry a `[ref]` (class `HAS_REF`). `check_shard_coverage.py`
lists a HAS_REF unit with no record exactly like a skipped blank. For each HAS_REF unit:
- Open the cited URL(s) (the worklist's `current_ref`, and `existing_ref_checks` where the builder
  already HTTP-checked them). Does it resolve, NAME this pipeline/segment, and STATE the value?
  - Yes -> `class_out: "REVERIFIED"`, `values` = the recorded value, `proposed_refs` = the existing
    ref(s) you re-verified PLUS the second independent source if you found one (the second source
    is still owed — rule 4d), `verifications` for each.
  - Resolves but does not state the value, or does not name the pipeline (a system page on a
    string row, a field page, a terminus/city page, an aggregate Gazprom statistic) -> the cell is
    effectively UNCITED: find the document that does state it and stage it as REFS_ADDED; if
    nothing states it, UNRESOLVED saying so. Keep the old ref in `researcher_notes`, never
    silently dropped.
  - Confirmed 404/410 -> `class_out: "DEAD_LINK"` with the Wayback capture if one exists, plus a
    replacement source. A 403/timeout/WAF/geo-block is NOT dead — never retire a ref over an
    access failure. **This matters more here than anywhere: the builder's existing-ref check ran
    from a US IP that the gazprom.ru zone does not answer (see MEASURED CONDITIONS). A
    `existing_ref_checks` entry with a timeout on a gazprom.ru / *.gazprom.ru / *.gov.ru host
    is an ACCESS FAILURE — read the page through Wayback and grade it on its content.**
  - The source DISAGREES with the recorded value -> stage the sourced value AND a `spec` concern.
- Where one document re-verifies several HAS_REF cells, say so once and stage it on each.
- `sudact.ru` (19 refs) and `legalacts.ru` are court-decision aggregators: a judgment that names
  the pipeline and a figure is a real document (name_found true) but a weak origin for a spec —
  medium at best, and never the second source for a `high`.

STATUS REVIEW IS ON FOR EVERY ROW (one status_reviews object per row).
- **Operating rows (17):** the question is whether each is STILL operating and whether StartYear1
  is right. A clean "still operating" verdict needs a dated source newer than LastUpdated (a
  2024–2026 Gazprom/Transgaz/operator page, an annual report, a regional gasification report,
  Interfax/TASS reporting flows) — say which. Post-2022 disclosure thinning means a 2021–2023
  source may be the newest primary one; that is `confirm` with the date noted, not `unclear`.
  Specific leads (VERIFY, do not copy): Power of Siberia reached its 38 bcm/y design in 2025 and
  Gazprom/CNPC agreed in Sept 2025 to raise it to 44 bcm/y (P2352 — a capacity CHANGE candidate
  only if a dated source states the new design figure, otherwise a note); the Kovykta–Chayanda
  section (P2353) came on stream Dec 2022 — its start year should be 2022 not the field's date;
  the Sakhalin–Khabarovsk–Vladivostok trunk (P0758) has run since Sept 2011 and its second
  Komsomolsk–Khabarovsk string (P2027) is a separate physical string — establish that before
  treating P2027 as a duplicate; P1783 TransSakhalin's owner changed in 2022 (Sakhalin Energy
  Investment Company Ltd → Sakhalin Energy LLC, the Russian successor; Shell's 27.5% stake was
  reallocated) — an attribution finding on Owner, with the date.
- **Construction rows (5):** confirm construction is underway with a dated source newer than
  LastUpdated, or find the completion. P4111 Bolshoy Kamen–Vrangel (start target 2022, LastUpdated
  2022) is very likely operating — source the commissioning; P3175 Aykhal–Udachny (2023 target)
  same question; P6710 Srednetyungskoye–Nakyn (2025 target) — find the Sakhatransneftegaz /
  Alrosa commissioning or the slip; P5521 Belogorsk–Khabarovsk (2027 target, Gazprom) — confirm
  the construction start date and what has been laid; P7600 Tas-Yuryakhskoye–Verkhnevilyuchanskoye
  (no route, no length, no diameter) — establish what this line IS (lead: the Rosneft /
  Taas-Yuryakh Neftegazodobycha gas supply into Power of Siberia agreed 2022) before anything
  else; if it is a field-connection line inside Rosneft's licence, say so as a classification
  concern.
- **Proposed rows (4):** confirm with a dated source NEWER than LastUpdated, or find the change.
  P3895 Dalnerechensk–Hulin is the cross-border piece of Gazprom's "Far Eastern route" (10 bcm/y
  contract with CNPC signed Feb 2022; supplies from 2027; the Sept 2025 memorandum raised the
  route to 12 bcm/y) — Gazprom has reported construction under way on the Russian side: proposed
  -> construction is the status question, with the date. P5409 Soyuz Vostok (the Mongolian
  section of Power of Siberia 2, 962.9 km, 1,420 mm, 50 bcm/y): the Sept 2, 2025 Gazprom–CNPC
  memorandum is described by Gazprom as legally binding with price open — that keeps it
  `proposed`, but the StartYear1 (2030) and ProposalYear need a source; the Russian section P0734
  is NOT in this batch (R6 Siberia) — write cross_row_leads for it. P3896 Kysyl-Syr–Amga–Ayan
  (Globaltec, 1,358 km, 28 bcm/y, EUR 5 bn — an LNG-export scheme to the Okhotsk coast): is
  there any activity after 2022? If nothing since the announcement, `stale` with the last dated
  mention. P6682 Srednebotuobinskoye–Novolenskaya CHP (2028): the gas supply line for RusHydro's
  Novolenskaya TPP at Lensk — verify the sponsor (Alrosa-Gas is recorded; RusHydro and
  Gazprom/Rosneft are the other candidates) and the 2028 date.
- **Shelved rows (P1440 Trans-Korea, P4559 China-Russia Binhai-Jilin):** both lack ShelvedYear and
  ShelvedCancelledType — owed. Trans-Korea (KOGAS–Gazprom roadmap 2011, dormant since ~2013,
  sanctions since 2022): find the last dated statement and grade `inferred` vs `confirmed`. P4559
  is a Chinese-side scheme (Hunchun, Jilin) whose only English record may be GEM-derived — test
  existence in Chinese (中俄滨海-吉林海外天然气登陆通道 / 珲春) before anything else; if the only
  traces are GEM, existence concern.
- **Cancelled rows (4):** the question is whether the cancellation is RIGHT and SOURCED. P0828
  Sakhalin–Hokkaido (CancelledYear 2021, `confirmed`) — find the dated JPDO/Gazprom statement.
  P2706 Yakutsk–Aldan (no year, no type) — owed both; the Yakutia gasification programme may have
  replaced it with another routing, which is `cancelled` with a reason, or it may be alive under
  another name (then a status change). P3208 Power of Siberia "Phase I Expansion"
  (Blagoveshchensk–Khabarovsk, 620 km, 32 bcm/y, cancelled) vs P5521 Belogorsk–Khabarovsk
  (Svobodny–Khabarovsk, 828 km, 28 bcm/y, construction): these are very likely ONE project under
  two names — the link between Power of Siberia and the Sakhalin–Khabarovsk–Vladivostok system.
  Decide it: if P5521 IS the built version of P3208, P3208 is a duplicate concern naming P5521
  (not "cancelled"), and the two rows' specs must not be cross-cited. P3603 Power of Siberia 2
  Sayansk Branch (no specs, no locations, cancelled) — establish what was proposed and when it
  died; the Kovykta–Sayansk–Irkutsk rows P2327/P5510 are in R6, not here — cross_row_leads if a
  document covers them. A cancelled row still needs its specs sourced AS PROPOSED.
- For every non-operating row with a status change, put the new Status in BOTH
  `status_reviews[].proposed_changes` and the Status fill (the two must agree — never stage the
  old Status as REVERIFIED while your status review proposes a new one). A flip to operating on
  a row carrying CancelledYear/ShelvedYear is a CLEARING: keep the honest ref record, put
  `{"CancelledYear": ""}` in `contested` and `proposed_changes`, and say the `[ref]` clears with it.

STATE CELLS AND ROUTES — the state audit (`batches/russia-gas/staging/state-audit-20260914/
region_audit.csv`) joined every row's routes-repo geometry to Natural Earth admin-1. Its
findings for this batch are LEADS you must judge, not edits to copy:
1. **Judge the route first.** Is the geometry, at its termini, the right project (not the parent
   system, a sibling string, or a different pipeline)? Check it against sourced maps (Gazprom's
   project-page scheme, the operator's system map, a Glavgosexpertiza approval's route
   description, a regional gasification-programme map). Give the geometry's first and last
   points in plain words in researcher_notes.
2. **Then decide the cells.** If the route is right and the cell is wrong -> a fills[] record on
   `Location [ref]` with `value_cols: ["StartState/Province", "EndState/Province"]` and the sourced
   subjects, plus an `attribution` concern with `contested: {"StartState/Province": "<subject>"}`.
   If the route is wrong -> a validity concern `contested: {"RouteAccuracy": "<your grade>"}`, the
   recommendation "route candidate for §8" with the sourced termini, and the cells stay as
   sourced. Both can be wrong. Never edit a state cell to match a bad route, and never propose
   coordinates. A route digitized in the reverse direction is not a mismatch — say so and move on.
3. **Subject names.** The sheet's canonical spellings are the English federal-subject names
   (`Sakhalin Oblast`, `Khabarovsk Krai`, `Primorsky Krai`, `Amur Oblast`, `Kamchatka Krai`,
   `Sakha Republic`, `Chukotka Autonomous Okrug`, `Republic of Buryatia`, `Irkutsk Oblast`) — the
   audit's `typos` column lists this batch's variants (`Sakhalin region`, `Primorsky territory`,
   `Khabarovsk Territory`, `Amur region`, `Amur Oblas`, `Yakutia`, `Republic of Sakha (Yakutia)`,
   `Respublic of Sakha (Yakutia)`, `Kamchatka territory`, `Chukotka Autonomus District`). Stage
   the corrected spelling as a `Location [ref]` fill with a source that places the termini (the
   spelling is mechanical; the ref is still owed). Foreign termini keep their own subject
   (`Heilongjiang`, `Jilin`, `Hokkaido`, `Selenge Province`) with the country in EndCountry.
This batch's cases:
- **P2352 Power of Siberia Phase I** — start state BLANK, end `Amur Oblas` (typo); route runs
  Sakha Republic -> Sakha Republic per the audit (the very-high-accuracy geometry may be the
  Chayanda–Blagoveshchensk line stored in a way whose last point is not the border — check the
  last coordinate). Sheet start `Yakutia`, end blank. Source: Chayanda field (Sakha) to
  Blagoveshchensk (Amur Oblast) at the Amur river crossing.
- **P2353 Phase II Kovykta–Chayanda** — start blank, end `Yakutia`; geometry Sakha -> Irkutsk
  (reverse direction). Source: Kovykta field (Irkutsk Oblast) to Chayanda (Sakha Republic).
- **P5409 Soyuz Vostok** — sheet start `Republic of Buryatia` (Kyakhta), end `Shanghai`; geometry
  starts in Shanghai (CN) and ends in Selenge Province (MN). The Mongolian section runs Kyakhta/
  Altanbulag border -> Mongolia -> Chinese border at Zamyn-Üüd/Erenhot; a geometry that reaches
  Shanghai is the CHINESE onshore continuation, not Soyuz Vostok. Grade the route, and source
  the sheet's termini (end should be the Mongolia–China border, not Shanghai) — an attribution
  concern with `contested: {"EndState/Province": "<sourced>"}` if the sources agree.
- **P0828 Sakhalin–Hokkaido** — start blank (route starts Sakhalin Oblast, ends Chiba Prefecture
  JP — the proposed line ran Sakhalin -> Hokkaido -> Tokyo area, so the sheet's `Hokkaido` end may
  be the first landfall only). Source the concept's termini; fill the start (`Sakhalin Oblast`).
- **P1440 Trans-Korea** — both blank; route Primorsky Krai -> South Gyeongsang (KR). Fill both
  from the 2011 roadmap documents (Vladivostok -> via DPRK -> South Korea).
- **P2706 Yakutsk–Aldan** — both blank; a 2-point straight line inside Sakha. Fill both `Sakha
  Republic` with the source that describes the project.
- **P3603 Sayansk Branch** — both blank; route Republic of Buryatia -> Irkutsk Oblast. Source what
  the branch was and fill from that.
- **P4559 Binhai-Jilin** — start blank; the 2-point geometry sits entirely in Jilin (CN). If the
  project's Russian landfall is documented (Primorsky Krai — Zarubino/Kraskino area), fill it;
  otherwise leave blank and say so.
- **P7600 Tas-Yuryakhskoye–Verkhnevilyuchanskoye** — NO ROUTE, both cells `Sakha Republic`. Source
  the endpoints; note the sourced termini so a §8 route can be drawn later.
- **P2424 Sobolevo–Petropavlovsk-Kamchatsky** — StartLocation reads `Sobolevsky
  DistrictPetropavlovsk-Kamchatskiy` (two cells run together). Stage `Sobolevsky District` on
  `StartLocation` with the source, and note the end is Petropavlovsk-Kamchatsky.
- Straight-line routes (`very low`): P2706, P3895 Dalnerechensk–Hulin, P4559, P6690
  Zapadno-Ozernoye–Anadyr, P6710 Srednetyungskoye–Nakyn. The grade is already honest; note the
  sourced termini so a §8 route can be drawn later, but do not file a concern just for `very low`.

DUPLICATES AND FAMILIES — get these right before anything else:
- **Power of Siberia (Сила Сибири), 4 rows here: P2352 Phase I (Chayanda–Blagoveshchensk, 2,200
  km, 1,420 mm, 38 bcm/y, 2019), P2353 Phase II Kovykta–Chayanda (800 km, 2022), P3208 Phase I
  Expansion (cancelled — see above), P7600 Tas-Yuryakhskoye–Verkhnevilyuchanskoye (a feeder).**
  The system is ~3,000 km Kovykta -> Chayanda -> Blagoveshchensk; the SYSTEM figure (3,000 km,
  the 38 bcm/y export contract, the ~RUB 1.1 tn programme cost) is never a ref for a STRING
  cell. P2352's SegmentCost `55,000,000,000 USD` is almost certainly the whole Eastern Gas
  Programme / field-plus-pipeline aggregate — test it against Gazprom's own pipeline budget and
  file a `spec` concern if it is not the pipeline's own figure. Capacity 38 bcm/y belongs to the
  export contract; the pipeline's design throughput per section may differ — say which figure
  each source states.
- **Power of Siberia 2 / Soyuz Vostok: P5409 (Mongolian section) here; P0734 (Russian section)
  and P2327/P5510 (Kovykta–Sayansk–Irkutsk) in R6; P3603 Sayansk Branch here.** Do not cross-cite
  the 50 bcm/y, 2,600-km system figures onto P5409's 962.9-km Mongolian cells unless the source
  states the Mongolian section's own numbers (the Gazoprovod Soyuz Vostok feasibility study,
  approved Jan 2022, does).
- **Sakhalin–Khabarovsk–Vladivostok (SKV), 3 rows: P0758 trunk (1,822 km, 1,220/700 mm, 2011),
  P2027 Komsomolsk-on-Amur–Khabarovsk II (390.8 km, 15 bcm/y, 2021), P3895 Dalnerechensk–Hulin
  (the Far Eastern route spur to China).** P0758 vs P2027 is the batch's named duplicate suspect:
  the second string Komsomolsk–Khabarovsk was built 2019–2021 to raise SKV throughput toward
  Khabarovsk — if so it is a legitimate separate string (LengthKnown = its own length) and NOT a
  duplicate, but its Capacity `15 bcm/y` needs a source that states it for the second string, and
  P0758's Capacity `20 bcm/y` vs the trunk's 30 bcm/y design (first stage 6 bcm/y) needs
  reconciling in a `spec` concern. P0758's SegmentCost `24,000,000,000 USD` — test it (Gazprom's
  reported cost was in the RUB 400–470 bn range; a USD 24 bn figure may be a system/programme
  aggregate). P3895's cost `25,700,000 RUB` for a 25-km, 1,020/1,200-mm river crossing is far too
  small — likely a units error (thousands or millions); source the real figure or file `spec`.
- **Sakhatransneftegaz Srednevilyuyskoye–Yakutsk family, 8 rows: P3365 Kysyl-Syr–Mastakh I
  (84 km, 530 mm, 2014), P6695 Kysyl-Syr–Mastakh II (84.2 km, 530 mm, 2014, EndLocation reads
  `Yakutsk` — check), P3361 Kysyl-Syr–Mastakh III (84 km, 700 mm, 2.9 bcm/y, 2024, RUB 8.57 bn),
  P3364 Mastakh–Berge I (184 km, 530 mm, 1982), P6691 Mastakh–Berge II (183.8 km, 1982), P2334
  Taas-Tumus–Yakutsk I (200 km, 530 mm, 1967), P6696 Taas-Tumus–Yakutsk II (201.9 km, 1978),
  P6694 Mastakh–Yakutsk III (382 km, 720 mm, 2014).** The trunk is three strings from the
  Srednevilyuyskoye/Mastakh fields to Yakutsk (≈ 380–390 km each); the row model is
  string-by-section. Read the family as a WHOLE from one document set (aostng.ru, the Yakutia
  government's gasification pages, ysia.ru, ulus.media, the Sakhatransneftegaz annual report /
  e-disclosure.ru) and stage the same document on every sibling cell it states, via
  cross_row_leads naming the sibling PID. Do not attach a string-III figure to a string-I row.
  Two of the pairs have identical values on I and II (P3364/P6691, P2334/P6696) — confirm each
  string's own year and diameter rather than assuming.
- **Alrosa-Gas: P2431 Tas-Yuryakh–Mirny–Aykhal (686 km, 1 bcm/y, 2002) and P3175 Aykhal–Udachny
  Branch (57 km, 300 mm, 2023, RUB 5.8 bn).** The row family name is "Tas-Yuryakh–Mirny–Udachny";
  the Udachny branch is the 2023 extension. Alrosa's annual reports and press releases, the
  Yakutia government and Glavgosexpertiza are the sources. P3175's Capacity `0.72
  mill.Sm3/day` is a non-standard CapacityUnits string — stage the sourced figure in the
  sheet's unit if a source gives bcm/y or million m3/day, and note the unit.
- **Yakutia feeders and gasification: P6710 Srednetyungskoye–Nakyn (Sakhatransneftegaz to
  Alrosa's Nyurba mine), P6682 Srednebotuobinskoye–Novolenskaya CHP, P3896 Kysyl-Syr–Amga–Ayan,
  P2706 Yakutsk–Aldan, P7600.** Distinct projects; the Yakutia gasification programme
  (`программа газификации Республики Саха (Якутия)`) and RusHydro's Novolenskaya TPP pages
  are the common document set.
- **Sakhalin: P1783 TransSakhalin (Sakhalin-2, 472 km? — the onshore gas trunk from the OPF to
  Prigorodnoye is ~800 km including the oil line's parallel; source the GAS pipeline's own
  length and 1,220 mm), P1824 Okha–Komsomolsk (Rosneft, 1987, Length/Diameter/Capacity all
  blank — owed), P0828 Sakhalin–Hokkaido (cancelled).** P1783's Capacity `18.6 mtpa` is a gas
  pipeline in LNG-plant units — find the pipeline's design throughput (bcm/y) and file the unit
  question as a `spec` note. P1824 is the 1987 Sakhalin–mainland gas line (Okha -> Komsomolsk-on-
  Amur, across the Nevelskoy Strait) — Rosneft/Sakhalinmorneftegaz and Gazprom Transgaz Tomsk
  (which took over its operation) are the sources.
- **Kamchatka / Chukotka singletons: P2424 Sobolevo–Petropavlovsk-Kamchatsky (Gazprom, 392 km,
  530 mm, 2010, RUB? — SegmentCost reads `3,000,000,000 USD`, implausible for a 392-km 530-mm
  line; the reported cost was in RUB) and P6690 Zapadno-Ozernoye–Anadyr (Sibneft-Chukotka, 105
  km, 219 mm, StartYear blank — owed; the line feeds the Anadyr CHP since ~2008).**
- **Cross-border: P3895 (Heilongjiang), P4559 (Jilin), P5409 (Mongolia), P0828 (Japan), P1440
  (Korea).** Chinese-side sources (CNPC, PipeChina, NDRC, provincial DRCs) exist for P3895 and
  P4559; read them in Chinese.

LENGTHS AND UNITS. Everything is metric: LengthKnown in km, Diameter in mm (1,420 mm = 56 in;
1,220 = 48; 1,020 = 40; 720/700 = 28; 530 = 21; 325/300 = 12; 219 = 8), Capacity in bcm/y
(a Russian source's `млрд куб. м в год`), Pressure in MPa (7.5 / 9.8 / 11.8 classes — `Pressure`
is blank on every row and is the one column a Gazprom/Transgaz page routinely states: look). A
source in `млн куб. м в сутки` (million m3/day) converts to bcm/y by ×0.365; a source in
`тыс. куб. м/ч` by ×0.00876. Read YOUR row's units cells before writing a number, and convert
into the sheet's unit with the conversion in the note. P1440's Capacity is in `MMcf/d` (1,071 ≈
11.1 bcm/y) — keep the row's unit. Multi-value diameters (`1220, 700`; `325, 1020`; `1020, 1200`)
are the sheet's convention for a line with sections of different size — a source stating one of
them supports the cell with the other noted.

OWNERSHIP. Leads to verify, not answers: Gazprom PJSC (the trunk and export rows; operators are
Gazprom Transgaz Tomsk for the Far East — Power of Siberia, SKV, Kamchatka — and Gazprom Transgaz
Khabarovsk did not exist: check which subsidiary operates each line), Sakhatransneftegaz JSC
(Yakutia; owned by the Republic of Sakha), Alrosa-Gas JSC (Alrosa), Rosneft PJSC (P1824 — check
whether Gazprom now operates it), Sakhalin Energy LLC (P1783 — Gazprom Sakhalin Holding 50%+1,
Mitsui 12.5%, Mitsubishi 10%, the ex-Shell 27.5% — state the post-2022 structure with a date),
Sibneft-Chukotka LLC (Gazprom Neft), KOGAS + Gazprom (P1440), Gazprom + JPDO (P0828), Globaltec
LLC (P3896), CNPC (P3895 Chinese side). Owner/operator work stages onto the `Gas_OperatorsOwners`
tab; a disputed CURRENT owner is an `attribution` concern with `contested` naming `Owner1` /
`Owner2%` / `Operator`.

THE SOURCE LADDER (in this order):
1. **The operator's own record** — `gazprom.ru` / `gazprom.com` project pages and press releases
   (`Сила Сибири`, `Сахалин – Хабаровск – Владивосток`, `Дальневосточный маршрут`), Gazprom's
   annual and sustainability reports and IFRS notes (PDFs), Gazprom Transgaz Tomsk's site,
   Sakhatransneftegaz (`aostng.ru`), Alrosa (`alrosa.ru`), Sakhalin Energy (`sakhalinenergy.ru`),
   Rosneft, Gazprom Neft. **The gazprom.ru zone does not answer from here — read every Gazprom
   page through its Wayback capture** (MEASURED CONDITIONS), cite the LIVE URL as the ref with
   the capture URL alongside in `proposed_refs`, and record the capture you read in the
   verification `note`.
2. **State approvals and programmes** — Glavgosexpertiza (`gge.ru`, per-project approvals naming
   length, diameter, pressure), Minenergo, the FAS tariff orders (`fas.gov.ru`; blocked from here,
   Wayback / `consultant.ru` / `garant.ru` / `docs.cntd.ru` mirrors), the regional gasification
   programmes and government sites (`sakha.gov.ru`, `khabkrai.ru`, `primorsky.ru`, `amurobl.ru`,
   `kamgov.ru`, `sakhalin.gov.ru` — most blocked from here; Wayback), `dfo.gov.ru` (the Far East
   presidential envoy's office).
3. **Corporate disclosure** — `e-disclosure.ru` (annual reports of Sakhatransneftegaz, Alrosa),
   Gazprom investor presentations, RusHydro (Novolenskaya TPP).
4. **Russian trade and regional press** — `neftegaz.ru` (51 existing refs here), Interfax /
   interfax-russia.ru, TASS, Kommersant, Vedomosti, RBC, RIA, `1prime.ru`, `oilcapital.ru`,
   `energypolicy.ru`, `peretok.ru`, `eastrussia.ru`, `ysia.ru` and `ulus.media` (Yakutia),
   `vestiprim.ru` (Primorye), `dvnovosti.ru` (Khabarovsk), `sakh.online` (Sakhalin), `nedradv.ru`
   and `sibneft.org` (existing refs — grade each on what it actually states).
5. **International** — Reuters, Bloomberg, Interfax.com, Upstream, OGJ, S&P/Argus, IEA, OIES
   (Oxford Institute for Energy Studies papers on Power of Siberia 1/2 and the Far Eastern route
   are the best English secondary source), Chinese sources for the China legs.

INDEPENDENCE, precisely. A Gazprom press release and the Gazprom annual report = ONE origin. A
Transgaz subsidiary page and gazprom.ru = ONE origin. Interfax quoting Gazprom's release = the
same origin (say so). Gazprom vs a Glavgosexpertiza approval = TWO. Gazprom vs the Yakutia
government = TWO. A regional-press piece quoting the operator's press service is the operator's
origin unless it adds its own reporting. Anything citing GEM is disqualified. Sanctions-era
thinning: when the newest primary source is 2021–2023, cite it, state the date, grade `medium` —
never `UNRESOLVED` for a value a dated primary source states.

EXISTENCE / DUPLICATE FLAGS — the bar is high. (a) Name the document you tested and what it does
and does not contain. (b) A regional feeder's absence from gazprom.ru is expected; look at the
regional operator and the regional government. (c) Read maps and schemes, not just text. (d)
Segment-vs-system: an aggregate restated on a string row is a `spec` defect, but the string
exists. (e) A proposed project "exists" if it was genuinely proposed: a memorandum, a
feasibility study, a government programme entry, an announcement with a sponsor.

RULES THAT BITE:
- Never cite GEM. abarrelfull, theodora and yingdodo are BANNED (url_verifier rejects them).
- Never fabricate a URL. Every URL goes through `scripts/url_verifier.py --name`. For a Cyrillic
  page pass the Cyrillic name (`--name "Сила Сибири"`) and a Cyrillic expected token.
- A blocked fetch is not a deletion; only a confirmed 404/410 retires a ref. Add Wayback captures.
- `energybase.ru` serves a 200 geo-block page to some clients — the verifier detects the block
  family; if it flags one, read the Wayback capture and add it ALONGSIDE, never swap.
- Cite the ARTICLE or the DOCUMENT, never a navigation surface (site root, search results, a
  tag page, an interactive map).
- SegmentCost: REFS_ADDED only when a primary source states THAT figure for THAT scope, in the
  sheet's currency (`SegmentCostUnits` here is `USD`, `RUB` or `EUR` per row — a RUB figure on a
  USD row is a `spec` concern with the conversion noted, not a silent swap).
- Pressure: a Gazprom/Transgaz/Glavgosexpertiza page states the working pressure for many lines;
  look, don't force.
- Never fill a `[ref]` without a paired value.
- Never propose a route edit; never write any live sheet.

TIMEOUTS. Put a hard timeout on every fetch (`curl --max-time 30`, the verifier's own timeout);
never let one slow host stall the row — the gazprom.ru zone hangs to the connect timeout, so
go to Wayback FIRST for any `*.gazprom.ru` / `gazprom.com` / `*.gov.ru` URL. **Write your shard
EARLY** (after the first few units) and update it as you go, so an interrupted run leaves
partial work on disk.

MEASURED CONDITIONS (2026-09-14, from this machine's US IP):
- CONNECT-TIMEOUT (no answer from a US IP; go to Wayback FIRST, cite live + capture): www.gazprom.ru,
  www.gazprom.com, ir.gazprom.ru, tomsk-tr.gazprom.ru, khabarovsk-tr.gazprom.ru, chukotka.gazprom.ru,
  krasnodar-dobycha.gazprom.ru, gazprominvest.ru, gazprom-invest.ru, www.gazprom-neft.ru,
  sakhalin-2.ru, alrosagas.ru, sakhatransneftegaz.ru (dead brand domain — the company's live site is
  www.aostng.ru, 200), rosneft.ru (rosneft.com 200), fas.gov.ru, dfo.gov.ru, sakha.gov.ru, khabkrai.ru,
  amurobl.ru, primorsky.ru, sakhalin.gov.ru, peretok.ru, docs.cntd.ru, rusgasmarket.ru, rostender.info.
- 403 / 401 / 5xx (blocked, NOT dead — browser UA, then Wayback): gge.ru 403, kamgov.ru 403,
  minvr.gov.ru 403, e-disclosure.ru 403 on deep links, spglobal 403, tass.ru 403 on some article
  URLs (tass.com 200), vedomosti.ru 502, rbc.ru 401, rg.ru 401, reuters.com 401, cnpc.com.cn 412.
- 200 (read directly): interfax.ru, interfax-russia.ru, interfax.com, tass.ru (most), tass.com,
  neftegaz.ru, kommersant.ru, energybase.ru (verifier OK), alrosa.ru, sakhalinenergy.ru,
  www.aostng.ru, minenergo.gov.ru, web.archive.org, ria.ru, ysia.ru, eastrussia.ru, novatek.ru,
  oilcapital.ru, 1prime.ru, ogj.com, iea.org, oxfordenergy.org, vestiprim.ru, dvnovosti.ru,
  sudact.ru, nedradv.ru, ipng.ysn.ru, ulus.media, energypolicy.ru, sibneft.org, gsprom.ru,
  legalacts.ru, 1sn.ru, sps38.ru, upstreamonline.com, forbes.ru, giprogazcentr.com, rosneft.com,
  consultant.ru, garant.ru, erdc.ru, themoscowtimes.com, bloomberg.com, argusmedia.com;
  sakh.online answers slowly (302 chain) — set the timeout and wait once.
- Wayback captures verified for the Gazprom Power of Siberia pages:
  http://web.archive.org/web/20250603074909/https://www.gazprom.ru/projects/power-of-siberia/ (verifier
  OK, contains "Сила Сибири") and https://web.archive.org/web/20250518173643/https://www.gazprom.com/projects/power-of-siberia/;
  rosneft.ru has a 2026-09-13 capture. No captures were found for sakhatransneftegaz.ru, fas.gov.ru
  or gge.ru root — check per-page with the CDX API (`http://web.archive.org/cdx/search/cdx?url=<url>&limit=5&fl=timestamp,statuscode`),
  one call per URL, never a fan-out; the availability API rate-limits after a handful of calls
  (a 429 or empty body is the rate limit, retry later in the run, not a missing capture).

THE HARVESTED CITATION POOL (`wiki_citations.json`) IS A WORKLIST, NOT A LOOKUP TABLE. Report in
researcher_notes how many of your row's harvested citations you opened, and which you could not
read.

VALUE CONVENTIONS: `*CostUnits` = bare currency code (`USD` / `RUB` / `EUR`). Controlled vocab
lowercase except `FIDStatus` (`Pre-FID` / `FID`); `ShelvedCancelledType` = `inferred` /
`confirmed`. Capacity, length and diameter in the sheet's units for your row (km / mm / bcm/y
unless the row says otherwise). Federal-subject names in their English canonical form (above).
A GulfPub recon ran standalone for Russia (`batches/russia-gas/staging/recon-gulfpub-20260914/`);
it is NOT an input to your row and GulfPub is never a `[ref]`.
