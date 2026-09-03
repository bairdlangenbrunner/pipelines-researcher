#!/usr/bin/env python3
"""Bundle the 18 in-scope PIDs into subagent batch payloads (sweep SOP "At scale").

Each payload is self-contained: current sheet values, the ref units actually OWED on that
row, the wiki-attributed candidate citations WITH this run's verification verdict, and the
row's own open questions. Seeding the verdicts is the point — a subagent that re-fetches
`m.qcc.com` learns nothing we don't already know, and the SOP forbids fanning verification
out at web.archive.org. So the payload tells each agent what is already settled and spends
its budget on corroboration and on the value/existence questions instead.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
SNAP = REPO / "data" / "GGIT_gas_snapshot_20260826.csv"
BATCH_SIZE = 4

KEEP = ["ProjectID", "PipelineName", "SegmentName", "OtherLanguageSegmentName",
        "PipelineNetworkGrouping", "Status", "Status [ref]", "Fuel",
        "StartLocation", "StartState/Province", "StartCountryOrArea",
        "EndLocation", "EndState/Province", "EndCountryOrArea",
        "LengthKnown", "LengthKnownUnits", "Length [ref]", "LengthDoubleCounting",
        "Diameter", "DiameterUnits", "Diameter [ref]",
        "Capacity", "CapacityUnits", "Capacity [ref]",
        "Pressure", "PressureUnits", "Pressure [ref]",
        "StartYear1", "Start [ref]",
        "SegmentCost", "SegmentCostUnits", "SegmentCostYear", "SegmentCost [ref]",
        "Owner", "RouteType", "RouteAccuracy", "Route [ref]",
        "Researcher", "ResearcherNotes", "LastUpdated", "Wiki"]

OPEN_QUESTIONS = {
    "P4777": ["NETWORK-GRANULARITY / AGGREGATE QUESTION. segment_name is bare 'Phase I'; "
              "endpoints blank; LengthKnown=825.00. The wiki's 'Phase I' h3 is a CONTAINER "
              "heading listing 18 constituent segments and carrying no field bullets, so this "
              "row is the Phase I parent, not a segment. Phase I rows that DO carry a length "
              "sum to 427.50 km, leaving ~397.50 km to sit in the 6 blank-length Phase I trunk "
              "rows. CORROBORATED 2026-08-26 by GEM's OWN route geometry: the 12 rows whose "
              "segment_name carries 'Phase I' sum to 798.74 km of merged length, and adding "
              "the 2 unlabelled branch rows (P5887, P5889) gives 853.36 km. 825.00 therefore "
              "sits INSIDE that band (-3.2% / +3.4%), which settles the SHAPE: parent row, "
              "not double count. NOTE the constraint: route-derived length is GEM's own "
              "geometry, so per standing rule 1 it may corroborate internally but may NEVER "
              "be cited as a [ref]. QUESTION: source the 825 km figure and state whether it is the Phase I "
              "system total. Do NOT recommend a fold/delete without sourcing — the Kazakhstan "
              "cluster-A lesson is that this signature is refuted as often as confirmed. "
              "class_out=UNRESOLVED unless you find a source that settles it."],
    "P4791": ["ROMANIZATION MISMATCH. GEM SegmentName is 'Leping-Dexing-Wuyuan'; the wiki lists "
              "'Leping-Dexing-Maoyuan'. 婺源 romanizes as Wuyuan, so the WIKI is wrong. Wiki "
              "edits are MZ's lane — flag it, do not fix the page. Confirm the correct name "
              "from an independent source."],
    "P4784": ["EXISTING REFS DO NOT SUPPORT THEIR VALUES. Pressure [ref] and Diameter [ref] "
              "both cite a cnr.cn article that states length 138 km, cost 5.98e8 RMB and "
              "capacity 3.13e8 m3/y, with NO pressure or diameter token in any form. That same "
              "URL DOES support Capacity and SegmentCost, which are uncited. Recommend "
              "REPOINTING it to Capacity/SegmentCost. Never delete a once-working ref: the "
              "Pressure/Diameter cells need a different source, not an empty cell."],
    "P4778": ["OVERLAP WITH AN OUT-OF-SCOPE TRUNK. Gao'an->Xinyu overlaps P5861 (WEP2 Xinyu "
              "Branch, 高安-新余), which is a national trunk in MZ's own scope. Flag the overlap; "
              "do not restate P5861."],
}
# Rows the Jiangxi DRC plan (赣发改规划〔2014〕325号) names as built Phase I trunks. On these
# the EXISTENCE and STATUS questions are closed by an official 2014 source — but the plan names
# the trunks without measuring them, so it can never fill a blank LengthKnown.
DRC_NAMED_TRUNK = {
    "P4780": "九江—南昌 Jiujiang-Nanchang",
    "P4781": "九江—沙河 Jiujiang-Shahe",
    "P4779": "九江—景德镇 Jiujiang-Jingdezhen",
    "P4782": "南昌—丰城 Nanchang-Fengcheng",
    "P4778": "高安—新余 Gao'an-Xinyu",
    "P4776": "丰城—抚州 Fengcheng-Fuzhou",
    "P4783": "田南—上高 Tiannan-Shanggao (支线)",
}

# Chinese-name cells that are corrupt in the snapshot. MZ owns names — record, never repair.
NAME_DEFECT = {
    "P4780": ["CHINESE NAME IS ON THE WRONG ROW. OtherLanguageSegmentName='上高支线' "
              "(Shanggao Branch), but this row is Jiujiang-Nanchang. 上高 belongs to P4783 "
              "(Tiannan-Shanggao), whose Chinese-name cell is EMPTY. Record as a __VALIDITY__ "
              "finding for MZ; do not repair the cell and do not treat 上高支线 as this row's "
              "name when searching."],
    "P4788": ["CHINESE NAME CELL IS A FRAGMENT. OtherLanguageSegmentName='丰段、进贤段；赣州南"
              "支线信丰瑞金段、上犹崇义' — a chopped piece of one longer multi-segment list "
              "shared with P4789, not a name. Do NOT search on it. It also plausibly explains "
              "this row's length: 340.30 km against a 31.75 km route trace is what you would "
              "expect if 340.30 was lifted from a multi-segment aggregate while the geometry "
              "covers one section. TEST that reading against sources; do not assume it. "
              "__VALIDITY__ finding for MZ."],
    "P4789": ["CHINESE NAME CELL IS A FRAGMENT. OtherLanguageSegmentName='段、樟树新干峡江段、"
              "井开区吉水永丰段、赣州南' — begins with a bare '段、' and ends truncated at "
              "'赣州南'. Same corrupt multi-segment list as P4788. Do NOT search on it. "
              "__VALIDITY__ finding for MZ."],
}

# LengthKnown vs GEM's own route-derived LengthEstimateKm. A large ratio means one of the
# two is wrong — either the sheet length or the attached geometry — and on a row with a
# `medium` RouteAccuracy both cannot be right. Routes are MZ's locked lane, so these route
# OUT as __VALIDITY__ findings; we do not redraw geometry here.
ROUTE_LENGTH_DIVERGENCE = {
    "P5862": (18.45, 553.78, 30.0, "medium"),
    "P4788": (340.30, 31.75, 10.7, "medium"),
    "P5866": (19.12, 123.15, 6.4, "very low (straight line/schematic)"),
    "P5887": (23.30, 49.27, 2.1, "medium"),
    "P4784": (138.00, 258.13, 1.9, "medium"),
}

BLANK_LENGTH = ["P4776", "P4778", "P4780", "P4781", "P4782", "P5859"]


def clean(v):
    if v is None:
        return ""
    if isinstance(v, float) and math.isnan(v):
        return ""
    return str(v).strip()


def main() -> None:
    wl = json.loads(Path("worklist.json").read_text())
    att = json.loads(Path("wiki_attributed.json").read_text())
    ver = json.loads(Path("wiki_attributed_verified.json").read_text())
    verified = {(r["project_id"], r["ref_col"]): r for r in ver["attributions"]}
    container = {c["project_id"]: c for c in att.get("container_rows", [])}

    df = pd.read_csv(SNAP, header=2, low_memory=False, keep_default_na=False, na_values=[])
    cols = [c for c in KEEP if c in df.columns]
    rows = {r["ProjectID"]: {c: clean(r[c]) for c in cols}
            for _, r in df.iterrows() if r["ProjectID"] in
            {u["project_id"] for u in wl["units"]}}

    by_pid: dict[str, list] = {}
    for u in wl["units"]:
        by_pid.setdefault(u["project_id"], []).append(u)

    payloads = []
    for pid in sorted(by_pid):
        units = by_pid[pid]
        u0 = units[0]
        owed = []
        for u in units:
            v = verified.get((pid, u["ref_col"]))
            owed.append({
                "ref_col": u["ref_col"],
                "value_cols": u["value_cols"],
                "values": u["values"],
                "current_ref": u.get("current_ref", ""),
                "class": u["class"],
                "existing_ref_checks": u.get("existing_ref_checks", []),
                "tab": "operators_owners" if u.get("tab") == "operators_owners" else None,
                "oo_sheet_row": u.get("oo_sheet_row"),
                "wiki_candidate": None if not v else {
                    "wiki_value": v["wiki_value"],
                    "candidate_urls": v["candidate_urls"],
                    "our_verdict": v["check"]["verdict"],
                    "our_verdict_detail": v["check"]["detail"],
                },
            })
        q = list(OPEN_QUESTIONS.get(pid, []))
        q += NAME_DEFECT.get(pid, [])
        if pid in DRC_NAMED_TRUNK:
            q.append(
                f"EXISTENCE AND STATUS ARE ALREADY CLOSED on this row. The Jiangxi DRC plan "
                f"(赣发改规划〔2014〕325号, in shared_evidence.md — READ IT, do not re-find it) "
                f"names this trunk as {DRC_NAMED_TRUNK[pid]} and states it was 已建成 (built) as "
                "of 2014. That is official independent support for Status. But the plan names "
                "the trunks WITHOUT measuring them, so it cannot source a length — do not "
                "stretch it into one. Spend your budget on the length and the other specs.")
        if pid in ROUTE_LENGTH_DIVERGENCE:
            k, e, ratio, acc = ROUTE_LENGTH_DIVERGENCE[pid]
            q.append(
                f"LENGTH vs ROUTE DISAGREE BY {ratio}x. Sheet LengthKnown={k} km, but the row's "
                f"own GEM route geometry measures {e} km, at RouteAccuracy '{acc}'. Both cannot "
                "be right. Decide WHICH is wrong from independent sources: a sourced length that "
                "matches the sheet means the geometry is wrong (a __VALIDITY__ finding to route "
                "to MZ, who owns routes — do NOT redraw it); a sourced length near the route "
                "measurement means LengthKnown is wrong (a value change, needs tier + ref). "
                "Route-derived length is GEM's own geometry, so it can never be the [ref].")
        if pid in BLANK_LENGTH:
            q.append("LengthKnown is BLANK on this row (a `fills` target). Source a length if "
                     "you can; a sourced fill is a value change, so give it a tier and a ref.")
        payloads.append({
            "project_id": pid,
            "sheet_row": u0["sheet_row"],
            "gem_wiki_page": u0.get("wiki", ""),
            "wiki_note": container.get(pid, {}).get("note"),
            "sheet_values": rows.get(pid, {}),
            "owed_ref_units": owed,
            "open_questions": q,
            "shared_evidence": "shared_evidence.md — two primary documents (Jiangxi DRC gas "
                               "utilisation plan 2013-2020; CCXI 2025 bond rating report) "
                               "already fetched to this directory as jx_plan.txt and "
                               "sse_bond_2025.txt. READ THE LOCAL FILES; do not re-download.",
        })

    out = Path("batches"); out.mkdir(exist_ok=True)
    batches = [payloads[i:i + BATCH_SIZE] for i in range(0, len(payloads), BATCH_SIZE)]
    for i, b in enumerate(batches, 1):
        Path(out / f"batch_{i:02d}.json").write_text(
            json.dumps({"batch": i, "n_rows": len(b), "rows": b}, ensure_ascii=False, indent=2))
        print(f"  batch_{i:02d}.json  {len(b)} rows: {', '.join(r['project_id'] for r in b)}"
              f"   ({sum(len(r['owed_ref_units']) for r in b)} owed units)")
    print(f"\n{len(batches)} batches, {len(payloads)} rows, "
          f"{sum(len(r['owed_ref_units']) for r in payloads)} owed units total")


if __name__ == "__main__":
    main()
