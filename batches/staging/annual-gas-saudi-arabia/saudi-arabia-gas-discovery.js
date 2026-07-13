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
 "staging": "batches/staging/annual-gas-saudi-arabia",
 "commodity": "gas",
 "country": "Saudi Arabia",
 "roster": [
  "P7766 | Hasbah-Wasit Gas Pipelines / Pipeline 1 aka=Fadali gas pipelines | ?->? | status=operating | len=80.0 dia=36 cap=1.0",
  "P7767 | Hasbah-Wasit Gas Pipelines / Pipeline 2 aka=Fadali gas pipelines | ?->? | status=operating | len=80.0 dia=36 cap=1.0",
  "P3966 | East\u2013West Gas Pipeline (Saudi Arabia) / SYSTEM/NETWORK INFO aka=Expansion | ?->Yanbu | status=? | len=821.0 dia=? cap=5.2",
  "P1921 | Abu Ali-Berri Gas Pipeline | ?->Berri Gas Plant | status=operating | len=44.0 dia=30 cap=220.0",
  "P7768 | Abu Ali-Berri Gas Pipeline / Sub-sea Pipeline | Al Jubail->Berri Gas Plant | status=operating | len=22.0 dia=30 cap=220.0",
  "P3961 | Madrakah\u2013Al Hawiyah Gas Pipeline | ?->Al Hawiyah | status=operating | len=450.0 dia=? cap=290.0",
  "P7544 | Marjan GOSP-4 Gas Pipeline | ?->? | status=operating | len=330.0 dia=? cap=750.0",
  "P7545 | Marjan GOSP-4 Gas Pipeline / Subsea Pipelines | ?->? | status=operating | len=62.0 dia=? cap=750.0",
  "P1909 | Juaymah-Jubail Gas Pipeline | ?->Al Jubail | status=operating | len=56.0 dia=38,30, 40 cap=820.0",
  "P0458 | Qatar-Turkey Gas Pipeline | North Field->Nabucco Pipeline | status=cancelled | len=1500.0 dia=? cap=?",
  "P1897 | A47-Yanbu Gas Pipeline aka=Pump Station- A47-Yanbu Gas Pipeline | ?->? | status=operating | len=966.0 dia=42, 48, 56 cap=?",
  "P1898 | UBTG-1-Berri Gas Pipeline | ?->? | status=operating | len=249.0 dia=56, 36, 38, 40, 42 cap=?",
  "P1899 | UBTG-1-Berri 2 Gas Pipeline | ?->? | status=operating | len=247.0 dia=56, 36, 38, 40, 42 cap=?",
  "P1900 | UBTG-km56-AY-1 KP916 Gas Pipeline | ?->? | status=operating | len=244.0 dia=56.00 cap=?",
  "P1901 | UBTG-1km-Juanymah Gas Pipeline | ?->? | status=operating | len=204.0 dia=28, 30, 38, 40 cap=?",
  "P1902 | Safianayh-Ju\u2019aymah Gas Pipeline | ?->Ju\u2019aymah | status=operating | len=198.0 dia=40.00 cap=?",
  "P1903 | AY\u20131 KP 943-Riyadh Gas Pipeline / Pump Station and A47/Yanbu | ?->? | status=operating | len=153.0 dia=48.00 cap=?",
  "P1904 | Tanajib-Berri Gas Pipeline | coast of the Persian Gulf->Berri Gas Plant | status=operating | len=145.0 dia=30.00 cap=?",
  "P1905 | Haradh-Uthmaniya Gas Pipeline | ?->Uthmaniya | status=operating | len=87.0 dia=48 cap=?",
  "P1906 | Abqaiq-Berri Gas Pipeline | ?->? | status=operating | len=137.0 dia=24, 36 cap=?",
  "P1907 | Haradh-3-Uthmaniya Gas Pipeline | ?->Uthmaniya | status=operating | len=124.0 dia=24, 32 cap=?",
  "P1908 | UA-1-km199-Uthmaniya Gas Pipeline | ?->Uthmaniya | status=operating | len=108.0 dia=24, 32 cap=?",
  "P1910 | UBTG-1-km0-UBTG-1-km56 Gas Pipeline | ?->? | status=operating | len=56.0 dia=48 cap=?",
  "P1911 | UBTG-1-km0-UBTG-1-km56 2 Gas Pipeline | ?->? | status=operating | len=56.0 dia=40 cap=?",
  "P1912 | Hawiyah-UBTG-1-km0 Gas Pipeline | ?->? | status=operating | len=56.0 dia=56 cap=?",
  "P1913 | Abqaiq-B-Shedgum Gas Pipeline | ?->Shedgum | status=operating | len=53.0 dia=42 cap=?",
  "P1914 | Waqr Khuff-Haradh Gas Pipeline | ?->? | status=operating | len=50.0 dia=30 cap=?",
  "P1915 | Hawiyah-Uthmniyah Gas Pipeline | ?->Uthmaniya | status=operating | len=47.0 dia=32 cap=?",
  "P1916 | Qatif North-Berri Gas Pipeline | ?->Berri Gas Plant | status=operating | len=45.0 dia=32 cap=?",
  "P1917 | Haradh Khuff-Hawiyah Gas Pipeline | ?->Al Hawiyah | status=operating | len=43.0 dia=30 cap=?",
  "P1918 | Haradh Khuff-Hawiyah 2 Gas Pipeline | ?->Al Hawiyah | status=operating | len=43.0 dia=30 cap=?",
  "P1919 | Haradh Khuff-Hawiyah 3 Gas Pipeline | ?->Al Hawiyah | status=operating | len=43.0 dia=30 cap=?",
  "P1920 | Tinat Kuff-Haradh Gas Pipeline | ?->? | status=operating | len=43.0 dia=20 cap=?",
  "P1922 | Berri-Abu Ali Gas Pipeline | ?->Abu Ali Island | status=operating | len=39.0 dia=8 cap=?",
  "P1923 | Berri-Abu Ali 2 Gas Pipeline | ?->Abu Ali Island | status=operating | len=39.0 dia=10 cap=?",
  "P1924 | Aindar-Shedgum Gas Pipeline | ?->Shedgum | status=operating | len=34.0 dia=12 cap=?",
  "P1925 | Depco-Abqaiq Gas Pipeline | ?->? | status=operating | len=32.0 dia=40 cap=?",
  "P3962 | East\u2013West Gas Pipeline (Saudi Arabia) / Main Line aka=Shedgum-Yanbu Gas Pipeline | ?->Yanbu | status=operating | len=1200.0 dia=48 cap=?",
  "P5854 | Wafra-Station 171 Gas Pipeline | Wafra Joint Operations->BS 171 | status=proposed | len=65.0 dia=20 cap=?",
  "P5885 | MGS III Gas Pipelines / SYSTEM/NETWORK INFO | ?->? | status=? | len=4000.0 dia=? cap=?",
  "P6717 | MGS III Gas Pipelines / EWPS-1-Shedgum \"3\" | ?->? | status=construction | len=28.0 dia=56 cap=?",
  "P6718 | MGS III Gas Pipelines / EWPS-1-Shedgum \"4\" | ?->? | status=construction | len=28.0 dia=56 cap=?",
  "P6719 | MGS III Gas Pipelines / EWPS-1-EWPS-3 \"3\" | ?->? | status=construction | len=150.0 dia=56 cap=?",
  "P6720 | MGS III Gas Pipelines / EWPS-1-EWPS-3 \"4\" | ?->? | status=construction | len=150.0 dia=56 cap=?",
  "P6721 | MGS III Gas Pipelines / EWPS-3-EWPS-4 \"3\" | ?->? | status=construction | len=83.0 dia=56 cap=?",
  "P6722 | MGS III Gas Pipelines / EWPS-3-EWPS-4 \"4\" | ?->? | status=construction | len=83.0 dia=56 cap=?",
  "P6723 | MGS III Gas Pipelines / EWPS-4-EWPS-6 \"3\" | ?->? | status=construction | len=185.0 dia=56 cap=?",
  "P6724 | MGS III Gas Pipelines / EWPS-4-EWPS-6 \"4\" | ?->? | status=construction | len=185.0 dia=56 cap=?",
  "P6725 | MGS III Gas Pipelines / EWPS-6-EWPS-8 \"3\" | ?->? | status=construction | len=170.0 dia=56 cap=?",
  "P6726 | MGS III Gas Pipelines / EWPS-6-EWPS-8 \"4\" | ?->? | status=construction | len=170.0 dia=56 cap=?",
  "P6727 | MGS III Gas Pipelines / EWPS-8-EWPS-10 \"3\" | ?->? | status=construction | len=190.0 dia=56 cap=?",
  "P6728 | MGS III Gas Pipelines / EWPS-8-EWPS-10 \"4\" | ?->? | status=construction | len=190.0 dia=56 cap=?",
  "P6729 | MGS III Gas Pipelines / BGCS-10-STS-2 \"EWJZG-1\" | ?->? | status=construction | len=458.0 dia=56 cap=?",
  "P6730 | MGS III Gas Pipelines / STS-2-STS-1 \"EWJZG-1\" | ?->? | status=construction | len=310.0 dia=56 cap=?",
  "P6731 | MGS III Gas Pipelines / STS-1-Shoqaiq \"EWJZG-1\" | ?->? | status=construction | len=462.0 dia=56 cap=?",
  "P6732 | MGS III Gas Pipelines / Eastern-Qassim | ?->? | status=construction | len=116.0 dia=12,4,16 cap=?",
  "P6733 | MGS III Gas Pipelines / Riyadh | ?->? | status=construction | len=470.0 dia=12,16,10,4 cap=?",
  "P6734 | MGS III Gas Pipelines / Shoaiba | ?->? | status=construction | len=212.0 dia=56,10,16 cap=?",
  "P6735 | MGS III Gas Pipelines / Yanbu-Rabigh | ?->? | status=construction | len=192.0 dia=20,16,12,4 cap=?",
  "P6736 | MGS III Gas Pipelines / Jeddah | ?->? | status=construction | len=52.0 dia=? cap=?",
  "P6737 | MGS III Gas Pipelines / Jizan | ?->? | status=construction | len=196.0 dia=30,16 cap=?",
  "P7711 | Pump Station 06- Qassim PS Gas Pipeline / Central Region Pipeline | Pump Station 06->Qassim power station | status=operating | len=226.0 dia=46 cap=?",
  "P7712 | Pump Station 07-Pump Station11 Gas Pipeline / Western Region Pipeline | Pump Station 07->Pump Station 11 | status=operating | len=422.0 dia=56 cap=?",
  "P7714 | Shedgum- Riyadh Gas Pipeline 3 / Eastern Region Pipeline aka=EWPS1- BGCS 3 | ?->? | status=operating | len=150.0 dia=56 cap=?",
  "P7715 | Shedgum- Riyadh Gas Pipeline 2 / Eastern Region Pipeline | ?->? | status=operating | len=40.0 dia=56 cap=?"
 ]
};
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
// The consolidate AGENT kept dying mid-response (API instability) despite only 3 candidates.
// Consolidation was done inline and written to discovery/queue.json; bake the queue here so the
// vet fan-out runs deterministically. Vet agents read queue.json from disk for the evidence URLs.
const consolidated = {
  queue: [
    { slug: 'dorra-durra-export-saudi', name: 'Dorra (Durra) Gas Field Export Pipeline (Saudi share)', note: 'Cross-Neutral-Zone Dorra/Arash shared-field gas export line landing at Al-Khafji; Package 2B (export pipelines) still pre-award. No roster match (P5854 Wafra onshore, P2702 Khafji crude are different).' },
    { slug: 'midyan-duba-sales-gas', name: 'Midyan Gas Plant–Duba Sales Gas Pipeline', note: 'NW Red Sea sales-gas line Midyan plant->Duba power station, operating ~2017, ~84-98 km. No NW/Red Sea gas row exists in the SA roster. Sales-gas line only.' },
    { slug: 'jafurah-export-package5', name: 'Jafurah Gas Plant Export Pipeline (Package 5)', note: '~349 km Jafurah Gas Plant sales-gas export line into national grid; distinct EPC package from MGS III (P5885 / P6717-P6737). Jafurah Phase 1 onstream Dec 2025 -> likely operating. Vet whether it should fold into P5885 network.' },
  ],
  matched: 0, dropped: 0,
}
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
