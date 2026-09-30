# R5 Volga — lean-pass pilot (plan, 2026-09-16)

First Russia batch run as a **lean pass** (`docs/sops/lean_pass.md`). Baird's ruling on 2026-09-16:
the weekly token budget is the constraint. Run this batch in ONE fresh session and stop at
delivery. Log engine defects in `DEFECTS.md` and don't fix them mid-batch unless they corrupt this
batch.

## Scope

31 rows / 467 full units from the state audit
(`../state-audit-20260914/batches/r5-volga/include_pids.txt`, `exclude_pids.txt` = the other 254).
29 operating, P2385 retired, **P2425 Pochinki–Anapa construction**, **P4063 Zorkino–Balakovo
proposed**. 30 of 31 rows were last touched in 2023. That staleness is the point of the status review.

Audit flags to carry into the brief (owed `Location [ref]` fixes; stage them if a source is already
open, else note):
- typos: P1466 `Lipetsk` → `Lipetsk Oblast`; P2341 `Republic of Udmurtia` → `Udmurt Republic`;
  P2425 `Nizhgorod Oblast` → `Nizhny Novgorod Oblast`
- geometry: P5714 START_MISMATCH; P2365, P2375 OK_REVERSED; P2310 OK_INTERIOR
- duplicate candidates: P5715/P5716 (Perm–Gorky I vs II, 0.987); P2340/P5744 (Minnibaevo–Kazan I vs
  II, 0.973); P5714 vs P2351/P5712 (Nizhnyaya Tura–Perm I/II are in R4b, **not this batch**, so
  judge the III line on its own evidence and note the sibling PIDs)

## Proposed family groups (11 agents instead of 31) — `groups_proposed.json`

| group | rows | shared documents |
|---|---|---|
| Nizhnyaya Tura–Perm–Gorky | P5714, P5715, P5716 | one trunk system, Gazprom Transgaz Chaikovsky / Nizhny Novgorod |
| Pochinki hub | P0756, P2370, P2371, P2372 | Pochinki CS, Gazprom Transgaz Nizhny Novgorod |
| Minnibaevo | P2340, P5744, P2341 | Tatarstan, Gazprom Transgaz Kazan |
| Orenburg | P2364, P2365, P2298, P2375 | Orenburg GPZ / Gazprom Dobycha Orenburg |
| Gorky | P2309, P2310, P2322 | Gorky (Nizhny Novgorod) hub |
| Saratov | P2383, P2385, P1466, P2342 | Gazprom Transgaz Saratov; Saratov–Moscow is the historic first trunk |
| Bashkortostan | P2388, P2390, P2435, P5743 | Gazprom Transgaz Ufa |
| Ulyanovsk | P2286, P2430, P5746 | Gazprom Transgaz Samara / Ulyanovsk gasification |
| solo | P2425 (construction), P4063 (proposed, distribution), P4112 (distribution) | status-heavy; own agent |

Compare against `--groups auto` output; split any group over ~60 owed units.

## Commands (run in the new session, in order)

```bash
STG=batches/russia-gas/staging/deepsweep-r5-volga
AUD=batches/russia-gas/staging/state-audit-20260914/batches/r5-volga
./scripts/refresh_csvs.sh
python scripts/build_ref_worklist.py --tracker gas --country Russia --owe-fills --verify-existing \
  --exclude-pids @$AUD/exclude_pids.txt --out $STG/worklist_full.json > $STG/worklist_build.log 2>&1
grep "scope:\|units:" $STG/worklist_build.log          # expect 31 rows
python scripts/lean_worklist.py --staging $STG/        # record full → owed in RUN.txt
python scripts/harvest_wiki_citations.py --worklist $STG/worklist.json --out $STG/wiki_citations.json
# write $STG/BRIEF.md — TARGET ≤15 k chars (see "Brief" below)
python scripts/build_deepsweep_args.py --staging $STG/ --status-review --lean \
  --groups $STG/groups_proposed.json --brief $STG/BRIEF.md --model sonnet --out $STG/deepsweep_args.json
node scripts/dryrun_deepsweep.mjs $STG/deepsweep_args.json   # must exit 0
# dispatch: Workflow({ name: 'critical-deep-sweep', args: <deepsweep_args.json> }); one check ~5 min in
python scripts/check_shard_coverage.py --staging $STG/ --all
python scripts/seed_resolutions_from_worklist.py --staging $STG/
python scripts/merge_deepsweep_shards.py --staging $STG/
python scripts/sweep_gates.py --staging $STG/
STAMP=$(TZ=America/New_York date "+%Y%m%d_%H%M_ET")
python scripts/build_ref_workbook.py --staging $STG/ \
  --output batches/russia-gas/deliverables/pipelines_batch_${STAMP}_russia-gas_deepsweep-r5-volga.xlsx
python scripts/recalc.py batches/russia-gas/deliverables/pipelines_batch_${STAMP}_russia-gas_deepsweep-r5-volga.xlsx
```

## Brief (≤15 k chars; R3's was 42 k)

Build it from R3's `BRIEF.md`, keeping only what applies to Volga:
- the Russia-wide rules that bit before: Cyrillic name search, the `магистральный газопровод` /
  `газопровод-отвод` / `межпоселковый` classification test, the aggregate-vs-segment rule for
  corridor figures, never retiring a geo-blocked gazprom link
- the Volga operator ladder: Gazprom Transgaz Nizhny Novgorod / Kazan / Samara / Saratov / Ufa /
  Chaikovsky, regional gasification programmes, decree 816-р / 3302-р items, neftegaz.ru /
  interfax.ru, and the weak surfaces to replace
- this batch's traps (audit flags above) and the status focus: 30 rows stale since 2023, P2425 and
  P4063 in development, P2385 retired (confirm the retirement evidence)

Cut the R1–R3 history, the NW-specific source lists and anything the workflow contract already says.

## Success metric (write to RUN.txt)

Workflow run id, agents, wall time, **total subagent tokens, tokens/row**, and the
`lean_summary.json` counts. **Reference: R3 full deep = ~184 k tokens/row (4.97 M / 27).** Target:
≤ ~70 k/row (≈2.2 M total). Quality check: every row has a status review and a validity record,
gate L = 0, and the per-row count of status changes and open validity concerns is not visibly
thinner than R1–R3's.

## Delivery

Update `docs/country_notes/russia.md` (R5 entry: counts, "lean pass: N units deferred" by reason,
tokens/row vs R3). Add a short memo section. If the pilot misses its target or thins the
findings, amend `docs/sops/lean_pass.md` with the adjustment before R4a. Don't commit unless Baird asks.
