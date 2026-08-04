# Egypt gas §8 route creation — 2026-08-04 pass (ENTSOG SYSCAP)

Scope (per Baird 2026-08-04): re-run route creation for Egypt gas — (a) the rows
still at `no route` (15 old partials + the 15 new P8026–P8045-range rows), and
(b) **replacement suggestions from the ENTSOG/GIE System Capacity Map 2026** for
the 35 `very low (straight line/schematic)` + 3 `low` rows. Interpretation
flagged to Baird: ENTSOG is the *enabling new source*, not an exclusivity
constraint — the best source-ladder rung wins per row (GulfPub sidecar > ENTSOG
traced), with ENTSOG corroboration recorded where it applies.

**Apply state:** the **10 replacement candidates were APPLIED 2026-08-04**
(Baird-authorized §8 step 6): routes-repo merge `752ab5d3` (QC 6 pass / 4 WARN
included — P0462 Gaza-waters vertices, P3936 +34% & P6034 +48% = the staged
gate FAILs, P3935 geocoder false-match on the wrong southern "Salam"), then
sheet columns via the new `apply_route_candidates.py --replace` mode (50 cells
written + verified; RouteCreator SET to `CB`; backup
`notes/sheet-write-2026-08-04-egypt-gas-route-replacements.csv`;
`audit_route_sync.py` Egypt gas clean). The **13 no-route candidates + 4
partials remain staged, NOT applied** — that half still needs its own
per-batch authorization.

Deliverable: `batches/egypt-gas/deliverables/pipelines_batch_20260804_1656_ET_egypt-gas_route-creation.xlsx`
(23 ROUTE_CANDIDATE + 4 ROUTE_PARTIAL; supersedes the `_1431_ET` build, archived).

**2026-08-04 trim (Baird):** rows he re-graded from low → `medium` on the sheet
drop out of replacement scope — that removed **P0436** (AGP Arish–Taba, was the
ENTSOG-traced medium replacement; a medium ENTSOG trace can't improve a row
already at medium). The other 10 replacement targets re-checked against the
fresh snapshot and still very low/low, so they stand.

## Source layer

`sources/entsog/ENTSOG_GIE_SYSCAP_2026_pipelines_{operational,project}_wgs84.geojson`
(vector extraction from the official ENTSOG PDF; see `sources/entsog/README.md`).
Measured accuracy over 24 high/medium Egypt GEM routes (`entsog_accuracy_check.py`):
median lateral offset **4.2 km**, p90 **13 km** → traced candidates capped at
`medium`, and ENTSOG never overrules a `high` route.

## Method

`entsog_match.py` builds a routable graph from the ENTSOG strokes over the
Egypt/Sinai/AGP window (snap-bridge stroke ends ≤4 km onto other strokes →
`unary_union` noding → MultiGraph; query endpoints inserted mid-edge, snap cap
20 km), then shortest-paths each PID's endpoints (existing-route termini for
replacement rows; researched endpoints — `noroute_match.py` +
`research_results_{sinai,suez,delta,west}.json` — for no-route rows). Every
PATH was human-adjudicated off `overlays/<PID>.png` / `nr_<PID>.png` by ratio
vs sheet length, snap distances, and corridor shape; accepted paths were
assembled per-PID with `build_route_candidate.py` (`assemble_replacements.py`,
`assemble_noroute.py`, `assemble_west.py`).

## Results — 23 candidates

**Replacements for very-low/low rows (10, all `--replace`):**
- ENTSOG traced, `medium` (7): P7567, P8019, P8024, P8010, P0462
  (EMG), P3928, P3936* — P0436 (AGP) withdrawn 2026-08-04, row now `medium`
- GulfPub sidecar, `high` (3): P3935 (fixes a south endpoint ~400 km off),
  P6034*, P6037 (GulfPub 58.9 km beat ENTSOG's 62 km path)

**No-route rows (13):**
- GulfPub sidecar, `high` (1): P8034 (ENTSOG corroborates: path 124.7 km, 0.982)
- ENTSOG traced, `medium` (10): P8041*, P8044, P8045 (Taba–Sharm, 199.8 vs
  206 km), P8033, P8036, P8038, P8042*, P8027, P8040, P8032
- Endpoints great-circle, `very low` (2): P8031, P8039 (network path rejected
  as off-corridor; straight line 77.5 vs sheet 74)

**\* 4 documented gate FAILs, staged deliberately (precedent P2231):**
- P3936 ratio 1.343 (barely over) — REVIEW: corridor may include WDGP trunk alignment.
- P6034 ratio 1.483 — sheet 38.5 km conflicts with the 57 km coastal geometry
  (Hurghada–Safaga road ≈ 55–60 km); length cell suspect.
- P8041 ratio 0.631 — sheet 55 km suspect; EIA chainage 33 km corroborates the
  34.7 km geometry.
- P8042 ratio 0.73 — sheet 215 km suspect (Port Said–Suez canal corridor ≈ 162 km).

**Replacement rejects (existing geometry stays):** P3929, P3939, P8014, P8004,
P8025, P6685, P6686, P7580, P8021, P8011, P8012, P7572, P6035, P7577, P6036,
P5132, P6032, P6703, P7589, P0473, P3930, P7574, P8002, P7597, P8013; P6033
HOLD (start identity unresolved); P7482 skipped (18 km Taba–Aqaba subsea hop —
an ENTSOG schematic marine stroke adds nothing over the existing `low` route).
GulfPub sidecar rejects: P8015 (stub + mislocated line), P5132/P6036 (Zohr II
trace stops ~70 km short of landfall — fragment corroboration only), P7572,
P6686, P8012, P7577/P7578, P7589, P7597.

## Still partial — 4 ROUTE_PARTIAL records this pass

- **P8026** — end (Ayoun Moussa PS) solid; no defensible start; possible
  "North Sinai" governorate mismatch.
- **P8022/P8023** — Abu Madi start ungeocodable; active source conflict on its
  governorate (Kafr El Sheikh coastal vs Dakahlia interior, ~80+ km apart).
- **P8035** — **duplicate of P8013** (same corridor, "Trans Gulf" marketing
  name); recommend merge/retirement, not a second route.

The 11 other old partials from the July pass (P6704, P6033, P7588, P7589,
P7605, P8001, P8003, P8005–P8009, P8020) were not re-researched here beyond
what ENTSOG could resolve; they remain in
`batches/egypt-gas/staging/route-creation/` (still-pending July staging).

## Files

- `candidates.json` + `candidate_routes/<PID>.geojson` — the staged output.
- `staged_resolutions.json` — 24 ROUTE_CANDIDATE + 4 ROUTE_PARTIAL records.
- `entsog_match.py`, `noroute_match.py`, `entsog_accuracy_check.py`,
  `gulfpub_adjudicate.py`, `assemble_*.py` — this pass's tooling.
- `entsog_match_report.json`, `overlays/` — adjudication evidence (PNG + raw
  path geojson per PID).
- `research_brief.md`, `research_results_*.json` — endpoint research fan-out.
