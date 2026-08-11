export const meta = {
  name: 'india-gas-leg3',
  description: 'Leg-3 targeted research for the India gas handoff packet: twelve source-ladder briefs resolving the SPECIFIC flag on each flagged row (blank Operator, length-vs-route ratio, date logic, endpoint country). Read-and-stage only.',
  phases: [{ title: 'Research', detail: 'one subagent per source-ladder brief' }],
}

const REPO = '/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher'
const S = 'batches/india-gas/staging/qc'
const BRIEFS = ['gail-hvj-system', 'north-trunk-delhi-ncr', 'gail-west-coast-kkbmpl',
  'gail-east-jhbdpl', 'gail-regional-networks', 'rajasthan-and-cancelled-gail',
  'gspl-gujarat-grids', 'bhatinda-corridor', 'dahej-cluster', 'ongc-offshore-west',
  'east-coast-and-h-energy', 'northeast-and-crossborder']

const contract = (c) => `You are a meticulous GEM pipeline researcher working Leg 3 of the India gas
handoff QC packet. cd ${REPO} first.

## Read these two files BEFORE anything else
1. \`${S}/RESEARCH_PROTOCOL.md\` — the standing rules, the flag types, the deliverable shape, and a
   critical "READ THIS FIRST" section on why sourcing in India is unusual (short version: unlike
   Pakistan, the sources EXIST and were simply never cited, and the PNGRB NGPL MIS register is the
   unlock). Follow it exactly.
2. \`${S}/rows/_briefs/${c}.json\` — YOUR brief. Its \`source_ladder\` field was written for this
   specific group and tells you which documents to reach for and what earlier legs already settled
   (do NOT re-litigate those). Its \`rows\` array carries each row's flags and current sheet values.

## Your job
Resolve the SPECIFIC flagged question on each row in your brief — not the whole row. A per-row deep
sweep, an in-development status review, a cancelled-status review, a redundancy adjudication, a
PNGRB register crosswalk and two reconciliations (GulfPub, OSM) already ran over these rows; their
findings are staged elsewhere and re-researching them produces conflicting verdicts.

Work the brief as ONE research problem, not N independent lookups: these rows were grouped because
they share a source ladder. That matters most for the blank-\`Operator\` flag, which is one question
per COMPANY — establish who operates a system once and apply it to every segment row in your brief,
saying explicitly in each shard that you did.

Before searching, read \`batches/india-gas/staging/register-crosswalk/staged_resolutions.json\` for
your PIDs — the PNGRB register may already answer part of your question.

## Deliverable
Write ONE shard per row: \`${S}/rows/<PID>.json\`, exactly the shape given in the protocol's
"Deliverable" section — including \`"tab": "operators_owners"\` on any Operator/Owner fill. Write a
shard for EVERY row in your brief, including rows where everything came back UNRESOLVED — a
documented dead end is a result and a missing shard is not. Verify each parses with
\`python -c "import json; json.load(open('${S}/rows/<PID>.json'))"\`.

Return ONLY a 3-line summary: rows resolved vs unresolved, the single most useful source you found
(exact URL), and anything a human must decide. Your shard files are the deliverable.`

phase('Research')
log(`Leg 3: researching ${BRIEFS.length} India gas source-ladder briefs.`)
const out = await parallel(BRIEFS.map(c => () =>
  agent(contract(c), { label: `leg3:${c}`, phase: 'Research', agentType: 'general-purpose', model: 'sonnet' })
))
log(`Leg 3 complete: ${out.filter(Boolean).length}/${BRIEFS.length} briefs returned.`)
return { briefs: out.filter(Boolean).length, total: BRIEFS.length }
