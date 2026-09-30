export const meta = {
  name: 'critical-deep-sweep',
  description: 'Critical re-audit of an in-scope pipeline set: confirm each data point against independent sources and flag phantom / duplicate / misclassified / mis-attributed entries (existence+classification first). One skeptical subagent per pipeline; read-and-stage only, never auto-applies.',
  phases: [
    { title: 'Audit', detail: 'one subagent per pipeline (or per family group) — existence+classification, then attribution+spec' },
  ],
}

// args (from `python scripts/build_deepsweep_args.py --staging <dir>`):
//   { repo, staging, commodity, country, pids:[...], roster:[...], status_review?: true,
//     groups?: [[pid,...],...], lean?: true, model?, extra_brief? }
// groups: one agent per GROUP instead of per PID — sibling segments / strings / hub branches
// that share their documents (docs/sops/lean_pass.md). Every PID must appear in exactly one
// group; a singleton group is the classic one-agent-per-row contract, word for word.
// lean: the worklist was cut by scripts/lean_worklist.py — the agent works the owed set only,
// and the deferred units are recorded, not skipped.
// status_review: true = annual-update mode — each subagent ALSO stages a per-segment-row
// status verdict (confirm / change / stale / unclear) as `status_reviews` in its shard.
// tolerate a JSON-encoded string (some invocation paths stringify `args`)
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/russia-gas/staging/deepsweep-r4a-urals-yanao", "commodity": "gas", "country": "Russia", "pids": ["P0734", "P0737", "P0738", "P0755", "P2287", "P2348", "P2355", "P2358", "P2440", "P2450", "P2459", "P3493", "P3500", "P3506", "P3507", "P3607", "P4145", "P4146", "P4147", "P4148", "P4311", "P5402", "P5403", "P5404", "P5414", "P5612", "P5621", "P6540", "P7546", "P7547"], "roster": ["P0734 | Power of Siberia 2 Gas Pipeline | Novy Urengoy->Kyakhta | len=2700.0 dia=1420.00 cap=50.00 | status=proposed | updated=2025-08-14", "P0737 | Bovanenkovo-Ukhta Gas Pipeline | Bovanenkovskoye Oil and Gas Field->Komi Republic | len=1200.0 dia=1420.00 cap=57.50 | status=operating | updated=2025-08-05", "P0738 | Bovanenkovo-Ukhta Gas Pipeline | Bovanenkovskoye Oil and Gas Field->Komi Republic | len=1200.0 dia=1420.00 cap=57.50 | status=operating | updated=2025-08-05", "P0755 | Northern Tyumen Regions (SRTO)–Torzhok Gas Pipeline | Urengoy Gas Field->Tver Oblast | len=2200.0 dia=1420 cap=28.50 | status=operating | updated=2025-08-08", "P2287 | Bovanenkovo-Ukhta Gas Pipeline | Bovanenkovskoye Oil and Gas Field->Komi Republic | len=1158.6 dia=1420.00 cap=69.20 | status=construction | updated=2025-08-05", "P2348 | Nadym-Punga Gas Pipeline | Nadym->Khanty-Mansi Autonomous Okrug | len=696.0 dia=1220 cap=14.00 | status=operating | updated=2025-08-08", "P2355 | SRTO-Surgut-Omsk Gas Pipeline | Noyabrsk->Omsk Oblast | len=763.0 dia=1400, 1220 cap=32.80 | status=operating | updated=2025-08-20", "P2358 | Novoportovskoye Oil and Gas Condensate Field-Yamburg Gas Pipeline | Novoportovskoye Oil and Gas Condensate Field->Yamalo-Nenets Autonomus Okrug | len=115.5 dia=1020.00 cap=20.00 | status=operating | updated=2023-08-21", "P2440 | Urengoy-Chelyabinsk Gas Pipeline | Urengoy->Chelyabinsk Oblast | len=1780.0 dia=1420 cap=58.00 | status=operating | updated=2023-08-17", "P2450 | Yamburg-Tula Gas Pipeline | Yamburg->Tula Oblast | len=2946.0 dia=1020, 1420 cap=? | status=operating | updated=2023-07-27", "P2459 | Zapolyarnoye-Novy Urengoy Gas Pipeline | Tazovsky District->Yamalo-Nenets Oblast | len=190.0 dia=1420 cap=100.00 | status=operating | updated=2023-07-26", "P3493 | Urengoy-Petrovsk Gas Pipeline | Urengoy->Saratov Oblast | len=2733.0 dia=1420.00 cap=32.00 | status=operating | updated=2023-07-27", "P3500 | Yamburg-Yelets Gas Pipeline | Yamburg gas field->Lipetsk Oblast | len=3146.0 dia=1420.00 cap=? | status=operating | updated=2023-08-10", "P3506 | Yamburg-Volga Region Gas Pipeline | Yamburg gas field->Saratov Oblast | len=2755.0 dia=1420.00 cap=89.00 | status=operating | updated=2023-08-22", "P3507 | Urengoy-Center Gas Pipeline | Urengoy->Tambov Oblast | len=3211.0 dia=1420.00 cap=89.00 | status=operating | updated=2023-08-09", "P3607 | Kharasaveyskoye–Bovanenkovskoye Gas Pipeline | Kharasaveyskoye Gas Field->Yamalo-Nenets Autonomus Okrug | len=106.0 dia=1400 cap=32.00 | status=construction | updated=2025-08-14", "P4145 | Nadym-Punga Gas Pipeline | Nadym->Khanty-Mansi Autonomous Okrug | len=605.0 dia=1220 cap=14.00 | status=operating | updated=2025-08-08", "P4146 | Nadym-Punga Gas Pipeline | Nadym->Khanty-Mansi Autonomous Okrug | len=566.0 dia=1420 cap=30.00 | status=operating | updated=2025-08-08", "P4147 | Nadym-Punga Gas Pipeline | Nadym->Khanty-Mansi Autonomous Okrug | len=595.0 dia=1420 cap=30.00 | status=operating | updated=2025-08-08", "P4148 | Nadym-Punga Gas Pipeline | Nadym->Khanty-Mansi Autonomous Okrug | len=571.0 dia=1420 cap=30.00 | status=operating | updated=2025-08-08", "P4311 | Yamburg-Tula Gas Pipeline | Yamburg->Tula Oblast | len=3113.0 dia=1020, 1420.00 cap=? | status=operating | updated=2023-07-27", "P5402 | Bovanenkovo-Ukhta Gas Pipeline | Bovanenkovskoye Oil and Gas Field->Komi Republic | len=1158.6 dia=? cap=60.00 | status=proposed | updated=2025-08-05", "P5403 | Bovanenkovo-Ukhta Gas Pipeline | Bovanenkovskoye Oil and Gas Field->Komi Republic | len=1158.6 dia=? cap=60.00 | status=proposed | updated=2025-08-05", "P5404 | Bovanenkovo-Ukhta Gas Pipeline | Bovanenkovskoye Oil and Gas Field->Komi Republic | len=1158.6 dia=? cap=60.00 | status=construction | updated=2025-08-05", "P5414 | Komsomolsk-Surgut-Chelyabinsk Gas Pipeline | Gubkinsky->Chelyabinsk Oblast | len=1780.0 dia=1420 cap=? | status=operating | updated=2023-08-17", "P5612 | Urengoy-Center Gas Pipeline | Urengoy->Tambov Oblast | len=3035.0 dia=1400.00 cap=89.00 | status=operating | updated=2023-08-09", "P5621 | Yamburg-Yelets Gas Pipeline | Yamburg gas field->Lipetsk Oblast | len=3146.0 dia=1420.00 cap=? | status=operating | updated=2023-08-10", "P6540 | Tambeyskoye-Bovanenkovo Gas Pipeline | Tambeyskoye Oil and Gas Field->Yamalo-Nenets Autonomus Okrug | len=82.0 dia=1420 cap=105.12 | status=proposed | updated=2025-08-21", "P7546 | Medvezhye-Nadym Gas Pipeline | Medvezhye Gas Field->Yamalo-Nenets Autonomus Okrug | len=118.0 dia=1420 cap=28.00 | status=operating | updated=2025-08-08", "P7547 | Medvezhye-Nadym Gas Pipeline | Medvezhye Gas Field->Yamalo-Nenets Autonomus Okrug | len=115.0 dia=1420 cap=? | status=operating | updated=2025-08-08"], "status_review": true, "lean": true, "model": "sonnet", "extra_brief": "SCOPE: RUSSIA gas, batch R4a of 8 — URALS FEDERAL DISTRICT, YAMALO-NENETS (YaNAO) ORIGINS,\n**LEAN PASS** (the LEAN PASS section of your contract is binding). 30 rows / 183 owed units: 23\n`operating` (the Soviet-era Urengoy / Yamburg / Medvezhye export corridors plus Bovanenkovo–Ukhta 1–2\nand SRTO–Torzhok), 3 `construction` (P2287 Bovanenkovo–Ukhta 3, P5404 Bovanenkovo–Ukhta 6, P3607\nKharasavey–Bovanenkovo), 4 `proposed` (P0734 Power of Siberia 2, P5402/P5403 Bovanenkovo–Ukhta 4/5,\nP6540 Tambey–Bovanenkovo). 15 rows were last touched July–August 2023. Status review is on for every\nrow. Background: `docs/country_notes/russia.md` (do not re-read other batches).\n\nCALIBRATION — TWO POPULATIONS.\n(1) **12 rows carry NO `[ref]` on any researched column** — P2358, P2440, P2450, P2459, P3493,\nP3500, P3506, P3507, P4311, P5414, P5612, P5621 (8–12 owed units each: Status, Fuel, PipelineType,\nStart, Length, Diameter, Location, Owner, often FuelSource / Capacity / Operator). Rule 4(e) end to\nend: the value is on the sheet, find the document that states it, stage `REFS_ADDED` with the SAME\nvalue (a source within rounding IS a ref, discrepancy noted; `UNRESOLVED` only when nothing was\nfound, with what you searched).\n(2) **The other rows are cited**; you owe only the refs the script could not clear (49 `HAS_REF`\nunits, named under TRAPS) plus stray uncited cells. 82 cited units whose links merely time out\n(`*.gazprom.ru`) are DEFERRED — do not re-research them. Blank cells (146: Pressure, Proposal,\nSegmentCost, Construction, Operator) are DEFERRED — stage one only if a page you already opened\nstates it. P7546/P7547 have no owed ref units: they still get a status review + validity record.\nHarvested pool: 422 citations over 28 gem.wiki pages — richer than any earlier batch; open yours\nfirst, then go to the operator.\n\nWHERE THE VALUES LIVE. One document class answers six columns at once for an operating trunk: the\n**Gazprom Transgaz subsidiary's own site** — `about/history`, `about/today`, and a page per ЛПУМГ\nlisting the trunks it operates with diameter, length in its zone and commissioning year. ALL\n`*.gazprom.ru` hosts connect-time-out from here: Wayback FIRST, cite live + capture.\n- **Transgaz Yugorsk** `yugorsk-tr.gazprom.ru` (formerly Тюментрансгаз) — THE operator for this\n  batch: Nadym–Punga I–V, Medvezhye–Nadym, and the YaNAO/KhMAO head sections of Urengoy–Petrovsk,\n  Urengoy–Center I/II, Yamburg–Yelets I/II, Yamburg–Tula I/II, Yamburg–Volga Region, SRTO–Torzhok,\n  Urengoy–Uzhgorod. Its Надымское / Пангодинское / Ныдинское / Ямбургское / Пуровское / Ново-Уренгойское\n  ЛПУМГ pages list the corridors by name. Corporate paper «Транспорт газа».\n- **Transgaz Surgut** `surgut-tr.gazprom.ru` — Urengoy–Chelyabinsk (P2440), Komsomolskoye–Surgut–\n  Chelyabinsk (P5414), SRTO–Surgut–Omsk (P2355), Zapolyarnoye–Urengoy (P2459). Its VK longread\n  `vk.com/@gazpromtransgazsurgut-nash-uzhnyi-forpost` is cited on P2355 (vk.com serves a JS shell to\n  curl — try `m.vk.com`, Wayback, or the same text on the subsidiary site / «Сибирский газовик»).\n- **Transgaz Ukhta** `ukhta-tr.gazprom.ru` — Bovanenkovo–Ukhta (all six rows), SRTO–Torzhok's Komi\n  section. **Gazprom Dobycha Nadym** `nadymdobycha.gazprom.ru` — Bovanenkovo, Kharasavey (P3607),\n  Medvezhye. **Gazprom Dobycha Tambey** `gazdobtambey.ru` (200 — P6540). **Gazprom Neft / Gazpromneft-\n  Yamal** `gazprom-neft.ru` (times out — Wayback) for P2358 Novy Port–Yamburg («Газ Ямала», commissioned\n  2021/22). **gsprom.ru**, **gazprom invest** `invest.gazprom.ru` for construction rows.\n- Downstream ends (Tula, Yelets, Petrovsk, Saratov, Torzhok, Chelyabinsk, Omsk) belong to Transgaz\n  Moscow / Saratov / Nizhny Novgorod / Yekaterinburg / Tomsk — cite them only for the far terminus.\nSecond-source classes INDEPENDENT of the operator: federal planning scheme `Распоряжение\nПравительства РФ от 06.05.2015 N 816-р` + 2024 amendment 3302-р (sudact.ru / legalacts.ru /\nconsultant.ru — cite by number + date; a planned figure is `medium`, vintage stated); FAS tariff\norders; Glavgosexpertiza approvals; YaNAO / KhMAO government and territorial-planning documents;\nthe 1990s–2000s industry histories already cited here (Вяхирев, `gazanaliz.ru/books/Vyahirev/6.pdf`\non Wayback; `aup.ru/books/m5/6_1.htm`); ru.wikipedia articles (`Уренгой — Помары — Ужгород`,\n`Ямбург — Елец`, `Бованенково — Ухта`… ONE secondary source — cite its footnoted primary where it has\none); trade press with own reporting (neftegaz.ru, interfax.ru, tass.ru, 1prime.ru, kommersant.ru,\nvedomosti.ru; regional: sever-press.ru, ks-yanao.ru, yamal-media.ru, ugra-news.ru, muksun.fm).\nINDEPENDENCE: Transgaz page + Gazprom PJSC report = ONE origin. Transgaz + federal decree / FAS\norder / regional government / trade press with its own reporting = TWO. Two outlets running one\npress-service text = ONE. energybase.ru restating the operator is not independent.\n\nSEARCH IN RUSSIAN. Use `OtherLanguagePrimaryPipelineName` verbatim as `--name` where filled. For the\nblanks: P2358 `газопровод Новопортовское — Ямбург` / `«Газ Ямала»` (через Обскую губу); P3500/P5621\n`Ямбург — Елец` (I / II); P3506 `Ямбург — Поволжье`; P5612 `Уренгой — Центр II`; P6540 `Тамбейское —\nБованенково` / `газопровод подключения Тамбейского месторождения`; P2459 `Заполярное — Уренгой`.\n**The sheet's Cyrillic name on P2450 says «вторая нитка» although the row is string I — copy-paste\nfrom P4311; note it, search `Ямбург — Тула I`.** Vocabulary: `магистральный газопровод`, `нитка`,\n`ЛПУМГ`, `КС` (компрессорная станция), `газопровод подключения`, `введён в эксплуатацию`,\n`протяжённость … км`, `диаметр … мм`, `млрд куб. м в год`, `проектная производительность`.\n\nTRAPS — settle with documents, never by merging or blanking:\n- **P2440 Urengoy–Chelyabinsk vs P5414 Komsomolskoye–Surgut–Chelyabinsk**: both carry 1,780 km /\n  1420 mm, start years 1979 / 1978; GEM's note says they form a two-line corridor \"often referred to\n  as two segments of the same pipeline\". Decide from documents: two parallel нитки (two rows correct,\n  each with its OWN length/year/start point — Urengoy vs Komsomolskoye field near Gubkinsky), two\n  consecutive segments, or ONE pipe (file `duplicate`). A length copied across both is a `spec` concern.\n- **P5404 Bovanenkovo–Ukhta \"Pipeline 6\" is `construction` while Pipelines 4 and 5 are `proposed`**\n  — implausible ordering. 816-р/3302-р list нитки III–VI as planned; Gazprom has publicly built only\n  I (2012), II (2017) and started III. Find what, if anything, is under construction and which нитка\n  it is. P2287 (III): StartYear1 2024 is past on a `construction` row — find the current target\n  (tenders gsprom.ru, Gazprom investment programme 2025/26) and stage Start + Delay. Its `Capacity\n  69.20` is cited to the consultant.ru 816-р page + energybase — re-read: is 69.2 the per-string\n  figure or a system increment? P5402/P5403/P5404 each carry 60 bcm/y and 1158.6 km — per-string or\n  copied system numbers? P0737/P0738 `SegmentCost 20,000,000,000` each, cited to neftegaz 694037 —\n  value not found by the script; re-read for a prose form and whether it is the WHOLE project's cost\n  restated on both strings (`spec`).\n- **Nadym–Punga I–V (P2348, P4145–P4148)**: Start / Capacity / Length cited to `aup.ru/books/m5/6_1.htm`\n  (names the line; times out today — Wayback) and the Vyakhirev PDF on Wayback (name not matched —\n  Cyrillic PDF; read it). Confirm each string's OWN year (1972/74/75/77/81), diameter (1220 for I–II,\n  1420 for III–V) and capacity (14 / 14 / 30 / 30 / 30 — system figure or per string?). P4147/P4148\n  `Status [ref]`: nadymdobycha 2022 news (timeout) + an `oktregion.ru` tariff PDF — re-read, and find\n  a post-2023-08 item. P4148 Diameter cited only to energybase (geo-block page) — add an operator\n  source alongside. The audit marks P4145–P4148 geometry OK_REVERSED (digitized end→start): NOT a\n  mismatch. P2348 geometry is OK_INTERIOR — describe its first/last points; if it stops short of\n  Nadym or Punga, contest `RouteAccuracy` with what is missing.\n- **P6540 Tambey–Bovanenkovo**: eight units cite ONE `gazdobtambey.ru` public-hearings PDF that now\n  answers **404** (confirmed dead → it may retire, but find its replacement first: the host is up —\n  look for the moved ОВОС / проектная документация under `/ecology/`, and Wayback). Start 2028 and\n  Length 82 cite a rostender.info tender page (200, values not found — re-read; a tender listing is\n  weak, pair it). `Capacity 105.12` bcm/y on an 82-km DN1420 connection line is physically\n  implausible for one string — check whether it is a multi-string system total or a unit slip\n  (млн м³/сут?). File `spec` with the documents. The GulfPub recon mapped 76 reference features onto\n  this row — irrelevant to you, do not chase.\n- **P0734 Power of Siberia 2** (`proposed`, Start 2030, `Delayed = yes`): the legally binding\n  memorandum was signed 2025-09-02 (Gazprom–CNPC; price unsettled). Status review must use post-that\n  evidence: `confirm` proposed unless a source shows FID / construction start. Refs flagged: 816-р\n  annex (name not found — the decree may list it as `«Сила Сибири-2»`, «Алтай» or «Западный маршрут»\n  — read it), kommersant 6745001 (Construction 2024?? on a proposed row — a value/status\n  contradiction: settle it), dp.ru FT item (Delay), neftegaz 660602 (Length 2700 / Diameter /\n  SegmentCost 9.05 bn — not found by script; is 2,700 km the Russian section only? the row has no\n  EndLocation and end state `Kyakhta` — owed `Location [ref]` fix: end state → `Republic of\n  Buryatia`), kommersant 4771199 (FuelSource), eprussia + e-disclosure (Owner; e-disclosure 403 is an\n  access failure). Duplicate suspect P5409 Soyuz Vostok is the MONGOLIAN section and is carried by\n  another scope — name it in `cross_row_leads`, do not research it.\n- **P2459 Zapolyarnoye–Novy Urengoy**: GEM note — \"5 lines, capacity for the total 5, length for the\n  route\". One row stands for a five-string system (100 bcm/y, 190 km). File `spec`/`classification`\n  saying how documents count the strings and their years (2001–2004…); EndLocation blank; end state\n  `Yamalo-Nenets Oblast` is a typo.\n- **P2355 SRTO–Surgut–Omsk**: nearly every cell leans on the Transgaz Surgut VK longread + a\n  `tomsk-tr.gazprom.ru` page (timeout) + gasforum.ru + an nbra.ru attachment. Re-read; add one\n  non-VK source per unit if a page you open states it. StartLocation `Noyabrsk` vs the name's СРТО\n  origin — settle in validity.\n- **P3607 Kharasavey–Bovanenkovo** (`construction`, Start 2024 — past): GEM notes ask \"gathering\n  pipeline?\". It is a `газопровод подключения` (field-to-trunk connection). Status: Kharasavey\n  launch has slipped repeatedly — find the current date, stage Start + Delay. Capacity 32 cited to\n  816-р (name not found — read the annex).\n- **P3507 Urengoy–Center I**: GEM note says the route was drawn from the field to the site of a July\n  2021 accident — i.e. the geometry is NOT the 3,211-km line. Contest `RouteAccuracy` (\"route\n  candidate for §8\") with sourced termini; never propose coordinates. `Pervomaiskii` end: verify.\n- **P2358**: all 12 units uncited, EndLocation blank, Owner Gazprom Neft. P0755 Diameter cited only\n  to energybase. P0738 Start 2017 cited to invest.gazprom.ru (timeout) + gsprom.ru project page\n  (200, value not found — re-read).\n- **String pairs** (P3507/P5612, P3500/P5621, P2450/P4311, P7546/P7547): two rows are CORRECT if\n  documents describe two нитки with their own years. P3500/P5621 both carry 3,146 km; P3507/P5612\n  both 89 bcm/y; P3506 89 bcm/y too — a multi-line corridor total restated per row is a `spec`\n  concern naming every PID. Trunk capacity of one DN1420 7.5 MPa string is ~26–33 bcm/y: anything far\n  above is a system number.\nAGGREGATE-VS-SEGMENT: a system figure is never a ref for a string row — flag it, cite the system\ndocument as such, say which rows share it.\n\nSTATUS REVIEW — one record per row, all 30. For an operating trunk `confirm` needs a source DATED\nLATER THAN 2023-08 naming the line (operator page/news, a repair or diagnostics item, tariff order,\naccident report) — say which and its date. Absence of news about a 1980s trunk is not evidence; do\nnot `stale` an operating row. Export context: Ukraine transit ended 2025-01-01, so the Urengoy /\nYamburg corridors run at reduced load — reduced flow is NOT `idle`/`mothballed` without a document\nsaying a named line was taken out of service; if one does, that is a `change`. In-development rows:\nbuilt → `change` with date; a dated newer target → stage it; no progress evidence since the last\ntarget → `stale` with `shelved`, `ShelvedCancelledType = inferred`, no URL for the inference. A\nchanged Status goes in BOTH `status_reviews[].proposed_changes` and the Status fill.\n\nSTATE CELLS: `Yamalo-Nenets Autonomus Okrug` (typo) sits on 20 rows' Start/EndState — stage the\ncorrection to `Yamalo-Nenets Autonomous Okrug` as a `Location [ref]` fill (`value_cols` naming the\ncell) ONLY where you already hold a source placing that terminus; P2459 end `Yamalo-Nenets Oblast`\nand P0734 end `Kyakhta` → `Republic of Buryatia` likewise. Tyumen Oblast legally contains KhMAO and\nYaNAO — `Tyumen region` vs an okrug is vocabulary, not a mismatch.\n\nVALIDITY TEXT goes in `researcher_notes` + `recommendation` (never a bare `notes` key); use\n`contested: {\"<Column>\": \"<candidate value>\"}` only for a pasteable candidate.\n\nOWNERSHIP: `Owner [ref]` is owed on 19 rows and `Operator [ref]` on 8 (both live on the\n`Gas_OperatorsOwners` tab). One Transgaz page stating the trunks are ПАО «Газпром» property operated\nby the subsidiary, or the Gazprom annual report, settles a family — cite it on each row. P7546/P7547\nOwner is `--`: stage Gazprom PJSC as a free fill if the page you read says so. P2358 Gazprom Neft\n(ank72.ru 404 — find a replacement; market.neftegaz 468 is access failure); P6540 Gazprom Dobycha\nTambey (a Gazprom / RusGazDobycha JV — verify the 100% claim).\n\nUNITS: metric — km, mm, bcm/y (`млн куб. м в сутки` × 0.365), MPa. Multi-value `1020, 1420` is the\nsheet's convention for a line with two sizes. `*CostUnits` = bare currency code, magnitude in the\nnumber. Vocabulary lowercase; only `FIDStatus` is capitalized.\n\nRULES THAT BITE (the contract has the rest): no GEM cites; abarrelfull / theodora / yingdodo are\nbanned; every URL through `scripts/url_verifier.py --name \"<Cyrillic name>\"`; only a confirmed\n404/410 retires a ref — a `*.gazprom.ru` timeout, an `energybase.ru` geo-block page, a 401/403/468 is\nan ACCESS FAILURE: read the Wayback capture and add it ALONGSIDE, never swap; a category / search /\nmap-home / tender-index page is not a citation; openstreetmap.org is not a `[ref]`; an inferred\nstatus change has no URL. TIMEOUTS: `curl --max-time 30` on every fetch; Wayback FIRST for any host\nin the timeout list; a legal mirror first for any federal act. Wayback via the CDX API, one call per\nURL (`http://web.archive.org/cdx/search/cdx?url=<url>&limit=5&fl=timestamp,statuscode`); a 429 or\nempty body is the rate limit — retry later in the run, it is not a missing capture.\n\nMEASURED CONDITIONS (2026-09-21, this machine, US IP, 12 s budget):\n- TIMEOUT (Wayback first, cite live + capture): every `*.gazprom.ru` (yugorsk-tr, surgut-tr,\n  ukhta-tr, tomsk-tr, nadymdobycha, invest), gazprom-neft.ru, aup.ru, yanao.ru, government.ru,\n  pravo.gov.ru, docs.cntd.ru.\n- ACCESS FAILURE codes: kommersant.ru 500 and vedomosti.ru 502 on the home page (article deep links\n  verified 200 by the script — try them, else Wayback); admhmao.ru 447; e-disclosure.ru deep links\n  403; market.neftegaz.ru 468; rg.ru / rbc.ru 401.\n- 200: gazdobtambey.ru, gsprom.ru, sudact.ru, legalacts.ru, consultant.ru, neftegaz.ru, interfax.ru,\n  tass.ru, 1prime.ru, gasforum.ru, rostender.info, sever-press.ru, ks-yanao.ru, ru.wikipedia.org,\n  web.archive.org. energybase.ru answers 200 with its geo-block page. vk.com serves a JS shell.\n  dzen.ru is reposts — cite the original.\n", "groups": [["P0737", "P0738", "P2287"], ["P5402", "P5403", "P5404"], ["P2348", "P4145", "P4146"], ["P4147", "P4148", "P7546", "P7547"], ["P3607", "P6540", "P2358"], ["P3507", "P5612", "P3493"], ["P3500", "P5621", "P3506"], ["P2450", "P4311"], ["P2440", "P5414", "P2355"], ["P0755", "P2459"], ["P0734"]]}
if (!Array.isArray(A.pids) || !A.pids.length) {
  throw new Error("critical-deep-sweep needs args.pids — run scripts/build_deepsweep_args.py and pass its JSON as `args`.")
}
// Model is chosen by the orchestrator at dispatch time (standing rule: cheapest model
// genuinely good enough for this run) and passed via args.model; 'sonnet' is only the
// fallback when no choice is passed, not a pin.
const MODEL = A.model || 'sonnet'
const REPO = A.repo
const STAGING = A.staging
const COMMODITY = A.commodity || 'gas'
const COUNTRY = A.country || ''
const PIDS = A.pids
const GROUPS = Array.isArray(A.groups) && A.groups.length ? A.groups : PIDS.map(p => [p])
{
  const seen = GROUPS.flat()
  const missing = PIDS.filter(p => !seen.includes(p))
  const dup = seen.filter((p, i) => seen.indexOf(p) !== i)
  if (missing.length || dup.length || seen.length !== PIDS.length) {
    throw new Error(`args.groups must cover every pid exactly once (missing: ${missing.join(',')}; duplicated: ${dup.join(',')})`)
  }
}
const LEAN = !!A.lean
const ROSTER = (A.roster || []).join("\n")
const STATUS_REVIEW = !!A.status_review
// optional scope-specific guidance (e.g. China: research in Chinese, geo-blocked-site
// workarounds) appended verbatim to every subagent contract.
// INLINE IT. `args.extra_brief_path` (hand the agent the run dir's BRIEF.md and tell it to
// read the file first) was tried on Russia R2, 2026-09-15, to keep ~30KB out of the
// orchestrator's context: 8 of 8 agents skipped the file completely — zero reads — and went
// straight to Step 0. An agent reliably runs the Step 0 COMMANDS it is given and reliably
// reads text already in its prompt; it does not reliably go fetch a document it was told to
// read. The brief carries the scope's source ladder, language rules and blocked hosts, so a
// skip is silent research damage. The path form is kept only as a fallback, never the default.
const EXTRA = A.extra_brief
  ? `\n\n## Scope-specific guidance (from the orchestrator)\n${A.extra_brief}`
  : (A.extra_brief_path
     ? `\n\n## Scope-specific guidance (from the orchestrator) — READ THE FILE FIRST\n` +
       `\`${A.extra_brief_path}\` is part of this contract, not background reading. Read it IN FULL\n` +
       `before Step 0 — it carries the scope's source ladder, language rules, known-blocked hosts and\n` +
       `per-country gotchas, and research done without it will be wrong in ways the gates do catch.`
     : '')

const statusInstr = STATUS_REVIEW ? `

## STATUS REVIEW (annual-update mode — REQUIRED, one object per segment row)
This is an in-development row being checked for the annual update. Beyond the audit above,
determine the pipeline's CURRENT true status. Hunt for dated evidence NEWER than the sheet's
(the roster line shows updated=LastUpdated). A status change is a claim like any other:
>=2 independent sources, every URL through url_verifier. Verdict vocabulary:
- "confirm" — the recorded Status is still right; say what confirms it, with the evidence date.
- "change"  — evidence-based status change. Set proposed_status and proposed_changes as
  {column: value} pairs — Status (controlled vocab, lowercase) plus the matching date columns
  (e.g. now operating -> StartYear1; construction began -> ConstructionYear; newly shelved ->
  ShelvedYear). A change without a verified ref will be downgraded at merge — source it.
- "stale"   — NO independent news found. Apply the dormancy rules: proposed with no progress
  >=2y -> shelved; shelved >=4y -> cancelled. proposed_changes MUST include
  ShelvedCancelledType="inferred" (lowercase — that is the live column's vocabulary, NOT
  "Presumed") and the inference gets NO fabricated ref (standing rule 2);
  set staleness_rule to "2y->shelved" or "4y->cancelled". If dormant but under the threshold,
  use "confirm" and note the last-evidence date.
- "unclear" — genuinely cannot tell; explain what you tried in researcher_notes.
evidence_date = date of the MOST RECENT independent evidence found (YYYY-MM where possible).
Add to the shard: "status_reviews": [
  { "segment_name": "<or empty>", "sheet_row": <int from worklist>,
    "current_status": "<from the sheet>", "verdict": "confirm|change|stale|unclear",
    "proposed_status": "<or empty>", "proposed_changes": {"Status": "...", "...": "..."},
    "evidence_date": "YYYY-MM", "staleness_rule": "" ,
    "proposed_refs": ["https://...verified..."],
    "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
    "tier": "high|medium|low", "independent": true, "source_language": "en",
    "researcher_notes": "<what you searched, the newest dated evidence, your reasoning>" }
]` : ''

const leanInstr = LEAN ? `

## LEAN PASS (token-budgeted — read this before starting)
The worklist was cut to the OWED set (scripts/lean_worklist.py): uncited values (MISSING_REF),
cited values whose link is dead / missing the value / not about this pipeline, and — if listed —
a few blank-value columns. Blank values and cited values whose links already check out were
DEFERRED into deferred_units.json on purpose; they are not your job this pass. So:
- Work ONLY the units \`shard_upsert.py --remaining\` lists, plus the status review and ONE
  validity record per row. Do not go hunting for blank values. If a document you are already
  reading states a blank value, you MAY stage it as a FILL (it is free) — never search for one.
- Second source: ONE targeted search per data point (a different publisher and document class).
  If it does not land, stage at medium with a note saying what you searched, and move on.
- Validity: judge existence / duplicate / classification from the documents you already opened
  and the roster. Open a dedicated search only when the row's own sources fail to name the
  pipeline, or the scope guidance names this row as a duplicate/existence candidate.
- Stop when coverage prints OK and the status + validity records are saved. Do not widen scope.` : ''

const contract = (group) => group.length === 1 ? contractFor(group[0], '') : contractFor('<PID>', `
## FAMILY GROUP — you own ${group.length} rows: ${group.join(', ')}
These rows share their documents (sibling segments, strings of one corridor, or branches of one
hub). Research the SHARED documents ONCE, then report per row. Everything below is written for
one ProjectID: read every <PID> as EACH of ${group.join(', ')} in turn — each row gets its own shard
(its own Step 0 --init/--remaining), its own fills, its own status review and validity record, and
its own check_shard_coverage OK. A page that states a figure for one string is not a ref for its
sibling unless it states that sibling's figure too. Save as you go; if you run low on context,
finish the row you are on and return — a replacement agent resumes from --remaining.
Do not finish until check_shard_coverage prints OK for EVERY row in the group.
`)

const contractFor = (pid, familyHeader) => `You are a meticulous, skeptical GEM pipeline researcher. Critically RE-AUDIT ${pid === '<PID>' ? 'a family of' : 'one'} ${COUNTRY}
${COMMODITY} pipeline${pid === '<PID>' ? 's' : ''}: ${familyHeader ? 'ProjectIDs ' + familyHeader.match(/rows: (.*)/)[1] : 'ProjectID ' + pid}.${familyHeader} This is a deep-sweep validity pass — your job is to CONFIRM the
existing data and EXPOSE anything wrong, not to rubber-stamp it. Baird expects some of this data to
be wrong, some pipelines to not exist, and some to be duplicates or misclassified. Find those.

cd ${REPO} first.

## Inputs (read them — ALWAYS START FROM THE SOURCES THE SHEET ALREADY CITES)
- Your pipeline's current GEM values + existing refs: \`${STAGING}/worklist.json\` → load it and
  filter \`units\` to \`project_id == "${pid}"\`. Each unit has ref_col, value_cols, values,
  primary_value, current_ref, sheet_row, segment_name, pipeline_name, wiki.
- Source leads harvested from this row's gem.wiki page: \`${STAGING}/wiki_citations.json\`
  (your STARTING POINT — engage what the sheet itself cites BEFORE open-web search; verify each
  live, since many rot; READ gem.wiki for leads but NEVER cite it). A row whose only support is a
  generic/aggregate citation that does not actually name this pipeline is itself an existence flag.
- Roster of ALL ${PIDS.length} in-scope pipelines (for duplicate/relabel detection — does ${pid} look
  like the same physical pipe as another row under a different name?):
${ROSTER}

## Step 0 — open your shard BEFORE any research (save-as-you-go is mandatory)
Run, in this order:
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --init
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --remaining
\`--init\` creates \`${STAGING}/rows/${pid}.json\` from the worklist (idempotent; it never touches an
existing shard's records). \`--remaining\` lists every worklist unit the shard does not yet report on.
If some units are ALREADY reported, a previous agent ran out of context on this row: keep its
records, do NOT redo them, and research ONLY the OWED units it lists (re-open a saved record only
if \`--remaining\` flags it as FIX, or if your own research on a later unit contradicts it).

FROM HERE ON, EVERY RECORD IS SAVED THE MOMENT IT IS FINISHED — never batched to the end:
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --fill '<one fills[] JSON object>'
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --validity @/tmp/${pid}_v.json
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --status-review @/tmp/${pid}_s.json
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --lead '<one cross_row_leads[] object>'
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --summary "<one line>"
(\`--fill\` etc. take inline JSON, \`@file\`, or \`-\` for stdin, and accept a single object or a list.)
A record is FINISHED when it is sourced (refs verified, values filled) or honestly UNRESOLVED with
researcher_notes saying what you searched. Never save a placeholder to "reserve" a unit — an
UNRESOLVED you meant to come back to reads downstream as "searched, found nothing". Upserting the
same unit again REPLACES the earlier record (keyed on ref_col + sheet_row), so finding a source
after an UNRESOLVED is one more --fill, not an edit. NEVER write the shard file yourself with a
heredoc, Write, or json.dump — that overwrites everything saved so far; the helper is the only
writer. Each call prints "N/M owed units reported": that is your progress meter. The point: if
you hit your context limit on unit 12 of 15, units 1-11 are on disk and your replacement does
only 12-15.

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, or A Barrel Full /
   abarrelfull.wikidot.com / any wikidot.com page. Read for leads only. url_verifier rejects them.
2. NEVER fabricate a URL. If you cannot verify, say so in researcher_notes — no invented links.
3. Run EVERY url through the verifier before you cite it, WITH THE PIPELINE NAME:
   \`python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"] --name "<pipeline name>"\`
   (or \`verify_url(url, any_of=surface_forms(value), name=<pipeline_name>)\`) → cite only if it
   prints OK/200 AND contains the expected token(s) AND names the pipeline. Use distinctive tokens
   (numbers, place names). Every verification object you write carries "name_found": true|false.
   RELEVANCE: a page about terminus A, or about terminus B, or about the parent trunk, is NOT a ref
   for the "A-B" segment row unless it names that segment (its FULL name, or its local-language
   name from the worklist's OtherLanguage* columns). If the name is in another script and the
   verifier misses it, read the page and encode the hand-confirmed match as name_found=true with
   the matched string in "note". A ref whose page never names the pipeline is capped at low at
   merge and listed by the pre-delivery gates -- do not stage it as if it were support.
4. Corroborate with >=2 INDEPENDENT sources (separate origins; not one wire story reprinted, not two
   pages both tracing to GEM). tier: high = >=2 independent working+value-present; medium = 1 strong;
   low = 1 weak/partial/conflicting. TWO REFS PER DATA POINT IS THE TARGET FOR EVERY UNIT: after the
   first source lands, the second search is owed -- a different publisher and a different document
   class (regulator approval / operator disclosure / press / EIA or acceptance notice). A single-
   source unit is fillable at medium, but its researcher_notes must say what you searched for the
   second source and why none was found. Search in the country's languages too where English is thin.
5. Read every document you open TO EXHAUSTION, for every column and every sibling row. A source
   found for one cell is a source for every fact on its page: if the approval notice you found for
   Status also states length, diameter, investment, construction start and commissioning date, stage
   it onto Length / Diameter / SegmentCost / Construction / Start [ref] too (REFS_ADDED where the
   value is on the sheet, a fill where the cell is blank). Then check the roster: a page about the
   trunk names its branches, and a page about segment I states segment II's numbers -- write those
   into your researcher_notes naming the other PID, so the orchestrator can route them (findings do
   not propagate across a fan-out by themselves). Limit: a SYSTEM figure is never a ref for a
   SEGMENT cell (aggregate-vs-segment rule) -- note it and file a validity concern instead.

## What to do, IN THIS PRIORITY ORDER (existence + classification FIRST)
1. EXISTENCE — Is this pipeline real? Find independent evidence it physically exists/is being built.
   If the ONLY traces are GEM-derived, or the sheet's cited source does not actually name this
   pipeline, or you cannot find independent confirmation, flag verdict="concern",
   concern_type="existence" (possible hallucination / GEM-only entity).
2. CLASSIFICATION — Is it correctly classified as recorded (right commodity; a transmission trunk vs
   a gathering/process/feeder line)? Wrong → concern_type="classification".
3. DUPLICATE — Compare against the roster. If ${pid} is very likely the same physical pipe as another
   ProjectID (relabel / segment double-count), flag concern_type="duplicate" and NAME the other PID.
4. ATTRIBUTION — owner/operator, FuelSource, province, endpoints. Wrong → concern_type="attribution".
5. SPEC — length, diameter, capacity, dates. CRITICALLY confirm each against >=2 independent sources.
   It is NOT enough that a page mentions the pipeline — the source must AGREE with the GEM number.
   Material disagreement → concern_type="spec", verdict="concern" (never silently pass it).
   AGREEMENT IS ALSO AN OUTPUT, NOT A NO-OP: when the source agrees, that source is the ref the
   cell was missing — emit it as a fills[] REFS_ADDED record per rule 6. Confirming a value and
   reporting it nowhere machine-readable is the same as never checking it.
6. EVERY WORKLIST UNIT IS OWED A RECORD — UNCITED VALUES AND BLANKS ALIKE. Filter worklist.json to
   ${pid} and COUNT your units. You owe exactly ONE fills[] object per unit, whatever its class.
   Both classes are owed, and the first one is the one this leg exists for:
   - class == "MISSING_REF" — the sheet HAS a value (Length 52 mi, Capacity 700 MMcf/d, endpoints,
     dates, owner …) and its [ref] cell is EMPTY. An uncited value is an unsupported value, and
     supporting it is the CORE PRODUCT of this sweep. When your sources agree with the recorded
     value, that agreement IS the deliverable: emit the unit carrying the SAME values it already
     has, the verified ref(s) that state them, and class_out="REFS_ADDED". Writing "length and
     diameter confirmed as recorded" in your summary and nowhere else is INDISTINGUISHABLE FROM
     NOT DOING THE WORK — it is the single most common defect in this leg's history (381 units
     across four US gas batches, every one of them on a row whose documents the agent had already
     opened). When your sources DISAGREE, emit the corrected value AND file the spec concern in
     validity[]. When you genuinely find nothing, class_out="UNRESOLVED" with researcher_notes
     saying what you searched.
   - class == "MISSING_VALUE" — the cell is BLANK and the sheet owes a value (Length, Capacity,
     Diameter, StartYear, ConstructionYear, SegmentCost, Pressure, FuelSource, Operator, Owner …):
     a sourced value with a paired verified ref when you find one, otherwise class_out="UNRESOLVED"
     with researcher_notes saying what you searched. Never force a number (a weak Capacity stays
     blank rather than fabricated).
   Uncited values and blank cells on OPERATING rows come first -- they are what the researchers
   notice. A unit with NO object is a defect the pre-delivery gates list; an UNRESOLVED with EMPTY
   researcher_notes is a silent skip the gates list too. Never skip a unit silently.
7. A SOURCE THAT AGREES WITHIN ROUNDING IS A REF, NOT A NON-ANSWER. If a page names the pipeline and
   states essentially the recorded value — 51.97 mi + 0.5 mi against a recorded 52 mi, 38.5 against
   39, $10.7M against $11M — that is REFS_ADDED at medium/high tier with the small discrepancy
   stated in researcher_notes (and a validity spec concern if it is material). UNRESOLVED means you
   found NOTHING; it never means you found something slightly different. The limit stays the
   aggregate-vs-segment rule: a SYSTEM figure is never a ref for a SEGMENT cell.${statusInstr}${leanInstr}${EXTRA}

A pipeline that is real and correctly classified but has a lesser caveat → verdict="confirmed (caveat)".
Only open existence/duplicate/classification doubt → verdict="concern".

## Output — the shard (built by your upserts), then a summary
Your upserts produce \`${STAGING}/rows/${pid}.json\` = a single JSON object EXACTLY shaped like
(each --fill / --validity / --status-review / --lead call supplies ONE element of the matching list):
{
  "project_id": "${pid}",
  "pipeline_name": "<from worklist>",
  "sheet_row": <int from worklist>,
  "wiki": "<gem.wiki url from worklist>",
  "validity": [
    { "segment_name": "<or empty>", "verdict": "confirmed (caveat)|concern",
      "concern_type": "existence|duplicate|classification|attribution|spec|none",
      "recommendation": "<short human next step, e.g. 'reclassify as NGL' / 'merge into P####' / 'verify endpoint'>",
      "contested": {"<backend column the finding disputes>": "<candidate value, or \"\" if the evidence only says the current value is wrong>"},
      "researcher_notes": "<the full finding — what you checked, what the sheet's own sources say, what independent sources say vs GEM, your reasoning>",
      "proposed_refs": ["https://...verified..."], "tier": "high|medium|low",
      "independent": true, "source_language": "en" }
  ],
  "fills": [
    { "segment_name": "<or empty>", "sheet_row": <int>, "ref_col": "Capacity [ref]",
      "value_cols": ["Capacity"], "primary_value_col": "Capacity", "values": {"Capacity": "<val>"},
      "primary_value": "<val>", "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true,"name_found":true,
                          "note":"<the phrase on the page that states the value and names the line>"}],
      "class_out": "REFS_ADDED|UNRESOLVED", "tier": "high|medium|low", "independent": true,
      "source_language": "en", "researcher_notes": "<why this value / source; what you searched for a 2nd source>" }
  ],
  "cross_row_leads": [
    { "project_id": "<other PID from the roster>", "url": "https://...verified...",
      "facts": "<what the page states about THAT row, e.g. '825 km, 3.1 bn RMB, construction Oct 2008'>" }
  ],
  "summary": "<one line>"
}
Emit at least one validity object per pipeline (use verdict="confirmed (caveat)", concern_type="none"
if you found nothing wrong, summarizing what you confirmed). ON EVERY verdict="concern", fill
\`contested\` — it is the ONLY thing that puts your finding on the paste surface. A validity record
proposes no edit, so it is filtered off the _Backend mirror; \`contested\` is what tints the disputed
CURRENT value orange there with your finding attached. Omit it and a researcher pastes straight over
the cell you flagged. Name the EXACT backend column ("LengthKnownUnits", not "units"), give the
candidate value where your evidence names one, and "" where it only establishes the current value is
wrong. A concern about the row as a whole (existence/duplicate) may leave it {}.${STATUS_REVIEW ? ' In annual-update mode also emit\nat least one status_reviews object per segment row (shaped as specified above).' : ''} validity[].proposed_refs and all
fills[].proposed_refs must have passed url_verifier (with --name). One fills[] object per
WORKLIST UNIT in your slice -- MISSING_REF and MISSING_VALUE alike, sourced or honestly UNRESOLVED.
A unit with no object is a defect the pre-delivery gates list. Before finishing, run
\`python scripts/check_shard_coverage.py --staging ${STAGING} --pid ${pid}\`
and DO NOT FINISH UNTIL IT PRINTS OK -- it parses your shard and names every worklist unit you left
without a record. If it lists units, go back and report on them (a sourced record, or UNRESOLVED
with what you searched); do not delete the unit or hand back a shard it still rejects. Set the
one-line \`--summary\` last. Return ONLY a 2-line summary: the verdict/concern_types you staged, and any UNRESOLVED. Your shard
file is the deliverable, not your message.`

phase('Audit')
log(`Critically auditing ${PIDS.length} ${COUNTRY} ${COMMODITY} pipelines in ${GROUPS.length} agent(s)${LEAN ? ' (lean pass)' : ''} (existence+classification first).`)
const results = await parallel(GROUPS.map(group => () =>
  agent(contract(group), { label: `audit:${group.join('+')}`, phase: 'Audit', agentType: 'general-purpose', model: MODEL })
))
const done = results.filter(Boolean).length
log(`Audit complete: ${done}/${GROUPS.length} agents returned (${PIDS.length} pipelines). Shards in ${STAGING}/rows/ — run check_shard_coverage --all.`)
return { agents_returned: done, agents: GROUPS.length, pipelines: PIDS.length }
