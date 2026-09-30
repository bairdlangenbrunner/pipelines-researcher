#!/usr/bin/env python3
"""Cut a full sweep worklist down to the units a LEAN pass pays agents to work.

    python scripts/lean_worklist.py --staging <dir>            # reads <dir>/worklist_full.json
        [--owe-fill-cols "Start [ref],Construction [ref]"]     # keep these MISSING_VALUE units owed
        [--has-ref live|strict]                                # which cited units the script clears
        [--json]

Why (2026-09-16, Russia R5): a deep sweep hands every subagent every unit on its row —
blank values (MISSING_VALUE), uncited values (MISSING_REF) and already-cited values
(HAS_REF) alike. At R3's rate that was ~184k subagent tokens per row, and the payoff was
lopsided: 191 of R3's 222 fills re-proposed the value already on the sheet, while the
status changes and the uncited-value refs were what researchers acted on. The lean recipe
(`docs/sops/lean_pass.md`) spends agent tokens on those and DEFERS the rest — explicitly,
into a machine-readable file, never by silently dropping them.

Build the full worklist first, exactly as the deep preset does, but write it to
`worklist_full.json`:

    python scripts/build_ref_worklist.py ... --owe-fills --verify-existing \\
        --out <dir>/worklist_full.json

This script then writes, into the same dir:

- `worklist.json` — the OWED set every downstream script reads (shard_upsert,
  check_shard_coverage, seed_resolutions_from_worklist, sweep_gates, build_ref_workbook):
    * every MISSING_REF unit (standing rule 4(e): an uncited value is owed a ref);
    * every HAS_REF unit the deterministic `--verify-existing` check could NOT clear
      (confirmed 404/410, a live page missing the value, an index page, or the page does
      not name the pipeline; with
      `--has-ref strict`, also a non-numeric value the checker cannot match);
    * MISSING_VALUE units only for the columns named in `--owe-fill-cols`.
- `deferred_units.json` — every unit left out, each with `defer_reason`:
    * `fills_deferred` — a blank value; owed to a later fills pass (rule 4(c) still holds,
      the debt is recorded here instead of paid now);
    * `has_ref_cleared_by_script` — every existing ref is live and names the pipeline, so
      the only work left is the SECOND source (rule 4(d)) plus a relevance read, deferred;
    * `has_ref_access_blocked` — the cited links fail only on access (timeout, 401/403,
      geo-block), never 404/410: the ref stays (standing rule) and the Wayback add is
      deferred. `--work-blocked` keeps these owed.
- `lean_summary.json` — counts, for the run note and the per-row token comparison.

Scope carries `lean: true` so gate J reads "skipped — no MISSING_VALUE units" for the
right reason. Nothing here touches the live sheet or any shard.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path


def cleared(u: dict, mode: str) -> bool:
    """A HAS_REF unit the script can vouch for with no agent read at all.

    `live` (default): every cited link loads (`ok`) and none is flagged `name_absent`. For a
    numeric/year value `ok` already means the page states it; for an owner or a place name
    it means only "live" — the sheet already cites a working page there, and re-reading it
    for relevance is the deferred second-source pass's job, not the lean pass's.
    `strict`: additionally require a machine-checked value (or a status unit, which the
    status-review leg re-judges on every row anyway)."""
    checks = u.get("existing_ref_checks") or []
    if not checks:
        return False
    for c in checks:
        if not c.get("ok") or c.get("name_absent") or c.get("name_found") is False:
            return False
    if mode == "live":
        return True
    return bool(u.get("value_checked")) or any(c.get("status_token_absent") for c in checks)


ACCESS_FAIL = ("request failed", "HTTP 401", "HTTP 403", "HTTP 429", "HTTP 5")


def access_blocked(u: dict) -> bool:
    """Every link that failed, failed on ACCESS (timeout, 401/403/429/5xx, geo-block), and
    none is a confirmed 404/410 or a live page missing the value. Standing rule: an access
    failure never retires a ref, so the only agent work on such a unit is adding a Wayback
    copy alongside — worth doing, not worth a lean pass's tokens."""
    checks = u.get("existing_ref_checks") or []
    failed = [c for c in checks if not c.get("ok")]
    if not failed or any(c.get("name_absent") for c in checks):
        return False
    return all(any(m in (c.get("reason") or "") for m in ACCESS_FAIL)
               and c.get("status") not in (404, 410) for c in failed)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--full", help="full worklist (default <staging>/worklist_full.json)")
    ap.add_argument("--owe-fill-cols", default="",
                    help="comma-separated ref_col names whose MISSING_VALUE units stay owed")
    ap.add_argument("--has-ref", choices=["live", "strict"], default="live",
                    help="which HAS_REF units the script clears (see cleared()); default live")
    ap.add_argument("--work-blocked", action="store_true",
                    help="keep access-blocked HAS_REF units owed (default: defer them)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    stg = Path(a.staging)
    full_path = Path(a.full) if a.full else stg / "worklist_full.json"
    wl = json.loads(full_path.read_text())
    keep_fill = {c.strip() for c in a.owe_fill_cols.split(",") if c.strip()}

    owed, deferred = [], []
    for u in wl["units"]:
        cls = u.get("class")
        if cls == "MISSING_VALUE" and u.get("ref_col") not in keep_fill:
            deferred.append({**u, "defer_reason": "fills_deferred"})
        elif cls == "HAS_REF" and cleared(u, a.has_ref):
            deferred.append({**u, "defer_reason": "has_ref_cleared_by_script"})
        elif cls == "HAS_REF" and not a.work_blocked and access_blocked(u):
            deferred.append({**u, "defer_reason": "has_ref_access_blocked"})
        else:
            owed.append(u)

    by = lambda xs, k: dict(collections.Counter(x.get(k) for x in xs))
    per_pid = collections.Counter(u.get("project_id") for u in owed)
    all_pids = {u.get("project_id") for u in wl["units"]}
    summary = {
        "full_units": len(wl["units"]),
        "owed_units": len(owed),
        "deferred_units": len(deferred),
        "owed_by_class": by(owed, "class"),
        "deferred_by_reason": by(deferred, "defer_reason"),
        "pids": len(all_pids),
        "pids_with_no_owed_units": sorted(all_pids - set(per_pid)),
        "owe_fill_cols": sorted(keep_fill),
        "has_ref_mode": a.has_ref,
    }

    out = dict(wl)
    out["scope"] = {**wl.get("scope", {}), "lean": True, "owe_fills": bool(keep_fill),
                    "full_worklist": full_path.name}
    out["summary"] = {**wl.get("summary", {}), "lean": summary}
    out["units"] = owed
    (stg / "worklist.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    (stg / "deferred_units.json").write_text(json.dumps(
        {"scope": out["scope"], "summary": summary, "units": deferred},
        indent=1, ensure_ascii=False))
    (stg / "lean_summary.json").write_text(json.dumps(summary, indent=1))

    if a.json:
        print(json.dumps(summary, indent=1))
    else:
        print(f"full {summary['full_units']} units -> owed {summary['owed_units']} "
              f"{summary['owed_by_class']} | deferred {summary['deferred_units']} "
              f"{summary['deferred_by_reason']}")
        if summary["pids_with_no_owed_units"]:
            print(f"NOTE: {len(summary['pids_with_no_owed_units'])} PIDs have no owed ref units "
                  f"(they still get a status review + validity record): "
                  f"{', '.join(summary['pids_with_no_owed_units'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
