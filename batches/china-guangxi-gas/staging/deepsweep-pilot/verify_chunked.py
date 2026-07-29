#!/usr/bin/env python3
"""Resumable stand-in for build_ref_worklist --verify-existing, parallelized at the
unit level (the stock path is serial per unit and dead Chinese domains cost a 20s
timeout each). Each unit runs its own verify_many (per-unit any_of), 8 units at a
time; the worklist is checkpointed every 20 completions so a killed run resumes
where it left off (units with existing_ref_checks already filled are skipped)."""
import json
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from build_ref_worklist import _extract_urls, _numericish
from url_verifier import surface_forms, verify_many

WL = Path(__file__).parent / "worklist.json"
WORKERS = 8
CHECKPOINT = 20

wl = json.loads(WL.read_text())
todo = [u for u in wl["units"] if u["class"] == "HAS_REF" and not u["existing_ref_checks"]]
print(f"{len(todo)} HAS_REF units still unverified", flush=True)


def _one(u):
    urls = _extract_urls(u["current_ref"])
    if not urls:
        u["existing_ref_checks"] = []
        u["value_checked"] = False
        return u
    checked = _numericish(u["primary_value"])
    any_of = surface_forms(u["primary_value"]) if checked else None
    results = verify_many(urls, any_of=any_of)
    # existing_ref_checks is the resume marker — assign it LAST so a checkpoint
    # snapshot never captures a half-updated unit as done
    u["value_checked"] = checked
    u["existing_ref_checks"] = [
        {"url": url, **results.get(url, {"ok": False, "status": None, "reason": "not checked"})}
        for url in urls
    ]
    return u


write_lock = threading.Lock()
done = 0
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    for fut in as_completed([ex.submit(_one, u) for u in todo]):
        fut.result()
        done += 1
        if done % CHECKPOINT == 0 or done == len(todo):
            with write_lock:
                WL.write_text(json.dumps(wl, indent=2, ensure_ascii=False))
            print(f"verified {done}/{len(todo)}", flush=True)

dead = sum(1 for u in wl["units"] if u["class"] == "HAS_REF"
           and any(not c["ok"] for c in u["existing_ref_checks"]))
live = sum(1 for u in wl["units"] if u["class"] == "HAS_REF"
           and u["existing_ref_checks"] and all(c["ok"] for c in u["existing_ref_checks"]))
wl["scope"]["verify_existing"] = True
wl["summary"]["has_ref_all_live"] = live
wl["summary"]["has_ref_with_dead"] = dead
WL.write_text(json.dumps(wl, indent=2, ensure_ascii=False))
print(f"done: {live} all-live, {dead} with dead/missing link(s)", flush=True)
