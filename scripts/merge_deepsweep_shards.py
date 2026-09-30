#!/usr/bin/env python3
"""Merge critical-deep-sweep shards (rows/<PID>.json) onto the preserved ref-sweep work.

The `critical-deep-sweep` workflow writes one shard per pipeline under <staging>/rows/.
This folds them into staged_resolutions.json:

- Preserve every genuine ref record from the prior staged_resolutions.json
  (class_in HAS_REF / MISSING_REF and their class_out) — the ref sweep is not redone.
- Drop any OLD FILL / VALIDITY / STATUS / ROUTE records (this fresh critical pass supersedes them).
- Convert each shard's validity[] -> __VALIDITY__ records, fills[] -> FILL records,
  routes[] -> __ROUTE__ records, and (annual-update mode) status_reviews[] -> __STATUS__
  records, applying merge-time QC
  (strip refs that did not pass verification; downgrade to UNRESOLVED; a status "change"
  with zero verified refs -> "unclear"; a "stale" shelved/cancelled inference always gets
  ShelvedCancelledType=inferred).
- Recompute meta (verdict / concern / class / status-verdict counts); write staged_resolutions.json.

Run AFTER the workflow completes and BEFORE build_ref_workbook.py.
Expects a prior ref-sweep staged_resolutions.json; if only staged_resolutions.json exists
it is snapshotted to staged_resolutions.prior.json on first run.

Usage:
    python scripts/merge_deepsweep_shards.py --staging batches/saudi-arabia-gas/staging/ref-sweep/
"""
import argparse, json, os, collections, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_qc import (bad_cost_units, verified_refs, iter_shards, qc_note,  # noqa: E402
                      status_qc, is_ref_only, independence_qc, relevance_qc, BLOCK,
                      validated_tier, is_status_change, STATUS_CHANGE_MIN_PUBLISHERS,
                      load_sheet, sheet_value, off_schema_keys)


# A status_reviews[] record states the proposed status under whichever of these the
# subagent reached for. Only the first is the contract; the rest are forms shards
# actually wrote (Russia R3 P4149 used `candidate_value`/`current_value` throughout).
# An unrecognized key is not a missing finding — it is a finding that reaches no paste
# surface, the same defect class as R2's owner FILL that no tab drew.
PROPOSED_STATUS_KEYS = ("proposed_status", "candidate_value", "candidate_status",
                        "proposed_value", "recommended_status")
CURRENT_STATUS_KEYS = ("current_status", "current_value")


def first_key(s, keys):
    """The first of `keys` the record actually carries a non-empty value under."""
    for k in keys:
        v = s.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def status_changes(s, notes):
    """`status_reviews[].proposed_changes` is a {column: new value} map, but a shard
    occasionally writes the COLUMN NAMES alone (Russia R3 P4085: `["Status"]`), which
    used to kill the whole merge in `status_qc`'s `dict(changes)` with a ValueError
    naming no PID, or omits the map entirely while stating the new status in prose +
    a `proposed_status`-ish key (R3 P4109, P4149). One malformed record must not cost
    26 good shards a merge, and a `change` verdict whose value never lands in
    `values{}` is invisible on the Backend paste surface — the researcher sees a row
    flagged as changed with nothing to paste. Both are recoverable from the proposed
    status the record does carry; anything else named without a value is dropped with
    a QC note rather than guessed.

    Returns (changes, notes).
    """
    raw = s.get("proposed_changes")
    if isinstance(raw, dict) and raw:
        return dict(raw), notes
    # Russia R6 P4056/P4110 wrote the map as `recommended_fields` (with `recommended_status`)
    alt = s.get("recommended_fields")
    if not raw and isinstance(alt, dict) and alt:
        return dict(alt), qc_note(notes, "proposed_changes read from off-schema "
                                         "`recommended_fields`.")
    if raw is None or (isinstance(raw, dict) and not raw):
        proposed = first_key(s, PROPOSED_STATUS_KEYS)
        current = first_key(s, CURRENT_STATUS_KEYS)
        if proposed and proposed.lower() != current.lower():
            return ({"Status": proposed},
                    qc_note(notes, f"proposed_changes was empty; recovered Status="
                                   f"{proposed!r} from the record's own proposed status."))
        return {}, notes
    if not isinstance(raw, (list, tuple)):
        return {}, qc_note(notes, f"proposed_changes was {type(raw).__name__}, not a "
                                  "{column: value} map — dropped.")
    out, dropped = {}, []
    for item in raw:
        if isinstance(item, dict):
            out.update(item)
        elif isinstance(item, str) and item.strip() == "Status" and s.get("proposed_status"):
            out["Status"] = s["proposed_status"]
        elif isinstance(item, str) and item.strip():
            dropped.append(item.strip())
    if out or dropped:
        recovered = ", ".join(sorted(out)) or "none"
        note = (f"proposed_changes was a list of column names, not a {{column: value}} "
                f"map; recovered from proposed_status: {recovered}")
        if dropped:
            note += f"; dropped (no value stated): {', '.join(dropped)}"
        notes = qc_note(notes, note + ".")
    return out, notes


def clean_refs(raw):
    """URLs from a record's ref list, minus GEM / banned hosts and non-URLs. Validity refs
    are carried unfiltered by verification (a concern may rest on a page that does not
    contain a sheet value), but never a GEM surface (standing rule 1) — R6 P4056/P4110 put
    gem.wiki in `evidence_refs`. Tolerates [{url: ...}] as well as bare strings."""
    out, dropped = [], []
    for u in raw or []:
        if isinstance(u, dict):
            u = u.get("url") or ""
        u = str(u or "").strip()
        if not u:
            continue
        if not u.lower().startswith("http") or any(h in u.lower() for h in BLOCK):
            dropped.append(u)
        elif u not in out:
            out.append(u)
    return out, dropped


def normalize_validity(v):
    """A validity[] record in whichever shape the agent wrote -> the contract's fields.

    R6 P4056/P4110 wrote `summary` / `severity` / `evidence_refs` with no `verdict` and the
    merge staged verdict-'' concerns with an empty Recommendation (DEFECTS #2). Recover:
    `summary` -> `recommendation`, `evidence_refs` -> `proposed_refs`, `notes` ->
    `researcher_notes`, and a missing verdict from `concern_type`: `concern` when it names a
    concern, `confirmed` when it says there is none (`none`, `existence_confirmed`, or
    severity `info` — R1/R3 wrote both shapes).
    Returns (verdict, recommendation, notes, refs, n_fixes)."""
    fixes = []
    notes = v.get("researcher_notes") or v.get("notes", "")
    rec = (v.get("recommendation") or "").strip()
    if not rec and (v.get("summary") or "").strip():
        rec = v["summary"].strip()
        fixes.append("recommendation read from off-schema `summary`")
    verdict = (v.get("verdict") or "").strip()
    ctype = (v.get("concern_type") or "").strip().lower()
    if not verdict and ctype:
        none = ctype == "none" or "confirm" in ctype or \
            str(v.get("severity") or "").strip().lower() == "info"
        verdict = "confirmed" if none else "concern"
        fixes.append(f"verdict was empty with concern_type {ctype!r} -> {verdict}")
    raw = v.get("proposed_refs")
    if not raw and v.get("evidence_refs"):
        raw = v["evidence_refs"]
        fixes.append("refs read from off-schema `evidence_refs`")
    refs, dropped = clean_refs(raw)
    if dropped:
        fixes.append(f"dropped {len(dropped)} GEM/banned/non-URL ref(s): {', '.join(dropped)}")
    if fixes:
        notes = qc_note(notes, "; ".join(fixes) + ".")
    return verdict, rec, notes, refs, len(fixes)


def screen_value_keys(values, sheet, notes, what="values", ref_col=None):
    """Rename or drop `values{}` keys that reach no paste surface (merge_qc.off_schema_keys),
    returning (values, notes, off-schema keys). R6's
    Novosibirsk–Barnaul agent keyed values by ref-column stems (`Owner`, `Start`,
    `Construction`) and the merge staged them as fills of columns that do not exist
    (DEFECTS #4). The research is kept in the notes; the key never reaches a paste surface."""
    off = off_schema_keys(sheet, ref_col, values)
    if not off:
        return values, notes, []
    bad = list(off)
    kept = {k: v for k, v in values.items() if k not in off}
    # The usual slip is the ref column's own stem (`Owner` under `Owner [ref]`, `Start`,
    # `Operator1`): that is the pair's primary column, and R6's hand-fix renamed it so.
    # Location is excluded — its stem could mean either end.
    stem = (ref_col or "").removesuffix(" [ref]")
    prim = sheet.primary.get(ref_col or "")
    msgs = []
    if prim and stem != "Location" and prim not in kept:
        hit = [k for k in bad if k == stem or k.rstrip("0123456789") == stem]
        if len(hit) == 1:
            kept[prim] = values[hit[0]]
            bad.remove(hit[0])
            msgs.append(f"renamed {what} key {hit[0]!r} -> {prim!r}")
    if bad:
        lost = ", ".join(f"{k}={values[k]!r}" for k in bad)
        msgs.append(f"dropped {what} key(s) with no cell on this record's paste surface: {lost}")
    return kept, qc_note(notes, "; ".join(msgs) + "."), off


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    args = ap.parse_args()
    S = args.staging.rstrip("/")

    prior_path = os.path.join(S, "staged_resolutions.prior.json")
    cur_path = os.path.join(S, "staged_resolutions.json")
    if not os.path.exists(prior_path):
        if not os.path.exists(cur_path):
            raise SystemExit(f"no staged_resolutions.json or .prior.json in {S}")
        # snapshot the ref-sweep output as the preserved baseline
        json.dump(json.load(open(cur_path)), open(prior_path, "w"), indent=1)
        print(f"snapshotted {cur_path} -> {prior_path}")

    # The snapshot is the baseline, so a LATER re-seed never reaches the merged output --
    # which is exactly how a fix to seed_resolutions_from_worklist.py (`link_live` losing its
    # HTTP status) survived a --force re-seed and three merges unnoticed (2026-08-27, Egypt).
    # Re-seeding is the normal way to pick up a worklist repair, so say so rather than
    # silently preferring the stale file; refresh with:  cp staged_resolutions.json prior
    if os.path.exists(cur_path) and os.path.getmtime(cur_path) > os.path.getmtime(prior_path) + 1:
        print(f"  WARN {cur_path} is NEWER than {prior_path} -- merging the OLDER snapshot. "
              "If you just re-seeded, copy it over the .prior.json first.")

    prior = json.load(open(prior_path))
    meta = dict(prior.get("meta", {}))
    res = prior["resolutions"]
    sheet = load_sheet(meta.get("scope"))
    if sheet is None:
        print("  WARN snapshot named in meta.scope not found -- value keys are NOT screened "
              "against sheet columns and UNRESOLVED fills keep their values")
    n_badkeys = n_reset = n_vnorm = 0

    def is_old_deepsweep(r):
        # `leg == "refs"` marks a FILL that merge_ref_shards.py appended for a MISSING_VALUE
        # unit the seed never staged (see its fallback). It is the refs leg's own output, not
        # a stale copy of this leg's, so this purge — which exists to stop deep-sweep records
        # accumulating across re-runs — must not take it (2026-09-09: it silently dropped all
        # five the US gas recovery pass had just rescued).
        if r.get("leg") == "refs":
            return False
        return (r.get("class_in") in ("FILL", "VALIDITY", "STATUS", "ROUTE")
                or r.get("ref_col") in ("__VALIDITY__", "__STATUS__", "__ROUTE__"))

    kept = [r for r in res if not is_old_deepsweep(r)]

    # Index the preserved ref records so a shard fill that proposes exactly the value
    # already on the sheet can be folded onto its ref record (ref-only work) instead of
    # being staged as a FILL. See merge_qc.is_ref_only — a FILL tints the value cell on
    # the paste surface, which would tell the researcher to paste unchanged values.
    ref_by_key = {}
    for r in kept:
        for row in {str(r.get("sheet_row", "")), str(r.get("oo_sheet_row") or "")} - {""}:
            ref_by_key.setdefault((r.get("project_id"), row, r.get("ref_col", "")), r)
    # Row-agnostic fallback: owner/operator units live on the operators/owners tab and
    # subagents report ITS row (oo_sheet_row), which the seeded record does not carry —
    # so the row never matches. Fall back on (ProjectID, ref_col) only when exactly one
    # kept record has that pair, so a multi-segment row can never fold onto the wrong one.
    _by_pid_col = collections.defaultdict(list)
    for r in kept:
        _by_pid_col[(r.get("project_id"), r.get("ref_col", ""))].append(r)
    ref_by_pid_col = {k: v[0] for k, v in _by_pid_col.items() if len(v) == 1}
    n_refonly = 0

    n_shards = 0
    new_validity, new_fills, new_status, new_routes, missing = [], [], [], [], []

    pid_set = {r.get("project_id") for r in res}
    seen_shard_pids = set()
    for p, d in iter_shards(os.path.join(S, "rows", "*.json")):
        n_shards += 1
        pid = d.get("project_id") or os.path.basename(p)[:-5]
        seen_shard_pids.add(pid)
        ident = {"project_id": pid, "pipeline_name": d.get("pipeline_name", ""),
                 "wiki": d.get("wiki", "")}
        for v in d.get("validity", []) or []:
            # agents sometimes write the finding under `notes` (R5 Volga: 7 shards) or a
            # whole alternative shape (R6) — normalize rather than ship a blank Finding cell
            v_verdict, v_rec, v_notes, v_refs, fixed = normalize_validity(v)
            n_vnorm += bool(fixed)
            if v_verdict == "concern" and not v_rec:
                print(f"  WARN {pid} validity {v.get('concern_type', '')}: concern with an empty "
                      "recommendation (fix the shard)")
            contested, v_notes, bad = screen_value_keys(
                v.get("contested") or {}, sheet, v_notes, "contested")
            n_badkeys += len(bad)
            v_tier, v_indep, v_notes = independence_qc(
                v_refs, v.get("tier", ""), v.get("independent", False), v_notes)
            new_validity.append({**ident,
                "sheet_row": d.get("sheet_row", ""),
                "segment_name": v.get("segment_name", ""),
                "ref_col": "__VALIDITY__", "value_cols": [], "primary_value_col": None,
                "values": {}, "primary_value": "", "current_ref": "",
                "class_in": "VALIDITY", "class_out": "UNRESOLVED",
                "verdict": v_verdict, "concern_type": v.get("concern_type", ""),
                "recommendation": v_rec,
                "researcher_notes": v_notes,
                "proposed_refs": v_refs,
                "verifications": v.get("verifications", []) or [],
                "tier": v_tier, "independent": v_indep,
                # `contested` is what puts a concern on the Backend paste surface and
                # `promoted_from` is what ranks a researched finding above the ref-pass
                # echo of it — both are authored in the shard, so the merge must carry
                # them or the deliverable silently loses the orange marking entirely
                "contested": contested,
                "promoted_from": v.get("promoted_from", ""),
                "source_language": v.get("source_language", "en")})
        for f in d.get("fills", []) or []:
            refs = verified_refs(f.get("proposed_refs", []), f.get("verifications", []))
            notes = f.get("researcher_notes", "")
            cls = f.get("class_out", "UNRESOLVED")
            if f.get("proposed_refs") and not refs:
                cls = "UNRESOLVED"; notes = qc_note(notes, "dropped unverified ref(s).")
            # a proposed Status change stays green only on 2+ independent publishers
            f_stchg = is_status_change(f.get("values"), sheet, pid,
                                       f.get("sheet_row", d.get("sheet_row", "")))
            f_tier, f_indep, notes = independence_qc(
                refs, f.get("tier", ""), f.get("independent", False), notes,
                high_min=STATUS_CHANGE_MIN_PUBLISHERS if f_stchg else 1)
            if refs:
                f_tier, notes = relevance_qc(f.get("verifications", []), f_tier, notes)
                if not f_stchg:
                    f_tier, notes = validated_tier(refs, f.get("verifications", []),
                                                   f_tier, notes)
            f_values, notes, bad = screen_value_keys(f.get("values") or {}, sheet, notes,
                                                     ref_col=f.get("ref_col"))
            n_badkeys += len(bad)
            f_row = f.get("sheet_row", d.get("sheet_row", ""))
            # An UNRESOLVED record states no sourced value, so it must carry the SHEET's
            # value: a proposal left in `values` lands tinted on the paste surface as if it
            # were researched (R6 P2705 Status shelved, P3604 locations — DEFECTS #5). The
            # proposal survives in the notes.
            if cls == "UNRESOLVED" and sheet is not None:
                changed = {}
                for col, val in list(f_values.items()):
                    cur = sheet_value(sheet, pid, f_row, col)
                    if cur is None:
                        continue
                    if is_ref_only({col: val}, {col: cur}) or \
                            str(val or "").strip() == str(cur or "").strip():
                        continue
                    changed[col] = val
                    f_values[col] = cur
                if changed:
                    n_reset += 1
                    notes = qc_note(notes, "UNRESOLVED record proposed " + ", ".join(
                        f"{k}={v!r}" for k, v in changed.items())
                        + " with no sourced ref; values reset to the sheet's (proposal kept here).")
            for col, val in bad_cost_units(f.get("values")).items():
                print(f"  WARN {pid} {f.get('ref_col', '')}: {col}={val!r} — units must be "
                      "a bare currency code; put the magnitude in the cost number (fix the shard)")
            # ref-only work: the agent sourced a value that is already on the sheet ->
            # upgrade the existing ref record in place rather than staging a value change.
            rk = (pid, str(f.get("sheet_row", d.get("sheet_row", ""))), f.get("ref_col", ""))
            base = ref_by_key.get(rk) or ref_by_pid_col.get((pid, f.get("ref_col", "")))
            if base is not None and is_ref_only(f_values, base.get("values")):
                base["class_out"] = "REFS_ADDED" if refs else "UNRESOLVED"
                base["proposed_refs"] = refs
                base["verifications"] = f.get("verifications", []) or []
                base["tier"] = f_tier
                base["independent"] = f_indep
                base["source_language"] = f.get("source_language", "en")
                base["researcher_notes"] = notes
                n_refonly += 1
                continue
            new_fills.append({**ident,
                "sheet_row": f.get("sheet_row", d.get("sheet_row", "")),
                "segment_name": f.get("segment_name", ""),
                "ref_col": f.get("ref_col", ""), "value_cols": f.get("value_cols", []),
                "primary_value_col": f.get("primary_value_col", ""),
                "values": f_values,
                "primary_value": f_values.get(f.get("primary_value_col") or "",
                                              f.get("primary_value", "")),
                "current_ref": "", "class_in": "FILL", "class_out": cls,
                "proposed_refs": refs, "verifications": f.get("verifications", []) or [],
                "tier": f_tier, "independent": f_indep,
                "source_language": f.get("source_language", "en"), "researcher_notes": notes})
        for s in d.get("status_reviews", []) or []:
            refs = verified_refs(s.get("proposed_refs", []), s.get("verifications", []))
            notes = s.get("researcher_notes", "")
            if s.get("proposed_refs") and not refs:
                notes = qc_note(notes, "dropped unverified ref(s).")
            changes, notes = status_changes(s, notes)
            changes, notes, bad = screen_value_keys(changes, sheet, notes, "proposed_changes")
            n_badkeys += len(bad)
            verdict, changes, cls, notes = status_qc(
                s.get("verdict"), changes, refs, notes)
            s_chg = verdict == "change"
            s_tier, s_indep, notes = independence_qc(
                refs, s.get("tier", ""), s.get("independent", False), notes,
                high_min=STATUS_CHANGE_MIN_PUBLISHERS if s_chg else 1)
            if refs and not s_chg:
                s_tier, notes = validated_tier(refs, s.get("verifications", []), s_tier, notes)
            new_status.append({**ident,
                "sheet_row": s.get("sheet_row", d.get("sheet_row", "")),
                "segment_name": s.get("segment_name", ""),
                "ref_col": "__STATUS__", "value_cols": list(changes.keys()),
                "primary_value_col": "Status", "values": changes,
                "primary_value": changes.get("Status", s.get("current_status", "")),
                "current_ref": "", "class_in": "STATUS", "class_out": cls,
                "current_status": first_key(s, CURRENT_STATUS_KEYS), "verdict": verdict,
                "proposed_status": first_key(s, PROPOSED_STATUS_KEYS),
                "evidence_date": s.get("evidence_date", ""),
                "staleness_rule": s.get("staleness_rule", ""),
                "proposed_refs": refs, "verifications": s.get("verifications", []) or [],
                "tier": s_tier, "independent": s_indep,
                "source_language": s.get("source_language", "en"), "researcher_notes": notes})

        for rt in d.get("routes", []) or []:
            refs = verified_refs(rt.get("proposed_refs", []), rt.get("verifications", []))
            notes = rt.get("researcher_notes", "")
            if rt.get("proposed_refs") and not refs:
                notes = qc_note(notes, "dropped unverified ref(s).")
            # coordinates are never fabricated (standing rule 2): a suggestion with both
            # endpoints coordinated is SUGGESTED; a corridor-only one (missing coords) is PARTIAL.
            has_coords = all(rt.get(k) is not None for k in ("start_lat", "start_lon", "end_lat", "end_lon"))
            rt_tier, rt_indep, notes = independence_qc(
                refs, rt.get("tier", ""), rt.get("independent", False), notes)
            new_routes.append({**ident,
                "sheet_row": rt.get("sheet_row", d.get("sheet_row", "")),
                "segment_name": rt.get("segment_name", ""),
                "ref_col": "__ROUTE__", "value_cols": [], "primary_value_col": None,
                "values": {}, "primary_value": "", "current_ref": "",
                "class_in": "ROUTE", "class_out": "ROUTE_SUGGESTED" if has_coords else "ROUTE_PARTIAL",
                "start_name": rt.get("start_name", ""), "start_lat": rt.get("start_lat"),
                "start_lon": rt.get("start_lon"), "end_name": rt.get("end_name", ""),
                "end_lat": rt.get("end_lat"), "end_lon": rt.get("end_lon"),
                "waypoints": rt.get("waypoints", []) or [], "waypoint_note": rt.get("waypoint_note", ""),
                "corridor_desc": rt.get("corridor_desc", ""),
                "current_route_accuracy": rt.get("current_route_accuracy", ""),
                "suggested_route_accuracy": rt.get("suggested_route_accuracy", ""),
                "proposed_refs": refs, "verifications": rt.get("verifications", []) or [],
                "tier": rt_tier, "independent": rt_indep,
                "source_language": rt.get("source_language", "en"), "researcher_notes": notes})

    for pid in sorted(pid_set):
        if pid and pid not in seen_shard_pids:
            missing.append(pid)

    merged = kept + new_status + new_fills + new_validity + new_routes
    meta["n_units"] = len(merged)
    meta["class_out_counts"] = dict(collections.Counter(r.get("class_out") for r in merged))
    meta["class_in_counts"] = dict(collections.Counter(r.get("class_in") for r in merged))
    if "ref_class_out_counts" in meta:
        # merge_ref_shards wrote this before the shards flipped HAS_REF/MISSING_REF
        # class_out (line above: REFS_ADDED/UNRESOLVED); refresh it or it goes stale
        # (Egypt 08-27 shipped 45/202/19 in meta against 46/202/18 in the records).
        meta["ref_class_out_counts"] = dict(collections.Counter(
            r.get("class_out") for r in merged if r.get("class_in") in ("HAS_REF", "MISSING_REF")))
    meta["n_validity_flags"] = len(new_validity)
    meta["n_fills"] = len(new_fills)
    meta["n_status_reviews"] = len(new_status)
    meta["n_route_suggestions"] = len(new_routes)
    meta["verdict_counts"] = dict(collections.Counter(r.get("verdict") for r in new_validity))
    meta["concern_counts"] = dict(collections.Counter(
        r.get("concern_type") for r in new_validity if r.get("verdict") == "concern"))
    meta["status_verdict_counts"] = dict(collections.Counter(r.get("verdict") for r in new_status))

    json.dump({"meta": meta, "resolutions": merged}, open(cur_path, "w"), indent=1)
    print(f"shards merged: {n_shards} | missing PIDs: {len(missing)} {missing if missing else ''}")
    if n_refonly:
        print(f"ref-only folds: {n_refonly} fill(s) proposed the value already on the sheet "
              "-> upgraded their ref record (colored [ref], untinted value)")
    print(f"kept ref records: {len(kept)} | new fills: {len(new_fills)} | new validity: {len(new_validity)}"
          + (f" | new routes: {len(new_routes)}" if new_routes else "")
          + (f" | new status reviews: {len(new_status)}" if new_status else ""))
    if n_badkeys or n_reset or n_vnorm:
        print(f"normalized: {n_badkeys} off-schema value key(s) renamed or dropped | {n_reset} UNRESOLVED "
              f"fill(s) reset to sheet values | {n_vnorm} off-schema validity record(s) "
              "(each noted [QC] in its record)")
    print(f"verdicts: {meta['verdict_counts']}")
    print(f"open concerns by type: {meta['concern_counts']}")
    if new_status:
        print(f"status verdicts: {meta['status_verdict_counts']}")


if __name__ == "__main__":
    main()
