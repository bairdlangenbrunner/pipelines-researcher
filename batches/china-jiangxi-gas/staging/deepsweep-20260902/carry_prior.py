#!/usr/bin/env python3
"""Fold a superseded sweep's REFS_ADDED records into this run's fresh baseline.

Why this exists: `seed_resolutions_from_worklist.py` seeds from the WORKLIST only — it
knows nothing about a prior pass — and refuses to clobber an existing store. Re-running
a scope from scratch would therefore throw away work that is still good, while blindly
copying the old file forward would carry three kinds of rot:

  1. STALE LOCATORS. The GGIT gas tab re-sorts. Between 2026-08-26 and 2026-09-02 all 18
     shared Jiangxi PIDs moved by -2 rows. Every carried record takes its `sheet_row`,
     `values` and `current_ref` from the NEW worklist, never from the old record.
  2. STALE VALUES. If the sheet's value changed under a carried ref, the ref was verified
     against a value that is no longer there — flagged `value_drift`, never carried silently.
  3. STALE URLS. Every carried URL is re-verified (hard requirement: even URLs that worked
     in a prior batch). A confirmed 404/410 demotes the record to the agent's worklist —
     it is NOT dropped here, because only a human/agent read decides a ref is gone, and an
     access failure (403/timeout/WAF) is never a deletion.

Carried records are stamped `carried_from` so the workbook can show preserved work
distinctly from new work.

    python carry_prior.py --from ../deepsweep/ [--apply]
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from url_verifier import verify_url  # noqa: E402

HERE = Path(__file__).resolve().parent
CARRY_FIELDS = ("proposed_refs", "verifications", "tier", "independent",
                "source_language", "researcher_notes")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", required=True, help="superseded staging dir")
    ap.add_argument("--apply", action="store_true", help="write; default is a dry-run plan")
    a = ap.parse_args()

    store_path = HERE / "staged_resolutions.json"
    store = json.loads(store_path.read_text())
    prior = json.loads((Path(a.src) / "staged_resolutions.json").read_text())

    cur = {(r["project_id"], r["ref_col"]): r for r in store["resolutions"]}
    src = [r for r in prior["resolutions"] if r.get("class_out") == "REFS_ADDED"]

    # Re-verify every distinct carried URL once.
    urls = sorted({u for r in src for u in r.get("proposed_refs", [])})
    def go(u):
        try:
            return u, verify_url(u)
        except Exception as e:                                    # noqa: BLE001
            return u, {"ok": False, "status": None, "reason": f"exception: {e}"}
    with ThreadPoolExecutor(max_workers=6) as ex:
        checks = dict(ex.map(go, urls))

    carried, drift, gone, dead, fills = [], [], [], [], []
    for r in src:
        key = (r["project_id"], r["ref_col"])
        tgt = cur.get(key)
        if tgt is None:
            if r.get("class_in") == "FILL":
                # A FILL proposes a value for a cell the sheet leaves BLANK, so the
                # worklist (which only owes refs where a value exists) can never hold it --
                # and that same blankness is the proof the fill is still owed.
                #
                # It must go into THE STORE, not into a side file. carried_fills.json was
                # written by this script and read by nobody: build_ref_workbook takes
                # pending_fills from an ACTIONS packet (a §6 handoff), so on a standalone
                # deep-sweep build a carried fill reached no tab at all. That silently lost
                # the v1 Jiangxi sweep's one real fill (P4788 Pressure = 6.30 MPa, sourced).
                # The store IS the fills lane: build_ref_workbook's fill_res selects on
                # class_in == "FILL".
                rec = dict(r)
                sib = next((v for k, v in cur.items() if k[0] == r["project_id"]), None)
                if sib:
                    # Fresh locator, never the prior run's -- the tab re-sorts between pulls.
                    rec["sheet_row"] = sib.get("sheet_row", rec.get("sheet_row"))
                rec["kind"] = "FILL"
                rec["carried_from"] = (f"{Path(a.src).name}@"
                                       f"{prior.get('meta', {}).get('generated', '?')}")
                cur[key] = rec
                fills.append(r)
            else:
                # The unit is genuinely gone: the row's value was cleared, or the column moved.
                gone.append(key)
            continue
        # A carried ref was verified against the value the sheet held THEN.
        if {k: v for k, v in (r.get("values") or {}).items()} != (tgt.get("values") or {}):
            drift.append({"key": key, "then": r.get("values"), "now": tgt.get("values")})
        rechecks = [dict(checks[u], url=u) for u in r.get("proposed_refs", [])]
        confirmed_404 = [c for c in rechecks if c.get("status") in (404, 410)]
        rec = dict(tgt)
        for f in CARRY_FIELDS:
            if f in r:
                rec[f] = r[f]
        rec["class_out"] = "REFS_ADDED"
        rec["carried_from"] = f"{Path(a.src).name}@{prior.get('meta', {}).get('generated', '?')}"
        rec["carried_rechecks"] = rechecks
        if confirmed_404:
            # Demote, don't drop. The agent re-researches the cell with the dead URL and
            # the original evidence note both in hand.
            rec["class_out"] = "UNRESOLVED"
            rec["carried_needs_recheck"] = "confirmed 404/410 on re-verify"
            dead.append({"key": key, "urls": [c["url"] for c in confirmed_404]})
        if any(k == key for k in [d["key"] for d in drift]):
            rec["carried_needs_recheck"] = ((rec.get("carried_needs_recheck", "") + "; ")
                                            + "sheet value changed since the ref was verified").strip("; ")
        cur[key] = rec
        carried.append(key)

    print(f"prior REFS_ADDED: {len(src)}")
    print(f"  carried onto this run's units: {len(carried)}")
    print(f"  URL re-verify: {sum(1 for c in checks.values() if c.get('ok'))}/{len(checks)} live")
    print(f"  demoted to UNRESOLVED (confirmed 404/410): {len(dead)}")
    for d in dead:
        print(f"      {d['key'][0]} {d['key'][1]}  {d['urls']}")
    print(f"  VALUE DRIFT since 08-26: {len(drift)}")
    for d in drift[:12]:
        print(f"      {d['key'][0]} {d['key'][1]}: {d['then']} -> {d['now']}")
    print(f"  prior FILLS (blank cell — kept in the store as class_in=FILL): {len(fills)}")
    for f in fills:
        print(f"      {f['project_id']} {f['ref_col']}  {f.get('values')}")
    print(f"  unit no longer in scope/worklist: {len(gone)}")
    for g in gone:
        print(f"      {g[0]} {g[1]}")

    if not a.apply:
        print("\n(dry run — pass --apply to write)")
        return
    store["resolutions"] = [cur[k] for k in
                            sorted(cur, key=lambda k: (store_path and 0, k[0], k[1]))]
    order = {(r["project_id"], r["ref_col"]): i
             for i, r in enumerate(json.loads(store_path.read_text())["resolutions"])}
    store["resolutions"].sort(key=lambda r: order.get((r["project_id"], r["ref_col"]), 10**6))
    if fills:
        (HERE / "carried_fills.json").write_text(
            json.dumps(fills, indent=1, ensure_ascii=False))
        print(f"wrote {HERE / 'carried_fills.json'} ({len(fills)} prior fill(s)) — audit trail only; the records themselves are in the store")
    store.setdefault("meta", {})["carried_from"] = str(Path(a.src))
    store["meta"]["carried_units"] = len(carried)
    store_path.write_text(json.dumps(store, indent=1, ensure_ascii=False))
    print(f"\nwrote {store_path} ({len(store['resolutions'])} records)")


if __name__ == "__main__":
    main()
