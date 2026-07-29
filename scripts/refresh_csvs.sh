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
# TWO PATHS, in order. The anonymous `export?format=csv&gid=` URL is tried first because
# it needs no auth — but it began returning 401 on every tab on 2026-07-29 (the sheet is
# in a shared drive and its link-sharing was tightened). When it fails we fall back to an
# AUTHENTICATED per-tab read via gws (~/.config/gws-gem, read-only work profile) in
# scripts/_sheets_pull.py, which reproduces the export byte-shape (verified against the
# 07-28 snapshots: identical headers, identical row counts). If the fallback also fails
# with an auth error, ask Baird to run `gws-gem auth login` — it needs a browser.

set -euo pipefail

SHEET_ID="1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"
OIL_GID="456134080"
GAS_GID="1020144097"
OWNERS_GID="1489950650"
# Tab titles for the authenticated fallback (values.get takes a title, not a gid)
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

base_url="https://docs.google.com/spreadsheets/d/${SHEET_ID}/export?format=csv&gid"

# pull <label> <gid> <tab title> <out path>
pull() {
  local label="$1" gid="$2" tab="$3" out="$4"
  echo "→ ${label} → ${out}"
  if curl -fsSL "${base_url}=${gid}" -o "${out}" 2>/dev/null \
     && ! head -c 32 "${out}" | grep -qi "<html\|<!DOCTYPE"; then
    echo "   (anonymous export)"
    return 0
  fi
  echo "   anonymous export failed — falling back to authenticated read"
  rm -f "${out}"
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
