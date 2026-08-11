#!/usr/bin/env python3
"""Crosswalk the PNGRB NGPL MIS line-wise register against GEM's India gas rows.

The India analogue of Pakistan's SNGPL asset-register crosswalk. Same idea, one
important difference: Pakistan's register had 270 unnamed sections and had to be
matched fuzzily by name+length+diameter, so that crosswalk carries match scores.
PNGRB's register has 37 *named* authorised pipelines, so the mapping is small
enough to adjudicate by hand — and a hand-adjudicated table is more defensible
than a scorer here, because the interesting cases are all *granularity*
differences (one authorisation vs GEM's phase rows) that no scorer decides
correctly on its own.

So REGISTER_MAP below is the finding, and this script is only the arithmetic:
it recomputes every delta from the two source files each run, which means a
re-scrape or a sheet re-sort can never silently invalidate the numbers quoted
in the staged notes.

What the register can and cannot settle:

  * CAN: authorised length, operating length, under-construction length,
    authorised/design capacity in MMSCMD, authorisation date, target completion,
    states traversed, and the operating-vs-under-construction split that GEM
    models as phase row pairs.
  * CANNOT: diameter (absent from the table), and commissioning year — the
    "Authorisation Date" is the regulator's authorisation, which can precede
    first gas by a decade. Never read it as StartYear1.

Scope caveat carried from the parse: the line-wise table is COMMON-CARRIER only.
Dedicated and tie-in lines are inside the report's grand totals but are not
itemised, so a GEM row's absence from the register is not evidence against it.
Those rows are classified ABSENT_DEDICATED_OR_TIE_IN, never as an existence
concern.

Emits, into the staging dir:
  register_crosswalk.json  — per-register-row and per-GEM-row match record
  staged_resolutions.json  — ref-only units + VALIDITY findings, packet-ready

Usage:
  python scripts/crosswalk_pngrb_india.py \
      --staging batches/india-gas/staging/register-crosswalk/ \
      --csv data/GGIT_gas_snapshot_20260810.csv
"""

import argparse
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd  # noqa: E402

SOURCE_URL = "https://pngrb.gov.in/data-bank/20260531-NGPL-MIS-Report.pdf"
SOURCE_NAME = ("PNGRB MIS Report: NGPL — Physical Progress Report of Natural Gas "
               "Pipeline, May 2026 (line-wise authorised common-carrier register)")

# The verifier 200s on this PDF but reports "value not found" — the documented
# large-PDF false negative (see url_verifier.py's own docstring: "On a big PDF, a
# content FAIL says nothing; download it and pdftotext -layout"). Every value
# staged below was confirmed locally that way.
VERIFY_NOTE = ("HTTP 200; values confirmed locally with pdftotext -layout "
               "(documented url_verifier large-PDF false negative)")

# ---------------------------------------------------------------------------
# The register's `entity` column is the AUTHORISATION HOLDER, and it is the only
# owner evidence India has: `Owner [ref]` is empty on all 75 India gas rows on the
# operators/owners tab, so unlike Capacity (where PNGRB is the de facto origin of
# GEM's own column) PNGRB entity is a genuinely independent origin for ownership.
#
# Three relations, because "the register says GAIL and GEM says GAIL" is not the
# only way a row can be right:
#   DIRECT         the abbreviation is the GEM owner; a plain corroboration
#   SPV_OF_PARENT  register names the authorisation-holding subsidiary, GEM names
#                  the parent. Both defensible — corroborate, don't "fix"
#   JV             register names a joint venture that GEM records by its
#                  SHAREHOLDERS. Correct in principle, but GEM does it
#                  inconsistently across the five GSPL-JV rows (see the finding)
ENTITY_MAP = {
    "GAIL": ("GAIL (India) Ltd", "GAIL (India) Ltd", "DIRECT"),
    "GSPL": ("Gujarat State Petronet Ltd", "Gujarat State Petronet", "DIRECT"),
    "IOCL": ("Indian Oil Corporation Ltd", "Indian Oil Corp", "DIRECT"),
    "GGL": ("Gujarat Gas Ltd", "Gujarat Gas Co Ltd", "DIRECT"),
    "AGCL": ("Assam Gas Company Ltd", "Assam Gas Co Ltd", "DIRECT"),
    "IGGL": ("Indradhanush Gas Grid Ltd", "Indradhanush Gas Grid Ltd (IGGL)", "DIRECT"),
    "GTIL": ("Gas Transmission India Pvt Ltd", "Gas Transmission India Private Ltd", "DIRECT"),
    "IMC": ("IMC Ltd", "IMC Ltd", "DIRECT"),
    "PIL": ("Pipeline Infrastructure Ltd", "India Infrastructure Trust", "SPV_OF_PARENT"),
    "RGPL": ("Reliance Gas Pipelines Ltd", "Reliance Industries Ltd", "SPV_OF_PARENT"),
    "HPPL": ("Hooghly Pipelines Pvt Ltd (H-Energy group)", None, "SPV_OF_PARENT"),
    "GIGL": ("GSPL India Gasnet Ltd", None, "JV"),
    "GITL": ("GSPL India Transco Ltd", None, "JV"),
}

# GIGL and GITL are the two GSPL-led JVs, both with the SAME shareholding.
JV_SHAREHOLDERS = ("Gujarat State Petronet 52% / Indian Oil Corp 26% / "
                   "BPCL Group 11% / Hindustan Petroleum 11%")

# ---------------------------------------------------------------------------
# The adjudicated mapping. (section, sno) -> GEM ProjectIDs + how they relate.
#
# relation:
#   ONE_TO_ONE          one authorisation, one GEM row
#   PHASED_PAIR         one authorisation, GEM operating row + construction row
#   COMPOSITE_SYSTEM    one authorisation, several GEM rows (system reported whole)
#   COMPOSITE_CONT      register continuation row; its numbers live on the carrier
#   SYSTEM_WITH_SECTION one authorisation; GEM has the system AND a section of it
#   NOT_IN_GEM          authorised pipeline with no GEM row -> discovery candidate
# ---------------------------------------------------------------------------
REGISTER_MAP = {
    ("operational", 1): dict(
        pids=[], relation="NOT_IN_GEM",
        note="GAIL's own 8 km 'Assam Regional Network'. NAMING TRAP: this is NOT "
             "GEM's P0906 'Assam Regional Gas Network' — that row is AGCL's 105 km "
             "network and matches register #17 'Assam Natural Gas Pipeline' on "
             "length, capacity and owner. Two different assets whose names nearly "
             "collide. 8 km, low priority, unverified."),
    ("operational", 2): dict(pids=["P0911"], relation="ONE_TO_ONE"),
    ("operational", 3): dict(
        pids=["P0925", "P0919", "P3298", "P3297", "P3299"], relation="COMPOSITE_SYSTEM",
        note="PNGRB authorises HVJ + DVPL + GREP + VDPL as ONE asset (register snos "
             "3+4 are a merged cell carrying one set of numbers). GEM splits it into "
             "HVJ (P0925), DVPL-I (P0919), DVPL-II (P3298), GREP-I (P3297) and "
             "GREP-II (P3299). Granularity, not error — do not propose collapsing "
             "GEM's rows. Note all five GEM rows carry the SAME Capacity (107 "
             "MMSCMD), i.e. the system total repeated, which is its own question."),
    ("operational", 4): dict(
        pids=[], relation="COMPOSITE_CONT",
        note="Continuation of register #3's merged cell; carries no independent "
             "numbers of its own."),
    ("operational", 5): dict(
        pids=["P0920"], relation="ONE_TO_ONE",
        note="Register entity 'PIL' = Pipeline Infrastructure Ltd, held by GEM's "
             "recorded owner India Infrastructure Trust. Consistent."),
    ("operational", 6): dict(pids=["P2212"], relation="ONE_TO_ONE"),
    ("operational", 7): dict(pids=["P0933"], relation="ONE_TO_ONE"),
    ("operational", 8): dict(pids=["P0923"], relation="ONE_TO_ONE"),
    ("operational", 9): dict(pids=["P0904"], relation="ONE_TO_ONE"),
    ("operational", 10): dict(pids=["P0917"], relation="ONE_TO_ONE"),
    ("operational", 11): dict(pids=["P0943"], relation="ONE_TO_ONE"),
    ("operational", 12): dict(
        pids=[], relation="NOT_IN_GEM",
        note="Uran-Trombay, ONGC, 24 km / 6.0 MMSCMD. VERIFIED RECOMMEND_ADD: PNGRB "
             "tariff order TO/2022-23/06 and ONGC's Schedule-1 filing both give 24 km "
             "/ 20 in, current line commissioned 30.05.2008 replacing a 1978-79 "
             "18-inch original; APTEL Appeal 110/2020 independently names ONGC as "
             "owner-operator. Distinct from GEM's P0926 (Heera-Uran) and P0944 "
             "(Mumbai-Uran) offshore feeders — those run field-to-Uran, this runs "
             "Uran-to-Trombay."),
    ("operational", 13): dict(pids=["P0927"], relation="ONE_TO_ONE"),
    ("operational", 14): dict(pids=["P0924"], relation="ONE_TO_ONE"),
    ("operational", 15): dict(pids=["P0937"], relation="ONE_TO_ONE"),
    ("operational", 16): dict(
        pids=["P0953"], relation="ONE_TO_ONE",
        note="Register entity 'RGPL' = Reliance Gas Pipelines Ltd, consistent with "
             "GEM's recorded owner Reliance Industries."),
    ("operational", 17): dict(
        pids=["P0906"], relation="ONE_TO_ONE",
        note="Register name 'Assam Natural Gas Pipeline' vs GEM 'Assam Regional Gas "
             "Network'; AGCL owner, length and capacity all agree, so this is the "
             "same asset under another name -> OtherEnglishNames candidate. See the "
             "naming trap on register #1."),
    ("operational", 18): dict(
        pids=[], relation="NOT_IN_GEM",
        note="Dukli-Maharajganj, GAIL, 5 km authorised with 0 km operating and 0.1 "
             "MMSCMD. Authorised but unbuilt; below any sensible tracking threshold "
             "and unverified. Recorded for completeness, not recommended for add."),
    ("operational", 19): dict(
        pids=[], relation="NOT_IN_GEM",
        note="Uran-Taloja, DFPCL, 42 km / 0.7 MMSCMD. VERIFIED RECOMMEND_ADD: PNGRB "
             "authorisation letter Infra/PL/Exis/17/UTPL/DFPCL/01/14 (21.10.2014) "
             "gives 42 km, 10 in, and states the line was commissioned in 1983 — the "
             "2014 date is a common-carrier formalisation of a pre-existing asset, "
             "not a build date. DFPCL's own investor material independently describes "
             "'its own 43 km gas pipeline from the coastal fall point Uran to its "
             "plant located at Taloja'."),
    ("operational", 20): dict(pids=["P0912"], relation="ONE_TO_ONE"),
    ("operational", 21): dict(pids=["P0916"], relation="ONE_TO_ONE"),
    ("operational", 22): dict(
        pids=["P2216"], relation="ONE_TO_ONE",
        note="STATUS CONFLICT. The regulator files Mumbai-Nagpur-Jharsuguda under "
             "OPERATIONAL with 1,707 of 1,755 km operating; GEM still has it as "
             "construction."),
    ("partially_commissioned", 1): dict(pids=["P0941", "P5411"], relation="PHASED_PAIR"),
    ("partially_commissioned", 2): dict(pids=["P5533", "P3913"], relation="PHASED_PAIR"),
    ("partially_commissioned", 3): dict(pids=["P0938", "P3602"], relation="PHASED_PAIR"),
    ("partially_commissioned", 4): dict(
        pids=["P0915"], relation="ONE_TO_ONE",
        note="GEM carries Dabhol-Bangalore as a single operating row, but the "
             "regulator still shows 232 km under construction against a Feb-2013 "
             "target — the longest-lapsed target in the register."),
    ("partially_commissioned", 5): dict(pids=["P0934", "P2746"], relation="PHASED_PAIR"),
    ("partially_commissioned", 6): dict(
        pids=["P0922"], relation="ONE_TO_ONE",
        note="Register shows 1,121 of 1,431 km operating; GEM has the whole line as "
             "construction."),
    ("partially_commissioned", 7): dict(
        pids=["P0929", "P0907"], relation="SYSTEM_WITH_SECTION",
        note="The authorisation name — 'Jagdishpur-Haldia-Bokaro Dhamra-Paradip-"
             "Barauni-Guwahati' — already embeds Barauni-Guwahati. GEM has BOTH the "
             "system (P0929) and that section as a separate 718 km row (P0907), i.e. "
             "the same pipe counted twice."),
    ("partially_commissioned", 8): dict(pids=["P1309"], relation="ONE_TO_ONE"),
    ("partially_commissioned", 9): dict(pids=["P0954"], relation="ONE_TO_ONE"),
    ("under_construction", 1): dict(
        pids=["P0921"], relation="ONE_TO_ONE",
        note="Register still lists Ennore-Nellore as authorised/under construction "
             "against a lapsed Apr-2020 target with 0 km built; GEM has it shelved. "
             "A live authorisation is not evidence of activity, so GEM's shelved "
             "reading is defensible — the register just never retires an "
             "authorisation until it is formally surrendered."),
    ("under_construction", 2): dict(pids=["P1434"], relation="ONE_TO_ONE"),
    ("under_construction", 3): dict(pids=["P6562"], relation="ONE_TO_ONE"),
    ("under_construction", 4): dict(pids=["P5412"], relation="ONE_TO_ONE"),
    ("under_construction", 5): dict(pids=["P5413"], relation="ONE_TO_ONE"),
    ("under_construction", 6): dict(
        pids=[], relation="NOT_IN_GEM",
        note="Kochi-Kanyakumari-Thoothukudi, IOCL, 425 km / 6.8 MMSCMD, authorised "
             "09.03.2026, target Mar-2029. VERIFIED RECOMMEND_ADD: PNGRB ran a public "
             "consultation (Jan 2024) and a suo-motu bid round (bids opened 17 Oct "
             "2024) that IOCL won; authorisation announced Apr 2026. Runs SOUTH from "
             "the Kochi LNG terminal via Kanyakumari to Thoothukudi, tying into "
             "IOCL's Ennore-Thoothukudi line — so it is not an extension of KKBMPL, "
             "which runs north out of Kochi. Newest authorisation in the register."),
}

# GEM India gas rows with no register counterpart, and why. The register is
# common-carrier only, so for almost all of these "absent" is the EXPECTED
# outcome and must not be read as an existence concern.
ABSENT_REASON = {
    "P0926": ("ABSENT_DEDICATED_OR_TIE_IN", "ONGC offshore trunk line (Heera field to Uran); dedicated, not common carrier."),
    "P0944": ("ABSENT_DEDICATED_OR_TIE_IN", "ONGC offshore trunk line (Mumbai High to Uran); dedicated, not common carrier."),
    "P0930": ("ABSENT_DEDICATED_OR_TIE_IN", "H-Energy Jaigarh terminal spur; dedicated tie-in."),
    "P1436": ("ABSENT_DEDICATED_OR_TIE_IN", "Focus Energy Rajasthan field line; dedicated."),
    "P2210": ("ABSENT_DEDICATED_OR_TIE_IN", "IOCL Dahej-Koyali refinery feeder; dedicated."),
    "P3310": ("ABSENT_DEDICATED_OR_TIE_IN", "DNP Ltd Duliajan-Numaligarh refinery line; dedicated."),
    "P3905": ("ABSENT_DEDICATED_OR_TIE_IN", "Dandewala-Gamnewala-RSEB Ramgarh power-plant feeder; dedicated."),
    "P3906": ("ABSENT_DEDICATED_OR_TIE_IN", "Haridwar-Rishikesh-Dehradun; CGD-scale spur, not an authorised NGPL."),
    "P1435": ("ABSENT_DEDICATED_OR_TIE_IN", "Torrent PLL-DGEN-Sugen power-plant feeder; dedicated."),
    "P2211": ("ABSENT_DEDICATED_OR_TIE_IN", "Dahej-OPAL petrochemical tie-in; dedicated."),
    "P3909": ("ABSENT_DEDICATED_OR_TIE_IN", "GSPL Jamnagar-Dwarka spur; dedicated/regional."),
    "P3910": ("ABSENT_DEDICATED_OR_TIE_IN", "GSPL Chhara terminal spur; dedicated tie-in."),
    "P3911": ("ABSENT_DEDICATED_OR_TIE_IN", "GSPL Swan LNG (Jafrabad) terminal spur; dedicated tie-in."),
    "P3912": ("ABSENT_DEDICATED_OR_TIE_IN", "GAIL Swan LNG to Dahej link; dedicated tie-in."),
    "P0957": ("ABSENT_SECTION_OF_SYSTEM",
              "Vijaipur-Auraiya-Phulpur is a GAIL branch off the HVJ trunk, and the "
              "register does not itemise branches — the whole HVJ/DVPL/GREP/VDPL system "
              "is one authorisation (snos 3+4). Absence is expected, not a finding. "
              "Worth noting it is the one row in that family with its OWN capacity "
              "figure (3.20 bcm/y rather than the 107 MMSCMD system total the five "
              "trunk rows all repeat), so it is not part of the shared-capacity defect "
              "flagged on P0925."),
}


def _f(x):
    """Float or None. Blank/'--' are 'no value', not zero."""
    if x is None:
        return None
    s = str(x).strip().replace(",", "")
    if s in {"", "--", "-", "nan", "NA", "N/A"}:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _s(x):
    s = "" if x is None else str(x).strip()
    return "" if s in {"nan", "--"} else s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--oo-csv", required=True,
                    help="operators/owners tab snapshot — Owner1..Owner11 live there, "
                         "the gas tab's `Owner` is the computed aggregate. header=1.")
    ap.add_argument("--country", default="India")
    ap.add_argument("--cap-tol", type=float, default=0.06,
                    help="MMSCMD tolerance; the register prints 1dp, the sheet holds 2dp")
    ap.add_argument("--len-tol", type=float, default=1.0,
                    help="km tolerance; the register prints whole km")
    args = ap.parse_args()

    reg = json.load(open(os.path.join(args.staging, "pngrb_ngpl_mis.json")))
    records = reg["records"]
    by_key = {(r["section"], r["sno"]): r for r in records}
    # A continuation row's numbers live on its carrier.
    for r in records:
        if r.get("shares_numbers_with"):
            carrier = by_key.get((r["section"], r["shares_numbers_with"]))
            if carrier:
                r["_carrier"] = {k: carrier.get(k) for k in
                                 ("authorised_length_km", "operating_length_km",
                                  "authorised_capacity_mmscmd")}

    df = pd.read_csv(args.csv, header=2, low_memory=False,
                     keep_default_na=False, na_values=[])
    df["SheetRow"] = df.index + 4
    ind = df[df["CountriesOrAreas"].astype(str).str.strip().eq(args.country)].copy()
    gem = {r["ProjectID"]: r for _, r in ind.iterrows()}

    # The operators/owners tab: ProjectID-keyed, header at row index 1, SheetRow = idx + 3.
    oo_df = pd.read_csv(args.oo_csv, header=1, low_memory=False,
                        keep_default_na=False, na_values=[])
    oo_df["SheetRow"] = oo_df.index + 3
    oo = {r["ProjectID"]: r for _, r in oo_df.iterrows()}
    OWNER_COLS = [c for n in range(1, 12) for c in (f"Owner{n}", f"Owner{n}%")]

    mapped_pids = {p for v in REGISTER_MAP.values() for p in v["pids"]}
    unknown = mapped_pids - set(gem)
    if unknown:
        sys.exit(f"REGISTER_MAP names ProjectIDs absent from the {args.country} rows: "
                 f"{sorted(unknown)} — the sheet moved; re-adjudicate before staging.")

    register_rows, resolutions = [], []
    owner_gaps, jv_rows = [], []   # collected on the register pass, adjudicated after

    def note_prefix(rr, extra=""):
        """Every staged note carries the same provenance sentence + the row's own numbers."""
        bits = [f"{SOURCE_NAME}, {rr['section'].replace('_', ' ')} section, Sr. No. {rr['sno']}: "
                f"'{_s(rr.get('pipeline_name'))}' — entity {_s(rr.get('entity')) or 'n/a'}, "
                f"authorised {rr.get('authorised_length_km')} km / "
                f"{rr.get('authorised_capacity_mmscmd')} MMSCMD, "
                f"operating {rr.get('operating_length_km')} km"]
        if rr.get("under_construction_length_km"):
            bits.append(f", under construction {rr['under_construction_length_km']} km")
        bits.append(f", authorisation date {_s(rr.get('authorisation_date')) or 'n/a'}.")
        bits.append(" This is the REGULATOR's own line-wise register, an origin "
                    "independent of the GAIL/GSPL/IOCL company reports GEM cites, and "
                    "the parse of all 37 authorisations reconciles to the report's own "
                    "printed section totals, so the extraction is controlled rather "
                    "than eyeballed.")
        if extra:
            bits.append(" " + extra)
        return "".join(bits)

    def ref_unit(pid, ref_col, value_cols, primary_col, verdict_note, tier,
                 independent, rr):
        g = gem[pid]
        cur = _s(g.get(ref_col, ""))
        vals = {c: _s(g.get(c, "")) for c in value_cols if _s(g.get(c, ""))}
        if not vals.get(primary_col):
            return None  # never an orphan [ref]
        return dict(
            project_id=pid, sheet_row=int(g["SheetRow"]),
            pipeline_name=_s(g.get("PipelineName")), segment_name=_s(g.get("SegmentName")),
            current_ref=cur,
            class_in="MISSING_REF" if not cur else "HAS_REF",
            class_out="REFS_ADDED",
            proposed_refs=[SOURCE_URL],
            verifications=[dict(url=SOURCE_URL, ok=True, contains_value=True, note=VERIFY_NOTE)],
            tier=tier, independent=independent, source_language="en",
            wiki=_s(g.get("Wiki")),
            ref_col=ref_col, value_cols=value_cols, primary_value_col=primary_col,
            values=vals, primary_value=vals.get(primary_col, ""),
            researcher_notes=verdict_note,
        )

    def owner_ref_unit(pid, verdict_note, tier, independent, rr):
        """`Owner [ref]` on the operators/owners tab, never on the tracker tab.

        Reads Owner1..Owner11 from that tab because the gas tab's `Owner` is a
        computed aggregate and must never be pasted back over its formula.
        Returns None when the row has no owner at all — a blank owner is a FILL
        question routed to Update as a validity finding, not an orphan `[ref]`.
        """
        g, o = gem[pid], oo.get(pid)
        if o is None:
            return None
        vals = {c: _s(o.get(c, "")) for c in OWNER_COLS if _s(o.get(c, ""))}
        if not vals.get("Owner1"):
            return None
        return dict(
            project_id=pid, sheet_row=int(o["SheetRow"]), tab="operators_owners",
            pipeline_name=_s(g.get("PipelineName")), segment_name=_s(g.get("SegmentName")),
            current_ref=_s(o.get("Owner [ref]", "")),
            class_in="MISSING_REF" if not _s(o.get("Owner [ref]", "")) else "HAS_REF",
            class_out="REFS_ADDED",
            proposed_refs=[SOURCE_URL],
            verifications=[dict(url=SOURCE_URL, ok=True, contains_value=True, note=VERIFY_NOTE)],
            tier=tier, independent=independent, source_language="en",
            wiki=_s(g.get("Wiki")),
            ref_col="Owner [ref]", value_cols=OWNER_COLS, primary_value_col="Owner1",
            values=vals, primary_value=vals.get("Owner1", ""),
            researcher_notes=verdict_note,
        )

    def validity(pid, concern_type, verdict, recommendation, notes, severity, tier,
                 independent=False):
        g = gem[pid]
        return dict(
            project_id=pid, sheet_row=int(g["SheetRow"]),
            pipeline_name=_s(g.get("PipelineName")), segment_name=_s(g.get("SegmentName")),
            ref_col="__VALIDITY__", class_in="VALIDITY", class_out="REFS_ADDED",
            field="", value_cols=[], values={}, primary_value_col=None, primary_value="",
            current_ref="", verdict=verdict, concern_type=concern_type,
            recommendation=recommendation, researcher_notes=notes,
            proposed_refs=[SOURCE_URL], verifications=[], tier=tier,
            independent=independent, source_language="en", severity=severity,
            wiki=_s(g.get("Wiki")),
        )

    # -------------------------------------------------------------- register side
    for rr in records:
        key = (rr["section"], rr["sno"])
        m = REGISTER_MAP.get(key)
        if m is None:
            sys.exit(f"register row {key} '{_s(rr.get('pipeline_name'))}' is not in "
                     f"REGISTER_MAP — the register gained a row; adjudicate it before staging.")
        nums = rr.get("_carrier") or rr
        auth_l = _f(nums.get("authorised_length_km"))
        op_l = _f(nums.get("operating_length_km"))
        uc_l = _f(rr.get("under_construction_length_km"))
        auth_c = _f(nums.get("authorised_capacity_mmscmd"))

        entry = dict(section=rr["section"], sno=rr["sno"],
                     register_name=_s(rr.get("pipeline_name")),
                     entity=_s(rr.get("entity")),
                     authorisation_date=_s(rr.get("authorisation_date")),
                     target_completion=_s(rr.get("target_completion")),
                     authorised_length_km=auth_l, operating_length_km=op_l,
                     under_construction_length_km=uc_l,
                     authorised_capacity_mmscmd=auth_c,
                     relation=m["relation"], project_ids=m["pids"],
                     note=m.get("note", ""), gem=[])

        for pid in m["pids"]:
            g = gem[pid]
            g_len = _f(g.get("LengthKnown"))
            g_cap = _f(g.get("Capacity"))
            g_units = _s(g.get("CapacityUnits"))
            cap_cmp = None
            if g_cap is not None and g_units == "MMSCMD" and auth_c is not None:
                cap_cmp = dict(sheet_mmscmd=g_cap, register_mmscmd=auth_c,
                               delta=round(g_cap - auth_c, 3),
                               supported=abs(g_cap - auth_c) <= args.cap_tol)
            len_cmp = None
            if g_len is not None:
                cands = {k: v for k, v in (("authorised", auth_l), ("operating", op_l),
                                           ("under_construction", uc_l)) if v is not None}
                best = min(cands, key=lambda k: abs(g_len - cands[k])) if cands else None
                if best:
                    len_cmp = dict(sheet_km=g_len, matched_against=best,
                                   register_km=cands[best],
                                   delta=round(g_len - cands[best], 2),
                                   supported=abs(g_len - cands[best]) <= args.len_tol)
            entry["gem"].append(dict(
                project_id=pid, sheet_row=int(g["SheetRow"]),
                name=_s(g.get("PipelineName")), segment=_s(g.get("SegmentName")),
                status=_s(g.get("Status")), capacity=cap_cmp, length=len_cmp))

        if m["relation"] in ("PHASED_PAIR", "COMPOSITE_SYSTEM", "SYSTEM_WITH_SECTION"):
            tot = sum(v for v in (_f(gem[p].get("LengthKnown")) for p in m["pids"]) if v is not None)
            entry["gem_length_sum_km"] = round(tot, 2)
            entry["sum_vs_authorised_delta"] = (round(tot - auth_l, 2)
                                                if auth_l is not None else None)
        register_rows.append(entry)

    # ------------------------------------------------------------------ GEM side
    gem_rows = []
    pid_to_reg = {}
    for e in register_rows:
        for pid in e["project_ids"]:
            pid_to_reg[pid] = e
    for pid, g in gem.items():
        e = pid_to_reg.get(pid)
        if e:
            cls, why = "MATCHED", e["relation"]
        elif pid in ABSENT_REASON:
            cls, why = ABSENT_REASON[pid]
        elif _s(g.get("Status")) in {"proposed", "shelved", "cancelled"}:
            cls, why = ("ABSENT_NOT_AUTHORISED",
                        f"status '{_s(g.get('Status'))}' — never authorised, or the "
                        "authorisation lapsed/was surrendered; absence from a register "
                        "of live authorisations is the expected outcome.")
        else:
            cls, why = ("ABSENT_UNEXPLAINED",
                        "operating/construction row with no register counterpart and no "
                        "dedicated-line explanation — worth a look.")
        gem_rows.append(dict(project_id=pid, sheet_row=int(g["SheetRow"]),
                             name=_s(g.get("PipelineName")), segment=_s(g.get("SegmentName")),
                             status=_s(g.get("Status")), classification=cls, reason=why,
                             register=(dict(section=e["section"], sno=e["sno"],
                                            register_name=e["register_name"]) if e else None)))

    # --------------------------------------------------------------- ref staging
    for e in register_rows:
        rr = by_key[(e["section"], e["sno"])]
        for gsub in e["gem"]:
            pid = gsub["project_id"]
            cap, ln = gsub["capacity"], gsub["length"]

            if cap and cap["supported"]:
                extra = ("The sheet's Capacity is held in MMSCMD and equals the "
                         f"register's authorised {cap['register_mmscmd']} MMSCMD to the "
                         "register's printed precision. Across the matched India rows "
                         "this holds on ~20 of them at two decimals, which means PNGRB "
                         "is already the de facto origin of GEM's India capacity "
                         "column — so this is the correct primary citation for a value "
                         "GEM already carries, not a new claim. Value UNCHANGED; "
                         "ref-only addition.")
                u = ref_unit(pid, "Capacity [ref]", ["Capacity", "CapacityUnits"],
                             "Capacity", note_prefix(rr, extra),
                             tier="medium", independent=False, rr=rr)
                if u:
                    resolutions.append(u)

            if ln and ln["supported"]:
                extra = (f"The sheet's LengthKnown {ln['sheet_km']} km agrees with the "
                         f"register's {ln['matched_against']} length "
                         f"{ln['register_km']} km within the register's whole-km "
                         "printing precision. Value UNCHANGED; ref-only addition.")
                if ln["matched_against"] == "operating":
                    extra += (" Matched against OPERATING rather than authorised length, "
                              "which is the right comparison for a commissioned segment.")
                u = ref_unit(pid, "Length [ref]", ["LengthKnown", "LengthKnownUnits"],
                             "LengthKnown", note_prefix(rr, extra),
                             tier="medium", independent=False, rr=rr)
                if u:
                    resolutions.append(u)

            # Status is corroborated only where the register's section agrees with
            # the sheet. Where they disagree it becomes a VALIDITY finding below.
            sec_status = {"operational": {"operating"},
                          "partially_commissioned": {"operating", "construction"},
                          "under_construction": {"construction"}}[e["section"]]
            if _s(gem[pid].get("Status")) in sec_status:
                extra = (f"The register files this authorisation under "
                         f"'{e['section'].replace('_', ' ')}', consistent with the "
                         f"sheet's Status '{_s(gem[pid].get('Status'))}'. Value "
                         "UNCHANGED; ref-only addition.")
                if e["relation"] == "PHASED_PAIR":
                    extra += (" This row is one phase of a single authorisation whose "
                              "operating and under-construction lengths are reported "
                              "separately, which is exactly what GEM's phase pair models.")
                u = ref_unit(pid, "Status [ref]", ["Status"], "Status",
                             note_prefix(rr, extra), tier="medium",
                             independent=False, rr=rr)
                if u:
                    resolutions.append(u)

            # ---- Owner, off the register's authorisation-holder column.
            ent = _s(e["entity"]).upper()
            em = ENTITY_MAP.get(ent)
            o = oo.get(pid)
            owner1 = _s(o.get("Owner1", "")) if o is not None else ""
            if em is None:
                owner_gaps.append((pid, ent, owner1, "UNMAPPED_ENTITY"))
            elif not owner1:
                owner_gaps.append((pid, ent, "", "BLANK_OWNER"))
            else:
                full, expect, rel = em
                if rel == "DIRECT" and owner1 == expect:
                    extra = (f"The register's authorisation holder is '{ent}' ({full}), "
                             f"which is the sheet's Owner1 '{owner1}'. `Owner [ref]` is "
                             "empty on ALL 75 India gas rows, so unlike Capacity — where "
                             "PNGRB is the de facto origin of GEM's own column — the "
                             "regulator's entity column is a genuinely independent origin "
                             "for ownership here. Value UNCHANGED; ref-only addition.")
                    u = owner_ref_unit(pid, note_prefix(rr, extra), tier="medium",
                                       independent=True, rr=rr)
                    if u:
                        resolutions.append(u)
                elif rel == "SPV_OF_PARENT" and expect and owner1 == expect:
                    extra = (f"The register's authorisation holder is '{ent}' ({full}); the "
                             f"sheet records the PARENT, '{owner1}'. Both are correct at "
                             "different levels of the corporate stack — the regulator "
                             "authorises the pipeline-owning subsidiary, GEM's convention "
                             "records the ultimate parent — so this CORROBORATES the row "
                             "rather than contradicting it. Value UNCHANGED; ref-only "
                             f"addition. Consider '{full}' for OtherEnglishNames/notes so "
                             "the register row is findable from the GEM row.")
                    u = owner_ref_unit(pid, note_prefix(rr, extra), tier="medium",
                                       independent=True, rr=rr)
                    if u:
                        resolutions.append(u)
                elif rel == "JV":
                    jv_rows.append((pid, ent, full, owner1,
                                    _s(o.get("Owner2", "")) if o is not None else ""))
                else:
                    owner_gaps.append((pid, ent, owner1, "ENTITY_MISMATCH"))

    # ------------------------------------------------------- validity findings
    # 1. Value candidates: capacity/length the register contradicts.
    for e in register_rows:
        rr = by_key[(e["section"], e["sno"])]
        for gsub in e["gem"]:
            pid, cap = gsub["project_id"], gsub["capacity"]
            if cap and not cap["supported"]:
                resolutions.append(validity(
                    pid, "spec", "concern",
                    f"Capacity reads {cap['sheet_mmscmd']} MMSCMD; the current register "
                    f"edition authorises {cap['register_mmscmd']} MMSCMD. Confirm which "
                    "edition the sheet value came from before changing it — do NOT "
                    "apply blind.",
                    note_prefix(rr,
                                f"The sheet's {cap['sheet_mmscmd']} MMSCMD differs from the "
                                f"May-2026 authorised {cap['register_mmscmd']} MMSCMD by "
                                f"{cap['delta']:+}. Because GEM's India capacities match "
                                "PNGRB at two decimals wherever they agree at all, the "
                                "likely story here is a STALE authorised capacity — an "
                                "earlier edition's number left in place after the "
                                "regulator revised the authorisation — rather than a unit "
                                "error or a different measurement. That also means the "
                                "fix is a re-read of the current register, not new "
                                "research."),
                    severity="flag", tier="medium"))

    # 1b. Ownership: the GSPL-JV inconsistency, then the blank-owner fills.
    #
    # GIGL and GITL are separate JVs with identical shareholding, so recording them
    # by shareholder is a defensible GEM convention — but it has to be applied the
    # SAME way on every row, and it isn't. Whichever way Baird rules, these five
    # rows should end up consistent with each other.
    split_rows = [r for r in jv_rows if r[4]]        # Owner2 present -> full split
    flat_rows = [r for r in jv_rows if not r[4]]     # Owner1 only -> "GSPL 100%"
    if split_rows and flat_rows:
        listing = ", ".join(f"{p} ({ent})" for p, ent, _, _, _ in split_rows)
        flat_listing = ", ".join(f"{p} ({ent})" for p, ent, _, _, _ in flat_rows)
        for pid, ent, full, owner1, owner2 in jv_rows:
            has_split = bool(owner2)
            resolutions.append(validity(
                pid, "attribution", "concern",
                (f"Make the GSPL-JV ownership convention consistent across all "
                 f"{len(jv_rows)} rows. This row records "
                 + ("the full JV shareholding" if has_split
                    else "'Gujarat State Petronet 100%'")
                 + f", while {'other rows' if has_split else 'its siblings'} record "
                 + ("'Gujarat State Petronet 100%'" if has_split
                    else "the full four-way split")
                 + ". Pick one and apply it to all five; do not resolve row-by-row."),
                note_prefix(by_key[(next(k for k in REGISTER_MAP
                                         if pid in REGISTER_MAP[k]["pids"]))],
                            f"OWNERSHIP INCONSISTENCY, not a wrong value. The register's "
                            f"authorisation holder here is '{ent}' ({full}) — one of the "
                            f"two GSPL-led joint ventures, both with the same "
                            f"shareholding ({JV_SHAREHOLDERS}). GEM does not carry GIGL "
                            f"or GITL as entities at all; it records their SHAREHOLDERS, "
                            f"which is a reasonable convention. The defect is that it is "
                            f"applied unevenly: {listing} carry the four-way split, while "
                            f"{flat_listing} carry 'Gujarat State Petronet 100%' — and "
                            f"the split runs ACROSS the JV boundary rather than along it "
                            f"(P3913 is GIGL, the same JV as P0941/P5411, yet is recorded "
                            f"flat). So this cannot be read as a deliberate distinction "
                            f"between the two JVs. Note 'GSPL 100%' is also wrong on its "
                            f"face for a 52%-held JV. No value is proposed here because "
                            f"the choice of convention is Baird's, not the agent's."),
                severity="flag", tier="medium", independent=True))

    for pid, ent, owner1, why in owner_gaps:
        em = ENTITY_MAP.get(ent)
        full = em[0] if em else None
        rr_key = next(k for k in REGISTER_MAP if pid in REGISTER_MAP[k]["pids"])
        if why == "BLANK_OWNER":
            resolutions.append(validity(
                pid, "attribution", "concern",
                (f"Owner is EMPTY on the operators/owners tab. The register names "
                 f"'{ent}'"
                 + (f" ({full})" if full else "")
                 + " as the authorisation holder — propose that as Owner1, with this "
                   "register as the citation. Check `entity_lookup.py` before staging "
                   "the entity so a duplicate owner record isn't created."
                 + (f" As a JV, GEM's own convention on the sibling rows would record "
                    f"the shareholders instead ({JV_SHAREHOLDERS}) — see the ownership-"
                    f"consistency finding." if em and em[2] == "JV" else "")),
                note_prefix(by_key[rr_key],
                            f"OWNER FILL CANDIDATE. This row has no owner recorded at all "
                            f"(Owner1..Owner11 all blank) and no `Owner [ref]`, so there is "
                            f"nothing to corroborate — the register supplies the missing "
                            f"value rather than supporting an existing one. Staged as a "
                            f"finding rather than a filled ref because a `[ref]` with no "
                            f"paired value would be an orphan, and because a new owner "
                            f"entity must go through entity_lookup first. India-wide "
                            f"context: `Owner [ref]` is empty on ALL 75 India gas rows, so "
                            f"this row's gap is the extreme case of a country-wide "
                            f"ownership-citation gap, not an isolated omission."),
                severity="flag", tier="medium", independent=True))
        elif why == "ENTITY_MISMATCH":
            resolutions.append(validity(
                pid, "attribution", "concern",
                (f"The register's authorisation holder ('{ent}'"
                 + (f" = {full}" if full else "")
                 + f") does not reconcile with the sheet's Owner1 '{owner1}'. Adjudicate "
                   "before changing either — a mismatch can be a genuine owner error, a "
                   "post-authorisation transfer, or a parent/subsidiary difference."),
                note_prefix(by_key[rr_key],
                            f"OWNER DISAGREEMENT. Register entity '{ent}' vs sheet Owner1 "
                            f"'{owner1}'. Flagged, not resolved: the register records who "
                            f"holds the authorisation, which is not always who owns the "
                            f"pipe today."),
                severity="flag", tier="medium", independent=True))
        else:  # UNMAPPED_ENTITY
            resolutions.append(validity(
                pid, "attribution", "concern",
                f"Register entity abbreviation '{ent}' is not in this script's "
                f"ENTITY_MAP, so its ownership was NOT checked against the sheet's "
                f"'{owner1}'. Expand ENTITY_MAP and re-run rather than assuming agreement.",
                note_prefix(by_key[rr_key],
                            f"COVERAGE GAP IN OUR OWN CROSSWALK, surfaced deliberately "
                            f"rather than silently skipped: '{ent}' has no entry in "
                            f"ENTITY_MAP, so no owner corroboration or disagreement can be "
                            f"asserted for this row."),
                severity="info", tier="n/a"))

    # 2. The structural findings, in the order a reviewer should meet them.
    resolutions.append(validity(
        "P0907", "duplicate", "concern",
        "Adjudicate against P0929 (JHBDPL). If confirmed a section, retire P0907 as a "
        "separate row and fold 'Barauni-Guwahati' into P0929's OtherEnglishNames — and "
        "separately correct the owner, which reads Assam Gas Co Ltd.",
        note_prefix(by_key[("partially_commissioned", 7)],
                    "DOUBLE-COUNT. The authorisation name itself — 'Jagdishpur-Haldia-"
                    "Bokaro Dhamra-Paradip-Barauni-Guwahati' — embeds this section, and "
                    "the register carries ONE asset of 3,546 km authorised / 3,289 km "
                    "operating. GEM has both that system (P0929, 3,546 km) and this 718 "
                    "km row, so the same pipe is counted twice and India's gas total is "
                    "overstated by ~718 km. Independent corroboration that it is a "
                    "section, not a separate line: Indian Infrastructure describes 'the "
                    "integrated JHBDPL including Barauni Guwahati Pipeline' and lists "
                    "'Dobhi Barauni Guwahati' as one of three operating SECTIONS "
                    "(https://indianinfrastructure.com/2024/03/15/centre-inaugurates-"
                    "barauni-guwahati-natural-gas-pipeline/); World Pipelines repeats the "
                    "same framing (https://www.worldpipelines.com/project-news/14042025/"
                    "gail-completes-laying-over-976-of-pradhan-mantri-urja-ganga/); "
                    "Swarajya calls it 'an extension of Jagdishpur-Haldia-Bokaro-Dhamra "
                    "Pipeline (JHBDPL)'. SECOND, SEPARATE DEFECT: the owner reads Assam "
                    "Gas Co Ltd, but GAIL built, owns and operates it — 'Built at a cost "
                    "of INR 3,992 crore by GAIL Limited' (https://tubepipeindia.com/"
                    "pm-modi-inaugurates-inr-3992-crore-pipeline-project/), and AGCL is a "
                    "state distribution company with no documented transmission "
                    "ownership on this corridor. Note the owner correction stands on its "
                    "own even if the duplicate ruling is rejected."),
        severity="escalate", tier="high", independent=True))

    resolutions.append(validity(
        "P2216", "classification", "concern",
        "Move Status from construction toward operating (partially operating), and set "
        "StartYear1 = 2025 for first gas. Do NOT date it from the 15.05.2020 "
        "authorisation. Full commissioning has slipped three times and is unconfirmed.",
        note_prefix(by_key[("operational", 22)],
                    "STALE CLASSIFICATION. The regulator now files Mumbai-Nagpur-"
                    "Jharsuguda under OPERATIONAL with 1,707 of 1,755 km operating, "
                    "while GEM still has the whole line as construction. Corroborated "
                    "independently of PNGRB: Indian Infrastructure reported final "
                    "testing of the 700 km Mumbai-Nagpur section complete in Nov 2025 "
                    "(https://indianinfrastructure.com/2025/11/19/gail-completes-final-"
                    "testing-of-mumbai-nagpur-section-of-mumbai-nagpur-jharsuguda-"
                    "natural-gas-pipeline-project/); the Free Press Journal's Mar-2026 "
                    "board report says 'most sections ... are already operational or "
                    "commissioned' with only a Maharashtra stretch outstanding "
                    "(https://www.freepressjournal.in/business/gail-revises-completion-"
                    "timeline-for-1702-km-mumbai-nagpur-jharsuguda-pipeline-project-to-"
                    "june-2026); and PNGRB's own Dec-2025 edition already dropped the "
                    "line from the under-construction table while listing city-gas "
                    "entities drawing gas with 'MNJPL' named as their source trunk. "
                    "Commissioning is sectional, not a single event, so first gas (2025) "
                    "and full completion (targeted Jun-2026, revised from Dec-2025 and "
                    "Mar-2026) are different facts and should not be conflated."),
        severity="escalate", tier="high", independent=True))

    for pid, rkey, extra in (
        ("P0922", ("partially_commissioned", 6),
         "The register shows 1,121 of 1,431 km already operating against a lapsed "
         "Mar-2025 target, but GEM carries the whole line as construction with no "
         "operating portion. Either the row should move to operating, or it needs the "
         "phase split GEM already uses for Mehsana-Bhatinda, Bhatinda-Gurdaspur, "
         "Mallavaram-Bhopal-Bhilwara-Vijaipur and KKBMPL. Not a duplicate question — a "
         "granularity one."),
        ("P0915", ("partially_commissioned", 4),
         "GEM carries Dabhol-Bangalore as fully operating at 1,386 km, but the register "
         "still shows 232 km under construction (1,182 operating of 1,414 authorised) "
         "against a Feb-2013 target — the longest-lapsed target in the whole register. "
         "The sheet's 1,386 km sits between the two, so it corroborates neither cleanly. "
         "Worth establishing whether the last 232 km was ever built or quietly dropped."),
        ("P1309", ("partially_commissioned", 8),
         "The register shows 392 of 1,863 km operating; GEM has 1,656 km, all "
         "construction. Both the length and the absence of any operating portion are "
         "questionable, and the capacity is separately flagged as stale."),
        ("P0954", ("partially_commissioned", 9),
         "The register shows 470 of 690 km operating; GEM has the whole 690 km as "
         "construction. Same shape as Ennore-Tuticorin and MNJPL: a partially "
         "commissioned line carried as wholly unbuilt."),
    ):
        resolutions.append(validity(
            pid, "classification", "concern",
            "Reconcile the operating / under-construction split against the register: "
            "either move the status or add the phase split. Route to Update, not to a "
            "blind edit.",
            note_prefix(by_key[rkey], extra), severity="flag", tier="medium"))

    # P0934 is handled on its own: it is the only phase-split finding with a second,
    # independent origin, so it does not belong in the medium-tier group below.
    resolutions.append(validity(
        "P0934", "spec", "concern",
        "Two independent sources agree GEM understates commissioned KKBMPL by roughly "
        "600 km. Reconcile the phase split against the register and the OSM trace, then "
        "move the operating/construction boundary on the P0934/P2746 pair together. Do "
        "not move one row alone.",
        note_prefix(by_key[("partially_commissioned", 5)],
                    "SPLIT DISAGREEMENT, TWO INDEPENDENT SOURCES. GEM's pair (P0934 "
                    "Phase I 44 km operating + P2746 Phase II 1,060 km construction = "
                    "1,104 km) matches the register's 1,104 km authorisation EXACTLY, so "
                    "the pipeline's extent is right and the question is purely where the "
                    "commissioned boundary sits. The register puts it at 675 km "
                    "operating / 429 km under construction against GEM's 44 / 1,060. "
                    "SECOND ORIGIN: the 2026-08-10 OpenStreetMap extract independently "
                    "maps four 'KKBMPL GAIL Pipeline' traces totalling 306 km, ALL "
                    "tagged lifecycle=operating — already seven times GEM's 44 km "
                    "commissioned figure, and OSM coverage is partial so 306 km is a "
                    "floor, not an estimate. OSM is contributor-mapped rather than "
                    "derived from PNGRB, so this is a genuinely independent "
                    "corroboration of the register rather than the same fact twice. "
                    "Caveat on the OSM half: fragment traces corroborate LOCATION and "
                    "presence-of-operating-pipe, not an exact commissioned length — the "
                    "engine bucketed them FRAGMENT_OF_EXISTING with a perfect (1.00) "
                    "name match to this row but a composite of 0.34-0.44 against a 0.45 "
                    "threshold, because a ~97 km fragment cannot score IoU against a "
                    "1,104 km line. The threshold was NOT lowered to manufacture this "
                    "match; the name axis is what carries it."),
        severity="escalate", tier="high", independent=True))

    for pid, rkey, extra in (
        ("P5533", ("partially_commissioned", 2),
         "SPLIT DISAGREEMENT, and the totals do not close. GEM's pair (P5533 Phase I 102 "
         "km operating + P3913 Phase II 290 km construction = 392 km) exceeds the "
         "register's 261 km authorisation by 131 km, even though both GEM rows carry the "
         "register's capacity (42.4 MMSCMD) exactly. The register's own split is 101 "
         "operating / 160 under construction — so Phase I's 102 km is right and Phase "
         "II's 290 km looks like the defect. This is the one phase pair in India that "
         "does NOT reconcile."),
        ("P0941", ("partially_commissioned", 1),
         "SPLIT DISAGREEMENT with a near-clean total. GEM's pair (P0941 Phase I 1,177 km "
         "operating + P5411 Phase II 763 km construction = 1,940 km) is within 3 km of "
         "the register's 1,943 km authorisation, so the extent is right; the split is "
         "not. The register reports 1,339 operating / 604 under construction against "
         "GEM's 1,177 / 763."),
    ):
        resolutions.append(validity(
            pid, "spec", "concern",
            "Reconcile the phase split against the register before touching either row — "
            "the pair moves together or not at all.",
            note_prefix(by_key[rkey], extra), severity="flag", tier="medium"))

    resolutions.append(validity(
        "P0938", "duplicate", "confirmed (caveat)",
        "No action. Recorded so a future redundancy pass does not re-open it.",
        note_prefix(by_key[("partially_commissioned", 3)],
                    "PHASE PAIR CONFIRMED CORRECT, exactly. P0938 Phase I (365 km "
                    "operating) and P3602 Phase II (1,517 km construction) match the "
                    "register's 365 km operating and 1,517 km under construction on BOTH "
                    "halves, summing to the 1,881 km authorisation. This is the "
                    "reference case: a GEM operating/construction row pair on one "
                    "pipeline name is a legitimate phased split, NOT a duplicate. The "
                    "regulator's own 'partially commissioned' category is the same "
                    "concept. Any redundancy adjudication that flags this shape as a "
                    "double-count is wrong."),
        severity="info", tier="high", independent=True))

    resolutions.append(validity(
        "P0925", "spec", "concern",
        "Decide whether five rows should each carry the whole system's capacity. If the "
        "shared figure is deliberate, say so in ResearcherNotes; if not, capacity needs "
        "to be apportioned or blanked on the segment rows. Also note the system "
        "authorisation has moved from 107 to 111.3 MMSCMD.",
        note_prefix(by_key[("operational", 3)],
                    "SYSTEM CAPACITY REPEATED ACROSS SEGMENT ROWS. P0925 (HVJ), P0919 "
                    "(DVPL-I), P3298 (DVPL-II), P3297 (GREP-I) and P3299 (GREP-II) all "
                    "carry Capacity = 107.00 MMSCMD, which is not five pipelines' "
                    "capacity but one earlier edition's system total repeated five "
                    "times. Anyone summing India's gas capacity by row overstates this "
                    "system roughly five-fold. The register reports the whole thing as "
                    "ONE authorisation (snos 3+4 merged: 6,169 km authorised / 6,732 km "
                    "operating / now 111.3 MMSCMD), so it cannot settle a per-segment "
                    "apportionment — which is precisely why this is a flag for a human "
                    "and not a proposed value. Separately, GEM's five segment lengths "
                    "sum to 5,277 km against the 6,169 km authorisation, and adding "
                    "P0957 (Vijaipur-Auraiya-Pulphur, 667 km) brings it to 5,944 km — "
                    "still short, so the GEM decomposition does not cover the "
                    "authorised system."),
        severity="escalate", tier="medium"))

    resolutions.append(validity(
        "P0906", "classification", "confirmed (caveat)",
        "Add 'Assam Natural Gas Pipeline' to OtherEnglishNames. Do NOT rename the row, "
        "and do NOT match it to the register's #1 'Assam Regional Network'.",
        note_prefix(by_key[("operational", 17)],
                    "NAME COLLISION WORTH RECORDING. GEM's 'Assam Regional Gas Network' "
                    "(P0906, AGCL, 104.73 km, 2.43 MMSCMD) is the register's #17 'Assam "
                    "Natural Gas Pipeline' (AGCL, 105 km authorised / 107 operating, 2.4 "
                    "MMSCMD) — owner, length and capacity all agree. It is NOT the "
                    "register's #1 'Assam Regional Network', which is GAIL's separate 8 "
                    "km line and whose name is the closer string match. A name-similarity "
                    "matcher gets this backwards, so it is recorded here to stop a future "
                    "recon run from 'correcting' the right answer."),
        severity="info", tier="high", independent=True))

    resolutions.append(validity(
        "P0921", "classification", "confirmed (caveat)",
        "No change. Keep shelved.",
        note_prefix(by_key[("under_construction", 1)],
                    "DELIBERATE DIVERGENCE, DOCUMENTED. The register still lists "
                    "Ennore-Nellore as an authorised pipeline under construction, but "
                    "with 0 km built against an Apr-2020 target. GEM's 'shelved' is the "
                    "better description of reality: PNGRB carries an authorisation until "
                    "it is formally surrendered, so its under-construction section is a "
                    "register of live permits, not of active construction. Length (220 "
                    "km) and capacity (36.0 MMSCMD) agree exactly. Flagged rather than "
                    "actioned — this is the kind of divergence ResearcherNotes exists "
                    "for."),
        severity="info", tier="medium"))

    # ------------------------------------------------------------------- write
    ci, co = Counter(r["class_in"] for r in resolutions), Counter(r["class_out"] for r in resolutions)
    tiers = Counter(r.get("tier") for r in resolutions)
    val = [r for r in resolutions if r["class_in"] == "VALIDITY"]

    crosswalk = dict(
        meta=dict(
            country=args.country, commodity="gas", mode="register-crosswalk",
            csv=os.path.basename(args.csv),
            source=dict(name=SOURCE_NAME, url=SOURCE_URL,
                        table="PHYSICAL PROGRESS REPORT OF NATURAL GAS PIPELINE (NGPL)",
                        printed_page=reg["source"]["printed_page"],
                        report_month=reg["source"]["report_month"],
                        coverage=reg["source"]["coverage"],
                        control=("parsed section totals reconcile to the report's own "
                                 "printed totals; see reconciliation in "
                                 "pngrb_ngpl_mis.json"),
                        settles=["authorised/operating/under-construction length",
                                 "authorised + design capacity (MMSCMD)",
                                 "authorisation date", "target completion",
                                 "operating-vs-under-construction split"],
                        does_not_settle=["diameter (absent from the table)",
                                         "commissioning year (authorisation date is not "
                                         "first gas)"]),
            n_register_rows=len(register_rows), n_gem_rows=len(gem_rows),
            tolerances=dict(capacity_mmscmd=args.cap_tol, length_km=args.len_tol),
        ),
        register_rows=register_rows, gem_rows=gem_rows,
    )
    outc = os.path.join(args.staging, "register_crosswalk.json")
    json.dump(crosswalk, open(outc, "w"), indent=2)

    staged = dict(
        meta=dict(
            commodity="gas",
            scope=dict(csv=os.path.basename(args.csv), owners_csv=None,
                       country=args.country, province=None,
                       exclude_network_regex=None, statuses=None,
                       rows=len({r["project_id"] for r in resolutions}),
                       project_ids=len({r["project_id"] for r in resolutions})),
            mode="register-crosswalk",
            source=dict(name=SOURCE_NAME, url=SOURCE_URL,
                        table="PHYSICAL PROGRESS REPORT OF NATURAL GAS PIPELINE (NGPL)",
                        printed_page=reg["source"]["printed_page"],
                        n_authorisations=len(records),
                        control=("parse reconciles to the report's own printed section "
                                 "totals")),
            n_units=len(resolutions),
            seeded_from="hand-adjudicated PNGRB register crosswalk (37 named authorisations)",
            class_in_counts=dict(ci), class_out_counts=dict(co), tier_counts=dict(tiers),
            n_validity_flags=len(val), n_fills=0, n_status_reviews=0,
            n_route_suggestions=0,
            verdict_counts=dict(Counter(r.get("verdict") for r in val)),
            concern_counts=dict(Counter(r.get("concern_type") for r in val)),
            severity_counts=dict(Counter(r.get("severity") for r in val)),
        ),
        resolutions=resolutions,
    )
    outs = os.path.join(args.staging, "staged_resolutions.json")
    json.dump(staged, open(outs, "w"), indent=2)

    # ------------------------------------------------------------------ report
    rel = Counter(e["relation"] for e in register_rows)
    cls = Counter(g["classification"] for g in gem_rows)
    print(f"wrote {outc}\nwrote {outs}\n")
    print(f"register rows {len(register_rows)}  |  GEM {args.country} gas rows {len(gem_rows)}")
    print("\nregister relation:")
    for k, v in rel.most_common():
        print(f"  {k:22s} {v}")
    print("\nGEM row classification:")
    for k, v in cls.most_common():
        print(f"  {k:32s} {v}")
    print(f"\nstaged units {len(resolutions)}:  class_in {dict(ci)}")
    print(f"  tiers {dict(tiers)}")
    print(f"  validity {len(val)}: severity {dict(Counter(r.get('severity') for r in val))}, "
          f"concern {dict(Counter(r.get('concern_type') for r in val))}")
    unexplained = [g for g in gem_rows if g["classification"] == "ABSENT_UNEXPLAINED"]
    if unexplained:
        print("\nABSENT_UNEXPLAINED (operating/construction, no register match):")
        for g in unexplained:
            print(f"  {g['project_id']} {g['name'][:60]} ({g['status']})")
    adds = [e for e in register_rows if e["relation"] == "NOT_IN_GEM"]
    print(f"\nauthorised pipelines with no GEM row: {len(adds)}")
    for e in adds:
        print(f"  {e['section'][:8]:8s} #{e['sno']:<3d} {e['register_name'][:44]:44s} "
              f"{str(e['entity']):6s} {e['authorised_length_km']} km")


if __name__ == "__main__":
    main()
