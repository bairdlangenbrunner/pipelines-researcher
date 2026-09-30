#!/usr/bin/env python3
"""Fold research agents' `__REDUNDANCY__` / `__VALIDITY__` shard objects into the store.

    python scripts/harvest_sentinel_findings.py --staging <dir> [--staging <dir> ...]

`merge_ref_shards.py` matches each shard resolution to a baseline record by
(project_id, ref_col, sheet_row). A sentinel object — `ref_col` of
`__REDUNDANCY__` or `__VALIDITY__` — deliberately has no baseline record: it is
not a ref cell, it is the agent answering "is this row real / is it a
double-count?". So the merge WARNs and drops it, and the sourced verdict is
lost while the refs survive. That was worth a script rather than a manual copy:
these are the highest-value findings in the batch (three misplaced condensate
lines in Libya came from them), and losing them silently is the worst failure
mode available.

This appends each sentinel as a proper `__VALIDITY__` resolution — the same
shape `build_redundancy.py` writes — with `class_out: UNRESOLVED`, because a
validity record is read-and-flag only and never an applied edit. Idempotent:
re-running replaces previously harvested records rather than duplicating them.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_qc import independence_qc, verified_refs  # noqa: E402

SENTINELS = ("__REDUNDANCY__", "__VALIDITY__")
MARK = "harvested_from_shard"


def harvest(staging: Path) -> int:
    store_p = staging / "staged_resolutions.json"
    if not store_p.exists():
        print(f"  {staging.name}: no staged_resolutions.json — skipped")
        return 0
    store = json.loads(store_p.read_text())

    # Drop any prior harvest so a re-run is a replace, not an append.
    kept = [r for r in store["resolutions"] if not r.get(MARK)]
    dropped = len(store["resolutions"]) - len(kept)

    found = []
    for sf in sorted((staging / "ref_shards").glob("P*.json")):
        sh = json.loads(sf.read_text())
        for r in sh.get("resolutions", []):
            if r.get("ref_col") not in SENTINELS:
                continue
            # This script is the LAST writer of a __VALIDITY__/__REDUNDANCY__ record:
            # merge_deepsweep_shards applies independence_qc to sentinels, but its own
            # is_old_deepsweep() then purges them and we re-append here, so whatever we
            # copy is what ships. Copying `tier`/`independent`/`proposed_refs` verbatim
            # (as this did until 2026-09-10) routed the batch's HIGHEST-value findings
            # around the one invariant every merger enforces -- Jiangxi v3 delivered 11
            # sentinels at tier `high` and 12 flagged `independent` on 0-1 verified refs,
            # and sweep_gates B/D flag sentinels precisely because they are in scope.
            #
            # Two different ref bases, deliberately:
            #   * `s_refs` keeps the EVIDENCE, host-filtered only (verifs=None -> scheme
            #     + blocklist screen). A validity concern usually has no value to contain,
            #     so screening it on `contains_value` would throw away the very document
            #     the concern rests on -- but a banned host must never ride in on a
            #     sentinel, which is the one hole this leaves open otherwise.
            #   * independence/tier are judged on refs that actually VERIFIED, the same
            #     ok && contains_value basis sweep_gates' verified() uses, so the store
            #     and its own gate cannot disagree.
            #     NB the strict basis is spelled out here rather than delegated to
            #     verified_refs(refs, verifs): that helper treats "no verifications at
            #     all" as "host-filter only and let the caller decide", so a record
            #     carrying refs but ZERO verification objects comes back fully verified.
            #     sweep_gates' verified() calls the same record 0-verified, and the two
            #     disagreeing is what left 4 P5866 __VALIDITY__ records at `high` +
            #     `independent` after the first pass of this fix. An unrecorded
            #     verification is not a verification, so the gate's reading is the
            #     correct one and this mirrors it exactly.
            s_refs = verified_refs(r.get("proposed_refs", []), None)
            _ok = {v.get("url") for v in (r.get("verifications") or [])
                   if v.get("ok") and v.get("contains_value")}
            s_tier, s_indep, s_notes = independence_qc(
                [u for u in s_refs if u in _ok],
                r.get("tier") or "n/a",
                bool(r.get("independent") or False),
                r.get("researcher_notes", ""))
            found.append({
                "project_id": sh.get("project_id"),
                "sheet_row": r.get("sheet_row", 0),
                # Row identity, from the record first and the shard doc second. Both were
                # read off `sh` alone (and segment_name was hardcoded blank), so every
                # harvested row landed on Gas_Validity with empty name columns -- on the tab
                # that carries a sweep's HIGHEST-value findings, leaving the reader a bare
                # ProjectID. split_shards now stamps identity onto each ref_shards/<PID>.json.
                "pipeline_name": r.get("pipeline_name") or sh.get("pipeline_name", ""),
                "segment_name": r.get("segment_name") or sh.get("segment_name", ""),
                "wiki": r.get("wiki") or sh.get("wiki", ""),
                "ref_col": "__VALIDITY__",
                "value_cols": [],
                "primary_value_col": "",
                "primary_value": "",
                "values": {},
                "current_ref": "",
                "class_in": "VALIDITY",
                # Read-and-flag only. An agent's redundancy verdict is evidence for
                # Baird's decision, never the decision itself.
                "class_out": "UNRESOLVED",
                "verdict": "concern",
                "concern_type": "redundancy"
                if r.get("ref_col") == "__REDUNDANCY__" else "validity",
                # A per-record `recommendation` wins when the shard sets one. The
                # boilerplate below is the right default for an agent's own verdict
                # (read-and-flag), but it BURIES an orchestrator ruling: a reviewer
                # scanning this column sees "see researcher_notes" where the actual
                # actionable change should be. No shard set this field before 2026-09-10,
                # so the default still fires everywhere it did and no committed run moves.
                "recommendation": (r.get("recommendation") or "").strip()
                or "Agent research verdict — see researcher_notes. "
                "Cross-check against the cluster-level recommendation in "
                "staging/redundancy/ before acting; where they differ, the cluster "
                "file is the adjudicated one.",
                "proposed_refs": s_refs,
                "verifications": r.get("verifications", []),
                # `or`, not a .get default: a shard that writes an explicit null tier
                # (sentinels carry no tier -- there is no value being sourced) has the
                # key present, so the default never fires and None reaches the store.
                "tier": s_tier,
                "independent": s_indep,
                "source_language": r.get("source_language", "en"),
                "researcher_notes": s_notes,
                MARK: str(sf.name),
            })

    store["resolutions"] = kept + found
    store.setdefault("meta", {})["sentinel_findings_harvested"] = {
        "count": len(found),
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    store_p.write_text(json.dumps(store, indent=1) + "\n")
    note = f" (replaced {dropped})" if dropped else ""
    print(f"  {staging.name}: harvested {len(found)} sentinel finding(s){note} "
          f"-> {', '.join(sorted({f['project_id'] for f in found})) or '-'}")
    return len(found)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", action="append", required=True,
                    help="staging dir (repeatable)")
    args = ap.parse_args()
    total = sum(harvest(Path(s)) for s in args.staging)
    print(f"total: {total}")


if __name__ == "__main__":
    main()
