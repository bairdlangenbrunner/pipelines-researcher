#!/usr/bin/env python3
"""Plan the repair of numbers stored as TEXT on the live tracker tabs (Baird 2026-10-08).

Two cell families must hold numbers, never strings:
  * every *Month column (ProposalMonth, ConstructionMonth, StartMonth1, ...): 1-12, never "July",
    "Mar" or the string "11";
  * every Owner<N>% column: a fraction under a percent format (0.75), never the string "75.00%".
A RAW write of "75.00%" or "July" lands as text, which the percent-verification and aggregate
formulas cannot read. review_app/push.py now coerces both on the way in; this finds the old ones.

Only mechanical conversions are planned. A cell that is not a month name, a month number or a plain
percentage (a URL pasted into a month column, "up to 100%") is listed for a person and left alone.
Each row it changes gets LastUpdated stamped and keeps its Researcher (a type fix has no research
behind it, like a style-only write).

    python scripts/fix_text_numbers.py                       # plan -> work/fix_text_numbers_plan.json
    python review_app/push.py --apply work/fix_text_numbers_plan.json   # ASK BAIRD FIRST
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "review_app"))
import push  # noqa: E402

MONTH_COL = re.compile(r"Month")
PCT_COL = re.compile(r"^Owner\d+%$")


def month_number(v):
    """1-12 for a month name, abbreviation or number-as-text; None when it is not a month."""
    return push.month_number(v)


def pct_fraction(v):
    m = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*%+\s*", str(v))
    return round(float(m.group(1)) / 100, 10) if m else None


def scan(tab, tname):
    cells, odd = {}, []
    pid_i = tab.col["ProjectID"]
    for c, i in tab.col.items():
        kind = "month" if MONTH_COL.search(str(c)) else "pct" if PCT_COL.match(str(c)) else None
        if not kind:
            continue
        for n, r in enumerate(tab.rows, 1):
            if n <= tab.header_idx + 1 or i >= len(r):
                continue
            v = r[i]
            if not isinstance(v, str) or not v.strip() or v.startswith("="):
                continue
            pid = r[pid_i] if pid_i < len(r) else ""
            new = month_number(v) if kind == "month" else pct_fraction(v)
            if new is None:
                odd.append((tab.title, f"{push.a1(i)}{n}", pid, c, v))
            else:
                cells[(tname, n, c)] = {"before": v, "after": new, "pid": pid, "lines": []}
    return cells, odd


def main():
    tabs = {"tracker": push.Tab(*push.TABS[("tracker", "gas")]),
            "oil": push.Tab(*push.TABS[("tracker", "oil")]),
            "oo": push.Tab(push.OO_TITLE, push.OO_HEADER)}
    cells, odd = {}, []
    for tname, tab in tabs.items():
        c, o = scan(tab, tname)
        cells.update(c)
        odd += o
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
    for t, cell, pid, c, v in odd:
        print(f"  LEFT FOR A PERSON {t}!{cell} {pid} {c}: {str(v)[:90]!r}")
    out = ROOT / "work" / "fix_text_numbers_plan.json"
    out.write_text(json.dumps({"token": push.token(plan), "commodity": "gas", "plan": plan, "meta": {},
                               "stale": [], "concerns": []}, ensure_ascii=False, indent=1))
    print(f"{len(plan)} cells; plan written: {out}")


if __name__ == "__main__":
    main()
