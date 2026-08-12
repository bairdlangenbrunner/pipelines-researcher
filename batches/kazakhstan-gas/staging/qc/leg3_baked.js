export const meta = {
  name: 'kazakhstan-gas-leg3',
  description: 'Leg-3 targeted research for the Kazakhstan gas handoff packet: ten system briefs resolving the SPECIFIC flag on each flagged row (blank Operator, multi-segment wiki union, length-vs-route ratio, endpoint country, date logic). Read-and-stage only.',
  phases: [{ title: 'Research', detail: 'one subagent per system brief' }],
}

const REPO = '/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher'
const S = 'batches/kazakhstan-gas/staging/qc'
const BRIEFS = ['central-asia-center', 'bukhara-ural', 'bukhara-tashkent-bishkek-almaty',
  'central-asia-china', 'uzen-zhetybay-aktau', 'beineu-bozoy-shymkent', 'saryarka',
  'west-transit-gazprom', 'north-central-domestic', 'almaty-east-and-proposals']

const contract = (c) => `You are a meticulous GEM pipeline researcher working Leg 3 of the Kazakhstan gas
handoff QC packet. cd ${REPO} first.

## Read these two files BEFORE anything else
1. \`${S}/RESEARCH_PROTOCOL.md\` — the standing rules, the flag types, the deliverable shape, and a
   critical "READ THIS FIRST" section on why sourcing in Kazakhstan is unusual (short version: there
   is NO line-wise register, so an UNRESOLVED per-string spec can be the correct outcome — but
   operatorship IS documented and is worth real effort; plus three gotchas about adilet.zan.kz, the
   map appendices, and KMG annual-report vintages that will cost you hours if you miss them).
   Follow it exactly.
2. \`${S}/rows/_briefs/${c}.json\` — YOUR brief. Its \`source_ladder\` field was written for this
   specific system and tells you which documents to reach for and what earlier legs already settled
   (do NOT re-litigate those). Its \`rows\` array carries each row's flags and current sheet values.

## Your job
Resolve the SPECIFIC flagged question on each row in your brief — not the whole row. A per-row deep
sweep, an in-development status review, a cancelled-status review, an eleven-cluster redundancy
adjudication and two reconciliations (GulfPub, OSM) already ran over these rows; their findings are
staged elsewhere and re-researching them produces conflicting verdicts.

Work the brief as ONE research problem, not N independent lookups: these rows were grouped because
they are strings of one system sharing a source ladder. That matters most for the blank-\`Operator\`
flag, which is one question per COMPANY — establish who operates a system once and apply it to every
string row in your brief, saying explicitly in each shard that you did. It matters equally for the
multi-segment wiki unions: the wiki page describes the whole system, so decide ONCE whether a GEM row
should carry the system's value set or its own, and record that judgement in \`validity[]\`.

If your brief touches a multi-string system, read
\`notes/escalation-2026-08-11-kazakhstan-system-level-values-on-strings.md\` first — it is this
country's defining defect and several of its questions are already closed.

## Deliverable
Write ONE shard per row: \`${S}/rows/<PID>.json\`, exactly the shape given in the protocol's
"Deliverable" section — including \`"tab": "operators_owners"\` on any Operator/Owner fill. Write a
shard for EVERY row in your brief, including rows where everything came back UNRESOLVED — a
documented dead end is a result and a missing shard is not. Verify each parses with
\`python -c "import json; json.load(open('${S}/rows/<PID>.json'))"\`.

Return ONLY a 3-line summary: rows resolved vs unresolved, the single most useful source you found
(exact URL), and anything a human must decide. Your shard files are the deliverable.`

phase('Research')
log(`Leg 3: researching ${BRIEFS.length} Kazakhstan gas system briefs.`)
const out = await parallel(BRIEFS.map(c => () =>
  agent(contract(c), { label: `leg3:${c}`, phase: 'Research', agentType: 'general-purpose', model: 'sonnet' })
))
log(`Leg 3 complete: ${out.filter(Boolean).length}/${BRIEFS.length} briefs returned.`)
return { briefs: out.filter(Boolean).length, total: BRIEFS.length }
