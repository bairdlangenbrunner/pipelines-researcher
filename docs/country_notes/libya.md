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
    from GGIT, do not "move" it.
  - **P6713** (10in Bahr Assalam-Mellitah) → GOIT already has **P6457** → **delete**.
  - **P6709** (4in Bouri-Bahr Assalam) → GOIT has **no** matching row → **move**.
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

## Deliverable

`batches/libya-gas/deliverables/pipelines_batch_20260728_1235_ET_libya-gas_handoff-{actions,evidence}.xlsx`
(gitignored — regenerate from `batches/libya-gas/staging/qc/` if missing). **Work from
the ACTIONS file**, not the per-leg workbooks: 89 open decisions, 229 paste-ready
backend cell units, 65 operator/owner units, 1 new row, 97 wiki updates, 51 open flags.
Both READMEs carry an `ESCALATIONS` row listing the five class-level rulings needed.

Ref work across the scope: 220 REFS_ADDED / 55 re-verified / 28 unresolved. Operator
attribution went from 0 referenced rows to referenced on every row Leg 3 touched.

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
  - **GOIT P5237 vs P5238** — Nafoora-Zueitina, one `operating` (68 km, 24/16in) and
    one `shelved` (68.5 km, 12in), on the same endpoints. Two GulfPub records both
    landed on the shelved one.
- **GulfPub additions** — 4 below-practice gathering laterals awaiting a scope
  ruling; 3 at 12–16in are Discovery candidates needing the 2-independent-source
  test.
