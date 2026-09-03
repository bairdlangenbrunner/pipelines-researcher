# Triage — China / Jiangxi gas, operating rows (deep sweep)

**Date:** 2026-08-26 · **Scope:** China, gas, `operating`, `江西输气管网` provincial grid —
**18 rows** · **Batch dir:** `batches/china-jiangxi-gas/`, staging `staging/deepsweep/`
**Snapshot:** `data/GGIT_gas_snapshot_20260826.csv` (fresh pull; the 08-12 snapshot was 2
weeks stale and MZ edits the live sheet continuously through Sep 11).

Requested by MZ via Baird. **Jiangxi is not on MZ's sketched province priority**
(Guangdong → Guangxi → Jiangsu → Fujian) — this is an insertion, plausibly because they
reached Jiangxi and found the citation base bare.

## Scope derivation

41 Jiangxi gas rows by either terminus; **29 operating**. Every `江西输气管网` row also
terminates in Jiangxi, so "the province and its provincial network" resolves to one set,
not a union. Split of the 29 operating:

- **18** — `江西输气管网` provincial grid → **this batch**
- **11** — national trunks terminating in Jiangxi (西气东输二线 ×8, 西气东输三线 ×2,
  川气东送一线 ×1) → **excluded**, MZ's own trunk scope per the locked division of labor
  (`docs/country_notes/china.md`). Baird's call 2026-08-26.

## The defining fact: refs exist on the wiki, never carried into the backend

Counting only cells where a ref is **owed** (a paired value exists — the naive "624 blank
ref cells" is an upper bound dominated by `Cancelled [ref]`-type columns with nothing to
cite):

**137 ref-gap units on the 18 rows · 6 already cited · 4.2% coverage.**
Plus **36 blank `Operator [ref]`/`Owner [ref]` units** on the operators/owners tab (0/18
filled). For reference, the 29-row set scores 2.19% raw fill — below Ukraine's 3.29%,
which the project notes flag as 2nd lowest of 52 scopes.

**This is a gap, not the correct outcome.** Provenance check (the SOP's cheap first move):
two researchers (MZ 12, XJ 6) across six dates Aug 2023 → Oct 2024 — incremental human
research, **not** a Pakistan-style cartographic bulk load. So calibrate this like **India,
not Pakistan**: an `UNRESOLVED` here is a weak result, and the legs should move a large
block off it.

All 18 rows point at **2 wiki pages** (17 → `Jiangxi_Natural_Gas_Pipeline_Network`,
P4789 → `Jinggangshan_Branch_Line,_Jiangxi_Gas_Pipeline_Network`). The shared page has
**29 per-segment `h3` sections** (bilingual, grouped Phase I / Phase II), each carrying a
field-labeled bullet list with **per-field superscripts**. Yield across 27 sections:

| wiki bullet | → GEM ref column | sections w/ value+ref |
|---|---|---|
| Owner | `Owner [ref]` (OO tab) | **27 / 27** |
| Operator | `Operator [ref]` (OO tab) | **26 / 26** |
| Status | `Status [ref]` | 26 / 27 |
| Length | `Length [ref]` | 19 / 27 |
| Diameter | `Diameter [ref]` | 17 / 27 |
| Capacity | `Capacity [ref]` | 14 / 27 |
| Start year | `Start [ref]` | 14 / 27 |
| Cost | `SegmentCost [ref]` | 13 / 27 |
| Parent company | (no direct column) | 1 / 27 |

~156 cited field-instances against 137 + 36 gap units. The page also carries **owner
percentages** (e.g. 54% / 46%) where the sheet has the `--` sentinel on 17 of 18 rows.

**The ceiling on that block:** most Owner/Operator superscripts resolve to ONE citation,
`m.qcc.com` (企查查 registry, **54 backlinks**). One source = single-source/yellow at best,
and a registry site likely bot-blocked from here. GEM's existing use of archive.org
*screenshot* items on these rows suggests they already hit this wall.

## Plan

`deep` preset (refs + fills + validity + recon), with two deliberate deviations:

- **Drop the `routes` leg** — routes are MZ's locked lane, and `RouteAccuracy` is already
  medium-or-better on 14/18.
- **GulfPub recon only; defer OSM.** GulfPub carries China trunks only, so ~0 overlaps is
  expected against provincial-grid rows — run it as a cheap recorded negative.
  `fetch_overpass.py` takes `--iso`, not a province, so a whole-China gas pull for 18 rows
  is poor value. Deferred, not silently skipped.

1. **Worklist + harvest.** `build_ref_worklist.py --tracker gas --country China --province
   Jiangxi --exclude-network-regex '^(?!.*输气管网$)' --status operating --verify-existing`,
   then `harvest_wiki_citations.py`.
2. **New: per-section wiki attribution.** Batch-local script parsing each `h3` segment
   section → bullet label → `(PID, ref_col)` candidate citation, joining sections to PIDs on
   the Chinese segment name + endpoint pair. The existing harvester is page-level only:
   `backlinks: 54` says a citation is used 54 times, not *where*. Promote to `scripts/` if it
   generalizes — every China province page has this shape.
3. **Verify.** `url_verifier` on every attributed URL, requiring `ok && contains_value`.
   Expect `m.qcc.com` to fail → Wayback snapshot; archive.org item upload only on an SPN 520.
4. **Fan out** `critical-deep-sweep`, one skeptical subagent per PID (18), model chosen at
   dispatch. Wiki-attributed citations seed the candidate set so subagent budget goes to
   corroboration and to the value/existence questions, not rediscovering refs.
5. **Merge:** `seed_resolutions_from_worklist.py` → `merge_deepsweep_shards.py` →
   **`harvest_sentinel_findings.py`** (mandatory — validity verdicts are otherwise dropped
   with a WARN, and they are the highest-value findings) → reconcile the WARN count.
6. **GulfPub recon** → crosswalk tab.
7. **Build + `recalc.py`** → `pipelines_batch_<stamp>_china-jiangxi-gas_deepsweep.xlsx`.
   **Staged, not applied.**

## Flags carried into the batch

- **P4777 is a NETWORK-GRANULARITY parent row, not a Kazakhstan-style double count.**
  *(Corrected 2026-08-26 during execution — the original "probably an aggregate / 825.00 vs
  993.80 km" framing was wrong, because that 993.80 summed Phase I and Phase II together.)*
  The wiki's `Phase I` `h3` is a **container heading**: its `<ul>` lists the 18 constituent
  segment names and it carries **no field bullets at all**, which is why P4777 alone attributed
  to nothing. **Now corroborated numerically**: the 12 in-scope rows whose `SegmentName` carries
  `Phase I` sum to **798.74 km** of merged length, and adding the two unlabelled branch rows
  (P5887, P5889) gives **853.36 km**. The sheet's 825.00 km sits *inside* that band (-3.2% /
  +3.4%), so 825 km is the Phase I **system total** and the row is the parent — a shape
  `gem_schema.md` explicitly supports. The **shape** question is therefore closed; the
  **sourcing** question is not, and a fold/delete recommendation without a source would still
  repeat the Kazakhstan cluster-A error.
  *Constraint on that arithmetic:* it leans on `LengthMergedKm`, which for the 6 blank-length
  rows is route-derived — i.e. **GEM's own geometry**. Per standing rule 1 that can corroborate
  internally but can **never** be a `[ref]` (the Egypt P8063/P8065/P8066 precedent: empty
  `Route [ref]` by design, provenance in `RouteNotes`).
- **P4778 (Gao'an→Xinyu) overlaps out-of-scope trunk P5861** (WEP2 XinYu Branch, 高安-新余).
  Flag only — P5861 is MZ's scope.
- **P5861's `Wiki` cell is malformed** — a stray superscript marker pasted into the URL
  (`…新余支线（高安-新余）[21]`). Out of scope; route to MZ.
- **NEW: `LengthKnown` and the row's own route geometry disagree by >2x on five rows.**
  Either the sheet length or the attached geometry is wrong, and at `medium` `RouteAccuracy`
  both cannot be right: **P5862** 18.45 km vs a 553.78 km trace (**30x**), **P4788** 340.30 vs
  31.75 (**10.7x**), **P5866** 19.12 vs 123.15 (**6.4x**, `very low`), **P5887** 23.30 vs 49.27
  (2.1x), **P4784** 138.00 vs 258.13 (1.9x). P5862's 30x is the sharp one — a 554 km trace on a
  row claiming 18 km reads like whole-network geometry attached to a spur. These route OUT as
  `__VALIDITY__` findings rather than fixes: **routes are MZ's locked lane** and this batch
  deliberately dropped the `routes` leg. All 18 rows *are* clean on the three-way sync rule
  (`RouteType` = `Mapped route (at any accuracy)` throughout, no violations).
- **`web.archive.org` is unreachable from this machine today — every Wayback result from this
  pass is void.** *(Diagnosis CORRECTED 2026-08-26; see the retraction below. The original
  reading — that a 17-query CDX sweep rate-limited our own IP — is WRONG.)* Either way the
  "0/17 usable captures" CDX result is an **artifact, not a finding**, and it (plus the P4791
  `Status`/P5864 `Route` timeouts) had to be re-run serially with a pause. This is the sweep SOP's own documented rule at `docs/sops/sweep.md:200` —
  never fan out verification at web.archive.org. Access failure, never deletion.
  *Redone 2026-08-26:* `cdx_snapshots.py` retired to `cdx_snapshots.VOID.json` and replaced by
  `wayback_serial.py` — one request at a time, 5 s pause between every one, availability API
  first with CDX only as fallback, and each returned capture confirmed by re-fetching its raw
  bytes through the `id_` modifier (CLAUDE.md's archiving rule, because SPN's interstitial
  returns HTTP 200 having captured nothing). **The throttle has NOT lifted** — the serial pass
  still `ConnectTimeout`s, so Wayback remains unresolved for this batch and every affected ref
  stays KEPT-with-access-failure. Retry later; do not read the timeouts as "no capture exists" —
  and the full 16-URL serial pass (log: `wayback_serial.log`) proves that reading is wrong. It
  ran to completion at 0/16 confirmed, but **entries 6 and 7 failed at a LATER stage than the
  other fourteen**: the availability lookup SUCCEEDED and returned a capture for
  `jxgajc.com/Hr/show-7403.aspx` and for `quannan.gov.cn/qnxxxgk/zdsjbg/…`, and only the `id_`
  byte-confirmation timed out. So captures demonstrably exist for at least those two; the run is
  blocked on egress, nothing about the source. Do not let a later pass conclude "no snapshot"
  from a `LOOKUP FAILED` line.
- **RETRACTION — it was never our rate limit.** Probed directly: `archive.org` returns **200 in
  0.7 s** (root) and the availability API answers `jxgajc.com/Hr/show-7403.aspx` in **1.6 s**
  with a real capture (`20221002084617`), while **every** `web.archive.org` path times out at
  **0 bytes** — the `id_` raw fetch, the plain `/web/2020/` form, and the CDX endpoint, *including
  a trivial `example.com` lookup we could not conceivably have throttled*. So the two hosts are
  split: `archive.org` fine, `web.archive.org` dead, host-wide, regardless of query. That is
  **the identical condition recorded the same day in the Uzbekistan batch** — "`web.archive.org`
  content serving was unreachable all day 2026-08-26 while `archive.org`'s API answered in 0.5 s,
  which is a network condition and **not** evidence about the source" (`docs/country_notes/uzbekistan.md`).
  Two independent batches, different query patterns, same split.
  Consequences: (1) the throttle theory is withdrawn — nothing we did caused this, and the
  self-inflicted-rate-limit reading in the line above was wrong; (2) **retrying later today is
  pointless** — this needs a different day, not a longer pause; (3) `wayback_serial.py`'s serial
  design is still correct practice per `docs/sops/sweep.md:200`, it just was not the remedy for
  this; (4) a subagent's report that "the rate limit cleared" because CDX answered is a **false
  positive** — the availability API clearing says nothing about content serving, and no
  "no snapshot archived" conclusion reached through `web.archive.org` today is admissible.
  Anything in this batch resting on "no Wayback rescue found" must be re-checked on a later day.
- **6 rows have a blank `LengthKnown`** (P4776, P4778, P4780, P4781, P4782, P5859) and most
  of those a blank `Diameter` — the `fills` leg targets.
- **`Owner`/`Operator` read blank, but `QCCOwner(业主单位)` already carries the answer** —
  e.g. P4776 holds `江西省天然气集团有限公司 [54%]; 国家石油天然气管网集团有限公司 [46%]`, and
  those percentages **match the wiki's own 54%/46%**. So the operator/owner work is largely a
  *citation* and column-placement question, not a discovery one. (Sentinel rows are still
  dropped silently by the ref merge — see the SOP's sentinel-harvest step.)
- The wiki page is this batch's main source, but **wiki edits are MZ's lane** — anything
  wrong *on the page* routes to them rather than getting fixed here.

## Execution findings (2026-08-26)

**Wiki attribution worked, and it is mechanical.** `attribute_wiki.py` (batch-local) parsed
29 `h3` sections → **100 attributions across 17 of 18 PIDs, 81 of them landing on units that
are actually owed a ref** — i.e. half the batch's 162-unit gap, before any web research. The
18th (P4777) is the container row above. Promote the script to `scripts/` if the next province
page has the same shape.

**The BACKEND's own citation base, measured (2026-08-26).** `seed_resolutions_from_worklist.py`
put a number on it: of **162 owed ref units, exactly 6 carry a link in the sheet — 3.7%** — and
those 6 sit on just **three rows**. P4784 holds four of them (`Status`, `Pressure`, `Length`,
`Diameter`); P4791 and P5889 hold one each (`Status`). Fifteen of the eighteen rows have **no
citation at all, on any column**. Worse, `--verify-existing` clears only **one** of the six:
P4784's `Length [ref]` REVERIFIED, the other five DEAD_LINK. So the sheet's working citation
base for the whole Jiangxi provincial grid is **one live link**.

That settles the calibration question the plan left open, and it settles it the India way, not
the Pakistan way: **a blank here means nobody has looked yet, not that the fact is unknowable**.
So an `UNRESOLVED` in this batch is a WEAK result to be pushed on, and 156 `MISSING_REF` at the
start is the size of the opportunity rather than the size of the problem. It also means the
"check whether existing refs work" half of the ask has a very small denominator — 6 units, 1
survivor — and the real work is the other half.

**But the citation base is far thinner than the attribution count.** Those 100 attributions
resolve to just **26 distinct URLs**, one of which (`m.qcc.com`, the 企查查 registry) carries
33. Verified verdicts on the 81 owed units: **7 SUPPORTED, 3 live-status-inferred,
9 NOT_SUPPORTED, 62 UNREACHABLE.**

**The unreachable 62 are NOT link rot** — and the distinction is the batch's main technical
result. Measured per host:

| class | hosts | remedy |
|---|---|---|
| **NXDOMAIN** (domain gone) | `nc.gov.cn`, `cx.jxgzwztb.com` | Wayback; no `nanchang.gov.cn` successor answers |
| **resolves, all ports shut** | `jxgajc.com`, `strq.jxngh.com` | Wayback |
| **host up, app-level block** | `m.qcc.com` (WAF `567`), `gas.in-en.com` (403), `zhaoqt.net`, `jndsb.jxnews.com.cn` (TLS), `skxox.com` (stub) | keep ref, add Wayback |
| **confirmed 404 — the only droppable class** | `m.xinhuanet.com/jx/…`, `cnlng.com/…id=19075`, `pipechina.com.cn/…xls` | 3 URLs |

China at large is reachable from here (baidu, sina, sohu, `gov.cn`, `jiangxi.gov.cn`,
`wuning.gov.cn` all 200), so the earlier geo-block hypothesis is **refuted** — these are
host-specific failures and Chinese-language search is worth doing.

**Own-defect fix — `url_verifier._BLOCK_PHRASES` had no Chinese entries.** qcc.com's WAF page
("由于您访问的链接有可能对网站造成安全威胁，您的访问被阻断") returned `_blocked_as() == None`,
so any Chinese block page served under HTTP 200 verified as clean prose — the same false-PASS
family as the `energybase.ru` case already documented in that file, and it affects every China
province sweep (Guangxi shipped, the GGIT China cycle queued). Ten Chinese WAF/challenge
phrases added 2026-08-26; the block page is now caught and real prose is not.

**Blast radius measured, and Guangxi is CLEAN.** All 34 `.cn` URLs banked `ok=True` in
Guangxi's `deepsweep-pilot` (648 resolutions) were re-verified serially against the patched
phrase list: **0 blocked-now, 33 still ok, 1 access failure**. The one failure is
`gdee.gd.gov.cn/attachment/0/393/393845/3008234.PDF` — a Guangdong government PDF attachment
returning no status at all, i.e. the documented large-PDF/gov-host false-negative family, an
access failure and **not** a deletion. So the defect was real but never *fired* on Guangxi;
its workbook stands. The fix's value is prospective — it protects this batch (where qcc.com
does serve a 200 WAF page) and the queued China cycle.

**Wiki-side defects to route to MZ** (page edits are their lane, not ours):
- P4791's segment is `Leping-Dexing-Wuyuan` in GEM but `Leping-Dexing-Maoyuan` on the wiki.
  婺源 romanizes as **Wuyuan** — the wiki is wrong.
- One citation is a `web.archive.org/save/…` **Save-Page-Now instruction endpoint**, which is
  never evidence (the defect class behind the 348 repaired in Aug 2026).

## The unlock: two primary documents (2026-08-26)

**`江西省天然气利用规划 (2013-2020)`, 赣发改规划〔2014〕325号 — the Jiangxi DRC's own plan.**
Its `省级天然气长输管道` passage is the document this batch needed:

> 承接**川气东送**工程气源的江西省天然气管网**一期工程已建成管道 870 公里**，主要建成
> **九江—南昌、九江—沙河、九江—景德镇、南昌—丰城、高安—新余、丰城—抚州 6 条干线**和
> **田南—上高支线**。…**二期工程已建成管道 98 公里**（吉安首段、赣州首段、安义段 + 宜春、
> 萍乡对接工程）。

- **It closes P4777's shape from OUTSIDE GEM.** 870 km as-built Phase I, with named constituent
  trunks — an official, independent, non-GEM statement that Phase I is a *system* with parts,
  which is exactly the parent-row reading. The sheet's 825.00 is 5.2% off, almost certainly a
  vintage/scope cut; the batch cites the plan for shape and magnitude and leaves the exact
  vintage `UNRESOLVED` rather than proposing 870 as a replacement.
- **All 7 named lines map 1:1 onto in-scope rows** — 九江—南昌 → P4780, 九江—沙河 → P4781,
  九江—景德镇 → P4779, 南昌—丰城 → P4782, 高安—新余 → P4778, 丰城—抚州 → P4776,
  田南—上高 → P4783. **Five of the six blank-`LengthKnown` rows are DRC-named trunks**, so on
  those rows existence and status are closed and the whole budget goes to the length.
- **The limit, stated so no leg oversteps it:** the plan *names* the trunks without *measuring*
  them. It cannot fill a blank length, and apportioning the 870 km across seven lines would be
  fabrication. It also fixes the supply source — Phase I off 川气东送, Phase II off WEP2/WEP3.

**CCXI credit rating report, 江西省投资集团有限公司 2025 bond (第一期)** — the programme frame:
provincial network 3,400+ km total, Phase I **~1,600 km planned** / Phase II ~1,800 km planned,
total investment **134 亿元** from Jan 2009; at end-March 2024 ~3,182 km built, 县县通 3,177 km
complete, **2,892 km in operation**, ~87 stations, one 20,000 m³ LNG tank. A `SegmentCost` and
`Status` corroboration surface. **Planned ≠ as-built** — 1,600 km (planned) and 870 km
(as-built) are not competing figures and must never be reconciled against each other.

Both are handed to every batch via `shared_evidence.md` + the local `jx_plan.txt` /
`sse_bond_2025.txt`, so four agents don't re-find them.

## Three snapshot name-cell defects — MZ's lane, recorded not repaired

- **P4780** holds `OtherLanguageSegmentName = 上高支线` (Shanggao Branch) on a row named
  *Jiujiang-Nanchang*. 上高 belongs to **P4783** (Tiannan-Shanggao), whose Chinese-name cell is
  **empty** — the name is simply on the wrong row. Also a search trap: researching P4780 on
  上高支线 finds P4783's line.
- **P4788 / P4789** each hold a **fragment of one longer multi-segment Chinese string, chopped
  mid-phrase** (`丰段、进贤段；赣州南支线信丰瑞金段、上犹崇义` and `段、樟树新干峡江段、井开区
  吉水永丰段、赣州南`). P4789's starts on a bare `段、` and ends truncated. Neither is a valid
  name for its row — a paste accident split across two rows. This is also the leading
  explanation for **P4788's 340.30 km against a 31.75 km trace (10.7x)**: a length lifted from a
  multi-segment aggregate while the geometry covers one section. Flagged as a hypothesis for the
  leg to test, not a conclusion.

## Run-order note

The plan's gate was "validate the contract on the first shard before scaling." batch_01 was
~45 min in without having written a shard, so **batch_02 was launched as a second contract
sample** rather than idling the run for an hour on a single gate — blast radius 2 batches, not
5, and both agents were told to write their shard incrementally so a finished record lands
early. Batches 03-05 stay held until a shard validates.

`batch_01.json` landed a partial shard (P4776, 8 units) and **cleared the contract gate** —
all 10 required keys present on 8/8 records, zero blocklisted URLs, every `proposed_ref`
verified, the operators/owners unit preserved. That released **03, 04 and 05**, so all five
batches are now in flight.

One merge-chain defect found during the wait and fixed before it could bite: the fan-out
shards by BATCH (`shards/batch_NN.json`), and while `merge_ref_shards.py` globs
`ref_shards/*.json`, **`harvest_sentinel_findings.py` globs `ref_shards/P*.json`** — so every
`__VALIDITY__` / `__REDUNDANCY__` sentinel in this batch would have been dropped by the merge
and then skipped by the very script that exists to rescue it, silently. `split_shards.py`
(this staging dir) splits the batch shards per-PID so both globs are satisfied; the SOP now
carries the general warning. Run order is therefore:
`split_shards.py` → `merge_ref_shards.py` → `harvest_sentinel_findings.py` (reconcile its
count against the merge's WARN) → `merge_deepsweep_shards.py` → `recalc.py` → build.

Merge-time QC needs no exception for the large-CJK-PDF hand-confirmations: `merge_qc.verified_refs`
reads the shard's OWN verification objects rather than re-running the verifier, so a documented
manual override (`ok: true`, `contains_value: true`, with the pdftotext evidence in `note`)
passes on its own terms. The earlier worry that the QC rule would strip batch_01's DRC ref is
withdrawn.

## Merge chain: two silent-loss defects found and closed (2026-08-26)

Both are the same class — a shard record that no merge step claims — and both are
**invisible**: no WARN, no count moves, the workbook just doesn't carry the finding.

**1. Filename.** `harvest_sentinel_findings.py` globs `ref_shards/P*.json`;
`merge_ref_shards.py` globs `ref_shards/*.json`. A fan-out sharding by BATCH
(`batch_02.json`) satisfies the merge and is invisible to the harvester, so every
sentinel vanishes. Closed by `split_shards.py` (split by ProjectID, satisfy both).

**2. Shape — fills fall through BOTH scripts.** A fill on a blank-value row has no
baseline ref unit *by construction* (no-orphan-refs: a blank value column emits no owed
unit), so `merge_ref_shards` drops it for want of a key and the harvester only rescues
sentinels. Fills are `merge_deepsweep_shards`' job, read from `rows/<PID>.json`.
It hid because **an UNRESOLVED fill loses nothing — the successfully sourced one is what
vanishes**, and six in-scope rows have a blank `LengthKnown`.

**Routing is structural, not tag-based.** The first cut routed on `kind == "FILL"`, which
trusts the shard to have labelled itself — and three batch-02 records had not: P4780/P4781/
P4782 `Length [ref]` say *"FILL target: LengthKnown is blank"* in their own
`researcher_notes` and carry `kind: null`. They were still being dropped. `split_shards.py`
now routes on the worklist: if it owes no unit at `(pid, ref_col)` the value column is
blank, so the record is a fill whatever it called itself. 4 fills → 7.

**Run order (corrected, and it is not cosmetic).**

    split_shards.py -> merge_ref_shards.py -> merge_deepsweep_shards.py -> harvest_sentinel_findings.py

The harvester runs **LAST**. `merge_deepsweep_shards` re-folds by purge-and-rebuild and its
`is_old_deepsweep()` drops every record whose `ref_col` is `__VALIDITY__`/`__STATUS__`/
`__ROUTE__` — exactly what the harvester writes. Harvest-then-merge silently zeroes the
sentinels (verified: 2 → 0, no warning). Both `docs/sops/sweep.md` and `docs/workflows.md`
documented the destructive order; both corrected.

**Verified on batches 01/02/05** (from the pristine baseline, kept as
`staged_resolutions.BASELINE.json`): 79 ref units applied, WARN 6 == 6 sentinels harvested
== fully reconciled, 7 fills carried. Store = 162 baseline ref records + 7 fills + 6
sentinels = 175. `class_in` MISSING_REF 156 / HAS_REF 6 confirms the 3.7% citation base
independently.

## Route vs sheet length: the objective table (all 18 rows, 2026-08-26)

Computed directly from the routes repo, independent of what any research agent found.
**7 rows diverge** past 1.5×/0.67× (my earlier "5" was short):

| PID | sheet km | route km | ratio | vtx | RouteAccuracy | note |
|---|---|---|---|---|---|---|
| P5862 | 18.45 | 555.31 | **30.10×** | 5 | medium | staged `__VALIDITY__`: route wrong, sheet right |
| P5866 | 19.12 | 123.03 | **6.43×** | 2 | very low | staged `__VALIDITY__`, explicitly weaker than P5862 |
| P5887 | 23.30 | 49.40 | 2.12× | 6 | medium | staged `__VALIDITY__` |
| P4784 | 138.00 | 258.45 | 1.87× | 65 | medium | batch 03 |
| P4783 | 29.41 | 16.78 | 0.57× | 6 | medium | its only candidate ref is a confirmed 404 |
| P4788 | 340.30 | 31.78 | **0.09×** | 8 | medium | batch 03 |
| P4777 | 825.00 | 61.26 | **0.07×** | 14 | medium | network-granularity parent — expected, not a defect |

P4777's 0.07× is the one that is *not* a finding: it is the Phase I parent row, so a
14-vertex trace of one corridor against an 825 km system total is segment-vs-network
granularity. P4788 (0.09×) and P5862 (30×) are the two extremes that are real.

**Every one of the 8 UNRESOLVED fills already has a route.** All six blank-`LengthKnown`
rows carry geometry — P4780 (20 vtx) and P4782 (38 vtx) at medium accuracy are substantive
traces; P4776 and P5859 are 2-vertex straight lines and are lower bounds only:

    P4776  62.34 km / 2 vtx (very low)      P4781   19.37 km / 6 vtx  (medium)
    P4778  56.88 km / 11 vtx (medium)       P4782  100.96 km / 38 vtx (medium)
    P4780 136.02 km / 20 vtx (medium)       P5859   50.62 km / 2 vtx  (very low)

So `UNRESOLVED` here means **uncitable, not unknown**. The geometry is GEM's own, and rule 1
forbids citing it, so the fill correctly stays unfilled — but MZ owns these routes and can
fill the cells from her own geometry, which is a different lane than ours. Carry the table
into the handoff rather than reporting eight bare UNRESOLVEDs.

---

## Batch 03: 14 confirmations encoded as failures (fixed)

A third silent-loss defect, same family as the two merge-chain ones but living in the
*shards* rather than the scripts. `merge_qc.verified_refs` keeps only refs whose
verification is `ok && contains_value`, reading the shard's own verification objects and
never re-fetching. Batches 01/04/05 encoded a hand-confirmed false negative as
`ok=true, contains_value=true` + a note saying how it was confirmed — which passes as data.
**Batch 03 encoded the same situations as `ok=false` with the explanation in prose**, so
every one of them was stripped, and `merge_ref_shards.py` (lines 74–77) then honestly
downgraded the emptied `REFS_ADDED` records to `UNRESOLVED`. The downgrade is a correct
safety net, and it is exactly what made this invisible: nothing errored, and the units
simply reported *no source found* when a source had been found and thrown away.

Scale, before the fix: **11 records zeroed, 16 refs stripped, 31 of 47 kept** — and batch 03
is the highest-yield batch of the five (34 `REFS_ADDED`). After: **45 of 47 kept, 0 records
zeroed.** The other four batches were already clean (25/25, 36/40, 2/2, 11/11).

Every promotion was re-verified by the orchestrator before being made, not taken on the
subagent's word:

| Ref | How re-verified |
|---|---|
| `quannan.gov.cn` PDF (8 units on P4788) | Read from the local 11,461,354-byte copy. Live URL 403s — access failure, not a deletion |
| `jxganan.com/…/9746.html` (P4784 Diameter) | `url_verifier` live: HTTP 200, contains `323.9`. D323.9 mm OD ≡ DN300 nominal (GB/ISO) |
| `sohu.com/a/278468337_693503` (P4789 Status) | `url_verifier` live: HTTP 200, contains 投产/通气 |
| `tt.m.jxnews.com.cn/news/1193625` (P4791 ×2) | HTTP 200, contains `2.8亿`. 2.8亿立方米 = 0.28 bcm/y and 3.8亿元 = 380M RMB, both exact |
| `news.cnr.cn/…/20201022/…` + `wuning.gov.cn` (P4784 Capacity) | Both HTTP 200, both contain `3.13`. 3.13亿立方米 = 0.313 bcm/y, rounds to the sheet's 0.31 |

Two refs are **deliberately left stripped** and now say so in their own notes: an
`archive.org` screenshot item and a `web.archive.org` capture, both correctly *kept in their
sheet cells* under standing rule 5 (neither is a 404/410) but neither content-verified, so
neither may enter a proposal. That distinction — kept in-cell vs. proposed — is the thing to
preserve when auditing this class.

**Correcting one of my own claims from earlier in this batch:** I reported `news.cnr.cn` as a
soft 404 (HTTP 200 serving a 404 body). That was true of the URL I tested — the 2019-12-31
path — but the shard cites the **2020-10-22** path, which is live and carries the value. The
soft-404 observation was real and is worth keeping as a host caveat; it was not evidence
against this ref.

Durable rule written into `docs/sops/sweep.md` (§ merge-time QC): the strip rule's converse
is a shard-authoring requirement, plus the per-batch check — count records whose
`proposed_refs` is non-empty while `verified_refs()` returns empty; expect zero, except
rule-5 in-cell keeps.

## P4788: three findings the batch did not have

**1. `FuelSource` is half wrong — filed as a conflict, not a ref-add.** The sheet reads
`Sichuan-Shanghai gas pipeline/West-East gas pipeline II`. The operator's own emergency
plan for this exact section states the feed points verbatim: *"本项目赣州南支线从西二线149#阀室或
西三线瑞金分输清管站引出气源"* — WEP2 valve chamber #149, or the **WEP3** Ruijin pig-launcher
station — and terminates the line 止于西三线瑞金分输站. Term counts across the full
494,223-char extraction: 西二线 2, 西三线 3, **川气东送 0, 川气 0, 西气东输 0**. So WEP2 is
corroborated, WEP3 is missing from the sheet, and Sichuan-Shanghai is unsupported by the most
specific source that exists for this segment. Stated plainly: absence in one document is not
absence in fact, and a province grid can draw from more than one trunk — this document
describes *this branch's* feed points, not the whole Jiangxi network's. Hence a flagged
divergence with a deferred recommendation, per the standing rule, not a value change. The
shard had staged a paraphrase (`"West-East Gas Pipeline"`) rather than the sheet's actual
cell and classed it `REFS_ADDED`, which would have implied the sheet value was confirmed;
the staged value is now realigned to the sheet text and a `__VALIDITY__` record filed.

**2. The redraw coordinates handed to MZ are DMS read as decimal.** The existing
`__VALIDITY__` gives the corridor as `信丰分输站 E114.49/N25.26 → 瑞金分输站 E116.01/N25.95`.
The document reads `E114°49'21.19"/N25°26'8.07"` and `E116°0'33.24"/N25°56'46.44"` — DMS.
Correct decimals: **Xinfeng 114.82255, 25.43558; Ruijin 116.00923, 25.94623.** The stated
Xinfeng point is **38.7 km** from the real station; the Ruijin one happens to land 0.4 km off
and is harmless. Operationally this matters because those coordinates are the redraw anchors.
Generalizable: coordinates in Chinese engineering PDFs are DMS, and transcribing the
degree-minute digits as decimals costs tens of kilometres.

**3. The length conclusion was too strong, and I am walking part of it back.** The batch
refuted the aggregate-length hypothesis on the grounds that the document attributes 340.3 km
to the 信丰-瑞金段 itself — *"管线全长537.5km，其中赣州南支线信丰-瑞金段线路长度约340.3km"* and
*"此段线路全长340.3km"*. **That attribution finding stands**: 340.3 km is not another segment's
number and not the four-branch total. What does *not* follow is the stronger claim that the
sheet length is therefore correct and only the route is wrong. The two named terminal stations
are **131.8 km apart great-circle**, so 340.3 km implies 2.58× sinuosity against the 1.1–1.4×
typical of a trunk corridor — even allowing the documented detours (沿赣龙铁路绕行城市规划区,
经河坑村/七堡村, 先向北再向东). Both figures are now open. GEM's 31.78 km route is wrong either
way; a redraw to the documented corridor should measure roughly 140–190 km, and if it does,
`LengthKnown` needs a source of its own rather than this document alone.

## Final build

`deliverables/pipelines_batch_20260826_1133_ET_china-jiangxi-gas_deepsweep.xlsx` —
**staged not applied.** 8 sheets, `recalc.py` clean (no error cells).

    store 186 = 162 ref units + 9 fills + 15 sentinels     PIDs 18
    class_in   MISSING_REF 156 / HAS_REF 6   -> 3.7% citation base, reconfirmed independently
    class_out  REFS_ADDED 98 / UNRESOLVED 88
    tabs       Gas_Backend, Gas_OperatorsOwners, Gas_Validity (15), Gas_Fills (9),
               Gas_GulfPub, Gas_Refs_Added (97), Gas_Refs_Unresolved (65)
    chain      split -> merge_ref_shards -> merge_deepsweep_shards -> harvest (LAST)
               WARN 15 == 15 harvested, reconciled exactly

Pre-delivery gates, all passing: **0** gem.wiki URLs in any `[ref]` column (189 occurrences,
all in `Wiki` columns explicitly labelled *visited, not cited*) · **0** abarrelfull ·
**0** orphan refs in either direction (ref-without-value, value-without-ref) · **0** `high`-tier
units with fewer than 2 refs (16 have 2, 2 have 3; the 72 single-ref units are `medium`, 7 are
`low`).

One host worth recording rather than flagging: `img9.qianzhan.com` carries 39 of the proposed
refs, and it is a third-party rehost of *the actual Jiangxi DRC document* (赣发改规划 2014
325号, 江西省天然气利用规划 2013–2020) whose government copy at `nc.gov.cn` is NXDOMAIN — a
rehosted primary, categorically unlike a tertiary aggregator's own content. It is a 2014
**planning** document, so it is thin support for 2026 operating status on its own, which is
why those units sit at `medium` unless paired. `huaon.com` appears only as the second
independent source alongside it on the units that reach `high`.
