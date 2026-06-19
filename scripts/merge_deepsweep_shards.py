#!/usr/bin/env python3
"""Merge critical-deep-sweep shards (rows/<PID>.json) onto the preserved ref-sweep work.

The `critical-deep-sweep` workflow writes one shard per pipeline under <staging>/rows/.
This folds them into staged_resolutions.json:

- Preserve every genuine ref record from the prior staged_resolutions.json
  (class_in HAS_REF / MISSING_REF and their class_out) — the ref sweep is not redone.
- Drop any OLD FILL / VALIDITY records (this fresh critical pass supersedes them).
- Convert each shard's validity[] -> __VALIDITY__ records and fills[] -> FILL records,
  applying merge-time QC (strip refs that did not pass verification; downgrade to UNRESOLVED).
- Recompute meta (verdict / concern / class counts); write staged_resolutions.json.

Run AFTER the workflow completes and BEFORE build_ref_workbook.py.
Expects a prior ref-sweep staged_resolutions.json; if only staged_resolutions.json exists
it is snapshotted to staged_resolutions.prior.json on first run.

Usage:
    python scripts/merge_deepsweep_shards.py --staging batches/staging/ref-sweep-gas-saudi-arabia/
"""
import argparse, json, glob, os, collections


def _verified(refs, verifs):
    """Keep only refs whose verification is ok && contains_value (no orphan/unsupported refs)."""
    okset = {v.get("url") for v in (verifs or []) if v.get("ok") and v.get("contains_value")}
    return [u for u in (refs or []) if (not verifs or u in okset)]


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

    prior = json.load(open(prior_path))
    meta = dict(prior.get("meta", {}))
    res = prior["resolutions"]

    def is_old_deepsweep(r):
        return r.get("class_in") in ("FILL", "VALIDITY") or r.get("ref_col") == "__VALIDITY__"

    kept = [r for r in res if not is_old_deepsweep(r)]

    shards = sorted(glob.glob(os.path.join(S, "rows", "*.json")))
    new_validity, new_fills, missing = [], [], []

    pid_set = {r.get("project_id") for r in res}
    seen_shard_pids = set()
    for p in shards:
        try:
            d = json.load(open(p))
        except Exception as e:
            print(f"  WARN unreadable shard {p}: {e}"); continue
        pid = d.get("project_id") or os.path.basename(p)[:-5]
        seen_shard_pids.add(pid)
        ident = {"project_id": pid, "pipeline_name": d.get("pipeline_name", ""),
                 "wiki": d.get("wiki", "")}
        for v in d.get("validity", []) or []:
            new_validity.append({**ident,
                "sheet_row": d.get("sheet_row", ""),
                "segment_name": v.get("segment_name", ""),
                "ref_col": "__VALIDITY__", "value_cols": [], "primary_value_col": None,
                "values": {}, "primary_value": "", "current_ref": "",
                "class_in": "VALIDITY", "class_out": "UNRESOLVED",
                "verdict": v.get("verdict", ""), "concern_type": v.get("concern_type", ""),
                "recommendation": v.get("recommendation", ""),
                "researcher_notes": v.get("researcher_notes", ""),
                "proposed_refs": v.get("proposed_refs", []) or [],
                "verifications": v.get("verifications", []) or [],
                "tier": v.get("tier", ""), "independent": v.get("independent", False),
                "source_language": v.get("source_language", "en")})
        for f in d.get("fills", []) or []:
            refs = _verified(f.get("proposed_refs", []), f.get("verifications", []))
            notes = f.get("researcher_notes", "")
            cls = f.get("class_out", "UNRESOLVED")
            if f.get("proposed_refs") and not refs:
                cls = "UNRESOLVED"; notes = (notes + " [QC] dropped unverified ref(s).").strip()
            new_fills.append({**ident,
                "sheet_row": f.get("sheet_row", d.get("sheet_row", "")),
                "segment_name": f.get("segment_name", ""),
                "ref_col": f.get("ref_col", ""), "value_cols": f.get("value_cols", []),
                "primary_value_col": f.get("primary_value_col", ""),
                "values": f.get("values", {}), "primary_value": f.get("primary_value", ""),
                "current_ref": "", "class_in": "FILL", "class_out": cls,
                "proposed_refs": refs, "verifications": f.get("verifications", []) or [],
                "tier": f.get("tier", ""), "independent": f.get("independent", False),
                "source_language": f.get("source_language", "en"), "researcher_notes": notes})

    for pid in sorted(pid_set):
        if pid and pid not in seen_shard_pids:
            missing.append(pid)

    merged = kept + new_fills + new_validity
    meta["n_units"] = len(merged)
    meta["class_out_counts"] = dict(collections.Counter(r.get("class_out") for r in merged))
    meta["class_in_counts"] = dict(collections.Counter(r.get("class_in") for r in merged))
    meta["n_validity_flags"] = len(new_validity)
    meta["n_fills"] = len(new_fills)
    meta["verdict_counts"] = dict(collections.Counter(r.get("verdict") for r in new_validity))
    meta["concern_counts"] = dict(collections.Counter(
        r.get("concern_type") for r in new_validity if r.get("verdict") == "concern"))

    json.dump({"meta": meta, "resolutions": merged}, open(cur_path, "w"), indent=1)
    print(f"shards merged: {len(shards)} | missing PIDs: {len(missing)} {missing if missing else ''}")
    print(f"kept ref records: {len(kept)} | new fills: {len(new_fills)} | new validity: {len(new_validity)}")
    print(f"verdicts: {meta['verdict_counts']}")
    print(f"open concerns by type: {meta['concern_counts']}")


if __name__ == "__main__":
    main()
