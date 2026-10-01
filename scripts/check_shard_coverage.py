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


def _owner_style(name: str):
    """`entity_style.style(name)`, or None if the styler (or its data files) is unavailable —
    a missing gazetteer must not block a shard over a check it cannot run."""
    try:
        from entity_style import style
        return style(name)
    except Exception:       # pragma: no cover — data files absent on a bare checkout
        return None


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
        # `values{}` keys land in real cells: a key that is no backend / owners-tab column
        # (R6: `Owner`, `Start`, `Construction` -- ref-column stems) reaches no paste surface.
        if sheet is not None and f.get("_leg") != "refs":
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
            if (f.get("class_out") or "").upper() == "UNRESOLVED":
                row = f.get("sheet_row")
                moved = [c for c, v in (f.get("values") or {}).items()
                         if (cur := sheet_value(sheet, pid, row, c)) is not None
                         and str(v or "").strip() != str(cur or "").strip()
                         and not is_ref_only({c: v}, {c: cur})]
                if moved:
                    why.append(f"UNRESOLVED but `values` changes {', '.join(moved)} from the "
                               "sheet — an unsourced proposal belongs in researcher_notes; "
                               "set values to the sheet's")
        # A proposed Owner<N> name is written the way the ownership team writes it
        # (docs/reference/owner_style.md): trailing short legal form, no punctuation, no
        # trailing acronym, team spelling on an exact/alias gazetteer hit. A value equal to
        # the sheet's current cell is carried, not proposed, so it is not checked here.
        if f.get("_leg") != "refs" and (f.get("tab") == "operators_owners"
                                        or f.get("ref_col") == "Owner [ref]"):
            restyle = []
            for c, v in (f.get("values") or {}).items():
                sv = str(v or "").strip()
                if not re.fullmatch(r"Owner\d+", str(c)) or not sv:
                    continue
                cur = sheet_value(sheet, pid, f.get("sheet_row"), c) if sheet is not None else None
                if cur is not None and str(cur).strip() == sv:
                    continue
                st = _owner_style(sv)
                if st is not None and st.changed:
                    restyle.append(f"{c}: {sv!r} -> {st.styled!r}")
            if restyle:
                why.append("owner name(s) not in the ownership team's style — "
                           + "; ".join(restyle)
                           + " (use the styled form in `values`; keep the source's spelling "
                             "and any dropped acronym in researcher_notes)")
        if why:
            malformed.append({"ref_col": f.get("ref_col"), "why": "; ".join(why)})
    return unreported, silent, malformed


def check_findings(shard: dict) -> list[dict]:
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
    malformed += check_findings(shard)
    return {
        "pid": pid, "units": len(units), "fills": len(records),
        "unreported": [{"ref_col": u.get("ref_col"), "class": u.get("class"),
                        "sheet_row": u.get("sheet_row"),
                        "primary_value": u.get("primary_value")} for u in unreported],
        "silent_unresolved": [f.get("ref_col") for f in silent],
        "unmergeable": malformed,
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
           or r["unmergeable"]]
    if not a.json:
        for r in out:
            if r.get("error"):
                print(f"FAIL {r['pid']}: {r['error']}")
                continue
            if not r["unreported"] and not r["silent_unresolved"] and not r["unmergeable"]:
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
        if a.all:
            n = sum(len(r.get("unreported") or []) for r in out)
            s = sum(len(r.get("silent_unresolved") or []) for r in out)
            m = sum(len(r.get("unmergeable") or []) for r in out)
            print(f"\n{len(out)} shard(s): {len(bad)} with gaps — "
                  f"{n} unreported unit(s), {m} unmergeable record(s), {s} silent UNRESOLVED.")
            if not bad:
                print("OK — every worklist unit is reported on in every shard.")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
