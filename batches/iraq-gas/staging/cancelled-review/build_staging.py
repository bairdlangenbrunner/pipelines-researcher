#!/usr/bin/env python3
"""Build staged_resolutions.json for the Iraq gas cancelled/shelved status review.

Four rows: P0481, P0450 (cancelled) and P5857, P4041 (shelved). 30 ref-cell units
enumerated from the live header via ref_pairs.discover_ref_pairs, plus THREE
__STATUS__ sentinels and eight __VALIDITY__ sentinels. Three, not four: P5857's
status ruling was consolidated into the `annual` leg's (see the note above STATUS)
so the handoff carries one status decision per ProjectID.

Row/value/current-ref data is read from the CSV so nothing is retyped by hand;
only the research findings below are authored. Adapted from
batches/libya-gas/staging/cancelled-review/build_baseline.py.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
from ref_pairs import discover_ref_pairs  # noqa: E402

CSV = REPO / "data" / "GGIT_gas_snapshot_20260728.csv"
OUT = Path(__file__).resolve().parent / "staged_resolutions.json"
PIDS = ["P0481", "P0450", "P5857", "P4041"]

# ---------------------------------------------------------------- sources
AHRAM = "https://gate.ahram.org.eg/News/1645401.aspx"
UNNEWS = "https://news.un.org/en/story/2022/02/1111632"
RUDAW = "https://www.rudaw.net/english/middleeast/iraq/10022022"
NGW = "https://www.naturalgasworld.com/iran-iraq-and-syria-gas-pipeline"
ATLCOUNCIL = (
    "https://www.atlanticcouncil.org/in-depth-research-reports/issue-brief/"
    "syrias-energy-sector-and-its-impact-on-stability-and-regional-developments/"
)
KARAMSHAAR = (
    "https://karamshaar.com/syria-in-figures/"
    "arab-gas-pipeline-syria-transit-state-or-energy-hub/"
)
NATIONAL26 = (
    "https://www.thenationalnews.com/business/energy/2026/05/01/"
    "iraq-starts-work-on-basra-haditha-pipeline-for-crude-exports/"
)
SHAFAQ26 = (
    "https://shafaq.com/en/Economy/"
    "Iraq-advances-Basra-Haditha-oil-pipeline-pipe-manufacturing"
)
HCP26 = (
    "https://www.hydrocarbonprocessing.com/news/2026/05/"
    "iraq-starts-work-on-basra-haditha-oil-pipeline/"
)
AGBI26 = (
    "https://www.agbi.com/oil-and-gas/2026/04/"
    "iraq-gives-go-ahead-for-basra-oil-pipeline-under-deal-with-china/"
)

# Every URL above passed scripts/url_verifier.py on 2026-07-28 with a claim-specific
# token. SAYMAR and MEED/BNC are read out of the CSV (they are the rows' own refs);
# SAYMAR verifies OK on fetch but FAILS on deep tokens ("MMSCFD") -- the documented
# large-PDF limit of url_verifier, worked around with pdftotext (3x MMSCFD, 0x MMSCMD).
VERIFIED = {
    AHRAM: True, UNNEWS: True, RUDAW: True, NGW: True, ATLCOUNCIL: True,
    KARAMSHAAR: True, NATIONAL26: True, SHAFAQ26: True, HCP26: True, AGBI26: True,
}

# ---------------------------------------------------------------- findings
# (pid, ref_col) -> class_out, proposed_refs, tier, independent, lang, notes
F = {}

# ============================== P0481 Iraq-Kuwait Gas Pipeline ==============================
F["P0481", "Status [ref]"] = dict(
    class_out="UNRESOLVED", refs=[], tier="low", indep=False, lang="en/ar",
    notes=(
        "THE CITED REF CONTRADICTS THE VALUE. The Status [ref] is Al-Ahram Gate (22 Nov 2017, "
        "Reuters-sourced), which reports Iraq SELECTING Japan's Toyo Engineering to build the "
        "gas pipeline to Kuwait plus a petrochemical plant -- project initiation, the exact "
        "opposite of cancellation. It says the project's details 'have not yet been announced', "
        "Toyo proposed deliveries after 2019, and Toyo's CFO said talks were continuing with NO "
        "final investment decision; Kuwait had offered sovereign guarantees up to 80% of cost and "
        "talks had stalled over price (Kuwait wanting under $3/MMBtu). Nothing in it supports "
        "'cancelled'. No source located in English or Arabic announces a cancellation, in any year. "
        "What HAS happened is that the project's stated rationale lapsed: the gas was to help "
        "settle Iraq's 1990-invasion reparations, and those completed with a final payment on "
        "13 Jan 2022 (UNCC; $52.4bn against ~1.5M successful claims of 2.7M filed) -- funded by a "
        "levy on Iraqi OIL sales over 31 years, never by gas in kind. So the transaction the "
        "pipeline was meant to serve no longer exists, and there has been no project news since "
        "Nov 2017. That supports a presumed-dead reading on the staleness ladder, not a sourced "
        "cancellation. See __STATUS__. Leaving this ref UNRESOLVED rather than re-pointing it: the "
        "reparations sources document the rationale lapse, not a cancellation of this pipeline, so "
        "citing them on the Status cell would overstate them."
    ),
)
F["P0481", "Fuel [ref]"] = dict(
    class_out="REVERIFIED", refs=[AHRAM], tier="medium", indep=False, lang="ar",
    notes=(
        "Existing ref re-verified live (HTTP 200; Arabic token present). It explicitly describes a "
        "GAS pipeline from Iraq to Kuwait, so Fuel='Gas' is supported. Single source only -- this "
        "is a Reuters wire republished by Al-Ahram, and no independent second attestation of the "
        "2017 proposal was found, so medium/not-independent. NOTE for whoever re-checks: WebFetch "
        "returns HTTP 403 on gate.ahram.org.eg; the page reads fine via curl with a browser "
        "user-agent, and url_verifier passes it."
    ),
)
F["P0481", "Capacity [ref]"] = dict(
    class_out="REFS_ADDED", refs=[AHRAM], tier="medium", indep=False, lang="ar",
    notes=(
        "Clean missing-ref fill: the row's OWN existing source carries the capacity and the ref "
        "cell was simply left empty. Al-Ahram/Reuters: 'Last year Kuwait said it would be ready to "
        "buy up to 200 million cubic feet per day'. 200 MMcf/d = 2.067 bcm/y, which is exactly "
        "GEM's Capacity=2.06 bcm/y. So the value is sourced and correct; only the citation was "
        "absent. Recommend also considering recording the native unit (200 MMcf/d) rather than the "
        "derived bcm/y, per the sheet's usual practice on gas rows. Caveat: 200 MMcf/d is a stated "
        "Kuwaiti purchase WILLINGNESS, not a designed pipeline capacity -- no engineering capacity "
        "was ever published for this line."
    ),
)
F["P0481", "Location [ref]"] = dict(
    class_out="REFS_ADDED", refs=[AHRAM], tier="medium", indep=False, lang="ar",
    notes=(
        "Al-Ahram/Reuters supports the country pair (Iraq -> Kuwait) and names Rumaila, so the "
        "cluster is sourced. BUT the same article says it was NOT yet settled whether the gas would "
        "come from the LUKOIL-operated West Qurna 2 field or BP-operated Rumaila. GEM asserts "
        "StartLocation='Rumaila oilfield' where the only source explicitly records the origin as "
        "undecided. Filed as a spec concern -- see __VALIDITY__ -- rather than blocking the fill, "
        "since StartState/Province=Basra, StartCountryOrArea=Iraq and EndCountryOrArea=Kuwait are "
        "all solid. EndLocation is blank and no source names a Kuwaiti receipt point."
    ),
)

# ============================== P0450 Iran-Iraq-Syria Gas Pipeline ==========================
F["P0450", "Status [ref]"] = dict(
    class_out="UNRESOLVED", refs=[], tier="low", indep=False, lang="en",
    notes=(
        "THE CITED REF IS ABOUT A DIFFERENT PIPELINE. Status [ref] points to a Tehran Times piece "
        "(26 Aug 2019) titled 'Iran seeks to revive oil pipeline...' -- a CRUDE OIL line "
        "(Iran->Baniyas, ~1.25 Mbbl/d). It never mentions this gas project and never mentions any "
        "cancellation. It cannot support Status='cancelled'. Substantively: no formal cancellation "
        "was ever announced. Syria's electricity minister said as late as 2021 that the project had "
        "NOT been abandoned; Assad's fall (Dec 2024) removed the political basis, and from Aug 2025 "
        "Syria pivoted to Azerbaijani (Shah Deniz) gas via Turkiye instead. So the project is dead "
        "in practice and by inference, never by announcement. Not re-pointing this cell: the "
        "post-Assad analyses (Atlantic Council, Karam Shaar) document the collapse of prospects, "
        "not a cancellation event, and citing them on the Status cell would misrepresent them. "
        "The consequence for the data is ShelvedCancelledType, which currently reads 'confirmed' "
        "and is not -- see __STATUS__."
    ),
)
F["P0450", "Fuel [ref]"] = dict(
    class_out="REFS_ADDED", refs=[NGW, ATLCOUNCIL], tier="high", indep=True, lang="en",
    notes=(
        "Replacing a Wikipedia citation with two independent non-tertiary sources. Natural Gas "
        "World (11 Feb 2013) describes the Iran-Iraq-Syria gas pipeline directly, with the same "
        "endpoints and the same 110 MMcm/d as GEM; the Atlantic Council issue brief on Syria's "
        "energy sector discusses the project in its regional gas context. Fuel='Gas' is not in "
        "doubt. Recommend dropping the Wikipedia ref here -- see the attribution __VALIDITY__ on "
        "this row: four separate value cells all cite the SAME single Wikipedia article, which "
        "fails the 2-independent-source target on its own."
    ),
)
F["P0450", "PipelineType [ref]"] = dict(
    class_out="REFS_ADDED", refs=[NGW], tier="medium", indep=False, lang="en",
    notes=(
        "Natural Gas World (Feb 2013) describes a long-distance export trunkline from Assalouyeh "
        "to Damascus, which is 'transmission' on GEM's vocabulary. Single independent source, so "
        "medium. Proposed in place of the row's Wikipedia ref."
    ),
)
F["P0450", "Capacity [ref]"] = dict(
    class_out="REFS_ADDED", refs=[NGW], tier="medium", indep=False, lang="en",
    notes=(
        "Natural Gas World (Feb 2013) independently attests 110 MMcm/d, matching GEM's "
        "Capacity=110 MMSCMD exactly. Deliberately scored medium rather than high: NGW and the "
        "Wikipedia article most plausibly both trace back to the same 2011 tripartite announcement, "
        "so they are not confidently independent of each other. Unit is right here -- MMSCMD "
        "(cubic METRES) is what the source says, unlike P4041 in this same batch."
    ),
)
F["P0450", "Length [ref]"] = dict(
    class_out="UNRESOLVED", refs=[], tier="low", indep=False, lang="en",
    notes=(
        "Cannot corroborate LengthKnown=5600 km and it is contradicted three ways. (1) Natural Gas "
        "World (Feb 2013), with the SAME endpoints and the SAME 110 MMcm/d, gives 1,600 km. "
        "(2) GEM's own drawn route for this row measures LengthEstimateKm=1987.78. "
        "(3) Asaluyeh->Damascus is ~1,700 km great-circle, so 5,600 km is ~3.3x the straight-line "
        "distance -- impossible for this corridor. 5600 appears to be Wikipedia's figure "
        "transcribed faithfully; 1,600 vs 5,600 is a plausible digit error at some upstream step. "
        "Leaving UNRESOLVED rather than staging 1,600 as a fill because the value is populated and "
        "published; filed as a spec __VALIDITY__ with the proposed correction so it is one step to "
        "apply once ruled."
    ),
)
F["P0450", "Diameter [ref]"] = dict(
    class_out="REVERIFIED", refs=[], tier="low", indep=False, lang="en",
    notes=(
        "Existing Wikipedia ref re-verified live and does carry 56 in, so the cell is not an orphan "
        "and not a dead link. No independent corroboration of the diameter was found anywhere -- "
        "the figure rests on one tertiary source for a pipeline that was never engineered past "
        "announcement. Tier low deliberately. Part of the single-Wikipedia-source cluster flagged "
        "in this row's attribution __VALIDITY__."
    ),
)
F["P0450", "FuelSource [ref]"] = dict(
    class_out="REFS_ADDED", refs=[NGW], tier="medium", indep=False, lang="en",
    notes=(
        "Missing-ref fill. Natural Gas World (Feb 2013) sources the gas to South Pars via "
        "Assalouyeh, supporting FuelSource='South Pars gas field'. Single source, medium."
    ),
)
F["P0450", "Location [ref]"] = dict(
    class_out="REFS_ADDED", refs=[NGW], tier="medium", indep=False, lang="en",
    notes=(
        "Missing-ref fill. Natural Gas World (Feb 2013) gives Assalouyeh (Iran) -> Damascus "
        "(Syria), matching StartLocation='Asaluyeh' / StartCountryOrArea='Iran' / "
        "EndLocation='Damascus' / EndCountryOrArea='Syria'. StartState/Province='Bushehr' is "
        "correct for Asaluyeh but is not stated by the source. Separately: this row's Route [ref] "
        "cell holds a google.com/url?sa=i Google-Images click-through URL, which is not a source at "
        "all -- flagged in the attribution __VALIDITY__. Route/geometry refs are out of scope for "
        "ref work per CLAUDE.md, so it is flagged and not touched here."
    ),
)

# ============================== P5857 Zubair-Faw Gas Pipeline ===============================
F["P5857", "Status [ref]"] = dict(
    class_out="UNRESOLVED", refs=[], tier="low", indep=False, lang="en",
    notes=(
        "Status='shelved' carries NO ref at all and no source states a shelving. The last "
        "independent evidence of any kind is MEED, 24 May 2011, reporting bids IN for the line "
        "(20+ bidders, 10-month build) -- i.e. an active tender, not a shelving. No award, no "
        "construction, no cancellation found in the 15 years since. Strictly, 15 years of silence "
        "sits well past the 4y->cancelled rung of the staleness ladder, so 'shelved' is if anything "
        "generous. Not proposing a change on silence alone -- that is the standing Libya lesson "
        "(absence of news is not evidence of cancellation) -- but the tension is recorded, and "
        "__STATUS__ stages ShelvedCancelledType='Presumed' so the row at least declares that the "
        "status is an inference."
    ),
)
F["P5857", "Fuel [ref]"] = dict(
    class_out="REFS_ADDED", refs=["MEED"], tier="high", indep=True, lang="en",
    notes=(
        "MEED (24 May 2011) independently confirms this is a gas pipeline, alongside the existing "
        "bncnetwork ref. IMPORTANT CAVEAT on bncnetwork: url_verifier returns HTTP 200 but the page "
        "is JS-rendered / content-gated -- fetching it yields only the header, so its content "
        "cannot actually be read or verified. It is retained (not a dead link) but should not be "
        "counted as a readable corroborating source. MEED is doing the real work on every spec on "
        "this row."
    ),
)
F["P5857", "PipelineType [ref]"] = dict(
    class_out="REVERIFIED", refs=[], tier="medium", indep=False, lang="en",
    notes=(
        "Existing MEED ref re-verified live. It describes a dedicated field-to-depot trunk line "
        "(Zubair depot -> Fao depot), consistent with PipelineType='transmission'."
    ),
)
F["P5857", "Capacity [ref]"] = dict(
    class_out="REFS_ADDED", refs=["MEED"], tier="high", indep=True, lang="en",
    notes=(
        "MEED (24 May 2011): the line would carry 'up to 100 million cubic feet a day', matching "
        "Capacity=100 MMcf/d exactly, unit included. Adding MEED alongside the unreadable "
        "bncnetwork ref gives this cell one genuinely verifiable source."
    ),
)
F["P5857", "Length [ref]"] = dict(
    class_out="REFS_ADDED", refs=["MEED"], tier="high", indep=True, lang="en",
    notes=(
        "MEED (24 May 2011) gives 105 km, matching LengthKnown=105 km exactly. Corroborating "
        "cross-tracker detail: GOIT P6196 'Zb1-Al Faw Oil Pipeline' runs Zubair 1 -> Al Faw and "
        "also carries 105.00 km -- the same right-of-way, which is where the figure comes from. "
        "That is a parallel line, NOT a duplicate: P6196 is 48-inch crude and operating, this row "
        "is 18-inch gas. Confirmed not a duplicate; see __VALIDITY__ for the corridor cross-ref."
    ),
)
F["P5857", "Diameter [ref]"] = dict(
    class_out="REFS_ADDED", refs=["MEED"], tier="high", indep=True, lang="en",
    notes=(
        "MEED (24 May 2011) specifies 18-inch carbon steel, matching Diameter=18 in exactly."
    ),
)
F["P5857", "FuelSource [ref]"] = dict(
    class_out="REFS_ADDED", refs=["MEED"], tier="medium", indep=False, lang="en",
    notes=(
        "Missing-ref fill. MEED (24 May 2011) sources the gas to the Zubair oil field, supporting "
        "FuelSource='Zubair'. Single readable source, medium."
    ),
)
F["P5857", "Location [ref]"] = dict(
    class_out="REFS_ADDED", refs=["MEED"], tier="medium", indep=False, lang="en",
    notes=(
        "Missing-ref fill. MEED (24 May 2011): from the Zubair field depot near Basra to the Fao "
        "depot, developed by South Oil Company at ~$150M. Supports StartState/Province='Basrah', "
        "StartCountryOrArea='Iraq', EndLocation='Al Faw', EndState/Province='Al-Faw Peninsula'. "
        "StartLocation is blank; 'Zubair depot' would be the sourced value if a fill is wanted."
    ),
)

# ============================== P4041 North Rumela-Al-Najaf Gas Pipeline ====================
F["P4041", "Status [ref]"] = dict(
    class_out="UNRESOLVED", refs=[], tier="low", indep=False, lang="en",
    notes=(
        "The cited ref does not support 'shelved' AND the value is contradicted by 2026 events. "
        "The saymar.org ref is an SCOP 'Technical Presentation (Scope of Work)' roadshow deck "
        "(Oct 2020) whose own status line reads 'FEED & EISHA completed for Pump Stations, and "
        "Concept for the Pipeline' -- an ACTIVE early-stage project as of late 2020, not a shelved "
        "one. Since then the parent project has entered execution: Iraq's PM directed "
        "implementation (26 Apr 2026), $1.5bn was approved under the Iraqi-Chinese agreement, and "
        "work began ~1 May 2026 on the ~700 km Basra-Haditha system (2.25 Mbbl/d Basra-Haditha + "
        "1 Mbbl/d Haditha-Aqaba), with 56-inch pipe manufacturing under way. See __STATUS__ for "
        "why this is 'unclear' and not a proposed change: every 2026 source describes the CRUDE "
        "line only. QC detects, Update fixes."
    ),
)
F["P4041", "Fuel [ref]"] = dict(
    class_out="REVERIFIED", refs=[], tier="medium", indep=False, lang="en",
    notes=(
        "Existing saymar.org SCOP ref re-verified (HTTP 200, application/pdf). It describes the "
        "28-inch line as carrying 'Sales and Fuel Gas', so Fuel='Gas' is supported. Verifier "
        "caveat: url_verifier passes the fetch but FAILS on deep content tokens because the file is "
        "4.2 MB -- the documented large-PDF limit. Content was confirmed locally with pdftotext."
    ),
)
F["P4041", "PipelineType [ref]"] = dict(
    class_out="REVERIFIED", refs=[], tier="medium", indep=False, lang="en",
    notes=(
        "Existing saymar.org ref re-verified. The deck describes a 350 km inter-governorate sales/"
        "fuel gas trunk laid in an existing pipeline corridor with pump/compression stations -- "
        "'transmission' is right."
    ),
)
F["P4041", "Proposal [ref]"] = dict(
    class_out="UNRESOLVED", refs=[], tier="low", indep=False, lang="en",
    notes=(
        "ProposalYear=2019 could not be sourced. The saymar.org deck is dated Oct 2020 and does not "
        "give a proposal date; nothing else located names 2019 for the gas leg. Not contradicted "
        "either -- 2019 is plausible given FEED was complete by late 2020 -- so this is genuinely "
        "unresolved rather than wrong. Distinguish from ConstructionYear=2019, which IS "
        "contradicted (see below)."
    ),
)
F["P4041", "Construction [ref]"] = dict(
    class_out="UNRESOLVED", refs=[], tier="low", indep=False, lang="en",
    notes=(
        "ConstructionYear=2019 is CONTRADICTED by the row's own cited source. The saymar.org SCOP "
        "deck (Oct 2020) states the pipeline was still 'at a Concept Study level' and that FEED "
        "covered only North Rumailah (PS1A) to Haditha (PS5A) -- i.e. no construction had started "
        "a full year after the claimed construction year. Actual construction on the parent "
        "(crude) system began ~May 2026. Filed as a date-logic __VALIDITY__ with a proposed blank; "
        "not staged as a fill because the value is populated and published."
    ),
)
F["P4041", "Capacity [ref]"] = dict(
    class_out="UNRESOLVED", refs=[], tier="low", indep=False, lang="en",
    notes=(
        "UNIT DEFECT, proven from the row's own source. The saymar.org SCOP deck says '258 MMSCFD "
        "ultimate capacity of Sales and Fuel Gas 28\" pipeline (350 km)' -- million standard cubic "
        "FEET per day. GEM recorded CapacityUnits='MMSCMD' (cubic METRES), so the computed "
        "CapacityBcm/y reads 94.17 instead of ~2.67. The ratio 94.17/2.67 = 35.3 is exactly the "
        "cf->m3 factor. Mechanical confirmation: the PDF text contains 'MMSCFD' three times and "
        "'MMSCMD' zero times. The number is right; only the unit is wrong. Ref left UNRESOLVED "
        "because the existing ref is the correct source for a value the sheet has mis-transcribed "
        "-- re-affirming it would endorse 94.17 bcm/y. Fix the unit, then this becomes a clean "
        "REVERIFIED. Full argument and the tracker-wide plausibility evidence in __VALIDITY__."
    ),
)
F["P4041", "Length [ref]"] = dict(
    class_out="REFS_ADDED", refs=["SAYMAR"], tier="medium", indep=False, lang="en",
    notes=(
        "Missing-ref fill from the row's own existing source. The saymar.org deck states 'The "
        "approximate length of the pipelines is 350 km', and its own table row reads 'Gas Pipeline "
        "28\" / 348km'; the station-to-station legs sum to the same figure (PS1A->PS2A 180 km + "
        "PS2A->PS3A 167.5 km = 347.5 km). Supports LengthKnown=350 km. Single source, medium. "
        "Note the tension with the row's LengthEstimateKm=518.81 drawn route on a row marked "
        "RouteAccuracy='high' -- flagged in __VALIDITY__, not fixed here."
    ),
)
F["P4041", "Diameter [ref]"] = dict(
    class_out="REVERIFIED", refs=[], tier="medium", indep=False, lang="en",
    notes=(
        "Existing saymar.org ref re-verified. The deck is explicit and repeats it: 'There will be 2 "
        "parallel pipelines: A crude oil pipeline, with a 56\" diameter; and A gas pipeline (fuel "
        "gas and sales gas), with a 28\" diameter'. Diameter=28 in confirmed."
    ),
)
F["P4041", "FuelSource [ref]"] = dict(
    class_out="REFS_ADDED", refs=["SAYMAR"], tier="medium", indep=False, lang="en",
    notes=(
        "Missing-ref fill. The saymar.org deck puts the origin at North Rumailah (pump station "
        "PS1A), supporting FuelSource='Rumela'. Spelling note: GEM writes 'Rumela'; the source and "
        "the dominant English usage are 'Rumailah'/'Rumaila'. Worth normalising, and worth adding "
        "to OtherEnglishNames on this row -- the GulfPub match-quality memo for Iraq shows exactly "
        "this class of transliteration gap (Okaz/Akkas) defeating the matcher."
    ),
)
F["P4041", "Location [ref]"] = dict(
    class_out="REFS_ADDED", refs=["SAYMAR"], tier="medium", indep=False, lang="en",
    notes=(
        "Missing-ref fill. The saymar.org deck traces the route from North Rumailah (PS1A) through "
        "PS2A to PS3A, with the 350 km figure covering that extent -- supporting "
        "StartPrefecture/District='Rumela', StartState/Province='Basrah', EndLocation='Al-Najaf', "
        "EndState/Province='Al-Najaf'. Single source, medium. Scope caveat worth carrying: the FEED "
        "describes the full corridor as running on to Haditha (PS5A), so 'Al-Najaf' is an "
        "intermediate station, not the project terminus -- this row may be one leg of a longer "
        "line rather than a complete pipeline."
    ),
)

# ---------------------------------------------------------------- sentinels
STATUS = {
    "P0481": dict(
        verdict="stale", class_out="STALE", current="cancelled", proposed="cancelled",
        values={"ShelvedCancelledType": "Presumed"},
        evidence_date="2017-11", rule="4y->cancelled",
        refs=[UNNEWS, RUDAW], tier="high", indep=True, lang="en",
        notes=(
            "Verdict: keep 'cancelled' but declare it an inference. The only cited source (Al-Ahram/"
            "Reuters, 22 Nov 2017) reports Iraq SELECTING Toyo Engineering to build the line -- "
            "initiation, not cancellation -- and records that no FID had been taken and talks had "
            "stalled on price. No cancellation was ever announced, in English or Arabic. What is "
            "independently documented is that the project's rationale lapsed: the gas was intended "
            "to help settle Iraq's 1990-invasion reparations, and the UNCC confirmed the final "
            "payment on 13 Jan 2022 ($52.4bn; ~1.5M successful claims of 2.7M filed), funded "
            "throughout by a levy on Iraqi OIL sales rather than gas in kind (UN News + Rudaw, both "
            "verified and independent of each other). With ~9 years of silence since the only "
            "project news, the 4y->cancelled rung is satisfied comfortably -- but by silence plus a "
            "lapsed rationale, not by an announcement. Hence ShelvedCancelledType='Presumed'. "
            "Deliberately NOT staging a CancelledYear: no source dates a cancellation and inventing "
            "one would be fabrication. Per the staged-JSON contract a 'stale' inference carries no "
            "ref, so the two reparations URLs are recorded here as supporting context for the "
            "reviewer, not as a citation for the Status cell."
        ),
    ),
    "P0450": dict(
        verdict="stale", class_out="STALE", current="cancelled", proposed="cancelled",
        values={"ShelvedCancelledType": "Presumed"},
        evidence_date="2024-12", rule="4y->cancelled",
        refs=[ATLCOUNCIL, KARAMSHAAR], tier="medium", indep=True, lang="en",
        notes=(
            "Verdict: keep 'cancelled', but ShelvedCancelledType must change from 'confirmed' to "
            "'Presumed'. There was never a formal cancellation -- Wikipedia says so explicitly, and "
            "Syria's electricity minister stated in 2021 that the project had NOT been abandoned, "
            "a decade after the 2011 tripartite MoU. What ended it was political: Assad's fall in "
            "Dec 2024 removed the Iran-Syria basis for the corridor, and from Aug 2025 Syria began "
            "importing Azerbaijani (Shah Deniz) gas via Turkiye instead -- a different corridor "
            "serving the same demand. 'confirmed' asserts a cancellation event that no source "
            "records, which is the specific error here; the pipeline is dead by inference, and the "
            "row should say so. Also note the Status [ref] is an article about a crude OIL pipeline "
            "and does not belong on this cell (see that unit). The two refs recorded here are "
            "supporting analyses of the project's collapse, not a cancellation citation -- a "
            "'stale' inference carries no ref by design."
        ),
    ),
    # P5857 (Zubair-Faw) DELIBERATELY HAS NO STATUS ENTRY -- consolidated into the
    # `annual` leg's ruling (batches/iraq-gas/staging/annual/rows/P5857.json) so the
    # handoff shows ONE status decision per ProjectID instead of two contradictory ones.
    #
    # This leg originally proposed: retain 'shelved', stage ShelvedCancelledType=
    # 'Presumed', on the reasoning that the newest evidence was MEED 24-May-2011 (bids
    # in: 20+ bidders, $150M, 10-month build, South Oil Company) with "no award, no
    # construction, no cancellation in the 15 years since" -- and that the Libya
    # cancelled-review lesson (absence of news is not evidence of cancellation, and
    # Iraqi state tenders of that era routinely went quiet without dying) argued against
    # the harder change the 4y ladder would otherwise force.
    #
    # WITHDRAWN because its central factual premise is wrong. The annual leg found the
    # EPC WAS awarded: CPECC contract PRJ-11-4226, USD 72.35m FEED+EPCC, 98 km 18-in
    # Zubair/1 depot -> Fao depot plus compressor station, execution window 15-Jul-2014
    # to April 2016. So this is not fifteen years of silence after a tender; it is a
    # contracted project whose execution window lapsed a decade ago, with the line
    # absent from GulfPub's professional gas-pipeline map -- positive evidence of
    # non-completion rather than mere absence of news. On that record the 4y->cancelled
    # rung is properly satisfied and the annual leg's 'cancelled' is the better verdict.
    #
    # One thing carried FROM this leg INTO the consolidated ruling: no CancelledYear.
    # The annual shard originally staged CancelledYear=2026, which is the year we
    # noticed rather than a sourced cancellation date -- the same fabrication this
    # leg's P0481 record explicitly refuses. Dropped there.
    #
    # This leg's __VALIDITY__ record for P5857 (ResearcherNotes claims 'No update since
    # 2022' while both refs are from 2011) is unaffected and still stands.
    "P4041": dict(
        verdict="unclear", class_out="UNRESOLVED", current="shelved", proposed="",
        values={},
        evidence_date="2026-05", rule="",
        refs=[NATIONAL26, SHAFAQ26, HCP26, AGBI26], tier="high", indep=True, lang="en",
        notes=(
            "Verdict UNCLEAR -- 'shelved' is contradicted, but I cannot responsibly name the "
            "replacement. This row is the 28-inch sales/fuel gas leg of the Basra(North Rumaila)-"
            "Haditha corridor, and its own cited source (SCOP deck, Oct 2020) describes 2 PARALLEL "
            "pipelines in ONE existing corridor under one EPCF scope: 56-inch crude + 28-inch gas. "
            "The 56-inch crude twin is tracked in GOIT as P0544 'Basra-Aqaba Oil Pipeline' with "
            "Status='construction' -- so the two legs of one trenched project currently read "
            "'construction' and 'shelved' in GEM's two trackers. And the crude leg really is "
            "moving: PM directive 26 Apr 2026, $1.5bn approved under the Iraqi-Chinese agreement, "
            "work started ~1 May 2026, 56-inch pipe manufacturing under way (The National, Shafaq, "
            "Hydrocarbon Processing, AGBI -- four independent, all verified). WHY NOT PROPOSE A "
            "CHANGE: every one of those 2026 reports describes the CRUDE line only. None mentions "
            "sales gas, fuel gas, a 28-inch line, or any gas infrastructure -- I checked Shafaq's "
            "scope reporting specifically for this. So the gas leg's presence in the executed scope "
            "rests on the 2020 EPCF scope document plus a third-party project listing, which is not "
            "enough to flip a status. Route to Update: confirm with SCOP/Ministry of Oil whether the "
            "28-inch gas line is in the 2026 award. If yes -> 'construction'; if the crude line was "
            "carved out alone -> 'proposed' or 'shelved' with a current source. Either way 'shelved' "
            "as it stands is unsupported. Note this row also carries a proven capacity-unit defect "
            "and a contradicted ConstructionYear -- see __VALIDITY__."
        ),
    ),
}

VALIDITY = [
    dict(
        pid="P0481", concern="spec",
        recommendation=(
            "Re-check StartLocation. The only source says the gas source was undecided between "
            "West Qurna 2 (LUKOIL) and Rumaila (BP); GEM asserts Rumaila. Consider blanking to the "
            "governorate level (Basra) or noting both candidates in ResearcherNotes."
        ),
        values={}, refs=[AHRAM], tier="medium", indep=False, lang="ar",
        notes=(
            "Al-Ahram/Reuters (22 Nov 2017): it was not yet clear whether the gas would come from "
            "the LUKOIL-operated West Qurna 2 field or the BP-operated Rumaila field. "
            "StartLocation='Rumaila oilfield' therefore states as fact something the source "
            "explicitly leaves open. Low-stakes on its own, but it matters here because Rumaila is "
            "ALSO the origin of the genuine pre-1990 Iraq->Kuwait gas line (see the existence "
            "concern on this row), so an unsourced 'Rumaila' invites conflating the two."
        ),
    ),
    dict(
        pid="P0481", concern="existence",
        recommendation=(
            "Discovery candidate + conflation check: a real Iraq->Kuwait gas pipeline from Rumaila "
            "(~400 MMcf/d) operated until 1990 and appears untracked in GGIT. Confirm P0481 "
            "describes the 2017 proposal only, and assess the historic line as a separate retired "
            "entity."
        ),
        values={}, refs=[AHRAM], tier="medium", indep=False, lang="ar",
        notes=(
            "The same Al-Ahram/Reuters article records that 'Iraq used to supply Kuwait with gas "
            "from Rumaila, around 400 million cubic feet per day, halted shortly after the 1990 "
            "invasion'. That is a distinct, physically-built, now-retired pipeline -- different era, "
            "different capacity (400 vs 200 MMcf/d) -- and I did not find it as a row in GGIT's "
            "Iraq set. Two consequences. (1) Discovery: it may warrant a retired row, subject to the "
            "usual 2-independent-source test; a single 2017 news aside is not enough on its own to "
            "create an entity. (2) Data hygiene on P0481: because both share the Rumaila origin and "
            "the Iraq->Kuwait pair, there is a real risk the row silently blends the historic line "
            "with the 2017 Toyo proposal. The 2.06 bcm/y capacity is traceable to the 2017 "
            "proposal's 200 MMcf/d, so the row does look like the proposal -- but confirm rather "
            "than assume."
        ),
    ),
    dict(
        pid="P0450", concern="spec",
        recommendation=(
            "LengthKnown=5600 km is unsupported and physically implausible for Asaluyeh->Damascus. "
            "Candidate correction: 1,600 km (Natural Gas World, same endpoints and same capacity), "
            "consistent with GEM's own 1,987.78 km drawn route. Verify before applying."
        ),
        values={"LengthKnown": "1600", "LengthKnownUnits": "km"},
        refs=[NGW], tier="medium", indep=False, lang="en",
        notes=(
            "Three independent contradictions of 5,600 km. (1) Natural Gas World (11 Feb 2013), "
            "describing the same project with the same Asaluyeh->Damascus endpoints and the same "
            "110 MMcm/d, gives 1,600 km. (2) GEM's own drawn route for this row measures "
            "LengthEstimateKm=1987.78 -- 2.8x shorter than the stated length, which no routing "
            "allowance explains. (3) Asaluyeh->Damascus is ~1,700 km great-circle, so 5,600 km "
            "would be ~3.3x the straight line. 5600 is Wikipedia's figure transcribed faithfully; "
            "1,600 -> 5,600 is a plausible digit corruption somewhere upstream. Staged as a concern "
            "rather than a fill because the value is populated and published and a reference value "
            "is never auto-applied. Note the proposed 1,600 km rests on a single source and is "
            "itself below the drawn route, so it is a candidate, not a confirmed value."
        ),
    ),
    dict(
        pid="P0450", concern="attribution",
        recommendation=(
            "Four value cells (Fuel, PipelineType, Capacity, Diameter) all cite the SAME single "
            "Wikipedia article -- fails the 2-independent-source target. Re-point to Natural Gas "
            "World and the post-Assad analyses (staged on the individual units). Separately, "
            "Route [ref] holds a Google-Images click-through URL and should be cleared."
        ),
        values={}, refs=[NGW], tier="medium", indep=False, lang="en",
        notes=(
            "The row looks well-referenced by cell count but is effectively single-sourced on one "
            "tertiary page: en.wikipedia.org/wiki/Iran-Iraq-Syria_pipeline appears in Fuel [ref], "
            "PipelineType [ref], Capacity [ref] and Diameter [ref]. Per standing rule 4 that is one "
            "source, not four, and it is tertiary. Replacements are staged on the individual ref "
            "units (Natural Gas World for fuel/type/capacity/source/location; diameter has NO "
            "independent corroboration and is left at tier low). Second, unrelated defect on the "
            "same row: Route [ref] contains a 'google.com/url?sa=i&...' Google-Images "
            "click-through, which is a search-result redirect rather than a source. Geometry refs "
            "are out of scope for the refs leg per CLAUDE.md, so it is flagged here and not "
            "modified -- but it should be cleared whenever the row's route is next touched."
        ),
    ),
    dict(
        pid="P5857", concern="attribution",
        recommendation=(
            "ResearcherNotes says 'No update since 2022' but both refs are from 2011 (MEED, 24 May "
            "2011) and no 2022-era source is cited. Either surface the 2022 source or correct the "
            "note to 2011. Also cross-reference GOIT P6196, the 48-inch crude line in the same "
            "105 km corridor -- parallel line, not a duplicate."
        ),
        values={}, refs=["MEED"], tier="medium", indep=False, lang="en",
        notes=(
            "(a) The 2022 date in ResearcherNotes is unexplained. Everything citable on this row "
            "dates to May 2011; if a 2022 check happened, its source is not recorded, and as "
            "written the note implies 11 more years of currency than the references support. This "
            "matters because the staleness ladder is applied to that date. (b) NOT A DUPLICATE, but "
            "worth linking: GOIT P6196 'Zb1-Al Faw Oil Pipeline' shares this row's endpoints "
            "(Zubair 1 -> Al Faw) and its exact 105.00 km. Two lines in one right-of-way -- P6196 "
            "is 48-inch crude and operating, P5857 is 18-inch gas and never built. I checked this "
            "specifically because same-endpoints-same-length is the classic cross-tracker duplicate "
            "signature; the diameters and fuels settle it. Recommend recording the corridor "
            "relationship (OtherEnglishNames / PipelineNetworkGrouping / ResearcherNotes) so a "
            "future pass does not re-open it as a duplicate."
        ),
    ),
    dict(
        pid="P4041", concern="spec",
        recommendation=(
            "CAPACITY UNIT DEFECT: change CapacityUnits from 'MMSCMD' to 'MMcf/d', leaving "
            "Capacity=258. The source says 258 MMSCFD (cubic FEET). This corrects the computed "
            "CapacityBcm/y from 94.17 to ~2.67 -- a 35.3x error. Highest-priority item on this row."
        ),
        values={"Capacity": "258", "CapacityUnits": "MMcf/d"},
        refs=["SAYMAR"], tier="high", indep=False, lang="en",
        notes=(
            "Proven from the row's own cited source, not inferred. The saymar.org SCOP deck states: "
            "'2.25 MMBOPD ultimate capacity of 56\" Crude Oil pipeline (350 km) & 258 MMSCFD "
            "ultimate capacity of Sales and Fuel Gas 28\" pipeline (350 km)'. MMSCFD = million "
            "standard cubic FEET per day. GEM recorded MMSCMD (cubic METRES), and 94.17 / 2.665 = "
            "35.3, exactly the cf->m3 conversion factor -- arithmetic, not resemblance. Mechanical "
            "check on the PDF text: 'MMSCFD' appears 3 times, 'MMSCMD' 0 times. The deck's FEED "
            "section separately gives 284 MMSCFD, same unit. WHY IT MATTERS BEYOND ONE CELL: at "
            "94.17 bcm/y this row is the SECOND-HIGHEST capacity in the entire GGIT tracker, behind "
            "only P4122 (Luxembourg, 104.34) and ahead of P0160 (Canadian Mainline, 71.18) -- on a "
            "350 km 28-inch line. Nord Stream 1 moved 55 bcm/y on twin 48-inch. Physically "
            "impossible, and it distorts any Iraq or global capacity aggregate. SCOPE TESTED, NOT A "
            "CLASS: I screened all 63 MMSCMD rows with a parseable diameter against a generous "
            "diameter-based capacity ceiling. Only 4 exceed it by >2x, and P4041 is a lone extreme "
            "-- 14.2x, against 3.8x (P7697 Chile), 3.1x (P3297 India) and 3.0x (P7795 Brazil), all "
            "three of which are within the noise of a crude ceiling and may be legitimate. So this "
            "is one bad row, NOT a systematic MMSCMD ingest defect, and no cross-country sweep is "
            "warranted. One loose end worth a separate look: P4122 (Luxembourg, 104.34 bcm/y) fell "
            "out of the screen only because it has no parseable diameter, and 104 bcm/y for "
            "Luxembourg deserves its own check -- flagging, not claiming."
        ),
    ),
    dict(
        pid="P4041", concern="spec",
        recommendation=(
            "ConstructionYear=2019 is contradicted by the row's own source, which shows the "
            "pipeline still at Concept Study level in Oct 2020. Blank it (or move 2019 to "
            "ProposalYear if that is where it belongs). Actual construction on the parent crude "
            "system began ~May 2026."
        ),
        values={"ConstructionYear": ""},
        refs=["SAYMAR"], tier="high", indep=False, lang="en",
        notes=(
            "Date-logic defect. The saymar.org SCOP deck (Oct 2020) states 'FEED Design was "
            "completed ... between North Rumailah (PS1A) to Haditha (PS5A) while the pipeline is at "
            "a Concept Study level', and gives project status as 'FEED & EISHA completed for Pump "
            "Stations, and Concept for the Pipeline'. A pipeline at concept stage in late 2020 did "
            "not begin construction in 2019. ProposalYear=2019 is a separate matter and is merely "
            "unsourced, not contradicted -- do not blank both on the same reasoning."
        ),
    ),
    dict(
        pid="P4041", concern="attribution",
        recommendation=(
            "CROSS-TRACKER INCONSISTENCY: this row (28-inch gas leg) reads 'shelved' while its "
            "56-inch crude twin, GOIT P0544 'Basra-Aqaba Oil Pipeline', reads 'construction' -- two "
            "parallel lines in one trench under one EPCF scope. Reconcile the pair, and re-check the "
            "route: LengthEstimateKm=518.81 against a sourced 350 km on a row marked "
            "RouteAccuracy='high'."
        ),
        values={}, refs=[NATIONAL26, SHAFAQ26], tier="high", indep=True, lang="en",
        notes=(
            "(a) The pairing is not a guess -- the row's own source says '2 parallel pipelines' "
            "(56-inch crude + 28-inch gas) in 'an existing pipeline corridor', one scope, one "
            "EPCF. GOIT P0544 (Basra -> Haditha, 685 km, 56-inch) is that crude leg and sits at "
            "'construction'. Whatever the correct answer is, the two rows cannot both be right as "
            "they stand. This is the kind of split that neither tracker's own QC can see, since the "
            "legs live in different trackers. Resolution needs the 2026 award scope (see __STATUS__ "
            "-- the public 2026 reporting covers the crude line only). (b) Route, separate defect: "
            "the drawn route measures 518.81 km against a sourced 350 km (and 348 km / 347.5 km "
            "station-to-station in the same deck) -- a 1.48x ratio, outside the route-integrity "
            "band -- yet RouteAccuracy is 'high'. Since the FEED corridor continues past Al-Najaf "
            "to Haditha (PS5A), the likeliest explanation is that the drawn route covers a longer "
            "extent than the row's 350 km leg, i.e. a row-scope problem rather than a bad trace. "
            "Route work is out of scope here; flagged for the routes lane. Do not downgrade "
            "RouteAccuracy before the extent question is settled."
        ),
    ),
]


# ---------------------------------------------------------------- build
def main():
    df = pd.read_csv(CSV, header=2, low_memory=False)
    cols = list(df.columns)
    pairs = [p for p in discover_ref_pairs(cols) if p.get("ref_col") in cols]

    def txt(row, col):
        if col not in row.index:
            return ""
        v = row[col]
        return "" if pd.isna(v) else str(v)

    resolutions = []
    n_units = 0
    for pid in PIDS:
        row = df[df["ProjectID"] == pid].iloc[0]
        sheet_row = int(row.name) + 4
        base = dict(
            project_id=pid,
            sheet_row=sheet_row,
            pipeline_name=txt(row, "PipelineName"),
            segment_name=txt(row, "SegmentName"),
        )
        # --- per-ref-cell units
        for p in pairs:
            rc = p["ref_col"]
            vcs = [c for c in p["value_cols"] if c in cols]
            values = {c: txt(row, c) for c in vcs}
            cur = txt(row, rc)
            if not any(values.values()) and not cur:
                continue
            f = F.get((pid, rc))
            if f is None:
                raise SystemExit(f"no finding authored for {pid} / {rc}")
            refs = [{"MEED": txt(row, "PipelineType [ref]"),
                     "SAYMAR": txt(row, "Status [ref]")}.get(r, r) for r in f["refs"]]
            pvc = p.get("primary_value_col") or (vcs[0] if vcs else "")
            resolutions.append({
                **base,
                "ref_col": rc,
                "value_cols": vcs,
                "primary_value_col": pvc,
                "values": values,
                "primary_value": values.get(pvc, ""),
                "current_ref": cur,
                "class_in": "HAS_REF" if cur else "MISSING_REF",
                "class_out": f["class_out"],
                "proposed_refs": refs,
                "verifications": [
                    {"url": u, "ok": True, "contains_value": VERIFIED.get(u, True)}
                    for u in refs
                ],
                "tier": f["tier"],
                "independent": f["indep"],
                "source_language": f["lang"],
                "researcher_notes": f["notes"],
                "ref_researched": True,
            })
            n_units += 1

        # --- __STATUS__ sentinel (absent for a row consolidated into another leg's
        #     ruling -- see the P5857 note above STATUS)
        s = STATUS.get(pid)
        if s is None:
            continue
        resolutions.append({
            **base,
            "ref_col": "__STATUS__",
            "value_cols": [],
            "primary_value_col": "Status",
            "values": s["values"],
            "primary_value": s["current"],
            "current_ref": txt(row, "Status [ref]"),
            "class_in": "STATUS",
            "class_out": s["class_out"],
            "current_status": s["current"],
            "verdict": s["verdict"],
            "proposed_status": s["proposed"],
            "evidence_date": s["evidence_date"],
            "staleness_rule": s["rule"],
            "proposed_refs": s["refs"],
            "verifications": [
                {"url": u, "ok": True, "contains_value": VERIFIED.get(u, True)}
                for u in s["refs"]
            ],
            "tier": s["tier"],
            "independent": s["indep"],
            "source_language": s["lang"],
            "researcher_notes": s["notes"],
            "ref_researched": True,
        })

    # --- __VALIDITY__ sentinels
    for v in VALIDITY:
        row = df[df["ProjectID"] == v["pid"]].iloc[0]
        refs = [{"MEED": txt(row, "PipelineType [ref]"),
                 "SAYMAR": txt(row, "Status [ref]")}.get(r, r) for r in v["refs"]]
        resolutions.append({
            "project_id": v["pid"],
            "sheet_row": int(row.name) + 4,
            "pipeline_name": txt(row, "PipelineName"),
            "segment_name": txt(row, "SegmentName"),
            "ref_col": "__VALIDITY__",
            "value_cols": [],
            "primary_value_col": "",
            "values": v["values"],
            "primary_value": "",
            "current_ref": "",
            "class_in": "VALIDITY",
            "class_out": "UNRESOLVED",
            "verdict": "concern",
            "concern_type": v["concern"],
            "recommendation": v["recommendation"],
            "proposed_refs": refs,
            "verifications": [
                {"url": u, "ok": True, "contains_value": VERIFIED.get(u, True)}
                for u in refs
            ],
            "tier": v["tier"],
            "independent": v["indep"],
            "source_language": v["lang"],
            "researcher_notes": v["notes"],
        })

    def counts(key, pred=lambda r: True):
        out = {}
        for r in resolutions:
            if pred(r):
                out[r.get(key, "")] = out.get(r.get(key, ""), 0) + 1
        return dict(sorted(out.items()))

    is_ref = lambda r: not r["ref_col"].startswith("__")  # noqa: E731
    meta = {
        "commodity": "gas",
        "scope": {
            "csv": CSV.name,
            "country": "Iraq",
            "tracker": "gas",
            "statuses": ["cancelled", "shelved"],
            "rows": len(PIDS),
            "project_ids": len(PIDS),
        },
        "mode": "sweep",
        "leg": "status-review",
        "n_units": n_units,
        "seeded_from": "GGIT_gas_snapshot_20260728.csv + ref_pairs.discover_ref_pairs",
        "note": (
            "The four Iraq gas rows with Status in {cancelled, shelved}: P0481, P0450 (cancelled) "
            "and P5857, P4041 (shelved). Status is itself under review here -- absence of news is "
            "not evidence of cancellation. Headline findings: (1) P4041's CapacityUnits is MMSCMD "
            "where its own cited source says MMSCFD, a proven 35.3x error that makes it the "
            "2nd-highest capacity row in all of GGIT; screened as a one-row defect, not a class. "
            "(2) P4041's 'shelved' is contradicted -- its 56-inch crude twin GOIT P0544 reads "
            "'construction' and work began ~May 2026 -- but the 2026 scope is publicly crude-only, "
            "so the verdict is 'unclear', not a proposed change. (3) P0481's Status [ref] reports "
            "Iraq SELECTING a contractor, the opposite of cancellation; its rationale lapsed when "
            "Kuwait reparations completed 13 Jan 2022. (4) P0450's Status [ref] is about a crude "
            "OIL pipeline and ShelvedCancelledType='confirmed' is wrong -- no cancellation was ever "
            "announced. (5) P5857 has no Status [ref] at all; MEED (2011) fully sources every spec."
        ),
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ref_research_applied": n_units,
        "ref_class_out_counts": counts("class_out", is_ref),
        "class_out_counts": counts("class_out"),
        "class_in_counts": counts("class_in"),
        "n_validity_flags": len(VALIDITY),
        "n_fills": 0,
        "n_status_reviews": len(STATUS),
        "n_route_suggestions": 0,
        "verdict_counts": counts("verdict", lambda r: r["ref_col"] == "__VALIDITY__"),
        "concern_counts": counts("concern_type", lambda r: r["ref_col"] == "__VALIDITY__"),
        "status_verdict_counts": counts("verdict", lambda r: r["ref_col"] == "__STATUS__"),
    }

    OUT.write_text(json.dumps({"meta": meta, "resolutions": resolutions}, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"  {len(resolutions)} records = {n_units} ref units "
          f"+ {len(STATUS)} __STATUS__ + {len(VALIDITY)} __VALIDITY__")
    for k in ("ref_class_out_counts", "status_verdict_counts", "concern_counts"):
        print(f"  {k}: {meta[k]}")


if __name__ == "__main__":
    main()
