"""Orchestrator check: every owed_fill in a payload has a kind:FILL record in its shard, with value_col/proposed_value; Owner fills carry tab."""
import json, sys, glob, os
pids = sys.argv[1:] or [os.path.basename(p)[:-5] for p in glob.glob("shards/P*.json")]
for pid in pids:
    if not os.path.exists(f"shards/{pid}.json"): continue
    pay = json.load(open(f"batches/{pid}.json")); sh = json.load(open(f"shards/{pid}.json"))
    owed = {f["ref_col"] for f in pay.get("owed_fills", [])}
    fills = {r["ref_col"]: r for r in sh["resolutions"] if (r.get("kind") or "").upper() == "FILL"}
    missing = sorted(owed - set(fills)); extra = sorted(set(fills) - owed)
    bad = [c for c, r in fills.items() if "value_col" not in r or "proposed_value" not in r]
    notab = [c for c, r in fills.items() if c == "Owner [ref]" and r.get("tab") != "operators_owners"]
    novc = [r["ref_col"] for r in sh["resolutions"] if r.get("class_out") in ("REFS_ADDED","REVERIFIED") and not r.get("value_cols") and not r["ref_col"].startswith("__")]
    print(f"{pid}: owed {len(owed)} fills, FILL records {len(fills)}; missing={missing} extra={extra} no_valuecol/proposed={bad} owner_no_tab={notab} sourced_empty_value_cols={novc}")
