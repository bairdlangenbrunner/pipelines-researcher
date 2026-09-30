#!/usr/bin/env python3
"""Scope the China-wide GulfPub crosswalk down to this sweep's 44 rows.

`reconcile.py` runs per COUNTRY, so a province sweep gets a country-wide crosswalk:
118 overlaps / 2 additions / 4 ambiguous across all 1,041 China gas rows.
`build_ref_workbook._recon_view` does NOT filter by ProjectID — it writes every row it
is given — so dropping the raw file in would put 115 out-of-scope China decisions into a
Jiangxi deliverable, burying the three that matter. This writes the scoped view the
workbook consumes; the country-wide file stays in recon-gulfpub-20260902/ as the audit
trail.

**Adding the trunks to scope changed the answer.** v1 (18 rows) found ONE apparent
overlap and hand-adjudicated it away, so the recon was a clean recorded negative. v2
(44 rows) finds THREE, and the two new ones are a real question:

    P4931  Middle Section (Zhongwei–Ji'an)  <- GulfPub "West - East Pipeline II"  0.685
    P4928  East Section (Ji'an–Fuzhou)      <- GulfPub "West - East Pipeline II"  0.701
    P4782  Phase I, Nanchang–Fengcheng      <- GulfPub "Cang-Zi Line"             0.475  FALSE POSITIVE

GEM files both as 西气东输三线 (WEP3); GulfPub names them West-East Pipeline II. That is a
line-identity disagreement on the two largest in-scope rows (2,090 km and 817 km).
Note what the geometry says: **route IoU is 0.000 and 0.009** — GulfPub's WEP2 trace does
not overlay either segment, so the composite is carried by name + attributes alone. That
is evidence the match is a NAME-FAMILY artifact (西气东输 二线/三线 differ by one numeral)
rather than corroboration, but it is NOT proof GEM's assignment is right — batch_13 is
researching the identity question from Chinese sources. Do not act on either row's values
off this match.

The recorded negative survives underneath all that, and is itself a finding:
  * GulfPub's 120 China gas records mention Jiangxi ZERO times (0 "jiangxi", 0 "江西").
  * 30 of the 44 in-scope rows land in `gem_only` — no reference counterpart at all.
  * The mainline parents P4934/P4947 are in `gem_only` while GulfPub's own mainline record
    matched the *Jiangxi segments* instead. Granularity observation, not a matcher defect.
Every one of the 44 rows is accounted for in some bucket (verified), so a thin result here
is a real absence of reference coverage, not records that never arrived.

    python scope_recon_crosswalk.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "recon_gulfpub_crosswalk.json"

# Hand adjudications, carried forward. Each is a claim about ONE pair, re-checked against
# the 2026-09-02 run; none is a blanket rule about the source.
NOTES = {
    "P4782": ("NOT A MATCH (hand-adjudicated, v1 2026-08-26, re-confirmed 2026-09-02). "
              "GulfPub's Cang-Zi Line is a Beijing/Hebei line at lon 116.21-116.56 / "
              "lat 39.22-39.89; P4782 Nanchang-Fengcheng is at ~lon 115.9 / lat 28.7 -- "
              "~1,240 km away, route IoU 0.0. The 0.475 composite is name/attribute "
              "similarity with no geometric support. Treat as gem_only. Do not act on "
              "any value in this row."),
    "P4931": ("OPEN LINE-IDENTITY QUESTION, do not act. GEM files this as West-East Gas "
              "Pipeline 3 (西气东输三线); GulfPub calls its counterpart West - East Pipeline "
              "II. Route IoU 0.009 -- the traces do not overlay, so the 0.685 composite "
              "rests on name + attributes, and the names differ by one numeral in a family "
              "where that numeral IS the line identity. Length also disagrees (GEM 2,090 km "
              "vs GulfPub 2,692 km). Adjudicate from Chinese sources before treating this "
              "as corroboration OR as a GEM error."),
    "P4928": ("OPEN LINE-IDENTITY QUESTION, do not act. Same disagreement as P4931 "
              "(GEM 西气东输三线 vs GulfPub 'West - East Pipeline II'), route IoU 0.000, "
              "GEM 817 km vs GulfPub 707 km. See P4931."),
}


def main() -> None:
    cw = json.loads(SRC.read_text())
    wl = json.loads((HERE / "worklist.json").read_text())
    pids = {u["project_id"] for u in wl["units"]}

    kept_o, kept_a, kept_amb = [], [], []
    for r in cw.get("overlaps", []) or []:
        pid = (r.get("gem_pid") or "").strip()
        if pid not in pids:
            continue
        if pid in NOTES:
            # Prepend rather than replace: the engine's own `action` text is the audit
            # trail for why the pair surfaced at all.
            r["action"] = f"{NOTES[pid]}  [engine said: {r.get('action', '')}]"
            r["hand_adjudicated"] = True
        kept_o.append(r)
    # An addition is a REFERENCE record with no GEM counterpart, so it has no in-scope PID
    # to filter on. Both of China's two are NEAR_MISS against out-of-scope rows; keeping
    # them would be importing another province's decisions into a Jiangxi deliverable.
    for r in cw.get("additions", []) or []:
        if (r.get("gem_pid") or "").strip() in pids:
            kept_a.append(r)
    for r in cw.get("ambiguous", []) or []:
        cands = r.get("candidates") or []
        # candidates are display strings like "P2299 (0.71)", not dicts.
        if any(p in str(c) for c in cands for p in pids):
            kept_amb.append(r)

    out = dict(cw)
    out["overlaps"], out["additions"], out["ambiguous"] = kept_o, kept_a, kept_amb
    out["scope"] = {
        "note": "Scoped to this sweep's 44 ProjectIDs. Country-wide crosswalk retained at "
                "batches/china-jiangxi-gas/staging/recon-gulfpub-20260902/match_diff.json.",
        "n_pids": len(pids),
        "country_wide": {k: len(cw.get(k) or []) for k in ("overlaps", "additions", "ambiguous")},
        "in_scope": {"overlaps": len(kept_o), "additions": len(kept_a),
                     "ambiguous": len(kept_amb), "gem_only_in_scope": 30},
        "recorded_negative": "GulfPub's 120 China gas records mention Jiangxi 0 times; "
                             "30 of 44 in-scope rows have no reference counterpart.",
        "hand_adjudicated": sorted(NOTES),
    }
    SRC.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"scoped {SRC.name} to {len(pids)} PIDs")
    print(f"  overlaps  {len(cw.get('overlaps') or [])} -> {len(kept_o)}")
    print(f"  additions {len(cw.get('additions') or [])} -> {len(kept_a)}")
    print(f"  ambiguous {len(cw.get('ambiguous') or [])} -> {len(kept_amb)}")
    for r in kept_o:
        flag = "  [hand-adjudicated]" if r.get("hand_adjudicated") else ""
        print(f"    {r['gem_pid']} <- {r.get('ref_name')}  {r.get('match_conf')} "
              f"{r.get('composite')} iou={r.get('route_iou')}{flag}")


if __name__ == "__main__":
    main()
