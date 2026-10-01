#!/usr/bin/env python3
"""Stage the first owner-style normalization slice over EXISTING Owner1..Owner11 cells of the
"Pipeline operators/owners" tab (docs/reference/owner_style.md; Baird 2026-10-01: lint first,
then a reviewable batch — gazetteer-backed, high-confidence changes only).

Reads the latest operators/owners snapshot, runs every non-blank Owner<N> cell through
scripts/entity_style.py and stages a `change` for each cell whose styled form differs AND
whose basis is an EXACT gazetteer match or a CONFIRMED alias (confidence high). Everything
else is listed under `held_back` with its reason so the ruling surface is complete:

  stem_medium          stem matched one gazetteer entry, legal form adopted (medium) — next slice
  rules_only           no gazetteer hit; punctuation/long-form rules only — next slice
  alias_candidate      resembles a canonical (subsidiary/JV/successor) — SPV ruling, by hand
  form_conflict        same stem, different legal form in the gazetteer — registration question
  acronym_not_initials dropped parenthetical is not the name's initials — look at it
  row_collision        two Owner<N> slots on ONE row would style to the SAME name (e.g. 'Saudi
                       Aramco' + 'Aramco') — merging shares is a human call, both cells held

No research, no URLs, no `[ref]` change: the Owner [ref] cell stays as it is (refs are
additive and untouched), only the spelling of Owner<N> moves. AggregateOwners and the tracker's
Owner column are formulas and follow on their own.

    python batches/owners-style/staging/update-owner-style-20261001/stage_owner_style.py \
        [--owners-csv data/GEM_operators_owners_snapshot_<date>.csv]
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

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "scripts"))
import entity_style as ES  # noqa: E402

ADOPT_BASES = ("exact", "alias")
NEVER_ADOPT_FLAGS = ("alias_candidate", "form_conflict", "form_ambiguous", "acronym_not_initials",
                     "multi_owner", "non_latin")


def latest_owners_csv() -> Path:
    files = sorted(glob.glob(str(REPO / "data" / "GEM_operators_owners_snapshot_*.csv")))
    if not files:
        sys.exit("no operators/owners snapshot in data/ — run ./scripts/refresh_csvs.sh")
    return Path(files[-1])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--owners-csv", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=HERE / "staged_updates.json")
    a = ap.parse_args()
    src = a.owners_csv or latest_owners_csv()

    with src.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    hdr = [c.strip() for c in rows[1]]            # row 0 is the filter-view banner
    idx = {c: i for i, c in enumerate(hdr)}
    owner_cols = [c for c in hdr if c.startswith("Owner") and c[5:].isdigit()]

    def cell(row, col):
        i = idx[col]
        v = row[i].strip() if i < len(row) else ""
        return "" if v == "#N/A" else v       # the sheet's lookup columns on a row with no tracker match

    styled: dict[str, ES.StyleResult] = {}
    names: dict[str, dict] = {}
    staged_rows: dict[str, dict] = {}
    held: list[dict] = []
    n_cells = 0

    for ri in range(2, len(rows)):
        row = rows[ri]
        pid = cell(row, "ProjectID")
        if not pid:
            continue
        sheet_row = ri + 1                          # raw CSV row index -> 1-based sheet row
        proposals: dict[str, tuple[str, ES.StyleResult]] = {}
        for col in owner_cols:
            raw = cell(row, col)
            if not raw:
                continue
            n_cells += 1
            r = styled.get(raw)
            if r is None:
                r = styled[raw] = ES.style(raw)
            d = names.setdefault(raw, {"styled": r.styled, "changed": r.changed, "basis": r.basis,
                                       "confidence": r.confidence, "entity_id": r.entity_id,
                                       "legal_form": r.legal_form, "aliases": list(r.aliases),
                                       "flags": list(r.flags), "cells": 0, "pids": []})
            d["cells"] += 1
            if pid not in d["pids"]:
                d["pids"].append(pid)
            if not r.changed:
                continue
            reason = None
            if any(f in r.flags for f in NEVER_ADOPT_FLAGS):
                reason = next(f for f in NEVER_ADOPT_FLAGS if f in r.flags)
            elif r.basis not in ADOPT_BASES or r.confidence != "high":
                reason = "stem_medium" if r.basis == "stem" else "rules_only"
            if reason:
                held.append({"project_id": pid, "sheet_row": sheet_row, "column": col, "current": raw,
                             "styled": r.styled, "basis": r.basis, "confidence": r.confidence,
                             "entity_id": r.entity_id, "flags": list(r.flags),
                             "candidate": (r.candidates[0]["name"] if r.candidates else ""),
                             "reason": reason})
                continue
            proposals[col] = (raw, r)

        if not proposals:
            continue
        # row collision: after the proposals, would two Owner<N> slots carry one name?
        final = {col: cell(row, col) for col in owner_cols if cell(row, col)}
        for col, (raw, r) in proposals.items():
            final[col] = r.styled
        counts = collections.Counter(v.casefold() for v in final.values())
        collided = {col for col, v in final.items() if counts[v.casefold()] > 1}
        for col in sorted(proposals, key=lambda c: int(c[5:])):
            raw, r = proposals[col]
            if col in collided or any(c in collided for c in collided if final[c].casefold() == r.styled.casefold()):
                others = sorted(c for c in final if c != col and final[c].casefold() == r.styled.casefold())
                held.append({"project_id": pid, "sheet_row": sheet_row, "column": col, "current": raw,
                             "styled": r.styled, "basis": r.basis, "confidence": r.confidence,
                             "entity_id": r.entity_id, "flags": list(r.flags), "candidate": "",
                             "reason": "row_collision",
                             "note": f"would equal {', '.join(others)} on this row — merge the shares by hand"})
                continue
            evid = (f"exact gazetteer match {r.entity_id or '(no entity id)'}" if r.basis == "exact"
                    else f"confirmed alias in data/owner_aliases.json -> {r.styled!r}"
                         + (f" {r.entity_id}" if r.entity_id else ""))
            if "acronym_dropped" in r.flags and r.aliases:
                evid += f"; dropped acronym {r.aliases[0]!r} kept as an alias"
            staged_rows.setdefault(pid, {
                "pipeline": cell(row, "PipelineName"), "segment": cell(row, "SegmentName"),
                "fuel": cell(row, "Fuel"), "countries": cell(row, "CountriesorAreas"),
                "sheet_row": sheet_row, "tab": "operators_owners", "changes": {},
            })["changes"][col] = {
                "old": raw, "new": r.styled, "action": "change", "tier": "high",
                "basis": r.basis, "entity_id": r.entity_id, "legal_form": r.legal_form,
                "aliases": list(r.aliases), "flags": list(r.flags), "evidence": evid, "refs": [],
            }

    n_changes = sum(len(v["changes"]) for v in staged_rows.values())
    staged_names = sorted({c["old"] for v in staged_rows.values() for c in v["changes"].values()})
    held_by = collections.Counter(h["reason"] for h in held)
    today = dt.date.today().isoformat()
    out = {
        "meta": {
            "batch": HERE.name,
            "mode": "update",
            "tracker": "both",
            "country": "",            # tracker-wide: deliberately NOT a (country, commodity) scope,
                                      # so discovery/handoff never pulls these rows into a country packet
            "scope": {"tab": "operators_owners", "columns": owner_cols,
                      "description": "every non-blank Owner<N> cell of the operators/owners tab, "
                                     "both trackers, all countries"},
            "owners_csv": src.name,
            "researched": today,
            "method": "scripts/entity_style.py (data/owner_gazetteer.csv + data/owner_aliases.json); "
                      "rules docs/reference/owner_style.md; no web research, no URL changes",
            "slice": "gazetteer-backed, high confidence: basis exact or confirmed alias; styled form differs "
                     "from the cell; no never-adopt flag; no row collision",
            "url_verification": "n/a — no URL is proposed or changed; every Owner [ref] cell stays as it is",
            "summary": (f"{n_changes} Owner<N> cells on {len(staged_rows)} ProjectIDs re-spelled to the "
                        f"ownership team's style ({len(staged_names)} distinct names); {len(held)} cells held back "
                        f"({', '.join(f'{k}={v}' for k, v in held_by.most_common())}). "
                        f"Input {src.name}: {n_cells} non-blank owner cells, {len(names)} distinct names."),
            "counts": {"cells_in": n_cells, "names_in": len(names), "changes": n_changes,
                       "pids": len(staged_rows), "names_changed": len(staged_names),
                       "held_back": dict(held_by)},
        },
        "names": {k: names[k] for k in sorted(names, key=lambda n: (-names[n]["cells"], n))},
        "rows": {pid: staged_rows[pid] for pid in sorted(staged_rows)},
        "held_back": sorted(held, key=lambda h: (h["reason"], -names[h["current"]]["cells"], h["project_id"], h["column"])),
    }
    a.out.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {a.out.relative_to(REPO)}")
    print(out["meta"]["summary"])


if __name__ == "__main__":
    main()
