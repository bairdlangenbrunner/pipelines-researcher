# Shard normalizations

Mechanical fixes applied to agent shards before the merge chain. Each one changes a field
the chain would otherwise mishandle; **none changes a finding, a value, a ref, or a tier.**
Logged here so the delivery note can state exactly what was touched.

## 2026-09-02 — batch_06 #22, P5866 `Operator [ref]`: `CONFIRMED` -> `REFS_ADDED`

`CONFIRMED` is not a ref class. `build_ref_workbook._ORDER` is
`[REFS_ADDED, REVERIFIED, DEAD_LINK, UNRESOLVED]`, so the record would have fallen into no
bucket and **vanished from the workbook silently** — the same silent-loss family as the
three defects this batch already hit.

The work it records: P5866's `Operator [ref]` carried one ref (SSE bond PDF, medium/single).
The agent re-verified it AND added a second independent document (CCXI 2022 rating report via
qixin), both hand-confirmed with `pdftotext -layout`, giving the same 54%/46% split →
medium upgrades to high.

`REFS_ADDED` over `REVERIFIED` because both classes render `proposed_refs` identically but
color differently: `REVERIFIED` paints the cell BLUE ("re-checked, no change"), `REFS_ADDED`
paints it by tier (green = 2+ independent). A new corroborating source WAS added, so blue
would understate the finding. Tier, refs, verifications and notes are untouched.

Not an owed unit — the agent flagged it as a bonus upgrade, and its note carries a live
caveat: both sources name the 46% holder as PipeChina's subsidiary
国家管网集团东部原油储运有限公司, not the sheet's parent-group entity string. Flagged, not
silently overwritten.

## batch_03 #13, #14 — P4787 `Capacity [ref]`, `Length [ref]`: `CONFIRMED` → `REFS_ADDED`

Same defect as batch_06 #22, found by the same check. `build_ref_workbook._ORDER` is
`["REFS_ADDED", "REVERIFIED", "DEAD_LINK", "UNRESOLVED"]`, so a record classed
`CONFIRMED` falls into no bucket and is **dropped from the workbook with no warning** —
the research would have been done and then silently discarded.

`REFS_ADDED` rather than `REVERIFIED`: both records carry `current_ref: null`, i.e. the
`[ref]` cell was empty and this pass filled it. `REVERIFIED` renders blue ("no change")
and would understate a cell going from unsourced to sourced.

Batch_03 #24 was left alone — it is a `__VALIDITY__` sentinel, and the harvester
normalizes sentinel `class_out` to `UNRESOLVED` by design.

Neither edit changes a finding, a value, a ref, a tier, or a verification.

## batch_99_crossshard.json — 3 `__VALIDITY__` sentinels (coordinator-authored)

Not a research shard. Batch_03 found, on two independent documents, that the 54/46 JV
operates Jiangxi Phase I only while Phase II runs under the Group's own 管道分公司 — but it
could only file that against its own three rows. Three sibling shards had meanwhile staged
that same JV against `Operator [ref]` on Phase II rows they were researching in parallel
(P4785 via batch_02, P4790 and P5860 via batch_04), never having seen the evidence.

This is the Egypt cross-shard blindness pattern, so the finding is propagated rather than
left to sit inside one shard. Filed as sentinels, deliberately: the tension is real but not
established — the staged value is an *owner* fact (`QCCOwner(业主单位)`, QCC registry) while
the evidence concerns the *operating* unit (运行单位), and both cells are blank on the live
operators/owners tab, so nothing is at risk of being overwritten.

No staged value, ref, class or tier was altered on any research shard. Adjudication of the
Phase I/Phase II operator split is Baird's, once for the cohort.

## Root cause of the three `CONFIRMED` silent-drops — a defect in our own BRIEF

`BRIEF.md`'s record contract listed `class_out` as
`REFS_ADDED | CONFIRMED | UNRESOLVED | DEAD_LINK`. `CONFIRMED` is **not** a ref class:
`build_ref_workbook._ORDER` is `["REFS_ADDED", "REVERIFIED", "DEAD_LINK", "UNRESOLVED"]`,
so every agent that followed the brief literally produced records that would be dropped
from the workbook with no warning. Three did (batch_06 #22, batch_03 #13 and #14).

The agents were not careless — they followed the spec we handed them. Fixed in `BRIEF.md`
so the follow-up pass cannot repeat it, and `validate_shards.py` now fails the batch on any
non-sentinel record whose `class_out` is outside `_ORDER`, so the defect cannot ship
silently again even if a brief regresses.

## 2026-09-02 — `jskedun.com` bare-host citation: 4 records stripped, 1 finding filed

**What.** `http://jskedun.com` appeared as a `proposed_ref` in four P4934 records
(batch_14 #2 Capacity, #4 Diameter, #7 SegmentCost; batch_16 #5 SegmentCost), three of
them staged `REFS_ADDED` at `high`/`medium`, each with a `verifications` entry recording
`ok=true, contains_value=true`.

**Why it is wrong, twice over.** (1) It is a **bare host**, not a document URL — the
Egypt EOG navigation-surface defect (`notes/escalation-2026-08-27-egypt-eog-navigation-
surface-citations.md`). (2) The site does not contain the values. It is 江苏科盾管道建设
工程有限公司, a cathodic-protection **contractor's marketing site**; its homepage, all
four 科盾学院 sections and all ten 天然气智库 articles were fetched and searched for
`1250` / `300亿` / `1219` / `1016` / `西气东输` — **zero hits** (the only WEP-adjacent
article is about a Guangdong LNG outbound line). The recorded verification was never a
real read.

**Done.** Ref + verification removed from all four; re-graded:
`Capacity` high→`medium` (1 surviving ref), `Diameter` `medium` (1), batch_14
`SegmentCost` → `UNRESOLVED`/`presumed` (0, and superseded by batch_16 anyway),
batch_16 `SegmentCost` `REFS_ADDED` with 2. `independent=False` on all four.

**Repo-wide check:** every shard scanned for bare-host and navigation-surface refs —
these 4 were the only instances, 0 elsewhere.

## 2026-09-02 — P4934 SegmentCost: independence corrected, scope mismatch filed

batch_16 graded the 125bn RMB figure `high`/`independent=true` on two refs it called
"independently-authored, no shared boilerplate". Both are **reprints whose explicit
source lines were not checked**: `cup.edu.cn` says 来源：**中国石油报** (PetroChina's own
house newspaper) and `chinanews.com.cn` says 来源：**经济参考报**. Two outlets, one
origin — PetroChina's announcement of its own project's investment. → `medium`,
`independent=False`. Rule: **read the attribution line; "differently worded" is not an
independence test.**

Separately filed as a `__VALIDITY__` on P4934 (batch_99): the source defines 1250亿元 as
the total for *1 trunk + 8 branches + **3 gas storages + 1 LNG peaking station***, so
GEM's SegmentCost plausibly overstates the pipeline's cost. **A new shape of the
aggregate-vs-segment hazard**: the row genuinely is the whole system, so the
system-vs-segment test passes — but the *source's* system is broader than GEM's. No
value changed.

**Not a defect:** `SegmentCostUnits = RMB` is the gas tab's own convention (601 rows).
The dispatch prompt said `CNY`; the prompt was wrong, the shards were right.

## 2026-09-02 — attribution audit across all `high` + independent records

Generalizing the P4934 lesson, all **66** records graded `tier=high` +
`independent=true` were audited. All carry >=2 refs (merge QC already enforces the
count). The reprint risk concentrates where **both** refs are news-class hosts — a
government approval paired with a news report is two origins; news + news may be one
wire. **18 such records** were isolated and the three riskiest patterns tested by
fetching both sides and measuring 12-gram overlap on the CJK body:

| pair | verdict |
|---|---|
| P4931 `Start` — sina 7x24 + bjd, both 2025-09-26 | **ONE origin.** bjd carries `来源：央视新闻客户端` (CCTV News); sina is a 333-char newsflash of the same announcement. → `medium`, `independent=False`. |
| P4928 ×5 + sentinel — chinanews + fznews, both 2016-12-12 | **Left as high.** 20.8% overlap, different lengths (3692/1649 chars), fznews self-attributes to 福州新闻网. Two newsrooms covering one commissioning, not a reprint. Borderline; flagged, not changed. |
| P4786 `Fuel` — thepaper/baijiahao + 163/dy | **Left as high.** 0.0% overlap — genuinely different documents (a 赣南日报 county piece vs a self-media repost of the Jiangxi 2021 key-projects list). Weak source *types*, but two origins. |

**Rule this establishes: read the `来源` line before claiming independence.** Wording
differences are not an independence test; a reprint says who it is reprinting.
Remaining 12 news+news records rest on refs separated by years (e.g. cpnn 2021 +
bjd 2025), so a shared wire is not possible.

## Validator hardened: citation FORM is now a gate (2026-09-02)

Four records this batch carried something that is not a fetchable URL in a citation
field, and nothing downstream would have caught it — `merge_ref_shards` copies
`proposed_refs` through verbatim, so the string lands in the `[ref]` cell and the
researcher cannot re-verify it:

- prose *inside* a URL (`'https://www.sohu.com (2021 Jiangxi 14th-FYP provincial
  project roster, energy infrastructure section, items 25-26)'`) — batch 18 ×3
- an angle-bracketed description in place of a link — batch 03 #25
- a **bare host** (`http://jskedun.com`) — batch 14 ×3 + batch 16 ×1, the site-root
  form that is the same defect as Egypt's `egyptoil-gas.com` navigation-surface
  citations (`notes/escalation-2026-08-27-…`).

`validate_shards.py` now hard-fails on both shapes, over `proposed_refs` **and**
`verifications[].url`: not `http`-prefixed, an empty or space-bearing `netloc`, or a
path of `/` with no query. All four were repaired before the gate went in, so it reports
clean — it exists so the next batch cannot ship one silently.

Same pass, the duplicate check was made honest rather than noisy. All 94 duplicate units
are v1 records deliberately re-researched by a followup batch, and `merge_ref_shards`
walks shards lexicographically, so `batch_18` lands last and wins — that is the design.
Those are now a **note**; a duplicate whose last writer is *not* a followup batch, or one
appearing 3+ times, stays a hard failure, because there the winner is decided by filename
luck. Verified: 0 of 94 fall in that class, and none appears more than twice.

## The v1 sweep's one real fill was invisible to the build (2026-09-02)

`carry_prior.py` folds the superseded 08-26 sweep's `REFS_ADDED` onto this run's units.
A **FILL** cannot land on a unit — the worklist owes a `[ref]` only where a value already
exists, so a fill (blank cell + proposed value) matches no key — and `carry_prior` handles
that correctly, routing fills to `carried_fills.json` rather than reporting them as lost.

What nothing handled is the **consumer side**. `build_ref_workbook.py:1468` reads
`pending_fills = actions.get("fills", [])` — an **actions packet** (§6 handoff), never
`carried_fills.json`. On a standalone deep-sweep build there is no actions packet, so the
file is written, counted by nobody, and read by nobody. The only consumer grep finds is
`counts["carried_fills"] = len(pending_fills)`, which counts the *actions* list.

v1's 9 `class_in: FILL` records were 8 `UNRESOLVED` with empty `values` plus **one real
fill**: **P4788 `Pressure [ref]` = 6.30 MPa**, `REFS_ADDED`, tier `low`, sourced to the
Quannan EIA PDF at `设计压力6.3MPa` for the 信丰-瑞金段 section by name. Re-checked against
the 2026-09-02 snapshot: the cell is still blank, so the fill is still owed.

Re-injected as `shards/batch_19_carried_fill.json` with `kind: FILL`, so it flows through
`split_shards`' fills lane like any other fill. Two corrections applied on the way:
- `sheet_row` 2679 → **2677** (the gas tab re-sorted between the two pulls; a carried
  record never keeps its old locator).
- Its URL re-verified per the standing rule — **HTTP 403**, an access failure on
  `quannan.gov.cn`, not a deletion, and the same 403 the other 24 verifications against
  this document in this batch carry. `ok`/`contains_value` stay true on the local read.

Generalisable: **a file written by one stage and read by none is a silent loss.** Reconcile
the count (`class_in FILL: 9 → 1`) rather than trusting the stage that reported "wrote 1
prior fill(s)".

## Three defects surfaced by the batch_20 Wayback recovery (2026-09-02)

The recovery pass re-worked two rows that six earlier shards had already touched. Nothing
about the research was novel; what it exposed is that this repo's silent-loss family has a
**silent-DUPLICATION** and a **silent-MISRENDER** twin. Each was found by reconciling a
count, not by an error.

### 1. `split_shards` appended every `__STATUS__` — a row collected contradictory verdicts

The ref lane keys on `(pid, ref_col)` and lets the last shard win. `__STATUS__` did not: it
`.append`ed. So P5865 reached `Gas_StatusReview` **three times** — `stale` from a batch-06
dormancy inference, `unclear` from the batch-17 followup, `change` from batch 20 once the
blocked source was actually read — with nothing marking which was current. No record is
lost; the reader simply cannot tell a superseded verdict from a live one, which on a
status-change tab is the more dangerous failure.

**A row has ONE status, so it gets ONE verdict**: last shard wins, and supersessions are
printed rather than swallowed (4 here: P4786×1, P5865×2, P5866×1). `__VALIDITY__` and
`__REDUNDANCY__` are deliberately NOT deduped — a row can legitimately carry several distinct
concerns. Status reviews moved 16 records → 12 verdicts.

### 2. A proposed value on a ref-lane record never tints — and reads as the sheet's own

`build_ref_workbook._backend_view` colors a value cell only when `class_in` is `FILL` or
`STATUS`; a ref-leg record's `values` are *current-sheet context*, overlaid untinted. Both
of batch 20's value corrections were written into `Location [ref]` records, so on
`Gas_Backend` — the primary paste surface — `Fengcheng` (P5865, correcting `Yifeng`) and
`Jiujiang` (P5866, filling a blank) printed **untinted, i.e. exactly as if the sheet already
said them**. That is worse than invisible: the workbook legend reserves a tinted value cell
for a proposed value, so an untinted one is a positive claim that nothing changes here.

Re-filed as the pattern the workbook already supports and documents (`_merge_ref_unit`): the
ref record carries the **sheet's current values**, a `kind: FILL` twin on the same cluster
carries the **proposed** value, and both records' refs are unioned onto the one `[ref]` cell.
`validate_shards` now keys duplicate detection by **lane**, so that designed pair reads as a
note instead of an "AMBIGUOUS duplicate unit" — which also surfaced the pre-existing pair on
P5862 `Operator [ref]`.

Rule: **if a shard proposes a value, the record that carries it must be in a lane that
tints.** Check the tint, not the store.

### 3. Every `Gas_Validity` row shipped with blank name columns

`harvest_sentinel_findings` reads `pipeline_name` off the shard **doc** and hardcoded
`segment_name` to `""`; `split_shards` wrote `{project_id, resolutions}` and nothing else. So
26 of 26 validity findings — the tab carrying a sweep's highest-value output — reached Baird
with a bare ProjectID and two empty name columns. Fixed at the cause in both scripts
(`split_shards` stamps identity onto each `ref_shards/<PID>.json`; the harvester reads the
record first, the doc second). The `harvest_sentinel_findings` change is repo-wide and only
fills what was previously an empty string.
