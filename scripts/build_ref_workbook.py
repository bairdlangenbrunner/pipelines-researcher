#!/usr/bin/env python3
"""Reference-sweep step 4: build the reviewable deliverable from staged_resolutions.json
(the agent's output). Nothing here is auto-applied — Baird pastes verified refs into the
live Sheet manually. Every Proposed ref(s) cell has passed url_verifier (HTTP 200 + value
present, no GEM/theodora).

    python scripts/build_ref_workbook.py --staging batches/staging/ref-sweep-saudi-arabia/ \
        --output batches/pipelines_batch_<stamp>_saudi-arabia_refsweep.xlsx
    # <stamp> from: TZ=America/New_York date "+%Y%m%d_%H%M_ET"   (never overwrite)

Sheets (commodity-prefixed; empty omitted; README first):
  <Cmdty>_Refs_Added       MISSING_REF resolved — green ≥2 independent / yellow single
  <Cmdty>_Refs_Reverified  HAS_REF, links live + contain value (blue)
  <Cmdty>_Refs_DeadLinks   HAS_REF with a dead/value-missing link + proposed replacement
  <Cmdty>_Refs_Unresolved  couldn't reach 2 working corroborating links → manual review
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_recon_workbook import (  # noqa: E402
    CONF_FILL, HEADER_FILL, J, _write_sheet,
)

BLUE_FILL = PatternFill("solid", fgColor="DDEBF7")   # re-verified (blue), per confidence_tiers

# class_out -> (sheet suffix, readme blurb)
_BUCKETS = {
    "REFS_ADDED": ("Refs_Added", "blank [ref] filled. Tier cell green = ≥2 independent working "
                   "sources; yellow = single source (still needs a 2nd)."),
    "REVERIFIED": ("Refs_Reverified", "existing [ref] re-checked: all links live AND still contain "
                   "the value, ≥2 independent. Blue = verified, no action needed."),
    "DEAD_LINK": ("Refs_DeadLinks", "existing [ref] has a dead / value-missing link (red). Proposed "
                  "ref(s) = a verified replacement to swap in."),
    "UNRESOLVED": ("Refs_Unresolved", "could not reach 2 working, independent, value-containing links "
                   "(red). Manual review — no fabricated URLs (standing rule 2)."),
}
_ORDER = ["REFS_ADDED", "REVERIFIED", "DEAD_LINK", "UNRESOLVED"]


def _verif_summary(r: dict) -> str:
    vs = r.get("verifications", [])
    if not vs:
        return ""
    live = sum(1 for v in vs if v.get("ok"))
    val = sum(1 for v in vs if v.get("contains_value"))
    return f"{live}/{len(vs)} live, {val} contain value"


def _ref_columns():
    g = lambda k: (lambda r: r.get(k, ""))
    return [
        ("ProjectID", g("project_id"), 12),
        ("SheetRow", g("sheet_row"), 9),
        ("PipelineName", g("pipeline_name"), 32),
        ("SegmentName", g("segment_name"), 22),
        ("Ref column", lambda r: r.get("ref_col") or "(Owner → ResearcherNotes)", 20),
        ("Data point(s)", lambda r: r.get("primary_value_col") or J(list(r.get("values", {}).keys())), 18),
        ("Current value", lambda r: r.get("primary_value") or J([f"{k}={v}" for k, v in r.get("values", {}).items()]), 22),
        ("Current ref", g("current_ref"), 30),
        ("Proposed ref(s)", lambda r: J(r.get("proposed_refs", [])), 52),
        ("Verification status", _verif_summary, 22),
        ("Corroboration tier", g("tier"), 13),
        ("Independent?", lambda r: "yes" if r.get("independent") else ("no" if r.get("proposed_refs") else ""), 11),
        ("Source language", g("source_language"), 12),
        ("ResearcherNotes", g("researcher_notes"), 50),
        ("Wiki (visited, not cited)", g("wiki"), 34),
    ]


def _tier_color(r: dict) -> str:
    if r.get("tier_color"):
        return r["tier_color"]
    return {"high": "green", "medium": "yellow"}.get(r.get("tier", ""), "red")


def _make_styler(columns, bucket: str):
    idx = {h: i + 1 for i, (h, _, _) in enumerate(columns)}
    tier_c = idx["Corroboration tier"]
    verif_c = idx["Verification status"]
    cur_ref_c = idx["Current ref"]

    def styler(ws, rn, r):
        if bucket == "REVERIFIED":
            ws.cell(rn, tier_c).fill = BLUE_FILL
            ws.cell(rn, verif_c).fill = BLUE_FILL
            return
        ws.cell(rn, tier_c).fill = CONF_FILL.get(_tier_color(r), PatternFill())
        if bucket == "DEAD_LINK":
            ws.cell(rn, cur_ref_c).fill = CONF_FILL["red"]
        elif bucket == "UNRESOLVED":
            ws.cell(rn, tier_c).fill = CONF_FILL["red"]
    return styler


def _fill_readme(ws, meta, sheet_defs):
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 100
    scope = meta.get("scope", {})
    counts = meta.get("counts", {})
    rows = [
        ("GEM reference sweep", ""),
        ("Tracker / commodity", meta.get("commodity", scope.get("tracker", ""))),
        ("Country", scope.get("country", meta.get("country", ""))),
        ("GEM CSV", scope.get("csv", "")),
        ("Statuses", J(scope.get("statuses", "all"))),
        ("Generated", meta.get("generated", "")),
        ("", ""),
        ("Counts", J([f"{k}={v}" for k, v in counts.items()])),
        ("", ""),
        ("Color key", "Tier: green=≥2 independent working sources / yellow=single / red=low or none. "
                      "Blue=re-verified existing ref (no action). Red Current-ref cell=dead/value-missing link."),
        ("Standing rules", "Start from the row's gem.wiki page but NEVER cite gem.wiki/globalenergymonitor "
                           "(rule 1). Never theodora. Never fabricate a URL (rule 2). Every Proposed ref "
                           "passed url_verifier (HTTP 200 + value present). Nothing auto-applied — paste manually."),
        ("Target", "Per data point: ≥2 links that both WORK and corroborate each other and contain the "
                   "precise value. Searched in-country languages where needed (see Source language)."),
        ("", ""),
        ("Sheets", ""),
    ]
    for r in rows:
        ws.append(r)
    for name, desc in sheet_defs:
        ws.append((name, desc))
    ws["A1"].font = Font(bold=True, size=13)
    for c in (1, 2):
        ws.cell(1, c).fill = HEADER_FILL
        ws.cell(1, c).font = Font(bold=True, color="FFFFFF", size=13)
    for rn in range(2, ws.max_row + 1):
        ws.cell(rn, 1).font = Font(bold=True)
        ws.cell(rn, 2).alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    out = Path(args.output)
    if out.exists():
        sys.exit(f"refusing to overwrite existing {out} (use a fresh <stamp>)")

    data = json.loads((Path(args.staging) / "staged_resolutions.json").read_text())
    meta = data.get("meta", {})
    resolutions = data.get("resolutions", [])
    cmdty = (meta.get("commodity") or meta.get("scope", {}).get("tracker") or "oil")
    prefix = cmdty.capitalize()

    wb = Workbook()
    wb.remove(wb.active)
    readme = wb.create_sheet("README")

    columns = _ref_columns()
    sheet_defs = []
    counts = {}
    for bucket in _ORDER:
        rows = [r for r in resolutions if r.get("class_out") == bucket]
        counts[bucket.lower()] = len(rows)
        if not rows:
            continue
        suffix, blurb = _BUCKETS[bucket]
        title = f"{prefix}_{suffix}"
        _write_sheet(wb, title, columns, rows, _make_styler(columns, bucket))
        sheet_defs.append((title, f"{len(rows)} — {blurb}"))

    meta.setdefault("counts", counts)
    _fill_readme(readme, meta, sheet_defs)

    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print(f"wrote {out}  ({len(wb.sheetnames)} sheets: {', '.join(wb.sheetnames)})")
    print(f"  counts: {counts}")
    print("  next: python scripts/recalc.py " + str(out))


if __name__ == "__main__":
    main()
