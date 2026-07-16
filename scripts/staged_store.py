#!/usr/bin/env python3
"""Canonical reader of the staged stores under batches/staging/ — the single
join that keeps every downstream consumer (handoff assembly, wiki/route QC,
summaries) consistent with corrections that are already staged but not yet
applied to the live Sheet.

Two entry points:

  discover_staging_dirs(country, commodity)
      Depth-1 scan of batches/staging/: a dir is in scope when its
      staged_resolutions.json or staged_new.json meta matches the requested
      country+commodity. Assembled packets (meta.mode qc/handoff) are skipped
      unless include_assembled=True — a packet's own records must not be
      re-imported as "prior staged work" into the next packet.

  load_staged_context(staging_dirs) -> ctx with:
      pending_values   {(project_id, column) -> {value, source_dir, tier,
                       class_out, kind}} from FILL records (class_out=
                       REFS_ADDED) and STATUS records (verdict change/stale).
      concerns         {project_id -> [{concern_type, verdict, ...,
                       source_dir}]} from __VALIDITY__ records with
                       concern_type != 'none' (full text; truncate at display).
      status_changes   {project_id -> [record]} — ALL __STATUS__ verdicts,
                       including confirm.
      ref_work         [record] — every HAS_REF / MISSING_REF unit, plus
                       ref_counts (Counter by class_out).
      route_staged     {project_id -> {class_out, source_dir, record}}.
      new_rows         [candidate + source_dir] from staged_new.json (all
                       classes); new_by_matched_pid indexes matched_existing
                       candidates by the GEM row they matched.
      researched_pids / audited_pids — as before (any __VALIDITY__ record
                       counts as existence-audited; the deep-sweep contract
                       puts existence first).

Keying is (project_id, column) — NEVER sheet_row, which drifts between
snapshots. Discovery candidates have no ProjectID; their stable identity is
(source_dir, slug) and they join sheet rows only via matched_project_id.

Used by wiki_alignment.py (emit WIKI_STALE_VS_STAGED instead of WIKI_UPDATE
when the sheet cell itself has a staged pending correction),
route_integrity.py, build_qc_staging.py (annotate flags "known — staged",
assemble staged_actions.json), and staged_summary.py.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import normalize as N
from ref_pairs import OO_PRIMARY

REPO_ROOT = Path(__file__).resolve().parent.parent
STAGING_ROOT = REPO_ROOT / "batches" / "staging"

# meta.mode values that mark a dir as an ASSEMBLED packet, not primary research
_ASSEMBLED_MODES = {"qc", "handoff"}

# mechanical-check / QC-flag field -> the validity concern_type that covers it
_FIELD_TO_CONCERN = {
    "Capacity": "spec", "CapacityUnits": "spec", "LengthKnown": "spec",
    "LengthKnownKm": "spec", "Diameter": "spec", "DiameterInMm": "spec",
    "ProjectLevelCost": "spec", "SegmentCost": "spec", "StartYear1": "spec",
    "StartLocation": "spec", "EndLocation": "spec",
    "StartCountryOrArea": "spec", "EndCountryOrArea": "spec",
    "Owner": "attribution", "Parent": "attribution", "Operator": "attribution",
    "FuelSource": "attribution",
    "PipelineName": "duplicate", "SegmentName": "duplicate",
    "Status": "classification",
}

# STATUS verdicts that mean a status change is pending
_STATUS_PENDING = {"change", "stale"}

# ref_work keeps the fields the handoff needs; drop the bulky value_cols echo
_REF_WORK_FIELDS = (
    "project_id", "sheet_row", "pipeline_name", "segment_name", "ref_col",
    "class_in", "class_out", "current_ref", "primary_value_col",
    "primary_value", "values", "proposed_refs", "verifications", "tier",
    "independent", "source_language", "researcher_notes", "wiki", "tab",
)

# Owner [ref] / Operator [ref] exist only on the "Pipeline operators/owners"
# backend tab — FILL records from the deep sweep don't carry a tab field, so
# derive it from the ref col (keeps the workbook's Target-tab routing correct).
_OO_REF_COLS = frozenset(OO_PRIMARY)


def _with_tab(rec: dict) -> dict:
    if not rec.get("tab") and rec.get("ref_col") in _OO_REF_COLS:
        rec["tab"] = "operators_owners"
    return rec

_STATUS_FIELDS = (
    "project_id", "sheet_row", "pipeline_name", "segment_name", "verdict",
    "class_out", "current_status", "proposed_status", "values",
    "evidence_date", "staleness_rule", "proposed_refs", "verifications",
    "tier", "independent", "researcher_notes", "wiki",
)


def _dir_scope(d: Path) -> tuple[str, str] | None:
    """(normalized_country, commodity) for a staging dir, or None if neither
    store file exists / carries scope metadata."""
    for fn in ("staged_resolutions.json", "staged_new.json"):
        f = d / fn
        if not f.exists():
            continue
        try:
            meta = json.loads(f.read_text()).get("meta", {})
        except (json.JSONDecodeError, OSError):
            continue
        scope = meta.get("scope") or {}
        country = scope.get("country", "")
        commodity = (meta.get("commodity") or scope.get("tracker")
                     or scope.get("commodity") or "")
        if country and commodity:
            return N.normalize_country(country), commodity.lower()
    return None


def _dir_mode(d: Path) -> str:
    f = d / "staged_resolutions.json"
    if not f.exists():
        return ""
    try:
        return json.loads(f.read_text()).get("meta", {}).get("mode", "")
    except (json.JSONDecodeError, OSError):
        return ""


def _slug_scope(name: str, country: str, commodity: str) -> bool:
    """Fallback: infer scope from the dir slug (e.g. ref-sweep-gas-egypt-operating).
    Requires the commodity token AND every word of the country present."""
    tokens = name.lower().split("-")
    if commodity.lower() not in tokens:
        return False
    country_tokens = N.normalize_country(country).lower().replace("-", " ").split()
    return all(t in tokens for t in country_tokens)


def discover_staging_dirs(country: str, commodity: str,
                          root: str | Path = STAGING_ROOT,
                          exclude: tuple | list = (),
                          include_assembled: bool = False) -> list[Path]:
    """All staging dirs holding staged work for this country+commodity.

    Matching is on store metadata (meta.scope.country + meta.commodity /
    meta.scope.tracker); dirs whose stores lack scope fields fall back to
    slug parsing with a WARN. Assembled packets (meta.mode qc/handoff) are
    excluded unless include_assembled. `exclude` paths (e.g. the packet's own
    dir) are always skipped.
    """
    root = Path(root)
    want = (N.normalize_country(country), commodity.lower())
    skip = {Path(e).resolve() for e in exclude}
    out = []
    if not root.is_dir():
        return out
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.resolve() in skip:
            continue
        scope = _dir_scope(d)
        if scope is None:
            if (d / "staged_resolutions.json").exists() or (d / "staged_new.json").exists():
                if _slug_scope(d.name, country, commodity):
                    print(f"WARN dir {d.name}: scope inferred from slug")
                    out.append(d)
            continue
        if scope != want:
            continue
        if not include_assembled and _dir_mode(d) in _ASSEMBLED_MODES:
            continue
        out.append(d)
    return out


def load_staged_context(staging_dirs: list[str | Path]) -> dict:
    ctx = {
        "pending_values": {},   # (pid, column) -> {...}
        "concerns": {},         # pid -> [ {...} ]
        "fills": [],            # corroborated FILL records (class_out=REFS_ADDED)
        "status_changes": {},   # pid -> [ {...} ]  (ALL verdicts incl. confirm)
        "ref_work": [],         # HAS_REF / MISSING_REF units, all dirs
        "ref_counts": Counter(),
        "route_staged": {},     # pid -> {class_out, source_dir, record}
        "new_rows": [],         # staged_new.json candidates, all classes
        "new_by_matched_pid": {},
        "researched_pids": set(),
        "audited_pids": {},     # pid -> source_dir (any validity verdict = existence-audited)
        "dirs": [],
    }
    for d in staging_dirs:
        d = Path(d)
        loaded = False
        f = d / "staged_resolutions.json"
        if f.exists():
            data = json.loads(f.read_text())
            loaded = True
            for r in data.get("resolutions", []):
                pid = r.get("project_id", "")
                if not pid:
                    continue
                ctx["researched_pids"].add(pid)
                ci = r.get("class_in", "")
                if ci in ("HAS_REF", "MISSING_REF"):
                    rec = _with_tab({k: r.get(k, "") for k in _REF_WORK_FIELDS})
                    rec["source_dir"] = d.name
                    ctx["ref_work"].append(rec)
                    ctx["ref_counts"][r.get("class_out", "")] += 1
                elif ci == "FILL" and r.get("class_out") == "REFS_ADDED":
                    rec = _with_tab({k: r.get(k, "") for k in _REF_WORK_FIELDS})
                    rec["source_dir"] = d.name
                    ctx["fills"].append(rec)
                    for col, val in (r.get("values") or {}).items():
                        if val in (None, ""):
                            continue
                        ctx["pending_values"].setdefault((pid, col), {
                            "value": str(val), "source_dir": d.name,
                            "tier": r.get("tier", ""),
                            "class_out": r.get("class_out", ""),
                            "kind": "fill",
                        })
                elif ci == "STATUS" or r.get("ref_col") == "__STATUS__":
                    rec = {k: r.get(k, "") for k in _STATUS_FIELDS}
                    rec["source_dir"] = d.name
                    ctx["status_changes"].setdefault(pid, []).append(rec)
                    if r.get("verdict", "") in _STATUS_PENDING:
                        proposed = (r.get("proposed_status")
                                    or (r.get("values") or {}).get("Status", ""))
                        if proposed:
                            ctx["pending_values"][(pid, "Status")] = {
                                "value": str(proposed), "source_dir": d.name,
                                "tier": r.get("tier", ""),
                                "class_out": r.get("class_out", ""),
                                "kind": "status",
                            }
                elif ci == "VALIDITY" or r.get("ref_col") == "__VALIDITY__":
                    ctx["audited_pids"].setdefault(pid, d.name)
                    if r.get("concern_type", "none") == "none":
                        continue
                    ctx["concerns"].setdefault(pid, []).append({
                        "concern_type": r.get("concern_type", ""),
                        "verdict": r.get("verdict", ""),
                        "sheet_row": r.get("sheet_row", ""),
                        "pipeline_name": r.get("pipeline_name", ""),
                        "segment_name": r.get("segment_name", ""),
                        "recommendation": r.get("recommendation") or "",
                        "researcher_notes": r.get("researcher_notes") or "",
                        "proposed_refs": r.get("proposed_refs") or [],
                        "tier": r.get("tier", ""),
                        "independent": r.get("independent", ""),
                        "source_dir": d.name,
                    })
                elif ci == "ROUTE" or r.get("ref_col") == "__ROUTE__":
                    ctx["route_staged"][pid] = {"class_out": r.get("class_out", ""),
                                                "source_dir": d.name,
                                                "record": r}
        f = d / "staged_new.json"
        if f.exists():
            data = json.loads(f.read_text())
            loaded = True
            for c in data.get("candidates", []):
                cand = dict(c)
                cand["source_dir"] = d.name
                ctx["new_rows"].append(cand)
                mpid = c.get("matched_project_id", "")
                if mpid:
                    ctx["new_by_matched_pid"].setdefault(mpid, []).append(cand)
        if loaded:
            ctx["dirs"].append(d.name)
    return ctx


def load_store(country: str, commodity: str, exclude: tuple | list = ()) -> dict:
    """Convenience: discover + load in one call."""
    return load_staged_context(discover_staging_dirs(country, commodity,
                                                     exclude=exclude))


def pending_for(ctx: dict, pid: str, column: str) -> dict | None:
    """The staged pending correction for this (pid, column), or None."""
    return ctx["pending_values"].get((pid, column))


def annotate(ctx: dict, pid: str, field: str | None = None,
             kind: str | None = None) -> str:
    """'known — staged (<dir>)' when an existing packet already covers this flag,
    else ''. `field` is a sheet column (mapped to a concern_type); `kind` may name
    a concern_type directly ('existence', 'duplicate', ...), 'route', or
    'new_row_match' (a discovery candidate matched this existing row)."""
    if kind == "route":
        rs = ctx["route_staged"].get(pid)
        return f"known — staged ({rs['source_dir']}: {rs['class_out']})" if rs else ""
    if kind == "new_row_match":
        for cand in ctx["new_by_matched_pid"].get(pid, []):
            return f"known — staged ({cand['source_dir']}: matched_existing)"
        return ""
    want = kind or (_FIELD_TO_CONCERN.get(field or "", ""))
    for c in ctx["concerns"].get(pid, []):
        if not want or c["concern_type"] == want:
            return f"known — staged ({c['source_dir']}: {c['concern_type']})"
    if want == "duplicate":
        for cand in ctx["new_by_matched_pid"].get(pid, []):
            return f"known — staged ({cand['source_dir']}: matched_existing)"
    if field and (pid, field) in ctx["pending_values"]:
        pv = ctx["pending_values"][(pid, field)]
        return f"known — staged ({pv['source_dir']}: pending {pv.get('kind', 'value')})"
    return ""


def existence_note(ctx: dict, pid: str) -> str:
    """Coverage note for a row-level existence question. A staged existence/duplicate
    concern wins; otherwise ANY prior validity verdict counts as coverage (the
    deep-sweep contract audits existence first on every row), so an audited row with
    no concern reads 'audited — no existence concern' rather than re-flagging."""
    for c in ctx["concerns"].get(pid, []):
        if c["concern_type"] in ("existence", "duplicate"):
            return f"known — staged ({c['source_dir']}: {c['concern_type']})"
    src = ctx["audited_pids"].get(pid)
    return f"audited — no existence concern ({src})" if src else ""


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="smoke-test the staged store")
    ap.add_argument("--country", required=True)
    ap.add_argument("--commodity", required=True, choices=["gas", "oil"])
    ap.add_argument("--staged-dir", action="append", default=[],
                    help="explicit dirs (skips auto-discovery)")
    args = ap.parse_args()
    dirs = args.staged_dir or discover_staging_dirs(args.country, args.commodity)
    print(f"dirs: {[Path(d).name for d in dirs]}")
    ctx = load_staged_context(dirs)
    print(f"researched_pids: {len(ctx['researched_pids'])}")
    print(f"pending_values: {len(ctx['pending_values'])}")
    print(f"concern rows: {sum(len(v) for v in ctx['concerns'].values())} "
          f"across {len(ctx['concerns'])} PIDs")
    print(f"status rows: {sum(len(v) for v in ctx['status_changes'].values())} "
          f"across {len(ctx['status_changes'])} PIDs")
    print(f"ref_work: {len(ctx['ref_work'])} units; {dict(ctx['ref_counts'])}")
    print(f"route_staged: {len(ctx['route_staged'])}")
    print(f"new_rows: {len(ctx['new_rows'])} "
          f"({Counter(c.get('class', '') for c in ctx['new_rows'])})")
