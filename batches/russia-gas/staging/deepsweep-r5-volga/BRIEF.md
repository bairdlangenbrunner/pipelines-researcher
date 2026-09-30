SCOPE: RUSSIA gas, batch R5 of 8 — VOLGA FEDERAL DISTRICT, **LEAN PASS** (the LEAN PASS section
of your contract is binding). 31 rows / 275 owed units: 29 `operating` Gazprom trunks, P2385
Saratov–Moscow `retired`, P2425 Pochinki–Anapa `construction`, P4063 Zorkino–Balakovo `proposed`.
30 of 31 rows were last touched July–August 2023, which is why the status review is on for every
row. Background: `docs/country_notes/russia.md` (do not re-read the R1–R3 batches).

CALIBRATION — THE ONE NUMBER THAT SHAPES THIS BATCH: 272 of the 275 owed units are `MISSING_REF`.
**30 of 31 rows carry NOT ONE `[ref]` on any researched column** — Length, Diameter, StartYear,
Capacity, Fuel, PipelineType, Location, Owner all have VALUES and no citation. Only P2425 has refs
(its 3 owed `HAS_REF` units are named below). So this pass is rule 4(e) almost end to end: the
value is on the sheet, find the document that states it, stage `REFS_ADDED` with the SAME value.
Owed by column: Status 31, Owner 31, Fuel 30, PipelineType 30, Start 30, Location 30, Diameter 27,
Length 24, Construction 12, Capacity 11, FuelSource 10, SegmentCost 3, Delay 2, Proposal 2,
Operator 1, Pressure 1. Blank cells (185, mostly Pressure / Proposal / Operator / SegmentCost)
are DEFERRED — do not search for them; stage one only if a page you already opened states it.
Harvested pool: 120 citations over 31 gem.wiki pages, THIN — 11 rows have ≤2, and `energybase.ru`
(an aggregator; geo-blocks with a 200 page) is 28 of the 120. Open yours, then go to the operator.

WHERE THE VALUES LIVE — one document class answers six columns at once for an operating Volga
trunk: the **Gazprom Transgaz subsidiary's own site**. Each has an `about/history` page and a
page per ЛПУМГ (линейное производственное управление магистральных газопроводов) listing the
trunks it operates with diameter, length in its zone and commissioning year — one read gives
Diameter / Length / Start / Fuel / PipelineType (`магистральный газопровод`) and Owner/Operator.
The subsidiaries, ALL on `*.gazprom.ru`, which connect-times-out from here (Wayback FIRST, cite
live + capture):
- **Transgaz Nizhny Novgorod** `n-novgorod-tr.gazprom.ru` (10 harvested cites) — the Pochinki hub
  (P0756, P2370, P2371, P2372), Gorky lines (P2309, P2310, P2322), Perm–Gorky (P5715, P5716),
  Saratov–Gorky (P2383). Its Починковское ЛПУМГ page is already cited on P2310.
- **Transgaz Kazan** `kazan-tr.gazprom.ru` (5) — Minnibaevo lines (P2340, P5744, P2341), P2322,
  the Zainsk end of P2365.
- **Transgaz Samara** `samara-tr.gazprom.ru` (2) — Ulyanovsk family (P2286, P2430, P5746),
  P2364, P2342.
- **Transgaz Saratov** `saratov-tr.gazprom.ru` — P2383, P2385, P1466, P2342, P4063; its
  корпоративная газета PDF is already cited on P2425.
- **Transgaz Ufa** `ufa-tr.gazprom.ru` (4) — Bashkortostan (P2388, P2390, P2435, P5743, P2375).
  Its book `d/textpage/95/149/book_pages.pdf` (cited on P5743) gives 571 km on p. 58 for
  Kartaly–Magnitogorsk–Sterlitamak + Ishimbay–Ufa TOGETHER — an aggregate, not P5743's length.
- **Transgaz Chaikovsky** `tchaikovsky-tr.gazprom.ru` (NOT `chaikovsky-tr`, which does not
  resolve) — Nizhnyaya Tura–Perm III (P5714), the Perm end of P5715/P5716; **Transgaz
  Yekaterinburg** for P5714's Sverdlovsk start; **Transgaz Moscow** `moskva-tr.gazprom.ru`
  (Елецкое ЛПУМГ, cited on P1466) for the Elets/Moscow ends; **Gazprom Dobycha Orenburg** for
  the Orenburg GPZ hub (P2298, P2364, P2365).
Second-source classes INDEPENDENT of the operator: the federal planning scheme `Распоряжение
Правительства РФ от 06.05.2015 N 816-р` and its 2024 amendment 3302-р (legalacts.ru / sudact.ru /
consultant.ru mirrors — cite by number + date; a 2015 planned figure is `medium` with the vintage
stated), FAS tariff orders (they list trunks by name), Glavgosexpertiza approvals, regional gasification programmes (Saratov 2021–2025 PDF on `saratovoblgaz.com`, cited
on P4063; Mari El decree `3326-р` of 25.11.2021 on P4112), oblast governments and MChS
"характеристика субъекта" pages (58.mchs.gov.ru names the Penza trunks), ru.wikipedia (`Нижняя
Тура — Пермь — Горький — Центр` has an article: ONE secondary source, cite its footnoted primary
where it has one), and the trade press (neftegaz.ru, interfax.ru, 1prime.ru, kommersant.ru;
Tatarstan: business-gazeta.ru, tatar-inform.ru; Bashkortostan: bashinform.ru; Ulyanovsk:
ulpravda.ru; Saratov: vzsar.ru; Perm: 59.ru). `ural-kraeved.ru` and `moluch.ru` name the
lines but grade `low`; pair them.
INDEPENDENCE: Transgaz page + Gazprom PJSC report = ONE origin. Transgaz + a federal decree, a
FAS order, an oblast government or a trade-press item with its own reporting = TWO. Two outlets
running one press-service text = ONE. energybase.ru restating the operator is not independent.

SEARCH IN RUSSIAN. `OtherLanguagePrimaryPipelineName` is filled on 14 rows (use it verbatim as
`--name`). Otherwise: P2340/P5744 `Миннибаево — Казань` (I / II нитка); P2341
`Миннибаево — Ижевск`; P2342 `Мокроус — Самара — Тольятти`; P2365 `Оренбург — Заинск`; P2370
`Починки — Изобильное — Северо-Ставропольское ПХГ`; P2371 `Починки — Пенза`; P2372 `Починки —
Ярославль`; P2385 `Саратов — Москва`; P2388 `Шкапово — Ишимбай`; P2430 `Сызрань — Ульяновск`;
P2435 `Туймазы — Уфа`; P4063 `газопровод-отвод Зоркино — Балаково`; P4112 `газопровод-отвод к ГРС
Кокшамары` (Звениговский район, Марий Эл); P5714 `Нижняя Тура — Пермь` (III нитка); P5715/P5716
`Пермь — Горький` (I / II нитка); P5743 `Ишимбай — Уфа`; P5746 `Новоспасское — Ульяновск`.
Vocabulary: `магистральный газопровод`, `нитка`, `ЛПУМГ`, `ГРС`, `введён в эксплуатацию`,
`протяжённость … км`, `диаметр … мм`, `млрд куб. м в год`. Gorky = Nizhny Novgorod, Kuibyshev =
Samara, Chernikovsk = Ufa.

CLASSIFICATION TEST (flag, never reclassify): `магистральный газопровод` and a `газопровод-отвод`
off it are TRANSMISSION (Transgaz-operated, ends AT a ГРС); `межпоселковый` / `внутрипоселковый`
networks past the ГРС are DISTRIBUTION (Gazprom Gazoraspredeleniye). The two `distribution` rows
— P4063 and P4112 — are both отводы to a ГРС, and GEM's own note on P4063 says the regional
government calls it a transmission branch. Where the documents draw the line that way, file a
`classification` concern with `contested: {"PipelineType": "transmission"}`. GEM notes on P2310
and P2383 record that `n-novgorod-tr.gazprom.ru/about/history/` calls Saratov–Gorky–Cherepovets
"distribution" while every other document says transmission — settle it in the validity record,
and note P2310's 566–582 km tail near Cherepovets went to distribution in 2022 (vologda-poisk.ru).
AGGREGATE-VS-SEGMENT: a system figure is never a ref for a string row. Watch it on:
P2340/P5744 (GEM note: 5.25 bcm/y "is total for the pipeline", copied onto BOTH strings, and both
carry 285 km — file a `spec` concern naming both PIDs unless a source gives per-string figures);
P5714/P5715/P5716 (one Cyrillic name for three rows, no Length on any); P2388 (GEM derived 192 km
by subtracting Magnitogorsk–Ishimbay from a 401-km total — cite the total, say it is derived);
P5743 (571 km aggregate above); P1466 (600 km on a Petrovsk–Elets row whose wiki page is the
Petrovsk–Algasovo–Elets SYSTEM; GEM added a separate looping row — out of scope, name its PID in
`cross_row_leads` if you find it); P2309 (GEM note: "length based on a reconstruction project,
may not be full length; capacity calculated from bcm/d" — find the stated values); P2372
Pochinki–Yaroslavl (36 bcm/y, 1420 mm, NO length, NO start year, route `very low`, and GEM's
note says its map was originally Pochinki–Gryazovets's — test existence as a distinct line
before anything else).

STATUS REVIEW — one record per row, all 31. For an operating trunk `confirm` needs a source
DATED LATER THAN 2023-08 (operator page, annual report, tariff order, a repair / diagnostics news
item naming the line) — say which and its date. Absence of news about a 1960s trunk is not
evidence; do not `stale` an operating row. The three rows carrying a real question:
- **P2385 Saratov–Moscow (`retired`, 1946, 840 km, 325 mm, StopYear BLANK).** The USSR's first
  long-distance trunk. Confirm the retirement with a document (operator history, a
  reconstruction / decommissioning record) and stage `StopYear` as a free fill if a source
  states it. If sources show sections still in service under Transgaz Moscow/Saratov, that is a
  `spec` concern, not a status flip without evidence.
- **P2425 Pochinki–Anapa (`construction`, StartYear1 2023, `Delayed = yes`, `DelayType inferred`,
  LastUpdated 2025-08, AV: "construction is ongoing").** The Южно-Европейский газопровод eastern
  section; 1,625 km, 1,420 mm, 63 bcm/y, 53.12 bn RUB, 9.8 MPa. Its three owed HAS_REF units:
  `Status [ref]` = Telegram `t.me/gspromru/1456` + `archive.org/details/gsprom_tenders_2025-05` +
  `rostender.info/category/…` (a CATEGORY INDEX page — replace it with the tender document);
  `Pressure [ref]` `zaogsp.ru/istoriya/pochinki-anapa` (200, but no 9.8 on the page — re-read;
  the design-approval documents state the class); `SegmentCost [ref]` neftegaz.ru/…/476146 (200,
  53.12 bn not found — re-read for a prose form, else find the figure's source). Also owed:
  `Start [ref]` (2023 is past on a row still `construction` — find the CURRENT target and stage
  it), `Delay [ref]` (the document showing the slipped date against the earlier target),
  `FuelSource [ref]`, `Owner [ref]`. Newest evidence: gsprom.ru tenders 2025, the 2021 project
  approval (proektirovanie.gazprom.ru, neftegaz.ru 672905), rg.ru 2022 "подан газ" on a
  completed section (rg.ru answers 401 — Wayback).
- **P4063 Zorkino–Balakovo (`proposed`, ProposalYear 2021, StartYear1 2022, `Delayed = yes
  inferred`, 36 km).** Was it built? `gazprommap.ru/saratovskaya/`, later editions of the
  Saratov programme and the oblast press say. Built → `change` to `operating` with the date; no
  progress since 2021 → `stale`, `shelved`, `ShelvedCancelledType = inferred`, no fabricated URL.
  Same test on **P4112 Kokshamary** (`operating`, 2022): the cited neftegaz.ru item says the ГРС
  and отвод BEGAN construction in 2022 — find commissioning.
A changed Status goes in BOTH `status_reviews[].proposed_changes` and the Status fill.

STATE CELLS AND ROUTES (state audit `region_audit.csv`, Natural Earth admin-1 names):
1. **Typos owed as `Location [ref]` fills** with `value_cols` naming the cell that moves and a
   source placing the termini: P1466 end `Lipetsk` → `Lipetsk Oblast`; P2341 end `Republic of
   Udmurtia` → `Udmurt Republic`; P2425 start `Nizhgorod Oblast` → `Nizhny Novgorod Oblast`.
2. **P5714 Nizhnyaya Tura–Perm III: START_MISMATCH.** The sheet runs Sverdlovsk Oblast → Perm
   Krai, but the stored geometry runs Perm Krai → Nizhny Novgorod Oblast — i.e. it is the
   Perm–Gorky section, the same corridor P5715/P5716 store. Judge the route first: describe its
   first and last points in plain words; if the geometry is the wrong segment, contest
   `RouteAccuracy` (`high` today) in a validity concern with "route candidate for §8" and the
   sourced termini. Never propose coordinates, never edit a state cell to match a bad route.
   Its I/II siblings (P2351, P5712) are in batch R4b, NOT here — judge the III string on its
   own evidence and name them in `cross_row_leads`.
3. **P2310 Gorky–Cherepovets: OK_INTERIOR** — the geometry starts in Yaroslavl Oblast, not
   Nizhny Novgorod, on a row graded `very high (within meters)`. If the stored line is only the
   northern part of a 582-km trunk, that is a fragment: contest `RouteAccuracy` with a grade and
   say what is missing. P2365 and P2375 are OK_REVERSED (digitized end→start): NOT a mismatch.

DUPLICATES — the audit's candidates, settled with documents, never by merging or blanking:
P5715 vs P5716 (Perm–Gorky I vs II, 0.987) and P2340 vs P5744 (Minnibaevo–Kazan I vs II, 0.973)
are parallel strings — two rows are CORRECT if the documents describe two нитки with their own
commissioning years (1974/1976; 1954/1963 on the sheet). Confirm that, stage each string's OWN
year, flag `duplicate` only if the documents describe ONE pipe. P2286 / P2430 / P5746 (a trunk
and its two branches, per GEM's notes) are three objects.

OWNERSHIP: `Owner = Gazprom PJSC [100.%]` on all 31 rows, uncited on all 31 (`Owner [ref]` goes
on the `Gas_OperatorsOwners` tab). One Transgaz page saying the trunks are `объекты ПАО «Газпром»`
operated by the subsidiary, or the Gazprom annual report, settles a whole family — cite it on
each row. `Operator` is BLANK on 30 rows and deferred, but the subsidiary's name is on the page
you are reading: stage it as a free fill. Mezhregiongaz / Gazoraspredeleniye = downstream, never
the trunk's operator.

UNITS: metric — km, mm, bcm/y (`млн куб. м в сутки` × 0.365), MPa. Multi-value `1020, 1220`
(P2375) is the sheet's convention for a line with two sizes. `*CostUnits` = bare `RUB`,
magnitude in the number (P2430 1,200,000,000). Vocabulary lowercase; only `FIDStatus` is capitalized.

RULES THAT BITE (the contract has the rest): no GEM cites; abarrelfull / theodora / yingdodo
are banned; every URL through `scripts/url_verifier.py --name "<Cyrillic name>"`; only a
confirmed 404/410 retires a ref — a `*.gazprom.ru` timeout, an `energybase.ru` geo-block, an
`rg.ru` 401 or an `e-disclosure.ru` 403 is an ACCESS FAILURE: read the Wayback capture and add it
ALONGSIDE, never swap; a category / search / map-home page is not a citation (P2425's
rostender.info); openstreetmap.org is not a `[ref]`; an inferred status change has no URL at
all. TIMEOUTS: `curl --max-time 30` on every fetch; Wayback FIRST for any host in the timeout
list below, a legal mirror first for any federal act. Wayback lookups via the CDX API, one call
per URL (`http://web.archive.org/cdx/search/cdx?url=<url>&limit=5&fl=timestamp,statuscode`); a
429 or empty body is the rate limit — retry later in the run, it is not a missing capture.

MEASURED CONDITIONS (2026-09-16, this machine, US IP, 15 s connect budget):
- TIMEOUT (Wayback first, cite live + capture): every `*.gazprom.ru` (n-novgorod-tr, kazan-tr,
  ufa-tr, samara-tr, saratov-tr, tchaikovsky-tr, gazprom.ru), government.ru, samregion.ru,
  permkrai.ru, tatarstan.ru, government-nnov.ru, saratov.gov.ru, mari-el.gov.ru, udmurt.ru,
  pravo.gov.ru, publication.pravo.gov.ru, docs.cntd.ru.
- 401 / 403 (access failure, Wayback): rg.ru, rbc.ru (401); orenburg-gov.ru, gge.ru (403);
  e-disclosure.ru home 200 but deep links 403.
- DNS: `chaikovsky-tr.gazprom.ru` does not exist (use `tchaikovsky-tr`); `ulgov.ru` redirects to
  `ulgov.gosuslugi.ru`, which does not resolve (Wayback); `sntat.ru` home answers 404 (article
  deep links may still work — verify each).
- 200: every other host named in this brief, including the legal mirrors, the trade and regional
  press, gazprommap.ru, saratovoblgaz.com, 58.mchs.gov.ru and web.archive.org. energybase.ru
  answers 200 with its geo-block page. dzen.ru is reposts — cite the original.
