#!/usr/bin/env python3
"""Stage the human-facing adjudications for the Libya GulfPub reconciliation.

`reconcile.py` produces `match_diff.json` — the mechanical diff. This script
records the *judgements* made on top of it (SOP §4 routing), which the engine
cannot make: which reference-only rows are really existing GEM pipelines under
another name, which "status conflicts" are spurious pairings, and which
additions are below GGIT's practical inclusion threshold.

    python batches/libya-gas/staging/recon-gulfpub-20260728/stage_adjudications.py

Run with `--commodity both` (not gas-only) so cross-tracker pairs are visible:
that is what surfaced GulfPub's own "Wafa - Mellitah Oil & Condensate" record
matching GOIT P0606 green, corroborating the P6705 verdict in the redundancy
cluster. Nothing here is applied — every record is a candidate for Update.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
DIFF = json.loads((OUT / "match_diff.json").read_text())
SOURCE = "gulfpub"
SCRAPED = "2026-02-02"

# --- reference-only rows that ARE an existing GEM pipeline under another name.
# SOP: "a reference-only (Addition) row is usually NOT a missing pipeline — match
# it to an existing GEM pipeline first". These go to OtherEnglishNames, not Discovery.
REPORT_ONLY = [
    {
        "ref_id": "gulfpub:gas:465",
        "ref_name": "Intisar D - Intisar A",
        "project_id": "P1857",
        "gem_name": "103D-103A Gas Pipeline",
        "proposed_other_english_names": "Intisar D-Intisar A Gas Pipeline",
        "recommendation": "Add 'Intisar D-Intisar A' to P1857 OtherEnglishNames. Do "
        "NOT create a new row.",
        "researcher_notes": "The engine scored this 0.4419 and filed it as an addition "
        "because the names share no tokens — GEM uses the well-designation form "
        "'103D-103A' and GulfPub the field-name form 'Intisar D - Intisar A'. They are "
        "the same pipe: both 40 in (an unusual diameter that only these two rows carry "
        "in the Libya gas set), both ~25-28 km, same Intisar-complex corridor. This is "
        "a naming-convention miss, not a missing pipeline, and it is exactly the case "
        "the SOP warns about. Adding the alias also stops the next scrape re-filing it "
        "as an addition.",
    },
]

# --- status conflicts the engine raised that are NOT real conflicts.
# A conflict is only meaningful if the two rows are the same pipeline.
STATUS_CONFLICTS = [
    {
        "ref_id": "gulfpub:gas:473",
        "ref_name": "Atshan - Awbari Power Plant",
        "ref_status": "proposed",
        "project_id": "P1872",
        "gem_name": "Km-91.5-Brega Gas Pipeline",
        "gem_status": "operating",
        "verdict": "spurious_pairing",
        "recommendation": "DISMISS as a status conflict; re-route to Discovery as a "
        "candidate ADDITION instead. Do not touch P1872's status.",
        "researcher_notes": "Matched at composite 0.4552 on diameter + length only — "
        "name scored 0.26 and there is no endpoint or geometry agreement. Atshan-Awbari "
        "is a southwest-Libya line feeding the Awbari power plant; Km-91.5-Brega is a "
        "Sirte-Basin trunk in the northeast. They are unrelated, so 'proposed vs "
        "operating' is not a disagreement about one pipeline's status. Flagged here "
        "rather than silently dropped so the next scrape does not re-raise it as new.",
    },
    {
        "ref_id": "gulfpub:oil:576",
        "ref_name": "Nafoora - Intisar",
        "ref_status": "operating",
        "project_id": "P5238/P5237",
        "gem_name": "Nafoora-Zueitina Oil Pipeline",
        "gem_status": "shelved",
        "verdict": "out_of_scope_oil",
        "recommendation": "OIL-TRACKER item — surfaced only because this run used "
        "--commodity both. Do not action in the gas batch; carry to a future Libya oil "
        "pass.",
        "researcher_notes": "GEM holds two Nafoora-Zueitina rows (P5237 operating 68 km "
        "24/16 in, P5238 shelved 68.5 km 12 in) and the matcher hit the shelved one. "
        "Worth a look on the oil side — a shelved and an operating row on the same "
        "endpoints at near-identical length is its own redundancy question — but it is "
        "outside this batch's gas scope and is NOT evidence about any gas row.",
    },
    {
        "ref_id": "gulfpub:oil:4967",
        "ref_name": "As Sarah - Nafoora",
        "ref_status": "operating",
        "project_id": "P5238/P5237",
        "gem_name": "Nafoora-Zueitina Oil Pipeline",
        "gem_status": "shelved",
        "verdict": "out_of_scope_oil",
        "recommendation": "OIL-TRACKER item, same P5237/P5238 pair as above. Carry to a "
        "future Libya oil pass.",
        "researcher_notes": "Second GulfPub record landing on the same shelved GEM row, "
        "which is itself a signal the P5237/P5238 pair needs oil-side attention. Out of "
        "gas scope.",
    },
]

# --- additions: GGIT scope judgement. GGIT does track gathering lines (34 rows
# globally, min 3.2 km), so small ≠ automatically excluded — but the tracker-wide
# diameter p05 is 12 in, which is the yardstick used below.
ADDITION_SCOPE = {
    "below_practice": {
        "refs": ["Bu Mras - Jofra (6in, 22.1 km)", "Khalifa - Samah (8in, 34.9 km)",
                 "Kotla - Beda (6in, 16.3 km)", "Masrab - Gialo (6in, 51.1 km)"],
        "recommendation": "HOLD — do not open Discovery rows without Baird's scope "
        "ruling.",
        "researcher_notes": "6-8 in sits below GGIT's tracker-wide 5th-percentile "
        "diameter of 12 in. These are field gathering laterals. GGIT does carry some "
        "gathering pipe, so this is a threshold judgement for Baird, not an exclusion "
        "the agent should make. Listing them here means the decision is recorded once "
        "instead of being re-litigated at every scrape.",
    },
    "borderline": {
        "refs": ["Bahi - Dahra West (12in, 24.8 km)", "Hakim - Zella (16in, 24.1 km)",
                 "Nakhla - Jakhira (16in, 48.1 km)"],
        "recommendation": "CANDIDATES for Discovery — 12-16 in is within normal GGIT "
        "practice. Research each before creating a row; GulfPub alone is one Tier-2 "
        "source and cannot justify a new entity.",
        "researcher_notes": "Each needs the standard 2-independent-source test. Note "
        "their engine best-guesses (Attahaddy-km-91.5, Wafa-Mellitah, Jakhira-Intesar) "
        "are all low-composite name-only artifacts and should NOT be read as probable "
        "matches — check for an existing GEM row under another name independently.",
    },
}

ROUTE_REPLACEMENTS = [
    o for o in DIFF["overlaps"] if o.get("route_replacement_candidate")
]


def main() -> None:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    meta = {
        "generated_utc": stamp,
        "scope": {"country": "Libya", "tracker": "gas"},
        "commodity": "gas",
        "mode": "recon",
        "source": SOURCE,
        "source_scraped_date": SCRAPED,
        "source_tier": 2,
        "reconcile_commodity": "both",
        "note": "Run with --commodity both to expose cross-tracker duplicates. Oil-side "
        "records are CONTEXT for the gas batch, not a completed Libya oil pass.",
        "counts": {k: len(DIFF.get(k, [])) for k in
                   ("overlaps", "additions", "gem_only", "status_conflicts", "ambiguous")},
    }

    for fname, payload in (
        ("staged_report_only_resolutions.json", {"meta": meta, "resolutions": REPORT_ONLY}),
        ("staged_status_conflicts.json", {"meta": meta, "conflicts": STATUS_CONFLICTS}),
        ("staged_addition_scope.json", {"meta": meta, "scope_calls": ADDITION_SCOPE}),
        ("staged_route_replacements.json", {"meta": meta, "candidates": ROUTE_REPLACEMENTS}),
    ):
        (OUT / fname).write_text(json.dumps(payload, indent=1) + "\n")
        n = len(payload.get("resolutions") or payload.get("conflicts")
                or payload.get("candidates") or payload.get("scope_calls") or [])
        print(f"  wrote {fname} ({n})")

    print(f"counts: {meta['counts']}")


if __name__ == "__main__":
    main()
