export const meta = {
  name: 'iraq-gas-operating-deepsweep',
  description: 'Iraq gas OPERATING deep sweep: per-pipeline critical re-audit (existence/classification/duplicate/attribution/spec) + ref confirmation + blank-value fills + corridor/endpoint route suggestions. Read-and-stage only.',
  phases: [ { title: 'Audit', detail: 'one subagent per operating gas pipeline' } ],
}

const A = {
 "repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher",
 "staging": "batches/staging/ref-sweep-gas-iraq-operating",
 "commodity": "gas",
 "country": "Iraq",
 "pids": [
  "P1841",
  "P1842",
  "P1845",
  "P1846",
  "P1847",
  "P1848",
  "P1850",
  "P1851",
  "P1852",
  "P1853",
  "P2231",
  "P2232",
  "P2233",
  "P2234",
  "P4054",
  "P4058",
  "P4061",
  "P4062",
  "P4064",
  "P4065",
  "P4066",
  "P4067",
  "P4068",
  "P4401",
  "P5855",
  "P5856",
  "P6823",
  "P6824",
  "P6826",
  "P6827",
  "P7435",
  "P7457",
  "P7468",
  "P7471",
  "P7474",
  "P7477"
 ],
 "roster": [
  "P1841 | Baiji-K3-Al Kaem Gas Pipeline | ?->Al Anbar | len=431.0 dia=16.00 cap=2.41 | status=operating | updated=2022-07-26",
  "P1842 | Baiji-Al Mushraq Gas Pipeline | ?->Mosul | len=211.0 dia=18.00 cap=160.00 | status=operating | updated=2024-08-15",
  "P1845 | Taji-South Baghdad Gas Pipeline | ?->Baghdad | len=56.0 dia=18.00 cap=2.00 | status=operating | updated=2022-07-26",
  "P1846 | Strategic-Kabesa Cement Gas Pipeline | ?->? | len=39.0 dia=10.00 cap=0.67 | status=operating | updated=2023-09-09",
  "P1847 | Strategic-Hilla Gas Pipeline | ?->? | len=72.0 dia=16.00 cap=0.70 | status=operating | updated=2023-09-09",
  "P1848 | Strategic-Najaf Gas Pipeline | ?->? | len=37.0 dia=16.00 cap=2.10 | status=operating | updated=2023-09-09",
  "P1850 | Khor Al-Zubair-Hartha Gas Pipeline | ?->Basra | len=77.0 dia=24.00 cap=4.80 | status=operating | updated=2023-09-14",
  "P1851 | Rumela-Nasriyaha Gas Pipeline | ?->Dhi Qar | len=216.0 dia=24.00 cap=10.42 | status=operating | updated=2023-09-14",
  "P1852 | Trans-Iraq-Nasriyaha Gas Pipeline | ?->? | len=470.0 dia=42.00 cap=11.03 | status=operating | updated=2023-09-14",
  "P1853 | West Qurna-Baghdad Gas Pipeline | West Qurna field->Baghdad | len=? dia=? cap=240.00 | status=operating | updated=2024-08-13",
  "P2231 | North Gas-Baiji Gas Pipeline | ?->Saladin | len=145.0 dia=24.00 cap=0.89 | status=operating | updated=2022-07-25",
  "P2232 | North Gas-K1 Gas Pipeline | ?->? | len=34.0 dia=18.00 cap=5.26 | status=operating | updated=2025-07-18",
  "P2233 | North Gas-Taji Gas Pipeline | ?->? | len=438.0 dia=16.00 cap=150.00 | status=operating | updated=2022-07-25",
  "P2234 | North Rumela-Khor Al-Zubair Gas Pipeline | Rumela Oil field->Basrah | len=87.0 dia=42.00 cap=10.00 | status=operating | updated=2023-09-14",
  "P4054 | Taji-Duara Gas Pipeline | ?->Al Rashid administrative district | len=? dia=18 cap=94.00 | status=operating | updated=2024-08-15",
  "P4058 | Eastern Iraq Gas Pipeline | ?->? | len=? dia=48 cap=350.00 | status=operating | updated=2022-07-25",
  "P4061 | National Gas Pipeline | ?->Basra | len=600.0 dia=42 cap=850.00 | status=operating | updated=2022-07-25",
  "P4062 | Trans-Iraq-Hilla-Gas Pipeline | ?->? | len=25.0 dia=24 cap=? | status=operating | updated=2022-07-25",
  "P4064 | Trans-Iraqi-Najaf PWR St Gas Pipeline | ?->? | len=74.0 dia=24 cap=? | status=operating | updated=2022-07-25",
  "P4065 | Trans-Iraqi-Dewania Gas Pipeline | ?->? | len=50.0 dia=24 cap=? | status=operating | updated=2022-07-25",
  "P4066 | Trans-Iraqi-Daura Gas Pipeline | ?->? | len=29.0 dia=18 cap=? | status=operating | updated=2022-07-25",
  "P4067 | Al-Ahdab-Al-Zubaydia PWR St Gas Pipeline | ?->Wasit | len=73.0 dia=16 cap=? | status=operating | updated=2022-07-25",
  "P4068 | Mishraq Cross Road-Mousil PWR ST Gas Pipeline | ?->Mosul | len=38.0 dia=12 cap=? | status=operating | updated=2022-07-26",
  "P4401 | Okaz Gas Pipeline | ?->Anbar | len=30.0 dia=16 cap=75.00 | status=operating | updated=2023-09-09",
  "P5855 | Iran-Iraq Gas Pipeline | ?->Diyala | len=? dia=? cap=35.00 | status=operating | updated=2023-09-18",
  "P5856 | Gharraf Gas Pipeline | ?->? | len=76.0 dia=20 cap=120.00 | status=operating | updated=2025-07-18",
  "P6823 | Khormor-Pirdawood PP Gas Pipeline | Khor Mor->Erbil | len=180.0 dia=24 cap=3.40 | status=operating | updated=2025-07-23",
  "P6824 | Shouibah-Khor Al-Zubair Gas Pipeline | Shouibah->Basrah | len=46.0 dia=10,8 cap=? | status=operating | updated=2024-08-14",
  "P6826 | Majnoon Gas Pipeline | ?->Basrah | len=8.0 dia=24 cap=? | status=operating | updated=2025-07-16",
  "P6827 | Khormor-Jambur-Kirkuk Gas Pipeline | ?->Kirkuk | len=1.05 dia=16 cap=100.00 | status=operating | updated=2024-08-14",
  "P7435 | Khor Al-Zubair-Shatt Al Arab Gas Pipeline | ?->Basrah | len=40.0 dia=42 cap=200.00 | status=operating | updated=2025-07-15",
  "P7457 | Semel-Duhok Gas Pipeline | ?->Kurdistan | len=40.0 dia=36 cap=120.00 | status=operating | updated=2025-07-18",
  "P7468 | Najaf Cement Factory Gas Pipeline | ?->Najaf | len=1.2 dia=10 cap=? | status=operating | updated=2025-07-22",
  "P7471 | Badra Oil Field–Wassit PS Gas Pipeline | ?->Wassit | len=106.5 dia=18 cap=? | status=operating | updated=2025-07-22",
  "P7474 | Al Najibiya PS Gas Pipeline | ?->Basra | len=4.5 dia=12 cap=? | status=operating | updated=2025-07-23",
  "P7477 | Mousal-Al Qayyarah PS Gas Pipeline | Mousal->Nineveh | len=22.0 dia=18 cap=130.00 | status=operating | updated=2025-07-23"
 ],
 "routes_context": {
  "P1841": {
   "route_accuracy": "low",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P1842": {
   "route_accuracy": "low",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P1845": {
   "route_accuracy": "low",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P1846": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P1847": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P1848": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P1850": {
   "route_accuracy": "low",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P1851": {
   "route_accuracy": "low",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P1852": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P1853": {
   "route_accuracy": "low",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P2231": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": "https://www.opec.org/opec_web/static_files_project/media/downloads/publications/ASB2017_13062017.pdf"
  },
  "P2232": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P2233": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P2234": {
   "route_accuracy": "low",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P4054": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P4058": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P4061": {
   "route_accuracy": "medium",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": "https://iraqenergy.org/wp/wp-content/uploads/2018/11/Jafar-Dhia-Jafar-URUK.pdf?ec1e82&ec1e82"
  },
  "P4062": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P4064": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P4065": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P4066": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P4067": {
   "route_accuracy": "low",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P4068": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P4401": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P5855": {
   "route_accuracy": "no route",
   "start": "Iran",
   "end": "Iraq",
   "route_notes": ""
  },
  "P5856": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P6823": {
   "route_accuracy": "low",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P6824": {
   "route_accuracy": "low",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P6826": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P6827": {
   "route_accuracy": "low",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P7435": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P7457": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P7468": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P7471": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P7474": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  },
  "P7477": {
   "route_accuracy": "no route",
   "start": "Iraq",
   "end": "Iraq",
   "route_notes": ""
  }
 },
 "gulfpub_oil_iraq": "  - Zubair - Khor Al Amaya | Operating | Zubair field, Iraq -> Khor Al Amaya terminal, Iraq | op=Basrah Oil Company dia=42.0 len_mi=114\n  - Strategic Pipeline | Operating | Hadithah, Iraq -> Al Faw, Iraq | op=Oil Pipelines Company (OPC) dia=42.0 len_mi=413\n  - Iraq - Jordan Oil Pipeline | Operating | Hadithah (K3), Iraq -> Tarbil border crossing, Iraq | op=Oil Pipelines Company (OPC) dia=16.0 len_mi=219\n  - Luhais - Rumaila | Operating | Luhais field, Iraq -> Rumaila field, Iraq | op=Basrah Oil Company dia=12.0 len_mi=32\n  - Baiji - Daura | Operating | Baiji (K2), Iraq -> Daura, Iraq | op=Oil Pipelines Company (OPC) dia=16.0 len_mi=213\n  - Iraq - Turkey Pipeline | Operating | Kirkuk, Iraq -> Ceyhan, Turkey | op=Botas dia=46.0 len_mi=600\n  - Iraq - Turkey Pipeline | Operating | Kirkuk, Iraq -> Dortyol, Turkey | op=Botas dia=40.0 len_mi=600\n  - Naft Khaneh - Daura | Operating | Naft Khaneh field, Iraq -> Daura, Iraq | op=Oil Pipelines Company (OPC) dia=12.0 len_mi=130\n  - Buzurgan - Rumaila | Operating | Buzurgan field, Iraq -> Rumaila field, Iraq | op=Basrah Oil Company dia=28.0 len_mi=101\n  - IPSA | Operating | Zubair field (IPSA1), Iraq -> Mu'ajiz, Saudi Arabia | op=Aramco dia=48.0 len_mi=995\n  - Tawke - Fish Khabur | Operating | Tawke field, Iraq -> Fish Khabur, Iraq | op=Oil Pipelines Company (OPC) dia=12.0 len_mi=14\n  - Al Quwayr - Kirkuk-Avanah | Operating | Al Quwayr field, Iraq -> Kirkuk-Avanah field, Iraq | op=Oil Pipelines Company (OPC) dia=12.0 len_mi=34\n  - Bai Hassan - Kirkuk | Operating | Bai Hassan field, Iraq -> Kirkuk refinery, Iraq | op=Oil Pipelines Company (OPC) dia=12.0 len_mi=20\n  - Kirkuk - Salah el-Dien | Operating | Kirkuk, Iraq -> Salah el-Dien (K2), Iraq | op=Oil Pipelines Company (OPC) dia=26.0 len_mi=83\n  - Mushorah - Baiji | Operating | Mushorah field, Iraq -> Baiji (K2), Iraq | op=Oil Pipelines Company (OPC) dia=12.0 len_mi=155\n  - Iraq - Turkey Pipeline | Operating | Kirkuk, Iraq -> Ceyhan, Turkey | op=Botas dia=46.0 len_mi=600\n  - Baiji - Hadithah | Operating | Baiji (K2), Iraq -> Hadithah (K3) | op=Oil Pipelines Company (OPC) dia=16.0 len_mi=84\n  - Iraq - Syria Oil Pipeline | Operating | Hadithah (K3), Iraq -> T2 pump station, Syria | op=Oil Pipelines Company (OPC) dia=12.0 len_mi=129\n  - Strategic Pipeline | Operating | Hadithah (K3), Iraq -> Al Basra terminal, Iraq | op=Oil Pipelines Company (OPC) dia=42.0 len_mi=413\n  - Strategic Pipeline | Operating | Hadithah (K3), Iraq -> Al Basra terminal, Iraq | op=Oil Pipelines Company (OPC) dia=32.0 len_mi=106\n  - Strategic Pipeline | Operating | Hadithah, Iraq -> Al Faw, Iraq | op=Oil Pipelines Company (OPC) dia=28.0 len_mi=87\n  - Rumaila (PS1) - Rumaila (IPSA2) | Operating | Rumaila field (PS1), Iraq -> Rumaila field (IPSA2), Iraq | op=Basrah Oil Company dia=12.0 len_mi=25\n  - Musaiab Power Station Line | Operating | Strategic Pipeline, Karbala, Iraq -> Musaiab Power Station, Iraq | op=Oil Pipelines Company (OPC) dia=16.0 len_mi=48\n  - Jumboor - Kirkuk | Operating | Jumboor field, Iraq -> Kirkuk refinery, Iraq | op=Oil Pipelines Company (OPC) dia=12.0 len_mi=16\n  - Kirkuk-Avanah - Kirkuk | Operating | Kirkuk-Avanah field, Iraq -> Kirkuk refinery, Iraq | op=Oil Pipelines Company (OPC) dia=12.0 len_mi=28\n  - Basra-Aqaba Oil Pipeline I | Under Construction | Basrah, Iraq -> Najaf, Iraq | op=State Company for Oil Projects (SCOP) dia=56.0 len_mi=216\n  - Basra-Aqaba Oil Pipeline II | Under Construction | Najaf, Iraq -> Aqaba, Jordan | op=State Company for Oil Projects (SCOP) dia=56.0 len_mi=720",
 "gulfpub_gas_note": "GulfPub's gas dataset has NO Iraq gas coverage (capped 1,000-feature 2024 export); the only Iraq gas entry is a bare name 'South Rumaila - Ratqa Pipeline' with all attributes null. Do NOT expect GulfPub to corroborate gas specs. The oil roster above is cross-commodity context: if this GEM 'gas' row is actually one of those crude/NGL lines, that's a classification/duplicate concern."
}

const REPO = A.repo
const STAGING = A.staging
const COMMODITY = A.commodity || 'gas'
const COUNTRY = A.country || 'Iraq'
const PIDS = A.pids
const ROSTER = (A.roster || []).join("\n")
const RC = A.routes_context || {}
const GULFPUB_OIL = A.gulfpub_oil_iraq || ''
const GULFPUB_GAS_NOTE = A.gulfpub_gas_note || ''

const contract = (pid) => {
  const rc = RC[pid] || {}
  const routeBlock = `
## ROUTE (corridor + endpoints — REQUIRED for this row; RouteAccuracy = "${rc.route_accuracy || '?'}")
This row's geometry is weak (no route / low / medium). Do NOT edit any Route [ref] cell and do NOT
touch the routes repo — instead RESEARCH and PROPOSE a corridor for a later human routes-repo branch.
Current sheet endpoints: start="${rc.start || ''}" end="${rc.end || ''}". RouteNotes="${(rc.route_notes||'').slice(0,200)}".
Establish the REAL endpoints (named facilities/fields/cities) and the corridor the line follows, with
independent sources. Give approximate lat/lon (decimal degrees, EPSG:4326) for each endpoint and any
key waypoint you can source (city, field, compressor/pump station, river/border crossing). If you can
only bound it loosely, say so and give the tightest corridor you can defend. NEVER fabricate coordinates
— if you cannot source a point, leave its lat/lon null and describe it in words.
Emit a "routes" array in the shard (schema below). This is a suggestion set, never an auto-applied route.`

  return `You are a meticulous, skeptical GEM pipeline researcher. Critically RE-AUDIT one ${COUNTRY}
${COMMODITY} OPERATING pipeline: ProjectID ${pid}. This is a deep-sweep validity pass — CONFIRM the
existing data and EXPOSE anything wrong, not rubber-stamp it. Baird expects some data to be wrong, some
pipelines to not exist, some to be duplicates or misclassified. Find those.

cd ${REPO} first.

## Inputs (ALWAYS START FROM THE SOURCES THE SHEET ALREADY CITES)
- Current GEM values + existing refs: \`${STAGING}/worklist.json\` -> load it, filter \`units\` to
  \`project_id == "${pid}"\`. Each unit has ref_col, value_cols, values, primary_value, current_ref,
  sheet_row, segment_name, pipeline_name, wiki.
- gem.wiki outbound citations for this row: \`${STAGING}/wiki_citations.json\` (your STARTING POINT;
  verify each — many rot; READ gem.wiki for leads but NEVER cite it). A row whose only support is a
  generic/aggregate citation not naming this pipeline is itself an existence flag.
- Roster of ALL ${PIDS.length} in-scope Iraq gas operating pipelines (duplicate/relabel detection —
  does ${pid} look like the same physical pipe as another row?):
${ROSTER}
- GulfPub cross-commodity context (Iraq OIL/NGL lines from the GulfPub PE World Map scrape):
${GULFPUB_OIL}
  NOTE: ${GULFPUB_GAS_NOTE}

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, A Barrel Full / any wikidot.com page.
   Read for leads only; url_verifier rejects them.
2. NEVER fabricate a URL or a coordinate. If you cannot verify, say so in researcher_notes.
3. Run EVERY url through the verifier before citing:
   \`python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"]\` -> cite only if OK/200
   AND contains the expected token(s). Use distinctive tokens (numbers, place names, Arabic forms).
4. Corroborate with >=2 INDEPENDENT sources (separate origins; not one wire story reprinted, not two
   pages tracing to GEM). tier: high = >=2 independent working+value-present; medium = 1 strong;
   low = 1 weak/partial/conflicting. Search Arabic sources too (Iraqi press, INA, SOMO, oil ministry).

## What to do, IN PRIORITY ORDER (existence + classification FIRST)
1. EXISTENCE — is this pipeline real? Independent evidence it physically exists. If the only traces are
   GEM-derived, or the cited source doesn't name it, or no independent confirmation -> verdict="concern",
   concern_type="existence".
2. CLASSIFICATION — correctly a GAS TRANSMISSION trunk (not gathering/process/feeder; not actually an
   oil/NGL line; not a plant-internal line)? Wrong -> concern_type="classification". Use the GulfPub oil
   list above: if this "gas" row is really one of those crude/NGL lines, flag it.
3. DUPLICATE — compare vs roster; if ${pid} is very likely the same physical pipe as another ProjectID
   (relabel / segment double-count), flag concern_type="duplicate" and NAME the other PID.
4. ATTRIBUTION — owner/operator, FuelSource, province, endpoints. Wrong -> concern_type="attribution".
5. SPEC — length, diameter, capacity, dates. CRITICALLY confirm each vs >=2 independent sources; a page
   merely mentioning the line is NOT enough — sources must AGREE with the GEM number. Material
   disagreement -> concern_type="spec", verdict="concern" (never silently pass).
Also DEEP-FILL genuinely blank value fields with a paired, verified ref (best-effort; don't force a
number on weak fields like Capacity).
${routeBlock}

A pipeline that is real and correctly classified but has a lesser caveat -> verdict="confirmed (caveat)".
Only open existence/duplicate/classification doubt -> verdict="concern".

## Output — write a shard, then return a summary
Write \`${STAGING}/rows/${pid}.json\` = a single JSON object EXACTLY shaped like:
{
  "project_id": "${pid}",
  "pipeline_name": "<from worklist>",
  "sheet_row": <int from worklist>,
  "wiki": "<gem.wiki url from worklist>",
  "validity": [
    { "segment_name": "<or empty>", "verdict": "confirmed (caveat)|concern",
      "concern_type": "existence|duplicate|classification|attribution|spec|none",
      "recommendation": "<short human next step>",
      "researcher_notes": "<full finding — what you checked, what the sheet's own sources say, what independent sources say vs GEM, your reasoning>",
      "proposed_refs": ["https://...verified..."], "tier": "high|medium|low",
      "independent": true, "source_language": "en|ar" }
  ],
  "fills": [
    { "segment_name": "<or empty>", "sheet_row": <int>, "ref_col": "Capacity [ref]",
      "value_cols": ["Capacity"], "primary_value_col": "Capacity", "values": {"Capacity": "<val>"},
      "primary_value": "<val>", "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
      "class_out": "REFS_ADDED|UNRESOLVED", "tier": "high|medium|low", "independent": true,
      "source_language": "en|ar", "researcher_notes": "<why this value / source>" }
  ],
  "routes": [
    { "segment_name": "<or empty>",
      "start_name": "<named start facility/field/city>", "start_lat": <dd or null>, "start_lon": <dd or null>,
      "end_name": "<named end facility/city>", "end_lat": <dd or null>, "end_lon": <dd or null>,
      "waypoints": [ {"name":"<place>", "lat": <dd or null>, "lon": <dd or null>} ],
      "corridor_desc": "<prose corridor: provinces/towns/features it passes, and how tight the bound is>",
      "current_route_accuracy": "${rc.route_accuracy || ''}",
      "suggested_route_accuracy": "high|medium|low (what the sourced corridor supports)",
      "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
      "tier": "high|medium|low", "source_language": "en|ar",
      "researcher_notes": "<how you established endpoints + corridor; note any fabrication avoided>" }
  ],
  "summary": "<one line>"
}
Emit >=1 validity object (use verdict="confirmed (caveat)", concern_type="none" if nothing wrong,
summarizing what you confirmed) and >=1 routes object (endpoints at minimum). validity[].proposed_refs,
fills[].proposed_refs, and routes[].proposed_refs must have passed url_verifier. Coordinates must be real
(sourced or defensible from a named place), never invented — null if unknown. Before finishing, run
\`python -c "import json; json.load(open('${STAGING}/rows/${pid}.json'))"\` to confirm it parses.
Return ONLY a 2-line summary: verdict/concern_types staged + suggested route accuracy, and any UNRESOLVED.
Your shard file is the deliverable, not your message.`
}

phase('Audit')
log(`Auditing ${PIDS.length} ${COUNTRY} ${COMMODITY} operating pipelines (existence+classification first, + corridor routes), one subagent each.`)
const results = await parallel(PIDS.map(pid => () =>
  agent(contract(pid), { label: `audit:${pid}`, phase: 'Audit', agentType: 'general-purpose', model: 'sonnet' })
))
const done = results.filter(Boolean).length
log(`Audit complete: ${done}/${PIDS.length} subagents returned. Shards in ${STAGING}/rows/`)
return { audited: done, total: PIDS.length }
