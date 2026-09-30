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
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/russia-gas/staging/deepsweep-r4b-urals-south", "commodity": "gas", "country": "Russia", "pids": ["P1446", "P2297", "P2315", "P2320", "P2336", "P2337", "P2350", "P2351", "P2357", "P2378", "P2429", "P3975", "P3976", "P3977", "P3978", "P3979", "P5537", "P5538", "P5686", "P5712", "P5717", "P5745", "P8087"], "roster": ["P1446 | Chelyabinsk-Petrovsk Gas Pipeline | Chelyabinsk->Samara | len=1285.0 dia=1420 cap=37.12 | status=operating | updated=2023-08-14", "P2297 | Dolgoderevenskoye-Sysert Gas Pipeline | Dolgoderevenskoye->Sverdlovsk Oblast | len=127.0 dia=1020 cap=? | status=operating | updated=2023-08-17", "P2315 | Igrim-Serov-Nizhny Tagil Gas Pipeline | Igrim->Sverdlovsk Oblast | len=525.0 dia=1000, 1020, 1200 cap=10.00 | status=operating | updated=2023-08-17", "P2320 | Kartaly-Magnitogorsk Gas Pipeline | ?->Chelyabinsk Oblast | len=150.0 dia=720, 1020 cap=4.80 | status=operating | updated=2023-08-18", "P2336 | Magnitogorsk-Ishimbay Gas Pipeline | Magnitogorsk->Republic of Bashkortostan | len=209.0 dia=530 cap=? | status=operating | updated=2023-08-18", "P2337 | Magnitogorsk-Sterlitamak Gas Pipeline | Magnitogorsk->Republic of Bashkortostan | len=? dia=820 cap=? | status=operating | updated=2023-08-21", "P2350 | Nizhnevartovsk-Parabel-Kuzbass Gas Pipeline | Nizhnevartovsk->Kemerovo region | len=1162.0 dia=1020, 1420 cap=4.10 | status=operating | updated=2025-08-18", "P2351 | Nizhnyaya Tura-Perm-Gorky Gas Pipeline | Nizhnyaya Tura->Perm Krai | len=? dia=1220 cap=? | status=operating | updated=2023-08-18", "P2357 | SRTO-Ural Gas Pipeline | Beryozovsky District->Sverdlovsk Oblast | len=1986.0 dia=1220 cap=16.20 | status=operating | updated=2025-08-20", "P2378 | Punga-Vuktyl-Ukhta Gas Pipeline | Svetlyi->Komi Republic | len=291.0 dia=1420 cap=14.00 | status=operating | updated=2025-08-07", "P2429 | Sverdlovsk-Nizhny Tagil Gas Pipeline | Yekaterinburg->Sverdlovsk Oblast | len=145.0 dia=1020 cap=? | status=operating | updated=2023-08-21", "P3975 | Mishkino-Yurgamysh-Kurgan Gas Pipeline | Mishkino->Kurgan Oblast | len=84.0 dia=400 cap=? | status=operating | updated=2023-08-22", "P3976 | Mishkino-Yurgamysh-Kurgan Gas Pipeline | Yurgamysh->Kurgan Oblast | len=54.0 dia=325 cap=? | status=operating | updated=2023-07-21", "P3977 | Shumikha-Almenevo Gas Pipeline | Shumikha->Kurgan Oblast | len=38.93 dia=200 cap=? | status=proposed | updated=2023-07-24", "P3978 | Vargashi-Lebyazhye Gas Pipeline | Vargashi->Kurgan Oblast | len=48.7 dia=? cap=? | status=proposed | updated=2023-07-25", "P3979 | Lebyazhye-Makushino Gas Pipeline | Lebyazhye->Kurgan Oblast | len=? dia=? cap=0.19 | status=proposed | updated=2023-07-24", "P5537 | Punga-Vuktyl-Ukhta Gas Pipeline | Svetlyi->Komi Republic | len=349.0 dia=1420 cap=29.20 | status=operating | updated=2025-08-07", "P5538 | Punga-Ukhta-Gryazovets Gas Pipeline | Svetlyi->Komi Republic | len=? dia=1420 cap=29.50 | status=operating | updated=2025-08-07", "P5686 | Urengoy-Chelyabinsk Gas Pipeline | Dolgoderevenskoye->Chelyabinsk Oblast | len=63.0 dia=1020 cap=? | status=operating | updated=2023-08-17", "P5712 | Nizhnyaya Tura-Perm-Gorky Gas Pipeline | Nizhnyaya Tura->Perm Krai | len=? dia=1220 cap=? | status=operating | updated=2023-08-18", "P5717 | Kartaly-Magnitogorsk Gas Pipeline | ?->Chelyabinsk Oblast | len=150.0 dia=720, 1020 cap=4.80 | status=operating | updated=2023-08-18", "P5745 | SRTO-Ural Gas Pipeline | Beryozovsky District->Sverdlovsk Oblast | len=1986.0 dia=1420 cap=? | status=operating | updated=2025-08-20", "P8087 | Ishim-Astana Gas Pipeline | Ishim area->? | len=658.0 dia=1000 cap=10.00 | status=proposed | updated=2026-08-28"], "status_review": true, "lean": true, "model": "sonnet", "extra_brief": "SCOPE: RUSSIA gas, batch R4b of 8 — URALS FEDERAL DISTRICT SOUTH (Chelyabinsk, Sverdlovsk, Kurgan,\nthe Ural trunks from KhMAO, the Punga–Ukhta corridor, the Bashkortostan and Perm branches), **LEAN\nPASS** (the LEAN PASS section of your contract is binding). 23 rows / 156 owed units: 19 `operating`\n(Soviet-era trunks and branches, 1959–1983, plus the 2016/2022 Kurgan отводы) and 4 `proposed`\n(P3977 Shumikha–Almenevo, P3978 Vargashi–Lebyazhye, P3979 Lebyazhye–Makushino, P8087 Ishim–Astana).\nMost rows were last touched July–August 2023 (researcher NF/ZK). Status review is on for every row.\nBackground: `docs/country_notes/russia.md` (do not re-read other batches).\n\nCALIBRATION — TWO POPULATIONS.\n(1) **16 rows carry NO `[ref]` on any researched column**: P1446, P2297, P2315, P2320, P2336, P2337,\nP2351, P2429, P3975, P3976, P3977, P3978, P3979, P5686, P5712, P5717 (7–10 owed units each: Status,\nFuel, PipelineType, Start, Length, Diameter, Location, Capacity, Proposal, Owner). Rule 4(e) end to\nend: the value is on the sheet, find the document that states it, stage `REFS_ADDED` with the SAME\nvalue. A source within rounding IS a ref (note the discrepancy). Use `UNRESOLVED` only when nothing was\nfound, and say what you searched.\n(2) **The other 7 are cited** (P2350, P2357, P2378, P5537, P5538, P5745, P8087). You owe only the 17\n`HAS_REF` units the script could not clear (named under TRAPS) plus one or two stray uncited cells.\n32 cited units whose links merely time out are DEFERRED. Do not re-research them. The 143 blank cells\n(Pressure, SegmentCost, Construction, Proposal, FuelSource, Operator, Capacity, Length) are DEFERRED.\nStage one only if a page you already opened states it (free fill).\nHarvested pool: 115 citations over 22 gem.wiki pages. Open yours first, then go to the operator.\n\nWHERE THE VALUES LIVE. For an operating trunk, one document class answers six columns at once: the\n**Gazprom Transgaz subsidiary's own site**: `about/history`, `about/today`, and one page per ЛПУМГ\nlisting the trunks it runs with diameter, length in its zone and commissioning year, plus the\nsubsidiary's corporate newspaper and anniversary books (PDF). ALL `*.gazprom.ru` hosts connect-time-out\nfrom here, so go to Wayback FIRST and cite live + capture.\n- **Transgaz Yekaterinburg** `ekaterinburg-tr.gazprom.ru` is THE operator for this batch:\n  Chelyabinsk–Petrovsk head section (P1446), Dolgoderevenskoye–Sysert (P2297), Kartaly–Magnitogorsk\n  I/II (P2320/P5717), Sverdlovsk–Nizhny Tagil (P2429), the Dolgoderevenskoye–Krasnogorsk looping\n  (P5686), SRTO–Ural's southern section (P2357/P5745), Igrim–Serov–Nizhny Tagil's Sverdlovsk end\n  (P2315), and ALL the Kurgan отводы (P3975–P3979). Its Челябинское / Долгодеревенское / Карталинское /\n  Шадринское / Курганское / Серовское / Нижнетуринское ЛПУМГ pages. Newspaper «Газовый курьер».\n- **Transgaz Yugorsk** `yugorsk-tr.gazprom.ru` (formerly Тюментрансгаз): Punga–Vuktyl–Ukhta I/II\n  (P2378/P5537) and Punga–Ukhta–Gryazovets III (P5538) at the Punga end; Igrim–Serov (P2315) at the\n  Igrim end (Игримское / Пунгинское / Уральское ЛПУМГ); SRTO–Ural at the KhMAO end.\n- **Transgaz Ukhta** `ukhta-tr.gazprom.ru`: the Komi half of P2378/P5537/P5538 (Вуктыльское ЛПУМГ,\n  newspaper «Северный газовик» / «Севергазпром»). The Punga–Vuktyl–Ukhta corridor is «Сияние\n  Севера» (Northern Lights).\n- **Transgaz Ufa** `ufa-tr.gazprom.ru`: Magnitogorsk–Ishimbay (P2336) and the Kartaly–Magnitogorsk–\n  Sterlitamak line (P2337). GEM's own note cites the Transgaz Ufa anniversary book\n  `https://ufa-tr.gazprom.ru/d/textpage/95/149/book_pages.pdf` p.58 (Wayback): read it for BOTH rows.\n- **Transgaz Tchaikovsky** `tchaikovsky-tr.gazprom.ru` (formerly Пермтрансгаз): Nizhnyaya Tura–Perm I/II\n  (P2351/P5712). **Transgaz Tomsk** `tomsk-tr.gazprom.ru`: Nizhnevartovsk–Parabel–Kuzbass (P2350).\n- Far termini belong to Transgaz Samara / Saratov / Nizhny Novgorod. Cite them only for that end.\nSecond-source classes INDEPENDENT of the operator: the federal planning scheme `Распоряжение\nПравительства РФ от 06.05.2015 N 816-р` + 2024 amendment 3302-р (sudact.ru / legalacts.ru /\nconsultant.ru; cite by number + date; a planned figure is `medium`, vintage stated); FAS tariff orders;\nGlavgosexpertiza approvals; **regional gasification programmes** (`программа развития газоснабжения и\nгазификации Курганской / Челябинской / Свердловской области на 2021–2025`, published on the regional\ngovernment / legal portals); regional government press services (kurganobl.ru, pravmin74.ru,\nmidural.ru); the industry histories (Вяхирев on Wayback; `aup.ru/books/m5/6_1.htm`); ru.wikipedia\n(ONE secondary source; cite its footnoted primary where it has one); trade press with its own\nreporting (neftegaz.ru, interfax.ru / interfax-russia.ru, tass.ru, kommersant.ru; regional:\noblgazeta.ru, 74.ru, znak.com, ura.news, nashgorod.ru, kurganobl press, bashinform.ru).\nINDEPENDENCE: a Transgaz page + a Gazprom PJSC report = ONE origin. Transgaz + federal decree / FAS\norder / regional programme / trade press with its own reporting = TWO. Two outlets running one\npress-service text = ONE. energybase.ru restating the operator is not independent.\n**gazprommap.ru** (Gazprom's gasification map; GEM's RouteNotes source for all five Kurgan rows) is\nGazprom-side: usable as ONE source, never the second source for a Gazprom page. R3 flagged rows sourced\nonly to gazprommap. Pair it with the regional programme or Glavgosexpertiza.\n\nSEARCH IN RUSSIAN. Use `OtherLanguagePrimaryPipelineName` verbatim as `--name` where it is filled.\nFor the blanks: P2336 `Магнитогорск — Ишимбай` / `Шкапово — Ишимбай — Магнитогорск`; P2429\n`Свердловск — Нижний Тагил` / `Екатеринбург — Нижний Тагил`; P5686 `лупинг Долгодеревенское —\nКрасногорский` (on `Уренгой — Челябинск`); P5717 `Карталы — Магнитогорск` (нитка II); P3975\n`Мишкино — Юргамыш — Курган`; P3978 `газопровод-отвод Варгаши — Лебяжье`. Old place names: Свердловск =\nЕкатеринбург, Горький = Нижний Новгород. СРТО = Северные районы Тюменской области. Vocabulary:\n`магистральный газопровод`, `газопровод-отвод`, `межпоселковый`, `нитка`, `лупинг`, `ЛПУМГ`, `КС`,\n`ГРС`, `введён в эксплуатацию`, `протяжённость … км`, `диаметр … мм`, `млрд куб. м в год`.\n\nTRAPS: settle each with documents, never by merging or blanking.\n- **Copied string pairs.** P2320/P5717 Kartaly–Magnitogorsk I/II carry identical 150 km / `720, 1020` /\n  4.80 bcm/y. P2357/P5745 SRTO–Ural I/II both carry 1986 km. Two rows are CORRECT if documents describe\n  two нитки with their own years (P2320 1963 vs P5717 1966; P2357 1974 vs P5745 1983). A figure copied\n  across both is a `spec` concern naming both PIDs. **P2320 is string I, but its Cyrillic name reads\n  «2-ая нитка»**, the same copy-paste pattern R4a found on P2450. Note it and search string I.\n- **P2350 Nizhnevartovsk–Parabel–Kuzbass I**: Capacity 4.10 is, per GEM's note, \"total 8.2 bcm/y split\n  evenly between two pipelines\". An even split is not a sourced per-string figure. Re-read the cited\n  `reph.ru/press-center/news/4059/` (200, value not found; look for the prose form or 8.2) and file\n  `spec` if the split is GEM's arithmetic. The sibling string II is NOT in this batch.\n- **P2337 Magnitogorsk–Sterlitamak**: the Cyrillic name is `Карталы—Магнитогорск—Стерлитамак` while\n  the English name drops Kartaly, and LengthKnown is `--`. GEM's note says 571 km is the total for\n  Kartaly–Magnitogorsk–Sterlitamak AND Ishimbay–Ufa (Transgaz Ufa book p.58), a combined figure.\n  Settle what the row IS (does it overlap P2320/P5717's Kartaly–Magnitogorsk section?) and file\n  `classification`/`spec`. **P2336**: GEM's note says it is part of Shkapovo–Ishimbay–Magnitogorsk (401\n  km). Is 209 km the Magnitogorsk–Ishimbay section of that line, and is 530 mm right for it?\n- **Nizhnyaya Tura–Perm I/II (P2351/P5712)**: both carry the WHOLE system's Cyrillic name «Нижняя Тура —\n  Пермь — Горький — Центр» and LengthKnown `--`. P5712's routes-repo geometry ends in Nizhny Novgorod\n  Oblast, which traces the whole Perm–Gorky run, not a Tura–Perm string. Contest `RouteAccuracy` (§8\n  route candidate) with sourced termini; never propose coordinates. P2351's ResearcherNotes read \"no\n  details except diameter\": find the per-string year (1967 / 1975) and diameter (1220).\n- **P1446 Chelyabinsk–Petrovsk** (1285 km, 1420 mm, 37.12 bcm/y, 1980): EndState reads `Samara`, but\n  Petrovsk is in **Saratov Oblast** and the geometry ends there. Stage the EndState correction as a\n  `Location [ref]` fill (`value_cols` naming the cell) with a source placing the terminus. Is 37.12 a\n  per-string figure, or does the corridor count several lines? Is 1285 km the Chelyabinsk–Petrovsk\n  section or the full line? `RouteAccuracy = very low`.\n- **P5686 Dolgoderevenskoye–Krasnogorsk looping** of Urengoy–Chelyabinsk (63 km, 1020 mm, 1977): a\n  лупинг is a parallel loop on a trunk. GEM's note ties it to Bukhara–Ural II. Confirm what it loops\n  and file `classification` if the parent is wrong. `RouteAccuracy = very low`.\n- **Punga corridor (P2378 / P5537 / P5538)**: Start/Diameter are cited to energybase (geo-block\n  page), `aup.ru/books/m5/6_1.htm` (200, names the line) and ukhta-tr PDFs (timeout; use Wayback).\n  P5537 Capacity 29.20 and P5538 Capacity 29.50 are \"value not found\" on aup.ru and on the 816-р\n  sudact page: re-read for the prose form, and file `spec` if 29.x is a corridor figure. P2378 carries\n  14.00: are 14 / 29.2 / 29.5 per string or cumulative corridor steps? **P5537 `Location [ref]` cites an\n  openstreetmap.org way. OSM is not a `[ref]`**: find a document naming the Svetlyi start and stage\n  it, and leave the OSM link for a human to drop. P5538 LengthKnown `--`; its geometry is digitized\n  end→start (OK_REVERSED, not a mismatch). P5539 (string IV, R2) is out of scope: name it in\n  `cross_row_leads` if relevant.\n- **P2357 / P5745 SRTO–Ural**: Length/Capacity/Diameter lean on energybase (geo-block page; read its\n  Wayback capture and add it ALONGSIDE) and `ungg.org/reference.html` (value not found; read it). P5745\n  Status cites `ekaterinburg-tr…/press/news/2024/11/1657/` (timeout, Wayback) and an `adm-serov.ru`\n  scanned PDF (no text layer; access/format failure, not a dead ref). P2357 Diameter 1220 vs P5745 1420:\n  confirm each string's own diameter.\n- **P2315 Igrim–Serov–Nizhny Tagil** (525 km, `1000, 1020, 1200`, 10 bcm/y, 1966): the first Siberian\n  gas to the Urals (Берёзово–Игрим field). A three-size multi-value is the sheet's convention for a\n  line with several diameters. Source each size or flag it.\n- **Kurgan отводы (P3975–P3979)** are all recorded `PipelineType = distribution`, and P3976/P3977/P3979\n  have `Газопровод-отвод … ГРС` Cyrillic names. GEM's own note on P3975 says Russian sources call it a\n  transmission branch. Rule: a `газопровод-отвод` terminating AT a ГРС is transmission (transgaz-\n  operated); `межпоселковый` downstream of the ГРС is distribution. File a `classification` concern\n  row by row. **Flag, never reclassify.** P3975 Mishkino–Yurgamysh–Kurgan (84 km, 400 mm, 2016) and\n  P3976 Yurgamysh–Kurtamysh (54 km, 325 mm, 2022) share one name: parent line plus branch, not a\n  duplicate, unless documents say otherwise. The interfax-russia URL in P3975's ResearcherNotes is a\n  lead. P3979 Capacity 0.19 bcm/y on an отвод: check the units (`тыс. м³/час`?).\n- **Kurgan in-development (P3977 Shumikha–Almenevo, P3978 Vargashi–Lebyazhye, P3979 Lebyazhye–\n  Makushino)**: these are the Gazprom programme for Kurgan Oblast 2021–2025. Find whether each was BUILT\n  (ввод ГРС Альменево / Лебяжье / Макушино; regional press; Gazprom Invest), is under construction, or\n  has slipped. P3978 is recorded 48.70 km with a blank diameter, and P3979's length is blank; those are\n  deferred unless the page states them.\n- **P8087 Ishim–Astana** (`proposed`, 658 km, 1000 mm, 10 bcm/y, Start 2030): the Russian gas supply\n  line to Astana (Kazakh name «Есіл – Астана»; Russian `Ишим — Астана`; QazaqGaz with Gazprom). Start\n  and Capacity cite `interfax.com/newsroom/top-stories/115988`, a **confirmed 404**, which may retire\n  once you find its replacement (the interfax.ru original, Wayback, QazaqGaz, kursiv.media, inform.kz,\n  kapital.kz, gov.kz). Status review: is there a signed agreement, a design contract or an FID after\n  2024? No route geometry: the row's only one (country note). EndState is blank; stage `Akmola\n  Region` / Astana as a `Location [ref]` fill only with a source.\nAGGREGATE-VS-SEGMENT: a system figure is never a ref for a string row. Flag it, cite the system\ndocument as such, and say which rows share it. One DN1420 7.5 MPa string carries ~26–33 bcm/y, DN1220\n~15–20, DN1020 ~8–12, DN720 ~3–5. Anything far above is a system number.\n\nSTATUS REVIEW: one record per row, all 23. For an operating trunk, `confirm` needs a source DATED\nLATER THAN 2023-08 naming the line (operator page/news, a repair or diagnostics item, a tariff order,\nan accident report, a regional gasification report). Say which source and its date. Absence of news\nabout a 1960s trunk is not evidence, so never `stale` an operating row. In-development rows: built →\n`change` with the date; a dated newer target → stage it; no progress evidence since the last target →\n`stale` with `shelved`, `ShelvedCancelledType = inferred`, and no URL for the inference. A changed\nStatus goes in BOTH `status_reviews[].proposed_changes` and the Status fill.\n\nSTATE CELLS: `Chelyabinsk region` / `Tyumen region` / `Kemerovo region` vs `… Oblast`, and `Khanty-Mansi\nAutonomus Okrug` (typo, P2378/P5537/P5538) → `Khanty-Mansi Autonomous Okrug`. Stage the correction as\na `Location [ref]` fill ONLY where you already hold a source placing that terminus. Tyumen Oblast\nlegally contains KhMAO and YaNAO, so `Tyumen region` vs an okrug is vocabulary, not a mismatch.\n\nVALIDITY TEXT goes in `researcher_notes` + `recommendation` (never a bare `notes` key). Use\n`contested: {\"<Column>\": \"<candidate value>\"}` only for a pasteable candidate.\n\nOWNERSHIP: `Owner [ref]` is owed on 19 rows and `Operator [ref]` on 4 (both live on the\n`Gas_OperatorsOwners` tab). One Transgaz page stating the trunks are ПАО «Газпром» property operated\nby the subsidiary, or the Gazprom annual report, settles a family, so cite it on each row. P8087 Owner is\n`--`: stage it only as a free fill.\n\nUNITS: metric: km, mm, bcm/y (`млн куб. м в сутки` × 0.365), MPa. A multi-value `720, 1020` is the\nsheet's convention for a line with two sizes. `*CostUnits` = bare currency code, with the magnitude in\nthe number. Vocabulary is lowercase; only `FIDStatus` is capitalized.\n\nRULES THAT BITE (the contract has the rest): no GEM cites; abarrelfull / theodora / yingdodo are\nbanned; every URL goes through `scripts/url_verifier.py --name \"<Cyrillic name>\"`; only a confirmed\n404/410 retires a ref. A `*.gazprom.ru` timeout, an `energybase.ru` geo-block page, or a 401/403/468 is\nan ACCESS FAILURE: read the Wayback capture and add it ALONGSIDE, never swap. A category / search /\nmap-home / tender-index page is not a citation, openstreetmap.org is not a `[ref]`, and an inferred\nstatus change has no URL. TIMEOUTS: `curl --max-time 30` on every fetch; Wayback FIRST for any host in\nthe timeout list; a legal mirror first for any federal act. Query Wayback via the CDX API, one call per\nURL (`http://web.archive.org/cdx/search/cdx?url=<url>&limit=5&fl=timestamp,statuscode`). A 429 or an\nempty body is the rate limit: retry later in the run. It is not a missing capture.\n\nMEASURED CONDITIONS (2026-09-21/22, this machine, US IP):\n- TIMEOUT (Wayback first, cite live + capture): every `*.gazprom.ru` (ekaterinburg-tr, yugorsk-tr,\n  ukhta-tr, ufa-tr, tchaikovsky-tr, tomsk-tr, invest), aup.ru intermittently, government.ru,\n  pravo.gov.ru, docs.cntd.ru.\n- ACCESS FAILURE codes: kommersant.ru 500 / vedomosti.ru 502 on the home page (try article deep links,\n  else Wayback); e-disclosure.ru 403; market.neftegaz.ru 468; rg.ru / rbc.ru 401.\n- 200: reph.ru (self-signed TLS), oblgazeta.ru, ungg.org, sudact.ru, legalacts.ru, consultant.ru,\n  neftegaz.ru, interfax.ru, tass.ru, gasforum.ru, ru.wikipedia.org, web.archive.org. energybase.ru\n  answers 200 with its geo-block page. vk.com serves a JS shell (try m.vk.com or Wayback). dzen.ru\n  pages are reposts, so cite the original.\n", "groups": [["P2378", "P5537", "P5538"], ["P3975", "P3976"], ["P3977", "P3978", "P3979"], ["P2297", "P5686", "P2429"], ["P2320", "P5717", "P2336", "P2337"], ["P2351", "P5712"], ["P2357", "P5745", "P2315"], ["P1446"], ["P2350", "P8087"]]}
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
