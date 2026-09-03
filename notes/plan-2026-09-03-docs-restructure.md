# Plan — restructure the docs redundancies (2026-09-03; not yet started)

Findings from the 2026-09-03 docs audit (Explore agent, 62 tool uses, every cited script/flag/path
verified real). The repo's rules are sound; its problem is that the same facts are narrated in two
or three places, so every update has to land three times and CLAUDE.md is 1,009 lines of which 57%
is per-country narrative that its own header says should be one-line pointers.

**Principle for the whole job: one fact, one home, pointers everywhere else.** The home for each
class of fact:

| Class of fact | Home | Everything else |
|---|---|---|
| Standing rules, hard requirements, router, vocab | `CLAUDE.md` (unchanged) | SOPs may *echo* one line + pointer |
| Country state and open items | `docs/country_notes/<country>.md` | `CLAUDE.md` bullet ≤ 3 lines; `research_backlog.md` one line |
| Engine bug ledgers (what broke, A/B, re-runs) | `notes/escalation-*.md` | `CLAUDE.md` Active workstreams: one paragraph per bug + pointer |
| Rules the bugs taught (e.g. never `==` on a country string) | the relevant SOP (`reconciliation.md`, `sweep.md`) | `CLAUDE.md` one sentence |
| Sweep rules and prose | `docs/sops/sweep.md` | `workflows.md` §3 = commands + one-line pointers |
| Disposition triage (ROUTE_FOR_EXISTING …) | `docs/sops/reconciliation.md` | `workflows.md`, `sweep.md`, `CLAUDE.md` router: one line + pointer |
| Confidence/tier rubric | `docs/reference/confidence_tiers.md` | `sweep.md` keeps only the tier→COLOR table |
| Workbook layout | `docs/reference/workbook_conventions.md` | — |

## Guardrails (apply to every phase)

- **Docs only.** Nothing under `batches/` data, `sources/`, or `scripts/` changes except Phase 7,
  which is opt-in. No live sheet, no routes repo, no email.
- **Every fact removed from a file must land in its home first**, in the same commit. Verify with
  the token check below before each commit: no PID, date, URL, `notes/` path or number from the
  removed text may be absent from the destination.
- **Do not rewrite the load-bearing sections of CLAUDE.md** (Standing rules, Live data access,
  Workflow router, Hard requirements, Controlled vocabulary, External tools, Common commands, When
  starting a new task). They stay verbatim.
- **Do not restructure the country notes' internal layout** — append or merge into their existing
  open-items sections; fix contradictions when touching a section.
- **One commit per phase**, lowercase message, no co-author trailer. Private repo, so names are fine.
- Read `docs/country_notes/_template.md` before touching any country note.

**Token check** (run before committing each phase; `$OLD` = the text you removed, saved to a scratch
file, `$DEST` = the file(s) it should have landed in):

```bash
grep -oE 'P[0-9]{4}|20[0-9]{2}-[0-9]{2}-[0-9]{2}|notes/[a-z0-9._-]+\.md|https?://[^ )`]+|[0-9]+(\.[0-9]+)? ?(km|rows|units|cells)' "$OLD" \
  | sort -u | while read t; do grep -qF -- "$t" $DEST || echo "MISSING: $t"; done
```

An empty result means nothing was lost. A `MISSING` line means the fact was not carried and the
commit is not ready.

## Phase 0 — clean starting point

The working tree currently carries ~33 modified files from 2026-09-03 (the MZ-feedback engine work:
`--owe-fills`, `name_found`, `relevance_qc`, `sweep_gates.py`, SOP/contract edits, two plan notes)
plus older uncommitted edits. **Commit those first** (or have Baird do it) so the restructure diffs
are readable on their own. Then `git status` must be clean before Phase 1.

## Phase 1 — CLAUDE.md "Pending country items" → country notes (the big one)

Section spans `### Pending country items` to `## External tools & resources`; 15 country bullets;
~570 lines. Target after: **≤ 60 lines**, every bullet ≤ 3 lines.

For each bullet, in this order (largest first: Egypt ~160 lines, Uzbekistan ~105, China ~105, then
Iraq, Kazakhstan, Ukraine, Malaysia, India, Pakistan, Libya, Saudi Arabia, Israel, Iran, US, Nigeria):

1. Copy the bullet to a scratch file (`$OLD`).
2. Open `docs/country_notes/<country>.md`. For every claim in the bullet, find it in the note. Any
   claim **not** in the note gets merged into the note's open-items / ledger section in the note's
   own tone (most will already be there — the notes are the fuller version for every country checked).
   Where the two disagree, the note wins unless CLAUDE.md is dated later; fix the stale one.
3. Collapse the CLAUDE.md bullet to the template:
   `- **<Country> (<commodity>: <state> <date>; <N> files to work):** `docs/country_notes/<c>.md``
   plus at most one more line for a structural warning the next session must know before opening
   the note (e.g. "recons are standalone, not in the packet", "13 rows are Kazakhstan's").
4. Run the token check with `$DEST=docs/country_notes/<country>.md notes/*.md`.

Keep the section's header paragraph ("One-line pointers only…") — it is now true. Commit:
`claude.md: collapse pending country items to pointers; facts live in country notes`.

## Phase 2 — CLAUDE.md "Active workstreams" → escalation notes + SOPs

Item 1 (~65 lines: GulfPub engine, multi-country JOIN bug, Cyrillic-name bug, `osm_id_key`) becomes
one paragraph per bug: what it was, the date fixed, the rule it taught (one sentence), the pointer to
its `notes/escalation-*.md` / `sources/osm/NOTES.md`. The **rules** the bugs taught move to the SOP
if not already there — check `docs/sops/reconciliation.md` for: "a country scope is a JOIN, never a
bare `==`", "a diagnostic must report the MATCHER's view of the data", "a thin recon is a claim about
the pipeline until the input count is checked", "`MATCH_QUALITY` is fixed by `geoarea_weight`, never
a threshold". Add what is missing there. Items 2–3 are already short; leave them. Target: section
≤ 25 lines. Token check with `$DEST="notes/*.md docs/sops/reconciliation.md sources/osm/NOTES.md"`.

## Phase 3 — `workflows.md` §3 vs `docs/sops/sweep.md`

`workflows.md` is the command sheet; `sweep.md` is the rulebook. In §3 (lines ~111–281):

- Keep: the legs table, presets, every command block, the transit-country exclusion mechanics
  (`--exclude-pids`) as commands + one sentence each.
- Move to `sweep.md` (or delete if already there — check first): the MATCH_QUALITY health-line
  example with the Iraq figures (it is in `sweep.md` § recon leg already — delete the §3 copy), the
  disposition triage prose (home is `reconciliation.md`; leave one line + pointer), the
  "harvester runs LAST" rationale (keep the ordering in the command block with a `# harvester LAST`
  comment; the *why* stays in `sweep.md`).
- Same treatment for §2 and §6 if they restate SOP prose (check `reconciliation.md` and `qc.md`).

Disposition triage appears in five files (`workflows.md`, `sweep.md`, `reconciliation.md`,
`research_backlog.md`, `CLAUDE.md` router). Canonical = `reconciliation.md`; the router keeps its
one-paragraph routing note (it is routing, not procedure); the other three point. Commit:
`docs: workflows.md is commands, sweep.md is rules; disposition triage has one home`.

## Phase 4 — tier rubric has one home

`sweep.md` restates the green/yellow/red rubric in its Sequence step 4 and again under "Tier →
color", and re-derives the P5984/eurasianet status-inference example that `confidence_tiers.md`
also carries. Keep the **Tier → color** table (colour is a workbook fact, not a rubric fact) and the
step-4 procedure; replace rubric prose with "tier per `confidence_tiers.md`" pointers; keep the
eurasianet example in `confidence_tiers.md` only. Commit: `sweep sop: tier rubric points at
confidence_tiers.md`.

## Phase 5 — `docs/research_backlog.md` becomes an index

Sections 2–4 narrate the same open threads as the country notes (Kazakhstan is the clearest
three-way copy). Rule for the file: **one line per open thread — scope, what is open, pointer** — no
prose. Move any fact the country note lacks into the note first (token check), then collapse.
Keep §4 "Decisions needed from Baird" as the one cross-country list of decisions, one line each.
Update the header sentence to describe this role. Commit: `research backlog: index only, one line
per thread`.

## Phase 6 — retire the two superseded docs (PROPOSE, then do on Baird's OK)

- `docs/GOIT_Pipeline_Research_Workflow.md` (285 lines): the still-live part is **Phase 3 search
  strategies**, referenced by `docs/sops/discovery.md` and mirrored in
  `.claude/workflows/country-discovery.js` `STRATEGIES`. Move that section into `discovery.md` (or a
  `docs/reference/search_strategies.md`), repoint both references, then move the file to
  `docs/archive/` with a one-line header saying what superseded it (`workbook_conventions.md`,
  `confidence_tiers.md`, `qc.md`). Its Phase 4 column-formatting rules duplicate
  `workbook_conventions.md` verbatim; its "3-sheet Excel" description predates the two-file packet.
- `docs/PROJECT_SETUP_AND_CONTEXT.md` (221 lines): already self-labelled historical. Move to
  `docs/archive/`; fix the stale vocabulary table (line ~115, `Delayed`/`Opposition` are lowercase)
  before archiving so the archive is not wrong; repoint the CLAUDE.md intro line.
- Update the CLAUDE.md "Where things live" list accordingly.

Ask before executing this phase: archiving vs deleting is Baird's call. Default is archive.

## Phase 7 — promote the two most-copied bespoke scripts (PROPOSE, then do on Baird's OK)

57 bespoke Python scripts live under `batches/*/staging/*/`. Two are genuine engine pieces copied
per batch and all copies differ (six distinct md5s / five distinct md5s):

- `build_redundancy.py` — iraq, india, ukraine, uzbekistan, kazakhstan, libya (`staging/redundancy/`)
- `build_leg3_briefs.py` — ukraine, libya, india, pakistan, kazakhstan (`staging/qc/`)

For each: diff all copies against the newest (Uzbekistan / Kazakhstan), list every divergence, fold
them into one `scripts/<name>.py` taking `--scope`/`--staging` arguments (same pattern as
`scripts/sweep_gates.py`, promoted 2026-09-03 from Jiangxi's `predelivery_checks.py`). Leave the
batch copies in place — they are the record of committed runs — and prepend a one-line
"SUPERSEDED by scripts/<name>.py" docstring, as was done for `predelivery_checks.py`. Then fix
`workflows.md` §3's "copy the Libya or Iraq script" line. Test each promoted script against one
archived staging dir and confirm identical output before committing.

## Phase 8 — small gaps (do with Phase 3)

- `docs/reference/route_conventions.md` never mentions the RouteAccuracy **unbuilt cap**
  (`controlled_vocab.md` "the unbuilt cap (Baird 2026-08-06)"). Add one line + pointer in its
  accuracy-ladder table.
- Already fixed 2026-09-03: `GOIT_Pipeline_Research_Workflow.md` `Delayed`/`Opposition` casing,
  `research_backlog.md` header date, theodora named in CLAUDE.md rule 5.

## Done when

- `wc -l CLAUDE.md` ≤ ~450 and "Pending country items" ≤ 60 lines.
- Every token check empty; `git log` shows one commit per phase.
- `grep -c ROUTE_FOR_EXISTING docs/workflows.md docs/sops/sweep.md docs/research_backlog.md` ≤ 1
  each (the pointer line).
- A final report listing, per phase, lines removed / lines added to the home / MISSING tokens (must
  be 0) / anything found contradictory between the copies and which version won.
