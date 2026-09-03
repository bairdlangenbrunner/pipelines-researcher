#!/usr/bin/env python3
"""Finish the two indeterminate tails of ia_probe_and_rescreen.py.

(a) 7 availability probes came back HTTP 429 — rate limiting, which is NOT evidence about the
    capture. Re-probe those with real backoff so each gets a determinate answer.
(b) 4 harvested citations are `web.archive.org/save/` addresses — the Save Page Now INSTRUCTION
    endpoint, never a snapshot, so url_verifier rejects them by design. Their ORIGINS were never
    screened; strip the wrapper and screen those as ordinary candidate sources.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from url_verifier import verify_many
from ia_probe_and_rescreen import available, origin_of

avail = json.load(open("ia_availability.json"))
res = json.load(open("harvest_rescreen.json"))

pending = [u for u, v in avail.items() if v.get("probe") == "error"]
print(f"=== (a) re-probing {len(pending)} rate-limited URLs with backoff")
for u in pending:
    for attempt, wait in enumerate((0, 8, 20, 45), start=1):
        if wait:
            time.sleep(wait)
        a = available(u)
        if a.get("probe") != "error":
            break
        print(f"    attempt {attempt}: {a.get('detail')}")
    avail[u] = {"klass": avail[u]["klass"], **a}
    note = a.get("timestamp") or a.get("detail") or ""
    print(f"  {a['probe']:15s} {note:16s} {u[:70]}")
Path("ia_availability.json").write_text(json.dumps(avail, ensure_ascii=False, indent=2))
n = sum(1 for v in avail.values() if v["probe"] == "capture_exists")
bad = sum(1 for v in avail.values() if v["probe"] == "error")
print(f"  -> {n}/{len(avail)} have a capture; {bad} still indeterminate")

save_wrapped = {u: origin_of(u) for u, r in res.items()
                if "web.archive.org/save/" in u}
print(f"\n=== (b) screening {len(save_wrapped)} origins hidden behind /save/ wrappers")
sres = verify_many(list(save_wrapped.values()), timeout=25)
for wrapper, org in save_wrapped.items():
    r = sres[org]
    print(f"  {str(r.get('status')):>5}  {r.get('reason','')[:38]:38} {org[:72]}")
Path("save_wrapper_origins.json").write_text(
    json.dumps({"wrapper_to_origin": save_wrapped, "checks": sres}, ensure_ascii=False, indent=2))
live = [o for o, r in sres.items() if r.get("status") == 200]
print(f"  -> {len(live)}/{len(sres)} origins live")
print("updated ia_availability.json; wrote save_wrapper_origins.json")
