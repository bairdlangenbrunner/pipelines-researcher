#!/usr/bin/env python3
"""Split a handoff-packet `worklist.json` into system briefs for the Leg-3 research fan-out.

Promoted 2026-09-03 from five per-batch copies (pakistan, libya, india, ukraine, kazakhstan
`staging/qc/build_leg3_briefs.py`). The emitter never changed between countries; only the
GROUPS table did — so the emitter lives here and the grouping stays in the run dir as data.

    python scripts/build_leg3_briefs.py --staging batches/<scope>/staging/qc/ \
        [--groups groups.json | groups.py] [--csv data/GGIT_gas_snapshot_<date>.csv] \
        [--fields Col1 Col2 ...] [--out <dir>]

`build_qc_staging.py` emits `worklist.json` as a flat list of rows × flags, but the flags
usually collapse into a few SYSTEM-shaped questions (one operator for every string of a
trunk, one wiki page covering a multi-segment system, one corridor's length ratios).
Rows that share a source ladder are briefed TOGETHER — one agent's find on a trunk answers
every string in it. Each brief carries its rows' flags verbatim plus the current sheet
values, so the agent answers a specific question rather than re-deriving the flag.

Groups data — two accepted shapes:
  * `groups.json`: a list of `{"key", "title", "source_ladder", "pids": [...]}`.
  * `groups.py`: a module defining `GROUPS = [(key, title, source_ladder, [pids]), ...]`
    — the in-code shape of the kazakhstan / ukraine / india copies, which still load.
Coverage must equal the worklist EXACTLY: a PID in two briefs, an unbriefed worklist row,
or a briefed PID that is not on the worklist all abort.

Output: `<staging>/rows/_briefs/<key>.json` per group + `_index.json`, the shape the
`leg3_baked.js` workflows read (verified identical to the Kazakhstan run, `_index.json`'s
`generated` aside).
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]

SNAPSHOT_GLOB = {"gas": "GGIT_gas_snapshot_*.csv", "oil": "GOIT_oil_ngl_snapshot_*.csv"}

# The sheet columns a brief carries as `current` — enough to answer a flag without opening
# the tracker. Override with --fields when a country's questions need other columns.
DEFAULT_FIELDS = ["PipelineName", "SegmentName", "Status", "StartYear1", "LengthKnownKm",
                  "Capacity", "CapacityUnits", "Diameter", "Owner", "RouteAccuracy",
                  "StartCountryOrArea", "EndCountryOrArea", "StartLocation", "EndLocation",
                  "StartState/Province", "EndState/Province", "FuelSource",
                  "PipelineNetworkGrouping"]


def _latest_snapshot(commodity: str) -> Path:
    hits = sorted(glob.glob(str(REPO / "data" / SNAPSHOT_GLOB[commodity])))
    if not hits:
        raise SystemExit(f"no {SNAPSHOT_GLOB[commodity]} in data/ — run scripts/refresh_csvs.sh")
    return Path(hits[-1])


def load_groups(src: Path) -> list[tuple[str, str, str, list[str]]]:
    if src.suffix == ".json":
        data = json.loads(src.read_text())
        return [(g["key"], g.get("title", ""), g.get("source_ladder", ""), list(g["pids"])) for g in data]
    if src.suffix == ".py":
        spec = importlib.util.spec_from_file_location("_groups_mod", src)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        raw = getattr(mod, "GROUPS", None)
        if not isinstance(raw, list):
            raise SystemExit(f"{src} defines no GROUPS list")
        return [(k, t, l, list(p)) for k, t, l, p in raw]
    raise SystemExit(f"unrecognised groups source {src} (want .json or .py)")


def _default_groups(staging: Path) -> Path:
    for name in ("groups.json", "groups.py"):
        p = staging / name
        if p.exists():
            return p
    raise SystemExit(f"no groups.json / groups.py in {staging} — pass --groups")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True, help="the qc run dir holding worklist.json")
    ap.add_argument("--groups", help="groups.json | groups.py (default: found in --staging)")
    ap.add_argument("--commodity", choices=("gas", "oil"), default="gas")
    ap.add_argument("--csv", help="tracker snapshot (default: newest in data/ for the commodity)")
    ap.add_argument("--fields", nargs="+", help="sheet columns to carry as `current` (default: the standard 18)")
    ap.add_argument("--out", help="briefs dir (default: <staging>/rows/_briefs)")
    args = ap.parse_args()

    staging = Path(args.staging)
    csv = Path(args.csv) if args.csv else _latest_snapshot(args.commodity)
    if not csv.is_absolute() and not csv.exists():
        csv = REPO / csv
    fields = args.fields or DEFAULT_FIELDS
    briefs_dir = Path(args.out) if args.out else staging / "rows" / "_briefs"
    groups = load_groups(Path(args.groups) if args.groups else _default_groups(staging))

    worklist = json.loads((staging / "worklist.json").read_text())["rows"]
    by_pid = {r["project_id"]: r for r in worklist}

    grouped = [p for _, _, _, pids in groups for p in pids]
    if len(grouped) != len(set(grouped)):
        dupes = {p for p in grouped if grouped.count(p) > 1}
        raise SystemExit(f"PID in two briefs: {sorted(dupes)}")
    missing = sorted(set(by_pid) - set(grouped))
    extra = sorted(set(grouped) - set(by_pid))
    if missing or extra:
        raise SystemExit(
            f"brief coverage is not exactly the worklist — unbriefed: {missing}; "
            f"not in worklist: {extra}"
        )

    df = pd.read_csv(csv, header=2, low_memory=False, keep_default_na=False, na_values=[])
    df["_sheet_row"] = df.index + 4
    rows_by_pid = {r["ProjectID"]: r for _, r in df.iterrows()}
    absent = sorted(p for p in grouped if p not in rows_by_pid)
    if absent:
        raise SystemExit(f"not in {csv.name}: {absent} — snapshot drift, re-check")

    briefs_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for key, title, ladder, pids in groups:
        rows = []
        for p in pids:
            src = rows_by_pid[p]
            rows.append({
                "project_id": p,
                "sheet_row": int(src["_sheet_row"]),
                "current": {f: str(src.get(f, "") or "") for f in fields},
                "flags": by_pid[p]["flags"],
                "wiki": by_pid[p].get("wiki", ""),
            })
        brief = {
            "brief": key,
            "title": title,
            "source_ladder": ladder,
            "n_rows": len(rows),
            "questions": sorted({f["field"] for r in rows for f in r["flags"]}),
            "rows": rows,
        }
        (briefs_dir / f"{key}.json").write_text(json.dumps(brief, indent=1, ensure_ascii=False))
        written.append((key, len(rows), sorted(brief["questions"])))

    (briefs_dir / "_index.json").write_text(json.dumps({
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_briefs": len(groups),
        "n_rows": len(grouped),
        "briefs": [{"brief": k, "n_rows": n, "questions": q} for k, n, q in written],
    }, indent=1, ensure_ascii=False))

    print(f"wrote {len(written)} briefs covering {len(grouped)}/{len(by_pid)} worklist rows -> {briefs_dir}")
    width = max((len(k) for k, _, _ in written), default=8)
    for k, n, q in written:
        print(f"  {n:2d}  {k:{width}s} {','.join(q)}")


if __name__ == "__main__":
    main()
