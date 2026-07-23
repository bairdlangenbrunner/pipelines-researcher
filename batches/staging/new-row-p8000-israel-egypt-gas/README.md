# new-row-p8000-israel-egypt-gas

One-off new-row addition (not a country sweep): **P8000 — Leviathan–Egypt Offshore
Gas Pipeline** (cancelled proposal, Israel → Egypt), identified 2026-07-22 from a
Delek investor-presentation map while cleaning contaminated geometry off P3657 in
the routes repo.

## Deliverables (batches/ top level)
- `pipelines_batch_20260722_1301_ET_israel-egypt-gas_p8000-new-row.xlsx` — gas-tab
  backend mirror (full 131-col header + one prefilled row); ref cells tier-colored
  (green ≥2 independent verified sources, yellow single source). Paste-ready; skip
  computed/formula columns.
- `pipelines_batch_20260722_1301_ET_israel-egypt-gas_p8000-wiki.txt` — full wikitext
  for a new gem.wiki page "Leviathan–Egypt Offshore Gas Pipeline" per the GEM
  pipeline-page template doc.

## Key decisions
- Status **cancelled** via the 4+-year dormancy rule (last development: Feb 2021
  Steinitz/El-Molla ministerial agreement); `ShelvedCancelledType=inferred`,
  cancelled year 2025. Superseded by Ashdod–El Arish third line (P3620/P3657) and
  Nitzana (P7864).
- Capacity/length/diameter/cost left blank — never published for the subsea option;
  the US$200m / 3–5 bcm/y Oct-2021 figures belong to the onshore Sinai link.
- All refs passed `scripts/url_verifier.py` 2026-07-22. arabnews.com 403s to bots →
  Wayback snapshot cited; mees.com live but paywalled (secondary ref only).
- Route: `P8000.geojson` committed in the routes repo (commit 782380e8), digitized
  from the Delek map (main line ~485 km + ~107 km Aphrodite spur, cf. P0473);
  RouteAccuracy low. `Route [ref]` left blank per sweep SOP (geometry out of scope).
- P8000 also exists as a blank pre-allocated placeholder row on the OIL tab —
  remove/renumber that when adding this row to the GAS tab.

`build_p8000.py` (this dir) rebuilds both deliverables from the routes-repo geojson
and the gas-tab snapshot CSV.
