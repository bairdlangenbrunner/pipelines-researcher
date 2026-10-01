#!/usr/bin/env python3
"""Rebuild the owner-name gazetteer the styler matches against (`scripts/entity_style.py`).

The ownership team's canonical entity names live in three places we can read, none of
them a pipeline-specific list:

  1. the `ownership_v5_11_0` export (sheet 1wGI0E4D1-VKbwwRFqnizr-ZDfaI4yMQ3794xjRNu1yQ) —
     `parent_name`/`parent_entity_id`, `immediate_source_owner`/`…_entity_id`,
     `source_operator`/`source_operator_id` for every asset the team has resolved
     (no pipelines in it, but ~15k styled entity names with their E1000… ids);
  2. the team-maintained `Owner/parent formatted` tab of our own backend sheet —
     `ParentString` + `OwnerEntityIDString` per ProjectID (what the tracker `Parent`
     column is a formula over), plus the raw `OwnerString` it was built from;
  3. the tracker tabs' `Parent` + `ParentEntityIDs` (gas) / `OwnerEntityIDs` (oil).

And the legal-forms list (sheet 1XieqEs3A9tKOFo7eRQIJFAIrMllkA3NtKDxWKNBcbpI, tab
`list of types`) — the `sp` column is the team's canonical spelling of each form.

Outputs (tracked, so every session styles against the same list):
  data/owner_gazetteer.csv   one row per (name, entity_id): name, name_norm, entity_id,
                             kinds, n_rows
  data/legal_forms.csv       the team's list verbatim (sp, Meaning, Notes, Sources, Countries)
  data/owner_aliases.json    SEEDED only when absent (or with --seed-aliases, into a sibling
                             *.seed.json for review): raw owner spelling -> styled parent
                             pairs from the `Owner/parent formatted` tab that look like the
                             SAME entity (fuzzy >= 80 or acronym-of-initials). Hand-confirm
                             before the styler adopts them — see docs/reference/owner_style.md.

Reads the sheets read-only through ../gem-db-ops/gem_sheets.py (`gws-gem`), caching the raw
pulls in the gitignored work/own/ dir; --no-refresh reuses the cache.

    python scripts/build_owner_gazetteer.py            # refresh pulls + rebuild
    python scripts/build_owner_gazetteer.py --no-refresh
    python scripts/build_owner_gazetteer.py --seed-aliases   # also write owner_aliases.seed.json
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import normalize_name, parse_owners  # noqa: E402
from paths import db_ops_repo, repo_root, work_dir  # noqa: E402

OWNERSHIP_EXPORT_KEY = "1wGI0E4D1-VKbwwRFqnizr-ZDfaI4yMQ3794xjRNu1yQ"
OWNERSHIP_EXPORT_TAB = "ownership_v5_11_0"
LEGAL_FORMS_KEY = "1XieqEs3A9tKOFo7eRQIJFAIrMllkA3NtKDxWKNBcbpI"
LEGAL_FORMS_TAB = "list of types"
OWNER_PARENT_TAB = "Owner/parent formatted"

DATA = repo_root() / "data"
GAZETTEER_CSV = DATA / "owner_gazetteer.csv"
LEGAL_FORMS_CSV = DATA / "legal_forms.csv"
ALIASES_JSON = DATA / "owner_aliases.json"

SENTINELS = {"unknown", "small shareholder(s)", "natural person(s)"}
_PCT = re.compile(r"\s*\[[^\]]*\]\s*$")


def _sheets():
    sys.path.insert(0, str(db_ops_repo()))
    import gem_sheets as G  # noqa: E402
    return G


def _pull(title: str, key: str, cache: Path, refresh: bool) -> list[list[str]]:
    if cache.exists() and not refresh:
        with cache.open(newline="", encoding="utf-8") as fh:
            return list(csv.reader(fh))
    G = _sheets()
    vals = G.read_tab_values(title, key)
    width = max(len(r) for r in vals)
    vals = [r + [""] * (width - len(r)) for r in vals]
    with cache.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(vals)
    return vals


def _latest(pattern: str) -> Path | None:
    hits = sorted(DATA.glob(pattern))
    return hits[-1] if hits else None


def _split_ids(s: str) -> list[str]:
    return [t.strip() for t in re.split(r"[;,]", s or "") if t.strip()]


def _strip_pct(name: str) -> str:
    return _PCT.sub("", name or "").strip()


def build(refresh: bool, seed_aliases: bool) -> dict:
    cache = work_dir() / "own"
    cache.mkdir(exist_ok=True)

    # (name, id) -> {kinds: Counter, n: int}
    gaz: dict[tuple[str, str], dict] = collections.defaultdict(
        lambda: {"kinds": collections.Counter(), "n": 0})

    def add(name: str, eid: str, kind: str, n: int = 1) -> None:
        name = (name or "").strip()
        if not name or name in ("--", "—"):
            return
        eid = (eid or "").strip()
        if eid and not re.fullmatch(r"E\d{9,}", eid):
            eid = ""
        g = gaz[(name, eid)]
        g["kinds"][kind] += 1
        g["n"] += n

    # 1. ownership export
    exp = _pull(OWNERSHIP_EXPORT_TAB, OWNERSHIP_EXPORT_KEY, cache / "ownership_export.csv", refresh)
    hdr = exp[0]
    col = {h: i for i, h in enumerate(hdr)}
    for r in exp[1:]:
        for nm, idc, kind in (("parent_name", "parent_entity_id", "parent"),
                              ("immediate_source_owner", "immediate_source_owner_entity_id", "immediate"),
                              ("source_operator", "source_operator_id", "operator")):
            if nm in col and idc in col:
                add(r[col[nm]], r[col[idc]], kind)

    # 2. Owner/parent formatted tab (our backend sheet)
    G = _sheets()
    opf = _pull(OWNER_PARENT_TAB, G.PIPELINES_SHEET_KEY, cache / "owner_parent_formatted.csv", refresh)
    pairs = collections.Counter()           # (raw owner, styled parent) -> rows
    for r in opf[1:]:
        if len(r) < 4:
            continue
        owners = [_strip_pct(x) for x in (r[1] or "").split(";") if x.strip()]
        parents = [_strip_pct(x) for x in (r[2] or "").split(";") if x.strip()]
        ids = _split_ids(r[3])
        for i, p in enumerate(parents):
            add(p, ids[i] if i < len(ids) else "", "tracker_parent")
        if len(owners) == len(parents):
            for o, p in zip(owners, parents):
                if o and p and o.lower() not in SENTINELS and p.lower() not in SENTINELS:
                    pairs[(o, p)] += 1

    # 3. tracker Parent + ids (positional zip when the counts agree)
    for pat, idcol in (("GGIT_gas_snapshot_*.csv", "ParentEntityIDs"),
                       ("GOIT_oil_ngl_snapshot_*.csv", "OwnerEntityIDs")):
        f = _latest(pat)
        if not f:
            continue
        with f.open(newline="", encoding="utf-8") as fh:
            rd = csv.reader(fh)
            rows = list(rd)
        h = rows[2]
        hc = {x: i for i, x in enumerate(h)}
        if "Parent" not in hc or idcol not in hc:
            continue
        for r in rows[3:]:
            if len(r) <= max(hc["Parent"], hc[idcol]):
                continue
            parents = parse_owners(r[hc["Parent"]])
            ids = _split_ids(r[hc[idcol]])
            for i, p in enumerate(parents):
                add(p, ids[i] if len(ids) == len(parents) else "", "tracker_parent")

    # 4. legal forms
    lf = _pull(LEGAL_FORMS_TAB, LEGAL_FORMS_KEY, cache / "legal_forms.csv", refresh)
    with LEGAL_FORMS_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        for r in lf:
            if any(c.strip() for c in r):
                w.writerow([c.strip() for c in r[:5]])

    # write gazetteer
    out_rows = []
    for (name, eid), g in gaz.items():
        if name.lower() in SENTINELS:
            continue
        out_rows.append({
            "name": name, "name_norm": normalize_name(name), "entity_id": eid,
            "kinds": "|".join(sorted(g["kinds"])), "n_rows": g["n"],
        })
    out_rows.sort(key=lambda d: (d["name_norm"], d["entity_id"]))
    with GAZETTEER_CSV.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["name", "name_norm", "entity_id", "kinds", "n_rows"])
        w.writeheader()
        w.writerows(out_rows)

    # alias seed
    seed = seed_from_pairs(pairs, out_rows)
    target = None
    if seed_aliases:
        target = ALIASES_JSON.with_suffix(".seed.json")
    elif not ALIASES_JSON.exists():
        target = ALIASES_JSON
    if target:
        target.write_text(json.dumps(seed, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    return {"gazetteer_rows": len(out_rows),
            "with_entity_id": sum(1 for r in out_rows if r["entity_id"]),
            "legal_forms": max(len(lf) - 1, 0),
            "owner_parent_pairs": len(pairs),
            "alias_seed_entries": len(seed["entities"]),
            "alias_seed_written_to": str(target) if target else None}


def _initials(name: str) -> str:
    return "".join(w[0] for w in re.findall(r"[A-Za-z0-9]+", name)).lower()


def seed_from_pairs(pairs: collections.Counter, gaz_rows: list[dict]) -> dict:
    """Owner-spelling -> parent-spelling pairs that look like ONE entity, as alias seeds.

    Kept when the two normalize to the same thing, fuzz >= 80, or the owner side is a
    short acronym of the parent's initials. Everything a seed proposes is `status: "seed"`:
    the styler adopts only `confirmed` entries (a subsidiary that happens to resemble its
    parent must never be flattened up — the SPV ruling, gem_schema.md)."""
    from rapidfuzz import fuzz
    by_name = collections.defaultdict(set)
    for r in gaz_rows:
        if r["entity_id"]:
            by_name[r["name"]].add(r["entity_id"])
    ent: dict[str, dict] = {}
    for (o, p), n in sorted(pairs.items(), key=lambda kv: -kv[1]):
        if o == p:
            continue
        no, np_ = normalize_name(o), normalize_name(p)
        same_norm = no == np_
        score = fuzz.token_set_ratio(no, np_)
        acro = re.fullmatch(r"[A-Z][A-Z0-9&.\-]{1,11}", o) and (
            o.replace(".", "").replace("&", "").lower() in _initials(p)
            or _initials(p).startswith(o.replace(".", "").lower()[:3]))
        paren = re.search(r"\(([A-Z0-9&.\-]{2,12})\)\s*$", o)
        if not (same_norm or score >= 80 or acro or (paren and normalize_name(o[:paren.start()]) == np_)):
            continue
        e = ent.setdefault(p, {"canonical": p, "entity_ids": sorted(by_name.get(p, ())),
                               "aliases": [], "status": "seed", "evidence": []})
        if o not in e["aliases"]:
            e["aliases"].append(o)
        if paren and paren.group(1) not in e["aliases"]:
            e["aliases"].append(paren.group(1))
        e["evidence"].append(f"Owner/parent formatted: {o!r} -> {p!r} on {n} row(s), fuzz {score:.0f}")
    return {
        "_doc": ("canonical owner name (ownership-team style) -> alternate spellings and "
                 "abbreviations. The styler adopts an alias only when status == 'confirmed'; "
                 "'seed' entries are proposals from build_owner_gazetteer.py and surface as "
                 "candidates to flag, never to adopt. Rules: docs/reference/owner_style.md."),
        "entities": sorted(ent.values(), key=lambda e: e["canonical"].lower()),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-refresh", action="store_true", help="reuse work/own/ pulls")
    ap.add_argument("--seed-aliases", action="store_true",
                    help="write data/owner_aliases.seed.json for review (never overwrites the live file)")
    a = ap.parse_args()
    out = build(refresh=not a.no_refresh, seed_aliases=a.seed_aliases)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
