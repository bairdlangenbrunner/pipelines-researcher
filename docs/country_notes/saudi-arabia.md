# Saudi Arabia

Crude, NGL, and gas. Deep-dive country and the home of the GulfPub reconciliation
proof-of-concept (`working_files/GOIT_SaudiArabia_Gulfpub_Comparison.xlsx`, the
golden reference the engine generalizes).

## Regulators / official data
- Saudi Aramco corporate + AramcoLife — project status, capacities, the Master Gas
  System (MGS) program.
- Saudipedia — Saudi infrastructure encyclopedia entries.

## Key operators / owners
- **Saudi Aramco** — operator/owner of essentially the entire network (`Saudi
  Aramco [100.%]` is the common Owner string). BAPCO (Bahrain) co-owns the AB-4
  cross-border line (P0637).

## Preferred sources (beyond the global roster)
- KS Al-Hajri, Samsung E&A — EPC contractors on MGS packages (good for diameters,
  scope, schedule).
- MEED — Gulf project tracking and tenders.

## Reconciliation notes
- GulfPub covers Saudi crude well; gas coverage thinner (GulfPub historically
  tracks mostly crude). Known matched anchors for validation: P0637 (AB-4), P1972
  (Abqaiq Plants–Qatif Junction), P3966 (East–West Gas), P6734 (MGS III / MGS-3).
- **Route-replacement candidates:** several matched lines have `low`/`medium` GEM
  `RouteAccuracy` while GulfPub carries a route (e.g. P3966 East–West, GEM
  `medium`) — prime targets for the geometry pass + human review.
- Diameters are frequently multi-valued (`56,10,16`, `40/42/48`) — set-membership
  matching, not equality.

## Gotchas
- Status_Conflicts seen in the POC: P2702 (Al Khafji Joint Operations Offshore) GEM
  `cancelled` vs GulfPub Operating; P0545 (IPSA) GEM `mothballed` vs GulfPub
  Operating — verify true current status, don't auto-flip.

## Open items
- Finish the GulfPub route-consistency pass for low/medium-accuracy matches; stage
  route-replacement candidates for review before any GeoJSON swap.
