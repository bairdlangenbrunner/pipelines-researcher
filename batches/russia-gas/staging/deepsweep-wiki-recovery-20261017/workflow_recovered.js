export const meta = {
  name: 'russia-wiki-recovered-citations',
  description: 'Critical re-audit of an in-scope pipeline set: confirm each data point against independent sources and flag phantom / duplicate / misclassified / mis-attributed entries (existence+classification first). One skeptical subagent per pipeline; read-and-stage only, never auto-applies.',
  phases: [
    { title: 'Audit', detail: 'one subagent per pipeline (or per family group) — existence+classification, then attribution+spec' },
  ],
}

// args (from `python scripts/build_deepsweep_args.py --staging <dir>`):
//   { repo, staging, commodity, country, pids:[...], roster:[...], status_review?: true,
//     groups?: [[pid,...],...], lean?: true, wiki_only?: true, model?, extra_brief? }
// groups: one agent per GROUP instead of per PID — sibling segments / strings / hub branches
// that share their documents (docs/sops/lean_pass.md). Every PID must appear in exactly one
// group; a singleton group is the classic one-agent-per-row contract, word for word.
// lean: the worklist was cut by scripts/lean_worklist.py — the agent works the owed set only,
// and the deferred units are recorded, not skipped.
// wiki_only: a wiki-citation recovery pass (scripts/wiki_prepass.py --write-worklist; 2026-10-17,
// Russia P0765) — the agent opens ONLY the citations harvested from the row's gem.wiki page,
// pre-screened in <staging>/wiki_prepass.json, and never runs an open-web search.
// status_review: true = annual-update mode — each subagent ALSO stages a per-segment-row
// status verdict (confirm / change / stale / unclear) as `status_reviews` in its shard.
// tolerate a JSON-encoded string (some invocation paths stringify `args`)
const A = {
 "repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher",
 "staging": "batches/russia-gas/staging/deepsweep-wiki-recovery-20261017",
 "commodity": "gas",
 "country": "Russia",
 "pids": [
  "P0753",
  "P0752",
  "P0758",
  "P2027",
  "P3894",
  "P3895",
  "P2352",
  "P2353",
  "P3208",
  "P3896",
  "P3975",
  "P2425",
  "P3976",
  "P7600",
  "P0734",
  "P0736",
  "P0755",
  "P0760",
  "P3603",
  "P4056",
  "P4147",
  "P4148",
  "P5409",
  "P5540",
  "P5541",
  "P5542",
  "P5543",
  "P6535",
  "P6635",
  "P7538",
  "P7559",
  "P7560",
  "P7612",
  "P0737",
  "P0738",
  "P0743",
  "P0751",
  "P0761",
  "P0767",
  "P0774",
  "P0791",
  "P0828",
  "P1439",
  "P1455",
  "P1475",
  "P1647",
  "P1824",
  "P2287",
  "P2297",
  "P2309",
  "P2334",
  "P2342",
  "P2346",
  "P2348",
  "P2350",
  "P2355",
  "P2357",
  "P2362",
  "P2379",
  "P2380",
  "P2440",
  "P2707",
  "P3361",
  "P3364",
  "P3365",
  "P3369",
  "P3370",
  "P3973",
  "P3974",
  "P4076",
  "P4077",
  "P4078",
  "P4094",
  "P4095",
  "P4096",
  "P4145",
  "P4146",
  "P4210",
  "P5402",
  "P5403",
  "P5404",
  "P5414",
  "P5517",
  "P5521",
  "P5537",
  "P5666",
  "P5667",
  "P5668",
  "P5686",
  "P5745",
  "P6540",
  "P7537",
  "P7546",
  "P7547",
  "P7615"
 ],
 "roster": [],
 "status_review": true,
 "lean": true,
 "wiki_only": true,
 "model": "sonnet",
 "extra_brief": "SCOPE: RUSSIA gas, ALL 285 rows (the R1–R7 regional batches plus the 33 rows carried from the Ukraine, Kazakhstan, Uzbekistan, Iran and China passes). **WIKI-CITATION RECOVERY PASS, LEAN** — your contract's WIKI-CITATION RECOVERY PASS and LEAN PASS sections bind, and the recovery section narrows everything else: your ONLY sources are the citations harvested from this row's gem.wiki page. No open-web search. Status review is on for every row.\n\nWHY THIS PASS EXISTS. The seven regional sweeps (September 2026) harvested each row's gem.wiki citations but did not say which data point each one supported, so agents closed units from open-web searches while the wiki's own citation stated the value. P0765 TurkStream: the wiki says \"Cost: US$7.8 billion\" cited to an rferl.org article that states the figure and passes every check; the sweep staged a Moscow Times article (\">EUR 7 bn\") at low. Baird has accepted many of those September lines, so this pass must find every wiki citation that states a value and stage it, and account for every one that does not. Background: `docs/country_notes/russia.md` (do not re-read the R-batch briefs).\n\nYOUR INPUTS. `wiki_prepass.json` → `candidates` filtered to your ProjectID. The pre-pass already opened every distinct URL once:\n- `read_via` set = the live page did not load but a Wayback capture did. Read the capture and cite the CAPTURE URL; put the live URL in the note.\n- `bucket: verifying` = the page loads, names the pipeline and shows the sheet's figure for the attributed unit. Confirm by reading the page (the screen is a substring match, not a judgment: 930 on a page may be a different 930) and stage the ref.\n- `bucket: wiki_differs` = the page shows the WIKI's figure and the wiki differs from the sheet. Value question under rule 4: two independent validated refs on one precise figure = propose the change with the old value in researcher_notes; one ref = REFS_ADDED at medium, sheet value stays, discrepancy noted.\n- `bucket: loads_unchecked` = loads but the text could not be screened (a PDF, an empty shell, an image page). Read it yourself: `python scripts/fetch.py \"<url>\" --text`, or `curl -o` and `pdftotext -layout` for a PDF.\n- `bucket: prose` = cited in the body text, not on a data bullet. Read it anyway against every owed unit: these are usually the status, start-year and ownership sources.\n- Ledger records for map-only (OpenStreetMap, ArcGIS, Google Maps), dead and blocked citations are already in your shard. `--remaining` does not list them. Do not re-try them and do not cite a map link.\n`name_forms` on each candidate lists the names a page may use for this row, including the Cyrillic names from the sheet. A page that names the pipeline only in Russian names it.\nThe refs already on the sheet were NOT re-opened for this store (the regional sweeps checked them in September); a unit's `existing_ref_checks` is empty. Judge only the wiki candidates. Never propose removing an existing ref.\n\nREADING RUSSIAN PAGES. Most citations are Russian: operator sites (`*.gazprom.ru`, all of which time out from here — the pre-pass supplies the Wayback capture as `read_via`), regional government portals, the federal planning decree 816-р and its amendments (sudact.ru, legalacts.ru, consultant.ru), FAS orders, and trade press (neftegaz.ru, interfax.ru, tass.ru, kommersant.ru, kavkaz-uzel.eu). Read the figures in the form the page uses: `млрд куб. м в год` = bcm per year; `млн куб. м в сутки` = million m3 per day; `км`, `мм`, `млрд руб.` = billion rubles (stage the cost as the full number in RUB, `4300000000`, with `SegmentCostUnits = RUB`); `ввод в эксплуатацию` = commissioning; `строительство` = construction; `проект` / `планируется` = proposed. A planned figure from the decree is `medium` with its vintage stated. Stage length and capacity in the unit the page states, never converted; months as numbers 1–12.\n\nINDEPENDENCE. One origin = a Gazprom Transgaz subsidiary + Gazprom PJSC; turkstream.info + gazprom.ru; two outlets reprinting one press-service text; energybase.ru restating the operator; gazprommap.ru (Gazprom-side). Two = the operator + a government decree, FAS order, regional programme, foreign regulator, or trade press with its own reporting. A proposed STATUS CHANGE needs two independent publishers among the citations to be high; with one it is medium. ru.wikipedia is one secondary source; if it is the citation, read it and cite its footnoted primary only when that primary is itself among the harvested citations or is the page the wiki footnote points to.\n\nWHAT GOES WHERE. A candidate that states the sheet's value → `REFS_ADDED`, same value, ref appended (existing refs are never removed, not even a weak one). The same page sources every column it states: one approval notice can close Length, Diameter, Capacity, Cost, Construction and Start at once, each as its own record. A system figure is never a ref for one string or segment unless the page states that segment's figure (TurkStream 930 km is per string; 31.5 bcm/y is the system). An owner named by a page is the lowest-level holder (South Stream Transport B.V., a Transgaz subsidiary), spelled the ownership team's way (`scripts/entity_style.py`); never a parent. A unit with no wiki candidate stating it → `UNRESOLVED` with the note \"no wiki citation states this value; not searched this pass\". A lead worth an open-web search (a page that names a newer figure, a merger, a cancellation) → `--lead`, not a search.\n\nSTATUS REVIEW AND VALIDITY. One record each per row, from the citations only. \"unclear\" and \"confirmed (caveat)\" are the honest defaults when the citations do not settle it. A citation dated more than two years ago for a `proposed` row with no newer citation is worth saying in the status note (it is the shelved-inferred signal), but the inference itself is for the regional batches, not this pass.\n\nCARRIED ROWS. The 33 rows swept earlier under Ukraine, Kazakhstan, Uzbekistan, Iran or China are in scope here for the first time as Russia rows; treat them like any other.\n\nOUTPUT. Save every record the moment it is finished with `shard_upsert.py`. One `--wiki-read` record per candidate you open. Finish when `check_shard_coverage.py --pid <PID>` prints OK, then `--summary`. Return a two-line summary only.\n\n## Recovered-citation wave (2026-10-19): read ONLY the reopened citations\n\nThis row was already worked in this store. Its shard holds a record for every owed unit, a status review and a validity record. A later full-ladder re-check found that some citations an earlier agent logged as dead or blocked do load (through the live site, a complete Wayback capture or archive.today). Those ledger records were removed, so `--remaining` now lists them as `WIKI` lines. That list is your whole job.\n\n- Run `--remaining` first. Read ONLY the citations it lists as `WIKI`. Do not re-open citations already in the ledger, and do not search the open web.\n- Each reopened candidate in `wiki_prepass.json` carries `read_via` when the live URL does not load: read that copy. Read the WHOLE document (download a PDF with `curl -sL -o` and run `pdftotext -layout`; strip tags from HTML) and search it for every figure on the row.\n- Read the shard's existing `fills`, `status_reviews` and `validity` first. A reopened page changes a record only when it states the value. If it does, re-write that record with `--fill` (same `ref_col`, so it replaces the old one) and KEEP every ref the old record already proposed. For example, an `UNRESOLVED` unit becomes `REFS_ADDED` with this page as its ref. A low or medium record gains this ref and is re-tiered by the normal rules. A sheet value that the page contradicts goes through standing rule 4, exactly as the main brief says. A status review is re-written only if the page changes the verdict or adds a dated source the review lacked.\n- Cite what you read. A page read as a Wayback copy is cited as the Wayback URL, with the live URL named in the note. For a pravo.gov.ru document read through its `doc_itself` view, cite the harvested URL, since both are the same live page on the same site.\n- Log every reopened citation with `--wiki-read` (used, no_value or not_this_row; dead or blocked only after the full ladder fails again, with every rung listed). Never set LNGCT_NO_BROWSER.\n- Finish with `check_shard_coverage.py` passing for each of your rows, then a one-line summary per row saying what the reopened pages changed, or that they changed nothing.\n",
 "groups": [
  [
   "P0753"
  ],
  [
   "P0752"
  ],
  [
   "P0758",
   "P2027",
   "P3894",
   "P3895"
  ],
  [
   "P2352",
   "P2353",
   "P3208",
   "P3896",
   "P3975",
   "P2425"
  ],
  [
   "P3976",
   "P7600",
   "P0734",
   "P0736",
   "P0755",
   "P0760",
   "P3603"
  ],
  [
   "P4056",
   "P4147",
   "P4148",
   "P5409",
   "P5540",
   "P5541",
   "P5542",
   "P5543"
  ],
  [
   "P6535",
   "P6635",
   "P7538",
   "P7559",
   "P7560",
   "P7612",
   "P0737",
   "P0738",
   "P0743",
   "P0751"
  ],
  [
   "P0761",
   "P0767",
   "P0774",
   "P0791",
   "P0828",
   "P1439",
   "P1455",
   "P1475",
   "P1647",
   "P1824"
  ],
  [
   "P2287",
   "P2297",
   "P2309",
   "P2334",
   "P2342",
   "P2346",
   "P2348",
   "P2350",
   "P2355",
   "P2357"
  ],
  [
   "P2362",
   "P2379",
   "P2380",
   "P2440",
   "P2707",
   "P3361",
   "P3364",
   "P3365",
   "P3369",
   "P3370"
  ],
  [
   "P3973",
   "P3974",
   "P4076",
   "P4077",
   "P4078",
   "P4094",
   "P4095",
   "P4096",
   "P4145",
   "P4146"
  ],
  [
   "P4210",
   "P5402",
   "P5403",
   "P5404",
   "P5414",
   "P5517",
   "P5521",
   "P5537",
   "P5666",
   "P5667"
  ],
  [
   "P5668",
   "P5686",
   "P5745",
   "P6540",
   "P7537",
   "P7546",
   "P7547",
   "P7615"
  ]
 ]
}
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
const WIKI_ONLY = !!A.wiki_only
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
one validated dated source makes it a change (tier medium); tier high needs >=2 independent publishers. Every URL through url_verifier. Verdict vocabulary:
- "confirm" — the recorded Status is still right; say what confirms it, with the evidence date.
- "change"  — evidence-based status change. Set proposed_status and proposed_changes as
  {column: value} pairs — Status (controlled vocab, lowercase) plus the matching date columns
  (e.g. now operating -> StartYear1; construction began -> ConstructionYear; newly shelved ->
  ShelvedYear). A change without a verified ref will be downgraded at merge — source it.
  DATES GO WITH THE STATUS (Baird 2026-10-16): stage the year AND the month (an integer 1-12)
  of the event your refs state, and check the row's other date columns against the same
  documents (ProposalYear/Month, ConstructionYear/Month, StartYear1/StartMonth1) — fix any the
  refs contradict, with the refs. If a source gives no date, say so in researcher_notes ("the
  start month was not found"). check_shard_coverage.py blocks a change with no date column.
- "stale"   — NO independent news found. Apply the dormancy rules: proposed with no progress
  >=2y -> shelved; shelved >=4y -> cancelled. proposed_changes MUST include
  ShelvedCancelledType="inferred" (lowercase — that is the live column's vocabulary, NOT
  "Presumed"), AND the year column that matches the new Status: ShelvedYear for shelved,
  CancelledYear for cancelled, set to the year of that newest dated source (never skipped, never
  left blank as "unsupported precision"; Baird 2026-10-16). The ref for the inference is the NEWEST dated independent source you found on the
  project (the one whose date is evidence_date): the last sign of life is the proof of dormancy
  (Baird 2026-10-16). Put it in proposed_refs, verified with the pipeline name, and give its date in
  the notes. Never invent a URL; if no dated source exists at all, say so. Tier medium at most.
  Set staleness_rule to "2y->shelved" or "4y->cancelled". If dormant but under the threshold,
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
- Work ONLY the units \`shard_upsert.py --remaining\` lists (its WIKI lines included: Step 0b is
  never cut), plus the status review and ONE validity record per row. Do not go hunting for blank values. If a document you are already
  reading states a blank value, you MAY stage it as a FILL (it is free) — never search for one.
- Second source: PREFERRED, NOT OWED. One validated ref closes the unit at medium. Add a second
  only if the document at hand or one quick search offers it; never spend searches chasing one --
  EXCEPT for a proposed status change, where a second independent source is worth one search (it is
  what makes the change high).
- A LONE REF THAT FAILS A CHECK (does not load, does not name this pipeline, or does not state the value)
  owes ONE bounded search (one or two queries) for an alternate that passes all three. Found: it closes the
  unit at high; keep the partial ref beside it if they mostly agree. Not found: keep the partial ref at its
  capped tier and say in the note what you searched.
- Validity: judge existence / duplicate / classification from the documents you already opened
  and the roster. Open a dedicated search only when the row's own sources fail to name the
  pipeline, or the scope guidance names this row as a duplicate/existence candidate.
- Stop when coverage prints OK and the status + validity records are saved. Do not widen scope.` : ''

const wikiOnlyInstr = WIKI_ONLY ? `

## WIKI-CITATION RECOVERY PASS (read this before starting — it narrows everything above)
This pass exists because earlier sweeps closed units from open-web searches while the row's own
gem.wiki page cited a source that states the value (P0765 TurkStream: the wiki's "US$7.8 billion"
cost is cited to an rferl.org article that passes every check; the sweep staged a weaker article
at low). Your ONLY sources this pass are the citations harvested from this row's gem.wiki page.
NO open-web search, NO new sources: if a value has no wiki citation that states it, the unit ends
UNRESOLVED with the note "no wiki citation states this value; not searched this pass".
- Your candidate list is \`${STAGING}/wiki_prepass.json\` → \`candidates\` filtered to
  \`project_id == "<PID>"\`. Each candidate is one harvested URL with: \`inline\` (the wiki
  bullet or sentence the footnote sits on — what GEM cited it FOR), \`units\` (the owed ref cells
  the wiki attributes it to, each with \`wiki_value\`, \`sheet_values\` and a \`compare\`
  verdict), \`bucket\` and, when the pre-pass could load it, \`screen\` (whether the page names
  the pipeline and where the sheet's / wiki's figures appear in its text) and \`verify\`.
  \`read_via\` is a Wayback snapshot URL that loaded when the live page did not: READ THAT, and
  cite the snapshot URL as the ref (the live URL goes in the note).
- Candidates whose ledger record is already in your shard (geometry links, confirmed dead or
  blocked after fetch.py + Wayback) are done: \`--remaining\` does not list them. Do not re-try them.
- Open EVERY remaining candidate and read the WHOLE page (strip tags, search for the figures)
  against EVERY owed unit on the row, not only the unit the wiki attached it to — one approval
  notice sources Length / Diameter / Cost / Construction / Start at once. A \`prose\` candidate (no
  attributed unit) still gets read: it is often the status / start-year source.
- A candidate that states the sheet's value → stage the ref ADDITIVELY (REFS_ADDED, same value,
  existing refs kept). A candidate that states the WIKI's value where the wiki differs from the
  sheet (\`compare.match == false\`) → a value question under standing rule 4: two independent
  validated refs on one precise figure = propose it as a FILL / change with the old value in
  researcher_notes; one ref = REFS_ADDED at medium with the discrepancy noted, sheet value stays.
  Never stage a value the page does not state.
- Length and capacity stay in the unit the page states; costs in full currency units; months as
  numbers. A ref must NAME this pipeline (an article about the system is not a ref for one segment
  unless it states the segment's figure).
- One \`--wiki-read\` record per candidate as you finish it (used / no_value / not_this_row /
  dead / blocked); it is what check_shard_coverage blocks on.
- Status review and validity: ONE record each per row, judged from the citations you opened only.
  A status-review verdict of "unclear" and a validity "confirmed (caveat)" are the honest defaults
  when the wiki's sources do not settle it; never widen to a search to settle them.
- Stop when coverage prints OK. Do not widen scope; a lead worth an open-web search goes in
  \`--lead\` for a later pass.` : ''

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
  (your STARTING POINT — you OPEN EVERY ONE in Step 0b below, before and in addition to open-web
  search; READ gem.wiki for leads but NEVER cite it).${WIKI_ONLY ? ` In THIS pass the pre-screened
  form of that list, \`${STAGING}/wiki_prepass.json\`, is your whole source set — see the
  WIKI-CITATION RECOVERY PASS section.` : ''} A row whose only support is a
  generic/aggregate citation that does not actually name this pipeline is itself an existence flag.
- Roster of ALL ${PIDS.length} in-scope pipelines (for duplicate/relabel detection — does ${pid} look
  like the same physical pipe as another row under a different name?):
${ROSTER || '  (roster omitted for this pass; judge duplicates only from the documents you open)'}

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

## Step 0b — open EVERY harvested wiki citation (Baird 2026-10-17; blocking)
\`--remaining\` lists them as WIKI lines. Before any open-web search, open each one and read it
against EVERY owed unit (capacity, length, diameter, dates, status, owner), not only the one you
are working. P1451 is why: the wiki cited two tables stating the sheet's 2 bcm/y, nobody opened
them, and a 1999 "up to 4 bcm" planned volume was staged as a change. This is IN ADDITION to your
other research, never instead of it.
- A dead or blocked link is not the end: run \`python scripts/fetch.py "<url>" --text\` (curl, TLS
  impersonation, Chrome clearance), then the Wayback CDX index
  (\`curl -s "https://web.archive.org/cdx/search/cdx?url=<url without scheme>&output=txt&filter=statuscode:200"\`,
  then \`https://web.archive.org/web/<timestamp>id_/<url>\`). The availability API
  (\`archive.org/wayback/available\`) misses captures the CDX index has; never stop at it.
- A page whose table or figure states a value for this pipeline IS a ref for it: cite the live URL,
  or the archived snapshot URL when the live one is gone.
- Save one record per citation, as you finish it:
  python scripts/shard_upsert.py --staging ${STAGING} --pid ${pid} --wiki-read '{"url": "<harvested url>", "outcome": "used|no_value|not_this_row|dead|blocked", "read_via": "<snapshot url if you read an archive>", "tried": ["scripts/fetch.py: <result>", "wayback CDX: <result>"], "note": "<what the page says, plainly>"}'
  \`used\` = it is in some record's proposed_refs. \`dead\`/\`blocked\` need BOTH fetch.py and a Wayback
  lookup in \`tried\`. check_shard_coverage blocks until every harvested citation has a record.

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
   DOWNLOADS: save any fetched file (curl -o, PDFs, pdftotext output) under \`${STAGING}/work/\`
   (gitignored) -- never the repo root or a tracked path.
3b. A 403, Cloudflare page, timeout or garbled PDF is a TOOLING failure, never a finding. Before you
   write "blocked" / "403" / "could not fetch" anywhere, run \`python scripts/fetch.py <url> --head 2000\`
   (curl -> curl_cffi TLS impersonation -> Chrome clearance; its \`notes:\` line names the route that
   worked) and READ the whole page it returns. url_verifier uses the same ladder, but a miss there is
   not final either. Name the route in researcher_notes ("read via fetch.py, cf_impersonate"); say a
   page is unreachable only after all three rungs failed, and then say so. P0278 2026-10-16: a "403 on
   every fetch" offshore-technology.com page read fine on the impersonation rung and held the system-wide
   diameter. check_shard_coverage.py blocks a blocked/403 note that never mentions fetch.py.
   NEVER set \`LNGCT_NO_BROWSER\` (not =1, not in a loop, not in a retry script) and never pass a flag or
   write a wrapper that skips the Chrome rung. It turns off the third rung, so bot-walled hosts read as
   "blocked" when they are readable (Baird 2026-10-19, after agents in the wiki recovery pass ran their
   own fetch loops with it set). If your shell already has it set, run \`unset LNGCT_NO_BROWSER\` first.
   Retries use the same full ladder; a miss on a host that returns a clearance page is retried once, then
   logged with every rung tried.
4. ONE VALIDATED SOURCE IS SUFFICIENT; >=2 INDEPENDENT IS PREFERRED. A ref that passes url_verifier,
   names THIS pipeline (name_found) and states the value (within rounding) closes the unit -- no
   second-search note is owed. Independent = separate origins (not one wire story reprinted, not two
   pages both tracing to GEM). tier: high = >=1 validated ref (sufficient, done) -- EXCEPT a status
   change, which is high only on >=2 independent publishers; medium = usable with a caveat you name,
   or a status change on one publisher; low = weak/partial/conflicting. Take a second source when it
   is cheap -- the document at hand or one quick search, a different publisher and document class --
   it sets independent=true (and a status change needs it); never hold a unit open for one. Search in the country's languages too where English is thin.
   EXCEPTION: when your ONLY ref fails one of the three core checks (loads / names this pipeline / states the
   value), spend one bounded search (one or two queries) for an alternate that passes all three. Found: it
   closes the unit at high, and the partial ref stays beside it when the two mostly agree. Not found: keep the
   partial ref at its capped tier and say in the note what you searched.
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
   OWNER = the LOWEST-LEVEL company that holds this pipeline (a JV, project company, or operating
   subsidiary such as a utility), never a parent or intermediate holding company. There is NO GEM
   convention of recording the ultimate parent. Do not research parents. If the sheet's Owner1 is a
   parent (e.g. Iberdrola for a NYSEG line) and a ref that names this pipeline names the lower-level
   owner, stage a change to that owner. A parent-level filing (merger 8-K, annual report) is never
   an owner ref. One company per Owner<N>/Operator value, a concern's contested candidate included:
   never two names joined by "/" or ";". Split into Owner1 and Owner2 with shares, or, for one
   company's old and new names, keep the current one.
5. SPEC — length, diameter, capacity, dates. CRITICALLY confirm each against a validated source (>=2 independent preferred).
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
   aggregate-vs-segment rule: a SYSTEM figure is never a ref for a SEGMENT cell.${statusInstr}${leanInstr}${wikiOnlyInstr}${EXTRA}

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
UNITS: stage LengthKnown and Capacity in the unit the SOURCE states (1,750 miles -> 1750 + LengthKnownUnits=mi; 90 MMcm/d -> 90 + MMSCMD). Never convert to km or bcm/y, and keep any conversion in the note only. The same goes for contested values.
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
log(`Critically auditing ${PIDS.length} ${COUNTRY} ${COMMODITY} pipelines in ${GROUPS.length} agent(s)${LEAN ? ' (lean pass)' : ''}${WIKI_ONLY ? ' (wiki-citation recovery)' : ''} (existence+classification first).`)
const results = await parallel(GROUPS.map(group => () =>
  agent(contract(group), { label: `audit:${group.join('+')}`, phase: 'Audit', agentType: 'general-purpose', model: MODEL })
))
const done = results.filter(Boolean).length
log(`Audit complete: ${done}/${GROUPS.length} agents returned (${PIDS.length} pipelines). Shards in ${STAGING}/rows/ — run check_shard_coverage --all.`)
return { agents_returned: done, agents: GROUPS.length, pipelines: PIDS.length }
