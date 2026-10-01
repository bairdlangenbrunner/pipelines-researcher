#!/usr/bin/env python3
"""Seed a §5 Update worklist from review-app decisions (review app milestone 5).

    python scripts/update_seed.py --country Russia --commodity gas [--dirs DIR ...] [--out PATH]

Walks the scope's staging dirs (`staged_store.discover_staging_dirs(..., include_assembled=True)`,
the same discovery `review_data.py` uses; `--dirs` skips it) and reads each dir's
`review_decisions.json` (via `review_app/decisions.py`, latest live record, undone ones ignored).
It emits, read-only over the staging dirs:

  (a) an UPDATE unit for every line whose live decision is a person's `suggest`: the reviewer
      disagrees with the proposed value and supplies another (pid, sheet_row, column, ref_col,
      proposed_value, suggested_value, note, reviewer, source dir). A suggest that took a validity
      concern's candidate (`rival` = the concern's key; review_app/store.py) also carries
      `rival_concern` + `rival_text`, and that concern yields NO research unit of its own: the
      line answers it;
  (b) a RESEARCH unit for every other concern item whose call is `confirmed` or `needs_research`
      (pid, concern_type, contested columns, text, note, call, source dir).

Output (default `batches/<scope>/staging/update-seed-<YYYYMMDD>/staged_updates_seed.json`) follows
the shape of the real `staged_updates.json` (`docs/sops/update.md` step 6; see
`batches/united-states-oil/staging/update-*/`): `meta`, `rows` keyed by ProjectID with
`pipeline`, `sheet_row` and `changes: {column: {old, new, action, tier, ref_col, refs, evidence}}`;
a `suggest` unit lands in `changes` (action `suggest`, `new` = the suggested value, `evidence` =
the note). Plus a flat `units` list carrying every unit with the fields above, and each row's
`research` list for concern units. The filename differs from `staged_updates.json` on purpose:
`staged_store` must not load a seed as pending values. A seed is a WORKLIST: the research and
the `[ref]`s are still to be done.

Fields of the update shape it cannot fill (left empty): `old` (the sheet's current value; the seed
reads no snapshot), `tier`, `refs` (a suggestion carries no verified URL), and the workbook
builder fields of the per-batch `build_update_workbook.py`. A dir with no decision file yields no
units (an empty seed, exit 0).
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for _p in (ROOT / "scripts", ROOT / "review_app"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import staged_store  # noqa: E402

UNIT_CALLS = ("confirmed", "needs_research")
BODY = ("recommendation", "action", "detail", "summary", "researcher_notes", "staged_note")


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def has_decisions(d):
    d = Path(d)
    return (d / "review_decisions.json").exists() or (d / "review_log.jsonl").exists()


def dir_records(d):
    """[(group, kind, staged record, probe)] for one staging dir: `probe` is the dict to hand to
    `Decisions.for_record(probe, kind)`. Resolutions use classify() from review_data; staged_new
    candidates (new_row lines / monitor items) are keyed `new:<slug>` like the dataset does."""
    from review_data import classify                 # lazy: review_data pulls build_ref_workbook
    d = Path(d)
    out = []
    f = d / "staged_resolutions.json"
    if f.exists():
        for r in _read(f).get("resolutions", []):
            group, kind = classify(r)
            if r.get("project_id"):
                out.append((group, kind, r, r))
    f = d / "staged_new.json"
    if f.exists():
        for i, c in enumerate(_read(f).get("candidates", [])):
            cls = c.get("class") or ""
            if cls not in ("new_row", "matched_existing", "monitor"):
                continue
            slug = c.get("slug") or (c.get("name") or f"cand{i}").lower().replace(" ", "-")
            pid = c.get("matched_project_id") or c.get("project_id") or f"new:{slug}"
            probe = {"project_id": pid, "ref_col": f"new:{slug}", "sheet_row": ""}
            out.append(("item" if cls == "monitor" else "line", "monitor" if cls == "monitor" else "new_row", c, probe))
    return out


def _column(rec, kind):
    if kind == "status":
        return "Status"
    if kind == "route":
        return "Route"
    if kind in ("fill", "oo"):
        return rec.get("primary_value_col") or next(iter(rec.get("values") or {}), "") or rec.get("ref_col", "")
    if kind == "new_row":
        return "PipelineName"
    return (rec.get("ref_col") or "").replace(" [ref]", "")


def _proposed(rec, kind):
    if kind == "status":
        return rec.get("proposed_status", "") or ""
    if kind in ("fill", "oo"):
        vals = rec.get("values") or {}
        v = rec.get("primary_value")
        if v in (None, ""):
            v = vals.get(rec.get("primary_value_col") or "", "") or next(iter(vals.values()), "")
        return "" if v is None else str(v)
    if kind == "new_row":
        return rec.get("name", "") or ""
    return ", ".join(rec.get("proposed_refs") or [])


def _text(rec):
    for k in BODY:
        v = rec.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def collect(dirs, label=None):
    """-> (units, stats). Pure read over the dirs' staged stores and decision sidecars."""
    from decisions import Decisions                  # lazy (imports review_data)
    label = label or staged_store.dir_label
    units, stats = [], {"dirs": 0, "dirs_with_decisions": 0, "suggest": 0, "research": 0, "answered_by_suggest": 0}
    for d in dirs:
        d = Path(d)
        stats["dirs"] += 1
        if not has_decisions(d):
            continue
        stats["dirs_with_decisions"] += 1
        dec = Decisions(d)
        found = [(g, k, rec, probe, dec.for_record(probe, k)) for g, k, rec, probe in dir_records(d)]
        found = [x for x in found if x[4] and not x[4].get("via")]   # a covered record repeats its status line's call: one unit
        concerns = {r.get("key"): rec for g, k, rec, probe, r in found if g == "item" and k == "concern"}
        answered = {r["rival"] for g, k, rec, probe, r in found
                    if g == "line" and r.get("decision") == "suggest" and r.get("rival")
                    and dec.person_decision(probe, k) == "suggest"}
        for group, kind, rec, probe, r in found:
            if group == "line" and r.get("decision") == "suggest" and dec.person_decision(probe, kind) == "suggest":
                rc = concerns.get(r.get("rival")) if r.get("rival") else None
                units.append({
                    "unit_type": "update", "project_id": probe["project_id"],
                    "pipeline_name": rec.get("pipeline_name") or rec.get("name") or "",
                    "sheet_row": r.get("sheet_row") or rec.get("sheet_row"),
                    "kind": kind, "column": _column(rec, kind), "ref_col": r.get("ref_col") or rec.get("ref_col", ""),
                    "proposed_value": _proposed(rec, kind), "suggested_value": r.get("suggested_value", ""),
                    "note": r.get("note", ""), "reviewer": r.get("reviewer"), "decided_at": r.get("ts"),
                    "source_dir": label(d), "key": r.get("key"),
                    "rival_concern": r.get("rival") or "", "rival_text": _text(rc) if rc else ""})
                stats["suggest"] += 1
            elif group == "item" and kind == "concern" and r.get("call") in UNIT_CALLS and not r.get("undecided"):
                if r.get("key") in answered:
                    stats["answered_by_suggest"] += 1
                    continue        # its candidate was taken on a line: the update unit above carries it
                units.append({
                    "unit_type": "research", "project_id": probe["project_id"],
                    "pipeline_name": rec.get("pipeline_name") or "",
                    "sheet_row": r.get("sheet_row") or rec.get("sheet_row"),
                    "concern_type": rec.get("concern_type", ""),
                    "contested_columns": sorted((rec.get("contested") or {}).keys()),
                    "text": _text(rec), "call": r.get("call"), "note": r.get("note", ""),
                    "reviewer": r.get("reviewer"), "decided_at": r.get("ts"),
                    "source_dir": label(d), "key": r.get("key")})
                stats["research"] += 1
    return units, stats


def rows_from_units(units):
    """Units -> the staged_updates.json `rows` shape (PID -> pipeline, sheet_row, changes, research)."""
    rows = {}
    for u in units:
        row = rows.setdefault(u["project_id"], {"pipeline": u.get("pipeline_name", ""), "sheet_row": u.get("sheet_row"),
                                                "changes": {}, "research": []})
        if u["unit_type"] == "update":
            row["changes"][u["column"]] = {
                "old": "", "new": u["suggested_value"], "action": "suggest", "tier": "", "ref_col": u["ref_col"],
                "refs": [], "evidence": u["note"], "proposed_value": u["proposed_value"],
                "reviewer": u["reviewer"], "source_dir": u["source_dir"],
                "rival_concern": u.get("rival_concern", ""), "rival_text": u.get("rival_text", "")}
        else:
            row["research"].append({k: u[k] for k in ("concern_type", "contested_columns", "text", "call", "note",
                                                      "reviewer", "source_dir")})
    return rows


def build_seed(units, dirs, country, commodity, label=None):
    label = label or staged_store.dir_label
    return {"meta": {"mode": "update-seed", "tracker": commodity.lower(), "country": country,
                     "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
                     "source": "review_app decisions (suggest lines + concerns called confirmed / needs_research)",
                     "source_dirs": [label(Path(d)) for d in dirs],
                     "unfilled": ["old", "tier", "refs"]},
            "rows": rows_from_units(units), "units": units}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--country", required=True)
    ap.add_argument("--commodity", required=True, choices=["gas", "oil"])
    ap.add_argument("--dirs", nargs="*", default=None, help="explicit staging dirs (skips discovery)")
    ap.add_argument("--batches-root", default=None, help="batches root (default: repo batches/)")
    ap.add_argument("--out", default=None,
                    help="default: <batches root>/<scope>/staging/update-seed-<YYYYMMDD>/staged_updates_seed.json")
    a = ap.parse_args(argv)
    root = Path(a.batches_root) if a.batches_root else staged_store.BATCHES_ROOT
    dirs = [Path(d) for d in a.dirs] if a.dirs else staged_store.discover_staging_dirs(
        a.country, a.commodity, root=root, include_assembled=True)
    if not dirs:
        sys.exit(f"no staging dirs found for {a.country} {a.commodity}")
    units, stats = collect(dirs)
    seed = build_seed(units, dirs, a.country, a.commodity)
    out = Path(a.out) if a.out else (root / staged_store.scope_dirname(a.country, a.commodity) / "staging" /
                                     f"update-seed-{datetime.now().strftime('%Y%m%d')}" / "staged_updates_seed.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(seed, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"update seed {a.country} {a.commodity}: {stats['suggest']} update unit(s) from suggest lines, "
          f"{stats['research']} research unit(s) from concerns ({stats['answered_by_suggest']} answered by a suggest "
          f"that took their candidate), {stats['dirs_with_decisions']} of {stats['dirs']} "
          f"dir(s) carry decisions -> {out}")
    return seed


if __name__ == "__main__":
    main()
