#!/usr/bin/env python3
"""Does a deep-sweep shard report on EVERY worklist unit assigned to its pipeline?

Called by each subagent before it finishes (the contract in
`.claude/workflows/critical-deep-sweep.js` blocks on it), and by the orchestrator with
`--all` to audit a whole staging dir before the merge.

The defect it exists to stop: a unit whose class is MISSING_REF — the sheet HAS a value and
its `[ref]` cell is EMPTY — being confirmed in prose and reported nowhere machine-readable.
`seed_resolutions_from_worklist.py` seeds a record for every MISSING_REF unit, so a dropped
one does not go missing downstream; it silently becomes UNRESOLVED with empty notes, which
is indistinguishable from "nobody looked". Measured at 26-45% of MISSING_REF units across
the 2026-09 US gas batches (218 never-worked units / 47 rows, gate-L accounting) while
MISSING_VALUE — the one class the contract named and gate J counted — ran at 0-1%. Same
agents, same runs: the variable was whether the contract carried a per-unit emit rule.

It also catches the neighbouring defect: a fills[] record that CANNOT be merged, because it
carries no `ref_col` to key on or a `class_out` outside the four the pipeline accepts
(`build_ref_workbook.py` drops anything else without a word). That record is research that
was done and will vanish — a different message from "you skipped this unit", and one the
agent can fix in place by re-keying rather than re-researching.

It also blocks a shard that has not opened every citation harvested from the row's gem.wiki
page (`wiki_citations.json`): each needs a `wiki_citations_read` entry (`shard_upsert.py
--wiki-read`) saying used / no_value / not_this_row / dead / blocked, and a dead or blocked
one must show the fetch.py ladder and a Wayback lookup were tried (Baird 2026-10-17, P1451).

    python scripts/check_shard_coverage.py --staging <dir> --pid P0187
    python scripts/check_shard_coverage.py --staging <dir> --all [--json]

Exit 0 = every unit has a record. Exit 1 = units left unreported (or the shard is missing
/ unparseable). Advisory elsewhere in this repo is deliberate; here it is a hard stop,
because the agent that would fix it is still running when this is called.
"""
from __future__ import annotations

import argparse
import collections
import itertools
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_qc import BLOCK, is_ref_only, load_sheet, off_schema_keys, sheet_value  # noqa: E402


SCOPE_MISMATCH = re.compile(
    r"documents only|only the [^.]{0,60}(lateral|phase|increment|segment|system)|not the (mainline|system|whole)"
    r"|flag for the orchestrator|worth a human check|different (event|entity)|reads as if", re.I)

# A status change carries the date of the event it reports (Baird 2026-10-16, P0241: operating was
# staged with StartYear1 only, and the June 2026 in-service month the Sempra release states was missed).
STATUS_DATE_COL = {"operating": "StartYear1", "construction": "ConstructionYear", "proposed": "ProposalYear",
                   "shelved": "ShelvedYear", "cancelled": "CancelledYear", "mothballed": "StopYear",
                   "idle": "StopYear", "retired": "StopYear"}
DATE_NOT_FOUND = re.compile(
    r"\b(start|in[- ]service|construction|proposal|proposed|shel\w*|cancel\w*|stop\w*|retire\w*)\b[^.]{0,80}"
    r"\b(not found|not stated|not given|no date|not reported|does not (say|state|give))", re.I)


def _carried(pid, col, value, snapshot_value) -> bool:
    """entity_style.carried_on_sheet, or the snapshot-only test when the styler is unavailable."""
    try:
        from entity_style import carried_on_sheet
        return carried_on_sheet(pid, col, value, snapshot_value)
    except Exception:       # pragma: no cover
        return snapshot_value is not None and str(snapshot_value).strip() == str(value or "").strip()


def _owner_style(name: str):
    """`entity_style.style(name)`, or None if the styler (or its data files) is unavailable —
    a missing gazetteer must not block a shard over a check it cannot run."""
    try:
        from entity_style import style
        return style(name)
    except Exception:       # pragma: no cover — data files absent on a bare checkout
        return None


# Every citation harvested from the row's gem.wiki page is OPENED and accounted for (Baird
# 2026-10-17, P1451): the harvest put the ukrrudprom and EEGAS tables stating the sheet's
# 2 bcm/y in wiki_citations.json, the agent never opened either, and staged a 1999 "up to 4 bcm"
# planned volume as a change. A shard carrying `wiki_citations_read` (shard_upsert --init adds
# it) must hold one entry per harvested citation; older shards without the key only warn.
WIKI_OUTCOMES = {"used", "no_value", "not_this_row", "dead", "blocked"}
_WAYBACK = re.compile(r"^https?://web\.archive\.org/web/[0-9a-z_*]+/", re.I)


def _norm_url(u: str) -> str:
    u = _WAYBACK.sub("", (u or "").strip())
    u = re.sub(r"^https?://", "", u, flags=re.I)
    u = re.sub(r"^www\.", "", u, flags=re.I)
    u = re.sub(r":80(?=/)", "", u)
    return u.rstrip("/").lower()


@lru_cache(maxsize=None)
def load_wiki_citations(staging: Path) -> dict:
    p = staging / "wiki_citations.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text()).get("pages") or {}


def wiki_citation_groups(staging: Path, pid: str) -> list[dict]:
    """One group per harvested citation (cite_id): the original URL and its archived copy
    are one source, so reading either accounts for both."""
    page = load_wiki_citations(staging).get(pid) or {}
    groups: dict[str, dict] = {}
    for c in page.get("citations") or []:
        key = c.get("cite_id") or c.get("url")
        g = groups.setdefault(key, {"cite_id": key, "urls": [], "link_text": c.get("link_text") or ""})
        g["urls"].append(c.get("url"))
    return list(groups.values())


def check_wiki_reads(staging: Path, pid: str, shard: dict) -> tuple[list[dict], bool]:
    """(gaps, enforced). Each gap is {"cite": ..., "why": ...}."""
    groups = wiki_citation_groups(staging, pid)
    enforced = "wiki_citations_read" in shard
    reads = [r for r in (shard.get("wiki_citations_read") or []) if isinstance(r, dict)]
    by_url = {}
    for r in reads:   # full URL, and the URL without its query string (tracking parameters)
        for u in (r.get("url"), r.get("read_via")):
            if u:
                by_url.setdefault(_norm_url(u), r)
                by_url.setdefault(_norm_url(u).split("?")[0], r)
    cited = set()
    for kind in ("fills", "validity", "status_reviews", "_units"):
        recs = load_units(staging).get(pid, []) if kind == "_units" else shard.get(kind) or []
        for rec in recs:
            for u in list(rec.get("proposed_refs") or []) + re.split(r"[\s;,]+", str(rec.get("current_ref") or "")):
                if u:
                    cited.add(_norm_url(u))
    gaps = []
    for g in groups:
        keys = [k for u in g["urls"] for k in (_norm_url(u), _norm_url(u).split("?")[0])]
        hit = next((by_url[k] for k in keys if k in by_url), None)
        label = g["urls"][0]
        if hit is None:
            gaps.append({"cite": label, "why": f"harvested wiki citation never opened ({g['link_text'][:60]!r})"})
            continue
        outcome = hit.get("outcome")
        if outcome not in WIKI_OUTCOMES:
            gaps.append({"cite": label, "why": f"outcome {outcome!r} is not one of {sorted(WIKI_OUTCOMES)}"})
        elif outcome in ("dead", "blocked"):
            tried = " ".join(map(str, hit.get("tried") or [])).lower()
            if "fetch" not in tried or not ("wayback" in tried or "archive" in tried):
                gaps.append({"cite": label, "why": f"{outcome} without the full ladder: `tried` must "
                             "show scripts/fetch.py AND a Wayback/archive lookup"})
        elif outcome == "used" and not ({_norm_url(u) for u in g["urls"]} | {_norm_url(hit.get("url"))}) & cited:
            gaps.append({"cite": label, "why": "marked used but no record carries it in proposed_refs"})
        if outcome in ("no_value", "not_this_row") and not str(hit.get("note") or "").strip():
            gaps.append({"cite": label, "why": f"{outcome} needs a note saying what the page does say"})
    return gaps, enforced


def load_units(staging: Path) -> dict[str, list[dict]]:
    wl = json.loads((staging / "worklist.json").read_text())
    by_pid: dict[str, list[dict]] = collections.defaultdict(list)
    for u in wl.get("units") or []:
        by_pid[u.get("project_id")].append(u)
    return by_pid


@lru_cache(maxsize=None)
def load_scope_sheet(staging: Path):
    """The snapshot the worklist was built from (merge_qc.load_sheet), or None."""
    wl = json.loads((staging / "worklist.json").read_text())
    return load_sheet(wl.get("scope"))


GAS_FUEL_VALUES = {"Gas", "Hydrogen", "Gas and hydrogen", "Coke oven gas"}
PIPELINE_TYPE_VALUES = {"transmission", "gathering", "distribution", "both transmission and gathering",
                        "both transmission and distribution", "both gathering and distribution"}
DATA_CENTER_VALUES = {"yes", ""}  # Baird 2026-10-16: `yes` or blank, never `no` or `Yes`
VALID_CLASS_OUT = {"REFS_ADDED", "REVERIFIED", "UNRESOLVED", "DEAD_LINK", "REF_BLOCKED",
                   "REF_UNSUPPORTED"}


def check(units: list[dict], fills: list[dict], sheet=None, pid: str = ""
          ) -> tuple[list[dict], list[dict], list[dict]]:
    """-> (unreported units, silent-UNRESOLVED records, unmergeable records).

    Matching is by ref_col, disambiguated by sheet_row ONLY where a pipeline carries several
    units on the same ref_col (multi-segment rows). Owner/Operator units are keyed to the
    separate operators-owners tab, so subagents report that tab's row rather than the
    tracker's — keying on sheet_row unconditionally would flag every one of them as missing
    (the same trap `merge_deepsweep_shards.py` works around).
    """
    by_col: dict[str, list[dict]] = collections.defaultdict(list)
    for f in fills:
        by_col[f.get("ref_col")].append(f)

    unreported = []
    for ref_col, group in itertools.groupby(
        sorted(units, key=lambda u: str(u.get("ref_col"))), key=lambda u: str(u.get("ref_col"))
    ):
        group = list(group)
        got = by_col.get(ref_col, [])
        if len(group) == 1:
            if not got:
                unreported.append(group[0])
            continue
        rows_got = {f.get("sheet_row") for f in got}
        for u in group:                                  # multi-segment: match per row
            if u.get("sheet_row") not in rows_got:
                unreported.append(u)

    silent = [f for f in fills
              if f.get("class_out") == "UNRESOLVED"
              and not (f.get("researcher_notes") or "").strip()]

    malformed = []
    SOURCED_OUT = {"REFS_ADDED", "REVERIFIED", "CONFIRMED"}
    for f in fills:
        why = []
        # SENTINELS (`__VALIDITY__` / `__REDUNDANCY__` / `__STATUS__`) are exempt from both
        # class checks below, and `validate_shards.py` exempts them the same way on the same
        # reasoning. A sentinel asserts a FINDING about a ROW -- a redundancy verdict, a
        # route-length divergence, a status re-read -- not a value for a worklist unit. It
        # carries `value_cols: []` and `values: {}` by construction, and its class comes from
        # the sentinel vocabulary (CONFIRMED/CONCERN/OPEN/REFUTED/INFO), not the ref
        # vocabulary. So it trips BOTH checks -- "not one of REFS_ADDED/..." and "sourced but
        # `values` is empty" -- and both readings are wrong. Nor is it "dropped at workbook
        # build": sentinels never travel the ref-fold path. split_shards.py routes them to
        # `ref_shards/<PID>.json` for `harvest_sentinel_findings.py`, which rewrites
        # `class_out` to UNRESOLVED itself, so whatever the shard wrote in that slot never
        # reaches the builder at all.
        # 2026-09-10: this cost 96 false class-trips + 87 false values-trips across four
        # staged batches (jiangxi v2 + v3, libya cancelled-review + ref-sweep-operating) and
        # hard-stopped the jiangxi v3 chain on 80 "unmergeable" records that were all fine.
        # The `silent UNRESOLVED` check above deliberately still applies: a sentinel with no
        # `researcher_notes` really does say nothing.
        if (f.get("ref_col") or "").strip().startswith("__"):
            continue
        # A value CHANGED on EIA comes from the NEWEST pipeline-projects release (Baird
        # 2026-10-08, eia_release.py): an older release cited without it is blocked. A ref added
        # to the sheet's own value is not a change, so an older release that states it is fine.
        # Unknown when the snapshot can't place the cell, and then not judged.
        vals_eia = f.get("values") or {}
        if sheet is not None and vals_eia:
            cur_eia = {c: sheet_value(sheet, pid, f.get("sheet_row"), c) for c in vals_eia}
            if None not in cur_eia.values() and not is_ref_only(vals_eia, cur_eia):
                try:
                    from eia_release import stale_reason
                    eia_why = stale_reason(f, changes_value=True)
                except Exception:       # pragma: no cover -- vintages.csv absent on a bare checkout
                    eia_why = None
                if eia_why:
                    why.append(eia_why)
        # A handful of tracker value columns have no paired `[ref]` column at all
        # (OtherEnglishNames, the OtherLanguage* names). A fill on one of those is
        # legitimately ref-less and merges fine as a FILL carrying only values — it is
        # not unkeyable research (2026-09-09: tx P0257's alias fix was flagged here for
        # a month while sitting correctly in the merged store the whole time).
        if not (f.get("ref_col") or "").strip():
            if not any(str(v).strip() for v in (f.get("values") or {}).values()):
                why.append("no ref_col and no values — nothing to key it to a worklist unit")
        if f.get("class_out") not in VALID_CLASS_OUT:
            why.append(f"class_out={f.get('class_out')!r} is not one of "
                       f"{'/'.join(sorted(VALID_CLASS_OUT))} — dropped at workbook build")
        # Length and capacity are staged in the unit the SOURCE states (Baird 2026-10-02): a
        # record whose notes show a conversion INTO the staged unit ("246 miles = 395.9 km"
        # staged as km, "CONVERSION DONE HERE") is not mergeable. The sheet's km / bcm/y
        # columns are computed, so the conversion is never the researcher's job.
        vals_ = f.get("values") or {}
        notes_ = str(f.get("researcher_notes") or "")
        if "LengthKnownUnits" in vals_ and str(vals_.get("LengthKnownUnits")) == "km" and re.search(
                r"\b\d[\d,.]*\s*(?:miles?|mi)\b[^.;]{0,60}?(?:=|->|to|is)\s*[\d,.]+\s*km\b",
                notes_, re.I) and not re.search(r"\bkm\b[^.;]{0,40}(?:states?|gives?|reports?)", notes_, re.I):
            why.append("the notes show the source gives MILES but `LengthKnownUnits` is km — "
                       "stage the source's own number and unit (`mi`); the km figure is computed")
        if re.search(r"conversion done here", notes_, re.I):
            why.append("notes say the figure was converted here — stage the source's own number "
                       "and unit instead (length/capacity are never converted)")
        for ucol_ in ("LengthKnownUnits", "CapacityUnits"):
            if ucol_ in vals_ and re.fullmatch(r"[\d.,]+", str(vals_[ucol_]).strip()):
                why.append(f"`{ucol_}` holds a number ({vals_[ucol_]!r}) — put the unit token there")
        # Month columns hold the NUMBER 1-12 (Baird 2026-10-08): "July" or "Sept" pasted or
        # written RAW lands as text the date formulas can't read.
        for mcol_, mval_ in vals_.items():
            if "Month" in str(mcol_) and str(mval_).strip() and not re.fullmatch(
                    r"(?:[1-9]|1[0-2])(?:\.0+)?", str(mval_).strip()):
                why.append(f"`{mcol_}` = {mval_!r} — month columns take the number 1-12, never "
                           "the month name or text")
        # `Fuel` on the gas tab takes one of four values (Baird 2026-10-09): never "natural gas",
        # "Natural Gas" or lowercase "gas". A value equal to the sheet's own is carried, not checked.
        if "Fuel" in vals_ and str(vals_["Fuel"]).strip() not in GAS_FUEL_VALUES:
            cur_fuel = sheet_value(sheet, pid, f.get("sheet_row"), "Fuel") if sheet is not None else None
            if str(vals_["Fuel"]).strip() != str(cur_fuel or "").strip():
                why.append(f"`Fuel` = {vals_['Fuel']!r} — the gas tab takes only "
                           + ", ".join(sorted(GAS_FUEL_VALUES)) + " (a plain gas pipeline is `Gas`)")
        # `PipelineType` takes transmission / gathering / distribution or a combination of two (Baird
        # 2026-10-14): never lateral, expansion, interstate, intrastate (EIA's labels) or free text.
        if "PipelineType" in vals_ and str(vals_["PipelineType"]).strip() \
                and str(vals_["PipelineType"]).strip() not in PIPELINE_TYPE_VALUES:
            cur_pt = sheet_value(sheet, pid, f.get("sheet_row"), "PipelineType") if sheet is not None else None
            if str(vals_["PipelineType"]).strip() != str(cur_pt or "").strip():
                why.append(f"`PipelineType` = {vals_['PipelineType']!r} — only "
                           + ", ".join(sorted(PIPELINE_TYPE_VALUES)) + " (a lateral or an expansion of a "
                           "transmission line is `transmission`; EIA's interstate/intrastate is not a type)")
        # `DataCenter` takes `yes` or blank (Baird 2026-10-16), and `yes` needs its own
        # `DataCenter [ref]`. A value equal to the sheet's own is carried, not checked.
        if "DataCenter" in vals_ and str(vals_["DataCenter"]).strip() not in DATA_CENTER_VALUES:
            cur_dc = sheet_value(sheet, pid, f.get("sheet_row"), "DataCenter") if sheet is not None else None
            if str(vals_["DataCenter"]).strip() != str(cur_dc or "").strip():
                why.append(f"`DataCenter` = {vals_['DataCenter']!r} — only `yes` or blank (never `no`)")
        # `DataCenterNotes` (added 2026-10-16) describes the related data center, so it only
        # goes beside `DataCenter = yes`, staged here or already on the sheet.
        if str(vals_.get("DataCenterNotes") or "").strip():
            dc_ = vals_["DataCenter"] if "DataCenter" in vals_ else (
                sheet_value(sheet, pid, f.get("sheet_row"), "DataCenter") if sheet is not None else "yes")
            if str(dc_ or "").strip() != "yes":
                why.append("`DataCenterNotes` without `DataCenter` = `yes`")
        # Costs are staged in FULL currency units (Baird 2026-10-02): EIA workbooks say
        # `Cost (millions)`, so 5,100 there is 5100000000. A USD cost under 100,000 is a figure
        # left unscaled. Other currencies are exempt (small RUB/RMB amounts can be real).
        for ccol_, cucol_ in (("SegmentCost", "SegmentCostUnits"),
                              ("ProjectLevelCost", "ProjectLevelCostUnits")):
            if ccol_ not in vals_:
                continue
            try:
                cval_ = float(str(vals_[ccol_]).replace(",", "").strip())
            except ValueError:
                continue
            cunit_ = vals_.get(cucol_)
            if cunit_ is None and sheet is not None:
                cunit_ = sheet_value(sheet, pid, f.get("sheet_row"), cucol_)
            if 0 < cval_ < 100000 and str(cunit_ or "").strip().upper() in ("", "USD"):
                why.append(f"`{ccol_}` = {vals_[ccol_]} looks unscaled — costs are staged in full "
                           "currency units (5100000000, not 5100); read the source's column "
                           "header (EIA says `Cost (millions)`) and scale it")
        # A SOURCED record must carry the value its refs state, in `values` — standing rule
        # 4(e). With `values` empty the ref-only fold has nothing to compare to the sheet, so
        # the record stays a separate FILL: the ref lands orphaned (gate E) and the unit's
        # real record keeps its unresearched seed. Stating the value only in researcher_notes
        # reads as done and is not (2026-09-09: appalachian P0310 shipped all 9 of its
        # columns this way and passed coverage, because a record existed for each).
        if f.get("_leg") != "refs" and (f.get("class_out") or "").upper() in SOURCED_OUT \
                and not any(
                str(v).strip() for v in (f.get("values") or {}).values()):
            why.append("class_out is sourced but `values` is empty — put the value the refs "
                       "state in `values` (the SAME value, when they agree with the sheet); "
                       "notes-only leaves an orphan [ref]")
        # ...and must carry its refs where the merge reads them: `proposed_refs` (URLs) plus
        # `verifications`. Any other shape is invisible to merge_deepsweep_shards.py, which
        # stages the record with no refs at all (2026-09-10: us-gas P0186 wrote
        # `refs: [{url, tier, note}]` on 10 sourced units and passed this check; the merge
        # dropped every ref and only gate E caught one of them). A column with no [ref] pair
        # (OtherEnglishNames; `ref_col` empty) has nowhere to put a ref, so it is exempt.
        if f.get("_leg") != "refs" and (f.get("class_out") or "").upper() in SOURCED_OUT \
                and f.get("ref_col") and not f.get("proposed_refs"):
            why.append("class_out is sourced but `proposed_refs` is empty"
                       + (" (refs are under `refs` — use `proposed_refs` + `verifications`)"
                          if f.get("refs") else "")
                       + " — the merge stages it with no ref")
        # ...and the verification objects the merge READS. `merge_qc.verified_refs` keeps a
        # URL only when a verification says `ok` AND `contains_value`; a sourced record with
        # no `verifications`, or with `ok` objects that omit `contains_value`, is stripped of
        # every ref at merge and downgraded to UNRESOLVED with a [QC] note -- silently,
        # because the downgrade is a safety net (Sweep SOP §Merge-time QC normalization).
        # 2026-09-14, Russia R1 pilot: two shards wrote no verifications at all and eight
        # omitted `contains_value` on every ok object; every one passed this check, the merge
        # turned ~110 sourced records into UNRESOLVED, and gate E noticed 26 of them on two
        # rows. `name_found` is the same failure one notch down: without it on any ok
        # verification the record ships "relevance unrecorded" and gate I' flags it (128
        # units, same run). The needs-attention classes are included because its replacement/Wayback refs walk
        # the same path.
        if f.get("_leg") != "refs" and (f.get("class_out") or "").upper() in (SOURCED_OUT | {"DEAD_LINK", "REF_BLOCKED", "REF_UNSUPPORTED"}) \
                and f.get("proposed_refs"):
            vers = [v for v in (f.get("verifications") or []) if isinstance(v, dict)]
            refs = {str(u or "").strip() for u in f["proposed_refs"]}
            good = [v for v in vers if v.get("ok") and v.get("contains_value")
                    and str(v.get("url") or "").strip() in refs]
            if not vers:
                why.append("sourced record with no `verifications` — the merge strips every "
                           "ref and downgrades it to UNRESOLVED; write one {url, ok, "
                           "contains_value, name_found, note} per proposed ref")
            elif not good:
                why.append("no verification says ok+contains_value for a proposed ref — the "
                           "merge strips every ref and downgrades it to UNRESOLVED (a missing "
                           "`contains_value` key reads as false)")
            elif any("name_found" not in v for v in vers if v.get("ok")):
                why.append("an ok verification lacks `name_found` — the record ships "
                           "'relevance unrecorded' and gate I' flags it; encode true|false "
                           "with the matched name in `note`")
        # A ref reported as blocked / 403 / unreachable must have been tried through the fetch
        # ladder (`scripts/fetch.py`: curl -> curl_cffi TLS impersonation -> Chrome clearance).
        # 2026-10-16, P0278: the agent wrote "403 on every fetch attempt" for an
        # offshore-technology.com page that fetch.py reads on the impersonation rung, so a 36 in
        # diameter sat unstaged. A bare 403 is a tooling failure, not a finding.
        _n = str(f.get("researcher_notes") or "")
        if (f.get("class_out") or "").upper() in {"REF_BLOCKED", "REF_UNSUPPORTED", "UNRESOLVED", "DEAD_LINK"} \
                and re.search(r"\b403\b|cloudflare|bot[- ]?wall|\bblocked\b|could not (?:be )?(?:fetch|load|access|read)|every fetch",
                     _n, re.I) \
                and not re.search(r"fetch\.py|cf_impersonate|curl_cffi|clearance", _n, re.I):
            why.append("notes say a page was blocked / 403 / could not be fetched but do not say it "
                       "went through `python scripts/fetch.py <url> --head 2000` (curl -> TLS "
                       "impersonation -> Chrome clearance); run it, read the page, and name the "
                       "route that worked (the `notes:` line) or that all three failed")
        # `values{}` keys land in real cells: a key that is no backend / owners-tab column
        # (R6: `Owner`, `Start`, `Construction` -- ref-column stems) reaches no paste surface.
        # The labels (`value_cols`, `primary_value_col`) must be real headers too, and the refs leg
        # is no exception (P4039 `StartState`, P4040 `Operator1`, P0168 `ConstructionYear1`,
        # Iraq P7459 `LengthUnits`: 2026-10-09; repair with scripts/fix_staged_columns.py).
        if sheet is not None:
            named = [c for c in list(f.get("value_cols") or []) + [f.get("primary_value_col")]
                     if c and c not in sheet.columns]
            if named:
                why.append(f"value_cols / primary_value_col {', '.join(map(repr, sorted(set(named))))} "
                           "are not sheet columns — use the exact backend/owners-tab header "
                           "(scripts/fix_staged_columns.py lists and repairs them)")
        if sheet is not None:
            bad = off_schema_keys(sheet, f.get("ref_col"), f.get("values"))
            if bad:
                allowed = sorted(sheet.pairs.get(f.get("ref_col") or "") or [])
                allowed = allowed[:6] + (["…"] if len(allowed) > 6 else [])
                why.append(f"values key(s) {', '.join(map(repr, bad))} are not "
                           + (f"{f.get('ref_col')} columns ({', '.join(allowed)})" if allowed
                              else "sheet columns")
                           + " — use the exact backend/owners-tab header")
            # An UNRESOLVED record has no sourced value, so it carries the sheet's own; a
            # proposal there is pasted as if researched (R6 P2705, P3604). Put it in notes.
            if f.get("_leg") != "refs" and (f.get("class_out") or "").upper() == "UNRESOLVED":
                row = f.get("sheet_row")
                moved = [c for c, v in (f.get("values") or {}).items()
                         if (cur := sheet_value(sheet, pid, row, c)) is not None
                         and str(v or "").strip() != str(cur or "").strip()
                         and not is_ref_only({c: v}, {c: cur})]
                if moved:
                    why.append(f"UNRESOLVED but `values` changes {', '.join(moved)} from the "
                               "sheet — an unsourced proposal belongs in researcher_notes; "
                               "set values to the sheet's")
        # A proposed Owner<N> or Operator name is written the way the ownership team writes it
        # (docs/reference/owner_style.md): trailing short legal form, no punctuation, no
        # trailing acronym, team spelling on an exact/alias gazetteer hit. A value equal to
        # the sheet's current cell — in the worklist's snapshot OR the newest one in data/, since
        # a batch pushed after the worklist was built leaves its values on the sheet — is
        # carried, not proposed, so it is not checked here (entity_style.carried_on_sheet).
        if f.get("_leg") != "refs" and (f.get("tab") == "operators_owners"
                                        or f.get("ref_col") in ("Owner [ref]", "Operator [ref]")):
            restyle = []
            for c, v in (f.get("values") or {}).items():
                sv = str(v or "").strip()
                if not re.fullmatch(r"Owner\d+|Operator", str(c)) or not sv:
                    continue
                cur = sheet_value(sheet, pid, f.get("sheet_row"), c) if sheet is not None else None
                if _carried(pid, c, sv, cur):
                    continue            # equal to the worklist's snapshot or the newest one
                st = _owner_style(sv)
                # an unchanged value can still be unfit: several owners, or a slash, in one cell
                if st is not None and (st.changed or ({"multi_owner", "slash"} & set(st.flags) and st.basis != "ruling")):
                    restyle.append(f"{c}: {sv!r} -> {st.styled!r}"
                                   + (" (one owner per cell)" if "multi_owner" in st.flags else "")
                                   + (" (a slash joins two names: split into two owners or pick the accurate one)"
                                      if "slash" in st.flags else "")
                                   + (" (the bracketed note is not part of the name; it may mean "
                                      "this is a parent, and Owner1 holds the lowest-level company that owns the pipeline)"
                                      if "owner_qualifier" in st.flags else ""))
            if restyle:
                why.append("owner name(s) not in the ownership team's style — "
                           + "; ".join(restyle)
                           + " (use the styled form in `values`; keep the source's spelling "
                             "and any dropped acronym in researcher_notes)")
        # A high-tier record whose own notes say the ref covers a different thing than the row
        # (one lateral, one phase, a parent system, a different event or entity) is not high
        # (Baird 2026-10-09, P0168: two 10-Ks for the High Plains lateral's 2008 in-service date
        # were staged high as the start year of the whole 1928 system). Re-scope the value, find
        # a ref that states it for this row, or drop the tier to low and say why.
        if (f.get("tier") or "").lower() == "high" and f.get("proposed_refs") \
                and (f.get("class_out") or "").upper() != "UNRESOLVED" \
                and (m := SCOPE_MISMATCH.search(f.get("researcher_notes") or "")):
            why.append(f"tier is high but the notes say the ref covers something other than this "
                       f"row ({m.group(0)!r}) — fix the value or ref, or set tier low")
        if why:
            malformed.append({"ref_col": f.get("ref_col"), "why": "; ".join(why)})
    return unreported, silent, malformed


DORMANCY_NOTE = re.compile(r"shelv|cancel|dorman|inferred|2[- ]year|4[- ]year|two[- ]year|four[- ]year", re.I)


def _aged_proposed(s: dict, sheet, pid: str) -> str:
    """A `confirm` on a `proposed` row old enough for the 2-year (shelved) / 4-year (cancelled)
    dormancy rules must say it applied them (Baird 2026-10-16, P4449). Passes when the row has no
    proposal year, the proposal is under 2 years old, the verdict's own newest evidence is under
    2 years old (the project is alive), or the notes discuss shelved / cancelled / dormancy."""
    import datetime
    this = datetime.date.today().year
    try:
        py = int(float(str(sheet_value(sheet, pid, s.get("sheet_row"), "ProposalYear") or "").strip()))
    except ValueError:
        return ""
    age = this - py
    if age < 2:
        return ""
    m = re.match(r"\d{4}", str(s.get("evidence_date") or ""))
    if m and this - int(m.group()) < 2:
        return ""
    if DORMANCY_NOTE.search(str(s.get("researcher_notes") or "")) or str(s.get("staleness_rule") or "").strip():
        return ""
    want = "cancelled" if age >= 4 else "shelved"
    return (f"confirm on a proposed row with ProposalYear {py} ({age} years old) and no evidence newer than "
            f"2 years -- apply the dormancy rule: stage a `stale` verdict ({want}, ShelvedCancelledType "
            f"inferred, year of the newest dated source) or say in researcher_notes why the project is alive")


def check_findings(shard: dict, sheet=None, pid: str = "") -> list[dict]:
    """The same ref-encoding defect, in the records `check()` never sees.

    `check()` walks `fills[]`. A deep-sweep shard also carries `status_reviews[]`, and the
    merge runs the SAME `merge_qc.verified_refs` filter over its `proposed_refs`. (`validity[]`
    is deliberately NOT checked here: `merge_deepsweep_shards.py` carries a concern's
    `proposed_refs` through unfiltered, so an unverified validity ref is not dropped.)
    2026-09-15, Russia R1 pilot: P1783 and P4111 each staged two live,
    on-point status refs with `contains_value` left unset, and the merge stripped both and
    rewrote the verdict to `unclear`; P6710 proposed Status operating <- construction off
    four named outlets and staged no URL at all, same downgrade. None of it tripped the
    fills[] checks, because none of it is a fill.
    """
    out: list[dict] = []
    # validity[] shape (Russia R6 DEFECTS #2): the merge recovers these, but the agent is
    # still running and can write the contract's shape in place.
    for i, v in enumerate(shard.get("validity") or []):
        if not isinstance(v, dict):
            continue
        label = f"validity[{i}] ({v.get('concern_type') or v.get('verdict') or 'no verdict'})"
        why = []
        # an extra key is harmless; one holding what the contract field lacks is lost
        off = [k for k, want in (("summary", "recommendation"), ("evidence_refs", "proposed_refs"))
               if v.get(k) and not v.get(want)]
        if off:
            why.append(f"off-schema key(s) {', '.join(off)} carry what "
                       "recommendation / proposed_refs should — move them there")
        if not (v.get("verdict") or "").strip():
            why.append("no `verdict` (concern | confirmed)")
        if (v.get("verdict") or "").strip() == "concern" and not (
                v.get("recommendation") or "").strip():
            why.append("concern with an empty `recommendation` — say what the researcher "
                       "should do (the finding itself goes in researcher_notes)")
        gem = [str(u.get("url") if isinstance(u, dict) else u)
               for u in (v.get("proposed_refs") or []) + (v.get("evidence_refs") or [])
               if any(h in str(u.get("url") if isinstance(u, dict) else u).lower() for h in BLOCK)]
        if gem:
            why.append(f"GEM/banned ref(s) {', '.join(gem)} — never cite GEM (standing rule 1)")
        # a concern's candidate owner is a proposal too: never two names in one cell (Baird
        # 2026-10-16, P6584 `TC Offshore / Kinetica Deepwater Express`)
        held = []
        for c, cv in (v.get("contested") or {}).items():
            sv = str(cv or "").strip()
            if not re.fullmatch(r"Owner\d+|Operator", str(c)) or not sv:
                continue
            st = _owner_style(sv)
            if st is not None and {"multi_owner", "slash"} & set(st.flags) and st.basis != "ruling":
                held.append(f"{c}: {sv!r}")
        if held:
            why.append("contested owner candidate(s) " + "; ".join(held) + " hold two names in one "
                       "cell — split into two owners or pick the accurate one")
        if why:
            out.append({"ref_col": label, "why": "; ".join(why)})
    for i, s in enumerate(shard.get("status_reviews") or []):
        if not isinstance(s, dict):
            continue
        off = [k for k in ("recommended_status", "recommended_fields") if k in s]
        if off:
            out.append({"ref_col": f"status_reviews[{i}]",
                        "why": f"off-schema key(s) {', '.join(off)} — use proposed_status / "
                               "proposed_changes {column: value}"})
        verdict = str(s.get("verdict") or "").strip().lower()
        label = f"status_reviews[{i}] ({verdict or 'no verdict'})"
        refs = [str(u or "").strip() for u in (s.get("proposed_refs") or []) if str(u or "").strip()]
        vers = [v for v in (s.get("verifications") or []) if isinstance(v, dict)]
        if verdict == "confirm" and str(s.get("current_status") or "").strip().lower() == "proposed":
            msg = _aged_proposed(s, sheet, pid)
            if msg:
                out.append({"ref_col": label, "why": msg})
        # Status is a controlled value: only the tracker's own words, never a source's label
        # (Baird 2026-10-16, P7825: EIA's "Applied" was staged as the proposed status).
        pc0 = s.get("proposed_changes") or s.get("values") or {}
        bad = sorted({str(x).strip() for x in (s.get("proposed_status"), pc0.get("Status"))
                      if str(x or "").strip() and str(x).strip() not in STATUS_DATE_COL})
        if bad:
            out.append({"ref_col": label,
                        "why": f"status {', '.join(map(repr, bad))} is not a tracker status "
                               f"({', '.join(sorted(STATUS_DATE_COL))}) -- a source's label such as EIA's "
                               "'Applied' or 'Approved' is evidence, not a value; stage the tracker status "
                               "(the sheet's current one when nothing changes)"})
        if verdict == "change":
            pc = s.get("proposed_changes") or s.get("values") or {}
            new_status = str(s.get("proposed_status") or pc.get("Status") or "").strip().lower()
            dcol = STATUS_DATE_COL.get(new_status)
            if dcol and not str(pc.get(dcol) or "").strip() and not DATE_NOT_FOUND.search(
                    str(s.get("researcher_notes") or "")):
                out.append({"ref_col": label,
                            "why": f"a change to {new_status} with no {dcol} in proposed_changes -- stage the "
                                   "year (and the month when the source gives it) the refs state for the event, or "
                                   "say in researcher_notes that the date was not found"})
        if not refs:
            # A `confirm` may legitimately rest on the fills' own refs; a verdict that MOVES
            # the sheet may not -- merge QC rewrites it to `unclear` and the change is lost.
            if verdict in {"change", "stale"} or any(
                    str(v).strip() for v in (s.get("values") or {}).values()):
                out.append({"ref_col": label,
                            "why": "a status verdict that changes the sheet with no "
                                   "`proposed_refs` — merge QC rewrites it to `unclear` and "
                                   "the proposed change never reaches the workbook; stage the "
                                   "URLs the notes name, verified"})
            continue
        good = [v for v in vers if v.get("ok") and v.get("contains_value")
                and str(v.get("url") or "").strip() in set(refs)]
        if not vers:
            out.append({"ref_col": label,
                        "why": "status refs with no `verifications` — the merge strips every "
                               "one and downgrades the verdict; write one {url, ok, "
                               "contains_value, name_found, note} per proposed ref"})
        elif not good:
            out.append({"ref_col": label,
                        "why": "no verification says ok+contains_value for a proposed status "
                               "ref — the merge strips every ref and downgrades the verdict "
                               "(a missing `contains_value` key reads as false)"})
    return out


def run_one(staging: Path, pid: str) -> dict:
    path = staging / "rows" / f"{pid}.json"
    units = load_units(staging).get(pid, [])
    if not path.exists():
        return {"pid": pid, "error": f"no shard at {path}", "units": len(units)}
    try:
        shard = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return {"pid": pid, "error": f"shard does not parse: {e}", "units": len(units)}
    records = list(shard.get("fills") or [])
    # A staging dir may carry a SEPARATE refs leg (`ref_shards/<PID>.json`, `resolutions[]`)
    # that covered the MISSING_REF units before the deep sweep ran — tx-operating does.
    # Ignoring it would report every one of those units as never worked and send a recovery
    # pass to redo research that is already staged.
    for sub in ("ref_shards", "ref_shards_recovery"):
        ref_shard = staging / sub / f"{pid}.json"
        if not ref_shard.exists():
            continue
        try:
            # The refs leg's schema carries no `values` — it confirms the value already on
            # the sheet, and merge_ref_shards.py applies its refs onto the seeded record that
            # holds it. Tag the origin so the "sourced but no values" rule below, which is
            # about deep-sweep fills[], does not fire on every one of them.
            records += [dict(r, _leg="refs")
                        for r in (json.loads(ref_shard.read_text()).get("resolutions") or [])]
        except json.JSONDecodeError as e:
            return {"pid": pid, "error": f"{sub}/{pid}.json does not parse: {e}",
                    "units": len(units)}
    unreported, silent, malformed = check(units, records, load_scope_sheet(staging), pid)
    malformed += check_findings(shard, load_scope_sheet(staging), pid)
    wiki_gaps, wiki_enforced = check_wiki_reads(staging, pid, shard)
    return {
        "pid": pid, "units": len(units), "fills": len(records),
        "unreported": [{"ref_col": u.get("ref_col"), "class": u.get("class"),
                        "sheet_row": u.get("sheet_row"),
                        "primary_value": u.get("primary_value")} for u in unreported],
        "silent_unresolved": [f.get("ref_col") for f in silent],
        "unmergeable": malformed,
        "wiki_unread": wiki_gaps if wiki_enforced else [],
        "wiki_unread_legacy": [] if wiki_enforced else wiki_gaps,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--pid", help="check one shard (what a subagent runs)")
    ap.add_argument("--all", action="store_true", help="check every shard in <staging>/rows/")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    staging = Path(a.staging)
    if not (a.pid or a.all):
        ap.error("pass --pid <PID> or --all")

    if a.all:
        pids = sorted(p.stem for p in (staging / "rows").glob("*.json"))
    else:
        pids = [a.pid]
    out = [run_one(staging, p) for p in pids]

    if a.json:
        print(json.dumps(out, indent=1))
    bad = [r for r in out if r.get("error") or r["unreported"] or r["silent_unresolved"]
           or r["unmergeable"] or r["wiki_unread"]]
    if not a.json:
        for r in out:
            if r.get("error"):
                print(f"FAIL {r['pid']}: {r['error']}")
                continue
            if r["wiki_unread_legacy"] and not a.all:
                print(f"WARN {r['pid']}: shard predates wiki_citations_read; "
                      f"{len(r['wiki_unread_legacy'])} harvested wiki citation(s) not accounted for.")
            if not r["unreported"] and not r["silent_unresolved"] and not r["unmergeable"] \
                    and not r["wiki_unread"]:
                if not a.all:
                    print(f"OK — {r['pid']}: all {r['units']} worklist unit(s) reported "
                          f"({r['fills']} fills[] object(s)).")
                continue
            parts = []
            if r["unreported"]:
                parts.append(f"{len(r['unreported'])} of {r['units']} worklist unit(s) "
                             f"have NO fills[] object")
            if r["unmergeable"]:
                parts.append(f"{len(r['unmergeable'])} record(s) cannot be merged")
            if r["silent_unresolved"]:
                parts.append(f"{len(r['silent_unresolved'])} UNRESOLVED with no notes")
            if r["wiki_unread"]:
                parts.append(f"{len(r['wiki_unread'])} harvested wiki citation(s) not accounted for")
            print(f"FAIL {r['pid']}: " + "; ".join(parts) + ".")
            for u in r["unreported"]:
                val = u["primary_value"]
                if u["class"] == "MISSING_REF":
                    hint = (f"sheet already has {val!r} — find the source that states it, "
                            f"emit REFS_ADDED")
                elif u["class"] == "MISSING_VALUE":
                    hint = "blank cell — fill it or say what you searched"
                else:                                    # HAS_REF — re-verify, don't refill
                    hint = (f"value {val!r} is already cited — re-verify the ref and emit "
                            f"REVERIFIED, DEAD_LINK only on a confirmed 404/410, or REF_UNSUPPORTED when the page loads but does not state it")
                print(f"     {u['ref_col']:24s} [{u['class']}] {hint}")
            for m in r["unmergeable"]:
                print(f"     {str(m['ref_col'] or '(none)'):24s} [UNMERGEABLE] {m['why']} "
                      f"— the research is done, re-key the record, do not redo it")
            for c in r["silent_unresolved"]:
                print(f"     {c:24s} [UNRESOLVED with empty researcher_notes — say what you searched]")
            for w in r["wiki_unread"]:
                print(f"     [WIKI] {w['cite'][:90]} — {w['why']}; open it and save "
                      f"shard_upsert.py --wiki-read")
        if a.all:
            n = sum(len(r.get("unreported") or []) for r in out)
            s = sum(len(r.get("silent_unresolved") or []) for r in out)
            m = sum(len(r.get("unmergeable") or []) for r in out)
            w = sum(len(r.get("wiki_unread") or []) for r in out)
            lw = sum(len(r.get("wiki_unread_legacy") or []) for r in out)
            print(f"\n{len(out)} shard(s): {len(bad)} with gaps — "
                  f"{n} unreported unit(s), {m} unmergeable record(s), {s} silent UNRESOLVED, "
                  f"{w} wiki citation(s) not accounted for."
                  + (f" ({lw} more on shards that predate wiki_citations_read, not blocking.)" if lw else ""))
            if not bad:
                print("OK — every worklist unit is reported on in every shard.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
