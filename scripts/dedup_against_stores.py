#!/usr/bin/env python3
"""Drop staged ref records that an earlier store of the same scope already proposes.

A recovery or re-sweep store (the Russia wiki-citation recovery pass, 2026-10-17) re-reads
sources an earlier batch may already have staged. A record here is an exact DUPLICATE when an
earlier store's record on the same unit (project_id, ref_col, sheet_row) proposes the same value
and already carries every URL this record proposes (URLs compared normalized: no fragment, no
trailing slash, lowercase host). Keeping both would put two lines for one unit in the review app.

    python scripts/dedup_against_stores.py --staging <new store> --against <store> [--against ...]
    python scripts/dedup_against_stores.py --staging <new store> --against ... --apply

Without --apply it only reports. With --apply the duplicates are removed from the new store's
staged_resolutions.json and written to dedup_dropped.json beside it (nothing is lost). A record
that proposes at least one URL the earlier store lacks is kept whole: refs are additive, and the
review app merges the URLs the cell already has.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_shard_coverage import _norm_url  # noqa: E402


def _key(r: dict) -> tuple:
    return (r.get("project_id"), r.get("ref_col"), r.get("sheet_row"))


def _val(r: dict) -> str:
    v = r.get("primary_value")
    return str(v).strip().lower() if v is not None else ""


def load(store: Path) -> list[dict]:
    p = store / "staged_resolutions.json"
    if not p.exists():
        return []
    return json.loads(p.read_text()).get("resolutions", [])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True, type=Path)
    ap.add_argument("--against", required=True, nargs="+", type=Path)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    earlier: dict[tuple, list[tuple[str, set[str], str]]] = {}
    for store in a.against:
        for r in load(store):
            if not r.get("proposed_refs"):
                continue
            earlier.setdefault(_key(r), []).append(
                (store.name, {_norm_url(u) for u in r["proposed_refs"]}, _val(r)))

    path = a.staging / "staged_resolutions.json"
    data = json.loads(path.read_text())
    keep, dropped = [], []
    for r in data.get("resolutions", []):
        refs = {_norm_url(u) for u in (r.get("proposed_refs") or [])}
        dup = None
        if refs:
            for name, prev_refs, prev_val in earlier.get(_key(r), []):
                if refs <= prev_refs and _val(r) == prev_val:
                    dup = name
                    break
        if dup:
            r["duplicate_of_store"] = dup
            dropped.append(r)
        else:
            keep.append(r)

    print(f"{len(data.get('resolutions', []))} records; {len(dropped)} exact duplicates of an earlier store"
          f"{' — removed' if a.apply else ' (report only; --apply to remove)'}")
    for r in dropped[:40]:
        print(f"  {r.get('project_id')} {r.get('ref_col')} row={r.get('sheet_row')} = {r.get('duplicate_of_store')}")
    if len(dropped) > 40:
        print(f"  ... {len(dropped) - 40} more")
    if a.apply and dropped:
        data["resolutions"] = keep
        data.setdefault("meta", {})["dedup_against"] = [s.name for s in a.against]
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False))
        (a.staging / "dedup_dropped.json").write_text(json.dumps(
            {"against": [str(s) for s in a.against], "dropped": dropped}, indent=1, ensure_ascii=False))
        print(f"wrote {path} and {a.staging / 'dedup_dropped.json'}")


if __name__ == "__main__":
    main()
