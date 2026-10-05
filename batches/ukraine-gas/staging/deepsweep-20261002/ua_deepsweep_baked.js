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
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/ukraine-gas/staging/deepsweep-20261002", "commodity": "gas", "country": "Ukraine", "pids": ["P0761", "P0768", "P0774", "P0775", "P0776", "P0777", "P0778", "P0779", "P0780", "P0783", "P0784", "P0786", "P0787", "P0788", "P0789", "P0790", "P0791", "P0793", "P1451", "P1452", "P1453", "P1454", "P1455", "P1457", "P1460", "P1462", "P1463", "P1465", "P1471", "P1480", "P1481", "P1483", "P1485", "P1487", "P1488", "P1489", "P1773", "P2387", "P3063", "P3381", "P3382", "P3484", "P5935", "P5938", "P5989", "P7817", "P7818"], "roster": ["P0761 | Soyuz Gas Pipeline | Orenburg->? | len=2750.0 dia=1420.00 cap=25.20 | status=mothballed | updated=2024-08-23", "P0768 | Urengoy-Pomary-Uzhgorod Gas Pipeline | Urengoy->Zakarpattia Oblast | len=4451.0 dia=1420, 1400 cap=32.00 | status=operating | updated=2023-08-09", "P0774 | Progress Gas Pipeline | Yamburg gas field->? | len=4590.7 dia=1400.00 cap=26.00 | status=operating | updated=2023-08-10", "P0775 | Yelets-Kursk-Dykanka Gas Pipeline | Yelets->Poltava Oblast | len=298.0 dia=1220 cap=65.00 | status=operating | updated=2023-09-11", "P0776 | Yelets-Kursk-Kyiv Gas Pipeline | Yelets->? | len=297.0 dia=1220 cap=45.00 | status=operating | updated=2023-09-11", "P0777 | Kyiv–Western Border Pipeline | Kyiv->? | len=1112.0 dia=1020, 1220 cap=? | status=operating | updated=2022-08-24", "P0778 | Komarno-Drozdovychi Gas Pipeline | Komarno Compressor Station->? | len=80.0 dia=800 cap=8.00 | status=operating | updated=2022-08-24", "P0779 | Torzhok-Smolensk-Mazyr-Dolyna Gas Pipeline | Torzhok->? | len=1300.0 dia=1420.00 cap=22.00 | status=operating | updated=2024-09-16", "P0780 | Uzhhorod-Berehove Gas Pipeline | Uzhgorod->? | len=? dia=? cap=13.00 | status=operating | updated=2022-08-24", "P0783 | Yelets-Kremenchuk–Kryvyi Rih Gas Pipeline | Yelets->Dnipropetrovsk Oblast | len=771.0 dia=1420 cap=95.00 | status=operating | updated=2023-09-11", "P0784 | Shebelinka-Dnipropetrovsk–Kryvyi Rih–Rozdilna-Izmail Gas Pipeline | Shebelinka->? | len=164.0 dia=1200 cap=24.00 | status=operating | updated=2022-08-24", "P0786 | Anan'iv-Tiraspol-Izmail Gas Pipeline | ?->? | len=257.0 dia=1200.00 cap=23.70 | status=operating | updated=2023-09-07", "P0787 | Rozdilna-Izmail Gas Pipeline | Rozdilna->? | len=230.0 dia=820 cap=7.30 | status=operating | updated=2023-09-07", "P0788 | Ostrogozhsk-Shebelinka Gas Pipeline | Ostrogozhsk->Kharkiv | len=312.0 dia=40 cap=22.50 | status=mothballed | updated=2023-09-11", "P0789 | Urengoy-Novopskov Gas Pipeline | Urengoy->Luhansk | len=3609.0 dia=1400 cap=31.00 | status=operating | updated=2023-07-27", "P0790 | Petrovsk-Novopskov Gas Pipeline | Petrovsk->Luhansk | len=609.0 dia=1220 cap=14.00 | status=operating | updated=2023-08-15", "P0791 | Orenburg-Novopskov Gas Pipeline | Orenburg->Luhansk | len=1230.0 dia=1220 cap=14.60 | status=operating | updated=2023-08-25", "P0793 | Stavropol-Moscow Gas Pipeline | Stavropol->? | len=1262.0 dia=? cap=? | status=retired | updated=2022-08-04", "P1451 | Hust–Satu Mare Gas Pipeline | Hust->? | len=20.6 dia=720 cap=2.00 | status=operating | updated=2022-08-25", "P1452 | Shebelinka-Poltava-Kiev Gas Pipeline | Shebelinka->? | len=454.7 dia=720 cap=? | status=operating | updated=2022-08-25", "P1453 | Efremovka-Dikanka-Kiev Gas Pipeline | Efremovka->? | len=477.0 dia=1000 cap=? | status=operating | updated=2022-08-25", "P1454 | Shebelinka-Dikanka-Kiev Gas Pipeline | Shebelinka->? | len=522.0 dia=1200, 2350 cap=? | status=operating | updated=2022-08-25", "P1455 | Tula-Shostka-Kiev Gas Pipeline | Tula->? | len=490.0 dia=1220 cap=? | status=operating | updated=2023-09-11", "P1457 | Taganrog-Mariupol-Berdyansk Gas Pipeline | Taganrog->Zaporizhzhia Oblast | len=516.0 dia=1000 cap=? | status=retired | updated=2023-09-11", "P1460 | Dikanka-Kremenchuk–Krivyi Rih Gas Pipeline | Dikanka->? | len=272.2 dia=700 cap=3.20 | status=operating | updated=2022-08-25", "P1462 | Bilche-Wolitz-Dolyna Gas Pipeline | Bliche->? | len=68.0 dia=1400 cap=? | status=operating | updated=2022-08-25", "P1463 | Bohorodchany-Dolyna Gas Pipeline | Bohorodchany->? | len=42.0 dia=1400 cap=? | status=operating | updated=2022-08-25", "P1465 | Dashava-Kiev-Bryansk-Moscow Gas Pipeline | Dashava->? | len=1301.0 dia=20.87 cap=1.80 | status=operating | updated=2023-09-12", "P1471 | Novopskov-Aksai-Mozdok Pipeline | Novopskov->? | len=878.0 dia=1200, 1220 cap=? | status=operating | updated=2022-08-02", "P1480 | Kyiv–Western Border of Ukraine Gas Pipeline | Kyiv->? | len=399.9 dia=1020, 1220 cap=? | status=operating | updated=2022-08-26", "P1481 | Ananjiv-Bohorodchani Gas Pipeline | Ananjiv->? | len=333.0 dia=1020 cap=9.10 | status=operating | updated=2023-09-07", "P1483 | Novopskov-Shebelinka Gas Pipeline | Novopskov->? | len=212.0 dia=1200 cap=14.50 | status=operating | updated=2022-08-26", "P1485 | Kremenchuk-Anan'iv-Bohorodchany Gas Pipeline | Kremenchug->? | len=532.0 dia=1020 cap=8.70 | status=operating | updated=2022-08-10", "P1487 | Poland-Ukraine Interconnector Gas Pipeline | Hermanowice->? | len=110.0 dia=700, 1000 cap=8.00 | status=cancelled | updated=2025-10-08", "P1488 | Kramatorsk-Donetsk-Mariupol Gas Pipeline | Kramatorsk->Donetsk Oblast | len=? dia=1000 cap=? | status=operating | updated=2023-09-12", "P1489 | Vojany-Uzhgorod Gas Pipeline | Vojany->? | len=? dia=700 cap=10.00 | status=operating | updated=2022-08-26", "P1773 | Romania-Ukraine Interconnector | Khotyn->Bukovina | len=30.0 dia=27.60 cap=7.70 | status=cancelled | updated=2025-05-29", "P2387 | Shebelinka-Belgorod-Kursk-Bryansk Gas Pipeline | Shebelinka->Bryansk Oblast | len=507.0 dia=1020 cap=13.00 | status=operating | updated=2023-09-11", "P3063 | Uzhgorod–Velke Kapusany Gas Pipeline | Uzhgorod->? | len=14.5 dia=1400 cap=7062.93 | status=operating | updated=2022-08-26", "P3381 | Shebelinka–Slovyansk Gas Pipeline | Shebelinka->? | len=70.0 dia=700.00 cap=? | status=operating | updated=2022-08-26", "P3382 | Shebelinka–Slovyansk Gas Pipeline | ?->? | len=54.0 dia=500.00 cap=? | status=operating | updated=2022-07-18", "P3484 | Ivatsevichy-Kobryn-Dolyna Gas Pipeline | Ivatsevichy->? | len=292.0 dia=1220.00 cap=29.00 | status=operating | updated=2024-09-16", "P5935 | Odessa-Chisinau Gas Pipeline | Odessa->? | len=44.0 dia=530 cap=1.30 | status=operating | updated=2023-09-07", "P5938 | Ivatsevichy-Kobryn-Dolyna Gas Pipeline | Ivatsevichy->? | len=292.0 dia=1220.00 cap=29.00 | status=operating | updated=2024-09-16", "P5989 | Taganrog-Melitopol-Berdyansk Gas Pipeline | Taganrog->Zaporizhzhia Oblast | len=? dia=? cap=? | status=operating | updated=2025-08-25", "P7817 | Taganrog-Mariupol-Berdyansk Gas Pipeline | Taganrog->Donetsk | len=? dia=700 cap=? | status=construction | updated=2025-10-10", "P7818 | Taganrog-Mariupol-Berdyansk Gas Pipeline | Mariupol->Zaporizhzhia | len=? dia=500 cap=? | status=proposed | updated=2025-10-10"], "status_review": true, "lean": true, "model": "sonnet", "extra_brief": "SCOPE: UKRAINE gas, all 47 rows, LEAN RE-SWEEP (your contract's LEAN PASS section binds). 447 owed units:\n357 `MISSING_REF`, 80 `MISSING_VALUE` (only Length, Capacity, Diameter, Start and Operator blanks are owed;\nother blanks are deferred), 10 `HAS_REF` the script could not clear. Statuses: 39 operating, 2 mothballed\n(P0761, P0788), 2 retired (P0793, P1457), 2 cancelled (P1487, P1773), 1 construction (P7817), 1 proposed\n(P7818), plus P5989. Status review is on for every row. Background: `docs/country_notes/ukraine.md`\n(read it only if a trap below needs it; do not re-read other countries).\n\nTHIS IS A RE-SWEEP. A full pass ran 2026-08-15 and was never applied to the sheet. Its records are your\nFIRST LEADS, before gem.wiki and before open search:\n- `batches/ukraine-gas/staging/ref-sweep-operating/staged_resolutions.json` (39 operating rows)\n- `batches/ukraine-gas/staging/annual/staged_resolutions.json` (P7817, P7818)\n- `batches/ukraine-gas/staging/cancelled-review/staged_resolutions.json` (P0761, P0788, P0793, P1457, P1487, P1773)\n- `batches/ukraine-gas/staging/redundancy/staged_resolutions.json` (cluster rulings) and its `*_evidence.md`\n  files (VTG table, Moldovatransgaz trunks, Ivatsevichy, isans Belarus PDF text).\nFilter by `project_id` + `ref_col`. For a prior `REFS_ADDED`: re-run url_verifier on its URLs with `--name`,\nand if they still pass and state the CURRENT sheet value, restage them (same value, `REFS_ADDED`). That is\ncheap and it is the bulk of this pass. If the sheet value changed since August, judge the new value.\nSpend your real search effort on the units the prior pass left `UNRESOLVED` (234 operating + 36 cancelled\n+ 4 annual), and on the status review, which the prior pass never did for operating rows. A prior record\nis a lead, not a ref: never restage a URL you did not verify today.\n\nCALIBRATION. 3.3% of Ukraine's `[ref]` cells are filled. A blank here means nobody looked, not that the\nfact is unknowable. The operator (GTSOU) and the Soviet design institute publish line-by-line specs.\n`UNRESOLVED` must say what you searched.\n\nWHERE THE VALUES LIVE (verify per row, never assume):\n- **Gas Transmission System Operator of Ukraine (GTSOU)** `tsoua.com`: line pages, the 10-year network\n  development plan (План розвитку газотранспортної системи … на 2024–2033 / 2025–2034), annual reports.\n  tsoua.com returns HTTP 403 (operator firewall). That is ACCESS, not deletion. Read it through Wayback.\n- **Ukrtransgaz** `utg.ua`: also 403, read via Wayback. Holds the construction chronology (year, km per\n  stage) that settles clusters A and G. Ukrtransgaz is the pre-2020 transmission entity; since the 2020\n  unbundling it runs storage only.\n- **ВНІПІтрансгаз (VTG) \"Основные объекты\" table**: live URL is a real 404. Use the capture\n  `https://web.archive.org/web/20220608014635/http://www.vtg.com.ua/experience/main/gts.html?lang=ru`\n  (name, diameter, pressure, length, strings, countries per Soviet trunk). TRAP: the name cells carry\n  rowspans. Sub-lines listed inside one cell map IN ORDER onto the data rows beneath. Check the grouping\n  before you attribute a figure. Summing two lines in one block produced P0777's wrong 1,112 km.\n- **Naftogaz** annual reports; **NEURC** (НКРЕКП, the energy regulator) decisions; **Energy Community**\n  and **ENTSOG** capacity maps and TYNDP project sheets; **EIB / EBRD** project pages (rehabilitation\n  loans name lines and km).\n- Neighbors: **Eustream** (Slovakia, Velke Kapusany / Vojany), **FGSZ** (Hungary, Beregdaróc),\n  **Transgaz** (Romania; PDSNT development plans, TRA-N codes), **Gaz-System** (Poland, Hermanowice),\n  **Moldovatransgaz** (use the `mtg.md` mirror; `moldovatransgaz.md` fails TLS), **Gazprom Transgaz\n  Belarus** `btg.by`, Gazprom subsidiaries for Russian sections (all `*.gazprom.ru` time out: Wayback).\n- Trade press with its own reporting: interfax.com.ua, ExPro, Enkorr, Kosatka, Reuters, ICIS, Argus;\n  uk.wikipedia / ru.wikipedia = one secondary source each (prefer their footnoted primary).\n\nINDEPENDENCE: GTSOU + Ukrtransgaz + Naftogaz = ONE origin (one corporate family). VTG is a design\ninstitute, a separate origin. A neighbor TSO or a regulator is independent of GTSOU.\n\nSEARCH IN UKRAINIAN AND RUSSIAN. Use `OtherLanguagePrimaryPipelineName` verbatim as `--name` where it is\nfilled. Soviet trunks: Союз / «Союз»; Уренгой–Помары–Ужгород; Прогресс (Ямбург–Западная граница);\nЕлец–Курск–Диканька / Єлець–Курськ–Диканька; Шебелинка–Днепропетровск–Кривой Рог–Измаил; Ананьев–\nТирасполь–Измаил; Долина–Ужгород–Государственная граница; Київ–Захід України; Дашава–Київ–Брянськ–Москва.\n\nTRAPS (the earlier pass's findings and leads; settle each with documents, never by merging or blanking):\n- **Cluster A, P0777 / P1480 (Kyiv–Western Border)**: duplicate confirmed in August, length 399.90 km on\n  the Ukrtransgaz chronology (183.6 km in 1970 + 216.3 km in 1972). VTG gives Київ–Захід України as 590 km\n  on one string: a documented second-source tension, record it, don't resolve silently. The 367 + 506 km\n  pair was withdrawn for misattribution; re-read uk.wikipedia only if it states it in its own voice.\n- **Cluster G, P3484 / P5938 (Ivatsevichy–Kobryn–Dolyna I/II)**: P5938's 292 km is contradicted by VTG\n  (374.1 / 394.2 km) and Ukrtransgaz (357.7 km in 1976, 366.7 km in 1977). 29 bcm/y is a system total on\n  both rows. VTG shows a third string GEM does not carry (a `cross_row_leads` note, not a new row).\n  The isans.org Belarus PDF on both Diameter cells did not name the line: re-read its text in\n  `batches/ukraine-gas/staging/redundancy/isans_belarus_energy.txt`.\n- **P3381 / P3382 Shebelinka–Slovyansk** share one geojson that is not the named corridor. Do not judge\n  either length from the route. Answer the duplicate question on documents.\n- **P1471 Novopskov–Aksai–Mozdok**: Novopskov is in Luhansk Oblast, Ukraine. The country columns are the\n  defect (a `spec`/`attribution` concern with the contested value), not the route.\n- **P1457 Taganrog–Mariupol–Berdyansk (retired)**: 516 km is the whole Rostov–Taganrog–Zhdanov system.\n  Do not shorten it toward the drawn route. P7817 / P7818 are its occupation-era reconstructed segments;\n  P5989 Taganrog–Melitopol–Berdyansk is a related occupation-era line. Check P5989 against P7817/P7818\n  for overlap (duplicate question, documents only).\n- **P1773 Romania–Ukraine (Siret–Khotyn), cancelled**: Transgaz's PDSNT 2021–2030 carries the Romanian\n  side as live (146 km, €150m, TRA-N-596, 2026 estimate), conditional on the Ukrainian side. Look for a\n  newer PDSNT or TYNDP 2024 entry. A status change needs a dated source on the UKRAINIAN section.\n- **P1487 Poland–Ukraine Interconnector, cancelled**: Operator still names Ukrtransgaz (pre-2020 entity).\n  Confirm the cancellation with a dated GTSOU or Gaz-System source.\n- **P1485 Kremenchuk–Anan'iv–Bohorodchany**: a wholly Ukrainian 532 km line recorded as 100% Gazprom.\n  `attribution` concern on documents (the 2020 unbundling put Ukrainian trunks under GTSOU).\n- **Owner notation `[100.%]` beside a second owner** (P0768, P0776, P0761) is a convention question for\n  Baird. Note it, don't restage it. On genuinely transnational Russia + Ukraine rows the pair\n  \"Gazprom PJSC; Gas Transmission System Operator of Ukraine\" is the accepted convention, not a defect.\n- **Occupied-territory operators stay `UNRESOLVED`** on P1488, P7817, P7818 (and P5989 if it applies).\n  GTSOU is wrong for pipe laid by the occupying power, and naming an occupation body as \"the operator\"\n  without qualification misstates the row. Write what is documented in `researcher_notes`.\n- **P0778 Komarno–Drozdovychi**: a geocoder put the start in Komárno, Slovakia. The 80 km is right.\n- P0779 refs (cyberleninka, isans.org) did not name the line: re-read for «Торжок–Минск–Ивацевичи–Долина»\n  or the Belarusian / Ukrainian forms before calling them unsupported.\n\nSTATUS REVIEW: one record per row, all 47.\n- Russian transit through Ukraine ended 2025-01-01 when the GTSOU–Gazprom agreement expired. A trunk that\n  carried only transit (Soyuz, Progress, Urengoy–Pomary–Uzhgorod, Yelets–Kursk–Dykanka …) may still carry\n  domestic or reverse flows (from Slovakia, Hungary, Poland) or storage traffic. `confirm` operating needs a\n  source DATED 2024 or later that says the Ukrainian section is in use; a source saying it is idle or\n  shut since 2025 supports a `change` (use the vocabulary word the source supports: `idle` vs\n  `mothballed`). Russia-side sections: the Russian section of an interstate trunk may be unused while the\n  Ukrainian section works. Say which section the evidence covers.\n- War damage and occupation: lines in Luhansk, Donetsk, Zaporizhzhia, Kherson and Crimea. A line in an\n  occupied area is not \"cancelled\" by occupation; state the dated evidence and stage a change only on it.\n- Absence of news about an old trunk is not evidence. Never `stale` an operating row.\n- In-development rows (P7817, P7818): built → `change` with the date; a dated newer target → stage it;\n  no progress since the last target → `stale` per the contract.\n- A changed Status goes in BOTH `status_reviews[].proposed_changes` and the Status fill.\n\nAGGREGATE-VS-SEGMENT: a system figure is never a ref for a string row. Per string, bcm/y: DN1420 ~26–33,\nDN1220 ~15–20, DN1020 ~8–12, DN720 ~3–5, DN530 ~1.5–2.5. Far above = a system number (P3484/P5938 29).\n\nDOCUMENTED DIVERGENCES: where `ResearcherNotes` explains how a value was derived, a source stating\nsomething else is a `spec` concern quoting both, not a value-changing fill.\n\nOWNERSHIP: `Owner [ref]` / `Operator [ref]` live on the `Gas_OperatorsOwners` tab. One GTSOU page or annual\nreport listing the trunks it operates settles a family: cite it on each row it names. Run\n`entity_lookup.py` before staging any owner; write owners the team's way (`entity_style.py`).\n\nVALUE RULES (2026-10-02, they bite):\n- LengthKnown and Capacity are staged in the unit the SOURCE states, with the matching units cell. A source\n  saying 54 млрд м³/рік is staged as 54 bcm/y; 100 млн м³/добу is staged as 100 + `MMSCMD`. Never convert;\n  a conversion goes in the note only.\n- Costs in full currency units (`150000000` + `EUR`), never millions. Read column headers.\n- `[ref]` cells are additive. Never propose removing an existing ref. A ref that cannot be read or does not\n  state the value is a concern (`REF_UNSUPPORTED` / `REF_BLOCKED` with no `proposed_refs`), not a removal.\n  Only a confirmed 404/410 is `DEAD_LINK`.\n- `values{}` keys are real columns (`Owner1`, `StartYear1`, `LengthKnown`), never ref stems.\n- Validity text goes in `researcher_notes` + `recommendation`. `contested` holds a pasteable value only.\n- Occupied Ukraine is `Ukraine` in every country/area cell (GEM naming convention). Don't re-label.\n- Notes are plain English for a person: short sentences, sources named by what they are, no repo jargon.\n\nACCESS CONDITIONS (this machine, US IP):\n- HTTP 403 (block, not deletion): tsoua.com, utg.ua. Go to Wayback first; cite live + capture.\n- TIMEOUT: every `*.gazprom.ru`, government.ru. Wayback first.\n- TLS failure: moldovatransgaz.md (use mtg.md).\n- FALSE PASS: energybase.ru returns 200 with an IP-block page («Доступ ограничен»). Wayback also 403s it.\n  Treat it as blocked; never stage it as a working ref.\n- Wayback via CDX, one call per URL (`http://web.archive.org/cdx/search/cdx?url=<url>&limit=5&fl=timestamp,statuscode`);\n  a 429 or empty body = rate limit, retry later.\n- `python scripts/fetch.py <url> --head 2000` is the escalation ladder for any other block.\n- Not citations: home pages, search or index pages, openstreetmap.org, gem.wiki. Banned: abarrelfull,\n  theodora, yingdodo.\n", "groups": [["P0761", "P0768", "P0774"], ["P0775", "P0776", "P0783"], ["P0777", "P1480"], ["P0784", "P0786", "P0787"], ["P1452", "P1453", "P1454"], ["P1457", "P7817", "P7818", "P5989"], ["P0789", "P0790", "P0791"], ["P1471", "P1483"], ["P3381", "P3382"], ["P0779", "P3484", "P5938"], ["P1481", "P1485"], ["P1462", "P1463"], ["P1489", "P3063"], ["P0778"], ["P0780"], ["P0788"], ["P0793"], ["P1451"], ["P1455"], ["P1460"], ["P1465"], ["P1487"], ["P1488"], ["P1773"], ["P2387"], ["P5935"]]}
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
one validated dated source makes it a change (tier medium); tier high needs >=2 independent publishers. Every URL through url_verifier. Verdict vocabulary:
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
- Second source: PREFERRED, NOT OWED. One validated ref closes the unit at medium. Add a second
  only if the document at hand or one quick search offers it; never spend searches chasing one --
  EXCEPT for a proposed status change, where a second independent source is worth one search (it is
  what makes the change high).
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
   DOWNLOADS: save any fetched file (curl -o, PDFs, pdftotext output) under \`${STAGING}/work/\`
   (gitignored) -- never the repo root or a tracked path.
4. ONE VALIDATED SOURCE IS SUFFICIENT; >=2 INDEPENDENT IS PREFERRED. A ref that passes url_verifier,
   names THIS pipeline (name_found) and states the value (within rounding) closes the unit -- no
   second-search note is owed. Independent = separate origins (not one wire story reprinted, not two
   pages both tracing to GEM). tier: high = >=1 validated ref (sufficient, done) -- EXCEPT a status
   change, which is high only on >=2 independent publishers; medium = usable with a caveat you name,
   or a status change on one publisher; low = weak/partial/conflicting. Take a second source when it
   is cheap -- the document at hand or one quick search, a different publisher and document class --
   it sets independent=true (and a status change needs it); never hold a unit open for one. Search in the country's languages too where English is thin.
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
5. SPEC — length, diameter, capacity, dates. CRITICALLY confirm each against a validated source (>=2 independent preferred).
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
UNITS: stage LengthKnown and Capacity in the unit the SOURCE states (1,750 miles -> 1750 + LengthKnownUnits=mi; 90 MMcm/d -> 90 + MMSCMD). Never convert to km or bcm/y, and keep any conversion in the note only. The same goes for contested values.
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
