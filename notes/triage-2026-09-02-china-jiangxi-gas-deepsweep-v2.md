# Triage — China / Jiangxi gas, FULL province sweep (deep + in-dev), v2

**Date:** 2026-09-02 · **Scope:** China, gas, **all statuses**, **44 rows** ·
**Batch dir:** `batches/china-jiangxi-gas/`, staging `staging/deepsweep-20260902/`
**Supersedes:** `staging/deepsweep/` (delivered 2026-08-26, staged never applied) —
archived at delivery, not before; its records are an INPUT to this run.

Baird's ask (2026-09-02): the 08-26 pass "wasn't very comprehensive", and this one is to
"include any trunk lines and things." Scope answers taken the same day: **44 rows**,
**carry the good refs and re-research the unresolved**, **add `status-review`**;
OSM, `routes` and `discovery` legs explicitly NOT run.

---

## Why v1 was thin — measured, not asserted

The 08-26 workbook is not wrong; it is **narrow**, and the narrowness is quantifiable:

| measure | v1 result |
|---|---|
| distinct URLs behind the whole batch | **15**, across 18 rows |
| concentration | 3 documents carry **71 of 98** `REFS_ADDED` (DRC plan rehost 39, huaon 16, SSE bond 16) |
| tier distribution | `high` **18** · medium 73 · low 7 · presumed 88 |
| rows with ZERO sourced ref | **2** (P5859, P5862); 2 more got exactly one |
| harvested citations never opened | **18 readable**, incl. two live `jiangxi.gov.cn` 能源局 approval documents |
| legs run | 4 of 7 — no `status-review`, no `routes`, no `discovery`, OSM deferred |
| fan-out | 5 batches × ~4 rows |

**Root cause, and it is a design flaw not an execution one:** the subagent payloads seeded
the *wiki-attributed candidate set* and asked agents to verify it. 26 candidate URLs, 33 of
them behind one WAF-blocked registry (`m.qcc.com`), so the budget went to confirming a small
closed set instead of searching for a new one. When Wayback then went dark host-wide all day
(`archive.org` API fine, `web.archive.org` timing out at 0 bytes — the same condition
Uzbekistan hit that day), the fallback path died too and every blocked ref stayed unremedied.

v2 inverts that: the candidate set is a **floor to clear, not a ceiling to verify**.

---

## Scope derivation — 41 by terminus, 44 with the transiting parents

Jiangxi has **41 rows** by the `--province` rule (either terminus in-province), not the 29
v1 counted from the operating filter:

| group | rows | statuses | v1 |
|---|---|---|---|
| `江西输气管网` provincial grid | 28 | 18 operating · 4 construction · 5 proposed · 1 shelved | only the 18 operating |
| national trunks terminating in Jiangxi | 13 | 11 operating · 1 proposed · 1 cancelled | **excluded** (MZ's locked lane) |

The 13 trunks: WEP2 ×8, WEP3 ×2, 川气东送一线 ×1, 川气东送二线 ×1, 新粤浙 ×1.

**Plus 3 rows selected on GEOMETRY, not termini.** Tested every China gas row's route
against the Jiangxi admin-1 polygon: exactly three cross the province with neither endpoint
in it, and all three are the national **parent** rows sitting above the in-scope branches —
**P4657** (川气东送一线 trunk, 1,628.64 km), **P4934** (WEP3 mainline, 7,378 km), **P4947**
(WEP2 mainline, 9,102 km). Baird's call 2026-09-02: **include them.** They carry the
aggregate-vs-segment question one level above P4777, and **all three have zero refs on any
column** (28 owed units, 28 `MISSING_REF`).

**Total: 44 rows / 411 owed units** (383 by terminus + 28 on the three parents).

### Two consequences to write down

1. **Six trunk rows are cross-province and this batch CLAIMS them** — P4661 (Anhui),
   P4752 (Fujian), P4928 (Fujian), P4931 (Ningxia), P4944 (Shanghai), P4946 (Hunan), plus
   all three mainline parents. A later Fujian / Hunan / Anhui / Shanghai / Ningxia sweep
   must exclude them or two staged records will point at one sheet cell and the last
   workbook pasted wins silently (the Uzbekistan↔Kazakhstan lesson). Emit
   `batches/china-jiangxi-gas/claimed_rows.txt` **at delivery**, derived from this run's
   `staged_resolutions.json`, never hand-typed, and note it in `docs/country_notes/china.md`.
2. **The 13 trunks + 3 parents are MZ's locked lane.** Baird has authorized researching
   them; that is a *scope* decision, not a licence to edit her lane's artifacts. Routes stay
   untouched (no `routes` leg) and wiki-page defects stay flagged, never fixed. **Confirm the
   overlap with Maggie before the fan-out launches** — she is mid-cycle on the trunk rows and
   a same-week edit collision on the live sheet is the one failure mode staging can't catch.

---

## What v2 does with the 18 rows already swept

Not a re-run from scratch, and not frozen. **Carry and deepen:**

- The **97 `REFS_ADDED` ref units are carried forward** into the new store, each **re-verified
  through `url_verifier`** (hard requirement: every URL is re-checked even if it worked in a
  prior batch) and tagged `carried_from: deepsweep@20260826` so the workbook shows at a glance
  what is new work versus preserved work.
- The **65 `UNRESOLVED` ref units are re-opened as first-class research targets**, with the v1
  attempt handed to the agent as *what was already tried and why it failed* — so budget goes
  to new avenues, not repeated ones.
- The **15 `__VALIDITY__` sentinels and 9 fills carry forward unchanged**; the three findings
  v1 corrected mid-flight (P4777 shape, P4788 attribution, P4788 DMS coordinates) travel as
  settled context so no agent re-derives them.

Real research targets: **65 (reopened) + 221 (new province rows) + 28 (parents) = 314 units**,
against 97 carried-and-reverified.

---

## Legs

| leg | run? | why |
|---|---|---|
| `refs` | **yes** (base) | 354 of 411 units have no ref at all — a 92.4% gap |
| `fills` | **yes** | 6 blank `LengthKnown` on grid rows + blanks across 23 unswept rows |
| `validity` | **yes** | existence / duplicate / classification; the trunks bring a new aggregate question |
| `status-review` | **YES — new** | 12 rows are non-operating and v1's operating filter never saw them |
| `recon` (gulfpub) | **yes, re-scoped** | trunks in scope changes the answer — see below |
| `recon` (osm) | no | Baird's call; `fetch_overpass` is `--iso`-scoped, a whole-China pull |
| `routes` | no | MZ's locked lane; the 7 length divergences ship as `__VALIDITY__` flags |
| `discovery` | no | Baird's call |

### The `status-review` leg is the highest-yield new surface

Twelve rows, most untouched for two years:

| PID | segment | status | last touched |
|---|---|---|---|
| P4786 | Ganzhou South Br. (Huichang–Xunwu) | **shelved** | 2023-08-30 |
| P4785 | Ganzhou South Br. (Dayu–Xinfeng) | proposed | 2023-08-30 |
| P4790 | Jingkai–Jishui–Yongfeng–Le'an–Yihuang | proposed | 2023-08-31 |
| P4792 | Yifeng–Tonggu Branch | proposed | 2023-08-31 |
| P5863 | Ganzhou–Fengxin Branch | proposed | 2024-10-03 |
| P5886 | Shenguili–Pengze Branch | proposed | 2024-10-04 |
| P4787 | Ganzhou South Br. (Longnan–Quannan) | construction | 2024-09-26 |
| P5860 | Yudu–Ningdu–Guangchang–Nanfeng | construction | 2024-10-03 |
| P5865 | Zhangshu Branch | construction | 2024-10-04 |
| P5888 | Wanzai–Tonggu Branch | construction | 2024-10-04 |
| P4661 | Anqing–Poyang Branch (川气东送二线) | proposed | 2025-08-19 |
| P4752 | Jiangxi–Fujian–Zhejiang Branch (新粤浙) | **cancelled** | 2023-08-19 |

A `construction` row last verified in Oct 2024 on a ~60 km branch is a prime `stale` verdict —
these lines commission in 18–24 months. **The 08-26 batch already has local evidence bearing
on two of them**: an unopened `jiangxi.gov.cn` 能源局 approval-variation notice covering the
Yudu–Ningdu–Guangchang–Nanfeng branches (P5860), and a 竣工环境保护验收 (completion
environmental acceptance) screenshot for the **Ningdu–Guangchang segment** — a completion
acceptance is close to dispositive for `operating`.

### GulfPub recon: adding the trunks changes the result

Re-scoped the existing China crosswalk against the 44 PIDs. v1 found **1** apparent overlap
and hand-dispositioned it as a false positive. v2 finds **3**, and the two new ones are real:

    P4931  Middle Section (Zhongwei–Ji'an)   ← GulfPub "West - East Pipeline II"  yellow 0.685
    P4928  East Section (Ji'an–Fuzhou)       ← GulfPub "West - East Pipeline II"  yellow 0.701
    P4782  Nanchang–Fengcheng                ← GulfPub "Cang-Zi Line"             yellow 0.475  FALSE_POSITIVE (v1, ~1,240 km apart)

**GEM files both as 西气东输三线 (WEP3); GulfPub names them West-East Pipeline II.** That is a
line-identity disagreement on the two largest in-scope rows (2,090 km and 817 km) and it is
the batch's first real recon question — adjudicate it, don't assume GulfPub is wrong.
Separately, the actual mainline parents **P4934/P4947 sit in `gem_only`** while GulfPub's
mainline record matched the *Jiangxi segments* instead — a granularity observation worth
recording, not a matcher defect.

Re-scope with `scope_recon_crosswalk.py` again: `build_recon_crosswalk.py` does **no
ProjectID filtering**, so unscoped it hands the reviewer 118 out-of-scope China decisions.

---

## The comprehensiveness fixes — this is the part that makes v2 different

**1. A source-diversity floor, enforced at merge.** No row ships with fewer than **2 distinct
origin hosts** unless its record says in prose why not. Add a pre-delivery check that counts
distinct hosts per PID and per unit; v1 would have failed it on 4 of 18 rows. Corollary: a
document already carrying ≥15 units in this batch (the DRC plan, the SSE bond) **cannot be
the second source** for a `high` tier — it is one origin restated.

**2. The harvested pool is a worklist, not a lookup table** (Uzbekistan rule, 2026-08-27).
Each agent **reports how many harvested citations it opened**, and an unopened citation on a
row with an owed cell is an open item, not a silent pass. v1's 18 unopened readable URLs go
into v2's pool as pre-screened targets — including the two `jiangxi.gov.cn` approval notices
and the `china5e` / `ichinaenergy` articles naming the Jinggangshan and
Jingkai–Jishui–Yongfeng branch lines.

**3. A named document ladder, because "search in Chinese" was too vague.** v1's agents mostly
searched news. The document classes that actually settle these rows:
   - **省能源局 / 省发改委 核准批复 and 核准变更批复** (`jiangxi.gov.cn/art/...`) — per-project
     approvals carrying length, diameter, investment. Two are already in hand, unopened.
   - **环境影响评价 (EIA) 拟批准公示 and 竣工环境保护验收** — the acceptance documents are the
     single best `operating` evidence for the in-dev leg, and they carry as-built lengths.
   - **市/县 政务公开 + 人大建议答复** — municipal replies that name the segment and its schedule.
   - **招投标 / 评标结果公示** — tender awards, which date construction starts.
   - **江西省天然气集团 / 江西省投资集团 disclosures + bond prospectuses** (CCXI, SSE) beyond the
     one already used; **PipeChina / CNPC / 中石油 annual and project disclosures** for the trunks.
   - **江西统计年鉴 / 江西省能源发展规划 (十四五)** — the 2022 十四五 energy plan is already in the
     unopened pool.
   Trunk rows have their own class: national EIA, PipeChina segment commissioning releases,
   provincial 输气管道 completion notices. **They are NOT served by the provincial DRC plan.**

**4. Wayback retry, on a different day.** v1's Wayback failure was a network condition, not a
finding — today is 7 days later. Re-run `wayback_serial.py` (serial, ≥1.5 s pause, `id_`
byte-confirmation) **before** the fan-out, so agents get real snapshot availability instead of
a wall of timeouts. **No "no snapshot archived" conclusion from v1 is admissible.**

**5. Two `url_verifier` cautions carried in.** The Chinese WAF/challenge phrases were added
2026-08-26, so `m.qcc.com`'s HTTP-200 block page is now caught rather than passing as clean
prose. And prove a suspected **soft 404** by fetching a nonsense sibling slug and diffing the
bodies (the `utg.uz` method) — `news.cnr.cn` already showed this behaviour on one path.

**6. Shard-authoring contract, stated up front.** A hand-confirmed false negative must be
encoded `ok:true, contains_value:true` **with the evidence in `note`** — prose in an `ok:false`
record is stripped by `merge_qc.verified_refs` and then honestly downgraded to `UNRESOLVED`,
so a found source reports as *no source found*. This cost v1 eleven records on its highest-yield
batch before it was caught.

---

## Tooling to close before the run

1. **`build_ref_worklist.py --include-pids`** — symmetric with `--exclude-pids`, same
   comma-list-or-`@file` parsing. Required for the three transiting parents (`--province`
   selects on termini by design), and it will recur on **every** China province sweep, since
   every province has mainline parents crossing it. Small, generalizes; not a batch-local hack.
   *(Usage note while we're here: `--exclude-pids` needs the `@` prefix for a file — a bare
   path parses as one literal PID and silently excludes nothing.)*
2. **Promote `attribute_wiki.py` to `scripts/`.** It parsed 29 `h3` sections into 100
   per-unit attributions mechanically, and every China province wiki page has this shape. The
   page-level harvester only reports that a citation is used *N* times, never *where*.
3. **A batch-local carry step** (the `split_shards.py` pattern): overlay v1's `REFS_ADDED`
   records onto the fresh seed, keyed `(project_id, ref_col)`, re-verifying each URL and
   stamping `carried_from`. Written and reconciled by count before the fan-out.

---

## Sequence

```bash
STG=batches/china-jiangxi-gas/staging/deepsweep-20260902

./scripts/refresh_csvs.sh                       # MANDATORY — 08-27 snapshot is stale; MZ edits live
python scripts/build_ref_worklist.py --tracker gas --country China --province Jiangxi \
  --include-pids P4657,P4934,P4947 --verify-existing --out $STG/worklist.json
python scripts/harvest_wiki_citations.py --worklist $STG/worklist.json --out $STG/wiki_citations.json
python scripts/attribute_wiki.py --staging $STG/          # after promotion
python $STG/wayback_serial.py                             # retry, different day
python scripts/seed_resolutions_from_worklist.py --staging $STG/
python $STG/carry_prior.py --from batches/china-jiangxi-gas/staging/deepsweep/   # re-verify + stamp
python scripts/build_deepsweep_args.py --staging $STG/ --status-review
#   → Workflow({ name: 'critical-deep-sweep', args: <JSON> })  ~11 batches × 4 rows,
#     model chosen at dispatch (cheapest genuinely sufficient), one shard per PID
python $STG/split_shards.py
python scripts/merge_ref_shards.py --staging $STG/
python scripts/merge_deepsweep_shards.py --staging $STG/
python scripts/harvest_sentinel_findings.py --staging $STG/     # LAST — see run-order note
python scripts/reconcile.py --source gulfpub --country China --commodity gas --staging $STG/
python scripts/build_recon_crosswalk.py --sweep-dir $STG/ && python $STG/scope_recon_crosswalk.py
python scripts/recalc.py && python scripts/build_ref_workbook.py ...
```

**Run order is not cosmetic.** `harvest_sentinel_findings.py` runs **LAST**:
`merge_deepsweep_shards` re-folds by purge-and-rebuild and drops every `__VALIDITY__` /
`__STATUS__` / `__ROUTE__` record, so harvest-then-merge zeroes the sentinels silently
(verified 2→0, no warning). Reconcile the merge's WARN count against the harvest count every
time — that reconciliation is what caught all three of v1's silent-loss defects.

---

## Landmines carried forward (do not re-derive)

- **P4788** — `FuelSource` names WEP3 not Sichuan-Shanghai (operator's own emergency plan);
  the redraw anchors in v1's `__VALIDITY__` are **DMS read as decimal** (correct: Xinfeng
  114.82255/25.43558, Ruijin 116.00923/25.94623 — the stated point was 38.7 km off); 340.30 km
  vs 131.8 km between its own terminals leaves length AND route open.
- **P4777** — Phase I network **parent** row, shape closed (DRC plan: 870 km as-built, named
  constituents). Sourcing of the 825.00 figure still open. Do **not** recommend a fold.
- **Name-cell defects, MZ's lane, record never repair** — P4780 holds P4783's Chinese name;
  P4788/P4789 each hold a chopped fragment of one multi-segment string. **Do not search on them.**
- **P4791** — 婺源 romanizes **Wuyuan**; the wiki's "Maoyuan" is wrong.
- **P4778** overlaps **P5861** (WEP2 Xinyu Branch) — and P5861 is now IN scope, so this stops
  being a flag and becomes an adjudicable duplicate question.
- **Route-vs-sheet length, 7 rows** — P5862 30.10×, P5866 6.43×, P5887 2.12×, P4784 1.87×,
  P4783 0.57×, P4788 0.09×; **P4777's 0.07× is expected** (network granularity, not a finding).
- **Host reachability** — `nc.gov.cn`, `cx.jxgzwztb.com` NXDOMAIN; `jxgajc.com`,
  `strq.jxngh.com` decommissioned; `m.qcc.com` WAF `567`; only 3 URLs are confirmed 404 and
  those are the only droppable class.
- **Rule 1 boundary** — GEM's own route geometry may corroborate internally but may never be a
  `[ref]`. That is why v1's 8 unresolved fills are *uncitable, not unknown*, and why the
  route-derived length table travels in the handoff rather than in cells.

## Escalation gates for this batch

Standing gates apply. Two are pre-armed by the scope change: GulfPub's WEP2-vs-WEP3 identity
disagreement on P4928/P4931 is a **material conflict** the moment it touches >10% of matched
rows (3 matches, so 2 of 3 — it clears on ratio and should be read on substance, not the
ratio); and any aggregate finding against P4657/P4934/P4947 is a **whole-class** question
about how GEM segments national trunks, which escalates rather than staging as a row edit.

## Deliverable

`deliverables/pipelines_batch_<stamp>_china-jiangxi-gas_deepsweep.xlsx` — **staged, not
applied.** Tabs: `Gas_Backend`, `Gas_OperatorsOwners`, `Gas_StatusReview` (new),
`Gas_Validity`, `Gas_Fills`, `Gas_GulfPub`, `Gas_Refs_Added`, `Gas_Refs_Unresolved`.
`recalc.py` clean. Pre-delivery gates: 0 gem.wiki in any `[ref]`, 0 abarrelfull, 0 orphan refs
either direction, 0 `high`-tier units with <2 refs, **plus the new source-diversity floor**.
At delivery: archive `staging/deepsweep/`, emit `claimed_rows.txt`, regenerate `INDEX.md`,
update `docs/country_notes/china.md`.
