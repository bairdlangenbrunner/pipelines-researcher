"""P8315 (Crossroads expansion): route moved to P0172 on 2026-11-05, so set the row back to
Not mapped / no route. Authorized by Baird 2026-11-05. Plan by default; --apply writes."""
import sys, csv, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
import pandas as pd
import apply_route_candidates as A

PID, TAB = "P8315", A.TABS["gas"]
SNAP = "data/GGIT_gas_snapshot_20261105.csv"
NOTE = ("Scope is loops and extensions on the existing line plus added compression. No route has been published. "
        "CB: no route for the expansion. The open season map trace that was here shows the existing line, so it was moved to P0172 on 2026-11-05.")
AFTER = {"RouteType": "Not mapped (but could be — route or endpoints are known)", "RouteAccuracy": "no route",
         "RouteNotes": NOTE, "RouteCreator": "", "Route [ref]": "", **A.stamp_values()}

hdr = pd.read_csv(SNAP, header=2, nrows=0).columns.tolist()
L = {c: A.a1(hdr.index(c)) for c in list(AFTER) + ["ProjectID"]}
d = pd.read_csv(SNAP, header=2, low_memory=False, keep_default_na=False, na_values=[])
row = int(d.index[d.ProjectID == PID][0]) + 4
cols = ["ProjectID"] + list(AFTER)
got = A.batch_get(TAB, [f"{L[c]}{row}" for c in cols], "FORMULA")
cur = {c: str((g[0] or [""])[0]) if g and g[0] else "" for c, g in zip(cols, got)}
assert cur["ProjectID"] == PID, f"row {row} holds {cur['ProjectID']!r}, not {PID}"
assert not any(v.startswith("=") for v in cur.values()), f"formula cell: {cur}"
assert cur["RouteAccuracy"] == "medium", f"sheet moved: {cur['RouteAccuracy']!r}"
plan = [{"pid": PID, "sheet_row": row, "before": {c: cur[c] for c in AFTER}, "after": AFTER}]
print(json.dumps(plan, indent=1, ensure_ascii=False))
bk = Path("notes/sheet-write-2026-11-05-united-states-gas-p8315-unroute.csv")
with bk.open("w", newline="") as f:
    w = csv.writer(f); w.writerow(["ProjectID", "SheetRow", "Column", "Before", "After"])
    for c in AFTER: w.writerow([PID, row, c, cur[c], AFTER[c]])
print("backup:", bk)
if "--apply" in sys.argv:
    A.apply_plan(plan, TAB, L)
