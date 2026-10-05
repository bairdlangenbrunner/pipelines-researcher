#!/usr/bin/env python3
"""Re-spell the Owner<N> / Operator values in PENDING staged proposals the ownership team's way
(docs/reference/owner_style.md; Baird 2026-10-05: restyle the pending shards in place before
they are reviewed — docs/plans/2026-10-05_owner-style-normalization.md, Phase 0.3).

Walks every live staging dir under batches/*/staging/ (archive/ and parked dirs excluded):
`staged_resolutions.json` (what the review app and the workbooks read) and the shard inputs
`rows/*.json` (`fills[]`), so a re-merge cannot bring the old spelling back. For every record on
the operators/owners tab, each non-blank Owner<N> / Operator value that DIFFERS from the sheet's
current cell (a value equal to the sheet is carried, not proposed) is run through
scripts/entity_style.py and rewritten when `entity_style.adoptable()` says so: exact gazetteer
hit, confirmed alias, a ruling in data/owner_rulings.json, or a rules result whose flags are all
mechanical. The source's spelling goes into researcher_notes. Anything else is left as it is
and listed in the report (notes/owner-restyle-staged-<date>.md + .csv).

    python scripts/restyle_staged_owners.py            # dry run: report only
    python scripts/restyle_staged_owners.py --apply    # rewrite the JSON + write the report
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime as dt
import glob
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import entity_style as ES  # noqa: E402
from json_patch import patch_text  # noqa: E402

NAME_COL = re.compile(r"Owner\d+|Operator")
OO_REFS = ("Owner [ref]", "Operator [ref]")


def latest_owners_csv() -> Path:
    files = sorted(glob.glob(str(REPO / "data" / "GEM_operators_owners_snapshot_*.csv")))
    if not files:
        sys.exit("no operators/owners snapshot in data/ — run ./scripts/refresh_csvs.sh")
    return Path(files[-1])


def load_current(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    idx = {c.strip(): i for i, c in enumerate(rows[1])}       # row 0 is the filter-view banner
    pi = idx["ProjectID"]
    out: dict[str, dict[str, str]] = {}
    for r in rows[2:]:
        if pi < len(r) and r[pi].strip():
            out[r[pi].strip()] = {c: (r[i].strip() if i < len(r) else "") for c, i in idx.items()}
    return out


def is_oo(rec: dict) -> bool:
    return rec.get("tab") == "operators_owners" or (rec.get("ref_col") or "") in OO_REFS


def live_dirs() -> list[Path]:
    out = []
    for d in sorted(glob.glob(str(REPO / "batches" / "*" / "staging" / "*"))):
        p = Path(d)
        if not p.is_dir() or p.name.startswith("parked") or "/archive/" in d:
            continue
        out.append(p)
    return out


def note_line(col: str, raw: str, res: ES.StyleResult) -> str:
    bits = [f"{col} is written '{raw}' by the source; spelled the ownership team's way as '{res.styled}'"]
    acr = [a for a in res.aliases if a != raw and a != res.styled]
    if acr and ("acronym_dropped" in res.flags or "acronym_lead" in res.flags):
        bits.append(f"the acronym {acr[0]} is kept as an alias")
    if res.basis == "ruling":
        bits.append("per Baird's ruling of " + (res.note.split(":")[0].replace("ruled by Baird", "").strip() or "2026-10-05"))
    return ". ".join(bits) + "."


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="rewrite the staged JSON (default: report only)")
    ap.add_argument("--owners-csv", type=Path, default=None)
    ap.add_argument("--dry-run-dir", default=str(REPO / "work"), help="where a dry run writes its report (default work/)")
    a = ap.parse_args()
    src = a.owners_csv or latest_owners_csv()
    current = load_current(src)
    today = dt.date.today().isoformat()

    changed_rows: list[dict] = []      # one per cell rewritten
    held_rows: list[dict] = []         # one per cell left as it is (styler says change, policy says no)
    per_dir = collections.Counter()
    per_file = collections.Counter()
    seen_equal = 0
    cache: dict[str, ES.StyleResult] = {}

    def visit(rec: dict, dirp: str, fpath: Path, where: str, path: tuple, edits: list,
              file_pid: str = "") -> bool:
        """Restyle one record; -> True if anything changed. `path` locates the record in the
        file; the edits are (path-to-string, new text) pairs applied without re-serializing."""
        nonlocal seen_equal
        if not isinstance(rec, dict) or not is_oo(rec):
            return False
        vals = rec.get("values")
        if not isinstance(vals, dict):
            return False
        pid = rec.get("project_id") or file_pid or ""      # shard records carry no project_id
        cur = current.get(pid, {})
        touched = False
        for col, v in list(vals.items()):
            sv = str(v or "").strip()
            if not NAME_COL.fullmatch(str(col)) or not sv:
                continue
            if cur.get(col, None) is not None and cur.get(col, "") == sv:
                seen_equal += 1
                continue
            res = cache.get(sv)
            if res is None:
                res = cache[sv] = ES.style(sv)
            if not res.changed:
                continue
            row = {"dir": dirp, "file": str(fpath.relative_to(REPO)), "where": where, "project_id": pid,
                   "sheet_row": rec.get("sheet_row"), "column": col, "raw": sv, "styled": res.styled,
                   "basis": res.basis, "confidence": res.confidence, "flags": ",".join(res.flags),
                   "class_out": rec.get("class_out") or ""}
            if not ES.adoptable(res):
                row["reason"] = next((f for f in res.flags if f in ES.JUDGMENT_FLAGS),
                                     "comma_list" if "," in res.styled else res.basis)
                held_rows.append(row)
                continue
            changed_rows.append(row)
            per_dir[dirp] += 1
            per_file[str(fpath.relative_to(REPO))] += 1
            if a.apply:
                edits.append((path + ("values", col), res.styled))
                vals[col] = res.styled
                if rec.get("primary_value") == sv:
                    edits.append((path + ("primary_value",), res.styled))
                    rec["primary_value"] = res.styled
                nl = note_line(col, sv, res)
                notes = str(rec.get("researcher_notes") or "").strip()
                if nl not in notes:
                    notes = (notes + " " + nl).strip()
                    rec["researcher_notes"] = notes
                    edits[:] = [e for e in edits if e[0] != path + ("researcher_notes",)]
                    edits.append((path + ("researcher_notes",), notes))
                touched = True
        return touched

    def write(fpath: Path, text: str, edits: list) -> None:
        """Apply the string edits to the file's own text (formatting kept) and prove the result."""
        if not edits:
            return
        new = patch_text(text, edits)
        json.loads(new)                                     # must still parse
        fpath.write_text(new, encoding="utf-8")

    for d in live_dirs():
        dirp = str(d.relative_to(REPO))
        f = d / "staged_resolutions.json"
        if f.exists():
            text = f.read_text(encoding="utf-8")
            data = json.loads(text)
            edits: list = []
            if isinstance(data, dict):
                for i, r in enumerate(data.get("resolutions") or []):
                    visit(r, dirp, f, "resolutions", ("resolutions", i), edits)
            else:
                for i, r in enumerate(data):
                    visit(r, dirp, f, "resolutions", (i,), edits)
            if a.apply:
                write(f, text, edits)
        for rf in sorted((d / "rows").glob("*.json")) if (d / "rows").is_dir() else []:
            try:
                text = rf.read_text(encoding="utf-8")
                data = json.loads(text)
            except json.JSONDecodeError:
                continue
            edits = []
            if isinstance(data, dict):
                file_pid = str(data.get("project_id") or rf.stem)
                for key in ("fills", "resolutions"):
                    for i, r in enumerate(data.get(key) or []):
                        visit(r, dirp, rf, key, (key, i), edits, file_pid)
            elif isinstance(data, list):
                for i, r in enumerate(data):
                    visit(r, dirp, rf, "list", (i,), edits, rf.stem)
            if a.apply:
                write(rf, text, edits)

    # report
    stem = REPO / "notes" / f"owner-restyle-staged-{today}"
    if not a.apply:                      # a dry run still writes its report, to the scratchpad
        stem = Path(a.dry_run_dir) / f"owner-restyle-staged-{today}-dryrun"
    n_res = sum(1 for r in changed_rows if r["where"] == "resolutions" and r["file"].endswith("staged_resolutions.json"))
    names_changed = collections.Counter((r["raw"], r["styled"]) for r in changed_rows)
    held_by = collections.Counter(r["reason"] for r in held_rows)
    held_names = collections.Counter((r["raw"], r["styled"], r["reason"]) for r in held_rows)
    lines = [f"# Owner and operator spellings in pending staged work, restyled {today}", "",
             f"Mode: {'APPLIED' if a.apply else 'dry run (nothing written)'}. Sheet snapshot: `{src.name}`.", "",
             "Every pending staging dir was read. A proposed Owner or Operator value that differs from "
             "the sheet's current cell was run through the styler; the ones the policy allows (an exact "
             "gazetteer hit, a confirmed alias, a ruling, or a rules result with only mechanical "
             "flags) were rewritten, with the source's spelling kept in the researcher notes. "
             "The rest were left as they were and are listed below for a person.", "",
             f"- cells rewritten: {len(changed_rows)} ({n_res} in staged_resolutions.json files, the rest in shard rows)",
             f"- distinct re-spellings: {len(names_changed)}",
             f"- cells left as they were (a judgment, not a spelling): {len(held_rows)} — "
             + ", ".join(f"{k} {v}" for k, v in held_by.most_common()),
             f"- proposed values equal to the sheet (carried, not touched): {seen_equal}", "",
             "## Rewritten, by staging dir", ""]
    lines += [f"- `{k}`: {v}" for k, v in per_dir.most_common()]
    lines += ["", "## Re-spellings (cells)", ""]
    lines += [f"- '{r}' -> '{s}' ({n})" for (r, s), n in names_changed.most_common()]
    lines += ["", "## Left as they were (a person decides)", ""]
    lines += [f"- '{r}' -> '{s}'? {why} ({n})" for (r, s, why), n in held_names.most_common()]
    lines += ["", "Next: the review app and the workbooks read these files on their next build; a decided "
              "line keeps its decision (the spelling moved, the entity did not).", ""]
    report = "\n".join(lines)
    if True:
        stem.parent.mkdir(parents=True, exist_ok=True)
        stem.with_suffix(".md").write_text(report, encoding="utf-8")
        with stem.with_suffix(".csv").open("w", newline="", encoding="utf-8") as fh:
            cols = ["action", "dir", "file", "where", "project_id", "sheet_row", "column", "raw", "styled",
                    "basis", "confidence", "flags", "class_out", "reason"]
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            for r in changed_rows:
                w.writerow(dict(r, action="rewritten", reason=""))
            for r in held_rows:
                w.writerow(dict(r, action="left"))
        print(f"wrote {stem.with_suffix('.md')} + .csv")
    if a.apply:
        print(report)


if __name__ == "__main__":
    main()
