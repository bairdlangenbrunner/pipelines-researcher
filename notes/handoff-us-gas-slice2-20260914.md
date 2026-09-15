# HANDOFF — US gas campaign, slice 2 (paste this into a new session)

You are resuming the **US gas slice-2 deep sweep** in
`/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher`.
Read this whole file before acting. Do not re-derive it from the transcript.

## 1. Scope and state

Slice 2 = 296 US gas rows, swept with `--status-review` in 7 batches (A1-A7), one
staging dir each under `batches/united-states-gas/staging/`:

| Batch | Staging dir | Rows | State |
|---|---|---|---|
| A1 Gulf in-dev | `deepsweep-s2-gulf-indev` | 44 | shards done; committed |
| A2 Gulf/SE operating | `deepsweep-s2-gulf-se-operating` | 41 | shards done; committed; owner concerns + re-merge owed |
| A3 Texas in-dev | `deepsweep-s2-tx-indev` | 40 | shards done; owner concerns + re-merge owed |
| A4 TX/Mid-Con operating | `deepsweep-s2-tx-midcon-operating` | 41 | shards done; P3184 patched -> re-merge owed |
| A5 Appalachian in-dev | `deepsweep-s2-appalachian-indev` | 46 | **35/46 shards**; 11 rows unresearched |
| A6 Northeast/Alaska | `deepsweep-s2-northeast-alaska` | 42 | not started (worklist built) |
| A7 West | `deepsweep-s2-west` | 42 | not started (worklist built) |

**A5 rows still owed (no shard):** P4450, P7108, P7794, P7800, P7801, P7806,
P7813, P7825, P7827, P7829, P7999. Their agents died on a spend limit 2026-09-14;
P4070, P5990 and P6008 finished just before it and pass coverage.

Slice 1 (batches 1-5) is staged, not applied, and **done** - do not rework it.

## 2. Non-negotiable rules

- **Oil is out of scope for this whole cycle.** Never fold it in, never propose it.
- **Never cite GEM** (gem.wiki, globalenergymonitor.org) in any ref or note.
- **Never fabricate a URL.** Every URL goes through `scripts/url_verifier.py --name`.
- **Banned hosts:** abarrelfull (.wikidot.com/.co.uk), theodora.com, yingdodo.com.
- **Never cite** the undated `EIA-NaturalGasPipelineProjects.xlsx` or the `data.php`
  navigation page. Cite the dated release + sheet name + Excel row in the note.
- `Status = "N/A"` means do not research. Read tracker CSVs with
  `keep_default_na=False, na_values=[]`.
- **Rule 4(e):** every MISSING_REF unit ends REFS_ADDED or UNRESOLVED-with-notes.
  UNRESOLVED means *nothing was found* - never "something slightly different was
  found", never "not looked for".
- **Never write the live Google Sheet or the routes repo** without explicit
  per-edit authorization from Baird. Approval never carries over.
- **Commits:** all lowercase, succinct, no attribution/co-author lines. Commit only
  your own hunks - another session holds uncommitted edits in CLAUDE.md,
  batches/INDEX.md, docs/country_notes/china.md, docs/reference/*,
  docs/research_backlog.md, docs/sops/sweep.md, the scripts `sweep_gates.py`,
  `check_shard_coverage.py`, `harvest_sentinel_findings.py`, `merge_qc.py`,
  `url_verifier.py`, and the Jiangxi staging. **Never `git add` those wholesale, and
  do not edit those scripts** - document new rules in the batch `ADDENDUM.md` instead.
- Only write to repos Baird created.

## 3. THE EIA OPERATOR/OWNER CORRECTION (do this first)

**Baird's ruling, 2026-09-14:** EIA's `Pipeline Operator Name` column **is a valid
`Owner` ref** - GEM uses operator and owner interchangeably - **for Owner1 only**.
Owner2+ and equity percentages still need their own source (parent 10-K, FERC order).
EIA remains ONE origin: EIA alone = `medium`; `high` needs a second independent host.

A prior session had ruled the opposite ("EIA has no ownership column, so it can never
be an Owner ref"), rejected 22 EIA-only Owner units, and re-sourced them from SEC
filings on an expensive model. That rule was wrong. `ADDENDUM.md` (all four copies)
and the project memory are already corrected - **read
`batches/united-states-gas/staging/deepsweep-s2-*/ADDENDUM.md` rules 2 and 5** before
dispatching anything, and make sure every row prompt still points at that ADDENDUM.

### Revalidation scope (already measured - do not re-scan blindly)

Across all US gas shards: 76 Owner units already carry an eia.gov ref (**now valid at
medium - no action**), 42 Owner units are UNRESOLVED. Of those, only these need work:

**Stage the EIA ref (sheet Owner1 matches EIA operator):**
- `P6008` (appalachian-indev) - Empire Pipeline; EIA operators "Empire Pipeline" /
  "National Fuel Gas Supply Corp"
- `P0245` (tx-indev) - Rio Bravo Pipeline Co LLC; EIA "Rio Bravo Pipeline Company"
- `P2538` (appalachian-indev) - sheet "Transco" vs EIA "Transcontinental Gas Pipeline"
  (partial - confirm the entity, then stage)

**Sheet Owner1 is BLANK and EIA can fill it** (a FILL, `class_out="REFS_ADDED"`):
- `P4448` (gulf-se-operating) - EIA operator "Columbia Gas Transmission"
- `P5417` (gulf-se-operating) - EIA "Momentum" / "Momentum Midstream"
- `P6900` (tx-midcon-operating) - check candidates before filling
- `P3663` (gulf-indev) - ownership genuinely ambiguous; check before filling

**EIA operator DIFFERS from sheet Owner1 -> a concern, never a ref** (leave
UNRESOLVED, keep/refresh the validity concern): P3200 (Transco vs Virginia Natural
Gas - also the P3200/P5990 duplicate question), P5967 and P5974 (Boardwalk vs Gulf
South), P0319 (Whistler vs NextEra/WhiteWater), P0378 (Gulf Coast Express vs
DCP/Targa/Kinder Morgan).

The remaining UNRESOLVED Owner units have **no strong EIA candidate** and are correct
as they stand (mostly stale-owner findings, e.g. P0159 EnLink->ONEOK).

Useful tooling: `batches/united-states-gas/staging/eia-crosswalk-20260910/eia_crosswalk.json`
(`rows[<PID>].candidates[]`, each with `tier`, `operator`, `cite_url`, `sheet`,
`excel_row`), and `sources/eia_pipeline_projects/data/eia_projects_long.csv`
(`release, sheet, excel_row` for every row of all 29 releases, May 2018 - Aug 2026,
raw files under `sources/eia_pipeline_projects/raw/`).

**Owner concerns still owed on A2/A3/A4 shards** (these survive the correction - they
are about Owner2+/percentages, not Owner1): P0287 (KMI 37.5% of NGPL), P0302 (KMI
27.74% of PHP, circular sourcing), P2582 (KMI + BCP, pre-2014 KMP entity), P3882 and
P2498 (MPLX 10%); plus naming flags on P7840 and P3589.

**Do NOT build any gate that flags "Owner refs that are all eia.gov"** - that check
came from the wrong rule.

## 4. Immediate task list, in order

1. ~~**Fix P3189**~~ - DONE.
2. ~~**Apply section 3**~~ (the EIA Owner work above) - DONE.
3. ~~**Research the 11 remaining A5 rows**~~ - DONE; A5 merged and delivered.
4. ~~**Adjudicate the two duplicate pairs**~~ - DONE. (Shards for all four exist:)
   - `P5405` <-> `P4070` - North Brooklyn Pipeline; P4070 carries the geometry;
     phases 1-4 built and operating, only the final phase cancelled in 2023.
   - `P3200` <-> `P5990` - VNG Interconnect; EIA has exactly one (Aug 2026 row 1143,
     10 mi, 245 MMcf/d) matching P3200, which also has a km-vs-mi unit error.
5. ~~**Dispatch A6 (northeast-alaska, 42) and A7 (west, 42)**~~ - DONE, both merged
   and delivered.
6. **Merge + gates + workbooks** (section 5), then rebuild the stale A1/A2/A3
   deliverables. **A5/A6/A7 delivered. A1-A4 repaired, coverage-clean, audit-clean
   and merged 2026-09-15 (see below); the remaining chain per batch is
   `harvest_sentinel_findings` -> `check_shard_coverage --all` -> `sweep_gates` ->
   `build_ref_workbook` -> `recalc`. A4 (tx-midcon-operating) has never had a
   deliverable; A1/A2/A3 deliverables are stale.**
7. ~~**Two slice-wide sweeps:**~~ - BOTH CLOSED. rows marked "not in EIA" that actually are in EIA (the
   Willis Lateral defect - one agent claimed absence for a project present in 27
   releases); and status flips to operating/proposed that left CancelledYear,
   ShelvedYear or ShelvedCancelledType populated.
8. **Update** the Progress paragraph in `docs/country_notes/united-states.md`, then
   commit your own hunks only (lowercase message, no attribution).

## 5. Merge / delivery recipe

Re-merge first: `cp <dir>/staged_resolutions.prior.json <dir>/staged_resolutions.json`
(the "NEWER than .prior.json" WARN afterwards is expected). Then, per staging dir:

```
python scripts/check_shard_coverage.py --staging <dir> --all
python scripts/merge_deepsweep_shards.py --staging <dir>
python scripts/backfill_name_found.py --staging <dir> --shards store \
    --csv data/GGIT_gas_snapshot_20260914.csv --apply
python scripts/harvest_sentinel_findings.py --staging <dir>
python scripts/check_shard_coverage.py --staging <dir> --all
python scripts/sweep_gates.py --staging <dir>
python scripts/build_ref_workbook.py --staging <dir>/ --output <deliverable>.xlsx
python scripts/recalc.py <deliverable>.xlsx
```

Stamp deliverables with `TZ=America/New_York date "+%Y%m%d_%H%M_ET"`.
Gates **E, F, I', J and L must be 0** at delivery; gate I should also be resolved.
A2/A3/A4 all need a re-merge (owner concerns + the P3184 patch).

### A6 (northeast-alaska) merged and delivered — 2026-09-15

`pipelines_batch_20260915_0629_ET_united-states-gas_deepsweep-s2-northeast-alaska.xlsx`
(10 sheets, `recalc.py` clean, no error cells). Merge: 42/42 shards, 0 missing; 341 ref-only
folds, 420 kept ref records, 309 new fills, 103 validity, 39 status reviews. Verdicts
`{confirmed (caveat): 53, concern: 44, confirmed: 2, change: 4}`; status verdicts
`{confirm: 37, stale: 1, unclear: 1}`. There is no `.prior.json` for this dir, so the re-merge
step in the recipe above does not apply to it. `harvest_sentinel_findings.py` returned 0.

**Gate state at delivery — the required five are all 0** (E orphan refs 0, F banned/GEM 0,
I' relevance-unchecked 0, J owed blanks 0, L uncited values never worked 0). What the advisory
gates say, and why none of it blocks:

- **Gate B (69) is a convention artifact, not a defect — do not "fix" it.** Every one of the 69
  is a `__VALIDITY__` record reported as `0 verified ref(s), hosts=[]`. Validity records carry
  `proposed_refs` but no `verifications[]` by repo convention, and gate B counts only
  verifications, so it reads every validity record as zero-evidence regardless of what it cites.
  Spot-checked against the store: e.g. P0144's validity record carries three distinct publishers
  (a Wayback capture of a FERC PDF, offshore-technology.com, commonwealthmagazine.org). The
  orchestrator audit, which counts validity tiers over `proposed_refs`, returned **0 findings across
  all 42 shards**. Gate B and that audit disagree by construction; the audit is the one that is
  right for validity records.
- **Gate I (17 relevance findings): 22 of the 25 gate-I-shaped records are CARRIED sheet refs**,
  i.e. citations the sheet already had, kept because the sweep honestly found nothing better
  (their replacement records came back `UNRESOLVED`). Only **3 are ours** — P4456 FuelSource,
  P6534 Operator, P6534 Owner — and all three are staged at `tier: low`, which is the correct
  handling for a source that supports the value without naming the segment. No repair owed.
- **Two carried-ref defects surfaced by gate I that are worth a tracker-wide follow-up, not a
  fix here:**
  - `https://www.eia.gov/naturalgas/data.php#pipelines` — the banned EIA navigation page — is the
    carried `[ref]` on **7 cells across 6 rows** (P0293 Shelved, P0309 Start + Location, P2526
    Start, P4456 Start, P5545 PipelineType + Length). The ban is on what WE cite, and none of
    these is staged by us, so gate F is legitimately 0; but they are live citations on the sheet.
  - The bare `https://www.npms.phmsa.dot.gov/` root is the carried `[ref]` on **4 cells** (P7450
    Location, P7455 Fuel, P7463 PipelineType, P7465 Location) — the same follow-up already logged
    for the rest of the tracker.
  - **P7455 `Owner [ref]` carries `archive.gov.krd/mnr/...first-gas-arrives-at-duhok-power-station`**
    — a Kurdistan Regional Government press release about a power station in Iraq, sitting on a US
    row. Add this to the P7455 adjudication group (existence + duplicate + the Fuel -> Oil ruling):
    that ref is simply wrong and should come off.
- Gate A (2): P0300 sourced only on `fairbankspipelinecompany.com`, P0308 only on
  `pinelandsalliance.org`. Gate K (120): single-verified-ref REFS_ADDED, the usual 2-per-point
  shortfall. Both advisory and expected on rows with thin public records.
- Dominant document: the EIA Aug2026 release carries 168 units — expected for a US gas batch, and
  the reason the one-origin rule for EIA matters.

### A1-A4 repaired and merged, and DELIVERED — 2026-09-15

All four A-batches (`gulf-indev` 44, `gulf-se-operating` 41, `tx-indev` 40,
`tx-midcon-operating` 41) now report **0 coverage gaps, 0 unmergeable records, 0 silent
UNRESOLVED**, and `audit_shard.py` returns **0 findings** on every shard. Merge
histograms:

| batch | shards | folds | kept refs | fills | validity | status | validity verdicts | status verdicts |
|---|---|---|---|---|---|---|---|---|
| gulf-indev | 44/44 | 373 | 448 | 305 | 101 | 38 | caveat 51 / concern 50 | change 23, confirm 13, stale 2 |
| gulf-se-operating | 41/41 | 332 | 386 | 279 | 59 | 35 | caveat 36 / concern 23 | confirm 27, change 6, stale 2 |
| tx-indev | 40/40 | 405 | 432 | 217 | 41 | 40 | caveat 24 / concern 17 | change 20, confirm 13, stale 5, unclear 2 |
| tx-midcon-operating | 41/41 | 321 | 376 | 289 | 52 | 41 | caveat 33 / concern 19 | confirm 29, unclear 6, change 5, stale 1 |

Open concern types: gulf-indev `{spec 37, attribution 9, duplicate 3, classification 1}`;
gulf-se-operating `{spec 12, attribution 10, classification 1}`; tx-indev `{spec 14,
attribution 2, existence 1}`; tx-midcon-operating `{spec 11, attribution 6,
classification 1, existence 1}`.

**Delivered 2026-09-15 at stamp `20260915_1116_ET`** — all four workbooks, 10 sheets each,
`recalc.py` clean, no error cells. The superseded A1/A2/A3 files (`_1712_ET`, `_0952_ET`,
`_1022_ET`) were moved to `batches/united-states-gas/archive/`. **Slice 2 is now 7/7
delivered**, staged not applied.

| batch | fills | refs added | reverified | dead link | unresolved | validity | status |
|---|---|---|---|---|---|---|---|
| gulf-indev | 305 | 356 | 34 | 22 | 36 | 101 | 38 |
| gulf-se-operating | 279 | 319 | 11 | 6 | 50 | 59 | 35 |
| tx-indev | 217 | 342 | 12 | 9 | 69 | 41 | 40 |
| tx-midcon-operating | 289 | 283 | 19 | 7 | 67 | 52 | 41 |

**Gate state — the required five (E, F, I', J, L) are 0 on all four.** `harvest_sentinel_findings`
returned 0 for each. Advisory gates and why none blocks: A (0/6/9/11), B (76/27/18/13 — the
`__VALIDITY__` convention artifact, do not "fix"), C (168/72/54/9 dominant-document, the EIA
release), D (84/29/19/14), K (97/255/328/344 — the 2-per-data-point shortfall). **Gate I fires
12 times total** (gulf-se-operating 1, tx-indev 1, tx-midcon-operating 10); classified by hand:
three are **carried sheet refs**, not ours — P2564 `Location [ref]` carries the banned
`eia.gov/naturalgas/data.php#pipelines` (another instance for the tracker-wide follow-up; gate F
is legitimately 0 because we did not stage it) and P3185 `Location [ref]` carries an Enbridge
Three-Rivers PDF. The nine that are ours (P0355 Construction, P3294 Cancelled, P0163 x5,
P3184 Fuel, P3184/P3185 FuelSource) are **all staged at `tier: low`** — the correct handling for
a source that supports the value without naming the segment. No repair owed.

Note: `build_ref_workbook.py` re-derives SheetRow locators against `meta.scope.csv`, which for
every slice-2 batch is `GGIT_gas_snapshot_20260910.csv` (the scoping snapshot), not the newer
20260914 pull. That is by design and keeps all seven batches' locators mutually consistent —
1/31/39/53 stale locators were re-derived across A1-A4.

**What was repaired, and why it matters for every future batch.** 41 finished records
were silently unmergeable — `merge_qc.verified_refs` keeps a proposed ref only when a
verification says `ok` AND `contains_value` AND its `url` is byte-identical to the
`proposed_refs` entry, so any of those three failing strips the record's refs and
re-keys it `UNRESOLVED`. Breakdown of the repair: **26** verifications were missing the
`contains_value` key outright (a missing key reads as false); **4** verified a URL that
was never added to `proposed_refs`; **1** pointed at the bare origin while the ref was
staged as a Wayback capture, and **3** at a different EIA release vintage than the one
staged; **11** were never actually supported and are now `UNRESOLVED`-with-notes — a
source that contradicts the value (PGJ 255 vs a recorded 225.00), measures a different
scope (Sabal Trail system total vs one phase), or supports it only by inference from an
absence (EIA's blank `miles` read as "adds zero pipe") is "nothing found" under rule
4(e). A prior pass had already done 140 UNRESOLVED-hygiene fixes and 65 tier fixes on
the same four batches.

Nine **validity/status vocabulary** variances were also repaired (the recurring defect
class of this campaign — the merge's verdict histograms are where it shows): validity
`verdict` is only `confirmed (caveat)`/`concern`, status_review `verdict` is only
`confirm`/`change`/`stale`/`unclear`, and `concern_type` is only
existence/duplicate/classification/attribution/spec/none. Seen and fixed: `change`,
`confirm`, `confirmed` as validity verdicts; `confirmed (caveat)` as a status verdict;
`validity`, `stale`, `misattribution` as concern_types. Plus one **`contested`-prose**
defect (P2564; P7814 the same shape) — `contested` holds candidate VALUES keyed by real
backend columns, and prose in it reaches the paste surface as if it were the proposed
cell content.

Every repaired record carries an `[ORCHESTRATOR AUDIT 2026-09-15]` note recording the
original value and stating that the finding itself is unchanged.

**All seven slice-2 `ADDENDUM.md` files were synced to one canonical 461-line version**
(2026-09-15) — the five older 266-line copies were stale. New sections: the
`contains_value`/URL-identity merge-read rule; the two verdict vocabularies; "a ref that
contradicts the value, or measures something else, is not a ref"; a third reproduced
blocked-fetch claim (BusinessWire 403 recovered via the Wayback **path** form — the
availability API 429s long before the path form does); and deferred-hardening items 8-11
including the `contested`-prose rule and the xata.sh caveat below.

**Two things a reviewer should know about specific records:**

- `gulf-indev/P7769` cites `https://us-east-1.storage.xata.sh/4oj4ue167p5a1anou7nvrf7u80`
  for FERC order 183 FERC ¶61,049, because ferc.gov 403s. The PDF is live and carries the
  real bytes, but an opaque object-store mirror names no publisher and will rot — the
  researcher should substitute the FERC eLibrary accession, and must never fabricate one.
- `tx-indev/P3969` is keyed `spec`, but the record also carries an **existence** signal:
  no independent mention of a distinct "Texas LNG Lateral Extension" segment appears in
  any EIA vintage, FERC docket, Enbridge release or regulator filing. Flagged for the
  reviewer rather than re-keyed.

Also confirmed here: `backfill_name_found.py --shards` accepts only
`ref_shards` | `rows` | `store` (`only` is not a value), and the
`EIA-NaturalGasPipelineProjects_Aug2026.xlsx` underscore form 404s — August 2026 is the
one release with no underscore (`...ProjectsAug2026.xlsx`).

### Shard schema traps
- A fill's `values` is a **dict keyed by column**; `validity` is a **LIST**;
  `contested` holds **values, not prose**; clearing a cell is `{"Col": ""}`.
- A status flip to operating/proposed must also clear `CancelledYear`, `ShelvedYear`
  and `ShelvedCancelledType`.
- `check_shard_coverage.py` accepts `class_out` in
  {REFS_ADDED, REVERIFIED, UNRESOLVED, DEAD_LINK}; sourced = {REFS_ADDED, REVERIFIED,
  CONFIRMED}.
- `independence_qc` in `scripts/merge_qc.py:104` only DEMOTES (fewer than 2 distinct
  hosts: high -> medium), so set tiers honestly by hand - two hosts carrying one wire
  story are still one origin.

## 6. Spend, models, dispatch

Baird's standing instruction: **fan out on token-efficient models**; the orchestrator
picks per task; judgment-heavy work stays in the main loop. Measured this session:

- sonnet row agent: ~5.8M tokens, ~47k output, ~18 min. haiku: ~2.1M, ~15k, ~3 min.
- Rows per spend-limit window: ~30 on sonnet-heavy work, 60+ on haiku-heavy.
- Nothing known up front predicts a row's cost well (3.5M-17.3M range). Heavily
  covered projects with conflicting figures (LNG feeders, big trunks with ownership
  history) cost the most; single-project expansions with a FERC docket the least.
- Haiku's failures were concentrated in **judgment** work: citing search/navigation
  pages as documents, calling SEC EDGAR "inaccessible" (it 403s undeclared clients
  and answers with an identifying User-Agent), and one flat-wrong owner.

Recommended split (Baird has not yet chosen): mechanical EIA ref staging by
**script, no model**; narrow yes/no lookups on **haiku**; ownership, status flips,
duplicates and merge calls on **sonnet or in the main loop**. Cap ~20 concurrent
agents, keep 10-15 in flight. **On a session-limit failure, sleep in the background
until the reset and resume without waiting for Baird** (his standing rule).

## 7. Open findings awaiting merge review

- `P4446` - capacity likely 10x too high: sheet + EIA 350 MMcf/d vs two FERC EIS
  notices ~35,000 Dth/d (~35 MMcf/d); staged 35 at high. proposed -> operating,
  StartYear1 2024. Owner stays **Columbia Gas Transmission LLC** (FERC CP21-498,
  interstate).
- `P4452` - capacity 250 vs EIA 240; ShelvedCancelledType=inferred; died at FERC
  pre-filing PF21-3.
- `P4451` - proposed -> operating, StartYear1 2023 (in service 2023-02-15, MPSC
  U-21525 PFD + EIA). **P4450 needs the same correction** when researched.
- `P4449` - proposed -> operating 2023; LengthKnown 0 (conversion of the existing Wet
  Header); cost $28M of a combined $56.47M across three facilities.
- `P6004` Chickahominy - shelved -> cancelled, type confirmed, CancelledYear 2022;
  fills Diameter 24, Owner/Operator Chickahominy Pipeline LLC.
- `P5601` NED/Northeast Energy Direct - EndState NY -> Massachusetts (Dracut);
  Diameter adds 30 alongside 36; ShelvedCancelledType=confirmed.
- `P4447` - 14 mi/24in (EIA) vs OPSB ~16 mi (12mi@24in + 4mi@16in); Pressure 720/190
  psig filled. Owner = **Columbia Gas of Ohio** (LDC, NiSource) - correct as staged.
- `P3184` Alliance - the 2018 open season failed; cancelled confirmed, owner really
  Pembina 50% / Enbridge 50%, endpoints reversed, NOT a duplicate of P3185.
- `P3189` Marysville Connector - Owner = Columbia Gas of Ohio (NiSource Exhibit 21).

**Columbia family discriminator:** an OPSB / intrastate / blanket-certificate tie-in
means the LDC **Columbia Gas of Ohio** (NiSource). A FERC certificate docket means the
interstate **Columbia Gas Transmission LLC** (TC Energy; NiSource sold it in 2016, TC
sold 40% to GIP in 2023). **CP82-479 is TC Energy's blanket certificate** (EIA 2025-07
row 65), not an Ohio LDC docket.

### A6 (northeast-alaska) / A7 (west) findings — added as the batches returned

- **Equitrans cluster defect (P6895, P6896, P6897).** All three carried `Capacity =
  4,400 MMcf/d`, a system/portfolio total copied onto each row. Corrected per row to
  5,000 / 450 / 850 with reciprocal `cross_row_leads`. Treat as a systematic error
  class, not three coincidences — check for the same shape wherever sibling rows of one
  operator share a round capacity.
- **`P7455` Cook Inlet Gathering (CIGGS).** `Fuel` should be Oil (2018 gas→oil
  conversion, DNR); `Diameter = 21` is actually a LENGTH (real diameter conflicts, 16"
  vs 10"); `Owner1` read **"Kurdistan Government"** — cross-country data contamination —
  corrected to Hilcorp Alaska, LLC. The Fuel→Oil call needs Baird's ruling, since oil is
  out of scope for this cycle: the row may belong out of GGIT entirely.
- **`P7461` Tyonek vs `P7455`.** P7461 raises BOTH an existence concern (no Alaska source
  documents a single 50.71 mi Nikiski→Beluga "Tyonek Gas Pipeline"; the only
  DNR-registered "Tyonek" is a smaller 2018 segment) and a duplicate concern against
  P7455/CIGGS. Cross-row leads also point at P7454. **Adjudicate P7455 / P7461 / P7454 as
  a group at merge**, not row by row.
- **`P0309` Adelphia Gateway — four material corrections**, each on 2+ distinct
  publishers: `Capacity` 250 → 850 MMcf/d (the 250 was the as-filed single-segment
  addition, not the certificated total; FERC CP18-46 EA + NJR 10-K + EIA), `LengthKnown`
  50 → 93.30 mi (FERC EA + operator site; EIA's 4.75 mi is the new-construction
  component only), `StartYear1` 2023 → 2022, `StartPrefecture` Bucks → Northampton.
- **`P6534` Point Thomson.** Owner/Operator → **8 Star Alaska LLC** (Glenfarne 75% /
  AGDC 25%); FIDYear contested to blank; distinct component of, not a duplicate of,
  P0147. SegmentCost confidential per the JVA — genuinely UNRESOLVED.
- **`P7465` Alyeska fuel-gas line.** `Owner1 = Alyeska` is really the OPERATOR per
  Alyeska's own factbook; StartLocation "Kuparuk" conflicts with the sourced "Pump
  Station 1".
- **`P7463` Northstar Gas.** Alaska DNR and Petroleum News independently describe gas
  flowing shore → Northstar Island, the REVERSE of the recorded Start/End. DNR's own page
  also contradicts itself on diameter (10-inch prose vs 10.15 recorded).
- **`P7857` Great Basin 2024.** An EIA candidate row had been misattributed here; it
  belongs to **P7859**.
- **A bare `https://www.npms.phmsa.dot.gov/` is not a ref, tracker-wide.** It is the sole
  `current_ref` for **44 worklist units across 11 rows** in A6 alone (P7450, P7453-P7456,
  P7458, P7461-P7465). It returns HTTP 200 while stating nothing about any pipeline —
  effectively UNCITED, and worse than a dead link because the 200 makes it look checked.
  Rule now in both `ADDENDUM.md` files. **Worth a slice-wide / tracker-wide sweep** for
  the same URL outside slice 2.

**P3942 (Northern Lights 2021 Expansion) — recorded Length is 14x FERC's own facilities
list.** The row carries `LengthKnown = 21.60` mi, traced to EIA and unchanged since a
Dec-2019 pre-filing snapshot that predates the application. FERC's certificate order
(`ferc.gov/sites/default/files/2021-05/C-2.pdf`) itemizes every new/replaced segment of the
certificated project: a 0.80-mi extension of the 24-inch Willmar D branch line, a 0.63-mi
24-inch loop and a 0.08-mi 12-inch replacement — **1.51 mi total** (plus ~0.15 mi of
separately itemized abandonment). Staged as a sourced value at medium / not-independent (one
publisher) with a validity spec concern, because it disagrees with an equally single-origin
recorded figure. **Adjudicate at merge.**

*Orchestrator repair on that record:* the agent had keyed the FERC verification
`contains_value: false` on the reasoning that no verbatim `1.51` token appears in the
document — which would have made the merge strip the ref and silently downgrade a genuinely
sourced record to `UNRESOLVED`. Re-keyed to `true` with the arithmetic spelled out, per the
standing rule that a ref is not unsupported merely because the value is not a substring
(prose/unit equivalence). **This is a defect shape to watch for**: a source that states a
value as its itemized components still states the value.

**P7790 (Northwest Gas Pipeline) is the Kelso-Beaver Reliability Project**, FERC CP25-89 —
an acquisition-plus-compression project: Williams acquired the existing ~17-18 mi
Kelso-Beaver lateral from PGE / KB Pipeline / B-R Pipeline and built only a new compressor
station. **No new pipe.** So the row's `LengthKnown = 0` and blank `Diameter` are CORRECT,
not gaps — and EIA's 18-mi figure describes the acquired existing pipe, not new
construction. Do not "fix" those cells at merge. Confirmed distinct from all four sibling
"Northwest Gas Pipeline" rows (P0230 system, P2626 Trail West/N-MAX, P5101 Kalama Lateral,
P7812 Wild Trail). It filed one **cross_row_lead on P7812**: Williams' 2026-08 10-Q places
Wild Trail's corridor at Colorado → Wyoming/Colorado (White River Hub), not Utah as P7812's
row records, with matching 83 Mdth/d capacity. Passed to the P7812 agent to verify
independently; check for a reciprocal lead when that shard lands.

**P7812 (Wild Trail Project, FERC CP25-497-000)** is a compression-only expansion on
Northwest Pipeline — a new Daggett Compressor Station in Daggett County, UT, 82.955 MMcf/d
(the sheet's 83). `LengthKnown = 0` and blank `Diameter` are therefore CORRECT; do not
"fix" them at merge. It staged an Operator correction — the sheet's **"Northwest Pipeline
Co" is a stale legal name; the current entity is "Northwest Pipeline LLC"** (FERC docket
applicant name + Williams FY2025 10-K Exhibit 21) — with `contested = {"Operator":
"Northwest Pipeline LLC"}`, and filed the same lead against **P0230, P2626, P5101 and
P7790**. Worth an A7-wide check at merge rather than four separate adjudications. Its
`status_review` is `confirm` (Status stays `proposed`: FERC approval is a pre-construction
milestone with no GEM vocab bucket) with a recommended `FIDStatus = FID`. It did NOT
reproduce P7790's Colorado→Wyoming corridor lead — it read the FERC docket as siting the
work in Utah, and says Location = Utah/Utah is the construction site, not the broader
service corridor. **Adjudicate P7790 and P7812 together on that point**: the two agents
looked at different documents (10-Q portfolio narrative vs. docket) and neither cited the
other.

**P0230 is the genuine whole-system Northwest Pipeline row** (~3,900 mi, San Juan Basin →
Sumas WA), not a duplicate of its four sub-project siblings. Its finding: **`StartYear1 =
1965` is unconfirmed and probably wrong** — no source states it, and the likeliest origin is
a conflation with Williams' unrelated 1965 Great Lakes acquisition (Williams acquired
Northwest Pipeline itself in 1983; the physical system is a 1950s predecessor's). Staged as
a validity concern with `contested = {"StartYear1": ""}` and no fabricated replacement. It
also flags four NWP system expansions carried in the EIA Aug2026 release with **no matching
roster row** — Huntingdon Connector, Naughton Coal-to-Gas Conversion, Ryckman Creek Lateral
Loop, Stanfield South — as Discovery candidates, not A7 work.

**P7820 / P7821 (Atlantic Bridge) carry a mirror-image value swap.** P7820 is Phase I,
compression-only: its recorded `LengthKnown = 6.00` mi belongs to the sibling, so P7820
should be **0** and **P7821 should take 6.3 mi / 42 in**. P7821's `SegmentCost` $451.8M and
Start 2021/Jan are already correct. Staged as a spec concern on P7820 with a cross_row_lead
on P7821; **adjudicate the pair as a unit at merge.** Secondary open question recorded
there: Enbridge accounts for Atlantic Bridge in three phases, GEM in two rows.

**P2578's own dispatch prompt was wrong, and the agent caught it.** The auto-generated
comparison table in `prompts/P2578.md` matched the row against the wrong EIA sibling
("Northern Lights 2021", PF20-1/CP20-503 — which is P3942), so every cell rendered as
"differs". The correct match, present in the same candidates list, is **Northern Lights 2019
(CP18-534)**, which agrees exactly with all recorded values (18.8 mi, 24/36 in, 101.41
MMcf/d, $158.07M, in-service 2019). No sheet value needed changing. **Treat a prompt's
"differs" table as a candidate, never a finding** — and expect the same mis-match shape on
other serial-named clusters. P2578 and P2603 (Rochester, 12.3 mi) are two physically
distinct facilities filed under one shared docket; both agents reached that independently
and cited each other's facts back.

**Two dispatch prompts stated the MountainWest acquisition as 2024. It closed 2023-02-14** —
confirmed from both sides by two different registrants (Williams' FY2023/FY2025 10-Ks as
buyer, Southwest Gas Holdings as seller). P6898 and P6899 each corrected it independently.
No sheet column changes; the lead itself was the error.

**P3943 (Northern Lights 2023, CP22-138-000)** staged two spec concerns off the FERC
certificate order: `LengthKnown` 9.00 → **9.83** mi and `Diameter` "8,20,24,30,36" →
**"4,8,24,30,36"**. **P7785 (MountainWest Westbound Compression)** has an inbound lead from
both P6898 and P6899: Williams' FY2025 10-K says the Overthrust Westbound Compression
project was placed in service during 2025, so its `construction` status and blank
`StartYear1` are likely due a change — check what that shard staged before adjudicating.

**P2626 is the biggest A7 finding so far: its Owner is probably wrong.** The row is the
**Trail West / N-MAX** project — a proposed, never-built 106-mi / 30-in lateral from GTN
near Madras OR to Northwest Pipeline's Grants Pass Lateral near Molalla OR. The sheet
records `Owner1 = Williams Companies (100%)`, but two independently authored and dated
sources (Sightline 2019, Bark 2020) both describe the sponsor as **Trail West Pipeline, LLC
— a 50/50 JV of NW Natural Holdings and TC Energy**, with Williams/NWP named only as the
*interconnecting system*. That is exactly the failure mode where a row lands in a
name-cluster it doesn't belong to and inherits the cluster owner. Staged as a high-tier
attribution concern with a corrected Owner and a new Operator fill. Two more concerns on the
same row: `CancelledYear` **2023 → 2022** (EIA's 28-release history flips the project to
Cancelled/On Hold at the 2022-01 release and nothing supports 2023, not even the sheet's own
existing ref), and a `Capacity` conflict — sheet and EIA agree on 450 MMcf/d while two
independent sources state a 500 MMcf/d design capacity, left unadjudicated as a possible
incremental-vs-design scope difference (`contested = {"Capacity": "500.00"}`).

Its agent also reproduced the **`url_verifier.py` numeric-boundary false negative** from the
other side: `_contains()` uses `(?<![\d.,])<token>(?![\d.,])`, so a bare year token fails
when the page writes "late 2023." with a trailing period — the same shape as the documented
"1961," trailing-comma case. It worked around it with a longer expected substring and
correctly did **not** edit the shared script.

**P7782 / P7783 (Intensity Pipeline, ND) — the phase split is CORRECT, do not merge them.**
Both agents, working independently, reached the same ruling from the same primary record:
Intensity Infrastructure Partners / Rainbow Energy Center announced ONE 344-mile project built
in two physically distinct, sequential phases — Phase I Watford City -> Washburn (136 mi, 36 in,
1,100 MMcf/d) = P7782, Phase II Washburn -> Casselton (208 mi, 30 in, 430 MMcf/d) = P7783. They
interconnect at Washburn rather than overlapping; 136 + 208 = 344. Two separate open seasons were
run (Feb 2025 Phase I, Apr 2025 "Phase II Extension"), and the routes-repo geojsons are contiguous
and non-overlapping. **EIA carries the project as ONE row** (Aug2026 release, sheet `Natural Gas
Pipeline Projects`, Excel row 67) whose `Miles` is the 344-mile aggregate while its capacity and
diameter describe Phase I alone — an internal EIA inconsistency. At merge, do NOT "correct" P7782's
136 mi to 344 off that workbook; this is the aggregate-vs-segment case, and GEM's per-segment
modeling is the right one. Two further items on this pair: (a) **FIDStatus** — the 2026-01-06 joint
release advances **Phase I only** to FID ("executed precedent agreements ... sufficient to underpin
the decision to advance Phase I"), independently corroborated by EIA's status moving Announced ->
Approved with a notes field naming the same date; `FIDStatus = FID` is owed on P7782 and is NOT
owed on P7783. It is not a worklist unit on either row, so it needs a researcher to apply it.
(b) **StartMonth1 on P7782** may be stale — the Jan 2026 release says "early 2029" where the 2025
announcement said July 2029. No source states a replacement month, so nothing was proposed; flagged
only. Neither agent proposed a Status change: FID is a milestone, not evidence of construction.

**P7830 (Double E "Original Proposal") — a genuine Fuel = Oil row sitting in the gas tracker,
and a Location error copied forward.** This is the 2011 Energy Transfer / Enterprise Products
crude-oil JV (Cushing, OK -> the Gulf Coast) that collapsed in 2011 when Enterprise left for the
Wrangler/Enbridge deal; the pipe was never built. It is NOT a duplicate of P5727 ("Double E Red
Hills Lateral") — different commodity, different decade, different basin, and P5727 is a lateral of
the operating Double E **gas** pipeline (P0061). Two consequences for merge:
  - **This is the second Fuel -> Oil ruling owed this slice** (the first is P7455). Oil is out of
    scope for the whole cycle, so nothing was done in GOIT; the open question is whether GGIT keeps
    the row as project genealogy or drops it. **Park it with the P7455 ruling — do not decide it at
    merge.**
  - **Location is wrong on the sheet**: both start and end states read New Mexico, copied forward
    from the later gas project. The agent corrected StartState/Province to Oklahoma (Cushing) at
    high tier and left EndState/Province `contested: {"EndState/Province": ""}` — both sources say
    only "the Gulf Coast", which is not a state. Do not invent one at merge.
  - Eight units are UNRESOLVED (Construction, Start, Capacity, Pressure, Length, Diameter,
    FuelSource, SegmentCost). That is correct under rule 4(e), not an unfinished row: the specs
    trace to a 2011 ETP press release that is 403 direct with no Wayback capture.

**P7782 `validity[1]` repaired in place (orchestrator, 2026-09-15)** — it claimed `tier: high` /
`independent: true` with an EMPTY `proposed_refs`. Validity records carry no `verifications[]` by
repo convention, so the tier is counted over `proposed_refs` and an empty list means zero
publishers. Staged the three origins the note already rested on (EIA Aug2026 release, Pipeline &
Gas Journal 2025-06-26, Intensity's own JV release). **This is the fourth occurrence of this exact
defect in slice 2** — P7863, P5101, P7782, and one earlier. It is invisible to
`check_shard_coverage.py`; only the orchestrator audit catches it. Whoever dispatches next should
put it in the prompt explicitly: *a validity record's tier is counted over its `proposed_refs`;
`high` with an empty list is a contradiction.*

**P3171 (GTN XPress) — a real SegmentCost correction and an unresolved state conflict.**
The row is the FERC CP22-2 compression-only expansion of the GTN system, correctly scoped separate
from the system row P0231 (swept elsewhere). Two items for merge:
  - **SegmentCost 75,000,000 -> 335,000,000 (2023), `contested: {"SegmentCost": "335000000.00"}`.**
    The recorded $75M is the FERC-application-era estimate; EIA carried $75.1M only in its 2021-10
    and 2022-01 releases and has said $335M in every release from 2022-10 onward, and bendbulletin.com
    (2023-10-20, contemporaneous with the FERC order) says $335M too. The currently-cited
    canadianenergycentre.ca article reused the stale figure. Two origins agree on $335M — apply it.
  - **Kent Compressor Station's state is unsettled.** bendbulletin.com places Kent in Oregon (matching
    the sheet); missoulacurrent.com groups Kent with Starbuck "in Washington state". The Federal
    Register EIS notice was bot-blocked and could not settle it. Staged as
    `contested: {"EndState/Province": ""}` with no replacement asserted — correct. **Settle it at merge
    from the FERC CP22-2 order text itself** rather than from either news account.
  - `LengthKnown = 0` / blank `Diameter` are CORRECT here (compression only, no new pipe) — a third
    row in this batch with that shape, after P7790 and P7812. Do not "fill" them.
  - Orchestrator repair: the Diameter record had staged two `proposed_refs` on an intentionally blank
    cell — an orphan ref, which the repo bans. Cleared them, evidence preserved in the note, matching
    how P7790 and P7812 staged the identical case.

**P5727 (Double E Red Hills Lateral) — a status flip to `cancelled`, plus an EIA citation defect
and a wrong-sibling prompt comparison.** FERC authorized the 20 mi / 24 in lateral under Docket
CP23-24-000 effective 2023-02-18 (Federal Register 87 FR 78950, FR Doc 2022-27975); EIA's Aug2026
Historical Projects release recodes it **Cancelled** after FERC denied the construction-deadline
extension on 2024-03-21, so the sheet's `proposed` is stale. The status_review is staged at
**medium** because EIA is a single origin there (Double E's 2026 refiling of a near-identical "Dude
Lateral Project" is circumstantial, not a second publisher) — that tier is honest, leave it.
Two things for merge:
  - **EIA's own `website` field on the Red Hills Lateral row is wrong.** It points at
    `govinfo.gov/content/pkg/FR-2024-05-03/pdf/2024-09686.pdf`, which is 89 FR 36808-36809,
    *Carlsbad Gateway, LLC, Docket CP24-200-000* — an unrelated Targa project that merely shares the
    place-name "Red Hills". The agent read the PDF and correctly refused to stage it. **Do not let
    that URL back in** via any EIA-driven backfill.
  - **The prompt's auto-generated comparison table matched the wrong EIA sibling again** — it diffed
    this segment against the *mainline* Double E record (1,350 MMcf/d, 133.8 mi, CP19-495) and
    flagged every field as differing. Against the correct Red Hills Lateral EIA row the sheet's
    specs match exactly. This is the third time in slice 2 (after P2578 and P5727's own sibling
    P7830) that the prompt table pointed at the wrong EIA row: **the table is a candidate, never a
    finding.**
  - P5727 is NOT a duplicate of P7830 — see the P7830 entry above; both agents reached that ruling
    independently from opposite directions.

**P7860 (Great Basin 2028 Expansion) — the largest of the five Great Basin rows, and two live
spec disagreements left deliberately unreconciled.** FERC pre-filing Docket **PF26-5-000** (opened
2026-01-20; FR Doc 2026-08459, 2026-04-30), six Nevada counties, Winnemucca to west of Fernley. It
is cleanly distinct from P7856 (898 mi Main Line, operating), P7857 (CP23-466), P7858 (CP25-551 /
PF24-6) and P7859 (CP25-209) by docket, filing date and physical scope. Two items:
  - **Length/Diameter**: the sheet's `0.00` / blank were effectively uncited; the agent staged
    FERC's ~210 mi (≈195 mi of new 42 in + ≈15 mi of new 24 in lateral) and flagged that the
    company's own materials say ~230 mi total. Unreconciled on purpose — adjudicate at merge.
  - **Capacity**: the sheet's 1,250 MMcf/d is a stale June-2025 pre-open-season estimate. Two later
    figures disagree with it and with each other — EIA's 800 MMcf/d (contracted) and the company's
    "up to 948,000 Dth/d". `contested.Capacity` was left BLANK rather than forcing one. Correct
    handling; decide it at merge, not by picking the larger number.
  - **EIA mislabels this row's docket** as CP25-209-000 (which is P7859's) while its Notes text is
    unambiguously P7860's. Informational only — P7859's own shard has its docket right.
  - One cross_row_lead to **P7856**: FERC's scoping notice says this project would abandon ~142 mi
    of the Main Line's existing 8/16 in pipe plus the Rye Patch and Lovelock compressor stations.
    That is a *future* fact contingent on certification — do not apply it to P7856 now.

**P7785 (MountainWest Westbound Compression) — status flip construction -> operating, and a second
sec.gov audit false positive.** FERC Docket CP24-13, certificated 2024-10-17, in service
2025-11-13, 325 MMcf/d. The status_review verdict is `change` and agrees with the Status fill.
Where EIA and FERC disagree on the delivery point (EIA: "Wamsutter to Opal hub"; FERC's certificate
order: a new Kern River interconnect near Roberson Compressor Station), the agent used FERC's text —
correct. Note the pending partial motion to vacate certificate authority for an unbuilt pig-launcher
at "Cabin 31"; it is capacity-neutral, so it does not disturb the flip. The cross_row_lead to P6899
states the rule that matters for this cluster: **2,800 MMcf/d is the Overthrust SYSTEM total and
325 MMcf/d is this project's increment — different scopes, never merged.**
`fills[14]` (Owner1) was flagged by the orchestrator audit as `tier=high on 1 publisher` and is
**upheld, not downgraded** — its two filings are by two different registrants (Williams CIK
0000107263 as buyer; Southwest Gas Holdings CIK 0001692115 as seller), which is two origins. The
audit script collapses every `sec.gov` URL to one netloc. **Read the CIKs before acting on any
sec.gov tier finding** — same shape as P6898 `fills[14]`.

**P7823 (Spring Creek, NV) — a PipelineType correction that raises a SCOPE question, park it
with the other classification rulings.** This is a Southwest Gas **local distribution company**
service-territory expansion, filed with the **PUCN** (not FERC) on 2019-06-12 under NRS 704.9925,
$61.9M, mid-construction on a 2020-2027 phased buildout. The applicant's own filing calls both
components "distribution" throughout ("high pressure steel distribution pipeline", "Distribution
System"), while the sheet records `PipelineType = transmission`. The agent staged `distribution`
and filed a classification concern — correct under rule 4(e). **But the larger question is whether
a distribution project belongs in GGIT at all**, and that is not a merge decision: add it to the
open rulings alongside P7455 and P7830. Two things that are NOT defects here: the project does
involve genuine new pipe (12.1 mi of 8 in steel approach main, ~22 mi of new PE "Backbone System"
which is what `LengthKnown = 22.00` tracks, plus 168 mi of further PE distribution main), so this
is NOT one of the compression-only rows; and it is not a duplicate of the Great Basin cluster
(P7856-P7860), which is a separate FERC-regulated interstate subsidiary of the same parent.

**P4455 (Crow Creek, ID->WY) — status flip `proposed` -> `construction`, and a diameter conflict.**
Lower Valley Energy Coop's Montpelier ID to Afton WY line, FERC/Forest Service jurisdictional,
confirmed across six-plus origins (EIA, FAST-41 via Wayback, DOJ, Pipeline & Gas Journal, JH News &
Guide, court dockets). `ConstructionYear = 2025`, evidence date 2025-09. The open item for merge:
**EIA says 12 in, two other sources say 8 in.** Staged as a spec concern, not silently resolved.
Four UNRESOLVED (Pressure, FuelSource, SegmentCost, StartYear1), each with search notes.

**P0237 (Pacific Connector) — two contested cells, a scope trap correctly avoided, and two tier
repairs.** The 229 mi / 36 in Malin OR -> Jordan Cove line; filed 2013 (CP13-492), denied 2016,
refiled 2017 (CP17-494), approved 2020, withdrawn by the developer December 2021. Status stays
`cancelled` (a 2025-02 OregonLive report of an OA Partners petition to revive the terminal is
corroborating, not status-changing — no docket reactivation). For merge:
  - **Capacity: sheet says 2,024 MMcf/d, which matches no source.** EIA and S&P Global Platts (2020)
    both say 1,200. `contested: {"Capacity": "1200"}` — apply it.
  - **Owner1%: sheet says Pembina 100%, unconfirmed.** FERC's 2016 order documents the original
    structure as a 50/50 Williams/Veresen JV and no source shows a full divestiture; only one source
    ties Pembina to the line at all. `contested: {"Owner1%": ""}` — correct, do not invent a split.
  - **The Jordan Cove scope trap was handled right**: the $10bn figure is terminal + pipeline
    combined and was excluded; `SegmentCost` is FERC's pipeline-only $1.74bn, corroborated by EIA's
    $1,700M.
  - Orchestrator repairs: `fills[1]` (Fuel) and `fills[2]` (PipelineType) both claimed
    high/independent on a SINGLE staged ref — a Wayback capture of the FERC certificate order —
    while leaning on EIA in prose without staging it. **Fuel**: staged the EIA Aug2026 release, since
    a natural-gas-projects dataset carrying the project does state the fuel; FERC and EIA are two
    agencies, so high/independent now stands on evidence. **PipelineType**: DOWNGRADED to
    medium/not-independent, because EIA's `New Pipeline` is a project-STAGE label, not GEM's
    functional transmission/gathering/distribution classification — the same reading the A6 agent
    applied to EIA's `Intrastate` on P5545. The value is not in doubt; the tier was.
  - **Audit-script blind spot, since FIXED:** `pubs_of` did NOT unwrap a `web.archive.org` capture
    to its origin host, so it both over-counted (a live page plus its own capture read as two
    publishers) and under-counted (a record whose refs are ALL captures of different publishers read
    as ONE). The under-count bit first on P0404, whose six flagged records are all captures of
    monitoreconomico.org / gob.mx / ienova.gcs-web.com. The scratchpad auditor now unwraps
    `web.archive.org/web/<ts>[id_]/<original url>` before taking the netloc; all six P0404 findings
    were false positives and no shard was changed for them. The remaining two standing false
    positives (P6898 / P7785 `fills[14]`) are the sec.gov two-registrant case, which is different and
    still unfixed by design — read the CIKs.

**P2553 (SDG&E Line 1600 Replacement, San Diego CA) — status flip AND a `LengthKnown = 0` that is
NOT the expansion convention.** CPUC-regulated intrastate line, Rainbow -> Mission Valley. Two merge
items:
  - **Status `proposed` -> `operating`.** EIA has tracked this project across 21 releases (2020-03 ->
    2026-08) and has shown it `Completed` since the Oct-2024 release, completed date 2023-10-15,
    in-service year 2024.
  - **`LengthKnown = 0.00` is a defect, not the no-new-pipe convention.** This project installs ~37
    mi of NEW pipe; the convention only covers expansions that add no physical pipe. Corrected to
    `LengthKnown = 49, LengthKnownUnits = mi` on EIA (Miles = 49, constant across all 21 releases)
    plus SDUT (37 mi new + 13 mi tested, agreeing within rounding). `Diameter = 36 in` was checked
    and is correct — do not touch it.
  - The agent correctly excluded the CPUC-REJECTED 2018 "Pipeline 3602" proposal ($639M, also 36 in)
    as a different project. Don't let its cost back in.
  - Orchestrator repair: `fills[0]` (Status) and `status_reviews[0]` both claimed high/independent
    while the shard's own verification marked the Valley Roadrunner article `contains_value: false`.
    The two valleycenter.com articles are ONE publisher and neither states an in-service status, so
    the flip rests on eia.gov alone. Both DOWNGRADED to medium / not-independent. The value is not in
    doubt — the local reporting does corroborate that the pipe was substantially built by late 2023 —
    only the tier was wrong.

**P2625 (Tioga to Emerson, WBI Energy) — the end state is Minnesota, not Manitoba.** GEM records
`EndState/Province = Manitoba` / `EndCountryOrArea = Canada`; three independent sources place the
terminus in **Minnesota**: WBI's own spokesperson in the Pierce County Tribune ("from the Tioga area
to northwestern Minnesota, which is near the Emerson natural gas hub"), EIA (`End_State = MN`), and
offshore-technology.com. "Emerson" names the interconnect hub the line targets, not a border
crossing — and a Federal Register full-text search for the project returns zero documents, consistent
with no Presidential Permit ever having been sought, which is what a genuine border crossing would
require. Staged as a validity concern AND a corrected `Location [ref]` fill (End state -> Minnesota,
End country -> United States, EndPrefecture/District cleared). Status review verdict `confirm`: EIA
flipped it Announced -> On Hold in the Oct-2024 release and WBI's live projects page and MDU's FY2025
10-K have both dropped it in favour of a separate **Bakken East Pipeline** (a distinct successor, not
on this roster — do not merge the two). ~2 years dormant as of 2026-09, so `shelved` is right and the
4-year cancellation threshold is not met.

**P1299 (Steady Eddy, WhiteWater Midstream, Eddy County NM -> Culberson County TX) — keep
`cancelled` / `inferred`, and a ROUTES-REPO defect worth filing.** 24 in / 23 mi lateral, real and in
scope (transmission-scale, not gathering), confirmed by Rigzone (2019-01-10) and RBN Energy
(2019-01-30, via Wayback). Status review verdict `stale` in the sense that it CONFIRMS the recorded
`cancelled` / `ShelvedCancelledType = inferred` under the dormancy rule: newest evidence is 2019-01,
and no dated cancellation source exists, so it must NOT be upgraded to `confirmed` and `CancelledYear`
stays blank (iraq.md precedent). Two things for merge: the **route geometry in the routes repo stops
~3 km short of the sourced Texas terminus** — the sheet's Location cells are correct, so this is a §8
fix, not a Location edit; and the sources disagree on intrastate-vs-interstate labelling (prose only,
no `PipelineType` fill staged, since it is not an owed unit here). One cross_row_lead to P7109 (Agua
Blanca).

**P0404 (Ehrenberg AZ -> San Luis Rio Colorado, Sonora) — a well-evidenced CANCELLED cross-border
row; three things for merge, none of them a defect in the shard.**
  - **Existence and classification confirmed at high tier, entirely off non-GEM Spanish-language
    government sources**: CFE's 23-Apr-2014 announcement (Monitor Economico; Somos Industria is the
    SAME press event, one origin), SENER's PRODESEN 2015-2029 and 2016-2030 planning tables
    (`Gasoductos en Proyecto`: CFE-tendered, 160 km, $249M, target COD 2017), CENAGAS's Jan-2015 Plan
    Quinquenal, and IEnova/Sempra's Jul-2014 investor deck (160 km, $246M capex). **Scope is right as
    recorded**: no source anywhere splits a US-only from a Mexico-only length/cost/capacity, so GEM's
    single whole-line segment is correct, not a scope mismatch.
  - **`Operator = IEnova` / `Owner1 = Sempra Energy` is UNCONFIRMED** — `contested: {"Operator": "",
    "Owner1": ""}`, staged at `low`. The ONLY document tying IEnova to this line is Sempra's own deck,
    and there it sits inside a market-wide table of all 17 National Infrastructure Program tenders —
    a sector-opportunity list, not an award. PRODESEN names the tender authority as CFE and gives no
    winning bidder, and IEnova's current asset map does not show the line. Plausible, unproven; do not
    silently keep it.
  - **`EndLocation` spelling**: sheet says "San Luis Colorado", every source says **"San Luis Rio
    Colorado"** (a real Sonoran city, not San Luis Potosi). `contested: {"EndLocation": "San Luis Rio
    Colorado"}` — apply it.
  - Status review: `cancelled` UPHELD by inference. Last positive evidence is PRODESEN 2016-2030
    (2016-05-30); the project is then completely absent from PRODESEN 2018-2032 and from IEnova's 2025
    map — 9+ years dormant, far past the 4-year threshold. `ShelvedCancelledType = inferred`, no
    fabricated ref. **The agent deliberately proposed NO `CancelledYear`**, because no dated
    withdrawal exists and picking 2017 (the missed COD) or 2018 (first absence) would be invented
    precision. That leaves the row technically short of the "cancelled implies a CancelledYear"
    convention — **accept the blank; standing rule 2 outranks the convention here.** Same shape as
    P1299.
  - **Dispatch-capacity note for future rounds:** this agent hit `WebSearch` budget exhaustion
    (200/200 calls) and then found DuckDuckGo and Bing via curl reproducibly bot-walled, and FERC
    eLibrary unscriptable (a JS SPA returning HTTP 200). It escalated properly and said so in the
    notes rather than reporting a clean negative — that is the right behaviour, but it means the
    FERC/DOE-permit axis for this row is genuinely unsearched, not searched-and-empty.

**P7850 (Targa "Forza Gas Pipeline") — the sheet's PipelineName is a PORTFOLIO label, and the
existing citations point at the wrong Targa project.** The row is `Targa Resources Pipeline System`,
segment `Forza Gas Pipeline`; the asset is a single real project (36 mi / 36 in, Red Hills Plant, Lea
County NM -> Wildcat Junction, Winkler County TX; FERC **CP26-34**; in-service 2028), confirmed in
EIA's Oct2025/Jan2026/Aug2026 releases and Targa's own 10-Q. Natural gas, not NGL/crude — the oil-
scope trap in this corridor was checked and cleared. Two things:
  - **The sheet's carried Status/Fuel/PipelineType citation is an OGJ article that resolves fine but
    describes a DIFFERENT Targa project (Speedway NGL / Buffalo Run).** A live link is not a
    relevant one. Re-grounded on EIA + Targa primaries. Same defect shape as the P5727 mis-cite.
  - Status `proposed` CONFIRMED (evidence 2026-08: 10-Q filed 2026-08-06 and EIA both still
    pre-construction, FERC application pending since 2025-12-03 with no order).
  - **Cross-row lead to P7109, worth working at merge**: Targa's own page describes a separate
    **Bull Run Pipeline extension** (~43 mi, 42 in, FERC **CP26-35**, jointly filed with Forza's
    CP26-34) that Forza leases capacity on. P7109's segment is `Targa Red Hills Interconnect` on the
    same Red Hills corridor with every spec blank — so P7109 may BE Bull Run (wholly Targa-owned)
    rather than a WhiteWater/Agua Blanca asset. **P1299's agent independently filed a cross_row_lead
    to the same P7109.** Two agents converging on that row from different directions is the signal to
    work it. Do not assert the identity from either lead alone.

**P0382 (Paso Norte, Deming NM -> El Encino/Chihuahua) — a cross-border row whose cost figure is
scoped to the US lateral only.** ~340 mi / 32 in Permian/Waha gas into Mexico, confirmed by Pipeline
& Gas Journal's Ongoing Projects compilations (2018 and 2023 editions), the sponsor's own site, and
NGI (2018). For merge:
  - **`SegmentCost` — `contested: {"SegmentCost": ""}`.** Both sourcing documents scope the $60M to
    the ~33-mile **US lateral only**, not the 340-mile cross-border line GEM's row describes. That is
    the same different-scope trap as Jordan Cove on P0237, decided the same way: a figure for a
    different extent is not a ref for this one.
  - Status review `stale` -> `cancelled` upheld with `ShelvedCancelledType = inferred` and
    **`CancelledYear = 2020`**. Note this row DOES get a year while P0404 and P1299 do not: PGJ's
    entry is internally dated "REV 11/20" and reads "Construction: On hold", republished unchanged
    through Jan 2023, so 2020-11 is a dated last-positive-evidence point rather than an invented one.
  - The escalation ladder was run and reported honestly (DDG/Bing bot-walls, DOE/FECM 404s, FERC
    eLibrary confirmed a JS shell), so the absence of a FERC Section 3 order / Presidential Permit is
    recorded as a caveat, not as proof.
  - Cross-row leads: P0061 Double E (extra-edition corroboration, slice 1 — apply only if that row's
    ref coverage is thin) and a **cautioned** P7863 lead the agent itself flagged as probably a
    different REX project. Do not act on the P7863 one.

**A7 (west) shard collection CLOSED — 42/42 on disk, coverage clean, 0 unreported units, 0
unmergeable records, 0 silent UNRESOLVED.** Orchestrator audit over all 42: the only remaining
findings are `P6898 fills[14]` and `P7785 fills[14]`, both the sec.gov two-registrant false positive,
both already annotated in-shard. Five shards were REPAIRED in place this round — P7782 and P5727
(validity claiming `tier: high` with empty `proposed_refs`), P3171 (an orphan ref on a correctly
blank Diameter), P0237 (`fills[1]`/`fills[2]` high on one publisher — Fuel upheld with EIA staged,
PipelineType downgraded) and P2553 (Status fill + status review high on one publisher, both
downgraded to medium).

**Defect shapes found in this round's shards (all repaired in place, all invisible to
`check_shard_coverage.py`):**

- **`tier=high` on multiple EDGAR filings by ONE filer** (P6899, two units + its
  status_review; both refs CIK 0000107263). The prose named a seller-side filing as the
  second origin but never staged it, and an unstaged ref cannot be counted. Downgraded to
  medium/not-independent.
- **The inverse, which the audit script gets WRONG:** two filings by two *different*
  registrants both live on `sec.gov`, so `pubs_of` collapses them to one netloc and reports
  a false positive. P6898's Owner unit (Williams as buyer, CIK 0000099250 joint-filer path;
  Southwest Gas Holdings as seller, CIK 0001692115) is legitimately high/independent — a
  note now says so in the shard. **Read the CIKs before acting on a `sec.gov` tier finding.**
- **`validity` record claiming `tier: high` with empty `proposed_refs`** — P5101, the third
  occurrence this slice (after P7863). A validity record carries no verifications by repo
  convention, so its tier counts over `proposed_refs`; empty reads as zero publishers.
  Staged the two publishers its prose already relied on (the Federal Register notice of
  application naming the Kalama Lateral Project, and EIA's dated Aug2026 release).
- **`UNRESOLVED` records with `tier` staged as an empty string** rather than `low` — P6898,
  six units.
- **An EDGAR company-search feed as a `proposed_ref`** (P0230's Operator unit: a
  `cgi-bin/browse-edgar?action=getcompany...&output=atom` URL) while the *verification*
  pointed at the real filing. Replaced the ref with the verified document.
- **`ok: false` on a unit-equivalence substring miss** — P0230's Capacity unit marked
  williams.com unsupported because the page says "3.8 million dekatherms per day" and not
  "3,800 MMcf/d". Re-fetched (200, 378,241 bytes) and confirmed; flipped to
  ok/contains_value true, which is what actually earns that record its second publisher.
  This is the same shape as P3942's itemized-components Length ref: **a source that states
  the value in its own units, or as its components, still states the value.**

**Recurring shard defect, for whoever dispatches next:** a single "search record"
verification block reused across several units with `contains_value` left `true`, while
the units themselves are correctly `UNRESOLVED`. Found on P7463 (5 units). The page names
the pipeline and states *some* facts, so the agent marks it verified — but it carries no
field for *that unit's* value. Fix is `contains_value: false` with the reason appended;
the entry stays as the record of what was searched.

## 8. Environment

- Python: `/Users/baird/miniconda3/bin/python3`. Use absolute paths (`cd` inside Bash
  changes the session cwd). Foreground `sleep` is blocked - use `run_in_background`.
- Gas snapshot `data/GGIT_gas_snapshot_20260910.csv` (**header=2**); operators tab
  `data/GEM_operators_owners_snapshot_20260910.csv` (**header=1**).
- SEC EDGAR is never blocked: UA `Baird Langenbrunner baird.langenbrunner@globalenergymonitor.org`
  (url_verifier already retries with it). Pipeline:
  `data.sec.gov/submissions/CIK##########.json` -> `filings.recent` ->
  `sec.gov/Archives/edgar/data/<int(cik)>/<accession-no-dashes>/index.json` -> fetch,
  strip tags, grep. EDGAR **navigation** URLs (cgi-bin/browse-edgar, cgi-bin/viewer,
  efts.sec.gov search, data.sec.gov/submissions/*.json) are never refs.
- globenewswire.com is unreachable to our tooling and ferc.gov 403s the fetch tool -
  both are tooling failures, never evidence. Escalate (curl+UA, Wayback, CDX,
  pdftotext) before calling anything unreachable.
- gem.wiki: <=5 req/s, harvests serially, `url_verifier.WIKI_UA` for gem.wiki only.

## 9. Script hardening deferred (another session holds those files)

Document in `ADDENDUM.md`, do not edit the shared scripts: reject a non-list
`validity`; reject `data.php` and undated-workbook refs; reject a non-dict
`proposed_changes` and a "change" verdict with empty `proposed_changes`; flag an
UNRESOLVED unit carrying an ok+contains_value verification; reject EDGAR navigation
refs; flag a live-status flip that leaves cancellation fields populated; flag prose in
`contested` values; **reject a fill whose `values` is not a dict** (the P3189 bug).
Also open: the `QCCOwner` column leaking into US worklist `value_cols` (P3187).
