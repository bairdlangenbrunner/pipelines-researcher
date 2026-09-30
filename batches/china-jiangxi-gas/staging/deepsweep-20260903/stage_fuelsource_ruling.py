#!/usr/bin/env python3
"""Ganzhou South Branch (赣州南支线) FuelSource ruling -- P4785 / P4786 / P4787 / P4788.

THE RULING (orchestrator, 2026-09-10). The four rows are four segments of ONE branch,
and the branch has TWO gas sources, one at each end. FuelSource on all four becomes

    West-East Gas Pipeline 2, West-East Gas Pipeline 3

and the 川气东送 (Sichuan-Shanghai) half of the sheet's existing P4787/P4788 value is
DROPPED.

WHY THIS SCRIPT EXISTS. The batch shipped four different answers for one branch:
P4785 'West-East Gas Pipeline II' (high), P4786 and P4788
'West-East Gas Pipeline III/West-East Gas Pipeline II' (high), and P4787 nothing at all
on the paste surface -- its only record is in ref_shards_recovery/, headed
'CONTRADICTION -- DO NOT TREAT AS CONFIRMATORY', whose single ref verified
`contains_value: false` (it was checked against the OLD sheet value, which it indeed does
not state), so merge_qc strips the ref and the unit delivers UNRESOLVED with no refs --
leaving the live cell's 'Sichuan-Shanghai gas pipeline/West-East gas pipeline II'
uncited, which is exactly the rule-4(e) defect. P4787's __VALIDITY__ item (4) asked for
this ruling in as many words ('Needs an orchestrator ruling').

THE EVIDENCE, re-read in full today rather than taken from the shard notes.

(1) THE OPERATOR'S OWN 2024 EMERGENCY PLAN -- 江西省天然气集团有限公司管道分公司,
《江西省天然气管网工程赣州南（信丰-瑞金段）、（龙南-全南段）等4条支线突发环境事件应急预案》
(JXTRQ/AF/B0-2023, disclosed by 全南县 2024-11, 321 pp). Verbatim:
    「江西省天然气管网工程赣州南（信丰-瑞金段）等 4 条支线线路分别为 赣州南支线信丰-瑞金段、
     赣州南支线龙南-全南段、赣州南支线会昌-寻乌段、上犹-崇义段，全长 537.5km。
     本项目赣州南支线从西二线 149#阀室或西三线瑞金分输清管站引出气源；
     上犹-崇义支线从西二线上犹分输站引出气源，经上犹支线到达崇义门站。」
    This is the operator, naming this row's own segment, stating the branch's gas sources
    exhaustively: WEP2 (the Dayu 149# valve chamber) and WEP3 (the Ruijin pigging/
    distribution station). **川气东送 does not occur once in the 321 pages** (mechanically
    checked over the extracted text). The 上犹-崇义 line is a separate spur off WEP2 at
    上犹 -- it is item (5)'s missing GEM row, not one of these four.

(2) THE 2021 PROVINCIAL ANNOUNCEMENT -- 江西日报/江西发布, 2021-04-05, republished on
tt.jxnews.com.cn/news/1266077 and m.thepaper.cn/baijiahao_12058235 (ONE origin; see the
new ORIGIN_GROUPS entry in normalize_independence.py -- no record cites both):
    「省天然气管网瑞金分输站…承接西气东输三线来气…另一路作为省网赣州南支线供气气源分输点，
     依次向会昌、寻乌、安远、定南、龙南、全南、信丰、大余等8个县（市）供气。未来省天然气集团
     管道分公司在完成与大余县西气东输二线149#阀室开口对接后，可实现…双气源双向供气」
    Eight counties in sequence off the Ruijin WEP3 station -- including every endpoint of
    all four rows -- with the Dayu WEP2 tie-in named as the then-future SECOND source and
    the stated end state 双气源双向供气 (dual source, bidirectional). So the branch is one
    hydraulic object fed from both ends; the sources are a property of the branch, not of
    the segment.
    川气东送 DOES appear on this page, and it is a false positive at row level: once for
    Nanchang's 2010 city-gas conversion and once in the province-wide sentence
    「目前，江西省的天然气供应以『川气东送』和『西气东输二线』为主」. Neither is about the
    Ganzhou South Branch. This is rule 4(a) working as intended -- a substring hit is not a
    ref, so the flag is recorded per-trunk with the quoted context, not as a bare boolean.

(3) THE COUNTY'S OWN 2024 REPLY -- 全南县住房和城乡建设局, 关于县十九届人大四次会议第202430号
建议的答复, 2024-05-16 (index B00400-2024-6458664):
    「2022 年底，我县正式启用长输管网天然气（西气东输二线），彻底告别了 LNG 燃气时代」
    Quannan's realized first pipeline gas, end-2022, is WEP2. A third publisher, and the
    one that settles which end actually flowed first at the western segments: the gas that
    reached 全南 came up from Dayu/WEP2, not down from Ruijin. It names the county
    (this row's EndLocation), not the segment, so it is corroboration for the TRUNK
    IDENTITY and is recorded with name_level 'terminus'.

(4) P4785's own two segment-level refs stay: the 2024 ccpc360 construction-bid notice
bounds its scope 「149#阀室—大余分输清管站-大余阀室、大余分输清管站-信丰分输站」, and the
2021 chinasei/赣州日报 article names the 西气东输二线大余149号阀室开口供气 work. Note the
operator plan's four branches do NOT include 大余-信丰段 -- P4785 was a separate, earlier
project -- yet the plan's own sourcing sentence runs the branch's gas through the 149#
valve chamber at Dayu, i.e. through P4785. Consistent, not contradictory.

WHY BOTH TRUNKS ON ALL FOUR ROWS, AND WHY NOT PER-SEGMENT PRIMACY. There is a real
realized-vs-designed distinction here -- WEP3-via-Ruijin was the sole source in 2021 and
the eastern counties (会昌、寻乌) took it first, while 全南 took WEP2 at end-2022 -- but
FuelSource records what feeds the pipe, and the operator's plan states both for the
project that names three of these four segments. Splitting the value by segment would
publish an inference about which molecule arrives where, on a branch whose own operator
describes it with 「或」 and whose design end state is bidirectional dual supply. The
per-end nuance belongs in the note, which is where it goes.

ORDER IS NUMERIC CONVENTION, NOT A PRIMACY CLAIM -- and it is the live sheet's own: the
sibling P4789 (井冈山支线) already carries
'West-East Gas Pipeline 2, West-East Gas Pipeline 3, Sichuan-Shanghai Gas Pipeline'.
Arabic numerals, title case, comma-space joins. That also retires the batch's roman-
numeral 'II'/'III' spellings on these four rows (the batch-wide orthography normalizer
handles the other nine variants; it no-ops here because these are already canonical).

WHY DROPPING 川气东送 IS SAFE. Three converging things, not one: the operator's 321-page
plan for these exact segments never mentions it; the 2021 announcement mentions it only at
province and Nanchang level; and CCXI's 2022 credit report separates the systems by
operator -- 天然气管道公司 runs the 承接川气东送气源 PHASE I network while 管道分公司
承接西气东输二线气源 runs Phase II, and all four of these rows are Phase II. A value that
no document ties to this branch, on a branch whose operator enumerates its sources
exhaustively, is a mis-attribution and not a second reading.

AN ACCESS GOTCHA WORTH KEEPING. www.quannan.gov.cn returns HTTP 403 over IPv6 and 200
over IPv4 -- so url_verifier (which does not pin an address family) now 403s on the
operator plan that it verified earlier in this sweep, and on the county reply. Per the
standing rule that is NOT a deletion: both refs stay, and both were read today via
`curl --ipv4` plus pdftotext, which is what the verification notes below record. If more
quannan.gov.cn refs are added, expect the same and re-check over IPv4 before believing a
403. (Filed as a candidate url_verifier improvement -- retry once over IPv4 on 403 --
deliberately NOT made here, mid-batch, in a shared script.)

Idempotent: every edit is keyed on MARKER. Runs with the normalizers, BEFORE
split_shards.py -- it rewrites shards/ AND ref_shards_recovery/ (see the note in main()
about which store wins at merge).

    python3 stage_fuelsource_ruling.py [--apply]
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = "GANZHOU-SOUTH-FUELSOURCE-RULING-2026-09-10"

VALUE = "West-East Gas Pipeline 2, West-East Gas Pipeline 3"

QN = ("https://www.quannan.gov.cn/qnxxxgk/wrfz/202411/b3adaed1adfe445db29769eaf2f7002b/"
      "files/faad1fb7c1214b8a8394299531ab10a8.pdf")
RDJY = "https://www.quannan.gov.cn/qnxxxgk/rdjy/202407/28daed350798421aa24c9746cab3bb2f.shtml"
JX = "https://tt.jxnews.com.cn/news/1266077"
TP = "https://m.thepaper.cn/baijiahao_12058235"
CCPC = "https://web.archive.org/web/20260514205837/https://www.ccpc360.com/bggg59218375210.html"
CSEI = "http://www.chinasei.com.cn/lsdt/jnjs/202107/t20210707_39693.html"

# One verification per (url, row-identity). Written from today's re-read, not copied from
# the shard notes. `contains_value` is judged against THE NEW VALUE and is per-trunk-
# explicit in the note -- the recovery record's `false` was correct against the OLD value
# and is not being overruled, it is being re-asked of a different question.
def v_qn(name_matched, level="segment"):
    return {"url": QN, "ok": True, "status": 200, "contains_value": True,
            "name_found": True, "name_matched": name_matched, "name_level": level,
            "note": "江西省天然气集团有限公司管道分公司 emergency plan (JXTRQ/AF/B0-2023, 321 pp, "
                    "disclosed by 全南县 2024-11): 「本项目赣州南支线从西二线 149#阀室或西三线瑞金"
                    "分输清管站引出气源」 -- the operator states BOTH trunks as this branch's gas "
                    "sources, in the document that names 赣州南支线信丰-瑞金段、龙南-全南段、"
                    "会昌-寻乌段 as its scope. 川气东送 occurs ZERO times in the 321 pages. "
                    "ACCESS: www.quannan.gov.cn 403s over IPv6 and serves 200 over IPv4, so "
                    "url_verifier now reports 403 on a ref it verified earlier in this sweep; "
                    "read today via `curl --ipv4` + pdftotext (11,461,354 bytes, 321 pages). "
                    "Not a deletion -- the ref stays."}

def v_wire(url, name_matched):
    return {"url": url, "ok": True, "status": 200, "contains_value": True,
            "name_found": True, "name_matched": name_matched, "name_level": "segment",
            "note": "江西日报/江西发布, 2021-04-05: 「省天然气管网瑞金分输站…承接西气东输三线来气…"
                    "另一路作为省网赣州南支线供气气源分输点，依次向会昌、寻乌、安远、定南、龙南、"
                    "全南、信丰、大余等8个县（市）供气。未来…在完成与大余县西气东输二线149#阀室"
                    "开口对接后，可实现…双气源双向供气」 -- states BOTH trunks: WEP3 as the source "
                    "at commissioning and the WEP2 Dayu 149# tie-in as the second, then-future "
                    "one, with the design end state dual-source bidirectional. CAUTION for "
                    "anyone re-verifying: 川气东送 IS a substring hit on this page, twice, and "
                    "both are false positives at row level -- Nanchang's 2010 city-gas "
                    "conversion and the province-wide sentence 「江西省的天然气供应以川气东送和"
                    "西气东输二线为主」. Neither is about the Ganzhou South Branch."}

V_RDJY = {"url": RDJY, "ok": True, "status": 200, "contains_value": True,
          "name_found": True, "name_matched": "全南", "name_level": "terminus",
          "note": "全南县住房和城乡建设局, 关于县十九届人大四次会议第202430号建议的答复, 2024-05-16 "
                  "(索引号 B00400-2024-6458664): 「2022 年底，我县正式启用长输管网天然气（西气东输"
                  "二线），彻底告别了 LNG 燃气时代」 -- the county's own bureau names WEP2 as the "
                  "long-distance pipeline gas it actually started using at end-2022. Names the "
                  "county (this row's EndLocation), NOT the segment, so it corroborates the "
                  "TRUNK IDENTITY rather than standing alone as a segment-level ref -- but it "
                  "is what settles which end of the branch flowed first in the west. ACCESS: "
                  "403 over IPv6, 200 over IPv4 (same host quirk as the operator plan); read "
                  "today via `curl --ipv4`."}


def note(row_specific: str) -> str:
    return (f"[{MARKER}] ORCHESTRATOR RULING -- ONE BRANCH, TWO SOURCES. The four Ganzhou "
            "South Branch rows (P4785 大余-信丰段, P4786 会昌-寻乌段, P4787 龙南-全南段, "
            "P4788 信丰-瑞金段) are segments of one hydraulically connected branch fed at both "
            f"ends, so FuelSource on all four is '{VALUE}' and the 川气东送 half of the sheet's "
            "P4787/P4788 value is dropped. Sourcing: the operator's own 2024 emergency plan "
            "states the branch's sources exhaustively as 西二线149#阀室 (Dayu) 或 西三线瑞金分输"
            "清管站, in the document that names three of these four segments, and 川气东送 does "
            "not occur once in its 321 pages; the 2021 江西日报/江西发布 announcement names all "
            "eight supplied counties off the Ruijin WEP3 station with the Dayu WEP2 tie-in as "
            "the second, then-future source and 双气源双向供气 as the end state; and 全南县's own "
            "2024 reply records WEP2 as the gas the county actually started taking at end-2022. "
            "CCXI 2022 assigns 川气东送 to the PHASE I provincial network (天然气管道公司) while "
            "these are Phase II rows (管道分公司, 承接西气东输二线气源). The order is NUMERIC "
            "convention and the live sheet's own -- sibling P4789 already reads 'West-East Gas "
            "Pipeline 2, West-East Gas Pipeline 3, Sichuan-Shanghai Gas Pipeline' -- not a "
            "primacy claim: realized-vs-designed differs by end (会昌/寻乌 took WEP3 from 2021, "
            "全南 took WEP2 from end-2022) and splitting the value per segment would publish an "
            "inference the operator's own 「或」 does not support. " + row_specific)


ROW_NOTES = {
 "P4785": ("THIS ROW: the two segment-level refs already here are kept and still carry the "
           "WEP2 half -- the 2024 ccpc360 bid notice bounds this segment's construction at "
           "the 149# valve chamber and the 2021 chinasei/赣州日报 article names the 大余149号"
           "阀室开口供气 work. Added: the operator plan (both trunks, branch level) and the "
           "2021 announcement, which names 大余 itself among the eight counties fed from "
           "Ruijin. That RESOLVES the 'complication' this record's prior note logged and "
           "left open -- the WEP3-via-Ruijin reading and the WEP2-at-Dayu reading are not "
           "rivals, they are the two ends of one dual-sourced branch. Note the operator "
           "plan's four branches do NOT include 大余-信丰段 (a separate, earlier project), "
           "yet its sourcing sentence runs the branch's gas through this segment's own "
           "149# valve chamber."),
 "P4786": ("THIS ROW: refs unchanged -- both already name this segment (the operator plan's "
           "scope list, and the 2021 announcement's 会昌、寻乌 by name). Only the value's "
           "spelling changes, from 'West-East Gas Pipeline III/West-East Gas Pipeline II' to "
           "the canonical arabic comma form. This is the EASTERN end of the branch: WEP3 via "
           "Ruijin is the source it took first, in 2021."),
 "P4787": ("THIS ROW: A NEW RECORD. This unit had no shard record at all -- only the "
           "ref_shards_recovery entry headed 'CONTRADICTION -- DO NOT TREAT AS CONFIRMATORY', "
           "whose single thepaper ref verified contains_value:false because it was checked "
           "against the OLD sheet value ('Sichuan-Shanghai gas pipeline/West-East gas pipeline "
           "II'), which that page indeed does not state. merge_qc therefore stripped the ref "
           "and the unit delivered UNRESOLVED with none, leaving the live value uncited on the "
           "paste surface -- the rule-4(e) defect. THAT FRAMING IS SUPERSEDED, not overruled: "
           "the recovery record's reading of its own source was right, and its recommendation "
           "('recommend checking whether Sichuan-Shanghai … should read West-East gas pipeline "
           "III instead') is what this ruling acts on. Against the NEW value the same page "
           "does state the trunks, so contains_value is true -- a different question, re-asked, "
           "not a hand-flipped flag. Also supersedes __VALIDITY__ item (4)'s interim "
           "recommendation that 'the sheet's existing Sichuan-Shanghai gas pipeline/West-East "
           "gas pipeline II is the better-supported reading': item (4) was right that the WEP3 "
           "evidence then in hand came from articles about the sibling 信丰-瑞金段, and right to "
           "escalate rather than apply v2's proposal blindly -- but the operator plan names "
           "龙南-全南段 itself and gives BOTH trunks, and 川气东送 appears nowhere in it, so no "
           "part of the sheet's value survives except the WEP2 half. Three publishers here: "
           "operator plan (segment), 2021 announcement (names 龙南、全南), 全南县 housing bureau "
           "(names the county, records WEP2 as what actually arrived end-2022)."),
 "P4788": ("THIS ROW: refs unchanged -- the operator plan names 信丰-瑞金段 and its own WEP3 "
           "Ruijin terminus, the 2021 announcement names 赣州南支线 and both trunks. The value "
           "loses nothing but the roman numerals. This is the segment that TERMINATES at the "
           "WEP3 Ruijin station, so it is the least ambiguous of the four."),
}

PLAN = {
 "P4785": ([CCPC, CSEI, QN, JX], [v_qn("赣州南支线", "branch"), v_wire(JX, "大余")]),
 "P4786": ([QN, JX], []),
 "P4787": ([QN, TP, RDJY], [v_qn("龙南-全南段"), v_wire(TP, "龙南 / 全南"), V_RDJY]),
 "P4788": ([QN, JX], []),
}
SHEET_ROW = {"P4785": 2674, "P4786": 2675, "P4787": 2676, "P4788": 2677}
SEGMENT = {"P4785": "Phase II, Ganzhou South Branch (Dayu-Xinfeng Segment)",
           "P4786": "Phase II, Ganzhou South Branch (Huichang-Xunwu Segment)",
           "P4787": "Phase II, Ganzhou South Branch (Longnan-Quannan Segment)",
           "P4788": "Phase II, Ganzhou South Branch (Xinfeng-Ruijin Segment)"}
COL = "FuelSource [ref]"


def record(pid):
    refs, new_verifs = PLAN[pid]
    return {"project_id": pid, "sheet_row": SHEET_ROW[pid], "ref_col": COL,
            "value_cols": ["FuelSource"], "kind": "FILL", "value_col": "FuelSource",
            "proposed_value": VALUE, "values": {"FuelSource": VALUE},
            "proposed_refs": list(refs), "verifications": list(new_verifs),
            "class_out": "REFS_ADDED", "tier": "high", "independent": True,
            "source_language": "zh", "researcher_notes": note(ROW_NOTES[pid])}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    touched, changes = {}, []
    for pid in ("P4785", "P4786", "P4787", "P4788"):
        p = HERE / "shards" / f"{pid}.json"
        d = json.loads(p.read_text())
        recs = d["resolutions"]
        hits = [r for r in recs if r.get("ref_col") == COL]
        if len(hits) > 1:
            sys.exit(f"{pid}: expected 0 or 1 {COL} record, found {len(hits)}")
        new = record(pid)
        if hits:
            r = hits[0]
            if MARKER in (r.get("researcher_notes") or ""):
                print(f"  {pid}: already applied -- skipped")
                continue
            old_val = (r.get("values") or {}).get("FuelSource", "")
            # keep every verification already on the record whose url survives, and add
            # today's; a ref with no verification of its own is stripped by merge_qc.
            keep = [v for v in (r.get("verifications") or [])
                    if v.get("url") in new["proposed_refs"]
                    and v.get("url") not in {x["url"] for x in new["verifications"]}]
            r["verifications"] = keep + new["verifications"]
            for k in ("values", "value_cols", "kind", "value_col", "proposed_value",
                      "proposed_refs", "class_out", "tier", "independent"):
                r[k] = new[k]
            r["researcher_notes"] = new["researcher_notes"] + " --- SUPERSEDED PRIOR NOTE: " + (
                r.get("researcher_notes") or "")
            changes.append(f"  {pid} {COL}: {old_val!r} -> {VALUE!r}, "
                           f"{len(r['proposed_refs'])} refs, high/independent")
        else:
            recs.append(new)
            changes.append(f"  {pid} {COL}: NO RECORD -> new REFS_ADDED/FILL {VALUE!r}, "
                           f"{len(new['proposed_refs'])} refs, high/independent")
        # P4787's __VALIDITY__ item (4) asked for this ruling; answer it in place so a
        # reader of the sentinel is not left with the superseded interim recommendation.
        if pid == "P4787":
            for r in recs:
                if r.get("ref_col") == "__VALIDITY__" and "FUELSOURCE" in (
                        r.get("researcher_notes") or "") and MARKER not in (
                        r.get("researcher_notes") or ""):
                    r["researcher_notes"] = (r["researcher_notes"] or "") + (
                        f"  [{MARKER}] ITEM (4) IS NOW RULED ON, and the interim "
                        "recommendation in it is SUPERSEDED: FuelSource on this row and its "
                        f"three siblings becomes '{VALUE}'. Item (4) was right to escalate "
                        "rather than apply v2's WEP3 proposal blindly, and right that the WEP3 "
                        "evidence then in hand described the sibling 信丰-瑞金段 -- but the "
                        "operator's own plan names 龙南-全南段 and gives BOTH trunks as the "
                        "branch's sources, 川气东送 appears nowhere in its 321 pages, and 全南县's "
                        "2024 reply names 西气东输二线 as the gas the county actually took at "
                        "end-2022. So the sheet's 'Sichuan-Shanghai gas pipeline/' half goes and "
                        "the WEP2 half stays, joined by WEP3. See the FuelSource [ref] record on "
                        "this row for the full ruling. Items (1)(2)(3)(5) are untouched.")
                    changes.append("  P4787 __VALIDITY__: item (4) answered, interim "
                                   "recommendation marked superseded")
        touched[p] = d

    # The recovery store WINS at merge. merge_ref_shards.py is last-writer-wins per
    # (project_id, ref_col, sheet_row) and run_merge_chain.sh passes --shard-dir ref_shards
    # --shard-dir ref_shards_recovery in that order, so a ref_shards_recovery record
    # overwrites the ref_shards one split_shards.py generates from shards/. Writing the
    # ruling ONLY into shards/ would therefore change nothing in the deliverable -- the
    # CONTRADICTION record would win again. Write the same record to both, so the answer
    # is the same whichever store the merge happens to prefer, and so neither store is
    # left telling the retired story.
    rp = HERE / "ref_shards_recovery" / "P4787.json"
    rd = json.loads(rp.read_text())
    hits = [r for r in rd["resolutions"] if r.get("ref_col") == COL]
    if hits and MARKER not in (hits[0].get("researcher_notes") or ""):
        r = hits[0]
        prior = r.get("researcher_notes") or ""
        r.update({k: v for k, v in record("P4787").items() if k != "researcher_notes"})
        r["segment_name"] = SEGMENT["P4787"]
        r["researcher_notes"] = record("P4787")["researcher_notes"] + (
            " --- SUPERSEDED RECOVERY RECORD (its own text follows, kept verbatim as "
            "provenance; its 'CONTRADICTION -- DO NOT TREAT AS CONFIRMATORY' heading and its "
            "merge-time independence bracket describe the question as it stood before this "
            "ruling): ") + prior
        touched[rp] = rd
        changes.append("  P4787 ref_shards_recovery: CONTRADICTION record replaced by the "
                       "ruling (this is the store that wins at merge)")

    for c in changes:
        print(c)
    if not changes:
        print("nothing to do")
        return
    if not args.apply:
        print("\ndry run -- re-run with --apply")
        return
    for p, d in touched.items():
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\napplied to " + ", ".join(str(p.relative_to(HERE)) for p in touched))


if __name__ == "__main__":
    main()
