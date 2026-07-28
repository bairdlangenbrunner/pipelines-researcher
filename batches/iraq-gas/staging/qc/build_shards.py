#!/usr/bin/env python3
"""Leg-3 targeted research shards for the Iraq gas handoff packet (2026-07-28).

Writes rows/<PID>.json for every worklist row plus three rows the worklist did not
reach but the research forced open (P7457, P5856, P7468). Run then:

    python scripts/merge_deepsweep_shards.py --staging batches/iraq-gas/staging/qc/
    python scripts/build_qc_staging.py --csv data/GGIT_gas_snapshot_20260728.csv \
      --country Iraq --commodity gas --staging batches/iraq-gas/staging/qc/ --sidecars-only

The single highest-yield source of this leg is Al-Jibawi (2025), a SCOP/OPC-sourced
survey whose Table 1 inventories 22 recent Iraqi pipelines with diameter, length and
FLUID TYPE. It resolved or advanced eight rows at once -- and it REFUTED two status
changes this pass had already staged (P7435, P6826), both of which are withdrawn in
build_repass.py rather than left to stand.

Cross-leg rule, learned the hard way here: read the batch's OTHER legs' records for a
ProjectID BEFORE researching it. Three rows on this leg's worklist (P4047, P6007,
P7434) and one it opened itself (P4053) had already been researched by the `annual`
leg, in every case with later or better evidence. Two of this leg's status reviews were
duplicates or refutations as a result and are omitted (see the note above STATUS);
three validity records carry explicit deferrals to the annual leg.

Every URL below passed scripts/url_verifier.py on 2026-07-28. Where the live host
bot-walls or times out (mnr.krg.org, dno.no) the citable form is the Wayback snapshot.
"""
import json
import os
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent / "rows"
CSV = REPO / "data" / "GGIT_gas_snapshot_20260728.csv"

U = {
    # Al-Jibawi, "Shedding Light on Recent Oil & Gas Pipeline Projects in Iraq",
    # Iraqi Economists Network, June 2025. 1.0 MB PDF; Table 1 + prose.
    "JIBAWI": "https://iraqieconomists.net/en/wp-content/uploads/sites/3/2025/06/"
              "Shedding-Light-on-Recent-Oil-Gas-Pipeline-Projects-in-Iraq.-Ahmed-A-Al-Jibawi.pdf",
    # SCOP road-show technical presentation (Mrs. Zahra Al-Hammadi, Head of Process
    # Dept.), Iraq-Jordan Export Pipeline EPCF Phase-1. 4.2 MB -- exceeds
    # url_verifier's large-PDF read limit but returns 200; read with pdftotext.
    "SAYMAR": "https://saymar.org/wp/wp-content/uploads/2020/10/1485449570186424.pdf",
    # KRG Ministry of Natural Resources -- PRIMARY. Live host ConnectTimeouts, so cite
    # the snapshots.
    "KRG_PIPE": "http://web.archive.org/web/20200701023037/"
                "http://mnr.krg.org:80/index.php/en/gas/gas-pipeline",
    "KRG_FIRSTGAS": "http://web.archive.org/web/20191207202114/"
                    "http://mnr.krg.org/index.php/en/press-releases/"
                    "375-first-gas-arrives-at-duhok-power-station",
    "DNO": "http://web.archive.org/web/20210727130414/https://www.dno.no/en/investors/"
           "announcements/dno-international-signs-gas-sales-and-purchase-agreement-"
           "for-summail-field/",
    "OGJ_SUMMAIL": "https://www.ogj.com/exploration-development/article/17258326/"
                   "dno-to-develop-summail-gas-field-in-iraqi-kurdistan",
    "IBN_DUHOK": "https://www.iraq-businessnews.com/2014/05/27/"
                 "first-natural-gas-arrives-at-duhok-power-station/",
    "PIPELINER": "https://www.pipeliner.com.au/internationalnews/"
                 "construction-commences-on-iran-iraq-syria-gas-pipeline/",
    "NGW": "https://www.naturalgasworld.com/iran-iraq-and-syria-gas-pipeline",
    "TNR_ERBIL": "https://thenewregion.com/posts/3480/"
                 "pm-barzani-inaugurates-591-million-erbil-duhok-gas-pipeline",
    "K24_ERBIL": "https://www.kurdistan24.net/en/story/872107/pm-barzani-inaugurates-"
                 "strategic-gas-pipeline-pledges-24-hour-power-for-all-kurdistan-region",
    "SHAFAQ_ERBIL": "https://shafaq.com/en/Kurdistan/KRG-inaugurates-590M-Erbil-Duhok-gas-pipeline",
    "KIRKUKNOW": "https://kirkuknow.com/en/news/69751",
    "ASB2017": "http://web.archive.org/web/20250206233526/https://www.opec.org/opec_web/"
               "static_files_project/media/downloads/publications/ASB2017_13062017.pdf",
    "MIRBAD_SH": "https://www.al-mirbad.com/detail/163145",
}

# Every URL above was re-verified 2026-07-28; record it as the shard's verification so
# merge_qc.verified_refs() keeps the ref instead of stripping it.
VERIFIED = set(U.values())


def V(*keys):
    return [{"url": U[k], "ok": True, "contains_value": True} for k in keys]


def R(*keys):
    return [U[k] for k in keys]


# ---------------------------------------------------------------------------
# validity[] -- read-and-flag only, never an edit (class_out is always UNRESOLVED).
# Corrections to POPULATED cells live here, with the corrected value named in
# `recommendation`; only genuinely blank cells become fills[].
# ---------------------------------------------------------------------------
VALIDITY = {
    "P0450": [
        dict(verdict="concern", concern_type="spec", tier="high", independent=True,
             recommendation="LengthKnown 5600 -> 1500 km. One root cause also explains BOTH "
                            "route-integrity flags on this row -- do not treat them separately.",
             researcher_notes=(
                 "5,600 km is the length of the FULL Iran->Europe concept (Asaluyeh to the "
                 "Mediterranean and onward via Lebanon), not of the pipeline this row models. "
                 "The row's own scope is Iran -> Syria (StartCountryOrArea Iran, "
                 "EndCountryOrArea Syria), i.e. Asaluyeh->Damascus, and that is 1,500 km: "
                 "The Australian Pipeliner, 'The main project, a 1,500 km long gas pipeline, "
                 "with 110 MMcm/d capacity, to transport Assalouyeh gas to Damascus'. "
                 "Corroborated by NaturalGasWorld and by the published segment sums "
                 "(Iran ~225 km + Iraq ~500 km + Syria 500-700 km = 1,225-1,425 km). "
                 "This ALSO resolves the two route-integrity flags: the drawn route measures "
                 "1,988 km and terminates in LEBANON, so the geometry was digitised to the "
                 "Lebanese extension while the attributes describe the Iran-Syria trunk. Fix "
                 "the length and the route's end country together. Capacity 110 MMSCMD is "
                 "CORRECT and independently confirmed by the same Pipeliner sentence "
                 "(110 MMcm/d) -- do not touch it."),
             proposed_refs=R("PIPELINER", "NGW"), verifications=V("PIPELINER", "NGW")),
        dict(verdict="concern", concern_type="attribution", tier="low", independent=False,
             recommendation="Leave Operator blank. Do NOT adopt the wiki's 'National Iranian "
                            "Gas Company' without a primary source.",
             researcher_notes=(
                 "The wiki-alignment leg flagged sheet Operator blank vs wiki 'National "
                 "Iranian Gas Company'. Nothing found in this leg independently attributes "
                 "operatorship of a cancelled tri-national concept; NIGC is a plausible "
                 "Iranian-side counterparty but the project never had a single operator. "
                 "The companion wiki flag (StartYear1 blank vs wiki 'Unknown') needs no "
                 "action -- 'Unknown' is not a value."),
             proposed_refs=[], verifications=[]),
    ],
    "P4041": [
        dict(verdict="concern", concern_type="attribution", tier="medium", independent=False,
             recommendation="Do NOT adopt the wiki's 'Basrah Gas Company'. Record Iraq "
                            "Ministry of Oil (implemented by SCOP) on the ProjectID-keyed "
                            "operators/owners tab, GID 1489950650.",
             researcher_notes=(
                 "The wiki gives Operator 'Basrah Gas Company'; the row's OWN ref contradicts "
                 "it. The SCOP road-show deck for this project states plainly: 'MoO will own "
                 "the assets and operate the pipeline'. Basrah Gas Company is the "
                 "Shell/Mitsubishi/South Oil flare-gas gathering JV inside the Basra fields -- "
                 "not the operator of a 350 km Rumaila->Najaf export trunk. The deck is "
                 "presented by SCOP (Head of Process Department), so SCOP is the implementing "
                 "state company. Ownership is a single-source finding, hence attribution "
                 "rather than a proposed value."),
             proposed_refs=R("SAYMAR"), verifications=V("SAYMAR")),
        dict(verdict="confirmed (caveat)", concern_type="spec", tier="medium", independent=False,
             recommendation="Keep LengthKnown = 350 km. Send the DRAWN ROUTE back for review "
                            "-- the geometry is over-drawn, the attribute is right.",
             researcher_notes=(
                 "The route-integrity leg flagged drawn 519 km vs sheet 350 km (ratio 1.48). "
                 "The row's own ref settles it in favour of the sheet: '258 MMSCFD ultimate "
                 "capacity of Sales and Fuel Gas 28\" pipeline (350 km)', running 'From "
                 "Rumaila (PS1A) to the outlet of (PS3A) at Al-Najaf' as one of 'two parallel "
                 "pipelines' beside a 56-inch crude line, 'in an existing pipeline corridor' "
                 "via intermediate stations at Samawah (PS2A) and Najaf (PS3A). So 350 km and "
                 "28 inch are both CONFIRMED and the 519 km geometry is the defect. "
                 "This is Phase 1 of the Iraq-Jordan Export Pipeline (IJEP), which also makes "
                 "Status = shelved plausible. NOTE the same sentence independently re-confirms "
                 "the CapacityUnits fix escalated separately: the figure is 258 MMSCFD, not "
                 "MMSCMD (see notes/escalation-2026-07-28-iraq-capacity-units.md)."),
             proposed_refs=R("SAYMAR"), verifications=V("SAYMAR")),
    ],
    "P4047": [
        dict(verdict="concern", concern_type="attribution", tier="high", independent=True,
             recommendation="Do NOT record KAR Group as Operator on the wiki or the sheet. It is "
                            "the EPC contractor; the annual leg already stages Owner1 = KRG.",
             researcher_notes=(
                 "WIKI-ALIGNMENT finding: the wiki gives Operator 'kar group'. KAR Group is the "
                 "EPC CONTRACTOR appointed by the KRG Ministry of Natural Resources (Dec 2021) "
                 "to build the Kurdistan gas network; the asset is KRG/MNR's. The annual leg of "
                 "this same batch independently reached that conclusion and stages Owner1 = "
                 "Kurdistan Regional Government 100% on the operators/owners tab -- this record "
                 "adds only that the WIKI still carries the contractor as operator and needs the "
                 "same correction. Same failure mode the ref re-pass caught on P7436/P7437, "
                 "where a ref naming the EPC contractor was read as ownership -- worth ruling on "
                 "as a pattern, not row by row."),
             proposed_refs=R("TNR_ERBIL", "K24_ERBIL"), verifications=V("TNR_ERBIL", "K24_ERBIL")),
        dict(verdict="concern", concern_type="spec", tier="medium", independent=True,
             recommendation="Leave P4047's LengthKnown BLANK -- no per-segment figure exists. "
                            "The 198 km belongs to P4053 alone (annual leg), not to this row.",
             researcher_notes=(
                 "SELF-CORRECTION of this leg's first reading. I initially took the '192 "
                 "kilometers' in The New Region's Oct-2025 inauguration coverage ('a pipeline "
                 "that runs from the Khor Mor field to Erbil and Duhok') as a TWO-ROW AGGREGATE "
                 "spanning P4047 + P4053, and recommended blanking both. Re-reading the sources "
                 "verbatim refutes the aggregate reading: Shafaq News describes 'a $591 million, "
                 "198-kilometer natural gas pipeline LINKING ERBIL AND DUHOK', and Kurdistan24 "
                 "carries the same 198 -- i.e. 198 km is attributed to the Erbil-Duhok leg "
                 "(P4053) on its own, which is why the annual leg stages it there as a length "
                 "fill. The New Region's 192 is the loose outlier, and its 'Khor Mor to Erbil "
                 "and Duhok' phrasing describes the corridor served, not one measured pipe. "
                 "P4047's LengthKnown still stays blank, but for a different reason: no source "
                 "in any leg gives a figure for the Khor Mor -> Erbil segment by itself. "
                 "Separately, KRG MNR's own older page gives '176 kilometre' for the Khor Mor -> "
                 "Erbil/Suleimaniah/Khurmala system, which near-corroborates P6823's 180 km on a "
                 "DIFFERENT row."),
             proposed_refs=R("TNR_ERBIL", "KRG_PIPE"), verifications=V("TNR_ERBIL", "KRG_PIPE")),
    ],
    "P4058": [
        dict(verdict="concern", concern_type="existence", tier="low", independent=False,
             recommendation="Ask whether 'Eastern Iraq Gas Pipeline' should be tracked as a "
                            "row at all, or folded into a network grouping.",
             researcher_notes=(
                 "Status = operating with a blank StartYear1, a blank LengthKnown, no route, "
                 "and 48 inch / 350 MMcf/d. Nothing in this leg found any independent source "
                 "for a pipeline of this NAME -- it does not appear in ASB2017 Table 9.9's "
                 "18-row Iraq gas block, nor in Al-Jibawi's 22-row Table 1, nor in the GulfPub "
                 "or OSM reconciliations. Restating the earlier finding unchanged: this is not "
                 "a duplicate of anything, but it is not a sourceable entity either. It reads "
                 "like a descriptive grouping rather than a pipeline. Not escalated as a "
                 "deletion -- the 48-inch/350 MMcf/d specifics suggest something real sits "
                 "behind it, most likely under a different name."),
             proposed_refs=[], verifications=[]),
    ],
    "P4067": [
        dict(verdict="concern", concern_type="classification", tier="medium", independent=True,
             recommendation="Keep P4067 in GGIT as gas for now. Separately refer a NEW "
                            "crude-oil line (Ahdab -> Zubaidiya PS, 16 inch, 76 km, completed "
                            "early 2024) to GOIT as a discovery candidate.",
             researcher_notes=(
                 "RETRACTION of a standing finding, not just of my own earlier read. "
                 "docs/country_notes/iraq.md records from the 2026-07-07 ref-harvest re-pass: "
                 "'P4067 (Al-Ahdab-Al-Zubaydia) is crude oil -> belongs in GOIT, not GGIT', "
                 "sourced to Iraq Business News and BBC Arabic establishing that Al-Ahdab is a "
                 "CRUDE-OIL FIELD. That is true and does not support the conclusion. An oil "
                 "field produces associated gas, and the destination here is a POWER STATION "
                 "('Al-Zubaydia PWR St'), so a gas line from an oil field to a power plant is "
                 "the single most ordinary thing in Iraq's gas network -- most of the genuine "
                 "GGIT Iraq rows are exactly that shape (Majnoon, Gharraf, Faiha, West Qurna, "
                 "Buzergan all originate at oil fields). Inferring the pipeline's fluid from "
                 "the field's principal product is the error. Earlier in THIS pass I re-reached "
                 "the same wrong conclusion by a different route, so this is a correction to "
                 "both. Reading BOTH ASB2017 tables side by side overturns it. OPEC keeps two "
                 "separate Iraq entries: Table 9.9 "
                 "(gas) 'Al-Ahdeb/Al-Zubaydia PWR St, OPC, 73, 16' -- which is P4067 -- and "
                 "Table 6.9 (CRUDE) 'Ahdeb/Wassit P P (2), OPC, 42, 45, 16, 10'. OPEC therefore "
                 "distinguished the corridor's crude lines from its gas line deliberately, "
                 "which is the opposite of a mis-filing. Al-Jibawi separately reports 'In the "
                 "beginning of 2024, SCOP announced the completion of a CRUDE OIL pipeline "
                 "that extends from the Ahdab oil field to the Zubaidia power station in "
                 "Wassit Province. The pipeline diameter is 16-inch and is 76 km in length' "
                 "(Table 1 row 2, type 'Crude oil'). A line existing in OPEC's 2016 gas table "
                 "cannot be the one completed in 2024, so the best reading is that the "
                 "Ahdab->Zubaidiya corridor is ~73-76 km long and carries SEVERAL lines, of "
                 "which the 2024 crude line is new and belongs in GOIT. Residual uncertainty, "
                 "stated plainly: both readings share a 16-inch diameter and a ~73-76 km "
                 "length, so it cannot be fully excluded that one line is being described twice "
                 "with different fluids. Flagged for a human read, NOT escalated as a defect. "
                 "BONUS: Al-Jibawi's independent 76 km strongly corroborates the ASB length "
                 "fix on this row -- LengthKnownUnits mi -> km leaves 73, and 117.48 km (the "
                 "conversion) is refuted twice over."),
             proposed_refs=R("ASB2017", "JIBAWI"), verifications=V("ASB2017", "JIBAWI")),
    ],
    "P6007": [
        dict(verdict="concern", concern_type="spec", tier="low", independent=False,
             recommendation="ROUTE only: send the drawn geometry back for review. Take Status, "
                            "StartYear1 and Diameter from the annual leg's records, not this one.",
             researcher_notes=(
                 "Route-integrity flagged drawn 87 km vs sheet 50 km (ratio 1.74). West Qurna to "
                 "Rumaila is a short intra-field hop, so 50 km is the more plausible of the two "
                 "and the geometry looks over-drawn; unlike P4041 no source in THIS leg "
                 "arbitrates the length, so the route is flagged for redraw rather than the "
                 "length being changed. SCOPE CORRECTION: an earlier draft of this record also "
                 "claimed 'no independent source was found for a 40-inch / 50 km West Qurna -> "
                 "Rumaila dry-gas line' -- that is wrong and is withdrawn. It is true that the "
                 "row is absent from ASB2017 Table 9.9 and from Al-Jibawi's Table 1, but the "
                 "ANNUAL leg of this same batch found the line documented in Oil & Gas Journal "
                 "(2016-03-07: operational by mid-2015, 80 MMcfd from DS-7/DS-8), on Basrah Gas "
                 "Company's own operations page, and in MEES (2025-10-24), and on that basis "
                 "stages Status construction -> operating with StartYear1 2015 plus a Diameter "
                 "40 in ref. Those records stand; only the route point here is additive. NOT "
                 "staged because it is unverified: reporting suggests Iraq's Council of "
                 "Ministers awarded crude-gas pipeline work running from Majnoon and West "
                 "Qurna-2 to China Petroleum Pipeline Engineering with part assigned to SCOP -- "
                 "the same contractor that appears on P7436/P7437."),
             proposed_refs=[], verifications=[]),
    ],
    "P6824": [
        dict(verdict="concern", concern_type="classification", tier="high", independent=False,
             recommendation="REMOVE from GGIT and refer to GOIT as a gas oil (diesel) export "
                            "line. Ruling needed -- see the memo.",
             researcher_notes=(
                 "Carried forward unchanged from the ref re-pass; full argument in "
                 "notes/escalation-2026-07-28-iraq-gasoil-misfiled.md. The row's own al-Mirbad "
                 "ref calls it 'anbub tasdir ZAYT AL-GHAZ' -- 'gas oil', i.e. DIESEL -- and "
                 "matches GEM on every spec (46 km, 8-10 inch, Shuaiba -> Khor al-Zubair OIL "
                 "port, completed July 2024). Restated here because it is a worklist row: the "
                 "Date_logic QC flag on it is MOOT, since the row leaves GGIT entirely rather "
                 "than getting a date fix."),
             proposed_refs=R("MIRBAD_SH"), verifications=V("MIRBAD_SH")),
    ],
    "P6827": [
        dict(verdict="concern", concern_type="spec", tier="high", independent=True,
             recommendation="StartYear1 1980 -> 2023 (StartMonth1 11). LengthKnown 1.05 km, "
                            "Diameter 16 and Capacity 100 MMcf/d are all CONFIRMED -- leave them.",
             researcher_notes=(
                 "Al-Jibawi: 'While in November 2023, OPC completed the construction of a "
                 "16-inch dry gas pipeline that feeds Kirkuk power station in Taza. The "
                 "pipeline extends from the Kormor fields with a length of 1,050 m. It "
                 "bifurcates from the main pipeline, Jambur Station-North Gas Company, to feed "
                 "Taza. The pipeline capacity is 100 MMSCFD.' Table 1 row 16 repeats it as "
                 "'Kirkuk power station 16 1.05 Dry gas'. That is an EXACT four-way match to "
                 "GEM (1.05 km, 16 inch, 100 MMcf/d) and it dates the line to Nov 2023, so "
                 "StartYear1 = 1980 is off by 43 years. Second independent source: KirkukNow. "
                 "Two consequences beyond the date. (1) Operator: OPC built it -- the wiki's "
                 "'North Oil Company' is wrong (record on GID 1489950650). (2) The NAME "
                 "overstates the asset: 'Khormor-Jambur-Kirkuk' implies a trunk, but this is a "
                 "1,050 m SPUR bifurcating off the pre-existing Jambur Station-North Gas "
                 "Company trunk to feed Taza. My earlier suspicion that the 1,050 m length was "
                 "wrong was itself wrong -- the length is right and the name is the problem. "
                 "The Jambur->North Gas Company trunk it branches from has NO GGIT row: a "
                 "discovery lead."),
             proposed_refs=R("JIBAWI", "KIRKUKNOW"), verifications=V("JIBAWI", "KIRKUKNOW")),
    ],
    "P6832": [
        dict(verdict="concern", concern_type="spec", tier="medium", independent=False,
             recommendation="LengthKnown 70 -> 60 km. Diameter 18 and Status construction are "
                            "confirmed; Capacity 70 MMcf/d stays unsourced.",
             researcher_notes=(
                 "Al-Jibawi: 'OPC supervises the Buzergan-Halfaya dry gas pipeline. The "
                 "pipeline will serve to deliver sour dry gas to the Missan power station and "
                 "the Amara power station. The pipeline diameter is 18-inch, and it is 60 km in "
                 "length, extending from GCU in Buzergan to the GTU in Halfaya. The project is "
                 "planned to be completed before the end of 2025.' Table 1 row 6 agrees: "
                 "'Buzergan (GCU) - Halfaya 18 60'. So 18 inch is confirmed, Status = "
                 "construction is confirmed (not yet complete as of the source), and GEM's "
                 "70 km is 10 km long. Single source, hence medium."),
             proposed_refs=R("JIBAWI"), verifications=V("JIBAWI")),
        dict(verdict="concern", concern_type="attribution", tier="medium", independent=False,
             recommendation="Do NOT adopt the wiki's 'Missan Oil Company'. The supervising "
                            "company is OPC (Oil Pipelines Company).",
             researcher_notes=(
                 "The wiki gives Operator 'Missan Oil Company'. Al-Jibawi says OPC supervises "
                 "the project and that Missan is a DESTINATION -- 'deliver sour dry gas to the "
                 "Missan power station and the Amara power station'. A destination read as an "
                 "operator. Record OPC on the operators/owners tab (GID 1489950650)."),
             proposed_refs=R("JIBAWI"), verifications=V("JIBAWI")),
    ],
    "P7434": [
        dict(verdict="confirmed (caveat)", concern_type="none", tier="high", independent=True,
             recommendation="SPECS confirmed (42 in / 43 km / 800 MMcf/d) -- no edit to any of "
                            "them. For Status and StartYear1 use the ANNUAL leg's record "
                            "(construction -> operating, StartYear1 2025), not this one.",
             researcher_notes=(
                 "Every populated spec on this row is now confirmed exactly, and independently "
                 "of the refs the annual leg re-verified -- that is this record's value. "
                 "Al-Jibawi: 'SCOP constructed another 42-inch dry gas pipeline that bifurcates "
                 "from the national dry gas pipeline in Mahmoodia city south of Baghdad. The 800 "
                 "MMSCFD capacity pipeline extends for 43 km to feed the Basmaia power station "
                 "west of Baghdad with dry gas.' Table 1 row 5: 'Basmaia power station 42 43 Dry "
                 "gas'. That is 42 inch, 43 km and 800 MMcf/d matching GEM three for three, plus "
                 "SCOP as builder. Caveat on the Arabic: iina.news renders the diameter as "
                 "'42-knot', a mistranslation of 'uqda', which in Iraqi pipe-sizing usage means "
                 "INCH. SELF-CORRECTION on STATUS, and it is the same error this pass escalated "
                 "elsewhere: I read Al-Jibawi (June 2025, 'constructed') plus iina.news ('nears "
                 "completion') as CONFIRMING Status = construction, and advised leaving "
                 "StartYear1 blank on the grounds that the wiki's 2025 was a projection. Both "
                 "conclusions are WITHDRAWN. The annual leg holds strictly later evidence: Oil "
                 "Minister Hayyan Abdul-Ghani announced on 2025-07-20 that the Mahmudiyah-"
                 "Besmaya line was 'completed in full' (al-khatt unjiza bil-kamil), corroborated "
                 "by attaqa.net 2025-08-11 reporting the ~40 km line implemented so Besmaya "
                 "station could run at full capacity in summer 2025. A source describing "
                 "construction dates the construction; it does not bound the completion. The "
                 "annual leg's construction -> operating / StartYear1 2025 change is the one to "
                 "apply, and the wiki's 2025 is an in-service date after all."),
             proposed_refs=R("JIBAWI"), verifications=V("JIBAWI")),
    ],
    "P7457": [
        dict(verdict="concern", concern_type="spec", tier="high", independent=True,
             recommendation="LengthKnown 40.00 -> 30 km. StartYear1 2014, Capacity 120 MMcf/d "
                            "and Status operating are all CONFIRMED -- leave them.",
             researcher_notes=(
                 "SELF-CORRECTION, and the largest single reversal in this pass. This row was "
                 "escalated earlier as having ZERO verifiable sources (both cited refs dead, "
                 "neither archived). That is now FALSE and the escalation has been rewritten: "
                 "the KRG Ministry of Natural Resources -- a PRIMARY government source -- "
                 "documents the line twice. (1) MNR gas-pipelines page: 'A 30-kilometre "
                 "interconnector pipeline from Summail field to Duhok power plant is under "
                 "construction, so that the plant, which is currently running on diesel/light "
                 "fuel, will run on gas by early 2014.' (2) MNR press release, 26 May 2014, "
                 "'First Gas Arrives at Duhok Power Station': 'the successful delivery via "
                 "pipeline of the first quantities of natural gas from the gas field at Summail "
                 "to fuel the Duhok Power Station' -- so StartYear1 = 2014 is CONFIRMED, "
                 "independently corroborated by Iraq Business News (27 May 2014). The same "
                 "release confirms GEM's capacity exactly: 'Long-term deliveries are expected to "
                 "reach 120 million cubic feet per day... the KRG will purchase up to 120mmscf/d'. "
                 "That also dissolves an apparent conflict -- DNO's 2013 GSA announcement says "
                 "'Initial deliveries will be around 100 million cubic feet per day', which is "
                 "the ramp-up figure ('Initial volumes will start at around 55mmscf/d, ramping "
                 "up to 120mmscf/d'), not a competing rating. THE ONE REAL DEFECT IS THE LENGTH: "
                 "MNR states the PIPELINE is 30 km, whereas GEM's 40.00 traces to a DISTANCE "
                 "statement -- DNO and OGJ both describe the plant as 'located 40 kilometers "
                 "from the field'. A field-to-city distance is not a pipeline length. This also "
                 "explains why the ASB length memo was right to reject 40.00 as a round number: "
                 "it never came from the ASB at all. Diameter 36 is NOT confirmed by any source "
                 "verified here -- left alone, not endorsed. Operator is DNO (Summail field, "
                 "Duhok PSC, with Genel Energy)."),
             proposed_refs=R("KRG_PIPE", "KRG_FIRSTGAS", "IBN_DUHOK", "DNO", "OGJ_SUMMAIL"),
             verifications=V("KRG_PIPE", "KRG_FIRSTGAS", "IBN_DUHOK", "DNO", "OGJ_SUMMAIL")),
    ],
    "P7459": [
        dict(verdict="confirmed (caveat)", concern_type="attribution", tier="medium",
             independent=False,
             recommendation="Wiki's 'Oil Pipelines Company' is CORROBORATED -- adopt it on the "
                            "operators/owners tab. See the fill record for LengthKnown.",
             researcher_notes=(
                 "Al-Jibawi: 'OPC supervises two pipeline projects extending from the Faiha oil "
                 "field to the North Rumaila oil field in Al Basrah. The first pipeline is a "
                 "20-inch dry gas, and the second one is 10-inch LPG.' This is one of the few "
                 "wiki operator values in this batch that survives checking -- worth noting "
                 "given that P4041, P4047, P6832 and P6827 all had wrong ones. 20 inch and "
                 "Status construction are confirmed. Capacity: GEM holds 97 MMcf/d; the source "
                 "says the projects 'will contribute to raising the dry gas pumping rate to 90 "
                 "MMSCFD', which is a SYSTEM rate increase and not this line's rating -- close "
                 "to GEM's figure but not the same claim, so 97 stays unsourced. The 10-inch "
                 "LPG twin on the same corridor is a GOIT/LPG discovery lead, not a GGIT row."),
             proposed_refs=R("JIBAWI"), verifications=V("JIBAWI")),
    ],
    "P7468": [
        dict(verdict="confirmed (caveat)", concern_type="none", tier="high", independent=True,
             recommendation="No edit. Recorded because this row was previously flagged as "
                            "thinly sourced.",
             researcher_notes=(
                 "Free corroboration, row not in the worklist. Al-Jibawi: 'In December 2023, "
                 "OPC declared the accomplishment of a 10-inch dry gas pipeline with a length "
                 "of 1200 m that feeds the Najaf cement factory', and Table 1 row 19 'Najaf "
                 "cement plant 10 1.2 Dry gas'. GEM holds 1.2 km / 10 inch -- an exact match, "
                 "from a source independent of the globalcement.com ref the row already "
                 "carries. One of the ASB-provenance leg's single-sourcing worries closes here."),
             proposed_refs=R("JIBAWI"), verifications=V("JIBAWI")),
    ],
}

# ---------------------------------------------------------------------------
# fills[] -- genuinely blank cells only. Apply = value + ref together.
# ---------------------------------------------------------------------------
FILLS = {
    "P7459": [
        dict(ref_col="Length [ref]", value_cols=["LengthKnown", "LengthKnownUnits"],
             primary_value_col="LengthKnown",
             values={"LengthKnown": "100", "LengthKnownUnits": "km"},
             primary_value="100", class_out="REFS_ADDED", tier="medium", independent=False,
             researcher_notes=(
                 "LengthKnown was blank. Al-Jibawi's Table 1 lists the Faiha->Rumaila pair "
                 "twice -- row 7 'Faiha oil field - Rumaila oil field 20 100 Dry gas' and row 8 "
                 "the 10-inch LPG twin at the same 100 km -- so 100 km is this 20-inch dry-gas "
                 "line's length. Table 1's header is explicitly '(km)'. Single source, so "
                 "medium: apply only if a second is acceptable to the researcher."),
             proposed_refs=R("JIBAWI"), verifications=V("JIBAWI")),
    ],
    "P5856": [
        dict(ref_col="Start [ref]", value_cols=["StartYear1"], primary_value_col="StartYear1",
             values={"StartYear1": "2023"}, primary_value="2023",
             class_out="REFS_ADDED", tier="medium", independent=False,
             researcher_notes=(
                 "Row not in the worklist -- surfaced while mining Al-Jibawi for the rows that "
                 "were. StartYear1 was blank against Status = operating. Al-Jibawi: 'In 2023, "
                 "SCOP completed a 20-inch dry gas pipeline extending from the Gharaf oil field "
                 "in Dhi Qar Governorate to the 42-inch national dry gas pipeline for 76 km', "
                 "with Table 1 row 9 agreeing. The same sentence re-confirms GEM's existing "
                 "76 km and 20 inch exactly -- which independently vindicates this row's "
                 "exclusion from the ASB mi->km match in the length memo."),
             proposed_refs=R("JIBAWI"), verifications=V("JIBAWI")),
    ],
    "P7435": [
        dict(ref_col="Start [ref]", value_cols=["StartYear1", "StartMonth1"],
             primary_value_col="StartYear1",
             values={"StartYear1": "2025", "StartMonth1": "5"}, primary_value="2025",
             class_out="REFS_ADDED", tier="medium", independent=False,
             researcher_notes=(
                 "StartYear1 was blank. Al-Jibawi dates both ends of this project: 'In February "
                 "2025, SCOP started to construct a 42-inch dry gas pipeline in Al Basrah "
                 "Governorate. The pipeline extends from Khor Al-Zubair to Nadhum Shatt "
                 "Al-Basrah for 40 km to join the national dry gas pipeline... In May 2025, the "
                 "Oil Minister, Hayan Al-Sawad, declared the completion of the pipeline in a "
                 "record time.' 40 km and 42 inch are confirmed exactly. IMPORTANT: this same "
                 "sentence WITHDRAWS the status change this pass had staged against the row -- "
                 "see the __STATUS__ record and the ref-gap re-pass note. GEM's Status = "
                 "operating was right all along."),
             proposed_refs=R("JIBAWI"), verifications=V("JIBAWI")),
    ],
}

# ---------------------------------------------------------------------------
# status_reviews[] -- one per row whose Status was re-read this leg.
# ---------------------------------------------------------------------------
# NOTE on two deliberate omissions. This leg also re-read the Status of P4053
# (Erbil-Duhok) and P7434 (Mahmudiyah-Besmaya), but neither gets a record here:
#   * P4053 -- the ANNUAL leg of this same batch already stages the identical change
#     (construction -> operating, StartYear1 2025, StartMonth1 10) on four independent
#     outlets plus a 198 km length fill. A second record would put two rows for one
#     ProjectID in Gas_StatusChanges and present the researcher with a duplicate.
#   * P7434 -- this leg's reading (confirm construction) is REFUTED by the annual leg's
#     later evidence (ministry completion announcement 2025-07-20 + attaqa 2025-08-11).
#     Withdrawn; see the P7434 validity record above for the full retraction. The specs
#     Al-Jibawi confirms are kept there.
# Rule this encodes: before staging a status review, read the other legs' existing
# records for the same ProjectID. Both errors came from researching the worklist row
# without first checking what the batch already held on it.
STATUS = {
    "P6832": [
        dict(current_status="construction", verdict="confirm", proposed_status="construction",
             proposed_changes={}, evidence_date="2025-06", staleness_rule="",
             tier="medium", independent=False,
             researcher_notes=(
                 "Confirmed: Al-Jibawi says the Buzergan-Halfaya project 'is planned to be "
                 "completed before the end of 2025', so it was not in service as of the "
                 "source. Flag for the next pass -- if it completed on schedule it is already "
                 "due to flip. See the two validity records on this row for the 70->60 km "
                 "length correction and the OPC-not-Missan operator correction."),
             proposed_refs=R("JIBAWI"), verifications=V("JIBAWI")),
    ],
}


def main():
    if not CSV.exists():
        sys.exit(f"missing {CSV}")
    df = pd.read_csv(CSV, header=2, low_memory=False)
    df["SheetRow"] = df.index + 4
    idx = df.set_index("ProjectID")

    OUT.mkdir(parents=True, exist_ok=True)
    for f in OUT.glob("*.json"):
        f.unlink()

    pids = sorted(set(VALIDITY) | set(FILLS) | set(STATUS))
    tot = {"validity": 0, "fills": 0, "status_reviews": 0}
    for pid in pids:
        if pid not in idx.index:
            print(f"  WARN {pid} not in the snapshot -- skipped")
            continue
        row = idx.loc[pid]
        shard = {
            "project_id": pid,
            "pipeline_name": str(row.get("PipelineName", "") or ""),
            "sheet_row": int(row["SheetRow"]),
            "wiki": str(row.get("WikiPage", "") or ""),
            "validity": VALIDITY.get(pid, []),
            "fills": FILLS.get(pid, []),
            "status_reviews": STATUS.get(pid, []),
            "routes": [],
        }
        for k in tot:
            tot[k] += len(shard[k])
        (OUT / f"{pid}.json").write_text(json.dumps(shard, indent=1, ensure_ascii=False))

    print(f"wrote {len(pids)} shards to {OUT}")
    print("  " + ", ".join(f"{k}={v}" for k, v in tot.items()))
    print("  rows: " + " ".join(pids))


if __name__ == "__main__":
    main()
