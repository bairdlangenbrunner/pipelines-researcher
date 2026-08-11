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
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/india-gas/staging/cancelled-review", "commodity": "gas", "country": "India", "pids": ["P0451", "P0913", "P0931", "P0932", "P0935", "P0936", "P0955", "P2214", "P2215", "P2748", "P2752", "P3334", "P3342"], "roster": ["P0451 | Iran-Pakistan-India Pipeline | Asaluyeh->India | len=2700.0 dia=? cap=3884.6 | status=cancelled | updated=2025-07-11", "P0913 | Contai-Paradip-Dattapulia Gas Pipeline | Contai->West Bengal | len=705.0 dia=? cap=5.26 | status=cancelled | updated=2023-07-12", "P0931 | Jaigarh-Mangalore Gas Pipeline | Jaigarh LNG Terminal->Karnataka | len=635.0 dia=? cap=17.0 | status=cancelled | updated=2024-07-10", "P0932 | Kakinada-Vizag-Srikakulam Gas Pipeline | Kakinada->Andhra Pradesh | len=275.0 dia=? cap=90.0 | status=cancelled | updated=2024-07-05", "P0935 | Kukrahati-Itinda Gas Pipeline | Kukrahati->West Bengal | len=125.0 dia=? cap=18.0 | status=cancelled | updated=2025-07-15", "P0936 | Langtala-Bhilwara Gas Pipeline | Langtala->Rajasthan | len=580.0 dia=? cap=1.83 | status=cancelled | updated=2023-07-20", "P0955 | Surat-Paradip Gas Pipeline | Surat->Odisha | len=2112.0 dia=? cap=27.3 | status=cancelled | updated=2023-07-21", "P2214 | Kanai Chhata-Shrirampur Gas Pipeline | Kanai Chhata->Maharashtra | len=250.0 dia=? cap=19.2 | status=cancelled | updated=2023-07-08", "P2215 | Langtala-Jodhpur-Pali Gas Pipeline | Langtala->Rajasthan | len=440.0 dia=? cap=5.0 | status=cancelled | updated=2025-07-16", "P2748 | Langtala-Pachpadra Gas Pipeline | Langtala->Rajasthan | len=290.0 dia=? cap=4.0 | status=cancelled | updated=2024-07-08", "P2752 | Kondalapalli-Tirupati Gas Pipeline | Kondalapalli->Andhra Pradesh | len=450.0 dia=? cap=4.0 | status=cancelled | updated=2025-07-16", "P3334 | Digha\u2013Contai Gas Pipeline | Digha->West Bengal | len=115.0 dia=? cap=? | status=cancelled | updated=2025-07-22", "P3342 | Kakinada-Haldia Gas Pipeline | Kakinada->West Bengal | len=? dia=? cap=? | status=cancelled | updated=2023-07-24"], "status_review": true, "model": "sonnet", "extra_brief": "INDIA GAS \u2014 CANCELLED / DORMANT REVIEW. These 13 rows are all currently Status=cancelled.\nYour job is NOT to find refs for a value you assume is right; it is to establish whether\n'cancelled' is the correct, sourced verdict, and to get the vocabulary right.\n\nTHE CENTRAL QUESTION, AND THE TRAP IN IT.\nDistinguish a CONFIRMED cancellation (someone with authority said the project is dead, or\nthe authorisation was formally surrendered/withdrawn) from an INFERRED one (no news for\nyears, so we infer dormancy). These take different vocabulary:\n  ShelvedCancelledType = confirmed   -> a source says it was cancelled/withdrawn\n  ShelvedCancelledType = inferred    -> our own dormancy inference, no cancellation source\nBoth are LOWERCASE. 'Presumed' is NOT in the vocabulary and must never be written.\nEIGHT of these 13 rows have a BLANK ShelvedCancelledType (P0931, P0932, P0935, P2214,\nP2215, P2748, P2752, P3334) \u2014 closing that gap with the right word, and a ref for\n'confirmed', is the single most valuable thing this pass can produce. If you cannot find\na cancellation source, the honest answer is `inferred` with NO fabricated URL, and you say\nso in ResearcherNotes.\n\nAlso test the OTHER direction: is 'cancelled' too strong? If a project is merely dormant\nwith a live authorisation or a sponsor still nominally pursuing it, `shelved` is the better\nstatus. Conversely, if a line quietly got built under a different name, that is a\nDISCOVERY/duplicate finding, not a cancellation \u2014 check the operating rows before\nconcluding a route was abandoned.\n\nABSENCE FROM THE REGULATOR PROVES NOTHING HERE, AND THIS IS THE MAIN THING TO NOT GET\nWRONG. PNGRB's monthly NGPL MIS register\n(https://pngrb.gov.in/data-bank/<YYYYMMDD>-NGPL-MIS-Report.pdf) lists only pipelines with\na LIVE authorisation, and it covers common-carrier lines only. A cancelled project is\nabsent from it by definition. So absence is the expected outcome and is NOT evidence of\ncancellation. Where the register DOES help:\n  - Walking BACK through monthly editions: a line that appears in an older edition's\n    UNDER CONSTRUCTION table and then disappears gives you a dated disappearance window,\n    which is real evidence and lets you date CancelledYear.\n  - PNGRB public notices, bid-round documents and board minutes DO announce withdrawals\n    and re-bids explicitly, and those are citable cancellation sources.\nNote the inverse trap, already seen on this country: PNGRB keeps an authorisation listed\nuntil it is formally surrendered, so presence in UNDER CONSTRUCTION with 0 km built and a\nlapsed target is evidence of DORMANCY, not of activity (P0921 Ennore-Nellore).\n\nWATCH FOR RE-BIDS AND SUCCESSOR PROJECTS. Several of these are Rajasthan/West Bengal/Andhra\ncorridors that PNGRB has re-tendered under new names, and a corridor being re-bid to a new\nsponsor means the OLD row is genuinely cancelled while a NEW pipeline exists. The Langtala\ncluster (P0936 Langtala-Bhilwara, P2215 Langtala-Jodhpur-Pali, P2748 Langtala-Pachpadra) is\nthree rows on one origin point and deserves particular scepticism: check whether they are\nthree separate proposals, three phases of one, or one proposal digitized three times. Same\nquestion for the West Bengal cluster (P0913 Contai-Paradip-Dattapulia, P3334 Digha-Contai,\nP0935 Kukrahati-Itinda, P2214 Kanai Chhata-Shrirampur) and the Andhra cluster (P0932\nKakinada-Vizag-Srikakulam, P3342 Kakinada-Haldia, P2752 Kondalapalli-Tirupati). Note\nP6562 Kanai Chhata-Panitar is a LIVE construction row in a different leg of this batch \u2014\nso P2214 Kanai Chhata-Shrirampur may be its predecessor or its sibling, worth checking.\n\nP0451 IRAN-PAKISTAN-INDIA is a different animal: a cross-border geopolitical project, and\nthe India leg specifically. India's withdrawal is well documented and separable from the\nIran-Pakistan segment's continued life. Be precise about WHICH leg is cancelled and cite\nthe India-specific withdrawal, not general IPI coverage.\n\nDATES. If you establish a cancellation, populate CancelledYear (or ShelvedYear for shelved)\nand pair it with a ref. Do not leave a year without a ref or a ref without a year. Note\nthese rows are also missing ProposalYear on most \u2014 a dateline in original coverage supports\nProposalYear and is worth capturing.\n\nSOURCES: PNGRB notices/tariff orders/bid documents; MoPNG annual reports and Parliament\n(Lok Sabha/Rajya Sabha) Q&A, which is unusually good for \"what happened to project X\" in\nIndia; sponsor annual reports (GAIL, GSPL, IOCL, ONGC, H-Energy, Reliance); state\ngovernment statements; trade press (Indian Infrastructure, Business Standard, Hindu\nBusinessLine, Economic Times Energy).\n\nSTANDING RULES: never cite gem.wiki or any GEM surface; never fabricate a URL \u2014 an\ninferred status change gets ShelvedCancelledType=inferred and NO URL; never use\nabarrelfull/wikidot. Report an unresolved row as unresolved."};
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
