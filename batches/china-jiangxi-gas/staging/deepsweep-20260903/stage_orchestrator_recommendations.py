#!/usr/bin/env python3
"""Put the orchestrator's definite rulings in the column a reviewer actually scans.

`harvest_sentinel_findings.py` used to stamp ONE boilerplate line as the
`recommendation` on all 99 sentinel findings -- "Agent research verdict -- see
researcher_notes. Cross-check against the cluster-level recommendation in
staging/redundancy/ ..." -- overwriting anything the shard had put there. That is the
right default for an agent's own read-and-flag verdict, and it stays the default. But
it is wrong twice over for a record the orchestrator has RULED on: the Recommendation
column is where a reviewer looks for the action, and these notes run 1,000-4,000
characters, so "see researcher_notes" hides the one sentence that says what to do.

The harvester now honours a per-record `recommendation` (`r.get("recommendation") or
<boilerplate>`), which also stopped it discarding the two recommendations the row
agents themselves had written (P4931, P4944's StartYear1 concern) -- a defect that
turns out to be confined to this batch: 341 sentinel records across every staging dir
in the repo, 6 carrying a recommendation, all 6 here. No committed run moves.

This step fills in the rulings that are DEFINITE -- one action, stated, with the
evidence behind it. Everything else keeps the boilerplate deliberately, because
"flagged for human review" is the honest recommendation for a genuinely open
question (P5866's 0.50-vs-0.492, P5862's existence, P4928's two candidate value
changes, the FuelSource convention, the phase adjudications). An orchestrator
recommendation is not a licence to convert open questions into instructions.

Records are matched on (PID, a marker substring of the note) rather than on list
position -- the order within a shard is not a contract, and split_shards renumbers.

Runs at merge-chain step 0e8 -- BEFORE split_shards.py, and it must precede step 4
(the harvester), which is what reads the field. Idempotent.
"""
import argparse, json
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (pid, marker in researcher_notes) -> recommendation
RULINGS = [
    ("P4778", "ORCHESTRATOR RULING: RETIRE P5861 INTO P4778", (
        "RETIRE P5861 (row 3325, 'West-East Gas Pipeline 2 / XinYu Branch(Gao'an-Xinyu)'). "
        "Adjudicated 2026-09-10: it is the same pipe as P4778, not a WEP2 branch. Decisive "
        "evidence is a negative in an exhaustive inventory -- PipeChina's live 2026 公平开放 "
        "workbook enumerates every 西气东输分公司 facility and its five Jiangxi entries contain "
        "no 新余支线, no 高安-新余 and no 69.21 km (checked mechanically: 西气东输 extracts from "
        "the file, 新余 does not; 高安 appears only as the start of the Nanchang-Shanghai "
        "branch). WEP2's actual Xinyu/Gao'an tie-ins are 3.46 km (2014-05) and 10.19 km, "
        "three orders of magnitude short of a 69.21 km branch. DO NOT paste P5861's "
        "contradicted cells onto P4778: the surviving row keeps its sourced 川气东送 "
        "FuelSource, and the 2024-12-31 WEP2 tie-in approval at 高安市大城镇 is a post-2025 "
        "supplementary source, not the 2010 feed. The three companion flags on this row "
        "(legacy 69.21 km length, the retired row's name, the StartMonth1=12 cross-phase "
        "paste) are filed separately and deliberately NOT staged. Orchestrator ruling."
    )),
    ("P5861", "VERDICT: DUPLICATE", (
        "RETIRE THIS ROW into P4778 -- the reciprocal of the ruling filed on P4778, "
        "adjudicated 2026-09-10. P4778's own __REDUNDANCY__ was explicitly carried from v2 "
        "and not re-adjudicated ('no new evidence found this run'), so the debt was "
        "outstanding on this side; every numbered item here is new relative to both that "
        "shard and _carried_v2.json. Act on the P4778 record, which carries the full "
        "disposal of each contradicted cell. Nothing from this row's values is to be "
        "pasted forward. Orchestrator ruling."
    )),
    ("P5866", "NAME ORTHOGRAPHY DEFECT", (
        "CHANGE OtherLanguageAlternativePipelineNames: 金沙湾 -> 金砂湾 (one character, 沙 -> 砂). "
        "All six primary sources spell it 砂 (2021 环保验收, 2023 安全验收, 2024 省能源局核准, 2025 "
        "LNG-II report, the 2017 中标公告, the 2014 DRC plan). This defect has a measured cost, "
        "which is why it is a recommendation and not just a note: the wrong character is why "
        "url_verifier read ALL TWELVE of this row's carried refs as system-only name matches, "
        "and why the 湖口-金砂湾-彭泽支线 lead surfaced on P4790 could not be keyed back to this "
        "row. The English transliteration is unaffected and needs no change. Orchestrator "
        "ruling; the relevance gate is one character deep on CJK place names, so this is "
        "worth a note in docs/country_notes/china.md too."
    )),
    ("P5862", "BATCH-WIDE SENTINEL", (
        "READ THIS FIRST -- it governs 23 rows, not one. Ruling A (normalize the 46% Phase I "
        "holder to the SUBSIDIARY 国家管网集团东部原油储运有限公司, never the parent 国家石油天然气管网集团有限公司) "
        "IS ALREADY APPLIED: merge-chain step 0c normalized 20 rows, and the only parent-form "
        "string left is P5863's, which sits on an UNRESOLVED record that merely echoes the "
        "sheet and proposes nothing. Rulings B-E are OWED and are three adjudications, not "
        "eight cell edits: (B/C) apply the phase test row-by-row BEFORE staging any "
        "owner/operator -- phase comes from the sources' own wording, never the sheet label "
        "and never the 一期/二期 string in segment_name (CCXI fn2 lists 42 Phase I counties, fn3 "
        "40 Phase II) -- then take P4787-vs-P4788 (same Quannan PDF, contradictory "
        "attributions; CCXI fn3's 大余 and the 2017-12 管道分公司 tender both favour P4788's "
        "100%-group reading), P4789's internal Owner/Operator split, and P5863-vs-P5862, "
        "where geography reads Phase I but chronology reads Phase II (a 2023 build, and "
        "管道分公司 was formed in 2016 to build the Phase II remainder) -- genuinely open. "
        "(D) The Phase II entity appears under FOUR different parent names across four "
        "tenders, two of them in one 2020-04 document, so a name-match on a tender string "
        "will mis-key rows. (E) Do not 'complete' P5862's owner cells while its existence is "
        "unresolved. Orchestrator ruling."
    )),
]


def main(apply=False, subdir="shards"):
    changed = 0
    for pid, marker, rec in RULINGS:
        path = HERE / subdir / f"{pid}.json"
        if not path.exists():
            print(f"  {subdir}/{pid}.json: absent, skipped")
            continue
        d = json.loads(path.read_text())
        hits = 0
        for i, r in enumerate(d.get("resolutions") or []):
            rc = (r.get("ref_col") or r.get("sentinel") or "").strip()
            if not rc.startswith("__"):
                continue
            if marker not in (r.get("researcher_notes") or ""):
                continue
            hits += 1
            if (r.get("recommendation") or "").strip() == rec:
                print(f"  {subdir}/{pid} #{i} {rc}: already set, skipped")
                continue
            r["recommendation"] = rec
            changed += 1
            print(f"  {subdir}/{pid} #{i} {rc}: recommendation set ({len(rec)} chars)")
            if apply:
                path.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                                encoding="utf-8")
        if hits == 0:
            # Loud, not silent: a marker that stops matching means a note was rewritten
            # and the ruling is no longer attached to anything.
            print(f"  {subdir}/{pid}: MARKER NOT FOUND {marker!r} -- ruling not attached")
        elif hits > 1:
            print(f"  {subdir}/{pid}: marker matched {hits} records -- check it is specific")
    if changed and not apply:
        print("  DRY RUN -- pass --apply to write")
    return changed


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dir", default="shards")
    a = ap.parse_args()
    n = main(apply=a.apply, subdir=a.dir)
    print(f"{n} recommendation(s) {'set' if a.apply else 'to set'}")
