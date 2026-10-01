#!/usr/bin/env python3
"""Fold targeted ref-sweep research shards onto the preserved ref baseline.

Companion to build_refsweep_briefs.py. Each research subagent writes
`<staging>/ref_shards/<PID>.json` with per-unit ref resolutions. This applies them onto
the ref records in staged_resolutions.prior.json (the baseline the deep-sweep merge
preserves), matching on (project_id, ref_col, sheet_row). It updates class_out /
proposed_refs / verifications / tier / independent / researcher_notes for matched units
and leaves every other record untouched.

Merge-time QC (same spirit as merge_deepsweep_shards.py) — never let an orphan or
unverified ref through:
- Keep only proposed_refs whose verification is ok && contains_value.
- REFS_ADDED / REVERIFIED with zero verified refs -> UNRESOLVED (MISSING_REF origin) or, for a
  HAS_REF origin, the class that says what happened to the link (`ref_classes.attention_class`:
  DEAD_LINK only for 404/410, REF_BLOCKED, REF_UNSUPPORTED); a note records the drop.
- A shard's own DEAD_LINK / REF_* label is re-derived from its verifications (`status`), so a
  page that loaded can never be staged as a dead link.
- GEM / blocklisted URLs are stripped (defense in depth; the verifier already rejects them).

Writes staged_resolutions.prior.json in place. Run AFTER research, BEFORE
merge_deepsweep_shards.py (which then re-folds validity/fills/status onto the refreshed
baseline). Idempotent: re-running with the same shards yields the same baseline.

Usage:
    python scripts/merge_ref_shards.py --staging batches/iraq-gas/staging/annual/
"""
import argparse, json, os, collections, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ref_classes import ATTENTION_SET, attention_class  # noqa: E402
from merge_qc import (verified_refs, iter_shards, qc_note, independence_qc,  # noqa: E402
                      relevance_qc, validated_tier)

_VALID_OUT = {"REFS_ADDED", "REVERIFIED", "UNRESOLVED"} | ATTENTION_SET


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    ap.add_argument("--shard-dir", action="append", dest="shard_dirs", metavar="DIR",
                    help="shard directory under --staging, repeatable; defaults to `ref_shards`. "
                         "A recovery pass writes `ref_shards_recovery/` rather than "
                         "`ref_shards/` so it cannot overwrite a shard from the original leg "
                         "(4 of tx's 41 would have been clobbered, 2026-09-09); merge both by "
                         "passing both.")
    args = ap.parse_args()
    S = args.staging.rstrip("/")
    # `action="append"` must not carry an argparse default: argparse appends onto the default
    # object itself, so a string default raises AttributeError and a list default silently
    # prepends `ref_shards` to every explicit set. Default here, after parsing, instead.
    dirs = args.shard_dirs or ["ref_shards"]

    prior_path = os.path.join(S, "staged_resolutions.prior.json")
    cur_path = os.path.join(S, "staged_resolutions.json")
    base_path = prior_path if os.path.exists(prior_path) else cur_path
    if not os.path.exists(base_path):
        raise SystemExit(f"no staged_resolutions(.prior).json in {S}")

    doc = json.load(open(base_path))
    res = doc["resolutions"]

    # index ref records by (pid, ref_col, sheet_row); fall back to (pid, ref_col)
    idx = {}
    for r in res:
        # FILL is here only so a re-run re-matches the records the MISSING_VALUE fallback
        # below appended, instead of appending them again. The fills leg's own FILL records
        # never reach this baseline — merge_deepsweep_shards.py adds those downstream, to
        # staged_resolutions.json, not to the .prior.json this script reads and writes.
        if r.get("class_in") not in ("HAS_REF", "MISSING_REF", "FILL"):
            continue
        idx[(r.get("project_id", ""), r.get("ref_col", ""), str(r.get("sheet_row", "")))] = r
        idx.setdefault((r.get("project_id", ""), r.get("ref_col", "")), r)

    # `MISSING_VALUE` units are never seeded into the store (seed_resolutions_from_worklist.py
    # only seeds MISSING_REF/HAS_REF), so a recovery pass that researches one has nothing to
    # match. Dropping it would silently re-lose exactly what gate J had just caught, so fall
    # back to the worklist and append the finding as a FILL record — the same shape
    # merge_deepsweep_shards.py produces for the fills leg.
    wl_by_key = {}
    wl_path = os.path.join(S, "worklist.json")
    if os.path.exists(wl_path):
        for u in json.load(open(wl_path)).get("units", []):
            wl_by_key.setdefault((u.get("project_id", ""), u.get("ref_col", "")), u)

    n_shards, applied, appended, unmatched, downgraded = 0, 0, 0, [], 0
    for p, d in iter_shards(*[os.path.join(S, sd, "*.json") for sd in dirs]):
        n_shards += 1
        pid = d.get("project_id") or os.path.basename(p)[:-5]
        for u in d.get("resolutions", []) or []:
            rc, sr = u.get("ref_col", ""), str(u.get("sheet_row", ""))
            r = idx.get((pid, rc, sr)) or idx.get((pid, rc))
            if not r:
                w = wl_by_key.get((pid, rc))
                if not w or w.get("class") != "MISSING_VALUE":
                    unmatched.append((pid, rc, sr)); continue
                r = {"project_id": pid, "pipeline_name": w.get("pipeline_name", ""),
                     "wiki": w.get("wiki", ""), "sheet_row": w.get("sheet_row", ""),
                     "segment_name": w.get("segment_name", ""), "ref_col": rc,
                     "value_cols": w.get("value_cols", []),
                     "primary_value_col": w.get("primary_value_col", ""),
                     "values": {}, "primary_value": "", "current_ref": "",
                     "class_in": "FILL", "leg": "refs"}
                if w.get("tab"):
                    r["tab"] = w["tab"]
                if w.get("oo_sheet_row"):
                    r["oo_sheet_row"] = w["oo_sheet_row"]
                vals = {k: v for k, v in (u.get("values") or {}).items() if str(v).strip()}
                if vals:
                    r["values"] = vals
                    r["primary_value"] = str(vals.get(r["primary_value_col"], "")) or ""
                res.append(r)
                idx[(pid, rc)] = r
                appended += 1

            verifs = u.get("verifications", []) or []
            refs = verified_refs(u.get("proposed_refs", []), verifs)
            cls = (u.get("class_out") or "").strip().upper()
            if cls not in _VALID_OUT:
                cls = "REFS_ADDED" if refs else "UNRESOLVED"
            notes = (u.get("researcher_notes") or "").strip()

            if cls in ATTENTION_SET:      # the label is a claim; the verifications decide it
                cls = attention_class(verifs or r.get("verifications"))
            if cls in ("REFS_ADDED", "REVERIFIED") and not refs:
                cls = (attention_class(list(verifs) + list(r.get("verifications") or []))
                       if r.get("class_in") == "HAS_REF" else "UNRESOLVED")
                notes = qc_note(notes, f"no verified corroborating ref -> {cls.lower()}.")
                downgraded += 1

            tier, indep, notes = independence_qc(
                refs, (u.get("tier") or "").strip().lower(),
                bool(u.get("independent", False)), notes)
            if refs:
                tier, notes = relevance_qc(verifs, tier, notes)
                tier, notes = validated_tier(refs, verifs, tier, notes, cls=cls)
            r["class_out"] = cls
            r["proposed_refs"] = refs
            r["verifications"] = verifs
            r["tier"] = tier
            r["independent"] = indep
            r["source_language"] = u.get("source_language", r.get("source_language", "en"))
            if notes:
                r["researcher_notes"] = notes
            r["ref_researched"] = True
            applied += 1

    meta = dict(doc.get("meta", {}))
    meta["ref_research_applied"] = applied
    meta["ref_class_out_counts"] = dict(collections.Counter(
        r.get("class_out") for r in res if r.get("class_in") in ("HAS_REF", "MISSING_REF")))
    json.dump({"meta": meta, "resolutions": res}, open(prior_path, "w"), indent=1, ensure_ascii=False)

    print(f"applied ref research to {applied} unit(s) across {n_shards} shard(s) -> {prior_path}")
    if downgraded:
        print(f"  QC downgraded {downgraded} unit(s) with no verified ref")
    if appended:
        print(f"  appended {appended} unseeded MISSING_VALUE unit(s) as new FILL record(s)")
    if unmatched:
        print(f"  WARN {len(unmatched)} shard unit(s) matched no baseline record: {unmatched[:8]}"
              + (" ..." if len(unmatched) > 8 else ""))
    print(f"  ref class_out now: {meta['ref_class_out_counts']}")


if __name__ == "__main__":
    main()
