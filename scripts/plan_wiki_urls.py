"""Plan the Wiki-column writes for newly published gem.wiki pages (plan only; no sheet write).
usage: python scripts/plan_wiki_urls.py MANIFEST.json OUT_PLAN.json
Fills a BLANK Wiki cell only; a non-blank cell that differs is reported, never overwritten."""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "review_app"))
sys.path.insert(0, os.path.dirname(__file__))
from apply_route_candidates import SHEET_ID, a1, gws
man = json.load(open(sys.argv[1]))
body = gws("gws-gem", "get", "--params", json.dumps({"spreadsheetId": SHEET_ID, "range": "'Gas pipelines'",
      "valueRenderOption": "FORMULA", "majorDimension": "ROWS"}))
rows = body["values"]; h = rows[2]; col = {c: i for i, c in reversed(list(enumerate(h)))}
pc, wc = col["ProjectID"], col["Wiki"]
by = {}
for i, r in enumerate(rows):
    if i > 2 and len(r) > pc and r[pc]: by[r[pc]] = i
plan, report = [], []
for m in man:
    for pid in m["pids"]:
        i = by.get(pid)
        if i is None: report.append((pid, "NOT ON SHEET")); continue
        cur = rows[i][wc] if len(rows[i]) > wc else ""
        if cur == m["url"]: report.append((pid, "already set")); continue
        if cur: report.append((pid, f"NONBLANK DIFFERENT: {cur!r} vs {m['url']}")); continue
        plan.append({"pid": pid, "row": i + 1, "before": cur, "after": m["url"], "page": m["title"]})
json.dump({"plan": plan, "report": report}, open(sys.argv[2], "w"), indent=1)
print(len(plan), "to write;", len(report), "other:")
for r in report: print(" ", r)
