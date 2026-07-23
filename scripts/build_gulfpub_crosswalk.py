#!/usr/bin/env python3
"""Flatten reconcile.py's match_diff.json into the flat gulfpub_crosswalk.json that the
deep-sweep workbook's <Cmdty>_GulfPub tab consumes (build_ref_workbook._gulfpub_view).

The reconciliation engine (ingest.py -> reconcile.py) emits match_diff.json with nested
ref/gem/signals objects; this collapses each overlap / addition / ambiguous into one flat
record with the GEM value beside its GulfPub counterpart, plus derived spec-disagreement
flags (status_conflict / diam_flag / len_flag) so a reviewer sees conflicts at a glance.
GulfPub (PE World Map / Petroleum Economist) is a Tier-2 source — this is read-and-flag
only; a single value here never reaches green, and nothing is applied.

Typical deep-sweep chain (scoped to one country/commodity):
    python scripts/ingest.py --source gulfpub --commodity gas --out batches/<scope>/staging/recon-<source>-<date>/
    python scripts/reconcile.py --source gulfpub --country Iraq --commodity gas \
        --staging batches/<scope>/staging/recon-<source>-<date>/
    python scripts/build_gulfpub_crosswalk.py --match-diff batches/<scope>/staging/recon-<source>-<date>/match_diff.json \
        --out batches/<scope>/staging/<deep-sweep-dir>/gulfpub_crosswalk.json

Drop the crosswalk into the deep-sweep staging dir; build_ref_workbook.py picks it up
automatically (gulfpub_crosswalk.json present -> the <Cmdty>_GulfPub tab is added).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from normalize import parse_number  # noqa: E402
except Exception:  # pragma: no cover - normalize should always import
    def parse_number(x):
        try:
            return float(str(x).replace(",", ""))
        except Exception:
            return None

_DIAM_TOL = 0.05    # <=5% diameter delta reads as "ok" (rounding / unit-print differences)
_LEN_TOL = 0.10     # <=10% length delta reads as "ok"


def _scalar(v):
    """GulfPub canonical fields are sometimes lists (source drift); Excel needs scalars."""
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return v

def _pid(gem: dict) -> str:
    pids = gem.get("project_ids") or ([gem.get("project_id")] if gem.get("project_id") else [])
    return ";".join(p for p in pids if p)


def _delta_flag(gem_val, gp_val, tol: float) -> str:
    """'ok' when both parse and agree within tol; 'DELTA N%' when they diverge; '' when a
    value is missing (nothing to compare)."""
    a, b = parse_number(gem_val), parse_number(gp_val)
    if a is None or b is None:
        return ""
    hi = max(abs(a), abs(b))
    if hi == 0:
        return "ok"
    delta = abs(a - b) / hi
    return "ok" if delta <= tol else f"DELTA {round(delta * 100)}%"


def _overlap_record(o: dict) -> dict:
    gem, ref = o.get("gem", {}), o.get("ref", {})
    gem_status = (gem.get("status") or "").strip()
    gp_status = (ref.get("status") or "").strip()
    return {
        "kind": "overlap",
        "gem_pid": _pid(gem),
        "gem_name": gem.get("pipeline_name", ""),
        "gem_segment": gem.get("segment_name", ""),
        "gulfpub_name": ref.get("name", ""),
        "match_conf": o.get("confidence", ""),
        "composite": o.get("composite", ""),
        "gem_status": gem_status,
        "gp_status": gp_status,
        "status_conflict": "CONFLICT" if (gem_status and gp_status and gem_status != gp_status) else "",
        "gem_diam": gem.get("diameter", ""),
        "gp_diam": ref.get("diameter", ""),
        "diam_flag": _delta_flag(gem.get("diameter"), ref.get("diameter"), _DIAM_TOL),
        "gem_len_km": gem.get("length_km", ""),
        "gp_len_km": ref.get("length_km", ""),
        "len_flag": _delta_flag(gem.get("length_km"), ref.get("length_km"), _LEN_TOL),
        "gem_route_acc": gem.get("route_accuracy", ""),
        "gp_start": ref.get("start", ""),
        "gp_end": ref.get("end", ""),
        "gp_has_geom": ref.get("has_geometry", False),
        "gp_operator": ref.get("operator", ""),
        "gp_owners": _scalar(ref.get("owners", "")),
        "gp_capacity": ref.get("capacity_raw") or ref.get("capacity", ""),
        "gp_startyear": ref.get("start_year", ""),
        "gp_desc": ref.get("description", ""),
    }


def _addition_record(a: dict) -> dict:
    ref = a.get("ref", {})
    return {
        "kind": "addition (GulfPub-only)",
        "gem_pid": "", "gem_name": "", "gem_segment": "",
        "gulfpub_name": ref.get("name", ""),
        "match_conf": a.get("confidence", "red"),
        "gp_status": (ref.get("status") or "").strip(),
        "gp_start": ref.get("start", ""),
        "gp_end": ref.get("end", ""),
        "gp_diam": ref.get("diameter", ""),
        "gp_len_km": ref.get("length_km", ""),
        "gp_has_geom": ref.get("has_geometry", False),
        "gp_operator": ref.get("operator", ""),
        "gp_owners": _scalar(ref.get("owners", "")),
        "gp_capacity": ref.get("capacity_raw") or ref.get("capacity", ""),
        "gp_startyear": ref.get("start_year", ""),
        "gp_desc": ref.get("description", ""),
    }


def _ambiguous_record(a: dict) -> dict:
    cands = a.get("candidates") or []
    cand_str = "; ".join(
        f"{';'.join(c.get('project_ids') or [])} ({round(c.get('composite', 0), 2)})"
        for c in cands)
    return {
        "kind": "ambiguous",
        "gulfpub_name": a.get("ref_name", ""),
        "candidates": cand_str,
    }


def build_crosswalk(diff: dict) -> dict:
    return {
        "overlaps": [_overlap_record(o) for o in diff.get("overlaps", [])],
        "additions": [_addition_record(a) for a in diff.get("additions", [])],
        "ambiguous": [_ambiguous_record(a) for a in diff.get("ambiguous", [])],
        "meta": diff.get("meta", {}),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--match-diff", required=True, help="reconcile.py match_diff.json")
    ap.add_argument("--out", required=True, help="destination gulfpub_crosswalk.json (usually the deep-sweep staging dir)")
    args = ap.parse_args()

    diff = json.loads(Path(args.match_diff).read_text())
    cw = build_crosswalk(diff)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cw, indent=1, ensure_ascii=False))
    print(f"wrote {out}  (overlaps={len(cw['overlaps'])} additions={len(cw['additions'])} "
          f"ambiguous={len(cw['ambiguous'])})")


if __name__ == "__main__":
    main()
