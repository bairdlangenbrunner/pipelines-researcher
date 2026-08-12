# Research backlog — unfinished / ongoing projects

Inventory of started-but-unfinished research threads. Baselined **2026-07-15** by a
full-repo audit and maintained continuously since (latest entries 2026-07-28). Update
this file when a thread closes or a new one opens; per-country detail stays in
`docs/country_notes/`, and this file just tracks what's open and where.

---

## 1. Global GGIT Stage A/B/C rollout — RETIRED (2026-07-15)

Plan doc: `docs/plans/ggit_update_2026-07.md` (decisions locked 2026-06-10) —
**superseded by the campaign annual-packet mechanism** (`campaigns/ggit-2026` roster
+ per-country Country Sweep `in-dev` preset / Discovery / Handoff Packet,
`docs/workflows.md §7`). Stage A's work (in-dev status sweep) IS the in-dev preset;
Stage B/C's ref/sweep-up work is the sweep's refs leg, run per country as the
campaign reaches it. The plan's Process-B tooling (`build_backfill_worklist.py`,
the ledger) was never built and won't be. The plan doc's row counts remain useful
as a scale reference (in-dev ~998 rows / 137 countries; stale tier-1 refs ~1,854
rows; incl. 9 broken-status rows flagged as data bugs). 4 of 137 countries done so
far via the campaign path (Iraq, Iran, Saudi Arabia, Egypt).

## 2. Research legs started but not finished

| Thread | State | Source |
|---|---|---|
| **Egypt oil (GOIT)** | never swept | `docs/country_notes/egypt.md` |
| **Saudi oil ref-sweep** | 3-row validation slice (2026-06-08) + 10-row batch staged; partial toward intended 50-row run | `batches/saudi-arabia-oil/staging/ref-sweep{,-10row}/`; `docs/country_notes/saudi-arabia.md` |
| **Saudi GulfPub route-consistency pass** | low/medium-accuracy matches not finished; route-replacement candidates not staged | `docs/country_notes/saudi-arabia.md` |
| **GulfPub route-comparison QC leg** | not started — Baird explicitly wants this later: extend the handoff packet's route-integrity leg to compare drawn routes against GulfPub *geometries* (ties into the unfinished Saudi route-consistency pass above). Distinct from the sweep's *attribute* crosswalk, which IS built and shipping (`build_recon_crosswalk.py`) | `docs/workflows.md` §6; `docs/sops/qc.md` |
| **Handoff-packet rollout (researcher onboarding, Arabic-speaking gas)** | Egypt is the pilot (2026-07-15); **Libya 38 done 2026-07-28**; remaining candidates by GGIT row count: Algeria 126, Qatar 59, UAE 39, Oman 23, Tunisia 21. Do Algeria next — 4 of its rows share the Libya `scm/y` capacity defect, so the fix and the sweep are one job | `docs/workflows.md` §6; `docs/country_notes/{egypt,libya}.md` |
| **Nigeria divestiture ownership sweep** | not started | `docs/country_notes/nigeria.md` |
| **Japan P1050 ownership: JAPEX or ENEOS?** | Surfaced 2026-08-12 by the spreadsheet-ref archiving batch. JOGMEC's **2024** edition credits the Shiroishi-Koriyama Line to "ENEOS / Tohoku Electric Power"; GEM's `Owner` says `JAPEX [50.%]; Tohoku Electric Power [50.%]`. The cited **2022** edition is gone from the web, so the two editions can't be diffed — cannot tell a JOGMEC correction from a real stake transfer. Needs an independent source; do NOT apply the ENEOS name off this document alone. The `Owner [ref]` cell (`operators/owners!U923`) was deliberately left pointing at the dead 2022 URL rather than repointed to a document that contradicts the value | `notes/escalation-2026-08-12-unarchivable-xlsx-refs.md` §2 |
| ~~**Gazprom Orenburg refs unarchivable**~~ | **RESOLVED 2026-08-12.** All 29 `[ref]` cells across P6110/P6111/P6114–P6118 repointed to the archived **earlier edition of the same file** — `lch-god.xls` (no `-2`), Wayback `20220506054715`, table dated 01.01.2021. The `-2` was a CMS collision-rename on re-upload, confirmed by verifying value-by-value first: 7/7 start years and 7/7 lengths match at two decimals. The origin itself stays permanently unreachable (Gazprom AS39045 geo-blocks non-RU IPs; SPN 520; no RU-exit proxy path found) — so treat any *future* Orenburg ref the same way: look for a sibling edition in Wayback before calling it unarchivable | `notes/escalation-2026-08-12-unarchivable-xlsx-refs.md` §1 |
| **United States** | deepwater-export terminal open item; 131-row Stage A queue slot unstarted | `docs/country_notes/united-states.md`; plan doc |
| **Iraq oil open items** | Grand Faw third offshore line (Esta/Micoperi) length/diameter/route; P0544 Basra–Haditha status review | `docs/country_notes/iraq.md`; CLAUDE.md |
| **Iraq oil: OSM + GulfPub recon untriaged** | First-ever OSM run for Iraq oil (2026-07-28, 246 features): 71 overlaps, 175 unmatched — **84 DISCOVERY_CANDIDATE (366 km, largest 26.5 km)**, 61 FRAGMENT_OF_EXISTING (incl. 80.9 km near P0548, 52.3 km near P0577), 21 ROUTE_FOR_EXISTING (86.1 km → P6255), 9 NEAR_MISS (80.3 + 53.6 km near P7898). GulfPub oil re-run: 20 overlaps, 8 status conflicts, 1 near-miss. Nothing triaged; no oil sweep or handoff packet exists to carry it | `batches/iraq-oil/deliverables/pipelines_batch_20260728_1804_ET_iraq-oil_{osm,gulfpub}-reconciliation.xlsx`; `docs/country_notes/iraq.md` |
| **Egypt gas: OSM + GulfPub recon untriaged** | Run 2026-07-29 to give Egypt the coverage Libya has; **both workbooks are standalone and NOT in the handoff packet**, so nothing routes them into the actions file. GulfPub (92 features): 52 overlaps, **40 additions all bucketed `NEAR_MISS`** (over the >30 escalation gate — adjudicate each against the near row before treating any as a discovery), 43 GEM-only, 3 status conflicts, 12 ambiguous clusters, 1 route-replacement candidate. First-ever Egypt OSM run (21 features / 476.6 km): **0 overlaps**, both `MATCH_QUALITY` escalations raised (0/21 named × 62/78 GEM rows routeless; top composite 0.4094 vs 0.45, threshold NOT lowered) → 9 `ROUTE_FOR_EXISTING`, 2 `FRAGMENT_OF_EXISTING`, 10 `DISCOVERY_CANDIDATE`. GulfPub rebuilt at `0941_ET` with the length-units fix (§4) — counts unchanged, `Ref Length (km)` now correct | `batches/egypt-gas/deliverables/pipelines_batch_20260729_0941_ET_egypt-gas_reconciliation-gulfpub.xlsx` + `…_0910_ET_…-osm.xlsx`; `docs/country_notes/egypt.md` |
| **Libya gas: OSM + GulfPub recon untriaged** | Same structural gap as Egypt's — the 2026-07-28 full pass built both recon workbooks but the handoff packet does **not** subsume them (`gulfpub_crosscompare=0`; neither recon dir appears in "Prior staged packets"), so ~100 gas rows needing a decision live only in those two files: 32 GulfPub gas overlaps / 8 additions / 18 GEM-only / 1 status conflict / 11 ambiguous, plus 5 OSM additions / 37 GEM-only. The GulfPub file also holds **untriaged `Oil_*` tabs** (72 overlaps / 17 additions / 19 GEM-only / 2 status conflicts / 24 ambiguous) from a `--commodity both` run — the only oil-facing Libya output that exists, and Libya oil has never been swept. GulfPub rebuilt `20260729_0941_ET` with the length-units fix (§4); same counts, 3 yellow→green and one re-target from a day of GEM drift | `batches/libya-gas/deliverables/pipelines_batch_20260729_0941_ET_libya-gas_reconciliation-gulfpub.xlsx` + `…_20260728_1149_ET_…-osm.xlsx`; `docs/country_notes/libya.md` |
| **Iraq gas: OSM + GulfPub recon untriaged** | Moved OUT of the handoff packet 2026-07-29 into two standalone workbooks (Libya's shape) — the packet's `Gas_GulfPubActions`/`Gas_OSMActions` tabs are **retired**, so recon rows are now reachable ONLY here. GulfPub (`--commodity both`, 47 refs, post-fix lengths): 39 overlaps (19 gas / 20 oil), 8 additions (7 gas / 1 oil), 105 GEM-only, 13 status conflicts, 14 ambiguous; its `Oil_*` tabs are untriaged and belong to the iraq-oil scope. OSM (52 refs, gas only): 8 overlaps, 44 unmatched — **30 `ROUTE_FOR_EXISTING`** (candidate geometry for routeless rows), 10 `DISCOVERY_CANDIDATE`, 2 `FRAGMENT_OF_EXISTING`, 2 `NEAR_MISS`, 50 GEM-only, 5 status conflicts. **The OSM run carries a `MATCH_QUALITY` warning** (3.8% of refs named × 35.7% of GEM gas rows routed → 96.2% of matching rests on the province-coarse admin-area signal); GulfPub is healthy (100% named, 83% overlap rate) | `batches/iraq-gas/deliverables/pipelines_batch_20260729_1104_ET_iraq-gas_reconciliation-{gulfpub,osm}.xlsx`; `docs/country_notes/iraq.md` |
| **Pakistan gas: OSM + GulfPub recon untriaged** | First-ever Pakistan pass (2026-08-07). Both workbooks are **standalone and NOT in the handoff packet** (`recon_actions=0`), so nothing routes them into the actions file. GulfPub (94 features): **82 overlaps — the best match rate of any country swept so far**, and the reason the existence question narrowed before the SNGPL register closed it; 12 additions (under the >30 gate), 0 status conflicts, 11 near-misses. OSM: only **9 features for the whole country** — 4 overlaps, 3 `FRAGMENT_OF_EXISTING`, 1 `ROUTE_FOR_EXISTING`, 1 `NEAR_MISS`, **0 discovery candidates**. OSM coverage of Pakistan gas transmission is effectively absent — do not read the thin result as agreement | `batches/pakistan-gas/deliverables/pipelines_batch_20260807_1530_ET_pakistan-gas_reconciliation-{gulfpub,osm}.xlsx`; `docs/country_notes/pakistan.md` |
| **India gas: OSM + GulfPub recon untriaged** | First-ever India pass (2026-08-10). Both workbooks are **standalone and NOT in the handoff packet** (`recon_actions=0`). GulfPub (158 features — the largest reference extract of any country swept): 74 overlaps, **84 additions**, 40 GEM-only, **22 status conflicts**, 22 ambiguous — **BOTH escalation gates crossed** (>30 additions; 22/74 = 30% conflicts, >10%). Dispositions: NEAR_MISS 56, DISCOVERY_CANDIDATE 23, FRAGMENT_OF_EXISTING 5. Caveat before adjudicating any length conflict: **15 of the 158 GulfPub features repeat a SYSTEM total on a segment feature** (the whole HVJPL/GREP/DVPL family carries one 4,657 km figure across 6 features) — that is GulfPub's artifact, not GEM's error. OSM (61 features / 2,721 km, 44% named): 1 overlap, 60 additions, 34 `FRAGMENT_OF_EXISTING`, 25 `DISCOVERY_CANDIDATE`. **The thin OSM overlap is NOT a matcher defect** — health line clean (44.3% named × 98.7% GEM routed, no `MATCH_QUALITY` warning), and the cause is granularity: short OSM fragments of very long GEM trunk lines score 1.00 on name but ~0.18 IoU → composite 0.34–0.44 against a 0.45 threshold. India is the healthiest OSM extract in the registry so far, and `sources/osm/manifest.yml` deliberately carries **no `geoarea_weight` override** for `gas_in` — do not add one | `batches/india-gas/deliverables/pipelines_batch_20260810_1851_ET_india-gas_reconciliation-{gulfpub,osm}.xlsx`; `docs/country_notes/india.md` |
| **Saudi Arabia / Iran gas: fresh standalone GulfPub recon workbooks (2026-07-29)** | Produced by the length-units re-run (§4) and **not in any packet**. Saudi (20 refs): 18 overlaps / 2 additions / 23 GEM-only / **9 status conflicts** / 1 ambiguous. Iran (43 refs): 25 overlaps / 18 additions / 25 GEM-only / 3 status conflicts / 10 ambiguous. **Both pre-fix runs date from 07-05/07-06 and predate the admin-area geo signal, per-dataset matching overrides and the 'very low' re-grade — read these as fresh runs, not deltas**, and expect their packets' `Gas_GulfPub` crosswalk tabs to be stale | `batches/{saudi-arabia-gas,iran-gas}/deliverables/pipelines_batch_20260729_0941_ET_*_reconciliation-gulfpub.xlsx` |
| **Israel gas: Ashdod–Ashkelon onshore gap (P3620)** | routes + sheet edits APPLIED 2026-07-23 (Baird bridged the Ashdod HDD bore so P3620 meets P3657; routes-repo merge `72d29de1`; sheet RouteAccuracy→medium/RouteNotes/Route [ref] written rows 1036/1063; batch archived), but P3620 geometry is still partial — 2.1 of 4 sheet km; the Ashkelon-side ~2.4 km onshore run has no public vector yet (OSM empty, TAMA 37/A/2/7 blueprint sheets cover Ashdod only) — need the Ashkelon-side statutory sheet or an INGL/permit map to finish it. P3657 is complete | `batches/israel-gas/archive/route-creation-p3620-p3657/README.md` |
| **Iran general open items** | P6074 verify-before-removal; P5367 reclassify as Neka–Ray segment | `docs/country_notes/iran.md`; CLAUDE.md |
| **Re-run link checks for every country swept before 2026-08-11 (engine defect, ours)** | `url_verifier.verify_url` returned a bare `request failed: SSLError` for hosts serving an incomplete TLS chain, which reads as a dead link. It now retries once with verification off and stamps `insecure_tls: True` — that verdict means **the page IS live**. In Kazakhstan gas the defect hit **51 of 105 ref cells with ZERO real 404s** (45 SSLError + 5 ConnectionError + 1 ReadTimeout; the operating leg went 55 → 63 all-live once fixed), because half the country's refs are `adilet.zan.kz`. So any earlier country whose worklist shows `SSLError` link-rot flags has **false DEAD_LINK findings staged**, and the only fix is to re-run the worklist — the flags cannot be re-read. Known affected hosts so far: `adilet.zan.kz`, `pgjonline.com`, `eeer.org`. Two sibling defects fixed the same day (diameter units per row; thousands separator vs multi-value comma) have their own blast radii recorded in `docs/sops/reconciliation.md` — the QC `Diameter_OutOfRange` sheet of **any** workbook built before 2026-08-11 should be discarded (1,497 false findings, 1 real) | `docs/sops/sweep.md` §Verifier false-negatives; `docs/sops/{reconciliation,qc}.md`; commits `37ab566`, `7613c39` |
| **OSM recon: read `best_guess` as arithmetic, not geography, in four pre-2026-08-11 runs (reporting defect, ours)** | `reconcile.py disposition()` printed "Nearest was P####" on every `DISCOVERY_CANDIDATE`/`NEAR_MISS`. When the reference is unnamed (`s_name` 0), the guessed GEM row has **no drawn route** (`g_untested`) and no province score got through (`s_geoarea` 0), the only live axis is **length** — so "nearest" was whichever row happened to be a similar number of kilometres, anywhere in the country. Kazakhstan OSM had 18 unnamed traces spread lon 51→78 all "nearest" to routeless P5776 (17.8 km), several 1,500 km from its corridor. **Fixed 2026-08-11**: the note now names the dead axes and says to read the PID as arithmetic. Kazakhstan was re-run + its workbook rebuilt. **NOT re-run** (their GEM snapshots are older, so a re-run would silently move matches and break the packets' `SheetRow` locators): `iraq-oil/recon-osm-20260728` **82 of 184**, `egypt-gas/recon-osm-20260729` 10/21, `india-gas/recon-osm-20260810` 8/61, `iraq-gas/recon-osm-20260729` 2/46 — in those workbooks ignore the `Nearest`/`best_guess` PID on any addition whose reference is unnamed and whose guessed row has no route. GulfPub runs are unaffected (0 blind in all 12) | `scripts/reconcile.py` `disposition()`; `batches/kazakhstan-gas/deliverables/…_20260811_1043_ET_…reconciliation-osm.xlsx` |
| **LNG carrier quarterly reconciliation** | "designed and partially executed" vs SFOC data; referenced `instructions.md` methodology is **not in this repo** — orphaned | `docs/PROJECT_SETUP_AND_CONTEXT.md` §9/§11 |

## 3. Staged, awaiting Baird's manual application (research complete)

Roster `applied` column is blank for all four countries — log the date when pasted.
Iraq/Iran xlsx deliverables are already pruned from disk, so file presence is not a
signal of application status. Neither is the blank roster column: Saudi and Egypt turn
out to be **partially applied** on the live sheet (see the second note below), so verify
per cell rather than trusting either signal.

> **Stale `SheetRow` locators — RESOLVED 2026-07-28.** `SheetRow` is positional, so it
> perishes as the sheet is re-sorted or rows are inserted (GGIT gas was re-ordered between
> the 07-04 and 07-05 pulls), which silently invalidated every locator staged by an earlier
> leg. Fixed three ways: `build_ref_workbook.py` now re-derives every locator from the fresh
> CSV at build time (`_restamp_sheet_rows`); all staged JSON was corrected at rest
> (8,853 nodes — saudi-arabia-gas 4,879 · egypt-gas 973 · saudi-arabia-oil 933 · iran-gas 600 ·
> libya-gas 4 · israel-gas 1 — a provably value-only diff); and the three affected packets were
> rebuilt against `GGIT_gas_snapshot_20260728.csv` (egypt-gas handoff, 43 bad cells →
> `…_20260728_1731_ET_…`; saudi-arabia-gas deepsweep 436 →; annual-indev 275 →), with the
> pre-fix files moved to each batch's `archive/`. **All 19 current deliverables now audit
> 0-bad against the live sheet.** No values were ever wrong (they were current at build time)
> and nothing was auto-applied. Any *new* consumer must re-derive from the current CSV keyed on
> ProjectID rather than trusting a staged `sheet_row` — see `docs/reference/gem_schema.md`.
>
> **Found while rebuilding: parts of these packets are already on the live sheet.** Measured by
> testing whether each staged ref URL is now present in its target `[ref]` cell —
> **saudi annual-indev 100 of 199** ref units fully live (4 partial), **saudi deepsweep 46 of
> 306** (5 partial), **egypt handoff 16 of 284** (26 partial); Iraq gas is 0 of 134, so the
> test isn't over-reporting. Corroborating: 32 of 40 in-scope Saudi *operating* rows were
> edited live between the 07-08 and 07-28 pulls (`Researcher`/`LastUpdated` churn on 28,
> plus `RouteNotes`/`StartLocation`/`ResearcherNotes` fills). So "staged, not applied" is
> wrong for Saudi and Egypt — they are **partially applied**, by whom and how deliberately is
> unknown. Because the rebuilt workbooks prefill from the 07-28 snapshot they now show that
> state, but nothing de-duplicates it: **before pasting Saudi/Egypt, check whether the cell
> already carries the ref.**

- **Kazakhstan gas** — **first-ever pass, 2026-08-11** (§9 full pass: operating deep sweep 39 rows ·
  in-dev annual review 11 · cancelled/mothballed review 2 · redundancy adjudication 11 clusters /
  28 rows · GulfPub + OSM recon · wiki alignment · route integrity · Leg-3 system-brief research).
  **THREE files to work:** `pipelines_batch_20260812_1255_ET_kazakhstan-gas_handoff-actions.xlsx`
  (119 open decisions · 3 status changes · 266 backend paste units · 64 operators/owners units ·
  31 wiki updates · 180 open flags) + its `-evidence` companion + the two **standalone recon
  workbooks** at `20260811_1001_ET` (GulfPub) and `20260811_1043_ET` (OSM), which the packet does
  not subsume (`recon_actions=0`; see §2). **The country's defining fact is that its network is
  multi-string trunks and there is NO public line-wise register** — the best line-wise source, the
  KMG Annual Report's gas-transportation table, itemises only the 8 major *systems*, i.e. exactly
  the system-level aggregates that are the defect. So in at least six systems one system figure is
  restated on every string (CAC 60.20 bcm/y on three rows, with P2292's 5.00 as the control that
  proves it; BTBA 1,585 km on both; Bukhara–Ural 21.00 bcm/y; ZhZhA 4.54 bcm/y on four), and an
  honest `UNRESOLVED` on a per-string spec is often the **correct** outcome — unlike India. Two
  method rules came out of it, both the hard way. **(1) Identical drawn geometry is not evidence of
  duplication here** (six systems share one corridor geojson across their strings), and cluster A
  is the cautionary tale: it had the aggregate-vs-segment signature (P3948's trace = P5777 +
  P5783 exactly) *and* the sheet's lengths agreed to 0.20 km, and the double count was still
  **REFUTED** — two independent official sources name P3948 as its own 720 mm / 149.1 km trunk
  parallel to a separately-named 529/530 mm one, and segment traces cut from a parent produce the
  union identity for free. Our fold recommendation is withdrawn; **only sourcing decides
  duplication in this country.** **(2) `adilet.zan.kz` serves an incomplete TLS chain**, which our
  verifier reported as a bare `SSLError` — it hit 51 of 105 ref cells with **zero real 404s**
  before the fix. `insecure_tls: True` means the page IS LIVE, and adilet's `#z250` anchors land in
  Appendices 5–7, which are графические схемы (**maps**), so a full-text miss is not evidence a ref
  fails. Five escalations open (`batches/kazakhstan-gas/staging/qc/escalations.json`), incl.
  P7819's three-way route-sync violation and both recon gates (GulfPub's 14.8% status conflicts
  collapse to two segment-vs-network artifacts; OSM's 110 additions are 55 explicit
  `FRAGMENT_OF_EXISTING` + 55 mostly-stub candidates — **do not add a `geoarea_weight` override**,
  the health line is clean). Oil (41 GOIT rows) not swept. `docs/country_notes/kazakhstan.md`.
- **India gas** — **first-ever pass, 2026-08-10** (§9 full pass: operating deep sweep 35 rows ·
  in-dev annual review 27 · cancelled review 13 · redundancy adjudication 11 clusters / 34 rows ·
  GulfPub + OSM recon · wiki alignment · route integrity · ref-gap re-pass · Leg-3), plus a
  **PNGRB NGPL MIS register crosswalk** — India's analogue of Pakistan's SNGPL register, and a
  better one. **FOUR files to work:** `pipelines_batch_20260810_1851_ET_india-gas_handoff-actions.xlsx`
  (161 open decisions · 15 status changes · 469 backend paste units · 119 operators/owners units ·
  111 wiki updates · 209 open flags) + its `-evidence` companion + the two **standalone recon
  workbooks** at the same stamp, which the packet does not subsume (`recon_actions=0`; see §2).
  **India is the INVERSE of Pakistan and that shapes everything.** Pakistan's problem was
  provenance — no text behind the rows. India's rows are actively maintained, coherent and real;
  what they lack is **citations**, filled on ~9% of ref cells (149/1,650), with the gap
  concentrated on *operating* rows (34 of 35 carry no PNGRB ref at all) while in-dev rows are
  well cited (27 of 28). **So an `UNRESOLVED` here is a WEAK result, not the correct outcome** —
  proven empirically: a second ref-gap pass moved the operating leg from 116 to **251**
  `REFS_ADDED` and 286 → **153** `UNRESOLVED`, DEAD_LINK 2 → 0. Do not carry Pakistan's
  "the refs genuinely don't exist" heuristic across. **The PNGRB register**
  (`pngrb.gov.in/data-bank/20260531-NGPL-MIS-Report.pdf`, parsed by
  `scripts/parse_pngrb_ngpl_mis.py`, crosswalked by `scripts/crosswalk_pngrb_india.py`)
  accounts for **all 71** India-only rows — 40 matched, 31 explained-absent — and staged 118
  ref-only units. It beats SNGPL's on three axes: it is the **regulator** (not the operator), it
  **carries dates**, and it reports operating *and* under-construction length per row. **Two
  caveats that must travel with it:** it is **common-carrier only** (14 rows are correctly
  absent as dedicated/tie-in lines, 1,601 km of residual inside the grand totals), and **PNGRB is
  the de facto ORIGIN of GEM's India capacity column** — equal at two decimals on ~20 rows — so
  PNGRB + a company restatement is **one** origin, not two, and cannot alone reach high tier.
  **India's duplicates are REGULATORY, not bibliographic:** the dispositive test is the
  authorisation number / sponsor / authorisation date holding constant across register editions
  while the project NAME changes — that beats any name-similarity argument, and it both
  CONFIRMED cluster F (Kanai Chhata) and REFUTED 5 of 11 clusters. Twelve escalations open
  (`batches/india-gas/staging/qc/escalations.json`), led by the 9% ref-density finding, the
  P0907-is-a-section-of-P0929 double count (~718 km), the 107.00 MMSCMD stamped on five HVJ
  rows, and `Operator` blank on 74/75 — **a genuine gap, not the tracker norm** (18.2% of GGIT
  gas rows carry one). Oil (26 GOIT rows) not swept. `docs/country_notes/india.md`.
- **Pakistan gas** — **first-ever pass, 2026-08-07** (operating deep sweep 63 rows · in-dev annual
  review 6 · cancelled review 1 · GulfPub + OSM recon · wiki alignment · route integrity · Leg-3
  corridor research), plus the **SNGPL asset-register crosswalk added 2026-08-10**. **THREE files
  to work:** `pipelines_batch_20260810_1112_ET_pakistan-gas_handoff-actions.xlsx` (59 open
  decisions · 4 status changes · 254 backend paste units · 22 operators/owners units ·
  22 wiki updates · 416 open flags) + its `-evidence` companion + the two **standalone recon
  workbooks** at
  `20260807_1530_ET`, which the packet does not subsume (`recon_actions=0`; see §2).
  **The country's defining fact is provenance, not thin research:** 51 of 70 rows are one
  July-2023 bulk load off two MAP files, so 362 ref units are legitimately `UNRESOLVED` and the
  16 `existence` flags were tracking *segment obscurity*. **The 2026-08-10 register crosswalk
  resolves that cohort** — SNGPL's own audited *"TRANSMISSION SYSTEM As at June 30, 2018"*
  (Annual Report 2018, 270 sections, parse reconciles to the printed grand total) accounts for
  **49 of the 51 rows** at two-decimal precision, closing **all five** residual existence
  questions and **all three** redundancy clusters (the register lists both pipes of each pair at
  *different diameters* — the ordinary mainline/loopline pattern). Staged as **98 ref-only units
  across 49 rows** with no value changes. **Two items survive:** P4074 (register 52.23 km vs
  sheet 55.23 — the only numeric disagreement in 49 rows; direction unknown, do not apply blind)
  and P5486 Mardan–Swat (the one row the register does not account for at all). Not helped by it:
  the 8 SSGC rows, and all 60 `operating`-with-no-`StartYear1` rows (the register carries no
  dates). **Method finding worth reusing:** 63 per-row subagents could not crack this cohort;
  one operator annual report did it in a single pass — where a country's rows trace to a bulk
  load off an operator artifact, go looking for that operator's audited annual report first.
  **The gem.wiki 403 blackout that ran through the whole 08-07 pass is fixed and both wiki legs
  were re-run 2026-08-10** (`WIKI_UA`: the WAF passes a UA leading with the `baird-wiki` token —
  same string as `goit-ggit-data-ops/gem-wiki/gemwiki.py`, keep them in sync). Alignment went
  70 all-`UNPARSED` → **99 records** (69 `SHEET_SUSPECT` / 24 `WIKI_UPDATE` /
  6 `WIKI_STALE_VS_STAGED`) and the harvest 0 → 63/63 pages. **68 of the 69 `SHEET_SUSPECT` are
  one question**, blank `Operator` — the GGIT norm (1,464/6,462 filled tracker-wide), so it is
  one bulk decision, not 68 tasks. Five escalations open. Still-open leads: the SSGC register
  (their TPA capacity declaration is not one) and the newer 03/2023 SNGPL transmission map.
  `docs/country_notes/pakistan.md`.
- **Iraq gas** — **full pass re-run 2026-07-28, rebuilt 2026-07-29** (refs sweep · cancelled review ·
  redundancy clusters · GulfPub + OSM recon · wiki alignment · route integrity · ref-gap re-pass · Leg-3),
  superseding the 2026-07-05 packet and the 2026-07-07 ASB ref-harvest, both folded in.
  **FOUR files to work, not two** (Libya's shape): `pipelines_batch_20260729_1104_ET_iraq-gas_handoff-actions.xlsx`
  (100 open decisions · 9 status changes · 265 backend paste units · 114 wiki updates ·
  36 route suggestions · 171 open flags) + its `-evidence` companion + the two **standalone recon
  workbooks** (`…_1104_ET_iraq-gas_reconciliation-{gulfpub,osm}.xlsx`), which the packet no longer
  subsumes — its `Gas_GulfPubActions`/`Gas_OSMActions` tabs are retired (`recon_actions=0`; see §2).
  Two reasons for the 07-29 rebuild: the GGIT gas tab was **re-sorted to ProjectID order** between the
  07-28 and 07-29 pulls (4,262 of 4,370 rows moved → every 07-28 `SheetRow` locator was wrong; 312
  re-derived, 430 verified 0-mismatched), and the retired GulfPub tab was built from the pre-fix
  miles-as-km run. The earlier OSM null (0 overlaps from 52 features) was a matcher failure, not a
  coverage finding. **Thirteen escalations open** — the structural ones
  are the ASB length mi→km defect (19 rows, two families with two *different* one-cell fixes),
  CapacityUnits on 3 rows, P6824 as a diesel line misfiled in GGIT, and the ASB-provenance ruling
  that **withdrew 12 of 16** of our own earlier duplicate/existence flags. **Three retractions —
  do not act on the older findings:** P4067 is *not* a misfiled crude line (stays in GGIT),
  "status stale forward" on P7435/P6826 is wrong (GEM was right), and P6007 is not a phantom.
  The earlier 37.5% status-change rate that tripped the >30% gate does not recur — 9 status
  changes across the country this pass. `docs/country_notes/iraq.md`.
- **Iran gas** — full packet staged 2026-07-05 (+ re-pass 2026-07-07, 35 refs).
  62.5% in-dev change rate (gate tripped); class-wide Owner NIOC→NIGC/IGTC fix on
  ~27 operating rows. `docs/country_notes/iran.md`.
- **Saudi gas** — full packet staged 2026-07-08 (discovery 2026-07-13), **partially applied**
  and **rebuilt 2026-07-28** as `pipelines_batch_20260728_1731_ET_saudi-arabia-gas_{annual-indev,
  deepsweep}.xlsx` (the 07-08 originals are in `archive/`). In-dev clean (22/22 confirm);
  hinges on the P1897–P1925 class decision (§4). `docs/country_notes/saudi-arabia.md`.
- **Egypt gas** — in-dev 2026-07-09 + operating deep sweep 2026-07-13 + discovery
  2026-07-15 (4 new rows / 3 monitor) + QC packet 2026-07-15. No escalation gate.
  All assembled into ONE two-file handoff packet, **rebuilt 2026-07-28** as
  `pipelines_batch_20260728_1731_ET_egypt-gas_handoff-{actions,evidence}.xlsx` (supersedes the
  07-16 pairs, now in `archive/`) — work from ACTIONS, not the four per-leg workbooks. Apply the
  Nitzana items (P3620/P7864 duplicate + discovery new-row Egyptian side) as one linked
  decision. Partially applied already (16/284 ref units live). `docs/country_notes/egypt.md`.
- **Israel gas: INGL/TMNG-map ground-truth batch** (2026-07-23) — 2 new discovery rows
  (P8001 Mari-B–Ashdod, P8003 Karish–Tanin FPSO), 5 validation candidate edits
  (P0462/P0479/P5276/P7604/P7606, none auto-applied), 5 route candidates (P7602/P7603/
  P0480/P8003 QC-pass, **P2197 QC-fail** documented). Deliverables:
  `pipelines_batch_20260723_1606_ET_israel-gas_discovery.xlsx` (+ P8001/P8003 wiki texts)
  and `…_1105_ET_israel-gas_route-creation.xlsx` (gitignored; predates the P8003 retrace —
  regenerate from the updated staged state before use). P8003 re-traced 2026-07-23 through the
  map's legend point-anchors (Tanin ⊕ → Karish ⊕ FPSO → Dor ○ OOAT; ~129 km incl. a
  future Tanin field-tieback leg) — see `route-creation-tmng-map/legend.md`. Open:
  Ashdod-vs-Ashkelon landfall (P8001 geometry deferred), Karish gem.wiki duplicate check,
  P8003 extent (full drawn vs operating-only trim), P0462 diameter needs a 2nd source.
  `docs/country_notes/israel.md`; `batches/israel-gas/staging/{discovery,validation}-tmng-map/`.
- **Libya gas: full pass** (2026-07-28) — operating ref sweep (30 rows) + cancelled-status
  review (P1728/P3985, both statuses failed review) + a 7-cluster redundancy pass +
  GulfPub and OSM reconciliations + handoff packet. GulfPub: 129 records at
  `--commodity both`, 25 additions (under the escalation gate). OSM: coverage null
  result for Libya, but it exposed three engine defects now fixed in `match.py` /
  `reconcile.py` / `route_compare.py` that affect every source. Three structural
  escalations are open (§4), plus a fourth found late in the pass: 14 lengths carry a
  spurious ASB miles→km conversion. Deliverable:
  `pipelines_batch_20260728_1235_ET_libya-gas_handoff-{actions,evidence}.xlsx` (work
  from ACTIONS; its README's `ESCALATIONS` row lists all five rulings needed).
  `docs/country_notes/libya.md`;
  `batches/libya-gas/staging/{ref-sweep-operating,cancelled-review,redundancy,recon-gulfpub-20260728,recon-osm-20260728,qc}/`.
- **US oil: Delaware Express** (P7995/P0354, researched 2026-06-12) and
  **Permian Express I–IV** (P0113/P2581/P2660/P2661, researched 2026-06-11) —
  `batches/united-states-oil/staging/update-{delaware,permian}-express/staged_updates.json`.
- **Saudi oil ref-sweep 10-row batch** (108 units: 67 REFS_ADDED / 25 DEAD_LINK /
  10 REVERIFIED / 6 UNRESOLVED) — `batches/saudi-arabia-oil/staging/ref-sweep-10row/`.

## 4. Decisions needed from Baird

- **Route three-way sync drift — 26 rows, none of them ours (2026-07-31).** The new
  standing audit `scripts/audit_route_sync.py` found `RouteType`/`RouteAccuracy`/routes-repo
  disagreements outside our batches. Two are urgent: **P7274 Longhorn Oil (US)** claims
  `Mapped` + `high` over an *empty* repo placeholder, and **P5970 BC Gas (Canada)** carries
  geometry **39.8×** its sheet length (near-certainly another pipeline's trace). ~12 more are
  mechanical `RouteType` flips; the rest split into route-correctness conflicts (incl. the
  Algerian LPG cluster P7297–P7300, three of four failing the ratio gate) and two repo-side
  bugs (P2041's geojson filed under gas while its row is on the oil tab — and P2041 exists on
  BOTH tabs). Per-row proposals, nothing written:
  `notes/review-2026-07-31-route-sync-drift-other-rows.md`.
- **P1897–P1925 (Saudi gas, 29 rows):** the 2026-06-19 escalation memo
  (`notes/escalation-2026-06-19-saudi-gas-opec-block.md`) requested a class-level
  decision (provenance of the 2022 GIS/km-post family, disposition of synthetic rows,
  dup-merge approval, re-citation) and was never answered; the identical question
  resurfaced in the 2026-07-08 packet. One decision closes both.
- **Libya cluster A (6 gas rows):** does P0483 "Libya Coastal Gas Pipeline" aggregate
  its own member segments P1862/P1863/P1864/P1865 (+ P1789)? Either delete the members
  or move P0483 to a network-route designation — remembering `n/a` is **not** a valid
  `Status`; aggregates take a blank Status + a `PipelineNetworkGrouping` label.
  `batches/libya-gas/staging/redundancy/`.
- **Three condensate lines in the GAS tracker (Libya):** P6705 and P6713 are already
  carried by GOIT (P0606, P6457) so they should be **deleted**, not moved; P6709 has no
  GOIT counterpart so it should be **moved**. Same defect, three different actions —
  needs one ruling. `batches/libya-gas/staging/redundancy/`.
- **`scm/y` / `scm/yr` zero-capacity class defect (8 rows: 4 Libya, 4 Algeria):** the
  OPEC ASB "(1,000 scm/yr)" multiplier was dropped at ingest and `scm/yr` is not a unit
  the `CapacityBcm/y` conversion recognises. ×1000 fits Libya's four and does **not**
  fit Algeria's, so no blanket fix.
  `notes/escalation-2026-07-28-scm-capacity-units.md`.
- **ASB length mi→km defect — now TWO countries, 33 rows: 14 Libya + 19 Iraq.** ASB Table
  4.10/9.9's length column is headed "miles" but those countries' blocks are tabulated in
  **kilometres** — the ingest converted anyway. Same table and same ingest as the `scm` defect
  above, different column, different fix. **The Libya memo's original "scope is Libya only,
  the Qatar/Iraq/Saudi blocks *are* miles" claim is superseded** — the Iraq gas pass
  (2026-07-28) found 19 Iraq rows with the same defect, arbitrated 6–0 by route geometry. The
  Qatar, Saudi and UAE controls *are* miles and their conversions stay correct, so the ingest is
  not broken — but "Libya only" is dead as a scope claim, and the remaining ASB countries should
  be tested the same way (take a row whose real length is independently known and see which
  reading it matches). Iraq needs TWO different one-cell fixes (13 rows fix the number;
  6 rows fix only the unit label). Fixing it should also clear most of both countries'
  route-integrity flags. `notes/escalation-2026-07-28-asb-libya-length-units.md` +
  `notes/escalation-2026-07-28-asb-iraq-length-units.md`.
- ~~**GulfPub gas `Length` is MILES, manifest says km.**~~ **FIXED AND RE-RUN 2026-07-29** —
  manifest flipped to `mi`, `units.length_units_by_country: {Canada: km}` added to the schema
  and the engine (Canada is the only country in the file whose block is really km), and all
  five affected countries (Egypt, Libya, Iraq, Saudi Arabia, Iran) re-run into
  `staging/recon-gulfpub-20260729/` with rebuilt `…_reconciliation-gulfpub.xlsx` at
  `20260729_0941_ET`. Display-only defect: `match.py` scores length on `geodesic_km`, so no
  match was ever mis-scored (Egypt re-run: `length_km` changed on 52/52 overlaps, `s_length`
  on 0, counts identical). Any gas recon workbook stamped before that time has `Ref Length
  (km)` ~38% short. `notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`.
- **GGIT small-diameter inclusion threshold:** GulfPub's Libya run surfaced 6–8in field
  gathering laterals, below the tracker-wide 12in 5th-percentile diameter, but GGIT does
  already carry 34 gathering rows globally. A one-time scope ruling stops this being
  re-litigated at every scrape. `batches/libya-gas/staging/recon-gulfpub-20260728/staged_addition_scope.json`.
- **Roster `applied` dates:** confirm whether the Iraq/Iran packets were actually
  applied to the live Sheet, and record dates in `campaigns/ggit-2026/roster.csv`.
