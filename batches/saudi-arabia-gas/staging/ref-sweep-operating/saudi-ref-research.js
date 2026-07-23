export const meta = {
  name: 'saudi-targeted-ref-research',
  description: 'Targeted ref-sweep research pass (Saudi Arabia gas): one subagent per PID brief fills/re-verifies gap [ref] cells to the >=2-independent target and writes ref_shards/<PID>.json. Read-and-stage only.',
  phases: [ { title: 'Research', detail: 'one ref-research subagent per pipeline brief' } ],
}

const A = {
 "repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher",
 "staging": "batches/staging/ref-sweep-gas-saudi-arabia-operating",
 "pids": [
  {
   "pid": "P1898",
   "name": "UBTG-1-Berri Gas Pipeline"
  },
  {
   "pid": "P1899",
   "name": "UBTG-1-Berri 2 Gas Pipeline"
  },
  {
   "pid": "P1900",
   "name": "UBTG-km56-AY-1 KP916 Gas Pipeline"
  },
  {
   "pid": "P1901",
   "name": "UBTG-1km-Juanymah Gas Pipeline"
  },
  {
   "pid": "P1902",
   "name": "Safianayh-Ju’aymah Gas Pipeline"
  },
  {
   "pid": "P1903",
   "name": "AY–1 KP 943-Riyadh Gas Pipeline"
  },
  {
   "pid": "P1904",
   "name": "Tanajib-Berri Gas Pipeline"
  },
  {
   "pid": "P1905",
   "name": "Haradh-Uthmaniya Gas Pipeline"
  },
  {
   "pid": "P1906",
   "name": "Abqaiq-Berri Gas Pipeline"
  },
  {
   "pid": "P1907",
   "name": "Haradh-3-Uthmaniya Gas Pipeline"
  },
  {
   "pid": "P1908",
   "name": "UA-1-km199-Uthmaniya Gas Pipeline"
  },
  {
   "pid": "P1909",
   "name": "Juaymah-Jubail Gas Pipeline"
  },
  {
   "pid": "P1910",
   "name": "UBTG-1-km0-UBTG-1-km56 Gas Pipeline"
  },
  {
   "pid": "P1911",
   "name": "UBTG-1-km0-UBTG-1-km56 2 Gas Pipeline"
  },
  {
   "pid": "P1912",
   "name": "Hawiyah-UBTG-1-km0 Gas Pipeline"
  },
  {
   "pid": "P1913",
   "name": "Abqaiq-B-Shedgum Gas Pipeline"
  },
  {
   "pid": "P1914",
   "name": "Waqr Khuff-Haradh Gas Pipeline"
  },
  {
   "pid": "P1915",
   "name": "Hawiyah-Uthmniyah Gas Pipeline"
  },
  {
   "pid": "P1916",
   "name": "Qatif North-Berri Gas Pipeline"
  },
  {
   "pid": "P1917",
   "name": "Haradh Khuff-Hawiyah Gas Pipeline"
  },
  {
   "pid": "P1918",
   "name": "Haradh Khuff-Hawiyah 2 Gas Pipeline"
  },
  {
   "pid": "P1919",
   "name": "Haradh Khuff-Hawiyah 3 Gas Pipeline"
  },
  {
   "pid": "P1920",
   "name": "Tinat Kuff-Haradh Gas Pipeline"
  },
  {
   "pid": "P1921",
   "name": "Abu Ali-Berri Gas Pipeline"
  },
  {
   "pid": "P1922",
   "name": "Berri-Abu Ali Gas Pipeline"
  },
  {
   "pid": "P1923",
   "name": "Berri-Abu Ali 2 Gas Pipeline"
  },
  {
   "pid": "P1924",
   "name": "Aindar-Shedgum Gas Pipeline"
  },
  {
   "pid": "P1925",
   "name": "Depco-Abqaiq Gas Pipeline"
  },
  {
   "pid": "P3961",
   "name": "Madrakah–Al Hawiyah Gas Pipeline"
  },
  {
   "pid": "P3962",
   "name": "East–West Gas Pipeline (Saudi Arabia)"
  },
  {
   "pid": "P7544",
   "name": "Marjan GOSP-4 Gas Pipeline"
  },
  {
   "pid": "P7545",
   "name": "Marjan GOSP-4 Gas Pipeline"
  },
  {
   "pid": "P7711",
   "name": "Pump Station 06- Qassim PS Gas Pipeline"
  },
  {
   "pid": "P7712",
   "name": "Pump Station 07-Pump Station11 Gas Pipeline"
  },
  {
   "pid": "P7714",
   "name": "Shedgum- Riyadh Gas Pipeline 3"
  },
  {
   "pid": "P7715",
   "name": "Shedgum- Riyadh Gas Pipeline 2"
  },
  {
   "pid": "P7766",
   "name": "Hasbah-Wasit Gas Pipelines"
  },
  {
   "pid": "P7767",
   "name": "Hasbah-Wasit Gas Pipelines"
  },
  {
   "pid": "P7768",
   "name": "Abu Ali-Berri Gas Pipeline"
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
log(`Targeted ref research: ${A.pids.length} Saudi Arabia gas pipelines, one subagent each (Sonnet).`)
const results = await parallel(A.pids.map(p => () =>
  agent(contract(p), { label: `refs:${p.pid}`, phase: 'Research', agentType: 'general-purpose', model: 'sonnet' })
))
const done = results.filter(Boolean).length
log(`Ref research complete: ${done}/${A.pids.length} subagents returned. Shards in ${S}/ref_shards/`)
return { done, total: A.pids.length }
