#!/usr/bin/env bash
# refresh_csvs.sh — pull the live GOIT oil/NGL, GGIT gas, and Pipeline operators/owners
# tabs as dated CSV snapshots.
#
# Usage:
#   ./scripts/refresh_csvs.sh            # writes data/{tracker}_snapshot_YYYYMMDD.csv
#   ./scripts/refresh_csvs.sh --working  # writes data/{tracker}_working.csv (gitignored)
#
# Header is at CSV row index 2 for the two tracker tabs (load with header=2). The
# operators/owners tab has its header at row index 1 (load with header=1); it is
# ProjectID-keyed and holds the Operator [ref] / Owner [ref] source columns.
#
# THE PULL ENGINE LIVES IN ../gem-db-ops — this script is a thin wrapper.
# As of 2026-08-11 the authenticated tab->CSV reader that used to live here
# (scripts/_sheets_pull.py, now deleted) is `gem-db-ops/gem_sheets.py`, and the
# per-tracker entry points are `gem-db-ops/{goit,ggit}/pull.py`. Same gws profile
# (~/.config/gws-gem, read-only), same FORMATTED_VALUE reads, same right-padding,
# so the row offsets this repo depends on are unchanged — verified byte-identical
# on the Oil/NGL tab against the 2026-08-11 10:19 snapshot. Do not re-add a local
# copy of the reader; fix gem-db-ops instead and every consumer gets the fix.
#
# Each pull also writes a sibling `<snapshot>.colmap.json` (header -> 0-indexed
# column, plus canonical short names and drift warnings). It's derivable, so it's
# gitignored; scripts that want it can re-derive with
# `python3 ../gem-db-ops/gem_colmap.py <csv> --tracker goit`.
#
# Anonymous access is gone for good: the old `export?format=csv&gid=` URL began
# returning 401 on every tab on 2026-07-29 (the sheet lives in a shared drive,
# driveId 0AFOra93TfZAeUk9PVA). Don't re-add it. The GIDs below are kept only
# because docs elsewhere in the repo identify the tabs by gid.
# If the read fails with an auth error, ask Baird to run `gws-gem auth login` (needs a browser).

set -euo pipefail

# Tab titles/GIDs now live in gem-db-ops/gem_sheets.py's TABS registry; these are
# retained as documentation of which tabs this script covers.
#   Oil/NGL pipelines          gid 456134080   -> gem-db-ops/goit/pull.py
#   Gas pipelines              gid 1020144097  -> gem-db-ops/ggit/pull.py
#   Pipeline operators/owners  gid 1489950650  -> --with-owners

# Resolve repo root no matter where the script is invoked from
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$( cd -- "${SCRIPT_DIR}/.." &> /dev/null && pwd )"
DATA_DIR="${REPO_ROOT}/data"
mkdir -p "${DATA_DIR}"

# Sibling checkout of the pull engine; override with GEM_DB_OPS_REPO.
DB_OPS="${GEM_DB_OPS_REPO:-${REPO_ROOT}/../gem-db-ops}"
if [[ ! -f "${DB_OPS}/gem_sheets.py" ]]; then
  echo "ERROR: gem-db-ops not found at ${DB_OPS}" >&2
  echo "       Clone it beside this repo, or set GEM_DB_OPS_REPO=/path/to/gem-db-ops" >&2
  exit 1
fi

if [[ "${1:-}" == "--working" ]]; then
  OIL_OUT="${DATA_DIR}/GOIT_oil_ngl_working.csv"
  GAS_OUT="${DATA_DIR}/GGIT_gas_working.csv"
  OWNERS_OUT="${DATA_DIR}/GEM_operators_owners_working.csv"
else
  STAMP="$(date +%Y%m%d)"
  OIL_OUT="${DATA_DIR}/GOIT_oil_ngl_snapshot_${STAMP}.csv"
  GAS_OUT="${DATA_DIR}/GGIT_gas_snapshot_${STAMP}.csv"
  OWNERS_OUT="${DATA_DIR}/GEM_operators_owners_snapshot_${STAMP}.csv"
fi

echo "→ Oil/NGL + operators/owners → ${OIL_OUT}, ${OWNERS_OUT}"
python3 "${DB_OPS}/goit/pull.py" --output "${OIL_OUT}" \
        --with-owners --owners-output "${OWNERS_OUT}"

echo "→ Gas → ${GAS_OUT}"
python3 "${DB_OPS}/ggit/pull.py" --output "${GAS_OUT}"

# Sanity check the pulled files aren't HTML error pages
for f in "${OIL_OUT}" "${GAS_OUT}" "${OWNERS_OUT}"; do
  if head -c 32 "$f" | grep -qi "<html\|<!DOCTYPE"; then
    echo "ERROR: ${f} looks like HTML, not CSV. Sheet permissions may have changed." >&2
    exit 1
  fi
done

echo "Done."
ls -lh "${OIL_OUT}" "${GAS_OUT}" "${OWNERS_OUT}"
