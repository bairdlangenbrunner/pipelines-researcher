export const meta = {
  name: 'critical-deep-sweep',
  description: 'Critical re-audit of an in-scope pipeline set: confirm each data point against independent sources and flag phantom / duplicate / misclassified / mis-attributed entries (existence+classification first). One skeptical subagent per pipeline; read-and-stage only, never auto-applies.',
  phases: [
    { title: 'Audit', detail: 'one subagent per pipeline (or per family group) — existence+classification, then attribution+spec' },
  ],
}

// args (from `python scripts/build_deepsweep_args.py --staging <dir>`):
//   { repo, staging, commodity, country, pids:[...], roster:[...], status_review?: true,
//     groups?: [[pid,...],...], lean?: true, model?, extra_brief? }
// groups: one agent per GROUP instead of per PID — sibling segments / strings / hub branches
// that share their documents (docs/sops/lean_pass.md). Every PID must appear in exactly one
// group; a singleton group is the classic one-agent-per-row contract, word for word.
// lean: the worklist was cut by scripts/lean_worklist.py — the agent works the owed set only,
// and the deferred units are recorded, not skipped.
// status_review: true = annual-update mode — each subagent ALSO stages a per-segment-row
// status verdict (confirm / change / stale / unclear) as `status_reviews` in its shard.
// tolerate a JSON-encoded string (some invocation paths stringify `args`)
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
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
const GROUPS = Array.isArray(A.groups) && A.groups.length ? A.groups : PIDS.map(p => [p])
{
  const seen = GROUPS.flat()
  const missing = PIDS.filter(p => !seen.includes(p))
  const dup = seen.filter((p, i) => seen.indexOf(p) !== i)
  if (missing.length || dup.length || seen.length !== PIDS.length) {
    throw new Error(`args.groups must cover every pid exactly once (missing: ${missing.join(',')}; duplicated: ${dup.join(',')})`)
  }
}
const LEAN = !!A.lean
const ROSTER = (A.roster || []).join("\n")
const STATUS_REVIEW = !!A.status_review
// optional scope-specific guidance (e.g. China: research in Chinese, geo-blocked-site
// workarounds) appended verbatim to every subagent contract.
// INLINE IT. `args.extra_brief_path` (hand the agent the run dir's BRIEF.md and tell it to
// read the file first) was tried on Russia R2, 2026-09-15, to keep ~30KB out of the
// orchestrator's context: 8 of 8 agents skipped the file completely — zero reads — and went
// straight to Step 0. An agent reliably runs the Step 0 COMMANDS it is given and reliably
// reads text already in its prompt; it does not reliably go fetch a document it was told to
// read. The brief carries the scope's source ladder, language rules and blocked hosts, so a
// skip is silent research damage. The path form is kept only as a fallback, never the default.
const EXTRA = A.extra_brief
  ? `\n\n## Scope-specific guidance (from the orchestrator)\n${A.extra_brief}`
  : (A.extra_brief_path
     ? `\n\n## Scope-specific guidance (from the orchestrator) — READ THE FILE FIRST\n` +
       `\`${A.extra_brief_path}\` is part of this contract, not background reading. Read it IN FULL\n` +
       `before Step 0 — it carries the scope's source ladder, language rules, known-blocked hosts and\n` +
       `per-country gotchas, and research done without it will be wrong in ways the gates do catch.`
     : '')

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

const leanInstr = LEAN ? `

## LEAN PASS (token-budgeted — read this before starting)
The worklist was cut to the OWED set (scripts/lean_worklist.py): uncited values (MISSING_REF),
cited values whose link is dead / missing the value / not about this pipeline, and — if listed —
a few blank-value columns. Blank values and cited values whose links already check out were
DEFERRED into deferred_units.json on purpose; they are not your job this pass. So:
- Work ONLY the units \`shard_upsert.py --remaining\` lists, plus the status review and ONE
  validity record per row. Do not go hunting for blank values. If a document you are already
  reading states a blank value, you MAY stage it as a FILL (it is free) — never search for one.
- Second source: ONE targeted search per data point (a different publisher and document class).
  If it does not land, stage at medium with a note saying what you searched, and move on.
- Validity: judge existence / duplicate / classification from the documents you already opened
  and the roster. Open a dedicated search only when the row's own sources fail to name the
  pipeline, or the scope guidance names this row as a duplicate/existence candidate.
- Stop when coverage prints OK and the status + validity records are saved. Do not widen scope.` : ''

const contract = (group) => group.length === 1 ? contractFor(group[0], '') : contractFor('<PID>', `
## FAMILY GROUP — you own ${group.length} rows: ${group.join(', ')}
These rows share their documents (sibling segments, strings of one corridor, or branches of one
hub). Research the SHARED documents ONCE, then report per row. Everything below is written for
one ProjectID: read every <PID> as EACH of ${group.join(', ')} in turn — each row gets its own shard
(its own Step 0 --init/--remaining), its own fills, its own status review and validity record, and
its own check_shard_coverage OK. A page that states a figure for one string is not a ref for its
sibling unless it states that sibling's figure too. Save as you go; if you run low on context,
finish the row you are on and return — a replacement agent resumes from --remaining.
Do not finish until check_shard_coverage prints OK for EVERY row in the group.
`)

const contractFor = (pid, familyHeader) => `You are a meticulous, skeptical GEM pipeline researcher. Critically RE-AUDIT ${pid === '<PID>' ? 'a family of' : 'one'} ${COUNTRY}
${COMMODITY} pipeline${pid === '<PID>' ? 's' : ''}: ${familyHeader ? 'ProjectIDs ' + familyHeader.match(/rows: (.*)/)[1] : 'ProjectID ' + pid}.${familyHeader} This is a deep-sweep validity pass — your job is to CONFIRM the
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

## Step 0 — open your shard BEFORE any research (save-as-you-go is mandatory)
Run, in this order:
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --init
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --remaining
\`--init\` creates \`${STAGING}/rows/${pid}.json\` from the worklist (idempotent; it never touches an
existing shard's records). \`--remaining\` lists every worklist unit the shard does not yet report on.
If some units are ALREADY reported, a previous agent ran out of context on this row: keep its
records, do NOT redo them, and research ONLY the OWED units it lists (re-open a saved record only
if \`--remaining\` flags it as FIX, or if your own research on a later unit contradicts it).

FROM HERE ON, EVERY RECORD IS SAVED THE MOMENT IT IS FINISHED — never batched to the end:
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --fill '<one fills[] JSON object>'
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --validity @/tmp/${pid}_v.json
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --status-review @/tmp/${pid}_s.json
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --lead '<one cross_row_leads[] object>'
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --summary "<one line>"
(\`--fill\` etc. take inline JSON, \`@file\`, or \`-\` for stdin, and accept a single object or a list.)
A record is FINISHED when it is sourced (refs verified, values filled) or honestly UNRESOLVED with
researcher_notes saying what you searched. Never save a placeholder to "reserve" a unit — an
UNRESOLVED you meant to come back to reads downstream as "searched, found nothing". Upserting the
same unit again REPLACES the earlier record (keyed on ref_col + sheet_row), so finding a source
after an UNRESOLVED is one more --fill, not an edit. NEVER write the shard file yourself with a
heredoc, Write, or json.dump — that overwrites everything saved so far; the helper is the only
writer. Each call prints "N/M owed units reported": that is your progress meter. The point: if
you hit your context limit on unit 12 of 15, units 1-11 are on disk and your replacement does
only 12-15.

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, or A Barrel Full /
   abarrelfull.wikidot.com / any wikidot.com page. Read for leads only. url_verifier rejects them.
2. NEVER fabricate a URL. If you cannot verify, say so in researcher_notes — no invented links.
3. Run EVERY url through the verifier before you cite it, WITH THE PIPELINE NAME:
   \`python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"] --name "<pipeline name>"\`
   (or \`verify_url(url, any_of=surface_forms(value), name=<pipeline_name>)\`) → cite only if it
   prints OK/200 AND contains the expected token(s) AND names the pipeline. Use distinctive tokens
   (numbers, place names). Every verification object you write carries "name_found": true|false.
   RELEVANCE: a page about terminus A, or about terminus B, or about the parent trunk, is NOT a ref
   for the "A-B" segment row unless it names that segment (its FULL name, or its local-language
   name from the worklist's OtherLanguage* columns). If the name is in another script and the
   verifier misses it, read the page and encode the hand-confirmed match as name_found=true with
   the matched string in "note". A ref whose page never names the pipeline is capped at low at
   merge and listed by the pre-delivery gates -- do not stage it as if it were support.
4. Corroborate with >=2 INDEPENDENT sources (separate origins; not one wire story reprinted, not two
   pages both tracing to GEM). tier: high = >=2 independent working+value-present; medium = 1 strong;
   low = 1 weak/partial/conflicting. TWO REFS PER DATA POINT IS THE TARGET FOR EVERY UNIT: after the
   first source lands, the second search is owed -- a different publisher and a different document
   class (regulator approval / operator disclosure / press / EIA or acceptance notice). A single-
   source unit is fillable at medium, but its researcher_notes must say what you searched for the
   second source and why none was found. Search in the country's languages too where English is thin.
5. Read every document you open TO EXHAUSTION, for every column and every sibling row. A source
   found for one cell is a source for every fact on its page: if the approval notice you found for
   Status also states length, diameter, investment, construction start and commissioning date, stage
   it onto Length / Diameter / SegmentCost / Construction / Start [ref] too (REFS_ADDED where the
   value is on the sheet, a fill where the cell is blank). Then check the roster: a page about the
   trunk names its branches, and a page about segment I states segment II's numbers -- write those
   into your researcher_notes naming the other PID, so the orchestrator can route them (findings do
   not propagate across a fan-out by themselves). Limit: a SYSTEM figure is never a ref for a
   SEGMENT cell (aggregate-vs-segment rule) -- note it and file a validity concern instead.

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
   AGREEMENT IS ALSO AN OUTPUT, NOT A NO-OP: when the source agrees, that source is the ref the
   cell was missing — emit it as a fills[] REFS_ADDED record per rule 6. Confirming a value and
   reporting it nowhere machine-readable is the same as never checking it.
6. EVERY WORKLIST UNIT IS OWED A RECORD — UNCITED VALUES AND BLANKS ALIKE. Filter worklist.json to
   ${pid} and COUNT your units. You owe exactly ONE fills[] object per unit, whatever its class.
   Both classes are owed, and the first one is the one this leg exists for:
   - class == "MISSING_REF" — the sheet HAS a value (Length 52 mi, Capacity 700 MMcf/d, endpoints,
     dates, owner …) and its [ref] cell is EMPTY. An uncited value is an unsupported value, and
     supporting it is the CORE PRODUCT of this sweep. When your sources agree with the recorded
     value, that agreement IS the deliverable: emit the unit carrying the SAME values it already
     has, the verified ref(s) that state them, and class_out="REFS_ADDED". Writing "length and
     diameter confirmed as recorded" in your summary and nowhere else is INDISTINGUISHABLE FROM
     NOT DOING THE WORK — it is the single most common defect in this leg's history (381 units
     across four US gas batches, every one of them on a row whose documents the agent had already
     opened). When your sources DISAGREE, emit the corrected value AND file the spec concern in
     validity[]. When you genuinely find nothing, class_out="UNRESOLVED" with researcher_notes
     saying what you searched.
   - class == "MISSING_VALUE" — the cell is BLANK and the sheet owes a value (Length, Capacity,
     Diameter, StartYear, ConstructionYear, SegmentCost, Pressure, FuelSource, Operator, Owner …):
     a sourced value with a paired verified ref when you find one, otherwise class_out="UNRESOLVED"
     with researcher_notes saying what you searched. Never force a number (a weak Capacity stays
     blank rather than fabricated).
   Uncited values and blank cells on OPERATING rows come first -- they are what the researchers
   notice. A unit with NO object is a defect the pre-delivery gates list; an UNRESOLVED with EMPTY
   researcher_notes is a silent skip the gates list too. Never skip a unit silently.
7. A SOURCE THAT AGREES WITHIN ROUNDING IS A REF, NOT A NON-ANSWER. If a page names the pipeline and
   states essentially the recorded value — 51.97 mi + 0.5 mi against a recorded 52 mi, 38.5 against
   39, $10.7M against $11M — that is REFS_ADDED at medium/high tier with the small discrepancy
   stated in researcher_notes (and a validity spec concern if it is material). UNRESOLVED means you
   found NOTHING; it never means you found something slightly different. The limit stays the
   aggregate-vs-segment rule: a SYSTEM figure is never a ref for a SEGMENT cell.${statusInstr}${leanInstr}${EXTRA}

A pipeline that is real and correctly classified but has a lesser caveat → verdict="confirmed (caveat)".
Only open existence/duplicate/classification doubt → verdict="concern".

## Output — the shard (built by your upserts), then a summary
Your upserts produce \`${STAGING}/rows/${pid}.json\` = a single JSON object EXACTLY shaped like
(each --fill / --validity / --status-review / --lead call supplies ONE element of the matching list):
{
  "project_id": "${pid}",
  "pipeline_name": "<from worklist>",
  "sheet_row": <int from worklist>,
  "wiki": "<gem.wiki url from worklist>",
  "validity": [
    { "segment_name": "<or empty>", "verdict": "confirmed (caveat)|concern",
      "concern_type": "existence|duplicate|classification|attribution|spec|none",
      "recommendation": "<short human next step, e.g. 'reclassify as NGL' / 'merge into P####' / 'verify endpoint'>",
      "contested": {"<backend column the finding disputes>": "<candidate value, or \"\" if the evidence only says the current value is wrong>"},
      "researcher_notes": "<the full finding — what you checked, what the sheet's own sources say, what independent sources say vs GEM, your reasoning>",
      "proposed_refs": ["https://...verified..."], "tier": "high|medium|low",
      "independent": true, "source_language": "en" }
  ],
  "fills": [
    { "segment_name": "<or empty>", "sheet_row": <int>, "ref_col": "Capacity [ref]",
      "value_cols": ["Capacity"], "primary_value_col": "Capacity", "values": {"Capacity": "<val>"},
      "primary_value": "<val>", "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true,"name_found":true,
                          "note":"<the phrase on the page that states the value and names the line>"}],
      "class_out": "REFS_ADDED|UNRESOLVED", "tier": "high|medium|low", "independent": true,
      "source_language": "en", "researcher_notes": "<why this value / source; what you searched for a 2nd source>" }
  ],
  "cross_row_leads": [
    { "project_id": "<other PID from the roster>", "url": "https://...verified...",
      "facts": "<what the page states about THAT row, e.g. '825 km, 3.1 bn RMB, construction Oct 2008'>" }
  ],
  "summary": "<one line>"
}
Emit at least one validity object per pipeline (use verdict="confirmed (caveat)", concern_type="none"
if you found nothing wrong, summarizing what you confirmed). ON EVERY verdict="concern", fill
\`contested\` — it is the ONLY thing that puts your finding on the paste surface. A validity record
proposes no edit, so it is filtered off the _Backend mirror; \`contested\` is what tints the disputed
CURRENT value orange there with your finding attached. Omit it and a researcher pastes straight over
the cell you flagged. Name the EXACT backend column ("LengthKnownUnits", not "units"), give the
candidate value where your evidence names one, and "" where it only establishes the current value is
wrong. A concern about the row as a whole (existence/duplicate) may leave it {}.${STATUS_REVIEW ? ' In annual-update mode also emit\nat least one status_reviews object per segment row (shaped as specified above).' : ''} validity[].proposed_refs and all
fills[].proposed_refs must have passed url_verifier (with --name). One fills[] object per
WORKLIST UNIT in your slice -- MISSING_REF and MISSING_VALUE alike, sourced or honestly UNRESOLVED.
A unit with no object is a defect the pre-delivery gates list. Before finishing, run
\`python scripts/check_shard_coverage.py --staging ${STAGING} --pid ${pid}\`
and DO NOT FINISH UNTIL IT PRINTS OK -- it parses your shard and names every worklist unit you left
without a record. If it lists units, go back and report on them (a sourced record, or UNRESOLVED
with what you searched); do not delete the unit or hand back a shard it still rejects. Set the
one-line \`--summary\` last. Return ONLY a 2-line summary: the verdict/concern_types you staged, and any UNRESOLVED. Your shard
file is the deliverable, not your message.`

phase('Audit')
log(`Critically auditing ${PIDS.length} ${COUNTRY} ${COMMODITY} pipelines in ${GROUPS.length} agent(s)${LEAN ? ' (lean pass)' : ''} (existence+classification first).`)
const results = await parallel(GROUPS.map(group => () =>
  agent(contract(group), { label: `audit:${group.join('+')}`, phase: 'Audit', agentType: 'general-purpose', model: MODEL })
))
const done = results.filter(Boolean).length
log(`Audit complete: ${done}/${GROUPS.length} agents returned (${PIDS.length} pipelines). Shards in ${STAGING}/rows/ — run check_shard_coverage --all.`)
return { agents_returned: done, agents: GROUPS.length, pipelines: PIDS.length }
