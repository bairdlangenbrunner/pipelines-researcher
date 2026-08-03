# Iraq gas route creation — 2026-07-31

Staged-only §8 route-creation pass for every Iraq gas row whose fresh
`GGIT_gas_snapshot_20260731.csv` value was exactly `RouteAccuracy = no route`.
Nothing in this directory has been applied to the routes repository or live sheet.

## Scope and result

- 34 ProjectIDs / 34 sheet rows in `worklist.json`.
- 15 `ROUTE_CANDIDATE` records and committed candidate GeoJSON files:
  - 6 GulfPub sidecar/vector routes, proposed `RouteAccuracy = high`.
  - 9 sourced endpoint great-circle routes, proposed
    `RouteAccuracy = very low (straight line/schematic)`.
- 19 `ROUTE_PARTIAL` records: sourced corridor and any defensible endpoint retained,
  but no geometry because an endpoint, identity, or extent remains unresolved.
- Review workbook:
  `batches/iraq-gas/deliverables/pipelines_batch_20260731_1525_ET_iraq-gas_route-creation.xlsx`.

## Important adjudications

- P7460 / P7466 / P7467 are the three successive Akkas/Okaz–Anbar sections:
  Akkas field–T1 / T1–K3 / K3–Anbar power plant. GulfPub sections 1/2/3 were
  assigned one-to-one from the sheet `SegmentName` values.
- P7436 (83 km, 20 inch) is treated as West Qurna 2–Artawi; P7437 (114 km,
  26 inch) as Majnoon–Artawi. The assignment follows project reporting plus the
  official-field-centroid separations to Artawi.
- The GulfPub Kirkuk–Baiji trace was manually reassigned to P2231 North Gas–Baiji.
  It was rejected for P2232 North Gas–K1.
- Known false GulfPub/OSM matches are recorded in the affected partial notes and
  were not converted to geometry.

## QC

- `validate_route_candidate.py`: 14 PASS, 1 FAIL. P2231 is the sole FAIL because
  the 102 km named trace is only 70.3% of the sheet's 145 km length; the candidate
  is retained for explicit length review.
- Routes-repo `scripts/qc_routes.py` report: 13 PASS, 2 WARN, 0 FAIL. WARNs are
  P2233 (218 km route vs 438 km sheet) and P4068 (42 km vs 61 km).
  The report is saved as `routes_repo_qc.json`.
- Workbook recalculation/open check: 3 sheets, no spreadsheet error cells.

## Reproduction

`assemble_endpoint_candidates.py` rebuilds the four audited legacy endpoint
candidates. Other source-specific candidates use the commands captured in the
repository history/agent run. `stage_partials.py` deterministically restores the
all-PID partial accounting after candidate assembly.

Before any authorized apply, review the 15 GeoJSONs visually, resolve/exclude the
three length-warning PIDs above, and re-run both validation gates. Routes-repo and
sheet-side application remain one synchronized operation under the §8 cardinal rule.
