export const meta = {
  name: 'critical-deep-sweep-pakistan-operating',
  description: 'Critical re-audit of an in-scope pipeline set: confirm each data point against independent sources and flag phantom / duplicate / misclassified / mis-attributed entries (existence+classification first). One skeptical subagent per pipeline; read-and-stage only, never auto-applies.',
  phases: [
    { title: 'Audit', detail: 'one subagent per pipeline — existence+classification, then attribution+spec' },
  ],
}

// args (from `python scripts/build_deepsweep_args.py --staging <dir>`):
//   { repo, staging, commodity, country, pids:[...], roster:[...], status_review?: true }
// status_review: true = annual-update mode — each subagent ALSO stages a per-segment-row
// status verdict (confirm / change / stale / unclear) as `status_reviews` in its shard.
// tolerate a JSON-encoded string (some invocation paths stringify `args`)
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/pakistan-gas/staging/ref-sweep-operating", "commodity": "gas", "country": "Pakistan", "pids": ["P3177", "P4014", "P4015", "P4016", "P4017", "P4018", "P4019", "P4020", "P4021", "P4022", "P4023", "P4024", "P4074", "P4075", "P4079", "P4087", "P4088", "P4089", "P4090", "P4091", "P4097", "P4098", "P4099", "P4100", "P4101", "P4102", "P4103", "P4104", "P4105", "P4106", "P4107", "P4108", "P4124", "P4128", "P4129", "P4133", "P4134", "P4135", "P4136", "P4137", "P4138", "P4139", "P4140", "P4141", "P4157", "P4158", "P4159", "P4161", "P4162", "P4163", "P4164", "P4165", "P4170", "P4173", "P4174", "P4175", "P4176", "P4177", "P4178", "P4179", "P4181", "P4182", "P5486"], "roster": ["P3177 | Karachi–Sawan Gas Pipeline | Karachi->Sindh | len=371.0 dia=42.00 cap=1200.0 | status=operating | updated=2023-07-07", "P4014 | Nawabshah-Karachi Gas Pipeline | Nawabshah->Sindh | len=290.0 dia=16 cap=80.0 | status=operating | updated=2023-07-07", "P4015 | Kadanwari-Malir-Karachi Gas Pipeline | Kadanwari->Sindh | len=412.0 dia=24, 20 cap=180.0 | status=operating | updated=2023-07-07", "P4016 | Sindh University to FJFC Offtake Loopline | Jamshoro->Sindh | len=116.0 dia=24 cap=60.0 | status=operating | updated=2023-07-07", "P4017 | HQ2-Tando Adam Gas Pipeline | Nawabshah->Sindh | len=81.0 dia=24 cap=85.0 | status=operating | updated=2023-07-07", "P4018 | Badin Gas Pipeline | Badin->Sindh | len=101.0 dia=18 cap=200.0 | status=operating | updated=2023-07-07", "P4019 | Dadu-Malir-Karachi Gas Pipeline | Dadu->Sindh | len=250.0 dia=20, 18 cap=400.0 | status=operating | updated=2023-07-07", "P4020 | Bajara-Karachi Loopline | Dadu->Sindh | len=200.0 dia=24 cap=240.0 | status=operating | updated=2023-07-07", "P4021 | Quetta Gas Pipeline | Jacobabad->Balochistan | len=344.0 dia=12, 18, 20 cap=90.0 | status=operating | updated=2023-07-07", "P4022 | Zarghun-Quetta Gas Pipeline | Zarghun->Balochistan | len=61.0 dia=12 cap=25.0 | status=operating | updated=2023-07-07", "P4023 | Dadu-Sui Gas Pipeline | Dadu->Balochistan | len=266.0 dia=20 cap=170.0 | status=operating | updated=2023-07-07", "P4024 | Hassan-Sui Gas Pipeline | Hassan->Balochistan | len=58.0 dia=16 cap=30.0 | status=operating | updated=2023-07-07", "P4074 | Kandhkot Gas Pipeline | Chachar->Sindh | len=55.23 dia=16 cap=? | status=operating | updated=2023-07-07", "P4075 | Pir Koh- Sui Gas Pipeline | Pir Koh->Balochistan | len=70.5 dia=24 cap=? | status=operating | updated=2023-07-07", "P4079 | Sawan- Qadirpur Gas Pipeline | Sawan->Sindh | len=131.0 dia=24 cap=? | status=operating | updated=2023-07-07", "P4087 | Qadirpur Gas Pipeline | Qadirpur->Punjab | len=53.13 dia=30 cap=? | status=operating | updated=2023-07-07", "P4088 | Qadirpur Gas Loopline | Qadirpur->Punjab | len=53.14 dia=36 cap=? | status=operating | updated=2023-07-07", "P4089 | Qadirpur Gas Pipeline (LNG Phase II) | Qadirpur->Punjab | len=53.14 dia=42 cap=? | status=operating | updated=2023-07-07", "P4090 | Sui-Multan Gas Pipeline | Sui->Punjab | len=288.06 dia=24 cap=? | status=operating | updated=2023-07-10", "P4091 | Sui-Multan Gas Loopline I | Sui->Punjab | len=313.78 dia=30 cap=? | status=operating | updated=2023-07-10", "P4097 | Sui-Multan Gas Loopline II | Bhong->Punjab | len=256.82 dia=18 cap=? | status=operating | updated=2023-07-10", "P4098 | Sui-Multan Gas Loopline III | Bhong->Punjab | len=213.68 dia=36 cap=? | status=operating | updated=2023-07-10", "P4099 | AV29-N2 RLNG Pipeline | Qadirpur Ran->Punjab | len=68.16 dia=24 cap=? | status=operating | updated=2023-07-10", "P4100 | N2-Sahiwal RLNG Pipeline | Mian Channu->Punjab | len=77.3 dia=24 cap=? | status=operating | updated=2023-07-10", "P4101 | SV1-QV1 Gas Pipeline | Sawan->Sindh | len=130.77 dia=42 cap=? | status=operating | updated=2023-07-10", "P4102 | AV22-Kot Addu Gas Pipeline | Ayazabad Qasba Maral->Punjab | len=69.65 dia=16 cap=? | status=operating | updated=2023-07-10", "P4103 | D.G. Khan Gas Pipeline | D.G. Khan->Punjab | len=72.06 dia=8 cap=? | status=operating | updated=2023-07-10", "P4104 | Dhodak-Kot Addu Gas Pipeline | Dhodak->Punjab | len=77.79 dia=16 cap=? | status=operating | updated=2023-07-10", "P4105 | AV29-Sahiwal Gas Pipeline | Qadirpur Ran->Punjab | len=145.46 dia=36 cap=? | status=operating | updated=2023-07-10", "P4106 | Sidhnai-Faisalabad Gas Pipeline | Abdul Hakīm->Punjab | len=163.58 dia=18 cap=? | status=operating | updated=2023-07-10", "P4107 | Sidhnai-Faisalabad Gas Pipeline II | Abdul Hakīm->Punjab | len=129.95 dia=24, 30, 36 cap=? | status=operating | updated=2023-07-10", "P4108 | Sahiwal-Lahore Gas Pipeline I | Sahiwal->Punjab | len=142.93 dia=18 cap=? | status=operating | updated=2023-07-10", "P4124 | Sahiwal-Akhtar Abad Gas Pipeline | Sahiwal->Punjab | len=66.69 dia=24 cap=? | status=operating | updated=2023-07-10", "P4128 | Faisalabad-Malakwal Gas Pipeline | Faisalabad->Punjab | len=158.67 dia=16 cap=? | status=operating | updated=2023-07-10", "P4129 | Faisalabad-Malakwal Gas Pipeline II | Faisalabad->Punjab | len=90.82 dia=30 cap=? | status=operating | updated=2023-07-10", "P4133 | Kot Momin-Jauharabad Gas Pipeline | Kot Momin->Punjab | len=72.41 dia=8 cap=? | status=operating | updated=2023-07-10", "P4134 | Jauharabad-Chashma Gas Pipeline | Jauharabad->Punjab | len=82.21 dia=8 cap=? | status=operating | updated=2023-07-10", "P4135 | Faisalabad-Shahdara Gas Pipeline-I | Faisalabad->Punjab | len=119.25 dia=16 cap=? | status=operating | updated=2023-07-10", "P4136 | Faisalabad-Shahdara Gas Pipeline-II | Faisalabad->Punjab | len=112.51 dia=16, 24 cap=? | status=operating | updated=2023-07-10", "P4137 | Sheikhupura-Gujranwala Gas Pipeline | Sheikhupura->Punjab | len=59.44 dia=10 cap=? | status=operating | updated=2023-07-10", "P4138 | MP 59.91-Nandipur Power Plant Gas Pipeline | Nandipur->Punjab | len=76.4 dia=24 cap=? | status=operating | updated=2023-07-10", "P4139 | Shahdara-Gujranwala-Rahwali Gas Pipeline | Shahdara->Punjab | len=73.4 dia=10 cap=? | status=operating | updated=2023-07-10", "P4140 | Sahiwal-Lahore Gas Pipeline-II | Sahiwal->Punjab | len=76.67 dia=16 cap=? | status=operating | updated=2023-07-10", "P4141 | Head Balloki-MP 59.91 Gas Pipeline | Head Balloki->Punjab | len=52.34 dia=18 cap=? | status=operating | updated=2023-07-11", "P4157 | Phool Nagar-Dawood Hercules Gas Pipeline | Phool Nagar->Punjab | len=62.38 dia=16 cap=? | status=operating | updated=2023-07-11", "P4158 | Phool Nagar-Dawood Hercules Gas Loopline | Phool Nagar->Punjab | len=65.47 dia=24 cap=? | status=operating | updated=2023-07-11", "P4159 | Gujrat-Jhelum Gas Pipeline | Gujrat->Punjab | len=54.27 dia=8 cap=? | status=operating | updated=2023-07-11", "P4161 | Dandot-Gali Jagir-Wah Gas Pipeline I | Dandot->Punjab | len=153.51 dia=16 cap=? | status=operating | updated=2023-07-11", "P4162 | Dandot-Gali Jagir-Wah Gas Pipeline II | Dandot->Punjab | len=151.92 dia=10, 30 cap=? | status=operating | updated=2023-07-11", "P4163 | Dakhni-Meyal-Dhulian Gas Pipeline | Dakhni->Punjab | len=50.44 dia=16 cap=? | status=operating | updated=2023-07-11", "P4164 | Dhulian-Daud Khel Gas Pipeline | Dhulian->Punjab | len=85.2 dia=8 cap=? | status=operating | updated=2023-07-11", "P4165 | Rawat-Murree Gas Pipeline | Rawat->Punjab | len=57.25 dia=12 cap=? | status=operating | updated=2023-07-11", "P4170 | Wah-Nowshera Gas Pipeline I | Wah->Khyber Pakhtunkhwa | len=50.41 dia=10 cap=? | status=operating | updated=2023-07-11", "P4173 | Wah-Nowshera Gas Pipeline II | Wah->Khyber Pakhtunkhwa | len=52.6 dia=16 cap=? | status=operating | updated=2023-07-11", "P4174 | Mian Channu-Hasilpur Gas Pipeline | Mian Channu->Punjab | len=83.85 dia=12 cap=? | status=operating | updated=2023-07-11", "P4175 | Haripur-Mansehra Gas Pipeline | Haripur->Khyber Pakhtunkhwa | len=70.53 dia=8 cap=? | status=operating | updated=2023-07-11", "P4176 | Kohat-Nowshera Gas Pipeline | Kohat->Khyber Pakhtunkhwa | len=85.52 dia=24 cap=? | status=operating | updated=2023-07-11", "P4177 | Krapa-Manjiwala Gas Pipeline | Krapa->Khyber Pakhtunkhwa | len=84.42 dia=12 cap=? | status=operating | updated=2023-07-11", "P4178 | Manjiwala-Pezu Gas Pipeline | Kala Manjiwala->Khyber Pakhtunkhwa | len=53.29 dia=8 cap=? | status=operating | updated=2023-07-11", "P4179 | Nowshera-Mardan-Takht Bhai-Sakhakot Gas Pipeline | Nowshera->Khyber Pakhtunkhwa | len=57.99 dia=8 cap=? | status=operating | updated=2023-07-11", "P4181 | Sakhakot-Swat Gas Pipeline | Sakhakot->Khyber Pakhtunkhwa | len=68.06 dia=8 cap=? | status=operating | updated=2023-07-11", "P4182 | Gurguri-Kohat Gas Pipeline | Gurguri->Khyber Pakhtunkhwa | len=78.0 dia=10 cap=? | status=operating | updated=2023-07-11", "P5486 | Mardan-Swat Gas Pipeline | Nowshera->Khyber Pakhtunkhwa | len=104.89 dia=12 cap=? | status=operating | updated=2023-07-11"], "model": "sonnet", "extra_brief": "PAKISTAN GAS — scope notes (2026-08-07):\n- **gem.wiki is returning HTTP 403 to every automated fetch this run (Cloudflare), so `wiki_citations.json` is EMPTY for every row.** Do not treat that as 'the row has no sources'. It means the harvest step failed, not that the sheet is unsourced. Skip straight to open-web research. You may still try the row's `wiki` URL yourself with WebFetch — if it loads, read it for LEADS ONLY (never cite it).\n- **Every operating row in this scope has a COMPLETELY EMPTY `[ref]` set** — all 459 ref units came back MISSING_REF. So there are no existing refs to re-verify: essentially all your ref work is new research. Correspondingly, an existence check here cannot lean on 'what the sheet cites' (it cites nothing) — you must find independent evidence the line is real, and a row you cannot independently source at all is a legitimate existence concern.\n- **Nearly every row's LastUpdated is 2023-07-07** and the values look like a single bulk load. Be alert for bulk-load artifacts: implausible round numbers, a spec repeated verbatim across many rows, capacity/length that cannot both be true, endpoints naming a province rather than a place.\n- Preferred Pakistani primary/secondary sources: **SNGPL** (sngpl.com.pk) and **SSGC** (ssgc.com.pk) annual reports & network maps — these two utilities own most of the domestic transmission grid; **OGRA** (ogra.org.pk) State of the Industry reports; **Pakistan Petroleum Ltd** (ppl.com.pk), **OGDCL** (ogdcl.com), **Mari Energies/Mari Petroleum** (marienergies.com); **ISGS / Inter State Gas Systems** (isgs.pk) for IP/TAPI/Pakistan Stream; **PPIS / Pakistan Petroleum Information Service**; the **Petroleum Division / Ministry of Energy** yearbooks (mpnr.gov.pk); **NEPRA**; ADB/World Bank project documents for financed lines. Business press: Business Recorder, Dawn Business, The News, Profit/Pakistan Today.\n- **Search in Urdu as well as English** where English coverage is thin (e.g. پائپ لائن, گیس پائپ لائن). Record the source language.\n- **Duplicate hunting matters here.** Many roster rows are short Sindh/Balochistan field-to-trunk lines with near-identical naming (Qadirpur Gas Pipeline vs Qadirpur Gas Loopline vs Qadirpur (LNG Phase II); several '<field>-Sui' lines). Loopline-vs-parent and field-gathering-vs-transmission are the two classification traps — a loopline paralleling an existing line is a legitimate separate row, but a gathering line from a field to a processing plant is usually NOT a transmission pipeline.\n- GulfPub (Petroleum Economist) has 94 Pakistan gas records and OSM has 9; a reconciliation ran separately, so do NOT spend your budget re-deriving that crosswalk."}
if (!Array.isArray(A.pids) || !A.pids.length) {
  throw new Error("critical-deep-sweep needs args.pids — run scripts/build_deepsweep_args.py and pass its JSON as `args`.")
}
// Model is chosen by the orchestrator at dispatch time (standing rule: cheapest model
// genuinely good enough for this run) and passed via args.model; 'sonnet' is only the
// fallback when no choice is passed, not a pin.
const MODEL = A.model || 'sonnet'
const REPO = A.repo
const STAGING = A.staging
const COMMODITY = A.commodity || 'gas'
const COUNTRY = A.country || ''
const PIDS = A.pids
const ROSTER = (A.roster || []).join("\n")
const STATUS_REVIEW = !!A.status_review
// optional scope-specific guidance (e.g. China: research in Chinese, geo-blocked-site
// workarounds) appended verbatim to every subagent contract
const EXTRA = A.extra_brief ? `\n\n## Scope-specific guidance (from the orchestrator)\n${A.extra_brief}` : ''

const statusInstr = STATUS_REVIEW ? `

## STATUS REVIEW (annual-update mode — REQUIRED, one object per segment row)
This is an in-development row being checked for the annual update. Beyond the audit above,
determine the pipeline's CURRENT true status. Hunt for dated evidence NEWER than the sheet's
(the roster line shows updated=LastUpdated). A status change is a claim like any other:
>=2 independent sources, every URL through url_verifier. Verdict vocabulary:
- "confirm" — the recorded Status is still right; say what confirms it, with the evidence date.
- "change"  — evidence-based status change. Set proposed_status and proposed_changes as
  {column: value} pairs — Status (controlled vocab, lowercase) plus the matching date columns
  (e.g. now operating -> StartYear1; construction began -> ConstructionYear; newly shelved ->
  ShelvedYear). A change without a verified ref will be downgraded at merge — source it.
- "stale"   — NO independent news found. Apply the dormancy rules: proposed with no progress
  >=2y -> shelved; shelved >=4y -> cancelled. proposed_changes MUST include
  ShelvedCancelledType="Presumed" and the inference gets NO fabricated ref (standing rule 2);
  set staleness_rule to "2y->shelved" or "4y->cancelled". If dormant but under the threshold,
  use "confirm" and note the last-evidence date.
- "unclear" — genuinely cannot tell; explain what you tried in researcher_notes.
evidence_date = date of the MOST RECENT independent evidence found (YYYY-MM where possible).
Add to the shard: "status_reviews": [
  { "segment_name": "<or empty>", "sheet_row": <int from worklist>,
    "current_status": "<from the sheet>", "verdict": "confirm|change|stale|unclear",
    "proposed_status": "<or empty>", "proposed_changes": {"Status": "...", "...": "..."},
    "evidence_date": "YYYY-MM", "staleness_rule": "" ,
    "proposed_refs": ["https://...verified..."],
    "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
    "tier": "high|medium|low", "independent": true, "source_language": "en",
    "researcher_notes": "<what you searched, the newest dated evidence, your reasoning>" }
]` : ''

const contract = (pid) => `You are a meticulous, skeptical GEM pipeline researcher. Critically RE-AUDIT one ${COUNTRY}
${COMMODITY} pipeline: ProjectID ${pid}. This is a deep-sweep validity pass — your job is to CONFIRM the
existing data and EXPOSE anything wrong, not to rubber-stamp it. Baird expects some of this data to
be wrong, some pipelines to not exist, and some to be duplicates or misclassified. Find those.

cd ${REPO} first.

## Inputs (read them — ALWAYS START FROM THE SOURCES THE SHEET ALREADY CITES)
- Your pipeline's current GEM values + existing refs: \`${STAGING}/worklist.json\` → load it and
  filter \`units\` to \`project_id == "${pid}"\`. Each unit has ref_col, value_cols, values,
  primary_value, current_ref, sheet_row, segment_name, pipeline_name, wiki.
- Source leads harvested from this row's gem.wiki page: \`${STAGING}/wiki_citations.json\`
  (your STARTING POINT — engage what the sheet itself cites BEFORE open-web search; verify each
  live, since many rot; READ gem.wiki for leads but NEVER cite it). A row whose only support is a
  generic/aggregate citation that does not actually name this pipeline is itself an existence flag.
- Roster of ALL ${PIDS.length} in-scope pipelines (for duplicate/relabel detection — does ${pid} look
  like the same physical pipe as another row under a different name?):
${ROSTER}

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, or A Barrel Full /
   abarrelfull.wikidot.com / any wikidot.com page. Read for leads only. url_verifier rejects them.
2. NEVER fabricate a URL. If you cannot verify, say so in researcher_notes — no invented links.
3. Run EVERY url through the verifier before you cite it:
   \`python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"]\` → cite only if it
   prints OK/200 AND contains the expected token(s). Use distinctive tokens (numbers, place names).
4. Corroborate with >=2 INDEPENDENT sources (separate origins; not one wire story reprinted, not two
   pages both tracing to GEM). tier: high = >=2 independent working+value-present; medium = 1 strong;
   low = 1 weak/partial/conflicting. Search in the country's languages too where English is thin.

## What to do, IN THIS PRIORITY ORDER (existence + classification FIRST)
1. EXISTENCE — Is this pipeline real? Find independent evidence it physically exists/is being built.
   If the ONLY traces are GEM-derived, or the sheet's cited source does not actually name this
   pipeline, or you cannot find independent confirmation, flag verdict="concern",
   concern_type="existence" (possible hallucination / GEM-only entity).
2. CLASSIFICATION — Is it correctly classified as recorded (right commodity; a transmission trunk vs
   a gathering/process/feeder line)? Wrong → concern_type="classification".
3. DUPLICATE — Compare against the roster. If ${pid} is very likely the same physical pipe as another
   ProjectID (relabel / segment double-count), flag concern_type="duplicate" and NAME the other PID.
4. ATTRIBUTION — owner/operator, FuelSource, province, endpoints. Wrong → concern_type="attribution".
5. SPEC — length, diameter, capacity, dates. CRITICALLY confirm each against >=2 independent sources.
   It is NOT enough that a page mentions the pipeline — the source must AGREE with the GEM number.
   Material disagreement → concern_type="spec", verdict="concern" (never silently pass it).
Also DEEP-FILL genuinely blank value fields with a paired, verified ref (best-effort; do not force a
number on weak fields like Capacity — leave blank rather than fabricate).${statusInstr}${EXTRA}

A pipeline that is real and correctly classified but has a lesser caveat → verdict="confirmed (caveat)".
Only open existence/duplicate/classification doubt → verdict="concern".

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
      "recommendation": "<short human next step, e.g. 'reclassify as NGL' / 'merge into P####' / 'verify endpoint'>",
      "researcher_notes": "<the full finding — what you checked, what the sheet's own sources say, what independent sources say vs GEM, your reasoning>",
      "proposed_refs": ["https://...verified..."], "tier": "high|medium|low",
      "independent": true, "source_language": "en" }
  ],
  "fills": [
    { "segment_name": "<or empty>", "sheet_row": <int>, "ref_col": "Capacity [ref]",
      "value_cols": ["Capacity"], "primary_value_col": "Capacity", "values": {"Capacity": "<val>"},
      "primary_value": "<val>", "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
      "class_out": "REFS_ADDED|UNRESOLVED", "tier": "high|medium|low", "independent": true,
      "source_language": "en", "researcher_notes": "<why this value / source>" }
  ],
  "summary": "<one line>"
}
Emit at least one validity object per pipeline (use verdict="confirmed (caveat)", concern_type="none"
if you found nothing wrong, summarizing what you confirmed).${STATUS_REVIEW ? ' In annual-update mode also emit\nat least one status_reviews object per segment row (shaped as specified above).' : ''} validity[].proposed_refs and all
fills[].proposed_refs must have passed url_verifier. Before finishing, run
\`python -c "import json; json.load(open('${STAGING}/rows/${pid}.json'))"\` to confirm it parses.
Return ONLY a 2-line summary: the verdict/concern_types you staged, and any UNRESOLVED. Your shard
file is the deliverable, not your message.`

phase('Audit')
log(`Critically auditing ${PIDS.length} ${COUNTRY} ${COMMODITY} pipelines (existence+classification first), one subagent each.`)
const results = await parallel(PIDS.map(pid => () =>
  agent(contract(pid), { label: `audit:${pid}`, phase: 'Audit', agentType: 'general-purpose', model: MODEL })
))
const done = results.filter(Boolean).length
log(`Audit complete: ${done}/${PIDS.length} subagents returned. Shards in ${STAGING}/rows/`)
return { audited: done, total: PIDS.length }
