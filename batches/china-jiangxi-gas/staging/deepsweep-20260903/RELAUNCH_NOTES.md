# Relaunch addendum — 2026-09-09 (read AFTER BRIEF.md, before your payload)

The 2026-09-04 fan-out stopped after 13 of 44 rows. You are one of the 31 relaunched rows.
Everything in BRIEF.md still binds. What the 13 finished shards learned, so you do not re-learn it:

1. **Cross-row leads addressed to your row are in `leads_by_target.json`** (key = your PID).
   Open every one; each is a document another agent read that states something about YOUR row.
   Verify the URL yourself with `--name` before staging — a lead is a pointer, not a verification.
   Read `shards/P4789.json` and `shards/P4788.json` for the shape of a passing shard.
2. **Phase I vs Phase II operator/owner (whole grid).** CCXI 2022 credit report: the SSE-prospectus
   54% 江西省天然气集团 / 46% 国家管网集团东部原油储运有限公司 JV is the PHASE I network company
   (江西省天然气管道有限公司); PHASE II segments sit with 江西省天然气集团 (管道分公司) at 100%.
   Decide which phase YOUR segment belongs to from a naming source (DRC plan tables, approvals),
   stage Owner/Operator accordingly on the operators_owners tab, and say the phase in notes. Do not
   copy the 54/46 split onto a Phase II row. The 46% holder is the PipeChina SUBSIDIARY
   东部原油储运有限公司, not the parent.
3. **Aggregates already known to be system/multi-branch figures — never stage them on a segment:**
   2,172,600,000 CNY (four Ganzhou-south branches total); china5e 3-branch figures on the Yifeng/
   Tonggu/Xiushui cluster; 110 km for 宜丰-铜鼓-修水 as one project; 44.7e9 / 436.48亿 RMB (WEP3
   system); 30 bcm/y (WEP3 system, not a section); 626.76亿 (川气东送 incl. Puguang field).
4. **FuelSource on the grid:** WEP2 is the confirmed feed for the Ganzhou-south branches; v2's WEP3
   claim is weaker — do not carry it forward without a segment-naming source.
5. **2009 vs 2010 start cluster on Phase I trunks (P4779/P4780):** segment-naming sources say
   completed 2009; sheet says 2010. Treat as ONE cluster — file `__VALIDITY__` with the evidence,
   do not silently change.
6. **Access notes since the brief:** `www.quannan.gov.cn` needs IPv4 (`curl -4`); P4787's soft-404
   quannan 2021 page has a live replacement under `/qnxxxgk/zdsjbg/202201/`; jdzmc.com and
   chinanews.com.cn no longer false-flag as blocked (verifier fixed 09-04). WebFetch has
   HALLUCINATED quotes from sina/sohu pages in this batch — quote only text you saw in a fetched
   body (`curl` + read), never a summary.
7. **Possible missing rows / discovery guards:** 上犹-崇义段 (43 km DN250) flagged by P4787 as a
   possible missing row — match against OtherEnglishNames before calling it new. WEP3's
   株洲-郴州支干线 / 邓州支线 / 新野支线 were cancelled by the regulator, not missing rows.
8. Trunk parents P4934 / P4947 (and P4657, done): system-level name IS the row name; a section's
   figure never sources the mainline cell and vice versa.

Write `shards/<PID>.json` even if partly unresolved. Do not edit any other shard, the payloads,
or anything outside `shards/`. Never write the live sheet; never cite GEM.

## 9. 2026-09-09 relaunch (read this if your row was dispatched after 08:45 EDT)

- At 08:33 EDT every running agent (20 rows) was killed by an account spend limit before writing a shard. Only `shards/P4649.json` and `shards/P4777.json` landed from that wave. If you are a relaunched row: **start fresh** — there is no partial work to find, and nothing outside `shards/` was written for you.
- Two new finished shards worth reading: `shards/P4777.json` (the Phase I network PARENT — 57 documents opened, 6 cross_row_leads; its evidence is the best index of Phase I documents) and `shards/P4649.json` (川气东送 江西支线 — 30 documents, 15 leads). Their `cross_row_leads` are NOT yet folded into `leads_by_target.json` — scan them yourself for your row.
- Findings the killed agents reported but lost (re-find and cite; do not cite from this note):
  - P4791: the 江西省天然气集团 bond prospectus on sse.com.cn (text around line 613) names the 46% holder of the Phase I JV as 国家管网集团东部原油储运有限公司; CCXI 2022 states Phase I covers Jingdezhen prefecture while Phase II does not — CORRECTED 09-09 by the finished P4791 shard: CCXI's own prefecture footnotes put BOTH Jingdezhen (乐平) and Shangrao (德兴/婺源) under Phase I, and three segment-naming sources (jxnews 2020-12, jxganan 2024-04-28 安全验收, yingdodo 2018) call 乐平-德兴-婺源 a **一期** project run by the Phase I JV 江西省天然气管道有限公司. GEM's "Phase II" label on P4791 is wrong. Any row labelled Phase II must be checked against the sources' own phase wording, not the sheet's label — the Phase I/II operator rule (item 2) follows the SOURCES' phase, never the segment_name.
  - P5866: a safety-acceptance (安全验收) report exists for the 金沙湾支线 segment.
  - P5863: a definitive segment-naming source was found for that row.
  - P4944: a Zhejiang NEA (国家能源局浙江监管办公室) document names the branch.
  - P5886: a Jiujiang-specific document naming the row was the key find.
