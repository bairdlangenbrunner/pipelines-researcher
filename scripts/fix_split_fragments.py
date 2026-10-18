#!/usr/bin/env python3
"""Plan the repair of `[ref]` URLs that an old push split inside a text fragment (2026-10-18).

review_app/push.py used to split a `[ref]` cell on every comma and join the pieces back with ", ".
A URL with a text fragment holding a comma (`#:~:text=...utilize%20existing,Waha%20residue...`) came
back as `existing, Waha`, and the space breaks the link. push.py now splits only where the next URL
starts (`split_urls`); this finds the cells it already damaged and plans the space out again.

Only a comma inside a `#:~:text=` fragment that is followed by whitespace and NOT by a new URL is
mended. Each row it changes gets LastUpdated stamped and keeps its Researcher (a link repair has no
research behind it, like a style-only write).

    python scripts/fix_split_fragments.py                         # plan -> work/fix_split_fragments_plan.json
    python review_app/push.py --apply work/fix_split_fragments_plan.json   # ASK BAIRD FIRST
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "review_app"))
import push  # noqa: E402

SPLIT = re.compile(r"(#:~:text=\S*?,)\s+(?!https?://)(?=\S)")


def mend(v):
    while True:
        new = SPLIT.sub(r"\1", v)
        if new == v:
            return v
        v = new


def scan(tab, tname):
    cells = {}
    pid_i = tab.col["ProjectID"]
    for c, i in tab.col.items():
        if not str(c).endswith("[ref]"):
            continue
        for n, r in enumerate(tab.rows, 1):
            if n <= tab.header_idx + 1 or i >= len(r):
                continue
            v = r[i]
            if not isinstance(v, str) or v.startswith("=") or "#:~:text=" not in v:
                continue
            new = mend(v)
            if new != v:
                cells[(tname, n, c)] = {"before": v, "after": new, "pid": r[pid_i] if pid_i < len(r) else "",
                                        "lines": []}
    return cells


def main():
    tabs = {"tracker": push.Tab(*push.TABS[("tracker", "gas")]),
            "oil": push.Tab(*push.TABS[("tracker", "oil")]),
            "oo": push.Tab(push.OO_TITLE, push.OO_HEADER)}
    cells = {}
    for tname, tab in tabs.items():
        cells.update(scan(tab, tname))
    rows = {(t, n, d["pid"]) for (t, n, _), d in cells.items()}
    push.stamp_cells(rows, tabs, cells, style_only_rows=rows)        # LastUpdated only
    plan = []
    for (tname, row, c), d in sorted(cells.items(), key=lambda x: (x[0][0], x[0][1], tabs[x[0][0]].col[x[0][2]])):
        tab = tabs[tname]
        if str(d["before"]).startswith("="):
            sys.exit(f"ABORT: formula cell {tab.title}!{push.a1(tab.col[c])}{row}")
        plan.append({"tab": tab.title, "tabkey": tname, "column": c, "cell": f"{push.a1(tab.col[c])}{row}",
                     "sheet_row": row, "ProjectID": d["pid"], "before": d["before"], "after": d["after"],
                     "lines": [], "replaces": False})
    push.show(plan, [], [])
    out = ROOT / "work" / "fix_split_fragments_plan.json"
    out.write_text(json.dumps({"token": push.token(plan), "commodity": "gas", "plan": plan, "meta": {},
                               "stale": [], "concerns": []}, ensure_ascii=False, indent=1))
    print(f"{len(plan)} cells; plan written: {out}")


if __name__ == "__main__":
    main()
