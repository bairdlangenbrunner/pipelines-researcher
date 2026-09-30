#!/usr/bin/env python3
"""Build ONE payload per PID (`batches/P####.json`) for the Jiangxi gas v3 fan-out.

Each payload carries only the work still owed on that row, in the plan's priority order:
  1. exhaustion pass over the dominant documents that already serve this row / its family
  2. owed FILLs (worklist MISSING_VALUE units)          -- Length -> Diameter -> Capacity ->
     StartYear -> ConstructionYear -> SegmentCost -> Owner -> FuelSource -> Pressure
  3. owed ref units (UNRESOLVED / DEAD_LINK after the carry, incl. the trqi/thepaper demotions)
  4. relevance re-reads (carried refs whose name check came back unnamed / system-only / unchecked)
  5. second-source pass on single-source carried REFS_ADDED
Carried work travels as `already_sourced` (context + reusable documents), never as work to redo.
Run AFTER carry_prior.py --apply.
"""
from __future__ import annotations

import collections
import json
import re
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

wl = json.loads((HERE / "worklist.json").read_text())
store = json.loads((HERE / "staged_resolutions.json").read_text())
attrib = json.loads((HERE / "wiki_attributed.json").read_text())
screen = json.loads((HERE / "harvest_screen.json").read_text())
spn = json.loads((HERE / "spn_recovered_origins.json").read_text())
args = json.loads((HERE / "deepsweep_args.json").read_text())
forms = json.loads((HERE / "name_forms.json").read_text())
carried_shard = json.loads((HERE / "shards" / "_carried_v2.json").read_text())
doc_index = json.loads((HERE / "doc_index.json").read_text()) if (HERE / "doc_index.json").exists() else {}
prior_store = json.loads((HERE / "../deepsweep-20260902/staged_resolutions.json").read_text())
lanes = {l.split("\t")[0]: l.split("\t")[1] for l in (HERE / "researcher_lanes.txt").read_text().splitlines()
         if "\t" in l and not l.startswith("#")}
snap = REPO / "data" / wl["scope"]["csv"]
df = pd.read_csv(snap, header=2, low_memory=False, keep_default_na=False, na_values=[])
row_of = {str(r["ProjectID"]).strip(): r for _, r in df.iterrows()}
roster_of = {r.split(" | ")[0]: r for r in args["roster"]}

FILL_ORDER = ["Length", "Diameter", "Capacity", "Start", "Construction", "SegmentCost",
              "Owner", "FuelSource", "Pressure", "Proposal"]
STATUS_ORDER = {"operating": 0, "construction": 1, "proposed": 2, "shelved": 3, "cancelled": 4}

# ---------------------------------------------------------------- prior findings (settled)
PRIOR: dict[str, list[str]] = {
    "P4780": ["NAME DEFECT (MZ's lane — RECORD, never repair): this row's Chinese name cell "
              "holds P4783's 上高支线. Do NOT search on the Chinese name."],
    "P4783": ["Its Chinese name currently sits on P4780. Search '田南-上高支线'."],
    "P4788": ["SETTLED 2026-08-26: `FuelSource` names WEP3 (西气东输三线), not Sichuan–Shanghai — "
              "sourced to the operator's own emergency plan.",
              "OPEN (carried, do not re-derive): sheet length 340.30 km vs 131.8 km between its own "
              "terminals — a __VALIDITY__ question, not a fill. Route redraw anchors already staged "
              "(Xinfeng 114.82255/25.43558, Ruijin 116.00923/25.94623).",
              "Its name cell holds a chopped fragment of one multi-segment string (with P4789)."],
    "P4789": ["Its name cell holds a chopped fragment of one multi-segment string (with P4788)."],
    "P4777": ["SETTLED: this is the Phase I network PARENT row. Do NOT recommend folding it into its "
              "segments; its route-vs-sheet length ratio is expected network granularity.",
              "MZ (2026-09-03), THE example for the exhaustion rule: the Sina article staged on P4776 "
              "(news.sina.com.cn/o/2011-08-29/193423070729.shtml — check P4776's already_sourced for "
              "the exact URL) states THIS row's Length 825 km, SegmentCost 3.1 bn RMB and "
              "Construction Oct 2008. Verify with --name and stage them here (Length is on the "
              "sheet -> REFS_ADDED; SegmentCost/Construction are blank -> FILL). The DRC plan says "
              "870 km as-built — reconcile in notes."],
    "P4776": ["MZ (2026-09-03): the Sina article on this row also carries P4777's length/cost/"
              "construction date — put those in cross_row_leads for P4777 (they are pre-routed in "
              "P4777's payload too; confirm the phrasing). Read it for P4778/P4779 while open."],
    "P4791": ["婺源 romanizes as **Wuyuan**. The wiki's 'Maoyuan' is wrong."],
    "P4778": ["OPEN (carried v2 __REDUNDANCY__): overlaps P5861 (WEP2 Xinyu Branch). Carry the "
              "adjudication unchanged unless NEW evidence lands; do not re-file the same finding."],
    "P5861": ["OPEN (carried v2 __REDUNDANCY__): overlaps P4778. Same rule."],
    "P4782": ["Recon: GulfPub 'Cang-Zi Line' match ADJUDICATED FALSE POSITIVE 2026-08-26. Do not re-open."],
    "P4931": ["RECON QUESTION: GEM files this as 西气东输三线 (WEP3); GulfPub matches it to WEP2. "
              "Adjudicate on sources.", "Its three existing refs (Status/Fuel/PipelineType) name only "
              "the SYSTEM (西气东输三线), not the middle section — relevance re-read owed."],
    "P4928": ["RECON QUESTION: same as P4931 — GulfPub calls this WEP2 against GEM's WEP3."],
    "P4944": ["Its wiki section states values with NO citations — treat none of it as evidence."],
    "P4946": ["Same as P4944: wiki section states values, cites nothing."],
    "P4657": ["NATIONAL TRUNK PARENT (川气东送一线). Its v2 refs were the Sinopec 天然气分公司 disclosure "
              "page (trqi.sinopec.com …news_20191205_840069053975.shtml) — now a CONFIRMED HTTP 404 "
              "with no Wayback capture — and thepaper.cn newsDetail_forward_1543492, also 404 at the "
              "page and the content API. Both units DEMOTED; find the relocated Sinopec disclosure "
              "(trqi.sinopec.com moved under /trqi/; try the 天然气分公司 site search, sinopecgroup.com "
              "news, and archive the hit via https://web.archive.org/save/<url>) or another source."],
    "P4649": ["Same trqi.sinopec.com + thepaper.cn demotions as P4657 — 9 units fell back to "
              "UNRESOLVED; the old evidence is in `owed_ref_units[].prior_evidence`."],
    "P4934": ["NATIONAL TRUNK PARENT (WEP3 mainline). Parent of P4931/P4928 — a spec sourced for "
              "the MAINLINE does not source a SECTION."],
    "P4947": ["NATIONAL TRUNK PARENT (WEP2 mainline). Parent of the WEP2 branches — same rule."],
    "P5862": ["Carried v2 sentinel: Phase I/II operator question. Route-vs-sheet ratio 30.1x."],
    "P5865": ["Carried v2 route redraw finding; Location values changed on the sheet since v2 "
              "(carry flagged drift) — re-verify the Location ref against the NEW values."],
    "P5866": ["Carried v2 route redraw finding; Location values changed since v2 — re-verify."],
    "P5888": ["Gate A: the only row sourced from ONE host (sohu.com). Needs a second origin or a "
              "prose reason."],
}

# ---------------------------------------------------------------- dominant documents
DOC_NOTES = {
    "static.sse.com.cn": "Jiangxi Provincial Investment Group bond tracking report (35 pp). READ 2026-09-04: "
        "names the network only at SYSTEM level (省天然气管网一期/二期, 3,182 km built / 2,892 km "
        "operating, 湖口 LNG) — never a segment. It is an operator-class source for Operator/Owner "
        "at system level only; a segment row needs a segment-naming source alongside it.",
    "img9.qianzhan.com": "Jiangxi DRC gas development plan PDF (ONE origin; anything it sources stays "
        "`medium` until a second class lands). Lists grid segments with length/diameter/schedule.",
    "trqi.sinopec.com": "CONFIRMED HTTP 404 (2026-09-03/04), no Wayback capture. Do not cite; find the relocation.",
    "www.quannan.gov.cn": "Quannan county disclosure PDF — southern grid rows.",
    "www.huaon.com": "Industry-research restatement of the DRC plan — same ORIGIN as qianzhan for tiering.",
    "web.archive.org": "Wayback capture of jxgajc.com (Jiangxi gas pipeline co. HR/news pages, origin dead).",
    "en.wikipedia.org": "WEP system article — SYSTEM level; one secondary source.",
    "www.petrobest.com": "Contractor reference page — names lines it built.",
    "www.pipechina.com.cn": "PipeChina notice — national trunk rows.",
    "www.mee.gov.cn": "MEE EIA approval / acceptance — regulator class.",
    "www.nea.gov.cn": "NEA notice — regulator class, WEP rows.",
}
doc_units: dict[str, set] = collections.defaultdict(set)
for r in prior_store["resolutions"]:
    if r.get("class_out") == "REFS_ADDED":
        for u in r.get("proposed_refs", []) or []:
            doc_units[u].add((r["project_id"], r["ref_col"]))
screen_of = {s["url"]: s for s in screen}
dominant = []
for u, units in sorted(doc_units.items(), key=lambda kv: -len(kv[1])):
    if len(units) < 8:
        break
    host = urlparse(u).netloc
    di = doc_index.get(u, {})
    dominant.append({"url": u, "v2_units": len(units), "v2_pids": sorted({p for p, _ in units}),
                     "note": DOC_NOTES.get(host, ""),
                     "live": True if di.get("local_text") else (screen_of.get(u) or {}).get("ok"),
                     "local_text": di.get("local_text"),
                     "digest": di.get("digest"), "title": di.get("title", ""),
                     "names_rows_segment_level": sorted(p for p, m in di.get("mentions", {}).items() if m["segment"]),
                     "names_rows_system_level_only": sorted(p for p, m in di.get("mentions", {}).items()
                                                            if not m["segment"] and m["system"])})

# ---------------------------------------------------------------- per-row assembly
owed_refs: dict[str, list] = collections.defaultdict(list)
rereads: dict[str, list] = collections.defaultdict(list)
sourced: dict[str, list] = collections.defaultdict(list)
second_owed: dict[str, list] = collections.defaultdict(list)
carried_fills: dict[str, list] = collections.defaultdict(list)
prior_by_key = {(r["project_id"], r["ref_col"]): r for r in prior_store["resolutions"]}
for r in store["resolutions"]:
    pid, rc = r["project_id"], r["ref_col"]
    tab = "operators_owners" if rc in ("Operator [ref]", "Owner [ref]") else None
    if r.get("class_in") == "FILL":
        carried_fills[pid].append({"ref_col": rc, "value_col": r.get("primary_value_col") or r.get("value_col"),
                                   "proposed_value": r.get("primary_value") or r.get("proposed_value"),
                                   "refs": r.get("proposed_refs", []), "tier": r.get("tier"),
                                   "relevance_reread": r.get("relevance_reread", "")})
        continue
    if r["class_out"] in ("UNRESOLVED", "DEAD_LINK"):
        u = {"ref_col": rc, "value_cols": r.get("value_cols", []), "values": r.get("values", {}),
             "primary_value": r.get("primary_value"), "current_ref": r.get("current_ref", ""),
             "class_in": r["class_out"], "tab": tab}
        if r.get("carried_needs_recheck"):
            pr = prior_by_key.get((pid, rc), {})
            u["prior_evidence"] = {"why_demoted": r["carried_needs_recheck"],
                                   "v2_refs": pr.get("proposed_refs", []),
                                   "v2_notes": pr.get("researcher_notes", ""),
                                   "rechecks": r.get("carried_rechecks", [])}
        owed_refs[pid].append(u)
    elif r["class_out"] == "REFS_ADDED":
        ent = {"ref_col": rc, "values": r.get("values", {}), "refs": r.get("proposed_refs", []),
               "tier": r.get("tier"), "notes": (r.get("researcher_notes") or "")[:400],
               "name_check": [{k: v.get(k) for k in ("url", "name_found", "name_matched", "name_level")}
                              for v in r.get("verifications", []) or []]}
        if r.get("relevance_reread"):
            ent["relevance_reread"] = r["relevance_reread"]
            ent["task"] = {
                "unnamed": "No carried ref names this pipeline. Read each ref again for the segment name "
                           "(any form in name_forms); if it is there, encode name_found:true with the matched "
                           "string; if not, find a segment-naming source or downgrade with a prose note.",
                "system-only": "The refs name only the SYSTEM/trunk, not this segment. Find a segment-naming "
                               "source for the value (approval, EIA, municipal notice), keep the system "
                               "ref only alongside it; or state in notes why a system-level source is "
                               "the right evidence for THIS cell (e.g. one integrated network operator).",
                "unchecked": "The name recheck could not read the page (access failure). Read it via "
                             "Wayback or another route and encode name_found by hand.",
            }[r["relevance_reread"]]
            rereads[pid].append(ent)
        else:
            sourced[pid].append(ent)
        hosts = {urlparse(x).netloc for x in ent["refs"]}
        if len(hosts) < 2:
            second_owed[pid].append({"ref_col": rc, "refs": ent["refs"], "tier": ent["tier"]})
    elif r["class_out"] == "REVERIFIED":
        ent = {"ref_col": rc, "values": r.get("values", {}), "refs": [r.get("current_ref", "")],
               "tier": "existing-live",
               "name_check": [{k: v.get(k) for k in ("url", "name_found", "name_matched", "name_level")}
                              for v in r.get("verifications", []) or []]}
        if r.get("relevance_reread"):
            ent["relevance_reread"] = r["relevance_reread"]
            ent["task"] = ("EXISTING sheet ref names only the system / not this pipeline. Do not delete "
                           "it; add a segment-naming ref alongside (REFS_ADDED) or note why it stands.")
            rereads[pid].append(ent)
        else:
            sourced[pid].append(ent)

owed_fills: dict[str, list] = collections.defaultdict(list)
for u in wl["units"]:
    if u.get("class") != "MISSING_VALUE":
        continue
    pid = u["project_id"]
    if any(f["ref_col"] == u["ref_col"] for f in carried_fills[pid]):
        continue
    owed_fills[pid].append({"ref_col": u["ref_col"], "value_cols": u.get("value_cols", []),
                            "primary_value_col": u.get("primary_value_col"),
                            "current_values": u.get("values", {}),
                            "tab": u.get("tab") or None, "kind": "FILL"})
def _fill_rank(f):
    rc = f["ref_col"].replace(" [ref]", "")
    for i, k in enumerate(FILL_ORDER):
        if rc.startswith(k):
            return i
    return 99
for pid in owed_fills:
    owed_fills[pid].sort(key=_fill_rank)

attrib_by_pid: dict[str, list] = collections.defaultdict(list)
for a in attrib["attributions"]:
    attrib_by_pid[a["project_id"]].append(a)
uncited = {b["project_id"]: b for b in attrib.get("uncited_sections", [])}
pool_live: dict[str, list] = collections.defaultdict(list)
pool_dead: dict[str, list] = collections.defaultdict(list)
for s in screen:
    for pid in s["project_ids"]:
        (pool_live if s.get("ok") else pool_dead)[pid].append(
            s["url"] if s.get("ok") else {"url": s["url"], "status": s.get("status"),
                                          "reason": (s.get("reason") or "")[:110]})
spn_by_pid: dict[str, list] = collections.defaultdict(list)
for s in spn:
    for pid in s["project_ids"]:
        spn_by_pid[pid].append({k: s.get(k) for k in ("origin", "ok", "status", "reason")})
carried_sent: dict[str, list] = collections.defaultdict(list)
for r in carried_shard["resolutions"]:
    if (r.get("ref_col") or "").startswith("__"):
        carried_sent[r["project_id"]].append({"sentinel": r["ref_col"], "verdict": r.get("verdict"),
                                              "notes": (r.get("researcher_notes") or "")[:300]})

pids = list(dict.fromkeys(u["project_id"] for u in wl["units"]))
seg_of, srow_of, wiki_of = {}, {}, {}
for u in wl["units"]:
    seg_of.setdefault(u["project_id"], u.get("segment_name") or "")
    srow_of.setdefault(u["project_id"], u["sheet_row"])
    wiki_of.setdefault(u["project_id"], (u.get("wiki") or "").strip())

(HERE / "batches").mkdir(exist_ok=True)
(HERE / "shards").mkdir(exist_ok=True)
for old in (HERE / "batches").glob("*.json"):
    old.unlink()
summary = []
for pid in pids:
    src = row_of.get(pid)
    g = lambda c: str(src.get(c, "")) if src is not None else ""
    my_docs = [d for d in dominant if pid in d["v2_pids"] or pid in d["names_rows_segment_level"]]
    fam_docs = [d for d in dominant if d not in my_docs and
                (pid in d["names_rows_system_level_only"] or
                 any(wiki_of.get(p) == wiki_of[pid] for p in d["v2_pids"]))]
    # every indexed document (dominant or not) that names THIS row at segment level
    named_in = [{"url": u, "local_text": di.get("local_text"), "digest": di.get("digest"),
                 "title": di.get("title", ""), "matched": di["mentions"][pid]["segment"]}
                for u, di in doc_index.items() if di.get("mentions", {}).get(pid, {}).get("segment")]
    status = g("Status")
    payload = {
        "project_id": pid, "sheet_row": srow_of[pid], "country": "China", "province": "Jiangxi",
        "commodity": "gas", "snapshot": wl["scope"]["csv"],
        "pipeline_name": g("PipelineName"), "segment_name": seg_of[pid],
        "other_names": {c: g(c) for c in ("OtherEnglishNames", "OtherLanguagePrimaryPipelineName",
                                          "OtherLanguageSegmentName", "OtherLanguageAlternativePipelineNames") if g(c)},
        "name_forms": forms.get(pid, {}),
        "status": status, "wiki": wiki_of[pid], "roster": roster_of.get(pid, ""),
        "researcher_lane": lanes.get(pid, ""),
        "work_order": ["1 exhaustion pass: dominant_documents (read each for EVERY column here and "
                       "sibling rows -> cross_row_leads)", "2 owed_fills (operating rows first, in listed order)",
                       "3 owed_ref_units", "4 relevance_rereads", "5 second_source_owed",
                       "6 harvest_pool_live (open every one; report harvest_opened)",
                       "7 __STATUS__ if status != operating; __VALIDITY__/__REDUNDANCY__ only on NEW evidence"],
        "dominant_documents": [dict(d, relation=("names this row" if pid in d["names_rows_segment_level"]
                                                  else "served this row in v2" if pid in d["v2_pids"]
                                                  else "system-level / family document")) for d in my_docs + fam_docs],
        "documents_naming_this_row": named_in,
        "local_text_note": "local_text = plain-text extraction made 2026-09-04 (read it with the Read tool "
                           "or `cat`); `digest` = the same document filtered to lines with lengths/diameters/pressures/"
                           "dates/place names — read the digest first on the two very long PDFs, the full text "
                           "when a fact needs context. ALWAYS cite the URL, never the local path.",
        "owed_fills": owed_fills[pid],
        "owed_ref_units": owed_refs[pid],
        "relevance_rereads": rereads[pid],
        "second_source_owed": second_owed[pid],
        "already_sourced": sourced[pid],
        "carried_fills": carried_fills[pid],
        "carried_sentinels_v2": carried_sent[pid],
        "wiki_attributions": attrib_by_pid[pid],
        "wiki_section_uncited": uncited.get(pid),
        "harvest_pool_live": sorted(set(pool_live[pid])),
        "harvest_pool_failed": pool_dead[pid],
        "spn_origins": spn_by_pid[pid],
        "prior_findings": PRIOR.get(pid, []),
        "status_review_owed": status != "operating",
    }
    (HERE / "batches" / f"{pid}.json").write_text(json.dumps(payload, indent=1, ensure_ascii=False))
    summary.append((pid, status, len(owed_fills[pid]), len(owed_refs[pid]), len(rereads[pid]),
                    len(second_owed[pid]), len(pool_live[pid]), len(my_docs) + len(fam_docs)))

summary.sort(key=lambda t: (STATUS_ORDER.get(t[1], 9), -(t[2] + t[3] + t[4])))
print(f"wrote {len(summary)} payloads -> batches/P####.json")
print(f"  {'pid':6} {'status':12} fills refs rereads 2nd pool docs")
for t in summary:
    print(f"  {t[0]:6} {t[1]:12} {t[2]:5} {t[3]:4} {t[4]:7} {t[5]:3} {t[6]:4} {t[7]:4}")
print(f"  totals: fills {sum(t[2] for t in summary)} refs {sum(t[3] for t in summary)} "
      f"rereads {sum(t[4] for t in summary)} second-source {sum(t[5] for t in summary)}")
print(f"  dominant documents: {len(dominant)}")
for d in dominant:
    print(f"    {d['v2_units']:3} units / {len(d['v2_pids'])} rows live={d['live']} {d['url'][:95]}")
