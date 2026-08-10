export const meta = {
  name: 'pakistan-gas-leg3',
  description: 'Leg-3 targeted research for the Pakistan gas handoff packet: ten corridor briefs resolving the SPECIFIC flag on each of 50 rows (commissioning year, length-vs-route, transnational endpoint). Read-and-stage only.',
  phases: [{ title: 'Research', detail: 'one subagent per corridor brief' }],
}

const REPO = '/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher'
const S = 'batches/pakistan-gas/staging/qc'
const CLUSTERS = ['ssgc-sindh', 'sngpl-sindh-feeders', 'rlng-punjab', 'punjab-central',
  'punjab-north', 'potohar-kp', 'length-sindh', 'length-qadirpur', 'length-punjab-kp',
  'transnational-endpoints']

const contract = (c) => `You are a meticulous GEM pipeline researcher working Leg 3 of the Pakistan gas
handoff QC packet. cd ${REPO} first.

## Read these two files BEFORE anything else
1. \`${S}/RESEARCH_PROTOCOL.md\` — the standing rules, the flag types, the deliverable shape,
   and a critical "READ THIS FIRST" section on why sourcing in Pakistan is unusual. Follow it exactly.
2. \`${S}/rows/_briefs/${c}.json\` — YOUR brief. It has a \`context\` field written specifically for
   this corridor (read it carefully — it tells you what is already staged and must NOT be
   re-litigated), and a \`rows\` array with each row's flags and current sheet values.

## Your job
Resolve the SPECIFIC flagged question on each row in your brief — not the whole row. A 63-agent
deep sweep, a cancelled-status review and two reconciliations already ran over these rows; their
findings are staged elsewhere and re-researching them produces conflicting verdicts.

Work the corridor as ONE research problem, not N independent lookups: the rows in your brief were
grouped because they share a source ladder. A single SNGPL/SSGC annual report, OGRA licence
schedule or engineering document may answer several of them at once — that is the intended win.

## Deliverable
Write ONE shard per row: \`${S}/rows/<PID>.json\`, exactly the shape given in the protocol's
"Deliverable" section. Write a shard for EVERY row in your brief, including rows where everything
came back UNRESOLVED — a documented dead end is a result and a missing shard is not. Verify each
parses with \`python -c "import json; json.load(open('${S}/rows/<PID>.json'))"\`.

Return ONLY a 3-line summary: rows resolved vs unresolved, the single most useful source you
found (exact URL), and anything a human must decide. Your shard files are the deliverable.`

phase('Research')
log(`Leg 3: researching ${CLUSTERS.length} Pakistan gas corridor briefs (50 flagged rows).`)
const out = await parallel(CLUSTERS.map(c => () =>
  agent(contract(c), { label: `leg3:${c}`, phase: 'Research', agentType: 'general-purpose', model: 'sonnet' })
))
log(`Leg 3 complete: ${out.filter(Boolean).length}/${CLUSTERS.length} briefs returned.`)
return { briefs: out.filter(Boolean).length, total: CLUSTERS.length }
