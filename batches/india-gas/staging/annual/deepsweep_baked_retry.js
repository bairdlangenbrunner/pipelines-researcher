export const meta = {
  name: 'critical-deep-sweep',
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
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/india-gas/staging/annual", "commodity": "gas", "country": "India", "pids": ["P3910", "P3912", "P3913", "P5411", "P5412", "P5413", "P6538", "P6562", "P6646"], "roster": ["P3910 | Chhara to Lonhtpur Gas Pipeline | Chhara->Gujarat | len=85.0 dia=? cap=18.0 | status=construction | updated=2025-07-17", "P3912 | Swan LNG Terminal to Dahej LNG Terminal Gas Pipeline | Jafrabad->Gujarat | len=170.0 dia=? cap=7.0 | status=construction | updated=2025-07-17", "P3913 | Bhatinda-Gurdaspur Gas Pipeline | Bhatinda->Punjab | len=290.0 dia=? cap=42.42 | status=construction | updated=2025-07-17", "P5411 | Mehsana-Bhatinda Gas Pipeline | Mehsana->Punjab | len=763.0 dia=? cap=80.11 | status=construction | updated=2025-07-17", "P5412 | Hazaribagh-Ranchi Gas Pipeline | Hazaribagh->Jharkhand | len=65.0 dia=? cap=1.03 | status=construction | updated=2025-07-17", "P5413 | Gurdaspur-Jammu Gas Pipeline | Gurdaspur->Jammu and Kashmir | len=175.0 dia=? cap=2.0 | status=construction | updated=2025-07-16", "P6538 | Kakinada-Srikakulam Gas Pipeline | Kakinada->Andhra Pradesh | len=? dia=? cap=20.0 | status=proposed | updated=2025-07-17", "P6562 | Kanai Chhata-Panitar Gas Pipeline | Kanai Chhata->West Bengal | len=317.0 dia=? cap=19.2 | status=construction | updated=2025-07-17", "P6646 | Ennore Barshi Gas Pipeline | Ennore->Maharashtra | len=875.0 dia=? cap=8.0 | status=proposed | updated=2025-07-17"], "status_review": true, "model": "sonnet", "extra_brief": "INDIA GAS \u2014 IN-DEVELOPMENT STATUS REVIEW. Country-specific guidance so you corroborate\nrather than re-derive what is already established.\n\nTHE REGULATOR'S REGISTER IS THE FIRST STOP FOR STATUS.\nPNGRB (Petroleum and Natural Gas Regulatory Board) publishes a monthly MIS report whose\n\"Physical Progress Report of Natural Gas Pipeline\" page is a line-wise register of every\nAUTHORISED common-carrier gas pipeline, in three sections: OPERATIONAL, PARTIALLY\nCOMMISSIONED, and UNDER CONSTRUCTION. Each row gives authorised length, operating length,\nunder-construction length, authorised + design capacity (MMSCMD), authorisation date,\ntarget completion date, and states traversed.\n  URL pattern: https://pngrb.gov.in/data-bank/<YYYYMMDD>-NGPL-MIS-Report.pdf\n  (month-end stamped; 20260531 = May 2026. Earlier editions are the way to date a change:\n  a line that sits in UNDER CONSTRUCTION in one edition and OPERATIONAL in a later one\n  gives you the commissioning window from the regulator itself.)\nA repo-local controlled extraction of the May-2026 edition already exists at\nbatches/india-gas/staging/register-crosswalk/pngrb_ngpl_mis.json (37 authorisations; the\nparse reconciles to the report's own printed totals). READ IT before searching \u2014 it may\nalready answer your row. The adjudicated GEM mapping is in register_crosswalk.json in the\nsame directory.\n\nFOUR TRAPS, EACH OF WHICH HAS ALREADY PRODUCED A WRONG ANSWER ON THIS COUNTRY:\n\n1. AUTHORISATION DATE IS NOT A COMMISSIONING YEAR. PNGRB's \"Authorisation Date\" is when\n   the regulator granted the authorisation. It can precede first gas by a decade, and for\n   pre-existing lines brought under common-carrier regulation it POSTDATES construction by\n   decades (Uran-Taloja: authorised 2014, commissioned 1983). Never write StartYear1 from\n   an authorisation date. Say which one your source gives.\n\n2. \"PARTIALLY COMMISSIONED\" IS A REAL CATEGORY, AND IT EXPLAINS GEM'S ROW PAIRS.\n   Several Indian lines are commissioned in phases, and GEM models this as an operating row\n   PLUS a construction row on the same pipeline name. That is a legitimate phased split,\n   NOT a duplicate. The reference case is Mallavaram-Bhopal-Bhilwara-Vijaipur: P0938\n   (365 km operating) + P3602 (1,517 km construction) match the register's 365 operating /\n   1,517 under construction on BOTH halves. If you are tempted to flag a pair like this as\n   a double-count, check the register first. (The genuine double-count in this country is a\n   different shape: P0907 Barauni-Guwahati is a SECTION of P0929 JHBDPL, whose authorisation\n   name literally embeds it.)\n\n3. COMMISSIONING IS SECTIONAL, NOT AN EVENT. For long trunk lines, \"first gas\", \"section X\n   commissioned\" and \"project complete\" are three different facts with different dates, and\n   Indian trade press uses them interchangeably. Report the partial and the full separately\n   and say which your source supports. Target completion dates slip repeatedly \u2014 MNJPL has\n   slipped at least three times (Dec-2025 -> Mar-2026 -> Jun-2026) and a target date in a\n   company board report is a plan, not an outcome.\n\n4. A LIVE AUTHORISATION IS NOT EVIDENCE OF ACTIVITY. PNGRB keeps a pipeline in its\n   UNDER CONSTRUCTION section until the authorisation is formally surrendered, so a row can\n   sit there for years with 0 km built against a target that lapsed in 2020 (Ennore-Nellore,\n   P0921 \u2014 GEM's 'shelved' is the better description and is a deliberate, documented\n   divergence). Do not \"correct\" shelved to construction merely because the register lists\n   it. Conversely, 0 km built + a lapsed target IS good evidence FOR shelved/dormant.\n\nCAPACITY AND LENGTH AXES.\n- GEM's India Capacity is stored in MMSCMD on most rows and equals PNGRB's authorised\n  MMSCMD at two decimals wherever the two agree at all. So PNGRB is already the de facto\n  ORIGIN of that column: citing it is the correct primary citation but is NOT an\n  independent second source for a value GEM took from it. Where the sheet and the current\n  edition disagree, the likely story is a STALE earlier-edition figure, not a unit error.\n- Propose values against Capacity / CapacityUnits and LengthKnown. NEVER against\n  CapacityBcm/y or LengthKnownKm \u2014 those are computed columns in the live sheet.\n- DIAMETER IS THE REAL GAP and PNGRB has no diameter column. Only about 10 of India's 75\n  gas rows carry a diameter, so a sourced diameter is high-value. Company annual reports,\n  PNGRB tariff orders and bid documents are where they appear.\n\nOTHER INDIAN SOURCES WORTH REACHING FOR (all independent of PNGRB):\n  GAIL, GSPL/Gujarat State Petronet, GIGL, GITL, IGGL (Indradhanush Gas Grid), IOCL, ONGC,\n  Petronet LNG \u2014 annual reports and investor presentations; PNGRB public notices, tariff\n  orders and bid documents; PPAC (ppac.gov.in) for throughput; MoPNG annual report; CEA and\n  state gazettes for power-plant feeders. Trade press: Indian Infrastructure, World\n  Pipelines, Business Standard, Hindu BusinessLine, Economic Times Energy.\n\nMULTI-COUNTRY ROWS IN THIS BATCH: P0766 (TAPI), P0928 (India-Myanmar-Bangladesh) and\nP2213 (Gorakhpur-Rupandehi, India-Nepal) are cross-border. PNGRB's register covers the\nIndian domestic grid and will not carry them; judge these on sponsor/government sources\nfrom every country involved, and be sceptical of long-dormant cross-border MOUs.\n\nSTANDING RULES: never cite gem.wiki or any GEM surface; never fabricate a URL; never use\nabarrelfull/wikidot; if a value cannot be corroborated say so and mark it unresolved\nrather than guessing."};
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
  ShelvedCancelledType="inferred" (lowercase — that is the live column's vocabulary, NOT
  "Presumed") and the inference gets NO fabricated ref (standing rule 2);
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
