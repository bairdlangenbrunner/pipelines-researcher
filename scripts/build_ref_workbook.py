#!/usr/bin/env python3
"""Reference-sweep step 4: build the reviewable deliverable from staged_resolutions.json
(the agent's output). Nothing here is auto-applied — Baird pastes verified refs into the
live Sheet manually. Every Proposed ref(s) cell has passed url_verifier (HTTP 200 + value
present, no GEM/theodora).

    python scripts/build_ref_workbook.py --staging batches/staging/ref-sweep-saudi-arabia/ \
        --output batches/pipelines_batch_<stamp>_saudi-arabia_refsweep.xlsx
    # <stamp> from: TZ=America/New_York date "+%Y%m%d_%H%M_ET"   (never overwrite)

Sheets (commodity-prefixed; empty omitted; README first):
  <Cmdty>_Backend          PRIMARY paste-ready view — mirrors the GEM backend layout (each
                           touched data point as <value> then <value> [ref] carrying the
                           proposed ref(s), colored by corroboration tier). Work from this.
  <Cmdty>_Refs_Added       MISSING_REF resolved — green ≥2 independent / yellow single
  <Cmdty>_Refs_Reverified  HAS_REF, links live + contain value (blue)
  <Cmdty>_Refs_DeadLinks   HAS_REF with a dead/value-missing link + proposed replacement
  <Cmdty>_Refs_Unresolved  couldn't reach 2 working corroborating links → manual review

The four *_Refs_* bucket tabs are supporting detail; the <Cmdty>_Backend tab is the one
Baird works from. Route/geometry `[ref]` cells are out of scope (reconciled separately).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_recon_workbook import (  # noqa: E402
    CONF_FILL, HEADER_FILL, J, _style_header, _write_sheet,
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


def _ref_cell_text(r: dict) -> str:
    """What to paste into the `[ref]` cell: the proposed ref(s); for a re-verified unit
    with no proposed change, the existing (re-checked) ref."""
    refs = r.get("proposed_refs") or []
    if refs:
        return J(refs)
    if r.get("class_out") == "REVERIFIED":
        return r.get("current_ref", "")
    return ""


def _ref_cell_fill(r: dict):
    """Corroboration color for a `[ref]` cell: blue=re-verified, else tier green/yellow/red."""
    if r.get("class_out") == "REVERIFIED":
        return BLUE_FILL
    return CONF_FILL.get(_tier_color(r), PatternFill())


def _backend_view(wb, title, resolutions):
    """The PRIMARY tab: a paste-ready mirror of the GEM backend. One row per pipeline
    segment; each touched data point is shown as its value column immediately followed by
    its `[ref]` column carrying the proposed ref(s), color-coded by corroboration tier
    (same green/yellow/red/blue key as the bucket tabs). Column order follows the sheet
    (first-appearance order of each ref unit in the staged resolutions, which are emitted
    in row-then-pair order). Owner/Parent have no `[ref]` column — their corroboration
    rides in a labeled (→ResearcherNotes) column."""
    # ordered data points (one per distinct ref unit), by first appearance
    dp_order: list[str] = []                 # ordered keys
    dp_meta: dict[str, tuple[str, str]] = {}  # key -> (value header, ref header)
    for r in resolutions:
        key = r.get("ref_col") or "Owner"
        if key in dp_meta:
            continue
        dp_order.append(key)
        if r.get("ref_col"):
            vcol = r.get("primary_value_col") or next(iter(r.get("values", {})), "") \
                or key[: -len(" [ref]")]
            dp_meta[key] = (vcol, r["ref_col"])
        else:
            dp_meta[key] = ("Owner", "Owner (→ResearcherNotes)")

    # group resolutions by segment, preserving first-seen order
    seg_order: list[tuple] = []
    segs: dict[tuple, dict] = {}
    for r in resolutions:
        sk = (r.get("project_id", ""), r.get("sheet_row", ""))
        if sk not in segs:
            segs[sk] = {"base": r, "by_key": {}}
            seg_order.append(sk)
        segs[sk]["by_key"][r.get("ref_col") or "Owner"] = r

    ws = wb.create_sheet(title)
    base = ["ProjectID", "SheetRow", "PipelineName", "SegmentName"]
    headers = list(base)
    for key in dp_order:
        vh, rh = dp_meta[key]
        headers += [vh, rh]
    ws.append(headers)

    base_w = [12, 9, 30, 22]
    for i, w in enumerate(base_w, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for j in range(len(dp_order)):
        vcol = 5 + 2 * j
        ws.column_dimensions[get_column_letter(vcol)].width = 16
        ws.column_dimensions[get_column_letter(vcol + 1)].width = 46

    for sk in seg_order:
        b = segs[sk]["base"]
        by_key = segs[sk]["by_key"]
        rowvals = [b.get("project_id", ""), b.get("sheet_row", ""),
                   b.get("pipeline_name", ""), b.get("segment_name", "")]
        for key in dp_order:
            r = by_key.get(key)
            rowvals += [r.get("primary_value", "") if r else "", _ref_cell_text(r) if r else ""]
        ws.append(rowvals)
        rn = ws.max_row
        for j, key in enumerate(dp_order):
            r = by_key.get(key)
            if not r:
                continue
            cell = ws.cell(rn, 5 + 2 * j + 1)   # the [ref] cell
            cell.fill = _ref_cell_fill(r)
            cell.alignment = Alignment(wrap_text=False, vertical="top")

    _style_header(ws, len(headers))
    ws.freeze_panes = "E2"   # keep ProjectID..SegmentName visible while scrolling refs
    return ws


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
        ("Work from", f"the {meta.get('commodity', scope.get('tracker', 'oil')).capitalize()}_Backend tab — "
                      "it mirrors the live-sheet layout (value next to its [ref]); the *_Refs_* tabs are detail."),
        ("Color key", "[ref]-cell color = corroboration tier: green=≥2 independent working sources / "
                      "yellow=single / red=low or none. Blue=re-verified existing ref (no action). On the "
                      "*_Refs_DeadLinks tab, a red Current-ref cell = dead/value-missing link."),
        ("Out of scope", "Route/geometry [ref] cells are NOT swept — pipeline geometry is reconciled against "
                         "the GOIT-GGIT-pipeline-routes repo (separate human branch+PR), not media [ref] URLs."),
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
        ws.cell(rn, 2).alignment = Alignment(wrap_text=False, vertical="top")
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

    # PRIMARY tab first (after README): the backend-mirror, paste-ready view.
    if resolutions:
        backend_title = f"{prefix}_Backend"
        _backend_view(wb, backend_title, resolutions)
        sheet_defs.append((backend_title,
                           "PRIMARY — paste-ready mirror of the GEM backend: one row per segment, each "
                           "touched data point as <value> then <value> [ref] carrying the proposed ref(s). "
                           "[ref] cell color = corroboration tier (green=≥2 independent / yellow=single / "
                           "red=low or none / blue=re-verified). Work from THIS tab; the *_Refs_* tabs below "
                           "are supporting detail."))

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
