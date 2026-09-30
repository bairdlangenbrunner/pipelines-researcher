# Lean pass SOP — a token-budgeted deep sweep

A **lean pass** is the `deep` / `in-dev` sweep (`workflows.md` §3) run to a token budget. It
keeps the outputs researchers act on and **defers**, into a machine-readable ledger, the work
that mostly re-confirms what the sheet already says. It is a mode of the Country Sweep, not a
new workflow: same worklist, same shards, same merge, same gates, same workbook.

**Portable.** Nothing here is Russia-specific. It applies to any country / province / slice
that runs through `critical-deep-sweep`.

## When to use it

- The default whenever the weekly token budget matters more than finishing every column in one
  visit, e.g. a multi-batch campaign (Russia R4–R7, US slices, China provinces).
- **Not** for a first-ever pass on a country whose blanks nobody has looked at, where the fills
  ARE the deliverable (India, Ukraine-style 3% citation bases). Run the full deep preset there,
  or name the fill columns that matter with `--owe-fill-cols`.
- **Not** for a recovery pass. Recovery already works only the owed gap list.

## Why it is cheaper (the evidence)

Russia R3 (2026-09-15, full deep preset): 27 rows, 4.97 M subagent tokens, **~184 k per row**, and
63 k-char prompts ×27. 191 of its 222 fills re-proposed the value already on the sheet. The
outputs that changed anything were the status changes, the validity findings and the refs on
uncited values. On R2/R3 the lean cut owes **43–46 % of the units** and defers the rest.

Russia R5 Volga (2026-09-16, the pilot under this SOP): 31 rows, 275 of 467 units owed, 1.18 M
subagent tokens, **~38 k per row** (39 min wall, Sonnet), 38 k-char prompts ×11 — with 236 refs
added, 22 open validity concerns on 17 rows and no thinning against R2's operating slice. Details in
`batches/russia-gas/staging/deepsweep-r5-volga/RUN.txt`.

## What is owed vs deferred

| Unit | Lean pass | Deferred reason (`deferred_units.json`) |
|---|---|---|
| `MISSING_REF` (value on sheet, `[ref]` blank) | **owed** (rule 4e) | — |
| `HAS_REF` the script could not clear (404/410, live page missing the value, index page, page doesn't name the pipeline) | **owed** | — |
| `HAS_REF`, every link live and names the pipeline | deferred | `has_ref_cleared_by_script`: numeric/year values are validated by the script and DONE (one validated ref suffices, 2026-09-30); non-numeric values (owner, place) owe a value read only |
| `HAS_REF`, links fail only on access (timeout, 401/403/429/5xx) | deferred (`--work-blocked` keeps it) | `has_ref_access_blocked`: ref stays, Wayback add owed |
| `MISSING_VALUE` (blank value) | deferred (`--owe-fill-cols` keeps named columns) | `fills_deferred`: rule 4(c) debt, recorded |
| status review (`--status-review`), one per row | **owed** | — |
| validity record, one per row | **owed**, judged from docs already opened | — |

**Deferral is recorded, never silent.** Rule 4(c) still holds. The debt moves to
`deferred_units.json` and gets paid by a later **fills / second-source pass** over the same
ledger. A lean pass that loses its ledger has skipped the work, and that is a defect. A free
fill is still welcome: a value an agent reads in a document it already opened gets staged.

## Recipe

```bash
STG=batches/<scope>/staging/deepsweep-<batch>
./scripts/refresh_csvs.sh                                   # fresh CSV every batch
# 1. full worklist, exactly as the deep preset, but to worklist_full.json
python scripts/build_ref_worklist.py --tracker gas --country "<C>" --owe-fills --verify-existing \
  [--exclude-pids @<exclude_pids.txt>] --out $STG/worklist_full.json > $STG/worklist_build.log 2>&1
# 2. lean cut → worklist.json (owed) + deferred_units.json + lean_summary.json
python scripts/lean_worklist.py --staging $STG/ [--owe-fill-cols "Start [ref]"] [--work-blocked]
# 3. harvest from the OWED set (fewer fetches)
python scripts/harvest_wiki_citations.py --worklist $STG/worklist.json --out $STG/wiki_citations.json
# 4. trimmed brief (see "Brief budget"), then compile args with family groups
python scripts/build_deepsweep_args.py --staging $STG/ --status-review --lean --groups auto \
  --brief $STG/BRIEF.md --model sonnet --out $STG/deepsweep_args.json
#    READ the printed GROUP lines; fix a wrong grouping by editing "groups" in the JSON
#    (or pass --groups <file.json>), then re-check:
node scripts/dryrun_deepsweep.mjs $STG/deepsweep_args.json      # blocking; 0 tokens
# 5. dispatch: Workflow({ name: 'critical-deep-sweep', args: <deepsweep_args.json contents> })
# 6. close out, same as the deep preset
python scripts/check_shard_coverage.py --staging $STG/ --all    # blocking
python scripts/seed_resolutions_from_worklist.py --staging $STG/
python scripts/merge_deepsweep_shards.py --staging $STG/
python scripts/sweep_gates.py --staging $STG/                   # J reads "skipped — lean pass: N deferred"
python scripts/build_ref_workbook.py --staging $STG/ --output <deliverable>.xlsx
python scripts/recalc.py <deliverable>.xlsx
```

`shard_upsert.py --init` falls back to `worklist_full.json` for a row with no owed units, so such
a row still gets a shard carrying its status review and validity record.

## The four levers (and their guardrails)

1. **Cut the worklist**, as above. Choose `--has-ref live` (the default). `strict` also sends every
   non-numeric cited value to an agent, which costs more and rarely pays.
2. **Family groups.** One agent owns 2–4 rows that share documents (same `PipelineName`
   strings/stages, one hub's spurs, one trunk's loops). It researches the shared decree / programme /
   annual report once. Every row still gets its own shard, Step 0, status, validity and
   coverage OK, so merge and gates see no difference. Caps are `--max-group 4` and
   `--max-group-units 60` owed units. Review `--groups auto`: it groups by shared name, then by
   shared leading hub, and a big hub (e.g. "Ukhta-") can pull together unrelated lines. Split those.
   Never group across a ≥2-independent-source dependency: a sibling row's figure is not a second
   source.
3. **Brief budget: ≤ 15–20 k chars** (`build_deepsweep_args.py` warns above 20 k). Every agent
   pays for every character, and R3's 42 k brief cost 23 agents about 1 M prompt chars before any
   research started. Keep only what THIS batch needs:
   - the row-specific traps (known 404s, suspected duplicates, audit typos, classification tests)
   - the operator/source ladder for this region
   - banned and weak surfaces

   Cut campaign history, other batches' results and anything already in the workflow contract.
   Point at the country note for background; never paste it. **Always inline the brief**
   (`--brief`). `extra_brief_path` is not read (R2: 8/8 agents skipped it).
4. **Cheapest sufficient model, chosen at dispatch.** Use Sonnet for research agents. Use Haiku
   only for mechanical rechecks (re-verifying a URL list, a coverage re-dispatch with a precise gap
   list). Judgment stays in the main loop: brief, grouping review, gates and delivery note.

## Orchestrator discipline (where main-loop tokens go)

- **One batch per session.** Start a fresh chat per batch from the batch's `PLAN.md`. A long
  campaign session re-reads its whole history on every turn.
- **Scripts before agents.** Anything deterministic (verification, coverage, gates, counts) runs as
  a script. Its output is summarized, never pasted back wholesale.
- **Defect log, not mid-batch fixes.** An engine bug found mid-batch goes into `$STG/DEFECTS.md` (one
  line each: symptom, file, row). Fix it in a separate session unless it blocks delivery. The
  exception is a defect that corrupts THIS batch's output: fix it before merging.
- **No side quests.** Recon re-runs, doc cleanups and other countries wait.
- **Monitor lightly.** One check about 5 minutes in (confirm the prompts landed in live
  transcripts), then wait for the completion notification. Don't poll.

## Measure it (every lean batch)

Write `$STG/RUN.txt`: workflow run id, agents, wall time, **total subagent tokens**, rows,
**tokens per row**, and the `lean_summary.json` counts (full → owed, deferred by reason). Compare to
the reference: **R3 full deep = ~184 k tokens/row**. Also record outputs per row (status changes,
open validity concerns, refs added). A cheaper pass that finds nothing is not a win.

## Paying the deferred ledger later

`deferred_units.json` has the worklist-unit shape plus `defer_reason`. Build a follow-up pass from
it into its own run dir: fills first, then value reads on the non-numeric cleared refs, then Wayback adds
for the blocked ones. That can be one cross-batch pass per campaign, sorted by the columns
researchers care about. It does not have to be one pass per batch. Until that pass runs, the
batch's delivery note and country note say **"lean pass: N units deferred"**, with the reason
counts.
