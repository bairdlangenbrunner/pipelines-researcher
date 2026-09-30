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
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/russia-gas/staging/deepsweep-r7-central-south", "commodity": "gas", "country": "Russia", "pids": ["P0736", "P0743", "P0744", "P0751", "P0760", "P0765", "P0769", "P1368", "P1470", "P1472", "P1475", "P1477", "P2227", "P2285", "P2288", "P2296", "P2321", "P2339", "P2343", "P2366", "P2379", "P2380", "P2381", "P2426", "P2432", "P2433", "P3483", "P3714", "P3971", "P3972", "P3973", "P3974", "P3996", "P3997", "P3998", "P4012", "P4013", "P4130", "P4131", "P4132", "P4142", "P4143", "P4144", "P5551", "P5654", "P5655", "P5656", "P5665", "P5875"], "roster": ["P0736 | Blue Stream Gas Pipeline | Izobilny->? | len=1213.0 dia=610, 1200, 1400 cap=16.00 | status=operating | updated=2023-08-08", "P0743 | Dzhubga-Lazarevskoye-Sochi Gas Pipeline | Dzhubga->Krasnodar Krai | len=171.6 dia=530 cap=3.80 | status=operating | updated=2025-08-22", "P0744 | Dzuarikau-Tskhinvali Gas Pipeline | Dzuarikau->Republic of South Ossetia | len=162.3 dia=426 cap=0.25 | status=operating | updated=2023-08-11", "P0751 | Hajigabul-Shirvanovka-Mozdok Pipeline | Hajigabul (Kazi Magomed)->North Ossetia | len=680.0 dia=1220 cap=10.00 | status=operating | updated=2024-09-20", "P0760 | South Stream Gas Pipeline | Anapa->Udine and Lower Austria | len=2380.0 dia=? cap=63.00 | status=cancelled | updated=2025-09-06", "P0765 | TurkStream Gas Pipeline | Anapa->Kırklareli | len=930.0 dia=813 cap=15.75 | status=operating | updated=2023-08-11", "P0769 | Yamal-Europe Gas Pipeline | Torzhok->? | len=1660.0 dia=1420.00 cap=33.00 | status=idle | updated=2024-09-16", "P1368 | TurkStream Gas Pipeline | Anapa->Kırklareli | len=930.0 dia=813 cap=15.75 | status=operating | updated=2023-08-11", "P1470 | Krasnodar Krai-Serpukhov Gas Pipeline | Krasnodar->Moscow Oblast | len=1177.0 dia=1020 cap=? | status=operating | updated=2023-08-03", "P1472 | North Caucasus-Transcaucasia Gas Pipeline | Tiblisi->? | len=? dia=500, 700, 1200, 1400 cap=12.00 | status=operating | updated=2024-09-25", "P1475 | Maykop-Samur-Sochi Pipeline | Maykop->Krasnodar Krai | len=186.0 dia=700 cap=2.00 | status=operating | updated=2023-08-02", "P1477 | Kumli-Kizlyar-Babayurt-Aksai Pipeline | Kumli->Republic of Dagestan | len=115.0 dia=1020 cap=8.50 | status=operating | updated=2023-08-15", "P2227 | Russian Federation – Turkey Natural Gas Main Transmission Line | Malkoclar->Ankara | len=842.0 dia=24, 36 cap=4.00 | status=mothballed | updated=2022-08-02", "P2285 | Belousovo-Leningrad Gas Pipeline | Zhukovsky District->Leningrad Oblast | len=765.0 dia=1020 cap=7.00 | status=operating | updated=2023-08-04", "P2288 | Bryansk-Smolensk Gas Pipeline | Bryansk->Smolensk Oblast | len=240.0 dia=530 cap=? | status=operating | updated=2023-08-15", "P2296 | Sohranovka-Oktyabrskaya Gas Pipeline | Sokhranovka->Rostov Oblast | len=310.0 dia=1420 cap=28.00 | status=operating | updated=2023-08-16", "P2321 | Kasimovskoye UGS-KS Voskresensk Gas Pipeline | ?->Moscow Oblast | len=204.0 dia=1220 cap=2.70 | status=operating | updated=2023-08-21", "P2339 | Maykop-Nevinnomyssk Gas Pipeline | ?->Stavropol Krai | len=? dia=720 cap=2.50 | status=operating | updated=2023-08-16", "P2343 | Mozdok-Nevinnomyssk Gas Pipeline | ?->Stavropol Krai | len=257.0 dia=820, 1020 cap=? | status=operating | updated=2023-08-15", "P2366 | Ostrogozhsk-Belousovo Gas Pipeline | Ostrogozhsky District->Kaluga Oblast | len=810.0 dia=1020 cap=8.79 | status=operating | updated=2023-08-21", "P2379 | Ring of the Moscow region-Belousovo Gas Pipeline | ?->Kaluga Oblast | len=150.0 dia=820 cap=? | status=operating | updated=2023-08-09", "P2380 | Ring of the Moscow Region Gas Pipeline | ?->Moscow Oblast | len=365.0 dia=800 cap=90.00 | status=operating | updated=2023-08-09", "P2381 | Rostov-Maykop Gas Pipeline | ?->Republic of Adygea | len=? dia=820 cap=3.10 | status=operating | updated=2023-08-16", "P2426 | Pisarevka-Anapa Gas Pipeline | Kantemirovsky District->Krasnodar Krai | len=880.0 dia=700-1400 cap=63.00 | status=operating | updated=2023-08-03", "P2432 | Torzhok-Valdai Gas Pipeline | Torzhok->Novgorod Oblast | len=? dia=1020 cap=? | status=operating | updated=2023-08-14", "P2433 | Tula-Torzhok Gas Pipeline | Tula->Tver Oblast | len=? dia=1220 cap=? | status=operating | updated=2023-08-09", "P3483 | Torzhok-Minsk-Ivatsevichy Gas Pipeline | Torzhok->? | len=851.0 dia=1220.00 cap=40.00 | status=operating | updated=2024-09-16", "P3714 | Vladimir Filanovsky Gas Pipeline | ?->Stavropol Krai | len=114.0 dia=28.00 cap=? | status=operating | updated=2023-08-18", "P3971 | Zam'yany-Bugrinskoye Gas Pipeline | Zam'yany compressor station->Astrakhan Oblast | len=151.0 dia=325 cap=0.38 | status=proposed | updated=2023-07-27", "P3972 | Kharabali-Akhtubinsk 2-Akhtubinsk 1 Gas Pipeline | Kharabali gas distribution station->Astrakhan Oblast | len=179.5 dia=530, 325, 219, 159, 108 cap=0.74 | status=proposed | updated=2023-07-27", "P3973 | Puchezh-Yuryevets Gas Pipeline | Puchezh gas distribution station->Ivanovo Oblast | len=46.49 dia=100 cap=0.61 | status=proposed | updated=2023-07-26", "P3974 | Palekh-Lukh Gas Pipeline | Palekh gas distribution station->Ivanovo Oblast | len=44.53 dia=200 cap=0.05 | status=proposed | updated=2023-07-26", "P3996 | Zaterechny Gas Distribution Station Gas Pipeline | South of Zaterechny gas distribution station->Stavropol Krai | len=1.0 dia=? cap=0.23 | status=proposed | updated=2023-07-28", "P3997 | Zaterechny Gas Distribution Station Gas Pipeline | Zaterechny gas distribution station->Stavropol Krai | len=? dia=? cap=? | status=proposed | updated=2023-07-28", "P3998 | Zaterechny-Velichaevskoe Gas Pipeline | Zaterechny gas distribution station->Stavropol Krai | len=26.9 dia=? cap=? | status=proposed | updated=2023-07-28", "P4012 | Gorky-Cherepovets Gas Pipeline | Mitino->Yaroslavl Oblast | len=60.0 dia=? cap=11.27 | status=proposed | updated=2025-08-19", "P4013 | Borok-Breytovo Gas Pipeline | Borok->Yaroslavl Oblast | len=? dia=? cap=0.01 | status=proposed | updated=2023-07-26", "P4130 | Stomino-Nikitenki Gas Pipeline | Stomino-CS Smolenskaya->Smolensk Oblast | len=67.0 dia=? cap=0.08 | status=construction | updated=2023-07-21", "P4131 | Selivanovo Gas Pipeline | Vyazma->Smolensk Oblast | len=36.4 dia=? cap=0.10 | status=proposed | updated=2023-07-21", "P4132 | Smolenskaya GRES-Zharkovskii Gas Pipeline | Dobrino->Tver Oblast | len=35.4 dia=? cap=? | status=operating | updated=2024-07-19", "P4142 | Rzhev-Olenino-Zapadnaya Dvina Gas Pipeline | Rzhev->Tver Oblast | len=148.3 dia=? cap=? | status=proposed | updated=2023-07-26", "P4143 | Rzhev-Olenino-Zapadnaya Dvina Gas Pipeline | Nikitino->Tver Oblast | len=? dia=? cap=? | status=proposed | updated=2023-07-26", "P4144 | Alkhazurovo-Shatoi Gas Pipeline | Alkhazurovo->Chechen Republic | len=28.5 dia=300 cap=0.18 | status=proposed | updated=2023-07-31", "P5551 | Krasnodar Krai-Serpukhov Gas Pipeline | Krasnodar->Moscow Oblast | len=1177.0 dia=820 cap=? | status=operating | updated=2023-08-03", "P5654 | Torzhok-Minsk-Ivatsevichy Gas Pipeline | Torzhok->? | len=851.0 dia=1220.00 cap=40.00 | status=operating | updated=2024-09-16", "P5655 | Torzhok-Minsk-Ivatsevichy Gas Pipeline | Torzhok->? | len=851.0 dia=1220.00 cap=40.00 | status=operating | updated=2024-09-16", "P5656 | Petrovsk-Elets Gas Pipeline | ?->? | len=? dia=1220 cap=16.40 | status=operating | updated=2023-08-15", "P5665 | Rostov-Maykop Gas Pipeline | ?->Republic of Adygea | len=? dia=820 cap=4.10 | status=operating | updated=2023-08-16", "P5875 | North Caucasus-Transcaucasia Gas Pipeline | Mozdok->? | len=271.0 dia=720 cap=? | status=operating | updated=2024-09-25"], "status_review": true, "lean": true, "model": "sonnet", "extra_brief": "SCOPE: RUSSIA gas, batch R7 of 8 — CENTRAL + SOUTHERN + NORTH CAUCASUS FEDERAL DISTRICTS (Moscow ring,\nTver/Smolensk/Bryansk/Kaluga/Tula/Voronezh/Ryazan/Yaroslavl/Ivanovo, Rostov, Krasnodar, Adygea, Astrakhan,\nStavropol, Dagestan, North Ossetia, Chechnya) plus the EXPORT TRUNKS that start here (TurkStream, Blue\nStream, South Stream, Yamal–Europe, Torzhok–Minsk–Ivatsevichy, North Caucasus–Transcaucasia,\nHajigabul–Mozdok, Russia–Turkey West line). **LEAN PASS** (your contract's LEAN PASS section\nbinds). The regional pass ends here. 49 rows / 408 owed units: 32 `operating`, 13 `proposed`,\n1 `construction` (P4130), 1 `cancelled` (P0760), 1 `idle` (P0769), 1 `mothballed` (P2227). Mostly NF 2023.\nStatus review is on for every row.\nBackground: `docs/country_notes/russia.md` (do not re-read other batches).\n\nCALIBRATION. **44 of 49 rows carry no `[ref]` on any researched column**, so nearly every unit is\n`MISSING_REF` (385). Apply rule 4(e) end to end: the value is on the sheet, so find the document that\nstates it and stage `REFS_ADDED` with the SAME value. A source within rounding IS a ref (note the\ndiscrepancy). `UNRESOLVED` means nothing was found, and the record says what you searched. The 23\n`HAS_REF` units the script could not clear:\n- **P0743 DLS**: 7 cells cite energybase (geo-block page) + gazprom.ru/projects/dls (timeout). Read the\n  Wayback captures and add them ALONGSIDE. SegmentCost on kommersant.ru/doc/1655365 (value 31.5 bn not\n  found; re-read for «31,5 млрд руб.»).\n- **P4012**: sudact 816-р annex 4_1 (Capacity not found); archive.org item + yarregion PDF and\n  gazprommap.ru/yaroslavskaya (value present, name not found). Re-read for the Cyrillic segment name.\n- **P0751**: IEA Azerbaijan profile + fief.ru (name not found).\n- **P1475**: `expert.ru/` is a HOME PAGE (not a citation; replace it); kavkaz-uzel, vtg Wayback, krasnodar-tr.\n- **P0769**: isans.org Belarus PDF (name not found; re-read p.34 for «Ямал — Европа»).\n\nBlank cells (Pressure, SegmentCost, Construction, Proposal, FuelSource, Operator, Capacity, Length,\nDiameter, StartYear1) are DEFERRED. Stage one only if a page you already opened states it (free fill).\nHarvested pool: 435 citations over 49 gem.wiki pages. Open yours first, then go to the operator.\n\nWHERE THE VALUES LIVE. For an operating trunk the operator's own site (`about/history`, `about/today`,\nper-ЛПУМГ pages: diameter, length in zone, commissioning year) + its newspaper/anniversary PDFs answer\nsix columns at once. ALL `*.gazprom.ru` hosts connect-time-out from here (verified 2026-09-22: moskva-tr, spb-tr,\nkrasnodar-tr, gazpromexport). Go to Wayback FIRST and cite live + capture. Operator by region (VERIFY\nper row — never assume; a regional boundary does not settle which subsidiary runs a trunk):\n- **Gazprom Transgaz Moscow** `moskva-tr.gazprom.ru`: Moscow ring КГМО (P2380, P2379), Serpukhov end of\n  Krasnodar–Serpukhov (P1470/P5551), Kasimov UGS–Voskresensk (P2321), Belousovo (P2285/P2366/P2379),\n  Tula–Torzhok (P2433), Bryansk–Smolensk (P2288), Petrovsk–Elets (P5656), and possibly the Smolensk\n  отводы (P4130–P4132).\n- **Gazprom Transgaz Saint Petersburg** `spb-tr.gazprom.ru`: Torzhok hub (P2432 Torzhok–Valdai, the\n  Torzhok end of P0769/P3483), Belousovo–Leningrad (P2285), and the Tver отводы (P4142/P4143).\n- **Gazprom Transgaz Krasnodar** `krasnodar-tr.gazprom.ru`: DLS (P0743), Maykop–Samurskaya–Sochi (P1475),\n  Rostov–Maykop (P2381/P5665), Maykop–Nevinnomyssk (P2339), Pisarevka–Anapa (P2426), the Krasnodar end\n  of P1470/P5551, and the TurkStream/Blue Stream onshore КС «Русская» / «Береговая».\n- **Gazprom Transgaz Stavropol** `stavropol-tr.gazprom.ru`: Mozdok–Nevinnomyssk (P2343), Izobilny (Blue\n  Stream start), Zaterechny (P3996–P3998), Chechnya (P4144), Dzuarikau–Tskhinvali (P0744), Mozdok\n  (P0751, P5875).\n- **Gazprom Transgaz Makhachkala** `makhachkala-tr.gazprom.ru`: Kumli–Aksai (P1477).\n- **Gazprom Transgaz Volgograd** `volgograd-tr.gazprom.ru`: Sokhranovka–Oktyabrskaya (P2296), the\n  Astrakhan отводы (P3971/P3972).\n- **Gazprom Transgaz Nizhny Novgorod** `nn-tr.gazprom.ru`: Ivanovo отводы (P3973/P3974).\n- **Gazprom Transgaz Ukhta** `ukhta-tr.gazprom.ru`: Gorky–Cherepovets / Burmakino–Rybinsk (P4012; the\n  owners tab already names it as Operator) and possibly Borok–Breytovo (P4013).\n- **Export/foreign**: TurkStream offshore = South Stream Transport B.V. `turkstream.info`; Blue Stream\n  offshore = Blue Stream Pipeline Co. B.V. (Gazprom/Eni); Turkish onshore = BOTAŞ `botas.gov.tr`;\n  Yamal–Europe Poland = EuRoPol GAZ `europolgaz.com.pl`; Belarus + Torzhok–Minsk–Ivatsevichy = Gazprom\n  Transgaz Belarus `btg.by`; Georgia = GOGC, Armenia = Gazprom Armenia, Azerbaijan = SOCAR.\n- **P3714 Vladimir Filanovsky = LUKOIL** (`lukoil.ru`/`.com`, Nizhnevolzhskneft), NOT Gazprom.\n- Regional gasification programmes are the primary for every proposed/construction отвод:\n  `Программа развития газоснабжения и газификации <региона> на 2021–2025` (Astrakhan,\n  Ivanovo, Tver, Smolensk, Yaroslavl, Stavropol, Chechnya) and the 2026–2030\n  successors (regional portals; gazprommap.ru). gazprommap is Gazprom-side: ONE source,\n  never the second source for a Gazprom page.\n\nSecond-source classes INDEPENDENT of the operator:\n- **Federal planning scheme** `Распоряжение Правительства РФ от 06.05.2015 N 816-р` + the 2024 amendment\n  3302-р (sudact.ru / legalacts.ru / consultant.ru). Cite by number + date; a planned figure is\n  `medium`, with the vintage stated.\n- Minenergo's Генеральная схема; FAS tariff orders; Glavgosexpertiza.\n- Regional government press services (the region's `.ru` / `.gov.ru` portal).\n- **Trade press** with its own reporting (neftegaz, interfax, tass, kommersant, kavkaz-uzel); for\n  export lines IEA / OIES, Reuters, Anadolu, EPDK, ENTSOG and the foreign regulators.\n- ru.wikipedia = ONE secondary source; cite its footnoted primary.\n\nINDEPENDENCE: ONE origin = Transgaz + Gazprom PJSC; turkstream.info + gazprom.ru; two outlets on one\npress-service text; energybase restating the operator. TWO = Transgaz + decree / FAS / regional\nprogramme / foreign regulator / trade press with its own reporting.\n\nSEARCH IN RUSSIAN. Use `OtherLanguagePrimaryPipelineName` verbatim as `--name` where it is filled.\nFor the blanks:\n- **Trunks:** P2339 `Майкоп — Невинномысск`; P2343 `Моздок — Невинномысск`; P2366 `Острогожск —\n  Белоусово`; P2379 `КГМО — Белоусово`; P2381/P5665 `Ростов — Майкоп` (нитки I/II); P5551 `Краснодарский\n  край — Серпухов, II нитка`; P2432 `Торжок — Валдай`; P2433 `Тула — Торжок`; P5875 `Моздок — Тбилиси`\n  and P1472 `Тбилиси — Ереван` (both «Северный Кавказ — Закавказье»); P0751 `Гаджигабул — Моздок`\n  (Azeri: Hacıqabul–Şirvanovka).\n- **Export lines:** P0760 `Южный поток`; P0765/P1368 `Турецкий поток` (нитка 1/2); P2227 = the Turkish\n  section of the Трансбалканский газопровод (BOTAŞ «Batı Hattı», Malkoçlar–Ankara).\n- **LUKOIL:** P3714 `газопровод с месторождения им. В. Филановского` (ЛУКОЙЛ-Нижневолжскнефть →\n  Будённовск).\n- **Отводы:** P3971 `Замьяны — Бугринское` (КС Замьяны); P3972 `Харабали — Ахтубинск`; P3973 `Пучеж —\n  Юрьевец`; P3974 `Палех — Лух`; P4013 `Борок — Брейтово`; P4142 `Ржев — Оленино — Западная Двина`;\n  P4144 `Алхазурово — Шатой`; P3996/P3997 `ГРС Затеречная` / `АГРС`; P3998 `Затеречный —\n  Величаевское`; P4130 `Стомино — Никитенки` (the Cyrillic segment name says д. Никитино — check which).\n\nTRAPS (the researcher's leads, NOT verified). Settle each with documents, never by merging or blanking.\n- **Copied figures on paired rows (strings/segments).** For each pair, find whether the figure belongs to\n  one string, the other, or the corridor. A sibling's figure is never a second source, and a system\n  figure on a string row is a `spec` concern (see AGGREGATE-VS-SEGMENT).\n  - **P0765/P1368 TurkStream 1/2**: both 930 km, 813 mm, 15.75 bcm/y, 2020. 930 km is the OFFSHORE\n    length per string, and 15.75 = 31.5/2 is the per-string design, so these may be right. Confirm\n    against turkstream.info. Owner1 = Gazprom PJSC 100%: the offshore owner is South Stream Transport\n    B.V. (a Gazprom subsidiary), and the Turkish onshore of string 2 runs to the Bulgarian border\n    (BOTAŞ). `attribution` only on documents. P0765 ends Lüleburgaz, P1368 ends Malkoçlar: check each\n    landfall/terminus.\n  - **P1470/P5551 Krasnodar Krai–Serpukhov I/II**: both 1177 km and Start 1961 at 1020 / 820 mm. NF 2022:\n    \"seems to be of 2 strings … data is limited\" (olginskaya-aksay PDF). Is 1177 km per string, and\n    did both open in 1961? P1470 Operator = `Gazprom PJSC` (a Transgaz subsidiary is the usual operator:\n    flag, don't restage).\n  - **P2381/P5665 Rostov–Maykop I/II**: StartState `Yaroslavl Oblast` on BOTH, an obvious error for\n    Rostov Oblast. Stage a `Location [ref]` fill only with a source placing the Rostov terminus. No\n    length; capacities 3.10 vs 4.10 bcm/y. NF cites government.ru/docs/all/101903 (government.ru times\n    out: use Wayback).\n  - **P3483/P5654/P5655 Torzhok–Minsk–Ivatsevichy I/II/III**: all 851 km, 1220 mm, 40 bcm/y. NF\n    DOCUMENTED \"the capacity number is total for the pipeline\" and \"some sources report different\n    length\". That is a divergence: FLAG, do not overwrite. File a `spec` concern naming all three rows.\n    Mostly in Belarus (`btg.by`). Source Start 1974/1978/1983 per string.\n  - **P5656 Petrovsk–Elets Looping**: 16.4 bcm/y is a two-pipe system total also carried on P1466\n    (R5 found this). Start/End locations and states are blank (free fill only).\n  - **P3996/P3997 Zaterechny GDS** (1 km, 0.23 bcm/y / connecting segment) + P3998\n    Zaterechny–Velichaevskoe. Is P3997 a real separate object or a sketch of P3996? Answer the\n    `duplicate` question on documents.\n  - **P4142/P4143 Rzhev–Olenino–Zapadnaya Dvina** (148.3 km) + Nikitino–Nelidovo segment (P4143's\n    Cyrillic is a separate `Газопровод-отвод к г. Нелидово … ГРС «Нелидово»`). Is it a segment or its\n    own отвод?\n- **P2227 \"Russian Federation – Turkey Natural Gas Main Transmission Line\"** (mothballed, 842 km,\n  Diameter `24, 36` = INCHES on a Turkish line, BOTAŞ, 1986, Malkoçlar→Ankara): this is most likely the\n  Turkish end of the Trans-Balkan / West line, which lost its Russian supply when TurkStream took the\n  flows in 2020. Ask the duplicate question FIRST: is it the same pipe as the Turkish onshore of Blue\n  Stream (Samsun–Ankara) or of TurkStream (Kıyıköy–Lüleburgaz/Malkoçlar)? File on documents.\n  `mothballed` vs reused-for-TurkStream needs a dated BOTAŞ/EPDK source. Inches = a `spec` note.\n- **P0769 Yamal–Europe** (idle, 1660 km Torzhok→Frankfurt/Oder, 33 bcm/y, Owner1 EuRoPol Gaz 100%,\n  Operator \"Gazprom, EuRoPol Gaz, Gascade\"):\n  - Status: Polish sanctions on EuRoPol GAZ (2022-04) and zero eastbound flow since 2022-05; reverse\n    westward→eastward flows to Poland. Word `idle` vs `mothballed` from a dated source.\n  - Scope: the row spans Russia + Belarus + Poland, but Owner1 = EuRoPol (Polish leg only). File\n    `attribution` if the owner covers one leg only.\n- **P0760 South Stream** (cancelled 2014, 2380 km, 63 bcm/y, Owner South Stream BV): confirm the\n  cancellation date and source. Do NOT count the cancellation against the TurkStream rows. TurkStream\n  reused the South Stream offshore works, which is a `cross_row_leads` note only.\n- **P2426 Pisarevka–Anapa** (880 km, `700-1400`, 63 bcm/y, 2016): 63 bcm/y is SOUTH STREAM's design\n  figure, the Южный коридор aggregate. The Cyrillic name mixes «Южно-Европейский газопровод» with\n  «Южный поток». Which corridor is this row (western route Pisarevka–Russkaya)? File `spec` on the\n  capacity; `700-1400` uses a hyphen, not the sheet's comma convention (note it).\n- **P0736 Blue Stream** (Izobilny→Ankara 1213 km, 16 bcm/y, 2003, Owner1 Gazprom 50%): did Eni sell its\n  50% (HF/NF unclear)? Dated Eni/Gazprom source. Russian onshore = Gazprom 100%, Turkish onshore = BOTAŞ:\n  `attribution` note if the row mixes them.\n- **P1472/P5875 North Caucasus–Transcaucasia**: P1472 Tbilisi–Yerevan lies wholly in Georgia/Armenia\n  (Owner blank, no length, `500, 700, 1200, 1400`, 12 bcm/y, 1988). P5875 Mozdok–Tbilisi (271 km, 720 mm,\n  1965, Gazprom). Keep the tracker's existing country/area and segment conventions. Flag, never\n  re-scope. `Tiblisi` is a typo (vocab note).\n- **P0744 Dzuarikau–Tskhinvali** (162.3 km, 426 mm, 0.25 bcm/y, 2009): EndState `Republic of South Ossetia`.\n  Keep the tracker's existing country/area convention and do not re-label. Flag nothing political.\n- **P0751 Hajigabul–Shirvanovka–Mozdok** (680 km, 1220 mm, 10 bcm/y, 1982, Owner SOCAR): flows have\n  reversed repeatedly (Russia↔Azerbaijan). The status review needs a dated post-2023 flow source.\n  Russian-side ownership (Gazprom) vs SOCAR: `attribution` only on documents.\n- **P3714 Vladimir Filanovsky** (offshore Caspian → Budyonnovsk, 114 km, Diameter `28.00` = inches,\n  2016, `gathering`, LUKOIL): NF documented gathering (associated gas to the Budyonnovsk GPP, cyberleninka\n  article). Classification is flag-only. Diameter is inches on a Russia row, so find the mm figure; if\n  a document states it, stage a Diameter fill (medium) with a `spec` concern. Never guess a conversion.\n  StartLocation is blank (free fill: field / platform name).\n- **P2380/P2379 Moscow ring (КГМО) and Ring–Belousovo**: 90 bcm/y on a 365 km DN800 ring is a SYSTEM\n  number (NF: \"capacity needs to be confirmed\"). File `spec`. Segment vs network: КГМО-1 vs КГМО-2\n  (which loop is this row; does it overlap P2285/P2366 at Belousovo?) — concern only on documents.\n- **P1475 Maykop–Samurskaya–Sochi**: Diameter 700 is not a standard size (720?); find the mm figure\n  or flag.\n- **Regional gasification отводы** (P3971, P3972, P3973, P3974, P4012, P4013, P4130, P4131, P4132,\n  P4142, P4143, P4144, P3996–P3998). All recorded `distribution`.\n  - **Classification rule:** a `газопровод-отвод` terminating AT a ГРС is transmission; `межпоселковый`\n    downstream of a ГРС is distribution. File `classification` row by row. **Flag, never\n    reclassify.**\n  - **STATUS FIRST**: R6 found three stale in-dev statuses. Targets here:\n    - P4144 start 2024;\n    - P4013 construction 2022;\n    - P4142/P4143 construction 2023;\n    - P3971 construction 2023;\n    - P4130 already `construction`;\n    - P4132 already `operating` with no Start.\n  - **Unit checks:**\n    - P3973 CapacityUnits `mill.Sm3/day` is off-vocabulary (× 0.365 → bcm/y; flag).\n    - P3973 0.61 on a DN100 line looks too high (unit?).\n    - P3972's multi-diameter `530, 325, 219, 159, 108` looks like a network of branches.\n  - P4012 is a capacity RECONSTRUCTION of an existing Gorky–Cherepovets segment (NF: \"capacity\n    expansion only\"), so `LengthKnown = 0` / blank Diameter is the expansion convention. Flag, don't\n    change.\n- **P2296 Sokhranovka–Oktyabrskaya** (1420 mm, 28 bcm/y, 2006): per-line capacity vs a corridor figure.\n\nAGGREGATE-VS-SEGMENT: a system figure is never a ref for a string row. Flag it, cite the system document\nas such, and say which rows share it. Per string, bcm/y: DN1420 ~26–33, DN1220 ~15–20, DN1020 ~8–12,\nDN720 ~3–5, DN530 ~1.5–2.5, DN325 ~0.3–0.8. Far above = a system number (P2380 90, P2426 63, P3483×3 40).\n\nSTATUS REVIEW: one record per row, all 49.\n- **Operating line**: `confirm` needs a source DATED LATER THAN 2023-08 naming the line (operator\n  page/news, a repair or diagnostics item, a tariff order, an accident report, a regional gasification\n  report, a flow statistic). Say which source and its date. Absence of news about an old trunk is not\n  evidence, so never `stale` an operating row.\n- **Export lines**: name the dated flow fact (TurkStream is the only southern route to Europe since\n  Ukraine transit stopped on 2025-01-01; Yamal–Europe has carried no eastbound flow since 2022-05).\n- **In-development rows**:\n  - built → `change`, with the date;\n  - a dated newer target → stage it;\n  - no progress evidence since the last target → `stale` with `shelved`, `ShelvedCancelledType =\n    inferred`, and no URL for the inference.\n- A changed Status goes in BOTH `status_reviews[].proposed_changes` and the Status fill.\n\nSTATE CELLS: normalize nothing by fiat. `… region` vs `… Oblast`, `Reublic of Adygea` (P2339 typo) and\n`North Ossetia` variants are vocabulary notes, not findings.\n- **Blank states**: P5656, P1472, P3714, P3483/P5654/P5655, P0736/P2227 EndState. Stage a `Location\n  [ref]` fill ONLY where you already hold a source placing that terminus.\n\nVALIDITY TEXT goes in `researcher_notes` + `recommendation` (never a bare `notes` or `summary` key — the\nValidity tab reads `recommendation`). A `concern` with an empty `recommendation` fails the coverage\ncheck. Use `contested: {\"<Column>\": \"<candidate value>\"}` ONLY for a pasteable candidate value, never\nprose. `values{}` keys are real columns (`Owner1`, `StartYear1`, `ConstructionYear`, `LengthKnownKm`),\nnever ref stems (`Owner`, `Start`). `UNRESOLVED` keeps the sheet's values (candidate → `researcher_notes`).\n`check_shard_coverage.py` blocks on all three.\n\nDOCUMENTED DIVERGENCES: when ResearcherNotes explains how a value was derived (a total carried per\nstring, a calculation, an estimate), a source stating something else is a `spec` concern quoting both,\nNOT a value-changing fill. Rows with such notes here:\n- P3483/P5654/P5655 (total capacity);\n- P2366 (bcm/day × 365);\n- P3973/P3974 (converted units);\n- P3972/P3971 (\"2014 details, could be outdated\");\n- P1368 (length per project website; IJGlobal 910 km).\n\nOWNERSHIP: `Owner [ref]` is owed on most rows (it lives on the `Gas_OperatorsOwners` tab).\n- **Gazprom trunks**: one Transgaz page stating the trunks are ПАО «Газпром» property operated by the\n  subsidiary, or the Gazprom annual report, settles a family. Cite it on each row.\n- **Export rows**: cite the owner entity's own page (South Stream Transport B.V., Blue Stream Pipeline\n  Co., EuRoPol GAZ, BOTAŞ, SOCAR, LUKOIL).\n- Don't restage entities (`entity_lookup.py` first).\n- **Operator [ref]** is owed on P1470, P3483/P5654/P5655 (Gazprom Transgaz Belarus: btg.by), P4012\n  (Transgaz Ukhta) and P0769.\n\nUNITS: km, mm, bcm/y (`млн куб. м в сутки` × 0.365; `тыс. м³/ч` × 8.76 / 1000).\nRussia rows are mm, so an inch figure (24, 28, 36) is a unit error (flag it). Multi-value `720, 1020` = two sizes.\n`*CostUnits` = bare currency code. Vocabulary lowercase; only `FIDStatus` capitalized.\n\nRULES THAT BITE (the contract has the rest):\n- No GEM cites. abarrelfull / theodora / yingdodo are banned.\n- Every URL goes through `scripts/url_verifier.py --name \"<Cyrillic name>\"`.\n- Only a confirmed 404/410 retires a ref. A `*.gazprom.ru` timeout, an `energybase.ru` geo-block page,\n  or a 401/403/468 is an ACCESS FAILURE: read the Wayback capture and add it ALONGSIDE, never swap.\n- These are not citations: a home page (`expert.ru/`), a category / search / map-home / tender-index\n  page, or openstreetmap.org. An inferred status change has no URL.\n- TIMEOUTS: `curl --max-time 30`; Wayback FIRST for timeout hosts; a legal mirror first for federal acts;\n  Wayback via CDX, one call per URL (`http://web.archive.org/cdx/search/cdx?url=<url>&limit=5&fl=\n  timestamp,statuscode`); a 429 / empty body = rate limit, retry later, not a missing capture.\n\nMEASURED CONDITIONS (2026-09-22, this machine, US IP):\n- **TIMEOUT** (Wayback first, cite live + capture): every `*.gazprom.ru` (moskva-tr, spb-tr,\n  krasnodar-tr, gazpromexport too), pravo.gov.ru, government.ru, docs.cntd.ru, aup.ru intermittently.\n- **ACCESS FAILURE codes**: kommersant.ru 500 / vedomosti.ru 502 on the home page (try article deep\n  links, else Wayback); e-disclosure.ru 403; market.neftegaz.ru 468; rg.ru / rbc.ru 401.\n- **200**: turkstream.info, botas.gov.tr (slow ~7 s), btg.by, europolgaz.com.pl, lukoil.ru / lukoil.com,\n  kavkaz-uzel.eu, sudact.ru, legalacts.ru, consultant.ru, neftegaz.ru, interfax.ru, tass.ru,\n  ru.wikipedia.org, web.archive.org.\n- energybase.ru = 200 geo-block page; vk.com = JS shell (m.vk.com / Wayback); dzen.ru = repost (cite\n  the original).\n", "groups": [["P0765", "P1368", "P0760", "P2426"], ["P0736", "P2227", "P0743", "P1475"], ["P2381", "P5665", "P2339"], ["P1470", "P5551", "P5656", "P2296"], ["P1472", "P5875", "P0744", "P0751"], ["P2343", "P1477", "P3714", "P4144"], ["P3996", "P3997", "P3998"], ["P3483", "P5654", "P5655", "P0769"], ["P2380", "P2379", "P2285", "P2366"], ["P2321", "P2433", "P2432"], ["P4130", "P4131", "P4132", "P2288"], ["P4142", "P4143"], ["P3971", "P3972"], ["P3973", "P3974", "P4012", "P4013"]]}
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
