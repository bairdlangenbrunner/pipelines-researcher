#!/usr/bin/env python3
"""Reference-sweep step 4: build the reviewable deliverable from staged_resolutions.json
(the agent's output). Nothing here is auto-applied — Baird pastes verified refs into the
live Sheet manually. Every Proposed ref(s) cell has passed url_verifier (HTTP 200 + value
present, no GEM/theodora).

    python scripts/build_ref_workbook.py --staging batches/staging/ref-sweep-saudi-arabia/ \
        --output batches/pipelines_batch_<stamp>_saudi-arabia_refsweep.xlsx
    # <stamp> from: TZ=America/New_York date "+%Y%m%d_%H%M_ET"   (never overwrite)

Sheets (commodity-prefixed; empty omitted; README first):
  <Cmdty>_StatusReview     ANNUAL UPDATE only — one verdict per in-dev segment row: confirm /
                           change (evidence-based, with proposed Status + date cols) / stale
                           (dormancy rule -> Presumed) / unclear. Leads the packet when present.
  <Cmdty>_Backend          PRIMARY paste-ready view — a 1:1 mirror of the GEM tracker backend:
                           the FULL backend column set in exact sheet order, current values
                           prefilled, with proposed ref(s)/values overlaid on touched cells
                           (colored by corroboration tier). Leading SheetRow = row locator.
  <Cmdty>_OperatorsOwners  paste-ready mirror of the separate "Pipeline operators/owners"
                           backend tab (ProjectID-keyed; [ref] PRECEDES its values) — the
                           Operator [ref] / Owner [ref] cells, colored by tier.
  <Cmdty>_Validity         DEEP SWEEP only — existence/duplicate/classification/attribution/
                           spec concerns per pipeline (read-and-flag, never auto-applied).
  <Cmdty>_Fills            DEEP SWEEP only — blank value fields researched + filled with a
                           paired ref (or left blank when not corroborated).
  <Cmdty>_RouteSuggestions DEEP SWEEP only — sourced endpoint coords + corridor for weak-
                           RouteAccuracy rows (feeds the routes repo via a separate human PR).
  <Cmdty>_GulfPub          DEEP SWEEP only — GulfPub (PE World Map, Tier 2) cross-comparison:
                           overlaps / additions / ambiguous, present when gulfpub_crosswalk.json
                           was generated (build_gulfpub_crosswalk.py) for the staging dir.
  <Cmdty>_Refs_Added       MISSING_REF resolved — green ≥2 independent / yellow single
  <Cmdty>_Refs_Reverified  HAS_REF, links live + contain value (blue)
  <Cmdty>_Refs_DeadLinks   HAS_REF with a dead/value-missing link + proposed replacement
  <Cmdty>_Refs_Unresolved  couldn't reach 2 working corroborating links → manual review

The four *_Refs_* bucket tabs are supporting detail; the <Cmdty>_Backend tab is the one
Baird works from. Route/geometry `[ref]` cells are out of scope (reconciled separately).
"""
from __future__ import annotations

import argparse
import csv
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
VALIDITY_REF = "__VALIDITY__"   # synthetic ref_col sentinel on deep-sweep validity records
STATUS_REF = "__STATUS__"       # synthetic ref_col sentinel on annual-update status reviews
ROUTE_REF = "__ROUTE__"         # synthetic ref_col sentinel on deep-sweep route suggestions

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
        ("Ref column", lambda r: r.get("ref_col") or "(Owner → Operators/Owners tab)", 24),
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


# --- validity + fills (deep-sweep extensions) ------------------------------ #
# Ordered most-important-first so the strongest signal wins; the Finding column is
# authoritative — Concern type is only a sort/filter hint when the record carries no
# explicit `concern_type` (older staging predates the structured field).
_CONCERN_RULES = [
    ("existence", ("does not exist", "doesn't exist", "no evidence", "cannot find",
                   "can't find", "hallucinat", "phantom", "fabricat", "not a real",
                   "non-existent", "nonexistent", "no independent evidence")),
    ("duplicate", ("duplicate", "relabel", "same pipe", "same physical", "same as ",
                   "already tracked", "redundant", "double-count", "double count")),
    ("classification", ("not a transmission", "not dry gas", " ngl", "(ngl", "reclassif",
                        "gathering line", "process line", "feeder line", "misclassif",
                        "should be classified", "not a pipeline", "may be ngl",
                        "commodity may be")),
    ("attribution", ("wrong owner", "wrong operator", "wrong province", "wrong endpoint",
                     "misattribut", "endpoint", "fuelsource", "start state", "province error",
                     "naming", "operator")),
    ("spec", ("length", "diameter", "capacity", "discrepancy", " km vs", "does not reconcile",
              "conflict", "mismatch", "uncorroborated")),
]


# Phrasing that signals the agent CONFIRMED the pipeline is real (often while raising a
# lesser caveat). Used to keep negated mentions ("NOT a duplicate/non-existent flag",
# "exists and is correctly attributed") from being miscoded as existence/duplicate reds.
_CONFIRM_SIGNALS = ("genuine", "genuinely exist", "exists and is correctly", "correctly attributed",
                    "correctly identified", "not a duplicate", "non-existent flag", "existence ok",
                    "existence is", "does exist", "is real", "well-sourced", "not an error",
                    "segment exists", "pipeline exists", "plausibly exists")


def _validity_verdict(r: dict) -> str:
    v = (r.get("verdict") or "").strip()
    if v:
        return v
    note = (r.get("researcher_notes") or "").lower()
    return "confirmed (caveat)" if any(s in note for s in _CONFIRM_SIGNALS) else "concern"


def _concern_type(r: dict) -> str:
    explicit = (r.get("concern_type") or "").strip()
    if explicit:
        return explicit
    note = (r.get("researcher_notes") or "").lower()
    rules = _CONCERN_RULES
    # If existence/identity is affirmatively confirmed, drop the existence/duplicate buckets
    # (their keywords are usually negated here) — a confirmed pipeline can still be a spec,
    # attribution, or classification (e.g. NGL-vs-gas) concern, so keep those.
    if any(s in note for s in _CONFIRM_SIGNALS):
        rules = [(l, k) for (l, k) in _CONCERN_RULES if l not in ("existence", "duplicate")]
    for label, kws in rules:
        if any(k in note for k in kws):
            return label
    return "review"


_HIGH_CONCERN = {"existence", "duplicate", "classification"}


def _validity_columns():
    g = lambda k: (lambda r: r.get(k, ""))
    return [
        ("ProjectID", g("project_id"), 12),
        ("SheetRow", g("sheet_row"), 9),
        ("PipelineName", g("pipeline_name"), 30),
        ("SegmentName", g("segment_name"), 22),
        ("Verdict", _validity_verdict, 16),
        ("Concern type", _concern_type, 16),
        ("Finding", g("researcher_notes"), 72),
        ("Recommendation", g("recommendation"), 40),
        ("Sources", lambda r: J(r.get("proposed_refs", [])), 52),
        ("Corroboration tier", g("tier"), 13),
        ("Independent?", lambda r: "yes" if r.get("independent") else ("no" if r.get("proposed_refs") else ""), 11),
        ("Source language", g("source_language"), 12),
        ("Wiki (visited, not cited)", g("wiki"), 34),
    ]


def _validity_styler(columns):
    idx = {h: i + 1 for i, (h, _, _) in enumerate(columns)}
    tier_c = idx["Corroboration tier"]
    concern_c = idx["Concern type"]
    verdict_c = idx["Verdict"]

    def styler(ws, rn, r):
        ws.cell(rn, tier_c).fill = CONF_FILL.get(_tier_color(r), PatternFill())
        is_concern = _validity_verdict(r) == "concern"
        ws.cell(rn, verdict_c).fill = CONF_FILL["red"] if is_concern else CONF_FILL["green"]
        # red the concern type only for an OPEN high-severity concern (phantom / duplicate /
        # misclassified) — not when the pipeline was confirmed real with a lesser caveat.
        if is_concern and ws.cell(rn, concern_c).value in _HIGH_CONCERN:
            ws.cell(rn, concern_c).fill = CONF_FILL["red"]
    return styler


def _fills_columns():
    g = lambda k: (lambda r: r.get(k, ""))
    return [
        ("ProjectID", g("project_id"), 12),
        ("SheetRow", g("sheet_row"), 9),
        ("PipelineName", g("pipeline_name"), 30),
        ("SegmentName", g("segment_name"), 22),
        ("Field", lambda r: r.get("primary_value_col") or J(r.get("value_cols", [])), 18),
        ("Proposed value", lambda r: r.get("primary_value") or J([f"{k}={v}" for k, v in r.get("values", {}).items()]), 24),
        ("Proposed ref(s)", lambda r: J(r.get("proposed_refs", [])), 52),
        ("Verification status", _verif_summary, 22),
        ("Outcome", lambda r: {"REFS_ADDED": "filled (corroborated)",
                               "UNRESOLVED": "not corroborated / dropped"}.get(r.get("class_out", ""), r.get("class_out", "")), 24),
        ("Corroboration tier", g("tier"), 13),
        ("Independent?", lambda r: "yes" if r.get("independent") else ("no" if r.get("proposed_refs") else ""), 11),
        ("Source language", g("source_language"), 12),
        ("ResearcherNotes", g("researcher_notes"), 50),
        ("Wiki (visited, not cited)", g("wiki"), 34),
    ]


def _fills_styler(columns):
    idx = {h: i + 1 for i, (h, _, _) in enumerate(columns)}
    tier_c = idx["Corroboration tier"]

    def styler(ws, rn, r):
        if r.get("class_out") == "UNRESOLVED":
            ws.cell(rn, tier_c).fill = CONF_FILL["red"]
        else:
            ws.cell(rn, tier_c).fill = CONF_FILL.get(_tier_color(r), PatternFill())
    return styler


# --- status review (annual-update extension) ------------------------------- #
_STATUS_VERDICT_FILL = {"confirm": "green", "change": "yellow", "stale": "red", "unclear": "red"}


def _status_columns():
    g = lambda k: (lambda r: r.get(k, ""))
    return [
        ("ProjectID", g("project_id"), 12),
        ("SheetRow", g("sheet_row"), 9),
        ("PipelineName", g("pipeline_name"), 30),
        ("SegmentName", g("segment_name"), 22),
        ("Current status", g("current_status"), 13),
        ("Verdict", g("verdict"), 10),
        ("Proposed status", g("proposed_status"), 13),
        ("Proposed changes", lambda r: J([f"{k}={v}" for k, v in r.get("values", {}).items()]), 36),
        ("Evidence date", g("evidence_date"), 12),
        ("Staleness rule", g("staleness_rule"), 13),
        ("Proposed ref(s)", lambda r: J(r.get("proposed_refs", [])), 52),
        ("Verification status", _verif_summary, 22),
        ("Corroboration tier", g("tier"), 13),
        ("Independent?", lambda r: "yes" if r.get("independent") else ("no" if r.get("proposed_refs") else ""), 11),
        ("Source language", g("source_language"), 12),
        ("ResearcherNotes", g("researcher_notes"), 60),
        ("Wiki (visited, not cited)", g("wiki"), 34),
    ]


def _status_styler(columns):
    idx = {h: i + 1 for i, (h, _, _) in enumerate(columns)}
    verdict_c = idx["Verdict"]
    prop_c = idx["Proposed status"]
    tier_c = idx["Corroboration tier"]

    def styler(ws, rn, r):
        v = (r.get("verdict") or "").lower()
        ws.cell(rn, verdict_c).fill = CONF_FILL.get(_STATUS_VERDICT_FILL.get(v, "red"), PatternFill())
        if r.get("proposed_status"):
            ws.cell(rn, prop_c).fill = CONF_FILL["yellow"]
        if r.get("proposed_refs"):
            ws.cell(rn, tier_c).fill = CONF_FILL.get(_tier_color(r), PatternFill())
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


def _backend_snapshot(meta: dict):
    """Load the GEM tracker backend's FULL header + every data row keyed by
    (ProjectID, SheetRow), so the _Backend tab can reproduce the complete backend column
    layout in exact sheet order with current values prefilled. The tracker header is at CSV
    row index 2; data rows follow, and SheetRow = data-row index + 4 (verified against the
    snapshot). Returns (header, rows) — or ([], {}) if the snapshot named in meta.scope.csv
    can't be located, in which case the caller falls back to a structure-only mirror."""
    csv_name = (meta.get("scope") or {}).get("csv")
    if not csv_name:
        return [], {}
    # snapshots live in the repo data/ dir; tolerate either an absolute path or a bare name
    cand = Path(csv_name)
    if not cand.exists():
        cand = Path(__file__).resolve().parent.parent / "data" / Path(csv_name).name
    if not cand.exists():
        return [], {}
    try:
        with cand.open(newline="") as f:
            allrows = list(csv.reader(f))
    except OSError:
        return [], {}
    if len(allrows) < 3:
        return [], {}
    header = allrows[2]
    try:
        pid_i = header.index("ProjectID")
    except ValueError:
        return header, {}
    rows: dict[tuple, dict] = {}
    for di, raw in enumerate(allrows[3:]):        # data starts after the header at CSV index 2
        pid = raw[pid_i] if pid_i < len(raw) else ""
        sheet_row = di + 4                         # SheetRow = data-row index + 4
        rows[(pid, sheet_row)] = {col: (raw[ci] if ci < len(raw) else "")
                                  for ci, col in enumerate(header)}
    return header, rows


def _backend_view(wb, title, resolutions, backend_header, snapshot_rows):
    """The PRIMARY tab: a 1:1 paste-ready mirror of the GEM tracker backend. Reproduces the
    tracker's FULL column set in exact sheet order (every backend column, including computed
    ones), one row per in-scope segment, with current values prefilled from the snapshot.
    On each touched cluster the proposed ref(s) are overlaid on the `[ref]` cell — color-
    coded by corroboration tier (same green ≥2-independent / yellow single / red low-or-none
    / blue re-verified key as the bucket tabs) — and any proposed value is overlaid on its
    value cell. A single leading SheetRow locator column (the tracker's own row number, not a
    backend field) rides in front so Baird can find each scattered row; everything after it
    is the backend layout verbatim. Owner/Parent refs are staged on the separate
    Operators/Owners tab, so they never overlay here (there is no Owner [ref] backend column).
    Falls back to identity columns only if the snapshot header can't be loaded."""
    # group resolutions by segment (ProjectID, SheetRow), first-seen order; index by ref_col
    seg_order: list[tuple] = []
    segs: dict[tuple, dict] = {}
    for r in resolutions:
        sk = (r.get("project_id", ""), r.get("sheet_row", ""))
        if sk not in segs:
            segs[sk] = {"base": r, "by_ref": {}}
            seg_order.append(sk)
        rc = r.get("ref_col")
        if rc and rc not in (VALIDITY_REF, STATUS_REF):
            segs[sk]["by_ref"].setdefault(rc, r)

    # fall back to a minimal identity header if the snapshot couldn't be loaded
    header = list(backend_header) if backend_header else \
        ["ProjectID", "PipelineName", "SegmentName"]

    ws = wb.create_sheet(title)
    headers = ["SheetRow"] + header
    ws.append(headers)

    # 1-based sheet-column index of each backend column (offset by the leading SheetRow col)
    col_idx = {h: i + 2 for i, h in enumerate(header)}
    ref_idx = {h: ci for h, ci in col_idx.items() if h.endswith(" [ref]")}

    for sk in seg_order:
        pid, srow = sk
        current = snapshot_rows.get((pid, srow), {})
        b = segs[sk]["base"]
        # prefill from the snapshot; if the row is missing, seed the identity cells we know
        if not current:
            current = {"ProjectID": b.get("project_id", ""),
                       "PipelineName": b.get("pipeline_name", ""),
                       "SegmentName": b.get("segment_name", "")}
        ws.append([srow] + [current.get(h, "") for h in header])
        rn = ws.max_row
        for rc, r in segs[sk]["by_ref"].items():
            # overlay proposed value(s) onto their backend value cells (skip cols off-schema)
            for vc, vv in (r.get("values") or {}).items():
                ci = col_idx.get(vc)
                if ci and str(vv).strip():
                    ws.cell(rn, ci, vv)
            # overlay proposed ref text onto the [ref] cell + color by corroboration tier
            ci = ref_idx.get(rc)
            if ci:
                cell = ws.cell(rn, ci, _ref_cell_text(r))
                cell.fill = _ref_cell_fill(r)
                cell.alignment = Alignment(wrap_text=False, vertical="top")

    ws.column_dimensions["A"].width = 9
    for h, ci in col_idx.items():
        ws.column_dimensions[get_column_letter(ci)].width = 46 if h.endswith(" [ref]") else 16
    _style_header(ws, len(headers))
    # keep the SheetRow locator + identity columns (through ProjectID) visible while scrolling
    anchor = get_column_letter(col_idx["ProjectID"] + 1) if "ProjectID" in col_idx else "B"
    ws.freeze_panes = f"{anchor}2"
    return ws


def _prune_trailing_empty(value_cols, resolutions, ref_col):
    """Drop trailing value cols that are blank across every in-scope row for this ref
    (keeps the paste left-aligned; unused Owner2..Owner11 slots stay off-sheet). Always
    keep at least the first value col."""
    used = set()
    for r in resolutions:
        if r.get("ref_col") != ref_col:
            continue
        for c, v in r.get("values", {}).items():
            if str(v).strip():
                used.add(c)
    last = -1
    for i, c in enumerate(value_cols):
        if c in used:
            last = i
    return value_cols[: last + 1] if last >= 0 else value_cols[:1]


def _operators_owners_view(wb, title, resolutions):
    """Paste-ready mirror of the backend "Pipeline operators/owners" tab (GID 1489950650),
    where the `[ref]` column PRECEDES its values. ProjectID-keyed (one row per ProjectID);
    for each ref unit the `[ref]` cell — carrying the proposed ref(s), color-coded by
    corroboration tier — comes FIRST, then its value columns for context. Trailing all-empty
    owner slots are pruned. Baird pastes each `[ref]` cell back onto that tab by ProjectID."""
    # ref units in native order (Operator [ref] before Owner [ref]), by first appearance
    ref_order: list[str] = []
    ref_vcols: dict[str, list[str]] = {}
    for r in resolutions:
        rc = r.get("ref_col")
        if rc and rc not in ref_vcols:
            ref_order.append(rc)
            ref_vcols[rc] = list(r.get("value_cols", []))
    for rc in ref_order:
        ref_vcols[rc] = _prune_trailing_empty(ref_vcols[rc], resolutions, rc)

    # group by ProjectID (the OO tab is one row per ProjectID)
    proj_order: list[str] = []
    projs: dict[str, dict] = {}
    for r in resolutions:
        pid = r.get("project_id", "")
        if pid not in projs:
            projs[pid] = {"base": r, "by_ref": {}}
            proj_order.append(pid)
        projs[pid]["by_ref"][r.get("ref_col")] = r

    ws = wb.create_sheet(title)
    base = ["ProjectID", "PipelineName", "SegmentName"]
    headers = list(base)
    ref_pos: dict[str, int] = {}      # ref_col -> 1-based column index of its [ref] cell
    for rc in ref_order:
        headers.append(rc)            # ref FIRST (mirrors the tab)
        ref_pos[rc] = len(headers)
        headers.extend(ref_vcols[rc])  # then its value cols
    ws.append(headers)

    for i, w in enumerate([12, 30, 20], 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for col, h in enumerate(headers[len(base):], start=len(base) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 46 if h.endswith(" [ref]") else 18

    for pid in proj_order:
        b = projs[pid]["base"]
        by_ref = projs[pid]["by_ref"]
        rowvals = [pid, b.get("pipeline_name", ""), b.get("segment_name", "")]
        for rc in ref_order:
            r = by_ref.get(rc)
            rowvals.append(_ref_cell_text(r) if r else "")
            for vc in ref_vcols[rc]:
                rowvals.append(r.get("values", {}).get(vc, "") if r else "")
        ws.append(rowvals)
        rn = ws.max_row
        for rc in ref_order:
            r = by_ref.get(rc)
            if not r:
                continue
            cell = ws.cell(rn, ref_pos[rc])   # the [ref] cell
            cell.fill = _ref_cell_fill(r)
            cell.alignment = Alignment(wrap_text=False, vertical="top")

    _style_header(ws, len(headers))
    ws.freeze_panes = "D2"   # keep ProjectID..SegmentName visible while scrolling
    return ws


# --- route suggestions (deep-sweep extension) ------------------------------ #
def _fmt_coord(v):
    """A lat/lon for display — blank when unsourced (coordinates are never fabricated)."""
    return "" if v is None or v == "" else v


def _fmt_waypoints(r: dict) -> str:
    wps = r.get("waypoints") or []
    parts = []
    for w in wps:
        nm = (w.get("name") or "").strip()
        lat, lon = w.get("lat"), w.get("lon")
        coord = f" ({lat},{lon})" if lat is not None and lon is not None else ""
        parts.append(f"{nm}{coord}".strip())
    txt = "; ".join(p for p in parts if p)
    note = (r.get("waypoint_note") or "").strip()
    return (txt + (f" — {note}" if note else "")) if (txt or note) else ""


def _route_columns():
    g = lambda k: (lambda r: r.get(k, ""))
    return [
        ("ProjectID", g("project_id"), 12),
        ("SheetRow", g("sheet_row"), 9),
        ("PipelineName", g("pipeline_name"), 28),
        ("SegmentName", g("segment_name"), 22),
        ("Current RouteAccuracy", g("current_route_accuracy"), 16),
        ("Suggested RouteAccuracy", g("suggested_route_accuracy"), 16),
        ("Start", g("start_name"), 30),
        ("Start lat", lambda r: _fmt_coord(r.get("start_lat")), 10),
        ("Start lon", lambda r: _fmt_coord(r.get("start_lon")), 10),
        ("End", g("end_name"), 30),
        ("End lat", lambda r: _fmt_coord(r.get("end_lat")), 10),
        ("End lon", lambda r: _fmt_coord(r.get("end_lon")), 10),
        ("Waypoints", _fmt_waypoints, 40),
        ("Corridor description", g("corridor_desc"), 72),
        ("Proposed ref(s)", lambda r: J(r.get("proposed_refs", [])), 52),
        ("Verification status", _verif_summary, 20),
        ("Corroboration tier", g("tier"), 13),
        ("Independent?", lambda r: "yes" if r.get("independent") else ("no" if r.get("proposed_refs") else ""), 11),
        ("Source language", g("source_language"), 12),
        ("ResearcherNotes", g("researcher_notes"), 50),
        ("Wiki (visited, not cited)", g("wiki"), 34),
    ]


def _route_styler(columns):
    idx = {h: i + 1 for i, (h, _, _) in enumerate(columns)}
    tier_c = idx["Corroboration tier"]
    coord_cs = [idx[h] for h in ("Start lat", "Start lon", "End lat", "End lon")]

    def styler(ws, rn, r):
        ws.cell(rn, tier_c).fill = CONF_FILL.get(_tier_color(r), PatternFill())
        # corridor-only suggestion (endpoints not both coordinated) → yellow the empty
        # coord cells so it reads as "needs a sourced trace", not "ready to digitize"
        if r.get("class_out") == "ROUTE_PARTIAL":
            for cc in coord_cs:
                if not str(ws.cell(rn, cc).value or "").strip():
                    ws.cell(rn, cc).fill = CONF_FILL["yellow"]
    return styler


# --- GulfPub cross-comparison (deep-sweep extension) ------------------------ #
def _gulfpub_view(wb, title, crosswalk: dict):
    """Flat cross-comparison of the scoped GulfPub (PE World Map) reconciliation against GEM:
    one row per overlap (matched pair), then GulfPub-only additions, then ambiguous matches.
    GulfPub is a Tier-2 source — a single value here NEVER reaches green on its own; conflicts
    route to Update's normal ≥2-independent source search. Read-and-flag only, nothing applied.
    Reads the crosswalk produced by build_gulfpub_crosswalk.py (from reconcile's match_diff.json)."""
    cols = [
        ("Kind", 18), ("GEM ProjectID", 13), ("GEM name", 28), ("GEM segment", 20),
        ("GulfPub name", 28), ("Match conf", 11), ("Composite", 10),
        ("GEM status", 12), ("GP status", 12), ("Status conflict", 14),
        ("GEM diam", 10), ("GP diam", 10), ("Diam flag", 12),
        ("GEM len km", 11), ("GP len km", 11), ("Len flag", 12),
        ("GEM route acc", 14), ("GP start", 26), ("GP end", 26), ("GP has geom", 11),
        ("GP operator", 24), ("GP owners", 24), ("GP capacity", 11), ("GP startyear", 11),
        ("Candidates", 30), ("GP description", 60),
    ]
    field = {
        "Kind": "kind", "GEM ProjectID": "gem_pid", "GEM name": "gem_name",
        "GEM segment": "gem_segment", "GulfPub name": "gulfpub_name", "Match conf": "match_conf",
        "Composite": "composite", "GEM status": "gem_status", "GP status": "gp_status",
        "Status conflict": "status_conflict", "GEM diam": "gem_diam", "GP diam": "gp_diam",
        "Diam flag": "diam_flag", "GEM len km": "gem_len_km", "GP len km": "gp_len_km",
        "Len flag": "len_flag", "GEM route acc": "gem_route_acc", "GP start": "gp_start",
        "GP end": "gp_end", "GP has geom": "gp_has_geom", "GP operator": "gp_operator",
        "GP owners": "gp_owners", "GP capacity": "gp_capacity", "GP startyear": "gp_startyear",
        "Candidates": "candidates", "GP description": "gp_desc",
    }
    ws = wb.create_sheet(title)
    headers = [h for h, _ in cols]
    ws.append(headers)
    for i, (_, wdt) in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = wdt
    idx = {h: i + 1 for i, (h, _) in enumerate(cols)}

    rows = (crosswalk.get("overlaps") or []) + (crosswalk.get("additions") or []) \
        + (crosswalk.get("ambiguous") or [])
    n = 0
    for rec in rows:
        vals = []
        for h, _ in cols:
            v = rec.get(field[h], "")
            vals.append("" if v is None else v)
        ws.append(vals)
        rn = ws.max_row
        n += 1
        # match confidence cell → tier color
        mc = str(rec.get("match_conf", "")).lower()
        if mc in ("green", "yellow", "red"):
            ws.cell(rn, idx["Match conf"]).fill = CONF_FILL[mc]
        # status/spec disagreements → red/yellow flags
        if str(rec.get("status_conflict", "")).upper() == "CONFLICT":
            ws.cell(rn, idx["Status conflict"]).fill = CONF_FILL["red"]
        for flag_col, cell_col in (("diam_flag", "Diam flag"), ("len_flag", "Len flag")):
            fv = str(rec.get(flag_col, "")).lower()
            if fv and fv not in ("ok", ""):
                ws.cell(rn, idx[cell_col]).fill = CONF_FILL["yellow"]

    _style_header(ws, len(headers))
    ws.freeze_panes = "E2"   # keep Kind..GulfPub name visible while scrolling
    return ws, n


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
        ("Work from", f"the {meta.get('commodity', scope.get('tracker', 'oil')).capitalize()}_Backend tab "
                      "(mirrors the tracker layout, value next to its [ref]) and the _OperatorsOwners tab "
                      "(owner/operator refs → the separate \"Pipeline operators/owners\" backend tab, "
                      "ProjectID-keyed); the *_Refs_* tabs are supporting detail."),
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

    # full backend header + current rows from the snapshot, so the Backend tab reproduces the
    # tracker's complete column layout (exact order) with current values prefilled
    backend_header, snapshot_rows = _backend_snapshot(meta)

    # Deep-sweep records (class_in VALIDITY / FILL) get their own dedicated tabs — they are
    # NOT ref-pairs, so they must never reach the backend mirror (a VALIDITY record's synthetic
    # `__VALIDITY__` ref_col would otherwise leak in as a phantom column) or the class_out
    # bucket tabs (where they'd be buried among ordinary unresolved refs).
    # Key off the synthetic ref_col sentinel too, not just class_in: an agent occasionally
    # mislabels a validity record's class_in (seen: HAS_REF) while still stamping the
    # `__VALIDITY__` ref_col, and that sentinel must never reach the backend mirror.
    is_validity = lambda r: r.get("class_in") == "VALIDITY" or r.get("ref_col") == VALIDITY_REF
    is_status = lambda r: r.get("class_in") == "STATUS" or r.get("ref_col") == STATUS_REF
    is_route = lambda r: r.get("class_in") == "ROUTE" or r.get("ref_col") == ROUTE_REF
    validity_res = [r for r in resolutions if is_validity(r)]
    status_res = [r for r in resolutions if is_status(r) and not is_validity(r)]
    route_res = [r for r in resolutions if is_route(r)
                 and not is_validity(r) and not is_status(r)]
    fill_res = [r for r in resolutions if r.get("class_in") == "FILL"
                and not is_validity(r) and not is_status(r) and not is_route(r)]
    ref_res = [r for r in resolutions if r.get("class_in") not in ("VALIDITY", "FILL", "STATUS", "ROUTE")
               and not is_validity(r) and not is_status(r) and not is_route(r)]

    # owner/operator refs land on the separate "Pipeline operators/owners" backend tab, so
    # they get their own paste-ready mirror; everything else mirrors the tracker tab.
    oo_res = [r for r in ref_res if r.get("tab") == "operators_owners"]
    tracker_res = [r for r in ref_res if r.get("tab") != "operators_owners"]

    # Annual-update StatusReview tab leads the packet when present — the per-row status
    # verdict is what researchers act on first in an update cycle.
    if status_res:
        s_cols = _status_columns()
        s_title = f"{prefix}_StatusReview"
        _write_sheet(wb, s_title, s_cols, status_res, _status_styler(s_cols))
        sheet_defs.append((s_title,
                           f"{len(status_res)} — ANNUAL-UPDATE status verdicts, one per in-dev segment row "
                           "(NOT auto-applied). Verdict green=confirm (status verified, see evidence date) / "
                           "yellow=change (evidence-based new status; Proposed changes lists the exact "
                           "column=value edits, refs verified) / red=stale (dormancy rule -> inferred "
                           "shelved/cancelled, ShelvedCancelledType=Presumed, no ref by design) or unclear."))

    # PRIMARY tab first (after README): the tracker backend-mirror, paste-ready view.
    if tracker_res:
        backend_title = f"{prefix}_Backend"
        _backend_view(wb, backend_title, tracker_res, backend_header, snapshot_rows)
        sheet_defs.append((backend_title,
                           "PRIMARY — 1:1 paste-ready mirror of the GEM tracker backend: the FULL backend "
                           "column set in exact sheet order, one row per in-scope segment, current values "
                           "prefilled (leading SheetRow = the tracker row locator). Touched [ref] cells carry "
                           "the proposed ref(s), colored by corroboration tier (green=≥2 independent / "
                           "yellow=single / red=low or none / blue=re-verified); proposed values overlaid on "
                           "their cells. Work from THIS tab; the *_Refs_* tabs below are supporting detail."))

    # operators/owners paste-ready mirror (ProjectID-keyed, ref-precedes-values)
    if oo_res:
        oo_title = f"{prefix}_OperatorsOwners"
        _operators_owners_view(wb, oo_title, oo_res)
        sheet_defs.append((oo_title,
                           "PASTE-READY — mirror of the separate \"Pipeline operators/owners\" backend tab "
                           "(GID 1489950650), ProjectID-keyed, where the [ref] column PRECEDES its values. "
                           "Operator [ref] / Owner [ref] cells carry the proposed ref(s), color-coded by "
                           "tier. Paste each back onto that tab by ProjectID — NOT onto a tracker row."))

    # Validity tab (deep sweep): existence / duplicate / classification / attribution / spec
    # concerns — read-and-flag only, no proposed edit. Placed prominently after the paste tabs.
    if validity_res:
        v_cols = _validity_columns()
        v_title = f"{prefix}_Validity"
        _write_sheet(wb, v_title, v_cols, validity_res, _validity_styler(v_cols))
        sheet_defs.append((v_title,
                           f"{len(validity_res)} — DEEP-SWEEP existence/identity check (NOT ref work, NOT auto-"
                           "applied). Each row flags a concern for human review: Concern type red = "
                           "existence / duplicate / classification (the pipeline may be phantom, a relabel of "
                           "another GEM row, or misclassified — e.g. NGL vs dry gas / not a transmission line). "
                           "Finding is authoritative; Sources back the judgment."))

    # Fills tab (deep sweep): blank value fields researched + filled with a paired ref.
    if fill_res:
        f_cols = _fills_columns()
        f_title = f"{prefix}_Fills"
        _write_sheet(wb, f_title, f_cols, fill_res, _fills_styler(f_cols))
        sheet_defs.append((f_title,
                           f"{len(fill_res)} — DEEP-SWEEP blank-value fills: a previously empty data point "
                           "researched and filled with a paired Proposed ref. Outcome 'filled (corroborated)' = "
                           "ready to paste (tier-colored); 'not corroborated / dropped' (red) = no ≥2-independent "
                           "value found — left blank, not fabricated (standing rule 2)."))

    # RouteSuggestions tab (deep sweep): endpoint coords + corridor for weak-RouteAccuracy
    # rows — a candidate for the routes repo (separate human branch+PR), never applied here.
    if route_res:
        rt_cols = _route_columns()
        rt_title = f"{prefix}_RouteSuggestions"
        _write_sheet(wb, rt_title, rt_cols, route_res, _route_styler(rt_cols))
        sheet_defs.append((rt_title,
                           f"{len(route_res)} — DEEP-SWEEP route suggestions for low/medium/no-route rows: "
                           "sourced endpoint coordinates + a corridor description (tier-colored). Yellow coord "
                           "cells = corridor-only (endpoints not both coordinated — no fabricated coordinates, "
                           "standing rule 2). These feed a SEPARATE human branch+PR against the "
                           "GOIT-GGIT-pipeline-routes repo — a route is NEVER auto-replaced."))

    # GulfPub cross-comparison tab (deep sweep): scoped reconcile of the PE World Map dataset
    # vs GEM, if a crosswalk was generated for this staging dir (build_gulfpub_crosswalk.py).
    cw_path = Path(args.staging) / "gulfpub_crosswalk.json"
    gulfpub_n = 0
    if cw_path.exists():
        crosswalk = json.loads(cw_path.read_text())
        gp_title = f"{prefix}_GulfPub"
        _, gulfpub_n = _gulfpub_view(wb, gp_title, crosswalk)
        cw_counts = (crosswalk.get("meta") or {}).get("counts", {})
        sheet_defs.append((gp_title,
                           f"{gulfpub_n} — DEEP-SWEEP GulfPub (PE World Map / Petroleum Economist, Tier 2) "
                           "cross-comparison: overlaps (matched pairs, Match conf tier-colored), GulfPub-only "
                           "additions (match to an existing GEM row FIRST before treating as a discovery), and "
                           "ambiguous multi-candidate matches. Red Status conflict / yellow Diam or Len flag = "
                           "a disagreement to resolve via Update's ≥2-independent source search — a single "
                           "Tier-2 value NEVER reaches green alone; nothing here is applied. "
                           f"(counts: {J([f'{k}={v}' for k, v in cw_counts.items()])})"))

    counts = {}
    counts["status_reviews"] = len(status_res)
    counts["validity"] = len(validity_res)
    counts["fills"] = len(fill_res)
    counts["route_suggestions"] = len(route_res)
    counts["gulfpub_crosscompare"] = gulfpub_n
    for bucket in _ORDER:
        rows = [r for r in ref_res if r.get("class_out") == bucket]
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
