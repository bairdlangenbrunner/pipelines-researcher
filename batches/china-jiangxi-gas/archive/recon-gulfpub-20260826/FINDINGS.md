# GulfPub recon — China gas, Jiangxi provincial grid (2026-08-26)

Run as a **cheap recorded negative**, exactly as the batch plan predicted: GulfPub carries
Chinese national trunks, so ~0 overlaps against provincial-grid rows was the expected outcome.
It is now measured rather than assumed.

Input: `canonical_records.json` + `geometry_sidecar.json` reused from
`batches/china-trunks-gas/staging/recon-gulfpub-20260812/` — a **post-multicountry-fix** ingest,
so the transit-trunk filter defect is not in play here.

## Result: GulfPub coverage of the Jiangxi grid is ZERO

- GulfPub's China gas extract holds **120 records**, and **not one mentions Jiangxi / 江西**.
- China-wide the run produced 118 overlaps, 2 additions, 2 near-misses, 503 `gem_only`,
  20 status conflicts.
- **17 of our 18 in-scope rows land in `gem_only`** — "no reference counterpart exists", the
  correct bucket. 0 near-misses, 0 status conflicts, 0 additions touching this scope.
- The 2 additions and 20 status conflicts are all on out-of-scope national trunks (MZ's lane).

So there is **no GulfPub corroboration available for this batch**, and that is a fact about
GulfPub's coverage, not a matcher failure. The health line is clean; do **not** add a
`geoarea_weight` override to chase it.

## The one apparent overlap (P4782) is a FALSE POSITIVE — hand-dispositioned

`gulfpub:gas:6163` **Cang-Zi Line** matched **P4782** (Phase I, Nanchang-Fengcheng) at
composite **0.4748**, confidence **yellow**:

    name 0.571 · endpoints 0.545 · length 0.80 · route IoU 0.0

It is geographically impossible:

| | GulfPub Cang-Zi Line | GEM P4782 |
|---|---|---|
| endpoints | Ji-Ning Branch → **Beijing** | Nanchang → Fengcheng, **Jiangxi** |
| geometry bbox | lon 116.21–116.56, lat **39.22–39.89** | Nanchang ≈ lon 115.9, lat **28.7** |
| separation | — | **~1,240 km** |
| route IoU | **0.0** | |

The match is carried entirely by `length 0.80` (ref 80.47 km against P4782's route-derived
100.87 km) plus a spurious name score — "Cang-Zi" against "Nanchang-Fengcheng" on shared
substrings. **Dispositioned by hand as a non-match. No finding flows from it.**

## Engine observation — recorded, deliberately NOT acted on

A **`route IoU` of exactly 0.0 where BOTH sides carry geometry is dispositive of a non-match**,
yet here it only diluted the composite to 0.4748, which still cleared into `overlaps` at yellow.
A veto rule ("both sides routed and IoU 0 ⇒ never an overlap") would have killed this without
any threshold change.

Not implemented, on purpose: the matcher is shared, so a veto rule **moves committed runs in
other countries**, which CLAUDE.md explicitly warns against. Flagging it for a decision with a
cross-country A/B rather than changing it inside a country batch. Note this is *not* the
`MATCH_QUALITY` case — that covers a dead matcher; this is a live matcher scoring one bad match.

## Wiring into the deliverable (2026-08-26)

`build_recon_crosswalk.py --sweep-dir deepsweep/` produced the tab input, then
`deepsweep/scope_recon_crosswalk.py` scoped it. That second step is not optional:
`reconcile.py` runs per COUNTRY, so the raw crosswalk carried **118 overlaps / 2 additions /
4 ambiguous** across all 1,041 China gas rows, and `build_ref_workbook._recon_view` does
**no ProjectID filtering** — it writes every crosswalk row it is handed. Unscoped, a Jiangxi
reviewer would have been given 117 out-of-scope China decisions, with the one row that
matters buried inside them.

Scoped: **1 overlap, 0 additions, 0 ambiguous**. The single overlap is P4782, re-labelled
`FALSE_POSITIVE` with the geographic adjudication written into its `Action` cell so the
non-match travels with the row instead of living only in this file. Neither country-wide
addition is anywhere near Jiangxi (Altai Pipeline; a Shenzhen LNG link), and all four
ambiguous records are Central Asia–China / Qinhuangdao–Beijing trunks.

The recorded negative is preserved in `diagnostics.recorded_negative` rather than left to
an empty tab, and it says why the absence is trustworthy: the matcher is healthy here
(100% of reference records named *and* routed, 97.4% of the GEM pool routed, country-wide
overlap rate 98.3%), so **no `MATCH_QUALITY` warning fired and none is owed**. The gap is
GulfPub's coverage of inland provincial grids, not a matcher defect — so this is *not* a
case for a `geoarea_weight` override.
