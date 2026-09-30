export const meta = {
  name: 'us-gas-leg3',
  description: 'Leg-3 targeted research for the United States gas handoff packet: sixteen system briefs resolving the SPECIFIC flag on each of the 91 rows in the B/D/E cut (blank/stale Operator, candidate Diameter and Capacity fills, date logic, hard route-geometry flags). Read-and-stage only; never writes the live sheet or the routes repo.',
  phases: [{ title: 'Research', detail: 'one subagent per system brief' }],
}

const REPO = '/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher'
const S = 'batches/united-states-gas/staging/qc'
const BRIEFS = ['transco', 'gulf-south', 'williams-west', 'leap', 'energy-transfer-tx',
  'kinder-morgan', 'tc-energy', 'enbridge-northeast', 'permian-mexico', 'whitewater-permian',
  'appalachian-east', 'florida-gas', 'lng-feeders', 'permian-gathering', 'misc-systems',
  'alaska']

const contract = (c) => `You are a meticulous GEM pipeline researcher working Leg 3 of the United States gas
handoff QC packet. cd ${REPO} first.

## Read these two files BEFORE anything else
1. \`${S}/RESEARCH_PROTOCOL.md\` — the standing rules, the flag types, the deliverable shape, and a
   critical "READ THIS FIRST" section on why sourcing in the US is unusual. Short version: the US is
   the INVERSE of Kazakhstan — for a FERC-jurisdictional interstate row the FERC eLibrary
   environmental assessment states every loop's length in miles and diameter in inches, so an
   UNRESOLVED spec is almost always "nobody looked"; but roughly half these rows are INTRASTATE and
   are not in eLibrary at all by statute, where an eLibrary miss is evidence of nothing. It also
   carries seven gotchas — units (miles/inches vs the tracker's km/mm) being the single largest
   false-negative source in this country, and the compression-only-expansion rule that turns many
   Diameter flags into confirmations rather than fills. Follow it exactly.
2. \`${S}/rows/_briefs/${c}.json\` — YOUR brief. Its \`source_ladder\` field was written for this
   specific system and tells you which documents to reach for, whether your rows are
   FERC-jurisdictional or intrastate, and what earlier legs already settled (do NOT re-litigate
   those). Its \`rows\` array carries each row's flags and current sheet values.

## Your job
Resolve the SPECIFIC flagged question on each row in your brief — not the whole row. Twelve prior
deep-sweep batches already ran over these rows: 764 concerns, 1,547 corroborated fills, ~3,900 ref
records and 1,252 validity verdicts are staged elsewhere, and re-researching them produces
conflicting verdicts.

Work the brief as ONE research problem, not N independent lookups: these rows were grouped because
they are strings or projects of one system sharing a source ladder. That matters most for the
\`Operator\` flag, which is one question per COMPANY — establish who operates a system once and
apply it to every row in your brief, saying explicitly in each shard that you did. It matters
equally for the Diameter flags: one FERC environmental assessment usually answers every project row
in a brief at once, and one merger event (Energy Transfer/Enable, ONEOK/Magellan,
Williams/MountainWest, Berkshire/EGTS) usually answers every Operator flag at once.

## Deliverable
Write ONE shard per row: \`${S}/rows/<PID>.json\`, exactly the shape given in the protocol's
"Deliverable" section — including \`"tab": "operators_owners"\` on any Operator/Owner fill, and the
REQUIRED \`fields\` array on every \`validity[]\` record. Write a shard for EVERY row in your brief,
including rows where everything came back UNRESOLVED — a documented dead end is a result and a
missing shard is not.

Before you finish, run all three gates for EVERY row in your brief and fix anything they report:
  python3 -c "import json; json.load(open('${S}/rows/<PID>.json'))"
  python3 ${S}/check_flag_coverage.py --pid <PID>
  python3 scripts/audit_shard.py ${S}/rows/<PID>.json
A non-zero exit is a defect to fix in place, not a result to report.

Return ONLY a 3-line summary: rows resolved vs unresolved, the single most useful source you found
(exact URL), and anything a human must decide. Your shard files are the deliverable.`

phase('Research')
log(`Leg 3: researching ${BRIEFS.length} US gas system briefs (91 rows, 104 flags).`)
const out = await parallel(BRIEFS.map(c => () =>
  agent(contract(c), { label: `leg3:${c}`, phase: 'Research', agentType: 'general-purpose', model: 'sonnet' })
))
log(`Leg 3 complete: ${out.filter(Boolean).length}/${BRIEFS.length} briefs returned.`)
return { briefs: out.filter(Boolean).length, total: BRIEFS.length }
