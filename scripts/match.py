"""Attribute matching: load GEM rows (segment + synthetic network level) and score
name / endpoint / diameter / length signals against a canonical reference record.

Geometry signals are added separately by route_compare.py; reconcile.py combines
both into the composite confidence.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field

import pandas as pd
from rapidfuzz import fuzz

import normalize as N

# GEM length columns, in preference order (all km)
_LENGTH_COLS = ["LengthKnownKm", "LengthMergedKm", "LengthEstimateKm"]


def load_gem_df(path: str) -> pd.DataFrame:
    """Load a GEM tracker CSV (header at row index 2), drop buffer/blank rows.
    fillna('') is essential: NaN floats are truthy, so `cell or ''` would yield the
    string 'nan' and collapse all blank-grouping segments into one fake network."""
    df = pd.read_csv(path, header=2, low_memory=False, dtype=str).fillna("")
    if "PipelineName" in df.columns:
        df = df[df["PipelineName"].str.strip() != ""]
    return df.reset_index(drop=True)


def _length_km(row) -> float | None:
    for c in _LENGTH_COLS:
        n = N.parse_number(row.get(c))
        if n:
            return n
    return None


@dataclass
class GemRow:
    kind: str                       # 'segment' | 'network'
    project_id: str
    project_ids: list
    pipeline_name: str
    segment_name: str
    network_grouping: str
    name_variants: list             # normalized name strings to match against
    status: str
    owner: str
    diameter_set: list
    length_km: float | None
    start_loc: str                  # normalized
    end_loc: str                    # normalized
    countries: set
    route_accuracy: str
    wiki: str
    diameter_raw: str = ""          # raw GEM Diameter string, for display
    start_raw: str = ""             # raw StartLocation, for display
    end_raw: str = ""               # raw EndLocation, for display
    matched: bool = field(default=False)   # set by reconcile when used as a best match


def _variants(*names) -> list:
    out = []
    for nm in names:
        nn = N.normalize_name(nm)
        if nn and nn not in out:
            out.append(nn)
    return out


def gem_rows_for_country(df: pd.DataFrame, country: str):
    """Return (segments, networks) whose CountriesOrAreas includes `country`."""
    want = N.normalize_country(country)
    mask = df.get("CountriesOrAreas").astype(str).map(lambda s: want in N.split_countries(s))
    segs: list[GemRow] = []
    for _, row in df[mask].iterrows():
        other_names = [o for o in re.split(r";", str(row.get("OtherEnglishNames") or "")) if o.strip()]
        segs.append(GemRow(
            kind="segment",
            project_id=str(row.get("ProjectID") or "").strip(),
            project_ids=[str(row.get("ProjectID") or "").strip()],
            pipeline_name=str(row.get("PipelineName") or "").strip(),
            segment_name=str(row.get("SegmentName") or "").strip(),
            network_grouping=str(row.get("PipelineNetworkGrouping") or "").strip(),
            name_variants=_variants(row.get("PipelineName"), row.get("SegmentName"),
                                    row.get("PipelineNetworkGrouping"), *other_names),
            status=str(row.get("Status") or "").strip().lower(),
            owner=str(row.get("Owner") or "").strip(),
            diameter_set=N.parse_diameter_set(row.get("Diameter")),
            length_km=_length_km(row),
            start_loc=N.normalize_name(row.get("StartLocation")),
            end_loc=N.normalize_name(row.get("EndLocation")),
            countries=set(N.split_countries(row.get("CountriesOrAreas"))),
            route_accuracy=str(row.get("RouteAccuracy") or "").strip(),
            wiki=str(row.get("Wiki") or "").strip(),
            diameter_raw=str(row.get("Diameter") or "").strip(),
            start_raw=str(row.get("StartLocation") or "").strip(),
            end_raw=str(row.get("EndLocation") or "").strip(),
        ))
    return segs, _build_networks(segs)


def _build_networks(segs: list[GemRow]) -> list[GemRow]:
    """Synthetic network rows: segments grouped by PipelineNetworkGrouping (else
    PipelineName) when ≥2 members. A reference trunk that GEM split into segments
    matches the network even when no single segment does."""
    groups: dict[str, list[GemRow]] = defaultdict(list)
    for s in segs:
        groups[s.network_grouping or s.pipeline_name].append(s)
    nets: list[GemRow] = []
    for key, members in groups.items():
        if len(members) < 2:
            continue
        nv: list = []
        kn = N.normalize_name(key)
        if kn:
            nv.append(kn)
        for m in members:
            for v in m.name_variants:
                if v not in nv:
                    nv.append(v)
        lengths = [m.length_km for m in members if m.length_km]
        nets.append(GemRow(
            kind="network",
            project_id="",
            project_ids=[p for m in members for p in m.project_ids],
            pipeline_name=key,
            segment_name="",
            network_grouping=key,
            name_variants=nv,
            status=Counter(m.status for m in members).most_common(1)[0][0],
            owner=members[0].owner,
            diameter_set=sorted({d for m in members for d in m.diameter_set}),
            length_km=sum(lengths) if lengths else None,
            start_loc="",
            end_loc="",
            countries=set().union(*[m.countries for m in members]),
            route_accuracy="",
            wiki=members[0].wiki,
            diameter_raw=", ".join(str(int(d)) if d == int(d) else str(d)
                                   for d in sorted({d for m in members for d in m.diameter_set})),
        ))
    return nets


# --------------------------------------------------------------------------- #
# attribute signals
# --------------------------------------------------------------------------- #
def _name_score(ref_norm: str, variants: list) -> float:
    if not ref_norm or not variants:
        return 0.0
    return round(max(fuzz.token_set_ratio(ref_norm, v) for v in variants) / 100.0, 3)


def _endpoint_score(ref_s, ref_e, gem_s, gem_e):
    if not (gem_s or gem_e):
        return None
    rs, re_ = N.normalize_name(ref_s), N.normalize_name(ref_e)
    if not (rs or re_):
        return None

    def sc(a, b):
        return fuzz.token_set_ratio(a, b) / 100.0 if (a and b) else 0.0

    same = (sc(rs, gem_s) + sc(re_, gem_e)) / 2
    swap = (sc(rs, gem_e) + sc(re_, gem_s)) / 2
    return round(max(same, swap), 3)


def _diameter_score(ref_set, gem_set):
    if not ref_set or not gem_set:
        return None
    rs = {round(x) for x in ref_set}
    gs = {round(x) for x in gem_set}
    if rs <= gs or gs <= rs:
        return 1.0
    union = rs | gs
    return round(len(rs & gs) / len(union), 3) if union else None


def _length_score(a, b):
    if not a or not b:
        return None
    lo, hi = min(a, b), max(a, b)
    return round(lo / hi, 3) if hi > 0 else None


def attribute_signals(ref: dict, gem: GemRow):
    """Return (signals dict, human-readable reason fragments). Absent signals are
    omitted (not zero) so reconcile can renormalize weights over present signals."""
    sig: dict = {}
    reasons: list[str] = []

    sig["s_name"] = _name_score(ref["name_norm"], gem.name_variants)
    reasons.append(f"name {sig['s_name']:.2f}")

    se = _endpoint_score(ref.get("start_loc"), ref.get("end_loc"), gem.start_loc, gem.end_loc)
    if se is not None:
        sig["s_endpoints"] = se
        reasons.append(f"endpoints {se:.2f}")

    sd = _diameter_score(ref.get("diameter_in"), gem.diameter_set)
    if sd is not None:
        sig["s_diameter"] = sd
        reasons.append("diameter " + ("✓" if sd == 1.0 else f"{sd:.2f}"))

    ref_len = ref.get("geodesic_km") or ref.get("length_km")
    sl = _length_score(ref_len, gem.length_km)
    if sl is not None:
        sig["s_length"] = sl
        reasons.append(f"length {sl:.2f}")

    return sig, reasons
