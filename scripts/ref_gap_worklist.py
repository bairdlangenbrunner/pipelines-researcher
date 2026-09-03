#!/usr/bin/env python3
"""Ref-sweep step 1b: emit the OWED-BUT-UNCOVERED subset of a worklist.

A ref leg is complete when every *owed* unit has a staged record. Owed means:

  * class == MISSING_REF                      -> a filled value with no [ref]
  * class == HAS_REF and some existing check   -> the cited ref has a problem
    did not come back clean

Coverage is measured structurally, off (project_id, ref_col) pairs found in
the shards' `fills[]` bucket — never off a `kind` tag, which is the Jiangxi
lesson. A leg that reports plenty of REFS_ADDED can still have skipped a whole
class of owed units; only reconciling counts catches it.

The failure REASON matters and is carried through, because the standing rule
is that an access failure is not a deletion:

  DEAD_404       404/410 — the page is genuinely gone, the ref must be replaced
  LIVE_NO_VALUE  200 but the automated substring test missed the value. This is
                 the LARGEST bucket and mostly NOT a defect: "6 BCM annually"
                 does not contain "6.00", so the unit needs an agent to READ
                 the page, not a replacement URL.
  NON_CITATION   200 and live, but the URL is a site-search query or an archive
                 index — navigation, not a document, so it cannot support any
                 value and never could. Chase the underlying article/report.
  BLOCKED        401/403/429/WAF — keep the ref, add a Wayback snapshot beside it
  UNREACHABLE    timeout/DNS/TLS — same: a network condition, not evidence
  MISSING_REF    no ref cited at all

Usage:
  python scripts/ref_gap_worklist.py --staging <dir> [--out <gap.json>]
"""
import argparse, collections, glob, json, os, sys


def bucket(check):
    status = check.get("status")
    reason = (check.get("reason") or "").lower()
    if check.get("non_citation") or "search/index page" in reason:
        return "NON_CITATION"
    if status in (404, 410):
        return "DEAD_404"
    if status == 200 and "not found" in reason:
        return "LIVE_NO_VALUE"
    if status in (401, 403, 429) or "block" in reason:
        return "BLOCKED"
    if status and 500 <= status < 600:
        return "SERVER_ERR"
    if not status:
        return "UNREACHABLE"
    return "OTHER_%s" % status


def owed_reason(unit):
    """None if the unit is not owed, else its worst failure bucket."""
    if unit.get("class") == "MISSING_REF":
        return "MISSING_REF"
    checks = unit.get("existing_ref_checks") or []
    if not checks:
        return "UNCHECKED"
    bad = [bucket(c) for c in checks if not c.get("ok")]
    if not bad:
        return None
    for rank in ("DEAD_404", "NON_CITATION", "SERVER_ERR", "UNREACHABLE",
                 "BLOCKED", "LIVE_NO_VALUE"):
        if rank in bad:
            return rank
    return bad[0]


def covered_pairs(staging):
    """(project_id, ref_col) pairs that already carry a staged fill."""
    seen = set()
    for path in glob.glob(os.path.join(staging, "rows", "*.json")):
        try:
            shard = json.load(open(path))
        except (ValueError, OSError):
            continue
        pid = shard.get("project_id")
        for fill in shard.get("fills") or []:
            seen.add((pid, fill.get("ref_col")))
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    ap.add_argument("--out", help="default: <staging>/gap_worklist.json")
    args = ap.parse_args()

    wl = json.load(open(os.path.join(args.staging, "worklist.json")))
    done = covered_pairs(args.staging)

    gaps, owed_total = [], 0
    by_reason = collections.Counter()
    for unit in wl["units"]:
        reason = owed_reason(unit)
        if reason is None:
            continue
        owed_total += 1
        if (unit["project_id"], unit["ref_col"]) in done:
            continue
        u = dict(unit)
        u["gap_reason"] = reason
        gaps.append(u)
        by_reason[reason] += 1

    out = args.out or os.path.join(args.staging, "gap_worklist.json")
    doc = {
        "scope": wl.get("scope"),
        "summary": {
            "owed": owed_total,
            "covered": owed_total - len(gaps),
            "gaps": len(gaps),
            "coverage_pct": round(100.0 * (owed_total - len(gaps)) /
                                  owed_total, 1) if owed_total else 100.0,
            "by_reason": dict(by_reason),
            "rows": len({g["project_id"] for g in gaps}),
        },
        "units": gaps,
    }
    json.dump(doc, open(out, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(doc["summary"], indent=1))
    print("wrote %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
