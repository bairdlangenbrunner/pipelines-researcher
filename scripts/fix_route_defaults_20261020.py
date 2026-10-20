"""One-off (Baird 2026-10-20): P8091+ rows set to Unavailable, and BLANK RouteType/RouteAccuracy rows,
get RouteType = Not mapped + RouteAccuracy = no route (nonzero or unknown length), or Capacity expansion only
for a zero-length expansion. Plan by default; --apply writes (gws-gem-write, RAW, cell-scoped), backup + verify."""
import csv, json, re, sys
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "review_app")); sys.path.insert(0, str(ROOT / "scripts"))
import push  # noqa: E402
from push import Tab, stamp_values, a1, gws, SHEET_ID  # noqa: E402

NM = "Not mapped (but could be — route or endpoints are known)"
UN = "Unavailable (cannot find route)"
CE = "Capacity expansion only"
tab = Tab("Gas pipelines", 2)
c = tab.col
def cell(r, name):
    row = tab.rows[r - 1]; i = c[name]
    return row[i] if i < len(row) else ""
plan, rows = [], set()
for pid, rs in tab.by_pid.items():
    m = re.match(r"P(\d+)$", pid)
    if not m or len(rs) != 1: continue
    r, n = rs[0], int(m.group(1))
    rt, ra = cell(r, "RouteType"), cell(r, "RouteAccuracy")
    if not ((n >= 8091 and rt == UN) or rt == "" or (rt and ra == "")): continue
    if cell(r, "Status") == "N/A": continue
    try: L = float(str(cell(r, "LengthKnown")).strip() or "x")
    except ValueError: L = None
    want_rt = CE if (L == 0 and rt in ("", UN)) else (rt if rt and rt != UN else NM)
    if rt and rt not in ("", UN) and rt != want_rt: continue
    want_ra = "no route"
    if ra not in ("", "no route"):   # accuracy already set: leave it (never overwrite a tier)
        continue
    for col, old, new in (("RouteType", rt, want_rt), ("RouteAccuracy", ra, want_ra)):
        if old != new: plan.append(dict(pid=pid, row=r, col=col, before=old, after=new))
    rows.add((pid, r))
for pid, r in sorted(rows):
    for k, v in stamp_values().items():
        if str(cell(r, k)) != str(v): plan.append(dict(pid=pid, row=r, col=k, before=cell(r, k), after=v))
for p in plan:
    p["cell"] = f'{a1(c[p["col"]])}{p["row"]}'
bad = [p for p in plan if str(p["before"]).startswith("=")]
if bad: sys.exit(f"ABORT: formula cells {bad[:3]}")
print(len(rows), "rows,", len(plan), "cells")
from collections import Counter
print(Counter((p["col"], p["after"]) for p in plan if p["col"] != "LastUpdated"))
if "--apply" not in sys.argv: sys.exit(0)
stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
bk = ROOT / "notes" / f"sheet-write-{stamp}-route-defaults.csv"
with bk.open("x", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["tab", "column", "cell", "sheet_row", "ProjectID", "before", "after"])
    for p in plan: w.writerow(["Gas pipelines", p["col"], p["cell"], p["row"], p["pid"], p["before"], p["after"]])
print("backup:", bk)
data = [{"range": f"'Gas pipelines'!{p['cell']}", "majorDimension": "ROWS", "values": [[p["after"]]]} for p in plan]
for i in range(0, len(data), 100):
    resp = gws("gws-gem-write", "batchUpdate", "--params", json.dumps({"spreadsheetId": SHEET_ID}),
               "--json", json.dumps({"valueInputOption": "RAW", "data": data[i:i + 100]}))
    print("batchUpdate:", resp.get("totalUpdatedCells"), "cells")
