#!/usr/bin/env python3
"""List every harvested wiki citation that could not be opened, for a person to work through.

    python scripts/export_unreadable_citations.py --staging <store> [--out unreadable_citations.csv]

The shard ledgers are the record of truth: every `wiki_citations_read` entry whose outcome is
`dead` or `blocked`, with the rungs the agent tried. A pre-pass candidate in `dead`/`blocked` that no
shard has logged at all is listed too (one an agent read another way is not). Each row carries the wiki sentence the citation supports, the sheet
units it was attributed to, and, when `recheck_full_ladder.json` exists (the post-pass full-ladder
re-check), what that re-check found. Sorted so one host's links sit together.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from urllib.parse import urlsplit


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    pre = json.loads((a.staging / "wiki_prepass.json").read_text())
    cands = {(c["project_id"], c["url"]): c for c in pre["candidates"]}
    rpath = a.staging / "recheck_full_ladder.json"
    recheck = json.loads(rpath.read_text()) if rpath.exists() else {}

    failed, logged = {}, set()
    for f in sorted((a.staging / "rows").glob("*.json")):
        shard = json.loads(f.read_text())
        for w in shard.get("wiki_citations_read") or []:
            logged.add((shard["project_id"], w["url"]))
            if w.get("outcome") in ("dead", "blocked"):
                failed[(shard["project_id"], w["url"])] = w
    for key, c in cands.items():
        if c["bucket"] in ("dead", "blocked") and key not in logged:
            failed[key] = c.get("ledger") or {"url": c["url"], "outcome": c["bucket"]}

    rows = []
    for (pid, url), w in failed.items():
        c = cands.get((pid, url)) or {}
        v = c.get("verify") or {}
        r = recheck.get(url) or {}
        conf = r.get("confirm") or {}
        if r:
            rc = r["result"] if r["result"] == "failed" else f"{r['result']} loaded but not the document: {conf.get('head', '')[:120]}"
        else:
            rc = ""
        rows.append({
            "ProjectID": pid,
            "host": (urlsplit(url).hostname or "").lower(),
            "url": url,
            "outcome": w.get("outcome") or c.get("bucket") or "",
            "http_status": v.get("status") or "",
            "agent_note": (w.get("note") or v.get("reason") or "")[:300],
            "tried": "; ".join(w.get("tried") or [])[:300],
            "wayback_state": c.get("wayback_state") or "not recorded",
            "full_ladder_recheck": rc,
            "link_text": c.get("link_text") or "",
            "wiki_context": (c.get("context") or "")[:300],
            "attributed_units": "; ".join(f"{u['ref_col']} = {u.get('wiki_value') or ''}".strip(" =") for u in c.get("units") or []),
            "my_notes": "",
        })
    rows.sort(key=lambda r: (r["host"], r["ProjectID"], r["url"]))
    out = a.out or a.staging / "unreadable_citations.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["ProjectID"])
        w.writeheader()
        w.writerows(rows)
    hosts = {}
    for r in rows:
        hosts[r["host"]] = hosts.get(r["host"], 0) + 1
    print(f"{len(rows)} unreadable citations ({len({r['url'] for r in rows})} distinct URLs) -> {out}")
    for h, n in sorted(hosts.items(), key=lambda x: -x[1])[:12]:
        print(f"  {n:4d}  {h}")


if __name__ == "__main__":
    main()
