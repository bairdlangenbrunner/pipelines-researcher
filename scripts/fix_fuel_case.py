#!/usr/bin/env python3
"""Plan the repair of non-canonical `Fuel` spellings on the gas tracker tab (Baird 2026-10-14).

The gas tab takes `Gas`, `Hydrogen`, `Gas and hydrogen`, `Coke oven gas` (controlled_vocab.md). The
2026-10-05 discovery append wrote lowercase `gas` (and some `natural gas` / `Natural Gas`) before that
rule was enforced. Only a case-insensitive `gas` or `natural gas` is rewritten, to `Gas`; anything else
is left alone. Also (Baird 2026-10-14): an off-list `PipelineType` on the gas tab (lateral, expansion,
intrastate, interstate, pipeline, natural gas) becomes `transmission`, and `gathering and transmission`
becomes the sheet's own `both transmission and gathering`. A spelling fix has no research behind it, so each row gets LastUpdated only.

    python scripts/fix_fuel_case.py                              # plan -> work/fix_fuel_case_plan.json
    python review_app/push.py --apply work/fix_fuel_case_plan.json   # ASK BAIRD FIRST
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "review_app"))
import push  # noqa: E402

BAD = {"gas", "natural gas"}
PTYPE_OK = {"transmission", "gathering", "distribution", "both transmission and gathering",
            "both transmission and distribution", "both gathering and distribution", ""}
PTYPE_FIX = {"gathering and transmission": "both transmission and gathering"}


def main():
    tab = push.Tab(*push.TABS[("tracker", "gas")])
    tabs = {"tracker": tab}
    i, pid_i = tab.col["Fuel"], tab.col["ProjectID"]
    cells = {}
    for n, r in enumerate(tab.rows, 1):
        if n <= tab.header_idx + 1 or i >= len(r):
            continue
        v = r[i]
        if isinstance(v, str) and v.strip().lower() in BAD and v != "Gas":
            if v.startswith("="):
                sys.exit(f"ABORT: formula cell {tab.title}!{push.a1(i)}{n}")
            cells[("tracker", n, "Fuel")] = {"before": v, "after": "Gas", "pid": r[pid_i], "lines": []}
    ti = tab.col["PipelineType"]
    for n, r in enumerate(tab.rows, 1):
        if n <= tab.header_idx + 1 or ti >= len(r):
            continue
        v = r[ti]
        if isinstance(v, str) and v not in PTYPE_OK:
            if v.startswith("="):
                sys.exit(f"ABORT: formula cell {tab.title}!{push.a1(ti)}{n}")
            cells[("tracker", n, "PipelineType")] = {"before": v, "after": PTYPE_FIX.get(v.lower(), "transmission"),
                                                     "pid": r[pid_i], "lines": []}
    rows = {(t, n, d["pid"]) for (t, n, _), d in cells.items()}
    push.stamp_cells(rows, tabs, cells, style_only_rows=rows)        # LastUpdated only
    plan = []
    for (tname, row, c), d in sorted(cells.items(), key=lambda x: (x[0][1], tab.col[x[0][2]])):
        plan.append({"tab": tab.title, "tabkey": tname, "column": c, "cell": f"{push.a1(tab.col[c])}{row}",
                     "sheet_row": row, "ProjectID": d["pid"], "before": d["before"], "after": d["after"],
                     "lines": [], "replaces": False})
    push.show(plan, [], [])
    out = ROOT / "work" / "fix_fuel_case_plan.json"
    out.write_text(json.dumps({"token": push.token(plan), "commodity": "gas", "plan": plan, "meta": {},
                               "stale": [], "concerns": []}, ensure_ascii=False, indent=1))
    print(f"{len(plan)} cells; plan written: {out}")


if __name__ == "__main__":
    main()
