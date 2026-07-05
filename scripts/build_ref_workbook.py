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
  <Cmdty>_Backend          PRIMARY paste-ready view — mirrors the GEM tracker layout (each
                           touched data point as <value> then <value> [ref] carrying the
                           proposed ref(s), colored by corroboration tier). Work from this.
  <Cmdty>_OperatorsOwners  paste-ready mirror of the separate "Pipeline operators/owners"
                           backend tab (ProjectID-keyed; [ref] PRECEDES its values) — the
                           Operator [ref] / Owner [ref] cells, colored by tier.
  <Cmdty>_Validity         DEEP SWEEP only — existence/duplicate/classification/attribution/
                           spec concerns per pipeline (read-and-flag, never auto-applied).
  <Cmdty>_Fills            DEEP SWEEP only — blank value fields researched + filled with a
                           paired ref (or left blank when not corroborated).
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
from ref_pairs import discover_ref_pairs  # noqa: E402

BLUE_FILL = PatternFill("solid", fgColor="DDEBF7")   # re-verified (blue), per confidence_tiers
VALIDITY_REF = "__VALIDITY__"   # synthetic ref_col sentinel on deep-sweep validity records
STATUS_REF = "__STATUS__"       # synthetic ref_col sentinel on annual-update status reviews

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


def _schema_clusters(meta: dict, staging: Path) -> dict:
    """Map `{ref_col: value_cols}` derived from the ACTUAL GEM header (the schema), via the
    same discover_ref_pairs the worklist uses — the authoritative cluster definition so the
    Backend tab mirrors the backend's full value-col run (Cost+CostUnits, Capacity+
    CapacityUnits, …) even for older staging whose resolutions predate per-unit value_cols.
    Best-effort: returns {} if the snapshot CSV named in meta.scope.csv can't be located."""
    csv_name = (meta.get("scope") or {}).get("csv")
    if not csv_name:
        return {}
    # snapshots live in the repo data/ dir; tolerate either an absolute path or a bare name
    cand = Path(csv_name)
    if not cand.exists():
        cand = Path(__file__).resolve().parent.parent / "data" / Path(csv_name).name
    if not cand.exists():
        return {}
    try:
        with cand.open(newline="") as f:
            header = list(csv.reader(f))[2]   # tracker header at CSV row index 2
    except (OSError, IndexError):
        return {}
    return {p["ref_col"]: p["value_cols"]
            for p in discover_ref_pairs(header) if p["ref_col"]}


def _backend_view(wb, title, resolutions, schema_clusters=None):
    """The PRIMARY tab: a paste-ready mirror of the GEM backend. One row per pipeline
    segment; each touched cluster is shown as ALL its value columns in schema order
    (e.g. `Cost` then `CostUnits`; `Capacity` then `CapacityUnits`; `StartYear1`,
    `StartMonth1`, … — not just the primary), immediately followed by its `[ref]` column
    carrying the proposed ref(s), color-coded by corroboration tier (same green/yellow/
    red/blue key as the bucket tabs). Column order follows the sheet (first-appearance
    order of each ref unit in the staged resolutions, which are emitted in row-then-pair
    order). Owner/Parent have no `[ref]` column on the pipeline tab — their source URL
    belongs in the separate "Pipeline operators/owners" backend tab, so it rides in a
    labeled (→ Operators/Owners tab) column here."""
    # ordered clusters (one per distinct ref unit), by first appearance; capture the FULL
    # value-col run so sibling cols (CostUnits, CapacityUnits, *Month, location sub-fields)
    # are mirrored exactly as in the backend rather than collapsed to the primary value.
    # Source of truth for the run: the schema (discover_ref_pairs on the real header), then
    # the resolution's own value_cols, then — last resort — just the primary value col.
    schema_clusters = schema_clusters or {}
    dp_order: list[str] = []                        # ordered keys (ref_col)
    dp_meta: dict[str, tuple[list[str], str]] = {}  # key -> (value headers, ref header)
    for r in resolutions:
        key = r.get("ref_col") or "Owner"
        if key in (VALIDITY_REF, STATUS_REF):   # never mirror a sentinel as a backend column
            continue
        if key in dp_meta:
            continue
        dp_order.append(key)
        if r.get("ref_col"):
            vcols = list(schema_clusters.get(key) or r.get("value_cols") or [])
            if not vcols:
                vcols = [r.get("primary_value_col") or next(iter(r.get("values", {})), "")
                         or key[: -len(" [ref]")]]
            dp_meta[key] = (vcols, r["ref_col"])
        else:
            dp_meta[key] = (["Owner", "Parent"], "Owner (→ Pipeline operators/owners tab)")

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
    ref_pos: dict[str, int] = {}      # key -> 1-based column index of its [ref] cell
    for key in dp_order:
        vcols, rh = dp_meta[key]
        headers.extend(vcols)
        headers.append(rh)
        ref_pos[key] = len(headers)
    ws.append(headers)

    base_w = [12, 9, 30, 22]
    for i, w in enumerate(base_w, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for col, h in enumerate(headers[len(base):], start=len(base) + 1):
        ws.column_dimensions[get_column_letter(col)].width = 46 if h.endswith(" [ref]") else 16

    for sk in seg_order:
        b = segs[sk]["base"]
        by_key = segs[sk]["by_key"]
        rowvals = [b.get("project_id", ""), b.get("sheet_row", ""),
                   b.get("pipeline_name", ""), b.get("segment_name", "")]
        for key in dp_order:
            vcols, _ = dp_meta[key]
            r = by_key.get(key)
            vals = r.get("values", {}) if r else {}
            for vc in vcols:
                rowvals.append(vals.get(vc, ""))
            rowvals.append(_ref_cell_text(r) if r else "")
        ws.append(rowvals)
        rn = ws.max_row
        for key in dp_order:
            r = by_key.get(key)
            if not r:
                continue
            cell = ws.cell(rn, ref_pos[key])   # the [ref] cell
            cell.fill = _ref_cell_fill(r)
            cell.alignment = Alignment(wrap_text=False, vertical="top")

    _style_header(ws, len(headers))
    ws.freeze_panes = "E2"   # keep ProjectID..SegmentName visible while scrolling refs
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

    # authoritative cluster definition from the real GEM header (so the Backend tab mirrors
    # the full value-col run — Cost+CostUnits, etc. — regardless of staging vintage)
    schema_clusters = _schema_clusters(meta, Path(args.staging))

    # Deep-sweep records (class_in VALIDITY / FILL) get their own dedicated tabs — they are
    # NOT ref-pairs, so they must never reach the backend mirror (a VALIDITY record's synthetic
    # `__VALIDITY__` ref_col would otherwise leak in as a phantom column) or the class_out
    # bucket tabs (where they'd be buried among ordinary unresolved refs).
    # Key off the synthetic ref_col sentinel too, not just class_in: an agent occasionally
    # mislabels a validity record's class_in (seen: HAS_REF) while still stamping the
    # `__VALIDITY__` ref_col, and that sentinel must never reach the backend mirror.
    is_validity = lambda r: r.get("class_in") == "VALIDITY" or r.get("ref_col") == VALIDITY_REF
    is_status = lambda r: r.get("class_in") == "STATUS" or r.get("ref_col") == STATUS_REF
    validity_res = [r for r in resolutions if is_validity(r)]
    status_res = [r for r in resolutions if is_status(r) and not is_validity(r)]
    fill_res = [r for r in resolutions if r.get("class_in") == "FILL"
                and not is_validity(r) and not is_status(r)]
    ref_res = [r for r in resolutions if r.get("class_in") not in ("VALIDITY", "FILL", "STATUS")
               and not is_validity(r) and not is_status(r)]

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
        _backend_view(wb, backend_title, tracker_res, schema_clusters)
        sheet_defs.append((backend_title,
                           "PRIMARY — paste-ready mirror of the GEM tracker backend: one row per segment, each "
                           "touched data point as <value> then <value> [ref] carrying the proposed ref(s). "
                           "[ref] cell color = corroboration tier (green=≥2 independent / yellow=single / "
                           "red=low or none / blue=re-verified). Work from THIS tab; the *_Refs_* tabs below "
                           "are supporting detail."))

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

    counts = {}
    counts["status_reviews"] = len(status_res)
    counts["validity"] = len(validity_res)
    counts["fills"] = len(fill_res)
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
