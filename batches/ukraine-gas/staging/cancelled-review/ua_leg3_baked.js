export const meta = {
  name: 'ua-gas-cancelled-review',
  description: 'Critical re-audit of an in-scope pipeline set: confirm each data point against independent sources and flag phantom / duplicate / misclassified / mis-attributed entries (existence+classification first). One skeptical subagent per pipeline; read-and-stage only, never auto-applies.',
  phases: [
    { title: 'Audit', detail: 'one subagent per pipeline — existence+classification, then attribution+spec' },
  ],
}

// args (from `python scripts/build_deepsweep_args.py --staging <dir>`):
//   { repo, staging, commodity, country, pids:[...], roster:[...], status_review?: true }
// status_review: true = annual-update mode — each subagent ALSO stages a per-segment-row
// status verdict (confirm / change / stale / unclear) as `status_reviews` in its shard.
// tolerate a JSON-encoded string (some invocation paths stringify `args`)
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/ukraine-gas/staging/cancelled-review", "commodity": "gas", "country": "Ukraine", "pids": ["P0761", "P0788", "P0793", "P1457", "P1487", "P1773"], "roster": ["P0761 | Soyuz Gas Pipeline | Orenburg->? | len=2750.0 dia=1420.00 cap=25.2 | status=mothballed | updated=2024-08-23", "P0788 | Ostrogozhsk-Shebelinka Gas Pipeline | Ostrogozhsk->Kharkiv | len=312.0 dia=40 cap=22.5 | status=mothballed | updated=2023-09-11", "P0793 | Stavropol-Moscow Gas Pipeline | Stavropol->? | len=1262.0 dia=? cap=? | status=retired | updated=2022-08-04", "P1457 | Taganrog-Mariupol-Berdyansk Gas Pipeline | Taganrog->Zaporizhzhia Oblast | len=516.0 dia=1000 cap=? | status=retired | updated=2023-09-11", "P1487 | Poland-Ukraine Interconnector Gas Pipeline | Hermanowice->? | len=110.0 dia=700, 1000 cap=8.0 | status=cancelled | updated=2025-10-08", "P1773 | Romania-Ukraine Interconnector | Khotyn->Bukovina | len=30.0 dia=27.60 cap=7.7 | status=cancelled | updated=2025-05-29"], "status_review": true, "extra_brief": "UKRAINE GAS — read this before you search. It is the difference between a real result and a wasted pass.\n\n### 1. Search in Ukrainian AND Russian, and expect the sheet's transliteration to be the WRONG spelling\nThe sheet uses Soviet/Russian-era transliterations. English-only search will find almost nothing.\nKiev = Київ / Kyiv; Dikanka/Dykanka = Диканька; Efremovka = Єфремівка / Ефремовка; Ananjiv / Anan'iv =\nАнаньїв; Bohorodchany = Богородчани; Komarno = Комарно; Drozdovychi = Дроздовичі; Bilche-Wolitz =\nБільче-Волиця; Dolyna = Долина; Novopskov = Новопсков; Shebelinka = Шебелинка; Slovyansk = Слов'янськ;\nKremenchuk = Кременчук; Uzhhorod/Uzhgorod = Ужгород; Velke Kapusany = Veľké Kapušany (Slovak);\nVojany = Vojany (Slovak); Hust = Хуст; Rozdilna = Роздільна; Izmail = Ізмаїл; Kryvyi Rih = Кривий Ріг.\nTry «газопровід <name>» (uk) and «газопровод <name>» (ru) and the DN/Ду diameter form («Ду 1220»).\n\n### 2. Operatorship and ownership — this is the single most likely error class in the country\n- Ukraine's transmission system is STATE-owned. Since 1 Jan 2020 the operator is the\n  **Gas TSO of Ukraine / Оператор газотранспортної системи України (TSOU, tsoua.com)**; the assets are\n  held by **MGU / ТОВ «Оператор ГТС України»** structures, NOT by Naftogaz's old **Ukrtransgaz**\n  (which operated it until 2019 — a pre-2020 source naming Ukrtransgaz is not evidence about today).\n- **Gazprom does not own any Ukrainian section.** A row lying wholly inside Ukraine that records\n  `Gazprom PJSC` as owner (or 100% owner) is an ATTRIBUTION concern — say so explicitly. On genuinely\n  cross-border rows the correct reading is a split: the Russian/Belarusian section is Gazprom's, the\n  Ukrainian section is the Ukrainian state's. Establish this ONCE and apply it consistently.\n- Operator/Owner refs belong on the operators/owners tab: put them in `fills[]` with\n  `\"tab\": \"operators_owners\"`.\n\n### 3. Russian transit ended 1 January 2025 — and that is NOT a reason to change `Status`\nThe 2020–2024 Gazprom–Naftogaz transit contract expired unrenewed on 1 Jan 2025; the Sokhranivka\nentry point was shut 11 May 2022, leaving Sudzha the sole entry until the end. So Russian gas transit\nthrough Ukraine has ceased.\nBUT: Ukraine's GTS keeps operating — domestic transmission, storage cycling, and reverse-flow imports\nfrom Poland, Hungary, Slovakia, Romania and Moldova. `Status = operating` describes the physical asset\nin service. **Do NOT propose retiring/mothballing a line merely because transit stopped.** What IS\nreportable: the cessation itself (ResearcherNotes), and the gap between *technical* and *utilised*\ncapacity. If you believe a specific line is genuinely out of service, you need dated evidence about\nTHAT line, not about transit in general.\n\n### 4. Occupied territory — count Russian state media as ONE origin, never two\nP1488, P1457, P5989, P7817 and P7818 concern Donetsk / Luhansk / Zaporizhzhia and the Russian-built\nTaganrog–Mariupol–Berdyansk rebuild. The only reporting is Russian state or occupation-administration\noutput (TASS, RIA, Gazprom releases, DAN, regional occupation press). Those outlets reprint one\nannouncement: **two of them agreeing is ONE source, tier medium at best**, and you must say so.\nUkrainian/Western reporting on the same asset (Reuters, Ukrainian ministry, ISW, energy trade press)\nis what makes a second independent origin.\n\n### 5. Ukraine is the most citation-poor country in the tracker so far — 34 of 1,034 `[ref]` cells\nAn `UNRESOLVED` here is a WEAK result, not the correct outcome (the opposite of Kazakhstan/Pakistan).\nThe values are largely right; what is missing is sourcing. Push for a real citation on every unit.\nWhere the sheet already cites something, note that three cells cite `drive.google.com` links —\nthose are not public citations; flag them and find a public source instead of reusing them.\n\n### 6. Source ladder (work down it, don't start with a generic web search)\n1. **Gas TSO of Ukraine (tsoua.com)** — technical capacity documents, network maps, annual reports,\n   the ten-year network development plan (План розвитку ГТС). Best single source for length,\n   diameter, capacity and CS locations.\n2. **ENTSOG** — the Transparency Platform and the ENTSOG/GIE System Capacity Map 2026 (a copy is in\n   this repo at `sources/entsog/`, PDF + traced vectors; its `size_class` gives DN900+ /\n   DN600–900 / <DN600 which corroborates diameter class). Ukraine IS on the map.\n3. **Energy Community Secretariat** (energy-community.org) — Ukraine is a Contracting Party; its\n   reports carry GTS technical detail.\n4. **Counterpart TSOs for the interconnectors**: eustream (SK), Gaz-System (PL), Transgaz (RO),\n   FGSZ (HU), Moldovatransgaz / Vestmoldtransgaz (MD).\n5. **Ukrainian official**: zakon.rada.gov.ua, mev.gov.ua (Ministry of Energy), NEURC/НКРЕКП decisions.\n6. **Soviet-era engineering literature** for 1950s–1980s build facts (year, diameter, route) — often\n   the only source for the older trunks; cite the digitised document, never a wiki mirror.\n7. Trade press: Interfax-Ukraine, ExPro Consulting, Naftogaz/Ukrtransgaz archived releases.\n\n### 7. A metric-origin number stored in an imperial unit with false precision is a REAL flag\nThree rows carry machine round-trips, not source values: P1465 `Diameter = 20.87 in` (= 530 mm),\nP1773 `27.60 in` (= 700 mm), P3063 `Capacity = 7062.93 MMcf/d` (= 200 mcm/d). If your row is one of\nthese, report the underlying metric figure the sources actually state and flag the unit provenance\nas `concern_type=\"spec\"`. Also check P1454's `Diameter = 1200, 2350` — 2350 mm is not a pipeline\ndiameter and is very likely a typo.\n\n### 8. Duplicate hunting is high-yield here — check these families against your roster\nNear-identical names and split trunks: P0777 vs P1480 (both \"Kyiv–Western Border\", 1112 km vs\n399.9 km); P3381 vs P3382 (both \"Shebelinka–Slovyansk\"); P3484 vs P5938 (Ivatsevichy-Kobryn-Dolyna\nI and II — two threads may be legitimate, like other Soviet multi-thread trunks); P0775 vs P0776\n(Yelets-Kursk-Dykanka 298 km vs Yelets-Kursk-Kyiv 297 km, both 1220 mm); the **Dikanka family**\n(P1452 / P1453 / P1454 / P1460); the **Izmail corridor** (P0784 / P0786 / P0787); the **Uzhhorod exit**\n(P0780 / P1489 / P3063); the **Dolyna hub** (P1462 / P1463 / P3484 / P5938 / P0779). Name the other\nPID when you flag one. Do not try to resolve a cluster yourself — flag it; a separate cluster-level\nadjudication pass follows.\nAlso sanity-check P0784: 164 km is implausible for endpoints spanning Shebelinka to Izmail.\n", "model": "sonnet"}
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
const ROSTER = (A.roster || []).join("\n")
const STATUS_REVIEW = !!A.status_review
// optional scope-specific guidance (e.g. China: research in Chinese, geo-blocked-site
// workarounds) appended verbatim to every subagent contract
const EXTRA = A.extra_brief ? `\n\n## Scope-specific guidance (from the orchestrator)\n${A.extra_brief}` : ''

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

const contract = (pid) => `You are a meticulous, skeptical GEM pipeline researcher. Critically RE-AUDIT one ${COUNTRY}
${COMMODITY} pipeline: ProjectID ${pid}. This is a deep-sweep validity pass — your job is to CONFIRM the
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

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, or A Barrel Full /
   abarrelfull.wikidot.com / any wikidot.com page. Read for leads only. url_verifier rejects them.
2. NEVER fabricate a URL. If you cannot verify, say so in researcher_notes — no invented links.
3. Run EVERY url through the verifier before you cite it:
   \`python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"]\` → cite only if it
   prints OK/200 AND contains the expected token(s). Use distinctive tokens (numbers, place names).
4. Corroborate with >=2 INDEPENDENT sources (separate origins; not one wire story reprinted, not two
   pages both tracing to GEM). tier: high = >=2 independent working+value-present; medium = 1 strong;
   low = 1 weak/partial/conflicting. Search in the country's languages too where English is thin.

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
Also DEEP-FILL genuinely blank value fields with a paired, verified ref (best-effort; do not force a
number on weak fields like Capacity — leave blank rather than fabricate).${statusInstr}${EXTRA}

A pipeline that is real and correctly classified but has a lesser caveat → verdict="confirmed (caveat)".
Only open existence/duplicate/classification doubt → verdict="concern".

## Output — write a shard, then return a summary
Write \`${STAGING}/rows/${pid}.json\` = a single JSON object EXACTLY shaped like:
{
  "project_id": "${pid}",
  "pipeline_name": "<from worklist>",
  "sheet_row": <int from worklist>,
  "wiki": "<gem.wiki url from worklist>",
  "validity": [
    { "segment_name": "<or empty>", "verdict": "confirmed (caveat)|concern",
      "concern_type": "existence|duplicate|classification|attribution|spec|none",
      "recommendation": "<short human next step, e.g. 'reclassify as NGL' / 'merge into P####' / 'verify endpoint'>",
      "researcher_notes": "<the full finding — what you checked, what the sheet's own sources say, what independent sources say vs GEM, your reasoning>",
      "proposed_refs": ["https://...verified..."], "tier": "high|medium|low",
      "independent": true, "source_language": "en" }
  ],
  "fills": [
    { "segment_name": "<or empty>", "sheet_row": <int>, "ref_col": "Capacity [ref]",
      "value_cols": ["Capacity"], "primary_value_col": "Capacity", "values": {"Capacity": "<val>"},
      "primary_value": "<val>", "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
      "class_out": "REFS_ADDED|UNRESOLVED", "tier": "high|medium|low", "independent": true,
      "source_language": "en", "researcher_notes": "<why this value / source>" }
  ],
  "summary": "<one line>"
}
Emit at least one validity object per pipeline (use verdict="confirmed (caveat)", concern_type="none"
if you found nothing wrong, summarizing what you confirmed).${STATUS_REVIEW ? ' In annual-update mode also emit\nat least one status_reviews object per segment row (shaped as specified above).' : ''} validity[].proposed_refs and all
fills[].proposed_refs must have passed url_verifier. Before finishing, run
\`python -c "import json; json.load(open('${STAGING}/rows/${pid}.json'))"\` to confirm it parses.
Return ONLY a 2-line summary: the verdict/concern_types you staged, and any UNRESOLVED. Your shard
file is the deliverable, not your message.`

phase('Audit')
log(`Critically auditing ${PIDS.length} ${COUNTRY} ${COMMODITY} pipelines (existence+classification first), one subagent each.`)
const results = await parallel(PIDS.map(pid => () =>
  agent(contract(pid), { label: `audit:${pid}`, phase: 'Audit', agentType: 'general-purpose', model: MODEL })
))
const done = results.filter(Boolean).length
log(`Audit complete: ${done}/${PIDS.length} subagents returned. Shards in ${STAGING}/rows/`)
return { audited: done, total: PIDS.length }
