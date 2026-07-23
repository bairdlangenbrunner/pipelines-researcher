export const meta = {
  name: 'egypt-operating-ref-research',
  description: 'Targeted ref-sweep research pass (Egypt gas): one subagent per PID brief fills/re-verifies gap [ref] cells to the >=2-independent target and writes ref_shards/<PID>.json. Read-and-stage only.',
  phases: [ { title: 'Research', detail: 'one ref-research subagent per pipeline brief' } ],
}

const A = {
 "repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher",
 "staging": "batches/staging/ref-sweep-gas-egypt-operating",
 "pids": [
  {
   "pid": "P0436",
   "name": "Arab Gas Pipeline"
  },
  {
   "pid": "P0462",
   "name": "Arish\u2013Ashkelon Pipeline"
  },
  {
   "pid": "P0474",
   "name": "Obaiyed-Amreya Northern Gas Pipeline"
  },
  {
   "pid": "P0476",
   "name": "Salam-Abu Gharadig Southern Gas Pipeline"
  },
  {
   "pid": "P0477",
   "name": "South Valley Gas Pipeline"
  },
  {
   "pid": "P3343",
   "name": "El Tina Gas Pipeline"
  },
  {
   "pid": "P3346",
   "name": "El Noubareya Gas Pipeline"
  },
  {
   "pid": "P3366",
   "name": "El Tina- Abu Sultan- New Administrative Capital Gas Pipeline"
  },
  {
   "pid": "P3659",
   "name": "Port Said - Arish Gas Pipeline"
  },
  {
   "pid": "P3928",
   "name": "Nubaria\u2013Sadat Gas Pipeline"
  },
  {
   "pid": "P3929",
   "name": "El Wasta\u2013Beni Suef Gas Pipeline"
  },
  {
   "pid": "P3930",
   "name": "New Administrative Capital\u2013Dahshur Gas Pipeline"
  },
  {
   "pid": "P3931",
   "name": "Amriya\u2013El Alamein Gas Pipeline"
  },
  {
   "pid": "P3932",
   "name": "Nooros\u2013Abu Madi\u2013El Gamil Gas Pipline"
  },
  {
   "pid": "P3934",
   "name": "Obaiyed-Amreya Northern Gas Pipeline"
  },
  {
   "pid": "P3935",
   "name": "Salam\u2013Matruh Terminal Gas Pipeline"
  },
  {
   "pid": "P3936",
   "name": "BED/AS\u2013Ameryia Gas Pipeline"
  },
  {
   "pid": "P3937",
   "name": "Badr El Din Spur Gas Pipelines"
  },
  {
   "pid": "P3938",
   "name": "Badr El Din Spur Gas Pipelines"
  },
  {
   "pid": "P3939",
   "name": "Abu Gharadig\u2013Dahshour (1) Gas Pipeline"
  },
  {
   "pid": "P5132",
   "name": "Zohr\u2013Al Gamil Pipelines"
  },
  {
   "pid": "P6032",
   "name": "Borg El Arab\u2013Midor Gas pipeline"
  },
  {
   "pid": "P6033",
   "name": "Damietta\u2013SEGAS Pipeline"
  },
  {
   "pid": "P6034",
   "name": "Hurghada\u2013Safaga Gas Pipeline"
  },
  {
   "pid": "P6035",
   "name": "Gamasa\u2013Veunsa Gas Pipeline"
  },
  {
   "pid": "P6036",
   "name": "Zohr\u2013Al Gamil Pipelines"
  },
  {
   "pid": "P6037",
   "name": "Al Gamil\u2013Damietta Gas Pipeline"
  },
  {
   "pid": "P6687",
   "name": "Obaiyed-Amreya Northern Gas Pipeline"
  },
  {
   "pid": "P6688",
   "name": "Shams-Obaiyed Gas Pipeline"
  },
  {
   "pid": "P6689",
   "name": "Abu Sennan Spur Gas Pipeline"
  },
  {
   "pid": "P6692",
   "name": "Qasr-Shams Gas Pipeline"
  },
  {
   "pid": "P6693",
   "name": "Salam Spurline Gas Pipeline"
  },
  {
   "pid": "P6697",
   "name": "South Valley Gas Pipeline"
  },
  {
   "pid": "P6698",
   "name": "South Valley Gas Pipeline"
  },
  {
   "pid": "P6699",
   "name": "South Valley Gas Pipeline"
  },
  {
   "pid": "P6700",
   "name": "South Valley Gas Pipeline"
  },
  {
   "pid": "P6701",
   "name": "South Valley Gas Pipeline"
  },
  {
   "pid": "P6702",
   "name": "South Valley Gas Pipeline"
  },
  {
   "pid": "P6703",
   "name": "Raven-Western Desert Cmplex Gas Pipeline"
  },
  {
   "pid": "P6704",
   "name": "Raven-Al Ameryia Gas Pipeline"
  },
  {
   "pid": "P7447",
   "name": "Denise Gas Pipeline"
  },
  {
   "pid": "P7482",
   "name": "Arab Gas Pipeline"
  },
  {
   "pid": "P7567",
   "name": "Idku-Abu Hummus Gas Pipeline"
  },
  {
   "pid": "P7572",
   "name": "Qarun Gas Pipeline"
  },
  {
   "pid": "P7574",
   "name": "New Administration Capital PS Gas Pipeline"
  },
  {
   "pid": "P7577",
   "name": "Baltim Field Gas Pipelines"
  },
  {
   "pid": "P7578",
   "name": "Baltim Field Gas Pipelines"
  },
  {
   "pid": "P7580",
   "name": "Mahmoudiah PS Gas Pipeline"
  },
  {
   "pid": "P7588",
   "name": "Edfu Gas Pipeline"
  },
  {
   "pid": "P7589",
   "name": "Framid Field Gas Pipeline"
  }
 ]
}

const S = A.staging
const REPO = A.repo

const contract = (p) => `You are a GEM pipeline reference researcher. Fill/re-verify the gap ref cells for ONE Egypt gas pipeline: ProjectID ${p.pid} (${p.name}).

cd ${REPO} first.

Read your brief: ${S}/ref_shards/_briefs/${p.pid}.json — it lists \`units\` (each a ref cell needing a working ref that supports the stated value) and \`seed_citations\` (gem.wiki outbound cites as leads — verify, never cite gem.wiki).

For EACH unit: find a source that supports its \`values\`, and produce a working, verified ref.

STANDING RULES (non-negotiable):
1. NEVER cite gem.wiki / globalenergymonitor.org / theodora.com / A Barrel Full / any wikidot.com page. Read for leads only.
2. NEVER fabricate a URL. If none verifies, mark the unit UNRESOLVED.
3. Verify EVERY url before citing: \`python scripts/url_verifier.py "<url>" "<expected substring>"\` — cite only if OK/200 AND it contains the expected token (a distinctive number/place/name; Arabic forms welcome). Try Wayback (https://web.archive.org/web/2023/<url>) for dead originals.
4. Corroborate with >=2 INDEPENDENT sources where possible (separate origins; not one wire reprinted; nothing tracing to GEM). tier: high = >=2 independent working+value-present; medium = 1 strong; low = 1 weak/partial/conflicting.
5. Search Arabic + regional/trade sources (Egypt Oil & Gas / egyptoil-gas.com, Enterprise Press, MEES, MEED, Zawya, Al-Ahram, Daily News Egypt, Egypt Today, Al Borsa, official GASCO / EGAS / Egyptian Petroleum Ministry pages, Pipeline & Gas Journal, Oil & Gas Journal, EIA, Offshore Technology, NS Energy).

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

// Resume 2026-07-13: only PIDs whose ref_shards/<PID>.json is not yet on disk (21/50 done previously).
const REF_REMAINING = new Set(["P3937","P6032","P6033","P6034","P6036","P6037","P6687","P6688","P6689","P6692","P6693","P6697","P6698","P6699","P6700","P6701","P6702","P6703","P6704","P7447","P7482","P7567","P7572","P7574","P7577","P7578","P7580","P7588","P7589"])
const REF_PIDS = A.pids.filter(p => REF_REMAINING.has(p.pid))

phase('Research')
log(`Targeted ref research: ${REF_PIDS.length} Egypt gas pipelines, one subagent each (Sonnet).`)
const results = await parallel(REF_PIDS.map(p => () =>
  agent(contract(p), { label: `refs:${p.pid}`, phase: 'Research', agentType: 'general-purpose', model: 'sonnet' })
))
const done = results.filter(Boolean).length
log(`Ref research complete: ${done}/${REF_PIDS.length} subagents returned. Shards in ${S}/ref_shards/`)
return { done, total: REF_PIDS.length }
