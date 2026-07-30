#!/usr/bin/env python3
"""Apply staged ROUTE_CANDIDATEs' sheet-side route columns to the live tracker.

THE SHEET-WRITE HALF OF THE §8 APPLY FLOW (workflows.md §8 step 6). Requires
explicit, per-batch authorization from Baird — approval never carries over
(CLAUDE.md hard requirements). Run only AFTER the candidates' geojsons have
merged into GOIT-GGIT-pipeline-routes via its qc_routes.py gate; this script
writes the columns that describe those now-live routes.

Generalizes the three one-off drivers from the Egypt gas batch (2026-07-30,
backups `notes/sheet-write-2026-07-30-egypt-gas-*.csv`). Per row it writes:

  RouteAccuracy  = staged suggested_route_accuracy   (current must be 'no route')
  RouteNotes    += CB method stamp + " — " + researcher_notes   (append)
  RouteCreator  += "CB"                    (append; gas tab only — oil has no column)
  Route [ref]   += staged URLs not already in the cell           (append)

Column letters are DERIVED FROM THE FRESH CSV HEADER each run (schema drifts;
never hard-code offsets) — CSV col index == sheet col index, CSV row index + 4
== sheet row (header=2).

Protocol (all mechanical, all pre-verified):
  plan phase (default; gws-gem, READ-ONLY):  batchGet valueRenderOption=FORMULA;
    abort on any formula cell, ProjectID mismatch, RouteAccuracy != 'no route',
    or an existing 'CB: route' stamp in RouteNotes (double-append guard).
    Appends are recomputed from LIVE cell content. Writes the before/after
    backup CSV to notes/ (commit it) + the plan JSON next to it.
  apply phase (--apply; gws-gem-write):  values.batchUpdate,
    valueInputOption=RAW, one cell-scoped range per row, then re-read every
    written cell and verify it matches the plan exactly.

Usage:
  python scripts/apply_route_candidates.py --staging batches/<scope>/staging/route-creation \
      --commodity gas --csv data/GGIT_gas_snapshot_<date>.csv --scope-slug egypt-gas \
      [--pids P8013,P8014,P8021]        # plan phase; then, after reviewing:
  python scripts/apply_route_candidates.py ... --apply
"""
import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SHEET_ID = "1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"
TABS = {"gas": "Gas pipelines", "oil": "Oil/NGL pipelines"}
VOCAB = {"high", "medium", "low", "very low (straight line/schematic)",
         "very high (within meters)"}
COLS = ["RouteAccuracy", "RouteNotes", "RouteCreator", "Route [ref]"]


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


def batch_get(tab: str, ranges: list[str], render: str) -> list[list[list]]:
    params = json.dumps({"spreadsheetId": SHEET_ID,
                         "ranges": [f"'{tab}'!{r}" for r in ranges],
                         "valueRenderOption": render, "majorDimension": "ROWS"})
    body = gws("gws-gem", "batchGet", "--params", params)
    vrs = body["valueRanges"]
    assert len(vrs) == len(ranges), f"got {len(vrs)} ranges, asked {len(ranges)}"
    return [vr.get("values") or [[]] for vr in vrs]


def stamp_of(proposed_notes: str) -> str:
    i = proposed_notes.rfind("CB: route")
    assert i >= 0, f"no CB stamp in {proposed_notes!r}"
    return proposed_notes[i:].strip()


def build_plan(args, tab: str, col_letter: dict, pid_letter: str) -> list[dict]:
    import pandas as pd
    staged = json.loads((Path(args.staging) / "staged_resolutions.json").read_text())
    cands = [r for r in staged["resolutions"] if r.get("class_out") == "ROUTE_CANDIDATE"]
    if args.pids:
        want = set(args.pids.split(","))
        cands = [r for r in cands if r["project_id"] in want]
        missing = want - {r["project_id"] for r in cands}
        assert not missing, f"no ROUTE_CANDIDATE staged for: {sorted(missing)}"
    assert cands, "nothing to apply"

    df = pd.read_csv(args.csv, header=2, low_memory=False)
    have_creator = "RouteCreator" in col_letter

    items = []
    for r in sorted(cands, key=lambda x: x["project_id"]):
        rows = df.index[df["ProjectID"] == r["project_id"]].tolist()
        assert len(rows) == 1, f"{r['project_id']}: {len(rows)} rows in fresh snapshot"
        acc = (r.get("suggested_route_accuracy") or "").strip()
        assert acc in VOCAB, f"{r['project_id']}: bad accuracy {acc!r}"
        items.append({"pid": r["project_id"], "sheet_row": rows[0] + 4,
                      "proposed": r["proposed_sheet"], "acc": acc,
                      "researcher_notes": (r.get("researcher_notes") or "").strip()})

    # the four target columns are contiguous on neither tab necessarily — read
    # each column cell-scoped, plus the ProjectID cell, all in one batchGet
    ranges = []
    per_row = [pid_letter] + [col_letter[c] for c in COLS if c in col_letter]
    for c in items:
        ranges += [f"{L}{c['sheet_row']}" for L in per_row]
    got = batch_get(tab, ranges, "FORMULA")

    n = len(per_row)
    plan = []
    for i, c in enumerate(items):
        cells = [((got[n * i + j][0] or [""]) + [""])[0] for j in range(n)]
        cells = [str(v).strip() if v else "" for v in cells]
        pid_cell, rest = cells[0], cells[1:]
        assert pid_cell == c["pid"], \
            f"row {c['sheet_row']}: ProjectID cell is {pid_cell!r}, expected {c['pid']}"
        for v in cells:
            assert not v.startswith("="), \
                f"{c['pid']} row {c['sheet_row']}: formula cell {v!r} — aborting"
        cur = dict(zip([k for k in COLS if k in col_letter], rest))

        assert cur["RouteAccuracy"] == "no route", \
            f"{c['pid']}: RouteAccuracy is {cur['RouteAccuracy']!r}, expected 'no route' — aborting"
        assert "CB: route" not in cur["RouteNotes"], \
            f"{c['pid']}: RouteNotes already has a CB stamp — double-append guard"

        stamp = stamp_of(c["proposed"]["RouteNotes"])
        addition = f"{stamp} — {c['researcher_notes']}" if c["researcher_notes"] else stamp
        sep = " " if cur["RouteNotes"].endswith(".") else "; "
        after = {"RouteAccuracy": c["acc"],
                 "RouteNotes": f"{cur['RouteNotes']}{sep}{addition}"
                               if cur["RouteNotes"] else addition}

        if have_creator:
            toks = [t.strip() for t in cur["RouteCreator"].split(";")]
            after["RouteCreator"] = cur["RouteCreator"] if "CB" in toks else \
                (f"{cur['RouteCreator']}; CB" if cur["RouteCreator"] else "CB")

        staged_urls = [u for u in c["proposed"]["Route [ref]"].split("; ") if u]
        new_urls = [u for u in dict.fromkeys(staged_urls) if u not in cur["Route [ref]"]]
        after["Route [ref]"] = "; ".join(
            ([cur["Route [ref]"]] if cur["Route [ref]"] else []) + new_urls)

        plan.append({"pid": c["pid"], "sheet_row": c["sheet_row"],
                     "before": cur, "after": after})
    return plan


def apply_plan(plan: list[dict], tab: str, col_letter: dict) -> None:
    data = []
    for p in plan:
        for k, v in p["after"].items():
            data.append({"range": f"'{tab}'!{col_letter[k]}{p['sheet_row']}",
                         "majorDimension": "ROWS", "values": [[v]]})
    body = json.dumps({"valueInputOption": "RAW", "data": data,
                       "includeValuesInResponse": False})
    resp = gws("gws-gem-write", "batchUpdate",
               "--params", json.dumps({"spreadsheetId": SHEET_ID}), "--json", body)
    print(f"batchUpdate: {resp.get('totalUpdatedCells')} cells updated")

    ranges = [d["range"].split("!", 1)[1] for d in data]
    got = batch_get(tab, ranges, "UNFORMATTED_VALUE")
    bad = [(d["range"], v, d["values"][0]) for d, v in
           zip(data, ([str(x) for x in (g[0] or [""])[:1]] for g in got))
           if v != [str(x) for x in d["values"][0]]]
    if bad:
        for rng, gotv, want in bad:
            print(f"MISMATCH {rng}:\n  got  {gotv}\n  want {want}", file=sys.stderr)
        sys.exit(f"{len(bad)} cells failed verification")
    print(f"verified: all {len(data)} cells read back exactly as planned")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--staging", required=True)
    ap.add_argument("--commodity", required=True, choices=["gas", "oil"])
    ap.add_argument("--csv", required=True,
                    help="FRESH tracker snapshot (pull first; header=2)")
    ap.add_argument("--scope-slug", required=True,
                    help="e.g. egypt-gas — names the notes/ backup CSV")
    ap.add_argument("--pids", help="comma-separated subset (default: all staged ROUTE_CANDIDATEs)")
    ap.add_argument("--apply", action="store_true",
                    help="write the sheet (plan JSON must exist from a plan run)")
    args = ap.parse_args()

    import pandas as pd
    tab = TABS[args.commodity]
    header = pd.read_csv(args.csv, header=2, low_memory=False, nrows=0).columns.tolist()
    col_letter = {c: a1(header.index(c)) for c in COLS if c in header}
    pid_letter = a1(header.index("ProjectID"))
    for required in ("RouteAccuracy", "RouteNotes", "Route [ref]"):
        assert required in col_letter, f"{required} not in {args.csv} header"
    if "RouteCreator" not in col_letter:
        print("note: no RouteCreator column on this tab — skipping that append")

    plan_path = Path(args.staging) / "apply_route_candidates_plan.json"
    if args.apply:
        apply_plan(json.loads(plan_path.read_text()), tab, col_letter)
        return

    plan = build_plan(args, tab, col_letter, pid_letter)
    plan_path.write_text(json.dumps(plan, indent=1, ensure_ascii=False))
    backup = REPO / "notes" / \
        f"sheet-write-{date.today().isoformat()}-{args.scope_slug}-route-columns.csv"
    with backup.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["project_id", "sheet_row", "column", "before", "after"])
        for p in plan:
            for col in p["after"]:
                w.writerow([p["pid"], p["sheet_row"], col,
                            p["before"].get(col, ""), p["after"][col]])
    print(f"plan: {len(plan)} rows -> {plan_path}")
    print(f"backup written (commit it): {backup}")
    for p in plan:
        print(f"  {p['pid']} row {p['sheet_row']}: acc -> {p['after']['RouteAccuracy']!r}, "
              f"refs {len(p['after']['Route [ref]'].split('; '))}")
    print("review the plan, then re-run with --apply (requires per-batch authorization)")


if __name__ == "__main__":
    main()
