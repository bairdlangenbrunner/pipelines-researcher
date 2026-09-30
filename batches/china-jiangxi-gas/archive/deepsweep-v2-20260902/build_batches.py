#!/usr/bin/env python3
"""Build the per-subagent batch payloads for the Jiangxi gas v2 sweep.

One payload per batch of rows; rows are grouped by wiki page family so agents sharing a
source document read it once. Each row carries ONLY the units still owed — carried work
from 2026-08-26 travels as `already_sourced` (context and reusable documents), never as
work to redo.
"""
from __future__ import annotations

import collections
import json
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BATCH_SIZE = 5      # max rows per agent
OWED_CAP = 28       # max owed ref units per agent

wl = json.loads((HERE / "worklist.json").read_text())
store = json.loads((HERE / "staged_resolutions.json").read_text())
attrib = json.loads((HERE / "wiki_attributed.json").read_text())
screen = json.loads((HERE / "harvest_screen.json").read_text())
args = json.loads((HERE / "deepsweep_args.json").read_text())
snap = REPO / "data" / wl["scope"]["csv"]
df = pd.read_csv(snap, header=2, low_memory=False, keep_default_na=False, na_values=[])
row_of = {str(r["ProjectID"]).strip(): r for _, r in df.iterrows()}
roster_of = {r.split(" | ")[0]: r for r in args["roster"]}

# ---------------------------------------------------------------- prior findings
# Carried verbatim from notes/triage-2026-08-26-…md. These are SETTLED — an agent that
# re-derives one has spent budget for nothing; one that contradicts one must say so
# explicitly with new evidence.
PRIOR: dict[str, list[str]] = {
    "P4780": ["NAME DEFECT (MZ's lane — RECORD, never repair): this row's Chinese name cell "
              "holds P4783's 上高支线. Do NOT search on the Chinese name."],
    "P4783": ["Its Chinese name currently sits on P4780. Search '田南-上高支线'."],
    "P4788": ["SETTLED 2026-08-26: `FuelSource` names WEP3 (西气东输三线), not Sichuan–Shanghai — "
              "sourced to the operator's own emergency plan.",
              "SETTLED: the redraw anchors staged on 08-26 were DMS read as decimal. Correct "
              "decimals: Xinfeng 114.82255/25.43558, Ruijin 116.00923/25.94623 (the staged "
              "Xinfeng point was 38.7 km off). Do not re-derive; do not re-stage the bad ones.",
              "OPEN: sheet length 340.30 km vs 131.8 km between its own terminals. Length AND "
              "route both open — this is a __VALIDITY__ question, not a fill.",
              "Its name cell holds a chopped fragment of one multi-segment string (with P4789)."],
    "P4789": ["Its name cell holds a chopped fragment of one multi-segment string (with P4788)."],
    "P4777": ["SETTLED: this is the Phase I network PARENT row (the wiki h3 'Phase I' is a "
              "container heading listing constituents, no field bullets). Do NOT recommend "
              "folding it into its segments. Its route-vs-sheet length ratio 0.07 is expected "
              "network granularity, NOT a finding.",
              "OPEN: where the 825.00 km figure comes from. The DRC plan says 870 km as-built."],
    "P4791": ["婺源 romanizes as **Wuyuan**. The wiki's 'Maoyuan' is wrong."],
    "P4778": ["OPEN: overlaps P5861 (WEP2 Xinyu Branch) — and P5861 is IN SCOPE this time, so "
              "this is now an adjudicable duplicate question, not just a flag. Use __REDUNDANCY__."],
    "P5861": ["OPEN: overlaps P4778 (see that row). __REDUNDANCY__ between the two."],
    "P4782": ["Recon: GulfPub matched this row to 'Cang-Zi Line' at composite 0.475 (yellow). "
              "ADJUDICATED FALSE POSITIVE 2026-08-26 — the two are ~1,240 km apart, route IoU 0.0. "
              "Do not re-open."],
    "P4931": ["RECON QUESTION (new this batch): GEM files this as 西气东输三线 (WEP3) but GulfPub "
              "matches it to 'West - East Pipeline II' at 0.685. Line identity is genuinely in "
              "question — adjudicate on sources, do not assume GulfPub is wrong."],
    "P4928": ["RECON QUESTION (new this batch): same as P4931 — GulfPub calls this "
              "'West - East Pipeline II' at 0.701 against GEM's WEP3."],
    "P4944": ["Its wiki section states length/diameter/capacity/start year with NO citations at "
              "all. Every number on that page is unsourced — treat none of it as evidence."],
    "P4946": ["Same as P4944: wiki section states values, cites nothing."],
    "P4657": ["NATIONAL TRUNK PARENT (川气东送一线), included because it transits Jiangxi. It has "
              "ZERO refs on every column. Its wiki page has no section matching 'Trunk line', so "
              "work page-level citations. Expect aggregate-vs-segment questions against P4649."],
    "P4934": ["NATIONAL TRUNK PARENT (WEP3 mainline, 7,378 km). ZERO refs on every column. Parent "
              "of P4931/P4928 — a spec sourced for the MAINLINE does not source a SECTION."],
    "P4947": ["NATIONAL TRUNK PARENT (WEP2 mainline, 9,102 km). ZERO refs on every column. Parent "
              "of the WEP2 branches in this batch — same aggregate-vs-segment rule."],
    "P5862": ["Route-vs-sheet length ratio 30.1x (sheet 18.45 km vs route 553.78 km, accuracy "
              "'medium'). One of the two rows v1 could source NOTHING for. Push hard."],
    "P5859": ["One of the two rows v1 could source NOTHING for. Push hard."],
    "P5866": ["Route-vs-sheet length ratio 6.43x — route accuracy is 'very low "
              "(straight line/schematic)', so the ROUTE is the weak side here, not necessarily "
              "the length."],
    "P5887": ["Route-vs-sheet length ratio 2.12x (accuracy 'medium')."],
    "P4784": ["Route-vs-sheet length ratio 1.87x (accuracy 'medium'). v1 flagged that its "
              "existing refs do not support their values — re-check that first."],
}
# Rows whose LengthKnown is blank on the sheet: a sourced length is a FILL, not a ref.
BLANK_LENGTH = ["P4776", "P4778", "P4780", "P4781", "P4782", "P5859"]

# ---------------------------------------------------------------- per-row assembly
owed_by_pid: dict[str, list] = collections.defaultdict(list)
sourced_by_pid: dict[str, list] = collections.defaultdict(list)
for r in store["resolutions"]:
    pid = r["project_id"]
    if r["class_out"] in ("UNRESOLVED", "DEAD_LINK"):
        owed_by_pid[pid].append({
            "ref_col": r["ref_col"], "value_cols": r["value_cols"], "values": r["values"],
            "primary_value": r.get("primary_value"), "current_ref": r.get("current_ref", ""),
            "class_in": r["class_out"],
            "tab": "operators_owners" if r["ref_col"] in ("Operator [ref]", "Owner [ref]") else None,
        })
    elif r["class_out"] == "REFS_ADDED":
        sourced_by_pid[pid].append({"ref_col": r["ref_col"], "values": r["values"],
                                    "refs": r.get("proposed_refs", []), "tier": r.get("tier"),
                                    "carried": True})
    elif r["class_out"] == "REVERIFIED":
        sourced_by_pid[pid].append({"ref_col": r["ref_col"], "values": r["values"],
                                    "refs": [r.get("current_ref", "")], "tier": "existing-live"})

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

pids = [u["project_id"] for u in wl["units"]]
pids = list(dict.fromkeys(pids))
seg_of, srow_of = {}, {}
for u in wl["units"]:
    seg_of.setdefault(u["project_id"], u.get("segment_name") or "")
    srow_of.setdefault(u["project_id"], u["sheet_row"])
wiki_of = {}
for u in wl["units"]:
    wiki_of.setdefault(u["project_id"], (u.get("wiki") or "").strip())

rows = []
for pid in pids:
    src = row_of.get(pid)
    rows.append({
        "project_id": pid,
        "sheet_row": srow_of[pid],
        "pipeline_name": str(src.get("PipelineName", "")) if src is not None else "",
        "segment_name": seg_of[pid],
        "chinese_name": str(src.get("OtherNames", "") or src.get("PipelineName", "")) if src is not None else "",
        "status": str(src.get("Status", "")) if src is not None else "",
        "wiki": wiki_of[pid],
        "roster": roster_of.get(pid, ""),
        "length_is_blank": pid in BLANK_LENGTH,
        "n_owed": len(owed_by_pid[pid]),
        "owed_ref_units": owed_by_pid[pid],
        "already_sourced": sourced_by_pid[pid],
        "wiki_attributions": attrib_by_pid[pid],
        "wiki_section_uncited": uncited.get(pid),
        "harvest_pool_live": sorted(set(pool_live[pid])),
        "harvest_pool_failed": pool_dead[pid],
        "prior_findings": PRIOR.get(pid, []),
    })

# Group by wiki page family so agents on one page share its documents, then pack by OWED
# UNITS rather than row count. Rows carrying 08-26 work owe almost nothing while the
# never-swept national trunks owe ~10 units each; chunking by row count alone gave one
# agent 2 units of work and another 41.
rows.sort(key=lambda r: (r["wiki"], r["project_id"]))
batches, cur, cur_owed = [], [], 0
for r in rows:
    if cur and (len(cur) >= BATCH_SIZE or cur_owed + r["n_owed"] > OWED_CAP):
        batches.append(cur); cur, cur_owed = [], 0
    cur.append(r); cur_owed += r["n_owed"]
if cur:
    batches.append(cur)

(HERE / "batches").mkdir(exist_ok=True)
(HERE / "shards").mkdir(exist_ok=True)
for i, b in enumerate(batches, 1):
    payload = {"batch": i, "n_batches": len(batches), "country": "China",
               "province": "Jiangxi", "commodity": "gas",
               "snapshot": wl["scope"]["csv"], "rows": b}
    (HERE / "batches" / f"batch_{i:02d}.json").write_text(
        json.dumps(payload, indent=1, ensure_ascii=False))

print(f"wrote {len(batches)} batch payloads to {HERE / 'batches'}")
tot_owed = sum(r["n_owed"] for r in rows)
print(f"  rows {len(rows)}  owed units {tot_owed}  carried/already-sourced "
      f"{sum(len(r['already_sourced']) for r in rows)}")
for i, b in enumerate(batches, 1):
    pg = collections.Counter(urlparse(r["wiki"]).path.split("/")[-1][:34] for r in b)
    print(f"  batch_{i:02d}: {len(b)} rows, {sum(r['n_owed'] for r in b):>3} owed, "
          f"{sum(len(r['harvest_pool_live']) for r in b):>3} live pool URLs | "
          f"{','.join(r['project_id'] for r in b)} | {'/'.join(pg)}")
