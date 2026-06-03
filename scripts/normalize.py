"""Normalizers shared across the engine: country, name, status, diameter, length,
owners. Pure functions, no I/O. Keep deterministic (no clocks/randomness)."""
from __future__ import annotations

import re
import unicodedata

# GEM Status controlled vocab (lowercase) — see docs/reference/controlled_vocab.md
GEM_STATUSES = {
    "operating", "proposed", "construction", "shelved",
    "cancelled", "idle", "mothballed", "retired",
}

MILES_TO_KM = 1.609344

# Country aliases -> canonical lowercase form used for blocking. GEM uses common
# names; scraped datasets use ISO/long forms. Extend as new sources appear.
_COUNTRY_ALIASES = {
    "russian federation": "russia",
    "united states of america": "united states",
    "usa": "united states",
    "us": "united states",
    "united kingdom of great britain and northern ireland": "united kingdom",
    "uk": "united kingdom",
    "great britain": "united kingdom",
    "türkiye": "turkey",
    "turkiye": "turkey",
    "iran (islamic republic of)": "iran",
    "islamic republic of iran": "iran",
    "korea, republic of": "south korea",
    "republic of korea": "south korea",
    "korea, democratic people's republic of": "north korea",
    "viet nam": "vietnam",
    "syrian arab republic": "syria",
    "lao people's democratic republic": "laos",
    "brunei darussalam": "brunei",
    "côte d'ivoire": "ivory coast",
    "cote d'ivoire": "ivory coast",
    "congo, the democratic republic of the": "democratic republic of the congo",
    "tanzania, united republic of": "tanzania",
    "bolivia (plurinational state of)": "bolivia",
    "venezuela (bolivarian republic of)": "venezuela",
    "czechia": "czech republic",
    "myanmar": "myanmar",
    "burma": "myanmar",
}


def fold_diacritics(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def normalize_country(s: str | None) -> str:
    """Canonical lowercase country for blocking. Idempotent."""
    if not s:
        return ""
    c = fold_diacritics(str(s)).strip().lower()
    c = re.sub(r"\s+", " ", c)
    return _COUNTRY_ALIASES.get(c, c)


def split_countries(s: str | None) -> list[str]:
    """GEM CountriesOrAreas can be multi-country: 'Qatar, Saudi Arabia, Jordan'."""
    if not s:
        return []
    parts = re.split(r"[;,/]", str(s))
    return [normalize_country(p) for p in parts if p and p.strip()]


_NAME_STOP = {
    "pipeline", "pipelines", "line", "lines", "system", "systems", "project",
    "the", "of", "and", "oil", "gas", "crude", "ngl", "natural", "co", "company",
    "ltd", "ltda", "inc", "llc", "plc", "corp", "sa", "pipe",
}


def normalize_name(s: str | None, *, drop_stopwords: bool = False) -> str:
    """Lowercase, fold diacritics, punctuation->space, collapse whitespace.
    rapidfuzz token_set_ratio handles word order; stopword removal is optional."""
    if not s:
        return ""
    t = fold_diacritics(str(s)).lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)
    toks = [w for w in t.split() if w]
    if drop_stopwords:
        kept = [w for w in toks if w not in _NAME_STOP]
        toks = kept or toks  # never empty
    return " ".join(toks)


def map_status(raw: str | None, status_map: dict | None) -> str | None:
    """Source status string -> GEM lowercase vocab via the manifest status_map,
    with a lowercased-passthrough fallback when it's already valid."""
    if raw is None:
        return None
    raw_s = str(raw).strip()
    if not raw_s:
        return None
    if status_map:
        # exact, then case-insensitive
        if raw_s in status_map:
            return status_map[raw_s]
        low = {k.lower(): v for k, v in status_map.items()}
        if raw_s.lower() in low:
            return low[raw_s.lower()]
    return raw_s.lower() if raw_s.lower() in GEM_STATUSES else None


def parse_diameter_set(s, units: str = "in") -> list[float]:
    """Parse GEM/source multi-value diameters ('46, 48', '40/42/48', '56,10,16')
    into a sorted set of inches. Converts mm/cm to inches if needed."""
    if s is None:
        return []
    out: set[float] = set()
    for tok in re.split(r"[,/;]+", str(s)):
        tok = tok.strip()
        m = re.search(r"-?\d+(?:\.\d+)?", tok)
        if not m:
            continue
        v = float(m.group())
        if units == "mm":
            v /= 25.4
        elif units == "cm":
            v /= 2.54
        if v > 0:
            out.add(round(v, 2))
    return sorted(out)


def parse_length_km(s, units: str = "km") -> float | None:
    """Attribute length -> km. Source 'length' may be miles (GulfPub oil) or km."""
    if s is None:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", str(s).replace(",", ""))
    if not m:
        return None
    v = float(m.group())
    if v <= 0:
        return None
    if units == "mi":
        v *= MILES_TO_KM
    elif units == "m":
        v /= 1000.0
    return round(v, 3)


def parse_number(s) -> float | None:
    if s is None:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", str(s).replace(",", ""))
    return float(m.group()) if m else None


def parse_year(s) -> int | None:
    if s is None:
        return None
    m = re.search(r"(19|20)\d{2}", str(s))
    return int(m.group()) if m else None


def parse_owners(s) -> list[str]:
    """Split an owner/shareholder string into entity names, stripping percentages.
    Handles 'Sonatrach (52%), Eni (48%)' and GEM-style 'Saudi Aramco [100.%]'.
    Best-effort: owners are a low-weight matching signal."""
    if not s:
        return []
    text = str(s).strip()
    if text in ("--", "—", ""):
        return []
    # Prefer splitting at ')'/']' + comma boundaries (keeps names with internal commas);
    # fall back to plain comma/semicolon/&/ ' and '.
    if re.search(r"[)\]]\s*,", text):
        parts = re.split(r"(?<=[)\]])\s*,\s*", text)
    else:
        parts = re.split(r"\s*[;&]\s*|\s*,\s*|\s+\band\b\s+", text)
    out = []
    for p in parts:
        name = re.sub(r"\s*[\(\[][^)\]]*[\)\]]\s*$", "", p).strip()  # trailing (NN%) / [NN.%]
        name = re.sub(r"\s+", " ", name).strip(" .,-")
        if name and name not in out:
            out.append(name)
    return out
