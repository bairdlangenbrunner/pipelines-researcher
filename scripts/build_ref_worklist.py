#!/usr/bin/env python3
"""Reference-sweep step 1: scan a country (optionally sub-country via --province /
--exclude-network-regex, e.g. China's province batches) + tracker scope and emit a worklist of every
ref-bearing data point that needs work — blank `[ref]` cells whose value is filled
(MISSING_REF), filled `[ref]` cells to re-verify (HAS_REF), and — with --owe-fills — blank
VALUE cells that the sweep owes a researched value + paired ref (MISSING_VALUE).

Why MISSING_VALUE exists: without it a blank value cell classifies SKIP and is never owed,
so the `fills` leg only ever filled cells an agent happened to notice (Jiangxi v2 2026-09-02:
571 blank cells skipped, 4 fills staged; MZ's first feedback point was "lots of blank data on
operating projects"). A blank on an operating row is a research gap, not a non-unit. The
default owed set is the spec/date/cost/attribution pairs (see FILL_PAIRS_DEFAULT); a blank
`[ref]` beside a blank value is fine, but a FILLED `[ref]` beside a blank value is an orphan
ref and is flagged `orphan_ref` on the unit (the cited page may hold the value).

Owner/operator refs do NOT live on the tracker tab (it has the Owner/Parent values but no
`[ref]` column). They live on the separate **ProjectID-keyed "Pipeline operators/owners"
tab** (GID 1489950650, header at CSV row index 1), in its `Operator [ref]` / `Owner [ref]`
columns. We join that tab by ProjectID for the in-scope rows and emit real operator/owner
ref units (tab='operators_owners', kind='operator'|'owner') — classified MISSING_REF /
HAS_REF just like tracker units. The tracker's synthetic `kind='owner'` placeholder pair is
dropped here in favour of those.

Tracker pairing comes from ref_pairs.discover_ref_pairs; OO pairing from
discover_owner_ref_pairs (forward walk — the OO `[ref]` PRECEDES its values). With
--verify-existing, every existing ref URL (tracker + OO) is HTTP-checked up front
(deterministic, no agent tokens) so most HAS_REF units pre-classify as live vs dead.

    python scripts/build_ref_worklist.py --tracker oil --country "Saudi Arabia" \
        --verify-existing --out batches/saudi-arabia-oil/staging/ref-sweep/worklist.json

SheetRow = read_csv(header=2) index + 4. We deliberately do NOT use match.load_gem_df
(it reset_index'es, which breaks that mapping) — we replicate its buffer-row drop while
preserving the original index. OO sheet row = read_csv(header=1) index + 3.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import normalize as N  # noqa: E402
import paths  # noqa: E402
from ref_pairs import (  # noqa: E402
    OO_HEADER_INDEX, discover_owner_ref_pairs, discover_ref_pairs,
)
from url_verifier import surface_forms, verify_many  # noqa: E402

_URL_RE = re.compile(r"https?://[^\s<>\"\]]+")
_YEAR_RE = re.compile(r"^(19|20)\d{2}$")

# Ref-column stems whose blank value cells are OWED by the fills leg (`--owe-fills`).
# Chosen as the columns a researcher expects populated on an operating row and that a
# single project document typically states together (approval / EIA / bond prospectus):
# spec, dates, cost, fuel, and the two attribution units on the operators/owners tab.
# Status / Location / PipelineType are effectively never blank on a real row; Route is
# out of scope (geometry lives in the routes repo). Override with --fill-pairs.
FILL_PAIRS_DEFAULT = ("Length", "Capacity", "Diameter", "Start", "Construction",
                      "SegmentCost", "Pressure", "FuelSource", "Proposal",
                      "Operator", "Owner")

# The sheet's own "no value" marker in some raw cells (e.g. Owner `--`). Treated as blank.
_BLANK_MARKERS = {"", "--", "-", "n/a", "na"}


def _blank(v) -> bool:
    return str(v if v is not None else "").strip().lower() in _BLANK_MARKERS


def _ref_stem(ref_col: str) -> str:
    return (ref_col or "").replace("[ref]", "").strip()


def _load_indexed(csv: str) -> pd.DataFrame:
    """Load a GEM tracker (header at row index 2), drop buffer/blank rows, but KEEP the
    original index so SheetRow = index + 4 holds."""
    df = pd.read_csv(csv, header=2, low_memory=False,
                     keep_default_na=False, na_values=[], dtype=str).fillna("")
    if "PipelineName" in df.columns:
        df = df[df["PipelineName"].str.strip() != ""]
    return df


def _load_owners(csv: str) -> tuple[pd.DataFrame, dict]:
    """Load the operators/owners tab (header at row index 1), keep the original index
    (OO sheet row = index + 3), and return (df, {ProjectID -> df-index})."""
    df = pd.read_csv(csv, header=OO_HEADER_INDEX, low_memory=False,
                     keep_default_na=False, na_values=[], dtype=str).fillna("")
    by_pid: dict[str, int] = {}
    if "ProjectID" in df.columns:
        for idx, pid in df["ProjectID"].items():
            pid = str(pid).strip()
            if pid and pid not in by_pid:   # first row wins on the rare dup
                by_pid[pid] = int(idx)
    return df, by_pid


def _owner_units(owners_df: pd.DataFrame, by_pid: dict, scope_ctx: list[dict],
                 fill_pairs: frozenset = frozenset()) -> list[dict]:
    """Emit operator + owner ref units for each in-scope ProjectID by joining the
    operators/owners tab. `scope_ctx` is the per-ProjectID tracker context (name/segment/
    wiki) gathered while walking the tracker, in first-seen order."""
    oo_pairs = discover_owner_ref_pairs(list(owners_df.columns))
    units: list[dict] = []
    for ctx in scope_ctx:
        pid = ctx["project_id"]
        oo_idx = by_pid.get(pid)
        if oo_idx is None:
            continue                      # no operators/owners row for this ProjectID
        oo_row = owners_df.loc[oo_idx]
        oo_sheet_row = int(oo_idx) + 3
        for p in oo_pairs:
            ref_col = p["ref_col"]
            value_cols = p["value_cols"]
            values = {c: str(oo_row.get(c, "")).strip() for c in value_cols
                      if not _blank(oo_row.get(c, ""))}
            current_ref = str(oo_row.get(ref_col, "")).strip()
            klass = _classify(p["kind"], ref_col, bool(values), current_ref,
                              owe_fill=_ref_stem(ref_col) in fill_pairs)
            if klass == "SKIP":
                continue
            primary_col = p["primary_value_col"]
            primary_value = str(oo_row.get(primary_col, "")).strip()
            if not primary_value and values:
                primary_value = next(iter(values.values()))
            units.append({
                "project_id": pid,
                "sheet_row": ctx["sheet_row"],       # tracker row, for cross-reference
                "oo_sheet_row": oo_sheet_row,         # the operators/owners tab row
                "pipeline_name": ctx["pipeline_name"],
                "segment_name": ctx["segment_name"],
                "status": ctx.get("status", ""),
                "wiki": ctx["wiki"],
                "ref_col": ref_col,
                "value_cols": value_cols,
                "primary_value_col": primary_col,
                "values": values,
                "primary_value": primary_value,
                "current_ref": current_ref,
                "class": klass,
                "orphan_ref": klass == "MISSING_VALUE" and bool(current_ref),
                "kind": p["kind"],
                "irregular": p["irregular"],
                "tab": "operators_owners",
                "existing_ref_checks": [],
                "value_checked": False,
            })
    return units


# Trailing punctuation to shave off a captured URL. Includes the ARABIC COMMA (U+060C)
# and semicolon (U+061B) and the closing guillemet, which turn up constantly in Arabic-
# language ref cells and used to ride along into the request as part of the path — a
# live page then 404s and reads as a deletion.
_URL_TRAIL = '.,;:)]}\u060c\u061b\u00bb\u201d\u2019\'"\u0640'


def _extract_urls(cell: str) -> list[str]:
    """Pull http(s) URLs out of a ref cell (may hold several + free text), trimming
    trailing punctuation.

    `[ref]` cells are comma-delimited, and researchers do not always put a space after
    the comma. The URL character class cannot exclude ',' (real URLs contain them), so a
    bare `a.com/x,https://b.com/y` used to capture as ONE fused URL: the request 404s
    even though both pages are live, and — worse — the second URL is never checked at
    all. Split on any comma that is immediately followed by a scheme."""
    out: list[str] = []
    for m in _URL_RE.findall(cell or ""):
        for part in re.split(r",(?=https?://)", m):
            u = part.strip().rstrip(_URL_TRAIL)
            if u and u not in out:
                out.append(u)
    return out


def _numericish(value: str) -> bool:
    """Whether a value is specific enough for a deterministic 'page contains it' check
    (numbers, years). Free-text place names/owners are left to the agent, and so is
    STATUS — see `_is_status` for why it is deliberately NOT in here."""
    v = (value or "").strip()
    if not v:
        return False
    return (N.parse_number(v) is not None) or bool(_YEAR_RE.match(v))


def _is_status(value: str) -> bool:
    """A controlled-vocabulary Status value.

    Status is checked for CONTEXT but never scored as a substring. `url_verifier`'s own
    contract says so: "STATUS is inferable, not literal. Do NOT require the status token
    ('operating', etc.) as a substring ... treat a status `any_of` miss as expected" — a
    page that describes the line carrying gas, an inauguration, or export volumes confirms
    `operating` without ever using the word. Scoring it as a miss marked live, supporting
    refs as problems and inflated every scope's owed set on the status axis (Egypt 2026-08-27:
    65 of 112 re-verification gaps across the two cohorts were status units, and the screen,
    not the source, was what failed)."""
    return (value or "").strip().lower() in N.GEM_STATUSES


def _pid_set(raw: str | None, flag: str) -> set[str] | None:
    """Parse a --*-pids value: a comma list, or @<path> for one-per-line ('#' comments ok).

    The @ prefix is load-bearing — a bare filesystem path parses as a single literal
    ProjectID and silently matches nothing, which reads as 'the filter did nothing'.
    """
    if not raw:
        return None
    if raw.startswith("@"):
        src = Path(raw[1:])
        if not src.exists():
            sys.exit(f"{flag} {raw}: no such file {src}")
        raw = ",".join(ln.split("#", 1)[0] for ln in src.read_text().splitlines())
    elif "/" in raw or raw.endswith(".txt"):
        sys.exit(f"{flag} {raw}: looks like a file path — prefix it with '@' to read PIDs from it")
    pids = {p.strip() for p in raw.replace("\n", ",").split(",") if p.strip()}
    return pids or None


def _classify(kind: str, ref_col, any_value_filled: bool, current_ref: str,
              owe_fill: bool = False) -> str:
    if not any_value_filled:
        # A blank value cell is a research gap when the pair is in the owed-fills set —
        # the agent owes a sourced value + paired ref, or an honest UNRESOLVED fill.
        return "MISSING_VALUE" if (owe_fill and ref_col is not None) else "SKIP"
    if ref_col is None:                      # tracker synthetic owner placeholder (no [ref] col)
        return "MISSING_REF_NO_COLUMN"
    # real [ref] column — including the operators/owners tab's Operator/Owner [ref]
    return "HAS_REF" if current_ref.strip() else "MISSING_REF"


def build(csv: str, country: str | None, statuses: set[str] | None,
          verify_existing: bool, owners_csv: str | None = None,
          province: str | None = None,
          exclude_network_regex: str | None = None,
          exclude_pids: set[str] | None = None,
          include_pids: set[str] | None = None,
          owe_fills: bool = False,
          fill_pairs: frozenset | None = None) -> dict:
    # Which pairs owe a fill when their value cells are blank (empty set = none owed).
    fill_pairs = frozenset(fill_pairs if fill_pairs is not None else FILL_PAIRS_DEFAULT) \
        if owe_fills else frozenset()
    df = _load_indexed(csv)
    # `Status = "N/A"` is an explicit EXCLUSION marker, not a missing value (Baird
    # 2026-09-10): it means the row should not be researched and does not belong in the
    # database. Drop it before every other filter — including before `df_all`, so an
    # `--include-pids` union cannot resurrect one — and note it is NOT the same as a blank
    # Status, which is just an unfilled cell. Read the CSV with `keep_default_na=False` to
    # see these at all: pandas parses the literal string "N/A" as NaN by default, which is
    # how P3162 was reported as a blank-status row. 8 gas / 3 oil rows tracker-wide today
    # (US: gas P3162, oil P3681 + P7378). The exclusion is about RESEARCH TARGETS only —
    # discovery and reconciliation must keep N/A rows in their match roster, or a recorded
    # pipeline comes back as a false Addition.
    if "Status" in df.columns:
        na_mask = df["Status"].map(lambda s: str(s).strip().upper() == "N/A")
        if int(na_mask.sum()):
            print(f"  excluded {int(na_mask.sum())} row(s) tracker-wide with Status = N/A "
                  f"(marked not-for-research)")
            df = df[~na_mask]
    df_all = df
    cols = set(df.columns)
    if country:
        want = N.normalize_country(country)
        df = df[df["CountriesOrAreas"].map(lambda s: want in N.split_countries(s))]
    if exclude_pids:
        # Transit countries share rows: a trunk crossing Uzbekistan AND Kazakhstan is ONE
        # row that both country scopes select. Whichever scope is swept second must skip
        # the rows the first already staged, or two staged records end up pointing at one
        # sheet cell and the last workbook pasted wins silently. Excluding here (rather
        # than post-filtering the worklist) keeps `scope.rows` honest downstream.
        df = df[~df["ProjectID"].map(lambda s: str(s).strip() in exclude_pids)]
    if province:
        # In scope if EITHER terminus sits in a wanted province. Transited provinces
        # don't count — a trunk line crossing the province belongs to its own scope.
        wants = {p.strip().lower() for p in province.split(",") if p.strip()}
        prov_cols = [c for c in ("StartState/Province", "EndState/Province") if c in cols]
        if not prov_cols:
            sys.exit(f"--province given but no Start/EndState/Province columns in {csv}")
        mask = pd.Series(False, index=df.index)
        for c in prov_cols:
            mask |= df[c].map(lambda s: str(s).strip().lower() in wants)
        df = df[mask]
    if exclude_network_regex:
        rx = re.compile(exclude_network_regex)
        if "PipelineNetworkGrouping" in cols:
            df = df[~df["PipelineNetworkGrouping"].map(lambda s: bool(rx.search(str(s))))]
    if statuses:
        df = df[df["Status"].map(lambda s: str(s).strip().lower() in statuses)]
    if include_pids:
        # The mirror of --exclude-pids, and the reason it exists: --province selects on
        # TERMINI, so a national trunk that merely transits the province is invisible to
        # it by design — yet the trunk's parent row is often exactly what the province's
        # branch rows hang off. Named PIDs are unioned back in regardless of province,
        # status or network-regex filters (--exclude-pids still wins, so the two can be
        # combined without the include quietly resurrecting a row another scope staged).
        want = {p for p in include_pids if not (exclude_pids and p in exclude_pids)}
        extra = df_all[df_all["ProjectID"].map(lambda s: str(s).strip() in want)]
        extra = extra[~extra.index.isin(df.index)]
        if not extra.empty:
            df = pd.concat([df, extra]).sort_index()

    # Tracker pairs: drop the synthetic owner placeholder — owner/operator refs come from
    # the operators/owners tab join below (when --owners-csv is supplied).
    pairs = [p for p in discover_ref_pairs(list(df.columns))
             if p["kind"] != "owner" and all(c in cols for c in p["value_cols"])]

    units: list[dict] = []
    scope_ctx: list[dict] = []   # per-ProjectID tracker context for the OO join
    seen_pids: set[str] = set()
    skip_count = 0
    for idx, row in df.iterrows():
        sheet_row = int(idx) + 4
        pid = str(row.get("ProjectID", "")).strip()
        pname = str(row.get("PipelineName", "")).strip()
        sname = str(row.get("SegmentName", "")).strip()
        status = str(row.get("Status", "")).strip().lower()
        wiki = str(row.get("Wiki", "")).strip()
        if pid and pid not in seen_pids:
            seen_pids.add(pid)
            scope_ctx.append({"project_id": pid, "sheet_row": sheet_row,
                              "pipeline_name": pname, "segment_name": sname,
                              "status": status, "wiki": wiki})
        for p in pairs:
            ref_col = p["ref_col"]
            value_cols = p["value_cols"]
            values = {c: str(row.get(c, "")).strip() for c in value_cols
                      if not _blank(row.get(c, ""))}
            current_ref = str(row.get(ref_col, "")).strip() if ref_col else ""
            klass = _classify(p["kind"], ref_col, bool(values), current_ref,
                              owe_fill=_ref_stem(ref_col) in fill_pairs if ref_col else False)
            if klass == "SKIP":
                skip_count += 1
                continue
            primary_col = p["primary_value_col"]
            primary_value = str(row.get(primary_col, "")).strip() if primary_col else ""
            if not primary_value and values:
                primary_value = next(iter(values.values()))
            units.append({
                "project_id": pid,
                "sheet_row": sheet_row,
                "pipeline_name": pname,
                "segment_name": sname,
                "status": status,
                "wiki": wiki,
                "ref_col": ref_col,
                "value_cols": value_cols,
                "primary_value_col": primary_col,
                "values": values,
                "primary_value": primary_value,
                "current_ref": current_ref,
                "class": klass,
                "orphan_ref": klass == "MISSING_VALUE" and bool(current_ref),
                "kind": p["kind"],
                "irregular": p["irregular"],
                "existing_ref_checks": [],
                "value_checked": False,
            })

    # Operators/owners join: emit real Operator/Owner [ref] units per in-scope ProjectID.
    owner_units = 0
    owners_csv_name = None
    if owners_csv:
        owners_df, by_pid = _load_owners(owners_csv)
        oo_units = _owner_units(owners_df, by_pid, scope_ctx, fill_pairs=fill_pairs)
        owner_units = len(oo_units)
        units.extend(oo_units)
        owners_csv_name = Path(owners_csv).name

    if verify_existing:
        _verify_existing(units)

    by_class: dict[str, int] = {}
    for u in units:
        by_class[u["class"]] = by_class.get(u["class"], 0) + 1
    dead = sum(1 for u in units if u["class"] == "HAS_REF"
               and any(not c["ok"] for c in u["existing_ref_checks"]))
    live = sum(1 for u in units if u["class"] == "HAS_REF"
               and u["existing_ref_checks"] and all(c["ok"] for c in u["existing_ref_checks"]))
    name_absent = sum(1 for u in units if u["class"] == "HAS_REF"
                      and any(c.get("name_absent") for c in u["existing_ref_checks"]))
    fills_owed = [u for u in units if u["class"] == "MISSING_VALUE"]
    fills_by_status: dict[str, int] = {}
    fills_by_col: dict[str, int] = {}
    for u in fills_owed:
        fills_by_status[u.get("status") or "?"] = fills_by_status.get(u.get("status") or "?", 0) + 1
        fills_by_col[u["ref_col"]] = fills_by_col.get(u["ref_col"], 0) + 1
    return {
        "scope": {
            "csv": Path(csv).name,
            "owners_csv": owners_csv_name,
            "country": country or "global",
            "province": province,
            "exclude_network_regex": exclude_network_regex,
            "exclude_pids": sorted(exclude_pids) if exclude_pids else None,
            "include_pids": sorted(include_pids) if include_pids else None,
            "statuses": sorted(statuses) if statuses else "all",
            "rows": int(df.shape[0]),
            "project_ids": len(scope_ctx),
            "pairs": len(pairs),
            "verify_existing": verify_existing,
            "owe_fills": owe_fills,
            "fill_pairs": sorted(fill_pairs) if fill_pairs else [],
        },
        "summary": {
            "units": len(units),
            "by_class": by_class,
            "owner_operator_units": owner_units,
            "skip": skip_count,
            "has_ref_all_live": live,
            "has_ref_with_dead": dead,
            "has_ref_name_absent": name_absent,
            "fills_owed": len(fills_owed),
            "fills_owed_by_status": fills_by_status,
            "fills_owed_by_ref_col": fills_by_col,
            "fills_owed_orphan_ref": sum(1 for u in fills_owed if u.get("orphan_ref")),
        },
        "units": units,
    }


def _verify_existing(units: list[dict]) -> None:
    """HTTP-check every existing ref URL (per unit, with the value's surface forms when
    the value is numeric/year/status). Mutates units in place.

    RELEVANCE is checked too, ADVISORY only: the pipeline's `PipelineName` is passed as
    `name=` and a live, value-present page that never mentions the pipeline is marked
    `name_absent: True` (ok stays as the value check left it). It is advisory because the
    fuzzy name match is Latin-script — an English `PipelineName` will not appear on a
    Chinese or Arabic page that names the line in its own script — so flipping `ok` would
    manufacture dead links the way the status-token screen once did. The flag is the
    worklist's answer to the keyword-matching failure MZ reported (a page about "A" or "B"
    cited for the "A–B" line): every `name_absent` HAS_REF unit owes a human/agent read for
    relevance, and the count is reported in the summary."""
    for u in units:
        if u["class"] != "HAS_REF":
            continue
        urls = _extract_urls(u["current_ref"])
        if not urls:
            u["existing_ref_checks"] = []
            u["value_checked"] = False
            continue
        checked = _numericish(u["primary_value"])
        is_status = (not checked) and _is_status(u["primary_value"])
        any_of = surface_forms(u["primary_value"]) if (checked or is_status) else None
        results = verify_many(urls, any_of=any_of, name=u.get("pipeline_name") or None)
        u["existing_ref_checks"] = [
            {"url": url, **results.get(url, {"ok": False, "status": None, "reason": "not checked"})}
            for url in urls
        ]
        for c in u["existing_ref_checks"]:
            # Liveness + value govern `ok`; a NAME miss is a relevance flag, not a failure.
            if c.get("name_found") is False and c.get("status") == 200 \
                    and "name not found" in (c.get("reason") or ""):
                c["ok"] = True
                c["name_absent"] = True
                c["reason"] = ("200, live, value present; pipeline name NOT found on the page "
                               "(fuzzy, Latin) — read it for relevance: does it describe THIS "
                               "line, or only one of its endpoints / the network?")
        if is_status:
            # Liveness still governs; a missing status TOKEN does not.
            for c in u["existing_ref_checks"]:
                if not c.get("ok") and c.get("status") == 200 \
                        and "data value not found" in (c.get("reason") or ""):
                    c["ok"] = True
                    c["status_token_absent"] = True
                    c["reason"] = ("200, live; status token not present verbatim "
                                   "(expected \u2014 status is inferred from prose, not matched)")
        u["value_checked"] = checked


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tracker", required=True, choices=["oil", "gas"])
    ap.add_argument("--country")
    ap.add_argument("--province",
                    help="comma-separated Start/EndState/Province filter (row in scope if EITHER "
                         "terminus matches; transited provinces don't count). Combine with "
                         "--country for sub-country batches, e.g. China by province")
    ap.add_argument("--exclude-network-regex",
                    help="drop rows whose PipelineNetworkGrouping matches this regex (re.search). "
                         "China idiom: '^(?!.*输气管网$)' keeps only provincial-grid rows, "
                         "excluding national trunk systems (their own batch scope)")
    ap.add_argument("--exclude-pids",
                    help="comma-separated ProjectIDs to drop from the scope, or @<path> to read "
                         "them from a file (one per line, '#' comments ok). Use when a transit "
                         "country's shared trunks were already staged by another country's pass — "
                         "re-researching them stages contradictory records on the same cells")
    ap.add_argument("--include-pids",
                    help="comma-separated ProjectIDs to union INTO the scope (or @<path>, same "
                         "file form as --exclude-pids), bypassing the province/status/network "
                         "filters. --province matches on termini only, so a national trunk "
                         "TRANSITING the province needs naming here to be swept with the "
                         "branches that hang off it. --exclude-pids wins on conflict")
    ap.add_argument("--status", help="comma-separated Status filter (e.g. proposed,construction)")
    ap.add_argument("--csv", help="GEM CSV (default: latest snapshot for the tracker)")
    ap.add_argument("--owners-csv",
                    help="operators/owners tab CSV (default: latest GEM_operators_owners_snapshot_*.csv; "
                         "pass --no-owners to skip the owner/operator join)")
    ap.add_argument("--no-owners", action="store_true",
                    help="skip the operators/owners join (no Operator/Owner [ref] units)")
    ap.add_argument("--verify-existing", action="store_true",
                    help="HTTP-check existing ref URLs up front (deterministic, no agent tokens)")
    ap.add_argument("--owe-fills", action="store_true",
                    help="also emit MISSING_VALUE units for blank value cells on the owed pairs "
                         "(default set: " + ",".join(FILL_PAIRS_DEFAULT) + "), so the fills leg "
                         "has an owed set instead of filling opportunistically. Part of the "
                         "`deep` preset")
    ap.add_argument("--fill-pairs",
                    help="comma-separated ref-column stems that owe fills (e.g. "
                         "'Length,Capacity,Diameter'), or 'all' for every ref pair; implies "
                         "--owe-fills")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    csv = args.csv
    if not csv:
        pat = "GOIT_oil_ngl_snapshot_*.csv" if args.tracker == "oil" else "GGIT_gas_snapshot_*.csv"
        files = sorted(glob.glob(str(paths.repo_root() / "data" / pat)))
        if not files:
            sys.exit("no GEM snapshot found — run ./scripts/refresh_csvs.sh")
        csv = files[-1]

    owners_csv = None
    if not args.no_owners:
        owners_csv = args.owners_csv
        if not owners_csv:
            oo = sorted(glob.glob(str(paths.repo_root() / "data" / "GEM_operators_owners_snapshot_*.csv")))
            if oo:
                owners_csv = oo[-1]
            else:
                print("  note: no operators/owners snapshot found — skipping owner/operator join "
                      "(run ./scripts/refresh_csvs.sh, or pass --no-owners to silence)", file=sys.stderr)

    statuses = None
    if args.status:
        statuses = {s.strip().lower() for s in args.status.split(",") if s.strip()}

    exclude_pids = _pid_set(args.exclude_pids, "--exclude-pids")
    include_pids = _pid_set(args.include_pids, "--include-pids")

    fill_pairs = None
    owe_fills = args.owe_fills
    if args.fill_pairs:
        owe_fills = True
        if args.fill_pairs.strip().lower() != "all":
            fill_pairs = frozenset(p.strip() for p in args.fill_pairs.split(",") if p.strip())
        else:
            fill_pairs = None   # resolved to every pair below
    if owe_fills and args.fill_pairs and args.fill_pairs.strip().lower() == "all":
        _probe = _load_indexed(csv)
        fill_pairs = frozenset(_ref_stem(p["ref_col"]) for p in discover_ref_pairs(list(_probe.columns))
                               if p["ref_col"]) | {"Operator", "Owner"}

    if args.verify_existing:
        # verify_many runs once per HAS_REF unit, so a row whose 20 cells cite one document
        # would download it 20 times (US gas slice 2: 40+ min per batch). Cache the RESPONSE
        # for this run only; each unit still runs its own value/name check against it.
        import url_verifier
        url_verifier.RESPONSE_CACHE = {}
    wl = build(csv, args.country, statuses, args.verify_existing, owners_csv=owners_csv,
               province=args.province, exclude_network_regex=args.exclude_network_regex,
               exclude_pids=exclude_pids, include_pids=include_pids,
               owe_fills=owe_fills, fill_pairs=fill_pairs)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(wl, indent=2, ensure_ascii=False))

    s, m = wl["scope"], wl["summary"]
    print(f"wrote {out}")
    if s.get("exclude_pids"):
        # Never drop rows silently — an excluded PID is uncovered work, and the reader
        # needs to see which rows this worklist is NOT accountable for.
        ex = s["exclude_pids"]
        print(f"  EXCLUDED {len(ex)} ProjectID(s) from scope: {','.join(ex)}")
    if s.get("include_pids"):
        inc = s["include_pids"]
        print(f"  INCLUDED {len(inc)} ProjectID(s) past the province/status filters: {','.join(inc)}")
    prov = f" / {s['province']}" if s.get("province") else ""
    print(f"  scope: {s['country']}{prov} | {args.tracker} | {s['rows']} rows | "
          f"statuses={s['statuses']} | {s['pairs']} ref-pairs"
          + (f" | owners={s['owners_csv']}" if s.get("owners_csv") else " | owners=skipped"))
    print(f"  units: {m['units']}  by_class={m['by_class']}  "
          f"(operator/owner {m.get('owner_operator_units', 0)}; skipped {m['skip']} blank)")
    if args.verify_existing:
        print(f"  existing refs: {m['has_ref_all_live']} all-live, {m['has_ref_with_dead']} with dead/missing link(s), "
              f"{m['has_ref_name_absent']} live but pipeline name absent (relevance read owed)")
    if s.get("owe_fills"):
        print(f"  fills owed (MISSING_VALUE): {m['fills_owed']}  by status={m['fills_owed_by_status']}  "
              f"orphan [ref] on blank value={m['fills_owed_orphan_ref']}")
        print(f"    by column: {m['fills_owed_by_ref_col']}")


if __name__ == "__main__":
    main()
