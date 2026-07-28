# Superseded

Gas-only GulfPub ingest for Libya (40 reference records). Superseded on
2026-07-28 by `staging/recon-gulfpub-20260728/`, which was run with
`--commodity both` (129 records, oil+gas) so that cross-tracker duplicates are
visible — that is what surfaced GulfPub's own "Wafa - Mellitah Oil &
Condensate" record matching GOIT P0606, corroborating the P6705 redundancy
verdict. The 20260728 run also postdates three engine fixes (name-token
inflation, absent-geometry-scored-as-pass, IoU collapse on partial references),
so this run's composites are not comparable to it.

Kept for provenance only. Do not read its `match_diff.json` as current.
