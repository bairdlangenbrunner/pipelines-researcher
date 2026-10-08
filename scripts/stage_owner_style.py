#!/usr/bin/env python3
"""Stage the owner-style normalization batch over EXISTING Operator and Owner1..Owner11 cells of
the "Pipeline operators/owners" tab (docs/reference/owner_style.md;
docs/plans/2026-10-05_owner-style-normalization.md, Phase 1).

Reads an operators/owners snapshot, runs every non-blank Operator / Owner<N> cell through
scripts/entity_style.py and stages a change for each cell whose styled form differs AND which
`entity_style.adoptable()` allows: an EXACT gazetteer match or a CONFIRMED alias (high), a RULING
in data/owner_rulings.json (high; a cell ruling may also CLEAR a cell), or a rules / stem result
whose flags are all mechanical (medium; the entity is the same, only the spelling moves).
Everything else is listed under `held_back` with its reason so the ruling surface is complete:

  fuzzy_candidates / alias_candidate / form_conflict / form_ambiguous / acronym_not_initials /
  no_legal_form / non_latin / ...   the styler's judgment flag (docs/reference/owner_style.md)
  comma_list           a comma survives in a rules-only value: a list the rules cannot split
  multi_operator       one Operator cell lists several operators ('A; B') and no ruling covers it
  row_collision        two Owner<N> slots on ONE row would style to the SAME name ('Saudi Aramco'
                       + 'Aramco') — merging shares is a human call, both cells held
                       (Operator is never part of a collision: Operator == Owner1 is normal)
  rules_only / stem_medium   a rules / stem result with no flag at all (nothing to adopt on)

No research, no URLs, no `[ref]` change: the Owner [ref] / Operator [ref] cells stay as they are,
only the spelling of Owner<N> / Operator moves. The store is marked `style_only`, so a push of an
accepted line updates `LastUpdated` only and leaves `Researcher` alone (Baird 2026-10-05).
AggregateOwners and the tracker's Owner / Operator columns are formulas and follow on their own.
The store is deliberately UNSCOPED (`meta.country = ""`): no country packet picks it up; the review
app reads it through its tracker-wide scope (country `*`).

    python scripts/stage_owner_style.py [--owners-csv data/GEM_operators_owners_snapshot_<date>.csv]
                                        [--staging batches/owners-style/staging/update-owner-style-<date>]
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import glob
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import entity_style as ES  # noqa: E402

TIER_BY_BASIS = {"exact": "high", "alias": "high", "ruling": "high", "rules": "medium", "stem": "medium"}


def col_order(c: str) -> int:
    """Sheet order of the name columns: Operator first, then Owner1..Owner11."""
    return 0 if c == "Operator" else int(c[5:])


def latest_owners_csv() -> Path:
    files = sorted(glob.glob(str(REPO / "data" / "GEM_operators_owners_snapshot_*.csv")))
    if not files:
        sys.exit("no operators/owners snapshot in data/ — run ./scripts/refresh_csvs.sh")
    return Path(files[-1])


def held_reason(r: ES.StyleResult, col: str) -> str:
    if "multi_owner" in r.flags and col == "Operator" and r.basis != "ruling":
        return "multi_operator"
    for f in r.flags:
        if f in ES.JUDGMENT_FLAGS:
            return f
    if "," in r.styled and r.basis in ("rules", "stem"):
        return "comma_list"
    return "stem_medium" if r.basis == "stem" else "rules_only"


def evidence(r: ES.StyleResult) -> str:
    if r.basis == "exact":
        e = f"exact gazetteer match {r.entity_id or '(no entity id)'}"
    elif r.basis == "alias":
        e = f"confirmed alias in data/owner_aliases.json -> {r.styled!r}" + (f" {r.entity_id}" if r.entity_id else "")
    elif r.basis == "ruling":
        e = r.note                                    # "ruled by Baird <date>: <ruling>"
    else:
        e = "spelling rules only (" + ", ".join(r.flags) + "); no gazetteer hit, entity unchanged"
    if ("acronym_dropped" in r.flags or "acronym_lead" in r.flags) and r.aliases:
        e += f"; dropped acronym {r.aliases[0]!r} kept as an alias"
    return e


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--owners-csv", type=Path, default=None)
    ap.add_argument("--staging", type=Path, default=None,
                    help="store dir (default batches/owners-style/staging/update-owner-style-<today>)")
    a = ap.parse_args()
    src = a.owners_csv or latest_owners_csv()
    today = dt.date.today().isoformat()
    staging = (a.staging or (REPO / "batches" / "owners-style" / "staging"
                             / f"update-owner-style-{today.replace('-', '')}")).resolve()

    with src.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    hdr = [c.strip() for c in rows[1]]            # row 0 is the filter-view banner
    idx = {c: i for i, c in enumerate(hdr)}
    owner_cols = [c for c in hdr if c.startswith("Owner") and c[5:].isdigit()]
    name_cols = (["Operator"] if "Operator" in idx else []) + owner_cols

    def cell(row, col):
        i = idx[col]
        v = row[i].strip() if i < len(row) else ""
        return "" if v == "#N/A" else v       # the sheet's lookup columns on a row with no tracker match

    styled: dict[str, ES.StyleResult] = {}
    names: dict[str, dict] = {}
    staged_rows: dict[str, dict] = {}
    held: list[dict] = []
    n_cells = 0
    n_by_col: collections.Counter = collections.Counter()

    def hold(pid, sheet_row, col, raw, r, reason, note=""):
        h = {"project_id": pid, "sheet_row": sheet_row, "column": col, "current": raw,
             "styled": r.styled, "basis": r.basis, "confidence": r.confidence,
             "entity_id": r.entity_id, "flags": list(r.flags),
             "candidate": (r.candidates[0]["name"] if r.candidates else ""), "reason": reason}
        if note:
            h["note"] = note
        held.append(h)

    for ri in range(2, len(rows)):
        row = rows[ri]
        pid = cell(row, "ProjectID")
        if not pid:
            continue
        sheet_row = ri + 1                          # raw CSV row index -> 1-based sheet row
        proposals: dict[str, tuple[str, ES.StyleResult, str]] = {}   # col -> (raw, result, action)
        for col in name_cols:
            raw = cell(row, col)
            if not raw:
                continue
            n_cells += 1
            n_by_col["Operator" if col == "Operator" else "Owner<N>"] += 1
            r = styled.get(raw)
            if r is None:
                r = styled[raw] = ES.style(raw)
            d = names.setdefault(raw, {"styled": r.styled, "changed": r.changed, "basis": r.basis,
                                       "confidence": r.confidence, "entity_id": r.entity_id,
                                       "legal_form": r.legal_form, "aliases": list(r.aliases),
                                       "flags": list(r.flags), "cells": 0, "operator_cells": 0, "pids": []})
            d["cells"] += 1
            if col == "Operator":
                d["operator_cells"] += 1
            if pid not in d["pids"]:
                d["pids"].append(pid)
            cr = ES.cell_ruling(pid, col)
            if cr:                                  # a ruling on THIS cell beats the name's styling
                rr = ES.StyleResult(raw=raw, styled=("" if cr.get("clear") else cr.get("styled", raw)))
                rr.basis, rr.confidence, rr.flags = "ruling", "high", ["ruled"]
                rr.note = f"ruled by Baird {cr.get('date', '')}: {cr.get('ruling', '')}".strip()
                if rr.styled != raw:
                    proposals[col] = (raw, rr, "clear" if cr.get("clear") else "change")
                continue
            if not r.changed:
                continue
            if not ES.adoptable(r):
                hold(pid, sheet_row, col, raw, r, held_reason(r, col))
                continue
            proposals[col] = (raw, r, "change")

        if not proposals:
            continue
        # row collision: after the proposals, would two Owner<N> slots carry one name?
        # (Operator sits outside: the operator is usually also Owner1, by design)
        final = {col: cell(row, col) for col in owner_cols if cell(row, col)}
        for col, (raw, r, action) in proposals.items():
            if col != "Operator":
                if action == "clear":
                    final.pop(col, None)
                else:
                    final[col] = r.styled
        collided = {c for c in final if sum(1 for v in final.values() if v.casefold() == final[c].casefold()) > 1}
        for col, (raw, r, action) in proposals.items():
            if col != "Operator" and col in collided:
                others = sorted(c for c in final if c != col and final[c].casefold() == final[col].casefold())
                hold(pid, sheet_row, col, raw, r, "row_collision",
                     f"would equal {', '.join(others)} on this row — merge the shares by hand")
                continue
            staged_rows.setdefault(pid, {
                "pipeline": cell(row, "PipelineName"), "segment": cell(row, "SegmentName"),
                "fuel": cell(row, "Fuel"), "countries": cell(row, "CountriesorAreas"),
                "sheet_row": sheet_row, "tab": "operators_owners", "changes": {},
            })["changes"][col] = {
                "old": raw, "new": r.styled, "action": action, "tier": TIER_BY_BASIS.get(r.basis, "medium"),
                "basis": r.basis, "confidence": r.confidence, "entity_id": r.entity_id,
                "legal_form": r.legal_form, "aliases": list(r.aliases), "flags": list(r.flags),
                "evidence": evidence(r), "refs": [],
            }

    changes = [c for v in staged_rows.values() for c in v["changes"].values()]
    n_changes = len(changes)
    n_op_changes = sum(1 for v in staged_rows.values() for c in v["changes"] if c == "Operator")
    n_clear = sum(1 for c in changes if c["action"] == "clear")
    by_basis = collections.Counter(c["basis"] for c in changes)
    by_tier = collections.Counter(c["tier"] for c in changes)
    staged_names = sorted({c["old"] for c in changes})
    held_by = collections.Counter(h["reason"] for h in held)
    held_op = sum(1 for h in held if h["column"] == "Operator")
    out = {
        "meta": {
            "batch": staging.name,
            "mode": "update",
            "tracker": "both",
            "country": "",            # tracker-wide: deliberately NOT a (country, commodity) scope,
                                      # so discovery/handoff never pulls these rows into a country packet
            "style_only": True,       # a push updates LastUpdated only; Researcher stays (Baird 2026-10-05)
            "group_by": "name",       # the review app shows one card per current spelling, not per PID
            "scope": {"tab": "operators_owners", "columns": name_cols,
                      "description": "every non-blank Operator and Owner<N> cell of the operators/owners "
                                     "tab, both trackers, all countries"},
            "owners_csv": src.name,
            "researched": today,
            "method": "scripts/entity_style.py (data/owner_gazetteer.csv + data/owner_aliases.json + "
                      "data/owner_rulings.json); rules docs/reference/owner_style.md; adoption policy "
                      "entity_style.adoptable(); no web research, no URL changes",
            "slice": "exact gazetteer match / confirmed alias / Baird's ruling (high) and rules or stem "
                     "results whose flags are all mechanical (medium); styled form differs from the cell; "
                     "no judgment flag; no row collision",
            "url_verification": "n/a — no URL is proposed or changed; every Owner [ref] cell stays as it is",
            "summary": (f"{n_changes} cells ({n_changes - n_op_changes} Owner<N> + {n_op_changes} Operator; "
                        f"{n_clear} cleared) on {len(staged_rows)} ProjectIDs re-spelled to the ownership "
                        f"team's style ({len(staged_names)} distinct names; "
                        f"{', '.join(f'{k}={v}' for k, v in by_basis.most_common())}; "
                        f"{', '.join(f'{k}={v}' for k, v in by_tier.most_common())}); "
                        f"{len(held)} cells held back ({held_op} of them Operator; "
                        f"{', '.join(f'{k}={v}' for k, v in held_by.most_common())}). "
                        f"Input {src.name}: {n_cells} non-blank name cells "
                        f"({n_by_col['Owner<N>']} Owner<N> + {n_by_col['Operator']} Operator), "
                        f"{len(names)} distinct names."),
            "counts": {"cells_in": n_cells, "cells_in_by_column": dict(n_by_col), "names_in": len(names),
                       "changes": n_changes, "changes_owner": n_changes - n_op_changes,
                       "changes_operator": n_op_changes, "clears": n_clear,
                       "by_basis": dict(by_basis), "by_tier": dict(by_tier),
                       "pids": len(staged_rows), "names_changed": len(staged_names),
                       "held_back": dict(held_by), "held_back_operator": held_op},
        },
        "names": {k: names[k] for k in sorted(names, key=lambda n: (-names[n]["cells"], n))},
        "rows": {pid: staged_rows[pid] for pid in sorted(staged_rows)},
        "held_back": sorted(held, key=lambda h: (h["reason"], -names[h["current"]]["cells"], h["project_id"], h["column"])),
    }
    staging.mkdir(parents=True, exist_ok=True)
    outp = staging / "staged_updates.json"
    outp.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {outp.relative_to(REPO)}")
    print(out["meta"]["summary"])


if __name__ == "__main__":
    main()
