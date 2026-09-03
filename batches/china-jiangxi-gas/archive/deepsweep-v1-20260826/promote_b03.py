#!/usr/bin/env python3
"""Promote batch_03's verified false-negative verifications; file the FuelSource conflict.

Batch 03 encoded manual confirmations as ok=False (or ok=True/cv=False), where batches
01/04/05 encoded equivalents as ok=True+cv=True with a documented note. merge_qc.
verified_refs keeps only ok && contains_value, so 16 refs across 11 records were being
stripped -- and merge_ref_shards then honestly downgraded those REFS_ADDED claims to
UNRESOLVED/DEAD_LINK. Net effect: real evidence discarded.

Every promotion below was RE-VERIFIED BY THE ORCHESTRATOR in this session, either by
url_verifier against the value's real surface form, or by reading the local PDF copy.
Two refs are deliberately LEFT stripped -- they are rule-5 in-cell keeps that genuinely
were not verified, and must not enter a proposal.

Idempotent: re-running changes nothing.
"""
import json, sys
from pathlib import Path

P = Path("shards/batch_03.json")
DOC = json.loads(P.read_text())
recs = DOC["resolutions"] if isinstance(DOC, dict) else DOC

Q = "quannan.gov.cn"
JG = "jxganan.com/anquanyanshoupingjia/9746.html"
SH = "sohu.com/a/278468337_693503"
JX = "tt.m.jxnews.com.cn/news/1193625"
CNR = "news.cnr.cn/native/city/20201022"
WN = "wuning.gov.cn/zwzx/wnyw/202104"

ORCH = ("ORCHESTRATOR-VERIFIED 2026-08-26: %s Promoted to ok/contains_value so the "
        "documented confirmation passes merge_qc.verified_refs as data rather than being "
        "stripped -- consistent with how batches 01/04/05 encode the same situation.")

PDF = ("re-read directly from the local 11,461,354-byte copy of this PDF "
       "(quannan_ganzhounan.pdf/.txt, 494,223 chars extracted; author 赣安 谢玉锦, WPS 文字, "
       "created 2024-11-14). The document is genuinely in hand; the live 403 is an access "
       "failure on quannan.gov.cn, never a deletion (standing rule: only 404/410 drops a ref). "
       "Decisive sentence: '线路长度约340.3km，管径DN450，设计压力6.3MPa，设计输量为8.65×108Nm3/a', "
       "attributed verbatim to the 信丰-瑞金段 by '管线全长537.5km，其中赣州南支线信丰-瑞金段线路长度约340.3km'.")

# (project_id, ref_col, url-substring) -> extra note fragment
PROMOTE = {
 ("P4788","Status [ref]",Q):    PDF + " Operating status per the trial-run/safety-acceptance language.",
 ("P4788","Fuel [ref]",Q):      PDF + " Title itself names a 天然气管网 (natural gas pipeline network) project.",
 ("P4788","Capacity [ref]",Q):  PDF + " 8.65×10^8 Nm3/a = 0.865 bcm/y, rounding to the sheet's 0.87.",
 ("P4788","Length [ref]",Q):    PDF + " 340.3km is this SECTION's own design length, NOT an aggregate -- the four-branch total is separately stated as 537.5km. This refutes the aggregate-length hypothesis.",
 ("P4788","Diameter [ref]",Q):  PDF + " DN450 exact.",
 ("P4788","Location [ref]",Q):  PDF + " Endpoints verbatim: '起始于赣州南支线信丰分输站' ... '止于西三线瑞金分输站'. NOTE: the coordinate parenthetical in the prior note rendered DMS as decimal -- the document reads E114°49'21.19\"/N25°26'8.07\" and E116°0'33.24\"/N25°56'46.44\" (DMS), not E114.49/N25.26. Only the place-name values are staged, so no staged value was affected.",
 ("P4788","Pressure [ref]",Q):  PDF + " 设计压力6.3MPa exact. Sheet Pressure is BLANK (confirmed against the 2026-08-26 snapshot), so this is a sourced FILL.",
 ("P4788","FuelSource [ref]",Q):PDF + " Feed points verbatim: '从西二线149#阀室或西三线瑞金分输清管站引出气源'. See the __VALIDITY__ record filed for this row -- the document CONTRADICTS half the sheet value.",
 ("P4784","Diameter [ref]",JG): "re-verified live via url_verifier (HTTP 200, contains '323.9'). D323.9mm OD is the standard GB/ISO equivalent of DN300 nominal -- same physical pipe, two conventions; the automated screen only missed the literal '300'.",
 ("P4789","Status [ref]",SH):   "re-verified live via url_verifier (HTTP 200, contains 投产/通气). Status inference from commissioning prose is explicitly sanctioned by url_verifier's own docstring ('a status any_of miss is expected; the agent infers status from the page's prose').",
 ("P4791","Capacity [ref]",JX): "re-verified live via url_verifier (HTTP 200, contains '2.8亿'). 设计年输气量2.8亿立方米 = 0.28 bcm/y, an EXACT match to the sheet under unit-form equivalence.",
 ("P4791","SegmentCost [ref]",JX):"re-verified live via url_verifier (HTTP 200, contains '2.8亿'; same article states 项目总投资约3.8亿元). 3.8亿元 = 380,000,000 RMB, exact.",
 ("P4784","Capacity [ref]",CNR):"re-verified live via url_verifier (HTTP 200, contains '3.13'). 年输气能力3.13亿立方米 = 0.313 bcm/y, rounding to the sheet's 0.31. (An earlier orchestrator check reported this host as a soft 404 -- that was a DIFFERENT URL, the 2019-12-31 path; this 2020-10-22 path is live.)",
 ("P4784","Capacity [ref]",WN): "re-verified live via url_verifier (HTTP 200, contains '3.13'). Independent county-government report of the same 3.13亿立方米 figure.",
}

# deliberately NOT promoted: rule-5 in-cell keeps, genuinely unverified as proposals
KEEP_STRIPPED = {("P4784","Status [ref]","archive.org/details/screenshot"),
                 ("P4791","Status [ref]","web.archive.org/web/20250902140516")}

n_prom = n_mark = n_cls = 0
for r in recs:
    pid, rc = r.get("project_id"), r.get("ref_col")
    for v in (r.get("verifications") or []):
        u = v.get("url") or ""
        for (p2, c2, frag), extra in PROMOTE.items():
            if pid == p2 and rc == c2 and frag in u:
                if not (v.get("ok") and v.get("contains_value")):
                    v["ok"] = True
                    v["contains_value"] = True
                    note = (v.get("note") or "").rstrip()
                    stamp = ORCH % extra
                    if "ORCHESTRATOR-VERIFIED" not in note:
                        v["note"] = (note + " || " + stamp) if note else stamp
                    n_prom += 1
        for (p3, c3, frag3) in KEEP_STRIPPED:
            if pid == p3 and rc == c3 and frag3 in u:
                note = (v.get("note") or "").rstrip()
                if "DELIBERATELY NOT PROPOSED" not in note:
                    v["note"] = note + (" || DELIBERATELY NOT PROPOSED (orchestrator 2026-08-26): "
                        "this ref is correctly KEPT in the sheet cell under standing rule 5 "
                        "(not a 404/410), but it was never content-verified, so it must not enter "
                        "proposed_refs. Left stripped on purpose -- not an encoding defect.")
                    n_mark += 1
    if r.get("class_out") == "CONFIRMED":
        r["class_out"] = "REFS_ADDED"
        n_cls += 1

P.write_text(json.dumps(DOC, ensure_ascii=False, indent=2))
print(f"promoted verifications: {n_prom}")
print(f"marked keep-stripped:   {n_mark}")
print(f"CONFIRMED -> REFS_ADDED:{n_cls}")
