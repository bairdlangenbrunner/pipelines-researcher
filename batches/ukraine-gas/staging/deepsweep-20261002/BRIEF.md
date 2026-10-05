SCOPE: UKRAINE gas, all 47 rows, LEAN RE-SWEEP (your contract's LEAN PASS section binds). 447 owed units:
357 `MISSING_REF`, 80 `MISSING_VALUE` (only Length, Capacity, Diameter, Start and Operator blanks are owed;
other blanks are deferred), 10 `HAS_REF` the script could not clear. Statuses: 39 operating, 2 mothballed
(P0761, P0788), 2 retired (P0793, P1457), 2 cancelled (P1487, P1773), 1 construction (P7817), 1 proposed
(P7818), plus P5989. Status review is on for every row. Background: `docs/country_notes/ukraine.md`
(read it only if a trap below needs it; do not re-read other countries).

THIS IS A RE-SWEEP. A full pass ran 2026-08-15 and was never applied to the sheet. Its records are your
FIRST LEADS, before gem.wiki and before open search:
- `batches/ukraine-gas/staging/ref-sweep-operating/staged_resolutions.json` (39 operating rows)
- `batches/ukraine-gas/staging/annual/staged_resolutions.json` (P7817, P7818)
- `batches/ukraine-gas/staging/cancelled-review/staged_resolutions.json` (P0761, P0788, P0793, P1457, P1487, P1773)
- `batches/ukraine-gas/staging/redundancy/staged_resolutions.json` (cluster rulings) and its `*_evidence.md`
  files (VTG table, Moldovatransgaz trunks, Ivatsevichy, isans Belarus PDF text).
Filter by `project_id` + `ref_col`. For a prior `REFS_ADDED`: re-run url_verifier on its URLs with `--name`,
and if they still pass and state the CURRENT sheet value, restage them (same value, `REFS_ADDED`). That is
cheap and it is the bulk of this pass. If the sheet value changed since August, judge the new value.
Spend your real search effort on the units the prior pass left `UNRESOLVED` (234 operating + 36 cancelled
+ 4 annual), and on the status review, which the prior pass never did for operating rows. A prior record
is a lead, not a ref: never restage a URL you did not verify today.

CALIBRATION. 3.3% of Ukraine's `[ref]` cells are filled. A blank here means nobody looked, not that the
fact is unknowable. The operator (GTSOU) and the Soviet design institute publish line-by-line specs.
`UNRESOLVED` must say what you searched.

WHERE THE VALUES LIVE (verify per row, never assume):
- **Gas Transmission System Operator of Ukraine (GTSOU)** `tsoua.com`: line pages, the 10-year network
  development plan (План розвитку газотранспортної системи … на 2024–2033 / 2025–2034), annual reports.
  tsoua.com returns HTTP 403 (operator firewall). That is ACCESS, not deletion. Read it through Wayback.
- **Ukrtransgaz** `utg.ua`: also 403, read via Wayback. Holds the construction chronology (year, km per
  stage) that settles clusters A and G. Ukrtransgaz is the pre-2020 transmission entity; since the 2020
  unbundling it runs storage only.
- **ВНІПІтрансгаз (VTG) "Основные объекты" table**: live URL is a real 404. Use the capture
  `https://web.archive.org/web/20220608014635/http://www.vtg.com.ua/experience/main/gts.html?lang=ru`
  (name, diameter, pressure, length, strings, countries per Soviet trunk). TRAP: the name cells carry
  rowspans. Sub-lines listed inside one cell map IN ORDER onto the data rows beneath. Check the grouping
  before you attribute a figure. Summing two lines in one block produced P0777's wrong 1,112 km.
- **Naftogaz** annual reports; **NEURC** (НКРЕКП, the energy regulator) decisions; **Energy Community**
  and **ENTSOG** capacity maps and TYNDP project sheets; **EIB / EBRD** project pages (rehabilitation
  loans name lines and km).
- Neighbors: **Eustream** (Slovakia, Velke Kapusany / Vojany), **FGSZ** (Hungary, Beregdaróc),
  **Transgaz** (Romania; PDSNT development plans, TRA-N codes), **Gaz-System** (Poland, Hermanowice),
  **Moldovatransgaz** (use the `mtg.md` mirror; `moldovatransgaz.md` fails TLS), **Gazprom Transgaz
  Belarus** `btg.by`, Gazprom subsidiaries for Russian sections (all `*.gazprom.ru` time out: Wayback).
- Trade press with its own reporting: interfax.com.ua, ExPro, Enkorr, Kosatka, Reuters, ICIS, Argus;
  uk.wikipedia / ru.wikipedia = one secondary source each (prefer their footnoted primary).

INDEPENDENCE: GTSOU + Ukrtransgaz + Naftogaz = ONE origin (one corporate family). VTG is a design
institute, a separate origin. A neighbor TSO or a regulator is independent of GTSOU.

SEARCH IN UKRAINIAN AND RUSSIAN. Use `OtherLanguagePrimaryPipelineName` verbatim as `--name` where it is
filled. Soviet trunks: Союз / «Союз»; Уренгой–Помары–Ужгород; Прогресс (Ямбург–Западная граница);
Елец–Курск–Диканька / Єлець–Курськ–Диканька; Шебелинка–Днепропетровск–Кривой Рог–Измаил; Ананьев–
Тирасполь–Измаил; Долина–Ужгород–Государственная граница; Київ–Захід України; Дашава–Київ–Брянськ–Москва.

TRAPS (the earlier pass's findings and leads; settle each with documents, never by merging or blanking):
- **Cluster A, P0777 / P1480 (Kyiv–Western Border)**: duplicate confirmed in August, length 399.90 km on
  the Ukrtransgaz chronology (183.6 km in 1970 + 216.3 km in 1972). VTG gives Київ–Захід України as 590 km
  on one string: a documented second-source tension, record it, don't resolve silently. The 367 + 506 km
  pair was withdrawn for misattribution; re-read uk.wikipedia only if it states it in its own voice.
- **Cluster G, P3484 / P5938 (Ivatsevichy–Kobryn–Dolyna I/II)**: P5938's 292 km is contradicted by VTG
  (374.1 / 394.2 km) and Ukrtransgaz (357.7 km in 1976, 366.7 km in 1977). 29 bcm/y is a system total on
  both rows. VTG shows a third string GEM does not carry (a `cross_row_leads` note, not a new row).
  The isans.org Belarus PDF on both Diameter cells did not name the line: re-read its text in
  `batches/ukraine-gas/staging/redundancy/isans_belarus_energy.txt`.
- **P3381 / P3382 Shebelinka–Slovyansk** share one geojson that is not the named corridor. Do not judge
  either length from the route. Answer the duplicate question on documents.
- **P1471 Novopskov–Aksai–Mozdok**: Novopskov is in Luhansk Oblast, Ukraine. The country columns are the
  defect (a `spec`/`attribution` concern with the contested value), not the route.
- **P1457 Taganrog–Mariupol–Berdyansk (retired)**: 516 km is the whole Rostov–Taganrog–Zhdanov system.
  Do not shorten it toward the drawn route. P7817 / P7818 are its occupation-era reconstructed segments;
  P5989 Taganrog–Melitopol–Berdyansk is a related occupation-era line. Check P5989 against P7817/P7818
  for overlap (duplicate question, documents only).
- **P1773 Romania–Ukraine (Siret–Khotyn), cancelled**: Transgaz's PDSNT 2021–2030 carries the Romanian
  side as live (146 km, €150m, TRA-N-596, 2026 estimate), conditional on the Ukrainian side. Look for a
  newer PDSNT or TYNDP 2024 entry. A status change needs a dated source on the UKRAINIAN section.
- **P1487 Poland–Ukraine Interconnector, cancelled**: Operator still names Ukrtransgaz (pre-2020 entity).
  Confirm the cancellation with a dated GTSOU or Gaz-System source.
- **P1485 Kremenchuk–Anan'iv–Bohorodchany**: a wholly Ukrainian 532 km line recorded as 100% Gazprom.
  `attribution` concern on documents (the 2020 unbundling put Ukrainian trunks under GTSOU).
- **Owner notation `[100.%]` beside a second owner** (P0768, P0776, P0761) is a convention question for
  Baird. Note it, don't restage it. On genuinely transnational Russia + Ukraine rows the pair
  "Gazprom PJSC; Gas Transmission System Operator of Ukraine" is the accepted convention, not a defect.
- **Occupied-territory operators stay `UNRESOLVED`** on P1488, P7817, P7818 (and P5989 if it applies).
  GTSOU is wrong for pipe laid by the occupying power, and naming an occupation body as "the operator"
  without qualification misstates the row. Write what is documented in `researcher_notes`.
- **P0778 Komarno–Drozdovychi**: a geocoder put the start in Komárno, Slovakia. The 80 km is right.
- P0779 refs (cyberleninka, isans.org) did not name the line: re-read for «Торжок–Минск–Ивацевичи–Долина»
  or the Belarusian / Ukrainian forms before calling them unsupported.

STATUS REVIEW: one record per row, all 47.
- Russian transit through Ukraine ended 2025-01-01 when the GTSOU–Gazprom agreement expired. A trunk that
  carried only transit (Soyuz, Progress, Urengoy–Pomary–Uzhgorod, Yelets–Kursk–Dykanka …) may still carry
  domestic or reverse flows (from Slovakia, Hungary, Poland) or storage traffic. `confirm` operating needs a
  source DATED 2024 or later that says the Ukrainian section is in use; a source saying it is idle or
  shut since 2025 supports a `change` (use the vocabulary word the source supports: `idle` vs
  `mothballed`). Russia-side sections: the Russian section of an interstate trunk may be unused while the
  Ukrainian section works. Say which section the evidence covers.
- War damage and occupation: lines in Luhansk, Donetsk, Zaporizhzhia, Kherson and Crimea. A line in an
  occupied area is not "cancelled" by occupation; state the dated evidence and stage a change only on it.
- Absence of news about an old trunk is not evidence. Never `stale` an operating row.
- In-development rows (P7817, P7818): built → `change` with the date; a dated newer target → stage it;
  no progress since the last target → `stale` per the contract.
- A changed Status goes in BOTH `status_reviews[].proposed_changes` and the Status fill.

AGGREGATE-VS-SEGMENT: a system figure is never a ref for a string row. Per string, bcm/y: DN1420 ~26–33,
DN1220 ~15–20, DN1020 ~8–12, DN720 ~3–5, DN530 ~1.5–2.5. Far above = a system number (P3484/P5938 29).

DOCUMENTED DIVERGENCES: where `ResearcherNotes` explains how a value was derived, a source stating
something else is a `spec` concern quoting both, not a value-changing fill.

OWNERSHIP: `Owner [ref]` / `Operator [ref]` live on the `Gas_OperatorsOwners` tab. One GTSOU page or annual
report listing the trunks it operates settles a family: cite it on each row it names. Run
`entity_lookup.py` before staging any owner; write owners the team's way (`entity_style.py`).

VALUE RULES (2026-10-02, they bite):
- LengthKnown and Capacity are staged in the unit the SOURCE states, with the matching units cell. A source
  saying 54 млрд м³/рік is staged as 54 bcm/y; 100 млн м³/добу is staged as 100 + `MMSCMD`. Never convert;
  a conversion goes in the note only.
- Costs in full currency units (`150000000` + `EUR`), never millions. Read column headers.
- `[ref]` cells are additive. Never propose removing an existing ref. A ref that cannot be read or does not
  state the value is a concern (`REF_UNSUPPORTED` / `REF_BLOCKED` with no `proposed_refs`), not a removal.
  Only a confirmed 404/410 is `DEAD_LINK`.
- `values{}` keys are real columns (`Owner1`, `StartYear1`, `LengthKnown`), never ref stems.
- Validity text goes in `researcher_notes` + `recommendation`. `contested` holds a pasteable value only.
- Occupied Ukraine is `Ukraine` in every country/area cell (GEM naming convention). Don't re-label.
- Notes are plain English for a person: short sentences, sources named by what they are, no repo jargon.

ACCESS CONDITIONS (this machine, US IP):
- HTTP 403 (block, not deletion): tsoua.com, utg.ua. Go to Wayback first; cite live + capture.
- TIMEOUT: every `*.gazprom.ru`, government.ru. Wayback first.
- TLS failure: moldovatransgaz.md (use mtg.md).
- FALSE PASS: energybase.ru returns 200 with an IP-block page («Доступ ограничен»). Wayback also 403s it.
  Treat it as blocked; never stage it as a working ref.
- Wayback via CDX, one call per URL (`http://web.archive.org/cdx/search/cdx?url=<url>&limit=5&fl=timestamp,statuscode`);
  a 429 or empty body = rate limit, retry later.
- `python scripts/fetch.py <url> --head 2000` is the escalation ladder for any other block.
- Not citations: home pages, search or index pages, openstreetmap.org, gem.wiki. Banned: abarrelfull,
  theodora, yingdodo.
