#!/usr/bin/env python3
"""Stage the India-gas redundancy adjudication (§3 `validity` leg, cluster-level).

The operating / in-dev / cancelled deep sweeps and the PNGRB register crosswalk each
raised duplicate-and-overlap questions row-by-row. This pass resolves them into ELEVEN
structural clusters and stages one `__VALIDITY__` record per implicated row carrying
the CLUSTER-level recommendation. Detection lives in the prior dirs; adjudication
lives here. Read-and-flag only — never an edit (QC detects, Update fixes).

    python batches/india-gas/staging/redundancy/build_redundancy.py

India's redundancy profile is unlike Libya's. Libya's clusters were mostly ONE
physical asset entered several times by different aggregators. India's are mostly
**regulatory**: PNGRB authorises a corridor, later amends the terminus or forecloses
the grant and re-lets it in pieces, and GEM ends up carrying both the superseded
authorisation and its successor as separate rows. So the dispositive test is usually
not name similarity — it is **PNGRB's authorisation number, sponsor and authorisation
date, which stay fixed across register editions while the project NAME changes**
(see `docs/reference/source_roster.md` → PNGRB). Four clusters are settled that way.

Five of the eleven clusters REFUTE a duplicate hypothesis outright (D, G, H, I, K),
and E refutes it for four phase pairs while confirming one real defect. Those are
recorded on purpose: an unrecorded refutation gets re-raised by the next sweep, and
three of them (D, H, I) look like textbook duplicates on name alone. G was drafted as
a probable merge and REVERSED on row-level evidence — the capacity gap that made it
look like a duplicate turned out to be the thing distinguishing the two projects.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

CSV = "data/GGIT_gas_snapshot_20260810.csv"
OO_CSV = "data/GEM_operators_owners_snapshot_20260810.csv"
OUT = Path(__file__).resolve().parent
REPO = OUT.parents[3]

PNGRB_MAY26 = "https://pngrb.gov.in/data-bank/20260531-NGPL-MIS-Report.pdf"
PNGRB_2021 = "https://www.pngrb.gov.in/data-bank/NGPL-25062021.pdf"
PNGRB_2024 = "https://www.pngrb.gov.in/data-bank/NGPL-20240626.pdf"

# (concern_type, recommendation, researcher_notes, severity)
CLUSTERS: dict[str, dict] = {
    # ---------------------------------------------------------------- A
    "A": {
        "title": "Bhatinda-Jammu-Srinagar: one foreclosed 725 km grant vs three live rows",
        "refs": [PNGRB_MAY26],
        "rows": {
            "P0908": (
                "duplicate",
                "Retire this row's 725 km / GIGL / proposed framing: PNGRB foreclosed that "
                "authorisation and re-let the corridor in three pieces, two of which GEM "
                "already tracks (P5533+P3913 Bhatinda-Gurdaspur, P5413 Gurdaspur-Jammu). "
                "Recommended: Status=cancelled with ShelvedCancelledType=confirmed. Do NOT "
                "simply shorten the row to the surviving remainder — the ~325 km "
                "Jammu-Srinagar piece PNGRB re-tendered in Dec-2023/Jan-2024 is a NEW, "
                "separately-bid authorisation with no awardee found through Aug-2026, so it "
                "belongs in Discovery as its own candidate row, not as a rescoped P0908.",
                "AGGREGATE-VS-SEGMENT DOUBLE-COUNT, regulatory in origin. P0908 as modelled "
                "(single 725 km Bhatinda->Srinagar line, owner GSPL/GIGL consortium, "
                "Status=proposed) describes an authorisation PNGRB formally voided. The "
                "corridor was then re-let as three separate authorisations. GEM already "
                "carries two of them, so keeping P0908's 725 km on top of P5533 (102 km) + "
                "P3913 (290 km) + P5413 (175 km) = 567 km double-counts ~465-567 km of the "
                "same corridor, under a stale owner and status. The still-open piece is only "
                "the ~325 km Jammu-Srinagar tender. This cluster therefore has BOTH a "
                "retirement and a discovery action, which is why it leads the list.",
                "escalate",
            ),
            "P5533": (
                "spec",
                "KEEP — this is a real, separately-authorised phase, not part of P0908's "
                "double-count. Two open items of its own: (1) Owner is entirely blank on "
                "the operators/owners tab while the register names GIGL as authorisation "
                "holder; (2) with P3913 its phase lengths do not reconcile to the register "
                "(see cluster E).",
                "Phase I of the surviving Bhatinda-Gurdaspur authorisation. Named here so "
                "the P0908 retirement is not misread as retiring this corridor's real rows.",
                "flag",
            ),
            "P3913": (
                "spec",
                "KEEP — real, separately-authorised Phase II. See cluster E for the length "
                "reconciliation and the GSPL-JV ownership inconsistency.",
                "Phase II of the surviving Bhatinda-Gurdaspur authorisation.",
                "info",
            ),
            "P5413": (
                "spec",
                "KEEP — the Gurdaspur-Jammu authorisation is genuinely distinct from P0908, "
                "and it is now GAIL's rather than GIGL's. Its Owner is blank on the "
                "operators/owners tab; the register names GAIL.",
                "The second of the three re-let authorisations. Its existence under a "
                "DIFFERENT owner (GAIL, not GIGL) is part of the evidence that P0908's "
                "single-owner 725 km framing is superseded.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- B
    "B": {
        "title": "JHBDPL: Barauni-Guwahati carried twice, once as its own row",
        "refs": [PNGRB_MAY26],
        "rows": {
            "P0907": (
                "duplicate",
                "Adjudicate against P0929 and, if confirmed a section, retire P0907 and fold "
                "'Barauni-Guwahati Pipeline' into P0929's OtherEnglishNames. SEPARATELY and "
                "regardless of that ruling, correct the owner: it reads Assam Gas Co Ltd, "
                "the register's authorisation holder is GAIL, and GAIL built and operates "
                "it. The owner fix stands even if the duplicate ruling is rejected.",
                "The register carries ONE authorisation whose own name embeds this section — "
                "'Jagdishpur-Haldia-Bokaro Dhamra-Paradip-Barauni-Guwahati' — at 3,546 km "
                "authorised, which is already exactly P0929's LengthKnown. So P0929's length "
                "ALREADY includes this row's 718 km and India's gas total is overstated by "
                "~718 km. Independent corroboration that it is a section: the 2024-05 ERDMP "
                "certification audit published via PNGRB is titled 'GAIL (India) Limited "
                "NGPL network of JHBDPL and BGPL, Barauni-Guwahati and its associated "
                "facilities of Integrated JHBDPL' and treats the Barauni-Guwahati 24in spur "
                "as one operating segment of the same integrated system. The AGCL owner "
                "value looks copy-pasted from the ADJACENT sheet row P0906 (Assam Regional "
                "Gas Network), which is genuinely AGCL's.",
                "escalate",
            ),
            "P0929": (
                "duplicate",
                "KEEP — P0929 is the correct surviving row. If the P0907 retirement is "
                "accepted, add 'Barauni-Guwahati Pipeline' to OtherEnglishNames (it already "
                "carries 'JHBDPL, Pradhan Mantri Urja Ganga project'). No length change: "
                "3,546 km already covers the section.",
                "The system row. Flagged here so the cluster is legible from either side.",
                "info",
            ),
            "P1309": (
                "classification",
                "KEEP and do NOT merge into this cluster — P1309 (IGGL's North East Natural "
                "Gas Pipeline Grid) is a separate authorisation under a separate owner, and "
                "is the row most likely to be wrongly folded into JHBDPL by a future sweep "
                "because both serve the north-east.",
                "REFUTED CONFLATION, recorded to prevent it. The register lists IGGL's "
                "north-east grid as its own authorisation, distinct from GAIL's JHBDPL. "
                "P1309's own open item is different and lives in the crosswalk: the register "
                "shows part of it already operating while GEM carries it wholly as "
                "construction.",
                "info",
            ),
        },
    },
    # ---------------------------------------------------------------- C
    "C": {
        "title": "HVJ/DVPL/GREP: one system capacity (107.00 MMSCMD) stamped on five rows",
        "refs": [PNGRB_MAY26],
        "rows": {
            p: (
                "spec",
                "Do not read 107.00 MMSCMD as this segment's own throughput. The register "
                "reports the HVJ/DVPL/GREP system as ONE authorisation, so 107.00 is the "
                "SYSTEM figure repeated across all five GEM rows. Either record it once on "
                "a network row and leave the segments' own capacities blank, or source each "
                "segment's design capacity individually — but the present state, five rows "
                "each asserting 107.00 MMSCMD as its own, cannot be right and will inflate "
                "any capacity aggregation fivefold.",
                "COMPOSITE_SYSTEM artifact, not five coincidences. P0925 (HVJ, 2,887 km), "
                "P0919 (DVPL-I, 770), P3298 (DVPL-II, 610), P3297 (GREP-I, 505) and P3299 "
                "(GREP-II, 505) all carry Capacity=107.00 MMSCMD. These are series AND "
                "parallel members of GAIL's single integrated HVJ system: series segments' "
                "capacities do not sum, and parallel loops (DVPL-I/II, GREP-I/II) each add "
                "capacity, so no reading of the physical system makes one number correct for "
                "all five. PipelineNetworkGrouping is the column for this and is blank on "
                "every India row (see cluster E). Note the LENGTHS are fine and independent "
                "— this is a capacity-only defect.",
                "flag" if p != "P0925" else "escalate",
            )
            for p in ("P0925", "P0919", "P3298", "P3297", "P3299")
        },
    },
    # ---------------------------------------------------------------- D
    "D": {
        "title": "Langtala trio: three proposals off one gas field, NOT one project (refuted)",
        "refs": [PNGRB_MAY26],
        "rows": {
            "P0936": (
                "duplicate",
                "KEEP all three Langtala rows — the duplicate hypothesis is REFUTED (see "
                "notes). No merge.",
                "REFUTED. P0936 Langtala-Bhilwara (580 km), P2215 Langtala-Jodhpur-Pali "
                "(440 km) and P2748 Langtala-Pachpadra (290 km) share an origin point and a "
                "state and read as one project described three ways — but they have THREE "
                "DIFFERENT owners (Focus Energy, GAIL, GIGL) and three different "
                "destinations in three different directions. Langtala is a gas FIELD (Focus "
                "Energy's SGL field, block RJ-ON/6), so competing evacuation proposals from "
                "rival offtakers are the expected pattern, not a data defect. Corroborating "
                "the field-not-project reading: the operating P1436 'Rajasthan Gas Pipeline "
                "(Focus)' runs from the same SGL/RJ-ON-6 area to the RRVUNL Ramgarh power "
                "plant and was independently confirmed distinct from P3905 "
                "Dandewala-Gamnewala-RSEB Ramgarh in the operating sweep. All three "
                "proposals are cancelled, so nothing is being double-counted in a live "
                "total either.",
                "info",
            ),
            "P2215": (
                "spec",
                "CapacityUnits is the actionable defect in this cluster: 5.00 MMcf/d on a "
                "440 km trunk proposal is ~0.14 MMSCMD, two orders of magnitude too small, "
                "and MMcf/d is anomalous for India (every other India gas row uses MMSCMD or "
                "bcm/y). Almost certainly 5.00 MMSCMD mis-unitised. Confirm against the "
                "original proposal before changing — do not convert blind.",
                "Found while refuting the duplicate hypothesis, which is why it is recorded "
                "here rather than in the ref sweep. The unit is wrong on its face: no source "
                "is needed to see that a 440 km transmission proposal is not 5 MMcf/d, but a "
                "source IS needed to know whether the intended figure was 5 MMSCMD.",
                "flag",
            ),
            "P2748": (
                "duplicate",
                "KEEP — GIGL's Langtala-Pachpadra is a distinct proposal (Pachpadra "
                "refinery offtake). See P0936 for the cluster ruling.",
                "Third member of the refuted cluster.",
                "info",
            ),
        },
    },
    # ---------------------------------------------------------------- E
    "E": {
        "title": "Four phase pairs, zero PipelineNetworkGrouping labels — and one pair "
                 "whose lengths do not reconcile",
        "refs": [PNGRB_MAY26],
        "rows": {
            "P0938": (
                "duplicate",
                "KEEP both phases. Set PipelineNetworkGrouping on this pair (and on the "
                "other three pairs, and on the cluster-C system) — it is blank on ALL 75 "
                "India gas rows even though India has four phase pairs and an eight-row "
                "system, which is precisely what the column exists for. This pair is the "
                "REFERENCE CASE: no value defect, label only.",
                "P0938 Phase I (365 km, operating) + P3602 Phase II (1,517 km, "
                "construction) = 1,882 km, which reconciles to the register's single "
                "Mallavaram-Bhopal-Bhilwara-Vijaipur authorisation on BOTH the operating and "
                "under-construction splits. Phased rows are additive lengths of distinct "
                "pipe, so a phase pair is NOT a double-count and must not be merged — the "
                "only thing missing is the grouping label that makes the relationship "
                "legible. Recorded as the reference case so the three other pairs can be "
                "judged against a known-good one.",
                "info",
            ),
            "P3602": (
                "duplicate",
                "KEEP — Phase II of the reference-case pair. Grouping label only.",
                "See P0938.",
                "info",
            ),
            "P0941": (
                "duplicate",
                "KEEP both phases; grouping label. Lengths reconcile: 1,177 + 763 = 1,940 "
                "km, within 3 km of the register's authorised total for the single "
                "Mehsana-Bhatinda authorisation.",
                "Second clean pair. Its own open item is ownership, not redundancy: this "
                "pair records GIGL's full four-way shareholding while its siblings record "
                "'GSPL 100%' (see the crosswalk's ownership-consistency finding).",
                "info",
            ),
            "P5411": (
                "duplicate",
                "KEEP — Phase II; the SHEET lengths are fine. But the ROUTE is not: this "
                "row's drawn geometry measures 2,317 km against its stated 763 km (3.0x), "
                "and Phase I (P0941) is length-ratio-flagged too. 2,317 km exceeds the "
                "1,940 km of BOTH phases combined, so the Phase II geojson is not Phase II — "
                "it is at least the whole line and probably more. Route-side duplication of "
                "the same corridor across a phase pair, which is the geometry analogue of "
                "the length double-count this leg exists to catch. Route the geometry to a "
                "§8 review; do not touch the sheet lengths, which reconcile to the register.",
                "Found by the packet's route integrity leg after the cluster was drafted. "
                "Recorded here rather than left in the route QC because it is a "
                "redundancy finding that happens to live in the geometry column: the pair's "
                "VALUES are correct and its GEOMETRY double-counts, which is the exact "
                "inverse of cluster A.",
                "flag",
            ),
            "P2746": (
                "duplicate",
                "KEEP both KKBMPL phases; grouping label. This pair's real problem is not "
                "redundancy but UNDERSTATEMENT — see the crosswalk's P0934 escalation, where "
                "both PNGRB (675 km operating) and OSM (306 km of independently-mapped "
                "operating trace) show far more commissioned pipe than GEM's 44 km Phase I. "
                "A THIRD independent line now agrees: GEM's OWN drawn route for P0934 "
                "measures 375 km against its stated 44 km (8.5x — the largest length-ratio "
                "flag in the country), so the understatement is visible inside GEM's own "
                "data without reference to any outside source.",
                "Third pair. Flagged here to keep the phase-pair inventory complete and to "
                "point at the escalation that actually matters for it — which is now "
                "corroborated three ways (PNGRB register, OSM trace, GEM's own geometry) "
                "and is the strongest single finding of the India pass.",
                "flag",
            ),
            "P0934": (
                "duplicate",
                "KEEP — Phase I. See P2746 and the crosswalk escalation.",
                "See P2746.",
                "info",
            ),
            "P5533_E": (
                "spec",
                "THE ONE PAIR THAT DOES NOT CLOSE: P5533 Phase I (102 km) + P3913 Phase II "
                "(290 km) = 392 km against the register's 261 km for the whole "
                "Bhatinda-Gurdaspur authorisation — a 131 km overshoot, where the other "
                "three pairs reconcile. Phase II's 290 km is the likelier defect (Phase I's "
                "102 km is close to a plausible first-section length). Re-read the current "
                "register edition before changing either figure.",
                "The exception that makes the phase-pair convention worth checking rather "
                "than assuming. Because the other three pairs sum correctly to their "
                "register authorisations, the method is sound and this pair is a real "
                "outlier rather than a modelling artifact. Note this row ALSO appears in "
                "cluster A (as a keep) and has a blank owner — three separate open items on "
                "one row.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- F
    "F": {
        "title": "Kanai Chhata: one PNGRB authorisation, two GEM rows "
                 "(settled by register diff)",
        "refs": [PNGRB_2021, PNGRB_2024],
        "rows": {
            "P2214": (
                "duplicate",
                "Merge/retire P2214 into P6562. There is ONE authorisation behind both rows "
                "— PNGRB/Auth/2-NGPL/BID/KSPL/(8)/2019, granted 08.07.2019 to Hooghly "
                "Pipelines Pvt Ltd — whose terminus was shifted from Shrirampur to Panitar "
                "by a 01-Aug-2022 PNGRB amendment. Keeping a 'cancelled' 250 km row "
                "alongside the live 317 km successor double-counts the one real pipeline. "
                "Two further defects on this row if it is retained instead: LengthKnown 250 "
                "km contradicts the register's 317 km in BOTH editions, and "
                "EndState/Province reads Maharashtra when the whole route is in West Bengal.",
                "SETTLED BY REGISTER DIFF, which is the dispositive method for this country: "
                "register row 5.11.NGPL has the SAME sponsor (HPPL), the SAME authorisation "
                "date (08.07.2019), the SAME 317 km and the SAME 19.20 MMSCMD in both the "
                "25-Jun-2021 and 26-Jun-2024 editions — only the NAME changes, from 'Kanai "
                "Chhata - Shrirampur' to 'Kanai - Chhata - Panitar'. The amendment letter "
                "itself (an image-only scan, read by rendering it) states the purpose: "
                "'Amendment in letter of Grant of Authorization for Kanai Chhata - "
                "Shrirampur Natural Gas pipeline due to shifting of termination point from "
                "Shrirampur to Panitar'. So these are not two projects but one authorisation "
                "split across two GEM rows by a rename. The EndState error is separately a "
                "place-name collision: Shrirampur is in Nadia district, West Bengal, not the "
                "Shrirampur in Ahmednagar district, Maharashtra — a 250 km line cannot span "
                "the ~1,500 km between them.",
                "escalate",
            ),
            "P6562": (
                "duplicate",
                "KEEP — P6562 is the surviving row and matches the current register exactly "
                "(317 km, 19.20 MMSCMD). On merge, fold 'Kanai Chhata-Shrirampur Gas "
                "Pipeline' into OtherEnglishNames so the pre-2022 name stays searchable. "
                "Its Owner is blank; the register names HPPL (H-Energy group).",
                "The successor row. Its blank owner is staged separately in the crosswalk.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- G
    "G": {
        "title": "Kakinada-Srikakulam: cancelled authorisation and its 2024 successor "
                 "proposal — two rows, correctly (refuted)",
        "refs": [PNGRB_MAY26],
        "rows": {
            "P0932": (
                "spec",
                "KEEP BOTH ROWS — the duplicate hypothesis is REFUTED. P0932 is the "
                "formally-authorised, formally-cancelled APGDC project; P6538 is PNGRB's "
                "Jan-2024 suo-motu successor proposal for the same corridor at a smaller "
                "scale, which is a distinct forward project rather than P0932 renamed. What "
                "P0932 does need are two value corrections found in the cancelled review: "
                "LengthKnown 275 -> 391 km, and CancelledYear 2024 -> 2023. Also swap the "
                "two mis-filed Start location fields (StartPrefecture/District currently "
                "holds the truncated state name 'Andhra', StartState/Province holds the "
                "district 'East Godavari' — they belong the other way round, matching the "
                "already-correct End columns).",
                "REFUTED, and the capacity gap that made it look like a duplicate is the "
                "evidence: P0932 carries 90.00 MMSCMD, P6538 carries 20.00 MMSCMD, and "
                "PNGRB's Jan-2024 suo-motu relaunch is explicitly for the smaller 20 MMSCMD "
                "scale — so the 4.5x difference is the point of distinction, not a "
                "discrepancy between two records of one thing. Neither row appears in the "
                "line-wise register (P0932 cancelled, P6538 not yet authorised), so the "
                "authorisation-number test that settles clusters A/B/F cannot be run here; "
                "the ruling rests on the cancelled review's own finding that the 2024 "
                "relaunch is a separate proposal with its own gem.wiki article. NOTE the "
                "reframing: this cluster was drafted as a probable merge and reversed on the "
                "row-level evidence.",
                "flag",
            ),
            "P6538": (
                "spec",
                "KEEP — the 2024 successor proposal, not a duplicate of P0932. It does need "
                "filling out: LengthKnown is empty and Owner is blank on the operators/owners "
                "tab. If PNGRB awards the authorisation, the awardee and the authorised "
                "length/capacity will appear in the line-wise register and can be taken from "
                "there. Fold 'Kakinada-Vizag-Srikakulam' into OtherEnglishNames ONLY as a "
                "corridor alias if a source ties the two — do not merge the rows.",
                "The thinner of the two rows (no length, no owner) and therefore the one that "
                "looked like a stub duplicate. Its 20.00 MMSCMD is what identifies it as the "
                "2024 relaunch rather than a restatement of P0932.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- J
    "J": {
        "title": "H-Energy's West Bengal / Digha cluster: five rows off one evolving "
                 "east-coast LNG-evacuation concept",
        "refs": [PNGRB_MAY26, PNGRB_2024],
        "rows": {
            "P3334": (
                "duplicate",
                "Cross-check against P2214/P6562 (cluster F) before next publish. P3334 "
                "'Digha-Contai' (115 km, cancelled, no capacity, no ProposalYear, no "
                "CancelledYear) may be the abandoned precursor of a corridor now tracked as "
                "the Kanai Chhata line rather than an independent proposal. If it is, retire "
                "it into that family; if it stands, it still needs "
                "ShelvedCancelledType=inferred and a capacity. SEPARATELY and regardless: "
                "drop the Financial Express URL from this row's Status/Fuel/PipelineType "
                "[ref] cells — it was fetched and does not mention Contai, 115 km, or this "
                "pipeline at all; it is a 2024 article about the DIFFERENT, later Kanai "
                "Chhata line. Keep the Business Standard 2019 article.",
                "The weakest-documented row in the family and the one most likely to be a "
                "phantom stub: three empty date/capacity fields and a mis-cited ref. The "
                "cancelled review found the underlying commercial concept — evacuating "
                "H-Energy's Digha-area FSRU gas toward Bangladesh — persisted past 2019 via "
                "the Kanai Chhata corridor, which is why the ref that was attached here "
                "actually describes that project. Two readings remain open and no source "
                "settles between them: one evolving project renamed, or an abandoned "
                "precursor plus a live successor. Flagged rather than merged. ROUTE-SIDE "
                "CORROBORATION added after this cluster was drafted: the packet's route "
                "integrity leg measures P3334's own drawn geometry at 599 km against its "
                "stated 115 km — a 5.2x overshoot, and close to P0913's 705 km. A 115 km "
                "feeder carrying a ~600 km route is itself evidence that these rows' "
                "identities are entangled, and it means the geometry must be re-checked "
                "whichever way the merge question is resolved.",
                "flag",
            ),
            "P0913": (
                "classification",
                "Do not merge, but fix the scope: PNGRB's tender bundled this as ONE bid "
                "covering TWO branches off the Contai hub — Contai-Dattapulia (the "
                "Bangladesh-facing leg, which is what GEM's Start/EndLocation records) AND "
                "Contai-Jajpur-Dhamra-Cuttack-Paradip (the Odisha-facing leg, named in the "
                "row's own title but absent from every Location field). So the 705 km length "
                "covers pipe the location columns do not describe. Either record the Paradip "
                "leg's intermediate points, or split the row along the two branches — and "
                "check whether P3334 (Digha-Contai) is the short feeder INTO this hub rather "
                "than a separate proposal.",
                "A scope/granularity defect rather than a duplicate: nothing here is "
                "double-counted, but the row silently aggregates a two-branch authorisation "
                "and the shorter branch is invisible. Independent confirmation that the "
                "bundled tender is real: H-Energy's own EOI cover letter to PNGRB (ref "
                "HEPL/2015/PNGRB/EOI/01, 5 March 2015) is titled for 'Contai (West Bengal) - "
                "Paradip (Odisha) - Dattapulia (West Bengal) Natural Gas Pipeline'. That PDF "
                "is an image-only scan with no text layer, so url_verifier cannot confirm it "
                "and it is deliberately NOT cited as a ref — it informs confidence only.",
                "flag",
            ),
            "P0935": (
                "spec",
                "KEEP as its own row — the Kukrahati-Itinda EOI is a separate, later (Jan "
                "2018) H-Energy filing, NOT part of the Contai-Paradip-Dattapulia bid. Its "
                "own items: ProposalYear 2020 -> 2018 (EOI ref HEPL/BD/PNGRB/KIPL/001, filed "
                "15 Jan 2018), ShelvedCancelledType=inferred with no fabricated ref, and ADD "
                "the Wayback snapshot of the henergy.com Status ref alongside the live URL — "
                "that host now serves a mismatched *.cloudwaysapps.com certificate, which is "
                "a hosting-side SSL failure and NOT evidence of deletion, so the existing ref "
                "must not be dropped.",
                "Recorded here because of a filing artifact that would otherwise look like "
                "evidence of a duplicate: PNGRB published this EOI concatenated into the SAME "
                "PDF as the 2015 Contai-Paradip-Dattapulia EOI (pages 4-6 of "
                "EOI-NG_HEnergy-1.pdf). Two unrelated filings under one URL is a PNGRB "
                "housekeeping quirk, not a GEM data issue — but anyone opening that URL to "
                "check P0913 will find P0935 in it and could reasonably conclude the two rows "
                "trace to one bid. They do not.",
                "flag",
            ),
            "P2214_J": (
                "duplicate",
                "Also a member of this family — but its adjudication is cluster F "
                "(dispositively settled against P6562 by register diff). Listed here so the "
                "H-Energy family reads as complete.",
                "See cluster F.",
                "info",
            ),
            "P6562_J": (
                "duplicate",
                "Also a member of this family — see cluster F. It is the family's one live "
                "asset: everything else in the H-Energy West Bengal group is cancelled.",
                "See cluster F.",
                "info",
            ),
        },
    },
    # ---------------------------------------------------------------- K
    "K": {
        "title": "Kondalapalli-Tirupati vs Kakinada-Vijayawada-Nellore: adjacent Andhra "
                 "corridors, two sponsors (refuted)",
        "refs": [PNGRB_MAY26],
        "rows": {
            "P2752": (
                "duplicate",
                "KEEP both — REFUTED. P2752 (GAIL, Kondalapalli-Tirupati, 450 km, cancelled) "
                "and P1434 (IMC Ltd, Kakinada-Vijayawada-Nellore, 667 km, construction) both "
                "pass through the Vijayawada area but are different routes under different "
                "sponsors and different authorisations. No merge. P2752's own open items are "
                "unsourced Capacity and LengthKnown, which stay UNRESOLVED until a further "
                "PNGRB document surfaces.",
                "REFUTED with the register as the discriminator: P1434 corresponds to a "
                "distinct line-wise authorisation dated 19.02.2018 held by IMC Ltd, at 667 "
                "km — matching GEM's row. GEM already carries it, so this cross-check also "
                "confirms there is no missing row here. Recorded because the cancelled review "
                "explicitly routed the question to this leg, and an unrecorded refutation "
                "gets re-raised.",
                "info",
            ),
            "P1434": (
                "duplicate",
                "KEEP — distinct IMC authorisation. No action from this cluster.",
                "See P2752.",
                "info",
            ),
        },
    },
    # ---------------------------------------------------------------- H
    "H": {
        "title": "Gujarat's three grid rows: two owners, not one network entered thrice "
                 "(refuted)",
        "refs": [PNGRB_MAY26],
        "rows": {
            "P0923": (
                "duplicate",
                "KEEP all three — the duplicate hypothesis is REFUTED. P0923 is GAIL's "
                "Gujarat regional network; P0927/P0937 are GSPL's. Different owners, "
                "different authorisations in the register, different assets.",
                "REFUTED. Three overlapping-sounding rows for one state — 'Gujarat Regional "
                "Gas Network' (608.82 km), 'High Pressure Gujarat Gas Grid Network' (2,207 "
                "km) and 'Low Pressure Gujarat Gas Grid Network' (58 km) — is the shape of a "
                "triple-count, but the register lists GAIL and GSPL authorisations "
                "separately and GEM's owners match that split (GAIL for P0923; GSPL for "
                "P0927 and P0937). Two companies genuinely both operate transmission grids "
                "in Gujarat. No merge.",
                "info",
            ),
            "P0937": (
                "classification",
                "KEEP, but review the classification rather than the redundancy: a 58 km "
                "'Low Pressure' grid attributed to GSPL sits oddly — GSPL is a "
                "high-pressure transmission company, and low-pressure distribution in "
                "Gujarat is Gujarat Gas's business. Either the owner or the "
                "high/low-pressure characterisation is likely wrong, and 58 km is small "
                "enough to be a fragment of something larger.",
                "The one genuinely open question in this refuted cluster. Raised as "
                "classification, not duplicate: nothing suggests it duplicates P0927, only "
                "that it may be mis-attributed or mis-scoped.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- I
    "I": {
        "title": "Uran offshore trunk lines: two real ONGC pipelines, and a missing "
                 "GOIT counterpart (refuted)",
        "refs": [PNGRB_MAY26],
        "rows": {
            "P0926": (
                "duplicate",
                "KEEP both — HUT and MUT are two genuinely distinct ONGC trunk lines, not "
                "one asset entered twice. The real open items on P0926 are elsewhere: "
                "FuelSource reads 'Mumbai High Gas Field' but the line is named for, and "
                "sourced from, the HEERA field; and HUT carries oil as well as gas with no "
                "GOIT row to absorb the oil share, unlike MUT whose oil flow is already "
                "tracked as GOIT P5191.",
                "REFUTED, with independent evidence that they are distinct: India's "
                "Comptroller & Auditor General (Report No. 21 of 2016) treats them as two "
                "lines in one sentence — 'Crude oil from the offshore platform is despatched "
                "to Uran through two pipelines, Mumbai-Uran Trunk line (MUT) and Heera Uran "
                "Trunk line (HUT)' — and reports a measured 3.09% MUT/HUT metering "
                "discrepancy for Aug-2014-Aug-2015, i.e. both flowing and separately "
                "metered. The FuelSource error is the likely origin of any duplicate "
                "suspicion: pointing HUT at Mumbai High makes it look like a second "
                "Mumbai-High-to-Uran line, which is exactly what MUT is.",
                "flag",
            ),
            "P0944": (
                "duplicate",
                "KEEP — MUT is distinct from HUT. No action from this cluster.",
                "See P0926. Named here so the refutation is visible from both rows.",
                "info",
            ),
        },
    },
}

# Rows appearing in more than one cluster carry a suffix in CLUSTERS to keep the
# dict keys unique; strip it to get the real ProjectID.
def _pid(key: str) -> str:
    return key.split("_")[0]


def main() -> None:
    gas = pd.read_csv(REPO / CSV, header=2, low_memory=False,
                      keep_default_na=False, na_values=[])
    gas["_sheet_row"] = gas.index + 4
    by_pid = {r["ProjectID"]: r for _, r in gas.iterrows()}

    resolutions = []
    for key, cl in CLUSTERS.items():
        for rowkey, (ctype, rec, notes, severity) in cl["rows"].items():
            p = _pid(rowkey)
            row = by_pid.get(p)
            if row is None:
                raise SystemExit(f"{p} not found in {CSV} — snapshot drift, re-check")
            resolutions.append({
                "project_id": p,
                "sheet_row": int(row["_sheet_row"]),
                "pipeline_name": str(row.get("PipelineName") or ""),
                "segment_name": str(row.get("SegmentName") or ""),
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
                "severity": severity,
                "recommendation": rec,
                "proposed_refs": cl.get("refs", []),
                "verifications": [],
                "tier": "n/a",
                "independent": False,
                "source_language": "en",
                "wiki": str(row.get("Wiki") or ""),
                "redundancy_cluster": key,
                "redundancy_cluster_title": cl["title"],
                "researcher_notes": f"[cluster {key}: {cl['title']}] {notes}",
            })

    ctypes: dict[str, int] = {}
    sev: dict[str, int] = {}
    for r in resolutions:
        ctypes[r["concern_type"]] = ctypes.get(r["concern_type"], 0) + 1
        sev[r["severity"]] = sev.get(r["severity"], 0) + 1

    out = {
        "meta": {
            "commodity": "gas",
            "mode": "redundancy",
            "scope": {
                "csv": Path(CSV).name,
                "oo_csv": Path(OO_CSV).name,
                "country": "India",
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
            "severity_counts": sev,
            "cluster_titles": {k: v["title"] for k, v in CLUSTERS.items()},
            "note": (
                "Cluster-level adjudication of duplicate/overlap questions raised "
                "row-by-row by india-gas/{ref-sweep-operating,annual,cancelled-review} "
                "and the PNGRB register crosswalk. Read-and-flag only; no edits staged. "
                "FIVE of the eleven clusters REFUTE a duplicate hypothesis (D, G, H, I, K; "
                "plus the four phase pairs in E) — recorded deliberately so the next sweep "
                "does not re-raise them. India's duplicates are regulatory rather than "
                "bibliographic: the dispositive test is PNGRB's authorisation "
                "number/sponsor/date holding constant across register editions while the "
                "project NAME changes."
            ),
        },
        "resolutions": resolutions,
    }
    (OUT / "staged_resolutions.json").write_text(json.dumps(out, indent=1))
    print(f"wrote {len(resolutions)} validity records across {len(CLUSTERS)} clusters")
    for k, v in CLUSTERS.items():
        print(f"  {k}: {len(v['rows'])} row(s) — {v['title']}")
    print(f"  concern types: {ctypes}")
    print(f"  severity:      {sev}")


if __name__ == "__main__":
    main()
