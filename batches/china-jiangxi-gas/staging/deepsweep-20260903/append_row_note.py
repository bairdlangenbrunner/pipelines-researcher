#!/usr/bin/env python3
"""Append a standardized per-row done-note to orchestrator_notes.md for each PID given.

Mechanical part only -- counts, sentinels, leads out, anything that needs a merge decision.
The orchestrator's own prose (verdicts, cross-row consequences) goes in by hand underneath.
Idempotent: a PID whose block is already present is skipped unless --force.

    python3 append_row_note.py P4797 P4796 ...
"""
import collections
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
NOTES = HERE / "orchestrator_notes.md"
FORCE = "--force" in sys.argv
pids = [a.upper() for a in sys.argv[1:] if a.startswith(("P", "p"))]

existing = NOTES.read_text(encoding="utf-8") if NOTES.exists() else ""
out = []
for pid in pids:
    marker = f"### {pid} —"
    if marker in existing and not FORCE:
        print(f"{pid}: block already present, skipped")
        continue
    sp = HERE / "shards" / f"{pid}.json"
    if not sp.exists():
        print(f"{pid}: NO SHARD, skipped")
        continue
    s = json.loads(sp.read_text())
    res = s.get("resolutions") or []
    cls = collections.Counter(r.get("class_out") for r in res)
    tiers = collections.Counter(r.get("tier") for r in res if not (r.get("ref_col") or "").startswith("__"))
    payload = json.loads((HERE / "batches" / f"{pid}.json").read_text())
    nm = (payload.get("name_forms") or {}).get("segment") or [pid]
    label = next((n for n in nm if any("一" <= c <= "鿿" for c in n)), nm[0])

    L = [f"### {pid} — {label}  (row {payload.get('sheet_row')}, {payload.get('status')})", ""]
    L.append(f"- classes: " + ", ".join(f"{k} {v}" for k, v in sorted(cls.items(), key=lambda x: -x[1]) if k))
    if tiers:
        L.append("- tiers on ref units: " + ", ".join(f"{k or '(none)'} {v}" for k, v in sorted(tiers.items(), key=lambda x: -x[1])))
    L.append(f"- harvest_opened: {s.get('harvest_opened')}"
             f"   |   cross_row_leads filed: {len(s.get('cross_row_leads') or [])}"
             + (" -> " + ", ".join(sorted({l.get('project_id', '?') for l in (s.get('cross_row_leads') or [])}))
                if s.get('cross_row_leads') else ""))
    sent = [r for r in res if (r.get("ref_col") or "").startswith("__")]
    for r in sent:
        L.append(f"- **{r['ref_col']} {r.get('class_out')}** ({r.get('tier')}, "
                 f"independent={r.get('independent')})")
    chg = []
    for r in res:
        if (r.get("ref_col") or "").startswith("__"):
            continue
        for col, val in (r.get("values") or {}).items():
            cur = (payload.get("current_values") or {}).get(col)
            if cur not in (None, "") and str(cur) != str(val):
                chg.append(f"{col}: {cur!r} -> {val!r}")
    if chg:
        L.append("- **proposed value CHANGES:** " + "; ".join(sorted(set(chg))))
    L.append("")
    out.append("\n".join(L))

if out:
    with NOTES.open("a", encoding="utf-8") as fh:
        fh.write("\n" + "\n".join(out))
    print(f"appended {len(out)} block(s)")
