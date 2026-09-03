#!/usr/bin/env python3
"""SUPERSEDED 2026-09-03 by scripts/build_redundancy.py (generic --staging/--clusters
emitter, same record schema; this CLUSTERS table still loads via `--clusters <this
file>`). Kept for the run record only.

Stage the Uzbekistan-gas redundancy adjudication (§3 `validity` leg, cluster-level).

The operating deep sweep + status review and the targeted ref-gap re-pass raised
duplicate-and-overlap questions row by row. This pass resolves them into EIGHT
structural clusters and stages one `__VALIDITY__` record per implicated row carrying the
CLUSTER-level recommendation. Detection lives in `../ref-sweep-operating/`; adjudication
lives here. Read-and-flag only — never an edit (QC detects, Update fixes).

    python batches/uzbekistan-gas/staging/redundancy/build_redundancy.py

SCOPE: 17 of the 18 in-scope rows are implicated. The 18th, P2698 (Shurtan-Sherabad), has
no sibling and no corridor overlap with anything else in scope — its one open item is a
ref-provenance defect (its Diameter [ref] points at an unrelated Baysun GPZ environmental
summary) already staged as a ref record, not a validity question. All 13 rows Kazakhstan
already staged are excluded from the research legs, and that matters here twice over:
cluster C's three Mubarek-Zirabulak strings hang off BTBA parent rows P0739/P5810, which
are two of those 13, so the parent's citations describe the parent trunk and not the
strings; and cluster H (P2030) is a five-country row that is NOT one of the 13 (Kazakhstan
is not among its countries), so it is legitimately in scope while still sharing its cells
with four other country scopes.

**Read this before any cluster below: as in Kazakhstan, IDENTICAL OR NEAR-IDENTICAL DRAWN
GEOMETRY IS NOT EVIDENCE OF DUPLICATION HERE.** Uzbekistan's rows are multi-string trunk
systems and the geometry follows the same shared-right-of-way convention: the three
Gazli-Kagan rows (cluster A) carry a BYTE-IDENTICAL 105.34 km trace and identical
LengthEstimateKm 105.50; the three Mubarek-Zirabulak strings (C) are 2-vertex schematics
~131 km long drawn a few hundred metres apart; the two Mubarek-Kagan strings (D) likewise
at ~99.5 km. For parallel threads on one right-of-way that is a convention, not a defect,
so every duplicate hypothesis here is decided on ATTRIBUTES and SOURCES.

The one shape geometry WOULD decide is the aggregate-vs-segment case, whose signature is a
row whose trace is the UNION of other rows that each have their own DISTINCT trace. No
cluster here has it. Cluster A's three rows do not have distinct traces at all (they share
one), which is the opposite pattern; and cluster F's near-coincidence — P5870's line lying
along P4073's corridor with its end on the exact Gazli vertex all three cluster-A rows
start from — is one shared network node, not containment.

Where geometry DOES earn its keep in this batch is as a falsifier, twice:

* **It sharpens cluster E's existence concern.** P6964 is carried as Yangiyer-Ahangaran I,
  but its drawn line does not lie on that corridor at all: it starts 0.432 km from
  P4071's END and runs east, with Yangiyer 178.2 km from its nearest vertex, Pungan
  10.2 km and Andijan 65.2 km. That is the Ahangaran-Pungan line's continuation, not
  Yangiyer-Ahangaran.
* **It REFUTES an agent finding on P6937 (cluster G).** The operating sweep flagged a
  material 35% gap between LengthKnown 300.00 km and LengthEstimateKm 406.14 km and asked
  for a route/length review. There is no disagreement to review: the geometry is THREE
  parts, and the MAINLINE alone measures 282.3 km ending 20.0 km from Dushanbe — exactly
  the sheet's ~300 km. The 406 km is that mainline plus two spurs (85.5 km and 38.1 km).
  The estimate is a multi-part summation artifact; the recommendation is withdrawn and
  what remains is a narrower question about what those two spurs are.

Uzbekistan's structural motif is the one India and Kazakhstan both have: **a system-level
figure restated on every string.** Capacity 35.00 mill.Sm3/day sits on BOTH P2290 and
P3984 (cluster A), and the sheet's own cited diameter source gives one figure
(Ø1020x12 mm) for all three Mubarek-Zirabulak threads together while the rows carry
1020 / 1021 / 1022 (cluster C). The second of those is the batch's clearest defect: a
segment index folded into a diameter cell.

SIX of the eight clusters REFUTE a duplicate hypothesis (A, C, D, F, G, and B's
parent/expansion pairing). That is deliberate — an unrecorded refutation gets re-raised by
the next sweep, and two of them (C's three identical-looking schematics, F's shared Gazli
node) read as textbook duplicates on geometry alone. Cluster E is the one live existence
question, and even there the standing rule holds: an unconfirmed row is not deleted.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

CSV = "data/GGIT_gas_snapshot_20260826.csv"
OO_CSV = "data/GEM_operators_owners_snapshot_20260826.csv"
OUT = Path(__file__).resolve().parent
REPO = OUT.parents[3]

UZREPORT_EDC = ("https://uzreport.news/economy/epsilon-edc-prodoljaetsya-razvitie-"
                "gazotransportnoy-infrastrukturi-uzbekistana")
KUNUZ = "https://kun.uz/ru/08357022#!"
LEXUZ_PP4563 = "https://lex.uz/ru/docs/4689644"
GAZETA_PUNGAN = "https://www.gazeta.uz/ru/2024/03/26/pungan-namangan/"
UZDAILY_AP = "https://www.uzdaily.uz/en/post/6945/"
MNGMAJ = "http://www.mngmaj.uz/about/index.htm"
# ngm.uz answered 503 on 2026-08-26 -- an access failure, not a deletion, so it is
# deliberately NOT attached as a citable proposed ref; cluster F's prose says retry.
NGM = "https://ngm.uz/ru/page/view/22"

# (concern_type, recommendation, researcher_notes, severity)
CLUSTERS: dict[str, dict] = {
    # ---------------------------------------------------------------- A
    "A": {
        "title": "Gazli-Kagan (P2290 / P3984 / P3983): the shared 105.34 km trace is a "
                 "right-of-way convention, NOT a double count — four numbered strings "
                 "across three rows, duplicate hypothesis REFUTED; what survives is "
                 "Capacity 35.00 mill.Sm3/day restated on two rows and P3983's 140 km "
                 "length outlier",
        "refs": [],
        "rows": {
            "P2290": (
                "spec",
                "KEEP — not a duplicate of P3983/P3984, and do not fold anything in this "
                "cluster. Two open items, neither of them duplication. (1) CAPACITY: "
                "Capacity=35.00 mill.Sm3/day (CapacityBcm/y 12.78) sits on BOTH this row "
                "and P3984 while P3983 carries 25.00 — the signature of a corridor-total "
                "throughput attributed to individual strings rather than a per-line split. "
                "Establish whether 35.00 is the whole Gazli-Kagan corridor or this row's "
                "strings specifically; if it is the corridor figure it belongs on "
                "PipelineNetworkGrouping, with per-row throughput or a blank plus "
                "ResearcherNotes on each row. (2) GRANULARITY: SegmentName is "
                "'Segment I, II' and Diameter is '720, 1020' — this single row carries TWO "
                "physical strings of different diameter, so no per-string length, capacity "
                "or diameter on it is separable and none should be 'corrected' to a single "
                "value. Consider splitting it into two rows on the same evidence that "
                "P3984 (III) and P3983 (IV) are separate rows; that is a structural call "
                "for Update, not a cell fix.",
                "DUPLICATE HYPOTHESIS REFUTED. What raised it: all three Gazli-Kagan rows "
                "carry BYTE-IDENTICAL geometry — the same 13-vertex, 105.34 km trace "
                "(Gazli 63.4856,40.1538 -> Kagan 64.5399,39.7218), and the sheet's own "
                "LengthEstimateKm reads 105.50 on all three. Under the Kazakhstan ruling "
                "that decides nothing: parallel strings on one right-of-way conventionally "
                "share a corridor geojson, and this is not the aggregate-vs-segment shape "
                "either (that needs a row whose trace is the UNION of others' DISTINCT "
                "traces; here no row has a distinct trace at all). WHAT REFUTES IT on "
                "attributes: the rows enumerate four numbered strings across three rows "
                "with different diameters, different commissioning years and different "
                "lengths — this row = Segments I and II (720 and 1020 mm, 1973, "
                "115.30 km), P3984 = Segment III (1020 mm, 2006, 116.00 km), P3983 = "
                "Segment IV (2023, 140.00 km, diameter separately corrected to 1220 mm). "
                "A fifty-year build-out of successive parallel threads on one corridor is "
                "exactly what this pattern looks like, and the row-by-row sweep confirmed "
                "existence, dates, status, classification and location on every one of "
                "them. RESIDUAL: the 35.00 mill.Sm3/day on this row and P3984 is the "
                "system-level-figure-on-every-string motif India carries with 107.00 "
                "MMSCMD on five HVJ rows and Kazakhstan with 4.54 bcm/y on four "
                "Zhanaozen rows; and this row's two-strings-in-one-row packing is why its "
                "115.30 km cannot be checked against the 105.34 km drawn corridor the way "
                "P3984's 116.00 km can.",
                "flag",
            ),
            "P3984": (
                "spec",
                "KEEP as Segment III — a real third string, not a copy. One open item: "
                "Capacity=35.00 mill.Sm3/day is the same figure P2290 carries, likely a "
                "corridor total duplicated onto two segment rows rather than each "
                "segment's own throughput; resolve it once for the cluster (see P2290). "
                "Its own length (116.00 km against the 105.34 km drawn corridor, a normal "
                "schematic-vs-as-built margin) and its 2006 start year need no change.",
                "REFUTED as a duplicate on the same cluster evidence as P2290: distinct "
                "SegmentName (III), distinct start year (2006 vs 1973 and 2023), distinct "
                "single diameter (1020 mm where P2290 carries two). Its byte-identical "
                "trace with P2290 and P3983 is the shared-right-of-way convention. The "
                "one thing it shares that is NOT explained by that convention is the "
                "capacity value, which is the cluster's real finding.",
                "flag",
            ),
            "P3983": (
                "spec",
                "KEEP as Segment IV. TWO cell-level items for Update, both already staged "
                "in the ref sweep and repeated here because they are what the cluster "
                "reduces to: (1) Diameter 1020 -> 1220 mm (sourced; DiameterUnits stays "
                "mm); (2) LengthKnown 140.00 km is the cluster's one length outlier — it "
                "exceeds the shared drawn corridor (105.34 km) by ~33% and its two "
                "siblings' 115.30 / 116.00 km by ~21%, on nominally the same Gazli->Kagan "
                "endpoints. Establish whether Segment IV takes a longer alignment, or "
                "whether 140.00 belongs to a different stretch. Do NOT reconcile it "
                "downward to the drawn geometry: the corridor trace is shared and is a "
                "lower bound, not a measurement of this string.",
                "REFUTED as a duplicate: Segment IV is the 2023 string, the newest in a "
                "corridor built out since 1973, and its capacity (25.00 mill.Sm3/day) is "
                "the one value in the cluster that is NOT restated from a sibling. Its "
                "length is the open question and it is a genuine spec question, not a "
                "rollup: an aggregate row would exceed the corridor because it summed "
                "siblings, but 140.00 is not the sum of anything here (115.30 + 116.00 = "
                "231.30). The diameter correction to 1220 mm came from sourcing that "
                "disagreed with the recorded 1020 mm, which is why that ref unit was left "
                "UNRESOLVED rather than staged as a confirmation.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- B
    "B": {
        "title": "Ahangaran-Pungan (P4071 + P4072 Expansion): a legitimate parent + "
                 "25 km loop, not a duplicate — but EndState/Province='Fergana' is wrong "
                 "on BOTH rows (Pungan is in Namangan Region), a defect the row-by-row "
                 "sweep caught only on the expansion row",
        "refs": [GAZETA_PUNGAN, LEXUZ_PP4563, UZDAILY_AP],
        "rows": {
            "P4071": (
                "attribution",
                "KEEP — the 2009 parent line, independently confirmed. TWO items. (1) "
                "EndState/Province='Fergana' is WRONG on this row too: Pungan is in Pop "
                "district (Papskiy rayon), NAMANGAN Region. The ref sweep flagged this on "
                "the expansion row P4072 only; it propagates from the parent, so fix both "
                "or neither. Do not apply blind — confirm the terminus is the Pungan "
                "settlement in Namangan rather than a like-named point, then correct both "
                "rows in one edit. (2) SegmentCost 429,900,000 -> 492,900,000 USD (already "
                "staged as a sourced fill; a digit transposition, 429.9 <-> 492.9, with "
                "every dated primary source giving US$492.9M = $417.9M own funds + $75M "
                "Fund for Reconstruction and Development credit).",
                "NOT A DUPLICATE of P4072 and the pairing is correct as modelled: P4072 is "
                "an 'Expansion' carrying 25 km of NEW physical pipe (a loop), so the "
                "standing expansion rule (no new pipe -> LengthKnown=0, Diameter blank) "
                "does not apply and its 25.00 km / 1020 mm are right in principle. The "
                "province error is the cluster's real finding and it is a cross-row one: "
                "both rows read StartState='Tashkent' / EndState='Fergana', and only the "
                "start half is right. This row's drawn line (102.38 km, 2 vertices, "
                "69.6334,40.9187 -> 70.8269,40.7391) is a straight-line schematic against "
                "LengthKnown 165.00 km, so the drawn span is a LOWER BOUND and not "
                "evidence against the stated length.",
                "flag",
            ),
            "P4072": (
                "attribution",
                "KEEP as the expansion. THREE items, all routed to Update. (1) "
                "EndState/Province 'Fergana' -> 'Namangan' — same fix as the parent row, "
                "apply together. (2) LENGTH: 25 km (2020 construction-start "
                "announcement, matching the sheet) vs 'almost 22 km' (2025 completion "
                "reporting, as-built). Both are independently sourced and they are "
                "planned-vs-as-built, not a contradiction; decide which the column should "
                "carry and record the other in ResearcherNotes rather than overwriting. "
                "(3) DIAMETER: 1020 mm is not supported by the cited Facebook video (the "
                "verifier's substring hit was JS/inline-CSS telemetry, '-1020px', not "
                "article text) — leave it uncited pending a source that states this "
                "looping segment's diameter. It is plausible from the programme's standard "
                "trunk diameter, but plausible is not sourced. Also the one routeless row "
                "in the cluster (RouteAccuracy='no route', RouteType='Unavailable') and a "
                "natural §8 candidate: its corridor is already pinned by the parent's "
                "trace.",
                "REFUTED as a duplicate of P4071 — a 25 km loop on a 165 km line is new "
                "pipe on an existing corridor, which is exactly what an Expansion row is "
                "for, and existence/classification/non-duplicate status were all "
                "independently confirmed row-by-row. The province defect is inherited from "
                "the parent, which is why it is adjudicated at cluster level: fixing it on "
                "one row alone leaves the tracker internally inconsistent on the same "
                "physical terminus.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- C
    "C": {
        "title": "Mubarek-Zirabulak I/II/III (P6933 / P6934 / P6935): three real parallel "
                 "threads, duplicate REFUTED — but the diameter ladder 1020 / 1021 / 1022 "
                 "is a SEGMENT INDEX FOLDED INTO THE DIAMETER CELL, and the sheet's own "
                 "cited source gives Ø1020x12 mm for all three",
        "refs": [UZREPORT_EDC],
        "rows": {
            "P6933": (
                "spec",
                "KEEP — thread I, confirmed. No change to this row's Diameter (1020 mm is "
                "the correct, sourced value and is what makes its two siblings' values "
                "diagnosable). Its Owner [ref] is a confirmed dead link "
                "(utg.uz/ru/about/history/, genuine 404): under the standing rule that is "
                "a deletion candidate only once its Wayback capture has been read — ADD "
                "the snapshot alongside, never swap it in, and never drop the ref over an "
                "access failure. Length / Capacity stay UNRESOLVED at thread level, which "
                "is the correct outcome here, not a gap (see notes).",
                "REFUTED as a duplicate of P6934/P6935. What raised it: three 2-vertex "
                "schematics of near-identical length (131.33 / 130.87 / 130.76 km) drawn a "
                "few hundred metres apart on the same Mubarek<->Zirabulak axis, with "
                "P6934 digitized in the opposite direction. Under the shared-right-of-way "
                "convention that is what three parallel threads look like. WHAT CONFIRMS "
                "THEY ARE REAL: the sheet's own cited source (uzreport.news, 2020-09-09, "
                "the EDC/Epsilon overhaul report) names threads I, II and III explicitly "
                "and gives Ø1020x12 mm for the 50-78 km section of ALL THREE together. "
                "That same sentence is what convicts the diameter cells: one figure for "
                "three threads cannot be the origin of 1020 / 1021 / 1022. WHY THESE ROWS "
                "ARE LEGITIMATELY THIN: their parent is the Bukhara-Tashkent-Bishkek-Almaty "
                "trunk, whose GEM rows P0739/P5810 are two of the 13 Kazakhstan already "
                "staged and therefore excluded from this batch — so the parent page's "
                "citations describe the PARENT TRUNK, not these strings, and a harvested "
                "wiki URL does not earn a cell on a Mubarek-Zirabulak row. Per-thread "
                "length and capacity are genuinely unpublished; UNRESOLVED is the honest "
                "answer, the Kazakhstan calibration rather than the India one.",
                "flag",
            ),
            "P6934": (
                "spec",
                "Correct Diameter 1021 -> 1020 mm, citing the row's OWN existing Diameter "
                "[ref] (uzreport.news), which states Ø1020x12 mm. Do NOT fold this row "
                "into P6933/P6935 — it is real, separate pipe. One-cell fix; DiameterUnits "
                "unchanged.",
                "REFUTED as a duplicate; the finding is a data defect, not a redundancy. "
                "The row's own cited source gives 1020 mm and the cell says 1021 — the "
                "value does not match the byte it is attached to, which is why the ref "
                "sweep left this unit UNRESOLVED rather than staging it as a "
                "confirmation. Taken with P6935's 1022 the pattern is unmistakable: "
                "thread index I/II/III added to a base diameter of 1020. It is recorded at "
                "cluster level because neither row's fix is defensible in isolation — the "
                "argument is the LADDER, and the source that refutes it covers all three "
                "threads at once.",
                "flag",
            ),
            "P6935": (
                "spec",
                "Correct Diameter 1022 -> 1020 mm, same source and same one-cell shape as "
                "P6934. Do NOT fold into P6933/P6934.",
                "REFUTED as a duplicate; same defect as P6934 one step further along the "
                "ladder. The cited uzreport.news report does not differentiate a diameter "
                "per thread at all — it gives Ø1020x12 mm for threads I, II and III "
                "together on the 50-78 km overhaul section — so there is no source "
                "anywhere for 1021 or 1022, and the two values are internally generated. "
                "Fix both rows in one edit so the ladder cannot be half-repaired.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- D
    "D": {
        "title": "Mubarek-Kagan I/II (P6965 / P6966): two parallel threads ~1.5 km apart, "
                 "duplicate REFUTED — per-string Length/Diameter/Capacity are genuinely "
                 "unpublished, so UNRESOLVED is the correct outcome, not a gap",
        "refs": [MNGMAJ],
        "rows": {
            "P6965": (
                "spec",
                "KEEP as thread I. No value changes. One sourcing item: ADD "
                "mngmaj.uz/about/index.htm as a corroborating existence ref ALONGSIDE the "
                "existing liting.uz citation — do not replace it. liting.uz is reachable "
                "and is not a confirmed 404; it is a client-rendered SPA our tooling "
                "cannot read, which is an access limitation and explicitly not grounds to "
                "drop a once-working ref. Leave Length / Diameter / Capacity UNRESOLVED.",
                "REFUTED as a duplicate of P6966. What raised it: two 2-vertex schematics "
                "of 99.84 and 99.27 km on the same Kagan<->Mubarek axis, offset ~1.5 km — "
                "again the shared-right-of-way convention for numbered threads (SegmentName "
                "I and II). NETWORK COHERENCE supports both being real: this thread's "
                "start vertex (64.5446,39.7220) is the same Kagan node the three "
                "Gazli-Kagan rows terminate on, and its Mubarek end is the node cluster C "
                "and G both hang off — the drawn network joins up as a system rather than "
                "repeating one line. WHY THE THIN SPECS ARE CORRECT: no public "
                "Uzbek source itemises these strings individually; the best line-wise "
                "material describes the systems. Calibrate as Kazakhstan (an honest "
                "UNRESOLVED on a per-string spec), not as India (where a blank means "
                "nobody looked).",
                "flag",
            ),
            "P6966": (
                "spec",
                "KEEP as thread II. Existence, classification and endpoints all "
                "corroborate. ADD the newly sourced StartState/Province='Qashqadaryo "
                "Region' and EndState/Province='Bukhara Region' (staged as a fill; the "
                "unit had to be re-opened by hand after the brief builder dropped it). "
                "Leave Length / Diameter / Capacity UNRESOLVED — genuinely unsourceable at "
                "string level. Consider adding a Wayback capture alongside liting.uz/page/4 "
                "since it is an SPA our tooling cannot read; do not remove the live URL.",
                "REFUTED as a duplicate on the same cluster evidence as P6965. Its "
                "province fill is the one value this cluster gained: it was sourced against "
                "a gazetteer rather than inferred, after the deep sweep left the same unit "
                "UNRESOLVED for want of a citable location source (the Egypt Abu "
                "Madi/GeoNames precedent). Both rows carry a blank Owner on the "
                "operators/owners tab, which in GGIT gas is the norm rather than an "
                "Uzbekistan defect — do not import India's reading of a blank Operator "
                "here.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- E
    "E": {
        "title": "Yangiyer-Ahangaran I/II (P6964 operating / P6963 construction): THE "
                 "batch's one live existence question, and geometry sharpens it — P6964's "
                 "drawn line is not on the Yangiyer-Ahangaran corridor at all but starts "
                 "0.432 km from P4071's END and runs east toward Andijan",
        "refs": [],
        "rows": {
            "P6964": (
                "existence",
                "TREAT AS UNCONFIRMED pending sourcing — and do NOT delete it on this "
                "evidence. Investigate whether it is a phantom or a duplicate artifact of "
                "P6963 (same PipelineName, same endpoints, one row per status) rather than "
                "a distinct pre-existing physical line. THREE things to establish, in this "
                "order: (1) whether an OPERATING Yangiyer-Ahangaran thread exists at all, "
                "independent of the line P6963 has under construction; (2) if it does, "
                "REDRAW the route — the current geometry is on the wrong corridor (see "
                "notes) and its 111.29 km LengthEstimateKm is therefore not a measurement "
                "of this pipeline; (3) StartState/Province 'Fergana' -> 'Sirdaryo' "
                "(Yangiyer is in Sirdaryo Region), the same fix P6963 needs. If the "
                "operating thread cannot be sourced, this is a row-level escalation for "
                "Baird, not a silent removal.",
                "THE ONE EXISTENCE CONCERN IN THE BATCH, and the only cluster where "
                "geometry argues FOR a defect rather than against one. The row-by-row "
                "sweep raised it on attributes: blank Owner, blank LengthKnown, blank "
                "StartYear1, no per-row sourcing, and an identical PipelineName and "
                "endpoint pair to P6963 with only Status separating them (operating vs "
                "construction) — the shape of one pipeline entered twice at two stages. "
                "GEOMETRY SHARPENS IT DECISIVELY: this row's 2-vertex trace runs "
                "70.8243,40.7424 -> 71.9792,40.2657, which is NOT the Yangiyer-Ahangaran "
                "corridor. Yangiyer is 178.2 km from its nearest vertex and Ahangaran "
                "75.2 km, while Pungan is 10.2 km and Andijan 65.2 km — and its start "
                "point is 0.432 km from the END of P4071 (Ahangaran-Pungan). So the drawn "
                "line is an eastward continuation of the Ahangaran-Pungan axis toward "
                "Andijan, ~2 degrees of longitude from where this row's own endpoints put "
                "it. Two readings remain open and geometry cannot separate them: the row "
                "is real and its route was mis-digitized off the neighbouring corridor, or "
                "the row itself is a mis-entry. Either way its LengthEstimateKm is an "
                "artifact. WHAT IS NOT EVIDENCE: the near-identical schematics of "
                "clusters C and D are the convention; this is the opposite case, a trace "
                "that does not touch its own stated endpoints.",
                "escalate",
            ),
            "P6963": (
                "attribution",
                "KEEP — existence, classification, spec and non-duplicate status were all "
                "corroborated row-by-row; this row is the better-evidenced half of the "
                "pair and is NOT the one in question. Two items: (1) StartState/Province "
                "'Fergana' -> 'Sirdaryo Region' (Yangiyer is not in Fergana) — do not "
                "apply blind, pin the actual compressor-station location rather than the "
                "city centre first, and fix it together with P6964 since both rows carry "
                "the same wrong value; (2) it is routeless (RouteAccuracy='no route', "
                "RouteType='Unavailable') and a §8 candidate — but sequence it AFTER "
                "P6964's existence question is settled, because if the two rows turn out "
                "to be one pipeline the route belongs to whichever survives.",
                "The CONFIRMED half of the pair, recorded here so the cluster is not read "
                "as casting doubt on both rows. Its 95.00 km Yangiyer->Ahangaran under "
                "construction is coherent and independently corroborated. Its own "
                "geometry is absent (null placeholder), so it contributes nothing to the "
                "corridor question either way — which is worth stating, because the "
                "temptation is to read P6964's wrong-corridor trace as belonging to this "
                "row instead. It does not: P6964's trace is on the Ahangaran-Pungan-Andijan "
                "axis, not on Yangiyer-Ahangaran, so it is not this row's missing route.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- F
    "F": {
        "title": "Gazli-Nukus (P4073) vs Gazli-Sarymay (P5870): the shared Gazli node and "
                 "P5870 lying along P4073's corridor are network topology, NOT containment "
                 "— segment-of hypothesis REFUTED; what survives is P4073's 350-vs-562 km "
                 "length vintage and P5870's route stopping 110.8 km short of Sarymay",
        "refs": [],
        "rows": {
            "P4073": (
                "spec",
                "KEEP — existence, classification and non-duplicate status are solidly "
                "confirmed; P5870 is not a segment of it (see notes). TWO open items. "
                "(1) LENGTH VINTAGE: LengthKnown 350.00 km against a 562.50 km drawn "
                "route in two parts. The most likely reading is that 350 km is the 1997 "
                "FIRST-STAGE line while the geometry includes the 2004+ expansion "
                "sections — establish which the column is meant to carry, and record the "
                "other in ResearcherNotes. Do not reconcile the column to the geometry. "
                "(2) DIAMETER: independently verify 1220 mm against the ORIGINAL 1997 "
                "350 km run specifically — the only diameter figure any independent "
                "source states outright is for the 2004+ expansion sections, not the base "
                "line, which is the same first-stage-vs-expansion ambiguity as (1) and "
                "probably resolves with it. Also carries the open Capacity [ref] lead the "
                "sweep left UNRESOLVED (a 2004 Gazli-Nukus expansion to 7 bcm/y, then "
                "12 bcm/y after a 2005-2006 stage) — chase Uzbekneftegaz/UTG annuals and "
                "Gazprom Central Asia purchase reporting.",
                "SEGMENT-OF HYPOTHESIS REFUTED. What raised it: P5870's entire 2-vertex "
                "span lies along this row's corridor — its start is 5.8 km and its end "
                "9.8 km from this row's nearest vertices — and its end sits on the EXACT "
                "Gazli vertex (63.485626,40.153802, 0.0000 km) that all three cluster-A "
                "Gazli-Kagan rows start from. On geometry alone that reads as a slice of "
                "this line. WHAT REFUTES IT: a shared origin NODE is not containment. Four "
                "systems radiate from the Gazli hub in this snapshot (Gazli-Kagan x3, "
                "Gazli-Nukus, Gazli-Sarymay) and a coincident vertex is what a correctly "
                "digitized network looks like, not a double count. Nor is this the "
                "aggregate signature: this row's trace is not the union of others' "
                "distinct traces, and P5870's own destination is a DIFFERENT place — "
                "Sarymay in Xorazm, 30.7 km off this corridor, versus Nukus in "
                "Karakalpakstan 22.7 km off it. Two lines sharing a departure hub and "
                "diverging to different termini are two lines. RESIDUAL, and it is a real "
                "one: 350.00 km stated against 562.50 km drawn is a 61% gap, far outside "
                "schematic slack, and the first-stage-vs-expansion reading needs sourcing "
                "rather than assumption.",
                "flag",
            ),
            "P5870": (
                "spec",
                "KEEP — not a segment of P4073. One route-and-length item, and it is the "
                "cluster's actual defect: the drawn line stops 110.8 km short of Sarymay "
                "itself, so the geometry does not reach this row's own stated terminus, "
                "and it measures 163.75 km against LengthKnown 103.00 km. Establish where "
                "the Sarymay end actually is before touching either: if 103.00 km is right "
                "the route is over-drawn along the Nukus corridor; if the route's extent is "
                "right the length is short. RouteAccuracy is already 'very low (straight "
                "line/schematic)', which is honest, so this is a redraw candidate rather "
                "than a correction. No value change is staged. Retry ngm.uz next sweep to "
                "convert the spec figures from strongly-suggested to independently cited.",
                "REFUTED as a segment of P4073 on the reasoning recorded on that row: "
                "shared Gazli origin node, divergent termini. This row's own problem is "
                "internal consistency, not redundancy. Its 2-vertex trace runs "
                "61.9533,41.0568 -> 63.4856,40.1538 — digitized SARYMAY-ward-to-GAZLI, "
                "i.e. reversed relative to its name — and its far end is 110.8 km from "
                "Sarymay while Sarymay is only 30.7 km from P4073's corridor. So the drawn "
                "line neither reaches its stated terminus nor is it simply P4073's first "
                "163 km. Because the route is an admitted straight-line schematic, the "
                "drawn 163.75 km is a LOWER BOUND on a real alignment and cannot be used "
                "to overwrite the stated 103.00 km — which makes the two figures a "
                "question, not a contradiction to resolve arithmetically.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- G
    "G": {
        "title": "Kelif-Mubarek (P6936) / Kelif-Dushanbe (P6937): distinct consecutive "
                 "trunks, duplicate REFUTED — and P6937's '35% length gap' is REFUTED too "
                 "(the mainline alone is 282.3 km ending 20.0 km from Dushanbe; the 406 km "
                 "estimate sums two spurs). What survives: transposed "
                 "OtherLanguagePrimaryPipelineName values and a shared dead Owner ref",
        "refs": [KUNUZ],
        "rows": {
            "P6936": (
                "attribution",
                "KEEP — data is sound on existence, classification and non-duplicate "
                "status. THREE sourcing repairs, no value changes. (1) Swap "
                "OtherLanguagePrimaryPipelineName with P6937 — the two rows' values are "
                "TRANSPOSED; fix both in one edit. (2) Repoint Fuel [ref] and "
                "PipelineType [ref] off the Facebook video onto the already-verified "
                "kun.uz URL (or another source that actually names Kelif-Mubarek); the "
                "Facebook match was JS/inline-CSS telemetry, not article text. (3) Owner2 "
                "= Turkmengaz needs independent verification: the utg.uz/ru/about/history/ "
                "half of the Owner [ref] pair is a confirmed genuine 404 and the "
                "mfa.gov.tm half, though live, does not name this pipeline. Do NOT delete "
                "the ref pair on this pass — the 404 is real but its Wayback capture "
                "(20260314231446) exists and could not be read this session, so the "
                "correct action is to ADD the snapshot alongside once a researcher with "
                "working web.archive.org access can confirm it carries the value.",
                "REFUTED as a duplicate of P6937. The two rows are CONSECUTIVE, not "
                "parallel: this row is drawn 65.4817,39.1680 (Mubarek) -> 66.2273,37.2115 "
                "(Kelif), 252.97 km, and P6937 starts 0.4 km away at Kelif and runs on "
                "toward Dushanbe. They share one junction node and no corridor, which is "
                "the same network-topology reading that refutes cluster F — and here it is "
                "even cleaner, since the traces abut rather than overlap. Both rows are "
                "genuinely thin on specs (blank Length, Diameter and Capacity on this "
                "row), which is the Kazakhstan calibration for a cross-border trunk with "
                "no line-wise register, not a defect to fill by inference.",
                "flag",
            ),
            "P6937": (
                "attribution",
                "KEEP as a standalone transmission trunk distinct from P6936. TWO items, "
                "and one WITHDRAWAL. (1) Swap OtherLanguagePrimaryPipelineName with P6936 "
                "(transposed; one edit for both rows). (2) Drop the dead utg.uz URL from "
                "Owner [ref] ONLY under the standing rule — it is a confirmed 404, but add "
                "its Wayback capture alongside first rather than leaving the cell thinner; "
                "and note that the mfa.gov.tm URL sharing that cell is live but does not "
                "mention this pipeline, so Owner1/2/3 (Uztransgaz / Tajik Transgaz / "
                "Turkmengaz) remains effectively uncited and is the row's real open item. "
                "(3) WITHDRAWN — the earlier recommendation to review LengthKnown 300.00 "
                "against LengthEstimateKm 406.14 as a material 35% gap. There is no gap to "
                "review (see notes); do not re-raise it. Its Start [ref] and Length [ref] "
                "rest solely on a UN Statistics Division PPT reachable only through a "
                "Wayback URL whose content could not be re-read this session — existence "
                "of the capture is API-confirmed at the cited timestamp, but the "
                "value-present claim is unverified, so confirm the link opens and carries "
                "the figure before pasting either ref.",
                "REFUTED TWICE. As a duplicate of P6936: consecutive trunks abutting at "
                "Kelif, no shared corridor. And on the LENGTH FINDING, which is a "
                "reversal of this batch's own row-by-row verdict and is recorded in full "
                "because the numbers looked decisive. What was flagged: LengthKnown "
                "300.00 km vs LengthEstimateKm 406.14 km, a 35% gap on a route graded "
                "'high' accuracy, with the drawn end appearing to fall 216 km short of "
                "Dushanbe. WHAT REFUTES IT: the geometry is THREE parts, and the naive "
                "reading took the last coordinate of the last part as the line's end. The "
                "MAINLINE is part one — 7 vertices, 282.3 km, Kelif 66.232,37.208 -> "
                "68.569,38.616, whose end is 20.0 km from Dushanbe. That is the pipeline, "
                "and 282.3 km drawn against 300.00 km stated is ordinary schematic slack "
                "on a correctly routed trunk. The other two parts are spurs of 85.5 km "
                "(66.750,37.406 -> 67.332,37.910) and 38.1 km (66.878,37.426 -> "
                "67.109,37.137), and LengthEstimateKm simply sums all three — 282.3 + "
                "85.5 + 38.1 = 405.9, the 406.14 figure. So the estimate is a multi-part "
                "summation artifact, the route is right, and the stated length is right. "
                "WHAT STAYS OPEN, narrower than what was withdrawn: what those two spurs "
                "are and whether they belong on this row at all, since a computed length "
                "column that silently includes branch geometry will misreport every "
                "multi-part row in the tracker. GENERAL LESSON, and the reason this is "
                "written out: a computed length is a claim about the GEOMETRY'S EXTENT, "
                "not about the pipeline — read the parts before believing the sum.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- H
    "H": {
        "title": "Central Asia-China Line D (P2030): not a duplication question but a "
                 "MULTI-COUNTRY SCOPE one — a five-country shelved row whose 966 km and "
                 "30 bcm/y are whole-project figures, in Uzbekistan's scope but sharing "
                 "its cells with four other country scopes",
        "refs": [],
        "rows": {
            "P2030": (
                "attribution",
                "KEEP — existence, classification, length, capacity, delay flag, cost and "
                "endpoints all confirmed at row level. THREE items, and one procedural "
                "warning that governs all of them. (1) OWNERSHIP: replace Owner2/Owner3 "
                "'Turkmengaz' and 'QazaqGaz' with 'Tajiktransgaz' (the confirmed 50% "
                "co-owner of the operating JV alongside Owner1); neither current value is "
                "corroborated as an owner of Line D by any independent source found. (2) "
                "StartYear1=2022 is unsupported — no source corroborates it as a target or "
                "actual date; either source a current target or blank it rather than carry "
                "an apparently stale figure. Do not fabricate a ref. (3) PROCEDURAL: this "
                "row's CountriesOrAreas is 'Turkmenistan, Uzbekistan, Tajikistan, "
                "Kyrgyzstan, China'. Every cell on it is shared with four other country "
                "scopes, so it must be edited ONCE at whole-project level and the edit "
                "recorded where the next country's researcher will see it — the failure "
                "mode is exactly the one the 13-row exclusion exists to prevent, two "
                "batches staging contradictory records on the same cells with the last "
                "workbook pasted winning silently. Do not attempt to apportion the 966 km "
                "or 30 bcm/y to Uzbekistan: they are whole-project figures and no "
                "per-country spec is separable from this row.",
                "NOT A DUPLICATION QUESTION — recorded in this leg because it is a "
                "structural scope finding and this is the leg that carries those. It is "
                "legitimately in Uzbekistan's research scope: Kazakhstan is NOT among its "
                "five countries, so it is not one of the 13 rows the exclusion list "
                "removes, even though it is exactly the multi-country shape those 13 have. "
                "That makes it the batch's one cross-scope row and the reason the "
                "procedural warning above is stated as an action rather than a note. Its "
                "geometry is a 3-VERTEX schematic measuring 1053.92 km (Galkynysh "
                "62.3792,37.2726 -> Wuqia 73.9262,39.6957) against 966.00 km stated — for "
                "a 3-point straight-line trace across five countries that is schematic "
                "slack and not a length defect, and it is NOT evidence about routing. "
                "Status is 'shelved', which is the reason StartYear1=2022 reads as stale "
                "rather than wrong: a shelved project's last announced target ages into "
                "an unsourced figure, and blanking it is defensible where re-sourcing "
                "fails. The Kazakhstan batch left a related CA-China 1,833 km question "
                "open; it concerns different rows but the same programme, so resolve the "
                "ownership question consistently across both.",
                "escalate",
            ),
        },
    },
}


def main() -> None:
    gas = pd.read_csv(REPO / CSV, header=2, low_memory=False,
                      keep_default_na=False, na_values=[])
    gas["_sheet_row"] = gas.index + 4
    by_pid = {r["ProjectID"]: r for _, r in gas.iterrows()}

    excl = set((REPO / "batches/uzbekistan-gas/carried_from_kazakhstan.txt")
               .read_text().split())

    resolutions = []
    for key, cl in CLUSTERS.items():
        for pid, (ctype, rec, notes, severity) in cl["rows"].items():
            if pid in excl:
                raise SystemExit(f"{pid} is one of the 13 Kazakhstan-staged rows — "
                                 "out of scope for the research legs")
            row = by_pid.get(pid)
            if row is None:
                raise SystemExit(f"{pid} not found in {CSV} — snapshot drift, re-check")
            resolutions.append({
                "project_id": pid,
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
                "country": "Uzbekistan",
                "rows": len({r["project_id"] for r in resolutions}),
                "clusters": len(CLUSTERS),
                "excluded_carried_rows": len(excl),
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
                "Cluster-level adjudication of the duplicate/overlap questions raised "
                "row-by-row by uzbekistan-gas/ref-sweep-operating (deep sweep + status "
                "review + targeted ref-gap re-pass). Read-and-flag only; no edits staged. "
                "17 of the 18 in-scope rows are implicated — P2698 is deliberately not "
                "(no sibling, no corridor overlap; its open item is a ref-provenance "
                "defect already staged as a ref record). READ THIS FIRST: as in "
                "Kazakhstan, IDENTICAL OR NEAR-IDENTICAL DRAWN GEOMETRY IS NOT EVIDENCE "
                "OF DUPLICATION — the three Gazli-Kagan rows share a byte-identical "
                "105.34 km trace and an identical LengthEstimateKm 105.50, the three "
                "Mubarek-Zirabulak strings are ~131 km schematics a few hundred metres "
                "apart, and the two Mubarek-Kagan strings the same at ~99.5 km. For "
                "parallel threads on one right-of-way that is a convention, so every "
                "duplicate hypothesis is decided on attributes and sources. No cluster "
                "has the aggregate-vs-segment signature (a row whose trace is the UNION "
                "of others' DISTINCT traces). SIX of the eight clusters REFUTE a "
                "duplicate hypothesis (A, B, C, D, F, G), recorded in full so the next "
                "sweep does not re-raise them. Geometry earns its keep twice as a "
                "FALSIFIER instead: it sharpens cluster E, the batch's one live existence "
                "question, because P6964's trace is not on the Yangiyer-Ahangaran "
                "corridor at all (Yangiyer 178.2 km from its nearest vertex, start "
                "0.432 km from P4071's END, running east toward Andijan); and it REFUTES "
                "this batch's own P6937 finding of a material 35% length gap — the "
                "geometry is three parts, the MAINLINE alone is 282.3 km ending 20.0 km "
                "from Dushanbe against 300.00 km stated, and LengthEstimateKm 406.14 "
                "simply sums that mainline plus two spurs (85.5 + 38.1 km). A computed "
                "length is a claim about the geometry's extent, not about the pipeline: "
                "read the parts before believing the sum. Uzbekistan's structural motif "
                "is the one India and Kazakhstan share, a system-level figure restated on "
                "every string — Capacity 35.00 mill.Sm3/day on both P2290 and P3984, and "
                "the sheet's own cited source giving one diameter (1020x12 mm) for all "
                "three Mubarek-Zirabulak threads while the rows read 1020 / 1021 / 1022. "
                "That last is the batch's clearest defect: a segment index folded into a "
                "diameter cell, two one-cell fixes that must be applied together because "
                "the argument is the LADDER, not either row alone. Per-string Length / "
                "Diameter / Capacity are genuinely unpublished for clusters C and D, so "
                "UNRESOLVED there is the correct outcome — calibrate as Kazakhstan, not "
                "as India. Two dead-ref cautions apply throughout: "
                "utg.uz/ru/about/history/ is a genuine 404 whose Wayback capture "
                "(20260314231446) exists and was unreadable this session, so ADD the "
                "snapshot rather than dropping the ref; and liting.uz is a client-rendered "
                "SPA our tooling cannot read, which is an access limitation and never "
                "grounds to delete a once-working ref."
            ),
        },
        "resolutions": resolutions,
    }
    (OUT / "staged_resolutions.json").write_text(json.dumps(out, indent=1))
    print(f"wrote {len(resolutions)} validity records across {len(CLUSTERS)} clusters")
    for k, v in CLUSTERS.items():
        print(f"  {k}: {len(v['rows'])} row(s) — {v['title'][:96]}")
    print(f"  concern types: {ctypes}")
    print(f"  severity:      {sev}")


if __name__ == "__main__":
    main()
