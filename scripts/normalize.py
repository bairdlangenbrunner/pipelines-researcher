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


# Cyrillic -> Latin. normalize_name() strips everything outside [a-z0-9], so
# without this a Cyrillic-only name ("Союз", "Кременчук - Ананьїв - Богородчани")
# normalizes to the EMPTY STRING and the record is silently unnamed to the matcher
# — not mismatched, invisible. That is how the Ukraine OSM extract scored 0.1%
# overlap while reporting 9.2% of records "named".
# Merged Ukrainian / Russian / Kazakh table, BGN/PCGN-flavoured. It does not have to
# agree with any one romanization standard: both sides go through it and the name
# axis is fuzzy (token_set_ratio), so soyuz/soiuz and bogorodchani/bohorodchany
# still score high. `г` is the one letter worth branching on — it is `h` in
# Ukrainian (Bohorodchany) and `g` in Russian (Gazprom).
_CYRILLIC_RE = re.compile(r"[Ѐ-ԯ]")
_UKRAINIAN_MARKERS = re.compile(r"[іїєґ]")

_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "д": "d", "е": "e", "ё": "e", "є": "ie",
    "ж": "zh", "з": "z", "і": "i", "ї": "i", "й": "i", "к": "k", "л": "l",
    "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
    "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh",
    "щ": "shch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    "ґ": "g",
    # Kazakh / Central Asian extras
    "ә": "a", "ғ": "g", "қ": "k", "ң": "ng", "ө": "o", "ұ": "u", "ү": "u",
    "һ": "h", "ы": "y", "і": "i",
}


def translit_cyrillic(s: str) -> str:
    """Romanize Cyrillic so it survives normalize_name()'s ASCII filter."""
    if not _CYRILLIC_RE.search(s):
        return s
    low = s.lower()
    uk = bool(_UKRAINIAN_MARKERS.search(low))
    out = []
    for ch in low:
        if ch == "г":
            out.append("h" if uk else "g")
        elif ch == "и":
            out.append("y" if uk else "i")
        else:
            out.append(_TRANSLIT.get(ch, ch))
    return "".join(out)


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


def country_matches(rec_country: str | None, want: str) -> bool:
    """Does a record whose country field may name SEVERAL countries belong to `want`?

    Use this for every country-scope filter on the REFERENCE side. A scraped
    source routinely writes cross-border trunks as one multi-country string —
    GulfPub has 'Russian Federation / Ukraine', 'Ukraine / Moldova',
    'Russian Federation / Kazakhstan / Ukraine'. `ingest.py` and `reconcile.py`
    both used to test plain equality against one normalized string, so every such
    record was silently dropped and a country-scoped run saw only the segments
    lying wholly inside one border. That discarded 47 of 158 GulfPub gas features
    for Ukraine and 31 of 63 for Kazakhstan — precisely the transit trunks, which
    are the majority of GEM's rows in both countries (defect found 2026-08-12).

    The GEM side has always done this correctly via `split_countries`; the
    reference side was the asymmetry. Whole-string equality is tried FIRST because
    four `_COUNTRY_ALIASES` keys contain a comma ('congo, the democratic republic
    of the', 'korea, republic of', …) and splitting before the alias lookup would
    shred them.
    """
    if not rec_country:
        return False
    if rec_country == want:
        return True
    return want in split_countries(rec_country)


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
    t = fold_diacritics(translit_cyrillic(str(s))).lower()
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


# A comma is BOTH the multi-value delimiter GEM uses ('700, 720, 820') and the
# thousands separator prose uses ('1,020 mm') — so splitting naively turned wiki text
# '1,020 mm' into [1, 20] -> [0.04, 0.79] inches. Collapse only the unambiguous
# thousands case: 1-2 digits, comma, exactly 3 digits, no space and no 4th digit.
# '530,720' keeps its comma (leading group is 3 digits) and '8, 600' keeps it (space).
# The lookbehind excludes a preceding '.' as well as a digit, or the real multi-value
# row '323.9,168.3' would have its '9,168' collapsed into one bogus 323.9168.
_THOUSANDS = re.compile(r"(?<![\d.])(\d{1,2}),(\d{3})(?!\d)")
# A token may carry its OWN unit, which beats the caller's default: multi-segment wiki
# strings mix them ('1,020 mm; 700, 1015 mm') and restate one value in two units
# ('820 mm / 32.28 inches', which read as a second mm value = 1.27 in).
# No leading \b on mm/cm: sources write it flush against the number ('1200mm'). Inches
# DOES need one, or the 'in' in 'line'/'min' would match.
_TOK_MM = re.compile(r"(?:mm|millimet\w*|мм)\b", re.I)
_TOK_CM = re.compile(r"(?:cm|centimet\w*|см)\b", re.I)
_TOK_IN = re.compile(r"\b(?:in|ins|inch\w*|дюйм\w*)\b|[\"”″]", re.I)


def parse_diameter_set(s, units: str = "in") -> list[float]:
    """Parse GEM/source multi-value diameters ('46, 48', '40/42/48', '56,10,16')
    into a sorted set of inches. Converts mm/cm to inches if needed.

    `units` is the DEFAULT for tokens that don't state a unit; a token that names its
    own unit ('820 mm / 32.28 inches') is converted on its own terms. Thousands
    separators are collapsed first — see `_THOUSANDS`."""
    if s is None:
        return []
    out: set[float] = set()
    for tok in re.split(r"[,/;]+", _THOUSANDS.sub(r"\1\2", str(s))):
        tok = tok.strip()
        m = re.search(r"-?\d+(?:\.\d+)?", tok)
        if not m:
            continue
        v = float(m.group())
        u = units
        if _TOK_MM.search(tok):
            u = "mm"
        elif _TOK_CM.search(tok):
            u = "cm"
        elif _TOK_IN.search(tok):
            u = "in"
        if u == "mm":
            v /= 25.4
        elif u == "cm":
            v /= 2.54
        if v > 0:
            out.add(round(v, 2))
    return sorted(out)


def gem_diameter_set(row) -> list[float]:
    """GEM `Diameter` -> inches, honouring the row's OWN `DiameterUnits` column.

    GEM stores diameter in whichever unit the source stated and tags the unit per row:
    across GGIT gas 1,499 rows say `mm` and 1,669 say `in` (GOIT oil: 400 mm / 1,062 in).
    So a bare `parse_diameter_set(row['Diameter'])` — which defaults to inches — silently
    reads 530 mm as 530 INCHES. That was live in match.py and build_qc_workbook.py until
    2026-08-11: it zeroed the diameter signal on ~45% of gas rows (42 of 44 Kazakhstan gas
    rows are mm) and made check_diameter flag every mm row as out-of-range.

    Do NOT use the sheet's `DiameterInMm` column instead: it is a formula that emits `--`
    on multi-value rows ('700, 720, 820, 1000, 1020'), which is exactly the case the
    multi-value parser exists for. When `DiameterUnits` is blank (5 gas rows), fall back on
    magnitude — no real pipeline is 100 inches (2.54 m), so >=100 can only be millimetres.
    """
    raw = row.get("Diameter")
    units = str(row.get("DiameterUnits") or "").strip().lower()
    if units.startswith("mm"):
        units = "mm"
    elif units.startswith("cm"):
        units = "cm"
    elif units.startswith("in"):
        units = "in"
    else:
        vals = parse_diameter_set(raw, "in")   # unconverted magnitudes
        units = "mm" if vals and max(vals) >= 100 else "in"
    return parse_diameter_set(raw, units)


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


# capacity unit -> multiplier to bcm/y (1 MMcf/d = 1e6 cf/d * 0.0283168 m3 * 365 / 1e9)
_CAP_UNIT_FACTORS = [
    (r"bcm\s*/\s*y|billion\s+cubic\s+met", 1.0),
    (r"bcf\s*/\s*d|billion\s+cubic\s+feet\s+per\s+day", 10.336),
    (r"mmcf|million\s+cubic\s+feet", 0.010336),          # per day assumed
    (r"mcm\s*/\s*d|million\s+cubic\s+met", 0.365),       # per day
    (r"m3\s*/\s*h|m³\s*/\s*h|cubic\s+met\w*\s+per\s+hour", 24 * 365 / 1e9),
]


def capacity_to_bcmy(value, units: str | None = None) -> tuple[float, float] | None:
    """Capacity value (+ optional separate units string) -> (lo, hi) in bcm/y.
    Handles embedded units ('180 MMcf/d', '12 billion cubic meters per year') and
    ranges ('5-7 bcm/y'). Returns None when no number or no recognizable unit."""
    if value is None:
        return None
    text = str(value).replace(",", "")
    nums = [float(m) for m in re.findall(r"\d+(?:\.\d+)?", text)]
    if not nums:
        return None
    # a range is exactly two numbers joined by -, – or 'to'
    if len(nums) >= 2 and re.search(r"\d\s*(?:[-–—]|to)\s*\d", text):
        lo, hi = min(nums[0], nums[1]), max(nums[0], nums[1])
    else:
        lo = hi = nums[0]
    unit_text = f"{text} {units or ''}".lower()
    for pat, factor in _CAP_UNIT_FACTORS:
        if re.search(pat, unit_text):
            return (round(lo * factor, 4), round(hi * factor, 4))
    return None


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
