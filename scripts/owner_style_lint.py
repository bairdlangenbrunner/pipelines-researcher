#!/usr/bin/env python3
"""Lint the EXISTING Owner1..Owner11 cells of the operators/owners tab against the ownership
team's naming style (docs/reference/owner_style.md; scripts/entity_style.py). Read-only and
counts-only: it stages nothing and writes nothing but a report under notes/ — the decision
whether to run a normalization batch over existing owners is Baird's (2026-10-01: "new owners
first, lint report on existing").

    python scripts/owner_style_lint.py [--owners-csv data/GEM_operators_owners_snapshot_<date>.csv]
                                       [--out notes/owner-style-lint-<today>.md] [--top 60]

Writes the markdown report plus a sibling `.csv` (one line per DISTINCT raw name: raw, styled,
basis, confidence, flags, entity_id, rows, pids) so a later Update batch can be scoped from it
without re-running the styler. Default input: the latest `data/GEM_operators_owners_snapshot_*.csv`
(header at row index 1 — row 0 is a filter-view banner).
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import glob
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import entity_style as ES  # noqa: E402

REPO = Path(__file__).resolve().parent.parent


def latest_owners_csv() -> Path | None:
    files = sorted(glob.glob(str(REPO / "data" / "GEM_operators_owners_snapshot_*.csv")))
    return Path(files[-1]) if files else None


def lint(owners_csv: Path) -> dict:
    with owners_csv.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    hdr = [c.strip() for c in rows[1]]
    idx = {c: i for i, c in enumerate(hdr)}
    owner_cols = [c for c in hdr if c.startswith("Owner") and c[5:].isdigit()]
    pid_i = idx["ProjectID"]
    by_name: dict[str, dict] = {}
    cells = 0
    for row in rows[2:]:
        pid = row[pid_i].strip() if pid_i < len(row) else ""
        if not pid:
            continue
        for c in owner_cols:
            i = idx[c]
            v = row[i].strip() if i < len(row) else ""
            if not v:
                continue
            cells += 1
            d = by_name.setdefault(v, {"rows": 0, "pids": set(), "cols": collections.Counter()})
            d["rows"] += 1
            d["pids"].add(pid)
            d["cols"][c] += 1
    results = {}
    for name in by_name:
        results[name] = ES.style(name)
    return {"csv": owners_csv.name, "cells": cells, "owner_cols": owner_cols,
            "by_name": by_name, "results": results}


def report(L: dict, out_md: Path, top: int) -> None:
    by_name, results = L["by_name"], L["results"]
    distinct = len(by_name)
    changed = {n: r for n, r in results.items() if r.changed}
    changed_rows = sum(by_name[n]["rows"] for n in changed)
    basis = collections.Counter(); conf = collections.Counter(); flags = collections.Counter()
    basis_rows = collections.Counter(); flag_rows = collections.Counter()
    for n, r in results.items():
        basis[r.basis] += 1; conf[r.confidence] += 1
        basis_rows[r.basis] += by_name[n]["rows"]
        for f in r.flags:
            flags[f] += 1; flag_rows[f] += by_name[n]["rows"]
    in_gaz = sum(1 for r in results.values() if r.basis in ("exact", "alias") and not r.changed)
    today = dt.date.today().isoformat()

    L_ = []
    L_.append(f"# Owner-style lint — existing Owner1..Owner11 cells ({today})\n")
    L_.append(f"Input: `data/{L['csv']}` (operators/owners tab, header row index 1). Styler: "
              f"`scripts/entity_style.py` against `data/owner_gazetteer.csv` + `data/owner_aliases.json`. "
              f"Rules: `docs/reference/owner_style.md`.\n")
    L_.append("**Counts only.** Nothing is staged and nothing is written to the sheet; this report is "
              "the input to a decision on whether to run a normalization batch over existing owners "
              "(Baird 2026-10-01: new owners first, lint on existing). The sibling `.csv` holds one "
              "line per distinct name so that batch can be scoped from it.\n")
    L_.append("## Headline\n")
    L_.append("| | distinct names | owner cells |\n|---|---:|---:|")
    L_.append(f"| non-blank Owner<N> cells | {distinct} | {L['cells']} |")
    L_.append(f"| already in team style (exact gazetteer / confirmed alias, unchanged) | {in_gaz} | "
              f"{sum(by_name[n]['rows'] for n, r in results.items() if r.basis in ('exact', 'alias') and not r.changed)} |")
    L_.append(f"| styler would CHANGE | {len(changed)} | {changed_rows} |")
    L_.append(f"| … of which gazetteer-backed (exact / alias / stem) | "
              f"{sum(1 for r in changed.values() if r.basis in ('exact', 'alias', 'stem'))} | "
              f"{sum(by_name[n]['rows'] for n, r in changed.items() if r.basis in ('exact', 'alias', 'stem'))} |")
    L_.append(f"| … of which rules-only (no gazetteer hit) | "
              f"{sum(1 for r in changed.values() if r.basis == 'rules')} | "
              f"{sum(by_name[n]['rows'] for n, r in changed.items() if r.basis == 'rules')} |\n")
    L_.append("## By basis (all distinct names)\n")
    L_.append("| basis | distinct | cells |\n|---|---:|---:|")
    for b, n in basis.most_common():
        L_.append(f"| {b} | {n} | {basis_rows[b]} |")
    L_.append("\n## By confidence\n")
    L_.append("| confidence | distinct |\n|---|---:|")
    for c, n in conf.most_common():
        L_.append(f"| {c} | {n} |")
    L_.append("\n## By flag (a name can carry several)\n")
    L_.append("| flag | distinct | cells | meaning |\n|---|---:|---:|---|")
    meaning = {
        "no_legal_form": "no trailing legal form recognized — add one if a quick registry search gives it",
        "form_punctuation": "legal form spelled with punctuation (`Co., Ltd.`, `S.p.A.`)",
        "form_long": "long form (`Corporation`, `Company Limited`) where the team writes the short one",
        "form_moved": "legal form leads the name (`PAO Gazprom`); the team writes it trailing",
        "form_russian": "CIS form (OOO/PAO/AO/TOO) mapped to LLC/PJSC/JSC/LLP",
        "form_check_registration": "ZAO/OAO/NJSC — keep only if the entity is still registered under it",
        "form_from_gazetteer": "stem matches ONE gazetteer entry; its legal form adopted (medium)",
        "form_conflict": "same stem in the gazetteer under a DIFFERENT form — registration question",
        "form_ambiguous": "same stem in the gazetteer under several forms — pick by hand",
        "acronym_dropped": "trailing parenthetical acronym dropped (kept as alias)",
        "acronym_not_initials": "the dropped parenthetical is not the name's initials — look at it",
        "dots_stripped": "dotted abbreviation (`U.S.A.`) written without dots",
        "quotes_stripped": "quotation marks around the name removed",
        "state_body": "ministry / government rewritten to `Body (Country)` / `Government of X`",
        "alias_candidate": "owner_aliases.json lists it as a CANDIDATE (subsidiary/JV/successor) — never adopted",
        "fuzzy_candidates": "fuzzy gazetteer near-match listed, not adopted",
        "jv": "joint venture — no legal form expected",
        "group": "`… Group` — may be a holding name with no form",
        "multi_owner": "several owners in ONE cell — the sheet wants one per Owner<N>",
        "non_latin": "non-Latin script — romanized legal name wanted",
        "percent_stripped": "`[55%]` tail stripped — the share belongs in Owner<N>%",
        "former": "`[former]` tail kept",
    }
    for f, n in flags.most_common():
        L_.append(f"| `{f}` | {n} | {flag_rows[f]} | {meaning.get(f, '')} |")
    L_.append(f"\n## Top {top} changes by owner cells affected\n")
    L_.append("| cells | PIDs | raw | styled | basis/conf | flags |\n|---:|---:|---|---|---|---|")
    for n, r in sorted(changed.items(), key=lambda kv: (-by_name[kv[0]]["rows"], kv[0]))[:top]:
        d = by_name[n]
        L_.append(f"| {d['rows']} | {len(d['pids'])} | {n} | {r.styled} | {r.basis}/{r.confidence} | "
                  f"{', '.join(r.flags)} |")
    L_.append("\n## Not for the styler to decide (listed for a human)\n")
    for key, title in (("multi_owner", "Several owners in one cell"),
                       ("alias_candidate", "Subsidiary / JV / successor of a canonical entity (SPV ruling: stays as is)"),
                       ("form_conflict", "Same stem, different legal form in the gazetteer"),
                       ("acronym_not_initials", "Dropped parenthetical that is not the name's initials")):
        names = sorted((n for n, r in results.items() if key in r.flags),
                       key=lambda n: -by_name[n]["rows"])
        L_.append(f"### {title} — {len(names)}\n")
        for n in names[:25]:
            r = results[n]
            extra = f" ~ {r.candidates[0]['name']!r}" if r.candidates else ""
            L_.append(f"- {n!r} ({by_name[n]['rows']} cells){extra}")
        if len(names) > 25:
            L_.append(f"- … {len(names) - 25} more in the csv")
        L_.append("")
    out_md.write_text("\n".join(L_) + "\n", encoding="utf-8")

    out_csv = out_md.with_suffix(".csv")
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["raw", "styled", "changed", "basis", "confidence", "flags", "entity_id",
                    "legal_form", "aliases", "candidate_1", "cells", "n_pids", "pids"])
        for n, r in sorted(results.items(), key=lambda kv: (-kv[1].changed, -by_name[kv[0]]["rows"], kv[0])):
            d = by_name[n]
            w.writerow([n, r.styled, int(r.changed), r.basis, r.confidence, "|".join(r.flags),
                        r.entity_id, r.legal_form, "|".join(r.aliases),
                        r.candidates[0]["name"] if r.candidates else "",
                        d["rows"], len(d["pids"]), " ".join(sorted(d["pids"]))])
    print(f"wrote {out_md} and {out_csv}: {distinct} distinct names, {len(changed)} would change "
          f"({changed_rows} of {L['cells']} cells)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--owners-csv", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--top", type=int, default=60)
    a = ap.parse_args()
    src = a.owners_csv or latest_owners_csv()
    if not src or not Path(src).exists():
        sys.exit("no operators/owners snapshot in data/ — run ./scripts/refresh_csvs.sh")
    out = a.out or (REPO / "notes" / f"owner-style-lint-{dt.date.today().isoformat()}.md")
    report(lint(Path(src)), out, a.top)


if __name__ == "__main__":
    main()
