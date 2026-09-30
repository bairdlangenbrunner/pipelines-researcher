#!/usr/bin/env python3
"""Gather cross_row_leads from every agent shard, group by TARGET pid, re-verify each lead URL
with the target row's name forms, and write leads_by_target.json for the routing pass
(the orchestrator turns each lead into a record on the target row -- findings never
propagate across a fan-out by themselves).  python3 collect_leads.py [--no-verify]"""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "scripts")); sys.path.insert(0, str(HERE))
forms = json.loads((HERE / "name_forms.json").read_text())
leads = {}
for sh in sorted((HERE / "shards").glob("P*.json")):
    d = json.loads(sh.read_text())
    for L in d.get("cross_row_leads") or []:
        tgt = str(L.get("project_id", "")).strip()
        if not tgt:
            continue
        leads.setdefault(tgt, []).append(dict(L, from_shard=sh.stem))
if "--no-verify" not in sys.argv:
    import url_verifier
    from url_verifier import verify_many
    from names import all_forms, name_level
    url_verifier.RESPONSE_CACHE = {}
    for tgt, Ls in leads.items():
        urls = sorted({L["url"] for L in Ls if L.get("url")})
        if not urls or tgt not in forms:
            continue
        res = verify_many(urls, name=all_forms(forms[tgt]), max_workers=4)
        for L in Ls:
            v = res.get(L.get("url"))
            if v:
                v = dict(v); v["name_level"] = name_level(v.get("name_matched"), forms[tgt]); L["verification"] = v
(HERE / "leads_by_target.json").write_text(json.dumps(leads, ensure_ascii=False, indent=1))
n = sum(len(v) for v in leads.values())
print(f"{n} lead(s) for {len(leads)} target row(s) -> leads_by_target.json")
for tgt, Ls in sorted(leads.items()):
    print(f"\n== {tgt}  ({len(Ls)} lead(s); in scope: {tgt in forms})")
    for L in Ls:
        v = L.get("verification") or {}
        print(f"  from {L['from_shard']}: ok={v.get('ok')} name_found={v.get('name_found')} level={v.get('name_level')}  {L.get('url','')[:80]}")
        print(f"     {str(L.get('facts',''))[:300]}")
