export const meta = {
  name: 'country-discovery',
  description: 'Country-scoped discovery of pipelines missing from GEM: parallel search-strategy agents surface candidates (new announcements AND older never-captured lines), a consolidator dedups + matches-to-existing against the full GEM roster, then one vetting agent per surviving candidate applies the add-threshold and researches a stageable row. Read-and-stage only, never auto-applies.',
  phases: [
    { title: 'Search', detail: 'one agent per search strategy (news / regulators / operators / maps / cross-border)' },
    { title: 'Consolidate', detail: 'dedup across strategies + match-to-existing FIRST' },
    { title: 'Vet', detail: 'one agent per surviving candidate — add-threshold + full row research' },
  ],
}

// args (from `python scripts/build_discovery_context.py --tracker <t> --country <C> --staging <dir>`):
//   { repo, staging, commodity, country, roster:[...], strategies?:[{key,brief}] }
// tolerate a JSON-encoded string (some invocation paths stringify `args`)
const A = {
 "repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher",
 "staging": "batches/staging/annual-gas-iran",
 "commodity": "gas",
 "country": "Iran",
 "roster": [
  "P5984 | Rasht-Chelavend Gas Pipeline | ?->? | status=operating | len=150.0 dia=42 cap=5.5",
  "P0749 | Korpeje-Kordkuy Gas Pipeline aka=Korpezhe-Kurt Kui Gas Pipeline | Korpeje->Kordkuy | status=operating | len=197.0 dia=1000 cap=8.0",
  "P0748 | Hajiqabul–Astara–Abadan Gas Pipeline aka=Kazi Magomed–Astara–Abadan Gas Pipeline | Gazimammad->Abadan | status=operating | len=1474.5 dia=1020, 1200 cap=10.0",
  "P2225 | Iran-Oman Gas Pipeline | Rudan County->Sohar port | status=construction | len=1000.0 dia=? cap=10.0",
  "P1639 | Sarakhs-Sari Pipeline | Sarakhs->Sari | status=operating | len=795.0 dia=30, 36 cap=12.0",
  "P0742 | Dauletabad-Sarakhs-Khangiran Gas Pipeline / Pipeline I aka=Turkmenistan-Iran Gas Pipeline | Dauletabad->Khangiran | status=operating | len=182.0 dia=48 cap=12.5",
  "P0459 | Tabriz-Ankara Gas Pipeline aka=Iran-Turkey Gas pipeline | Tabriz->Ankara | status=operating | len=2577.0 dia=40, 46 cap=14.0",
  "P6848 | Dauletabad-Sarakhs-Khangiran Gas Pipeline / Pipeline II | Dauletabad->Khangiran | status=proposed | len=125.0 dia=? cap=19.5",
  "P0442 | IGAT 2 Gas Pipeline aka=Iran Gas Trunkline | Kangan Refinery->Qazvin | status=operating | len=680.0 dia=56 cap=32.85",
  "P0443 | IGAT 3 Gas Pipeline aka=Iran Gas Trunkline | Asaluyeh->Saveh | status=operating | len=1195.0 dia=56 cap=32.85",
  "P5855 | Iran-Iraq Gas Pipeline | ?->? | status=operating | len=? dia=? cap=35.0",
  "P0457 | Persian Gas Pipeline aka=IGAT 9, Pars Pipeline, Iran–Europe pipeline, Iran–Turkey-Europe (ITE) pipeline | Asaluyeh->? | status=cancelled | len=3300.0 dia=56 cap=40.0",
  "P0444 | IGAT 4 Gas Pipeline aka=Iran Gas Trunkline | Asaluyeh->Saveh | status=operating | len=1145.0 dia=? cap=40.15",
  "P7104 | Russia–Iran Gas Pipeline | ?->? | status=construction | len=? dia=? cap=55.0",
  "P0441 | IGAT 11 Gas Pipeline aka=Iran Gas Trunkline 11 | Asaluyeh->Bazargan | status=construction | len=1200.0 dia=56 cap=110.0",
  "P0450 | Iran–Iraq–Syria Gas Pipeline aka=Friendship Pipeline, Islamic gas pipeline | Asaluyeh->Damascus | status=cancelled | len=5600.0 dia=56 cap=110.0",
  "P6026 | North–Northeast Gas Pipeline | ?->Shahid Babaei Expressway | status=operating | len=35.0 dia=48 cap=204.0",
  "P0449 | Iran-Armenia Gas Pipeline | Tabriz->Sardarian | status=operating | len=141.0 dia=700 cap=222.5",
  "P3949 | Siri–Asaluyeh Gas Pipeline | ?->Asaluyeh | status=operating | len=289.0 dia=32.00 cap=500.0",
  "P0452 | Iran-Pakistan Pipeline aka=Peace Pipeline | Asaluyeh->Nawabshah | status=construction | len=2775.0 dia=56 cap=750.0",
  "P3174 | Off-Shore Gas Pipeline | ?->? | status=proposed | len=1500.0 dia=? cap=1000.0",
  "P2015 | IGAT 7 Gas Pipeline / Expansion aka=Iran Gas Trunkline 7 | ?->? | status=operating | len=290.0 dia=? cap=1100.0",
  "P0446 | IGAT 7 Gas Pipeline aka=Iran Gas Trunkline 7, IGAT VII | Asaluyeh->Iranshahr | status=operating | len=907.0 dia=56 cap=1800.0",
  "P0440 | IGAT 10 Gas Pipeline aka=Iran Gas Trunkline | Kangan->Tiran | status=operating | len=632.0 dia=? cap=2472.03",
  "P0445 | IGAT 6 Gas Pipeline aka=Iran Gas Trunkline | Asaluyeh->Khorramshahr | status=operating | len=600.0 dia=56 cap=3884.6",
  "P0447 | IGAT 8 Gas Pipeline aka=Iran Gas Trunkline | Parsian Refinery->? | status=operating | len=1000.0 dia=56 cap=3884.6",
  "P0451 | Iran-Pakistan-India Pipeline aka=IPI Pipeline | Asaluyeh->New Delhi | status=cancelled | len=2700.0 dia=? cap=3884.6",
  "P0448 | IGAT 9 Gas Pipeline aka=Europe Gas Export Line, Iran Gas Trunkline, IGAT XI | Asaluyeh->Bazargan | status=construction | len=1900.0 dia=56 cap=3885.0",
  "P3950 | Salman–Siri Gas Pipeline | Lavan Island->Siri Island | status=operating | len=147.0 dia=30.00 cap=?",
  "P3951 | Siri–Mobarak Gas Pipeline | ?->Mobarak | status=operating | len=66.0 dia=30.00 cap=?",
  "P3957 | IGAT 1 Gas Pipeline | ?->? | status=operating | len=1104.0 dia=42 cap=?",
  "P6006 | Behbahan–Gachsaran Gas Pipeline | ?->Gachsaran | status=construction | len=62.0 dia=20 cap=?",
  "P6009 | Dizbad-Torbat Heydariyeh Gas Pipeline | ?->Abasabad | status=operating | len=50.0 dia=12, 30 cap=?",
  "P6021 | Torbat Heydariyeh–Kashmar Gas Pipeline | ?->Kashmar | status=operating | len=? dia=12 cap=?",
  "P6022 | Esfarayen–Neqab–Joghatai Gas Pipeline / Expansion 1 | ?->Joghatai | status=operating | len=48.0 dia=30 cap=?",
  "P6023 | Esfarayen–Neqab–Joghatai Gas Pipeline / Expansion 2 | ?->Joghatai | status=operating | len=35.0 dia=20 cap=?",
  "P6024 | Esfarayen Gas Pipeline | ?->? | status=operating | len=? dia=10 cap=?",
  "P6025 | Sabzevar Steel Plant Gas Pipeline | ?->? | status=operating | len=3.5 dia=12 cap=?",
  "P6027 | Kuh Sefid–Charmshahr Gas Pipeline | ?->Charmshahr | status=operating | len=45.0 dia=56 cap=?",
  "P6028 | Zahedan–Zabol Gas Pipeline | Zahedan->Zabol | status=operating | len=250.0 dia=? cap=?",
  "P6029 | Kuhdasht–Pol-e-Dokhtar Gas Pipeline | ?->Pol-e-Dokhtar | status=operating | len=50.0 dia=12 cap=?",
  "P6030 | Zarand–Ravar Gas Pipeline | ?->Ravar | status=operating | len=106.0 dia=12,10 cap=?"
 ]
}
if (!Array.isArray(A.roster) || !A.roster.length) {
  throw new Error("country-discovery needs args.roster — run scripts/build_discovery_context.py and pass its JSON as `args`.")
}
const REPO = A.repo
const STAGING = A.staging
const COMMODITY = A.commodity || 'gas'
const COUNTRY = A.country || ''
const ROSTER = A.roster.join("\n")

const STRATEGIES = A.strategies || [
  { key: 'news', brief: `Industry + business news sweep for NEWLY ANNOUNCED ${COUNTRY} ${COMMODITY} pipeline projects (roughly the last 3 years): "<country> new ${COMMODITY} pipeline <year>", FID announcements, MOUs, FEED/EPC awards, tenders, capacity-expansion projects that include new pipe. Search in-country languages too.` },
  { key: 'regulators', brief: `Regulator / ministry / TSO paper trail for ${COUNTRY}: national energy regulator filings and project inventories, environmental-permit applications, ministry project lists, TSO ten-year development plans (or the national equivalent — FERC-style dockets where they exist).` },
  { key: 'operators', brief: `Operator/sponsor project pages: identify the main midstream, TSO, and NOC players operating in ${COUNTRY} and crawl their project/infrastructure pages and annual reports for ${COMMODITY} pipeline projects.` },
  { key: 'maps', brief: `The MISSING-pipeline stance: ${COUNTRY} national ${COMMODITY} grid maps, TSO network maps, gas/energy master plans, IEA/EIA and national-statistics infrastructure inventories — OPERATING or under-construction transmission lines that GEM never captured (not just new announcements). A line on the national grid map with no roster match is exactly what this strategy exists to find.` },
  { key: 'crossborder', brief: `Cross-border lines touching ${COUNTRY} in either direction: interconnectors, import/export lines, transit corridors. Check the neighbouring countries' TSO/ministry project lists for lines that terminate in ${COUNTRY}.` },
]

const searchContract = (s) => `You are a GEM pipeline discovery researcher. Find ${COMMODITY} TRANSMISSION pipelines in/touching
${COUNTRY} that are MISSING from GEM's tracker. Your single search angle for this pass:

${s.brief}

cd ${REPO} first.

## The existing GEM roster (ALL statuses) — a candidate matching one of these rows is NOT a discovery
${ROSTER}

## Rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, or any wikidot.com page (read for
   leads only). NEVER fabricate a URL.
2. Verify every URL you emit: \`python scripts/url_verifier.py "<url>" "<expected substring>"\` —
   emit only OK/200 + token-present links.
3. Transmission lines only — skip gathering/process/feeder lines and distribution networks.
4. Pre-filter against the roster (names, other names, endpoints). Borderline match → still emit it,
   but say which PID it might match in why_maybe_new; the consolidator decides.

## Output — write a file, then return a summary
Write ${STAGING}/discovery/found_${s.key}.json EXACTLY shaped:
{ "strategy": "${s.key}", "candidates": [
  { "name": "<best project name>", "aka": ["<other names seen>"], "sponsor": "<company or empty>",
    "from": "<start point>", "to": "<end point>", "status_guess": "<proposed|construction|operating|...>",
    "evidence": [ { "url": "https://...verified...", "date": "YYYY-MM", "note": "<what it says>" } ],
    "why_maybe_new": "<why this does not appear in the roster / which PID it might match>" }
] }
Empty candidates list is a valid result — do NOT pad with weak candidates. Before finishing, run
\`python -c "import json; json.load(open('${STAGING}/discovery/found_${s.key}.json'))"\`.
Return ONLY a 2-line summary (count found, strongest lead). The file is the deliverable.`

const QUEUE_SCHEMA = {
  type: 'object',
  properties: {
    queue: { type: 'array', items: { type: 'object', properties: {
      slug: { type: 'string' }, name: { type: 'string' }, note: { type: 'string' } },
      required: ['slug', 'name'] } },
    matched: { type: 'number' }, dropped: { type: 'number' },
  },
  required: ['queue'],
}

const consolidateContract = `You are the GEM discovery consolidator for ${COUNTRY} (${COMMODITY}).
cd ${REPO} first. Read every ${STAGING}/discovery/found_*.json (strategy outputs) and
${STAGING}/discovery_context.json (the full existing-row context).

For the union of all candidates:
1. DEDUP across strategies — the same physical project found by two strategies is ONE candidate
   (merge their evidence lists).
2. MATCH-TO-EXISTING FIRST (Discovery SOP): compare each candidate against the existing rows
   (names, other_names, endpoints, specs). A likely match to an existing ProjectID is NOT a
   discovery — record it as matched (candidate name -> OtherEnglishNames suggestion for that PID).
3. The survivors form the vetting queue. Give each a short kebab-case slug (filesystem-safe).

Write ${STAGING}/discovery/queue.json:
{ "queue":   [ { "slug": "...", "name": "...", "strategies": ["news"], "note": "<1-line why new>",
                 "evidence": [ {"url":"...","date":"...","note":"..."} ] } ],
  "matched": [ { "name": "<candidate>", "matched_project_id": "P####", "reason": "...",
                 "other_names_suggestion": "<name to add>", "evidence": [ ... ] } ],
  "dropped": [ { "name": "...", "reason": "<duplicate-of-candidate / not transmission / no evidence>" } ] }
Then ALSO return { queue: [{slug, name, note}], matched: <n>, dropped: <n> } as your structured
output (the queue drives the next fan-out).`

const vetContract = (q) => `You are a skeptical GEM discovery researcher. Vet ONE candidate ${COUNTRY} ${COMMODITY}
pipeline for addition to the GEM tracker: "${q.name}" (slug: ${q.slug}).
${q.note ? `Consolidator note: ${q.note}` : ''}

cd ${REPO} first. Read your candidate's entry (evidence URLs included) in
${STAGING}/discovery/queue.json and the existing-row context in ${STAGING}/discovery_context.json.

## Rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org / theodora / wikidot. NEVER fabricate a URL.
2. Every URL through \`python scripts/url_verifier.py "<url>" "<expected substring>"\` before citing.
3. Corroborate with >=2 INDEPENDENT sources (not one wire story reprinted). Search in-country languages.
4. RE-CHECK match-to-existing yourself before anything else — if this is really an existing GEM row
   under another name, class it matched_existing and STOP researching a new row.
5. New owner/operator entities: \`python scripts/entity_lookup.py "<owner>" "${COUNTRY}"\` first.

## The add-threshold (Discovery SOP §3) — ALL THREE or it is monitor, not new_row:
(a) an identified sponsor; (b) at least country + region/endpoints; (c) a concrete step
(MOU signed, FEED/EPC award, permit applied, tender issued, FID). Early rumor -> "monitor".

## For a qualifying new_row, research the GEM columns
Use EXACT GEM column names (header row 3 of data/<csv named in discovery_context.json>):
PipelineName, SegmentName, OtherEnglishNames, Status (controlled vocab, lowercase), Fuel,
PipelineType, CountriesOrAreas, StartLocation/StartState/Province/StartCountryOrArea,
EndLocation/EndState/Province/EndCountryOrArea, Capacity+CapacityUnits, LengthKnown+LengthKnownUnits,
Diameter+DiameterUnits, Owner, Parent, ProposalYear, FIDStatus, ProjectLevelCost+Units,
RouteType/RouteAccuracy/RouteNotes (route research per docs/reference/route_conventions.md —
official GIS first; expansion with no new pipe -> LengthKnown=0, Diameter blank, 'no route').
Every filled value needs a verified ref in the matching "<X> [ref]" key — no orphan values, no
orphan refs.

## Output — write a shard, then return a summary
Write ${STAGING}/discovery/vetted/${q.slug}.json EXACTLY shaped:
{ "slug": "${q.slug}", "class": "new_row|monitor|matched_existing",
  "matched_project_id": "<P#### when matched_existing, else empty>",
  "name": "${q.name}",
  "values": { "<GEM column>": "<value>", ... },
  "refs": { "<GEM [ref] column>": ["https://...verified..."], ... },
  "verifications": [ {"url":"https://...","ok":true,"contains_value":true} ],
  "tier": "high|medium|low", "independent": true, "source_language": "en",
  "monitor_reason": "<for monitor: which threshold leg failed>",
  "researcher_notes": "<what you confirmed, sources, confidence tier, route notes>" }
Before finishing: \`python -c "import json; json.load(open('${STAGING}/discovery/vetted/${q.slug}.json'))"\`.
Return ONLY a 2-line summary (class + strongest evidence). The shard is the deliverable.`

phase('Search')
log(`Discovery sweep for ${COUNTRY} (${COMMODITY}): ${STRATEGIES.length} strategy agents vs a roster of ${A.roster.length} existing rows.`)
await parallel(STRATEGIES.map(s => () =>
  agent(searchContract(s), { label: `search:${s.key}`, phase: 'Search', agentType: 'general-purpose' })
))

phase('Consolidate')
const consolidated = await agent(consolidateContract, {
  label: 'consolidate', phase: 'Consolidate', agentType: 'general-purpose', schema: QUEUE_SCHEMA,
})
if (!consolidated || !consolidated.queue.length) {
  log(`No candidates survived consolidation (matched: ${consolidated ? consolidated.matched : '?'}, dropped: ${consolidated ? consolidated.dropped : '?'}).`)
  return { queued: 0, matched: consolidated ? consolidated.matched : null }
}
log(`${consolidated.queue.length} candidates queued for vetting (${consolidated.matched || 0} matched to existing rows, ${consolidated.dropped || 0} dropped).`)

phase('Vet')
const vetted = await parallel(consolidated.queue.map(q => () =>
  agent(vetContract(q), { label: `vet:${q.slug}`, phase: 'Vet', agentType: 'general-purpose' })
))
const done = vetted.filter(Boolean).length
log(`Vetting complete: ${done}/${consolidated.queue.length}. Shards in ${STAGING}/discovery/vetted/ — next: scripts/merge_discovery_shards.py`)
return { queued: consolidated.queue.length, vetted: done, matched: consolidated.matched || 0 }
