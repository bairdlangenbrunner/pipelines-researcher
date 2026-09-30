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
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/russia-gas/staging/deepsweep-r6-siberia", "commodity": "gas", "country": "Russia", "pids": ["P1647", "P2282", "P2283", "P2327", "P2362", "P2376", "P2458", "P2703", "P2705", "P3367", "P3368", "P3369", "P3370", "P3604", "P3980", "P3981", "P3982", "P4056", "P4110", "P5091", "P5510", "P5517", "P5666", "P5667", "P5668", "P6535", "P6674", "P6675", "P6683", "P6684", "P7612", "P7615"], "roster": ["P1647 | Messoyakha-Norilsk Pipeline | Messoyakha Gas Field->Krasnoyarsk Krai | len=263.0 dia=720 cap=? | status=retired | updated=2024-07-29", "P2282 | Barnaul-Biysk-Gorno-Altaysk Gas Pipeline | Barnaul->Altai Republic | len=325.0 dia=300, 325, 520, 720 cap=1.70 | status=operating | updated=2023-08-16", "P2283 | Novosibirsk-Barnaul Gas Pipeline | Novosibirsk->Altai Krai | len=292.0 dia=16 cap=1.70 | status=operating | updated=2023-07-24", "P2327 | Kovykta-Sayansk-Irkutsk Gas Pipeline | Kovykta gas field->Irkutsk Oblast | len=660.0 dia=28.35 cap=2.50 | status=proposed | updated=2025-08-18", "P2362 | Omsk-Novosibirsk-Kuzbass Gas Pipeline | Omsk->Novosibirsk Oblast | len=658.0 dia=1000, 1200, 1220 cap=14.00 | status=operating | updated=2025-08-19", "P2376 | Proskokovo-Achinsk-Krasnoyarsk-Kansk-Balagansk Gas Pipeline | Proskokovo->Irkutsk Oblast | len=1600.0 dia=? cap=? | status=cancelled | updated=2022-08-22", "P2458 | Yurga-Novosibirsk Gas Pipeline | Yurga->Novosibirsk Oblast | len=99.0 dia=530 cap=? | status=operating | updated=2025-08-19", "P2703 | Achinsk-Abakan Gas Pipeline | Achinsk->? | len=341.18 dia=? cap=? | status=cancelled | updated=2022-08-22", "P2705 | Ust-Kamovskaya - Lesosibirsk - Achinsk Gas Pipeline | Ust-Kamovskaya field->? | len=725.8 dia=? cap=? | status=cancelled | updated=2022-07-12", "P3367 | Novosibirsk-Barnaul Gas Pipeline | Barnaul->Altai Krai | len=50.0 dia=16 cap=? | status=operating | updated=2023-07-24", "P3368 | Novosibirsk-Barnaul Gas Pipeline | Shakhi->Altai Krai | len=77.0 dia=? cap=1.20 | status=operating | updated=2023-07-24", "P3369 | Novosibirsk-Barnaul Gas Pipeline | Rebrikha->Altai Krai | len=246.0 dia=40 cap=0.96 | status=proposed | updated=2024-07-17", "P3370 | Novosibirsk-Barnaul Gas Pipeline | Rebrikha->Altai Krai | len=277.0 dia=40 cap=0.86 | status=proposed | updated=2024-07-17", "P3604 | Angarskaya Gas Pipeline | gas fields in central Russia (likely, Yurubcheno-Tokhomskoye Oil and Gas Field)->Irkutsk Oblast | len=? dia=? cap=? | status=cancelled | updated=2024-07-15", "P3980 | Andreevskaya-Ingaly-Bolsherechenskaya Gas Pipeline | Andreevka->Omsk Oblast | len=70.25 dia=325 cap=0.22 | status=proposed | updated=2023-07-25", "P3981 | Bolsherechenskaya-Tarskaya Gas Pipeline | Bolsherechye->Omsk Oblast | len=94.0 dia=325 cap=? | status=proposed | updated=2023-07-24", "P3982 | Tyukalinsk-Valuevskaya-Nalimovskaya-Nazyvaevsk Gas Pipeline | Tyukalinsk->Omsk Oblast | len=98.0 dia=? cap=0.04 | status=construction | updated=2023-07-24", "P4056 | Novokuznetsk-Prokopyevsk Gas Pipeline | Novokuznetsk->Kemerovo Oblast | len=? dia=? cap=0.78 | status=proposed | updated=2023-07-24", "P4110 | Karasuk-Bagan-Kupino-Chistoozernoe-Chany Gas Pipeline | Karasuk->Novosibirsk Oblast | len=? dia=? cap=? | status=proposed | updated=2023-07-25", "P5091 | Prokopyevsky-Toutunhe Pipeline | Prokopyevsky District->Xinjiang | len=? dia=? cap=? | status=cancelled | updated=2025-09-08", "P5510 | Kovykta-Sayansk-Irkutsk Gas Pipeline | Kovykta gas field->Irkutsk Oblast | len=112.0 dia=720 cap=0.00 | status=proposed | updated=2025-08-18", "P5517 | Omsk-Novosibirsk-Kuzbass Gas Pipeline | Novosibirsk->Kemerovo Oblast | len=99.0 dia=1000, 1200, 1220 cap=14.00 | status=operating | updated=2025-08-19", "P5666 | Messoyakha-Norilsk Pipeline | Messoyakha Gas Field->Krasnoyarsk Krai | len=263.0 dia=720 cap=? | status=operating | updated=2024-07-29", "P5667 | Messoyakha-Norilsk Pipeline | Messoyakha Gas Field->Krasnoyarsk Krai | len=263.0 dia=? cap=? | status=operating | updated=2024-07-29", "P5668 | Messoyakha-Norilsk Pipeline | Messoyakha Gas Field->Krasnoyarsk Krai | len=263.0 dia=? cap=? | status=operating | updated=2024-07-29", "P6535 | Volodino-Krasnoyarsk Gas Pipeline | Volodino->Krasnoyarsk Territory | len=700.0 dia=? cap=28.50 | status=proposed | updated=2025-08-18", "P6674 | Bratskoye-Bratsk Gas Pipeline | Bratskoye Gas and Condensate Field->Irkutsk region | len=26.6 dia=325 cap=? | status=operating | updated=2025-08-20", "P6675 | Bratskoye-Bratsk Gas Pipeline | Bratskoye Gas and Condensate Field->Irkutsk region | len=43.6 dia=426, 630, 720 cap=? | status=proposed | updated=2025-08-20", "P6683 | Pelyatka-Messoyakha Gas Pipeline | Pelyatkinskoye Oil and Gas Field->Krasnoyarsk Krai | len=117.0 dia=720 cap=1.80 | status=operating | updated=2024-07-29", "P6684 | Pelyatka-Messoyakha Gas Pipeline | Pelyatkinskoye Oil and Gas Field->Krasnoyarsk Krai | len=62.0 dia=720 cap=1.80 | status=operating | updated=2024-07-29", "P7612 | Myldzhino-Vertikos Gas Pipeline | Myldzhino->Tomsk region | len=110.0 dia=720 cap=2.00 | status=operating | updated=2025-08-18", "P7615 | Nizhnevartovsk-Parabel-Kuzbass Gas Pipeline | Vertikos->Kemerovo region | len=714.0 dia=700 cap=4.10 | status=operating | updated=2025-08-19"], "status_review": true, "lean": true, "model": "sonnet", "extra_brief": "SCOPE: RUSSIA gas, batch R6 of 8 — SIBERIAN FEDERAL DISTRICT (Omsk, Novosibirsk, Tomsk, Kemerovo/Kuzbass,\nAltai Krai + Altai Republic, Krasnoyarsk incl. Taimyr/Norilsk, Irkutsk), **LEAN PASS** (the LEAN PASS\nsection of your contract is binding). 32 rows / 180 owed units: 16 `operating`, 1 `retired`\n(P1647), 1 `construction` (P3982), 9 `proposed`, 5 `cancelled` (P2376, P2703, P2705, P3604, P5091).\nMost rows were last touched 2023–2025 by NF (a few HF 2022, AV 2025, AY 2025). Status review is on for\nevery row. Background: `docs/country_notes/russia.md` (do not re-read other batches).\n\nCALIBRATION — TWO POPULATIONS.\n(1) **Uncited rows** (no `[ref]` on any researched column): 13 rows — P2282, P2283, P2376, P2703, P2705,\nP3367, P3368, P3980, P3981, P3982, P4056, P4110, P5091 (5–11 owed units each: Status, Fuel, PipelineType,\nStart, Length, Diameter, Location, Capacity, Proposal, Owner); plus 159 `MISSING_REF` units scattered over\nthe cited rows. Rule 4(e) end to end: the value\nis on the sheet, find the document that states it, stage `REFS_ADDED` with the SAME value. A source\nwithin rounding IS a ref (note the discrepancy). Use `UNRESOLVED` only when nothing was found, and say\nwhat you searched.\n(2) **The cited rows** owe only the 21 `HAS_REF` units the script could not clear plus their stray\nuncited cells. The 21 (live page, value not found unless noted — re-read for the prose/Cyrillic form):\nenergybase geo-block page on P2327 Capacity+Length and P2458 Diameter (read the Wayback capture, add it\nALONGSIDE); `eo.nadzor-info.ru/expertise/2806481` on P2362+P5517 Diameter; consultant.ru 816-р excerpt on\nP3369/P3370 Capacity; sudact 816-р on P5510 Fuel/PipelineType/Capacity, P6535 Capacity, P6683/P6684\nCapacity; dela.ru on P6535 Start; interfax-russia on P6535 Length; bratsk.irk.today on P6675 Diameter;\nDudinka genplan PDF on P6683/P6684 Length; reph.ru on P7615 Capacity; ttg_n121 PDF (timeout) +\nenergyland on P7615 Length; **P6535 Owner [ref] sonatrach.com = confirmed 404** (may retire once replaced). Cited units whose links merely time out are DEFERRED. Do not\nre-research them. Blank cells (Pressure, SegmentCost, Construction, Proposal, FuelSource, Operator,\nCapacity, Length, Diameter) are DEFERRED. Stage one only if a page you already opened states it (free fill).\nHarvested pool: 295 citations over 32 gem.wiki pages. Open yours first, then go to the operator.\n\nWHERE THE VALUES LIVE. For an operating trunk, one document class answers six columns at once: the\noperator's own site (`about/history`, `about/today`, one page per ЛПУМГ listing its trunks with\ndiameter, length in zone and commissioning year), its corporate newspaper and anniversary books (PDF).\nALL `*.gazprom.ru` hosts connect-time-out from here, so go to Wayback FIRST and cite live + capture.\n- **Gazprom Transgaz Tomsk** `tomsk-tr.gazprom.ru` (ООО «Газпром трансгаз Томск») is THE operator for\n  this batch: Omsk–Novosibirsk–Kuzbass (P2362/P5517; Омское / Новосибирское / Юргинское ЛПУМГ),\n  Yurga–Novosibirsk (P2458), Nizhnevartovsk–Parabel–Kuzbass II (P7615; Парабельское / Александровское /\n  Кожевниковское / Новокузнецкое ЛПУМГ), Myldzhino–Vertikos (P7612), Novosibirsk–Barnaul and the Altai\n  branches (P2283, P3367–P3370, P2282; Барнаульское ЛПУМГ), the Omsk / Novosibirsk / Kuzbass отводы\n  (P3980–P3982, P4110, P4056), and the Irkutsk / Krasnoyarsk projects it services (P2327, P5510, P6535,\n  P6674/P6675 — Иркутское ЛПУМГ, Bratsk). Newspaper «Сибирский газовик» / «Газовик Сибири»; its annual\n  «Годовой отчёт» and `d/journal/…` PDFs. Owners tab already cites `tomsk-tr.gazprom.ru/about/today/`\n  and `/about/history/` for several rows — re-use them via Wayback.\n- **Norilsk cluster (NOT Gazprom)**: АО «Норильсктрансгаз» `norilsktgaz.ru` (Messoyakha–Norilsk I–IV\n  P1647/P5666/P5667/P5668; Pelyatka–Messoyakha P6683/P6684) and АО «Норильскгазпром» (fields,\n  Pelyatkinskoye/Messoyakhskoye/Solenin'skoye), both Nornickel group. Nornickel annual reports\n  (`nornickel.ru`, e-disclosure) and the Taimyr / Dudinka municipal genplans are independent-ish\n  second sources (Nornickel report + Norilsktransgaz = ONE origin; a municipal genplan = second).\n- **Transgaz Yugorsk / Gazprom Dobycha Tomsk (Востокгазпром)**: the Myldzhino field end of P7612 and\n  the Nizhnevartovsk GPZ end of P7615 (the ГПЗ belongs to SIBUR). Cite them only for that end.\n- **Gazprom Invest / Gazprom Mezhregiongaz**: the in-development отводы and Kovykta works. The regional\n  gasification programmes are the primary for every proposed/construction branch:\n  `Программа развития газоснабжения и газификации <Омской / Новосибирской / Кемеровской области /\n  Алтайского края / Иркутской области / Красноярского края> на 2021–2025` and the 2026–2030 successors\n  (regional government portals, gazprommap.ru). gazprommap.ru is Gazprom-side: ONE source, never the\n  second source for a Gazprom page.\nSecond-source classes INDEPENDENT of the operator: the federal planning scheme `Распоряжение\nПравительства РФ от 06.05.2015 N 816-р` + 2024 amendment 3302-р (sudact.ru / legalacts.ru /\nconsultant.ru; cite by number + date; a planned figure is `medium`, vintage stated); Minenergo's\nГенеральная схема развития газовой отрасли; FAS tariff orders; Glavgosexpertiza approvals; regional\ngovernment press services (omskportal.ru, nso.ru, altairegion22.ru, ako.ru, krasnoyarsk.ru / krskstate.ru,\nirkobl.ru, 42.gov / ako.ru for Kuzbass); trade press with its own reporting (neftegaz.ru, interfax.ru /\ninterfax-russia.ru, tass.ru, kommersant.ru; regional: sibkray.ru, ngs.ru, altapress.ru, tayga.info,\nirk.ru, vse42.ru, newslab.ru, ttelegraf.ru). ru.wikipedia is ONE secondary source; cite its footnoted\nprimary where it has one. INDEPENDENCE: a Transgaz page + a Gazprom PJSC report = ONE origin. Transgaz +\nfederal decree / FAS order / regional programme / trade press with its own reporting = TWO. Two outlets\nrunning one press-service text = ONE. energybase.ru restating the operator is not independent.\n\nSEARCH IN RUSSIAN. Use `OtherLanguagePrimaryPipelineName` verbatim as `--name` where it is filled. For\nthe blanks: P3367 `Барнаул — Шахи`; P3368 `Шахи — Ребриха`; P3369 `Ребриха — Рубцовск`; P3370 `Ребриха —\nСлавгород`; P3980 `Андреевская — Ингалы — Большереченская` / `ГРС Большереченская`; P3982 `Тюкалинск —\nВалуевская — Налимовская — Называевск`; P4056 `Новокузнецк — Прокопьевск`; P4110 `Карасук — Баган —\nКупино — Чистоозёрное — Чаны`; P6674/P6675 `Братское ГКМ — Братск` (Братскэкогаз); P3604 `Ангарский\nгазопровод` (Юрубчено-Тохомское). P5091's only name is Chinese `中俄天然气管道西线` = the Altai / «Сила\nСибири — 2» western route (`газопровод «Алтай»`). Old names: Кузбасс = Кемеровская область; Taimyr =\nТаймырский Долгано-Ненецкий район. Vocabulary: `магистральный газопровод`, `газопровод-отвод`,\n`межпоселковый`, `нитка`, `лупинг`, `ЛПУМГ`, `КС`, `ГРС`, `введён в эксплуатацию`, `протяжённость … км`,\n`диаметр … мм`, `млрд куб. м в год`, `тыс. куб. м в час`.\n\nTRAPS: settle each with documents, never by merging or blanking.\n- **P7615 Nizhnevartovsk–Parabel–Kuzbass II** (714 km, Diameter 700, 4.10 bcm/y, Start 2012, starts\n  `Vertikos`): Capacity 4.10 is NF's DOCUMENTED even split of 8.2 bcm/y (\"total capacity is 8.2 bcm/y\n  - split evenly between two pipelines\", ResearcherNotes 2025-08-19). R4b (sibling P2350, string I)\n  found the 8.2 figure is stated for the whole line and that string II was built in PARTIAL STAGES\n  (1992 / 1994 / 2011), and filed a `spec` concern on P2350. This is a documented divergence: **flag,\n  do not overwrite** — no value-changing Capacity fill; file a `spec` concern naming P2350 + P7615 and\n  cite the whole-line document as such. Also settle: StartYear1 2012 vs the staged build (which stage\n  is 2012?); Diameter 700 is not a standard Russian size (720?); StartLocation Vertikos vs the\n  Nizhnevartovsk GPZ name; 714 km for string II vs P2350's 1162 km.\n- **Omsk–Novosibirsk–Kuzbass (P2362 / P5517) and Yurga–Novosibirsk (P2458)**: P2362 and P5517 both\n  carry Diameter `1000, 1200, 1220` and 14.00 bcm/y — a system figure copied onto both segments (a `spec`\n  concern naming both, per AGGREGATE-VS-SEGMENT). P2362's 658 km and P5517's 99 km are NF's DOCUMENTED\n  estimates (\"could not find … should be around 650 km\"; P5517 \"around 99 km (similar to\n  Yurga–Novosibirsk)\"): search for a sourced length, but a different figure is a concern, not a\n  value-changing fill. P5517 Novosibirsk–Kuzbass (ends Proskokovo КС) and P2458 Yurga–Novosibirsk (99\n  km, 530 mm, 1980) both run Novosibirsk ↔ Yurga/Proskokovo: are they the same corridor at different\n  diameters (parallel lines = two rows OK) or one line recorded twice? File `duplicate`/`classification`\n  only on documents. StartYear1 is blank on P2362/P5517 (deferred; free fill if stated).\n- **Novosibirsk–Barnaul family (P2283, P3367, P3368, P3369, P3370) + P2282 Barnaul–Biysk–Gorno-Altaysk.**\n  **Diameter units**: P2283 and P3367 carry `16`, P3369/P3370 carry `40` — Russia rows are mm, so these\n  look like inches or cm (16\" ≈ 426 mm; 40 cm = 400 mm?). Find the mm figure; if a document states it,\n  stage a Diameter fill (medium) with a `spec` concern explaining the unit error; never guess a\n  conversion. P3368 CapacityUnits `mill.Sm3/day` is off-vocabulary (sheet uses bcm/y; × 0.365) — flag.\n  P3367 is recorded 50 km while ZK's note says the one link found was about an 8.5 km pipeline. P3368\n  StartYear 2022 vs HF's note \"commissioned in Dec 2021\". P3369/P3370 targets 2023: status review — built,\n  under construction, re-dated in the 2026–2030 programme, or slipped (NF 2024: removed from Minenergo's\n  planned-transmission list, re-typed distribution). Classification: P2283 is `transmission` while the\n  segment rows are `distribution` — apply the отвод test row by row. P2282 multi-value `300, 325, 520,\n  720` — source each size or flag.\n- **Messoyakha–Norilsk I–IV (P1647 retired / P5666 / P5667 / P5668)**: all four carry 263 km — per-string\n  length or corridor length copied? NF 2023 retired string I off the 2009 annual report (\"segments 2, 3\n  and 4 operating\"); status review needs a post-2023 Norilsktransgaz / Nornickel source for II–IV and\n  anything that says I was dismantled or is back in service. Strings III/IV Diameter blank (deferred).\n  Owners tab: P5666–P5668 carry `АО \"Норильсктрансгаз\"` (Cyrillic) in the English `Operator` column —\n  note it in the Owner/Operator record, don't restage the entity.\n- **Pelyatka–Messoyakha I/II (P6683 / P6684)**: Length 117 / 62 km is NF's DOCUMENTED choice (\"Used NGL\n  pipeline length since it runs parallel to it\", Dudinka genplan) — flag, don't overwrite. Both carry\n  1.80 bcm/y (copied?). P6684's Cyrillic name drops Pelyatka («Северо-Соленинское – Южно-Соленинское –\n  Мессояха, II нитка») while its EnglishName starts at Pelyatka: settle each string's actual termini.\n- **Kovykta–Sayansk–Irkutsk P2327 vs P5510 (duplicate suspect, campaign memo §4)**: P2327 (660 km, 2.50\n  bcm/y, Start 2028, Diameter `28.35` — that is 720 mm in INCHES, a unit error) and P5510 (112 km, 720 mm,\n  Capacity 0.00, Start 2025, ends Zhigalovo; NF note: \"built a while ago, but is not operating, will need\n  to be rebuilt\"). P5510 looks like the existing Kovykta–Zhigalovo local line (РУСИА Петролеум, 2000s),\n  i.e. a separate pipeline under the trunk's name, not a segment of it. Settle identity with documents\n  (`classification`/`duplicate`), flag Capacity 0.00 and the 28.35 unit error. Related rows outside this\n  batch: P2353 Power of Siberia Kovykta–Chayanda, P3603 PoS-2 Sayansk branch (cancelled) — name them in\n  `cross_row_leads` if relevant. Status: Gazprom's Irkutsk gasification (Kovykta → Sayansk → Irkutsk)\n  target dates slipped repeatedly; stage a newer dated target if found.\n- **P6535 Volodino–Krasnoyarsk** (proposed, 700 km, 28.50 bcm/y, Start 2028): **Owner is recorded as\n  `Sonatrach` with a sonatrach.com Owner [ref]** — an obvious mis-attribution (Gazprom project). File an\n  `attribution` concern with the Gazprom/Transgaz Tomsk source; never cite sonatrach.com. 28.50 bcm/y\n  on a Krasnoyarsk gasification line looks like a Power of Siberia–scale number: `spec` unless a\n  document states it for THIS line. Relation to cancelled P2376 (Proskokovo–Achinsk–Krasnoyarsk–Kansk)\n  and to P0734 PoS-2 (NF note: will become part of it) → `cross_row_leads`.\n- **Bratskoye–Bratsk I/II (P6674 operating 2009, 26.6 km, 325 mm; P6675 proposed 2027, 43.6 km, `426,\n  630, 720`)**: the Bratskoye field licence holder is reported as ООО «Братскэкогаз» — find who owns and\n  operates the LINE (it may not be Transgaz Tomsk or Gazprom); owners tab puts `ООО «Газпром трансгаз Томск»` in the Chinese `QCCOwner` column on P6674 and cites\n  tomsk-tr history for Owner — verify the owner/operator and file `attribution` on evidence.\n- **Omsk / Novosibirsk / Kuzbass in-development отводы (P3980, P3981, P3982, P4110, P4056)**: all recorded\n  `distribution`, no refs. P3981's Cyrillic name is a `Газопровод-отвод от ГРС … до ГРС «Тарская»` —\n  rule: a `газопровод-отвод` terminating AT a ГРС is transmission; `межпоселковый` downstream of the ГРС\n  is distribution. File `classification` row by row. **Flag, never reclassify.** Status: P3982\n  `construction` target 2023 — finished? P3981 target 2025, P4110 2025 (NF: stages 2025–2027) — built,\n  re-dated in the 2026–2030 programme, or slipped? P4056 (FEED in progress 11/2022; NF: a small branch\n  off an existing untracked line) — any construction? P3980 Capacity 0.22 bcm/y on a 325 mm отвод:\n  check units.\n- **Cancelled rows (P2376, P2703, P2705, P3604, P5091)**: mostly HF-2022 entries off the East Siberian gas\n  programme / PE map. Status review: confirm the cancellation with the newest document (a scheme\n  revision dropping it, an operator statement), or detect a REVIVAL (the Krasnoyarsk gasification\n  pipeline and PoS-2 debates revived Achinsk/Kansk routings — P2376/P2703/P6535). Existence: P2703\n  (\"found in Exxon database\") and P3604 (NF: \"don't know the exact name and start location\") — file\n  `existence_classification` if no primary document describes the project. P5091 is the Altai route\n  (Prokopyevsk → Xinjiang); owners `--`; suspended after 2015 and superseded by PoS-2 via Mongolia —\n  confirm `cancelled` vs `shelved` with dated sources; relation to P0734 → `cross_row_leads`.\nAGGREGATE-VS-SEGMENT: a system figure is never a ref for a string row. Flag it, cite the system document\nas such, and say which rows share it. One DN1420 string carries ~26–33 bcm/y, DN1220 ~15–20, DN1020\n~8–12, DN720 ~3–5, DN530 ~1.5–2.5, DN325 ~0.3–0.8. Anything far above is a system number.\n\nSTATUS REVIEW: one record per row, all 32. For an operating line, `confirm` needs a source DATED LATER\nTHAN 2023-08 naming the line (operator page/news, a repair or diagnostics item, a tariff order, an\naccident report, a regional gasification report). Say which source and its date. Absence of news about\nan old trunk is not evidence, so never `stale` an operating row. In-development rows: built → `change`\nwith the date; a dated newer target → stage it; no progress evidence since the last target → `stale`\nwith `shelved`, `ShelvedCancelledType = inferred`, and no URL for the inference. Cancelled rows: confirm\nor `change` on a revival document. A changed Status goes in BOTH `status_reviews[].proposed_changes` and\nthe Status fill.\n\nSTATE CELLS: `Irkutsk region` vs `Irkutsk Oblast` (P2327/P5510 disagree with themselves), `Kemerovo region`\nvs `Kemerovo Oblast`, `Tomsk region`, `Altai territory` vs `Altai Krai`, `Krasnoyarsk Territory` vs\n`Krasnoyarsk Krai`; P2703/P2705 Start/EndState blank. Stage a correction as a `Location [ref]` fill ONLY\nwhere you already hold a source placing that terminus. Vocabulary drift is a note, not a finding.\n\nVALIDITY TEXT goes in `researcher_notes` + `recommendation` (never a bare `notes` or `summary` key — the\nValidity tab reads `recommendation`). Use `contested: {\"<Column>\": \"<candidate value>\"}` ONLY for a\npasteable candidate value — never prose.\n\nDOCUMENTED DIVERGENCES: when ResearcherNotes explains how a value was derived (an even split, a parallel\nline's length, an estimate), a source stating something else is a `spec` concern quoting both — NOT a\nvalue-changing fill. Rows with such notes here: P7615, P2362, P5517, P6683, P6684.\n\nOWNERSHIP: `Owner [ref]` is owed on most Gazprom rows (both live on the `Gas_OperatorsOwners` tab). One\nTransgaz Tomsk page stating the trunks are ПАО «Газпром» property operated by the subsidiary, or the\nGazprom annual report, settles a family, so cite it on each row. Norilsk rows: Nornickel group. The\nexisting entity string `Gazrpom Transgaz Tomsk LLC` (P7612/P7615) is a known typo on the owners tab —\ndon't restage the entity.\n\nUNITS: metric: km, mm, bcm/y (`млн куб. м в сутки` × 0.365; `тыс. м³/ч` × 8.76 / 1000), MPa. A multi-value\n`720, 1020` is the sheet's convention for a line with two sizes. `*CostUnits` = bare currency code, with\nthe magnitude in the number. Vocabulary is lowercase; only `FIDStatus` is capitalized.\n\nRULES THAT BITE (the contract has the rest): no GEM cites; abarrelfull / theodora / yingdodo are banned;\nnever cite sonatrach.com for a Russian line; every URL goes through `scripts/url_verifier.py --name\n\"<Cyrillic name>\"`; only a confirmed 404/410 retires a ref. A `*.gazprom.ru` timeout, an `energybase.ru`\ngeo-block page, or a 401/403/468 is an ACCESS FAILURE: read the Wayback capture and add it ALONGSIDE,\nnever swap. A category / search / map-home / tender-index page is not a citation, openstreetmap.org is\nnot a `[ref]`, and an inferred status change has no URL. TIMEOUTS: `curl --max-time 30` on every fetch;\nWayback FIRST for any host in the timeout list; a legal mirror first for any federal act. Query Wayback\nvia the CDX API, one call per URL (`http://web.archive.org/cdx/search/cdx?url=<url>&limit=5&fl=timestamp,\nstatuscode`). A 429 or an empty body is the rate limit: retry later in the run, not a missing capture.\n\nMEASURED CONDITIONS (2026-09-21/22, this machine, US IP):\n- TIMEOUT (Wayback first, cite live + capture): every `*.gazprom.ru` (tomsk-tr, invest, mrg), aup.ru\n  intermittently, government.ru, pravo.gov.ru, docs.cntd.ru.\n- ACCESS FAILURE codes: kommersant.ru 500 / vedomosti.ru 502 on the home page (try article deep links,\n  else Wayback); e-disclosure.ru 403; market.neftegaz.ru 468; rg.ru / rbc.ru 401.\n- 200: reph.ru (self-signed TLS), sudact.ru, legalacts.ru, consultant.ru, neftegaz.ru, interfax.ru,\n  tass.ru, gasforum.ru, ru.wikipedia.org, web.archive.org. energybase.ru answers 200 with its geo-block\n  page. vk.com serves a JS shell (try m.vk.com or Wayback). dzen.ru pages are reposts: cite the original.\n", "groups": [["P1647", "P5666", "P5667", "P5668"], ["P6683", "P6684"], ["P2283", "P3367", "P3368", "P2282"], ["P3369", "P3370"], ["P2362", "P5517", "P2458"], ["P7615", "P7612"], ["P2327", "P5510", "P6674", "P6675"], ["P3980", "P3981", "P3982"], ["P4110", "P4056"], ["P2376", "P2703", "P2705", "P3604"], ["P6535", "P5091"]]}
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
