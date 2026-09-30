#!/usr/bin/env python3
"""Re-run the carried name check for selected PIDs after name_forms.json changed (e.g. the
phase-parent 一期 forms). Updates staged_resolutions.json records (verifications name_*,
carried_rechecks, relevance_reread), shards/_carried_v2.json, carry_report.json.
    python3 recheck_relevance.py P4777 [P....]"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "scripts")); sys.path.insert(0, str(HERE))
import url_verifier
from url_verifier import verify_many
from names import all_forms, name_level
url_verifier.RESPONSE_CACHE = {}
pids = sys.argv[1:]
forms = json.loads((HERE / "name_forms.json").read_text())
store_p = HERE / "staged_resolutions.json"; store = json.loads(store_p.read_text())
shard_p = HERE / "shards" / "_carried_v2.json"; shard = json.loads(shard_p.read_text())
rep_p = HERE / "carry_report.json"; rep = json.loads(rep_p.read_text())

def relevance(pid, verifs):
    seg = forms.get(pid, {}).get("segment", [])
    named = [v for v in verifs if "name_found" in v]
    if not named: return "unchecked"
    if any(v.get("name_found") and (v.get("name_level") == "segment" or not seg) for v in named): return ""
    if any(v.get("name_found") for v in named): return "system-only"
    return "unnamed"

for pid in pids:
    recs = [r for r in store["resolutions"] if r["project_id"] == pid] + \
           [r for r in shard["resolutions"] if r["project_id"] == pid]
    urls = sorted({v["url"] for r in recs for v in (r.get("verifications") or []) if v.get("url")})
    res = verify_many(urls, name=all_forms(forms[pid]), max_workers=4)
    checks = {}
    for u, v in res.items():
        v = dict(v); v["name_level"] = name_level(v.get("name_matched"), forms[pid]); checks[u] = v
        print(f"  {pid} {v.get('ok')} name_found={v.get('name_found')} matched={v.get('name_matched')} level={v['name_level']} {u[:70]}")
    changed = 0
    for r in recs:
        for v in r.get("verifications") or []:
            c = checks.get(v.get("url"))
            if not c: continue
            if c.get("ok") or "name_found" in c:
                v["name_found"] = bool(c.get("name_found")); v["name_matched"] = c.get("name_matched"); v["name_level"] = c["name_level"]
                v.pop("name_recheck", None)
            else:
                v["name_recheck"] = f"unchecked: {c.get('status')} {c.get('reason','')[:80]}"
        for cr in r.get("carried_rechecks") or []:
            c = checks.get(cr.get("url"))
            if c:
                cr.update({k: c.get(k) for k in ("ok", "status", "name_found", "name_matched", "name_level", "reason")})
        if r.get("class_out") in ("REFS_ADDED", "REVERIFIED"):
            before = r.get("relevance_reread")
            rr = relevance(pid, r.get("verifications") or [])
            if rr: r["relevance_reread"] = rr
            else: r.pop("relevance_reread", None)
            if before != r.get("relevance_reread"): changed += 1
            for x in rep["records"]:
                if x["project_id"] == pid and x["ref_col"] == r["ref_col"]: x["relevance"] = rr
    for x in rep["checks"]:
        if x["project_id"] == pid and x["url"] in checks:
            x.update({k: checks[x["url"]].get(k) for k in ("ok", "status", "name_found", "name_matched", "name_level", "reason")})
    print(f"{pid}: {len(urls)} urls rechecked, {changed} record(s) changed relevance")
store_p.write_text(json.dumps(store, ensure_ascii=False, indent=1))
shard_p.write_text(json.dumps(shard, ensure_ascii=False, indent=1))
rep_p.write_text(json.dumps(rep, ensure_ascii=False, indent=1))
print("written")
