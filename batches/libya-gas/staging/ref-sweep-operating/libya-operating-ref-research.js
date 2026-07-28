export const meta = {
  name: 'libya-operating-ref-research',
  description: 'Targeted ref-sweep research pass (Libya gas): one subagent per PID brief fills/re-verifies gap [ref] cells to the >=2-independent target and writes ref_shards/<PID>.json. Read-and-stage only.',
  phases: [ { title: 'Research', detail: 'one ref-research subagent per pipeline brief' } ],
}

const A = {
 "repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher",
 "staging": "batches/libya-gas/staging/ref-sweep-operating",
 "pids": [
  {
   "pid": "P0439",
   "name": "Greenstream Gas Pipeline"
  },
  {
   "pid": "P0482",
   "name": "Defa-Brega Gas Pipeline"
  },
  {
   "pid": "P0483",
   "name": "Libya Coastal Gas Pipeline"
  },
  {
   "pid": "P0484",
   "name": "Wafa-Mellitah Gas Pipeline"
  },
  {
   "pid": "P1789",
   "name": "Khoms-Melita Pipeline"
  },
  {
   "pid": "P1855",
   "name": "Bahr Assalam–Mellitah Gas Pipeline"
  },
  {
   "pid": "P1856",
   "name": "Intesar-Brega Gas Pipeline"
  },
  {
   "pid": "P1857",
   "name": "103D-103A Gas Pipeline"
  },
  {
   "pid": "P1858",
   "name": "Bu-Attifel-Intesar Gas Pipeline"
  },
  {
   "pid": "P1859",
   "name": "Bouri-Bahr Assalam Gas Pipeline"
  },
  {
   "pid": "P1860",
   "name": "Waha-Nasser Gas Pipeline"
  },
  {
   "pid": "P1861",
   "name": "Farigh-Intesar Gas Pipeline"
  },
  {
   "pid": "P1862",
   "name": "Brega-Benghazi Gas Pipeline"
  },
  {
   "pid": "P1863",
   "name": "Brega-Khoms Gas Pipeline"
  },
  {
   "pid": "P1864",
   "name": "Khoms-Tripoli Gas Pipeline"
  },
  {
   "pid": "P1865",
   "name": "Tripoli-Mellitah Gas Pipeline"
  },
  {
   "pid": "P1866",
   "name": "Nasser-Brega Gas Pipeline"
  },
  {
   "pid": "P1867",
   "name": "Attahaddy-km-91.5 Gas Pipeline"
  },
  {
   "pid": "P1868",
   "name": "Km-81.5-Brega Gas Pipeline"
  },
  {
   "pid": "P1869",
   "name": "Raguba-Km-110 Gas Pipeline"
  },
  {
   "pid": "P1870",
   "name": "Intesar-Sahel Gas Pipeline"
  },
  {
   "pid": "P1871",
   "name": "Sahel-km-81.5 Gas Pipeline"
  },
  {
   "pid": "P1872",
   "name": "Km-91.5-Brega Gas Pipeline"
  },
  {
   "pid": "P1873",
   "name": "Jakhira-Intesar Gas Pipeline"
  },
  {
   "pid": "P3987",
   "name": "Intisar–Sarir Gas Pipeline"
  },
  {
   "pid": "P3988",
   "name": "Fargh–Sarir Gas Pipeline"
  },
  {
   "pid": "P6705",
   "name": "Wafa-Mellitah Gas Pipeline"
  },
  {
   "pid": "P6709",
   "name": "Bouri-Bahr Asslam Gas Pipeline"
  },
  {
   "pid": "P6713",
   "name": "Bahr Assalam–Mellitah Gas Pipeline"
  },
  {
   "pid": "P6714",
   "name": "Bu-Attifel-Intesar Gas Pipeline"
  }
 ]
}
const S = A.staging
const REPO = A.repo

const contract = (p) => `You are a GEM pipeline reference researcher. Fill/re-verify the gap ref cells for ONE Libya gas pipeline: ProjectID ${p.pid} (${p.name}).

cd ${REPO} first.

Read your brief: ${S}/ref_shards/_briefs/${p.pid}.json — it lists \`units\` (each a ref cell needing a working ref that supports the stated value) and \`seed_citations\` (gem.wiki outbound cites as leads — verify, never cite gem.wiki).

For EACH unit: find a source that supports its \`values\`, and produce a working, verified ref.

STANDING RULES (non-negotiable):
1. NEVER cite gem.wiki / globalenergymonitor.org / theodora.com / A Barrel Full / any wikidot.com page. Read for leads only.
2. NEVER fabricate a URL. If none verifies, mark the unit UNRESOLVED.
3. Verify EVERY url before citing: \`python scripts/url_verifier.py "<url>" "<expected substring>"\` — cite only if OK/200 AND it contains the expected token (a distinctive number/place/name; Arabic forms welcome). Try Wayback (https://web.archive.org/web/2023/<url>) for dead originals.
4. Corroborate with >=2 INDEPENDENT sources where possible (separate origins; not one wire reprinted; nothing tracing to GEM). tier: high = >=2 independent working+value-present; medium = 1 strong; low = 1 weak/partial/conflicting.
5. Search Arabic + regional/trade sources (Libya Herald, The Libya Observer, Libya Update, Al Wasat / alwasat.ly, Attaqa / attaqa.net, Ean Libya, official National Oil Corporation pages (noc.ly), Mellitah Oil & Gas, Sirte Oil Company, Zueitina Oil Company, Waha Oil Company, OPEC Annual Statistical Bulletin, MEED, Zawya, Pipeline & Gas Journal, Oil & Gas Journal, EIA, Offshore Technology, NS Energy, World Bank / AfDB reports).
6. KNOWN GOTCHA in this scope: many Sirte-Basin rows cite OPEC ASB 2012 Table 4.10 whose live opec.org PDF link is DEAD (redirects to the homepage). The table IS recoverable via Wayback Machine snapshots of the ASB PDF + \`pdftotext\` — a recovered Wayback ASB URL that names the pipeline and its specs is a valid ref. Other agents in this batch have already done this successfully; prefer a Wayback ASB URL over UNRESOLVED for those rows, and add a second independent non-OPEC source where one exists.

Write ${S}/ref_shards/${p.pid}.json = a single JSON object EXACTLY:
{
 "project_id": "${p.pid}",
 "pipeline_name": ${JSON.stringify(p.name)},
 "resolutions": [
   { "ref_col": "<e.g. Status [ref]>", "sheet_row": <int from brief>,
     "class_out": "REFS_ADDED|REVERIFIED|DEAD_LINK|UNRESOLVED",
     "proposed_refs": ["https://...verified..."],
     "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
     "tier": "high|medium|low", "independent": true, "source_language": "en|ar",
     "researcher_notes": "<what you searched, the value's support vs sources, any contradiction to flag>" }
 ]
}
One resolution object per unit in the brief. Before finishing, run \`python -c "import json; json.load(open('${S}/ref_shards/${p.pid}.json'))"\` to confirm it parses. Return ONLY a 2-line summary (units REFS_ADDED vs UNRESOLVED, any value contradictions found). The shard file is the deliverable.`

phase('Research')
log(`Targeted ref research: ${A.pids.length} Libya gas pipelines, one subagent each (Sonnet).`)
const results = await parallel(A.pids.map(p => () =>
  agent(contract(p), { label: `refs:${p.pid}`, phase: 'Research', agentType: 'general-purpose', model: 'sonnet' })
))
const done = results.filter(Boolean).length
log(`Ref research complete: ${done}/${A.pids.length} subagents returned. Shards in ${S}/ref_shards/`)
return { done, total: A.pids.length }
