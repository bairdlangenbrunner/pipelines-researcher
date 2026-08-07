# Libya

38 gas rows (GGIT) and 57 oil rows (GOIT). Gas was swept deeply in July 2026 —
ref sweep, cancelled-status review, redundancy pass, and two reconciliations
(GulfPub, OSM). **Oil has not been swept**, and several findings below point
straight at it. Libya's distinguishing problem is not thin sourcing; it is
**structural**: aggregate rows sitting alongside their own member segments, and
condensate/oil lines filed in the gas tracker.

## Regulators / official data
- **National Oil Corporation (NOC)** — noc.ly — the owner of record on essentially
  every Libyan row. Site is intermittently down; Wayback usually has it.
- **OPEC Annual Statistical Bulletin, Table 4.10** (gas pipelines) / **Table 4.9**
  (oil) — the single most productive source for Libyan pipeline specs, and the
  origin of most of GEM's existing Libya citations. **The live opec.org PDF links
  are dead** (they redirect to the homepage); the tables are recoverable from
  Wayback snapshots of the ASB PDF via `pdftotext`. A recovered Wayback ASB URL
  that actually names the pipeline is a valid ref; the bare dead opec.org link on
  the row is not.
  - **Read its column header before using a number — and then check whether the
    header is telling the truth.** Both of Table 4.10's numeric columns have burned
    GEM's Libya rows, in opposite directions:
    - The **capacity** column is headed **"(1,000 scm/yr)"** and the ingest dropped
      that multiplier — 4 rows read as zero-capacity.
    - The **length** column is headed **"(miles)"** but the **Libya block is
      actually in kilometres** (Qatar's, Iraq's and Saudi's are genuinely miles).
      The ingest converted anyway — 14 rows are 1.609× too long. ASB2013 fixed the
      source; ASB2012 did not.
    Both in the Gotchas section, with a memo each.

## Key operators / owners
NOC is the **owner**; the operator is almost always one of its joint-venture
operating companies. Do not put "National Oil Corporation" in `Operator`.
- **Mellitah Oil & Gas B.V.** (NOC / Eni 50:50) — the whole western complex: Wafa,
  Bahr Essalam, Sabratha/DP3–DP4, Mellitah, and the Greenstream export line.
- **Sirte Oil Company** — the Sirte Basin grid around Brega. Formed **1981** out of
  Esso Standard Libya; lines it operates today were commissioned by predecessors in
  the 1960s–70s, so **1981 is a corporate date, never a commissioning date**.
- **Waha Oil Company** (NOC 59.18% / ConocoPhillips 16.33% / TotalEnergies 16.33% /
  Hess 8.16%) — Waha, Farigh, Defa.
- **Zueitina Oil Company** (NOC 81% / Occidental 14.25% / OMV 4.75%) — Intesar /
  Zueitina.
- Also present: Akakus, Harouge Oil Operations.

**Every Libya gas row has a blank `Operator [ref]` — all 38, including the 11 where
`Operator` is filled.** 27 of 38 have a blank `Operator` as well. Operator work goes
on the separate ProjectID-keyed operators/owners tab (GID 1489950650, `header=1`),
not the tracker tab.

## Preferred sources (beyond the global roster)
- **Libya Herald**, **The Libya Observer**, **Libya Update**, **Al Wasat**
  (alwasat.ly), **Attaqa** (attaqa.net), **Ean Libya** — regional and Arabic-language
  coverage that the English majors miss entirely.
- **Mellitah Oil & Gas** and **Sirte Oil Company** corporate pages — good for
  operator attribution, weak on specs.
- **Offshore Technology / NS Energy** — best coverage of the Western Libya Gas
  Project and Bahr Essalam phases.

## Routing / GIS tips
- 20 of 38 gas rows have drawn geometry. Route integrity flags **12** of them —
  11 `length_ratio` and 1 `null_geometry`. Check which side is wrong before touching
  either, because in Libya **both** failure modes are present and common:
  - On the 14 ASB-derived rows the **length** is wrong (spurious mi→km — see
    Gotchas). Six of the seven such rows with geometry pass the ratio test once the
    length is corrected. Do not "fix" the route on these.
  - Elsewhere the drawn line is a **straight-line schematic** and the length is fine
    (P1858 is a 91 km two-point line against a sourced ~132 km).
- Several Sirte Basin routes are literally two-point lines (P1858 is a 91 km
  straight segment against a sourced 131.96 km). Those are `RouteAccuracy`
  problems, not length problems.
- **The Fanack / PetroGas Libya gas-production map is an infographic, not a map —
  do not try to georeference it** (attempted 2026-08-06, packet
  `batches/libya-gas/staging/route-creation-p1855-p6457/packets/P6457/`). Affine
  RMSE 10.4 km / LOO 16.7 km against a 5 km gate; quadratic overfits (LOO 36 km);
  pairwise scale varies ~2× (0.38–0.73 km/px); the traced Bahr Essalam–Mellitah
  line measures 163 km against the map's own "110km" label; and the Bahr Essalam
  node is drawn NNW of Mellitah when the field is NNE (azimuth 022° real vs −025°
  drawn), landing ~100 km off. Its **attribute** content is good, though: the
  36″ gas + 10″ oil/condensate pairing and ~110 km length corroborate the
  operator's own page (`mellitahog.ly/en/sites/sabratha-platform/`) → high tier.
- **No offshore platform tie-backs are available from vector sources.** OSM has
  Greenstream and the onshore lines but no Mellitah→Sabratha-platform pipe; OSM
  seamarks cover Bouri (DP3/DP4/SPM) only, and NGA Pub. 113 (2019) lists the Bouri
  lights but has no Sabratha entry. So rung 4 (`endpoints`) is blocked for the
  Bahr Essalam corridor for want of a *citable* platform coordinate — GOGET has one
  but it is internal-only and never a `[ref]`.
- **OSM is not usable for Libya gas.** Of 545 Libyan pipeline features in OSM, 270
  are tagged `substance=oil`, 248 are untagged, 21 are water and **6 are gas** —
  four of those six being unnamed 0.0–0.1 km stubs. Absence from OSM here says
  nothing about GEM. Detail: `sources/osm/NOTES.md`. (OSM is ODbL share-alike —
  copying its coordinates into a GEM route is a redistribution decision for Baird,
  never the agent's.)

## Reconciliation notes
- **GulfPub** covers Libya well: 129 records at `--commodity both` (89 oil, 40 gas),
  all with geometry → 104 overlaps, 25 additions, 3 status conflicts. Under the >30
  escalation trigger. Staged: `batches/libya-gas/staging/recon-gulfpub-20260728/`.
  - **Run Libya with `--commodity both`, not gas-only.** That is the only reason the
    Wafa-Mellitah condensate duplicate surfaced — GulfPub's own record is named
    "Wafa - Mellitah Oil & Condensate" and matched GOIT P0606 green.
  - Known name-convention mismatch: GEM uses well designations (`103D-103A`) where
    GulfPub uses field names (`Intisar D - Intisar A`). Same 40in pipe; belongs in
    `OtherEnglishNames`, not a new row.
  - 25 additions are mostly 6–8in field gathering laterals, below GGIT's tracker-wide
    12in 5th-percentile diameter. Held pending a scope ruling; three at 12–16in are
    genuine Discovery candidates.
- **OSM** is registered (`sources/osm/`) but returned a coverage null result for
  Libya — see above. It was still worth running: it exposed three engine defects
  (name-token inflation in `match.py`, absent-geometry-scored-as-a-pass in
  `reconcile.py`, IoU collapse on partial references in `route_compare.py`) that
  were fixed and affect **every** source.

## Gotchas
- **The gas tracker contains condensate lines.** Three of them, each needing a
  *different* disposition — which is why this is a class defect and not three fixes:
  - **P6705** (16in Wafa-Mellitah) → GOIT already has it as **P0606** → **delete**
    from GGIT, do not "move" it. **DONE 2026-08-06** (row deleted from GGIT).
  - **P6713** (10in Bahr Assalam-Mellitah) → GOIT already has **P6457** → **delete**.
    **DONE 2026-08-06** (row deleted from GGIT).
  - **P6709** (4in Bouri-Bahr Assalam) → GOIT has **no** matching row → **move**.
    **Still open** — the row is still in GGIT as of 2026-08-06.
- **`scm/y` / `scm/yr` capacities all compute to zero.** 8 rows tracker-wide (4
  Libya, 4 Algeria) — the ASB "(1,000 scm/yr)" multiplier was dropped at ingest, and
  `scm/yr` is not even a unit the `CapacityBcm/y` conversion recognises. Full
  writeup: `notes/escalation-2026-07-28-scm-capacity-units.md`. **Do not apply a
  blanket ×1000** — it fits Libya's four and does not fit Algeria's.
- **14 Libya lengths are 1.609× too long.** ASB2012 Table 4.10 labels its length
  column "miles", but the Libya block is tabulated in **kilometres**; the ingest
  converted anyway. Every one of the 14 matches `ASB raw × 1.609344` to within 1 km.
  Full list + the Qatar/Greenstream controls:
  `notes/escalation-2026-07-28-asb-libya-length-units.md`. **This inverts the usual
  reading of a `length_ratio` flag in Libya** — on these rows the length is wrong,
  not the route, so don't downgrade `RouteAccuracy` before the lengths are fixed.
  P1872 and P1873 are exactly 2.00× their ASB figure instead, which is a *different*,
  undiagnosed mechanism.
- **P0484 `LengthKnownKm = 5246`** against a 526 km drawn route: a decimal shift live
  in the published tracker.
- **A shared name + an exact shared length is a reason to look, not a verdict.** In
  clusters B and D that signature was a misfiled condensate line; in clusters C, F
  and G it was genuine twinning, and OPEC ASB tabulates each line of the pair
  separately with its own capacity. Three of the seven redundancy clusters were
  opened as duplicates and then **refuted with sources**. The cleanest example:
  P1860 and P1861 both read `LengthKnownKm = 177.00`, which looks exactly like a
  copy-paste — but ASB2012 lists *both* Waha/Nasser and Faregh/Intesar at 110, so
  both converted to the same wrong number. The duplication is in the source.
- **`cancelled` is a claim like any other.** Both Libya cancelled rows failed review:
  P1728's cancellation is contradicted by World Bank (2013) and Libya Herald (2013)
  coverage of active discussions, and P3985's origin article shows the line ~60%
  complete in May 2020. Absence of news is not evidence of cancellation.
- **Entity-linkage error to watch for:** P1728 Mellitah-Gábes lists its owner as
  "Gaz-System [100.%]" — Poland's transmission operator, on a Libya–Tunisia line.
  The real vehicle is the Tunisian-Libyan Gas Transportation Company ("Joint Gas"),
  a NOC/STEG 50:50 JV.
- **"Mellitah" is ambiguous.** It is both the coastal complex and the *company*
  (Mellitah Oil & Gas). P3985's endpoints were manufactured from that confusion —
  the source's "Mellitah" was the operator, and the line is a 4in backup feed
  entirely inside the Abu Attifel field.

## Deliverables — THREE files to work, not one

`batches/libya-gas/deliverables/` (all gitignored — regenerable from staging):

1. `pipelines_batch_20260728_1235_ET_libya-gas_handoff-actions.xlsx` — **the main surface.**
   Work from the ACTIONS file, not the per-leg workbooks: 89 open decisions, 229 paste-ready
   backend cell units, 65 operator/owner units, 1 new row, 97 wiki updates, 51 open flags.
   Both READMEs carry an `ESCALATIONS` row listing the five class-level rulings needed.
   (`…_handoff-evidence.xlsx` is its audit trail, not a work surface.)
2. `pipelines_batch_20260729_0941_ET_libya-gas_reconciliation-gulfpub.xlsx` and
   `…_20260728_1149_ET_libya-gas_reconciliation-osm.xlsx` — **NOT subsumed by the handoff.** The
   packet README's "Prior staged packets" line omits both recon dirs and it carries
   `gulfpub_crosscompare=0`, so ~100 gas rows needing a decision (32 GulfPub gas overlaps, 8
   additions, 18 GEM-only, 1 status conflict, 11 ambiguous clusters; 5 OSM additions, 37
   GEM-only) exist **only** in these two files. Do not archive them with the packet.
   - The GulfPub file also carries `Oil_*` tabs (72 overlaps / 17 additions / 19 GEM-only /
     2 status conflicts / 24 ambiguous) because the recon ran `--commodity both`. Libya oil
     has never been swept, so that is the only oil-facing output that exists for Libya —
     untriaged, and out of scope for this gas batch.
   - The GulfPub file was **rebuilt 2026-07-29** (`0941_ET`; the `07-28 1148_ET` version is in
     `archive/`) after the dataset-wide fix to `Ref Length (km)`, which had been miles read as
     km, ~38% short. Counts are unchanged; three overlaps moved yellow→green and one re-targeted
     from a day of GEM drift, not from the unit fix (matching scores length on `geodesic_km`).
     `notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`.

Archived 2026-07-29 as subsumed by the handoff (in `archive/`, not deleted): the 07-23
`…_annual-indev.xlsx` (its `staging/annual` is a listed prior staged packet; 8 decisions
carried) and `…_discovery.xlsx` (its single new row is the packet's `Gas_NewRows`).

Ref work across the scope: 220 REFS_ADDED / 55 re-verified / 28 unresolved. Operator
attribution went from 0 referenced rows to referenced on every row Leg 3 touched.

## Applied 2026-08-06 — §8 routes + GGIT row deletions

Routes-repo merge `445b3613`; sheet backup `notes/sheet-write-2026-08-06-libya-gas-route-replacements.csv`.
`audit_route_sync.py --country Libya --commodity gas` = **0 out-of-sync rows**.

- **P6708 / P6715 duplicate resolved → P6715 kept, P6708 deleted from GGIT.** One
  pipeline, named at two levels: "NC 41-Mellitah" is the *concession* (Area D, ex-NC41,
  which also contains Bahr Essalam), "E Structure-Mellitah" is the *structure*. The
  operator's own prequalification enquiry JPTPQ/018/21 lists exactly one new gas line to
  Mellitah — 32in, 130 km, from PP E. P6708's every field traced to a single GlobalData
  marketdata profile whose primary ref (`libyasummit.com/libya-rolls-out-downstream-gas-capture-plans/`)
  404s with **no Wayback snapshot at all**. Keep the 130 km / 32in / construction values.
- **P6715 route replaced and applied.** The prior geometry started within ~1 km of the
  Mellitah O&G **Tripoli office** (an OSM POI, not the complex) and ran onshore, ending
  ~19 km short of Mellitah — `medium` was unsupportable. Replacement is a straight-line
  schematic PP E → Mellitah complex, 134 km vs the sheet's 130. `RouteAccuracy` →
  `very low (straight line/schematic)`; `RouteCreator` `NA` → `CB` (5 cells).
  - **PP E is a derived coordinate**: 33.849 N, 13.054 E, ±10 km, from georeferencing the
    Area D location map in JPTPQ/018/21 (scale-bar fit anchored on the OSM Bouri
    platforms; the map's *coastline* is decorative — an early fit off coastal towns
    missed by 128 km). WHP A derives to 33.568 N, 12.439 E on the same fit.
  - Mellitah complex = **32.854994 N, 12.2414883 E** (OSM way 310844993), not the
    ~11.71 E / 33.005 N value used earlier in the sweep.
- **P3987 Intisar–Sarir route replaced** (BL's own 45-pt digitized trace, replacing a
  2-pt schematic); start snapped exactly to GOGPT `Sarir power station`
  **26.909488 N, 22.095786 E**. Row values unchanged — `RouteCreator BL` /
  `RouteAccuracy medium` already fit the new geometry, so **no sheet write**.
  - **Open conflict**: the trace is 280 km against `LengthKnown` 114 km (+146%,
    `qc_routes` WARN, included deliberately). Sarir power station → Intisar is ≥269 km
    straight-line, so **114 km cannot be right for these endpoints** — either the length
    is wrong or the route overshoots the actual pipe. `LengthEstimateKm` is also stale
    at 185.11 (the old schematic).
- **Three orphan geojsons removed** from the routes repo (`P6705`, `P6708`, `P6713` —
  rows deleted from GGIT). P3987 was deleted and then restored the same day, so its
  route was kept.
- **Still open from this pass:**
  - The **design conflict on the E-Structure line** is unresolved: the operator says a
    dedicated 32in / 130 km sealine direct to Mellitah, offshore-technology says a 30 km
    36in tie-in to the existing Sabratha–Mellitah line. **GOIT P6445 "NC 41–Mellitah
    Condensate Pipeline"** (shelved, 30 km, 10in) carries the same conflict and should
    be resolved with it. The derived PP E sits 36 km from the Sabratha platform, which
    makes the "30 km" figure geometrically sensible for the *same* asset.
  - **Structure A's 18in / 43 km line to Sabratha appears missing from GGIT** — a
    discovery candidate. (Weakest check in the georeference: A→Sabratha measures 29 km
    straight-line against the stated 43 km, a 48% detour, so A is the softer of the two
    derived positions.)
  - **P6715 row edits not yet applied** (non-route): add `NC 41-Mellitah Gas Pipeline`
    to `OtherEnglishNames`, `StartYear1` 2025 → 2026, drop the "Bay of Tripoli" origin,
    and fix `Diameter [ref]` — it is a `google.com/url?q=` redirect wrapper, not the
    bare PDF URL.

## Applied 2026-08-07 — "Intesar" → "Intisar" (spelling)
The field is **Intisar**; GGIT carried the "Intesar" misspelling on 7 Libya gas rows
(0 oil rows). Authorized write, **12 value cells across 6 rows** applied and verified —
`PipelineName` / `StartLocation` / `EndLocation` / `RouteNotes` on P1856, P1858, P1870,
P1873, P6714, P8043 (P1861 needed no value change; its name is already
"Farigh-Intisar 103A"). Backup: `notes/sheet-write-2026-08-07-libya-gas-intesar-intisar.csv`.
The operators/owners tab's 13 hits are **XLOOKUP formulas** off the gas tab — they
auto-update and must never be written.

- **Wiki half DONE the same day.** All five pages moved to the `Intisar` spelling
  (`Intesar-Brega` / `Bu-Attifel-Intesar` / `Faregh-Intesar` / `Intesar-Sahel` /
  `Jakhira-Intesar` `_gas_pipeline`), each leaving a **redirect** at the old title — the
  account lacks `suppressredirect`/`delete`, and Baird's call was to leave them. Column D
  then repointed on all 7 rows (7 cells, applied and verified; P6714's leading space
  stripped). Backup: `notes/sheet-write-2026-08-07-libya-gas-intisar-wikilinks.csv`.
  - The moves were blocked for most of the day by Cloudflare **Under Attack Mode** on the
    gem.wiki zone (a traffic flood took the site down earlier that week). Fix was a WAF
    bypass keyed on the User-Agent token **`baird-wiki`** — the UA string is load-bearing,
    full writeup in `goit-ggit-data-ops/gem-wiki/README.md` → Auth. `move_page()` was
    added to `gemwiki.py` in the same pass.
  - **Page bodies still say "Intesar"** — a move renames only. The bolded lead sentence
    (and possibly infobox/prose) on all five needs a separate `edit_page` pass.
- **Non-spelling defects found in passing** (not fixed): **P1856** "Intisar-Zueitina"
  links to `Intesar-Brega_gas_pipeline` — the wrong page, shared with P8043;
  **P1858 and P6714** are both "Bu-Attifel-Intisar Gas Pipeline" on one wiki page and
  look like duplicate rows; **P6714's** column D has a leading space; and the wiki title
  says "Faregh" where the tracker says "Farigh" (P1861).

## Open items
- **Cluster A — the structural double-count (Baird's ruling needed).** P0483 "Libya
  Coastal Gas Pipeline" appears to aggregate its own member segments P1862 / P1863 /
  P1864 / P1865, with P1789 a sixth overlapping row. Baird's initial read: either
  delete the member segments, or move P0483 to a network-route designation. Note the
  vocab constraint — **`n/a` is not a valid `Status`**; aggregate rows take a **blank
  Status plus a `PipelineNetworkGrouping` label** (precedent: P3656, P3672, P3966,
  P5885, P7150). Corroborating geometry: P1789's drawn route is the entire
  Khoms→Mellitah coast (249 km) against a stated 25 km, and is very nearly
  P1864 (105 km) + P1865 (117 km) laid end to end.
- **Three condensate lines** (P6705 delete / P6713 delete / P6709 move) — above.
  P6705 and P6713 were deleted 2026-08-06; **only the P6709 move is still open**.
- **`scm` capacity units** — 4 Libya + 4 Algeria rows — above.
- **14 lengths carry a spurious miles→km conversion** (P1856, P1857, P1859, P1860,
  P1861, P1862, P1864, P1865, P1866, P1867, P1868, P1869, P1870, P1871) — above, and
  `notes/escalation-2026-07-28-asb-libya-length-units.md`.
- **Operator attribution is a systematic gap**: 27/38 blank, 38/38 unreferenced.
- **Oil-side flags raised from the gas batch, not yet actioned** (a Libya oil pass
  would pick these up):
  - **GOIT P0606 vs P5215** — "Wafa-Mellitah Oil Pipeline" and "Wafa-Mellitah NGL
    Pipeline", both 16in on the same endpoints, adjacent rows. Possible within-GOIT
    duplicate.
  - **GOIT P6457 route is drawn to the wrong Sabratha** (found 2026-08-06, needs a
    replacement decision). "Sabratha-Mellitah Condensate Pipeline", `LengthKnownKm`
    107, but the geojson is a 2-point 21.9 km line whose start (12.463719,
    32.792894) is **2.2 km from the Roman ruins of Sabratha** and 109.9 km from the
    Sabratha *platform* — a name collision. Length ratio 0.20, well outside
    `[0.75, 1.33]`. The gas twin **P1855 is sound** (3 vtx, 105.5 km vs 109, ratio
    0.97, starting offshore at 12.6906, 33.7238). Since the operator states both the
    36″ gas line and the 10″ condensate line run platform→Mellitah, the fix is to
    reuse P1855's corridor for P6457 — a human "reuse another PID's geometry" call
    (cf. China P3894), staged nowhere yet. Replacement is permitted rather than an
    escalation because the existing accuracy is `very low (straight line/schematic)`.
  - **GOIT P5237 vs P5238** — Nafoora-Zueitina, one `operating` (68 km, 24/16in) and
    one `shelved` (68.5 km, 12in), on the same endpoints. Two GulfPub records both
    landed on the shelved one.
- **GulfPub additions** — 4 below-practice gathering laterals awaiting a scope
  ruling; 3 at 12–16in are Discovery candidates needing the 2-independent-source
  test.
