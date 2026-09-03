#!/usr/bin/env bash
# Jiangxi gas v2 -- merge chain, in the ONE order that does not lose data.
#
# The order is not stylistic. merge_deepsweep_shards' is_old_deepsweep() drops any record
# whose ref_col is __VALIDITY__ -- which is exactly what harvest_sentinel_findings WRITES.
# So the harvester must run LAST; harvesting earlier zeroes the sentinels out silently
# (verified empirically on the v1 batch: 2 -> 0, no warning).
#
# recalc.py validates a BUILT workbook (positional xlsx), so it runs after the build,
# not before it.
#
#   ./run_merge_chain.sh
set -euo pipefail
cd "$(dirname "$0")"
REPO=$(cd ../../../.. && pwd)
STG=batches/china-jiangxi-gas/staging/deepsweep-20260902
STAMP=$(TZ=America/New_York date "+%Y%m%d_%H%M_ET")
XLSX="batches/china-jiangxi-gas/deliverables/pipelines_batch_${STAMP}_china-jiangxi-gas_deepsweep.xlsx"

step() { printf '\n\033[1m=== %s\033[0m\n' "$*"; }

step "0. validate shards (structural contract)"
python3 validate_shards.py

step "1. split_shards.py  -> ref_shards/ + rows/"
python3 split_shards.py

step "2. merge_ref_shards.py"
cd "$REPO" && python3 scripts/merge_ref_shards.py --staging "$STG"

step "3. merge_deepsweep_shards.py  (purges __VALIDITY__ -- must precede the harvester)"
python3 scripts/merge_deepsweep_shards.py --staging "$STG"

step "4. harvest_sentinel_findings.py  (LAST -- writes the sentinels)"
python3 scripts/harvest_sentinel_findings.py --staging "$STG"

step "5. build_ref_workbook.py"
mkdir -p "$(dirname "$XLSX")"
python3 scripts/build_ref_workbook.py --staging "$STG" --output "$XLSX"

step "6. recalc.py  (validates the built workbook)"
python3 scripts/recalc.py "$XLSX"

step "7. pre-delivery gates A-H"
cd "$STG" && python3 predelivery_checks.py

printf '\n\033[1mworkbook:\033[0m %s\n' "$REPO/$XLSX"
