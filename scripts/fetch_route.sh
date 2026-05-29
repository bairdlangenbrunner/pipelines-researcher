#!/usr/bin/env bash
# fetch_route.sh — fetch a pipeline route GeoJSON from the public GEM routes repo.
#
# Usage:
#   ./scripts/fetch_route.sh P5367
#   ./scripts/fetch_route.sh P5367 routes/  # write to a specific directory
#
# Uses the GitHub Contents API to search for the ProjectID across the repo,
# then downloads the first matching .geojson via the raw URL.

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <ProjectID> [output_dir]" >&2
  echo "Example: $0 P5367" >&2
  exit 1
fi

PROJECT_ID="$1"
OUT_DIR="${2:-.}"
REPO="GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes"

mkdir -p "${OUT_DIR}"

# Use GitHub code search to find files containing the ProjectID in their name
echo "Searching ${REPO} for ${PROJECT_ID}..."
# GitHub Search API: filename search restricted to the repo
SEARCH_URL="https://api.github.com/search/code?q=${PROJECT_ID}+in:path+repo:${REPO}"

# If GITHUB_TOKEN is set, use it (raises rate limit from 10/min to 30/min for search)
AUTH_HEADER=()
if [[ -n "${GITHUB_TOKEN:-}" ]]; then
  AUTH_HEADER=(-H "Authorization: Bearer ${GITHUB_TOKEN}")
fi

RESPONSE="$(curl -fsSL "${AUTH_HEADER[@]}" -H "Accept: application/vnd.github+json" "${SEARCH_URL}")"

# Pick the first .geojson hit
PATH_IN_REPO="$(echo "${RESPONSE}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
items = data.get('items', [])
for it in items:
    if it['path'].endswith('.geojson'):
        print(it['path']); break
")"

if [[ -z "${PATH_IN_REPO}" ]]; then
  echo "No .geojson found for ${PROJECT_ID} in ${REPO}." >&2
  echo "Tip: try browsing https://github.com/${REPO} directly, or check the ProjectID." >&2
  exit 2
fi

OUT_FILE="${OUT_DIR}/$(basename "${PATH_IN_REPO}")"
RAW_URL="https://raw.githubusercontent.com/${REPO}/main/${PATH_IN_REPO}"

echo "Found: ${PATH_IN_REPO}"
echo "→ ${OUT_FILE}"
curl -fsSL "${RAW_URL}" -o "${OUT_FILE}"
echo "Done. $(wc -c < "${OUT_FILE}") bytes."
