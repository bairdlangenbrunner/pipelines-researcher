"""Has a staged route candidate already been added? Read only: the local routes-repo mirror, its git log, and the snapshot row.

    python review_app/route_state.py --staging batches/united-states-gas/staging/route-creation [--snapshot CSV]

The past §8 applies left no marker on the staged record, so the review page cannot tell an applied route line from an open one by the record alone (docs/plans/2026-10-21_review-app-route-maps.md, "Already added"). This module compares the candidate geojson with the routes-repo file for the same ProjectID (coordinates rounded to 6 decimals, lines in any order) and reads the sheet's route columns:

    repo same,    sheet mapped                    -> applied {by: routes_repo, at, commit, sheet: true}
    repo same,    sheet not mapped                -> disagree (finding A of scripts/audit_route_sync.py)
    repo differs, sheet carries the CB stamp      -> disagree (a non-replacement only; for a replacement, differs is the state before the apply)
    repo missing, sheet carries the CB stamp      -> disagree
    anything else                                 -> an open line

A staged `applied` marker (written by scripts/apply_route_candidates.py --apply from 2026-10-22) makes the line applied by `apply_route_candidates` whatever the mirror says; a disagreement is still reported beside it. The fix for a disagreement is never on the page: it is the sheet half of the §8 apply (apply_route_candidates.py, or its --backfill-route-type when only RouteType is behind). The mirror is only as fresh as its last pull.
"""
import argparse
import functools
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "scripts"))

import paths  # noqa: E402

MAPPED = "Mapped route (at any accuracy)"


def lines_of(gj):
    """The (Multi)LineString coordinates in a geojson object as a sorted tuple of lines of (x, y) rounded to 6 decimals; z and properties are ignored. None when it holds no line."""
    out = []

    def walk(g):
        if not isinstance(g, dict):
            return
        t = g.get("type")
        if t == "FeatureCollection":
            for f in g.get("features") or []:
                walk(f)
        elif t == "Feature":
            walk(g.get("geometry"))
        elif t == "GeometryCollection":
            for x in g.get("geometries") or []:
                walk(x)
        elif t in ("LineString", "MultiLineString"):
            ls = [g.get("coordinates")] if t == "LineString" else g.get("coordinates") or []
            for ln in ls:
                try:
                    pts = tuple((round(float(c[0]), 6), round(float(c[1]), 6)) for c in ln or [])
                except (TypeError, ValueError, IndexError):
                    continue
                if pts:
                    out.append(pts)
    walk(gj)
    return tuple(sorted(out)) or None


def _read(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def repo_state(cand_path, pid, commodity=None):
    """('same' | 'differs' | 'missing', the routes-repo path or None). An unreadable candidate compares as differs."""
    rp = paths.gem_route_path(pid, commodity)
    if rp is None:
        return "missing", None
    have = lines_of(_read(rp))
    if have is None:
        return "missing", rp
    return ("same" if lines_of(_read(cand_path)) == have else "differs"), rp


@functools.lru_cache(maxsize=None)
def last_commit(path):
    """(short hash, commit date) of the newest routes-repo commit touching `path`, or ("", "") when git cannot say."""
    p = Path(path)
    try:
        out = subprocess.run(["git", "-C", str(p.parent), "log", "-1", "--format=%h,%cs", "--", p.name],
                             capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "", ""
    h, _, d = out.partition(",")
    return h, d


def _cell(row, col):
    v = (row or {}).get(col)
    return "" if v is None else str(v).strip()


def sheet_mapped(row):
    return _cell(row, "RouteType") == MAPPED and _cell(row, "RouteAccuracy").lower() not in ("", "no route")


def cb_stamped(row, replacement=False):
    """The sheet row says CB added this route: RouteNotes carries the stamp apply_route_candidates.py writes and RouteCreator is CB (a tab without RouteCreator counts the notes alone)."""
    stamp = "CB: route replaced" if replacement else "CB: route"
    creator = _cell(row, "RouteCreator")
    return stamp in _cell(row, "RouteNotes") and (creator == "CB" or "RouteCreator" not in (row or {}))


def _sheet_words(row):
    return f"RouteType {_cell(row, 'RouteType') or 'blank'!r}, RouteAccuracy {_cell(row, 'RouteAccuracy') or 'blank'!r}"


def judge(rec, cand_path, row, commodity=None):
    """{"state", "applied", "disagree"} for one staged route candidate. `row` is the snapshot row (a dict by column name); `applied` is None or {by, at, commit?, sheet?}; `disagree` is None or a sentence for the card."""
    pid = rec.get("project_id") or ""
    repl = bool(rec.get("replacement"))
    state, rp = repo_state(cand_path, pid, commodity)
    applied = disagree = None
    mapped = sheet_mapped(row)
    if state == "same":
        h, d = last_commit(str(rp))
        if mapped:
            applied = {"by": "routes_repo", "at": d, "commit": h, "sheet": True}
        else:
            # only RouteType behind: the backfill; nothing written yet: the sheet half of the §8 apply
            fix = ("apply_route_candidates.py --backfill-route-type"
                   if _cell(row, "RouteAccuracy").lower() not in ("", "no route")
                   else "the sheet half of the §8 apply (apply_route_candidates.py)")
            disagree = (f"The routes repo holds this geometry (commit {h or 'unknown'}, {d or 'date unknown'}), "
                        f"but the sheet row says {_sheet_words(row)}. Fix the sheet columns with {fix}, not here.")
    elif row and cb_stamped(row, repl) and (state == "missing" or not repl):
        where = "has no file for this pipeline" if state == "missing" else "holds a different geometry from this candidate"
        disagree = (f"The sheet says CB added a route ({_sheet_words(row)}), but the routes repo {where}. "
                    "Check the routes repo before deciding.")
    m = rec.get("applied")
    if isinstance(m, dict) and m:
        applied = {"by": m.get("by") or "apply_route_candidates", "at": m.get("date") or "",
                   **({"commit": m["commit"]} if m.get("commit") else {})}
    return {"state": state, "applied": applied, "disagree": disagree}


def snapshot_rows(path):
    """ProjectID -> row dict (by column name) from a tracker snapshot CSV (header on the third line); the first row wins for a repeated id."""
    import csv
    rows = {}
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        for _ in range(2):
            next(rd, None)
        head = next(rd, [])
        for r in rd:
            d = dict(zip(head, r))
            rows.setdefault(d.get("ProjectID", ""), d)
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--staging", required=True, help="a staging dir holding route candidates")
    ap.add_argument("--snapshot", help="tracker snapshot CSV (default: the newest gas or oil one for the dir)")
    ap.add_argument("--commodity", choices=["gas", "oil"], help="default: from the batch dir name")
    a = ap.parse_args(argv)
    st = Path(a.staging)
    commodity = a.commodity or ("oil" if "-oil" in str(st) else "gas")
    pat = "GGIT_gas_snapshot_*.csv" if commodity == "gas" else "GOIT_oil*_snapshot_*.csv"
    snap = Path(a.snapshot) if a.snapshot else max((ROOT / "data").glob(pat), default=None)
    rows = snapshot_rows(snap) if snap else {}
    recs = json.loads((st / "staged_resolutions.json").read_text())["resolutions"]
    for r in recs:
        if r.get("class_out") != "ROUTE_CANDIDATE" or not r.get("geometry_file"):
            continue
        j = judge(r, st / r["geometry_file"], rows.get(r["project_id"]), commodity)
        tag = "applied" if j["applied"] else "DISAGREE" if j["disagree"] else "open"
        print(f"{r['project_id']}  {j['state']:8}  {tag}  {j['applied'] or ''}  {j['disagree'] or ''}".rstrip())


if __name__ == "__main__":
    main()
