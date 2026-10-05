Belarus gas deep sweep: setup is done, dispatch and finish it. Use a workflow (I opt in to multi-agent orchestration for this run).

Repo: pipelines-researcher, branch main. Read CLAUDE.md, docs/workflows.md section 3 (deep / in-dev presets) and docs/sops/sweep.md before acting.

State (2026-10-05):
- Fresh snapshots pulled 2026-10-05 (data/GGIT_gas_snapshot_20261005.csv).
- Scope: Belarus gas, preset deep (refs + fills + validity + routes + recon), all statuses. Gas only; oil is out of scope.
- 20 Belarus gas rows. 8 are already staged by other runs and are excluded from the research legs: P0750, P0769, P3483, P5654, P5655 (Russia) and P0779, P3484, P5938 (Ukraine). List: batches/belarus-gas/carried_from_others.txt. The recon leg keeps all 20.
- Research set: 12 rows (P0806, P3486, P6967, P6968, P7020, P7021, P7022, P7027, P7028, P7029, P7030, P7032), 183 units: 42 uncited values, 68 existing refs to re-check, 73 blank values owed a fill.
- Run dir: batches/belarus-gas/staging/deepsweep-20261005/ (STG). Worklist built with --owe-fills --verify-existing. Baseline seeded (staged_resolutions.json, 110 ref records). Args built (deepsweep_args.json). Rows dir not created yet.
- GulfPub recon already run: batches/belarus-gas/staging/recon-gulfpub-20261005/ (34 reference records, 22 overlaps, 12 additions all NEAR_MISS, 3 status conflicts, 10 ambiguous). Crosswalk not yet built.

Known quirk: scripts/dryrun_deepsweep.mjs reports FAIL on all 12 agents because it requires the marker `shard_upsert.py --remaining`, which only the lean-pass branch of the workflow prints. The full-deep prompt does tell agents to use shard_upsert.py (workflow lines 146-147). Ignore that FAIL. Do not fix the script mid-batch; log it as a defect.

Do, in order:
1. Dispatch: Workflow({ name: 'critical-deep-sweep', args: <contents of STG/deepsweep_args.json> }). Pick the subagent model at dispatch time, cheapest that is good enough (Sonnet is fine for the research agents). Keep merge, gates and QC judgment in the main loop.
2. When it finishes: python scripts/check_shard_coverage.py --staging $STG/ --all. Re-dispatch just the gap PIDs if any (resume the same run with resumeFromRunId, or a follow-up run with pids = the gap list).
3. python scripts/merge_deepsweep_shards.py --staging $STG/ (baseline is already seeded, do not re-seed).
4. python scripts/harvest_sentinel_findings.py --staging $STG/ (last, per workflows.md).
5. python scripts/sweep_gates.py --staging $STG/ and quote the gate counts. Gate L must read 0. If not, run a recovery pass (workflows.md section 3, ref_shards_recovery).
6. python scripts/harvest_wiki_citations.py --worklist $STG/worklist.json --out $STG/wiki_citations.json (visit gem.wiki, never cite it).
7. python scripts/build_recon_crosswalk.py --match-diff batches/belarus-gas/staging/recon-gulfpub-20261005/match_diff.json --sweep-dir $STG/
8. Build the deep-sweep workbook into batches/belarus-gas/deliverables/ (stamp from TZ=America/New_York date "+%Y%m%d_%H%M_ET"), per workflows.md section 3 and the QC SOP pre-delivery checks. Do not paste computed or formula columns.
9. At delivery, run review_app/scopes.py check. If it exits 3, ask me "Add Belarus gas to the review app? Y / n / later" and scopes.py set my answer.
10. Add a Belarus entry to docs/country_notes/ (new file) and a one-line pointer under Pending country items in CLAUDE.md. Regenerate batches/INDEX.md with python scripts/staged_summary.py --index. Commit lowercase, succinct, no co-author line.

Standing rules to carry into the agent briefs: never cite GEM; never fabricate URLs; banned hosts (abarrelfull, theodora.com, yingdodo.com); one validated ref closes a unit, a status change is green only on 2+ independent publishers; stage length and capacity in the source's original units; costs in full currency units; never propose removing an existing ref; notes written in plain language per the notes style rule. Never write the live sheet or the routes repo.

Context to flag in the delivery note: Belarus rows are mostly Torzhok-Minsk-Ivatsevichy branch lines (P7020 to P7032) that are one bulk-load family with sparse data, so check for duplicates among them. P0806 (Yamal-Europe 2) is cancelled and Researcher WA; P3486 Kobryn-Brest-Warsaw and P6967 Volkovysk-Gosgranitza are the Poland interconnects.
