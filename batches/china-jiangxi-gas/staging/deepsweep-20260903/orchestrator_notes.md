# orchestrator notes — v3 fan-out (decisions + validator warnings to handle at merge)

## P4779 (sonnet, wave 1) — done
- validator: Status [ref] independent=true with <2 verified refs; Location [ref] orphan (Location value blank on sheet — check worklist before merge).
- decision owed: StartYear1 2009 (jdzmc.com + petrobest) vs sheet 2010 → __VALIDITY__ sentinel carries it; route to status-review/validity tab, do not overwrite.
- decision owed: Owner/Operator refs are system-level (SSE prospectus + qixin) — acceptable under the single-network-operator exception; note it in ResearcherNotes.
- 9 cross_row_leads (archive.org screenshot items per segment, chyxx 2008 Phase I approval, CCXI 2022 report for Owner fills) → collect_leads.py.

## P4789 (sonnet, wave 2) — done
- Fills: Pressure 4 MPa, Proposal 2016-08, Owner1 Jiangxi Natural Gas Group 100%.
- Capacity/SegmentCost UNRESOLVED: china5e figures are a 3-branch aggregate, not this segment. FuelSource over-lists WEP3 + Sichuan-Shanghai (only WEP2 confirmed) → validity note.
- Construction second source disagrees by a month (Sept vs Nov 2016) — kept medium.
- DECISION (cross-cutting): the SSE 54%/46% Operator JV split belongs to a Phase-I-only subsidiary per CCXI 2022 credit report; may be mis-applied to ~20 Phase-II rows sharing the SSE citation. Reconcile with the carried P5862 operator sentinel before merge; check every Phase II row's Operator record.

## engine fix landed mid-run (2026-09-04)
- url_verifier: block-phrase check now ignores <script>/<noscript> (comment-widget `alert("请输入验证码！")` on jdzmc.com / chinanews.com.cn produced false `blocked=True`). Content matching still sees script JSON. P4657/P4779 hand-encoded those verifications; re-verify their chinanews/jdzmc URLs at merge with the fixed verifier so `verifications` carry a real verdict.
- name_forms gap: P4657 system forms lack the short form 川气东送 (only 川气东送输气管道) → add to names.py before the merge-time recheck.

## P4657 (opus, wave 1) — done
- Fills: Construction 2007-08 (high); Owner1 国家管网 50% / 中国人寿 43.86% / 国投交通 6.14% (OO tab, medium); Proposal 2006 (medium). SegmentCost blank (626.76亿 is project-wide incl. Puguang field), Pressure blank.
- DECISION Start: sheet 2009/12 unsupported; staged change → 2010/3 (nea.gov.cn + Xinhua 建成投产 2010-03-29); optional StartYear2 2010-08 commercial ops. dazhou.gov.cn 2009-12-03 全线贯通 claim unreachable.
- DECISION Length: 1628.64 has no live source (trqi.sinopec 404, no Wayback). Published: 1635 as-built (中国证券报/chinanews), 1674 (2006 plan), ~1700 (ce.cn). Keep route-derived w/ caveat, or adopt 1635.
- Diameter: trunk is 1016 Puguang–Xuancheng / 864 Xuancheng–Shanghai → may need multi-value form (validity note).
- Capacity 15 bcm single-origin (others give 12 bcm design).
- 5 leads (2 P4649, 3 P4661 incl. 2023-09-16 开工 + 2025 MEE 批复).

## P4787 (opus, wave 2) — done
- Soft-404 replaced: same document live at quannan.gov.cn/qnxxxgk/zdsjbg/202201/1a999e0f….shtml (IPv4 only); 57.09 km (changed from 56.7), DN250, 6.3 MPa, 2021 approval.
- Fills: Pressure 6.3 MPa (high); Start 2022-12 (medium); Construction 2021 (low); Owner1 江西省天然气集团 54% + Owner2 国家管网集团东部原油储运有限公司 46% (medium).
- STATUS: change construction → operating (2024 operator plan live ops; 3 county origins date gas Dec 2022).
- DECISIONS: (a) do NOT apply v2 WEP3 FuelSource — WEP2 better supported; (b) Proposal ≤2017 (4-branch EIA approval 2017-12-28), 2021 is a 变更; (c) 46% holder is PipeChina subsidiary 东部原油储运, not parent → entity_lookup; (d) POSSIBLE MISSING ROW 上犹-崇义段 43 km DN250 6.3 MPa 0.9e8 Nm3/a → Discovery candidate (match against OtherEnglishNames first).
- P4786 lead: 2024 plan contradicts `shelved` for 会昌-寻乌 (97.5 km, DN250) → confirm in P4786 shard.

## process restart 2026-09-04 ~13:11 — agents P4782/P4785/P4786 lost before writing; relaunched with sibling-lead hints. Earlier user-killed P4649/P5866 relaunched 13:06.

## P4788 (opus, wave 1) — done
- Fills: Owner1 Jiangxi Natural Gas Group 100% (OO tab, medium); Proposal 2017 (low). Value corrections staged: StartYear1 2018→2022 (4 independent sources); FuelSource → WEP3/WEP2 (was Sichuan-Shanghai); Operator → 江西省天然气集团管道分公司 100% (was 54/46) — consistent with P4789's CCXI Phase-II finding.
- All 10 rereads resolved at segment level (quannan over IPv4; name_matched 信丰-瑞金段).
- Physical specs (340.3 km / DN450 / 8.65e8 / 6.3 MPa) single-origin (quannan plan) → medium.
- DECISIONS: SegmentCost 2,172,600,000 CNY is the FOUR-BRANCH aggregate → left UNRESOLVED; check P4786/P4787 for the same figure (__REDUNDANCY__). Start 2022 is a change proposal. Construction 2017 = EIA year, low. 340.3 vs 131.8 km straight-line resolved in the sheet's favour (loops via Longnan/Dingnan/Anyuan/Huichang).
- 3 leads (P4786, P4787, P4785).

## merge-prep 13:18 — hand-encoded verifications re-checked with the fixed verifier
- P4657 chinanews 2010/03-29/2196730 + 2010/09-01/2503669 and P4779 jdzmc 2009/11/19/13919: all three now return OK (200, name found) through url_verifier after the script-block interstitial fix. No shard edit needed.

## P4792 (sonnet, wave 2) — done 13:20
- 8 UNRESOLVED (Length/Diameter/Capacity/Start/Construction/SegmentCost/FuelSource/Pressure), 3 REFS_ADDED (Owner 54/46 on OO tab, Proposal 2014-04, Location), 3 REVERIFIED (Fuel/PipelineType medium at segment level via qianzhan Table 5; Operator high). Status verdict unclear (carried). 24/24 harvest opened.
- MERGE CHECK: Owner staged as 54/46 JV — reconcile with P4788/P4789's Owner1 Group 100% + Phase-I-only JV rule (CCXI). Decide which phase this branch belongs to before applying the operator/owner rule.
- 110 km figure bundles 宜丰-铜鼓-修水 as a 3-town project → keep Length UNRESOLVED, do not apportion. Possible competing/superseded 2014-era routing options across P4792/P5888/P4784 flagged in __VALIDITY__.
- Agent debunked 2 WebFetch hallucinations (sina/sohu fabricated quotes) — noted in shard; nothing relies on them. tonggu.gov.cn lead for P5888 is UNVERIFIED (soft-404, no capture) — "direct outreach" suggestion ignored (no email goes out).

## P4780 (sonnet, wave 1) — done 13:22 (九江-南昌 Phase I trunk)
- 4 REFS_ADDED (Status/Fuel/PipelineType/Location at segment level: qianzhan 九江一南昌 alt-dash + petrobest 九江至南昌), 2 FILL (FuelSource 川气东送 high; Owner1 Group 54% / Owner2 国家管网东部原油储运 46% medium), 1 REVERIFIED (Operator system-level medium), 8 UNRESOLVED. 25/25 harvest opened (bjx Aliyun WAF = access failure).
- DECISION: Start conflict — petrobest (segment-naming) says completed 2009 vs sheet 2010/6 (huaon, non-naming). Left UNRESOLVED; surface as a status-review/Update item in the delivery note, do not silently change. Same 2009-vs-2010 pattern as P4779 — treat as one cluster.
- MERGE CHECK: Owner here staged 54/46 (like P4792) vs Group 100% (P4788/P4789) — Phase I row, so 54/46 JV is the right owner model for Phase I; confirm P4788/P4789's Group-100% claims are Phase II rows.
- P4780 DEFECT 13:26: all 14 verifications lack `contains_value` → merge would drop every ref. Agent messaged to fix its own shard honestly per URL; re-validate on its reply.

## P4931 (opus, wave 1) — done 13:24 (WEP3 middle section 中卫-吉安)
- 7 REFS_ADDED, 1 UNRESOLVED (SegmentCost), __VALIDITY__ confirmed. 4/4 rereads resolved: news.cn 2025-07-17 DOES name the segment (comma split fooled matcher) — hand-confirmed. Fills: Pressure 10 MPa (high, 3 refs; 2014's 12 MPa on 中卫-枣阳 superseded by 环审〔2021〕104号); Proposal 2012-03 (medium, both mee.gov.cn = one origin, stated). Start [ref] upgraded to high (Xinhua + 光明网 2025-09-26; operating independently confirmed). 17 harvest.
- DECISIONS: (1) SegmentCost 44.7e9 RMB unsourceable (matches wiki Finance field); only sourced figure is 436.48亿 = 43,648,000,000 RMB (2014 NDRC 核准 via 人民网/新华网, approval-scope incl. later-cancelled branches). Stage as a candidate VALUE CHANGE flagged for Update, not silent. (2) ProposalMonth=3 off an EIA-notice date: KEEP year 2012, drop the month at merge (too fine).
- 9 leads incl. out-of-scope P4932/P4935/P4936 (route to country note); P4928 lead: SASAC 832.4 km / 15 bcm/y / construction 2012-10-16 / gas 2016-12-12 → GEM's 30 bcm/y on P4928 is likely the system figure. Discovery guard: 株洲-郴州支干线/邓州支线/新野支线 were cancelled by regulator, not missing rows.

## P4781 (sonnet, wave 1) — done 13:24 (九江-沙河 Phase I trunk)
- 8 UNRESOLVED, 3 REFS_ADDED (Owner 54/46 FILL, FuelSource 川气东送 FILL, Operator reread + 2nd source CCXI 2022/2026), 1 REVERIFIED (Start downgraded to low: unnamed, no 2nd source). 11 leads. 25 harvest.
- Validator: 7 "ref does not name pipeline" notes on system-level Owner/FuelSource/Operator refs (justified in notes — expected for system-level exception); Operator record has empty value_cols (cosmetic).
- DECISION: agent flags the carried Operator [ref] cell as holding Owner-shaped 54/46 data and suggests Operator may be 江西省天然气管道有限公司 — check against CCXI Phase I/II operator rule at merge; do not change without a naming source.

## P4783 (sonnet, wave 1) — done 13:24 (田南-上高 Phase I branch)
- 4 REFS_ADDED, 8 UNRESOLVED. Fills: FuelSource (Puguang/川气东送, system-level), Owner 54/46 with SPECIFIC 46% holder (国家管网集团东部原油储运有限公司) — corrects generic-parent naming. Start: carried huaon ref names NOTHING on full read → recommend drop; replaced by qianzhan (segment-named, year only). Operator 2nd source CCXI 2022. pipechina xls confirmed dead (404, no capture). 10 leads. 25 harvest.
- Note: huaon.com is a once-working ref — it may only be DEMOTED/removed from the cell if the page truly does not support the value; it is live (not 404), so the merge keeps it out of the proposed set but never records it as DEAD_LINK.
- P4780 fixed 13:29: contains_value/name_level on all 14 verifications; PipelineType petrobest honestly contains_value=false → medium; PASS.

## relaunch 2026-09-09 — 31 remaining rows off existing payloads; RELAUNCH_NOTES.md added as the addendum; leads_by_target.json rebuilt (70 leads / 32 targets, --no-verify; verified rebuild running in background)

## relaunch wave 2 dispatched 2026-09-09 — 10 agents (P4785 P4786 P5860 P5861 P5862 P5863 P5865 P5886 P5888 P4944); P4946 deferred to wave 3 (concurrent-agent cap of 20 reached). Wave 3 pending: P4946 P4661 P4752 P4794 P4795 P4796 P4797 P4928 P5864 P5887 P5889.
- merge-prep check: name_forms.json P4657 already carries the 川气东送 short form under system (names.py stem-strip landed 2026-09-04); no names.py edit owed.

## P4776 (sonnet, relaunch w1) — done 09-09
- 6 REFS_ADDED (Owner/FuelSource/Operator/Status/Fuel/Location), 8 UNRESOLVED (Length/Capacity/Construction/SegmentCost/Pressure/Proposal/Diameter + __VALIDITY__ on the four conflicting Phase I system totals 825/870/876/680 km), 2 REVERIFIED (PipelineType/Start). 25/25 harvest. No value change. Phase I → 54/46 JV confirmed.
- Status/Fuel/Location lifted to high: Sina 2011 names both endpoints 丰城-抚州 (outlier vs sibling Phase I trunk rows at medium — note at merge).
- 3 leads: 2 → P4777 (Sina 825 km / 2008-10 / 31亿 and sohu-2008 680 km / 26亿 / 5.7 bcm/y are AGGREGATE-row figures), 1 → P5865 (jxgajc capture 20.2 km / DN508).

## P4782 (sonnet, relaunch w1) — done 09-09 (南昌-丰城 Phase I trunk)
- 3 REFS_ADDED (Owner 54/46 FILL medium, FuelSource 川气东送 FILL high, Operator), 8 UNRESOLVED (7 physical/finance blanks genuine — only network aggregates exist; Location kept medium), 1 REVERIFIED (Start huaon downgraded to low, unnamed). 25/25 harvest. No value change. Validator: Operator empty value_cols (same cosmetic as P4781).
- DECISION: carried Operator [ref] holds QCCOwner ownership data; wiki uncited Operator = 江西省天然气管道有限公司 — fold into the Phase I/II operator rule check (P5862 sentinel). qcc.com 567 / zhaoqt.net = access failures, not cited.
- 1 lead → P4776 (Sina 2011-08-29 names 丰城至抚州 with test-commissioning date).

## spend-limit kill 2026-09-09 08:33 EDT — 20 agents lost, relaunch wave 4 dispatched ~08:55
- Account spend limit (HTTP 429, reset 13:00 ET) killed every in-flight agent: P4944 P5886 P4785 P5865 P4661 P5861 P4791 P4777 P5860 P4947 P5888 P5862 P4649 P4786 P5866 P4946 P4934 P4784 P5859 P5863. P4649 (08:35) and P4777 (08:33:55) had already written valid shards → 17 shards + carried. Profile switched to personal account; relaunched immediately per the limit-hit memory.
- Lost partial findings recorded as re-find hints in RELAUNCH_NOTES.md item 9 (P4791 SSE line-613 / CCXI Jingdezhen; P5866 安全验收; P5863 naming source; P4944 Zhejiang NEA; P5886 Jiujiang doc).
- Wave 4 = 20 agents: the 18 killed rows without shards + P4928 (opus) + P4752 (sonnet). Remaining 7 (P4794 P4795 P4796 P4797 P5864 P5887 P5889, all sonnet) fill freed slots. Prompts identical to the killed dispatches (recovered from the transcript; wave-3 rows written from the same template), delivered by file pointer.

## P4777 (opus, relaunch w1) — done 09-09 (Phase I parent) — shard landed before the kill; report lost
- From the shard: 12 REFS_ADDED, 4 UNRESOLVED, 1 CONFIRMED sentinel; harvest_opened 57; 6 cross_row_leads. Validator: only "null tier on UNRESOLVED" notes (Diameter, Pressure). Read the shard at merge for value changes/decisions (no agent report).

## P4649 (opus, relaunch w1) — done 09-09 (川气东送 江西支线) — shard landed before the kill; report lost
- From the shard: 8 REFS_ADDED, 7 UNRESOLVED, 3 CONFIRMED sentinels; harvest_opened 30; 15 cross_row_leads (fold into leads_by_target at merge). Read the shard at merge for decisions.
- 09:0x: `collect_leads.py` re-run with P4649/P4777 shards → leads_by_target.json 95 leads / 42 targets (was 70/32; pre-image kept as leads_by_target.pre-w4.json). New leads on FINISHED rows owe a merge-time routing pass: P4657 +1, P4776 +2, P4778 +1, P4779 +1, P4780 +1, P4781 +1, P4782 +1, P4783 +1, P4790 +1, P4777 +3. In-flight rows (P5866 +3, P4784 +2, P5865 +2, P5886/P4944/P4946/P4791 +1) were told to scan the two shards directly; wave-5 rows (P5889 +1) get the regenerated file.

## P4661 (sonnet, relaunch w4) — done 09-09 (川气东送二线 皖赣支干线 安庆-鄱阳, proposed)
- 12 REVERIFIED (dominant docs: pipechina.com.cn 2024-05-14 EIA disclosure + mee.gov.cn 环审〔2025〕83号 2025-09-24 final approval, both name 皖赣支干线), 3 UNRESOLVED (Start/Construction/SegmentCost — branch-specific evidence absent; no backfill from 二线 aggregates), 0 REFS_ADDED, 0 leads. 16/16 harvest. Validator clean.
- STATUS: CONFIRM `proposed` — all 2023-09-16 开工 / 2025-08-25 in-service milestones name the west section (川渝鄂段) only; this branch's own EIA approval is 2025-09-24, no branch tender/construction since.
- DECISION at merge: agent dropped the payload's `rise.cnpc.com.cn` PDF as "dead" via REVERIFIED replacement — CHECK the verifier status: only a confirmed 404/410 may drop; a WAF/timeout keeps the ref + Wayback added (standing rule).

## P4946 (sonnet, relaunch w4) — done 09-09 (WEP2 樟树-湘潭支线)
- 5 REFS_ADDED (Pressure FILL 10 MPa high: MEE 2016 竣工验收 letter + Hunan 2013 gas plan; Location medium; Owner/Operator PipeChina medium via inference chain — no single source names PipeChina + this branch; FuelSource → high), 1 REVERIFIED (Length medium), 3 UNRESOLVED (Construction/SegmentCost/Proposal: only East-section bundle aggregates exist — 2009-02/2012-12/630.24亿 — not staged per aggregate rule). No value change. Validator clean. 2 leads (→P4944 own spec 1016mm/10MPa/10 bcm/y from the MEE letter; →P4793 trunk aggregates).
- DECISION at merge: WEP2-branch Owner/Operator = PipeChina inference chain (CNPC→国家管网 2020) — align across P4944/P4794–P4797/P5861; medium tier is right unless a naming source appears. Location "Changfu Town" sub-detail unconfirmed.

## P4791 (sonnet, relaunch w4) — done 09-09 (乐平-德兴-婺源) — PHASE LABEL DEFECT
- 3 REFS_ADDED (Owner FILL 54/46; Pressure FILL 6.3 MPa 2 sources; Start FILL 2022-09 trial production, jxganan), 5 REVERIFIED, 6 UNRESOLVED, 1 `__VALIDITY__`. 25/25 harvest (7 archive.org screenshot items resolved via IA metadata API — all other segments). Validator clean. 3 leads.
- VALUE CHANGES: Owner1/2 filled (江西省天然气集团 54% / 国家管网集团东部原油储运有限公司 46%); Operator [ref] entity corrected — payload's staged 46% holder "国家石油天然气管网集团有限公司" (parent) is WRONG, SSE prospectus footnote 5 names the subsidiary 国家管网集团东部原油储运有限公司.
- `__VALIDITY__`: three independent segment-naming sources call this a 一期 (Phase I) project under the Phase I JV; CCXI 2022 places Jingdezhen AND Shangrao under Phase I → GEM's "Phase II" segment label is wrong; recommend relabel to Phase I. RELAUNCH_NOTES item 9 corrected accordingly. Second conflict left UNRESOLVED: jxganan D323.9 mm / 2.252亿 for the 61.64 km 乐平-德兴 leg vs staged 200 mm / 3.8亿 for the 97 km route.
- DECISION at merge: re-check every "Phase II" row (P4788 P4789 done as Group 100%; P5860 in flight) against the sources' own phase wording before applying the Phase I/II operator rule; the rule keys on SOURCE phase, not the sheet label.

## P4786 (sonnet, relaunch w4) — done 09-09 (Phase II 赣州南支线 会昌-寻乌段) — STATUS CHANGE
- 8 REFS_ADDED, 5 REVERIFIED, 1 UNRESOLVED (SegmentCost: only the four-branch package 21.726亿 exists), `__STATUS__` + `__VALIDITY__`. 24/24 harvest. Validator clean. 0 leads.
- STATUS: CHANGE shelved → operating, high/independent: quannan 2024 operator emergency plan (live branch, 运行未满三年 at 2024-09-20), Huichang county 2023-07 (gas-in 2022-11), Xunwu county 2021-07, 2021 provincial key-projects roster. Start 2022/11 filled.
- VALUE CHANGES: Owner 江西省天然气集团 100%; Operator corrected from stale Phase I 54/46 split to 江西省天然气集团有限公司管道分公司 100%; FuelSource WEP3/WEP2 (item 4's WEP2-only guidance superseded); Pressure 6.3 MPa; Proposal 2017 (low).
- DECISION at merge: (1) ShelvedCancelledType / shelved-year cells become owed CLEARS under operating — check the sheet row; (2) Phase II operator correction applies identically to P4786/P4787/P4788/P4789 (but see P4791: verify each row's phase from sources first); (3) 上犹-崇义段 still no PID → Discovery/missing-row item for the delivery note (also P4787).

## P4784 (sonnet, relaunch w4) — done 09-09 (Phase I 永修-武宁-修水支线)
- 7 REFS_ADDED (PipelineType/Construction → high; Owner/FuelSource/Proposal 2018-06/Start 2023-10 FILLs; Operator), 4 REVERIFIED, 0 UNRESOLVED. 25/25 harvest. Validator clean. 1 lead → P5889 (2018-06-20 Jiujiang land-acquisition notice names both branches).
- VALUE CHANGE: 46% holder corrected 国家石油天然气管网集团有限公司 (parent) → 国家管网集团东部原油储运有限公司 (subsidiary), same as P4783/P4791.
- OWN DEFECT (fix before merge): `news.cnr.cn/native/city/20201022/t20201022_525306219.shtml` serves GBK; url_verifier decodes as UTF-8 → mojibake → name_found false / system-level mis-score. Page names 永修——武宁——修水支线工程. Same URL cited in P4783/P4781/P4792 — re-score those verifications after the charset fix. Proposal fill = land-acquisition notice proxy (flag); Start single-sourced (jxic.yingcaicheng.com unreachable — retry at merge).
- 09:4x CORRECTION to the P4784 note: NOT a charset bug — url_verifier already flips ISO-8859-1 → apparent_encoding (GB2312) and finds 永修 on the cnr.cn page. The real defect was `_cjk_norm`: the page writes 永修——武宁——修水 (doubled em-dashes) which normalised to `永修--武宁--修水` ≠ `永修-武宁-修水`. FIXED in scripts/url_verifier.py (dash runs → one dash; 至 → dash so 丰城至抚州 matches 丰城-抚州). Verified: 永修-武宁-修水支线 / 永修—武宁—修水 / 永修至武宁至修水 all OK against the page; 永修至修水 still FAIL (correct — different name). MERGE TASK: re-run the verifier over every `name_found: false` verification in all shards and list which flip to true (agents may have under-tiered on the old matcher).

## P4785 (sonnet, relaunch w4) — done 09-09 (Phase II 赣州南支线 大余-信丰段) — STATUS CHANGE (medium)
- 8 REFS_ADDED, 6 UNRESOLVED (Length 57.70 km unsourced — only a superseded 2014 plan figure 36 km; Diameter/Capacity/Start/SegmentCost/Pressure), 2 sentinels. 24 harvest (bjx.com.cn = Aliyun WAF + Wayback 429 → access failures, not deletions; jiangxi.gov.cn soft-404s; toutiao JS shell). Validator clean. 2 leads → P4786 (瑞金-会昌 segment bundled in the same 2024 tender — no matching sibling name → possible missing row; 2021 WEP3-via-Ruijin chronology).
- STATUS: CHANGE proposed → construction, MEDIUM: the row's own Status ref (Wayback of a ccpc360 tender aggregator) is a 2024-07-27 construction-bid AMENDMENT naming the segment endpoints (149# WEP2 valve chamber → 大余分输站 → 信丰分输站). Bid amendment = active procurement, not groundbreaking — orchestrator judgment owed (deliver as change/medium with the caveat, or `unclear`).
- VALUE CHANGES: Operator/Owner → Phase II 江西省天然气集团 管道分公司 100% (CCXI footnote names 大余 county under Phase II — source-phase confirmed, consistent with P4791 rule); FuelSource WEP2 (segment-naming); Fuel/PipelineType/Location → high.
- Missing-row candidates for the delivery note now: 上犹-崇义段 (P4786/P4787) and 瑞金-会昌段 (P4785).

## Merge-decision RESOLVED 2026-09-10 (orchestrator) — P4661's dropped `rise.cnpc.com.cn` PDF

The queued question was whether P4661's drop of the payload's original `Status [ref]`
(`http://rise.cnpc.com.cn/bjzyjs/wsgs/202503/.../d1e861bc7cd9419f8c7c1c82b2548638.pdf`)
was a real deletion or an access failure dressed up as one. Verified by hand:

- `curl -4` on the origin → **302 → `https://www.cnpc.com.cn/cnpc/error/error.shtml`**,
  which returns 200 with the body `NOT FOUND / 您访问页面无法找到 / 请确认其拼写正确`.
  That is CNPC's own not-found page, not a WAF challenge, not a login wall, not a timeout.
- `https://` variant → 504 (origin only speaks http here).
- Wayback exact-URL CDX → `[]`. **No capture of the PDF exists anywhere**, so there is
  nothing to add alongside. (`archive.org/wayback/available` was 429ing throughout — rate,
  not ban; the CDX answer is the decisive one.)

**Verdict: the drop is UPHELD.** A vendor-served "NOT FOUND" page with no capture in
existence is a confirmed deletion in substance, and the letter of the never-drop rule
(protect a once-working ref against an *access failure*) is not in tension with it. The
cell also strictly improves: the shard replaced it with two independent, segment-naming
documents — PipeChina's 2024-05-14 首次环境影响评价信息公开 and MEE's 2025-09-24
环审〔2025〕83号 — both of which name 皖赣支干线 itself and agree on 169.5 km / D1016 / 10 MPa.
No further action at merge.

## BATCH-LEVEL FINDING 2026-09-10 (orchestrator) — six `Status [ref]` cells are cited to GEM's own screenshots

Found while routing the 111 leads: two leads pointed at `archive.org/details/screenshot-*`
items. Checked their IA metadata, then swept all 44 payloads' `already_sourced`.

**Six rows cite `Status [ref]` to an archive.org item and nothing else:**

| PID | item | IA `description` |
|---|---|---|
| P4787 | `screenshot-2024-09-26-at-1.39.33-pm`  | `二期工程, 赣州南支线 (龙南-全南段)` |
| P4792 | `screenshot-2024-09-26-at-2.12.34-pm`  | `宜丰-铜鼓支线管道` |
| P5860 | `screenshot-2024-10-03-at-4.59.47-pm`  | `西三线于都分输站-宁都-广昌-南丰输气管线` |
| P5863 | `screenshot-2024-10-03-at-5.08.57-pm`  | `干洲-奉新支线` |
| P5886 | `screenshot-2024-10-04-at-10.05.50-am` | `一期工程, 沈贵里-彭泽支线` |
| P5889 | `screenshot-2024-10-04-at-10.17.45-am` | `一期工程，蔡岭-都昌支线` |

(A seventh, `screenshot-2024-09-26-at-11.47.34-am` = `永修-武宁-修水支线天然气管道`, is in P4784's
`already_sourced` name_check and in the harvest pool, not as a `Status [ref]`.)

All seven share the same provenance: `uploader = xiaojun.peng@globalenergymonitor.org`,
`source = None`, `originalurl = None`, `collection = opensource_image`, and a `description`
that is raw HTML pasted out of a Google Doc (`font-family:'docs-Calibri'`). They are a GEM
researcher's own screenshots of some other page, uploaded with **no record of what page**.

**Ruling.** These are a GEM surface, so **standing rule 1** applies: not citable, and — unlike
a footnote in a banned aggregator — there is no origin recorded to chase to a primary. Those
six `Status` cells are therefore **effectively uncited**, and rule 4(e) makes each one an OWED
ref unit that `build_ref_worklist.py` mis-classified as settled because the `[ref]` string was
non-empty. Two corollaries:

- **We never propose deleting them.** They are live sheet refs and dropping one is the
  researcher's call, not ours (and not an access-failure case either — the items resolve 200).
  We source the cell properly *alongside* the existing ref.
- **We never propose one as a ref of our own.** Zero banned/GEM URLs are staged in any shard,
  and zero appear in any other `already_sourced` cell — checked all 44 payloads for
  gem.wiki / globalenergymonitor.org / abarrelfull / theodora as well: clean. The screenshots
  were the only covert GEM surface in the batch.
- **The `一期工程` / `二期工程` labels in two descriptions carry no weight** — they are GEM's own
  phase labels, and per RELAUNCH_NOTES item 9 the phase determination keys on the SOURCES'
  wording, never on a GEM label.

**Dispatched:** the four affected rows still in flight (P5860, P5863, P5886, P5889) were
messaged mid-run to move `Status [ref]` into their owed set and resolve it like any other unit.

**Owed at merge:** P4787 and P4792 finished before this was found and have **no `Status`
resolution at all** (Status was never in their owed set). Both owe a `Status [ref]` follow-up
pass before delivery — otherwise gate L will read six sourced Status cells that aren't.

**Also owed:** a country-note open item. This is a measurement defect, not just six cells —
the "3.7% cited" Jiangxi baseline counts a GEM screenshot as a citation, so the true base is
lower, and the same pattern very likely exists in other Chinese provinces MZ has worked.

## Lead routing 2026-09-10 (orchestrator) — 111 leads / 46 targets

Cross-checked every lead against the shard of its target row. 58 were already cited by the
target's own shard (no action). 44 land on rows still in flight (their agents were given the
`leads_by_target.json` key). **Nine land on a FINISHED row that its shard does not cite** —
adjudicated here:

- **P4657 (川气东送 trunk) — `sohu.com/a/278023532_825427`, the strongest of the nine.**
  Gives the TRUNK `设计压力 10MPa` and `管径 1016mm`, both of which P4657 left `UNRESOLVED`;
  those are sourceable now and owe a follow-up. It also puts a FOURTH length on the table:
  1611.7 km 主干管道 (sohu) vs 2270 km 全线设计总长 incl. branches (same page) vs 2170 km
  (thepaper 1578871) vs 约1702公里 (Jiangxi DRC plan). GEM has 1628.64. The four figures are
  measuring different things (mainline / mainline+branches / unclear), so this does NOT resolve
  the queued P4657 Length question — it explains WHY it is unresolvable from secondary prose and
  argues for leaving Length alone with the disagreement documented.
  The lead further notes the DRC plan's mainline province list (`经重庆、湖北、安徽、浙江、江苏`)
  omits Jiangxi. **That is a conflict, not a finding** — the sohu page's own province list DOES
  include 江西 (and is internally inconsistent: eight province names introduced as "6省"). Not
  grounds to touch P4657's scope; record both and move on.
- **P4789 — `img9.qianzhan.com/.../20230714-d7d735aa6fb9eae9.pdf`, Table 5: `西二线棒树-新干-峡江 43公里`**
  (OCR-corrupted 棒树 = 樟树). Matches the `樟树新干峡江段` wording already in P4789's own
  `OtherLanguageSegmentName`. A leg-level candidate for a row whose Length is owed → follow-up.
- **P4790 — same PDF, three legs: `吉水-永丰 45.4公里`, `永丰-乐安 49.3公里`, `吉安-井开区门站 20公里`.**
  The table has NO Le'an–Yihuang leg, and P4790's corridor runs Jingkai–Jishui–Yongfeng–Le'an–Yihuang.
  So these cannot be summed into a row length — **aggregate-vs-segment in reverse**: partial legs
  are not a row total. Stage none of them as `LengthKnown`; they are corridor corroboration only.
- **P4786 — `web.archive.org/web/20260514205837/ccpc360.com/bggg59218375210.html`.** A 2024-07-27
  bid amendment bundling a `瑞金—会昌段` leg into the same tender as an actively-bid Dayu–Xinfeng
  leg. Two consequences, both already in the queue and now corroborated: it strengthens the
  **missing-row candidate 瑞金-会昌段**, and an actively-bid 2024 tender sits awkwardly against
  P4786's `shelved` verdict → include in the P4786 status re-check.
- **P4649 — `energy.people.com.cn/power/n1/2019/0618/c71901-31166381.html`.** 新华网 via
  people.com.cn on the trunk's gas sources (普光/涪陵/元坝 + 洋山港 LNG). System-level for a branch
  row, so `FuelSource` context at `low` only, beside a branch-naming source. Marginal; take it
  only if the follow-up finds nothing better.
- **P4787 — `qxb-pdf-osscache.qixin.com/AnBaseinfo/85599868a5a6e3c2fc8db704da8180b8.pdf`.**
  Verification `ok:false`. No value as a ref; its substance (whether this row's Operator/FuelSource
  citations were mechanically reused from the SSE Phase-I-scoped 54/46 split) folds into the
  standing Phase I/II operator reconciliation.
- **P4784 + P4792 — the two `archive.org/details/screenshot-*` items.** REJECTED as refs per the
  finding above (GEM's own uploads, no provenance). Their IA descriptions are still useful as
  naming data — `永修-武宁-修水支线天然气管道` and `宜丰-铜鼓支线管道` confirm the name forms GEM's
  researcher worked from — but they never enter a `[ref]` cell.

**Net follow-up owed on finished rows:** P4657 (Pressure + Diameter, sourceable now),
P4789 (Length 43 km candidate), P4787 + P4792 (`Status [ref]`, per the finding above),
P4786 (status re-check + 瑞金-会昌段 missing-row candidate). P4790's legs and the two
screenshots are closed with no action.

## Out-of-scope + unmatched lead buckets 2026-09-10 (orchestrator) — resolved

`collect_leads.py` grouped 7 lead targets that are not roster PIDs. Dispositions:

**→ `docs/country_notes/china.md` open items (WEP3, outside Jiangxi, all three from P4931's shard):**
- **P4932** — WEP3 west section (霍尔果斯-中卫): `cpnn.com.cn/news/nytt/202109/t20210924_1434107.html`
  gives `西段（霍尔果斯-中卫）2014年8月25日建成投产`, a segment-naming operator release that would
  source `StartYear1=2014` / `StartMonth1=8`.
- **P4935** — Zhongwei–Jingbian connector: MEE 环审〔2021〕104号
  (`mee.gov.cn/xxgk2018/xxgk/xxgk11/202112/t20211215_964280.html`) records that of the
  2014-approved branch set only 中卫联络压气站 and the 中卫-靖边联络线 were built — the regulator
  confirming this row BUILT in 2021.
- **P4936** — Changsha branch: same approval, `长沙支线单独立项` — permitted as a standalone
  project after removal from the middle-section scope, which explains why its dates do not
  track the trunk's.

**`P4779-context` (2 leads) — reusable, not row-specific:**
- `chyxx.com/industry/200808/2143827QU5.html` (智研咨询, 2008-08-30): `江西省天然气管网一期工程启动`,
  provincial approval "in recent days", >RMB 1.6bn, completion expected end-2009, 九江 gate station
  as entry. **SYSTEM-level (553 km Phase I aggregate)** — usable for a trunk/system Proposal or
  Construction sentinel, never for a segment cell. Relevant to the queued 2009-vs-2010 Phase I
  start cluster (P4779/P4780): it independently dates the Phase I *programme* to 2008 approval /
  end-2009 target, which is consistent with 2009 commissioning claims and against a 2010 sheet value.
- `qxb-pdf-osscache.qixin.com/AnBaseinfo/85599868a5a6e3c2fc8db704da8180b8.pdf` — the CCXI 2022
  rating report for 江西省天然气集团. Confirms 江西省天然气管道有限公司 is the 54%-owned Phase I
  subsidiary. This is the document the whole Phase I/II operator reconciliation turns on.

**The two screenshot buckets — CLOSED, all seven items matched to roster PIDs.** P4791 filed
them as "3 Jiangxi network branches not yet matched to a PID" and P4779 as
`unknown-other-Jiangxi-segments`; the sweep in the finding above matched every one:
`赣州南支线(龙南-全南段)`→P4787, `永修-武宁-修水`→P4784, `宜丰-铜鼓`→P4792,
`西三线于都分输站-宁都-广昌-南丰`→P5860, `干洲-奉新`→P5863, `沈贵里-彭泽`→P5886,
`蔡岭-都昌`→P5889. None is citable (GEM uploads), so the value of the match is the
**name-form confirmation** plus the fact that six of the seven ARE the row's only `Status [ref]`.
No lead work remains in these buckets.

**`(all Jiangxi-network Phase-II-labeled rows in Jingdezhen or Shangrao prefecture)` — ACTED ON.**
P4791's hypothesis, from CCXI's own footnotes read directly: footnote 2 (`一期管网工程...涉及南昌、
九江、景德镇、新余、宜春、抚州、鹰潭、上饶等42个县市`) puts BOTH 景德镇 and 上饶 under **Phase I**;
footnote 3 (`二期管网...涉及井冈山市、莲花县、永新县、大余县等40个县（市，区）`) names no county of
either prefecture. Swept the roster for Jiangxi-network rows in those two prefectures:
- **P4791** — the row that found it. `__VALIDITY__ CONFIRMED`, phase label contradicted.
- **P5887** (广丰-玉山支线, both endpoints in Shangrao) — in flight; messaged mid-run with the
  hazard, told to key the phase on its OWN segment-naming sources and not to copy P4791's verdict,
  and warned that the phase choice decides the owner (Phase I 54/46 JV vs Phase II 100% 管道分公司).
- **P4779** (九江-景德镇) — finished. Its `__VALIDITY__` is about the 2009-vs-2010 start, not the
  phase. **Owes a phase check at merge**, since Jingdezhen is footnote 2 territory.
- **P4796** (WEP2 余江-景德镇) — NOT a Jiangxi-network row, so the footnotes do not bear on it; its
  agent already carries the WEP2-vs-Phase-I attribution hazard for Jingdezhen documents.

## BATCH-LEVEL RULING 2026-09-10 (orchestrator) — the WEP2-Jiangxi-branch cohort: five rows attributed to the wrong parent network

This is the consolidated ruling P4797's block deferred, now issued against every shard in the
cohort. **Rows: P4793 (高余线 高安-余江), P4794 (九高线 九江-新建-高安), P4795 (黎川支线 临川-黎川),
P4796 (余景线 余江-景德镇), P4797 (鹰潭支线 余江-鹰潭).** P5861 (新余支线 高安-新余) was in the
cohort and has left it by a different door — it is retired into P4778 by the reciprocal redundancy
ruling, which turns out to be the same finding seen from the other side (see below).

**What every one of these five rows says today:** `PipelineName` = West-East Gas Pipeline 2,
`FuelSource` = West-East Gas Pipeline, `Operator`/`Owner` = 国家石油天然气管网集团有限公司
(PipeChina) at 100%. Not one of those four values is supported by a document that names the
segment.

**What the documents say.** Two independent regulators each enumerate WEP2's Jiangxi structure
*exhaustively*, and they agree with each other:

- Jiangxi DRC provincial gas plan 赣发改规划〔2014〕325号 (via qianzhan): WEP2's entire Jiangxi
  footprint is **一干两支** — the 中卫-樟树-广州 mainline section plus exactly two branches,
  樟树-湘潭支干线 (= **P4946**) and 南昌-上海支干线 (= **P4944**) — 1,097 km, first gas 2011-09,
  built out 2012-04.
- MEE completion-acceptance notice 环验〔2016〕98号: WEP2's East section comprises exactly five
  named components (mainline, 樟树-湘潭联络线, 广州-南宁支干线, 广州-深圳支干线, 南昌-上海支干线
  含嘉兴-甪直联络线), each with its own diameter/pressure/capacity.
- NDRC's Dec-2023 interprovincial tariff table — a document whose whole purpose is enumerating
  operating branches — concurs.

None of the five rows appears in any of those lists. GEM tracks the two branches that DO appear
(P4944, P4946) as separate rows already, so the cohort is not "the same branches under other
names" — it is five segments WEP2's own paperwork does not contain.

**And the positive attribution.** CCXI's 2022 credit-rating report for 江西省天然气集团有限公司
splits the province by GAS SOURCE into two operators with **disjoint** service areas:

| | Phase I | Phase II |
|---|---|---|
| operator | 江西省天然气管道有限公司 ("天然气管道公司") | 江西省天然气集团…管道分公司 ("管道分公司") |
| ownership | 54% Jiangxi Gas Group / 46% 国家管网集团东部原油储运有限公司 | 100% Jiangxi Gas Group, formed 2016 |
| gas source | 川气东送 | **西气东输二线** |
| footprint (fn. 2/3) | 42 counties incl. 九江, 宜春, 抚州, 景德镇, 鹰潭 | ~40 counties: 井冈山市, 莲花县, 永新县, 大余县 … (Ji'an/Ganzhou, far southwest) |

Every endpoint of all five rows — Jiujiang, Xinjian/Nanchang, Gao'an (Yichun), Linchuan/Fuzhou,
Lichuan, Yujiang/Yingtan, Jingdezhen — falls inside Phase I's stated footprint and outside Phase
II's. The rows are labelled with Phase II's gas source while sitting in Phase I's territory.
Three rows add their own corroboration: P4796's Jingdezhen is *explicitly excluded* from WEP2's
Jiangxi footprint by the DRC plan, which names 九江-景德镇 (川气东送-fed) as the province's actual
Jingdezhen trunk; P4795's entry in the DRC plan's Table 5 (抚州-南城-黎川, 128 km) lacks the
西二线 prefix that table puts on every WEP2-sourced segment; P4794's own Chinese name routes
through Xinjian District of Nanchang, i.e. the confirmed Phase I trunk P4780 (九江-南昌) extended
onward, and its StartLocation Lushan is the same Phase I trunk origin as P4779.

**The P5861 cross-check, which is why I am confident.** 高安-新余 was labelled a WEP2 branch on
P5861 and duplicated the 川气东送-labelled P4778. PipeChina's own live 2026 公平开放 facility
workbook enumerates all 34 facilities of 国家管网集团西气东输分公司 and contains no Xinyu branch
at all; the DRC plan names 高安-新余 as one of six 已建成 Phase I 干线. So on the one row of this
cohort where a segment-naming document exists, the WEP2 attribution is not merely unsupported —
it is **refuted**, and the correct answer was Phase I. That is the cohort's hypothesis, tested
once and confirmed.

### The ruling

1. **Nothing is staged as a value change on any of the five rows.** Rule 4(a) cuts both ways: a
   document that does not name the segment cannot fix `Operator`/`Owner`/`FuelSource` any more
   than it can source them. The evidence here is convergent and, I think, correct — but it is
   footprint-and-omission reasoning at prefecture level, and P5861 shows what the *segment*-level
   document looks like when one exists. Painting 江西省天然气管道有限公司 onto five rows on
   inference would swap an unsourced attribution for a differently-unsourced one.
2. **ONE consolidated `__VALIDITY__` is what MZ receives**, per the working position in P4797's
   block — not five near-duplicate per-row sentinels. Each row keeps its own sentinel because the
   fan-out wrote them and each carries row-specific evidence; this section is the anchor they all
   resolve to, and the deliverable's `Gas_Validity` tab should be read with it.
3. **The search that would settle it, stated once so it is not re-derived per row:** a
   竣工环境保护验收 filing in the jxgajc.com / 江西赣安检测技术 pattern (which is what sourced
   P5865 and P4789 at segment level), or a 江西省天然气集团 / 天然气管道公司 disclosure listing its
   own named trunk inventory. Either would resolve `PipelineName`, `FuelSource`, `Operator` and
   `Owner` for all five rows at once. This is the single highest-value follow-up in the batch.
4. **Do not let a future dedup run "fix" this by merging.** None of the five is a duplicate of
   P4944 or P4946, and P4794 is not a duplicate of P4780 (shared start area, different terminus).
   The defect is attribution, not existence — every one of these corridors plausibly exists and
   operates. The one genuine duplicate in the family was P5861, and it is handled.
5. **`PipelineName` stays out of scope for staging** for the same reason the P4785–P4790
   `OtherLanguageSegmentName` paste defect did: name columns are a column-semantics call for the
   researcher, and "QC detects, Update fixes."


### P4797 — 西气东输二线鹰潭支线(余江-鹰潭)  (row 2686, operating)

- classes: UNRESOLVED 11, REVERIFIED 2, REFS_ADDED 1, CONFIRMED 1
- tiers on ref units: inferred 11, medium 2, low 1
- harvest_opened: 14   |   cross_row_leads filed: 2 -> P4793, P4796
- **__VALIDITY__ CONFIRMED** (medium, independent=True)
**Orchestrator on P4797.** Accepted. 11 `UNRESOLVED` would normally be a weak result under the
BRIEF's calibration, but here it is the right answer and is evidenced as such: 14/14 harvest URLs
opened and none mentions 余江 or 鹰潭, ~8 Chinese search formulations tried, no sibling shard's
dominant documents name the branch, and the closest sibling (P4793, same Yujiang terminus) came out
identically. The `inferred` tier on all 11 is honest. No value changed, correctly — every candidate
source was prefecture- or province-level.

Its `__VALIDITY__` is the useful output, and it escalates a **cohort-wide question I am deferring to
one consolidated ruling** once every WEP2-Jiangxi-branch shard has landed (P4793, P4794, P4795,
P4796, P4797, P5861, plus the finished P4944/P4946). Four mutually exclusive readings of
Operator/Owner are now on the table for these rows:
1. **PipeChina itself** (per the sheet, and per the wiki specifically 西气东输分公司) — what the rows
   say today, uncorroborated by any segment-naming document.
2. **PipeChina East-section component** — the P4946/P4944 inference chain (CNPC → 国家管网 2020) at
   `medium`. Weakened for P4797 because the MEE 2016 East-section completion letter's *exhaustive*
   five-branch list does not include this branch.
3. **Phase I 54/46 JV** (江西省天然气管道有限公司) — implied by CCXI 2022's footnote 2 putting all of
   Yingtan prefecture under Phase I. This reading is not on the sheet at all.
4. **Phase II 江西省天然气集团 管道分公司 100%** — implied by P4797's own new find, a 2011-01-06
   suntront.com repost of a Jiangxi provincial planning article (hand-verified by curl):
   `管网工程涉及...鹰潭9个设区市...2012年全线建成并具备通气条件`, i.e. Yingtan among the 9 target
   cities of the planned WEP2-sourced provincial network.

Readings 3 and 4 flatly contradict each other, and both are prefecture/province-level, so under the
aggregate-vs-segment rule neither can override the other **or** the sheet. RELAUNCH_NOTES item 9's
precedent (segment-naming sources trump the CCXI footnote) cannot be applied because no
segment-naming source exists for any of these branches. The consolidated ruling therefore has to be
about what we *stage*, not about which reading is true — my working position, to confirm against the
remaining shards: leave Operator/Owner values untouched on the cohort, keep the P4946 inference chain
capped at `medium`, and carry ONE `__VALIDITY__` describing the four-way tension for MZ rather than
five near-duplicate per-row sentinels.

### P5863 — 干洲-奉新支线  (row 3327, proposed)

- classes: UNRESOLVED 12, REVERIFIED 2, CONFIRMED 2, REFS_ADDED 1
- tiers on ref units: (none) 12, high 2, medium 1
- harvest_opened: 25   |   cross_row_leads filed: 0
- **__STATUS__ CONFIRMED** (, independent=None)
- **__VALIDITY__ CONFIRMED** (, independent=None)
**Orchestrator on P5863.** Strong pass, and it is the row that validates the mid-run correction:
told that its lone `Status [ref]` was a GEM screenshot, it went and found two genuinely new
non-GEM segment-naming documents — a 2023-06 Fengxin County carbon-peak plan via a
`fengxin.gov.cn` Wayback capture plus a `ccn.ac.cn` republication — and staged `REFS_ADDED` with
the value unchanged (`proposed`), leaving the screenshot ref in place rather than proposing a
deletion. Exactly right on both halves. It also capped the tier at `medium` on the correct ground:
the two URLs are two hosts but ONE document, so they are not two independent sources even though
they clear the 2-distinct-host diversity floor. Keep that reasoning; do not let the merge promote
it to `high`.

Its `__VALIDITY__` (verdict `confirm`) settles the identity question decisively: 干洲镇 is a town
*inside* Fengxin County, confirmed from Fengxin's own government site index, and only collides with
赣州市 in romanization — tone 1 vs tone 4, different place, different row family (P4785–P4788). Not
a duplicate of P5862 either, checked field by field. **No row-existence concern survives; drop it
from the open list.**

`__STATUS__` verdict `stale` (reaffirming v2, no change evidenced) is well-built: a 2021-05
provincial 44-item key-project roster that does NOT name this branch, a 2023-06 county plan still
calling it a forward-looking "accelerate construction" target, and a 2023-07-25 EIA pre-approval
notice the agent confirmed by viewing the screenshot PNG itself. Nothing after July 2023 in either
direction. `proposed` stands; the point for MZ is that the newest evidence is ~3 years old.

Owed at merge from this row: `Length`/`Diameter`/`SegmentCost` trace to a `gas.in-en.com` page that
is genuinely unreachable (403 on every UA/protocol, no Wayback capture, SPN 520) — left
`UNRESOLVED`, correctly, and recoverable only if a mirror turns up. Its Operator/Owner carries the
same Phase I/II misattribution shape as P4791 and P4797 (row's own alt-name says 二期工程 while the
54/46 split is the Phase I company's figure), with no segment-specific source to correct it.

## Access-condition finding 2026-09-10 (orchestrator) — no blocked host holds a live ref

P5863's dead ends prompted a check of whether the batch's recurring blocked hosts are load-bearing.
`gas.in-en.com` appears in 28 payloads and `m.qcc.com` in 39 — but swept against
`already_sourced[].refs` across all 44 rows, **neither is a live sheet `[ref]` on a single row.**
They appear only as wiki-citation candidates and in `harvest_pool_failed`.

That closes a whole class of risk: the never-delete-a-ref-over-an-access-failure rule has nothing
to bite on in this batch. The only hosts actually cited in live `[ref]` cells that we could not read
are the six archive.org screenshot items — and those resolve fine (200); their problem is
provenance, not access. So there is no ref anywhere in these 44 rows that we are keeping on faith
because a WAF blocked us. Every blocked host cost us *candidate evidence*, never an existing citation.

### P5864 — 宜丰支线(上高-宜丰)  (row 3328, operating)

- classes: UNRESOLVED 8, REFS_ADDED 4, REVERIFIED 3
- tiers on ref units: presumed 8, medium 5, high 2
- harvest_opened: 25   |   cross_row_leads filed: 0

Its headline task was a redundancy hazard, and the agent retired it properly: it rendered the
qianzhan DRC plan page to an image and read Table 5 by eye rather than trusting the text layer,
finding `上高—宜丰 16` and `宜丰—铜鼓—修水 110` as two separate adjacent rows. So P5864 and P4792 are
two distinct planned projects, and P5888 (万载-铜鼓) is a third route into Tonggu from Wanzai. **No
redundancy; drop all three pairings from the open list.** No sentinel was filed for that verdict,
which is correct under work-order item 7 (sentinels only on NEW evidence of a problem) — the
no-redundancy finding lives in `notes_to_merge`.

**Length record RESHAPED at merge (orchestrator).** The agent found the only segment-naming source
for this row's length — the 2014 DRC plan — and it says **16 km against the sheet's 17.90 km**, a
~1.9 km / ~12% gap. Its reasoning was right: a 2014 planning-stage figure should not overwrite an
as-built value, and this batch has already documented that exact planned-vs-built pattern one row
down the very same table (P4792's lead to P4784: 永修-武宁-修水 planned 160 km vs 138 km as-built).
But it recorded that conclusion as `REFS_ADDED` carrying `LengthKnown = 17.90` with the
contradicting PDF as the record's only ref — and its own verification says `contains_value: false`.
That shape renders in the workbook as a tier-colored Length ref implying 17.90 is sourced by a
document that disputes it. Rule 4(e) admits a ref that agrees *within rounding*; 12% is not
rounding. So:

- `Length [ref]` → `UNRESOLVED` / `presumed`, `proposed_refs` emptied, with the full search trail
  and the planned-vs-built reasoning preserved in `researcher_notes`. Nothing now claims 17.90.
- the conflict moved to a new `__VALIDITY__` (`flag: length_discrepancy`, CONFIRMED/medium) holding
  both figures, the document's planning-stage qualifier, and the DRC plan in `proposed_refs`.
- the DRC plan **stays** a genuine ref on the four cells it does support (Location, Proposal, Fuel,
  PipelineType) — this is a reshape, not a rejection of the source.

That is the same shape P4752 used for its own Capacity/Length conflicts, so the batch is internally
consistent. `validate_shards.py P5864` PASSes on the rewritten shard. The human call owed is
whether 17.90 (as-built) or 16 (planned) is right — not an average. Note the sheet's 17.90 traces
only to the dead pipechina.com.cn `.xls` that this row's wiki cites for every cell, so its origin
cannot be checked at all.

## BATCH-LEVEL RULING 2026-09-10 (orchestrator) — the 46% counterparty, and how ownership is modelled

P5864 reported an "Owner2 name correction" against sibling P4792 and I went to see how far it
spread. It is not a two-row disagreement — it is the whole Phase I cohort, and the shards are split
six ways on how to name one entity:

| form | shards |
|---|---|
| `国家管网集团东部原油储运有限公司` (precise) | P4776 P4777 P4778 P4783 P4784 P4787 P4791 P5864 P5865 P5887 |
| `国家石油天然气管网集团有限公司` (the PipeChina parent) | P4779 P4780 P4781 P4782 P4789 P4792 P5863 |
| `国家石油天然气管网集团有限公司东部原油储运有限公司` | P4782 (Owner) |
| "National Petroleum and Natural Gas Pipeline Network Group (East China Crude Oil…)" | P4780 |
| "National Pipeline Network Group Eastern Crude Oil Storage and Transportation Co., Ltd." | P4776 P4778 P4783 P4784 |
| "PipeChina Eastern Crude Oil Storage and Transportation Co., Ltd." | P4791 P5864 |

**I verified the primary source myself** rather than adjudicating off agent reports, since this
moves 26 rows. Re-downloaded the SSE bond report (`242696_20250403_SXBW.pdf`, 35 pp, HTTP 200) and
read footnote 5 directly:

> 天然气集团持有天然气管道公司 54%的股权，剩余 46%股权由国家管网集团东部原油储运有限公司（原"中国石化管道储运有限公司"）持有。

So the document that the sheet's `Operator [ref]` **already cites** names the 46% holder as the
subsidiary 国家管网集团东部原油储运有限公司 (formerly 中国石化管道储运有限公司). The sheet says the parent. The
generic form is not a different opinion — it is a rollup of what this citation states, so under
rule 4(e) the cell is not supported by its own ref.

Rulings, in force for the merge:

1. **`国家管网集团东部原油储运有限公司` is the entity, everywhere in the Phase I cohort.** P4782's
   `国家石油天然气管网集团有限公司东部原油储运有限公司` is a **fabricated compound** (two 有限公司; no such
   registrant) and must not ship. P4780's "East China" is a mistranslation — 东部 is *Eastern*.
2. **English is `PipeChina Eastern Crude Oil Storage and Transportation Co Ltd`** — not a new
   entity: it is already in the operators/owners tab verbatim on P3782 and P6298, and
   `entity_lookup.py` surfaces no true duplicate. `Owner1` is English tab-wide (5,694 non-empty
   values, **zero** containing CJK), so the bilingual "English (中文)" strings that ten shards
   proposed are off-style; the Chinese belongs in `OperatorLocalLanguage` / `QCCOwner(业主单位)`.
3. **Ownership is modelled project-company-at-100, not as a 54/46 split in `Owner1`/`Owner2`.**
   This reverses what ~10 shards proposed, and the reason is that the tab already models this exact
   corporate structure four rows over. P4650/P4651/P4652/P5906/P5912/P5913 (Jiangsu segments of the
   same trunk family) carry `Owner1 = Jiangsu Natural Gas Co Ltd [100.00%]` with the JV split held
   only in `QCCOwner(业主单位)`: `江苏省国信集团有限公司 [51%]; 国家管网集团东部原油储运有限公司 [49%]` —
   the same PipeChina-East minority stake, and **already named precisely there**. It is also what
   the source literally supports at each level: the 54/46 is ownership *of the project company*
   (江西省天然气管道有限公司), not of the pipe. Beneficially the pipe is 54/46; literally its owner is the
   project company. So the Phase I cohort gets `Owner1 = Jiangxi Natural Gas Pipeline Co Ltd`,
   `Owner1% = 100.00%`, and the split stays in `QCCOwner`. Nothing is lost — the 54/46 fact and its
   ref survive on the same row.
   *Reviewer's option:* if MZ prefers the split in the `Owner1`/`Owner2` columns (the schema does
   provide `Owner1%..Owner11%` + `Percentage Verification` for exactly that), it is a one-column
   flip from this staging and the ref is unchanged. Flagged rather than decided silently.
4. **Scope guard — this ruling does NOT reach:** P4649/P4657 (川气东送, a genuinely different
   shareholder set: 国家石油天然气管网集团 50% / 中国人寿 43.86% / 国投交通控股 6.14%); P4661 (100% parent);
   P4797/P4944/P4946/P4947 (WEP2 — 西气东输分公司 is a branch *of* the parent and correct as written,
   pending the separate cohort ruling below).
5. **The ruling normalizes a STRING; it never assigns a phase.** P5860 is the proof that these are
   two different questions: it *removed* the 54/46 split entirely, replacing it with 江西省天然气集团有限公司
   at 100% on two segment-naming primary documents, because it is a Phase II row. Phase keys on the
   sources' wording, never on the sheet's label (RELAUNCH_NOTES item 9). So normalization applies
   only where a 54/46 split is itself correct for the row.

Also confirmed from the same bond-report page, and it settles the *structure* half of the pending
Phase I/II reconciliation: 「公司天然气业务…主要由子公司天然气集团控股的江西省天然气管道有限公司…和江西省天然气集团有限公司管道分公司
（以下简称"管道分公司"）负责运营。」 — the two operating entities coexist, 天然气管道公司 (54/46) and
管道分公司 (a 分公司, i.e. 100% Group). What the report does *not* do is assign named segments to
either, so it corroborates the two-entity model and cannot resolve per-segment phase. Per-row
phase assignment still needs a segment-naming source, exactly as P5887 did it this session.

**Open item this exposed:** `Operator` and `OperatorLocalLanguage` are blank across the whole Phase I
cohort while `QCCOwner(业主单位)` carries the value. They never entered the worklist as owed fills
because the unit already had a value in one of its three paired value columns, so the sweep never
asked for them. That is a worklist-construction gap worth carrying to the next province.

## BATCH-LEVEL FINDING 2026-09-10 (orchestrator) — a 2023 completion list names six Jiangxi branches GEM does not track

The P5860 agent filed a batch-wide lead with `project_id: null` — off the
`cross_row_leads[]` contract `{project_id, url, facts}`, so the harvester could
never have seen it. It was worth keeping, so it is resolved here rather than
dropped.

**Source.** 2023-11-23 SSE bond prospectus, 江西省投资集团有限公司 2023年公司债券
募集说明书第二期 (`static.sse.com.cn/disclosure/bond/announcement/company/c/new/
2023-11-23/240328_20231123_D5XK.pdf`), listing as **已建成并投产 as of
2023-06-30**, verbatim:

> 井冈山支线、于都支线、井（冈山支线、井开区支线）安福段、莲花支线、湘东支线、信丰-龙南-定南段、瑞金-会昌段

**Two branches map onto rows in scope** and were re-filed as targeted leads on
P5860 (see that shard): 瑞金-会昌段 → **P4786** (GEM's onward 会昌-寻乌段 is
`shelved`), and 信丰-龙南-定南段 → **P4787** (GEM's 龙南-全南段 is
`construction`, consistent only if scoped to the 全南 leg). 井冈山支线 → **P4789**,
already `operating`, consistent, no action.

**The rest have no GEM row.** None of these appears in the Jiangxi gas tab under
any name or alternative name:

| branch | note |
|---|---|
| 于都支线 | distinct from P5860's 于都-宁都-广昌-南丰 trunk — the agent checked this explicitly |
| 莲花支线 | Pingxiang-area spur |
| 湘东支线 | Pingxiang-area spur |
| 安福段 | rendered 井（冈山支线、井开区支线）安福段 in the source; the parenthetical is quoted as-is and NOT interpreted |
| 定南 leg of 信丰-龙南-定南段 | GEM stops at 龙南/全南 |
| 瑞金-会昌段 | the link between P4788 and P4786; may be a missing row rather than an unnamed part of either |

**Routing.** This is a **Discovery / coverage** finding, not a refs finding, and
this sweep has no discovery leg — so it does not become staged rows here. It goes
to `docs/country_notes/china.md` as a Jiangxi discovery candidate cluster, to be
worked as a §4 run. Six named branches reported in service by a bond prospectus
is well past the ">5 candidate clusters" escalation line in CLAUDE.md, so it is
Baird's call whether Jiangxi gets a discovery pass before the next province.

One caveat on the whole list: it is **one document, one publisher**. Its own
completion claims are dated 2023-06-30 and at least one (大余-信丰段, lead#0 on
P5860 → P4785) sits in apparent tension with a 2024-07 construction bid
amendment on the same corridor. Treat the list as a discovery pointer, never as
a status source on its own.

## BATCH-LEVEL RULING 2026-09-10 (orchestrator) — five heavily-reused documents are ONE origin, and the engine defect behind it

The single most-cited evidence base in this run is five URLs that 22 records
counted as mutual corroboration. They are not independent. Established from the
documents themselves, not inferred:

| URL fragment | what `pdftotext` shows it actually is |
|---|---|
| `242696_20250403_SXBW.pdf` (sse.com.cn) | 中诚信国际 rating report, serial **CCXI-20250789D-01** |
| `fileDownLoad.do?contentId=3375767` (chinamoney) | 中诚信国际 rating report, serial **CCXI-20262364M-01** |
| `85599868a5a6e3c2fc8db704da8180b8.pdf` (qixin) | 中诚信国际 rating report, serial **CCXI-20222923M-01** |
| `267eb2e9bb8d0f73972210e2a2241bbb.pdf` (qixin) | 中诚信国际 2022 跟踪评级报告 |
| `240328_20231123_D5XK.pdf` (sse.com.cn) | the issuer's own **募集说明书** (bond prospectus) |

Four of the five are **中诚信国际 (CCXI) rating reports on the same issuer** — one
publisher, one analytical process. And `cm3375767.pdf` is **md5-identical** to the
separately downloaded `ccxi2026.pdf` (`a47195d52877446d4f6ccb49f5912a9f`): two URLs
on two hosts serving one byte-stream.

The ruling does not rest on my judgement of rating agencies. CCXI's own reports
declare that the issuer is responsible for the accuracy of the underlying
information (「相关信息的…准确性由发行人负责」). A rating report is therefore a
**re-publication of issuer self-disclosure**, exactly the case standing rule 4
excludes ("the same wire story republished, multiple outlets tracing to one
original"). Two CCXI reports agreeing tells us the issuer said it twice.

**Applied** by `normalize_independence.py`, which now enforces two criteria —
`len(kept) < 2`, and *origin collapse*, where same-origin documents count once:

- **22 records** flipped `independent: true -> false`.
- **5 demoted `tier` high -> medium** (P4792#6, P4792#13, P5864#3, P5864#15, P5865#2).
- **P5860#0 KEPT at `high`**, deliberately. `docs/reference/confidence_tiers.md`
  line 16 makes `high` earnable by "2+ independent sources agree, **OR one
  primary/regulatory source**", and P5860#0's kept refs include the issuer's own
  募集说明书 — a primary filing. Losing the independence *claim* does not
  automatically cost the tier, so the two are decided separately (`PRIMARY_FILING`
  in the script, not a hand-edit).
- 16 records were already `medium`; their flag flipped, tier unchanged.
- Values, refs and verifications are never touched. Idempotent.

**Two shard justifications were factually wrong** and are corrected by this ruling.
P4776#4 claimed "Two independent documents (2025 SSE bond tracker vs. 2022 CCXI
credit report — different publisher…)"; P5865#2 claimed "two independent,
differently-published, differently-classed financial-disclosure documents". The
"SSE bond tracker" **is** a CCXI rating report. Same publisher, both times.

### The engine defect this exposed — fixed in shared code

`merge_qc.independence_qc()` counted independence by `origin_host(url)`. Host is a
proxy for publisher, and **document-redistribution venues break the proxy**: an
exchange, NAFMII/CFETS, or a company-data aggregator serves documents it did not
write, so two filings on `sse.com.cn` scored as two publishers when they are one
issuer's disclosures.

Fixed once, in `scripts/merge_qc.py`: new `publisher_key()` collapses
`VENUE_HOSTS` (sse.com.cn, szse.cn, bse.cn, neeq.com.cn, cninfo.com.cn,
chinamoney.com.cn, qixin.com, qcc.com, tianyancha.com) into a single
`<venue-hosted: publisher unverified>` bucket. `scripts/sweep_gates.py`'s `host()`
now **delegates** to it, so the gates and the mergers cannot drift apart.
Deliberately conservative: it can under-credit genuinely distinct publishers who
happen to file at the same venue, but it can never manufacture independence.

**Blast radius measured BEFORE fixing**, across every staged batch: **Jiangxi
only**. No other country's staged work moves. Consequence to expect on the next
gate run: the 6 formerly-`high` records now trip **gate B**, and more rows trip
**gate A** (single-publisher row) — intended, so each tier decision becomes
explicit rather than assumed.

**Recorded as a narrower sub-case, revisitable on its own:** a rating report and
the issuer's own prospectus are both issuer-sourced, but they are not the same
document class. This run treats the prospectus as primary and the rating reports
as re-publication. If MZ wants rating reports to count as a second origin against
a prospectus, that is one constant (`PRIMARY_FILING`) and a re-run, not a re-audit.

## BATCH-LEVEL FINDING 2026-09-10 (orchestrator) — `OtherLanguageSegmentName` on P4785–P4790 is one sliced sentence

Six **consecutive** rows (SheetRow 2672–2677) do not hold six Chinese segment
names in `OtherLanguageSegmentName`. They hold **one prose sentence, chunked at a
fixed width and pasted down the column**:

| PID | len | cell content |
|---|---|---|
| P4785 | 8 | 目前开工建设井冈 |
| P4786 | 22 | 山支线、井开区支线；靖安支线、湘东支线、赣州 |
| P4787 | 22 | 南支线大余信丰段；于都宁都石城段、宁都广昌南 |
| P4788 | 22 | 丰段、进贤段；赣州南支线信丰瑞金段、上犹崇义 |
| P4789 | 22 | 段、樟树新干峡江段、井开区吉水永丰段、赣州南 |
| P4790 | 16 | 支线（信丰-龙南-定南段）等项目 |

Two proofs it is one string, not six names: the four interior chunks are **all
exactly 22 characters** (a width, not a name), and **all five seams split a word**
— 井冈|山支线, 赣州|南支线, 广昌南|丰段, 上犹崇义|段, 赣州南|支线（ — so no chunk
stands alone. Reassembled, the 112 characters are one grammatical sentence:

> 目前开工建设井冈山支线、井开区支线；靖安支线、湘东支线、赣州南支线大余信丰段；于都宁都石城段、宁都广昌南丰段、进贤段；赣州南支线信丰瑞金段、上犹崇义段、樟树新干峡江段、井开区吉水永丰段、赣州南支线（信丰-龙南-定南段）等项目

— a "currently under construction" branch list.

**All six cells are wrong**, P4785's included (its chunk carries no separators, so
it looks the least broken). The fragment does not even describe its own row:
P4790's names 信丰-龙南-定南段 while the row **is** 井开区-吉水-永丰-乐安-宜黄.

**Why it matters beyond tidiness.** Anything keying on this column — name
matching, dedup, discovery guards — is matching sentence debris. It already
produced one live false positive in this run: the 靖安 hit that made the tendered
安义-靖安支线 look like it might already be tracked (see the P5862 discovery guard).

**Staged** by `stage_olsn_paste_defect.py` as one `__VALIDITY__` sentinel per row
(`class_out CONFIRMED`, `verdict concern`). Deliberately **detection only, with no
proposed `values`**: each row's correct name is already on the row, in
`OtherLanguageAlternativePipelineNames` as `二期工程, <name>`, and each sentinel
records that `<name>` — copied verbatim from that cell, never re-rendered, so it
carries the live tab's own punctuation — as the recommended replacement. Which
exact form belongs in the cell is a column-semantics call for the researcher, and
the corrupt text is evidence of a paste, not of any research finding. QC detects,
Update fixes.

## Merge-chain normalizers wired 2026-09-10 (orchestrator)

All five now run inside `run_merge_chain.sh` as steps 0a–0e, between
`validate_shards.py` and `split_shards.py`, with a re-validate at 0f. They rewrite
`shards/*.json` in place, and `split_shards.py` regenerates `ref_shards/` and
`rows/` from `shards/` on every run — so a normalizer running after it would edit
a source nothing reads again. Every one is idempotent and dry-run by default.

| step | script | what it settles |
|---|---|---|
| 0a | `normalize_independence.py` | `kept < 2`, and same-origin refs, are not independent (22 records, 5 tier demotions) |
| 0b | `normalize_owner_entities.py` | the 46% holder; projco ownership model (29 changes / 21 rows) |
| 0c | `stage_olsn_paste_defect.py` | the P4785–P4790 sliced-sentence cells (6 sentinels) |
| 0d | `normalize_cross_row_leads.py` | every lead target is one real PID (9 resolved, 7 → `batch_leads[]`) |
| 0e | `normalize_schema_keys.py` | last conformance gate (22 fixes; runs after the key-mutating passes) |

`normalize_schema_keys.py` runs **last** so it catches whatever the earlier passes
left off-contract — `normalize_owner_entities.py` deletes Owner keys, which
stranded `value_cols` declaring columns that no longer existed (the workbook
builder reads `value_cols`, so that silently drops a value). That pass now
re-syncs its own `value_cols`, making the ordering belt-and-braces rather than
load-bearing.

Two schema fixes worth naming: `class_out: "VALIDITY"` on two carried-v2 sentinels
(P4789 `__VALIDITY__`, P5861 `__REDUNDANCY__`) repeated the `ref_col` in the class
slot. `VALIDITY` is not in `SENTINEL_CLASSES`, so both degraded to `UNRESOLVED`
downstream — reading as "nothing found" on sentinels that assert a real problem.
Both now map to `CONFIRMED`, exactly as `CONCERN` already did; the class does not
imply refs (11 sentinels in this run are `CONFIRMED` with `proposed_refs` empty),
it means the finding is established.

`normalize_cross_row_leads.py` gained a **stale-key guard**. Its `RESOLVE` table is
keyed positionally, and P5862's shard was rewritten by its own agent after the
table was written, moving the discovery guard from lead #4 to #7 — so the mapping
silently fell through to the generic "no resolution was found" fallback, quietly
demoting a researched finding to an unexplained batch item. Unconsumed keys are
now reported, and the guard distinguishes *spent* (post-apply, every target
already a PID) from *drifted* (keys unmatched while leads still needed resolving).

### `batch_leads[]` — the 7 leads that address a cohort, not a row

Moved off `cross_row_leads[]` because they cannot route to one PID. These are the
**orchestrator's** to act on:

| from | subject |
|---|---|
| P4779 #8 | the CCXI 2022 qixin PDF is already a kept ref on 14 rows here — nothing to route; see the one-origin ruling above |
| P4791 #1 | systematic Phase-II-label hypothesis for Jingdezhen/Shangrao prefectures — a batch ruling |
| P4791 #2 | duplicate of the seven IA screenshots already routed from P4779 |
| P5862 #7 | **discovery guard** — 余干等支线 / 安义-靖安支线 / 安远-定南段 |
| P5866 #4 | the 2014 DRC plan is a whole-phase `ProposalYear` source; routing needs a blank-`ProposalYear` scan |
| P5866 #5 | the 46% holder correction (already the standing ruling); the new part is its own single-origin caveat |
| P5866 #6 | prefecture-level `FuelSource` corroboration naming no branch — supports many Jiujiang rows, sources none alone |

**P5862 #7 checked and confirmed** against the live gas tab (snapshot 20260910,
986 China rows, all seven name columns): 余干 = 0 hits, 安义 = 0, 安远 = 0. The two
apparent hits are not these segments — 靖安 occurs only inside P4786's corrupt
paste fragment (above), and 定南 only in P4790's `赣州南支线（信丰-龙南-定南段）`, a
Xinfeng–Longnan–Dingnan pairing distinct from the tendered 安远-定南段. So all
three are genuinely **absent** from the tracker rather than present under another
name, and they join the discovery cluster. The same jxsggzy sweep also establishes
P5862's negative: 奉新 = 0, 赤岗 = 0, 干洲 = 0, 石鼻 = 0 across 1,097 gas notices
(2016-11 → 2025-02).

## Banned-source defect: yingdodo.com (2026-09-10)

Caught while verifying the first recovery shards (P4784/P4791) rather than from any
gate — nothing in the chain was flagging it.

**What it is.** `yingdodo.com` is 小柱工程, a commercial construction-**leads**
database. The single page cited, `/html/news/201852592751.html`, is an explicit
marketing **sample**: it carries `项目样例1类` and `备注：以下样例非最新项目，仅表示内容
格式`, redacted owner phone numbers, and zero attribution (来源 / 转载 / 出处 /
责任编辑 / 数据来源 / 信息来源 all absent). That is the abarrelfull/theodora class —
restating someone else's filing without saying whose — and standing rule 5 bars it
"not even alongside corroborating sources."

**How it got in.** It is on **GEM's own gem.wiki citation list** — present in
`wiki_citations.json` for 27 Jiangxi PIDs under link text `乐平-德兴-婺源支线工程` — so
every Jiangxi agent was handed it as a seed. It was NOT in `BLOCKLIST_HOSTS`, so
`url_verifier` passed it, `merge_qc` would not have stripped it, and `sweep_gates`
would not have flagged it. Eight of nine agents that opened it correctly declined to
cite it ("opened, no match"); the ninth scored it `independent: true` while its own
note called it a "小柱工程 project-database listing".

**Citation exposure: 4 records, all P4791.** `PipelineType` (3 refs -> 2, tier stayed
low), `Pressure`, `Location`, and the recovery `Length` (each 2 refs -> 1, tier
high -> medium, `independent` true -> false). Mentions in other shards' notes are
*reading*, not citing, and needed no surgery.

**Fixed at the engine, not just here.** Added to `url_verifier.BLOCKLIST_HOSTS`, which
`harvest_wiki_citations.py`, `merge_qc.py` and `sweep_gates.py` all import — so it now
drops at harvest (never re-offered as a seed), at merge, and at the delivery gate. That
also cleans the stale 09-04 `staged_resolutions.json` baseline automatically: it holds a
v2-era `P4791 Diameter [ref]` whose ONLY ref was yingdodo, and `merge_ref_shards.py`
carries unmatched baseline records through untouched, so without the blocklist entry
that record would have reached the deliverable. `merge_qc` now strips it and converts
the zero-verified-ref `REFS_ADDED` to `UNRESOLVED` with a note — the correct rule-4(e)
outcome. Blast radius checked: 90 files, all `china-jiangxi-gas`; no other country
cites it.

**Belt to those braces:** `normalize_banned_hosts.py` (new, chain step 0a) strips
banned hosts from shards ALREADY written, since a blocklist cannot retroactively edit a
landed shard. It re-adjudicates rather than leaving a stale tier — a strip that removes
the only corroborating origin demotes `high` -> `medium` and `independent` -> false —
and exits non-zero on a record left with ZERO refs rather than auto-downgrading it,
because that is an orphan `[ref]` and a human call. Runs FIRST among the normalizers:
it removes refs, and every judgment after it counts refs.

**Concrete data consequence, verified not assumed** (ran `merge_qc.verified_refs`
against the baseline): the baseline `P4791 Length` keeps its real jxnews ref and
survives; the baseline `P4791 Diameter` had the aggregator as its ONLY ref, so it drops
to zero and merge_qc turns it into `UNRESOLVED`. No v3 shard re-researches P4791's
Diameter, so **P4791 loses its Diameter citation in this deliverable** -- correct under
rule 4(e) (the value was never independently sourced), and the 立项备案 lead below is the
route to restoring it. P4791's `Length` is unaffected because the v3 recovery shard
overwrites that baseline record with the already-corrected (medium, non-independent)
version.

**LEAD TO CHASE (do not lose).** The aggregator's figures are clearly lifted from a
Jiangxi **立项备案** filing for 乐平-德兴-婺源支线: 97 km total, 德兴境内 9.9 km, DN200,
6.3 MPa, 投资2亿元, 开工 2018-06-13. Per rule 5 that filing is the citable source. Find
it and P4791's Pressure/Location/Length go back to two independent origins.

## Wikipedia interwiki counted twice (2026-09-10)

`source_roster.md` has said since the 2026-08-27 citability reversal that "two language
editions of the same article are ONE source, not two", but nothing enforced it. The
P4947 recovery record cited en: and zh: Wikipedia for the same 9,102 km system length
and its report called them independent in as many words. `normalize_independence.py`
now collapses every `*.wikipedia.org` ref into one `WIKIPEDIA-INTERWIKI` origin.

P4947's `Length` still keeps `independent: true` on its merits — the third ref is
People's Daily, a genuine second origin — so this cost no tier. Checked separately, and
clean: none of the three Wikipedia articles in play (en/zh 西气东输, en
Sichuan–Shanghai) footnotes GEM anywhere, so no GEM figure is being laundered back in
as corroboration.

## Two QC-engine defects fixed at the merge (2026-09-10)

Both were found by running the chain and disbelieving a PASS, not by a gate firing.
Both are in shared code, so both are recorded here AND in the cross-country backlog.

### 1. `merge_qc.independence_qc()` enforced only half its own invariant

The rubric sentence is unconditional: "A unit that loses the claim cannot stay at tier
`high`; a single source is `medium` at best" (`docs/reference/confidence_tiers.md`). The
code hung BOTH halves off one guard — `if not independent or len(hosts) >= 2: return` —
so the tier demotion could only fire on a record that had already claimed
`independent: true`. A record that honestly declared `independent: false` on one
surviving publisher kept its `high`; an identical record that over-claimed `true` got
demoted to `medium`. **The bug rewarded the wrong answer.**

Measured before changing anything: **84 records across every staged batch sat at `high`
on <2 surviving publishers purely because they had not claimed independence** (56 real
ref columns; the rest `__VALIDITY__`/`__ROUTE__` sentinels). The fix enforces the two
halves independently and idempotently (already-correct records get no new note).
Unit-tested across all five branches.

**Blast radius, separated from pre-existing debt.** Re-implemented old and new logic
side by side across all 50 staging dirs: the honest delta of this fix is **0 flags and
72 tier demotions**. The much larger 1,578 wrong `independent: yes` flags / 605 tiers
were already there — `repair_independence.py` was written and never applied. That is
now a backlog item with the exact command, deliberately NOT run: applying it invalidates
~50 delivered workbooks belonging to paused campaigns, so it goes per-country as each
is picked back up. **Jiangxi v3 is clean** — this chain applies the fixed logic.

### 2. `harvest_sentinel_findings.py` bypassed QC entirely

It imported no `merge_qc` and it is the **LAST writer** of `__VALIDITY__` /
`__REDUNDANCY__` records: `merge_deepsweep_shards.py` QCs the sentinels, then
`is_old_deepsweep()` purges them, then this script re-appends them from the shards —
un-QC'd. So gates B and D (11 and 12 findings) were reporting on records the store had
already, correctly, been told to fix. The store and the gate disagreed because only one
of them ran the rule.

Fixed by importing `independence_qc` and deriving tier/independent/notes immediately
before the record is appended. Result: **gate B 11 -> 0 PASS, gate D 12 -> 0 PASS.**

**Second pass needed, and why** — four P5866 records survived the first patch. Root
cause: `merge_qc.verified_refs(urls, verifs)` treats a falsy `verifs` as "clean and
blocklist-filter only" and returns **all** the URLs, while `sweep_gates.verified()`
requires `ok && contains_value` strictly and returns none. Delegating to the lenient
fallback reproduced the same store-vs-gate split one layer down. The harvester now
spells the strict basis out inline (`{v.url for v in verifications if v.ok and
v.contains_value}`) instead of trusting the helper's absent-verification behaviour.
**Lesson for any new consumer: `verified_refs` is lenient with no verifications;
`sweep_gates.verified` is strict. Never mix them across a store/gate boundary.**

## Sentinel records carry live refs but no `verifications[]` — a shard-contract gap (2026-09-10)

Surfaced by fix #2 above. **11 records** (P5866 ×8, P4776, P4778, P4779, P4777, P4792)
carry `proposed_refs` and an EMPTY `verifications` array, so under the now-strict basis
they QC to `medium` / `independent: false` regardless of how well sourced they are.

**This is a schema gap, not weak research.** Every one is a `values: {}` sentinel —
`__VALIDITY__`, `__REDUNDANCY__`, `__STATUS__` narrative findings. The
`verifications[]` contract binds `contains_value` to a *value*, and a prose sentinel has
none, so an agent writing one honestly has nothing to put in the array. P5866's eight
records cite three statutory documents (2021 环保验收公示, 2023 安全验收公示, 2024
省能源局核准批复) and read `high` in substance; they now deliver as `medium`.

**Nothing is lost and nothing is wrong in the deliverable**: the prose carries the full
evidence, the tier on a sentinel is not a paste signal (sentinels route to the merge for
adjudication, they are not pasted), and store and gate now agree. The understatement is
the conservative direction. **Not fixed here** — redefining `contains_value` for
value-less sentinels is a shard-contract change, and a delivery is the wrong place for
one. Backlogged.

**Liveness settled, so no ref may be dropped.** All 10 distinct unverified URLs were
probed 2026-09-10: **zero 404/410**. Nine returned HTTP 200 through `url_verifier`; the
tenth, the SSE bond prospectus
(`static.sse.com.cn/.../242696_20250403_SXBW.pdf`), came back `ok=False status=None`
on the first pass and HTTP 200 `application/pdf` 4,179,660 bytes on a `curl -I` retry
(twice) and on a second `url_verifier` pass — a transient timeout on a 4 MB PDF, i.e. an
access failure, which per the standing rule is never grounds to delete a once-working
ref.

### P4752 — 赣闽浙支干线(株洲-抚州-江山  (row 2641, cancelled)

- classes: UNRESOLVED 8, REVERIFIED 4, CONFIRMED 2, REFS_ADDED 2
- tiers on ref units: presumed 8, low 5, medium 1
- harvest_opened: 9   |   cross_row_leads filed: 0
- **__STATUS__ CONFIRMED** (medium, independent=True)
- **__VALIDITY__ CONFIRMED** (medium, independent=False)
**Orchestrator on P4752.** Accepted, and it is the strongest status adjudication in the batch.
The v2 pass left this row `stale` — "no source found either confirming or overturning" — which is
the honest answer when nobody has looked hard. This pass looked hard and built a verdict out of a
*structured absence*: the branch was real and province-planned in 2014 with its own routing, a
743 km Jiangxi portion and 100亿m³/y; the NDRC's current Dec-2023 tariff table, whose entire job is
to enumerate every operating branch, lists the sibling Guangxi branch by name and omits this one;
Jiangxi's own 2022 十四五 energy plan mentions it in neither the retrospective nor the prospective
sections; and a 2025-09 industry survey written specifically to account for the 新粤浙 project's
five original branches names 赣闽浙 among them while stating the project "shrunk dramatically".
Eleven years of consistent omission from documents that would have to list it.

`Status = cancelled` confirmed, `ShelvedCancelledType = inferred` — correctly `inferred`, because no
document says 终止 or "cancelled" of this branch in so many words, and standing rule 2 puts an
inferred status change here with no fabricated URL. Note for MZ: **GEM's own wiki page for this
project currently shows `Proposed`**, so the live sheet and the wiki disagree and the sheet is the
one this pass corroborates. (The wiki was opened for orientation only and is not cited — standing
rule 1.)

Two flags on this row travel to the verifier-defect list rather than to research: its
`Operator [ref]` and `Owner [ref]` sit in gate I (`name_found=false` on the mee.gov.cn EIA notice),
and the `name_found` recheck's two apparent flips to `true` on `Jiangxi-Fujian` are the
`url_verifier` raw-markup false positive — rejected, with the reproduction recorded in
`stage_name_found_recheck.py`. The `false` flags are right: those pages are about the parent
新粤浙 system, not this branch. The 8 `presumed` tiers are the correct calibration for a
cancelled-by-omission row.

### P4778 — 高安-新余输气干线  (row 2667, operating)

- classes: UNRESOLVED 7, REVERIFIED 5, REFS_ADDED 4, CONFIRMED 4
- tiers on ref units: medium 8, presumed 6, low 1
- harvest_opened: 25   |   cross_row_leads filed: 6 -> P4784, P4789, P4790, P4791, P5860
- **__VALIDITY__ UNRESOLVED** (n/a, independent=False)
- **__REDUNDANCY__ CONFIRMED** (medium, independent=False)
- **__VALIDITY__ CONFIRMED** (medium, independent=False)
- **__VALIDITY__ CONFIRMED** (medium, independent=False)
- **__VALIDITY__ CONFIRMED** (medium, independent=False)
**Orchestrator on P4778.** This is the survivor of the batch's one genuine duplicate pair, and the
row where the WEP2-cohort hypothesis got tested against a segment-naming document (see the
BATCH-LEVEL RULING above). **P5861 retires into this row**, ruled 2026-09-10 and staged by
`stage_p5861_retirement.py` at merge-chain step 0e2. Three load-bearing items, all new relative to
this shard's own reading: PipeChina's live 2026 公平开放 workbook enumerates all 34 facilities of
国家管网集团西气东输分公司 and contains no Xinyu branch (`西气东输` extracts mechanically from the
file, `新余` does not); the 2014 DRC plan names 高安-新余 as one of six 已建成 Phase I 干线; CCXI 2022
separates the two networks by gas source and operator. P5861's WEP2 framing, its `FuelSource` and
its PipeChina-100% ownership were one mis-attribution, and this row already carries the sourced
川气东送 `FuelSource` (canonicalized to `Sichuan–Shanghai Gas Pipeline` at step 0e4) and the sourced
54/46 ownership — so **nothing from P5861's contradicted cells is to be pasted.**

What transfers, staged on this row: `Pressure` 6.3 MPa and `EndPrefecture`/`District` Xinyu. What is
flagged and deliberately *not* staged, three sentinels:

- **LengthKnown 69.21 km** — a human call with two defensible answers, and read the asymmetry
  carefully. P5861's own argument that the figure is impossible refutes a 69.21 km *WEP2* branch;
  it says nothing against a 69.21 km *Phase I* 高安-新余 trunk, which is the pipe that survives
  (Gao'an to Xinyu is ~55 km straight-line). The two-decimal precision reads like a figure someone
  once copied off a filing. Carry it as unsourced legacy data and accept a `MISSING_REF` owed unit
  next sweep, or let it die with the row — but if carried it must **never** be cited to a WEP2
  source.
- **The retired row's name** — the pending-list proposal to move
  `西气东输二线新余支线（高安-新余）` into `OtherEnglishNames` is **declined**. That string is not an
  alias for this pipe, it *is* the mis-attribution being retired, and promoting it to a name column
  would re-seed the next dedup/discovery run with the exact string that produced the duplicate.
  Record the retirement in `ResearcherNotes` instead, where a human reads it and no matcher indexes
  it.
- **StartMonth1 = 12** is probably a cross-phase paste: `2010 年 12 月` is the 开工 date of Jiangxi
  **Phase II** in the 2023 SSE prospectus, which dates Phase I's first commissioning to 2010年6月
  and its construction start to 2008年10月. The *year* survives independently (petrobest bounds
  Phase I through-connection to 2010 with Xinyu among the six cities served), so `StartYear1 = 2010`
  stands; clear the month unless a document dates this trunk's commissioning.

Its `__VALIDITY__` is `UNRESOLVED` and that is right: three mutually inconsistent Phase I
network-wide totals were opened (870 km / 6 trunks + 1 branch per the DRC plan; 876 km per the
petrobest contractor page; a design-stage 680 km and 5.7 bcm/y in a 2008 pre-construction article),
none apportionable to this trunk. Same conflicting-aggregate shape already carried on P4777 —
flagged, not re-adjudicated, and no figure staged onto `Length`/`Capacity`.

### P4790 — 井开区-吉水-永丰-乐安-宜黄输气管道  (row 2679, proposed)

- classes: REVERIFIED 7, REFS_ADDED 4, UNRESOLVED 3, CONFIRMED 3
- tiers on ref units: medium 11, (none) 3
- harvest_opened: 23   |   cross_row_leads filed: 0
- **__STATUS__ CONFIRMED** (, independent=None)
- **__VALIDITY__ CONFIRMED** (, independent=None)
- **__VALIDITY__ CONFIRMED** (None, independent=None)

**Orchestrator on P4790.** Status is reaffirmed `proposed` and needs no change: the new
sohu/大江网 evidence is a **provincial 44-item roster of projects still to be implemented in
2021-2023**, naming this exact segment as item 17 three years after ichinaenergy's projected 2018
completion. That is a positive statement that the 2017/2018 schedule slipped, not merely an absence
of completion news — a much stronger reaffirmation than the carried v2 `stale` verdict rested on.

The **OLSN paste defect** is proven and is the batch's most consequential non-research finding: one
prose sentence chunked at a fixed 22-character width and pasted down SheetRow 2672-2677
(P4785-P4790). Two independent proofs — the four interior chunks are all exactly 22 characters, and
all five seams split a word — and the reassembled 112 characters are one grammatical
"currently under construction" branch list. The cell does not even describe its own row. Staged as
**detection only with no `values`** (a name column is never its own `[ref]`), which is right:
the exact form the cell should take is a column-semantics call, and the corrupt text is evidence of
a paste, not of any research finding. It has **already produced one false positive** — the 靖安 hit
that made the tendered 安义-靖安支线 look tracked — so anything keying on OLSN (name matching,
dedup, discovery guards) is matching sentence debris on six rows, including P4785's, whose chunk
carries no separators and so looks least broken.

**The cohort-wide Phase I/II operator check this row asked for is now run, and it does NOT produce a
cohort-wide correction.** Twenty-one rows in this batch stage or echo the 54/46 Phase I JV; four of
them are *named* Phase II — P4787 (赣州南支线 龙南-全南段), P4789 (井冈山支线, Operator only), P4791
(乐平-德兴-婺源) and P5863 (干洲-奉新支线) — but CCXI's geography splits them two ways, and the name
label is the least reliable discriminator:

- P4787's 龙南/全南 and P4789's 井冈山 sit **inside** the Phase II footprint CCXI enumerates
  (井冈山/莲花/永新/大余, WEP2-fed, 管道分公司 100%, no JV). The 54/46 is wrong on both. P4789's
  `Owner1` already carries the Group and only its Operator needs moving — which is the explanation
  for the "internal Owner/Operator split" flagged on that row.
- P4791's 乐平/德兴/婺源 (Jingdezhen-Shangrao, northeast) and P5863's 奉新 (Yichun) sit inside the
  **Phase I** 川气东送-fed footprint. On **P4791 that settles it**: the 54/46 is right and the
  `Phase II` label in the row name is the defect, because this row's own source independently calls
  乐平-德兴-婺源支线 a **Phase I** project — external corroboration, and the explanation for P4791's
  separately-flagged Phase-II label defect. On **P5863 it does not settle it, and I overstated this
  above**: geography reads Phase I, but chronology reads the other way — the row is a **2023** project
  and 管道分公司 was formed in 2016 expressly to build the Phase II remainder, so a 2023 build inside
  the fn2 county footprint is exactly the case where the two tests disagree. Treat P5863's phase as
  genuinely open (P5862's batch-wide sentinel frames it as either/or, and that is the right weight).
  P5863's own shard reached the same suspicion from the other end and correctly declined to stage a
  corrected split with no segment-specific source.
- P5863's parent-form 46% string survives `normalize_owner_entities.py` untouched, and that is
  correct, not a gap: the record is `UNRESOLVED`, so it echoes the sheet rather than proposing
  anything, and the normalizer only touches `REFS_ADDED`/`REVERIFIED`.

So the operator fix for P4787/P4789 belongs in the **Phase I/II per-segment reconciliation** still
owed, and that ruling must decide phase from **geography and gas source, never from the name
label**. Nothing further staged this round.

**All five "no PID identified" sibling finds are rows in this very batch** — 井冈山支线 = P4789,
乐平-德兴-婺源支线 = P4791, 樟树支线 = P5865, 湖口-金砂湾-彭泽支线 = P5866 + P5886, 丰城至抚州段 =
P4776. **Nothing goes to Discovery.** The reason no `cross_row_leads` entry could be filed is a
worklist gap, not an absence: `worklist.json` units carry `pipeline_name`/`segment_name` in
**English only** (`"Huangmei-Jiujiang branch"`), with no CJK form anywhere, so a CJK keyword lookup
against it cannot match by construction. Fix that before the next CJK batch — it silently converts
"already tracked" into "possible discovery candidate", the most expensive error a sweep can make.

Reassuringly, every figure surfaced here was already resolved *better* on its own row:

- **井冈山支线** 203 km / 3.15亿 m³/y / RMB 520M / 2016-09-20 → 2018-11-26, against P4789's staged
  129 km, 0.32 bcm/y, RMB 520M, 2018-11. Cost, capacity and commissioning agree exactly; the 203 km
  is the **combined three-branch** project (mainline + 安福 + 莲花), which P4789's own `Length [ref]`
  note already identifies and rejects as a second source. Its `Capacity` record goes further and
  names 0.32 as very likely that same aggregate-vs-segment mismatch — so this find corroborates the
  *problem*, not the value.
- **乐平-德兴-婺源支线** 97 km / 2020-12-09 / 2.8亿 / RMB 380M, against P4791's staged 0.28 bcm/y,
  RMB 380M, `ConstructionYear/Month 2020-12` and Start 2022-09. Capacity and cost agree exactly, and
  2020-12-09 is the 开工 date P4791 already staged — two different events, not a conflict. **Nothing
  is owed here either, and my first reading of it was wrong twice over**: P4791's `LengthKnown` is
  not blank (the sheet already carries 97.00, so the unit is `MISSING_REF`, not `MISSING_VALUE`), and
  its `Length [ref]` is **already `REFS_ADDED` at 97.00 in `ref_shards_recovery/`** off a 大江网/德兴
  municipal-media groundbreaking report — the same origin family this find surfaced. The recovery
  record ran a second source too (yingdodo, 2018-05-25) and the banned-host strip correctly removed
  it, which is why the tier reads `medium` rather than `high` and why a genuinely independent second
  origin for 97 km is still worth having.
- **丰城至抚州段** trial operation 2011-08-29 is the **same Sina article** P4776's `Start [ref]`
  already cites. That record's `second_source_owed` note therefore stands unresolved — this does not
  discharge it.
- **樟树支线** and **湖口-金砂湾-彭泽支线** are the same jxgajc.com Wayback family P5865/P5866 already
  cite. P5866's shard also records the **金砂湾-vs-金沙湾** orthography that made the verifier read all
  twelve of its refs as system-only — an `OtherLanguageAlternativePipelineNames` candidate and a
  standing matcher gotcha.

All three sentinels here carry `tier`/`independent` empty or `None`: the benign class (no refs, no
verifications, nothing to claim), not the off-contract case P5887 has.

### P4793 — 西气东输二线高余线(高安-余江)  (row 2682, operating)

- classes: UNRESOLVED 11, REVERIFIED 3, REFS_ADDED 1, CONFIRMED 1
- tiers on ref units: presumed 6, n/a 5, medium 3, low 1
- harvest_opened: 14   |   cross_row_leads filed: 7 -> P4794, P4795, P4796, P4797, P4946, P5861, P5865
- **__VALIDITY__ CONFIRMED** (medium, independent=False)
**Orchestrator on P4793.** Accepted as the cohort anchor it declared itself to be; the ruling above
is issued on its evidence plus four more shards. Its own contribution is the CCXI two-operator
split — Jiangxi has exactly two provincial long-distance gas operators, cleanly divided by gas
source — and the negative that WEP2's own East-section branch structure in this corridor is exactly
two named PipeChina branches (南昌-上海支干线 = P4944, 樟树-湘潭联络线 = P4946), neither of them
高安-余江.

Two judgment calls in this shard I want to keep, because both resist an easy shortcut. It records
the 高安-鹰潭供气管道 tie-in named in P5865's Zhangshu-branch completion EIA as a *geographically
plausible but unconfirmed* lead — Yingtan administers Yujiang (2018 county-to-district conversion),
so this could be the same corridor — and refuses to treat "could be" as identity. And it explicitly
rules out 高安-新余 as a naming collision: superficially similar, but a different line by phase and
gas source. That second call is now independently confirmed, since 高安-新余 turned out to be P4778
and P5861's duplicate pair. Nothing staged as a value change, correctly.

### P4794 — 西气东输二线九高线(九江-新建-高安)  (row 2683, operating)

- classes: UNRESOLVED 11, REVERIFIED 3, REFS_ADDED 1, CONFIRMED 1
- tiers on ref units: presumed 6, n/a 5, medium 3, low 1
- harvest_opened: 14   |   cross_row_leads filed: 4 -> P4778, P4780, P4793, P5861
- **__VALIDITY__ CONFIRMED** (medium, independent=True)
**Orchestrator on P4794.** Accepted, and this is the shard that made the cohort ruling issuable —
it turned v2's loose timing tension (`StartYear1` 2010-08 lines up with 川气东送's 2010-06 Jiujiang
arrival, not WEP2's 2011-09) into four convergent documentary threads: WEP2's exhaustive 一干两支
Jiangxi structure with no Jiujiang-Gao'an component; the MEE 2016 East-section notice reaching the
same result through a different regulator, in which 九江市 appears only as a prefecture whose
environmental bureau *monitors* the completed mainline; the separately-verified Yangtze-crossing
notice landing that mainline at 瑞昌市码头镇 — which is the actual confirmed WEP2 presence in
Jiujiang prefecture, a river crossing and not a branch; and CCXI's footnote 2 putting both of this
row's endpoints inside Phase I's 42-county footprint while Phase II's ~1,500 km is disjoint and in
the far southwest.

Its restraint is the part worth keeping on the record. It did **not** file `__REDUNDANCY__` against
P4780 (九江-南昌): shared start area, different terminus, not a same-pipe duplicate — and it grepped
every sibling payload and shard in the batch (P4776–P4797, P5859–P5866, P5886–P5889) to confirm no
other row claims 九江-新建-高安 / 九高线 / 新建-高安 as its own segment, so there was no candidate PID
to pair against. Classification concern, not an existence question. Nothing staged.

### P4795 — 西气东输二线黎川支线(临川-黎川)  (row 2684, operating)

- classes: UNRESOLVED 13, CONFIRMED 2, REFS_ADDED 1
- tiers on ref units: presumed 12, medium 2
- harvest_opened: 14   |   cross_row_leads filed: 1 -> P4793
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (medium, independent=True)
**Orchestrator on P4795.** Accepted; two sentinels, and they are different kinds of finding.

The `high`-tier one is a clean **paste-contamination defect**: `OtherLanguageSegmentName` reads
`河北曹妃甸新天LNG接收站外輸管线` — a real, distinct Hebei LNG-terminal outbound line with no
connection to a Jiangxi provincial gas branch. The correct Chinese name for this row is already
sitting one cell over in `OtherLanguageAlternativePipelineNames`
(`西气东输二线黎川支线（临川-黎川）`). The shard checked whether GEM tracks the Caofeidian line
separately before calling it contamination, which is the right order of operations — it rules out
a duplication angle and leaves a pure data-entry defect. Clear the cell or copy the adjacent name
into it: a name-column call for the researcher, not staged, same convention as the P4785–P4790
sliced-sentence defect.

The second is this row's contribution to the cohort ruling, and it is the sharpest single piece of
naming-convention evidence in it: the DRC plan's Table 5 **prefixes every WEP2-sourced segment with
西二线**, and the entry that corresponds to this row (抚州-南城-黎川, 128 km) carries no such prefix.
Add that Linchuan was already Phase-I-connected per the same plan's Table 4, and 抚州 is named in
the Phase I JV operator's own stated 8-prefecture territory. Gate A flags this row for source
diversity (one sourced unit, one host — `img9.qianzhan.com`); that is a true reading of a row where
the only segment-level document found was the provincial plan, and the fix is the
竣工环境保护验收 search named in the ruling, not another host.

### P4796 — 西气东输二线余景线(余江-景德镇)  (row 2685, operating)

- classes: UNRESOLVED 12, REFS_ADDED 2, CONFIRMED 1
- tiers on ref units: inferred 12, high 1, low 1
- harvest_opened: 14   |   cross_row_leads filed: 2 -> P4793
- **__VALIDITY__ CONFIRMED** (medium, independent=True)
**Orchestrator on P4796.** Accepted, including its refusal to resolve. This row carries the
cohort's most direct contradiction — the 2014 DRC plan states WEP2's Jiangxi footprint covers
`途经除景德镇外的10个设区市`, every prefecture **except** Jingdezhen, which is this row's own
endpoint — and it names the province's actual Jingdezhen-serving trunk as 九江-景德镇, 川气东送-fed.
CCXI 2022 independently puts both endpoints (Jingdezhen and Yingtan, which administers Yujiang)
under Phase I.

And then the shard argues the other side, which is why I trust it: the same DRC plan lists a
still-planned 13 km WEP2 Yingtan gate-station tie-in dated around 2014, timeline-consistent with a
genuine separate WEP2-fed lateral from Yujiang to Jingdezhen built *alongside* the older
川气东送-fed trunk. Two lines feeding one city from different directions and different sources is
ordinary, and would explain why GEM's row and the provincial trunk have different names. It lands
on Phase I as the weight of evidence and stops there, because no document names 余景线 or
余江-景德镇 directly. Right call. The 12 `inferred` tiers are honest and the `low` cap on the
FuelSource unit is the correct consequence.

Two things to carry forward. The follow-up ladder is specific and was genuinely exhausted (the
CAPTCHA-walled jxic.jczh.com / jczh.com tender notices via direct fetch *and* r.jina.ai, the
m.qcc.com / sasac.gov.cn / reuters.com candidates, the dead wiki footnote, and the WebSearch budget)
— a human with a fresh budget and a solvable CAPTCHA is the next step, not another agent pass. And
this row's Jingdezhen exclusion **collides with P4779's own sentinel**, where jdzmc.com 2009 says
the 九江-景德镇 line's resource base is both 川气东送江西支线黄梅——九江管线工程 *and* 西气东输二线.
Both cannot be flatly true as stated; that tension is routed to the Phase I/II per-segment
reconciliation, not settled here.

### P4928 — 西三线东段(吉安-福州)  (row 2814, operating)

- classes: REFS_ADDED 7, UNRESOLVED 3, CONFIRMED 3
- tiers on ref units: high 5, presumed 2, medium 2, inferred 1
- harvest_opened: 40   |   cross_row_leads filed: 4 -> P4931, P4934
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (medium, independent=True)

**Orchestrator on P4928.** Two `high` candidate value changes and one unsupported-value flag. Both
changes are the same shape — GEM holds a **system** figure on a **section** row — and both are
well-sourced enough that I would apply them; but they are value changes on an `operating` row, so
they route to Update and stay out of this batch's paste surface.

- **Capacity 30.00 → 15.00 bcm/y.** Four hosts, three document classes (MEE 环审〔2015〕231号, the
  operator's 2021 EIA filed with 泉州市生态环境局, SASAC 2018, 中新网 + 福州新闻网 2016-12-12), every
  one of them segment-naming. The corollary is the load-bearing part: **15 must not travel to
  P4934**, whose 30 bcm/y is the WEP3 *system* design capacity and is correct there. And the section
  is not uniform — the same 2021 EIA rates the shorter 漳州-福州 leg at 10 bcm/y — so 15 is the
  headline design throughput and the 吉安-漳州 rating, not a whole-section constant.
- **LengthKnown 817.00 → 832.40 km.** The strongest single finding in the WEP3 family, because the
  four published lengths form an **explained sequence** rather than a disagreement: 817 = the
  original 环审〔2012〕196号 design (what GEM holds), 830 = the design after MEE approved eight route
  realignments (环审〔2015〕231号, with 12 stations + 36 valve rooms), 825 = the operator's own 2021
  EIA arithmetic (509 + 316), 832.4 = **as-built**, given identically by SASAC's 2018-12-14
  completion-acceptance release and by three 2016-12-12 commissioning articles. The row is
  `operating`, so as-built wins, and it is also the best-sourced of the four. If the length is
  applied the **station/valve counts move with it** (11 + 40 → 12 + 36) or the row becomes
  internally inconsistent.
- **Operator/Owner is unsupported.** Nothing found names 国家管网集团联合管道有限责任公司 in
  connection with 西气东输三线东段（吉安-福州）. What the segment-naming documents name is
  国家石油天然气管网集团有限公司西气东输分公司 and its 南昌输气分公司, and NDRC's 2023 table puts the
  section under PipeChina's inter-provincial trunks. The 100% single-owner shape is not in doubt
  (福建省发改委's 2019 核准 shows the pre-transfer holder was 中国石油管道有限责任公司 at 100%
  through the same 西气东输分公司), so this is a naming fix, not an equity finding. It belongs inside
  the **WEP-family `Owner1` style ruling** still owed — P4934/P4947 staged CJK, P4944/P4946 English —
  and should not be decided for this row alone.

### P4934 — P4934  (row 2820, operating)

- classes: REFS_ADDED 8, CONFIRMED 3
- tiers on ref units: high 6, medium 2
- harvest_opened: 40   |   cross_row_leads filed: 5 -> P4928, P4931, P4947
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (medium, independent=True)

**Orchestrator on P4934.** The trunk parent, and the row where three system-vs-section traps get
pinned down at once. Nothing here changes Status or the staged `StartYear1`.

- **The 2014-vs-2024 west-section date is resolved for 2014**, on four independent grounds (SASAC
  2018 "both segments finished and fully operational"; 国家能源局西北监管局 2023 counting the west
  section inside the operating system through end-2022; 中新网 2014-09-01 全线贯通; 国家能源局
  2012-10-22 expecting 霍尔果斯-乌鲁木齐 in service by end-2012), and the 2024 text is **one origin**
  mirrored verbatim. **2024 must not be staged here or on any WEP3 sibling.** Flagging it rather
  than dropping it is the right call — a resolved conflict that goes unrecorded gets re-adjudicated
  from scratch by the next pass that meets the sentence.
- **The scope table is the row's real output.** `SegmentCost` 125e9 RMB is *correct* at system scope
  and sourced (中新网 2012-10-22: 1 干线 + 8 支线 + 3 储气库 + 1 LNG peaking station, 总投资1250亿元),
  which **resolves** the carried v2 SegmentCost-scope `__VALIDITY__` for this row. Three other
  investment figures exist and none belongs in the cell — notably 436.48亿, the **middle section's**
  2014 核准. Length 7,378 km is the system (1 trunk + 8 branches) and matches the row's own stated
  extent: **nobody is to "correct" it to the 5,220 km trunk-only figure.** Pressure is 12/10 by
  section, so the staged 12/10 range is the honest form; a scalar would be wrong at one end.
- **The chinanews.com.cn decoding failure is a live tooling defect and still open** — and it is
  *not* the 09-04 BLOCKED fix. The host serves GB-mixed bytes that strict gb18030 **and** utf-8 both
  reject, so `url_verifier` extracts no text at all and returns "200 but name not found" for every
  chinanews article, including one already sitting in this row's `SegmentCost [ref]`;
  `errors='replace'` reads them cleanly. Encoded here as hand-confirmed false negatives with the
  evidence in each note, per convention — but the fix belongs in `scripts/url_verifier.py` beside the
  two already filed (the `_match_surface` raw-markup false positive that step 0e5 adjudicated, and
  the missing IPv4 retry on a 403). **Three verifier defects surfaced by one batch** is itself a
  finding worth carrying to the script's next edit window.
- **Ownership: the staged PipeChina 100% is a default, not a documented equity figure**, and the note
  is right to say so out loud. The only split any primary document states is the **2012 planned** JV
  in Baosteel's 临2012-050 (CNPC 325亿/~52%, 宝钢 80亿/~12.8%, 华宝 20亿/~3.2%, plus 社保基金 and
  国联能源基金; 625亿 registered capital, 20-year term) — prospective (拟/框构协议), and nothing found
  confirms it was formed on those terms, survived the 2019-20 restructuring, or holds the pipe today.
  What *is* documented is operatorship. Ruling: apply PipeChina 100% consistently across the three
  trunk parents (P4657/P4934/P4947 all landed there), and **adjudicate the 2012 minority stakes once
  for the whole WEP3 family**, not row by row — the same discipline as the WEP2 cohort ruling above.
  If the reviewer wants subsidiary-level precision, the sheet's own QCCOwner naming
  国家管网集团西部管道有限责任公司 is the candidate, and RELAUNCH_NOTES item 2 (the Phase I 46% holder
  is the subsidiary, not the parent) is the analogous trap.

Cosmetic: this block is headed `### P4934 — P4934` because the payload carries no CJK
`name_forms["segment"]`, so `append_row_note.py`'s label falls back to the PID. Same on P4947. Not
patched.

### P4944 — 西气东输二线南昌-上海支干线  (row 2830, operating)

- classes: REFS_ADDED 13, CONFIRMED 2, UNRESOLVED 1
- tiers on ref units: high 11, medium 2, (none) 1
- harvest_opened: 0   |   cross_row_leads filed: 3 -> P4946, P4947
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (medium, independent=True)

**Orchestrator on P4944.** One clean correction and one convention question; the pipeline itself is
real, operating and correctly classified.

- **The start location is wrong, and the fix is not one cell.** The sheet says 东阳镇, 安义县 (Anyi
  County, Nanchang); three branch-naming sources on three hosts put the 南昌分输压气站 offtake where
  this branch begins in 大城镇, **高安市** — which is in **Yichun** prefecture, not Nanchang. So
  `StartLocation`, the county/district **and** the prefecture all move together. Gao'an and Anyi are
  adjacent counties either side of the prefecture boundary, so this reads as a place-name slip rather
  than a different pipeline, and no source places any facility of this branch in Anyi. It also
  cross-checks: 大城镇/高安 is the same WEP2 offtake node that anchors P4778's transferred `Pressure`
  and the DRC plan's 高安-新余 trunk — Gao'an is where WEP2 hands off into the Jiangxi structure.
  `EndLocation` and both end-province values are supported and stay.
- **StartYear1 2011 vs 2012 is a convention call for Baird, with both readings sourced.** Gas reached
  Jiangxi via WEP2 in 2011-09 and CNPC said in 2011-07 the branch would be done by year-end; but the
  NEA Zhejiang office's own filing puts the Zhejiang section into production in 2012-05 and the
  Jiangxi DRC plan dates full completion to 2012-04 — so the branch cannot have been delivering to
  its Shanghai terminus in 2011. First-gas vs full-line commissioning. The identical question is open
  on P4946 (its one-month Start gap) and implicitly on P4934's west section: **decide it once for the
  WEP family.** `StartMonth1` stays blank either way.

Both records read `CONFIRMED` only because step 0f rewrote `CONCERN` (not in BRIEF's set); the audit
line is inline in each note. **Do not read `CONFIRMED` here as "no action owed"** — one is a
multi-cell correction and the other is a question for the reviewer.

### P4947 — P4947  (row 2833, operating)

- classes: REFS_ADDED 7, CONFIRMED 1
- tiers on ref units: high 4, medium 3
- harvest_opened: 14   |   cross_row_leads filed: 5 -> P4928, P4934, P4944, P4946
- **__VALIDITY__ CONFIRMED** (high, independent=True)

**Orchestrator on P4947.** The WEP2 trunk parent. Existence and scope are confirmed against the
NDRC 2023 PipeChina tariff table — exactly two regulated segments, 新疆霍尔果斯→宁夏中卫 and
宁夏中卫→广东广州, matching the sheet's Khorgas→Guangzhou extent — and the two MEE 竣工验收 letters
covering the same two halves. **No duplication with the branch rows**: the NDRC table and 环验〔2016〕
100号 both name them as 支干线 *of* this trunk. That is the same document family that anchors the
WEP2-Jiangxi-branch cohort ruling above, and the reason the ruling could be issued at all — this row
is where the trunk's structure was established exhaustively enough for absence from it to mean
something.

- **The v2 owner misattribution is upheld and now evidenced.** `China Petroleum West Pipeline Co Ltd`
  is a **west-section-only, pre-2020** attribution: the NEA Henan filing shows a different CNPC
  company (中石油西气东输管道公司) on the east section, and CNPC's trunk assets moved to PipeChina
  effective 2020-10-01. 国家石油天然气管网集团有限公司 [100%] staged on both units.
- **Pressure is section-dependent** — MEE gives 12 兆帕 west mainline, 10 east mainline, 10 for every
  支干线/联络线 — and one cell cannot hold both. 12 stays, as design maximum. The reviewer's
  alternative (blank on the parent, 12/10 on section rows) is cleaner in principle, but WEP2 has no
  west/east section rows the way WEP3 does, so blanking would lose the figure entirely.
- **Length: 9,102 km is right for the sheet's extent and is deliberately not re-staged.** The note
  exists so nobody "corrects" it to 8,704 km (NEA/界面: 干线 4,918 + 8 支干线) or to the Jiangxi DRC
  plan's 8,653; the two MEE acceptance packages sum to 7,813.84 km, a third scope again, and the
  sub-line count is quoted as 8 支干线 or as 3 (人民网 2021, counting only the large ones) — the same
  scope artefact in another column. **This row is the batch's clearest illustration of why a Chinese
  trunk row's extent must be stated before any of its figures is judged**; the identical trap sits on
  P4934 (7,378 vs 5,220) and P4928 (30 vs 15).
- `Owner1` is staged in CJK here and in English on P4944/P4946 — the WEP-family style question,
  still owed and listed above.

### P5859 — 高安-丰城输气干线  (row 3323, operating)

- classes: UNRESOLVED 9, REVERIFIED 5, REFS_ADDED 2
- tiers on ref units: presumed 8, medium 6, low 1
- harvest_opened: 25   |   cross_row_leads filed: 0
- **__VALIDITY__ UNRESOLVED** (n/a, independent=False)

**Orchestrator on P5859.** `__VALIDITY__` is `UNRESOLVED` and that is the correct terminal state,
not a failure. The concern now rests on four exhaustive inventories, none of which contains
高安-丰城: the 2014 DRC plan's six Phase I trunks (which P4777 independently re-derived from a
57-document base, and all six of which already map to separately-tracked GEM rows), the DRC plan's
Table 5 72-segment expansion (re-read line by line — the nearest pairings are 大城-高安 11.2 km and
what may read as 高安-吉水 18.2 km, both different pairings), P4777's own documentation, and this
row's 25 opened documents. Both endpoints are real Phase I nodes — Gao'an is a named franchise city
(CCXI 2022), Fengcheng is the end of P4782 and the start of P4776 — but they are **never paired**.
And petrobest, the row's own system-level source, names **neither** endpoint (zero occurrences of
both strings), a weaker evidentiary position than sibling P4778, where petrobest at least names
Xinyu.

Two things on top of that.

**This row's negative is load-bearing evidence elsewhere and must not be flattened.** The absence of
高安-丰城 from the DRC plan's six named trunks is one half of the **qianzhan-vs-SSE-2023 decomposition
conflict** still open at P4777 — qianzhan reads the Phase I trunks as 南昌-丰城 + 高安-新余, SSE's 2023
bond report as 南昌-新余 + 高安-丰城. SSE 2023 is the one document that *does* pair Gao'an with
Fengcheng. So the real question is not only "does this pipe exist" but "which of two published
decompositions of the same trunk mileage is right", and P5859 is the row where the sheet has taken
SSE's side. That is exactly why merge-chain step 0e5 refused to flip this row's `FuelSource`
`name_found` on the DRC plan: **the correct negative is the datum**, and flipping it would have
destroyed the evidence.

The note's three-way framing — (a) real, distinctly-named later-built infill this batch's sources
don't cover, (b) a conflation of the adjacent already-tracked 高安-新余 + 南昌-丰城/丰城-抚州 pair,
(c) a query against GEM's own wiki-edit history for the uncited 高安-丰城输气干线 section — is right,
and **(c) is the actionable one**, with its constraint correctly stated: this pass may cite no GEM
surface, so it is a question for the researcher who wrote that section, not a research task.
**Explicitly not a delete recommendation.** Phase I grew from 870 km in the 2014 plan to 876 km per
petrobest, so some post-2014 mileage exists somewhere, and `UNRESOLVED` means nothing was found —
never that something narrower was found (rule 4(e)).

Its tier profile (presumed 8, medium 6, low 1) is the honest shape for a row whose every value rests
on system-level sourcing, and the `Start [ref]` StartYear1 2010-vs-later conflict carries forward
unresolved.

### P5860 — 西三线于都分输站-宁都-广昌-南丰输气管线  (row 3324, construction)

- classes: REFS_ADDED 11, UNRESOLVED 2, CONFIRMED 2
- tiers on ref units: high 7, medium 4, presumed 2
- harvest_opened: 27   |   cross_row_leads filed: 3 -> P4785, P4786, P4787
- **__STATUS__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (high, independent=True)

**Orchestrator on P5860.** A clean row, and the one place in this batch where a `stale` verdict was
correctly *downgraded* to a `confirm`. The distinction matters and the shard states it exactly:
`stale` is the right call when no fresher evidence exists either way; here fresher evidence exists
(a 2023-06-30 bond prospectus that enumerates which sub-legs of the family are complete and
conspicuously omits this one; a 2025-03-26 CCXI report — different preparer, different document
class — still framing the containing Phase II programme as under construction; a 2021 provincial
roster ruling out shelved/cancelled) and it **points the same way as the current value**. Keep
`Status = construction`. Note the shape of the negative: the bond prospectus is a *positive
enumeration* of completions, so the segment's absence from it is evidence, not silence — the same
inferential move that carries the WEP2 cohort ruling and P5859's negative.

The operator/attribution tension is **resolved** for this row rather than merely flagged, and it is
the model for how the cohort question should be answered: two segment-naming primary documents
spanning the entity's 2016 and 2020 names, verified for *this* row specifically, put it at
江西省天然气集团有限公司 100% (Phase II, 管道分公司, WEP3-fed) instead of the Phase I 54/46 JV. That
is why `normalize_owner_entities.py`'s 54/46 gate exists — this row must pass through untouched, and
it does.

Two loose ends, both correctly placed rather than repeated here: the `SegmentCost` figure spans a
three-branch approval family (the unrelated Jinxian spur is one of them), documented on the
`SegmentCost` record itself; and the three `cross_row_leads` to P4785/P4786/P4787 include the
**P4785 大余-信丰段 「已建成并投产」 tension**, which is on the micro-pass list and is the same
Ganzhou-south package that P4787-vs-P4788 turns on. Worth working those together, not separately.

### P5861 — 西气东输二线新余支线(高安-新余)  (row 3325, operating)

- classes: UNRESOLVED 9, REFS_ADDED 6, CONFIRMED 2
- tiers on ref units: presumed 9, medium 4, high 1, low 1
- harvest_opened: 56   |   cross_row_leads filed: 11 -> P4649, P4777, P4778, P4793, P4794, P4928, P4944, P4946, P5859
- **__REDUNDANCY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (high, independent=True)

**Orchestrator on P5861.** The batch's one genuine duplicate, and the row is **retired into P4778**
— ruled 2026-09-10, staged by `stage_p5861_retirement.py` at merge-chain step `0e2`. The full
reasoning and the disposal of each contradicted cell sit in the BATCH-LEVEL RULING and in P4778's
block above; three points belong here.

The adjudication was **owed to this row and it discharged the debt properly.** P4778's
`__REDUNDANCY__` is explicitly marked carried-from-v2, not re-adjudicated, with "no new evidence
found this run" — so the reciprocal was outstanding, and every numbered item filed here is new
relative to both P4778's shard and `_carried_v2.json`. That is exactly how a paired-row question is
supposed to close: one side does the work, the other side's carry is honoured rather than
double-counted.

The **decisive evidence is a negative in an exhaustive inventory**, again: PipeChina's own live 2026
公平开放 gas-facility workbook enumerates every facility of 西气东输分公司 and its Jiangxi entries are
exactly five — none is a 新余支线, none is 高安-新余, and 高安 appears only as the *start point of the
Nanchang-Shanghai branch*. Mechanically checked, too (`西气东输` extracts from the workbook, `新余`
does not), which is what makes the absence citable rather than an impression. And this is the live
successor of the very NEA disclosure series GEM's own wiki cited for this row. The corroborating
detail is better still: WEP2's *actual* Xinyu and Gao'an tie-ins are 3.46 km (2014-05) and 10.19 km
(2014), from the 2018-06 provincial facility table — so a WEP2 connection to this corridor exists,
it is just three orders of magnitude shorter than a 69.21 km branch and seven years later than the
row's dates.

**A WEP2 link to the corridor does now exist, and it must not be used to rescue the row's
`FuelSource`.** The 1.52 km DN500 tie-in at 高安市大城镇 was approved **2024-12-31**, expressly to
"增加省天然气管网一期工程环鄱阳湖管网气源接入点", with Gao'an's planning notice still at 公示 in
2026-06. If Update ever wants WEP2 recorded against this corridor it is a **post-2025 supplementary
source, not the 2010 feed** — and the surviving row (P4778) carries the sourced 川气东送 `FuelSource`,
canonicalized at step `0e4`. Nothing from this row's contradicted cells is to be pasted.

### P5862 — 奉新支线(赤岗-奉新)  (row 3326, operating)

- classes: UNRESOLVED 10, CONFIRMED 5, REFS_ADDED 3, REVERIFIED 2
- tiers on ref units: inferred 10, medium 3, high 2
- harvest_opened: 25   |   cross_row_leads filed: 11 -> P4776, P4777, P4785, P4786, P4787, P4788, P4790, P4791, P5863, P5865, P5886
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (medium, independent=True)
- **__REDUNDANCY__ CONFIRMED** (medium, independent=True)
- **__VALIDITY__ CONFIRMED** (presumed, independent=False)
- **__VALIDITY__ CONFIRMED** (medium, independent=False)

**Orchestrator on P5862.** This row carries two things at once: the **batch-wide Phase I/II
operator-owner ruling**, filed here because this is the row that owed both an Owner ref and an
Operator second source, and its **own existence problem**. Take them separately.

**The batch-wide sentinel is the best-evidenced ruling in the batch and it supersedes my own
cohort sketch on P4790.** It quotes the two authoritative footnotes verbatim (CCXI 2022 fn1: Phase I
= 江西省天然气管道有限公司, 川气东送-fed, 54% group / 46% 国家管网集团东部原油储运有限公司 per SSE
242696 fn5; Phase II = 江西省天然气集团有限公司管道分公司, WEP2-fed, 100% group, no PipeChina equity)
and — critically — supplies a **usable phase test where no segment-naming source exists**: CCXI
fn2's 42-county Phase I list (Nanchang, Jiujiang, Jingdezhen, Xinyu, **Yichun**, Fuzhou, Yingtan,
Shangrao) against fn3's 40-county Phase II list (井冈山市, 莲花县, 永新县, 大余县). The binding rule it
applies is right and worth restating: **the phase is whatever the sources' own wording says, never
the sheet's label and never the `一期/二期` string inside `segment_name`** — P4791 is the
counter-example that proves it, and this row is the inverse, a label the test *confirms* (奉新县 is in
宜春市; fn3 contains no Yichun-prefecture county).

Its ruling A — normalize the 46% holder to the subsidiary 国家管网集团东部原油储运有限公司 on every
Phase I row, as a mechanical fix, not eleven research questions — **is already implemented and
verified.** `normalize_owner_entities.py` at step `0c` did exactly that: 20 rows now carry the
subsidiary in their staged values, and the only parent-form 46% string left anywhere is P5863's,
which is an `UNRESOLVED` record echoing the sheet and proposes nothing (the normalizer deliberately
skips `UNRESOLVED`). The two rows the sentinel flags as disagreeing with *themselves* between Owner
and Operator — P4787 and P5887 — agree on the entity string now; what survives on them is the
JV-vs-100%-group question, which is a phase decision, not an entity-string one.

Rulings B–E remain owed, and the sentinel's framing of them is correct: **three adjudications, not
eight cell edits** — P4787-vs-P4788 (same four-branch 赣州南 package, same Quannan PDF, contradictory
attributions; CCXI fn3's 大余 and the 2017-12 管道分公司 tender both favour P4788's 100%-group
reading), P4789's internal split, and P5863-vs-P5862. On P5863 my P4790 note leaned on geography
alone (奉新 → Yichun → Phase I, so the label is the defect); this row's sentinel is right that
**chronology cuts the other way** — a 2023 build is Phase II by construction programme regardless of
where it sits, since 管道分公司 was formed in 2016 precisely to build the Phase II remainder. Take
that as genuinely open, not as settled by the county lists. Also carry ruling D: the Phase II entity
appears under **four different parent names** across four tenders (one 2020-04 notice names two of
them in a single document), so a merge that name-matches on the tender string will mis-key rows.

**The row's own existence is `NOT ATTESTED, and partly CONTRADICTED`, and that is the most important
thing here.** 赤岗 appears as a place on this corridor in *zero* reachable documents — not the 2014
DRC plan, not SSE or CCXI, not the EPC contractor's page, not any of 25 harvest-pool URLs, and not
in a full-text title sweep of all 1,097 gas notices (1,013 unique titles, 2016-11 → 2025-02) on
Jiangxi's mandatory public-resource trading platform, which names ~39 sibling branches at segment
level. The honest caveat is stated and it is the right one — the platform's gas coverage starts
2016-11, so it cannot disprove a 2011-13 build — but **every other operating Phase I branch in this
cohort generates post-2016 notices and this one generates none.** Against that sit three affirmative
contraries: the DRC plan's own Anyi-to-Fengxin branch is 石鼻阀室-奉新, 16 km, listed in 2014 as
*still to be built* (a pipe in service since 2013-07 cannot be), and Fengxin County's own 2023 碳达峰
plan is still asking for 干洲-奉新支线 **construction** to be accelerated.

Filed as a concern rather than a deletion because the disposition is an adjudication **against
P5863**, not a unilateral call — correct, and the `__REDUNDANCY__` record frames it precisely: P5863's
own ruling tested P5862's *values* against P5863's values and found them different, which is true and
not contradicted; it did not test whether P5862's values describe anything real. If they do not, the
two rows are one corridor entered twice, and the merge should keep P5863 (a named, dated, EIA-backed
2023 project) and adjudicate P5862. The 14.70 + 18.45 = 33.15 km arithmetic is offered as a datum
rather than an argument, which is the right weight to give it — it fits both readings.

Two consequences to hold onto. **Do not "complete" this row's owner cells** off the phase mapping if
the existence question resolves against it — a correct owner on a row that should not exist is worse
than a blank, and the sentinel says so itself (ruling E). And **do not repair the route geometry**:
the v2 stray-vertex defect is re-affirmed (one vertex ~270 km off corridor, north of the Yangtze;
the other four haversine to ~23.5 km), but the routes leg must not redraw a corridor the row may not
own, and if the row is adjudicated away the three-way sync rule requires `RouteType`, `RouteAccuracy`
and the routes repo to move **together**.

The `FuelSource`-vs-phase mismatch carried from v2 is re-affirmed and strengthened, and its framing
is the one I endorse: the CCXI footnote is one document stating one fact, so **if it is good enough
to re-attribute the owner it is good enough to raise the gas source** — but then it must be applied
to all 23 phase-labelled rows, not silently to the one row that happened to owe a ref. Twelve blank
`FuelSource` cells are waiting on the same convention call (does `FuelSource` name the trunk a branch
physically taps, or the origin of the molecules?). On *this* row the question is moot until existence
resolves; for the cohort it is not moot at all. Step `0e5` is consistent with all of this: it
accepted this row's `Location [ref]` `name_found` flip on 奉新支线 (the row's own segment form, on the
Fengxin County capture) and lifted the tier `low → medium`, while refusing every parent/system-name
flip elsewhere.

### P5865 — 樟树支线  (row 3329, construction)

- classes: REVERIFIED 8, UNRESOLVED 4, CONFIRMED 2, REFS_ADDED 2
- tiers on ref units: medium 9, low 4, high 1
- harvest_opened: 24   |   cross_row_leads filed: 3 -> P4777, P4793, P4797
- **__STATUS__ CONFIRMED** (medium, independent=False)
- **__VALIDITY__ CONFIRMED** (medium, independent=False)

**Orchestrator on P5865.** A status change and a capacity conflict, and the two are independent.

**Status `construction` → `operating`** is well-founded and I would apply it. The v2 sentinel had
already reached `change` off a time-elapsed inference; this pass replaces the inference with the
primary document — the jxgajc 竣工环境保护验收 notice, published 2022-06-10, i.e. *after* the Nov 2021
construction completion, with a passing verdict on every monitored category. Per the batch's document
ladder a passed post-completion environmental acceptance is close to dispositive (the P4786
precedent), and the honesty of the note is what makes it usable: no distinct 通气 statement was found
for this branch, so the verdict rests on **construction-complete + acceptance-passed**, not on a
quoted commissioning date. Single document, so `medium`/not-independent — but the document *class* is
a regulatory filing, and no source in the 24-URL pool suggests the line was still under construction
in 2022 or later. Note this is the same jxgajc.com / 江西赣安检测技术 filing family flagged as the
batch's highest-value follow-up in the cohort ruling; it is doing real work on several rows now.

**Capacity is a 26× conflict, deliberately left `UNRESOLVED`, and that is right.** The only
segment-naming document gives 供气规模 5×10⁶ Nm³/a ≈ 0.005 bcm/y against the sheet's 0.13 — not a
rounding disagreement (rule 4(e)) but a material one, so the record neither cites the document for
0.13 (it does not support that number) nor overwrites to 0.005 off one source. Both readings the note
offers are live: 0.13 may be a whole-system or whole-Phase-I figure mis-attributed to a 20.2 km
branch — the **same aggregate-vs-segment shape** as P4789's 0.32 bcm/y, P4928's 30 bcm/y and P4934's
7,378 km, which is now the single most common defect class in this batch — or the filing's figure may
be a planning-stage throughput distinct from the branch's capacity. Update should search
specifically for a capacity-bearing document before this cell is touched.

### P5866 — 金沙湾支线(湖口-金沙湾)  (row 3330, operating)

- classes: REFS_ADDED 15, CONFIRMED 8
- tiers on ref units: high 8, medium 7
- harvest_opened: 41   |   cross_row_leads filed: 8 -> P4777, P4780, P4784, P4791, P4795, P5865, P5886
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (high, independent=True)
- **__VALIDITY__ CONFIRMED** (medium, independent=False)
- **__REDUNDANCY__ CONFIRMED** (high, independent=True)
- **__STATUS__ CONFIRMED** (high, independent=True)

**Orchestrator on P5866.** The best-worked row in the batch, and the one that pays for itself in
findings the batch reuses elsewhere. Six sentinels, all `high`/independent, and every carried v2 flag
closed from primary text rather than re-flagged.

- **The v2 "6.43× outlier" was a misdiagnosis and is now closed correctly.** Capacity is *not* an
  outlier — the 2021 环保验收 disclosure's own 设计最大供气规模 5亿Nm³/a = 0.50 bcm/y matches the sheet
  exactly. The 6.44 ratio is `LengthKnown` 19.12 km against `LengthEstimateKm` 123.15 km, i.e. a
  **defective route geometry**, not a length dispute: three segment-naming documents put the whole
  line inside Hukou County. Correctly routed to the routes leg with the corridor described (湖口分输站
  → 金砂湾工业园区 LNG plant via the 沈贵里 valve chamber) and **no coordinates fabricated**. Worth
  noting for the QC leg that a ratio alarm found a real defect in the wrong column — the alarm was
  right, its attribution was not.
- **The 金沙湾 → 金砂湾 orthography fix is the batch's most instructive one-character defect.** Every
  primary source (2021 环保验收, 2023 安全验收, 2024 省能源局核准, 2025 LNG-II report, the 2017 中标公告,
  the 2014 DRC plan) writes 砂; the sheet writes 沙. That single character is **why `url_verifier`
  reported all twelve of this row's carried refs as system-only** and why the payload owed twelve
  relevance re-reads: a correctly-named segment-level ref looked like a parent-network ref. It is
  also the reason P4790's 湖口-金砂湾-彭泽支线 find could not be keyed to this row. Recommend the fix
  (`OtherLanguageAlternativePipelineNames` only; the English transliteration is unaffected), and read
  it as a general warning — the relevance gate is one character deep on CJK place names.
- **Two figures where a decision is owed and neither is a defect.** Capacity 0.50 (设计最大供气规模,
  2021 as-built disclosure) vs 0.492 (设计输气规模, 2023 安全验收) — different Chinese terms, different
  quantities, and 0.492 does not round to 0.50; the maximum is kept, and if GEM prefers throughput
  the cell becomes 0.49. Length 19.12 (as-built) vs 19.13 (the two *later* documents) — a 10 m spread,
  within rounding, kept as recorded, and recorded only so the merge knows which figure the more recent
  statements carry.
- **The duplication guard closes cleanly and answers a Discovery question in the negative.** The
  Jinshawan→Pengze continuation is *not* missing from GEM: it is P5886, and the link is physical and
  documented — this row's 安全验收 report records the 沈贵里 valve chamber as the one new structure, and
  that chamber is exactly P5886's start point, so the continuation was re-scoped to begin there rather
  than at Jinshawan. Also cleanly separated: the 2024-approved 650 m LNG-II tie-in is a different
  spur, and the planned 金砂湾分输站 **was never built** (「因政策原因已拆除，现场恢复原貌」) — which
  matters the moment any discovery pass treats a Jinshawan distribution station as existing
  infrastructure.
- **The prefecture-granularity item is handled exactly the way the rules require**: the blank
  `StartPrefecture/District` is staged (`Hukou County`) because a blank is an owed unit, and the
  existing coarser `Jiujiang` on the End side is *not* overwritten, because which granularity these
  columns take is a house-style question rather than a factual error. Sibling P5886 uses county
  granularity for the same places, so the inconsistency is real; it is Baird's call, and it should be
  made once for the tab, not on this row.

### P5886 — 沈贵里-彭泽支线  (row 3349, proposed)

- classes: UNRESOLVED 9, REFS_ADDED 6, CONFIRMED 3
- tiers on ref units: low 10, medium 5
- harvest_opened: 24   |   cross_row_leads filed: 2 -> P4784, P5889
- **__STATUS__ CONFIRMED** (medium, independent=True)
- **__VALIDITY__ CONFIRMED** (medium, independent=True)
- **__VALIDITY__ CONFIRMED** (medium, independent=True)

**Orchestrator on P5886.** A status change I would apply, and a good example of an access-failure
chain handled correctly.

**Status `proposed` → `construction`.** Two independent legs: GEM's own `ProposalYear/Month`
(2022/10, currently unreferenced on the sheet) already post-dates the 2021-01 completion of the
upstream Hukou-Jinshawan section, which is exactly what a follow-on downstream section looks like;
and the Jiujiang municipal 14th-FYP energy plan (2023-06-09, independent of GEM and of the operator)
places 湖口-彭泽支线 as 开工建设 and still needing to be 继续完成…建设 inside the 2021-25 plan period.
A row whose construction has commenced and is a named active task in a current government plan is not
merely proposed. The `Phase I` label is independently re-derived from both sources' own wording — and
the note explicitly refuses to take it from the archive.org GEM screenshot's own 一期工程 label, which
is right on two counts: that screenshot is a **GEM surface** (standing rule 1) and RELAUNCH_NOTES
item 9 gives sheet-side phase labels no evidentiary weight.

The existence question closes affirmatively and by a **hand-confirmed chain rather than a string
match**: 沈贵里-彭泽支线 is the downstream continuation of the officially-named 湖口-金砂湾-彭泽支线,
picking up at the 沈贵里 valve chamber where the built upstream section ends. No document using the
exact string was reachable, and the note says so plainly instead of implying one was. P5866's
`__REDUNDANCY__` record reaches the identical conclusion from the other end, with the valve chamber as
the shared physical anchor — two shards, opposite directions, same answer, which is the strongest form
of confirmation available inside one batch.

The completion caveat is the model for how a blocked source should be reported. The most specific
leads (a jxgqcg.com construction tender and gas.in-en.com survey/design pages, matching this row's
length, diameter and endpoints) were beaten by a Tencent Cloud WAF CAPTCHA with an empty CDX and by a
403, after a full escalation ladder — curl UA/header/cookie/IPv4 variants, WebFetch, the r.jina.ai
reader proxy, and the Wayback CDX API with 3/8/15 s backoff. **Their content was never read and was
not used to support any value**, and they are recorded as access failures rather than as evidence
about the segment. So the row lands on `construction` and whether it has since been *completed*
(2023-26) stays genuinely open — which is the correct state, not a gap.

Its Owner/Operator is the 54/46 Phase I JV with the 46% holder staged as the **subsidiary**, which is
the ruling this batch normalized cohort-wide at step `0c` (see P5862's batch-wide sentinel). Nothing
further owed on that axis here.

### P5887 — 广丰-玉山支线  (row 3350, operating)

- classes: UNRESOLVED 7, REFS_ADDED 4, REVERIFIED 4, CONFIRMED 2
- tiers on ref units: medium 7, presumed 7, low 1
- harvest_opened: 25   |   cross_row_leads filed: 0
- **__STATUS__ CONFIRMED** (medium, independent=None)
- **__VALIDITY__ CONFIRMED** (medium, independent=False)

**Orchestrator on P5887.** Two carried v2 concerns, both re-fetched and re-read this pass rather than
taken from the carried note text — which is the distinction between a restated flag and a verified
one, and it is why both are worth keeping.

The **status tension is real and reproducible**: chndaqi.com describes an end-2021 state that sits
awkwardly against `operating`. No verdict change is proposed and that is right — `status_review_owed`
is false for this row, so no formal status leg is running, and `operating` could well be correct if
commissioning followed the document's date. The supporting lead points that way (a 2024-11
广丰支线延长线 extension project in two Shangrao EPB EIA notices would imply the original branch was
already in service) but those notices are WAF-blocked and were **not read**, so they cannot be used
to close it either. Flagged for the reviewer, correctly.

The **split-row question is correctly declined.** chndaqi.com's own text combines the two legs into a
single clause (广丰-玉山支线管道 / 广丰-玉山天然气管网支线项目), and the DRC plan's Table 5 treats
广丰-广丰门站 (10 km) and 广丰-玉山门站 (12 km) as two legs off a shared Guangfeng hub — consistent
with one row for two named projects sharing an origin. The residue is a length ambiguity worth
recording: 10 + 12 = 22 km against the sheet's 23.30 km. Not a split, not a correction; a note.

**One off-contract record to fix, and it is this row's.** Its `__STATUS__` sentinel carries 1 ref and
1 verification with `tier: medium` but `independent: None` — the only one of the batch's 44
empty-tier/null-independent records that is genuinely off-contract (the other 43 have zero refs *and*
zero verifications, so they have no tier to claim). It is invisible to gate D **in both directions**,
and `normalize_independence.py:224` skips it twice over: `if not r.get("independent") or
rc.startswith("__")` — falsy `None` is skipped, and every `__*` sentinel is skipped. The value is not
in doubt: one ref is one publisher, so `independent = False`. **Stage it and fold it into the next
rebuild** rather than triggering one for a single field. Both of this row's sentinels also carry
`[SCHEMA NORMALIZED …]` audit lines for a missing `ref_col` that was colliding as a duplicate unit,
plus a `[TIER SET …]` line — read those as the merge's own trail, not as research findings.

### P5888 — 万载—铜鼓支线  (row 3351, construction)

- classes: UNRESOLVED 14, CONFIRMED 2, REVERIFIED 1
- tiers on ref units: presumed 14, medium 1
- harvest_opened: 24   |   cross_row_leads filed: 1 -> P4792
- **__STATUS__ CONFIRMED** (presumed, independent=False)
- **__VALIDITY__ CONFIRMED** (presumed, independent=False)

**Orchestrator on P5888.** `verdict: unclear` is the correct outcome and the row is a textbook case
of the rule holding under pressure. A WebSearch-surfaced county-government article describes
construction beginning 2022-03-21 and gas reaching a new Tonggu distribution station on 2024-10-30 —
which, if verifiable, moves this row to `operating` with a completion date. It is facially plausible
and internally consistent (the dates post-date the 2014 DRC plan, which does not name this segment at
all). Every avenue to verify it was exhausted: tonggu.gov.cn now 302s to a homepage shell with no
matching content, no Wayback capture under `matchType=exact` or a domain+date-range CDX query, no
archive.today snapshot, and the second candidate (a jxic.jczh.com tender bulletin naming the branch)
is WAF-CAPTCHA-blocked on every attempt including a fresh recheck. **No status change staged and the
unverifiable content cited nowhere** — exactly right, and worth saying plainly: the content is
probably true, and that is not the test. What the merge gets instead is a precise re-review trigger —
a different network path, a Baidu/Sogou cache of the original, or a way past the WAF — which is more
useful than a hedged value.

The **P4792 cross-check is the substantive finding**, and it comes from this row's side
independently: the 2014 DRC plan's Table 5 does *not* name 万载-铜鼓 anywhere (only 宜丰-铜鼓-修水 110 km
and 宜春-万载 31.9 km), and its Table 4 places both 万载县 and 铜鼓县 in the "not yet connected,
expected near-term" bucket as of 2014. So Wanzai-Tonggu reads as a **later planning addition** and
plausibly the routing that actually connected Tonggu county — which would put P4792's never-confirmed
2014-era Yifeng-Tonggu proposal in question. Correctly *not* acted on from this evidence alone: Tonggu
could be fed from two directions and both could exist. The right unit of work is the one the note
proposes — **a human pass across P4792 / P5888 / P4784 together**, the DRC plan's three adjacent
northwest-Jiangxi routing options, once the blocked sources are reachable. Note the tier is `presumed`
/ not independent, which is the honest label for a verdict resting on a document nobody could open.

### P5889 — 蔡岭-都昌支线  (row 3352, operating)

- classes: REFS_ADDED 9, UNRESOLVED 6, CONFIRMED 1
- tiers on ref units: medium 10, inferred 4, low 1
- harvest_opened: 34   |   cross_row_leads filed: 0
- **__VALIDITY__ CONFIRMED** (medium, independent=True)

**Orchestrator on P5889.** One flag, cleanly reasoned, and the arithmetic is what makes it a real
finding rather than a quibble. Two independent segment-naming planning-stage sources agree closely
with **each other** (jxganan.com 2017-12-18: ~34.4 km; the DRC plan's Table 5: a round 34 km) and
disagree with the sheet's 31.32 km by ~3 km — about 9-10%, well outside rule 4(e)'s own
rounding example (51.97 + 0.5 vs 52). Two sources agreeing with each other and not with the sheet is
a different situation from two sources disagreeing, and the record treats it that way.

The `Length [ref]` unit is left **`UNRESOLVED` rather than citing a discrepant source as if it
confirmed 31.32** — the P4779 precedent, and the correct reading of rule 4(e): a ref that states a
different number is not a ref for the recorded value, and `UNRESOLVED` here means no document states
31.32, not that nothing was found. The offered explanation — pre-construction estimate vs as-built
precision — is plausible and is labelled speculation, since no completion document was found. That
labelling is the right discipline; the alternative (asserting an as-built reading to make the cell
look sourced) is precisely the failure rule 4(e) exists to prevent.

Verdict left open for human review: is 31.32 km an as-built figure superseding two pre-construction
estimates, or does the sheet need moving toward ~34 km? An as-built document would settle it, and
this row's own jxganan.com / 江西赣安 family is where one would live — the same 竣工/安全验收 filing
family that the cohort ruling names as the batch's highest-value follow-up.
