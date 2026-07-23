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
- REFS_ADDED / REVERIFIED with zero verified refs -> UNRESOLVED (MISSING_REF origin) or
  DEAD_LINK (HAS_REF origin); a note records the drop.
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
from merge_qc import verified_refs, iter_shards, qc_note  # noqa: E402

_VALID_OUT = {"REFS_ADDED", "REVERIFIED", "DEAD_LINK", "UNRESOLVED"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    args = ap.parse_args()
    S = args.staging.rstrip("/")

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
        if r.get("class_in") not in ("HAS_REF", "MISSING_REF"):
            continue
        idx[(r.get("project_id", ""), r.get("ref_col", ""), str(r.get("sheet_row", "")))] = r
        idx.setdefault((r.get("project_id", ""), r.get("ref_col", "")), r)

    n_shards, applied, unmatched, downgraded = 0, 0, [], 0
    for p, d in iter_shards(os.path.join(S, "ref_shards", "*.json")):
        n_shards += 1
        pid = d.get("project_id") or os.path.basename(p)[:-5]
        for u in d.get("resolutions", []) or []:
            rc, sr = u.get("ref_col", ""), str(u.get("sheet_row", ""))
            r = idx.get((pid, rc, sr)) or idx.get((pid, rc))
            if not r:
                unmatched.append((pid, rc, sr)); continue

            verifs = u.get("verifications", []) or []
            refs = verified_refs(u.get("proposed_refs", []), verifs)
            cls = (u.get("class_out") or "").strip().upper()
            if cls not in _VALID_OUT:
                cls = "REFS_ADDED" if refs else "UNRESOLVED"
            notes = (u.get("researcher_notes") or "").strip()

            if cls in ("REFS_ADDED", "REVERIFIED") and not refs:
                cls = "DEAD_LINK" if r.get("class_in") == "HAS_REF" else "UNRESOLVED"
                notes = qc_note(notes, f"no verified corroborating ref -> {cls.lower()}.")
                downgraded += 1

            r["class_out"] = cls
            r["proposed_refs"] = refs
            r["verifications"] = verifs
            r["tier"] = (u.get("tier") or "").strip().lower()
            r["independent"] = bool(u.get("independent", False))
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
    if unmatched:
        print(f"  WARN {len(unmatched)} shard unit(s) matched no baseline record: {unmatched[:8]}"
              + (" ..." if len(unmatched) > 8 else ""))
    print(f"  ref class_out now: {meta['ref_class_out_counts']}")


if __name__ == "__main__":
    main()
