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
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/india-gas/staging/ref-sweep-operating", "commodity": "gas", "country": "India", "pids": ["P3906"], "roster": ["P3906 | Haridwar-Rishikesh-Dehradun Gas Pipeline | Haridwar->Uttarakhand | len=50.0 dia=? cap=? | status=operating | updated=2024-07-10"], "model": "sonnet", "extra_brief": "India-specific guidance (established by the orchestrator this run \u2014 use it, and challenge it):\n\n**The regulator's own line-wise register exists and is authoritative-ish.** PNGRB (Petroleum\nand Natural Gas Regulatory Board) publishes a MONTHLY line-wise inventory of authorised\nnatural-gas pipelines: `https://pngrb.gov.in/data-bank/<YYYYMMDD>-NGPL-MIS-Report.pdf`\n(latest edition 20260531). Printed page 2, \"PHYSICAL PROGRESS REPORT OF NATURAL GAS\nPIPELINE\", is the only line-wise table. Per pipeline it gives: entity, authorisation date,\nauthorised length (km), authorised + design/determined capacity (MMSCMD), monthly gas\nsupplied, capacity utilisation, OPERATING length, UNDER-CONSTRUCTION length,\nlowered/welded/hydrotested length, target completion date, and states traversed. It splits\npipelines into OPERATIONAL / PARTIALLY COMMISSIONED / UNDER CONSTRUCTION sections. This is\nthe regulator, so it is an origin INDEPENDENT of the GAIL / GSPL / IOCL annual reports.\nFetch it with curl and read it with `pdftotext -layout`; url_verifier will likely return\nHTTP 200 + \"value not found\" on it (documented large-PDF false negative), so confirm values\nlocally and say so in your notes.\n\n**IMPORTANT \u2014 it covers COMMON-CARRIER pipelines only.** Dedicated and tie-in lines (ONGC\ntrunk lines, Duliajan-Numaligarh, refinery feeders) are inside its grand totals but are NOT\nitemised. If your pipeline is absent from the table, that is NOT evidence it does not exist \u2014\nit most likely means it is a dedicated line. Do not raise an existence concern on that basis\nalone.\n\n**GEM's India CapacityBcm/y appears to be DERIVED from PNGRB's authorised MMSCMD** via\nMMSCMD x 365 / 1000. That reproduces the sheet value exactly to 2dp on ~20 rows (e.g. KG\nBasin 16.0 -> 5.84, Dadri-Panipat 20.0 -> 7.30, Ennore-Tuticorin 84.7 -> 30.90). So if the\nsheet's capacity disagrees with the CURRENT PNGRB edition, the likely story is a STALE\nauthorised capacity, not a unit error. Say which reading you land on.\n\n**Authorisation date is NOT a commissioning year.** PNGRB's \"Authorisation Date\" is when the\nregulator authorised the pipeline; it can precede first gas by a decade. Never propose\nStartYear1 from an authorisation date. (Same class of error as dating a pipeline from its\ngas field's discovery year.)\n\n**\"Partially commissioned\" is a real regulatory category and it explains GEM's India row\npairs.** Several Indian pipelines are tracked in GEM as TWO rows \u2014 an `operating` row for\nthe commissioned portion and a `construction` row for the rest (Mehsana-Bhatinda,\nBhatinda-Gurdaspur, Mallavaram-Bhopal-Bhilwara-Vijaipur, Kochi-Koottanad-Bangalore-\nMangalore). PNGRB lists each as ONE authorised asset with an operating length AND an\nunder-construction length that sum to the authorisation. So such a pair is a GRANULARITY\ndifference, NOT a duplicate. Do not raise a duplicate concern on a pair like this; instead\ncheck whether GEM's operating/under-construction SPLIT matches PNGRB's current numbers, and\nflag the split if it does not.\n\n**PNGRB reports HVJ + GREP + DVPL + VDPL as ONE combined system** (6,169 km authorised /\n6,732 km operating), whereas GEM splits it across P0925 (HVJ), P0919 (DVPL-I), P3298\n(DVPL-II), P3297 (GREP-I), P3299 (GREP-II) and possibly P0957. Again: granularity, not\nerror. Corroborate your row against the system total and say so; do not propose collapsing\nGEM's rows.\n\n**Diameter is the real gap.** Only 10 of 75 India gas rows carry a Diameter, and PNGRB's\ntable does NOT include diameter. Diameters live in PNGRB bid/tender documents and entity\nmaps (GAIL, GSPL, IOCL). A sourced diameter is high-value here.\n\nOther Indian sources worth trying: GAIL / GSPL / GIGL / GITL / IGGL / IOCL annual reports\nand investor presentations, PNGRB public notices and bid documents\n(`pngrb.gov.in/pdf/public-notice/...`, `.../bid/...`), the Petroleum Planning & Analysis\nCell (PPAC) `ppac.gov.in`, and the Ministry of Petroleum & Natural Gas annual report.\nRegional-language sources are rarely needed; English coverage is good."};
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
