export const meta = {
  name: 'saudi-annual-targeted-ref-research',
  description: 'Targeted ref-sweep research pass (Saudi Arabia gas): one subagent per PID brief fills/re-verifies gap [ref] cells to the >=2-independent target and writes ref_shards/<PID>.json. Read-and-stage only.',
  phases: [ { title: 'Research', detail: 'one ref-research subagent per pipeline brief' } ],
}

const A = {
 "repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher",
 "staging": "batches/staging/annual-gas-saudi-arabia",
 "pids": [
  {
   "pid": "P5854",
   "name": "Wafra-Station 171 Gas Pipeline"
  },
  {
   "pid": "P6717",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6718",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6719",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6720",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6721",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6722",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6723",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6724",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6725",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6726",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6727",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6728",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6729",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6730",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6731",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6732",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6733",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6734",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6735",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6736",
   "name": "MGS III Gas Pipelines"
  },
  {
   "pid": "P6737",
   "name": "MGS III Gas Pipelines"
  }
 ]
}
const S = A.staging
const REPO = A.repo

const contract = (p) => `You are a GEM pipeline reference researcher. Fill/re-verify the gap ref cells for ONE Saudi Arabia gas pipeline: ProjectID ${p.pid} (${p.name}).

cd ${REPO} first.

Read your brief: ${S}/ref_shards/_briefs/${p.pid}.json — it lists \`units\` (each a ref cell needing a working ref that supports the stated value) and \`seed_citations\` (gem.wiki outbound cites as leads — verify, never cite gem.wiki).

For EACH unit: find a source that supports its \`values\`, and produce a working, verified ref.

STANDING RULES (non-negotiable):
1. NEVER cite gem.wiki / globalenergymonitor.org / theodora.com / A Barrel Full / any wikidot.com page. Read for leads only.
2. NEVER fabricate a URL. If none verifies, mark the unit UNRESOLVED.
3. Verify EVERY url before citing: \`python scripts/url_verifier.py "<url>" "<expected substring>"\` — cite only if OK/200 AND it contains the expected token (a distinctive number/place/name; Arabic forms welcome). Try Wayback (https://web.archive.org/web/2023/<url>) for dead originals.
4. Corroborate with >=2 INDEPENDENT sources where possible (separate origins; not one wire reprinted; nothing tracing to GEM). tier: high = >=2 independent working+value-present; medium = 1 strong; low = 1 weak/partial/conflicting.
5. Search Arabic + regional/trade sources (Saudi Aramco annual reports & 20-F/prospectus filings, Argaam, Saudi Gazette, Arab News, Al-Jazirah, MEED, MEES, Zawya, Pipeline & Gas Journal, Oil & Gas Journal, EIA, Offshore Technology).

Write ${S}/ref_shards/${p.pid}.json = a single JSON object EXACTLY:
{
 "project_id": "${p.pid}",
 "pipeline_name": ${JSON.stringify(p.name)},
 "resolutions": [
   { "ref_col": "<e.g. Status [ref]>", "sheet_row": <int from brief>,
     "class_out": "REFS_ADDED|UNRESOLVED",
     "proposed_refs": ["https://...verified..."],
     "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
     "tier": "high|medium|low", "independent": true, "source_language": "en|ar",
     "researcher_notes": "<what you searched, the value's support vs sources, any contradiction to flag>" }
 ]
}
One resolution object per unit in the brief. Before finishing, run \`python -c "import json; json.load(open('${S}/ref_shards/${p.pid}.json'))"\` to confirm it parses. Return ONLY a 2-line summary (units REFS_ADDED vs UNRESOLVED, any value contradictions found). The shard file is the deliverable.`

phase('Research')
log(`Targeted ref research: ${A.pids.length} Saudi Arabia gas pipelines, one subagent each (Opus).`)
const results = await parallel(A.pids.map(p => () =>
  agent(contract(p), { label: `refs:${p.pid}`, phase: 'Research', agentType: 'general-purpose', model: 'opus' })
))
const done = results.filter(Boolean).length
log(`Ref research complete: ${done}/${A.pids.length} subagents returned. Shards in ${S}/ref_shards/`)
return { done, total: A.pids.length }
