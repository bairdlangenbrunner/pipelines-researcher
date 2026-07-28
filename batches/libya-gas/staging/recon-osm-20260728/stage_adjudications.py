#!/usr/bin/env python3
"""Stage the adjudications for the Libya OpenStreetMap reconciliation.

    python batches/libya-gas/staging/recon-osm-20260728/stage_adjudications.py

READ THIS BEFORE READING THE WORKBOOK. The OSM run for Libya gas is a COVERAGE
NULL RESULT, not a diff. OSM has mapped 6 gas features in Libya, four of which
are unnamed 0.0-0.1 km stubs. The run therefore cannot tell us anything about
the 37 GEM rows it fails to match, and its `gem_only` list must not be read as
37 GEM rows OSM contradicts. See sources/osm/NOTES.md.

The run was still worth doing for two reasons, both recorded here: it registered
OSM as a reusable source for countries where coverage IS good, and it exposed
three genuine engine defects (name-token inflation, absent-geometry scored as a
pass, IoU collapse on partial references) that were fixed in match.py /
reconcile.py / route_compare.py and affect EVERY source.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
DIFF = json.loads((OUT / "match_diff.json").read_text())

COVERAGE_VERDICT = {
    "verdict": "not_reconciliation_grade",
    "recommendation": "Do NOT action the gem_only list. Do not re-run OSM for Libya "
    "gas until OSM's Libya gas coverage improves; re-check the substance histogram "
    "first (sources/osm/NOTES.md documents how).",
    "researcher_notes": "Of 545 Libyan pipeline features in OSM: 270 tagged "
    "substance=oil, 248 untagged, 21 water, and 6 gas. Four of the 6 gas features are "
    "unnamed stubs of 0.0-0.1 km. Absence from OSM is therefore evidence about OSM's "
    "mapping effort in Libya, NOT evidence about GEM. The 248 untagged features may "
    "contain real gas pipe, but matching them on geometry alone would return mostly "
    "oil and is not worth the false-positive load.",
}

# The one pairing the run actually produced.
OVERLAPS = [
    {
        "ref_name": o["ref"].get("name") or "(unnamed OSM way)",
        "ref_id": o["ref"]["ref_id"],
        "project_id": o["gem"].get("project_id"),
        "gem_name": o["gem"].get("pipeline_name"),
        "confidence": o.get("confidence"),
        "composite": o.get("composite"),
        "route_iou": o.get("route_iou"),
        "recommendation": "Corroborative geometry only. OSM is tier 3 and cannot be a "
        "[ref] or a corroboration source on its own; it does not lift this row's "
        "confidence tier. Do NOT copy OSM coordinates into a GEM route without Baird's "
        "explicit ODbL call (share-alike).",
        "researcher_notes": "Recovered only after buffer_km_for_overlap was raised to "
        "10 km for this source: at the 2 km engine default the same pipeline scored IoU "
        "0.07 and read as no match, despite near-identical bounding boxes and a length "
        "ratio of 0.96. Offshore trunk geometry from public sources is coarse on both "
        "sides.",
    }
    for o in DIFF.get("overlaps", [])
]

ENGINE_FIXES = [
    {
        "defect": "name-token inflation",
        "file": "scripts/match.py",
        "detail": "rapidfuzz token_set_ratio scores on the token INTERSECTION, so two "
        "unrelated names sharing only boilerplate ('gas', 'pipeline') scored ~0.67. One "
        "GEM row became a magnet: four unrelated GulfPub lines all matched P6705. Fixed "
        "by stripping GENERIC_NAME_TOKENS before scoring.",
    },
    {
        "defect": "absent geometry scored as a PASS",
        "file": "scripts/reconcile.py",
        "detail": "The composite renormalizes over present signals, so dropping g_score "
        "when a GEM row had no route scored that row as if it had passed the geometry "
        "test. Routeless rows structurally outranked correctly-matched rows with real "
        "but imperfect geometry - the engine preferred the rows it knew least about. "
        "Fixed with geometry_untested_score=0.15 applied to the whole candidate pool, "
        "plus a green gate requiring a PHYSICAL signal (endpoints, diameter, or a TESTED "
        "geometry score).",
    },
    {
        "defect": "IoU collapse on partial references",
        "file": "scripts/route_compare.py",
        "detail": "A 97 km fragment lying exactly on a 520 km GEM route scores IoU 0.02, "
        "indistinguishable from an unrelated line. Added `containment` "
        "(intersection / smaller buffer), which is the signal that survives fragmentary "
        "sources - i.e. most of OSM.",
    },
]


def main() -> None:
    meta = {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": {"country": "Libya", "tracker": "gas"},
        "commodity": "gas",
        "mode": "recon",
        "source": "osm",
        "source_tier": 3,
        "source_scraped_date": "2026-07-28",
        "license": "ODbL (share-alike) — geometry reuse is Baird's call, never the agent's",
        "counts": {k: len(DIFF.get(k, [])) for k in
                   ("overlaps", "additions", "gem_only", "status_conflicts", "ambiguous")},
    }
    payload = {
        "meta": meta,
        "coverage_verdict": COVERAGE_VERDICT,
        "overlaps": OVERLAPS,
        "engine_defects_found_and_fixed": ENGINE_FIXES,
    }
    (OUT / "staged_recon_verdicts.json").write_text(json.dumps(payload, indent=1) + "\n")
    print(f"  wrote staged_recon_verdicts.json "
          f"({len(OVERLAPS)} overlap(s), {len(ENGINE_FIXES)} engine fixes)")
    print(f"counts: {meta['counts']}")
    print(f"verdict: {COVERAGE_VERDICT['verdict']}")


if __name__ == "__main__":
    main()
