# Delivery — China / Jiangxi gas, deep sweep v3 (2026-09-10)

**ONE file to work:**
`batches/china-jiangxi-gas/deliverables/pipelines_batch_20260910_1154_ET_china-jiangxi-gas_deepsweep.xlsx`

Staged, not applied. **Nothing was written to the live sheet or the routes repo.** v3
SUPERSEDES the 2026-09-02 v2 workbook — same 44 PIDs, carried forward and extended — so
**`deliverables/` holds exactly one file and the pending state is one workbook**. Moved to
`archive/` on delivery, per the v1→v2 precedent: v2's workbook
(`…_20260902_1232_ET_…`), its staging dir (now `archive/deepsweep-v2-20260902/`), the two
intermediate 09-10 rebuilds (`_1125_ET`, `_1150_ET`), and the 08-26 v1.

Staging dir: `batches/china-jiangxi-gas/staging/deepsweep-20260903/`.

## What v3 was for

MZ reviewed v2 ("looks really good") with four points, and v3 exists to answer them —
the plan is `notes/plan-2026-09-03-china-jiangxi-gas-deepsweep-v3.md`:

1. **blanks on operating rows unfilled** — v2 staged 4 fills against 241 owed blanks.
   v3 runs `--owe-fills`: **248 FILL units reported, 94 filled with a corroborated
   value**, 154 honest `UNRESOLVED`. Gate J is 0 — no owed blank went unreported.
2. **facts in found sources not carried to the other columns** — document-exhaustion is
   now in the contract and enforced per shard by `check_shard_coverage.py`; the
   `doc_index.json` / `leads_by_target.json` pair routes one document's facts to every
   row and column it touches.
3. **refs that don't name the pipeline** — `name_found` per verification +
   `merge_qc.relevance_qc` cap, surfaced as gates I / I'. Down to **5 units** whose refs
   don't name the row's pipeline, plus **1** never checked (P4788 `Pressure [ref]`).
4. **one ref per data point** — gate K counts them: **72** `REFS_ADDED` still rest on a
   single verified ref, against 194 total. Every one says in `researcher_notes` what was
   searched for the second.

## Numbers

| | v2 | v3 |
|---|---|---|
| rows / records | 44 / 453 | 44 / **772** |
| ref units (`MISSING_REF` + `HAS_REF`) | 411 | 411 |
| — REFS_ADDED | 270 | **194** |
| — REVERIFIED | 12 | **106** |
| — UNRESOLVED | 127 | **109** |
| — DEAD_LINK | 2 | 2 |
| fills reported | 4 | **248** (94 filled / 154 unresolved) |
| validity concerns | 26 | **99** |
| status reviews | 12 | **14** |
| distinct verified hosts | 49 | **79** |

The `REFS_ADDED` drop is the carry-forward working as designed: v2's sourced units were
re-keyed onto the fresh worklist and re-verified, so **300 of the 411 ref units are
sourced** (194 + 106) against v2's 282 — a `REVERIFIED` is a v2 `REFS_ADDED` whose URLs
still resolve and still state the value.

Tiers on the 300 sourced ref units: **125 high / 154 medium / 21 low**;
`independent: true` on 164.

Fills by column (94): Owner 28, Pressure 18, Proposal 16, FuelSource 16, Construction 7,
Start 5, Capacity 2, PipelineType 1, SegmentCost 1 — across 34 of the 44 rows.

## Status review — 14 rows

| verdict | rows |
|---|---|
| `CHANGE_PROPOSED` | **P5865** → `operating` + `StartYear1 2021`; **P5886** `proposed` → `construction` |
| `CONFIRMED` | P4661 (`proposed`, high), P5866 (`operating`, medium) |
| `STALE` (re-verify owed, no sourced replacement) | P4752, P4785, P4787, P4790, P5860, P5863 |
| `UNRESOLVED` / unclear | P4786 (candidate `shelved`), P4792, P5887 (candidate `operating`), P5888 (candidate `construction`) |

The four unclear rows each carry a candidate value in the record and a note saying why it
is **not** proposed — P5888's is the clearest case: a plausible county article would move
the row to `operating`, it is unverifiable, and it is cited nowhere.

## Gates

| gate | result |
|---|---|
| A source diversity (<2 hosts on a sourced row) | 2 |
| B false `high` | **0 — PASS** |
| C `high` leaning on a dominant document (≥15 units) | 60 |
| D `independent=true` with <2 verified refs | **0 — PASS** |
| E orphan refs / unsourced values | **0 — PASS** |
| F banned or GEM sources | **0 — PASS** |
| G live pool URLs never opened on an `UNRESOLVED` row | 41 |
| H live origins behind SPN citations, unopened | 39 |
| I refs don't name the pipeline | 5 |
| I' relevance unchecked | 1 (P4788 `Pressure [ref]`) |
| J owed blanks with no record | **0 — PASS** |
| K `REFS_ADDED` on exactly one verified ref | 72 |
| L uncited values never worked | **0 — PASS** |

**Gate C is concentration, not a defect** — the same shape as v2, larger. Eleven documents
carry 404 units between them; read these before deciding whether "two sources" is really
two:

| units | document |
|---|---|
| 98 | `img9.qianzhan.com/policy/202307/14/…pdf` — the 2014 Jiangxi DRC gas-utilization plan (rehosted primary) |
| 60 | `qxb-pdf-osscache.qixin.com/AnBaseinfo/…pdf` — corporate registry extract |
| 48 | `static.sse.com.cn/…242696_20250403_…` — the 2025 SSE bond disclosure |
| 42 | `quannan.gov.cn/…faad1fb7c1214b8a8394299531ab10a8.pdf` |
| 25 | `ndrc.gov.cn/xxgk/zcfb/tz/202312/P020231205363278799826.pdf` |
| 24 | `mee.gov.cn/gkml/sthjbgw/spwj1/201612/t20161222_369429.htm` |
| 20 | Wayback `20230902105154` of `jxgajc.com/Hr/show-10438.aspx` (P5866's completion filing) |
| 20 | `petrobest.com/success_info.php?cid=74` |
| 19 | `en.wikipedia.org/wiki/West–East_Gas_Pipeline` |
| 17 | `nea.gov.cn/2012-11/05/c_131957190.htm` |
| 16 | `swj.jiujiang.gov.cn/…t20230609_6056040.html` |

The 19 wikipedia-cited units (P4657, P4793–P4797, P4934, P4947 — 22 units counting the
unsourced siblings) are the ones to challenge first: an encyclopaedia article is a
tertiary surface, and each needs its own primary.

## Workbook tabs

| tab | rows |
|---|---|
| `README` | 25 |
| `Gas_StatusReview` | 14 |
| `Gas_Backend` | 44 × 133 — 1:1 mirror of the full gas backend, overlays tier-colored on touched cells only |
| `Gas_OperatorsOwners` | 44 |
| `Gas_Validity` | 99 |
| `Gas_Fills` | 248 |
| `Gas_Refs_Added` | 194 |
| `Gas_Refs_Reverified` | 106 |
| `Gas_Refs_DeadLinks` | 2 |
| `Gas_Refs_Unresolved` | 109 |

`Gas_Validity`'s `Recommendation` column carries a **specific ruling on 7 of 99 rows**
(P4778, P4931, P4944 ×2, P5861, P5862, P5866); the other 92 keep the boilerplate on
purpose, because they are genuinely open questions and an orchestrator recommendation is
not a licence to convert an open question into an instruction.

## The four adjudicated rulings

Everything else in `Gas_Validity` is a question. These four are decisions, and they are in
the `Recommendation` column so a reviewer sees the action, not "see researcher_notes":

- **P5861 is a duplicate of P4778 → retire it into P4778.** Two agents at opposite ends of
  the fan-out each filed a `__REDUNDANCY__` naming the other's row; reciprocity is
  corroboration, not two findings, so it is delivered as ONE cluster. What settled it is a
  negative in PipeChina's exhaustive 2026 公平开放 inventory. The 2024-12-31 WEP2 tie-in is
  explicitly barred from rescuing P5861's `FuelSource`.
- **P5866's `segment_name` carries a one-character orthography defect** — 金沙湾 for the
  real 金砂湾. Cheap to fix and it *mechanically* caused twelve "system-only" ref reads,
  because every name-match on the wrong character missed.
- **P5862 is the batch-wide phase sentinel** (rulings A–E; A applied, 20 rows normalized at
  chain step 0c). Its own existence is `NOT ATTESTED, and partly CONTRADICTED`, so the
  standing instruction is **not** to "repair" a route geometry the row may not own.
- **P4944's start location: CHANGE 2 CELLS** — `StartLocation` `Dongyang Town, Anyi County`
  → `Dacheng Town, Gao'an City`, and `StartPrefecture/District` `Nanchang` → `Yichun`.
  Gao'an is a county-level city under Yichun, so both cells move together; leave
  `StartState/Province`, `StartCountryOrArea`, and the whole End side alone. One station,
  one place, four publishers, and **no** source places anything in 安义县.

## Method note — the refs leg cannot change a non-blank value

Found the hard way this pass, and it is now the rule for every batch (transcribed to
`docs/country_notes/china.md`): `scripts/merge_ref_shards.py` writes `class_out`,
`proposed_refs`, `verifications`, `tier`, `independent` and the notes fields onto a seeded
record and **never its `values`**. That is by design, not a bug — the refs leg carries a
value only for an owed BLANK (a `MISSING_VALUE` unit appended as a FILL).

So a **non-blank cell that is simply wrong has exactly one channel that reaches the
deliverable: the `__VALIDITY__` concern** ("QC detects, Update fixes"). Status changes have
their own channel (`status_reviews`, which do carry values). My first attempt at the P4944
correction wrote the right values onto the `Location [ref]` `REFS_ADDED` record, ran the
whole chain, and produced a workbook that still showed `Dongyang Town, Anyi County` — the
value reached `ref_shards/` and stopped. The agent's original conservative choice (stage it
as a `__VALIDITY__` concern rather than a silent change) turned out to be right for a
structural reason on top of the conservative one.

Two engine changes came out of it, both additive:

- `scripts/harvest_sentinel_findings.py` now honours a per-record `recommendation` instead
  of stamping one boilerplate line on all 99 sentinel findings. Blast radius checked
  repo-wide: **341 sentinel records across every batch, 6 carrying a recommendation the
  harvester was overwriting, all 6 in this batch** — a strict no-op for every other
  country. Two of those six were agent-written and were being silently discarded (P4931 #3,
  P4944 #15's `StartYear1` concern).
- Three run-dir stagers, wired into `run_merge_chain.sh` as steps 0e6–0e8 and verified
  idempotent: `stage_p5887_independence.py` (the one off-contract `independent: None` on a
  `__STATUS__` sentinel — invisible to gate D in both directions; `normalize_independence.py`
  can't reach it, because its gate skips falsy `None` *and* every `__*` sentinel),
  `stage_p4944_start_location.py` (reverts the unstageable value change and puts the ruling
  on the concern), `stage_orchestrator_recommendations.py` (the four rulings above).

## Chain provenance

`bash batches/china-jiangxi-gas/staging/deepsweep-20260903/run_merge_chain.sh` — 21 steps,
exit 0, no `MARKER NOT FOUND`, no error cells. `check_shard_coverage.py --all` reports
**0 shards with gaps — 0 unreported units, 0 unmergeable records, 0 silent UNRESOLVED**;
`normalize_schema_keys` applies 0 fixes (the store is conformant); `recalc` reports no error
cells. Gate counts are identical across the `_1125` → `_1150` → `_1154` rebuilds.

Two ordering constraints the chain encodes, worth not re-learning: `split_shards.py`
regenerates `ref_shards/` and `rows/` from `shards/` on every run and never touches
`ref_shards_recovery/`, so **every normalizer that rewrites `shards/` must run before step
1**, and the recovery dir gets its own pass at 1c. And `merge_ref_shards.py` is
last-writer-wins over `(project_id, ref_col, sheet_row)` with `--shard-dir` defaulting to
`["ref_shards"]` — omitting `--shard-dir ref_shards_recovery` silently drops that whole leg.

## Still open (not blockers — the workbook carries each as a concern)

- **The Phase I/II per-segment reconciliation** — P5862 rulings B–E. Ruling A is applied;
  B–E need the phase test run row-by-row, then P4787-vs-P4788, P4789's internal split,
  P5862-vs-P5863, and the P4779-vs-P4796 Jingdezhen tension. **P5863 is genuinely open**:
  geography reads Phase I, chronology reads Phase II (a 2023 project, and 管道分公司 was
  formed in 2016 expressly to build the Phase II remainder).
- **Conventions owed, each spanning several rows:** `FuelSource`-vs-phase across all 23
  phase-labelled rows (12 blanks waiting); the WEP-family English-vs-CJK `Owner1` style
  (P4934/P4947 CJK vs P4944/P4946 English, with P4928's fix inside it);
  first-gas-vs-full-line commissioning (P4944, P4946, P4934's west section); the
  qianzhan-vs-SSE-2023 Phase I trunk decomposition at P4777.
- **Candidate value changes deliberately NOT staged** — each is a real convention question
  where several published figures are all true of something, and each carries a "CANDIDATE
  VALUE CHANGE / decision owed at merge" concern: P4928 `Capacity` 30 → 15 bcm/y and
  `LengthKnown` 817 → 832.40 km (with station/valve counts 11+40 → 12+36); P5865 0.13 vs
  0.005 bcm/y; P5866 0.50 vs 0.492 bcm/y and 19.12 vs 19.13 km; P5889 31.32 vs ~34 km.
- **One Discovery item**: the missing GEM row 上犹–崇义段 — 43 km, DN250, 6.3 MPa,
  0.9×10⁸ Nm³/a, 西二线上犹分输站 → 崇义门站 (P4787 `__VALIDITY__` item 5). P4790's five
  "unrouted finds" are **not** Discovery items — all five belong to existing rows (P4789,
  P4791, P5865, P5866+P5886, P4776).
- **Routes leg (flagged, out of scope for this sweep):** redraw P5866's 123.15 km trace to
  the documented ~19 km corridor; remove or replace P5862's stray vertex
  `[114.81473, 31.077466]` — only if P5862's identity survives, and `RouteType` /
  `RouteAccuracy` / the routes repo must move together (three-way sync).
- **Micro-passes owed:** P4657 (Pressure + Diameter), P4789 (43 km Length), P4787 + P4792
  (`Status [ref]`), P4786 (瑞金–会昌段), P4779 (phase check), P4785 (P5860's 大余–信丰段
  已建成并投产 tension).

## Tooling defects found, deliberately not fixed mid-batch

`scripts/url_verifier.py` (already `M` in git status before this batch), three:

1. `_match_surface` false-positives a Latin name against raw markup.
2. No IPv4 retry on a 403 — `www.quannan.gov.cn` returns **403 over IPv6 and 200 over
   IPv4**, and 42 units in this batch cite it. `curl --ipv4` + `pdftotext -layout` reads it
   fine. **A 403 there is not a deletion.**
3. `chinanews.com.cn` decodes as a false negative: strict `gb18030` *and* `utf-8` both
   reject its mixed bytes, while `errors='replace'` reads cleanly.

Also owed before the next CJK batch: `worklist.json`'s name fields are English-only, which
is the mechanism behind P4790's false "no PID identified" — the CJK name never reached the
matcher.

Uncommitted script changes from this pass, awaiting Baird's say-so (commit/push only when
asked): `scripts/url_verifier.py`, `scripts/merge_qc.py`,
`scripts/harvest_sentinel_findings.py`, `scripts/sweep_gates.py`.
