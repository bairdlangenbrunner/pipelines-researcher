#!/usr/bin/env python3
"""Reference-sweep step 1: scan a country (optionally sub-country via --province /
--exclude-network-regex, e.g. China's province batches) + tracker scope and emit a worklist of every
ref-bearing data point that needs work — blank `[ref]` cells whose value is filled
(MISSING_REF), and filled `[ref]` cells to re-verify (HAS_REF).

Owner/operator refs do NOT live on the tracker tab (it has the Owner/Parent values but no
`[ref]` column). They live on the separate **ProjectID-keyed "Pipeline operators/owners"
tab** (GID 1489950650, header at CSV row index 1), in its `Operator [ref]` / `Owner [ref]`
columns. We join that tab by ProjectID for the in-scope rows and emit real operator/owner
ref units (tab='operators_owners', kind='operator'|'owner') — classified MISSING_REF /
HAS_REF just like tracker units. The tracker's synthetic `kind='owner'` placeholder pair is
dropped here in favour of those.

Tracker pairing comes from ref_pairs.discover_ref_pairs; OO pairing from
discover_owner_ref_pairs (forward walk — the OO `[ref]` PRECEDES its values). With
--verify-existing, every existing ref URL (tracker + OO) is HTTP-checked up front
(deterministic, no agent tokens) so most HAS_REF units pre-classify as live vs dead.

    python scripts/build_ref_worklist.py --tracker oil --country "Saudi Arabia" \
        --verify-existing --out batches/saudi-arabia-oil/staging/ref-sweep/worklist.json

SheetRow = read_csv(header=2) index + 4. We deliberately do NOT use match.load_gem_df
(it reset_index'es, which breaks that mapping) — we replicate its buffer-row drop while
preserving the original index. OO sheet row = read_csv(header=1) index + 3.
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
from ref_pairs import (  # noqa: E402
    OO_HEADER_INDEX, discover_owner_ref_pairs, discover_ref_pairs,
)
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


def _load_owners(csv: str) -> tuple[pd.DataFrame, dict]:
    """Load the operators/owners tab (header at row index 1), keep the original index
    (OO sheet row = index + 3), and return (df, {ProjectID -> df-index})."""
    df = pd.read_csv(csv, header=OO_HEADER_INDEX, low_memory=False, dtype=str).fillna("")
    by_pid: dict[str, int] = {}
    if "ProjectID" in df.columns:
        for idx, pid in df["ProjectID"].items():
            pid = str(pid).strip()
            if pid and pid not in by_pid:   # first row wins on the rare dup
                by_pid[pid] = int(idx)
    return df, by_pid


def _owner_units(owners_df: pd.DataFrame, by_pid: dict, scope_ctx: list[dict]) -> list[dict]:
    """Emit operator + owner ref units for each in-scope ProjectID by joining the
    operators/owners tab. `scope_ctx` is the per-ProjectID tracker context (name/segment/
    wiki) gathered while walking the tracker, in first-seen order."""
    oo_pairs = discover_owner_ref_pairs(list(owners_df.columns))
    units: list[dict] = []
    for ctx in scope_ctx:
        pid = ctx["project_id"]
        oo_idx = by_pid.get(pid)
        if oo_idx is None:
            continue                      # no operators/owners row for this ProjectID
        oo_row = owners_df.loc[oo_idx]
        oo_sheet_row = int(oo_idx) + 3
        for p in oo_pairs:
            ref_col = p["ref_col"]
            value_cols = p["value_cols"]
            values = {c: str(oo_row.get(c, "")).strip() for c in value_cols
                      if str(oo_row.get(c, "")).strip()}
            current_ref = str(oo_row.get(ref_col, "")).strip()
            klass = _classify(p["kind"], ref_col, bool(values), current_ref)
            if klass == "SKIP":
                continue
            primary_col = p["primary_value_col"]
            primary_value = str(oo_row.get(primary_col, "")).strip()
            if not primary_value and values:
                primary_value = next(iter(values.values()))
            units.append({
                "project_id": pid,
                "sheet_row": ctx["sheet_row"],       # tracker row, for cross-reference
                "oo_sheet_row": oo_sheet_row,         # the operators/owners tab row
                "pipeline_name": ctx["pipeline_name"],
                "segment_name": ctx["segment_name"],
                "wiki": ctx["wiki"],
                "ref_col": ref_col,
                "value_cols": value_cols,
                "primary_value_col": primary_col,
                "values": values,
                "primary_value": primary_value,
                "current_ref": current_ref,
                "class": klass,
                "kind": p["kind"],
                "irregular": p["irregular"],
                "tab": "operators_owners",
                "existing_ref_checks": [],
                "value_checked": False,
            })
    return units


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
    if ref_col is None:                      # tracker synthetic owner placeholder (no [ref] col)
        return "MISSING_REF_NO_COLUMN"
    # real [ref] column — including the operators/owners tab's Operator/Owner [ref]
    return "HAS_REF" if current_ref.strip() else "MISSING_REF"


def build(csv: str, country: str | None, statuses: set[str] | None,
          verify_existing: bool, owners_csv: str | None = None,
          province: str | None = None,
          exclude_network_regex: str | None = None) -> dict:
    df = _load_indexed(csv)
    cols = set(df.columns)
    if country:
        want = N.normalize_country(country)
        df = df[df["CountriesOrAreas"].map(lambda s: want in N.split_countries(s))]
    if province:
        # In scope if EITHER terminus sits in a wanted province. Transited provinces
        # don't count — a trunk line crossing the province belongs to its own scope.
        wants = {p.strip().lower() for p in province.split(",") if p.strip()}
        prov_cols = [c for c in ("StartState/Province", "EndState/Province") if c in cols]
        if not prov_cols:
            sys.exit(f"--province given but no Start/EndState/Province columns in {csv}")
        mask = pd.Series(False, index=df.index)
        for c in prov_cols:
            mask |= df[c].map(lambda s: str(s).strip().lower() in wants)
        df = df[mask]
    if exclude_network_regex:
        rx = re.compile(exclude_network_regex)
        if "PipelineNetworkGrouping" in cols:
            df = df[~df["PipelineNetworkGrouping"].map(lambda s: bool(rx.search(str(s))))]
    if statuses:
        df = df[df["Status"].map(lambda s: str(s).strip().lower() in statuses)]

    # Tracker pairs: drop the synthetic owner placeholder — owner/operator refs come from
    # the operators/owners tab join below (when --owners-csv is supplied).
    pairs = [p for p in discover_ref_pairs(list(df.columns))
             if p["kind"] != "owner" and all(c in cols for c in p["value_cols"])]

    units: list[dict] = []
    scope_ctx: list[dict] = []   # per-ProjectID tracker context for the OO join
    seen_pids: set[str] = set()
    skip_count = 0
    for idx, row in df.iterrows():
        sheet_row = int(idx) + 4
        pid = str(row.get("ProjectID", "")).strip()
        pname = str(row.get("PipelineName", "")).strip()
        sname = str(row.get("SegmentName", "")).strip()
        wiki = str(row.get("Wiki", "")).strip()
        if pid and pid not in seen_pids:
            seen_pids.add(pid)
            scope_ctx.append({"project_id": pid, "sheet_row": sheet_row,
                              "pipeline_name": pname, "segment_name": sname, "wiki": wiki})
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

    # Operators/owners join: emit real Operator/Owner [ref] units per in-scope ProjectID.
    owner_units = 0
    owners_csv_name = None
    if owners_csv:
        owners_df, by_pid = _load_owners(owners_csv)
        oo_units = _owner_units(owners_df, by_pid, scope_ctx)
        owner_units = len(oo_units)
        units.extend(oo_units)
        owners_csv_name = Path(owners_csv).name

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
            "owners_csv": owners_csv_name,
            "country": country or "global",
            "province": province,
            "exclude_network_regex": exclude_network_regex,
            "statuses": sorted(statuses) if statuses else "all",
            "rows": int(df.shape[0]),
            "project_ids": len(scope_ctx),
            "pairs": len(pairs),
            "verify_existing": verify_existing,
        },
        "summary": {
            "units": len(units),
            "by_class": by_class,
            "owner_operator_units": owner_units,
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
    ap.add_argument("--province",
                    help="comma-separated Start/EndState/Province filter (row in scope if EITHER "
                         "terminus matches; transited provinces don't count). Combine with "
                         "--country for sub-country batches, e.g. China by province")
    ap.add_argument("--exclude-network-regex",
                    help="drop rows whose PipelineNetworkGrouping matches this regex (re.search). "
                         "China idiom: '^(?!.*输气管网$)' keeps only provincial-grid rows, "
                         "excluding national trunk systems (their own batch scope)")
    ap.add_argument("--status", help="comma-separated Status filter (e.g. proposed,construction)")
    ap.add_argument("--csv", help="GEM CSV (default: latest snapshot for the tracker)")
    ap.add_argument("--owners-csv",
                    help="operators/owners tab CSV (default: latest GEM_operators_owners_snapshot_*.csv; "
                         "pass --no-owners to skip the owner/operator join)")
    ap.add_argument("--no-owners", action="store_true",
                    help="skip the operators/owners join (no Operator/Owner [ref] units)")
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

    owners_csv = None
    if not args.no_owners:
        owners_csv = args.owners_csv
        if not owners_csv:
            oo = sorted(glob.glob(str(paths.repo_root() / "data" / "GEM_operators_owners_snapshot_*.csv")))
            if oo:
                owners_csv = oo[-1]
            else:
                print("  note: no operators/owners snapshot found — skipping owner/operator join "
                      "(run ./scripts/refresh_csvs.sh, or pass --no-owners to silence)", file=sys.stderr)

    statuses = None
    if args.status:
        statuses = {s.strip().lower() for s in args.status.split(",") if s.strip()}

    wl = build(csv, args.country, statuses, args.verify_existing, owners_csv=owners_csv,
               province=args.province, exclude_network_regex=args.exclude_network_regex)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(wl, indent=2, ensure_ascii=False))

    s, m = wl["scope"], wl["summary"]
    print(f"wrote {out}")
    prov = f" / {s['province']}" if s.get("province") else ""
    print(f"  scope: {s['country']}{prov} | {args.tracker} | {s['rows']} rows | "
          f"statuses={s['statuses']} | {s['pairs']} ref-pairs"
          + (f" | owners={s['owners_csv']}" if s.get("owners_csv") else " | owners=skipped"))
    print(f"  units: {m['units']}  by_class={m['by_class']}  "
          f"(operator/owner {m.get('owner_operator_units', 0)}; skipped {m['skip']} blank)")
    if args.verify_existing:
        print(f"  existing refs: {m['has_ref_all_live']} all-live, {m['has_ref_with_dead']} with dead/missing link(s)")


if __name__ == "__main__":
    main()
