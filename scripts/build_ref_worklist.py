#!/usr/bin/env python3
"""Reference-sweep step 1: scan a country+tracker scope and emit a worklist of every
ref-bearing data point that needs work — blank `[ref]` cells whose value is filled
(MISSING_REF), and filled `[ref]` cells to re-verify (HAS_REF). Owner/Parent have no
`[ref]` column so they're MISSING_REF_NO_COLUMN (corroboration → ResearcherNotes).

Pairing comes from ref_pairs.discover_ref_pairs (group-walk over the FRESH header).
With --verify-existing, every existing ref URL is HTTP-checked up front (deterministic,
no agent tokens) so most HAS_REF units pre-classify as live vs dead before any research.

    python scripts/build_ref_worklist.py --tracker oil --country "Saudi Arabia" \
        --verify-existing --out batches/staging/ref-sweep-saudi-arabia/worklist.json

SheetRow = read_csv(header=2) index + 4. We deliberately do NOT use match.load_gem_df
(it reset_index'es, which breaks that mapping) — we replicate its buffer-row drop while
preserving the original index.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import normalize as N  # noqa: E402
import paths  # noqa: E402
from ref_pairs import discover_ref_pairs  # noqa: E402
from url_verifier import surface_forms, verify_many  # noqa: E402

_URL_RE = re.compile(r"https?://[^\s<>\"\]]+")
_YEAR_RE = re.compile(r"^(19|20)\d{2}$")


def _load_indexed(csv: str) -> pd.DataFrame:
    """Load a GEM tracker (header at row index 2), drop buffer/blank rows, but KEEP the
    original index so SheetRow = index + 4 holds."""
    df = pd.read_csv(csv, header=2, low_memory=False, dtype=str).fillna("")
    if "PipelineName" in df.columns:
        df = df[df["PipelineName"].str.strip() != ""]
    return df


def _extract_urls(cell: str) -> list[str]:
    """Pull http(s) URLs out of a ref cell (may hold several + free text), trimming
    trailing punctuation."""
    out: list[str] = []
    for m in _URL_RE.findall(cell or ""):
        u = m.rstrip(".,;)")
        if u and u not in out:
            out.append(u)
    return out


def _numericish(value: str) -> bool:
    """Whether a value is specific enough for a deterministic 'page contains it' check
    (numbers, years, status vocab). Free-text place names/owners are left to the agent."""
    v = (value or "").strip()
    if not v:
        return False
    return (N.parse_number(v) is not None) or bool(_YEAR_RE.match(v)) or (v.lower() in N.GEM_STATUSES)


def _classify(kind: str, ref_col, any_value_filled: bool, current_ref: str) -> str:
    if not any_value_filled:
        return "SKIP"
    if kind == "owner" or ref_col is None:
        return "MISSING_REF_NO_COLUMN"
    return "HAS_REF" if current_ref.strip() else "MISSING_REF"


def build(csv: str, country: str | None, statuses: set[str] | None,
          verify_existing: bool) -> dict:
    df = _load_indexed(csv)
    cols = set(df.columns)
    if country:
        want = N.normalize_country(country)
        df = df[df["CountriesOrAreas"].map(lambda s: want in N.split_countries(s))]
    if statuses:
        df = df[df["Status"].map(lambda s: str(s).strip().lower() in statuses)]

    pairs = [p for p in discover_ref_pairs(list(df.columns))
             if all(c in cols for c in p["value_cols"])]

    units: list[dict] = []
    skip_count = 0
    for idx, row in df.iterrows():
        sheet_row = int(idx) + 4
        pid = str(row.get("ProjectID", "")).strip()
        pname = str(row.get("PipelineName", "")).strip()
        sname = str(row.get("SegmentName", "")).strip()
        wiki = str(row.get("Wiki", "")).strip()
        for p in pairs:
            ref_col = p["ref_col"]
            value_cols = p["value_cols"]
            values = {c: str(row.get(c, "")).strip() for c in value_cols
                      if str(row.get(c, "")).strip()}
            current_ref = str(row.get(ref_col, "")).strip() if ref_col else ""
            klass = _classify(p["kind"], ref_col, bool(values), current_ref)
            if klass == "SKIP":
                skip_count += 1
                continue
            primary_col = p["primary_value_col"]
            primary_value = str(row.get(primary_col, "")).strip() if primary_col else ""
            if not primary_value and values:
                primary_value = next(iter(values.values()))
            units.append({
                "project_id": pid,
                "sheet_row": sheet_row,
                "pipeline_name": pname,
                "segment_name": sname,
                "wiki": wiki,
                "ref_col": ref_col,
                "value_cols": value_cols,
                "primary_value_col": primary_col,
                "values": values,
                "primary_value": primary_value,
                "current_ref": current_ref,
                "class": klass,
                "kind": p["kind"],
                "irregular": p["irregular"],
                "existing_ref_checks": [],
                "value_checked": False,
            })

    if verify_existing:
        _verify_existing(units)

    by_class: dict[str, int] = {}
    for u in units:
        by_class[u["class"]] = by_class.get(u["class"], 0) + 1
    dead = sum(1 for u in units if u["class"] == "HAS_REF"
               and any(not c["ok"] for c in u["existing_ref_checks"]))
    live = sum(1 for u in units if u["class"] == "HAS_REF"
               and u["existing_ref_checks"] and all(c["ok"] for c in u["existing_ref_checks"]))
    return {
        "scope": {
            "csv": Path(csv).name,
            "country": country or "global",
            "statuses": sorted(statuses) if statuses else "all",
            "rows": int(df.shape[0]),
            "pairs": len(pairs),
            "verify_existing": verify_existing,
        },
        "summary": {
            "units": len(units),
            "by_class": by_class,
            "skip": skip_count,
            "has_ref_all_live": live,
            "has_ref_with_dead": dead,
        },
        "units": units,
    }


def _verify_existing(units: list[dict]) -> None:
    """HTTP-check every existing ref URL (per unit, with the value's surface forms when
    the value is numeric/year/status). Mutates units in place."""
    for u in units:
        if u["class"] != "HAS_REF":
            continue
        urls = _extract_urls(u["current_ref"])
        if not urls:
            u["existing_ref_checks"] = []
            u["value_checked"] = False
            continue
        checked = _numericish(u["primary_value"])
        any_of = surface_forms(u["primary_value"]) if checked else None
        results = verify_many(urls, any_of=any_of)
        u["existing_ref_checks"] = [
            {"url": url, **results.get(url, {"ok": False, "status": None, "reason": "not checked"})}
            for url in urls
        ]
        u["value_checked"] = checked


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tracker", required=True, choices=["oil", "gas"])
    ap.add_argument("--country")
    ap.add_argument("--status", help="comma-separated Status filter (e.g. proposed,construction)")
    ap.add_argument("--csv", help="GEM CSV (default: latest snapshot for the tracker)")
    ap.add_argument("--verify-existing", action="store_true",
                    help="HTTP-check existing ref URLs up front (deterministic, no agent tokens)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    csv = args.csv
    if not csv:
        pat = "GOIT_oil_ngl_snapshot_*.csv" if args.tracker == "oil" else "GGIT_gas_snapshot_*.csv"
        files = sorted(glob.glob(str(paths.repo_root() / "data" / pat)))
        if not files:
            sys.exit("no GEM snapshot found — run ./scripts/refresh_csvs.sh")
        csv = files[-1]

    statuses = None
    if args.status:
        statuses = {s.strip().lower() for s in args.status.split(",") if s.strip()}

    wl = build(csv, args.country, statuses, args.verify_existing)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(wl, indent=2, ensure_ascii=False))

    s, m = wl["scope"], wl["summary"]
    print(f"wrote {out}")
    print(f"  scope: {s['country']} | {args.tracker} | {s['rows']} rows | "
          f"statuses={s['statuses']} | {s['pairs']} ref-pairs")
    print(f"  units: {m['units']}  by_class={m['by_class']}  (skipped {m['skip']} blank)")
    if args.verify_existing:
        print(f"  existing refs: {m['has_ref_all_live']} all-live, {m['has_ref_with_dead']} with dead/missing link(s)")


if __name__ == "__main__":
    main()
