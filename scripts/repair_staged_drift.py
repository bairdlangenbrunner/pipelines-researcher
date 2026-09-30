#!/usr/bin/env python3
"""One-off, idempotent repair of schema drift in committed staged JSON stores.

Walks batches/*/staging/**/staged_resolutions.json and staged_new.json (skips
*.prior.json and archive/ dirs) and normalizes three kinds of drift so the
review-app dataset builder (docs/plans/2026-09-30_review-app.md, milestone 0)
does not have to parse around bad data:

  1. sheet_row stored as a digit string ("123") -> int.
  2. proposed_refs / verifications stored as the Python repr of a list
     ("['https://...']", "[{'url': ...}]", seen in iran-gas STATUS records)
     -> the real list, via ast.literal_eval (left alone + warned if it fails).
  3. staged_new.json only: old israel-gas candidates carrying "<col> [ref]"
     keys inside `values` (comma-joined URL strings) -> moved into the
     candidate's `refs` dict as {"<col> [ref]": [url, ...]}, merged with any
     existing list without duplicates, and removed from `values`.

Default is --dry-run (table of per-file counts, nothing written). --apply
rewrites files, preserving each file's JSON style (indent from the second
line, ensure_ascii from the existing bytes, trailing newline, key order) so
the git diff touches only repaired lines. Re-running --apply reports zero.
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAMES = ("staged_resolutions.json", "staged_new.json")


def find_files():
    out = []
    for p in sorted(ROOT.glob("batches/*/staging/**/*.json")):
        if p.name not in NAMES or p.name.endswith(".prior.json"):
            continue
        rel = p.relative_to(ROOT).parts
        if "archive" in rel:
            continue
        out.append(p)
    return out


def detect_style(text):
    lines = text.split("\n")
    indent = None
    if len(lines) > 1:
        m = re.match(r"^( +)", lines[1])
        indent = len(m.group(1)) if m else None
    if "\\u" in text:
        ensure_ascii = True
    elif any(ord(c) > 127 for c in text):
        ensure_ascii = False
    else:
        ensure_ascii = True
    return indent, ensure_ascii, text.endswith("\n")


def records_of(data):
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ("resolutions", "candidates", "new", "records"):
            if isinstance(data.get(k), list):
                return data[k]
        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                return v
    return []


def repair(data, is_new, path):
    c = {"sheet_row": 0, "repr_lists": 0, "inline_refs": 0}
    for rec in records_of(data):
        if not isinstance(rec, dict):
            continue
        sr = rec.get("sheet_row")
        if isinstance(sr, str) and sr.strip().isdigit():
            rec["sheet_row"] = int(sr.strip())
            c["sheet_row"] += 1
        for key in ("proposed_refs", "verifications"):
            v = rec.get(key)
            if isinstance(v, str):
                try:
                    parsed = ast.literal_eval(v)
                    if not isinstance(parsed, list):
                        raise ValueError("not a list")
                    rec[key] = parsed
                    c["repr_lists"] += 1
                except (ValueError, SyntaxError):
                    print(f"WARN literal_eval failed: {path.relative_to(ROOT)} "
                          f"project_id={rec.get('project_id')} ref_col={rec.get('ref_col')} field={key}",
                          file=sys.stderr)
        if is_new:
            vals = rec.get("values")
            if isinstance(vals, dict):
                ref_keys = [k for k in vals if k.endswith(" [ref]")]
                if ref_keys:
                    refs = rec.get("refs")
                    if not isinstance(refs, dict):
                        refs = {}
                    for k in ref_keys:
                        raw = vals.pop(k)
                        urls = ([u.strip() for u in raw.split(", ")] if isinstance(raw, str)
                                else [str(u).strip() for u in (raw or [])])
                        urls = [u for u in urls if u]
                        cur = refs.get(k)
                        cur = list(cur) if isinstance(cur, list) else ([cur] if cur else [])
                        for u in urls:
                            if u not in cur:
                                cur.append(u)
                        refs[k] = cur
                    rec["refs"] = refs
                    c["inline_refs"] += 1
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--file", action="append", help="process only this file (repeatable)")
    a = ap.parse_args()
    files = [Path(f).resolve() for f in a.file] if a.file else find_files()
    tot = {"sheet_row": 0, "repr_lists": 0, "inline_refs": 0}
    rows, changed = [], []
    for p in files:
        text = p.read_text(encoding="utf-8")
        indent, ea, nl = detect_style(text)
        data = json.loads(text)
        c = repair(data, p.name == "staged_new.json", p)
        if any(c.values()):
            rows.append((p, c))
            for k in tot:
                tot[k] += c[k]
            if a.apply:
                out = json.dumps(data, indent=indent, ensure_ascii=ea) + ("\n" if nl else "")
                p.write_text(out, encoding="utf-8")
                changed.append(p)
    print(f"{'file':<90} {'sheet_row':>9} {'repr_lists':>10} {'inline_refs':>11}")
    for p, c in rows:
        try:
            name = str(p.relative_to(ROOT))
        except ValueError:
            name = str(p)
        print(f"{name:<90} {c['sheet_row']:>9} {c['repr_lists']:>10} {c['inline_refs']:>11}")
    print(f"{'TOTAL (' + str(len(rows)) + ' files)':<90} {tot['sheet_row']:>9} {tot['repr_lists']:>10} {tot['inline_refs']:>11}")
    print("APPLIED" if a.apply else "DRY RUN (nothing written)")


if __name__ == "__main__":
    main()
