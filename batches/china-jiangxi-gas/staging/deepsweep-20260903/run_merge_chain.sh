#!/usr/bin/env bash
# Jiangxi gas v3 -- merge chain, in the ONE order that does not lose data.
#
# The order is not stylistic. merge_deepsweep_shards' is_old_deepsweep() drops any record
# whose ref_col is __VALIDITY__ -- which is exactly what harvest_sentinel_findings WRITES.
# So the harvester must run LAST; harvesting earlier zeroes the sentinels out silently
# (verified empirically on the v1 batch: 2 -> 0, no warning).
#
# recalc.py validates a BUILT workbook (positional xlsx), so it runs after the build,
# not before it.
#
# The normalizers (step 0a-0e) all rewrite shards/ in place and so must precede
# split_shards.py; see the block comment at that step.
#
#   ./run_merge_chain.sh
set -euo pipefail
cd "$(dirname "$0")"
REPO=$(cd ../../../.. && pwd)
STG=batches/china-jiangxi-gas/staging/deepsweep-20260903
STAMP=$(TZ=America/New_York date "+%Y%m%d_%H%M_ET")
XLSX="batches/china-jiangxi-gas/deliverables/pipelines_batch_${STAMP}_china-jiangxi-gas_deepsweep.xlsx"

step() { printf '\n\033[1m=== %s\033[0m\n' "$*"; }

step "0. validate shards (structural contract)"
python3 validate_shards.py

# ---------------------------------------------------------------------------------
# NORMALIZERS. Every one of these rewrites shards/*.json in place, so they ALL must
# run before split_shards.py, which regenerates ref_shards/ and rows/ from shards/
# on every run -- a normalizer that runs after it edits a source that nothing reads
# again. Each is idempotent and each is a dry run without --apply.
#
# The order among them matters at both ends. normalize_banned_hosts.py is FIRST
# because it REMOVES refs and everything after it counts them -- independence and tier
# must be judged on the post-strip list. normalize_schema_keys.py is the last
# conformance gate, so it runs after the passes that mutate value keys and catches
# anything they left off-contract. (normalize_owner_entities.py re-syncs its own
# `value_cols` now, so this is belt-and-braces rather than load-bearing.)
# ---------------------------------------------------------------------------------
step "0a. normalize_banned_hosts.py  (banned tertiary aggregators are never a [ref])"
# FIRST normalizer, deliberately: it removes refs, and every judgment after it counts
# refs. normalize_independence.py's "kept<2 is not independent" rule and the tier must
# both see the POST-strip list, or a record keeps a `high` earned by a ref that no
# longer exists. Added 2026-09-10 after 4 P4791 records cited yingdodo.com (小柱工程, a
# construction-leads database) off a page that is an explicit marketing sample.
# The host is now in url_verifier.BLOCKLIST_HOSTS, so the verifier, merge_qc and
# sweep_gates all reject it upstream of here -- this step exists for shards ALREADY
# written (the blocklist cannot retroactively edit a landed shard) and as the belt to
# that braces. A record left with zero refs exits non-zero for hand adjudication
# rather than being auto-downgraded: that is an orphan [ref], a human call.
python3 normalize_banned_hosts.py --dir shards --apply
python3 normalize_banned_hosts.py --dir rows   --apply

step "0b. normalize_independence.py  (kept<2, and same-origin refs, are not independent)"
python3 normalize_independence.py --apply

step "0c. normalize_owner_entities.py  (46% holder; projco ownership model)"
python3 normalize_owner_entities.py --apply

step "0d. stage_olsn_paste_defect.py  (P4785-P4790 sliced-sentence cells)"
python3 stage_olsn_paste_defect.py --apply

step "0e. normalize_cross_row_leads.py  (every lead target must be one real PID)"
python3 normalize_cross_row_leads.py --apply

step "0e2. stage_p5861_retirement.py  (P4778 <-> P5861 reciprocal redundancy ruling)"
python3 stage_p5861_retirement.py --apply

step "0e3. stage_fuelsource_ruling.py  (Ganzhou South Branch: one branch, two sources)"
# Writes shards/ AND ref_shards_recovery/P4787.json. The recovery copy is not redundant:
# merge_ref_shards.py is last-writer-wins per (project_id, ref_col, sheet_row) and step 2
# passes ref_shards before ref_shards_recovery, so the recovery store overwrites whatever
# split_shards.py generates from shards/. Staging the ruling only in shards/ would leave
# the superseded CONTRADICTION record winning the merge, exactly as it did in the
# 2026-09-10 build.
python3 stage_fuelsource_ruling.py --apply

step "0e4. stage_fuelsource_orthography.py  (one canonical spelling per source system)"
# Runs AFTER 0e3, which sets the four Ganzhou rows to the canonical form this step
# normalizes everything else onto -- run it before and those four would be rewritten
# from a spelling the ruling had not yet issued. Touches shards/ only, and asserts on
# entry that no row in its scope has a FuelSource record in ref_shards_recovery/
# (which would win the merge and make the edit invisible in the deliverable).
# Carries one ruling, not just spellings: P4789's FuelSource narrows to West-East Gas
# Pipeline 2 and the record moves UNRESOLVED -> REFS_ADDED, because two independent
# sources confirm that one part of its three-part value and rule 4(e) forbids filing
# UNRESOLVED when something narrower was found.
python3 stage_fuelsource_orthography.py --apply

step "0e5. stage_name_found_recheck.py  (rule-4(a) relevance flags, adjudicated)"
# The name_found recheck re-ran url_verifier --name over all 27 verifications in the
# store carrying name_found:false; 14 came back true, and each one would lift a
# merge_qc relevance cap, so all 14 were adjudicated by hand. 13 REJECTED (11 matched
# only a parent/system name form -- for a branch row that is the CORRECT negative;
# 2 were a url_verifier false positive matching a Latin name against raw markup), 1
# ACCEPTED: P5862 Location [ref] names 奉新支线, its own segment, so tier low ->
# medium. Touches shards/ only; guards the recovery store on entry like 0e4. Order
# within 0e* does not matter -- no other step touches this record.
python3 stage_name_found_recheck.py --apply

step "0e6. stage_p5887_independence.py  (the one off-contract independence field)"
# P5887's __STATUS__ sentinel carried 1 proposed ref + 1 verification at tier medium
# with `independent: null`, which made it invisible to gate D in BOTH directions --
# never flagged as an over-claim, never counted as single-source. It cannot be fixed
# by 0b: normalize_independence.py's gate is `if not r.get("independent") or
# rc.startswith("__"): continue`, so falsy None is skipped and every __* sentinel is
# skipped regardless. One ref is one publisher -> False. The other 43 null-independent
# records have zero refs AND zero verifications, so they claim nothing and stay null.
# Mechanical schema fix, stamped in researcher_notes; idempotent. Order within 0e*
# does not matter -- no other step touches this record.
python3 stage_p5887_independence.py --apply
python3 stage_p5887_independence.py --apply --dir ref_shards_recovery

step "0e7. stage_p4944_start_location.py  (the refs leg cannot change a non-blank value)"
# P4944's Location [ref] is REFS_ADDED at tier high, and its own notes plus its
# __VALIDITY__ concern say those refs place the origin station 南昌分输压气站 in
# 大城镇/高安市 (Yichun), not in the recorded 东阳镇/安义县 (Nanchang). I first staged the
# correction onto that record's `values`; it reached ref_shards/ and stopped there.
# merge_ref_shards.py writes class_out/refs/verifications/tier/independent/notes onto a
# SEEDED record and never its `values` -- by design, because the refs leg does not change
# values; it carries one only for an owed BLANK appended as a FILL. So a non-blank cell
# that is simply wrong has exactly one channel to the deliverable: the __VALIDITY__
# concern. This step reverts the values (shards/, ref_shards/ and the store agree again)
# and puts the ruling in that concern's `recommendation`, which harvest_sentinel_findings
# now honours per-record instead of stamping one boilerplate line on all 99 findings.
python3 stage_p4944_start_location.py --apply
python3 stage_p4944_start_location.py --apply --dir ref_shards_recovery

step "0e8. stage_orchestrator_recommendations.py  (rulings go in the Recommendation column)"
# harvest_sentinel_findings.py stamped ONE boilerplate recommendation on all 99 sentinel
# findings and overwrote whatever the shard had put there. It now honours a per-record
# `recommendation`, which also stopped it discarding the two the row agents had written
# themselves (P4931, P4944's StartYear1 concern) -- 341 sentinel records across every
# staging dir in the repo, 6 carry one, all 6 in this batch, so no committed run moves.
# This step fills in the four DEFINITE rulings (P5861 retirement, both sides; P5866's
# orthography fix; P5862's batch-wide phase ruling). Everything else keeps the boilerplate
# on purpose: "flagged for human review" is the honest recommendation for an open
# question, and a recommendation field is not a licence to convert one into an
# instruction. Must precede step 4, the harvester, which is what reads the field.
python3 stage_orchestrator_recommendations.py --apply
python3 stage_orchestrator_recommendations.py --apply --dir ref_shards_recovery

step "0f. normalize_schema_keys.py  (LAST normalizer -- final conformance gate)"
python3 normalize_schema_keys.py --apply

step "0g. re-validate after the normalizers"
python3 validate_shards.py

step "1. split_shards.py  -> ref_shards/ + rows/"
python3 split_shards.py

step "1b. check_shard_coverage.py --all  (rule 4(e) per-unit gate)"
# Reads rows/ + ref_shards/, so it can only run AFTER split_shards -- and it must run
# BEFORE any merge, because a unit that no shard reports on becomes an UNRESOLVED with
# empty notes downstream, indistinguishable from "nobody looked". Exit 1 here is a hard
# stop by design: the fix is a recovery pass over the named units, not a merge.
cd "$REPO" && python3 scripts/check_shard_coverage.py --staging "$STG" --all
cd - >/dev/null

# ---------------------------------------------------------------------------------
# RECOVERY LEG. build_refsweep_briefs.py --from-coverage scopes briefs to exactly the
# units step 1b reported unreported, and its agents write ref_shards_recovery/<PID>.json.
# That dir is NOT under split_shards.py's control -- split only regenerates ref_shards/
# and rows/ (and wipes their stale P*.json), so recovery output survives a re-split, but
# for the same reason the 0a-0e normalizers' shards/ globs never reach it. Normalize it
# separately here, or a recovery record citing two of the five same-origin Jiangxi
# documents keeps a bogus `independent: true` and an off-contract key reaches the builder.
# ---------------------------------------------------------------------------------
if ls ref_shards_recovery/P*.json >/dev/null 2>&1; then
  step "1c. normalizers over ref_shards_recovery/  (recovery shards bypass the shards/ globs)"
  python3 normalize_banned_hosts.py  --dir ref_shards_recovery --apply
  python3 normalize_independence.py  --dir ref_shards_recovery --apply
  python3 normalize_owner_entities.py --dir ref_shards_recovery --apply
  python3 normalize_schema_keys.py    --dir ref_shards_recovery --apply
else
  step "1c. no ref_shards_recovery/P*.json -- no recovery leg to normalize (skipped)"
fi

step "2. merge_ref_shards.py  (BOTH shard dirs -- the default is ref_shards/ alone)"
# --shard-dir defaults to ["ref_shards"], so omitting the second one drops the whole
# recovery leg silently: the units come back as unreported on the next coverage run.
cd "$REPO" && python3 scripts/merge_ref_shards.py --staging "$STG" \
    --shard-dir ref_shards --shard-dir ref_shards_recovery

step "3. merge_deepsweep_shards.py  (purges __VALIDITY__ -- must precede the harvester)"
python3 scripts/merge_deepsweep_shards.py --staging "$STG"

step "4. harvest_sentinel_findings.py  (LAST -- writes the sentinels)"
python3 scripts/harvest_sentinel_findings.py --staging "$STG"

step "5. build_ref_workbook.py"
mkdir -p "$(dirname "$XLSX")"
python3 scripts/build_ref_workbook.py --staging "$STG" --output "$XLSX"

step "6. recalc.py  (validates the built workbook)"
python3 scripts/recalc.py "$XLSX"

step "7. sweep gates A-K"
python3 scripts/sweep_gates.py --staging "$STG"

printf '\n\033[1mworkbook:\033[0m %s\n' "$REPO/$XLSX"
