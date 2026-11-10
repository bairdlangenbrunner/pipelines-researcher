"""Write a small, Baird-authorized plan of Gas-tab cells. One authorization per run.
usage: python scripts/apply_cell_plan.py PLAN.json BACKUP.csv [--apply]
PLAN.json: {"tab": "Gas pipelines", "cells": [{"pid": "P4732", "column": "Wiki", "before": "...", "after": "..."}, ...]}
Reads the tab with FORMULA, finds each row by ProjectID, aborts on a formula cell or a cell that no longer holds
`before`, stamps Researcher = CB and LastUpdated = today serial on every touched row (CLAUDE.md hard requirements),
writes a before/after backup CSV, writes RAW cell-scoped ranges (only with --apply), re-reads and verifies."""
import csv, json, sys, os
from datetime import date, datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(__file__))
from apply_route_candidates import SHEET_ID, a1, gws, batch_get

plan = json.load(open(sys.argv[1]))
T = plan.get("tab", "Gas pipelines")
apply = "--apply" in sys.argv
body = gws("gws-gem", "get", "--params", json.dumps({"spreadsheetId": SHEET_ID, "range": f"'{T}'",
           "valueRenderOption": "FORMULA", "majorDimension": "ROWS"}))
rows = body["values"]
h = rows[2]
col = {c: i for i, c in reversed(list(enumerate(h)))}
pc = col["ProjectID"]
where = {}
for i, r in enumerate(rows[3:], start=4):
    if len(r) > pc and r[pc]:
        where.setdefault(r[pc], []).append(i)
def cell(r, c): return rows[r - 1][c] if len(rows[r - 1]) > c else ""
serial = (datetime.now(ZoneInfo("America/New_York")).date() - date(1899, 12, 30)).days
want, touched = {}, {}
for x in plan["cells"]:
    hits = where.get(x["pid"], [])
    assert len(hits) == 1, f"{x['pid']}: {len(hits)} rows"
    r, c = hits[0], col[x["column"]]
    now = cell(r, c)
    assert not str(now).startswith("="), f"formula in {x['column']} row {r}"
    assert str(now) == str(x["before"]), f"{x['pid']} {x['column']} is {now!r}, plan expected {x['before']!r}"
    want[(r, c)] = (x["pid"], x["column"], now, x["after"])
    touched[r] = x["pid"]
for r, pid in touched.items():
    for name, v in (("Researcher", "CB"), ("LastUpdated", serial)):
        c = col[name]
        if (r, c) not in want and cell(r, c) != v:
            assert not str(cell(r, c)).startswith("="), f"formula in {name} row {r}"
            want[(r, c)] = (pid, name, cell(r, c), v)
data = [{"range": f"'{T}'!{a1(c)}{r}", "values": [[v[3]]]} for (r, c), v in sorted(want.items()) if v[2] != v[3]]
with open(sys.argv[2], "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["tab", "cell", "ProjectID", "column", "before", "after"])
    for (r, c), (pid, name, b, a) in sorted(want.items()):
        if b != a:
            w.writerow([T, f"{a1(c)}{r}", pid, name, b, a])
print(len(data), "cells on", len(touched), "rows; backup", sys.argv[2])
if not apply:
    sys.exit("plan only; re-run with --apply to write")
for i in range(0, len(data), 100):
    resp = gws("gws-gem-write", "batchUpdate", "--params", json.dumps({"spreadsheetId": SHEET_ID}),
               "--json", json.dumps({"valueInputOption": "RAW", "data": data[i:i + 100]}))
    print("wrote", i + len(data[i:i + 100]), resp.get("totalUpdatedCells"))
got = batch_get(T, [d["range"].split("!")[1] for d in data], "UNFORMATTED_VALUE")
bad = [(d["range"], d["values"][0][0], g) for d, g in zip(data, got) if (g[0][0] if g and g[0] else None) != d["values"][0][0]]
print("VERIFY mismatches:", len(bad), bad[:5])
