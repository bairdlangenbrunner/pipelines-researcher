"""Geographic (admin-area) matching signal — where the pipe physically is.

The engine's other attribute signals all read TEXT the two sides happen to share:
name, endpoint strings, diameter, length. When a reference feature is unnamed and
the GEM row has no drawn route, every one of them is dead and the matcher scores on
nothing (Iraq OSM 2026-07-28: 2 of 52 features named, 34 of 54 GEM rows routeless →
0 overlaps out of 52, a silent null run).

This module supplies the signal that survives that: a reference geometry always
knows *where it is*, and a GEM row almost always declares its country and
state/province even when it has no route. Resolving the trace's vertices against
Natural Earth admin-0/admin-1 and scoring that footprint against GEM's
Start/End Country + State/Province + Prefecture/District recovers the match.

Worked case — OSM way/1494626715, unnamed, 42" / 116.6 km:
    start (45.459, 34.018) -> Iran, Kermanshah      GEM P5855 StartCountryOrArea = Iran
    end   (44.547, 33.319) -> Iraq, Diyala          GEM P5855 EndCountryOrArea   = Iraq
                                                    GEM P5855 EndState/Province  = Diyala
Three-way hit on a row whose name, endpoints, diameter, length and route are all blank.

OPT-IN BY DESIGN. `geoarea_weight` defaults to 0.0, so adding this module does not
move any composite in an already-committed run (Libya / Egypt / Saudi / Iran
reproduce bit-for-bit). A dataset turns it on in its manifest `matching:` block.
That is the deliberate answer to the GulfPub-Iraq escalation's warning that the
weights are global and retuning one country silently rewrites the others.

Data: data/boundaries/ne_10m_admin_1_states_provinces.shp (Natural Earth, already
committed for this repo; admin-0 comes from the same folder's ne_50m file used by
route_integrity.py). No network.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import paths  # noqa: E402
from normalize import fold_diacritics, normalize_country  # noqa: E402

ADMIN1_SHP = paths.repo_root() / "data" / "boundaries" / "ne_10m_admin_1_states_provinces.shp"

# Vertices sampled per trace when resolving its admin footprint. A pipeline crossing a
# province is caught by its interior vertices, not just its endpoints, but running
# point-in-polygon over every vertex of a 300-point way is wasteful — the footprint is
# stable well before that.
MAX_SAMPLE_VERTICES = 40

# Below this the two admin names are different places, not spelling drift.
_FUZZ_FLOOR = 0.80


class BoundariesUnavailable(RuntimeError):
    """Shapefile missing or geopandas not installed — caller degrades to no signal."""


@lru_cache(maxsize=1)
def _admin1():
    """(GeoDataFrame, spatial index). Cached: the read is ~1s and 4,596 polygons."""
    if not ADMIN1_SHP.exists():
        raise BoundariesUnavailable(
            f"missing {ADMIN1_SHP} — download Natural Earth 10m admin-1 "
            f"(ne_10m_admin_1_states_provinces.zip) into data/boundaries/")
    try:
        import geopandas as gpd
    except ImportError as e:  # pragma: no cover
        raise BoundariesUnavailable("geopandas not installed") from e
    gdf = gpd.read_file(ADMIN1_SHP)
    return gdf, gdf.sindex


def _norm_admin(s: str | None) -> str:
    """Fold an admin-area name to a comparison key.

    GEM, OSM and Natural Earth transliterate Arabic/Farsi province names three
    different ways ('Wassit' / 'Wasit', 'Erbil' / 'Arbil', 'Basrah' / 'Al-Basrah'),
    so the article prefix and separators come off and diacritics fold.
    """
    t = fold_diacritics(str(s or "")).lower().strip()
    for art in ("al-", "al ", "as-", "as ", "an-", "an ", "at-", "at ", "ad-", "ad "):
        if t.startswith(art):
            t = t[len(art):]
            break
    return " ".join(t.replace("-", " ").replace("_", " ").replace("'", "").split())


def _variants(row) -> set:
    """Every spelling Natural Earth carries for one admin-1 polygon.

    `name_alt` is a pipe-separated alias list and is the field that actually closes
    the gap to GEM's spellings (NE 'Wasit' has alt 'Kut|Kut-al-Imara'; NE 'Arbil' has
    'Arbela|Erbil|Irbil').
    """
    out = set()
    for key in ("name", "name_en", "name_alt", "gn_name", "woe_name", "gns_name"):
        val = row.get(key)
        if not val:
            continue
        for piece in str(val).split("|"):
            k = _norm_admin(piece)
            if k:
                out.add(k)
    return out


def admin_footprint(geom: dict, max_vertices: int = MAX_SAMPLE_VERTICES) -> dict:
    """Resolve a GeoJSON (Multi)LineString to the admin areas it passes through.

    Returns {"countries": {normalized-country: n_vertices},
             "admin1":    {(normalized-country, admin1-key): n_vertices},
             "admin1_display": {(country, key): "Pretty Name"},
             "endpoints": {"start": (country, key)|None, "end": (country, key)|None}}
    Vertex counts let a caller weight a province the line merely clips against one it
    runs the length of. Never raises on a bad geometry — returns empty dicts.
    """
    empty = {"countries": {}, "admin1": {}, "admin1_display": {}, "endpoints": {"start": None, "end": None}}
    pts = _sample_vertices(geom, max_vertices)
    if not pts:
        return empty
    try:
        gdf, sindex = _admin1()
        from shapely.geometry import Point
    except BoundariesUnavailable:
        raise
    except Exception:
        return empty

    countries: dict[str, int] = {}
    admin1: dict[tuple, int] = {}
    display: dict[tuple, str] = {}
    resolved: list = []

    for lon, lat in pts:
        p = Point(lon, lat)
        key = None
        for idx in sindex.query(p, predicate="intersects"):
            row = gdf.iloc[idx]
            ctry = normalize_country(row.get("admin"))
            if not ctry:
                continue
            a1 = _norm_admin(row.get("name"))
            key = (ctry, a1)
            countries[ctry] = countries.get(ctry, 0) + 1
            admin1[key] = admin1.get(key, 0) + 1
            display.setdefault(key, str(row.get("name") or ""))
            break
        resolved.append(key)

    return {"countries": countries, "admin1": admin1, "admin1_display": display,
            "endpoints": {"start": resolved[0], "end": resolved[-1]}}


def _sample_vertices(geom: dict | None, cap: int) -> list:
    """Endpoints always, plus an even stride through the interior up to `cap`."""
    if not geom:
        return []
    t, c = geom.get("type"), geom.get("coordinates") or []
    if t == "LineString":
        lines = [c] if c else []
    elif t == "MultiLineString":
        lines = [ln for ln in c if ln]
    else:
        return []
    pts = [pt for ln in lines for pt in ln if pt and len(pt) >= 2]
    if len(pts) <= cap:
        return pts
    step = len(pts) / float(cap - 1)
    out = [pts[min(int(i * step), len(pts) - 1)] for i in range(cap - 1)]
    out.append(pts[-1])
    return out


def _name_hit(gem_text: str | None, keys: set, aliases: dict) -> bool:
    """Does a GEM admin string name one of the footprint's admin areas?

    Exact on the folded key first, then the NE alias set, then a fuzzy floor for
    residual transliteration drift. Substring matching is deliberately NOT used: it
    would fire 'Najaf' against 'An-Najaf' correctly but also 'Basrah' against
    'Al-Basrah' *and* every string containing them.
    """
    k = _norm_admin(gem_text)
    if not k:
        return False
    if k in keys:
        return True
    for key, alts in aliases.items():
        if key in keys and k in alts:
            return True
    try:
        from rapidfuzz import fuzz
    except ImportError:
        return False
    return any(fuzz.token_set_ratio(k, cand) / 100.0 >= _FUZZ_FLOOR for cand in keys)


def geoarea_score(footprint: dict, gem, scope_country: str | None = None) -> tuple[float | None, list]:
    """Score a reference trace's admin footprint against a GEM row's declared geography.

    Returns (score in 0..1 or None when the row declares nothing discriminating, reasons).

    Two components, averaged over whichever are testable:
      * admin-1        — does the row's Start/End State/Province (or Prefecture/
                         District) name a province the trace passes through? A terminus
                         province scores full, one merely transited scores partial,
                         since GEM's Start/End fields describe termini, not corridors.
      * foreign-country — of the countries the row declares, do the ones OUTSIDE the
                         run's scope country show up in the trace? This is the
                         cross-border signal (P5855 declares Iran; the trace really does
                         start in Kermanshah).

    The scope country is deliberately excluded from scoring. A reconciliation run is
    scoped to one country, so "both are in Iraq" is true of every candidate row and
    discriminates nothing — crediting it would let a row that declares ONLY a country
    score a perfect 1.0 on no information (Iraq P4064 did exactly that in testing).
    That is the same renormalize-over-present-signals trap PHYSICAL_SIGNALS guards
    against in reconcile.py.

    None (not 0.0) when untestable, so composite() renormalizes instead of penalizing —
    absence of declared geography is not evidence against a match. A DECLARED province
    that the trace misses does score 0.0: that is real negative evidence.
    """
    if not footprint or not (footprint.get("countries") or footprint.get("admin1")):
        return None, []

    keys = set(footprint["admin1"].keys())
    a1_keys = {k[1] for k in keys}
    aliases = _alias_index(keys)
    ends = footprint.get("endpoints") or {}
    end_a1 = {v[1] for v in (ends.get("start"), ends.get("end")) if v}
    ctry_keys = set(footprint["countries"].keys())

    parts: list[tuple[float, float]] = []   # (weight, score)
    reasons: list[str] = []

    # --- foreign country (cross-border evidence only) ---
    scope = normalize_country(scope_country) if scope_country else None
    gem_ctries = [c for c in (normalize_country(t) for t in gem.country_texts()) if c]
    foreign = [c for c in gem_ctries if c != scope]
    if foreign:
        hits = sum(1 for c in foreign if c in ctry_keys)
        parts.append((0.4, hits / float(len(foreign))))
        reasons.append(f"geo-foreign {hits}/{len(foreign)} ({','.join(foreign)})")

    # --- admin-1 ---
    # A row's own termini (endpoint_admin_texts) score full on an endpoint province;
    # provinces inherited from a network's members can only ever be "transited", since
    # the network has no termini of its own.
    gem_a1 = gem.admin_area_texts()
    if gem_a1:
        termini = set(gem.endpoint_admin_texts())
        best = 0.0
        hit_names = []
        for t in gem_a1:
            if t in termini and _name_hit(t, end_a1, aliases):
                best = max(best, 1.0)
                hit_names.append(f"{t}=endpoint")
            elif _name_hit(t, a1_keys, aliases):
                best = max(best, 0.6)
                hit_names.append(f"{t}=transited")
        parts.append((0.6, best))
        reasons.append("geo-admin1 " + (", ".join(hit_names) if hit_names else "none"))

    if not parts:
        return None, []
    wsum = sum(w for w, _ in parts)
    return round(sum(w * s for w, s in parts) / wsum, 3), reasons


@lru_cache(maxsize=64)
def _alias_index_cached(keys: tuple) -> dict:
    gdf, _ = _admin1()
    want = set(keys)
    out: dict[tuple, set] = {}
    for _, row in gdf.iterrows():
        ctry = normalize_country(row.get("admin"))
        k = (ctry, _norm_admin(row.get("name")))
        if k in want:
            out[k] = _variants(row)
    return out


def _alias_index(keys: set) -> dict:
    try:
        return _alias_index_cached(tuple(sorted(keys)))
    except Exception:
        return {}


def footprint_summary(footprint: dict) -> str:
    """One-line human-readable footprint, for workbook/diagnostic display."""
    if not footprint or not footprint.get("admin1"):
        return ""
    disp = footprint.get("admin1_display", {})
    ordered = sorted(footprint["admin1"].items(), key=lambda kv: -kv[1])
    return "; ".join(f"{k[0].title()}/{disp.get(k) or k[1].title()}" for k, _ in ordered)
