"""Match GEM US gas rows to EIA's Natural Gas Pipeline Projects workbook (every release) and compare values.

EIA's workbook is project-level (a new line, an expansion, a lateral), with capacity, cost, miles,
diameter, in-service year, status and FERC docket — and 29 releases (May 2018 -> Aug 2026) give each
project a status history. Run `python sources/eia_pipeline_projects/prepare.py` first.

Matching is by FERC docket (strong: dockets are harvested from every text/[ref] cell of the GEM row),
then by name (PipelineName / SegmentName / OtherEnglishNames) with operator and state overlap as
support. A match is a CANDIDATE: an operating mainline legitimately matches many of its own
expansion projects, so value comparisons run only for docket or strong-name matches, and a
researcher still confirms the pairing before citing it.

usage:
  python scripts/eia_crosswalk.py --csv data/GGIT_gas_snapshot_<d>.csv --out <dir> \
      [--ops data/GEM_operators_owners_snapshot_<d>.csv] [--pids @file|P1,P2] [--md-dir <dir>]

writes <out>/eia_crosswalk.json, <out>/eia_crosswalk_disagreements.csv, and (with --md-dir) one
<PID>.md prompt block per row that has any candidate.
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

import pandas as pd
from rapidfuzz import fuzz

sys.path.insert(0, str(Path(__file__).resolve().parent))
from normalize import gem_diameter_set, parse_diameter_set, parse_number  # noqa: E402

SRC = Path(__file__).resolve().parent.parent / "sources" / "eia_pipeline_projects"
BASE_URL = "https://www.eia.gov/naturalgas/pipelines/"

STATES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}
_GENERIC = {"pipeline", "pipelines", "project", "projects", "natural", "gas", "system", "co",
            "company", "llc", "lp", "l", "p", "inc", "the", "of", "and", "transmission", "line"}
_DOCKET = re.compile(r"\b(CP|PF|RP|RM|PR)\s?(\d{2})-(\d{1,4})\b", re.I)
# EIA status -> GEM status. Order matters: "Approved/On Hold" is on hold, not approved.
# "Part Completed" is deliberately unmapped: which segment is in service is a per-row read.
_STATUS = [("cancel", "cancelled"), ("withdr", "cancelled"), ("terminat", "cancelled"),
           ("denied", "cancelled"), ("on hold", "shelved"), ("suspend", "shelved"),
           ("shelv", "shelved"), ("defer", "shelved"), ("part complet", ""), ("complet", "operating"),
           ("in service", "operating"), ("construct", "construction"), ("approv", "proposed"),
           ("appl", "proposed"), ("announc", "proposed"), ("propos", "proposed"),
           ("plann", "proposed"), ("pre-fil", "proposed"), ("prefil", "proposed")]


_ROMAN = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6"}
# words that never identify a project on their own ("Phase I" alone matches every Phase I in EIA)
_WEAK = {"phase", "phases", "expansion", "project", "lateral", "loop", "looping", "extension",
         "upgrade", "replacement", "segment", "mainline", "header", "interconnect"}


def toks(s) -> str:
    t = re.sub(r"[^a-z0-9]+", " ", str(s).lower()).split()
    return " ".join(_ROMAN.get(w, w) for w in t if w not in _GENERIC)


def distinctive(n: str) -> bool:
    return any(w not in _WEAK and not w.isdigit() for w in n.split())


def phases(s) -> set:
    return {int(_ROMAN.get(p, p)) for p in re.findall(r"phase\s*([ivx]+|\d+)\b", str(s).lower())
            if _ROMAN.get(p, p).isdigit()}


def eia_status(s) -> str:
    s = str(s).lower()
    return next((g for k, g in _STATUS if k in s), "")


def dockets(text) -> set:
    return {f"{a.upper()}{b}-{int(c)}" for a, b, c in _DOCKET.findall(str(text))}


def num(v):
    try:
        return parse_number(v)
    except Exception:
        return None


def gem_capacity_mmcfd(row):
    v, u = num(row["Capacity"]), str(row["CapacityUnits"]).strip().lower()
    if v is None:
        return None
    return {"mmcf/d": v, "mcf/d": v / 1000, "bcf/d": v * 1000, "bcm/y": v * 96.75,
            "dth/d": v / 1037, "mmbtu/d": v / 1037}.get(u)  # Dth ~ 1.037 Mcf; approximate


def gem_miles(row):
    v, u = num(row["LengthKnown"]), str(row["LengthKnownUnits"]).strip().lower()
    if v is None:
        return None
    return v if u == "mi" else v / 1.609344 if u == "km" else None


def gem_cost_musd(row):
    for c, cu in (("SegmentCost", "SegmentCostUnits"), ("ProjectLevelCost", "ProjectLevelCostUnits")):
        v = num(row[c])
        if v is not None and str(row[cu]).strip().upper() == "USD":
            return v / 1e6, c
    return None, ""


def rel(a, b):
    return abs(a - b) / max(abs(a), abs(b), 1e-9)


def load_pids(spec):
    if not spec:
        return None
    if spec.startswith("@"):
        return {l.strip() for l in open(spec[1:]) if l.strip() and not l.startswith("#")}
    return {p.strip() for p in spec.split(",") if p.strip()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--ops")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pids")
    ap.add_argument("--md-dir")
    a = ap.parse_args()

    latest = pd.read_csv(SRC / "data" / "eia_projects_latest.csv", keep_default_na=False,
                         na_values=[], dtype=str)
    vint = pd.read_csv(SRC / "raw" / "vintages.csv", dtype=str)
    releases = sorted(r for r in vint["release"] if r != "current")
    latest["_tok"] = latest["project_name"].map(toks)
    latest["_op"] = latest["pipeline_operator_name"].map(toks)
    latest["_dk"] = latest["docket_number"].map(dockets)
    latest["_st"] = latest["state_s"].map(lambda s: {x.strip().upper() for x in re.split(r"[,;/ ]+", str(s)) if x.strip()})
    eia = latest.to_dict("records")

    df = pd.read_csv(a.csv, header=2, low_memory=False, keep_default_na=False, na_values=[])
    df = df[df["CountriesOrAreas"].str.contains("United States") & (df["Status"] != "N/A")]
    want = load_pids(a.pids)
    if want:
        df = df[df["ProjectID"].isin(want)]
    ops = {}
    if a.ops:
        o = pd.read_csv(a.ops, header=1, low_memory=False, keep_default_na=False, na_values=[])
        ops = dict(zip(o["ProjectID"], o["Operator"]))

    out_rows, disagreements = {}, []
    for _, r in df.iterrows():
        pid = r["ProjectID"]
        raw = [r["PipelineName"], r["SegmentName"], f"{r['PipelineName']} {r['SegmentName']}"]
        raw += re.split(r"[;,]", str(r["OtherEnglishNames"]))
        names = [n for n in dict.fromkeys(toks(n) for n in raw) if distinctive(n)]
        gph = phases(" ".join(raw[:2]))
        operator = " ".join(filter(None, [ops.get(pid, ""), r["Owner"], r["Parent"]]))
        op_t = toks(operator)
        st = {STATES.get(str(r[c]).strip(), "") for c in ("StartState/Province", "EndState/Province")} - {""}
        dk = set().union(*(dockets(v) for v in r.values if isinstance(v, str)))
        yr = num(r["StartYear1"])

        cands = []
        for i, e in enumerate(eia):
            dk_hit = bool(dk & e["_dk"])
            ns = max((fuzz.token_set_ratio(n, e["_tok"]) for n in names), default=0) if e["_tok"] else 0
            if not dk_hit and ns < 75:
                continue
            # token_set scores 100 whenever one name's tokens are a subset of the other's (a mainline
            # vs each of its expansions); token_sort needs the names to be near-equal both ways.
            ss = max((fuzz.token_sort_ratio(n, e["_tok"]) for n in names), default=0) if e["_tok"] else 0
            os_ = fuzz.token_set_ratio(op_t, e["_op"]) if op_t and e["_op"] else 0
            so = bool(st & e["_st"])
            eph = phases(e["project_name"])
            ph_ok = bool(gph and eph and gph & eph)
            ph_clash = bool(gph and eph and not gph & eph)
            related = ns >= 88 and (so or os_ >= 70)
            if dk_hit:
                tier = "docket"
            elif related and ss >= 75 and not ph_clash:
                tier = "strong"
            elif related:
                tier = "related"
            elif ns >= 75 and so and os_ >= 60 and not ph_clash:
                tier = "possible"
            else:
                continue
            score = (ns + 0.5 * ss + 0.3 * os_ + (10 if so else 0) + (15 if ph_ok else 0)
                     + (100 if dk_hit else 0))
            cands.append((tier, score, i, ns, os_, so))
        rank = {"docket": 0, "strong": 1, "related": 2, "possible": 3}
        cands.sort(key=lambda c: (rank[c[0]], -c[1]))
        cands = cands[:6]
        if not cands:
            continue

        rec_c, comps = [], []
        for tier, score, i, ns, os_, so in cands:
            e = eia[i]
            c = {"tier": tier, "name_score": round(ns), "operator_score": round(os_), "state_overlap": so,
                 "project_key": e["project_key"], "project_name": e["project_name"],
                 "operator": e["pipeline_operator_name"], "project_type": e["project_type"],
                 "status": e["status"], "status_history": e["status_history"],
                 "year_in_service": e["year_in_service_date"], "year_in_service_history": e["year_in_service_date_history"],
                 "states": e["state_s"], "miles": e["miles"], "capacity_mmcfd": e["additional_capacity_mmcf_d"],
                 "diameter_in": e["pipeline_diameter_inches"], "cost_musd": e["cost_millions"],
                 "docket": e["docket_number"], "first_release": e["first_release"],
                 "last_release": e["last_release"], "cite_url": BASE_URL + e["last_file"],
                 "sheet": e["last_sheet"], "excel_row": e["last_excel_row"], "notes": e["notes_latest"][:400]}
            rec_c.append(c)
        best = next((c for c in rec_c if c["tier"] in ("docket", "strong")), None)
        if best:
            def add(field, gem, eia, verdict):
                comps.append({"field": field, "gem": gem, "eia": eia, "verdict": verdict,
                              "eia_project": best["project_name"], "eia_release": best["last_release"],
                              "cite_url": best["cite_url"], "match_tier": best["tier"]})
            g, e_ = gem_capacity_mmcfd(r), num(best["capacity_mmcfd"])
            if e_ is not None:
                add("Capacity (MMcf/d)", g, e_, "missing_on_sheet" if g is None else
                    "agree" if rel(g, e_) <= 0.10 else "differs")
            g, e_ = gem_miles(r), num(best["miles"])
            if e_ is not None and e_ > 0:
                add("Length (mi)", g, e_, "missing_on_sheet" if g is None else
                    "agree" if rel(g, e_) <= 0.10 or abs(g - e_) <= 1 else "differs")
            gd, ed = gem_diameter_set(r), parse_diameter_set(best["diameter_in"])
            if ed:
                add("Diameter (in)", gd, ed, "missing_on_sheet" if not gd else
                    "agree" if set(gd) & set(ed) else "differs")
            (g, gcol), e_ = gem_cost_musd(r), num(best["cost_musd"])
            if e_ is not None and e_ > 0:
                add(f"{gcol or 'SegmentCost'} (USD million)", g, e_, "missing_on_sheet" if g is None else
                    "agree" if rel(g, e_) <= 0.15 else "differs")
            e_ = num(best["year_in_service"])
            if e_ is not None:
                add("StartYear1 vs EIA in-service year", yr, int(e_), "missing_on_sheet" if yr is None else
                    "agree" if int(yr) == int(e_) else "differs")
            es = eia_status(best["status"])
            if es:
                add("Status", r["Status"], f"{best['status']} (= {es})",
                    "agree" if es == r["Status"] else "differs")
            for c in comps:
                if c["verdict"] != "agree":
                    disagreements.append({"ProjectID": pid, "PipelineName": r["PipelineName"],
                                          "SegmentName": r["SegmentName"], **c})
        out_rows[pid] = {"pipeline": r["PipelineName"], "segment": r["SegmentName"],
                         "gem_dockets": sorted(dk), "candidates": rec_c, "compare": comps}

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"snapshot": a.csv, "releases": releases, "generated": dt.datetime.now().isoformat(timespec="seconds"),
            "rows_in_scope": int(len(df)), "rows_with_candidates": len(out_rows)}
    (out / "eia_crosswalk.json").write_text(json.dumps({"meta": meta, "rows": out_rows}, indent=1, default=str))
    with open(out / "eia_crosswalk_disagreements.csv", "w", newline="") as fh:
        if disagreements:
            w = csv.DictWriter(fh, fieldnames=list(disagreements[0]))
            w.writeheader()
            w.writerows(disagreements)
    tiers = {}
    for v in out_rows.values():
        t = v["candidates"][0]["tier"]
        tiers[t] = tiers.get(t, 0) + 1
    print(f"{len(df)} rows in scope; {len(out_rows)} with EIA candidates (best tier: {tiers}); "
          f"{len(disagreements)} non-agree comparisons -> {out}")

    if a.md_dir:
        md = Path(a.md_dir)
        md.mkdir(parents=True, exist_ok=True)
        for pid, v in out_rows.items():
            (md / f"{pid}.md").write_text(render_md(pid, v, releases))


def render_md(pid, v, releases) -> str:
    L = [f"## EIA Natural Gas Pipeline Projects — pre-matched candidates for {pid} "
         f"({len(releases)} releases, {releases[0]} .. {releases[-1]})",
         "",
         "The orchestrator downloaded EVERY EIA release into `sources/eia_pipeline_projects/raw/` "
         "(`raw/vintages.csv` maps release -> file -> URL). Read them locally — do not re-download. "
         "`sources/eia_pipeline_projects/data/eia_projects_long.csv` has each project's row in every "
         "release (filter on `project_key`); use it for status / in-service / cost / capacity HISTORY "
         "(the first release showing a project Completed or Cancelled bounds that year).",
         "",
         "Tiers: `docket` = same FERC docket; `strong` = near-identical name + operator/state; "
         "`related` = the EIA project name CONTAINS this row's name (typically an expansion/lateral of "
         "the same system — use it for context and history, never compare its values to this row "
         "without checking scope); `possible` = weaker name match with state + operator support. "
         "These are CANDIDATES from docket / name / operator / state matching. Confirm each is really "
         "this row's project (an operating mainline matches its own expansions; an expansion's capacity "
         "is INCREMENTAL, not the line's total) before using it. All EIA releases are ONE origin. Cite the "
         "SPECIFIC dated release whose row states the value (the `cite_url` below, or an older release's "
         "file for a historical value), name sheet + Excel row in `note`, and run url_verifier with "
         "`--name` carrying the EIA project name as an alias. A `differs` line below is OWED a finding: a "
         "spec concern with `contested` and the value your sources support, or a record of why EIA is the "
         "wrong comparison (different scope/phase). A `missing_on_sheet` line is a fill candidate.",
         ""]
    if v["gem_dockets"]:
        L.append(f"Dockets found in the GEM row: {', '.join(v['gem_dockets'])}")
        L.append("")
    for c in v["candidates"]:
        L.append(f"- **[{c['tier']}]** {c['project_name']} — {c['operator']} ({c['project_type']}); "
                 f"status {c['status']} [{c['status_history']}]; in-service {c['year_in_service'] or '-'}; "
                 f"{c['states']}; {c['miles'] or '-'} mi; {c['diameter_in'] or '-'} in; "
                 f"{c['capacity_mmcfd'] or '-'} MMcf/d; ${c['cost_musd'] or '-'}M; docket {c['docket'] or '-'}; "
                 f"releases {c['first_release']}..{c['last_release']}; cite {c['cite_url']} "
                 f"sheet '{c['sheet']}' row {c['excel_row']}"
                 + (f"\n  notes: {c['notes']}" if c["notes"] else ""))
    if v["compare"]:
        L += ["", "Comparison against the best docket/strong candidate:"]
        for c in v["compare"]:
            L.append(f"- {c['field']}: sheet {c['gem']} vs EIA {c['eia']} -> **{c['verdict']}**")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
