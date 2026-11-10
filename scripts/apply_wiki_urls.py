"""Write the planned Wiki-column cells (plan from plan_wiki_urls.py). Baird-authorized per run.
usage: python scripts/apply_wiki_urls.py PLAN.json BACKUP.csv
Re-reads the target cells with FORMULA first (abort on any non-blank/formula cell), writes a before/after
backup CSV, RAW + cell-scoped ranges (Wiki, Researcher=CB, LastUpdated=today serial), re-reads and verifies."""
import csv, json, sys, os
from datetime import date, datetime
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "review_app"))
sys.path.insert(0, os.path.dirname(__file__))
from apply_route_candidates import SHEET_ID, a1, gws
T = "Gas pipelines"
plan = json.load(open(sys.argv[1]))["plan"]
body = gws("gws-gem", "get", "--params", json.dumps({"spreadsheetId": SHEET_ID, "range": f"'{T}'",
      "valueRenderOption": "FORMULA", "majorDimension": "ROWS"}))
rows = body["values"]; h = rows[2]; col = {c: i for i, c in reversed(list(enumerate(h)))}
wc, rc, lc, pc = col["Wiki"], col["Researcher"], col["LastUpdated"], col["ProjectID"]
def cell(r, c): return rows[r - 1][c] if len(rows[r - 1]) > c else ""
serial = (datetime.now(ZoneInfo("America/New_York")).date() - date(1899, 12, 30)).days
data, backup = [], []
for x in plan:
    r = x["row"]
    assert cell(r, pc) == x["pid"], f"row {r} is {cell(r, pc)} not {x['pid']}"
    assert cell(r, wc) == "", f"{x['pid']} Wiki not blank: {cell(r, wc)!r}"
    for c, name, v in ((wc, "Wiki", x["after"]), (rc, "Researcher", "CB"), (lc, "LastUpdated", serial)):
        before = cell(r, c)
        assert not str(before).startswith("="), f"formula in {name} row {r}"
        if before == v: continue
        data.append({"range": f"'{T}'!{a1(c)}{r}", "values": [[v]]})
        backup.append([x["pid"], r, name, before, v])
with open(sys.argv[2], "w", newline="") as f:
    w = csv.writer(f); w.writerow(["pid", "row", "column", "before", "after"]); w.writerows(backup)
print(len(data), "cells in", len(plan), "rows; backup", sys.argv[2])
for i in range(0, len(data), 100):
    resp = gws("gws-gem-write", "batchUpdate", "--params", json.dumps({"spreadsheetId": SHEET_ID}),
               "--json", json.dumps({"valueInputOption": "RAW", "data": data[i:i + 100]}))
    print("wrote", i + len(data[i:i + 100]), resp.get("totalUpdatedCells"))
from apply_route_candidates import batch_get
got = batch_get(T, [d["range"].split("!")[1] for d in data], "UNFORMATTED_VALUE")
bad = [(d["range"], d["values"][0][0], g) for d, g in zip(data, got) if (g[0][0] if g and g[0] else None) != d["values"][0][0]]
print("VERIFY mismatches:", bad[:5], len(bad))
