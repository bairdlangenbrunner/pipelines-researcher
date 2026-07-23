#!/usr/bin/env python3
"""Sheet <-> gem.wiki alignment QC (Leg 1 of the wiki/route QC workflow).

For each in-scope tracker row, fetch its `Wiki` page (rendered HTML, cache-first),
parse the displayed data (the "Project details"/"Pipeline details" bullet list +
the Location/intro prose), and diff it against the backend sheet's values. The
sheet is usually the more current side, so a mismatch normally means the WIKI
needs an edit — but the staged-packet join can redirect that (the sheet cell
itself may have a staged pending correction), and a blank sheet cell beside a
filled wiki value flags the SHEET instead.

Page shapes handled (2026-07-15 Egypt characterization, wiki_characterization.md):
"Project details" or "Pipeline details" heading; one shared <ul> or one <ul> per
<li>; values inside the <b> tag; multi-segment pages with per-<h3> bullet blocks
(set-typed fields union across segments; differing scalars -> info records).

Output: <staging>/wiki_alignment.json, records per the WIKIDIFF class
(ref_col "__WIKIDIFF__") documented in docs/reference/staged_json_schema.md.
class_out: WIKI_UPDATE | WIKI_STALE_VS_STAGED | SHEET_SUSPECT | UNPARSED.

Standing rule 1 applies: gem.wiki is VISITED here, never cited — nothing this
script emits goes in a [ref] column.

Usage:
  python scripts/wiki_alignment.py --csv data/GGIT_gas_snapshot_<date>.csv \
      --owners-csv data/GEM_operators_owners_snapshot_<date>.csv \
      --country Egypt --staging batches/egypt-gas/staging/qc/ \
      [--pids P0462,P0477] [--refetch] [--staged-dir <dir> ...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import (  # noqa: E402
    GEM_STATUSES, capacity_to_bcmy, normalize_name, parse_diameter_set,
    parse_length_km, parse_number, parse_owners,
)
from staged_store import annotate, discover_staging_dirs, load_staged_context, pending_for  # noqa: E402
from url_verifier import _MIN_INTERVAL, _UA  # noqa: E402

WIKIDIFF_REF = "__WIKIDIFF__"

# details-section heading variants seen in the 2026-07-15 characterization pass
_DETAILS_HEADINGS = re.compile(r"^(project|pipeline)\s+details$", re.I)

# sheet sentinels that mean "checked, none/unknown" — never pushed to the wiki
_SENTINELS = {"--", "—", "unknown", "n/a", "tbd", "unknown [unknown %]"}

# fields whose multi-segment wiki values union cleanly (sets), vs scalars
_UNION_KEYS = {"diameter", "owner", "operator", "parent company"}

# entity-name suffix tokens ignored in comparisons ('Chevron Corp' == 'Chevron')
_ENTITY_SUFFIX = {"co", "company", "corp", "corporation", "ltd", "limited",
                  "llc", "plc", "inc", "sa", "sae", "spa", "gmbh"}

# prose status phrases -> GEM vocab
_PROSE_STATUS = [
    (r"under\s+construction", "construction"),
    (r"\boperating\b|\boperational\b", "operating"),
    (r"\bproposed\b", "proposed"),
    (r"\bconstruction\b", "construction"),
    (r"\bshelved\b", "shelved"),
    (r"\bcancell?ed\b", "cancelled"),
    (r"\bidle\b", "idle"),
    (r"\bmothballed\b", "mothballed"),
    (r"\bretired\b", "retired"),
]


def _s(v) -> str:
    """NaN/None-safe cell -> stripped string ('' for missing)."""
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s.lower() in ("nan", "none") else s


def _blankish(v) -> bool:
    """Blank or a deliberate sheet sentinel ('--', 'unknown', ...)."""
    s = _s(v).lower()
    return not s or s in _SENTINELS


# ---------------------------------------------------------------- fetch/parse

def fetch_page(url: str, cache_dir: Path, pid: str, refetch: bool = False) -> dict:
    """Cache-first fetch. Returns {ok, html?, reason?}. Politeness handled by caller."""
    cached = cache_dir / f"{pid}.html"
    if cached.exists() and not refetch:
        return {"ok": True, "html": cached.read_text(), "cached": True}
    if not (url or "").lower().startswith("http"):
        return {"ok": False, "reason": "no wiki URL", "cached": False}
    try:
        import requests
        r = requests.get(url, timeout=25, headers={"User-Agent": _UA})
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "reason": f"request failed: {type(e).__name__}", "cached": False}
    if r.status_code != 200:
        return {"ok": False, "reason": f"HTTP {r.status_code}", "cached": False}
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached.write_text(r.text)
    return {"ok": True, "html": r.text, "cached": False}


def _prose_status(text: str) -> str:
    low = (text or "").lower()
    for pat, status in _PROSE_STATUS:
        if re.search(pat, low):
            return status
    return ""


def parse_wiki_page(html: str) -> dict:
    """-> {ok, bullets{key_lc: value}, ambiguous{key_lc: [values]}, intro,
    location, statuses{place: status}, n_sections}."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one("#mw-content-text")
    if content is None:
        return {"ok": False, "reason": "no #mw-content-text"}
    for sup in content.find_all("sup"):
        sup.decompose()

    out = {"ok": True, "bullets": {}, "ambiguous": {}, "union_keys": set(),
           "intro": "", "location": "", "statuses": {}, "n_sections": 0}
    p = content.find("p")
    if p:
        out["intro"] = " ".join(p.get_text(" ", strip=True).split())

    # details bullets: every <ul> between the details <h2> and the next <h2>,
    # grouped by intervening <h3> (multi-segment pages)
    details_h2 = None
    for h2 in content.find_all("h2"):
        if _DETAILS_HEADINGS.match(h2.get_text(strip=True)):
            details_h2 = h2
            break
    sections: list[dict] = []
    if details_h2 is not None:
        cur: dict = {}
        sections.append(cur)
        node = details_h2.find_next_sibling()
        while node is not None and node.name != "h2":
            if node.name == "h3":
                cur = {}
                sections.append(cur)
            elif node.name == "ul":
                for li in node.find_all("li", recursive=False):
                    b = li.find("b")
                    if b is None:
                        continue
                    bold = " ".join(b.get_text(" ", strip=True).split())
                    b.extract()
                    rest = " ".join(li.get_text(" ", strip=True).split()).lstrip(": ").strip()
                    if not rest and ":" in bold:
                        key, rest = bold.split(":", 1)
                    else:
                        key = bold
                    key = key.rstrip(":").strip().lower()
                    if key:
                        cur[key] = rest.strip()
            node = node.find_next_sibling()
    sections = [s for s in sections if s]
    out["n_sections"] = len(sections)

    # merge sections: agreement collapses; set-typed keys union; scalars -> ambiguous
    keys = {k for s in sections for k in s}
    for key in keys:
        vals = [s[key] for s in sections if s.get(key, "").strip()]
        distinct = sorted(set(vals))
        if len(distinct) <= 1:
            out["bullets"][key] = distinct[0] if distinct else ""
        elif key in _UNION_KEYS:
            out["bullets"][key] = "; ".join(distinct)
            out["union_keys"].add(key)
        else:
            out["ambiguous"][key] = distinct

    loc_span = content.find(id="Location")
    if loc_span is not None:
        lp = loc_span.find_parent(["h2", "h3"])
        p = lp.find_next_sibling("p") if lp is not None else None
        if p:
            out["location"] = " ".join(p.get_text(" ", strip=True).split())

    for place, text in (("details", out["bullets"].get("status", "")),
                        ("intro", out["intro"]), ("location", out["location"])):
        s = _prose_status(text)
        if s:
            out["statuses"][place] = s
    return out


# ---------------------------------------------------------------- comparators
# each returns (match: bool | None, sheet_norm, wiki_norm); None = incomparable

def _cmp_status(sheet_row: dict, wiki_val: str, _oo: dict):
    sv = _s(sheet_row.get("Status")).lower()
    wv = _prose_status(wiki_val) or wiki_val.strip().lower()
    if not sv or not wv:
        return None, sv, wv
    return (sv == wv and wv in GEM_STATUSES), sv, wv


def _cmp_capacity(sheet_row: dict, wiki_val: str, _oo: dict):
    wiki_rng = capacity_to_bcmy(wiki_val)
    sheet_bcmy = parse_number(_s(sheet_row.get("CapacityBcm/y")))
    if sheet_bcmy is None:
        rng = capacity_to_bcmy(_s(sheet_row.get("Capacity")), _s(sheet_row.get("CapacityUnits")))
        sheet_bcmy = rng[0] if rng else None
    sn = f"{sheet_bcmy:g} bcm/y" if sheet_bcmy is not None else ""
    wn = (f"{wiki_rng[0]:g}–{wiki_rng[1]:g} bcm/y" if wiki_rng and wiki_rng[0] != wiki_rng[1]
          else f"{wiki_rng[0]:g} bcm/y" if wiki_rng else "")
    if sheet_bcmy is None or wiki_rng is None:
        return None, sn, wn
    lo, hi = wiki_rng
    return (lo * 0.95 <= sheet_bcmy <= hi * 1.05), sn, wn


def _cmp_length(sheet_row: dict, wiki_val: str, _oo: dict):
    units = "mi" if re.search(r"\bmiles?\b", wiki_val, re.I) else "km"
    wkm = parse_length_km(wiki_val, units)
    skm = None
    for col in ("LengthKnownKm", "LengthMergedKm"):
        skm = parse_number(_s(sheet_row.get(col)))
        if skm is not None:
            break
    sn = f"{skm:g} km" if skm is not None else ""
    wn = f"{wkm:g} km" if wkm is not None else ""
    if skm is None or wkm is None:
        return None, sn, wn
    return (abs(skm - wkm) <= max(2.0, 0.10 * max(skm, wkm))), sn, wn


def _cmp_diameter(sheet_row: dict, wiki_val: str, _oo: dict):
    wunits = "mm" if re.search(r"\bmm\b", wiki_val, re.I) else "in"
    wset = parse_diameter_set(wiki_val, wunits)
    sunits = _s(sheet_row.get("DiameterUnits")).lower() or "in"
    sset = parse_diameter_set(_s(sheet_row.get("Diameter")), "mm" if sunits.startswith("mm") else "in")
    sn = ", ".join(f"{v:g}" for v in sset) + (" in" if sset else "")
    wn = ", ".join(f"{v:g}" for v in wset) + (" in" if wset else "")
    if not sset or not wset:
        return None, sn, wn
    return (set(sset) == set(wset)), sn, wn


def _cmp_start_year(sheet_row: dict, wiki_val: str, _oo: dict):
    wyears = {int(m) for m in re.findall(r"(?:19|20)\d{2}", wiki_val)}
    syears = set()
    for col in ("StartYear1", "StartYear2", "StartYear3"):
        m = re.search(r"(?:19|20)\d{2}", _s(sheet_row.get(col)))
        if m:
            syears.add(int(m.group()))
    sn = ", ".join(str(y) for y in sorted(syears))
    wn = ", ".join(str(y) for y in sorted(wyears))
    if not syears or not wyears:
        return None, sn, wn
    return (syears == wyears), sn, wn


def _entity_set(raw: str) -> set[str]:
    """Entity names -> comparison set: parentheticals stripped, names normalized,
    corporate suffix tokens dropped, 'unknown' sentinels removed."""
    text = re.sub(r"\([^)]*\)", " ", _s(raw))          # (28%) / (Israel) / (formerly ...)
    out = set()
    for name in parse_owners(text):
        toks = [t for t in normalize_name(name).split() if t not in _ENTITY_SUFFIX]
        norm = " ".join(toks)
        if norm and norm != "unknown":
            out.add(norm)
    return out


def _cmp_entities(col: str):
    def cmp(sheet_row: dict, wiki_val: str, oo: dict):
        raw_sheet = _s(oo.get(col, "")) if col == "Operator" else _s(sheet_row.get(col))
        if col == "Owner" and not raw_sheet:
            raw_sheet = _s(oo.get("Owner", ""))
        sset, wset = _entity_set(raw_sheet), _entity_set(wiki_val)
        sn, wn = "; ".join(sorted(sset)), "; ".join(sorted(wset))
        if not sset or not wset:
            return None, sn, wn
        return (sset == wset), sn, wn
    return cmp


# wiki key (lc) -> (sheet field label, sheet raw column, comparator, severity)
FIELD_MAP: dict[str, tuple[str, str, object, str]] = {
    "status": ("Status", "Status", _cmp_status, "flag"),
    "capacity": ("Capacity", "Capacity", _cmp_capacity, "flag"),
    "current capacity": ("Capacity", "Capacity", _cmp_capacity, "flag"),
    "length": ("LengthKnownKm", "LengthKnown", _cmp_length, "flag"),
    "diameter": ("Diameter", "Diameter", _cmp_diameter, "flag"),
    "start year": ("StartYear1", "StartYear1", _cmp_start_year, "flag"),
    "operator": ("Operator", "Operator", _cmp_entities("Operator"), "flag"),
    "owner": ("Owner", "Owner", _cmp_entities("Owner"), "flag"),
    "parent company": ("Parent", "Parent", _cmp_entities("Parent"), "flag"),
}


# ------------------------------------------------------------------- records

def _base_record(row: dict, field: str, wiki_key: str) -> dict:
    return {
        "project_id": row["ProjectID"], "sheet_row": row["SheetRow"],
        "pipeline_name": _s(row.get("PipelineName")),
        "segment_name": _s(row.get("SegmentName")),
        "wiki": _s(row.get("Wiki")),
        "ref_col": WIKIDIFF_REF, "class_in": "WIKIDIFF",
        "field": field, "wiki_key": wiki_key,
        "sheet_value": "", "sheet_value_norm": "",
        "wiki_value": "", "wiki_value_norm": "",
        "staged_value": "", "staged_source": "", "staged_note": "",
        "action": "", "severity": "flag",
        # common-core so records pass merge/apply tooling untouched
        "value_cols": [], "values": {}, "primary_value_col": None,
        "primary_value": "", "current_ref": "", "proposed_refs": [],
        "verifications": [], "tier": "", "independent": False,
        "source_language": "en", "researcher_notes": "",
    }


def _staged_is_noop(pend: dict, row: dict, raw_col: str, cmp, oo: dict) -> bool:
    """True when the staged 'pending value' equals what the sheet already says
    (a ref-add, not a value change) — then normal wiki-vs-sheet compare applies."""
    staged = _s(pend["value"])
    sheet_raw = _s(row.get(raw_col))
    if staged.lower() == sheet_raw.lower():
        return True
    a, b = parse_number(staged), parse_number(sheet_raw)
    if a is not None and a == b and not re.search(r"[a-df-z]", staged, re.I):
        return True
    m, _, _ = cmp(row, staged, oo)   # field-aware: '36, 32, 30' == sheet {30,32,36}
    return m is True


def compare_row(row: dict, page: dict, oo: dict, ctx: dict) -> list[dict]:
    recs: list[dict] = []
    pid = row["ProjectID"]

    for wiki_key, (field, raw_col, cmp, severity) in FIELD_MAP.items():
        if wiki_key == "capacity" and "current capacity" in page["bullets"]:
            continue  # prefer the more specific key when both exist
        if wiki_key not in page["bullets"]:
            continue
        wiki_val = page["bullets"][wiki_key]
        sheet_raw = _s(oo.get("Operator", "")) if field == "Operator" else _s(row.get(raw_col))

        match, sn, wn = cmp(row, wiki_val, oo)
        wiki_blank = not wiki_val.strip()
        sheet_blank = _blankish(sheet_raw) and not sn

        rec = _base_record(row, field, wiki_key)
        rec["severity"] = severity
        rec["sheet_value"], rec["sheet_value_norm"] = sheet_raw, sn
        rec["wiki_value"], rec["wiki_value_norm"] = wiki_val, wn

        pend = pending_for(ctx, pid, field)
        if pend and not _staged_is_noop(pend, row, raw_col, cmp, oo):
            rec["staged_value"], rec["staged_source"] = pend["value"], pend["source_dir"]
            if _s(pend["value"]).lower() == wn.strip().lower():
                continue  # wiki already matches the staged correction
            rec["class_out"] = "WIKI_STALE_VS_STAGED"
            rec["action"] = (f"after the staged sheet edit is applied, update wiki "
                             f"'{wiki_key}' to {pend['value']} ({pend['source_dir']})")
            recs.append(rec)
            continue
        if sheet_blank and wiki_blank:
            continue
        if sheet_blank and not wiki_blank:
            rec["class_out"] = "SHEET_SUSPECT"
            rec["staged_note"] = annotate(ctx, pid, field=field)
            if sheet_raw:  # a deliberate sentinel, not a hole
                rec["severity"] = "info"
                rec["action"] = (f"sheet {field} is '{sheet_raw}' (deliberate) but wiki shows "
                                 f"'{wiki_val}' — reconcile; verify independently (never cite the wiki)")
            else:
                rec["action"] = (f"sheet {field} is blank but wiki shows '{wiki_val}' — "
                                 f"candidate sheet fill; verify independently (never cite the wiki)")
            recs.append(rec)
            continue
        if wiki_blank and not sheet_blank:
            rec["class_out"] = "WIKI_UPDATE"
            rec["action"] = f"add '{wiki_key}' to wiki: {sn or sheet_raw}"
            recs.append(rec)
            continue
        if match is None or match:
            continue
        if wiki_key in page["union_keys"]:
            # value merged across per-segment sections — the single sheet row may
            # be missing a segment's value; direction is sheet-suspect, not wiki-lags
            rec["class_out"] = "SHEET_SUSPECT"
            rec["staged_note"] = annotate(ctx, pid, field=field)
            rec["action"] = (f"multi-segment wiki page unions '{wiki_key}' to {wn}; sheet has "
                             f"{sn or sheet_raw} — verify whether the sheet row should carry "
                             f"every segment's value (never cite the wiki)")
        else:
            rec["class_out"] = "WIKI_UPDATE"
            rec["action"] = f"update wiki '{wiki_key}' to {sn or sheet_raw}"
        recs.append(rec)

    # multi-segment pages: scalar fields whose per-segment values differ
    for wiki_key, vals in page["ambiguous"].items():
        entry = FIELD_MAP.get(wiki_key)
        if entry is None:
            continue
        field, raw_col, _, _ = entry
        rec = _base_record(row, field, wiki_key)
        rec["severity"] = "info"
        rec["sheet_value"] = _s(row.get(raw_col))
        rec["wiki_value"] = " / ".join(vals)
        rec["class_out"] = "WIKI_UPDATE"
        rec["action"] = (f"multi-segment wiki page shows differing '{wiki_key}' values "
                         f"({rec['wiki_value']}) vs one sheet row — review, don't hard-compare")
        recs.append(rec)

    # internal wiki inconsistency (e.g. intro says construction, details say operating)
    distinct = {v for v in page["statuses"].values() if v}
    if len(distinct) > 1:
        rec = _base_record(row, "Status", "(page-internal)")
        rec["wiki_value"] = "; ".join(f"{k}: {v}" for k, v in sorted(page["statuses"].items()))
        rec["sheet_value"] = _s(row.get("Status"))
        rec["sheet_value_norm"] = rec["sheet_value"]
        rec["wiki_value_norm"] = "; ".join(sorted(distinct))
        rec["class_out"] = "WIKI_UPDATE"
        rec["action"] = (f"wiki page is internally inconsistent about status "
                         f"({rec['wiki_value']}); align every mention to '{rec['sheet_value']}'")
        recs.append(rec)

    # location prose: sheet start/end country never mentioned (info)
    prose = f"{page['location']} {page['intro']}".lower()
    if prose.strip():
        for field, col in (("StartCountryOrArea", "start"), ("EndCountryOrArea", "end")):
            country = _s(row.get(field))
            if country and country.lower() not in prose:
                rec = _base_record(row, field, f"location prose ({col})")
                rec["severity"] = "info"
                rec["sheet_value"] = country
                rec["wiki_value"] = (page["location"] or page["intro"])[:200]
                rec["class_out"] = "WIKI_UPDATE"
                rec["action"] = (f"wiki location prose never mentions the sheet's "
                                 f"{col} country '{country}' — review the page's route description")
                recs.append(rec)
    return recs


# ---------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--owners-csv", required=True)
    ap.add_argument("--country", required=True)
    ap.add_argument("--commodity", default="gas", choices=["gas", "oil"])
    ap.add_argument("--staging", required=True)
    ap.add_argument("--pids", help="comma-separated subset (sample runs)")
    ap.add_argument("--refetch", action="store_true", help="ignore the HTML cache")
    ap.add_argument("--staged-dir", action="append", default=[],
                    help="staging dir(s) with prior packets (repeatable); "
                         "default: auto-discover by country+commodity")
    args = ap.parse_args()

    import pandas as pd
    df = pd.read_csv(args.csv, header=2, low_memory=False)
    df = df[df["PipelineName"].notna()].copy()
    df["SheetRow"] = df.index + 4
    scope = df[df["CountriesOrAreas"].fillna("").str.contains(args.country, case=False)]
    if args.pids:
        keep = {p.strip() for p in args.pids.split(",") if p.strip()}
        scope = scope[scope["ProjectID"].isin(keep)]

    oo_df = pd.read_csv(args.owners_csv, header=1, low_memory=False)
    oo_by_pid: dict[str, dict] = {}
    for _, r in oo_df.iterrows():
        pid = _s(r.get("ProjectID"))
        if pid and pid not in oo_by_pid:
            owners = "; ".join(
                f"{_s(r[f'Owner{i}'])} [{_s(r[f'Owner{i}%'])}]" if _s(r.get(f"Owner{i}%"))
                else _s(r[f"Owner{i}"])
                for i in range(1, 12) if _s(r.get(f"Owner{i}")))
            oo_by_pid[pid] = {"Operator": _s(r.get("Operator")), "Owner": owners}

    staged_dirs = args.staged_dir or discover_staging_dirs(
        args.country, args.commodity, exclude=[args.staging])
    ctx = load_staged_context(staged_dirs)

    staging = Path(args.staging)
    cache_dir = staging / "wiki_html"
    records: list[dict] = []
    n_fetched = 0
    for _, row in scope.iterrows():
        row = row.to_dict()
        pid = row["ProjectID"]
        wiki = _s(row.get("Wiki"))
        if not wiki:
            rec = _base_record(row, "", "")
            rec["class_out"] = "UNPARSED"
            rec["action"] = "row has no Wiki URL — create the wiki page (or fill the Wiki cell)"
            records.append(rec)
            continue
        res = fetch_page(wiki, cache_dir, pid, refetch=args.refetch)
        if not res.get("cached"):
            n_fetched += 1
            time.sleep(_MIN_INTERVAL)
        if not res["ok"]:
            rec = _base_record(row, "", "")
            rec["class_out"] = "UNPARSED"
            rec["action"] = f"wiki fetch failed ({res['reason']}) — review manually"
            records.append(rec)
            continue
        page = parse_wiki_page(res["html"])
        if not page["ok"] or not (page["bullets"] or page["ambiguous"]):
            rec = _base_record(row, "", "")
            rec["class_out"] = "UNPARSED"
            rec["action"] = ("wiki page has no parseable details section "
                             f"({page.get('reason', 'no bullets found')}) — review manually")
            records.append(rec)
            continue
        recs = compare_row(row, page, oo_by_pid.get(pid, {}), ctx)
        records.extend(recs)
        print(f"  {pid}: {len(recs)} record(s)"
              + (f" [{page['n_sections']} sections]" if page["n_sections"] > 1 else ""),
              file=sys.stderr)

    from collections import Counter
    out = {
        "meta": {
            "mode": "wiki_alignment",
            "scope": {"csv": Path(args.csv).name, "owners_csv": Path(args.owners_csv).name,
                      "country": args.country, "rows": int(len(scope))},
            "staged_dirs": ctx["dirs"],
            "n_pages_fetched": n_fetched,
            "class_out_counts": dict(Counter(r["class_out"] for r in records)),
            "severity_counts": dict(Counter(r["severity"] for r in records)),
            "field_counts": dict(Counter(r["field"] for r in records if r["field"])),
        },
        "records": records,
    }
    staging.mkdir(parents=True, exist_ok=True)
    path = staging / "wiki_alignment.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"wrote {path} — {len(records)} records over {len(scope)} rows; "
          f"{out['meta']['class_out_counts']}")


if __name__ == "__main__":
    main()
