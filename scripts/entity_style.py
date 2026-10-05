#!/usr/bin/env python3
"""Style an immediate-owner name the way GEM's ownership team writes entity names.

The rules are the team's (docs/reference/owner_style.md — distilled from their Immediate
Ownership Guide + Ownership research guide + legal-forms list), and the vocabulary is theirs
too: `data/owner_gazetteer.csv` (every styled entity name + E1000… id we can read, built by
`build_owner_gazetteer.py`), `data/legal_forms.csv` (their canonical form spellings) and
`data/owner_aliases.json` (canonical name -> confirmed alternate spellings/abbreviations).

    from entity_style import style
    r = style("Sui Northern Gas Pipelines Ltd (SNGPL)")
    r.styled      -> 'Sui Northern Gas Pipelines Ltd'
    r.legal_form  -> 'Ltd'
    r.basis       -> 'exact' | 'alias' | 'rules' | 'sentinel' | 'passthrough'
    r.confidence  -> 'high' (gazetteer exact / confirmed alias) | 'medium' (rules, form found)
                     | 'low' (rules, no form / state-body rewrite / unresolved)
    r.aliases     -> ['SNGPL']          # spellings to keep in researcher_notes + the alias file
    r.flags       -> ['acronym_dropped']
    r.candidates  -> fuzzy gazetteer near-hits, NEVER adopted — flagged for the orchestrator

Adoption policy (Baird 2026-10-01): adopt the canonical on an EXACT normalized match or a
CONFIRMED alias; anything fuzzy is a candidate to flag. A subsidiary or SPV that resembles its
parent is never flattened up (gem_schema.md, the SPV ruling).

CLI:  python scripts/entity_style.py "Name One" "Name Two" [--json]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import fold_diacritics, normalize_name  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
GAZETTEER_CSV = REPO / "data" / "owner_gazetteer.csv"
LEGAL_FORMS_CSV = REPO / "data" / "legal_forms.csv"
ALIASES_JSON = REPO / "data" / "owner_aliases.json"
RULINGS_JSON = REPO / "data" / "owner_rulings.json"     # Baird's per-name / per-cell rulings (basis `ruling`)
COUNTRIES_CSV = REPO / "docs" / "reference" / "gem_naming_conventions" / "countries.csv"
SUBDIVISIONS_CSV = REPO / "docs" / "reference" / "gem_naming_conventions" / "country_subdivisions.csv"

FUZZY_CUTOFF = 90

SENTINELS = {
    "unknown": "unknown",
    "unknown owner": "unknown",
    "n/a": "unknown",
    "natural person": "natural person(s)",
    "natural persons": "natural person(s)",
    "natural person(s)": "natural person(s)",
    "small shareholder": "small shareholder(s)",
    "small shareholders": "small shareholder(s)",
    "small shareholder(s)": "small shareholder(s)",
}

# Long-form words/phrases -> the team's short form. Matched at the END of the name (after a
# trailing acronym has been dropped), longest first. Values are the canonical `sp` spelling.
LONG_FORMS: list[tuple[str, str]] = [
    ("public joint stock company", "PJSC"),
    ("closed joint stock company", "CJSC"),
    ("open joint stock company", "OJSC"),
    ("joint stock company", "JSC"),
    ("joint-stock company", "JSC"),
    ("limited liability company", "LLC"),
    ("limited liability partnership", "LLP"),
    ("limited partnership", "LP"),
    ("public limited company", "PLC"),
    ("public company limited", "PCL"),
    ("private limited company", "Pvt Ltd"),
    ("private limited", "Pvt Ltd"),
    ("proprietary limited", "Pty Ltd"),
    ("sendirian berhad", "Sdn Bhd"),
    ("berhad", "Bhd"),
    ("aktiengesellschaft", "AG"),
    ("société anonyme", "SA"),
    ("societe anonyme", "SA"),
    ("sociedad anónima", "SA"),
    ("sociedad anonima", "SA"),
    ("società per azioni", "SpA"),
    ("societa per azioni", "SpA"),
    ("naamloze vennootschap", "NV"),
    ("besloten vennootschap", "BV"),
    ("gesellschaft mit beschränkter haftung", "GmbH"),
    ("gesellschaft mit beschrankter haftung", "GmbH"),
    ("company limited", "Co Ltd"),
    ("company ltd", "Co Ltd"),
    ("co limited", "Co Ltd"),
    ("corporation limited", "Corp Ltd"),
    ("corporation ltd", "Corp Ltd"),
    ("corp limited", "Corp Ltd"),
    ("company incorporated", "Co Inc"),
    ("company inc", "Co Inc"),
    # "Company" STAYS in the name when the form is LLC / LP (guide): the form is LLC, not Co LLC
    ("company llc", "Company LLC"),
    ("company lp", "Company LP"),
    ("incorporated", "Inc"),
    ("corporation", "Corp"),
    ("company", "Co"),
    ("limited", "Ltd"),
]

# Russian/CIS registration forms -> what the team records. ZAO/OAO are kept only if the entity
# is still registered under them (the guide) — the flag asks the researcher to check.
CIS_FORMS = {"ooo": "LLC", "pao": "PJSC", "ao": "JSC", "too": "LLP",
             "zao": "CJSC", "oao": "OJSC", "njsc": "JSC", "sp z o o": "SP zoo"}
CIS_CHECK = {"zao", "oao", "njsc"}

# Forms that commonly LEAD the name in local usage; the team writes them trailing.
LEADING_FORMS = {"ooo", "pao", "ao", "too", "zao", "oao", "pjsc", "jsc", "llc", "cjsc", "ojsc",
                 "llp", "njsc", "ab", "nv", "as", "a s", "oy", "oyj", "sia", "uab", "sa", "sas"}
# …but not these — a legitimate leading element of the legal name (Indonesian PT, Tbk etc.)
LEADING_KEEP = {"pt"}

# Parentheticals that stay even when they are all-caps: geography and legal-name elements
PAREN_KEEP = {"UK", "US", "USA", "UAE", "PRC", "EU", "RF", "LP", "NZ", "HK", "KSA", "DRC",
              "NSW", "WA", "SA", "QLD", "VIC", "NT", "BC", "AB", "ON", "QC"}
US_STATE_CODES = {"AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
                  "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
                  "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
                  "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC"}

# Adjective -> country, used ONLY inside the "<Adj> Ministry of …" pattern
COUNTRY_ADJ = {"iraqi": "Iraq", "iranian": "Iran", "egyptian": "Egypt", "saudi": "Saudi Arabia",
               "kuwaiti": "Kuwait", "qatari": "Qatar", "omani": "Oman", "syrian": "Syria",
               "libyan": "Libya", "algerian": "Algeria", "nigerian": "Nigeria", "pakistani": "Pakistan",
               "indian": "India", "russian": "Russia", "ukrainian": "Ukraine", "turkish": "Turkey",
               "israeli": "Israel", "jordanian": "Jordan", "lebanese": "Lebanon", "yemeni": "Yemen",
               "bahraini": "Bahrain", "emirati": "United Arab Emirates", "kazakh": "Kazakhstan",
               "uzbek": "Uzbekistan", "turkmen": "Turkmenistan", "azerbaijani": "Azerbaijan",
               "georgian": "Georgia", "afghan": "Afghanistan", "bangladeshi": "Bangladesh",
               "chinese": "China", "mexican": "Mexico", "brazilian": "Brazil", "argentine": "Argentina",
               "colombian": "Colombia", "venezuelan": "Venezuela", "peruvian": "Peru",
               "bolivian": "Bolivia", "chilean": "Chile", "mozambican": "Mozambique",
               "tanzanian": "Tanzania", "kenyan": "Kenya", "ugandan": "Uganda", "ghanaian": "Ghana",
               "angolan": "Angola", "sudanese": "Sudan", "south sudanese": "South Sudan",
               "cameroonian": "Cameroon", "chadian": "Chad", "nigerien": "Niger", "malaysian": "Malaysia",
               "indonesian": "Indonesia", "thai": "Thailand", "vietnamese": "Vietnam",
               "philippine": "Philippines", "filipino": "Philippines", "burmese": "Myanmar",
               "myanmar": "Myanmar", "japanese": "Japan", "korean": "South Korea"}

STATE_BODY_HEAD = r"(?:Ministry|Department|Directorate|Authority|Agency|Commission|Secretariat|Office)"
_SOVEREIGN = (r"(?:Republic|Kingdom|State|Sultanate|Emirate|Federation|Union|Commonwealth|"
              r"Islamic Republic|People's Republic|Federal Republic|Federal Democratic Republic|"
              r"Democratic Republic|Socialist Republic|Arab Republic|Hashemite Kingdom|Grand Duchy|"
              r"Principality|Plurinational State|Bolivarian Republic|United Republic|Federative Republic|"
              r"Oriental Republic|Co-operative Republic|Independent State|Kingdom of the)")
_PCT_TAIL = re.compile(r"\s*[\[(]\s*(?:\d+(?:[.,]\d+)?\s*%?|unknown\s*%?|[\d.]*\s*%)\s*[\])]\s*$", re.I)
_FORMER_TAIL = re.compile(r"\s*\[\s*former\s*\]\s*$", re.I)
# a trailing parenthetical: an acronym (YPFB), or a one-word trade name (Acme) — multi-word
# parentheticals (`(Private)`, `(Persero)`, `(Hong Kong)`) are judged by the keep sets below
# a LEADING acronym with the legal name in parentheses: `TGS (Transportadora de Gas del Sur SA)`.
# The team's form is the inner legal name; the acronym goes to the alias file (flag acronym_lead).
# Before 2026-10-05 the trailing-form rewrite ate the closing parenthesis of these.
_ACRONYM_LEAD = re.compile(r"^([A-Z][A-Z0-9&\-]{1,7})\s*\(\s*([^()]*\s[^()]*)\)\s*$")
_ACRONYM_TAIL = re.compile(r"\s*\(\s*([A-Za-z0-9][A-Za-z0-9&.\-]{1,13}(?: [A-Za-z]{2,12})?)\s*\)\s*$")
# parenthetical words that are legal-name elements, never trade names
PAREN_KEEP_WORDS = {"persero", "private", "public", "holding", "holdings", "group", "proprietary",
                    "pty", "pvt", "tbk", "national", "international", "overseas", "offshore",
                    "onshore", "international", "trading", "operations", "services", "state"}
_QUOTES = re.compile(r"[\"“”«»„‟]")
_NON_LATIN = re.compile(r"[Ѐ-ӿ؀-ۿ一-鿿぀-ヿ가-힯֐-׿]")


@dataclass
class StyleResult:
    raw: str
    styled: str
    legal_form: str = ""
    confidence: str = "low"
    basis: str = "rules"
    entity_id: str = ""
    aliases: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)
    candidates: list[dict] = field(default_factory=list)
    note: str = ""

    @property
    def changed(self) -> bool:
        return self.styled != self.raw

    def to_dict(self) -> dict:
        d = asdict(self)
        d["changed"] = self.changed
        return d


# ----------------------------------------------------------------------------- reference data

def _form_key(s: str) -> str:
    """`Co., Ltd.` / `S.p.A.` / `Pty. Ltd` -> 'co ltd' / 'spa' / 'pty ltd'. Dots are joined
    (S.A. is one token SA), everything else non-alphanumeric is a separator; '&' is kept."""
    t = fold_diacritics(str(s)).lower().replace(".", "")
    t = re.sub(r"[^a-z0-9&]+", " ", t)
    return " ".join(t.split())


@lru_cache(maxsize=None)
def legal_forms() -> dict[str, str]:
    """form key -> canonical spelling (the team's `sp` column), plus the long forms above."""
    out: dict[str, str] = {}
    if LEGAL_FORMS_CSV.exists():
        with LEGAL_FORMS_CSV.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                sp = (r.get("sp") or "").strip()
                if sp:
                    out.setdefault(_form_key(sp), sp)
    for long, short in LONG_FORMS:
        out.setdefault(_form_key(long), short)
        out.setdefault(_form_key(short), short)
    for k, v in CIS_FORMS.items():
        out.setdefault(k, v)
    # key variants the list spells with punctuation
    out.setdefault("a s", out.get("a s", "A/S"))
    out.setdefault("sp zoo", "SP zoo")
    return out


@lru_cache(maxsize=None)
def rulings() -> dict:
    """data/owner_rulings.json: {"names": {raw: {styled|clear, aliases, ruling, date}},
    "cells": {"<PID>/<col>": {...}}} — Baird's rulings on names the rules cannot settle
    (docs/plans/2026-10-05_owner-style-normalization.md, Phase 3). Keys are matched on the
    collapsed spelling (normalize_name), so whitespace variants of a ruled name still hit."""
    out = {"names": {}, "cells": {}}
    if not RULINGS_JSON.exists():
        return out
    d = json.loads(RULINGS_JSON.read_text(encoding="utf-8"))
    out["names"] = {normalize_name(k): dict(v, raw=k) for k, v in (d.get("names") or {}).items()}
    out["cells"] = dict(d.get("cells") or {})
    return out


def cell_ruling(pid: str, col: str) -> dict | None:
    """A ruling that names one cell (`P1321/Owner2` -> {"clear": true, ...}), else None."""
    return rulings()["cells"].get(f"{pid}/{col}")


@lru_cache(maxsize=None)
def gazetteer() -> dict[str, list[dict]]:
    """name_norm -> rows [{name, entity_id, kinds, n_rows}], best (most rows) first."""
    out: dict[str, list[dict]] = {}
    if not GAZETTEER_CSV.exists():
        return out
    with GAZETTEER_CSV.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            r["n_rows"] = int(r.get("n_rows") or 0)
            out.setdefault(r["name_norm"], []).append(r)
    for rows in out.values():
        rows.sort(key=lambda d: (-d["n_rows"], d["name"]))
    return out


@lru_cache(maxsize=None)
def _gaz_by_stem() -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    """Two more views of the gazetteer: `form key` (stem_norm|canonical form — equal for
    `Kuwait Oil Company Limited` and `Kuwait Oil Company Ltd`) and `stem` (stem_norm only —
    equal for `Enbridge` and `Enbridge Inc`). Junk rows (a bare legal form, an unbalanced
    parenthesis fragment from a split string) are left out."""
    by_form: dict[str, list[dict]] = {}
    by_stem: dict[str, list[dict]] = {}
    forms = legal_forms()
    for norm, rows in gazetteer().items():
        row = rows[0]
        name = row["name"]
        if norm in forms or _form_key(name) in forms or name.count("(") != name.count(")") \
                or len(norm) < 2:
            continue
        stem, form, _ = split_legal_form(name)
        sn = normalize_name(stem)
        if not sn:
            continue
        by_form.setdefault(f"{sn}|{form}", []).append(row)
        by_stem.setdefault(sn, []).append(row)
    return by_form, by_stem


@lru_cache(maxsize=None)
def aliases() -> tuple[dict[str, dict], dict[str, dict]]:
    """(confirmed alias_norm -> entity, candidate alias_norm -> entity)."""
    conf: dict[str, dict] = {}
    cand: dict[str, dict] = {}
    if not ALIASES_JSON.exists():
        return conf, cand
    data = json.loads(ALIASES_JSON.read_text(encoding="utf-8"))
    for e in data.get("entities") or []:
        for a in e.get("aliases") or []:
            conf.setdefault(normalize_name(a), e)
        for a in e.get("candidates") or []:
            cand.setdefault(normalize_name(a), e)
    return conf, cand


@lru_cache(maxsize=None)
def countries() -> set[str]:
    names: set[str] = set()
    if COUNTRIES_CSV.exists():
        with COUNTRIES_CSV.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                for k in ("GEM Standard Country Name", "ISO 3166 Country Name"):
                    if r.get(k):
                        names.add(r[k].strip())
    names |= {"Kurdistan Region", "Kosovo", "Russia", "Iran", "Syria", "Venezuela", "Bolivia",
              "Tanzania", "Vietnam", "Laos", "South Korea", "North Korea", "Taiwan", "Palestine",
              "Czech Republic", "Türkiye", "Turkey", "Moldova", "Brunei", "Micronesia"}
    return names


@lru_cache(maxsize=None)
def subdivisions() -> set[str]:
    names: set[str] = set()
    if SUBDIVISIONS_CSV.exists():
        with SUBDIVISIONS_CSV.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                for k in ("Subnational name", "Subnational name variations"):
                    for v in re.split(r"[;,]", r.get(k) or ""):
                        if v.strip():
                            names.add(fold_diacritics(v.strip()))
    return names


@lru_cache(maxsize=None)
def _country_norms() -> dict[str, str]:
    return {normalize_name(c): c for c in countries()}


def _as_country(s: str) -> str | None:
    return _country_norms().get(normalize_name(s))


# ----------------------------------------------------------------------------- helpers

def _collapse(s: str) -> str:
    return " ".join(str(s or "").split())


def _lookup_exact(name: str) -> dict | None:
    rows = gazetteer().get(normalize_name(name))
    return rows[0] if rows else None


def _split_form_tokens(tokens: list[str]) -> list[str]:
    """`Corp.,ltd.` -> ['Corp.', 'ltd.']; drop a comma that precedes a form token."""
    out: list[str] = []
    for t in tokens:
        parts = [p for p in re.split(r"(?<=\.),(?=\S)", t) if p]
        out.extend(parts)
    forms = legal_forms()
    for i in range(len(out) - 1):
        if out[i].endswith(",") and _form_key(out[i + 1]) in forms:
            out[i] = out[i].rstrip(",")
    return out


def _canonical_form(key: str) -> str:
    return legal_forms().get(key, "")


def split_legal_form(name: str) -> tuple[str, str, str]:
    """-> (stem, canonical form, form key) for a trailing legal form (1–4 tokens), else
    (name, '', ''). Pure lookup; no rewriting of the stem."""
    toks = _split_form_tokens(_collapse(name).split(" "))
    forms = legal_forms()
    for n in (4, 3, 2, 1):
        if len(toks) <= n:          # the whole name can't be a form
            continue
        key = _form_key(" ".join(toks[-n:]))
        if key in forms:
            return " ".join(toks[:-n]), forms[key], key
    return _collapse(name), "", ""


def stem_norm(name: str) -> str:
    """Normalized name with its trailing legal form removed — what two spellings of ONE
    entity share (`Enbridge` / `Enbridge Inc`, `Sonatrach` / `Sonatrach SpA`)."""
    stem, _, _ = split_legal_form(name)
    return normalize_name(stem)


def _initials(name: str) -> str:
    return "".join(w[0] for w in re.findall(r"[A-Za-z0-9]+", name)).lower()


def is_abbreviation_of(acro: str, name: str) -> bool:
    """`SNGPL` of `Sui Northern Gas Pipelines Ltd`; `ADNOC` of `Abu Dhabi National Oil Co`;
    `PDVSA` of `Petróleos de Venezuela SA`. Subsequence of word initials, or a prefix of the
    first word (TEPCO ~ Tokyo Electric Power Co is initials; Bapco ~ Bahrain Petroleum Co is a
    syllabic blend, caught by the first-letters-in-order test)."""
    a = re.sub(r"[^a-z0-9]", "", acro.lower())
    if len(a) < 2:
        return False
    init = _initials(name)
    it = iter(init)
    if all(ch in it for ch in a):
        return True
    letters = re.sub(r"[^a-z0-9]", "", fold_diacritics(name).lower())
    it2 = iter(letters)
    return a[0] == letters[:1] and all(ch in it2 for ch in a)


# ----------------------------------------------------------------------------- state bodies

def _state_body(name: str) -> tuple[str, str] | None:
    """-> (styled, note) when the name is a government body the guide styles with the
    country in parentheses, or a sovereign the guide writes `Government of X`."""
    s = _collapse(name)
    # already in style: `Ministry of Oil (Iraq)`, `Government of X`, `City of X (State)`
    m = re.match(rf"^Government of (?:the )?(?:{_SOVEREIGN} of (?:the )?)?(.+)$", s)
    if m:
        c = _as_country(m.group(1))
        if c and s != f"Government of {c}":
            return f"Government of {c}", "`Government of <GEM standard country name>`"
        return s, "state body already in team style"
    if re.match(rf"^{STATE_BODY_HEAD}\b.*\([^)]+\)$", s) or re.match(r"^City of .+", s):
        return s, "state body already in team style"
    m = re.match(rf"^(.+?)\s+({STATE_BODY_HEAD}\b.*)$", s)
    if m:
        c = _as_country(m.group(1)) or COUNTRY_ADJ.get(m.group(1).lower())
        if c:
            body = re.sub(r"\bMinistery\b", "Ministry", m.group(2))
            return f"{body} ({c})", f"'<country> <body>' -> '<body> (<country>)': {m.group(1)!r} is a country"
    m = re.match(rf"^({STATE_BODY_HEAD}\b.+)\s+of\s+(?:the\s+)?(.+)$", s)   # greedy: LAST " of "
    if m:
        body = re.sub(rf"\s+of\s+(?:the\s+)?{_SOVEREIGN}$", "", m.group(1))
        c = _as_country(m.group(2))
        if c and not re.search(r"\(", body):
            # `Ministry of Oil of Iraq` / `Ministry of Energy of the Republic of Kazakhstan` ->
            # `Ministry of Oil (Iraq)` / `Ministry of Energy (Kazakhstan)`
            return f"{body} ({c})", "'<body> of <country>' -> '<body> (<country>)'"
    m = re.match(rf"^{_SOVEREIGN} of (?:the )?(.+)$", s)
    if m:
        c = _as_country(m.group(1))
        if c:
            return f"Government of {c}", "a sovereign owner is `Government of <country>`"
    m = re.match(r"^(.+?) (?:Government|State)$", s)
    if m:
        c = _as_country(m.group(1))
        if c:
            return f"Government of {c}", "a sovereign owner is `Government of <country>`"
    c = _as_country(s)
    if c:
        return f"Government of {c}", "a bare country name as owner is `Government of <country>`"
    return None


# ----------------------------------------------------------------------------- the styler

def _adopt(res: StyleResult, hit: dict, basis: str, note: str) -> StyleResult:
    styled = hit["name"] if basis == "exact" else hit["canonical"]
    if styled != res.styled and res.styled not in res.aliases and res.styled != res.raw:
        res.aliases.append(res.styled)
    if styled != res.raw and _collapse(res.raw) not in res.aliases and basis == "alias":
        res.aliases.append(_collapse(_PCT_TAIL.sub("", res.raw)))
    res.styled = styled
    res.basis = basis
    res.confidence = "high"
    if basis == "exact":
        res.entity_id = hit.get("entity_id", "") or ""
    else:
        ids = hit.get("entity_ids") or []
        res.entity_id = ids[0] if len(ids) == 1 else ""
    _, res.legal_form, _ = split_legal_form(styled)
    res.note = note
    res.candidates = []
    return res


def _lookup_form(name: str) -> dict | None:
    """Exact modulo legal-form spelling: `Kuwait Oil Company Limited` ~ `Kuwait Oil Company Ltd`."""
    stem, form, _ = split_legal_form(name)
    rows = _gaz_by_stem()[0].get(f"{normalize_name(stem)}|{form}")
    return rows[0] if rows else None


def _lookup_stem(name: str) -> list[dict]:
    """Same stem, any legal form: `Enbridge` ~ `Enbridge Inc`; `OKEA` ~ `OKEA AS` + `OKEA ASA`."""
    stem, _, _ = split_legal_form(name)
    return _gaz_by_stem()[1].get(normalize_name(stem), [])


def _fuzzy(name: str, limit: int = 5) -> list[dict]:
    """Near-matches on the STEM (legal form removed), filtered so a bare `Gas` or `Co Ltd`
    fragment never counts: token_set ≥ FUZZY_CUTOFF and token_sort ≥ 75, and the candidate
    keeps at least half the query's tokens."""
    try:
        from rapidfuzz import fuzz, process
    except ImportError:          # pragma: no cover
        return []
    stem, _, _ = split_legal_form(name)
    q = normalize_name(stem)
    if not q:
        return []
    by_stem = _gaz_by_stem()[1]
    hits = process.extract(q, list(by_stem.keys()), scorer=fuzz.token_set_ratio, limit=limit * 4,
                           score_cutoff=FUZZY_CUTOFF)
    qn = len(q.split())
    out: list[dict] = []
    for norm, score, _ in hits:
        if norm == q:
            continue
        if len(norm.split()) * 2 < qn:
            continue
        sort_score = fuzz.token_sort_ratio(q, norm)
        if sort_score < 75:
            continue
        for row in by_stem[norm][:2]:
            out.append({"name": row["name"], "entity_id": row.get("entity_id", ""),
                        "score": round(float(min(score, sort_score + 10)), 1)})
        if len(out) >= limit:
            break
    return out[:limit]


def style(raw: str, country: str | None = None) -> StyleResult:
    """Style one immediate-owner cell value. `country` (the pipeline's) is accepted for
    callers that have it; the rules do not depend on it today."""
    s = _collapse(raw)
    res = StyleResult(raw=str(raw if raw is not None else ""), styled=s)
    if s != str(raw):
        res.flags.append("whitespace")
    if not s or s in ("--", "—"):
        res.basis, res.confidence, res.note = "passthrough", "low", "empty"
        return res

    ru = rulings()["names"].get(normalize_name(s))
    if ru and ru.get("styled"):
        res.styled = ru["styled"]
        res.basis, res.confidence = "ruling", "high"
        res.flags.append("ruled")
        res.aliases = [a for a in (ru.get("aliases") or []) if a != res.styled]
        if s != res.styled and s not in res.aliases:
            res.aliases.append(s)
        _, res.legal_form, _ = split_legal_form(res.styled)
        res.note = f"ruled by Baird {ru.get('date', '')}: {ru.get('ruling', '')}".strip()
        return res

    if ";" in s:
        parts = [p.strip() for p in s.split(";") if p.strip()]
        subs = [style(p) for p in parts]
        res.styled = "; ".join(x.styled for x in subs)
        res.flags.append("multi_owner")
        for x in subs:
            res.flags += [f for f in x.flags if f not in res.flags]
            res.aliases += [a for a in x.aliases if a not in res.aliases]
        res.confidence = "low"
        res.note = ("one cell holds several owners — the sheet wants one per Owner<N> with its "
                    "own Owner<N>%; styled each part")
        return res

    former = bool(_FORMER_TAIL.search(s))
    if former:
        s = _FORMER_TAIL.sub("", s)
        res.flags.append("former")
    if _PCT_TAIL.search(s):
        s = _PCT_TAIL.sub("", s).strip()
        res.flags.append("percent_stripped")

    low = s.lower()
    if low in SENTINELS:
        res.styled = SENTINELS[low]
        res.basis, res.confidence, res.legal_form = "sentinel", "high", ""
        res.flags.append("sentinel")
        res.note = "ownership-team sentinel value"
        return _finish(res, former)

    if _NON_LATIN.search(s):
        res.styled = s
        res.basis, res.confidence = "passthrough", "low"
        res.flags.append("non_latin")
        res.note = ("non-Latin script: the English Owner<N> cell wants the romanized legal "
                    "name; the local-language spelling belongs in researcher_notes (the "
                    "operators/owners tab has no owner local-language column)")
        return _finish(res, former)

    # 1. exact gazetteer / confirmed alias on the raw spelling (before the rules can touch a
    #    legitimately odd legal name such as `PT Pertamina (Persero)`)
    hit = _lookup_exact(s)
    if hit:
        res.styled = s
        return _finish(_adopt(res, hit, "exact", "exact match in the ownership gazetteer"), former)
    conf, cand = aliases()
    a = conf.get(normalize_name(s))
    if a:
        res.styled = s
        return _finish(_adopt(res, a, "alias", "confirmed alias in data/owner_aliases.json"), former)

    # 2. rules
    t = s
    if _QUOTES.search(t) or t.count("'") >= 2 and t.startswith("'"):
        t = _collapse(_QUOTES.sub("", t).strip("'"))
        res.flags.append("quotes_stripped")

    ml = _ACRONYM_LEAD.match(t)
    if ml and ml.group(1) not in PAREN_KEEP and ml.group(1) not in US_STATE_CODES \
            and _form_key(ml.group(1)) not in legal_forms() and not _as_country(ml.group(1)):
        acro, inner = ml.group(1), _collapse(ml.group(2))
        t = inner
        res.flags.append("acronym_lead")
        res.aliases.insert(0, acro)
        if s not in res.aliases:
            res.aliases.append(s)
        if not is_abbreviation_of(acro, inner):
            res.flags.append("acronym_not_initials")

    m = _ACRONYM_TAIL.search(t)
    if m:
        acro = m.group(1)
        stem_before = t[:m.start()].strip()
        keep = (acro in PAREN_KEEP or acro in US_STATE_CODES or _as_country(acro)
                or fold_diacritics(acro) in subdivisions()
                or _form_key(acro) in legal_forms() or acro.lower() in PAREN_KEEP_WORDS
                or not stem_before or len(acro) < 2
                # mixed-case multi-word parentheticals are names, not trade names
                or (" " in acro and not acro.isupper()))
        if not keep:
            t = stem_before
            res.flags.append("acronym_dropped")
            if acro not in res.aliases:
                res.aliases.insert(0, acro)        # index 0: the note and _finish read it there
            if f"{stem_before} ({acro})" != s and s not in res.aliases:
                res.aliases.append(s)
            if not is_abbreviation_of(acro, stem_before):
                res.flags.append("acronym_not_initials")

    sb = _state_body(t)
    if sb:
        styled, note = sb
        res.styled = styled
        res.legal_form = ""
        res.flags.append("state_body")
        res.basis = "rules"
        res.confidence = "medium" if styled == t else "low"
        res.note = note
        hit = _lookup_exact(styled)
        if hit:
            return _finish(_adopt(res, hit, "exact", "styled form matches the gazetteer"), former)
        a = conf.get(normalize_name(styled))
        if a:
            return _finish(_adopt(res, a, "alias", "styled form is a confirmed alias"), former)
        # fuzzy near-hits must share the parenthetical country, else every ministry matches
        mc = re.search(r"\(([^)]+)\)$", styled)
        res.candidates = [x for x in _fuzzy(styled) if not mc or f"({mc.group(1)})" in x["name"]]
        if res.candidates:
            res.flags.append("fuzzy_candidates")
        return _finish(res, former)

    toks = _split_form_tokens(t.split(" "))
    if " ".join(toks) != t:
        res.flags.append("form_punctuation")      # `X Company, LLC` -> `X Company LLC`: the comma went
    forms = legal_forms()

    # dotted all-caps abbreviations lose their dots (U.S.A. -> USA, S.A. -> SA); `E.ON` is
    # not one (letters after the dot) and keeps its integral punctuation
    for i, tok in enumerate(toks):
        if re.fullmatch(r"(?:[A-Z]\.){2,}", tok) and _form_key(tok) not in forms:
            toks[i] = tok.replace(".", "")
            res.flags.append("dots_stripped")

    # leading LONG form -> trailing short form (Public Joint Stock Company Transneft ->
    # Transneft PJSC; Limited Liability Company X -> X LLC). Only multi-word phrases here —
    # a leading `Company`/`Corporation` is part of a name (`Company of the Nile`).
    low_t = fold_diacritics(" ".join(toks)).lower()
    for long, short in LONG_FORMS:
        lk = fold_diacritics(long).lower()
        if " " in lk and low_t.startswith(lk + " ") and len(low_t) > len(lk) + 1:
            rest = " ".join(toks)[len(long):].strip(" ,")
            toks = rest.split(" ") + [short]
            res.flags += ["form_moved", "form_long"]
            break

    # leading form -> trailing (PAO Gazprom -> Gazprom PJSC; AB Amber Grid -> Amber Grid AB)
    lead_key = _form_key(toks[0]) if toks else ""
    if len(toks) > 1 and lead_key in LEADING_FORMS and lead_key not in LEADING_KEEP:
        mapped = CIS_FORMS.get(lead_key) or forms.get(lead_key, toks[0])
        toks = toks[1:] + [mapped]
        res.flags.append("form_moved")
        if lead_key in CIS_FORMS:
            res.flags.append("form_russian")
        if lead_key in CIS_CHECK:
            res.flags.append("form_check_registration")

    # long forms at the end (Corporation -> Corp, Company Limited -> Co Ltd, …)
    joined = " ".join(toks)
    low_j = fold_diacritics(joined).lower()
    for long, short in LONG_FORMS:
        lk = fold_diacritics(long).lower()
        if low_j.endswith(" " + lk) and len(low_j) > len(lk) + 1:
            cut = len(joined) - len(long)
            new_joined = joined[:cut].rstrip(" ,") + " " + short
            if new_joined != joined:
                res.flags.append("form_long")
            toks = new_joined.split(" ")
            break
    # also a long form immediately BEFORE a trailing form: `Kuwait Petroleum Corporation Ltd`
    # is covered above by the two-word entries; `X Company (Private) Ltd` is left alone.

    # punctuation inside trailing form tokens, CIS abbreviations trailing (Gazprom PAO)
    changed_form = False
    for i in range(len(toks) - 1, max(len(toks) - 5, 0) - 1, -1):
        k = _form_key(toks[i])
        if k in CIS_FORMS and i == len(toks) - 1:
            toks[i] = CIS_FORMS[k]
            res.flags.append("form_russian")
            if k in CIS_CHECK:
                res.flags.append("form_check_registration")
            changed_form = True
            continue
        if k in forms and i >= 1 and not re.search(r"[()]", toks[i]):
            # only rewrite when it reads as a form: trailing, or followed only by form tokens
            # (a token with a parenthesis is part of a parenthetical, never a bare form)
            rest = [_form_key(x) for x in toks[i + 1:]]
            if all(x in forms for x in rest):
                # "Company" STAYS when the form is LLC / LP (guide): `X Company, L.L.C.` ->
                # `X Company LLC`, not `X Co LLC`
                new = "Company" if k in ("company", "co") and set(rest) & {"llc", "lp"} and \
                    toks[i].strip(",.").lower() == "company" else forms[k]
                if new != toks[i]:
                    toks[i] = new
                    changed_form = True
    if changed_form and "form_long" not in res.flags and "form_punctuation" not in res.flags:
        res.flags.append("form_punctuation")

    styled = _collapse(" ".join(toks)).rstrip(",.")
    stem, form, _ = split_legal_form(styled)
    res.legal_form = form
    res.styled = styled

    if re.search(r"\b(?:JV|Joint Venture)$", styled):
        res.flags.append("jv")
    elif not form:
        if re.search(r"\bGroup$", styled):
            res.flags.append("group")
        res.flags.append("no_legal_form")

    # 3. gazetteer again, on the styled form
    hit = _lookup_exact(styled)
    if hit:
        return _finish(_adopt(res, hit, "exact", "styled form matches the ownership gazetteer"), former)
    a = conf.get(normalize_name(styled))
    if a:
        return _finish(_adopt(res, a, "alias", "styled form is a confirmed alias"), former)
    hit = _lookup_form(styled)
    if hit:
        # same stem, same canonical form, spelled differently (`Kuwait Oil Company Ltd` vs
        # our `Kuwait Oil Co Ltd`): the team's spelling wins — it is their vocabulary
        return _finish(_adopt(res, hit, "exact", "same name and legal form as a gazetteer entry; "
                              "the team's spelling adopted"), former)
    stems = _lookup_stem(styled)
    if stems and not form:
        # name without a legal form; the gazetteer has this exact name WITH one. The guide says
        # add the form, and the team already did — adopt when it is unambiguous.
        names = sorted({r["name"] for r in stems})
        if len(names) == 1:
            if styled != s:
                res.aliases.append(styled)
            res.flags = [f for f in res.flags if f != "no_legal_form"] + ["form_from_gazetteer"]
            out = _adopt(res, stems[0], "exact", "stem matches one gazetteer entry; its legal "
                         "form adopted (flag form_from_gazetteer — confirm in a quick search)")
            out.basis, out.confidence = "stem", "medium"
            return _finish(out, former)
        for r in stems:
            res.candidates.append({"name": r["name"], "entity_id": r.get("entity_id", ""),
                                   "score": 100.0, "source": "same stem, several forms"})
        res.flags.append("form_ambiguous")
    elif stems:
        # same stem, DIFFERENT form (Tatneft OJSC vs Tatneft PJSC) — a registration question
        for r in stems:
            if r["name"] != styled:
                res.candidates.append({"name": r["name"], "entity_id": r.get("entity_id", ""),
                                       "score": 100.0, "source": "same stem, different form"})
        if res.candidates:
            res.flags.append("form_conflict")
    c = cand.get(normalize_name(styled)) or cand.get(normalize_name(s))
    if c:
        res.flags.append("alias_candidate")
        res.candidates.append({"name": c["canonical"], "entity_id": (c.get("entity_ids") or [""])[0],
                               "score": None, "source": "owner_aliases.json candidates"})
    fuzzy = [x for x in _fuzzy(styled) if x["name"] not in {y["name"] for y in res.candidates}]
    if fuzzy:
        res.candidates += fuzzy
        res.flags.append("fuzzy_candidates")

    res.basis = "rules"
    res.confidence = "medium" if form or "jv" in res.flags else "low"
    bits = []
    if "acronym_dropped" in res.flags:
        bits.append(f"trailing acronym dropped (kept as alias: {res.aliases[0]!r})")
    if "acronym_lead" in res.flags:
        bits.append(f"leading acronym dropped, the legal name in parentheses kept (alias: {res.aliases[0]!r})")
    if "form_moved" in res.flags:
        bits.append("leading legal form moved to the end")
    if "form_russian" in res.flags:
        bits.append("CIS form mapped (OOO->LLC, PAO->PJSC, AO->JSC, TOO->LLP)")
    if "form_long" in res.flags or "form_punctuation" in res.flags:
        bits.append("legal form in the team's short, unpunctuated spelling")
    if "no_legal_form" in res.flags:
        bits.append("no legal form found — add it if a quick registry search gives one, "
                    "else record as the source spells it")
    if res.candidates:
        bits.append(f"near-match in gazetteer NOT adopted: {res.candidates[0]['name']!r}")
    res.note = "; ".join(bits) or "no change"
    return _finish(res, former)


# Flags a mechanical re-spelling may carry and still be adopted without a person looking:
# the entity is the same, only the team's spelling of it differs.
MECHANICAL_FLAGS = frozenset({"whitespace", "form_punctuation", "form_long", "form_moved", "form_russian",
                              "dots_stripped", "acronym_dropped", "acronym_lead", "quotes_stripped",
                              "form_from_gazetteer", "percent_stripped", "ruled"})
# Flags that make a re-spelling a judgment (who the entity is, which form it is registered under)
JUDGMENT_FLAGS = frozenset({"fuzzy_candidates", "no_legal_form", "form_conflict", "form_ambiguous",
                            "alias_candidate", "acronym_not_initials", "multi_owner", "non_latin",
                            "form_check_registration", "state_body", "jv", "group", "former", "sentinel"})


def adoptable(res: StyleResult) -> bool:
    """May this styled form replace the raw one with no person looking? Yes on an exact
    gazetteer hit, a confirmed alias or a ruling; yes on a rules/stem result whose flags are all
    mechanical; no otherwise (docs/plans/2026-10-05_owner-style-normalization.md, Phase 0/2a).
    A comma that survives styling in a rules-only value is a list of names the rules cannot see,
    so no; a comma the styler removed before a legal form (`Co., Ltd.`, `Company, LLC`) is
    punctuation and fine."""
    if not res.changed:
        return True
    if "acronym_not_initials" in res.flags and res.basis != "ruling":
        return False            # the dropped parenthetical ('affiliate', 'IOCL') may say something a
                                # person should read, whatever the rest of the name matched
    if res.basis in ("exact", "alias", "ruling"):
        return True
    if res.basis in ("rules", "stem"):
        if "," in res.styled:
            return False
        return bool(res.flags) and set(res.flags) <= MECHANICAL_FLAGS
    return False


def _finish(res: StyleResult, former: bool) -> StyleResult:
    if former and not res.styled.endswith("[former]"):
        res.styled = f"{res.styled} [former]"
    # a gazetteer adoption rewrites the note; the dropped acronym must still be in it so the
    # researcher carries it into researcher_notes (Baird 2026-10-01: drop it, keep it in notes)
    if ("acronym_dropped" in res.flags or "acronym_lead" in res.flags) and res.aliases \
            and "acronym" not in res.note:
        res.note = f"acronym dropped (kept as alias: {res.aliases[0]!r}); {res.note}"
    res.aliases = [a for a in dict.fromkeys(res.aliases) if a and a != res.styled]
    res.flags = list(dict.fromkeys(res.flags))
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("names", nargs="+")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    out = [style(n) for n in a.names]
    if a.json:
        print(json.dumps([r.to_dict() for r in out], ensure_ascii=False, indent=1))
        return
    for r in out:
        arrow = "==" if not r.changed else "->"
        print(f"{r.raw!r} {arrow} {r.styled!r}  [{r.confidence}/{r.basis}"
              f"{' ' + r.entity_id if r.entity_id else ''}] form={r.legal_form or '-'}"
              f"{'  flags=' + ','.join(r.flags) if r.flags else ''}")
        if r.aliases:
            print(f"    aliases: {r.aliases}")
        if r.candidates:
            print("    candidates (not adopted): " +
                  "; ".join(f"{c['name']} ({c.get('score')})" for c in r.candidates[:3]))
        if r.note:
            print(f"    {r.note}")


if __name__ == "__main__":
    main()
