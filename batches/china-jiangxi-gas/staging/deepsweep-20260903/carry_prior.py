#!/usr/bin/env python3
"""Carry the v2 sweep (deepsweep-20260902) forward onto this run's fresh baseline -- v3 rules.

Plan (notes/plan-2026-09-03-china-jiangxi-gas-deepsweep-v3.md, "Carry-forward rule"):
  1. Re-key every v2 REFS_ADDED / REVERIFIED onto the fresh worklist (sheet_row from the NEW
     worklist, never the old record).
  2. Re-verify every carried URL WITH the pipeline's name forms so every carried verification
     gains `name_found` (+ `name_matched`, `name_level` segment|system). A carried ref that
     comes back name_found=false -- or matches only the SYSTEM name on a row that has a
     segment identity -- is a RELEVANCE RE-READ owed to the agent, not a carried pass. The
     record keeps class_out REFS_ADDED (relevance_qc caps it at merge if the agent does not
     rescue it) and is stamped `relevance_reread`.
  3. Carried FILLs go into THE STORE as class_in FILL with the fresh sheet_row.
  4. v2's sentinels (__VALIDITY__/__REDUNDANCY__) and status reviews (__STATUS__) are carried
     as a shard, `shards/_carried_v2.json`, so the normal chain (split -> merge -> harvester)
     stages them; a v3 agent shard for the same row supersedes a carried __STATUS__ (last
     shard wins, and `_` sorts before `P`).
  5. Confirmed 404/410 on re-verify demotes the unit to UNRESOLVED (dead URL kept in
     `carried_rechecks` so the agent re-researches with the old evidence in hand). An access
     failure never demotes.

Writes carry_report.json (per-record relevance outcome) for build_payloads.py.

    python carry_prior.py --from ../deepsweep-20260902 [--apply]
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "scripts"))
sys.path.insert(0, str(HERE))
import url_verifier  # noqa: E402
from url_verifier import verify_many, surface_forms  # noqa: E402
url_verifier.RESPONSE_CACHE = {}   # one download per document, name-checked per row
from names import all_forms, name_level  # noqa: E402

CARRY_FIELDS = ("proposed_refs", "verifications", "tier", "independent",
                "source_language", "researcher_notes")
NO_VALUE_CHECK = {"Status [ref]", "Fuel [ref]", "PipelineType [ref]", "Location [ref]",
                  "FuelSource [ref]", "Operator [ref]", "Owner [ref]"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    src_dir = Path(a.src)
    if not src_dir.is_absolute():
        src_dir = (HERE / src_dir).resolve()

    store_path = HERE / "staged_resolutions.json"
    store = json.loads(store_path.read_text())
    prior = json.loads((src_dir / "staged_resolutions.json").read_text())
    forms = json.loads((HERE / "name_forms.json").read_text())
    stamp = f"{src_dir.name}@{prior.get('meta', {}).get('generated', '2026-09-02')}"

    cur = {(r["project_id"], r["ref_col"]): r for r in store["resolutions"]}
    src = [r for r in prior["resolutions"] if r.get("class_out") in ("REFS_ADDED", "REVERIFIED")]

    # ---- one name-aware verification per (pid, url) -------------------------------------
    want: dict[str, set] = collections.defaultdict(set)
    for r in src:
        for u in r.get("proposed_refs", []) or []:
            want[r["project_id"]].add(u)
    # this run's own HAS_REF baseline (REVERIFIED / DEAD_LINK from the seed) gets the same read
    for (pid, rc), r in cur.items():
        if r.get("class_in") == "HAS_REF" and r.get("current_ref"):
            want[pid].add(r["current_ref"])
    checks: dict[tuple, dict] = {}
    for pid in sorted(want):
        res = verify_many(sorted(want[pid]), name=all_forms(forms.get(pid, {})), max_workers=4)
        for u, v in res.items():
            v = dict(v)
            v["name_level"] = name_level(v.get("name_matched"), forms.get(pid, {}))
            checks[(pid, u)] = v
        print(f"  {pid}: {sum(1 for v in res.values() if v.get('ok'))}/{len(res)} live+named",
              file=sys.stderr)

    def stamp_name(v: dict, pid: str, u: str) -> dict:
        c = checks.get((pid, u))
        if not c:
            return v
        v = dict(v)
        if "name_found" in c:
            v["name_found"] = bool(c["name_found"])
            v["name_matched"] = c.get("name_matched")
            v["name_level"] = c.get("name_level", "")
        else:
            v["name_recheck"] = f"unchecked: {c.get('status')} {c.get('reason', '')[:80]}"
        return v

    def relevance(pid: str, verifs: list) -> str:
        """'' (fine) | 'unnamed' | 'system-only' | 'unchecked'."""
        seg = forms.get(pid, {}).get("segment", [])
        named = [v for v in verifs if "name_found" in v]
        if not named:
            return "unchecked"
        if any(v.get("name_found") and (v.get("name_level") == "segment" or not seg)
               for v in named):
            return ""
        if any(v.get("name_found") for v in named):
            return "system-only"
        return "unnamed"

    carried, drift, gone, dead, fills = [], [], [], [], []
    report = []
    for r in src:
        pid, rc = r["project_id"], r["ref_col"]
        key = (pid, rc)
        tgt = cur.get(key)
        if tgt is None:
            if r.get("class_in") == "FILL":
                rec = dict(r)
                sib = next((v for k, v in cur.items() if k[0] == pid), None)
                if sib:
                    rec["sheet_row"] = sib.get("sheet_row", rec.get("sheet_row"))
                rec["kind"] = "FILL"
                rec["carried_from"] = stamp
                rec["verifications"] = [stamp_name(v, pid, v.get("url", ""))
                                        for v in rec.get("verifications", []) or []]
                rr = relevance(pid, rec["verifications"])
                if rr:
                    rec["relevance_reread"] = rr
                cur[key] = rec
                fills.append(rec)
                report.append({"project_id": pid, "ref_col": rc, "lane": "FILL",
                               "relevance": rr, "class_out": rec["class_out"]})
            else:
                gone.append(key)
            continue
        if r.get("class_out") == "REVERIFIED":
            # The seed already re-verified the existing ref for liveness; add v2's notes
            # and the name-aware read of the existing URL.
            rec = dict(tgt)
            if r.get("researcher_notes"):
                rec["researcher_notes"] = r["researcher_notes"]
            rec["carried_from"] = stamp
            cur[key] = rec
            carried.append(key)
            continue
        if (r.get("values") or {}) != (tgt.get("values") or {}):
            drift.append({"key": key, "then": r.get("values"), "now": tgt.get("values")})
        rec = dict(tgt)
        for f in CARRY_FIELDS:
            if f in r:
                rec[f] = r[f]
        rec["verifications"] = [stamp_name(v, pid, v.get("url", ""))
                                for v in rec.get("verifications", []) or []]
        rechecks = [dict(checks[(pid, u)], url=u) for u in r.get("proposed_refs", [])
                    if (pid, u) in checks]
        confirmed_404 = [c for c in rechecks if c.get("status") in (404, 410)]
        rec["class_out"] = "REFS_ADDED"
        rec["carried_from"] = stamp
        rec["carried_rechecks"] = [{k: c.get(k) for k in ("url", "ok", "status", "name_found",
                                                          "name_matched", "name_level", "reason")}
                                   for c in rechecks]
        if confirmed_404:
            live = [u for u in r.get("proposed_refs", []) if u not in {c["url"] for c in confirmed_404}]
            if live:
                rec["proposed_refs"] = live
                rec["carried_needs_recheck"] = f"dropped confirmed-404 ref(s): {[c['url'] for c in confirmed_404]}"
            else:
                rec["class_out"] = "UNRESOLVED"
                rec["carried_needs_recheck"] = "confirmed 404/410 on re-verify (no live ref left)"
            dead.append({"key": key, "urls": [c["url"] for c in confirmed_404],
                         "demoted": not live})
        if any(d["key"] == key for d in drift):
            rec["carried_needs_recheck"] = (rec.get("carried_needs_recheck", "") +
                                            "; sheet value changed since the ref was verified").strip("; ")
        rr = relevance(pid, rec["verifications"]) if rec["class_out"] == "REFS_ADDED" else ""
        if rr:
            rec["relevance_reread"] = rr
        cur[key] = rec
        carried.append(key)
        report.append({"project_id": pid, "ref_col": rc, "lane": "REF", "relevance": rr,
                       "class_out": rec["class_out"],
                       "dead": [c["url"] for c in confirmed_404]})

    # ---- this run's own HAS_REF units: name-aware read of the existing ref ---------------
    has_ref_reread = []
    for (pid, rc), rec in cur.items():
        if rec.get("class_in") != "HAS_REF" or not rec.get("current_ref"):
            continue
        u = rec["current_ref"]
        c = checks.get((pid, u))
        if not c:
            continue
        v = {"url": u, "ok": bool(c.get("ok")) or c.get("status") == 200,
             "status": c.get("status"), "contains_value": None,
             "note": f"seed re-verify + name read: {c.get('reason', '')[:120]}"}
        v = stamp_name(v, pid, u)
        rec["verifications"] = [v]
        rr = relevance(pid, [v]) if rec.get("class_out") == "REVERIFIED" else ""
        if rr:
            rec["relevance_reread"] = rr
            has_ref_reread.append((pid, rc, rr))
        report.append({"project_id": pid, "ref_col": rc, "lane": "HAS_REF", "relevance": rr,
                       "class_out": rec["class_out"]})

    # ---- sentinels + status reviews -> a carried shard -----------------------------------
    sent = []
    for f in sorted((src_dir / "ref_shards").glob("P*.json")):
        for r in json.loads(f.read_text()).get("resolutions", []):
            if (r.get("ref_col") or "").startswith("__"):
                r = dict(r); r["carried_from"] = stamp
                r["researcher_notes"] = f"[carried from v2 {stamp}] " + (r.get("researcher_notes") or "")
                sent.append(r)
    n_sent = len(sent)
    for f in sorted((src_dir / "rows").glob("P*.json")):
        d = json.loads(f.read_text())
        for s in d.get("status_reviews", []) or []:
            sent.append({"project_id": d["project_id"], "sheet_row": s.get("sheet_row"),
                         "ref_col": "__STATUS__", "verdict": s.get("verdict"),
                         "current_status": s.get("current_status"),
                         "proposed_status": s.get("proposed_status"),
                         "proposed_changes": s.get("proposed_changes") or {},
                         "evidence_date": s.get("evidence_date"),
                         "staleness_rule": s.get("staleness_rule"),
                         "proposed_refs": s.get("proposed_refs") or [],
                         "verifications": s.get("verifications") or [],
                         "class_out": "UNRESOLVED", "tier": s.get("tier") or "",
                         "independent": bool(s.get("independent")),
                         "source_language": s.get("source_language", "en"),
                         "researcher_notes": f"[carried from v2 {stamp}] " + (s.get("researcher_notes") or ""),
                         "carried_from": stamp})
    n_status = len(sent) - n_sent
    for rec in fills:
        sent.append({**rec, "kind": "FILL", "value_col": rec.get("primary_value_col") or rec.get("value_col", ""),
                     "proposed_value": rec.get("primary_value") or rec.get("proposed_value", "")})

    rel = collections.Counter(x["relevance"] or "ok" for x in report if x["lane"] == "REF")
    print(f"prior REFS_ADDED+REVERIFIED: {len(src)}  carried: {len(carried)}  fills: {len(fills)}  gone: {len(gone)}")
    print(f"  name-aware rechecks: {len(checks)} (pid,url) pairs; "
          f"live: {sum(1 for c in checks.values() if c.get('status') == 200)}")
    print(f"  relevance of carried REFS_ADDED: {dict(rel)}")
    print(f"  confirmed 404/410: {len(dead)} unit(s), demoted {sum(1 for d in dead if d['demoted'])}")
    for d in dead[:30]:
        print(f"      {d['key'][0]} {d['key'][1]} {'DEMOTED' if d['demoted'] else 'ref dropped'} {d['urls']}")
    print(f"  value drift: {len(drift)} {drift[:5]}")
    print(f"  HAS_REF units owing a relevance re-read: {len(has_ref_reread)} {has_ref_reread}")
    print(f"  carried shard: {n_sent} sentinel(s) + {n_status} status review(s) + {len(fills)} fill(s)")
    for g in gone:
        print(f"      gone: {g}")
    (HERE / "carry_report.json").write_text(json.dumps(
        {"checks": [{"project_id": p, "url": u, **c} for (p, u), c in checks.items()],
         "records": report}, indent=1, ensure_ascii=False))
    if not a.apply:
        print("(dry run; carry_report.json written)"); return
    order = {(r["project_id"], r["ref_col"]): i for i, r in enumerate(store["resolutions"])}
    store["resolutions"] = sorted(cur.values(), key=lambda r: (order.get((r["project_id"], r["ref_col"]), 10**6), r["project_id"], r["ref_col"]))
    store.setdefault("meta", {})["carried_from"] = str(src_dir)
    store["meta"]["carried_units"] = len(carried)
    store_path.write_text(json.dumps(store, indent=1, ensure_ascii=False))
    (HERE / "shards").mkdir(exist_ok=True)
    (HERE / "shards" / "_carried_v2.json").write_text(json.dumps(
        {"batch": 0, "harvest_opened": 0, "carried_from": stamp, "resolutions": sent,
         "cross_row_leads": []}, indent=1, ensure_ascii=False))
    print(f"wrote {store_path} ({len(store['resolutions'])} records), shards/_carried_v2.json, carry_report.json")


if __name__ == "__main__":
    main()
