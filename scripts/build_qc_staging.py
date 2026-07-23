#!/usr/bin/env python3
"""Assemble the handoff packet staging (wiki/route QC + full staged-work join).

Combines, for one country+commodity scope:
  1. the ten mechanical checks (build_qc_workbook.run_checks) plus the
     Existence_support ref-thinness check (<=1 distinct reference URL across the
     row's [ref] cells -> "should we even track this?"), country-scoped, each
     flag annotated "known — staged (...)" when a prior packet already covers
     it -> <staging>/qc_flags.json (sidecar, rendered as the workbook's
     <Cmdty>_Flags tab);
  1b. <staging>/staged_actions.json — EVERY pending staged action carried in
     from PRIOR staging dirs (auto-discovered by country+commodity): validity
     concerns of ALL types, status changes, corroborated fills, actionable ref
     work, route suggestions, and discovery candidates — each with source_dir
     provenance, so the handoff deliverable is the one place a researcher sees
     everything staged for the country;
  2. Leg 1 wiki_alignment.json + Leg 2 route_integrity.json ->
     <staging>/staged_resolutions.json (meta.mode "handoff") for
     build_ref_workbook;
  3. <staging>/worklist.json — the rows whose flags need targeted research
     (Leg 3 fan-out briefs): SHEET_SUSPECT wiki diffs, hard route flags, and
     geo/date/existence mechanical flags, minus anything a staged packet
     already covers.

Run AFTER wiki_alignment.py and route_integrity.py have written their JSONs.
After the Leg-3 merge, re-run ONLY with --sidecars-only (the guard refuses to
overwrite a staged_resolutions.json that already holds merged validity/fills).

Usage:
  python scripts/build_qc_staging.py --csv data/GGIT_gas_snapshot_<date>.csv \
      --country Egypt --commodity gas --staging batches/egypt-gas/staging/qc/ \
      [--pids ...] [--staged-dir <dir> ...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import normalize as N  # noqa: E402
from build_qc_workbook import run_checks  # noqa: E402
from staged_store import (  # noqa: E402
    _FIELD_TO_CONCERN, annotate, discover_staging_dirs, existence_note,
    load_staged_context,
)

# mechanical check -> the sheet column annotate() maps to a staged concern_type
_CHECK_FIELD = {
    "Status": "Status", "Owner_format": "Owner", "Date_logic": "StartYear1",
    "Diameter_OutOfRange": "Diameter", "Geo_consistency": "StartCountryOrArea",
    "Name_uniqueness": "PipelineName",
}

# what goes on the Leg-3 research worklist (sheet might be wrong -> verify with
# >=2 independent sources); everything else is direct wiki-editing or mechanical fixup
_RESEARCH_WIKI_CLASSES = {"SHEET_SUSPECT"}
_RESEARCH_ROUTE_CHECKS = {"length_ratio", "countries", "endpoint_country", "degenerate"}
_RESEARCH_CHECKS = {"Geo_consistency", "Date_logic", "Diameter_OutOfRange",
                    "Existence_support"}

_URL_RE = re.compile(r"https?://\S+")


def _existence_support_flags(df, ctx) -> list[dict]:
    """Ref-thinness existence check: a row whose entire [ref] column set holds <=1
    distinct reference URL is a 'should we even be tracking this?' candidate —
    the whole entry may rest on a single source. Purely mechanical (URL counting;
    liveness is the sweep refs leg's job). Suppressed via existence_note() when a prior
    packet staged an existence/duplicate concern OR already existence-audited the
    row (any validity verdict — the deep-sweep contract checks existence first)."""
    ref_cols = [c for c in df.columns if "[ref]" in c]
    flags = []
    for _, r in df.iterrows():
        urls = set()
        for c in ref_cols:
            urls.update(u.rstrip(".,;)") for u in _URL_RE.findall(str(r.get(c, ""))))
        if len(urls) > 1:
            continue
        domains = {urlparse(u).netloc.lower().removeprefix("www.") for u in urls}
        detail = ("no reference URLs in any [ref] cell" if not urls else
                  f"single reference URL ({next(iter(domains))}) supports the entire row")
        flags.append({
            "check": "Existence_support",
            "project_id": r.get("ProjectID", ""),
            "sheet_row": int(r["SheetRow"]),
            "pipeline_name": r.get("PipelineName", ""),
            "segment_name": r.get("SegmentName", ""),
            "countries": r.get("CountriesOrAreas", ""),
            "detail": f"existence support thin: {detail} — verify the pipeline is "
                      "real and worth tracking (>=2 independent sources)",
            "staged_note": existence_note(ctx, r.get("ProjectID", "")),
        })
    return flags


# ref_work classes worth a researcher's attention in the handoff (REVERIFIED
# is counts-only — nothing to do)
_ACTIONABLE_REF_CLASSES = {"REFS_ADDED", "DEAD_LINK", "UNRESOLVED"}


def _resolve_sheet_row(rec: dict, rows_by_pid: dict) -> dict:
    """Overwrite a carried record's sheet_row from THIS packet's snapshot (staged
    records date from older CSVs); keep the original as source_sheet_row when it
    differs. Keying stays (project_id, column) — this is locator hygiene only."""
    r = rows_by_pid.get(rec.get("project_id", ""))
    if r is None:
        return rec
    new_sr = int(r["SheetRow"])
    old = rec.get("sheet_row", "")
    if old not in ("", None) and str(old) != str(new_sr):
        rec["source_sheet_row"] = old
    rec["sheet_row"] = new_sr
    return rec


def _build_staged_actions(ctx, df, args, flags, wiki_records) -> dict:
    """The full carried-in staged-work sidecar: every pending action from prior
    staging dirs, scoped to this country's rows, with source_dir provenance.
    Generalizes the old existence_carryover.json (existence/duplicate only)."""
    scope_pids = set(df["ProjectID"])
    rows_by_pid = {r["ProjectID"]: r for _, r in df.iterrows()}

    # this run's own flags indexed pid -> [(source, field, concern_type)] for the
    # reverse cross-reference (also_flagged on carried concerns)
    own: dict[str, list] = {}
    for f in flags:
        fld = _CHECK_FIELD.get(f["check"], "")
        ct = ("existence" if f["check"] == "Existence_support"
              else _FIELD_TO_CONCERN.get(fld, ""))
        if ct:
            own.setdefault(f["project_id"], []).append(("mechanical", f["check"], ct))
    for r in wiki_records:
        ct = _FIELD_TO_CONCERN.get(r.get("field", ""), "")
        if ct:
            own.setdefault(r.get("project_id", ""), []).append(
                ("wiki_alignment", r.get("field", ""), ct))

    def also_flagged(pid: str, concern_type: str) -> list[str]:
        return sorted({f"{src}:{fld}" for src, fld, ct in own.get(pid, [])
                       if ct == concern_type})

    n_out_of_scope = 0

    def in_scope(recs, key="project_id"):
        nonlocal n_out_of_scope
        kept = []
        for r in recs:
            if r.get(key, "") in scope_pids:
                kept.append(_resolve_sheet_row(dict(r), rows_by_pid))
            else:
                n_out_of_scope += 1
        return kept

    concerns = []
    for pid, cs in sorted(ctx["concerns"].items()):
        if pid not in scope_pids:
            n_out_of_scope += len(cs)
            continue
        for c in cs:
            rec = _resolve_sheet_row(dict(c), rows_by_pid)
            rec["project_id"] = pid
            rec["also_flagged"] = also_flagged(pid, c["concern_type"])
            concerns.append(rec)
    order = {"existence": 0, "duplicate": 1, "classification": 2,
             "attribution": 3, "spec": 4}
    concerns.sort(key=lambda c: (order.get(c["concern_type"], 9),
                                 c.get("source_dir", ""), c["project_id"]))

    status_changes, status_verdicts = [], Counter()
    for pid, recs in sorted(ctx["status_changes"].items()):
        for r in recs:
            status_verdicts[r.get("verdict", "")] += 1
            if r.get("verdict", "") == "confirm" or pid not in scope_pids:
                continue
            rec = _resolve_sheet_row(dict(r), rows_by_pid)
            rec["project_id"] = pid
            status_changes.append(rec)

    fills = in_scope(ctx["fills"])
    ref_work = in_scope([r for r in ctx["ref_work"]
                         if r.get("class_out", "") in _ACTIONABLE_REF_CLASSES])
    routes = in_scope([dict(v["record"], source_dir=v["source_dir"])
                       for v in ctx["route_staged"].values()])
    new_rows = [dict(c) for c in ctx["new_rows"]]

    actions = {
        "meta": {
            "mode": "handoff_actions", "country": args.country,
            "commodity": args.commodity, "csv": Path(args.csv).name,
            "staged_dirs": ctx["dirs"],
            "counts": {
                "concerns_by_type": dict(Counter(c["concern_type"] for c in concerns)),
                "status_verdicts": dict(status_verdicts),
                "status_changes": len(status_changes),
                "fills": len(fills),
                "ref_work_by_class": dict(Counter(r["class_out"] for r in ref_work)),
                "ref_reverified": ctx["ref_counts"].get("REVERIFIED", 0),
                "routes": len(routes),
                "new_rows_by_class": dict(Counter(c.get("class", "") for c in new_rows)),
                "out_of_scope_dropped": n_out_of_scope,
            },
        },
        "concerns": concerns,
        "status_changes": status_changes,
        "fills": fills,
        "ref_work": ref_work,
        "routes": routes,
        "new_rows": new_rows,
    }
    return actions


def _load_scope(csv: str, country: str, pids: str | None):
    import pandas as pd
    df = pd.read_csv(csv, header=2, low_memory=False, dtype=str).fillna("")
    df = df[df["PipelineName"].str.strip() != ""].copy()
    df["SheetRow"] = df.index + 4          # before any reset — CSV index + 4
    want = N.normalize_country(country)
    df = df[df["CountriesOrAreas"].map(lambda s: want in N.split_countries(s))]
    if pids:
        keep = {p.strip() for p in pids.split(",") if p.strip()}
        df = df[df["ProjectID"].isin(keep)]
    return df.reset_index(drop=True)


def _leg(staging: Path, name: str) -> dict:
    p = staging / name
    if not p.exists():
        sys.exit(f"missing {p} — run the leg script first")
    return json.loads(p.read_text())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--country", required=True)
    ap.add_argument("--commodity", default="gas", choices=["gas", "oil"])
    ap.add_argument("--staging", required=True)
    ap.add_argument("--pids")
    ap.add_argument("--staged-dir", action="append", default=[],
                    help="staging dir(s) with prior packets (repeatable); "
                         "default: auto-discover by country+commodity")
    ap.add_argument("--sidecars-only", action="store_true",
                    help="rewrite qc_flags.json / staged_actions.json / worklist.json "
                         "but leave staged_resolutions.json untouched — REQUIRED after the "
                         "Leg-3 merge (a full re-run would clobber the merged validity/fills)")
    args = ap.parse_args()

    staging = Path(args.staging)
    df = _load_scope(args.csv, args.country, args.pids)
    staged_dirs = args.staged_dir or discover_staging_dirs(
        args.country, args.commodity, exclude=[args.staging])
    ctx = load_staged_context(staged_dirs)

    # 1 — mechanical flags with staged annotations
    flags = []
    for check, rows in run_checks(df).items():
        for r in rows:
            flags.append({
                "check": check,
                "project_id": r.get("ProjectID", ""),
                "sheet_row": r.get("SheetRow", ""),
                "pipeline_name": r.get("PipelineName", ""),
                "segment_name": r.get("SegmentName", ""),
                "countries": r.get("CountriesOrAreas", ""),
                "detail": r.get("Detail", ""),
                "staged_note": annotate(ctx, r.get("ProjectID", ""),
                                        field=_CHECK_FIELD.get(check)),
            })
    flags.extend(_existence_support_flags(df, ctx))
    qc_flags = {
        "meta": {"mode": "qc_flags", "csv": Path(args.csv).name,
                 "country": args.country, "commodity": args.commodity,
                 "rows": int(len(df)), "staged_dirs": ctx["dirs"],
                 "check_counts": dict(Counter(f["check"] for f in flags))},
        "flags": flags,
    }
    (staging / "qc_flags.json").write_text(json.dumps(qc_flags, indent=1, ensure_ascii=False))

    # 1b — staged_actions.json: EVERY pending staged action from prior dirs
    # (all concern types + status + fills + ref work + routes + discovery),
    # scoped to this country's rows, with source_dir provenance — so nothing
    # staged stays buried in an earlier packet's workbook.
    wiki = _leg(staging, "wiki_alignment.json")
    route = _leg(staging, "route_integrity.json")
    actions = _build_staged_actions(ctx, df, args, flags, wiki.get("records", []))
    (staging / "staged_actions.json").write_text(
        json.dumps(actions, indent=1, ensure_ascii=False))

    # 2 — combined staged_resolutions.json from Legs 1 + 2
    resolutions = list(wiki.get("records", [])) + list(route.get("records", []))
    combined = {
        "meta": {
            "mode": "handoff",
            "commodity": args.commodity,
            "scope": {"csv": Path(args.csv).name, "country": args.country,
                      "commodity": args.commodity, "rows": int(len(df))},
            "staged_dirs": ctx["dirs"],
            "counts": {
                "wiki_alignment": len(wiki.get("records", [])),
                "route_integrity": len(route.get("records", [])),
                "mechanical_flags": len(flags),
                **{f"wiki_{k.lower()}": v
                   for k, v in (wiki.get("meta", {}).get("class_out_counts") or {}).items()},
                **{f"route_{k}": v
                   for k, v in (route.get("meta", {}).get("check_counts") or {}).items()},
            },
        },
        "resolutions": resolutions,
    }
    res_path = staging / "staged_resolutions.json"
    if args.sidecars_only:
        print(f"--sidecars-only: leaving {res_path} untouched")
    else:
        # clobber guard: once the Leg-3 merge has folded validity/fills into
        # staged_resolutions.json, a re-run would silently erase them
        if res_path.exists():
            prior = json.loads(res_path.read_text())
            merged = any(r.get("ref_col") == "__VALIDITY__" or r.get("class_in") in
                         ("VALIDITY", "FILL", "STATUS")
                         for r in prior.get("resolutions", []))
            if merged:
                sys.exit(f"{res_path} already contains merged Leg-3 records "
                         "(validity/fills) — re-run with --sidecars-only, or delete "
                         "the file first if you really mean to rebuild from Legs 1+2.")
        res_path.write_text(json.dumps(combined, indent=1, ensure_ascii=False))

    # 3 — Leg-3 research worklist: rows whose flags question the SHEET (not the wiki)
    by_pid: dict[str, list[dict]] = {}
    for r in wiki.get("records", []):
        if (r.get("class_out") in _RESEARCH_WIKI_CLASSES and r.get("severity") == "flag"
                and not r.get("staged_note")):
            by_pid.setdefault(r["project_id"], []).append({
                "source": "wiki_alignment", "field": r.get("field", ""),
                "detail": r.get("action", ""),
                "sheet_value": r.get("sheet_value", ""), "wiki_value": r.get("wiki_value", "")})
    for r in route.get("records", []):
        if (r.get("check") in _RESEARCH_ROUTE_CHECKS and r.get("severity") == "flag"
                and not r.get("staged_note")):
            by_pid.setdefault(r["project_id"], []).append({
                "source": "route_integrity", "field": r.get("check", ""),
                "detail": r.get("detail", ""),
                "measured": r.get("measured", ""), "expected": r.get("expected", "")})
    for f in flags:
        if f["check"] in _RESEARCH_CHECKS and not f["staged_note"]:
            by_pid.setdefault(f["project_id"], []).append({
                "source": "mechanical", "field": f["check"], "detail": f["detail"]})

    rows_ix = df.set_index("ProjectID")
    work_rows = []
    for pid, items in sorted(by_pid.items()):
        if pid not in rows_ix.index:
            continue
        r = rows_ix.loc[pid]
        r = r.iloc[0] if hasattr(r, "iloc") and getattr(r, "ndim", 1) == 2 else r
        work_rows.append({
            "project_id": pid, "sheet_row": int(r["SheetRow"]),
            "pipeline_name": r.get("PipelineName", ""),
            "segment_name": r.get("SegmentName", ""),
            "status": r.get("Status", ""), "wiki": r.get("Wiki", ""),
            "flags": items,
        })
    worklist = {
        "meta": {"mode": "qc_research", "country": args.country,
                 "commodity": args.commodity, "rows": len(work_rows),
                 "flag_rows_total": len(by_pid)},
        "rows": work_rows,
    }
    (staging / "worklist.json").write_text(json.dumps(worklist, indent=1, ensure_ascii=False))

    print(f"wrote {staging}/qc_flags.json — {len(flags)} mechanical flags; "
          f"{qc_flags['meta']['check_counts']}")
    ac = actions["meta"]["counts"]
    print(f"wrote {staging}/staged_actions.json — "
          f"{len(actions['concerns'])} concerns {ac['concerns_by_type']}; "
          f"{ac['status_changes']} status changes {ac['status_verdicts']}; "
          f"{ac['fills']} fills; ref work {ac['ref_work_by_class']} "
          f"(+{ac['ref_reverified']} reverified, counts-only); "
          f"{ac['routes']} route suggestions; "
          f"new rows {ac['new_rows_by_class']}; "
          f"{ac['out_of_scope_dropped']} out-of-scope dropped")
    if not args.sidecars_only:
        print(f"wrote {staging}/staged_resolutions.json — {len(resolutions)} records "
              f"(wiki {combined['meta']['counts']['wiki_alignment']}, "
              f"route {combined['meta']['counts']['route_integrity']})")
    print(f"wrote {staging}/worklist.json — {len(work_rows)} rows need targeted research")


if __name__ == "__main__":
    main()
