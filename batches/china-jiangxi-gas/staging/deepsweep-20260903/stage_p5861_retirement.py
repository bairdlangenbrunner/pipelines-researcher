#!/usr/bin/env python3
"""Apply the P5861 -> P4778 retirement ruling to the two shards it touches.

THE RULING (orchestrator, 2026-09-10). P5861 (row 3323, 'West-East Gas Pipeline 2 /
XinYu Branch(Gao'an-Xinyu)') and P4778 (row 2665, 'Jiangxi Natural Gas Pipeline Network
/ Phase I, Gao'an-Xinyu') are ONE physical pipeline: the 江西省天然气管网一期工程
高安-新余 干线. **Retire P5861 into P4778.**

WHY THIS SCRIPT EXISTS AT ALL -- the two shards disagreed and the deliverable shipped
both halves. P5861's `__REDUNDANCY__` reached verdict DUPLICATE on new evidence and
recommended the retirement. P4778's `__REDUNDANCY__` is the v2 record carried forward
verbatim, explicitly marked 'NOT re-adjudicated per this run's instruction' with 'NO NEW
EVIDENCE found this run' -- so a researcher reading the P4778 row learns the question is
open while the P5861 row says it is answered. The reciprocal adjudication was owed to
P4778 and this supplies it. Both rows must tell the same story.

The evidence is P5861's, not re-derived here; its three load-bearing items:
  (1) PipeChina's live 2026 油气管网设施公平开放 gas facility workbook enumerates all 34
      facilities of 国家管网集团西气东输分公司 and contains NO Xinyu branch and no
      高安-新余 (mechanically checked: '西气东输' extractable from the file, '新余' absent).
      A WEP2 branch that PipeChina's own disclosure does not list is not a WEP2 branch.
  (2) The 2014 provincial DRC plan (赣发改规划[2014]325号) names 高安-新余 by name as one of
      six 已建成 干线 of the 承接川气东送工程气源的江西省天然气管网一期工程 -- Phase I,
      Sichuan-East-fed, in the same sentence that names the segment.
  (3) CCXI's 2022 credit report separates the two systems by operator: 天然气管道公司 runs
      the 承接川气东送气源 Phase I network, while 管道分公司 承接西气东输二线气源.
So P5861's 'West-East Gas Pipeline 2' framing, its FuelSource, and its PipeChina-100%
ownership are one mis-attribution of a provincial Phase I trunk to the WEP2 system.

WHAT CARRIES TO THE SURVIVING ROW, AND WHAT DOES NOT.

CARRY -- Pressure = 6.3 MPa. P4778's Pressure is blank and its own record is UNRESOLVED
('no EIA found... do not force it'). P5861 resolved it, and the contingency it attached
('correct only under the Phase I reading of the row') is exactly what the retirement
establishes, so the value transfers with the contingency discharged. Two publishers
survive verification: the 2023 SSE bond prospectus gives 管道设计压力为6.3兆帕 for the
Phase I 干线 class, and the 2024-12-31 江西省能源局 approval independently specifies
6.3 MPa for the Phase-I side of the new interconnection at 高安市大城镇 (against 10 MPa
on the WEP2 side -- which is also why 10 MPa would be the answer under the sheet's own
WEP2 label, and is not). qianzhan supplies the segment-naming link (it names 高安-新余 as
one of those 干线) but states no pressure, so it verified name-only and is carried as the
relevance link rather than counted as a third publisher. Design pressure is a uniform
class parameter -- unlike a length or a cost it does not divide across segments -- so the
two-document chain does reach this segment. Tier medium (2+ publishers, but the
statement is class-level, not segment-level), independent yes.
  NB this also repairs an under-claim in P5861's own record: the drc.jiangxi.gov.cn
  approval verified ok && contains_value && name_found and the note leans on it in
  as many words, but it was never put in `proposed_refs` -- so merge_qc saw ONE surviving
  publisher and the record delivered at tier `low`. Added on both rows.

CARRY -- EndPrefecture/District = 'Xinyu'. Blank on both rows, i.e. an owed unit under
rule 4(c). 新余市 IS a prefecture-level city (districts 渝水区 / 分宜县 per the DRC plan),
so once the DRC plan sources the endpoint as 新余 the prefecture follows with no
inference; the same unambiguous-and-blank reasoning P4779 used to stage
EndPrefecture/District='Jingdezhen'. Goes on the existing Location record's own ref.
StartPrefecture/District needs nothing: P4778 already carries 'Yichun'.

DO NOT CARRY -- FuelSource 'West-East Gas Pipeline ', Owner1 'National Petroleum and
Natural Gas Pipeline Network Group Co Ltd' 100%. Each is contradicted by the evidence
above, and P4778 already carries the sourced replacement (川气东送 at medium/independent;
54% 江西省天然气集团有限公司 / 46% 国家管网集团东部原油储运有限公司). Pasting P5861's
values would overwrite a sourced value with the mis-attribution.

FLAG, DO NOT PASTE -- LengthKnown 69.21 km. Recorded as a sentinel, not staged as a
value: an unsourced number pasted into a blank cell is an orphan value, which is the
mirror of the orphan-[ref] rule. See the sentinel text for the full argument.

FLAG, DO NOT PASTE -- the retired row's Chinese name. Deliberately NOT staged into
P4778's OtherEnglishNames / OtherLanguageAlternativePipelineNames, though the pending
list proposed it: 西气东输二线新余支线（高安-新余） is not an alias for this pipe, it is the
mis-attribution being retired, and promoting it to an alias column would re-publish the
error as an alternative name and re-seed the next name-match run with it. Name columns
are a column-semantics call for the researcher in any case (same convention as
stage_olsn_paste_defect.py). Recorded as a sentinel with the recommendation that the
string live in ResearcherNotes as retirement provenance instead.

ALSO FLAGGED -- StartMonth1 = 12, on BOTH rows. P5861 traced the provenance: 2010年12月
is the SSE 2023 prospectus's 开工 date for the Jiangxi PHASE II network, while the same
document dates Phase I's first commissioning to 2010年6月 and its construction start to
2008年10月. On a Phase I trunk, 2010-12 looks like a cross-phase paste. P4778's own Start
record found no segment-naming source and downgraded to tier low, but it did not have
this provenance -- and StartYear1=2010 is separately bounded by petrobest, so the year
survives and only the month is in question. Recorded as a sentinel; clearing a value is
not staged unilaterally.

Idempotent: every edit is keyed on MARKER. Runs with the normalizers, BEFORE
normalize_schema_keys.py (the conformance gate) and therefore before split_shards.py.
    python3 stage_p5861_retirement.py [--apply]
"""
import argparse, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
MARKER = "P5861-RETIREMENT-RULING-2026-09-10"

SSE23 = "http://static.sse.com.cn/disclosure/bond/announcement/company/c/new/2023-11-23/240328_20231123_D5XK.pdf"
DRC24 = "https://drc.jiangxi.gov.cn/jxsfzhggwyh/col/col14665/content/content_1891743630814838784.html"
QIANZHAN = "https://img9.qianzhan.com/policy/202307/14/20230714-d7d735aa6fb9eae9.pdf"

RULING = (
    f"[{MARKER}] ORCHESTRATOR RULING: RETIRE P5861 INTO P4778. The two rows are one "
    "physical pipeline -- the 江西省天然气管网一期工程 高安-新余 干线. This supplies the "
    "reciprocal adjudication this record was owed: the text below is the v2 record carried "
    "forward and marked 'NOT re-adjudicated', but shards/P5861.json reached verdict "
    "DUPLICATE this run on evidence that is new relative to this shard, so the question is "
    "no longer open. Three load-bearing items: (1) PipeChina's live 2026 公平开放 gas "
    "facility workbook enumerates all 34 facilities of 国家管网集团西气东输分公司 and contains "
    "no Xinyu branch and no 高安-新余 ('西气东输' is mechanically extractable from the file, "
    "'新余' is not) -- a WEP2 branch absent from PipeChina's own disclosure is not a WEP2 "
    "branch; (2) the 2014 provincial DRC plan names 高安-新余 as one of six 已建成 干线 of "
    "the 承接川气东送工程气源的江西省天然气管网一期工程, in the same sentence that names the "
    "segment; (3) CCXI 2022 separates the systems by operator -- 天然气管道公司 runs the "
    "川气东送-fed Phase I network, 管道分公司 承接西气东输二线气源. P5861's WEP2 framing, its "
    "FuelSource and its PipeChina-100% ownership are one mis-attribution. THE SURVIVOR IS "
    "P4778, which already carries the sourced FuelSource (川气东送) and the sourced 54/46 "
    "ownership, so nothing from P5861's contradicted cells is to be pasted. What DOES "
    "transfer: Pressure 6.3 MPa (staged on this row's Pressure record) and "
    "EndPrefecture/District 'Xinyu' (staged on this row's Location record). What is flagged "
    "and NOT staged: LengthKnown 69.21 km, the retired row's Chinese name, and StartMonth1 "
    "-- one sentinel each on this row. This is not an obscurity call: the pipe exists and "
    "operates, the duplicate ROW is the artefact. --- CARRIED v2 TEXT FOLLOWS --- ")

PRESSURE_NOTE = (
    f"[{MARKER}] CARRIED FROM THE RETIRED P5861, contingency discharged. This record was "
    "UNRESOLVED ('no EIA found for this trunk... do not force it') and the cell is blank. "
    "P5861 resolved it and attached one condition -- 'correct only under the Phase I reading "
    "of the row' -- which is exactly what the retirement ruling establishes, so the value "
    "transfers. THE CHAIN: the 2023 SSE bond prospectus states a single design pressure for "
    "the Phase I network's trunk class ('一期工程 ... 干线全长 860 公里（不含支线）... 管道设计"
    "压力为 6.3 兆帕'), and the 2014 DRC plan names 高安-新余 as one of those six built 干线 "
    "-- so the two documents together reach this segment. Design pressure is a uniform "
    "engineering class parameter: unlike a length or a cost it does not divide across "
    "segments. CORROBORATED INDEPENDENTLY by the 2024-12-31 江西省能源局 approval, which "
    "specifies 6.3 MPa for the Phase-I side of the new 西二线与川气东送南昌联通工程 at "
    "高安市大城镇 ('第二段 ... 设计压力6.3兆帕') against 10 MPa on the WEP2 side ('第一段 ... "
    "设计压力10兆帕') -- which is also the proof that 10 MPa, not 6.3, would be the answer "
    "under the sheet's own (wrong) WEP2 label. Two publishers survive verification "
    "(static.sse.com.cn, drc.jiangxi.gov.cn); qianzhan verified name-only (it states no "
    "pressure) and is carried as the segment-naming relevance link, not counted as a third. "
    "Tier medium rather than high: 2+ publishers, but the statement is class-level, not "
    "segment-level. NB the drc approval was missing from P5861's own proposed_refs though "
    "its note leans on it, so that record delivered at tier low on one surviving publisher; "
    "added on both rows.")

LENGTH_NOTE = (
    f"[{MARKER}] LEGACY LENGTH 69.21 km -- FLAGGED, DELIBERATELY NOT STAGED AS A VALUE. "
    "The retired P5861 carries LengthKnown 69.21 km; this row's cell is blank and its own "
    "Length record is UNRESOLVED (no document gives a per-trunk length; the three Phase I "
    "figures found -- 870, 876 and a design-stage 680 km -- are all network aggregates). "
    "READ THE ASYMMETRY CAREFULLY, because P5861's own Length record argues the figure is "
    "impossible and that argument does NOT survive the retirement intact: its three proofs "
    "(PipeChina's 2026 inventory listing no Xinyu branch; the 2018-06 provincial table "
    "putting WEP2's actual Xinyu tie-in at 3.46 km and the whole Phase II network at 158.62 "
    "km province-wide; the DRC plan's 3.9 km WEP2 Xinyu spur) all refute a 69.21 km *WEP2* "
    "branch. They say nothing against a 69.21 km *Phase I* 高安-新余 trunk, which is the pipe "
    "the surviving row describes -- and Gao'an to Xinyu is roughly 55 km as the crow flies, "
    "so ~69 km of pipe is unremarkable. The 2-decimal precision is the signature of a "
    "figure someone once read off a filing, not of a round guess. SO: the number is "
    "plausible and unsourced, and its label was wrong rather than its magnitude. "
    "RECOMMENDATION -- a human call, two defensible answers. (a) Carry it into P4778's blank "
    "LengthKnown as unsourced legacy data, preserving a datum the retirement would otherwise "
    "destroy, and accept that it lands as a MISSING_REF owed unit for the next sweep to "
    "chase. (b) Let it die with the row, on the grounds that a retirement should not migrate "
    "unsourced numbers. NOT staged as a value either way, because staging it would paint an "
    "uncited number onto the paste surface -- the mirror of the no-orphan-[ref] rule. If it "
    "is carried, it must NEVER be cited to a WEP2 source, and any future document giving a "
    "per-trunk length for 高安-新余 overrides it outright.")

NAME_NOTE = (
    f"[{MARKER}] THE RETIRED ROW'S NAME -- FLAGGED, AND THE PENDING-LIST PROPOSAL TO MOVE IT "
    "TO OtherEnglishNames IS DECLINED. P5861 carries "
    "OtherLanguageAlternativePipelineNames = '西气东输二线新余支线（高安-新余）' and SegmentName "
    "= 'XinYu Branch(Gao'an-Xinyu)'. Preserving a retired row's names as aliases on the "
    "survivor is the normal courtesy, but not here: that string is not an alias for this "
    "pipe, it IS the mis-attribution being retired. Promoting it to an alias column would "
    "republish 'this is a West-East Gas Pipeline 2 branch' as an alternative NAME for a "
    "provincial Phase I trunk, and would re-seed the next name-match/dedup/discovery run "
    "with the very string that produced the duplicate. Name columns are also a "
    "column-semantics call for the researcher rather than something a sweep stages (same "
    "convention as the OtherLanguageSegmentName paste defect on P4785-P4790). RECOMMENDED "
    "INSTEAD: keep this row's own 一期工程, 高安-新余输气干线 as the Chinese name, and record "
    "the retirement in ResearcherNotes as provenance -- 'row P5861 (West-East Gas Pipeline "
    "2 / XinYu Branch, 西气东输二线新余支线（高安-新余）, LengthKnown 69.21 km) retired into this "
    "row 2026-09; its WEP2 attribution was incorrect' -- where a human reads it and no "
    "matcher indexes it as a name.")

START_NOTE = (
    f"[{MARKER}] StartMonth1 = 12 IS PROBABLY A CROSS-PHASE PASTE -- flagged on this row, "
    "not just on the retired one. Both rows carry StartYear1 2010 / StartMonth1 12. P5861 "
    "found the provenance: '2010 年 12 月' appears in the 2023 SSE bond prospectus as the "
    "开工 (construction-start) date of the Jiangxi PHASE II network -- the WEP2/WEP3-fed "
    "programme -- and nowhere as a commissioning date for anything in this corridor. The "
    "same document dates Phase I's FIRST commissioning to 2010年6月 (九江-南昌、九江-沙河段) "
    "and its construction start to 2008年10月. So on a Phase I trunk, a 2010-12 start month "
    "is most likely Phase II's 开工 date mis-carried -- and it would have arrived here via "
    "exactly the duplicate row this ruling retires, which was labelled 'West-East Gas "
    "Pipeline 2'. This row's own Start record found no segment-naming source and downgraded "
    "to tier low for that reason, but it did not have this provenance. THE YEAR SURVIVES "
    "INDEPENDENTLY: petrobest bounds Phase I full through-connection to 2010 with Xinyu "
    "named among the six cities served, so StartYear1 = 2010 stands. RECOMMENDATION: clear "
    "StartMonth1 unless a document is found dating this trunk's commissioning to a month. "
    "Not staged -- deleting a value is a human call, and the sweep's job here is to say why "
    "it is suspect.")


def find(recs, ref_col):
    hits = [r for r in recs if r.get("ref_col") == ref_col]
    if len(hits) != 1:
        sys.exit(f"expected exactly 1 {ref_col!r} record, found {len(hits)}")
    return hits[0]


# tier medium / independent False on every value-less record this script writes (the
# three sentinels and the __REDUNDANCY__ ruling), deliberately: they carry no refs of
# their OWN -- the evidence lives on P5861's records -- and a value-less record verifies
# to zero refs under the strict basis, so independence_qc would demote a `high` anyway.
# Setting it correctly up front keeps the store and the gate in agreement instead of
# leaning on a QC note to explain the gap. The SUBSTANCE of the redundancy verdict is
# high-confidence (three independent official documents); the tier field on a prose
# sentinel is not a paste signal, and understating it is the conservative direction.
def sentinel(template, sheet_row, ref_col="__VALIDITY__"):
    return {"project_id": "P4778", "sheet_row": sheet_row, "ref_col": ref_col,
            "value_col": None, "value_cols": [], "values": {}, "proposed_value": None,
            "class_out": "CONFIRMED", "kind": None, "tier": "medium", "independent": False,
            "proposed_refs": [], "verifications": [], "researcher_notes": template}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    p4778 = HERE / "shards" / "P4778.json"
    p5861 = HERE / "shards" / "P5861.json"
    a, b = json.loads(p4778.read_text()), json.loads(p5861.read_text())
    ra, rb = a["resolutions"], b["resolutions"]
    if any(MARKER in (r.get("researcher_notes") or "") for r in ra):
        print("already applied (marker present in shards/P4778.json) -- nothing to do")
        return
    row = find(ra, "Length [ref]").get("sheet_row")
    changes = []

    # 1. the reciprocal redundancy adjudication
    red = find(ra, "__REDUNDANCY__")
    red["class_out"], red["tier"], red["independent"] = "CONFIRMED", "medium", False
    red["researcher_notes"] = RULING + (red.get("researcher_notes") or "")
    changes.append("P4778 __REDUNDANCY__: UNRESOLVED/n-a -> CONFIRMED/medium, ruling prepended")

    # 2. Pressure carries across, with the ref P5861 verified but never proposed
    pr = find(ra, "Pressure [ref]")
    src = find(rb, "Pressure [ref]")
    pr["values"] = {"Pressure": "6.3", "PressureUnits": "MPa"}
    pr["value_cols"] = ["Pressure", "PressureUnits"]
    pr["class_out"], pr["kind"] = "REFS_ADDED", "FILL"
    pr["tier"], pr["independent"] = "medium", True
    # qianzhan verified name-only (contains_value False), so merge_qc would strip it
    # anyway; keeping it in `verifications` preserves the name evidence without making
    # the record look three-sourced. DRC24's name_found is True, so relevance_qc does
    # not cap this unit at `low` despite SSE23's name_found False.
    pr["proposed_refs"] = [SSE23, DRC24]
    pr["verifications"] = [dict(v) for v in (src.get("verifications") or [])
                           if v.get("url") in (SSE23, DRC24, QIANZHAN)]
    pr["researcher_notes"] = PRESSURE_NOTE + " --- SUPERSEDED PRIOR NOTE: " + (pr.get("researcher_notes") or "")
    changes.append("P4778 Pressure [ref]: UNRESOLVED/{} -> REFS_ADDED 6.3 MPa, 2 refs + 1 name-only verification, medium/independent")

    # ...and on the retired row too, so the two agree and the tier is not understated there
    if DRC24 not in (src.get("proposed_refs") or []):
        src["proposed_refs"] = list(src.get("proposed_refs") or []) + [DRC24]
        src["tier"], src["independent"] = "medium", True
        src["researcher_notes"] = (src.get("researcher_notes") or "") + (
            f"  [{MARKER}] REF ADDED at merge: the 2024-12-31 江西省能源局 approval "
            "(drc.jiangxi.gov.cn) verified ok && contains_value && name_found and this note "
            "relies on it in as many words, but it was absent from proposed_refs -- so "
            "merge_qc saw ONE surviving publisher and the record delivered at tier low. "
            "Now two publishers; tier low -> medium, independent -> yes. The same value and "
            "refs are staged on P4778, the surviving row.")
        changes.append("P5861 Pressure [ref]: drc.jiangxi.gov.cn added, low -> medium/independent")

    # 3. EndPrefecture/District: blank, owed, and unambiguous on the ref already there
    loc = find(ra, "Location [ref]")
    if "EndPrefecture/District" not in loc["values"]:
        vals = dict(loc["values"])
        keys = list(vals)
        i = keys.index("EndLocation") + 1 if "EndLocation" in keys else len(keys)
        loc["values"] = {**{k: vals[k] for k in keys[:i]},
                         "EndPrefecture/District": "Xinyu",
                         **{k: vals[k] for k in keys[i:]}}
        loc["value_cols"] = list(loc["values"])
        loc["researcher_notes"] = (loc.get("researcher_notes") or "") + (
            f"  [{MARKER}] FILLED an owed blank: EndPrefecture/District = 'Xinyu'. 新余市 IS "
            "a prefecture-level city (districts 渝水区 / 分宜县 per this record's own DRC-plan "
            "ref), so once that document sources the endpoint as 新余 the prefecture follows "
            "with no inference -- the same unambiguous-and-blank reasoning P4779 used to "
            "stage EndPrefecture/District = 'Jingdezhen'. Raised by the retired P5861, whose "
            "Location record recommended it and left it unstaged. StartPrefecture/District "
            "needs nothing: 'Yichun' is already here and already sourced.")
        changes.append("P4778 Location [ref]: + EndPrefecture/District = 'Xinyu' (owed blank)")

    # 4-6. three sentinels for the calls that are not the sweep's to make
    for note in (LENGTH_NOTE, NAME_NOTE, START_NOTE):
        ra.append(sentinel(note, row))
    changes.append("P4778: +3 __VALIDITY__ sentinels (legacy 69.21 km / retired row's name / StartMonth1)")

    for c in changes:
        print("  " + c)
    if not args.apply:
        print("\ndry run -- re-run with --apply")
        return
    p4778.write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")
    p5861.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\napplied to shards/P4778.json and shards/P5861.json")


if __name__ == "__main__":
    main()
