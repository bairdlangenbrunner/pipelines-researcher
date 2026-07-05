#!/usr/bin/env python3
"""Discovery deliverable: build the reviewable xlsx from staged_new.json. Nothing is
auto-applied — Baird pastes qualifying new rows into the live Sheet manually.

    python scripts/build_discovery_workbook.py --staging batches/staging/annual-gas-iraq/ \
        --output batches/pipelines_batch_<stamp>_<scope>_discovery.xlsx
    # <stamp> from: TZ=America/New_York date "+%Y%m%d_%H%M_ET"   (never overwrite)

Sheets (commodity-prefixed; empty omitted; README first):
  <Cmdty>_NewRows          PRIMARY paste-ready view — the EXACT tracker header (from the
                           snapshot named in discovery_context.json); one green-tinted row
                           per qualifying candidate, values + verified [ref]s in place.
  <Cmdty>_MonitorList      below the add-threshold (Discovery SOP §3) — watch, don't add.
  <Cmdty>_MatchedExisting  candidates that matched an existing GEM row under another name —
                           OtherEnglishNames suggestions, NOT new rows.
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

NEW_FILL = PatternFill("solid", fgColor="E2EFDA")   # green tint = candidate new row


def _tracker_header(scope: dict) -> list[str]:
    csv_name = scope.get("csv")
    if not csv_name:
        sys.exit("staged_new.json meta.scope.csv missing — cannot mirror the tracker header")
    cand = Path(csv_name)
    if not cand.exists():
        cand = Path(__file__).resolve().parent.parent / "data" / Path(csv_name).name
    if not cand.exists():
        sys.exit(f"snapshot {csv_name} not found in data/ — the NewRows tab mirrors its header")
    with cand.open(newline="") as f:
        return list(csv.reader(f))[2]   # tracker header at CSV row index 2


def _new_rows_view(wb, title, header, rows):
    ws = wb.create_sheet(title)
    ws.append(header)
    col_of = {h: i + 1 for i, h in enumerate(header) if h}
    unmapped = set()
    for c in rows:
        cells = {}
        for k, v in (c.get("values") or {}).items():
            (cells.__setitem__(col_of[k], v) if k in col_of else unmapped.add(k))
        for rc, urls in (c.get("refs") or {}).items():
            (cells.__setitem__(col_of[rc], J(urls)) if rc in col_of else unmapped.add(rc))
        notes = c.get("researcher_notes", "")
        if "ResearcherNotes" in col_of and col_of["ResearcherNotes"] not in cells:
            cells[col_of["ResearcherNotes"]] = notes
        ws.append([cells.get(i, "") for i in range(1, len(header) + 1)])
        rn = ws.max_row
        for i in cells:
            cell = ws.cell(rn, i)
            cell.fill = NEW_FILL
            cell.alignment = Alignment(wrap_text=False, vertical="top")
    _style_header(ws, len(header))
    for i, h in enumerate(header, 1):
        ws.column_dimensions[get_column_letter(i)].width = 40 if h.endswith(" [ref]") else 16
    ws.freeze_panes = "A2"
    if unmapped:
        print(f"  WARN: {title}: staged keys not in the tracker header (dropped from the "
              f"mirror; still in staged_new.json): {sorted(unmapped)}")
    return ws


def _compact_columns(extra):
    g = lambda k: (lambda r: r.get(k, ""))
    cols = [
        ("Candidate name", g("name"), 34),
        *extra,
        ("Key values", lambda r: J([f"{k}={v}" for k, v in r.get("values", {}).items()]), 44),
        ("Verified ref(s)", lambda r: J(sorted({u for us in r.get("refs", {}).values() for u in us})), 52),
        ("Corroboration tier", g("tier"), 13),
        ("ResearcherNotes", g("researcher_notes"), 64),
    ]
    return cols


def _fill_readme(ws, meta, sheet_defs):
    ws.column_dimensions["A"].width = 26
    ws.column_dimensions["B"].width = 100
    scope = meta.get("scope", {})
    rows = [
        ("GEM pipeline discovery", ""),
        ("Tracker / commodity", scope.get("tracker", "")),
        ("Country", scope.get("country", "")),
        ("GEM CSV", scope.get("csv", "")),
        ("Counts", J([f"{k}={v}" for k, v in meta.get("class_counts", {}).items()])),
        ("", ""),
        ("Work from", "the _NewRows tab (exact tracker header; green cells = staged values/refs). "
                      "MonitorList = below the add-threshold, watch only. MatchedExisting = "
                      "OtherEnglishNames suggestions for existing rows, NOT new pipelines."),
        ("Add-threshold", "new_row requires ALL of: identified sponsor; country + region/endpoints; "
                          "a concrete step (MOU / FEED / permit / tender / FID). Below -> monitor."),
        ("Standing rules", "Never cite gem.wiki/globalenergymonitor/theodora/wikidot (rule 1). No "
                           "fabricated URLs (rule 2). Every ref passed url_verifier. No orphan "
                           "values/refs. Nothing auto-applied — paste manually."),
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

    data = json.loads((Path(args.staging) / "staged_new.json").read_text())
    meta = data.get("meta", {})
    candidates = data.get("candidates", [])
    prefix = (meta.get("scope", {}).get("tracker") or "gas").capitalize()

    new_rows = [c for c in candidates if c.get("class") == "new_row"]
    monitor = [c for c in candidates if c.get("class") == "monitor"]
    matched = [c for c in candidates if c.get("class") == "matched_existing"]

    wb = Workbook()
    wb.remove(wb.active)
    readme = wb.create_sheet("README")
    sheet_defs = []

    if new_rows:
        title = f"{prefix}_NewRows"
        _new_rows_view(wb, title, _tracker_header(meta.get("scope", {})), new_rows)
        sheet_defs.append((title,
                           f"{len(new_rows)} — PRIMARY paste-ready: exact tracker header, one green row per "
                           "candidate that clears the add-threshold, values + verified [ref]s in place."))
    def _flag_col2(color):
        def styler(ws, rn, r):
            ws.cell(rn, 2).fill = CONF_FILL[color]
        return styler

    if monitor:
        cols = _compact_columns([("Why monitor (threshold leg failed)",
                                  lambda r: r.get("monitor_reason", ""), 40)])
        title = f"{prefix}_MonitorList"
        _write_sheet(wb, title, cols, monitor, _flag_col2("yellow"))
        sheet_defs.append((title,
                           f"{len(monitor)} — below the add-threshold: watch for the concrete step, "
                           "do NOT add yet."))
    if matched:
        cols = _compact_columns([("Matched ProjectID",
                                  lambda r: r.get("matched_project_id", ""), 16)])
        title = f"{prefix}_MatchedExisting"
        _write_sheet(wb, title, cols, matched, _flag_col2("green"))
        sheet_defs.append((title,
                           f"{len(matched)} — same physical pipe as an existing GEM row under another "
                           "name: add the candidate name to that row's OtherEnglishNames, no new row."))

    _fill_readme(readme, meta, sheet_defs)
    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    print(f"wrote {out}  ({len(wb.sheetnames)} sheets: {', '.join(wb.sheetnames)})")
    print("  next: python scripts/recalc.py " + str(out))


if __name__ == "__main__":
    main()
