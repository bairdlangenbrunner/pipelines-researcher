#!/usr/bin/env python3
"""Re-date pending inferred shelved/cancelled lines to the dormancy rule's year.

Baird 2026-10-20 (P3972): an inferred shelved/cancelled takes effect AFTER the quiet period, so
ShelvedYear = newest dated source + 2 and CancelledYear = newest dated source + 4, never the year of
the source itself. `merge_qc.status_qc` does this for new merges; this rewrites staged JSON that
already sits in `batches/*/staging/` (staged_resolutions.json `values` and rows/P*.json
`status_reviews[].proposed_changes`). A year that differs from the evidence year is kept (an on-hold
date the source states). Dry run unless --apply; json files keep their one-space indent.

    python scripts/fix_dormancy_years.py [--apply] [--dir batches/<scope>/staging/<run>]
"""
from __future__ import annotations

import argparse
import glob
import datetime
import json
from pathlib import Path

from merge_qc import dormancy_year

ROOT = Path(__file__).resolve().parent.parent


def fix(values: dict, evidence: str, current: str = "") -> tuple[str, str, str] | None:
    """(column, old, new) when `values` needs its year set or corrected, else None."""
    if str(values.get("ShelvedCancelledType") or "").lower() != "inferred":
        return None
    st = str(values.get("Status") or current or "").lower()
    if st not in ("shelved", "cancelled"):
        return None
    col = "CancelledYear" if st == "cancelled" else "ShelvedYear"
    new = dormancy_year(evidence, st)
    given = str(values.get(col) or "").strip()
    if new is None or (given and given != str(evidence)[:4]):
        return None
    if new > datetime.date.today().year:
        return col, given, f"{new} NOT YET (quiet period still running; check the evidence date)"
    values[col] = str(new)
    return col, given, str(new)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dir")
    a = ap.parse_args()
    base = str(ROOT / (a.dir or "batches/*/staging/*"))
    n = 0
    for f in sorted(glob.glob(base + "/staged_resolutions.json") + glob.glob(base + "/rows/P*.json")):
        try:
            d = json.load(open(f))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(d, dict):
            continue
        hits = []
        if f.endswith("staged_resolutions.json"):
            for r in d.get("resolutions") or []:
                if isinstance(r.get("values"), dict):
                    h = fix(r["values"], r.get("evidence_date") or "", r.get("current_status") or "")
                    if h:
                        hits.append((r.get("project_id"), *h))
        else:
            for s in d.get("status_reviews") or []:
                if isinstance(s, dict) and isinstance(s.get("proposed_changes"), dict):
                    h = fix(s["proposed_changes"], s.get("evidence_date") or "", s.get("current_status") or "")
                    if h:
                        hits.append((d.get("project_id"), *h))
        hits = [h for h in hits if h]
        for pid, col, old, new in hits:
            print(f"{Path(f).relative_to(ROOT)}  {pid}  {col} {old or '(blank)'} -> {new}")
        if a.apply:
            hits = [h for h in hits if "NOT YET" not in h[3]]
        if hits and a.apply:
            Path(f).write_text(json.dumps(d, indent=1, ensure_ascii=True) + "\n")
        n += len(hits)
    print(f"{n} record(s) {'rewritten' if a.apply else 'would change'}")


if __name__ == "__main__":
    main()
