SCOPE: RUSSIA gas, batch R7 of 8 — CENTRAL + SOUTHERN + NORTH CAUCASUS FEDERAL DISTRICTS (Moscow ring,
Tver/Smolensk/Bryansk/Kaluga/Tula/Voronezh/Ryazan/Yaroslavl/Ivanovo, Rostov, Krasnodar, Adygea, Astrakhan,
Stavropol, Dagestan, North Ossetia, Chechnya) plus the EXPORT TRUNKS that start here (TurkStream, Blue
Stream, South Stream, Yamal–Europe, Torzhok–Minsk–Ivatsevichy, North Caucasus–Transcaucasia,
Hajigabul–Mozdok, Russia–Turkey West line). **LEAN PASS** (your contract's LEAN PASS section
binds). The regional pass ends here. 49 rows / 408 owed units: 32 `operating`, 13 `proposed`,
1 `construction` (P4130), 1 `cancelled` (P0760), 1 `idle` (P0769), 1 `mothballed` (P2227). Mostly NF 2023.
Status review is on for every row.
Background: `docs/country_notes/russia.md` (do not re-read other batches).

CALIBRATION. **44 of 49 rows carry no `[ref]` on any researched column**, so nearly every unit is
`MISSING_REF` (385). Apply rule 4(e) end to end: the value is on the sheet, so find the document that
states it and stage `REFS_ADDED` with the SAME value. A source within rounding IS a ref (note the
discrepancy). `UNRESOLVED` means nothing was found, and the record says what you searched. The 23
`HAS_REF` units the script could not clear:
- **P0743 DLS**: 7 cells cite energybase (geo-block page) + gazprom.ru/projects/dls (timeout). Read the
  Wayback captures and add them ALONGSIDE. SegmentCost on kommersant.ru/doc/1655365 (value 31.5 bn not
  found; re-read for «31,5 млрд руб.»).
- **P4012**: sudact 816-р annex 4_1 (Capacity not found); archive.org item + yarregion PDF and
  gazprommap.ru/yaroslavskaya (value present, name not found). Re-read for the Cyrillic segment name.
- **P0751**: IEA Azerbaijan profile + fief.ru (name not found).
- **P1475**: `expert.ru/` is a HOME PAGE (not a citation; replace it); kavkaz-uzel, vtg Wayback, krasnodar-tr.
- **P0769**: isans.org Belarus PDF (name not found; re-read p.34 for «Ямал — Европа»).

Blank cells (Pressure, SegmentCost, Construction, Proposal, FuelSource, Operator, Capacity, Length,
Diameter, StartYear1) are DEFERRED. Stage one only if a page you already opened states it (free fill).
Harvested pool: 435 citations over 49 gem.wiki pages. Open yours first, then go to the operator.

WHERE THE VALUES LIVE. For an operating trunk the operator's own site (`about/history`, `about/today`,
per-ЛПУМГ pages: diameter, length in zone, commissioning year) + its newspaper/anniversary PDFs answer
six columns at once. ALL `*.gazprom.ru` hosts connect-time-out from here (verified 2026-09-22: moskva-tr, spb-tr,
krasnodar-tr, gazpromexport). Go to Wayback FIRST and cite live + capture. Operator by region (VERIFY
per row — never assume; a regional boundary does not settle which subsidiary runs a trunk):
- **Gazprom Transgaz Moscow** `moskva-tr.gazprom.ru`: Moscow ring КГМО (P2380, P2379), Serpukhov end of
  Krasnodar–Serpukhov (P1470/P5551), Kasimov UGS–Voskresensk (P2321), Belousovo (P2285/P2366/P2379),
  Tula–Torzhok (P2433), Bryansk–Smolensk (P2288), Petrovsk–Elets (P5656), and possibly the Smolensk
  отводы (P4130–P4132).
- **Gazprom Transgaz Saint Petersburg** `spb-tr.gazprom.ru`: Torzhok hub (P2432 Torzhok–Valdai, the
  Torzhok end of P0769/P3483), Belousovo–Leningrad (P2285), and the Tver отводы (P4142/P4143).
- **Gazprom Transgaz Krasnodar** `krasnodar-tr.gazprom.ru`: DLS (P0743), Maykop–Samurskaya–Sochi (P1475),
  Rostov–Maykop (P2381/P5665), Maykop–Nevinnomyssk (P2339), Pisarevka–Anapa (P2426), the Krasnodar end
  of P1470/P5551, and the TurkStream/Blue Stream onshore КС «Русская» / «Береговая».
- **Gazprom Transgaz Stavropol** `stavropol-tr.gazprom.ru`: Mozdok–Nevinnomyssk (P2343), Izobilny (Blue
  Stream start), Zaterechny (P3996–P3998), Chechnya (P4144), Dzuarikau–Tskhinvali (P0744), Mozdok
  (P0751, P5875).
- **Gazprom Transgaz Makhachkala** `makhachkala-tr.gazprom.ru`: Kumli–Aksai (P1477).
- **Gazprom Transgaz Volgograd** `volgograd-tr.gazprom.ru`: Sokhranovka–Oktyabrskaya (P2296), the
  Astrakhan отводы (P3971/P3972).
- **Gazprom Transgaz Nizhny Novgorod** `nn-tr.gazprom.ru`: Ivanovo отводы (P3973/P3974).
- **Gazprom Transgaz Ukhta** `ukhta-tr.gazprom.ru`: Gorky–Cherepovets / Burmakino–Rybinsk (P4012; the
  owners tab already names it as Operator) and possibly Borok–Breytovo (P4013).
- **Export/foreign**: TurkStream offshore = South Stream Transport B.V. `turkstream.info`; Blue Stream
  offshore = Blue Stream Pipeline Co. B.V. (Gazprom/Eni); Turkish onshore = BOTAŞ `botas.gov.tr`;
  Yamal–Europe Poland = EuRoPol GAZ `europolgaz.com.pl`; Belarus + Torzhok–Minsk–Ivatsevichy = Gazprom
  Transgaz Belarus `btg.by`; Georgia = GOGC, Armenia = Gazprom Armenia, Azerbaijan = SOCAR.
- **P3714 Vladimir Filanovsky = LUKOIL** (`lukoil.ru`/`.com`, Nizhnevolzhskneft), NOT Gazprom.
- Regional gasification programmes are the primary for every proposed/construction отвод:
  `Программа развития газоснабжения и газификации <региона> на 2021–2025` (Astrakhan,
  Ivanovo, Tver, Smolensk, Yaroslavl, Stavropol, Chechnya) and the 2026–2030
  successors (regional portals; gazprommap.ru). gazprommap is Gazprom-side: ONE source,
  never the second source for a Gazprom page.

Second-source classes INDEPENDENT of the operator:
- **Federal planning scheme** `Распоряжение Правительства РФ от 06.05.2015 N 816-р` + the 2024 amendment
  3302-р (sudact.ru / legalacts.ru / consultant.ru). Cite by number + date; a planned figure is
  `medium`, with the vintage stated.
- Minenergo's Генеральная схема; FAS tariff orders; Glavgosexpertiza.
- Regional government press services (the region's `.ru` / `.gov.ru` portal).
- **Trade press** with its own reporting (neftegaz, interfax, tass, kommersant, kavkaz-uzel); for
  export lines IEA / OIES, Reuters, Anadolu, EPDK, ENTSOG and the foreign regulators.
- ru.wikipedia = ONE secondary source; cite its footnoted primary.

INDEPENDENCE: ONE origin = Transgaz + Gazprom PJSC; turkstream.info + gazprom.ru; two outlets on one
press-service text; energybase restating the operator. TWO = Transgaz + decree / FAS / regional
programme / foreign regulator / trade press with its own reporting.

SEARCH IN RUSSIAN. Use `OtherLanguagePrimaryPipelineName` verbatim as `--name` where it is filled.
For the blanks:
- **Trunks:** P2339 `Майкоп — Невинномысск`; P2343 `Моздок — Невинномысск`; P2366 `Острогожск —
  Белоусово`; P2379 `КГМО — Белоусово`; P2381/P5665 `Ростов — Майкоп` (нитки I/II); P5551 `Краснодарский
  край — Серпухов, II нитка`; P2432 `Торжок — Валдай`; P2433 `Тула — Торжок`; P5875 `Моздок — Тбилиси`
  and P1472 `Тбилиси — Ереван` (both «Северный Кавказ — Закавказье»); P0751 `Гаджигабул — Моздок`
  (Azeri: Hacıqabul–Şirvanovka).
- **Export lines:** P0760 `Южный поток`; P0765/P1368 `Турецкий поток` (нитка 1/2); P2227 = the Turkish
  section of the Трансбалканский газопровод (BOTAŞ «Batı Hattı», Malkoçlar–Ankara).
- **LUKOIL:** P3714 `газопровод с месторождения им. В. Филановского` (ЛУКОЙЛ-Нижневолжскнефть →
  Будённовск).
- **Отводы:** P3971 `Замьяны — Бугринское` (КС Замьяны); P3972 `Харабали — Ахтубинск`; P3973 `Пучеж —
  Юрьевец`; P3974 `Палех — Лух`; P4013 `Борок — Брейтово`; P4142 `Ржев — Оленино — Западная Двина`;
  P4144 `Алхазурово — Шатой`; P3996/P3997 `ГРС Затеречная` / `АГРС`; P3998 `Затеречный —
  Величаевское`; P4130 `Стомино — Никитенки` (the Cyrillic segment name says д. Никитино — check which).

TRAPS (the researcher's leads, NOT verified). Settle each with documents, never by merging or blanking.
- **Copied figures on paired rows (strings/segments).** For each pair, find whether the figure belongs to
  one string, the other, or the corridor. A sibling's figure is never a second source, and a system
  figure on a string row is a `spec` concern (see AGGREGATE-VS-SEGMENT).
  - **P0765/P1368 TurkStream 1/2**: both 930 km, 813 mm, 15.75 bcm/y, 2020. 930 km is the OFFSHORE
    length per string, and 15.75 = 31.5/2 is the per-string design, so these may be right. Confirm
    against turkstream.info. Owner1 = Gazprom PJSC 100%: the offshore owner is South Stream Transport
    B.V. (a Gazprom subsidiary), and the Turkish onshore of string 2 runs to the Bulgarian border
    (BOTAŞ). `attribution` only on documents. P0765 ends Lüleburgaz, P1368 ends Malkoçlar: check each
    landfall/terminus.
  - **P1470/P5551 Krasnodar Krai–Serpukhov I/II**: both 1177 km and Start 1961 at 1020 / 820 mm. NF 2022:
    "seems to be of 2 strings … data is limited" (olginskaya-aksay PDF). Is 1177 km per string, and
    did both open in 1961? P1470 Operator = `Gazprom PJSC` (a Transgaz subsidiary is the usual operator:
    flag, don't restage).
  - **P2381/P5665 Rostov–Maykop I/II**: StartState `Yaroslavl Oblast` on BOTH, an obvious error for
    Rostov Oblast. Stage a `Location [ref]` fill only with a source placing the Rostov terminus. No
    length; capacities 3.10 vs 4.10 bcm/y. NF cites government.ru/docs/all/101903 (government.ru times
    out: use Wayback).
  - **P3483/P5654/P5655 Torzhok–Minsk–Ivatsevichy I/II/III**: all 851 km, 1220 mm, 40 bcm/y. NF
    DOCUMENTED "the capacity number is total for the pipeline" and "some sources report different
    length". That is a divergence: FLAG, do not overwrite. File a `spec` concern naming all three rows.
    Mostly in Belarus (`btg.by`). Source Start 1974/1978/1983 per string.
  - **P5656 Petrovsk–Elets Looping**: 16.4 bcm/y is a two-pipe system total also carried on P1466
    (R5 found this). Start/End locations and states are blank (free fill only).
  - **P3996/P3997 Zaterechny GDS** (1 km, 0.23 bcm/y / connecting segment) + P3998
    Zaterechny–Velichaevskoe. Is P3997 a real separate object or a sketch of P3996? Answer the
    `duplicate` question on documents.
  - **P4142/P4143 Rzhev–Olenino–Zapadnaya Dvina** (148.3 km) + Nikitino–Nelidovo segment (P4143's
    Cyrillic is a separate `Газопровод-отвод к г. Нелидово … ГРС «Нелидово»`). Is it a segment or its
    own отвод?
- **P2227 "Russian Federation – Turkey Natural Gas Main Transmission Line"** (mothballed, 842 km,
  Diameter `24, 36` = INCHES on a Turkish line, BOTAŞ, 1986, Malkoçlar→Ankara): this is most likely the
  Turkish end of the Trans-Balkan / West line, which lost its Russian supply when TurkStream took the
  flows in 2020. Ask the duplicate question FIRST: is it the same pipe as the Turkish onshore of Blue
  Stream (Samsun–Ankara) or of TurkStream (Kıyıköy–Lüleburgaz/Malkoçlar)? File on documents.
  `mothballed` vs reused-for-TurkStream needs a dated BOTAŞ/EPDK source. Inches = a `spec` note.
- **P0769 Yamal–Europe** (idle, 1660 km Torzhok→Frankfurt/Oder, 33 bcm/y, Owner1 EuRoPol Gaz 100%,
  Operator "Gazprom, EuRoPol Gaz, Gascade"):
  - Status: Polish sanctions on EuRoPol GAZ (2022-04) and zero eastbound flow since 2022-05; reverse
    westward→eastward flows to Poland. Word `idle` vs `mothballed` from a dated source.
  - Scope: the row spans Russia + Belarus + Poland, but Owner1 = EuRoPol (Polish leg only). File
    `attribution` if the owner covers one leg only.
- **P0760 South Stream** (cancelled 2014, 2380 km, 63 bcm/y, Owner South Stream BV): confirm the
  cancellation date and source. Do NOT count the cancellation against the TurkStream rows. TurkStream
  reused the South Stream offshore works, which is a `cross_row_leads` note only.
- **P2426 Pisarevka–Anapa** (880 km, `700-1400`, 63 bcm/y, 2016): 63 bcm/y is SOUTH STREAM's design
  figure, the Южный коридор aggregate. The Cyrillic name mixes «Южно-Европейский газопровод» with
  «Южный поток». Which corridor is this row (western route Pisarevka–Russkaya)? File `spec` on the
  capacity; `700-1400` uses a hyphen, not the sheet's comma convention (note it).
- **P0736 Blue Stream** (Izobilny→Ankara 1213 km, 16 bcm/y, 2003, Owner1 Gazprom 50%): did Eni sell its
  50% (HF/NF unclear)? Dated Eni/Gazprom source. Russian onshore = Gazprom 100%, Turkish onshore = BOTAŞ:
  `attribution` note if the row mixes them.
- **P1472/P5875 North Caucasus–Transcaucasia**: P1472 Tbilisi–Yerevan lies wholly in Georgia/Armenia
  (Owner blank, no length, `500, 700, 1200, 1400`, 12 bcm/y, 1988). P5875 Mozdok–Tbilisi (271 km, 720 mm,
  1965, Gazprom). Keep the tracker's existing country/area and segment conventions. Flag, never
  re-scope. `Tiblisi` is a typo (vocab note).
- **P0744 Dzuarikau–Tskhinvali** (162.3 km, 426 mm, 0.25 bcm/y, 2009): EndState `Republic of South Ossetia`.
  Keep the tracker's existing country/area convention and do not re-label. Flag nothing political.
- **P0751 Hajigabul–Shirvanovka–Mozdok** (680 km, 1220 mm, 10 bcm/y, 1982, Owner SOCAR): flows have
  reversed repeatedly (Russia↔Azerbaijan). The status review needs a dated post-2023 flow source.
  Russian-side ownership (Gazprom) vs SOCAR: `attribution` only on documents.
- **P3714 Vladimir Filanovsky** (offshore Caspian → Budyonnovsk, 114 km, Diameter `28.00` = inches,
  2016, `gathering`, LUKOIL): NF documented gathering (associated gas to the Budyonnovsk GPP, cyberleninka
  article). Classification is flag-only. Diameter is inches on a Russia row, so find the mm figure; if
  a document states it, stage a Diameter fill (medium) with a `spec` concern. Never guess a conversion.
  StartLocation is blank (free fill: field / platform name).
- **P2380/P2379 Moscow ring (КГМО) and Ring–Belousovo**: 90 bcm/y on a 365 km DN800 ring is a SYSTEM
  number (NF: "capacity needs to be confirmed"). File `spec`. Segment vs network: КГМО-1 vs КГМО-2
  (which loop is this row; does it overlap P2285/P2366 at Belousovo?) — concern only on documents.
- **P1475 Maykop–Samurskaya–Sochi**: Diameter 700 is not a standard size (720?); find the mm figure
  or flag.
- **Regional gasification отводы** (P3971, P3972, P3973, P3974, P4012, P4013, P4130, P4131, P4132,
  P4142, P4143, P4144, P3996–P3998). All recorded `distribution`.
  - **Classification rule:** a `газопровод-отвод` terminating AT a ГРС is transmission; `межпоселковый`
    downstream of a ГРС is distribution. File `classification` row by row. **Flag, never
    reclassify.**
  - **STATUS FIRST**: R6 found three stale in-dev statuses. Targets here:
    - P4144 start 2024;
    - P4013 construction 2022;
    - P4142/P4143 construction 2023;
    - P3971 construction 2023;
    - P4130 already `construction`;
    - P4132 already `operating` with no Start.
  - **Unit checks:**
    - P3973 CapacityUnits `mill.Sm3/day` is off-vocabulary (× 0.365 → bcm/y; flag).
    - P3973 0.61 on a DN100 line looks too high (unit?).
    - P3972's multi-diameter `530, 325, 219, 159, 108` looks like a network of branches.
  - P4012 is a capacity RECONSTRUCTION of an existing Gorky–Cherepovets segment (NF: "capacity
    expansion only"), so `LengthKnown = 0` / blank Diameter is the expansion convention. Flag, don't
    change.
- **P2296 Sokhranovka–Oktyabrskaya** (1420 mm, 28 bcm/y, 2006): per-line capacity vs a corridor figure.

AGGREGATE-VS-SEGMENT: a system figure is never a ref for a string row. Flag it, cite the system document
as such, and say which rows share it. Per string, bcm/y: DN1420 ~26–33, DN1220 ~15–20, DN1020 ~8–12,
DN720 ~3–5, DN530 ~1.5–2.5, DN325 ~0.3–0.8. Far above = a system number (P2380 90, P2426 63, P3483×3 40).

STATUS REVIEW: one record per row, all 49.
- **Operating line**: `confirm` needs a source DATED LATER THAN 2023-08 naming the line (operator
  page/news, a repair or diagnostics item, a tariff order, an accident report, a regional gasification
  report, a flow statistic). Say which source and its date. Absence of news about an old trunk is not
  evidence, so never `stale` an operating row.
- **Export lines**: name the dated flow fact (TurkStream is the only southern route to Europe since
  Ukraine transit stopped on 2025-01-01; Yamal–Europe has carried no eastbound flow since 2022-05).
- **In-development rows**:
  - built → `change`, with the date;
  - a dated newer target → stage it;
  - no progress evidence since the last target → `stale` with `shelved`, `ShelvedCancelledType =
    inferred`, and no URL for the inference.
- A changed Status goes in BOTH `status_reviews[].proposed_changes` and the Status fill.

STATE CELLS: normalize nothing by fiat. `… region` vs `… Oblast`, `Reublic of Adygea` (P2339 typo) and
`North Ossetia` variants are vocabulary notes, not findings.
- **Blank states**: P5656, P1472, P3714, P3483/P5654/P5655, P0736/P2227 EndState. Stage a `Location
  [ref]` fill ONLY where you already hold a source placing that terminus.

VALIDITY TEXT goes in `researcher_notes` + `recommendation` (never a bare `notes` or `summary` key — the
Validity tab reads `recommendation`). A `concern` with an empty `recommendation` fails the coverage
check. Use `contested: {"<Column>": "<candidate value>"}` ONLY for a pasteable candidate value, never
prose. `values{}` keys are real columns (`Owner1`, `StartYear1`, `ConstructionYear`, `LengthKnownKm`),
never ref stems (`Owner`, `Start`). `UNRESOLVED` keeps the sheet's values (candidate → `researcher_notes`).
`check_shard_coverage.py` blocks on all three.

DOCUMENTED DIVERGENCES: when ResearcherNotes explains how a value was derived (a total carried per
string, a calculation, an estimate), a source stating something else is a `spec` concern quoting both,
NOT a value-changing fill. Rows with such notes here:
- P3483/P5654/P5655 (total capacity);
- P2366 (bcm/day × 365);
- P3973/P3974 (converted units);
- P3972/P3971 ("2014 details, could be outdated");
- P1368 (length per project website; IJGlobal 910 km).

OWNERSHIP: `Owner [ref]` is owed on most rows (it lives on the `Gas_OperatorsOwners` tab).
- **Gazprom trunks**: one Transgaz page stating the trunks are ПАО «Газпром» property operated by the
  subsidiary, or the Gazprom annual report, settles a family. Cite it on each row.
- **Export rows**: cite the owner entity's own page (South Stream Transport B.V., Blue Stream Pipeline
  Co., EuRoPol GAZ, BOTAŞ, SOCAR, LUKOIL).
- Don't restage entities (`entity_lookup.py` first).
- **Operator [ref]** is owed on P1470, P3483/P5654/P5655 (Gazprom Transgaz Belarus: btg.by), P4012
  (Transgaz Ukhta) and P0769.

UNITS: km, mm, bcm/y (`млн куб. м в сутки` × 0.365; `тыс. м³/ч` × 8.76 / 1000).
Russia rows are mm, so an inch figure (24, 28, 36) is a unit error (flag it). Multi-value `720, 1020` = two sizes.
`*CostUnits` = bare currency code. Vocabulary lowercase; only `FIDStatus` capitalized.

RULES THAT BITE (the contract has the rest):
- No GEM cites. abarrelfull / theodora / yingdodo are banned.
- Every URL goes through `scripts/url_verifier.py --name "<Cyrillic name>"`.
- Only a confirmed 404/410 retires a ref. A `*.gazprom.ru` timeout, an `energybase.ru` geo-block page,
  or a 401/403/468 is an ACCESS FAILURE: read the Wayback capture and add it ALONGSIDE, never swap.
- These are not citations: a home page (`expert.ru/`), a category / search / map-home / tender-index
  page, or openstreetmap.org. An inferred status change has no URL.
- TIMEOUTS: `curl --max-time 30`; Wayback FIRST for timeout hosts; a legal mirror first for federal acts;
  Wayback via CDX, one call per URL (`http://web.archive.org/cdx/search/cdx?url=<url>&limit=5&fl=
  timestamp,statuscode`); a 429 / empty body = rate limit, retry later, not a missing capture.

MEASURED CONDITIONS (2026-09-22, this machine, US IP):
- **TIMEOUT** (Wayback first, cite live + capture): every `*.gazprom.ru` (moskva-tr, spb-tr,
  krasnodar-tr, gazpromexport too), pravo.gov.ru, government.ru, docs.cntd.ru, aup.ru intermittently.
- **ACCESS FAILURE codes**: kommersant.ru 500 / vedomosti.ru 502 on the home page (try article deep
  links, else Wayback); e-disclosure.ru 403; market.neftegaz.ru 468; rg.ru / rbc.ru 401.
- **200**: turkstream.info, botas.gov.tr (slow ~7 s), btg.by, europolgaz.com.pl, lukoil.ru / lukoil.com,
  kavkaz-uzel.eu, sudact.ru, legalacts.ru, consultant.ru, neftegaz.ru, interfax.ru, tass.ru,
  ru.wikipedia.org, web.archive.org.
- energybase.ru = 200 geo-block page; vk.com = JS shell (m.vk.com / Wayback); dzen.ru = repost (cite
  the original).
