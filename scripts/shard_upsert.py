#!/usr/bin/env python3
"""Save deep-sweep research to a shard AS IT HAPPENS, one finished record at a time.

    python scripts/shard_upsert.py --staging <dir> --pid P#### --init
    python scripts/shard_upsert.py --staging <dir> --pid P#### --fill @unit.json
    python scripts/shard_upsert.py --staging <dir> --pid P#### --fill '{"ref_col": ...}'
    python scripts/shard_upsert.py --staging <dir> --pid P#### --validity @v.json
    python scripts/shard_upsert.py --staging <dir> --pid P#### --status-review @s.json
    python scripts/shard_upsert.py --staging <dir> --pid P#### --lead @l.json
    python scripts/shard_upsert.py --staging <dir> --pid P#### --summary "<one line>"
    python scripts/shard_upsert.py --staging <dir> --pid P#### --remaining

Why this exists (2026-09-14, Russia R1 pilot): the deep-sweep contract asked agents to
"write the shard early and update it as you go", and most read that as optional — 7 of the
9 agents running at the time had no shard on disk after 30+ minutes of research. An agent
that hits its context limit mid-row then loses the whole row, and its replacement starts
from zero: a 15-unit row that dies on unit 12 costs 27 units of research. With this helper
every finished unit is on disk the moment it is resolved, `--remaining` tells a replacement
agent exactly which units are still owed, and the replacement researches only those.

Rules the helper enforces so incremental saving cannot degrade the shard:
- `--init` builds the skeleton (project_id, pipeline_name, sheet_row, wiki) from the
  worklist and is idempotent — it never touches an existing shard's records.
- A fills[] record is keyed the way check_shard_coverage.py keys worklist units:
  `ref_col`, disambiguated by `sheet_row` (multi-segment rows) — an upsert on the same key
  REPLACES the earlier record, so an agent that first wrote UNRESOLVED and later found a
  source overwrites cleanly rather than leaving two records for one unit.
- validity[] keys on (segment_name, concern_type); status_reviews[] on sheet_row (then
  segment_name); cross_row_leads[] on (project_id, url). Same replace-on-key semantics.
- Every write is atomic (temp file in the same dir + os.replace), so a crash mid-write
  leaves the previous complete shard, never a truncated one.
- Each call prints one line: how many owed units the shard now reports on, so the agent
  sees its own progress. It never validates content — check_shard_coverage.py (which the
  contract still blocks on before finishing) remains the gate.

Only FINISHED records belong here. Do not upsert a placeholder to "reserve" a unit: an
UNRESOLVED with empty researcher_notes still fails coverage as a silent record, and an
UNRESOLVED with notes reads downstream as "searched, found nothing" — which, if the agent
meant to come back and never did, is a false statement on the deliverable.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_shard_coverage import check, load_units  # noqa: E402

LIST_KEYS = ("validity", "fills", "status_reviews", "cross_row_leads")


def _load_payload(arg: str) -> list[dict]:
    if arg == "-":
        text = sys.stdin.read()
    elif arg.startswith("@"):
        text = Path(arg[1:]).read_text()
    else:
        text = arg
    obj = json.loads(text)
    if isinstance(obj, dict):
        return [obj]
    if isinstance(obj, list) and all(isinstance(x, dict) for x in obj):
        return obj
    raise SystemExit("payload must be a JSON object or a list of objects")


def _skeleton(staging: Path, pid: str) -> dict:
    units = load_units(staging).get(pid, [])
    if not units and (staging / "worklist_full.json").exists():
        # Lean pass (scripts/lean_worklist.py): a PID whose every unit was deferred still gets
        # a shard for its validity + status-review records; take the skeleton from the full list.
        units = [u for u in json.loads((staging / "worklist_full.json").read_text()).get("units") or []
                 if u.get("project_id") == pid]
    if not units:
        raise SystemExit(f"{pid}: no worklist units in {staging}/worklist.json — wrong --staging or --pid?")
    u = units[0]
    try:
        sheet_row = int(u.get("sheet_row"))
    except (TypeError, ValueError):
        sheet_row = u.get("sheet_row")
    return {
        "project_id": pid,
        "pipeline_name": u.get("pipeline_name") or "",
        "sheet_row": sheet_row,
        "wiki": u.get("wiki") or "",
        "validity": [],
        "fills": [],
        "status_reviews": [],
        "cross_row_leads": [],
        "summary": "",
    }


def _read(path: Path, staging: Path, pid: str) -> dict:
    if path.exists():
        try:
            shard = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            raise SystemExit(f"{path} does not parse ({e}) — fix or remove it before upserting")
        if not isinstance(shard, dict):
            raise SystemExit(f"{path} is not a JSON object")
        for k in LIST_KEYS:
            if not isinstance(shard.get(k), list):
                shard[k] = []
        shard.setdefault("project_id", pid)
        shard.setdefault("summary", "")
        return shard
    return _skeleton(staging, pid)


def _write(path: Path, shard: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.stem}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(shard, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _key_fill(r: dict) -> tuple:
    return (str(r.get("ref_col") or ""), str(r.get("sheet_row") or ""),
            str(r.get("primary_value_col") or "") if not (r.get("ref_col") or "").strip() else "")


def _key_validity(r: dict) -> tuple:
    return (str(r.get("segment_name") or ""), str(r.get("concern_type") or ""))


def _key_status(r: dict) -> tuple:
    return (str(r.get("sheet_row") or ""), str(r.get("segment_name") or ""))


def _key_lead(r: dict) -> tuple:
    return (str(r.get("project_id") or ""), str(r.get("url") or ""))


KEYS = {"fills": _key_fill, "validity": _key_validity,
        "status_reviews": _key_status, "cross_row_leads": _key_lead}


def upsert(shard: dict, kind: str, records: list[dict]) -> tuple[int, int]:
    keyf = KEYS[kind]
    existing = shard[kind]
    index = {keyf(r): i for i, r in enumerate(existing)}
    replaced = added = 0
    for r in records:
        k = keyf(r)
        if k in index:
            existing[index[k]] = r
            replaced += 1
        else:
            index[k] = len(existing)
            existing.append(r)
            added += 1
    return added, replaced


def progress_line(staging: Path, pid: str, shard: dict) -> str:
    units = load_units(staging).get(pid, [])
    unreported, silent, malformed = check(units, list(shard.get("fills") or []))
    done = len(units) - len(unreported)
    extra = []
    if silent:
        extra.append(f"{len(silent)} UNRESOLVED with empty notes")
    if malformed:
        extra.append(f"{len(malformed)} unmergeable")
    tail = f" ({'; '.join(extra)})" if extra else ""
    return f"{pid}: {done}/{len(units)} owed units reported{tail}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True, type=Path)
    ap.add_argument("--pid", required=True)
    ap.add_argument("--init", action="store_true", help="create the skeleton shard if absent")
    ap.add_argument("--fill", help="fills[] record(s): JSON, @file, or - for stdin")
    ap.add_argument("--validity", help="validity[] record(s)")
    ap.add_argument("--status-review", dest="status_review", help="status_reviews[] record(s)")
    ap.add_argument("--lead", help="cross_row_leads[] record(s)")
    ap.add_argument("--summary", help="set the shard's one-line summary")
    ap.add_argument("--remaining", action="store_true",
                    help="list the worklist units this shard does not yet report on, then exit")
    a = ap.parse_args()

    staging = a.staging
    path = staging / "rows" / f"{a.pid}.json"
    shard = _read(path, staging, a.pid)

    if a.remaining:
        units = load_units(staging).get(a.pid, [])
        unreported, silent, malformed = check(units, list(shard.get("fills") or []))
        print(progress_line(staging, a.pid, shard))
        for u in unreported:
            print(f"  OWED  {str(u.get('ref_col') or '(no ref col)'):24s} [{u.get('class')}] "
                  f"row={u.get('sheet_row')} value={str(u.get('primary_value') or '')[:60]!r}")
        for f in silent:
            print(f"  FIX   {str(f.get('ref_col') or ''):24s} UNRESOLVED with empty researcher_notes")
        for m in malformed:
            print(f"  FIX   {str(m.get('ref_col') or ''):24s} {m.get('why')}")
        if not shard.get("validity"):
            print("  OWED  validity[]                (at least one object per pipeline)")
        if not path.exists():
            print(f"  (no shard on disk yet — run --init)")
        return

    changed = []
    if a.init and not path.exists():
        changed.append("init")
    for kind, arg in (("fills", a.fill), ("validity", a.validity),
                      ("status_reviews", a.status_review), ("cross_row_leads", a.lead)):
        if arg:
            added, replaced = upsert(shard, kind, _load_payload(arg))
            changed.append(f"{kind} +{added}" + (f" ~{replaced}" if replaced else ""))
    if a.summary is not None:
        shard["summary"] = a.summary
        changed.append("summary")

    if not changed and path.exists():
        print(progress_line(staging, a.pid, shard) + "  (nothing to write)")
        return
    _write(path, shard)
    print(progress_line(staging, a.pid, shard) + f"  [{', '.join(changed) or 'written'}]")


if __name__ == "__main__":
    main()
