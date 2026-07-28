#!/usr/bin/env python3
"""Flatten reconcile.py's match_diff.json into the flat crosswalk a sweep workbook's
<Cmdty>_<Source> tab consumes (build_ref_workbook._recon_view).

SOURCE-AGNOSTIC by design. This replaces build_gulfpub_crosswalk.py, which hard-coded
GulfPub in its field names and so could only ever surface one dataset. That was the
structural reason the Iraq OSM reconciliation produced no workbook tab and its 52
features were never triaged: the engine ran, wrote match_diff.json, and had nowhere to
put the answer. Any registered source now flows to a tab by running this once per
source into the sweep's staging dir.

    python scripts/ingest.py --source osm --commodity gas --country Iraq \
        --out batches/<scope>/staging/recon-osm-<date>/
    python scripts/reconcile.py --source osm --country Iraq --commodity gas \
        --staging batches/<scope>/staging/recon-osm-<date>/
    python scripts/build_recon_crosswalk.py \
        --match-diff batches/<scope>/staging/recon-osm-<date>/match_diff.json \
        --out batches/<scope>/staging/<sweep-dir>/recon_osm_crosswalk.json

build_ref_workbook.py globs recon_*_crosswalk.json out of the staging dir, so dropping
the file in is the whole wiring step.

What each row carries beyond the raw diff:
  * `disposition` — for an unmatched reference: is this candidate GEOMETRY for a
    routeless GEM row, a fragment of a tracked line, a near miss, or a real discovery?
    A reference route is presumptively real pipe; the flat "addition" bucket this
    replaces let 52 traces be filed as one undifferentiated pile.
  * `coverage` — 'partial' when the reference covers a sliver of the GEM row, so a
    0.1 km OSM stub is never read as corroborating a 105 km pipeline.
  * `license` — from the source manifest. OSM is ODbL share-alike; whether its
    coordinates may ship in a GEM route is Baird's call, never laundered into an
    unlabelled value.
Nothing here is applied, and a single Tier-2/3 value never reaches green alone.
"""
from __future__ import annotations

import argparse
import json
import re
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

# What a reviewer should DO with each disposition, spelled out in the workbook rather
# than left to be inferred from a bucket name.
DISPOSITION_ACTION = {
    "ROUTE_FOR_EXISTING":
        "Candidate GEOMETRY for the named routeless GEM row — verify the identification, "
        "then route via a human routes-repo PR. Never auto-replace.",
    "FRAGMENT_OF_EXISTING":
        "Partial trace of a line GEM already tracks. Not a discovery; usable as route "
        "corroboration only, and only for the stretch it covers.",
    "NEAR_MISS":
        "Scored just under the match threshold. Adjudicate by hand — a false Addition "
        "hides a real one.",
    "DISCOVERY_CANDIDATE":
        "Real pipe with no plausible GEM match. Check for an existing row under another "
        "name (-> OtherEnglishNames) BEFORE treating as a new entry.",
}


def _scalar(v):
    """Canonical fields are sometimes lists (source drift); Excel needs scalars."""
    if isinstance(v, list):
        return "; ".join(str(x) for x in v)
    return v


def _pid(gem: dict) -> str:
    pids = gem.get("project_ids") or ([gem.get("project_id")] if gem.get("project_id") else [])
    return ";".join(p for p in pids if p)


def _delta_flag(gem_val, ref_val, tol: float) -> str:
    """'ok' when both parse and agree within tol; 'DELTA N%' when they diverge; '' when a
    value is missing (nothing to compare)."""
    a, b = parse_number(gem_val), parse_number(ref_val)
    if a is None or b is None:
        return ""
    hi = max(abs(a), abs(b))
    if hi == 0:
        return "ok"
    delta = abs(a - b) / hi
    return "ok" if delta <= tol else f"DELTA {round(delta * 100)}%"


def _ref_fields(ref: dict) -> dict:
    return {
        "ref_id": ref.get("ref_id", ""),
        "ref_name": ref.get("name", ""),
        "ref_status": (ref.get("status") or "").strip(),
        "ref_start": ref.get("start", ""),
        "ref_end": ref.get("end", ""),
        "ref_diam": ref.get("diameter", ""),
        "ref_len_km": ref.get("geodesic_km") or ref.get("length_km", ""),
        "ref_has_geom": ref.get("has_geometry", False),
        "ref_operator": ref.get("operator", ""),
        "ref_owners": _scalar(ref.get("owners", "")),
        "ref_capacity": ref.get("capacity_raw") or ref.get("capacity", ""),
        "ref_startyear": ref.get("start_year", ""),
        "ref_desc": ref.get("description", ""),
        "ref_url": ref.get("source_url", ""),
    }


def _overlap_record(o: dict, license_note: str) -> dict:
    gem, ref = o.get("gem", {}), o.get("ref", {})
    gem_status = (gem.get("status") or "").strip()
    ref_status = (ref.get("status") or "").strip()
    cov = o.get("coverage", "")
    rec = {
        "kind": "overlap",
        "disposition": "",
        "gem_pid": _pid(gem),
        "gem_name": gem.get("pipeline_name", ""),
        "gem_segment": gem.get("segment_name", ""),
        "match_conf": o.get("confidence", ""),
        "composite": o.get("composite", ""),
        "coverage": cov,
        "coverage_ratio": o.get("coverage_ratio", ""),
        "gem_status": gem_status,
        "status_conflict": "CONFLICT" if (gem_status and ref_status and gem_status != ref_status) else "",
        "gem_diam": gem.get("diameter", ""),
        "diam_flag": _delta_flag(gem.get("diameter"), ref.get("diameter"), _DIAM_TOL),
        "gem_len_km": gem.get("length_km", ""),
        # A partial trace covers a sliver of the row, so of course the lengths differ —
        # flagging that is a guaranteed false positive, and it was loud enough to bury the
        # real findings (5 of 8 Iraq gas OSM overlaps). Diameter still compares: it is a
        # local property, unaffected by how much of the line the trace covers.
        "len_flag": "" if cov == "partial" else _delta_flag(
            gem.get("length_km"), ref.get("geodesic_km") or ref.get("length_km"), _LEN_TOL),
        "gem_route_acc": gem.get("route_accuracy", ""),
        "route_iou": o.get("route_iou", ""),
        "route_replacement_candidate": "YES" if o.get("route_replacement_candidate") else "",
        "trace_footprint": o.get("trace_footprint", ""),
        "license": license_note,
        "action": ("PARTIAL COVERAGE — corroborates this row's LOCATION only, not its length, "
                   "capacity or extent." if cov == "partial" else ""),
        **_ref_fields(ref),
    }
    return rec


def _addition_record(a: dict, license_note: str) -> dict:
    ref = a.get("ref", {})
    disp = a.get("disposition", "")
    bg = a.get("best_guess") or {}
    return {
        "kind": "unmatched",
        "disposition": disp,
        # The nearest GEM row is carried even though this is unmatched — for
        # ROUTE_FOR_EXISTING / FRAGMENT it IS the finding, and for a discovery it is the
        # row to rule out first.
        "gem_pid": ";".join(bg.get("project_ids") or []),
        "gem_name": bg.get("name", ""),
        "gem_segment": "",
        "match_conf": a.get("confidence", "red"),
        "composite": bg.get("composite", ""),
        "coverage": "", "coverage_ratio": "",
        "gem_status": "", "status_conflict": "",
        "gem_diam": "", "diam_flag": "", "gem_len_km": "",
        "gem_route_acc": bg.get("route_accuracy", ""),
        "route_iou": "", "route_replacement_candidate": "",
        "trace_footprint": a.get("trace_footprint", ""),
        "license": license_note,
        "action": DISPOSITION_ACTION.get(disp, ""),
        "note": a.get("note", ""),
        **_ref_fields(ref),
    }


def _ambiguous_record(a: dict, license_note: str) -> dict:
    cands = a.get("candidates") or []
    return {
        "kind": "ambiguous",
        "disposition": "",
        "ref_name": a.get("ref_name", ""),
        "ref_id": a.get("ref_id", ""),
        "license": license_note,
        "candidates": "; ".join(
            f"{';'.join(c.get('project_ids') or [])} ({round(c.get('composite', 0), 2)})"
            for c in cands),
        "action": "Two unrelated GEM systems score alike — pick one by hand before using this row.",
    }


def _license_note(source: str) -> str:
    """provenance.license from the source manifest, if it declares one."""
    try:
        from ingest import load_manifest
        manifest, _ = load_manifest(source)
    except Exception:
        return ""
    lic = ((manifest.get("provenance") or {}).get("license") or "").strip()
    return " ".join(lic.split())


def build_crosswalk(diff: dict) -> dict:
    meta = diff.get("meta", {}) or {}
    source = meta.get("source", "")
    lic = _license_note(source)
    return {
        "source": source,
        "display_name": meta.get("display_name") or source,
        "source_tier": meta.get("source_tier"),
        "license": lic,
        "overlaps": [_overlap_record(o, lic) for o in diff.get("overlaps", [])],
        "additions": [_addition_record(a, lic) for a in diff.get("additions", [])],
        "ambiguous": [_ambiguous_record(a, lic) for a in diff.get("ambiguous", [])],
        # Carried verbatim so the tab's README line can state whether the matcher had
        # live signal — a zero-overlap run means nothing without it.
        "diagnostics": meta.get("diagnostics", {}),
        "meta": meta,
    }


def default_out(staging: Path, source: str) -> Path:
    slug = re.sub(r"[^a-z0-9]+", "_", source.lower()).strip("_") or "source"
    return staging / f"recon_{slug}_crosswalk.json"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--match-diff", required=True, help="reconcile.py match_diff.json")
    ap.add_argument("--out", help="destination recon_<source>_crosswalk.json; with --sweep-dir "
                                  "the name is derived from the source")
    ap.add_argument("--sweep-dir", help="sweep staging dir to write recon_<source>_crosswalk.json into")
    args = ap.parse_args()

    if not (args.out or args.sweep_dir):
        ap.error("give --out or --sweep-dir")

    diff = json.loads(Path(args.match_diff).read_text())
    cw = build_crosswalk(diff)
    out = Path(args.out) if args.out else default_out(Path(args.sweep_dir), cw["source"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cw, indent=1, ensure_ascii=False))

    from collections import Counter
    disp = Counter(a["disposition"] for a in cw["additions"] if a["disposition"])
    print(f"wrote {out}  (source={cw['source']} tier={cw['source_tier']} "
          f"overlaps={len(cw['overlaps'])} unmatched={len(cw['additions'])} "
          f"ambiguous={len(cw['ambiguous'])})")
    if disp:
        print("  dispositions: " + ", ".join(f"{k}={v}" for k, v in disp.most_common()))
    for e in (cw.get("diagnostics") or {}).get("escalations", []):
        print(f"  !! {e['code']}: {e['detail']}", file=sys.stderr)


if __name__ == "__main__":
    main()
