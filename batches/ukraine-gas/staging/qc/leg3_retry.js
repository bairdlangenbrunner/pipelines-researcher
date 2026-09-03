export const meta = {
  name: 'ukraine-gas-leg3-retry',
  description: 'Leg-3 targeted research for the Ukraine gas handoff packet: five remaining briefs resolving the SPECIFIC flag on each flagged row (blank Operator on 22 of 30, length-vs-route ratio, endpoint/landfall country, date logic, multi-segment wiki union). Read-and-stage only.',
  phases: [
    { title: 'Wave 1', detail: 'western interconnectors, Ivatsevychi-Dolyna, Shebelinka-Slovyansk' },
    { title: 'Wave 2', detail: 'occupied southeast + Russian-side transit' },
  ],
}

const REPO = '/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher'
const S = 'batches/ukraine-gas/staging/qc'
const MODEL = (typeof args === 'object' && args && args.model) || 'sonnet'

// Deliberately run in waves of three. An eight-wide fan-out on this repo stalled
// wholesale earlier in this pass; three concurrent research agents ran healthily.
const WAVES = [
  ['western-interconnectors', 'ivatsevychi-dolyna', 'shebelinka-slovyansk'],
  ['occupied-southeast', 'russian-side-transit'],
]

const contract = (c) => `You are a meticulous GEM pipeline researcher working Leg 3 of the Ukraine gas
handoff QC packet. cd ${REPO} first.

## Read these two files BEFORE anything else
1. \`${S}/RESEARCH_PROTOCOL.md\` — the standing rules, the flag types, the deliverable shape, and a
   critical "READ THIS FIRST" section on why sourcing in Ukraine is unusual (short version: this is
   the 2nd-worst-cited scope in the tracker at 3.29% of ref cells filled, so an UNRESOLVED is a WEAK
   result here rather than the correct outcome it often is elsewhere — but the pipe is Soviet-era
   and per-string specs may genuinely not exist, so a documented dead end still beats a plausible
   number with no origin). It also carries seven gotchas — the operator sites 403 behind a WAF and a
   403 is NOT a deletion, moldovatransgaz.md fails TLS, and Ukrainian routes are 2-5 vertex
   SCHEMATICS so a drawn span is only a LOWER BOUND — that will cost you hours if you miss them.
   Follow it exactly.
2. \`${S}/rows/_briefs/${c}.json\` — YOUR brief. Its \`source_ladder\` field was written for this
   specific corridor and tells you which documents to reach for and what earlier legs already
   settled (do NOT re-litigate those). Its \`rows\` array carries each row's flags and current
   sheet values.

## Your job
Resolve the SPECIFIC flagged question on each row in your brief — not the whole row. A per-row deep
sweep, an in-development status review, a cancelled-status review, an eight-cluster redundancy
adjudication and two reconciliations (GulfPub, OSM) already ran over these rows; their findings are
staged elsewhere and re-researching them produces conflicting verdicts.

Work the brief as ONE research problem, not N independent lookups: these rows were grouped because
they share a corridor and a source ladder. That matters most for the blank-\`Operator\` flag, which
is 22 of the 30 worklist rows and is one question per COMPANY — establish who operates a corridor
once and apply it to every row in your brief, saying explicitly in each shard that you did. In
Ukraine that answer is usually Gas TSO of Ukraine LLC (GTSOU) post-2020 unbundling, but it is NOT
that for occupied-territory or Russian-side pipe, so name the entity operating the section THIS row
describes and cite a source that says so.

## Deliverable
Write ONE shard per row: \`${S}/rows/<PID>.json\`, exactly the shape given in the protocol's
"Deliverable" section — including \`"tab": "operators_owners"\` on any Operator/Owner fill. Write a
shard for EVERY row in your brief, including rows where everything came back UNRESOLVED — a
documented dead end is a result and a missing shard is not. Verify each parses with
\`python -c "import json; json.load(open('${S}/rows/<PID>.json'))"\`.

Return ONLY a 3-line summary: rows resolved vs unresolved, the single most useful source you found
(exact URL), and anything a human must decide. Your shard files are the deliverable.`

let done = 0
for (let i = 0; i < WAVES.length; i++) {
  const title = `Wave ${i + 1}`
  phase(title)
  log(`Leg 3 ${title}: ${WAVES[i].join(', ')}`)
  const out = await parallel(WAVES[i].map(c => () =>
    agent(contract(c), { label: `leg3:${c}`, phase: title, agentType: 'general-purpose', model: MODEL })
  ))
  done += out.filter(Boolean).length
}
const total = WAVES.flat().length
log(`Leg 3 complete: ${done}/${total} briefs returned.`)
return { briefs: done, total }
