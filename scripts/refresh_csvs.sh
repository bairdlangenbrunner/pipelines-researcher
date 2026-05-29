#!/usr/bin/env bash
# refresh_csvs.sh — pull the live GOIT oil/NGL and GGIT gas tabs as dated CSV snapshots.
#
# Usage:
#   ./scripts/refresh_csvs.sh            # writes data/{tracker}_snapshot_YYYYMMDD.csv
#   ./scripts/refresh_csvs.sh --working  # writes data/{tracker}_working.csv (gitignored)
#
# Header is at CSV row index 2 for both tabs. Load with:
#   pd.read_csv(path, header=2, low_memory=False)

set -euo pipefail

SHEET_ID="1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"
OIL_GID="456134080"
GAS_GID="1020144097"

# Resolve repo root no matter where the script is invoked from
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
REPO_ROOT="$( cd -- "${SCRIPT_DIR}/.." &> /dev/null && pwd )"
DATA_DIR="${REPO_ROOT}/data"
mkdir -p "${DATA_DIR}"

if [[ "${1:-}" == "--working" ]]; then
  OIL_OUT="${DATA_DIR}/GOIT_oil_ngl_working.csv"
  GAS_OUT="${DATA_DIR}/GGIT_gas_working.csv"
else
  STAMP="$(date +%Y%m%d)"
  OIL_OUT="${DATA_DIR}/GOIT_oil_ngl_snapshot_${STAMP}.csv"
  GAS_OUT="${DATA_DIR}/GGIT_gas_snapshot_${STAMP}.csv"
fi

base_url="https://docs.google.com/spreadsheets/d/${SHEET_ID}/export?format=csv&gid"

echo "→ Oil/NGL → ${OIL_OUT}"
curl -fsSL "${base_url}=${OIL_GID}" -o "${OIL_OUT}"

echo "→ Gas     → ${GAS_OUT}"
curl -fsSL "${base_url}=${GAS_GID}" -o "${GAS_OUT}"

# Sanity check the pulled files aren't HTML error pages
for f in "${OIL_OUT}" "${GAS_OUT}"; do
  if head -c 32 "$f" | grep -qi "<html\|<!DOCTYPE"; then
    echo "ERROR: ${f} looks like HTML, not CSV. Sheet permissions may have changed." >&2
    exit 1
  fi
done

echo "Done."
ls -lh "${OIL_OUT}" "${GAS_OUT}"
