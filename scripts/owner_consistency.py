#!/usr/bin/env python3
"""One company, one spelling: group every Owner<N> / Operator spelling by company and say which
groups still hold more than one (Baird 2026-10-20; docs/plans/2026-10-20_owner-consistency.md,
step 2).

The styler (scripts/entity_style.py) works one cell at a time, so `Transco` in one row and
`Transcontinental Gas Pipe Line Company LLC` in the next were never compared. This script reads
every name cell on the newest operators/owners snapshot plus every pending staged value (live
staging dirs; archive/ and parked dirs excluded) and groups them by company. Two spellings join
one group when

  * they style to the same name, or
  * they share the same stem once the legal form is taken off (`Enbridge` / `Enbridge Inc`,
    `Kuwait Petroleum Corp` / `Kuwait Petroleum Co`; `Pipe Line` and `Pipeline` count as one), or
  * one is a short name of the other (`Transco` / `Transcontinental Gas Pipe Line ...`) and the
    two sit on the same row at least twice.

The gazetteer's entity_id is NOT a join: the ownership export gives one id to names that are
different companies (Eni SpA and Egyptian Natural Gas Holding Co share E100000000610). A name
the normalizer reduces to nothing (Arabic, Chinese) is left on its own. A whole name that is the
first word of a longer one (`Transneft` / `Transneft-Sibir`, `ADNOC` / `ADNOC Gas`) is a parent
and a subsidiary, not a short name, so it is never joined that way. A comma list of several
companies is held on its own and never grouped.

A group then gets a class:

  ruled       every spelling resolves to one name through data/owner_rulings.json
  settled     every spelling styles to one name and the styler may adopt each re-spelling itself;
              re-staging the style store (plan step 4) fixes it with no ruling
  held        every spelling styles to one name, but some re-spellings are held for a person
              (`no_legal_form` on a bare name and the like); a ruling settles it
  split       the spellings style to more than one name; a ruling settles it, after a registry
              check that they really are one company
  pair        joined only through a short name seen on the same rows; check before ruling

`proposed` is the name the group would take: a ruling's name, else the ownership team's
gazetteer spelling when exactly one member matches it exactly, else the styled name every member
shares, else blank. Near groups (one stem plus one distinguishing word, `Energy Transfer` /
`Energy Transfer Partners`) are listed apart so they are checked one by one and kept apart where
they really differ. They are never joined.

    python scripts/owner_consistency.py                 # report: notes/owner-consistency-<date>.md + .csv
    python scripts/owner_consistency.py --show transco  # print the groups whose key contains it
    python scripts/owner_consistency.py rule --group "transcontinental gas pipeline" \\
        --styled "Transcontinental Gas Pipe Line Co LLC" --ruling "SEC EDGAR lists ..." [--alias Transco] [--apply]
    python scripts/owner_consistency.py rule --from-json rulings.json [--apply]
        # a list of {"group", "styled", "ruling", "alias": [...], "only": [...], "extra": [...]}

`rule` writes one data/owner_rulings.json entry per spelling in the group (the target spelling
too, so it re-checks clean), keeping the file's one-entry-per-line layout. Without --apply it
prints what it would write. Ruled spellings are then picked up by stage_owner_style.py,
restyle_staged_owners.py, push.py and the review app with no other change.
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
from normalize import normalize_name  # noqa: E402

NAME_COL = re.compile(r"Owner\d+|Operator")
OO_REFS = ("Owner [ref]", "Operator [ref]")
# words that tell two companies apart even when the rest of the name is the same
DISTINGUISHING = {"partners", "partnership", "holdings", "holding", "midstream", "energy", "group", "international",
                  "operating", "resources", "infrastructure", "transmission", "services", "gas", "oil", "pipeline",
                  "pipelines", "development", "investment", "investments", "capital", "us", "usa", "canada"}


# ----------------------------------------------------------------------------- inputs

def latest_owners_csv() -> Path:
    files = sorted(glob.glob(str(REPO / "data" / "GEM_operators_owners_snapshot_*.csv")))
    if not files:
        sys.exit("no operators/owners snapshot in data/ — run ./scripts/refresh_csvs.sh")
    return Path(files[-1])


def live_dirs() -> list[Path]:
    out = []
    for d in sorted(glob.glob(str(REPO / "batches" / "*" / "staging" / "*"))):
        p = Path(d)
        if not p.is_dir() or p.name.startswith("parked") or "/archive/" in d:
            continue
        out.append(p)
    return out


def sheet_cells(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    hdr = [c.strip() for c in rows[1]]                   # row 0 is the filter-view banner
    idx = {c: i for i, c in enumerate(hdr)}
    cols = [c for c in hdr if NAME_COL.fullmatch(c)]
    out = []
    for r in rows[2:]:
        pid = r[idx["ProjectID"]].strip() if idx["ProjectID"] < len(r) else ""
        if not pid:
            continue
        for c in cols:
            v = r[idx[c]].strip() if idx[c] < len(r) else ""
            if v:
                out.append({"src": "sheet", "pid": pid, "col": c, "value": v})
    return out


def staged_cells() -> list[dict]:
    out = []
    for d in live_dirs():
        f = d / "staged_resolutions.json"
        if not f.exists():
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        for rec in data.get("resolutions") or []:
            if not isinstance(rec, dict):
                continue
            if rec.get("tab") != "operators_owners" and (rec.get("ref_col") or "") not in OO_REFS:
                continue
            for c, v in (rec.get("values") or {}).items():
                sv = str(v or "").strip()
                if NAME_COL.fullmatch(str(c)) and sv:
                    out.append({"src": f"{d.parent.parent.name}/{d.name}", "pid": rec.get("project_id") or "",
                                "col": c, "value": sv})
    return out


# ----------------------------------------------------------------------------- grouping

_FORM_WORDS: set[str] | None = None


def form_words() -> set[str]:
    """Single-word legal forms (`co`, `inc`, `llc`, `pjsc`, `pao` ...), stripped from a stem key."""
    global _FORM_WORDS
    if _FORM_WORDS is None:
        ws = {k for k in ES.legal_forms() if " " not in k}
        ws |= set(ES.CIS_FORMS) | {"company", "corporation", "incorporated", "limited", "the"}
        _FORM_WORDS = {normalize_name(w) for w in ws if normalize_name(w)}
    return _FORM_WORDS


def stem_key(name: str) -> str:
    """`Transcontinental Gas Pipe Line Company, LLC` -> `transcontinental gas pipeline`."""
    stem, _, _ = ES.split_legal_form(name)
    t = normalize_name(stem or name)
    t = re.sub(r"\bpipe line(s?)\b", r"pipeline\1", t)
    toks = t.split()
    fw = form_words()
    while toks and toks[0] in fw:
        toks.pop(0)
    while toks and toks[-1] in fw:
        toks.pop()
    return " ".join(toks)


def is_short_name(short: str, full: str) -> bool:
    """`Transco` of `Transcontinental Gas Pipe Line Co LLC`, `SNGPL` of `Sui Northern Gas Pipelines
    Ltd`: one word, at least 3 letters, and an abbreviation of the full name's stem."""
    s = short.strip()
    if " " in s or len(re.sub(r"[^A-Za-z0-9]", "", s)) < 3:
        return False
    stem, _, _ = ES.split_legal_form(full)
    words = normalize_name(stem).split()
    if len(words) < 2:
        return False
    a = re.sub(r"[^a-z0-9]", "", normalize_name(s))
    if a == words[0]:
        return False                       # a parent and its subsidiary, not a short name
    skip = ("of", "and", "the", "de", "del")
    for ws in (words, normalize_name(full).split()):   # the form's initial may count: SNGPL
        if "".join(w[0] for w in ws if w not in skip).startswith(a):
            return True                    # initials: SNGPL, ADNOC
    return len(a) >= 5 and words[0].startswith(a)   # a clipped first word: Transco


class UF:
    def __init__(self):
        self.p: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[max(ra, rb)] = min(ra, rb)


def skip_value(res: ES.StyleResult) -> bool:
    """Lists of owners and slashed names are held on their own (owner_style.md); never grouped."""
    if {"multi_owner", "slash"} & set(res.flags) or ";" in res.raw:
        return True
    return "," in res.styled and res.basis in ("rules", "stem")   # `A, B, C`: a list the rules cannot see


def build(cells: list[dict]) -> dict:
    styled: dict[str, ES.StyleResult] = {}
    for c in cells:
        if c["value"] not in styled:
            styled[c["value"]] = ES.style(c["value"])
    values = [v for v, r in styled.items() if not skip_value(r)]
    uf = UF()
    by_key: dict[str, str] = {}
    pair_join: set[tuple[str, str]] = set()
    for v in values:
        r = styled[v]
        uf.find(v)
        for k in ("s:" + normalize_name(r.styled), "k:" + stem_key(r.styled), "k:" + stem_key(v)):
            if len(k) <= 2:
                continue
            if k in by_key:
                uf.union(v, by_key[k])
            else:
                by_key[k] = v
    # short names that sit on the same row as the full name, twice or more
    row_vals: dict[str, set[str]] = collections.defaultdict(set)
    for c in cells:
        if c["value"] in uf.p:
            row_vals[c["pid"]].add(c["value"])
    co = collections.Counter()
    for vs in row_vals.values():
        for a in vs:
            for b in vs:
                if a != b and is_short_name(a, b):
                    co[(a, b)] += 1
    for (a, b), n in co.items():
        if n >= 2 and uf.find(a) != uf.find(b):
            pair_join.add((a, b))
            uf.union(a, b)
    paired_roots = {uf.find(a) for a, _ in pair_join}

    groups: dict[str, dict] = {}
    for c in cells:
        v = c["value"]
        if v not in uf.p:
            continue
        g = groups.setdefault(uf.find(v), {"spellings": collections.defaultdict(lambda: {
            "cells": 0, "sheet": 0, "staged": 0, "pids": set(), "srcs": set()})})
        s = g["spellings"][v]
        s["cells"] += 1
        s["sheet" if c["src"] == "sheet" else "staged"] += 1
        s["pids"].add(c["pid"])
        s["srcs"].add(c["src"])
    out = {}
    for root, g in groups.items():
        sp = g["spellings"]
        rs = {v: styled[v] for v in sp}
        targets = {r.styled for r in rs.values()}
        ruled = {r.styled for r in rs.values() if r.basis == "ruling"}
        exact = {r.styled for r in rs.values() if r.basis == "exact"}
        if len(ruled) == 1:
            proposed = next(iter(ruled))
        elif len(exact) == 1:
            proposed = next(iter(exact))
        elif len(targets) == 1:
            proposed = next(iter(targets))
        else:
            proposed = ""
        if len(sp) == 1 and len(targets) == 1 and not next(iter(rs.values())).changed:
            continue                                      # one spelling, already styled
        if len(targets) == 1 and all(r.basis == "ruling" or not r.changed for r in rs.values()):
            klass = "ruled"
        elif len(targets) == 1 and not any(ES.needs_person(r) for r in rs.values()):
            klass = "settled"
        elif len(targets) == 1:
            klass = "held"
        else:
            klass = "split"
        if root in paired_roots and klass != "ruled":
            klass = "pair"
        if len(sp) == 1 and klass in ("settled", "held"):
            continue                                      # one spelling: the style store's business, not a consistency one
        key = stem_key(proposed or max(sp, key=lambda v: sp[v]["cells"]))
        out[key] = {
            "key": key, "class": klass, "proposed": proposed,
            "cells": sum(s["cells"] for s in sp.values()),
            "spellings": [{
                "value": v, "cells": s["cells"], "sheet": s["sheet"], "staged": s["staged"],
                "styled": rs[v].styled, "basis": rs[v].basis, "flags": rs[v].flags,
                "entity_id": rs[v].entity_id, "held": ES.needs_person(rs[v]),
                "pids": sorted(s["pids"]), "srcs": sorted(s["srcs"])}
                for v, s in sorted(sp.items(), key=lambda kv: -kv[1]["cells"])],
        }
    near = near_groups(out, styled, values)
    return {"groups": out, "near": near}


def near_groups(groups: dict, styled: dict, values: list[str]) -> list[dict]:
    """Stems that differ by one distinguishing word (`energy transfer` / `energy transfer partners`).
    Listed for a one-by-one check, never joined."""
    keys: dict[str, int] = collections.Counter()
    for v in values:
        keys[stem_key(styled[v].styled)] += 1
    out = []
    ks = set(keys)
    for k in ks:
        toks = k.split()
        if len(toks) < 2:
            continue
        for i, w in enumerate(toks):
            if w not in DISTINGUISHING:
                continue
            shorter = " ".join(toks[:i] + toks[i + 1:])
            if shorter in ks and len(shorter) > 3:
                out.append({"short": shorter, "long": k, "word": w,
                            "short_values": keys[shorter], "long_values": keys[k]})
    return sorted(out, key=lambda d: (d["short"], d["long"]))


# ----------------------------------------------------------------------------- report

NEAR_VERDICTS = REPO / "data" / "owner_near_verdicts.json"


def near_verdicts() -> dict[str, dict]:
    """Verdicts on near groups and split groups, keyed 'shorter || longer' or by group key."""
    if not NEAR_VERDICTS.exists():
        return {}
    return json.loads(NEAR_VERDICTS.read_text(encoding="utf-8")).get("verdicts", {})


def write_report(res: dict, src: Path, out_md: Path) -> None:
    groups = sorted(res["groups"].values(), key=lambda g: (-g["cells"], g["key"]))
    by_class = collections.Counter(g["class"] for g in groups)
    lines = [f"# Owner and operator consistency, {dt.date.today().isoformat()}", "",
             f"Every Owner<N> and Operator spelling on `{src.name}` plus every pending staged value, grouped by company "
             "(`scripts/owner_consistency.py`; plan `docs/plans/2026-10-20_owner-consistency.md`). A group listed here "
             "is one company written more than one way.", "",
             f"{len(groups)} groups, {sum(g['cells'] for g in groups)} cells. "
             + ", ".join(f"{k} {by_class[k]}" for k in ("ruled", "settled", "held", "split", "pair") if by_class[k]) + ".",
             "", "Classes: `ruled` resolves through a ruling already; `settled` the style rules fix on re-staging; "
             "`held` and `split` need a ruling after a registry check; `pair` was joined through a short name on the "
             "same rows and needs a check first.", ""]
    verdicts = near_verdicts()
    for klass in ("pair", "split", "held", "settled", "ruled"):
        gs = [g for g in groups if g["class"] == klass]
        if not gs:
            continue
        lines += [f"## {klass} ({len(gs)})", "", "| group | cells | proposed | spellings | verdict |",
                  "|---|---|---|---|---|"]
        for g in gs:
            sp = "; ".join(f"`{s['value']}` {s['cells']}" + (" held" if s["held"] else "") for s in g["spellings"])
            v = verdicts.get(g["key"], {})
            vt = f"{v['verdict']}: {v['note']}" if v else ""
            lines.append(f"| {g['key']} | {g['cells']} | {g['proposed'] or ''} | {sp} | {vt} |")
        lines.append("")
    if res["near"]:
        lines += [f"## Near groups, checked one by one and never joined ({len(res['near'])})", "",
                  f"Verdicts live in `{NEAR_VERDICTS.relative_to(REPO)}`: `different` = two companies, kept apart; "
                  "`step3` = a rename or a gone company, fixed with refs in plan step 3; `unchecked` = still owed a check.",
                  "", "| shorter | longer | verdict | note |", "|---|---|---|---|"]
        for n in res["near"]:
            v = verdicts.get(f"{n['short']} || {n['long']}", {})
            lines.append(f"| {n['short']} | {n['long']} | {v.get('verdict', 'unchecked')} | {v.get('note', '')} |")
        lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")
    with out_md.with_suffix(".csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["group", "class", "proposed", "value", "cells", "sheet", "staged", "styled", "basis", "flags",
                    "held", "entity_id", "pids", "sources"])
        for g in groups:
            for s in g["spellings"]:
                w.writerow([g["key"], g["class"], g["proposed"], s["value"], s["cells"], s["sheet"], s["staged"],
                            s["styled"], s["basis"], " ".join(s["flags"]), "yes" if s["held"] else "",
                            s["entity_id"], " ".join(s["pids"]), " ".join(s["srcs"])])


# ----------------------------------------------------------------------------- rulings

def write_rulings(new: dict[str, dict]) -> None:
    """Merge `new` into data/owner_rulings.json["names"], one entry per line as the file is kept."""
    path = ES.RULINGS_JSON
    d = json.loads(path.read_text(encoding="utf-8"))
    names = d.get("names") or {}
    names.update(new)
    d["names"] = names
    parts = ["{"]
    keys = list(d.keys())
    for i, k in enumerate(keys):
        comma = "," if i < len(keys) - 1 else ""
        v = d[k]
        if isinstance(v, dict):
            parts.append(f" {json.dumps(k)}: {{")
            items = list(v.items())
            for j, (kk, vv) in enumerate(items):
                parts.append(f"  {json.dumps(kk, ensure_ascii=False)}: {json.dumps(vv, ensure_ascii=False)}"
                             + ("," if j < len(items) - 1 else ""))
            parts.append(" }" + comma)
        else:
            parts.append(f" {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}{comma}")
    parts.append("}")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def group_rulings(res: dict, group: str, styled: str, ruling: str,
                  aliases=None, only=None, extra=None) -> dict[str, dict]:
    """Rulings for every spelling of one group (or the `only` ones), plus any `extra` spellings.

    With no group, only the `extra` spellings are ruled (a near pair whose sides sit in different
    groups, or a group the report leaves out because it has one spelling)."""
    g = res["groups"].get(group) if group else {"spellings": []}
    if not g:
        sys.exit(f"no group {group!r}; run with --show to list keys")
    today = dt.date.today().isoformat()
    aliases = list(dict.fromkeys(aliases or []))
    entry = {"styled": styled, "aliases": aliases, "ruling": ruling, "date": today}
    new = {}
    for s in g["spellings"]:
        if only and s["value"] not in only:
            continue
        new[s["value"]] = dict(entry)
    for v in extra or []:
        new[v] = dict(entry)
    new.setdefault(styled, dict(entry))
    # a spelling the ownership team's list already gives as the target keeps that basis (and its
    # entity id); a ruling would only shadow it
    for v in list(new):
        r = ES.style(v)
        if r.basis in ("exact", "alias") and r.styled == styled and not r.flags:
            del new[v]
    return new


def cmd_rule(a, res: dict) -> None:
    if a.from_json:
        new = {}
        for r in json.loads(a.from_json.read_text(encoding="utf-8")):
            new.update(group_rulings(res, r.get("group"), r["styled"], r["ruling"],
                                     r.get("alias"), r.get("only"), r.get("extra")))
    else:
        if not (a.group and a.styled and a.ruling):
            sys.exit("rule needs --group, --styled and --ruling, or --from-json")
        new = group_rulings(res, a.group, a.styled, a.ruling, a.alias, a.only)
    for k, v in new.items():
        print(f"{k!r} -> {v['styled']!r}")
    if a.apply:
        write_rulings(new)
        print(f"wrote {len(new)} rulings to {ES.RULINGS_JSON.relative_to(REPO)}")
    else:
        print("(dry run; --apply writes them)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--owners-csv", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=None, help="report path (default notes/owner-consistency-<date>.md)")
    ap.add_argument("--show", default=None, help="print the groups whose key contains this text, and write nothing")
    ap.add_argument("--json", type=Path, default=None, help="also dump the groups as JSON here")
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("rule", help="write a ruling for every spelling in one group")
    r.add_argument("--group")
    r.add_argument("--styled")
    r.add_argument("--ruling", help="the basis, in plain words (the registry checked, what it says)")
    r.add_argument("--from-json", type=Path, default=None,
                   help="a list of {group, styled, ruling, alias?, only?, extra?} to rule in one go")
    r.add_argument("--alias", action="append", help="an acronym or short name kept as an alias (repeatable)")
    r.add_argument("--only", action="append", help="rule only these spellings of the group (repeatable)")
    r.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    src = a.owners_csv or latest_owners_csv()
    res = build(sheet_cells(src) + staged_cells())
    if a.cmd == "rule":
        return cmd_rule(a, res)
    if a.json:
        a.json.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    if a.show is not None:
        for g in sorted(res["groups"].values(), key=lambda g: -g["cells"]):
            if a.show.lower() in g["key"]:
                print(f"[{g['class']}] {g['key']} ({g['cells']} cells) -> {g['proposed'] or '?'}")
                for s in g["spellings"]:
                    print(f"    {s['value']!r} {s['cells']} (sheet {s['sheet']}, staged {s['staged']}) "
                          f"-> {s['styled']!r} {s['basis']} {' '.join(s['flags'])}{' HELD' if s['held'] else ''}")
        return
    out = a.out or REPO / "notes" / f"owner-consistency-{dt.date.today().isoformat()}.md"
    write_report(res, src, out)
    groups = res["groups"].values()
    by_class = collections.Counter(g["class"] for g in groups)
    verdicts = near_verdicts()
    unchecked = [n for n in res["near"] if f"{n['short']} || {n['long']}" not in verdicts]
    print(f"{len(res['groups'])} groups, {sum(g['cells'] for g in groups)} cells: "
          + ", ".join(f"{k} {v}" for k, v in sorted(by_class.items()))
          + f"; near {len(res['near'])} ({len(unchecked)} unchecked)")
    print(f"wrote {out} + .csv")


if __name__ == "__main__":
    main()
