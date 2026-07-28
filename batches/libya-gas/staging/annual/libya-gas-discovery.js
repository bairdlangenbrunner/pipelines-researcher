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
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/libya-gas/staging/annual", "commodity": "gas", "country": "Libya", "roster": ["P1789 | Khoms-Melita Pipeline | Khoms->Melita | status=operating | len=25.0 dia=34 cap=2.0", "P1873 | Jakhira-Intesar Gas Pipeline | Jakhira Oasis->Intesar Oil field | status=operating | len=160.0 dia=20, 8 cap=2.4", "P1859 | Bouri-Bahr Assalam Gas Pipeline / Pipeline 1 | ?->? | status=operating | len=32.0 dia=10.00 cap=3.88", "P1869 | Raguba-Km-110 Gas Pipeline | ?->? | status=operating | len=142.0 dia=20.00 cap=3.96", "P1860 | Waha-Nasser Gas Pipeline | ?->? | status=operating | len=177.0 dia=24.00 cap=5.66", "P1861 | Farigh-Intesar Gas Pipeline | ?->? | status=operating | len=177.0 dia=24.00 cap=7.08", "P1868 | Km-81.5-Brega Gas Pipeline | ?->? | status=operating | len=132.0 dia=30.00 cap=8.5", "P1862 | Brega-Benghazi Gas Pipeline | Mersa Brega->Benghazi | status=operating | len=396.0 dia=34.00 cap=10.76", "P1863 | Brega-Khoms Gas Pipeline | Mersa Brega->Khoms | status=operating | len=645.0 dia=34.00 cap=11.61", "P0484 | Wafa-Mellitah Gas Pipeline / Pipeline 1 aka=Western Libyan Gas Project | Wafa gas field->Mellitah Complex | status=operating | len=5246.0 dia=32 cap=13.0", "P1866 | Nasser-Brega Gas Pipeline | ?->Mersa Brega | status=operating | len=277.0 dia=36 cap=14.87", "P1865 | Tripoli-Mellitah Gas Pipeline | Tripoli->Mellitah | status=operating | len=158.0 dia=34.00 cap=16.99", "P1864 | Khoms-Tripoli Gas Pipeline | Khoms->Tripoli | status=operating | len=201.0 dia=34.00 cap=17.05", "P1857 | 103D-103A Gas Pipeline | ?->? | status=operating | len=41.0 dia=40.00 cap=17.84", "P1871 | Sahel-km-81.5 Gas Pipeline | ?->? | status=operating | len=79.0 dia=30.00 cap=19.54", "P1870 | Intesar-Sahel Gas Pipeline | ?->? | status=operating | len=129.0 dia=30.00 cap=19.82", "P0439 | Greenstream Gas Pipeline aka=Melita - Gela Sicily Pipeline, Melita TransGas | Mellitah Complex->Gela | status=operating | len=520.0 dia=36, 32, 10 cap=20.0", "P1872 | Km-91.5-Brega Gas Pipeline | ?->? | status=operating | len=184.0 dia=36, 16 cap=21.24", "P1855 | Bahr Assalam–Mellitah Gas Pipeline / Pipeline 1 | ?->Mellitah | status=operating | len=109.0 dia=36.00 cap=28.0", "P1867 | Attahaddy-km-91.5 Gas Pipeline | ?->? | status=operating | len=40.0 dia=30, 12 cap=28.32", "P1856 | Intesar-Brega Gas Pipeline | Intesar Oil field->Mersa Brega | status=operating | len=333.0 dia=42.00 cap=42.48", "P1728 | Mellitah-Gábes Pipeline | Mellitah->Gábes | status=cancelled | len=275.0 dia=24.00 cap=193.5", "P0483 | Libya Coastal Gas Pipeline | Mellitah Complex->Benghazi | status=operating | len=1164.0 dia=34 cap=604.0", "P6709 | Bouri-Bahr Asslam Gas Pipeline / Pipeline 2 | ?->? | status=operating | len=12.0 dia=4 cap=37213.0", "P6714 | Bu-Attifel-Intesar Gas Pipeline / Pipeline 2 | Bu-Attifel Oil Field->Intesar Oil field | status=operating | len=131.96 dia=10 cap=258425.0", "P6713 | Bahr Assalam–Mellitah Gas Pipeline / Pipeline 2 | ?->? | status=operating | len=109.0 dia=10 cap=465166.0", "P1858 | Bu-Attifel-Intesar Gas Pipeline / Pipeline 1 | Bu-Attifel Oil field->Intesar Oil field | status=operating | len=131.96 dia=34.00 cap=4134806.0", "P0482 | Defa-Brega Gas Pipeline | Defa gas field->Brega | status=operating | len=299.0 dia=? cap=?", "P3985 | Mellitah-BU-Attifel Gas Pipeline | Mellitah->Bu-Attifel Oil field | status=cancelled | len=? dia=4 cap=?", "P3987 | Intisar–Sarir Gas Pipeline | Intisar Oil field->Sarir field | status=operating | len=235.0 dia=20 cap=?", "P3988 | Fargh–Sarir Gas Pipeline | ?->? | status=operating | len=97.0 dia=? cap=?", "P6705 | Wafa-Mellitah Gas Pipeline / Pipeline 2 | Wafa Gas Field->Mellitah Complex | status=operating | len=524.65 dia=16 cap=?", "P6707 | Sirte Gulf PS Gas Pipeline | Brega->Sirte | status=construction | len=5.0 dia=24 cap=?", "P6708 | NC 41-Mellitah Gas Pipeline | ?->? | status=construction | len=130.0 dia=30 cap=?", "P6715 | E Structure-Mellitah Gas Pipeline | ?->? | status=construction | len=130.0 dia=32 cap=?", "P6716 | DP3–DP4–Sabratha Gas Pipeline / DP3–DP4 | ?->Sabratha platform | status=construction | len=8.5 dia=14 cap=?", "P7102 | Nigeria–Libya Gas Pipeline | ?->? | status=proposed | len=? dia=? cap=?", "P7617 | DP3–DP4–Sabratha Gas Pipeline / DP4–Sabratha aka=Bouri-Sabratha Gas Pipeline | Bouri Platform->? | status=construction | len=20.0 dia=10,4 cap=?"], "model": "sonnet", "strategies": [{"key": "news", "brief": "Industry + business news sweep for NEWLY ANNOUNCED Libya gas pipeline projects (roughly the last 3 years): \"Libya new gas pipeline <year>\", FID announcements, MOUs, FEED/EPC awards, tenders, capacity-expansion projects that include new pipe. Search Arabic too (attaqa.net, alwasat.ly, ean-libya.com, afrigatenews.net, Libya Herald/Observer/Update)."}, {"key": "regulators", "brief": "Regulator / ministry / NOC paper trail for Libya: National Oil Corporation (noc.ly) project announcements and subsidiary pages (Mellitah Oil & Gas, Sirte Oil Company, Waha, Zueitina, AGOCO), Ministry of Oil and Gas statements, GECOL (power) gas-supply projects, environmental permits. Much of this is Arabic-only."}, {"key": "operators", "brief": "Operator/sponsor project pages: Eni Libya (Mellitah complex, Bouri Gas Utilisation, Structures A&E), NOC and its subsidiaries, Mellitah Oil & Gas JV, Sirte Oil Company, plus EPC contractors active in Libya (Saipem, Rosetti Marino, Petrojet). Crawl project/infrastructure pages and annual reports for gas pipeline projects."}, {"key": "maps", "brief": "The MISSING-pipeline stance: Libya national gas grid maps, NOC/Sirte Oil network maps, gas master plans, OPEC/IEA/EIA and Arab Energy Organization infrastructure inventories, academic/World Bank Libya energy-sector reports — OPERATING or under-construction transmission lines GEM never captured (coastal line Brega–Khoms–Tripoli, field gathering-to-trunk links). A line on the national grid map with no roster match is exactly what this strategy exists to find."}, {"key": "crossborder", "brief": "Cross-border lines touching Libya in either direction: Greenstream (Mellitah–Gela, Italy) expansions/reversals; any Libya–Tunisia interconnector proposals; the Libya–Egypt corridor — KNOWN CONTEXT: Jan 2026 Petrojet–NOC MoU (Libya Energy & Economic Summit, Tripoli) is feasibility-study-only with no endpoints/route/capacity and was vetted MONITOR (below add-threshold) in GEM's Egypt discovery leg (batches/egypt-gas/staging/annual/discovery/vetted/libya-egypt-gas-pipeline.json — read it; your verdict must stay consistent with it unless NEWER concrete evidence exists); also the Nov 2022 NOC ADIPEC study floating Libya→Damietta and Libya→Greece lines, and the proposed Nigeria–Libya line already in GEM as P7102. Check Egyptian, Tunisian, Italian and Greek sources for anything terminating in Libya."}]}
if (!Array.isArray(A.roster) || !A.roster.length) {
  throw new Error("country-discovery needs args.roster — run scripts/build_discovery_context.py and pass its JSON as `args`.")
}
const REPO = A.repo
const STAGING = A.staging
const COMMODITY = A.commodity || 'gas'
const COUNTRY = A.country || ''
// Model is chosen by the orchestrator at dispatch time (standing rule: cheapest model
// genuinely good enough for this run) and passed via args.model; 'sonnet' is only the
// fallback when no choice is passed, not a pin.
const MODEL = A.model || 'sonnet'
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
  agent(searchContract(s), { label: `search:${s.key}`, phase: 'Search', agentType: 'general-purpose', model: MODEL })
))

phase('Consolidate')
const consolidated = await agent(consolidateContract, {
  label: 'consolidate', phase: 'Consolidate', agentType: 'general-purpose', schema: QUEUE_SCHEMA, model: MODEL,
})
if (!consolidated || !consolidated.queue.length) {
  log(`No candidates survived consolidation (matched: ${consolidated ? consolidated.matched : '?'}, dropped: ${consolidated ? consolidated.dropped : '?'}).`)
  return { queued: 0, matched: consolidated ? consolidated.matched : null }
}
log(`${consolidated.queue.length} candidates queued for vetting (${consolidated.matched || 0} matched to existing rows, ${consolidated.dropped || 0} dropped).`)

phase('Vet')
const vetted = await parallel(consolidated.queue.map(q => () =>
  agent(vetContract(q), { label: `vet:${q.slug}`, phase: 'Vet', agentType: 'general-purpose', model: MODEL })
))
const done = vetted.filter(Boolean).length
log(`Vetting complete: ${done}/${consolidated.queue.length}. Shards in ${STAGING}/discovery/vetted/ — next: scripts/merge_discovery_shards.py`)
return { queued: consolidated.queue.length, vetted: done, matched: consolidated.matched || 0 }
