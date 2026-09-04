#!/usr/bin/env python3
"""Stamp `contested` (backend column -> candidate value) onto staged validity CONCERNS.

A validity record is read-and-flag: it never proposes an edit, so `build_ref_workbook.py`
kept it off the `<Cmdty>_Backend` mirror entirely. But a `spec` concern is a claim that a
CURRENT value is wrong, and the Backend mirror is the tab the README tells the researcher
to work from — so "Capacity 16,800 MMcf/d is contradicted by its own cited source" rendered
there as an ordinary untinted cell, indistinguishable from a value nobody questioned.
(Found by Baird on US-gas P0271/Transco, 2026-09-04: 58 spec concerns across 45 rows,
several naming a concrete correction, all invisible on the paste surface.)

The builder now renders concerns ORANGE on that mirror, reading the record's `contested`
map. Deep-sweep subagents author it going forward (sweep SOP + staged_json_schema.md);
this backfills it for work staged before the field existed, by matching backend column
names in the record's `recommendation` — the terse, action-shaped field that names the
disputed column ("correct StartYear1 from 2019 to 2018", "Update Capacity from 200.00
MMcf/d ...", "Adjudicate the SegmentCost conflict raised during the ref pass").

Matching is CASE-SENSITIVE against the live header's real column names, which is what
makes it precise: prose says "capacity", the column is `Capacity`. No candidate value is
parsed out of the prose — the recommendation rides verbatim into the cell comment, and a
mis-parsed number on a paste surface is exactly the failure this repo cannot afford.
A concern that names no column still marks its row (the builder tints the SheetRow cell).

Idempotent; records already carrying `contested` are left alone unless --overwrite.
Writes `staged_resolutions.json` (canonical pending state) and the matching `rows/*.json`
validity entries, so a later re-merge does not drop the field.

Rewrites are FORMAT-PRESERVING. Shards authored by subagents are not all in one canonical
json.dumps style (some carry inline one-line lists/dicts), so a blanket re-dump reformatted
464 files / 28k lines and buried the real change. A file that round-trips through its own
detected dump options is rewritten normally; anything else gets `contested` spliced into the
record's text in place, leaving every other byte untouched.

    python scripts/backfill_contested.py --staging batches/<scope>/staging/<dir>/        # dry run
    python scripts/backfill_contested.py --staging batches/<scope>/staging/<dir>/ --apply
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ref_pairs import discover_ref_pairs  # noqa: E402

VALIDITY_REF = "__VALIDITY__"

# Owner/Parent carry no `[ref]` on the tracker tab (their sources live on the separate
# operators/owners tab) so discover_ref_pairs emits no cluster for them — but they ARE
# backend columns, and an `attribution` concern disputes exactly them.
EXTRA_VALUE_COLS = ["Owner", "Parent"]

# `promote_ref_concerns.py` writes this exact shape when it lifts a `CONCERN:` note out of
# a ref record; the word it names is the ref CLUSTER (Start, Length, SegmentCost, ...),
# not a column, so it resolves through the cluster's primary value column.
_PROMOTED_RE = re.compile(r"Adjudicate the ([A-Za-z][A-Za-z0-9]*) conflict")


_TRACKER_GLOB = {"gas": "GGIT_gas_snapshot_*.csv", "oil": "GOIT_oil_ngl_snapshot_*.csv"}


def _load_header(staging: Path, meta: dict) -> list[str]:
    scope = meta.get("scope") or {}
    csv_name = scope.get("csv")
    if not csv_name:
        # older runs recorded only the tracker; the newest snapshot of it is the right
        # vocabulary anyway (this header is used ONLY to learn real column names)
        pat = _TRACKER_GLOB.get((scope.get("tracker") or "").strip().lower())
        snaps = sorted((Path(__file__).resolve().parent.parent / "data").glob(pat)) if pat else []
        if not snaps:
            return []
        csv_name = str(snaps[-1])
    cand = Path(csv_name)
    if not cand.exists():
        cand = Path(__file__).resolve().parent.parent / "data" / Path(csv_name).name
    if not cand.exists():
        return []
    with cand.open(newline="") as f:
        rows = list(csv.reader(f))
    return rows[2] if len(rows) > 2 else []


def build_vocab(header: list[str]):
    """(compiled column-name regex, cluster-stem -> primary value col, valid column set)."""
    pairs = discover_ref_pairs(header) if header else []
    value_cols: list[str] = []
    stem_primary: dict[str, str] = {}
    for p in pairs:
        for c in p.get("value_cols") or []:
            if c not in value_cols:
                value_cols.append(c)
        rc = p.get("ref_col")
        prim = p.get("primary_value_col") or (p.get("value_cols") or [None])[0]
        if rc and prim:
            stem_primary[rc[: -len(" [ref]")]] = prim
    for c in EXTRA_VALUE_COLS:
        if c in header and c not in value_cols:
            value_cols.append(c)
    # longest-first so `LengthKnownUnits` wins over `LengthKnown`, `StartYear2` over
    # `StartYear` — Python alternation is leftmost-first, not longest-match
    ordered = sorted(value_cols, key=len, reverse=True)
    rx = re.compile(r"\b(" + "|".join(re.escape(c) for c in ordered) + r")\b") if ordered else None
    return rx, stem_primary, set(value_cols)


def infer_contested(rec: dict, rx, stem_primary: dict, valid: set) -> dict:
    """Backend columns this concern disputes, in first-mention order. Candidates stay ""
    — see the module docstring on why no number is parsed out of the prose."""
    rec_text = (rec.get("recommendation") or "").strip()
    cols: list[str] = []

    def add(c):
        if c in valid and c not in cols:
            cols.append(c)

    m = _PROMOTED_RE.search(rec_text)
    if m:
        prim = stem_primary.get(m.group(1))
        if prim:
            add(prim)
    if rx:
        for hit in rx.finditer(rec_text):
            add(hit.group(1))
        if not cols:
            # legacy/terse recommendations sometimes name nothing; the finding's own
            # ALL-CAPS lead ("CAPACITY spec check:", "LENGTH UNIT DEFECT") does
            notes = (rec.get("researcher_notes") or "")[:120]
            lead = re.match(r"\s*([A-Z][A-Z/ &-]{2,30}?)\s*(?::|\b(?:spec|unit|defect)\b)", notes)
            if lead:
                want = lead.group(1).strip().replace(" ", "").lower()
                for stem, prim in stem_primary.items():
                    if stem.lower() == want:
                        add(prim)
                        break
    return {c: "" for c in cols}


def _object_start(text: str, pos: int):
    """Index of the `{` opening the object that contains `pos` (string-aware scan)."""
    stack, i, in_str, esc = [], 0, False, False
    while i < pos:
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            stack.append(i)
        elif c == "}":
            if stack:
                stack.pop()
        i += 1
    return stack[-1] if stack else None


def splice_contested(text: str, targets: list, ensure_ascii: bool) -> tuple:
    """Add `"contested": {...}` as the first key of each named record, editing the file's
    TEXT rather than re-serializing it — the only way to touch a hand-formatted shard
    without reformatting every other line of it.

    `targets` is [(researcher_notes, contested_dict)]; a record is located by the verbatim
    JSON encoding of its notes string, and the object containing that string is the record.
    Returns (new_text, n_spliced)."""
    used, n = set(), 0
    for notes, cont in targets:
        if not notes:
            continue
        anchor = json.dumps(notes, ensure_ascii=ensure_ascii)
        start = 0
        while True:
            hit = text.find(anchor, start)
            if hit < 0:
                break
            b = _object_start(text, hit)
            if b is None or b in used:
                start = hit + 1
                continue
            # match the indentation of the record's existing first key
            m = re.match(r"[^\S\n]*\n([^\S\n]*)", text[b + 1:])
            ws = m.group(1) if m else "  "
            payload = json.dumps(cont, ensure_ascii=ensure_ascii)
            text = text[:b + 1] + f'\n{ws}"contested": {payload},' + text[b + 1:]
            used.add(b)
            n += 1
            break
    return text, n


def write_preserving(path: Path, original: str, doc: dict, opts: dict, targets: list,
                     allow_splice: bool = True) -> str:
    """Canonical-style file -> plain re-dump; anything else -> splice. Returns a label.

    Splicing only ever ADDS a key, so --overwrite (which replaces an existing `contested`)
    must re-dump instead — a splice there would leave two `contested` keys in one object."""
    if not allow_splice or json.dumps(json.loads(original), **opts) == original:
        path.write_text(json.dumps(doc, **opts))
        return "dump"
    new, n = splice_contested(original, targets, opts["ensure_ascii"])
    if n != len(targets):
        print(f"  ! {path}: spliced {n} of {len(targets)} — falling back to a re-dump")
        path.write_text(json.dumps(doc, **opts))
        return "dump"
    json.loads(new)  # never write a file we just broke
    path.write_text(new)
    return "splice"


def _dump_opts(text: str, default: int = 2) -> dict:
    """The json.dumps kwargs the file was written with, so a rewrite stays diff-clean.
    Writers in this repo differ on both indent (1 vs 2) and ensure_ascii (an escaped
    \\u2014 vs a literal em dash); getting either wrong reformats 22k lines."""
    return {"indent": _indent_of(text, default),
            "ensure_ascii": text.isascii()}


def _indent_of(text: str, default: int = 2) -> int:
    """Indent width the file was written with."""
    for line in text.split("\n")[1:4]:
        n = len(line) - len(line.lstrip(" "))
        if n:
            return n
    return default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    ap.add_argument("--overwrite", action="store_true",
                    help="re-infer even where `contested` is already present")
    args = ap.parse_args()
    S = Path(args.staging)

    store_path = S / "staged_resolutions.json"
    raw = store_path.read_text()
    store = json.loads(raw)
    # preserve the file's existing indent (different writers in this repo use 1 or 2) —
    # a reformat would bury the real change in a whole-file diff
    opts = _dump_opts(raw)
    header = _load_header(S, store.get("meta") or {})
    if not header:
        print("! could not load the snapshot header named in meta.scope.csv — aborting")
        return 1
    rx, stem_primary, valid = build_vocab(header)

    # key a concern by (ProjectID, first 60 chars of the finding) so the same record can be
    # located in both the merged store and its rows/<PID>.json origin
    def key(pid, r):
        return (pid, (r.get("researcher_notes") or "")[:60])

    stamped: dict[tuple, dict] = {}
    store_targets: list[tuple[str, dict]] = []
    n_seen = n_hit = n_skip = 0
    for r in store.get("resolutions", []):
        if r.get("ref_col") != VALIDITY_REF or (r.get("verdict") or "").strip() != "concern":
            continue
        n_seen += 1
        if r.get("contested") and not args.overwrite:
            n_skip += 1
            continue
        cont = infer_contested(r, rx, stem_primary, valid)
        if not cont:
            continue
        n_hit += 1
        r["contested"] = cont
        stamped[key(r.get("project_id"), r)] = cont
        store_targets.append((r.get("researcher_notes") or "", cont))
        print(f"  {r.get('project_id'):<7} {r.get('concern_type','') :<14} "
              f"{', '.join(cont):<40} {(r.get('recommendation') or '')[:70]}")

    print(f"\n{n_hit} of {n_seen} concern(s) stamped "
          f"({n_seen - n_hit - n_skip} name no backend column — row-level marker only"
          f"{f'; {n_skip} already stamped' if n_skip else ''})")

    # mirror onto the shard-of-record so a re-merge keeps the field
    n_rows = 0
    rows_dir = S / "rows"
    row_files: list[tuple[Path, str, dict, dict, list]] = []
    for p in sorted(rows_dir.glob("*.json")) if rows_dir.is_dir() else []:
        rtxt = p.read_text()
        d = json.loads(rtxt)
        targets: list[tuple[str, dict]] = []
        for v in d.get("validity") or []:
            k = key(d.get("project_id"), v)
            if k in stamped and (not v.get("contested") or args.overwrite):
                v["contested"] = stamped[k]
                targets.append((v.get("researcher_notes") or "", stamped[k]))
                n_rows += 1
        if targets:
            row_files.append((p, rtxt, d, _dump_opts(rtxt), targets))
    print(f"{n_rows} matching record(s) in {len(row_files)} rows/*.json shard(s)")

    if not args.apply:
        print("\ndry run — re-run with --apply to write")
        return 0
    ok = not args.overwrite
    write_preserving(store_path, raw, store, opts, store_targets, ok)
    for p, rtxt, d, o, t in row_files:
        write_preserving(p, rtxt, d, o, t, ok)
    print(f"\nwrote {store_path} + {len(row_files)} shard(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
