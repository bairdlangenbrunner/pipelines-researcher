#!/usr/bin/env python3
"""Screen the wiki-harvested citation pool for reachability (no name/value check -- that is
the agent's read). Writes harvest_urls.json {url: [pids]}, harvest_screen.json
[{ok,status,reason,url,project_ids}], spn_recovered_origins.json for the Save-Page-Now
citation form (the wiki cites `web.archive.org/save/<origin>`, which is an instruction, not a
snapshot -- see v2's FINDING-spn-citation-form.md; the ORIGIN is what gets screened)."""
from __future__ import annotations
import collections, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "scripts"))
from url_verifier import verify_many, GEM_HOSTS  # noqa: E402

cit = json.loads((HERE / "wiki_citations.json").read_text())
urls: dict[str, set] = collections.defaultdict(set)
spn: dict[str, dict] = {}
for pid, pg in cit["pages"].items():
    for c in pg.get("citations", []) or []:
        u = (c.get("url") or "").strip()
        if not u.startswith("http") or any(h in u.lower() for h in GEM_HOSTS):
            continue
        m = re.match(r"https?://web\.archive\.org/save/(https?://.*)$", u)
        if m:
            o = m.group(1)
            spn.setdefault(o, {"spn": u, "origin": o, "project_ids": set()})["project_ids"].add(pid)
            urls[o].add(pid)
            continue
        urls[u].add(pid)
res = verify_many(sorted(urls), max_workers=6, timeout=25)
screen = [{"ok": bool(r.get("ok")), "status": r.get("status"), "reason": r.get("reason", ""),
           "url": u, "project_ids": sorted(urls[u])} for u, r in res.items()]
(HERE / "harvest_urls.json").write_text(json.dumps({u: sorted(p) for u, p in sorted(urls.items())}, indent=1, ensure_ascii=False))
(HERE / "harvest_screen.json").write_text(json.dumps(screen, indent=1, ensure_ascii=False))
(HERE / "spn_recovered_origins.json").write_text(json.dumps(
    [{**s, "project_ids": sorted(s["project_ids"]), **{k: res[s["origin"]].get(k) for k in ("ok", "status", "reason")}}
     for s in spn.values()], indent=1, ensure_ascii=False))
live = sum(1 for s in screen if s["ok"]); dead = sum(1 for s in screen if s["status"] in (404, 410))
print(f"pool {len(screen)} URLs: live {live} / failed {len(screen)-live} / confirmed 404-410 {dead}; SPN origins {len(spn)}")
hosts = collections.Counter()
for s in screen:
    if not s["ok"]:
        hosts[(re.sub(r"^https?://([^/]+).*", r"\1", s["url"]), s["status"], s["reason"][:50])] += 1
for k, n in hosts.most_common(40):
    print(f"  {n:3d} {k}")
