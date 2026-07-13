export const meta = {
  name: 'egypt-gas-discovery',
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
 "staging": "batches/staging/annual-gas-egypt",
 "commodity": "gas",
 "country": "Egypt",
 "roster": [
  "P3620 | Israel\u2013Egypt Onshore Gas Pipeline | Ramat Hovav->? | status=construction | len=65.0 dia=? cap=6.0",
  "P3657 | Israel\u2013Egypt Offshore Gas Pipeline | ?->? | status=proposed | len=? dia=? cap=6.7",
  "P6035 | Gamasa\u2013Veunsa Gas Pipeline | ?->? | status=operating | len=34.0 dia=42 cap=6.8",
  "P0462 | Arish\u2013Ashkelon Pipeline | Ashkelon->Arish | status=operating | len=90.0 dia=? cap=7.0",
  "P0473 | Cyprus\u2013Egypt Gas Pipeline aka=Aphrodite-Damietta Gas Pipeline | Aphrodite offshore gas field->Damietta Segas LNG Terminal | status=proposed | len=310.0 dia=? cap=8.0",
  "P0436 | Arab Gas Pipeline / Arish-Taba Gas Pipeline aka=Phase I | Arish->Taba | status=operating | len=250.0 dia=36 cap=10.3",
  "P7482 | Arab Gas Pipeline / Taba-Aqaba Sea Gas Pipeline aka=Phase I | Taba->Aqaba | status=operating | len=18.0 dia=26 cap=10.3",
  "P0477 | South Valley Gas Pipeline / SYSTEM/NETWORK INFO aka=Upper Egypt Gas Pipeline | Dahshour->Aswan | status=operating | len=930.0 dia=36, 32, 32,32,32,30 cap=12.0",
  "P3928 | Nubaria\u2013Sadat Gas Pipeline | El Noubareya->? | status=operating | len=73.0 dia=36.00 cap=12.0",
  "P3935 | Salam\u2013Matruh Terminal Gas Pipeline | Salam->? | status=operating | len=75.0 dia=10.00 cap=22.0",
  "P7589 | Framid Field Gas Pipeline | ?->? | status=operating | len=38.0 dia=10 cap=25.0",
  "P3939 | Abu Gharadig\u2013Dahshour (1) Gas Pipeline | Abu Gharadig->? | status=operating | len=290.0 dia=24.00 cap=120.0",
  "P3938 | Badr El Din Spur Gas Pipelines / Badr El Din Spur (2) | Badr El Din Field->? | status=operating | len=130.0 dia=16.00 cap=150.0",
  "P3937 | Badr El Din Spur Gas Pipelines / Badr El Din Spur (1) | Badr El Din Field->? | status=operating | len=130.0 dia=20.00 cap=180.0",
  "P0476 | Salam-Abu Gharadig Southern Gas Pipeline aka=Salam-Abu Gharadig gas pipeline | Salam gas field->Abu Gharadig oilfield | status=operating | len=212.0 dia=18.00 cap=187.0",
  "P6688 | Shams-Obaiyed Gas Pipeline | Shams->Obaiyed | status=operating | len=42.0 dia=18 cap=240.0",
  "P6693 | Salam Spurline Gas Pipeline | Salam->Salam | status=operating | len=35.0 dia=22 cap=250.0",
  "P3936 | BED/AS\u2013Ameryia Gas Pipeline | Abu Sennan->? | status=operating | len=160.0 dia=24.00 cap=350.0",
  "P6692 | Qasr-Shams Gas Pipeline | Qasr->Shams | status=operating | len=40.0 dia=24 cap=350.0",
  "P6703 | Raven-Western Desert Cmplex Gas Pipeline | Rashid->? | status=operating | len=70.0 dia=30 cap=350.0",
  "P6687 | Obaiyed-Amreya Northern Gas Pipeline / Obaiyed Spurline | Obaiyed->Amreya | status=operating | len=41.5 dia=26 cap=480.0",
  "P7577 | Baltim Field Gas Pipelines / Sub-Sea Pipeline | ?->? | status=operating | len=18.0 dia=26 cap=500.0",
  "P7578 | Baltim Field Gas Pipelines / Onshore Pipeline | ?->? | status=operating | len=25.0 dia=26 cap=500.0",
  "P7597 | Cronos-Port Said Gas Pipeline | ?->? | status=proposed | len=90.0 dia=? cap=500.0",
  "P0474 | Obaiyed-Amreya Northern Gas Pipeline / Obaiyed-Tarek Gas Pipeline | Obaiyed gas field->Amreya oil & gas plant | status=operating | len=49.5 dia=32 cap=600.0",
  "P7864 | Nitzana Pipeline | ?->? | status=proposed | len=65.0 dia=36 cap=600.0",
  "P3932 | Nooros\u2013Abu Madi\u2013El Gamil Gas Pipline | Noors->? | status=operating | len=130.0 dia=24, 32 cap=700.0",
  "P6037 | Al Gamil\u2013Damietta Gas Pipeline | Al Gamil->Damietta | status=operating | len=50.0 dia=42 cap=750.0",
  "P3934 | Obaiyed-Amreya Northern Gas Pipeline / Tarek\u2013Ameryia Gas Pipeline | ?->? | status=operating | len=231.0 dia=34.00 cap=950.0",
  "P3343 | El Tina Gas Pipeline | El Tina->Mit Nema | status=operating | len=170.0 dia=42 cap=?",
  "P3346 | El Noubareya Gas Pipeline | El Noubareya->Mit Nema | status=operating | len=66.0 dia=32, 42 cap=?",
  "P3366 | El Tina- Abu Sultan- New Administrative Capital Gas Pipeline | El Tina Abou Sultan->New Administrative Capital | status=operating | len=165.0 dia=42.00 cap=?",
  "P3659 | Port Said - Arish Gas Pipeline | El Gamil->? | status=operating | len=235.0 dia=36, 42 cap=?",
  "P3929 | El Wasta\u2013Beni Suef Gas Pipeline | El Wasta->? | status=operating | len=65.0 dia=36.00 cap=?",
  "P3930 | New Administrative Capital\u2013Dahshur Gas Pipeline | New Administrative Capital->? | status=operating | len=70.0 dia=32.00 cap=?",
  "P3931 | Amriya\u2013El Alamein Gas Pipeline | Amriya->? | status=operating | len=130.0 dia=32.00 cap=?",
  "P5132 | Zohr\u2013Al Gamil Pipelines / Pipeline 1 | Shorouk concession->Al Gamil | status=operating | len=216.0 dia=30 cap=?",
  "P6032 | Borg El Arab\u2013Midor Gas pipeline | Borg El Arab->Al ameryia | status=operating | len=10.0 dia=24 cap=?",
  "P6033 | Damietta\u2013SEGAS Pipeline | Damietta->Damietta | status=operating | len=12.0 dia=42 cap=?",
  "P6034 | Hurghada\u2013Safaga Gas Pipeline | Hurghada->Safaga | status=operating | len=38.5 dia=24 cap=?",
  "P6036 | Zohr\u2013Al Gamil Pipelines / Pipeline 2 | Shorouk concession->Al Gamil | status=operating | len=210.0 dia=30 cap=?",
  "P6685 | Solaimaneyah-North Giza Gas Pipeline | Solaimaneyah->Giza | status=construction | len=20.0 dia=42 cap=?",
  "P6686 | New Fayoum Gas Pipeline | New Fayoum City->? | status=construction | len=40.0 dia=16,24 cap=?",
  "P6689 | Abu Sennan Spur Gas Pipeline | Abu Sennan->Abu Sennan | status=operating | len=45.0 dia=14 cap=?",
  "P6697 | South Valley Gas Pipeline / Dahshour-Al Kurimat Gas Pipeline | Dahshour->Al Kurimat | status=operating | len=90.0 dia=36 cap=?",
  "P6698 | South Valley Gas Pipeline / Al Kurimat-Beni Suef Gas Pipeline | Al Kurimat->Beni Suef | status=operating | len=30.0 dia=32 cap=?",
  "P6699 | South Valley Gas Pipeline / Beni Suef-Abu qurqas Gas pipeline | Beni Suef->Abu qurqas | status=operating | len=150.0 dia=32 cap=?",
  "P6700 | South Valley Gas Pipeline / Abu qurqas-Asyut Gas pipeline | Abu qurqas->Asyut | status=operating | len=147.0 dia=32 cap=?",
  "P6701 | South Valley Gas Pipeline / Asyut-Girga Gas pipeline | Asyut->Girga | status=operating | len=121.0 dia=32 cap=?",
  "P6702 | South Valley Gas Pipeline / Girga-Aswan Gas pipeline | Girga->Aswan | status=operating | len=390.0 dia=30 cap=?",
  "P6704 | Raven-Al Ameryia Gas Pipeline | Rashid->Ameriya | status=operating | len=5.0 dia=18 cap=?",
  "P7447 | Denise Gas Pipeline | ?->? | status=operating | len=405.0 dia=16 cap=?",
  "P7567 | Idku-Abu Hummus Gas Pipeline | ?->? | status=operating | len=30.0 dia=42 cap=?",
  "P7572 | Qarun Gas Pipeline | ?->? | status=operating | len=206.0 dia=10 cap=?",
  "P7574 | New Administration Capital PS Gas Pipeline | ?->? | status=operating | len=63.0 dia=32 cap=?",
  "P7580 | Mahmoudiah PS Gas Pipeline | ?->? | status=operating | len=52.0 dia=? cap=?",
  "P7588 | Edfu Gas Pipeline | Edfu->? | status=operating | len=37.0 dia=12 cap=?"
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
