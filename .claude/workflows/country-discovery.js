export const meta = {
  name: 'country-discovery',
  description: 'Country-scoped discovery of pipelines missing from GEM: parallel search-strategy agents surface candidates (new announcements AND older never-captured lines), a consolidator dedups + matches-to-existing against the full GEM roster, then one vetting agent per surviving candidate applies the add-threshold and researches a stageable row. Read-and-stage only, never auto-applies.',
  phases: [
    { title: 'Search', detail: 'one agent per search strategy (news / regulators / operators / maps / cross-border) + seed agents per args.seeds chunk' },
    { title: 'Consolidate', detail: 'dedup across strategies + match-to-existing FIRST + seed-ledger coverage gate' },
    { title: 'Vet', detail: 'one agent per surviving candidate — add-threshold + full row research' },
  ],
}

// args (from `python scripts/build_discovery_context.py --tracker <t> --country <C> --staging <dir>`):
//   { repo, staging, commodity, country, roster:[...], strategies?:[{key,brief}], seeds?, seedsOnly?, priorStaging? }
// tolerate a JSON-encoded string (some invocation paths stringify `args`)
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
if (!Array.isArray(A.roster) || !A.roster.length) {
  throw new Error("country-discovery needs args.roster — run scripts/build_discovery_context.py and pass its JSON as `args`.")
}
const REPO = A.repo
const STAGING = A.staging
const COMMODITY = A.commodity || 'gas'
const COUNTRY = A.country || ''
// Model is chosen by the orchestrator at dispatch time (standing rule: cheapest model
// genuinely good enough for this run) and passed via args.model; 'sonnet' is only the
// fallback when no choice is passed, not a pin. Per-phase overrides (args.modelSearch /
// modelConsolidate / modelVet) fall back to args.model — e.g. a top-tier consolidator
// (Cyrillic/translit matching against the roster) with cheaper search + vet agents.
const MODEL = A.model || 'sonnet'
const MODEL_SEARCH = A.modelSearch || MODEL
const MODEL_CONSOLIDATE = A.modelConsolidate || MODEL
const MODEL_VET = A.modelVet || MODEL
// args.scopeRule replaces the default transmission-only rule (e.g. a length threshold);
// args.extra is a block of run-specific context (territory rules, seeds, window) for every search agent.
const SCOPE_RULE = A.scopeRule || 'Transmission lines only — skip gathering/process/feeder lines and distribution networks.'
const EXTRA = A.extra ? `\n${A.extra}\n` : ''
const ROSTER = A.roster.join("\n")
// args.seeds = structured leads (e.g. OSM recon features) that MUST each end with a disposition in
// queue.json's seed_ledger: [{seed_id, name, km?, kind?, operator?, name_hint?}]. They get dedicated
// seed agents (chunks of args.seedChunk, default 8) instead of riding in `extra`, because a search
// agent handed a seed list reports the seeds it can cite and silently skips the rest (Russia D4/D5,
// 2026-09-30). args.seedsOnly = run only the seed agents (a coverage re-run).
// args.priorStaging = earlier run dirs for the same scope: a seed already decided there is
// recorded already_handled, not re-researched, and slugs must not collide with them.
const SEEDS = Array.isArray(A.seeds) ? A.seeds : []
const SEED_CHUNK = A.seedChunk || 8
const PRIOR = Array.isArray(A.priorStaging) ? A.priorStaging : []
const seedLine = (s) => `- ${s.seed_id} | ${s.name} | ${s.km ? `~${s.km} km merged OSM` : 'length unknown'}` +
  (s.kind ? ` | kind: ${s.kind}` : '') + (s.operator ? ` | operator: ${s.operator}` : '') +
  (s.name_hint ? ` | ${s.name_hint}` : '')
const seedChunks = []
for (let i = 0; i < SEEDS.length; i += SEED_CHUNK) seedChunks.push(SEEDS.slice(i, i + SEED_CHUNK))
const priorNote = PRIOR.length
  ? `\nEarlier runs for this scope (read their discovery/queue.json + discovery/vetted/*.json FIRST): ${PRIOR.join(', ')}.\n`
  : ''

const DEFAULT_STRATEGIES = [
  { key: 'news', brief: `Industry + business news sweep for NEWLY ANNOUNCED ${COUNTRY} ${COMMODITY} pipeline projects (roughly the last 3 years): "<country> new ${COMMODITY} pipeline <year>", FID announcements, MOUs, FEED/EPC awards, tenders, capacity-expansion projects that include new pipe. Search in-country languages too.` },
  { key: 'regulators', brief: `Regulator / ministry / TSO paper trail for ${COUNTRY}: national energy regulator filings and project inventories, environmental-permit applications, ministry project lists, TSO ten-year development plans (or the national equivalent — FERC-style dockets where they exist).` },
  { key: 'operators', brief: `Operator/sponsor project pages: identify the main midstream, TSO, and NOC players operating in ${COUNTRY} and crawl their project/infrastructure pages and annual reports for ${COMMODITY} pipeline projects.` },
  { key: 'maps', brief: `The MISSING-pipeline stance: ${COUNTRY} national ${COMMODITY} grid maps, TSO network maps, gas/energy master plans, IEA/EIA and national-statistics infrastructure inventories — OPERATING or under-construction transmission lines that GEM never captured (not just new announcements). A line on the national grid map with no roster match is exactly what this strategy exists to find.` },
  { key: 'crossborder', brief: `Cross-border lines touching ${COUNTRY} in either direction: interconnectors, import/export lines, transit corridors. Check the neighbouring countries' TSO/ministry project lists for lines that terminate in ${COUNTRY}.` },
]
const STRATEGIES = A.seedsOnly ? [] : (A.strategies || DEFAULT_STRATEGIES)

const LEDGER_SHAPE = `{ "seed_id": "<exact id from the list>", "name": "<seed name>",
    "disposition": "queued|matched|monitor|dropped|already_handled",
    "slug": "<candidate slug, when queued or already_handled via a vetted shard>",
    "matched_project_id": "<P#### when matched>",
    "reason": "<one line: what you found — length/sponsor/status, or why matched/dropped>",
    "evidence": [ { "url": "https://...verified...", "note": "..." } ] }`

const seedContract = (chunk, n) => `You are a GEM pipeline discovery researcher adjudicating SEED LEADS for ${COUNTRY} (${COMMODITY}).
Each seed below is a reference-dataset feature (e.g. an OpenStreetMap trace, merged by name) with no
GEM row. A reference route is presumptively REAL pipe — either geometry GEM is missing (an existing
row under another name) or a pipeline GEM is missing. OSM/GulfPub is a LEAD source, never a [ref].

cd ${REPO} first.
${EXTRA}${priorNote}
## Your seeds (${chunk.length}) — EVERY ONE must get exactly one ledger entry
${chunk.map(seedLine).join('\n')}

## The existing GEM roster (ALL statuses)
${ROSTER}

## For each seed, in order
1. already_handled: an earlier run (above) already queued/vetted/matched/dropped it → record that
   (slug or PID) and move on — do NOT re-research.
2. matched: it is an existing roster row under another name, or a string/section/loop of one (the
   I/II/III string convention) → matched_project_id + reason (a separate string with its own sourced
   specs goes to Update as a split, still recorded matched with that note).
3. Otherwise search for it (in-country language first: the Cyrillic name, "газопровод-отвод к ГРС …",
   operator LPUMG pages, regional gasification programmes, Glavgosekspertiza, tender sites) for
   length, sponsor/operator, status and year.
   - ${SCOPE_RULE}
   - sourced length >= 25 km and real evidence → candidate (write it to your found file, below)
     and ledger disposition "queued" (the consolidator assigns the final slug).
   - under 25 km, or length you cannot source → "monitor" with what you found.
   - not a gas pipeline / an urban distribution network / out of scope → "dropped" with why.
Rules: NEVER cite gem.wiki / globalenergymonitor.org / theodora / wikidot / abarrelfull / yingdodo;
NEVER fabricate a URL; verify every URL with \`python scripts/url_verifier.py "<url>" "<expected substring>"\`
and emit only OK + token-present links. Save downloads under \`${STAGING}/work/\`. Budget: about one
focused search per seed when the first result settles it — don't over-research monitor/dropped ones.

## Output — write a file, then return a summary
Write ${STAGING}/discovery/found_seeds-${n}.json EXACTLY shaped:
{ "strategy": "seeds-${n}",
  "candidates": [ { "name": "...", "aka": ["<Cyrillic name>", "..."], "seed_ids": ["<seed_id>"],
      "sponsor": "...", "from": "...", "to": "...", "status_guess": "...",
      "evidence": [ { "url": "https://...verified...", "date": "YYYY-MM", "note": "..." } ],
      "why_maybe_new": "..." } ],
  "seed_ledger": [ ${LEDGER_SHAPE} ] }
seed_ledger MUST hold all ${chunk.length} seed_ids. Validate with
\`python -c "import json; d=json.load(open('${STAGING}/discovery/found_seeds-${n}.json')); print(len(d['seed_ledger']))"\`.
Return ONLY a 2-line summary (disposition counts, strongest lead).`

const searchContract = (s) => `You are a GEM pipeline discovery researcher. Find ${COMMODITY} TRANSMISSION pipelines in/touching
${COUNTRY} that are MISSING from GEM's tracker. Your single search angle for this pass:

${s.brief}

cd ${REPO} first.
${EXTRA}${priorNote}
## The existing GEM roster (ALL statuses) — a candidate matching one of these rows is NOT a discovery
${ROSTER}

## Rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, or any wikidot.com page (read for
   leads only). NEVER fabricate a URL.
2. Verify every URL you emit: \`python scripts/url_verifier.py "<url>" "<expected substring>"\` —
   emit only OK/200 + token-present links.
   Save any downloaded file (curl -o, PDFs, pdftotext output) under \`${STAGING}/work/\` (gitignored),
   never the repo root.
3. ${SCOPE_RULE}
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
    seed_ledger: { type: 'array', items: { type: 'object', properties: {
      seed_id: { type: 'string' }, disposition: { type: 'string' } }, required: ['seed_id', 'disposition'] } },
  },
  required: SEEDS.length ? ['queue', 'seed_ledger'] : ['queue'],
}

const seedLedgerClause = SEEDS.length ? `
4. SEED LEDGER (mandatory — ${SEEDS.length} seeds): queue.json must carry "seed_ledger" with exactly one
   entry per seed_id below, final after dedup/match. Start from the found_seeds-*.json ledgers; a seed
   whose candidate you queued → "queued" + that slug; whose candidate you matched → "matched" + PID;
   whose candidate you dropped as a duplicate → "queued"/"matched" with the surviving slug/PID.
   Keep each seed agent's reason + evidence. A seed no file mentions: adjudicate it yourself
   (match-to-existing against the roster at minimum) — never leave one out. Entry shape:
   ${LEDGER_SHAPE}
   Seed ids: ${SEEDS.map(s => s.seed_id).join(', ')}
   Slugs must not collide with earlier runs' vetted shards${PRIOR.length ? ` (${PRIOR.join(', ')})` : ''}.` : ''

const consolidateContract = `You are the GEM discovery consolidator for ${COUNTRY} (${COMMODITY}).
cd ${REPO} first. Read every ${STAGING}/discovery/found_*.json (strategy outputs) and
${STAGING}/discovery_context.json (the full existing-row context).

For the union of all candidates:
1. DEDUP across strategies — the same physical project found by two strategies is ONE candidate
   (merge their evidence lists).
2. MATCH-TO-EXISTING FIRST (Discovery SOP): compare each candidate against the existing rows
   (names, other_names, endpoints, specs). A likely match to an existing ProjectID is NOT a
   discovery — record it as matched (candidate name -> OtherEnglishNames suggestion for that PID).
3. The survivors form the vetting queue. Give each a short kebab-case slug (filesystem-safe).${seedLedgerClause}
${priorNote}
Write ${STAGING}/discovery/queue.json:
{ "queue":   [ { "slug": "...", "name": "...", "strategies": ["news"], "note": "<1-line why new>",
                 "evidence": [ {"url":"...","date":"...","note":"..."} ] } ],
  "matched": [ { "name": "<candidate>", "matched_project_id": "P####", "reason": "...",
                 "other_names_suggestion": "<name to add>", "evidence": [ ... ] } ],
  "dropped": [ { "name": "...", "reason": "<duplicate-of-candidate / not transmission / no evidence>" } ]${SEEDS.length ? `,
  "seed_ledger": [ ...one entry per seed_id... ]` : ''} }
Then ALSO return { queue: [{slug, name, note}], matched: <n>, dropped: <n>${SEEDS.length ? ', seed_ledger: [{seed_id, disposition}]' : ''} } as your structured
output (the queue drives the next fan-out).`

const repairContract = (missing) => `You are the GEM discovery consolidator for ${COUNTRY} (${COMMODITY}), repair pass.
cd ${REPO} first. ${STAGING}/discovery/queue.json's seed_ledger has NO entry for these ${missing.length} seeds:
${missing.map(seedLine).join('\n')}
${priorNote}
Adjudicate each one now (roster below; search in-country language; url_verifier every URL; never cite
gem.wiki/GEM/theodora/wikidot/abarrelfull/yingdodo; never fabricate a URL). ${SCOPE_RULE}
A sourced >= 25 km line not in the roster → append a queue item to queue.json and ledger it "queued".
Then APPEND one ledger entry per seed to queue.json's seed_ledger (keep the file valid JSON):
${LEDGER_SHAPE}

## The existing GEM roster (ALL statuses)
${ROSTER}

Return { queue: [<only the items you appended: {slug, name, note}>], seed_ledger: [{seed_id, disposition}] }.`

const vetContract = (q) => `You are a skeptical GEM discovery researcher. Vet ONE candidate ${COUNTRY} ${COMMODITY}
pipeline for addition to the GEM tracker: "${q.name}" (slug: ${q.slug}).
${q.note ? `Consolidator note: ${q.note}` : ''}

cd ${REPO} first. Read your candidate's entry (evidence URLs included) in
${STAGING}/discovery/queue.json and the existing-row context in ${STAGING}/discovery_context.json.
${priorNote}
## Rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org / theodora / wikidot. NEVER fabricate a URL.
2. Every URL through \`python scripts/url_verifier.py "<url>" "<expected substring>"\` before citing.
   Save any downloaded file (curl -o, PDFs, pdftotext output) under \`${STAGING}/work/\` (gitignored),
   never the repo root.
3. One validated source (names the pipeline, states the value) suffices; >=2 INDEPENDENT preferred (not one wire story reprinted). Search in-country languages.
4. RE-CHECK match-to-existing yourself before anything else — if this is really an existing GEM row
   under another name, class it matched_existing and STOP researching a new row.
5. New owner/operator entities: \`python scripts/entity_lookup.py "<owner>" "${COUNTRY}"\` first.

## The add-threshold (Discovery SOP §3) — ALL THREE or it is monitor, not new_row:
(a) an identified sponsor; (b) at least country + region/endpoints; (c) a concrete step
(MOU signed, FEED/EPC award, permit applied, tender issued, FID). Early rumor -> "monitor".
${A.vetRule || ''}

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
log(`Discovery sweep for ${COUNTRY} (${COMMODITY}): ${STRATEGIES.length} strategy agents + ${seedChunks.length} seed agents (${SEEDS.length} seeds) vs a roster of ${A.roster.length} existing rows.`)
await parallel([
  ...STRATEGIES.map(s => () =>
    agent(searchContract(s), { label: `search:${s.key}`, phase: 'Search', agentType: 'general-purpose', model: MODEL_SEARCH })),
  ...seedChunks.map((c, i) => () =>
    agent(seedContract(c, i + 1), { label: `seeds:${i + 1}`, phase: 'Search', agentType: 'general-purpose', model: MODEL_SEARCH })),
])

phase('Consolidate')
const consolidated = await agent(consolidateContract, {
  label: 'consolidate', phase: 'Consolidate', agentType: 'general-purpose', schema: QUEUE_SCHEMA, model: MODEL_CONSOLIDATE,
})
if (!consolidated) {
  log('Consolidator returned nothing.')
  return { queued: 0, matched: null }
}
// Seed coverage gate: every seed_id ends with a disposition, or the run says which did not.
let unadjudicated = []
if (SEEDS.length) {
  const have = new Set((consolidated.seed_ledger || []).map(e => e.seed_id))
  const missing = SEEDS.filter(s => !have.has(s.seed_id))
  if (missing.length) {
    log(`Seed ledger is missing ${missing.length}/${SEEDS.length} seeds — running one repair agent.`)
    const repaired = await agent(repairContract(missing), {
      label: 'consolidate:repair', phase: 'Consolidate', agentType: 'general-purpose', schema: QUEUE_SCHEMA, model: MODEL_CONSOLIDATE,
    })
    if (repaired) {
      for (const e of (repaired.seed_ledger || [])) have.add(e.seed_id)
      consolidated.queue.push(...(repaired.queue || []))
    }
    unadjudicated = SEEDS.filter(s => !have.has(s.seed_id)).map(s => s.seed_id)
    if (unadjudicated.length) log(`STILL UNADJUDICATED (${unadjudicated.length}): ${unadjudicated.join(', ')}`)
  } else {
    log(`Seed ledger complete: ${SEEDS.length}/${SEEDS.length} seeds dispositioned.`)
  }
}
if (!consolidated.queue.length) {
  log(`No candidates survived consolidation (matched: ${consolidated.matched}, dropped: ${consolidated.dropped}).`)
  return { queued: 0, matched: consolidated.matched, seeds_unadjudicated: unadjudicated }
}
log(`${consolidated.queue.length} candidates queued for vetting (${consolidated.matched || 0} matched to existing rows, ${consolidated.dropped || 0} dropped).`)

phase('Vet')
const vetted = await parallel(consolidated.queue.map(q => () =>
  agent(vetContract(q), { label: `vet:${q.slug}`, phase: 'Vet', agentType: 'general-purpose', model: MODEL_VET })
))
const done = vetted.filter(Boolean).length
log(`Vetting complete: ${done}/${consolidated.queue.length}. Shards in ${STAGING}/discovery/vetted/ — next: scripts/merge_discovery_shards.py`)
return { queued: consolidated.queue.length, vetted: done, matched: consolidated.matched || 0, seeds_unadjudicated: unadjudicated }
