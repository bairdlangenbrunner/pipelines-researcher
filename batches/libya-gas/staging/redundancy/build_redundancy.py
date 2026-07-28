#!/usr/bin/env python3
"""Stage the Libya-gas redundancy adjudication (§3 `validity` leg, cluster-level).

The operating + in-dev deep sweeps each flagged duplicates row-by-row ("compare
P0483 against P1862"). This pass resolves those pairwise flags into SEVEN structural
clusters and stages one `__VALIDITY__` record per implicated row carrying the
CLUSTER-level recommendation. Detection lives in the prior dirs; adjudication
lives here. Read-and-flag only — never an edit (QC detects, Update fixes).

    python batches/libya-gas/staging/redundancy/build_redundancy.py

Cluster A resolution follows in-tracker precedent, not invention: GEM already
represents an aggregate corridor as a row with a BLANK Status carrying a
`PipelineNetworkGrouping` label, so status-filtered totals skip it while the
member segments keep their own status/length/capacity. Precedent rows (GGIT
2026-07-28): P3656 Moomba Sydney Pipeline System, P3672 NSW Gas Network,
P3966 East-West Gas Pipeline + P5885 MGS III (both `Master Gas System`),
P7150 OQGN. `n/a` is NOT in the Status vocab; the lone `mixed status` row
(P6249 Guizhou) is a non-vocab one-off and is not a convention to copy.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

CSV = "data/GGIT_gas_snapshot_20260728.csv"
OIL_CSV = "data/GOIT_oil_ngl_snapshot_20260728.csv"
OUT = Path(__file__).resolve().parent
REPO = OUT.parents[3]

NETWORK_LABEL = "Libya Coastal Gas Pipeline"

# (project_id, concern_type, recommendation, researcher_notes)
CLUSTERS: dict[str, dict] = {
    "A": {
        "title": "Coastal trunk aggregate vs its four member segments",
        "rows": {
            "P0483": (
                "duplicate",
                f"Convert to the NETWORK row for this corridor: set "
                f"PipelineNetworkGrouping='{NETWORK_LABEL}' and CLEAR Status to blank "
                "(GEM's documented aggregate convention - see precedent rows below). "
                "Keep LengthKnownKm=1164 as the corridor summary. Do NOT delete the "
                "member segments. Also re-derive Capacity: 604 MMcf/d is both unit-"
                "inconsistent with the members (bcm/y) and smaller than every one of "
                "them, which cannot be right for a trunk.",
                "P0483 (Mellitah Complex->Benghazi, 1164 km, 34in) is the aggregate of "
                "P1862 Brega-Benghazi (396) + P1863 Brega-Khoms (645) + P1864 "
                "Khoms-Tripoli (201) + P1865 Tripoli-Mellitah (158) = 1400 km. All five "
                "carry Status=operating today, so any status-filtered length total "
                "double-counts the corridor (1164 + 1400 = 2564 km of pipe recorded for "
                "~1200-1400 km of physical asset). Capacity is separately incoherent: "
                "these are SERIES segments of one trunk, so capacity does not sum, yet "
                "P0483's 604 MMcf/d (~6.24 bcm/y) is LOWER than each member "
                "(10.76/11.61/17.05/16.99 bcm/y). Fix is structural, not a value edit. "
                "GEM precedent for a blank-Status network row with a "
                "PipelineNetworkGrouping label: P3656 Moomba Sydney Pipeline System "
                "(2081 km, blank), P3672 NSW Gas Network (blank), P3966 East-West Gas "
                "Pipeline + P5885 MGS III Gas Pipelines (both grouping='Master Gas "
                "System', blank), P7150 OQGN 2023 Full Schematic Map (4223 km, blank). "
                "'n/a' is not a Status vocab value.",
            ),
            **{
                p: (
                    "duplicate",
                    f"Member segment of the '{NETWORK_LABEL}' corridor: set "
                    f"PipelineNetworkGrouping='{NETWORK_LABEL}'. KEEP Status=operating "
                    "and keep this row's own length/diameter/capacity/refs - the "
                    "segments are the real physical assets and must not be deleted; "
                    "the aggregate P0483 is what gets the blank Status.",
                    "Constituent of the Mellitah->Benghazi coastal trunk recorded in "
                    "aggregate as P0483. Grouping the five rows under one "
                    "PipelineNetworkGrouping is what makes the aggregate/segment "
                    "relationship legible and stops the double-count; it does not "
                    "change this row's own values.",
                )
                for p in ("P1862", "P1863", "P1864", "P1865")
            },
            "P1789": (
                "duplicate",
                "Likely retire or merge: a 25 km 'Khoms-Melita' line at 34in duplicates "
                "a stretch already fully covered by P1864 Khoms-Tripoli (201 km) + "
                "P1865 Tripoli-Mellitah (158 km) = 359 km on the same 34in corridor. "
                "Needs Baird's ruling: retire as a digitization artifact, or "
                "re-scope/rename it if it is a genuine distinct spur.",
                "Name ('Khoms-Melita' - note the non-standard 'Melita' spelling of "
                "Mellitah) describes the Khoms->Mellitah run, but the recorded 25 km is "
                "~7% of that run's actual 359 km, at the same 34in diameter as the "
                "coastal trunk. Reads as a fragment of the trunk captured as its own "
                "row rather than a standalone asset. No independent source names a "
                "distinct 25 km Khoms-Mellitah pipeline.",
            ),
        },
    },
    "B": {
        "title": "Wafa-Mellitah: a cross-tracker duplicate + a 10x length bug (sourced)",
        "rows": {
            "P0484": (
                "spec",
                "CORRECT LengthKnownKm: 5246.00 is a decimal-shift error. The Wafa "
                "field is ~525 km from the Mellitah Complex; P6705 carries the correct "
                "524.65. Propose LengthKnownKm=524.65 (or 525) pending Baird's "
                "confirmation. This is a live wrong value in the published tracker.",
                "P0484 records 5246.00 km for a line whose own gem.wiki page, the "
                "operator (mellitahog.ly) and offshore-technology all put at ~525 km - "
                "an order-of-magnitude error, and 5246.00 vs 524.65 is a clean decimal "
                "shift. 5246 km would be longer than any pipeline in Libya by a factor "
                "of four. NOT flagged by the deep sweep's spec check, caught by "
                "arithmetic during cluster review. Independently, P0484 is confirmed "
                "REAL and correctly in GGIT: it is the 32in sales-gas trunk of the "
                "Western Libya Gas Project.",
            ),
            "P6705": (
                "duplicate",
                "DELETE from GGIT - do NOT move to GOIT. The 16in Wafa-Mellitah line is "
                "oil/condensate, and GOIT ALREADY CARRIES IT as P0606 'Wafa-Mellitah Oil "
                "Pipeline' (operating, 525.00 km, 16.00in, Wadi Al-Shatii -> Mellitah "
                "Complex, sheet row 1939) - the same length and diameter as P6705's "
                "524.65 km / 16in. Reclassifying P6705 into GOIT would create a "
                "duplicate there. Fold any refs P6705 carries into P0606 and drop the "
                "GGIT row.",
                "RESOLVED WITH SOURCES (ref-sweep agent, 2026-07-28): six independent "
                "sources - Offshore Technology's separate gas and oil pages, and four "
                "Mellitah Oil & Gas pages - unanimously describe the Western Libya Gas "
                "Project's Wafa-Mellitah corridor as TWO parallel lines, 32in gas "
                "(P0484) and 16in oil/condensate (P6705). So P6705 is a real pipeline "
                "and not a duplicate OF P0484 - but it is a cross-tracker duplicate of "
                "GOIT P0606, verified against the 2026-07-28 GOIT snapshot. Keeping it "
                "in GGIT inflates Libya's gas count and km by a 525 km line that is not "
                "gas. SEPARATE, out-of-scope flag for the oil side: GOIT also holds "
                "P5215 'Wafa-Mellitah NGL Pipeline' (16in, same endpoints, row 1938) - "
                "P0606 vs P5215 may itself be a within-GOIT duplicate.",
            ),
        },
    },
    "C": {
        "title": "Bouri-Bahr Assalam: a real twinned pair (sourced) - but the 4in is condensate",
        "rows": {
            "P1859": (
                "spec",
                "KEEP - the duplicate hypothesis against P6709 is refuted (see notes). "
                "But CORRECT LengthKnownKm: 32 km appears stale. Later OPEC editions put "
                "BOTH lines on this corridor at ~12 mi (~19.3 km), which is exactly the "
                "19.31 km P6709 carries. Propose ~19.3 km pending Baird's confirmation. "
                "ALSO re-check Status: the Bouri Gas Utilisation Project (BGUP) targets "
                "first gas Sept 2026 and may add or replace same-diameter twin lines on "
                "this exact corridor - verify what is operating before the next publish.",
                "RESOLVED WITH SOURCES (ref-sweep agent, 2026-07-28): OPEC ASB 2012, 2013 "
                "and 2017 consistently tabulate Bouri<->Bahr Essalam as TWO parallel "
                "lines, with ASB 2017 marking the entry explicitly '(2)' / '2 x 12 mi' / "
                "'4, 10 in'. Mellitah Oil & Gas's own 2019 Bouri Gas Upgrading Project "
                "tender independently specs '10\" CS and 4\" CS pipelines 20 km long' on "
                "the same route. So the near-identical names are two real assets, not one "
                "row entered twice under a misspelling - though P6709's 'Asslam' spelling "
                "should still be normalised or captured in OtherEnglishNames.",
            ),
            "P6709": (
                "classification",
                "MOVE TO GOIT - this is the 4in CONDENSATE line, not gas. Unlike P6705 "
                "(cluster B) and P6713 (cluster D), GOIT does NOT already carry it: the "
                "2026-07-28 GOIT snapshot has no Bouri or Bahr Assalam row among Libya's "
                "57 oil rows. So this one is a genuine reclassification that creates a "
                "new GOIT row, not a delete. Confirm the GOIT check still holds at "
                "apply-time. Capacity is separately wrong - see the scm/y defect below; "
                "true value ~0.04 bcm/y.",
                "RESOLVED WITH SOURCES - see P1859 for the twinned-pair evidence. The "
                "4in of the pair is the condensate line. This is the THIRD condensate "
                "line found sitting in Libya's gas tracker in one batch (P6705, P6713, "
                "P6709), which is why the pattern is escalated as a class defect rather "
                "than three isolated fixes. Note the dispositions differ and must not be "
                "applied uniformly: two are deletes because GOIT already holds the asset, "
                "this one is a move because GOIT does not. ROOT CAUSE of the capacity "
                "figure: these come from OPEC ASB Table 4.10, whose column header reads "
                "'(1,000 scm/yr)'; the ingest took the raw cell and labelled it 'scm/yr', "
                "dropping the x1000. THE WORSE, SEPARATE DEFECT: 'scm/y' and 'scm/yr' are "
                "not units GGIT's CapacityBcm/y formula converts - all four Libya rows "
                "using them (P1858, P6709, P6713, P6714) compute CapacityBcm/y = 0.00 or "
                "blank and contribute ZERO to any Libya gas capacity total in the "
                "published tracker. Tracker-wide only 8 rows use this unit string: these "
                "4 plus 4 Algeria rows (P6616, P6617, P6618, P6620), and all 8 read zero. "
                "Every other scm-family row in GGIT uses MMSCMD, which converts fine.",
            ),
        },
    },
    "D": {
        "title": "Bahr Assalam-Mellitah Pipeline 2: a condensate line GOIT already has (sourced)",
        "rows": {
            "P6713": (
                "duplicate",
                "DELETE from GGIT - same disposition as P6705 in cluster B, and for the "
                "same reason. The 10in Sabratha->Mellitah line is CONDENSATE and GOIT "
                "ALREADY CARRIES IT as P6457 'Sabratha-Mellitah Condensate Pipeline' "
                "(operating, 107.00 km, 10in, sheet row 1765) against P6713's 109.00 km / "
                "10in. Do not reclassify into GOIT - that would duplicate P6457. Fold any "
                "refs into P6457 and drop the GGIT row. Separately, Capacity=465166 scm/y "
                "is subject to the scm/y defect (see cluster C / P6709): true value "
                "~0.47 bcm/y.",
                "RESOLVED WITH SOURCES (ref-sweep agent, 2026-07-28): Offshore Technology "
                "and Offshore Magazine independently describe the Sabratha platform "
                "feeding Mellitah via exactly two lines - one 36in GAS line (= P1855) and "
                "one 10in CONDENSATE line. P6713 is that condensate line. This is the "
                "second instance of the identical failure mode in one country (P6705 in "
                "cluster B), which is why the pattern is escalated rather than filed as "
                "two isolated fixes: a condensate line gets entered in GGIT while GOIT "
                "already holds it, inflating the gas tracker's count and km. It also "
                "explains cluster D's original trigger - P1855 and P6713 sharing an exact "
                "109.00 km is not a copy error, they are the two parallel lines of one "
                "riser bundle; only the tracker placement is wrong.",
            ),
        },
    },
    "G": {
        "title": "Bu-Attifel-Intesar: a real twinned pair, not a duplicate (sourced)",
        "rows": {
            "P1858": (
                "spec",
                "KEEP BOTH ROWS - the duplicate hypothesis is refuted (see notes). Two "
                "items remain on this row: (1) the scm/y capacity defect, see cluster C / "
                "P6709 - true value ~4.13 bcm/y; (2) verify the owner/operator split, "
                "which sources put at Mellitah Oil & Gas for THIS 34in line and Eni Oil "
                "for P6714's 10in line.",
                "RESOLVED WITH SOURCES (ref-sweep agent, 2026-07-28): OPEC ASB 2013 "
                "(2012 data) and ASB 2017 (2016 data), both Wayback-recovered and read "
                "with pdftotext, independently list 'Bu-Attifel/Intesar' as TWO PARALLEL "
                "LINES on one 82 mi / 131.96 km corridor - a 34in operated by Mellitah "
                "Oil & Gas and a 10in operated by Eni Oil. Each table's capacity matches "
                "its GEM row EXACTLY (4,134,806 -> P1858; 258,425 -> P6714). So the "
                "identical 2-decimal length that raised the flag is the correct answer, "
                "not a copy error: twinned lines share a route. This also disposes of the "
                "competing gas+condensate reading floated when the cluster was opened - "
                "OPEC carries both lines in its GAS table, so the 10in is not the "
                "condensate analogue of clusters B and D. Do not merge.",
            ),
            "P6714": (
                "spec",
                "KEEP - see P1858. Same two remaining items: the scm/y capacity defect "
                "(true value ~0.26 bcm/y) and the operator check (sources say Eni Oil for "
                "this 10in line).",
                "See P1858. Noting explicitly for the reviewer: this row was opened as a "
                "suspected duplicate and closed as a real asset. The pattern that made it "
                "look like a duplicate - a large and a small line sharing a name and an "
                "exact length - is genuine twinning here, even though the same signature "
                "in clusters B and D did turn out to be a misplaced condensate line. The "
                "signature is a reason to look, not a verdict.",
            ),
        },
    },
    "E": {
        "title": "NC-41 and E Structure: one Mellitah export corridor described twice",
        "rows": {
            "P6708": (
                "duplicate",
                "Cross-check against P6715 'E Structure-Mellitah Gas Pipeline' before "
                "next publish; if confirmed one asset, retain a single row and record "
                "the other name in OtherEnglishNames.",
                "P6708 (130 km, 30in, construction, StartYear 2025) and P6715 (130 km, "
                "32in, construction, StartYear 2026) are both ~130 km 'X->Mellitah' gas "
                "lines out of the same NC-41 / Contract Area D concession, and sit at "
                "adjacent sheet rows (3988 and 3990). Identical length with differing "
                "diameter/start-year is the signature of two aggregator "
                "(GlobalData/offshore-technology) descriptions of one export corridor, "
                "not two parallel 130 km pipelines.",
            ),
            "P6715": (
                "duplicate",
                "Paired with P6708 - see that row. Resolve as one cluster: keep one "
                "row, fold the other's name/refs in.",
                "See P6708. Whichever row survives should take the better-sourced "
                "diameter and start year rather than defaulting to either row's values.",
            ),
        },
    },
    "F": {
        "title": "Nasser-Brega in both trackers: two real lines (sourced) - but a bad length",
        "rows": {
            "P1866": (
                "spec",
                "KEEP BOTH ROWS - the cross-tracker duplicate hypothesis is refuted (see "
                "notes). But CORRECT LengthKnownKm: 277 km is unsupported by any source "
                "found; the corridor measures ~169-172 km. Propose ~172 km, or blank it, "
                "pending Baird's call. Do not resolve the length by copying GOIT P0599's "
                "171.62 - source it independently.",
                "RESOLVED WITH SOURCES (ref-sweep agent, 2026-07-28): P1866 (gas) and "
                "GOIT P0599 (oil) are two genuinely separate physical lines on the same "
                "Nasser/Zelten-Brega corridor, not one asset double-entered. OPEC ASB "
                "2012 lists them as distinct rows in SEPARATE tables (4.9 oil, 4.10 gas) "
                "with commodity-appropriate capacity units, and an independent 2014 "
                "incident report describes a 36in gas line commissioned 1970 rupturing "
                "at Km 18 - a real asset distinct from the 1961-built oil line. The "
                "length gap that raised the flag is therefore NOT evidence of a "
                "different, longer route: every source converges on ~172 km for the GAS "
                "line too, so 277 km is simply a wrong value. The redundancy question "
                "closes; the spec error stays open and is now the actionable item.",
            ),
        },
    },
}


def main() -> None:
    gas = pd.read_csv(REPO / CSV, header=2, low_memory=False)
    pid_col = next(c for c in gas.columns if c.strip() in ("ProjectID", "Project ID"))
    gas["_sheet_row"] = gas.index + 4
    by_pid = {r[pid_col]: r for _, r in gas.iterrows()}

    resolutions = []
    for key, cl in CLUSTERS.items():
        for p, (ctype, rec, notes) in cl["rows"].items():
            row = by_pid.get(p)
            if row is None:
                raise SystemExit(f"{p} not found in {CSV} - snapshot drift, re-check")
            resolutions.append({
                "project_id": p,
                "sheet_row": int(row["_sheet_row"]),
                "pipeline_name": str(row.get("PipelineName") or ""),
                "segment_name": "" if pd.isna(row.get("SegmentName")) else str(row["SegmentName"]),
                "ref_col": "__VALIDITY__",
                "value_cols": [],
                "primary_value_col": "",
                "primary_value": "",
                "values": {},
                "current_ref": "",
                "class_in": "VALIDITY",
                "class_out": "UNRESOLVED",
                "verdict": "concern",
                "concern_type": ctype,
                "recommendation": rec,
                "proposed_refs": [],
                "verifications": [],
                "tier": "n/a",
                "independent": False,
                "source_language": "en",
                "redundancy_cluster": key,
                "redundancy_cluster_title": cl["title"],
                "researcher_notes": f"[cluster {key}: {cl['title']}] {notes}",
            })

    ctypes: dict[str, int] = {}
    for r in resolutions:
        ctypes[r["concern_type"]] = ctypes.get(r["concern_type"], 0) + 1

    out = {
        "meta": {
            "commodity": "gas",
            "mode": "redundancy",
            "scope": {
                "csv": Path(CSV).name,
                "oil_csv": Path(OIL_CSV).name,
                "country": "Libya",
                "rows": len({r["project_id"] for r in resolutions}),
                "clusters": len(CLUSTERS),
            },
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "n_units": len(resolutions),
            "n_validity_flags": len(resolutions),
            "n_fills": 0,
            "n_status_reviews": 0,
            "n_route_suggestions": 0,
            "class_in_counts": {"VALIDITY": len(resolutions)},
            "class_out_counts": {"UNRESOLVED": len(resolutions)},
            "verdict_counts": {"concern": len(resolutions)},
            "concern_counts": ctypes,
            "cluster_titles": {k: v["title"] for k, v in CLUSTERS.items()},
            "note": (
                "Cluster-level adjudication of duplicate flags raised row-by-row by "
                "libya-gas/annual and libya-gas/ref-sweep-operating. Read-and-flag "
                "only; no edits staged. The prior dirs hold the per-row detection."
            ),
        },
        "resolutions": resolutions,
    }
    (OUT / "staged_resolutions.json").write_text(json.dumps(out, indent=1))
    print(f"wrote {len(resolutions)} validity records across {len(CLUSTERS)} clusters")
    for k, v in CLUSTERS.items():
        print(f"  {k}: {len(v['rows'])} row(s) — {v['title']}")
    print(f"  concern types: {ctypes}")


if __name__ == "__main__":
    main()
