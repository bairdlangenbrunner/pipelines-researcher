#!/usr/bin/env python3
"""Pre-delivery checks on a discovery run's merged staged_new.json (after merge_discovery_shards.py).

    python scripts/check_discovery_staged.py --staging <run dir> [--staging <run dir> ...] [--min-km 25]

Per new_row: length floor on a sourced length, cost scale (full currency units), bare cost-units
code, length/capacity units not numeric, owner names in the ownership team's style, no GEM or
banned host in any [ref], and no value without its [ref]. Across all the runs given: two new_rows
that name the same project (cross-slice duplicates). Prints one line per finding; exit 1 if any.
"""
import argparse, json, re, sys, os
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from url_verifier import BLOCKLIST_HOSTS, GEM_HOSTS  # noqa: E402
from merge_qc import bad_cost_units  # noqa: E402

TO_KM = {"km": 1.0, "mi": 1.609344, "miles": 1.609344, "mile": 1.609344, "m": 0.001}
VALUE_REF = {"Capacity": ("Capacity [ref]",), "LengthKnown": ("Length [ref]", "LengthKnown [ref]"),
             "Diameter": ("Diameter [ref]",)}  # the sheet column is Length [ref]; the builder maps LengthKnown [ref] onto it


def owner_style(name):
    try:
        from entity_style import style
        return style(name)
    except Exception:
        return None


def norm(s):
    s = re.sub(r"\b(project|pipeline|gas|natural|expansion|the|lateral|llc|inc)\b", " ", (s or "").lower())
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def num(v):
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return None


def check(cand, min_km):
    v, refs, why = cand.get("values") or {}, cand.get("refs") or {}, []
    km = num(v.get("LengthKnown"))
    unit = str(v.get("LengthKnownUnits", "")).strip().lower()
    if km is None or unit not in TO_KM:
        why.append(f"no sourced length ({v.get('LengthKnown')!r} {v.get('LengthKnownUnits')!r})")
    elif km * TO_KM[unit] < min_km:
        why.append(f"length {km:g} {unit} is under {min_km} km")
    for c in ("SegmentCost", "ProjectLevelCost"):
        n = num(v.get(c)) if v.get(c) not in (None, "") else None
        if n is not None and n < 100_000 and str(v.get(c + "Units", "USD")).upper() in ("USD", ""):
            why.append(f"{c} {v.get(c)} looks unscaled (full currency units, EIA says millions)")
    for c, u in bad_cost_units(v).items():
        why.append(f"{c} {u!r} is not a bare currency code")
    for c in ("LengthKnownUnits", "CapacityUnits"):
        if v.get(c) not in (None, "") and num(v.get(c)) is not None:
            why.append(f"{c} is numeric ({v.get(c)!r})")
    for c, val in v.items():
        if re.fullmatch(r"Owner\d*", c) and val:
            for part in str(val).split(";"):
                name = re.sub(r"\s*\[[^\]]*\]\s*$", "", part).strip()
                st = owner_style(name) if name else None
                if st is not None and st.changed:
                    why.append(f"{c} {name!r} -> team style {st.styled!r}")
    for col, urls in refs.items():
        for u in urls or []:
            host = urlparse(u).netloc.lower()
            if any(h in host for h in GEM_HOSTS) or any(h in host for h in BLOCKLIST_HOSTS):
                why.append(f"{col} cites a GEM/banned host: {u}")
    for c, rc in VALUE_REF.items():
        if v.get(c) not in (None, "") and not any(refs.get(k) for k in rc):
            why.append(f"{c} has no {rc[0]}")
    return why


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", action="append", required=True)
    ap.add_argument("--min-km", type=float, default=25.0)
    a = ap.parse_args()
    bad, seen = 0, {}
    for stg in a.staging:
        d = json.load(open(Path(stg) / "staged_new.json"))
        tag = Path(stg).name
        for c in d["candidates"]:
            if c.get("class") != "new_row":
                continue
            v = c.get("values") or {}
            for w in check(c, a.min_km):
                print(f"{tag}\t{c['slug']}\t{w}")
                bad += 1
            key = norm(f"{v.get('PipelineName', '')} {v.get('SegmentName', '')}") or norm(c.get("name"))
            seen.setdefault(key, []).append(f"{tag}:{c['slug']}")
    for key, where in seen.items():
        if len(where) > 1:
            print(f"DUPLICATE\t{key!r}\t{', '.join(where)}")
            bad += 1
    print(f"# {bad} finding(s)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
