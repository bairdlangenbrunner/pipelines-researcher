#!/usr/bin/env bash
# refresh_csvs.sh — pull the live GOIT oil/NGL, GGIT gas, and Pipeline operators/owners
# tabs as dated CSV snapshots.
#
# Usage:
#   ./scripts/refresh_csvs.sh            # writes data/{tracker}_snapshot_YYYYMMDD.csv
#   ./scripts/refresh_csvs.sh --working  # writes data/{tracker}_working.csv (gitignored)
#
# Header is at CSV row index 2 for the two tracker tabs (load with header=2). The
# operators/owners tab (GID 1489950650) has its header at row index 1 (load with header=1);
# it is ProjectID-keyed and holds the Operator [ref] / Owner [ref] source columns.
#
# ONE PATH: an AUTHENTICATED per-tab read via gws (~/.config/gws-gem, the read-only work
# profile) in scripts/_sheets_pull.py. Baird is deliberately removing anonymous access to
# these documents, so the authenticated CLI/MCP path is the standing method for every
# shared-drive and Google Docs/Sheets operation — not a fallback.
#
# The old anonymous `export?format=csv&gid=` URL began returning 401 on every tab on
# 2026-07-29 and is gone for good; don't re-add it. The GIDs below are kept only because
# they identify the tabs in docs and CSV-export URLs elsewhere in the repo.
# If the read fails with an auth error, ask Baird to run `gws-gem auth login` (needs a browser).

set -euo pipefail

SHEET_ID="1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"
OIL_GID="456134080"
GAS_GID="1020144097"
OWNERS_GID="1489950650"
# Tab titles drive the pull — Sheets values.get takes a title, not a gid
OIL_TAB="Oil/NGL pipelines"
GAS_TAB="Gas pipelines"
OWNERS_TAB="Pipeline operators/owners"

# Resolve repo root no matter where the script is invoked from
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$( cd -- "${SCRIPT_DIR}/.." &> /dev/null && pwd )"
DATA_DIR="${REPO_ROOT}/data"
mkdir -p "${DATA_DIR}"

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

# pull <label> <gid> <tab title> <out path>
pull() {
  local label="$1" gid="$2" tab="$3" out="$4"
  echo "→ ${label} (gid ${gid}) → ${out}"
  python3 "${SCRIPT_DIR}/_sheets_pull.py" "${tab}" "${out}"
}

pull "Oil/NGL"          "${OIL_GID}"    "${OIL_TAB}"    "${OIL_OUT}"
pull "Gas"              "${GAS_GID}"    "${GAS_TAB}"    "${GAS_OUT}"
pull "Operators/owners" "${OWNERS_GID}" "${OWNERS_TAB}" "${OWNERS_OUT}"

# Sanity check the pulled files aren't HTML error pages
for f in "${OIL_OUT}" "${GAS_OUT}" "${OWNERS_OUT}"; do
  if head -c 32 "$f" | grep -qi "<html\|<!DOCTYPE"; then
    echo "ERROR: ${f} looks like HTML, not CSV. Sheet permissions may have changed." >&2
    exit 1
  fi
done

echo "Done."
ls -lh "${OIL_OUT}" "${GAS_OUT}" "${OWNERS_OUT}"
