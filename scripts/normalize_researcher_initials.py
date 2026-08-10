#!/usr/bin/env python3
"""normalize_researcher_initials.py — collapse multi-person Researcher / RouteCreator
cells to the LAST person's initials ("XJ+AY" -> "AY").

Mechanical, pre-verified sheet edit (Baird directive 2026-08-10). Covers all three
backend tabs: Oil/NGL pipelines (Researcher), Gas pipelines (Researcher +
RouteCreator), Pipeline operators/owners (Researcher).

A cell is only touched when it splits into 2+ tokens on a person separator
(+ ; , / & " and ") AND every token is an initials code (2-3 capital letters).
Anything else — single names, junk values like '50.00%; 50.00%' — is reported and
left alone.

  plan (default; gws-gem, READ-ONLY):  batchGet valueRenderOption=FORMULA on every
    target cell, abort on any formula; writes the before/after backup CSV to notes/.
  apply (--apply; gws-gem-write):  values.batchUpdate, valueInputOption=RAW, one
    cell-scoped range per cell, then re-read every cell and diff against the plan.

Usage:
  python scripts/normalize_researcher_initials.py                # plan only
  python scripts/normalize_researcher_initials.py --apply
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

SHEET_ID = "1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"
REPO = Path(__file__).resolve().parent.parent

# (tab title, snapshot csv, pandas header row, sheet_row = csv_index + offset, columns)
TABS = [
    ("Oil/NGL pipelines", "data/GOIT_oil_ngl_snapshot_20260810.csv", 2, 4,
     ["Researcher"]),
    ("Gas pipelines", "data/GGIT_gas_snapshot_20260810.csv", 2, 4,
     ["Researcher", "RouteCreator"]),
    ("Pipeline operators/owners", "data/GEM_operators_owners_snapshot_20260810.csv", 1, 3,
     ["Researcher"]),
]

SEP = re.compile(r"\s*(?:\+|;|,|/|&|\band\b)\s*")
INITIALS = re.compile(r"^[A-Z]{2,3}$")


def a1(idx: int) -> str:
    """0-based column index -> A1 letters."""
    s = ""
    idx += 1
    while idx:
        idx, r = divmod(idx - 1, 26)
        s = chr(65 + r) + s
    return s


def gws(config: str, *args: str) -> dict:
    env = dict(os.environ,
               GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser(f"~/.config/{config}"),
               GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file")
    proc = subprocess.run(["gws", "sheets", "spreadsheets", "values", *args],
                          capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        sys.exit(f"ERROR: gws {args[0]} failed: {proc.stderr.strip()[:500]}")
    out = proc.stdout
    return json.loads(out[out.index("{"):])


def batch_get(tab: str, ranges: list[str], render: str,
              chunk: int = 100) -> list[list[list]]:
    """Cell-scoped batchGet, chunked — ranges ride in the query string."""
    out: list[list[list]] = []
    for i in range(0, len(ranges), chunk):
        part = ranges[i:i + chunk]
        params = json.dumps({"spreadsheetId": SHEET_ID,
                             "ranges": [f"'{tab}'!{r}" for r in part],
                             "valueRenderOption": render, "majorDimension": "ROWS"})
        body = gws("gws-gem", "batchGet", "--params", params)
        vrs = body["valueRanges"]
        assert len(vrs) == len(part), f"got {len(vrs)} ranges, asked {len(part)}"
        out += [vr.get("values") or [[]] for vr in vrs]
    return out


def collapse(raw: str) -> tuple[str | None, str]:
    """-> (new value or None if untouched, reason)."""
    v = raw.strip()
    if not v:
        return None, "blank"
    toks = [t for t in SEP.split(v) if t]
    if len(toks) < 2:
        return (None, "single") if INITIALS.match(v) else (None, "single-nonstandard")
    if not all(INITIALS.match(t) for t in toks):
        return None, "SKIP-nonstandard-multi"
    return toks[-1], "collapse"


def build_plan() -> tuple[list[dict], list[dict]]:
    plan, skipped = [], []
    for tab, rel, header, offset, cols in TABS:
        df = pd.read_csv(REPO / rel, header=header, low_memory=False,
                         keep_default_na=False, na_values=[], dtype=str).fillna("")
        pid_col = "ProjectID" if "ProjectID" in df.columns else df.columns[0]
        for col in cols:
            if col not in df.columns:
                sys.exit(f"ERROR: {tab} has no column {col!r}")
            letter = a1(list(df.columns).index(col))
            for i, raw in df[col].items():
                new, why = collapse(str(raw))
                rec = {"tab": tab, "col": col, "letter": letter,
                       "sheet_row": i + offset, "pid": str(df[pid_col].iloc[i]).strip(),
                       "before": str(raw), "after": new, "why": why}
                if new is not None and new != str(raw):
                    plan.append(rec)
                elif why.startswith("SKIP"):
                    skipped.append(rec)
    return plan, skipped


def write_backup(plan: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["tab", "column", "cell", "sheet_row", "ProjectID", "before", "after"])
        for p in plan:
            w.writerow([p["tab"], p["col"], f"{p['letter']}{p['sheet_row']}",
                        p["sheet_row"], p["pid"], p["before"], p["after"]])
    print(f"backup written: {path.relative_to(REPO)}")


def check_formulas(plan: list[dict]) -> None:
    """Abort if any target cell holds a formula, or if the live value drifted."""
    drift = 0
    for tab in {p["tab"] for p in plan}:
        rows = [p for p in plan if p["tab"] == tab]
        ranges = [f"{p['letter']}{p['sheet_row']}" for p in rows]
        got = batch_get(tab, ranges, "FORMULA")
        for p, g in zip(rows, got):
            live = str((g[0] if g else [""])[0] if (g and g[0]) else "")
            if live.startswith("="):
                sys.exit(f"ABORT: formula in {tab}!{p['letter']}{p['sheet_row']}: {live!r}")
            if live != p["before"]:
                print(f"DRIFT {tab}!{p['letter']}{p['sheet_row']}: "
                      f"live {live!r} != snapshot {p['before']!r}", file=sys.stderr)
                drift += 1
    if drift:
        sys.exit(f"ABORT: {drift} cells drifted from the snapshot — re-pull and re-plan")
    print(f"formula check: clean, {len(plan)} cells match the snapshot exactly")


def apply_plan(plan: list[dict]) -> None:
    data = [{"range": f"'{p['tab']}'!{p['letter']}{p['sheet_row']}",
             "majorDimension": "ROWS", "values": [[p["after"]]]} for p in plan]
    body = json.dumps({"valueInputOption": "RAW", "data": data,
                       "includeValuesInResponse": False})
    resp = gws("gws-gem-write", "batchUpdate",
               "--params", json.dumps({"spreadsheetId": SHEET_ID}), "--json", body)
    print(f"batchUpdate: {resp.get('totalUpdatedCells')} cells updated")

    bad = []
    for tab in {p["tab"] for p in plan}:
        rows = [p for p in plan if p["tab"] == tab]
        got = batch_get(tab, [f"{p['letter']}{p['sheet_row']}" for p in rows],
                        "UNFORMATTED_VALUE")
        for p, g in zip(rows, got):
            live = str((g[0] if g else [""])[0] if (g and g[0]) else "")
            if live != p["after"]:
                bad.append((f"{tab}!{p['letter']}{p['sheet_row']}", live, p["after"]))
    if bad:
        for rng, gotv, want in bad:
            print(f"MISMATCH {rng}: got {gotv!r} want {want!r}", file=sys.stderr)
        sys.exit(f"{len(bad)} cells failed verification")
    print(f"verified: all {len(plan)} cells read back exactly as planned")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true",
                    help="write to the live sheet (gws-gem-write); default is plan-only")
    ap.add_argument("--backup", default="notes/backup-2026-08-10-researcher-initials.csv")
    args = ap.parse_args()

    plan, skipped = build_plan()

    from collections import Counter
    print(f"\n{len(plan)} cells to collapse\n")
    for (tab, col), n in Counter((p["tab"], p["col"]) for p in plan).most_common():
        print(f"  {tab:28s} {col:13s} {n:4d}")
    print("\ntransformations:")
    for (b, a2), n in Counter((p["before"], p["after"]) for p in plan).most_common():
        print(f"  {b!r:22s} -> {a2!r:8s} x{n}")
    if skipped:
        print(f"\n{len(skipped)} cells LEFT ALONE (multi-token but not initials):")
        for s in skipped:
            print(f"  {s['tab']}!{s['letter']}{s['sheet_row']} "
                  f"({s['col']}, {s['pid'] or 'no PID'}): {s['before']!r}")

    write_backup(plan, REPO / args.backup)
    check_formulas(plan)
    if not args.apply:
        print("\nplan only — re-run with --apply to write")
        return
    apply_plan(plan)


if __name__ == "__main__":
    main()
