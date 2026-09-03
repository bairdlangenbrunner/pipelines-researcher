#!/usr/bin/env python3
"""SUPERSEDED 2026-09-03 by scripts/build_redundancy.py (generic --staging/--clusters
emitter, same record schema; this CLUSTERS table still loads via `--clusters <this
file>`). Kept for the run record only.

Stage the Kazakhstan-gas redundancy adjudication (§3 `validity` leg, cluster-level).

The operating / in-dev / cancelled deep sweeps, the GulfPub + OSM recons and the
source survey each raised duplicate-and-overlap questions row-by-row. This pass
resolves them into ELEVEN structural clusters and stages one `__VALIDITY__` record per
implicated row carrying the CLUSTER-level recommendation. Detection lives in the prior
dirs; adjudication lives here. Read-and-flag only — never an edit (QC detects, Update
fixes).

    python batches/kazakhstan-gas/staging/redundancy/build_redundancy.py

**The one thing to know before reading any cluster below: in Kazakhstan gas, IDENTICAL
DRAWN GEOMETRY IS NOT EVIDENCE OF DUPLICATION.** Six multi-string systems here assign
the SAME corridor geojson to every string in the system — P0739/P5810 (1,270.28 km
byte-identical), P2289/P5695 (1,928.22), P2291/P5771 (2,895.01, with P5770 a proper
subset), P1124/P2299/P2300 (1,841.45), P5927/P5928 (138.79), P6830/P6831 (83.21). For
parallel strings sharing a right-of-way that is a defensible convention, not a defect,
so every duplicate hypothesis here has to be decided on ATTRIBUTES and SOURCES.

The one shape geometry *would* decide is the aggregate-vs-segment case, whose signature
is a row whose trace is the UNION of other rows that each have their own distinct trace.
Exactly one cluster looked like that (A): P3948's 137.85 km route = P5777's 58.22 +
P5783's 79.63, to the centimetre, and the sheet's own lengths agreed (17.80 + 60.70 +
70.80 = 149.30 against P3948's 149.10). **That reading is REFUTED, and the earlier
recommendation to fold P3948 is WITHDRAWN.** Two independent official Russian-language
documents describe the corridor as carrying separately-NAMED, separately-DIAMETERED
lines, and P3948 is one of them by name, diameter *and* length: Intergas Central Asia's
own environmental-permit filing states «Магистральный газопровод высокого давления
Ду 720 мм «Жанаозен - Жетыбай - Актау» протяженностью 149,1 км», and the Mangistau
regional development plan (item 116) enumerates «Жанаозен – Жетыбай – Актау» Ду 720 мм,
«КазГПЗ-КС «Жанаозен»» Ду 720 мм and «Жанаозен – Жетыбай – Актау» Ду 529/530 мм as one
joint capital-repair programme. So GEM's rows map 1:1 onto real physical lines — P3948 =
the 720 mm trunk (149.1 km), P5776 = the KazGPP–KS Zhanaozen feeder (720 mm, 17.8 km),
P5777 + P5783 = the 529/530 mm trunk split at Zhetybay (60.70 + 70.80 = 131.50 km),
P5789 = the fourth thread under construction. The 0.2 km arithmetic near-identity is a
COINCIDENCE of two parallel trunks of similar length plus a feeder, and the geometric
identity is what you would expect if the segment routes were digitized by cutting the
parent's trace — neither is evidence of a rollup. Cluster A therefore becomes a
refutation like the others, with three residual questions: why the 529/530 trunk measures
131.50 km against the 720 mm trunk's 149.10 km for nominally the same endpoints; the
4.54 bcm/y that Intergas states for the strings TOGETHER sitting on all four rows; and
whether «3-х ниток» in item 116 enumerates those three named lines (in which case GEM's
roman numerals I / II / III / III are correct, not mislabelled, since two rows numbered
III are the two stretches of the third line) or means three threads of the 720 mm line
alone (in which case GEM is missing parallel pipe). Do not resolve that on the numerals.

Kazakhstan's other structural motif is **capacity restated at system level on every
string** (clusters B, E, J) — the same defect India had with 107.00 MMSCMD on five HVJ
rows. And because the country has no line-wise register (see
`docs/reference/source_roster.md` → Kazakhstan), several length figures trace to the KMG
Annual Report, whose 2019/2020 and 2021 vintages differ materially on the same systems.
**Two vintages of one publisher are ONE origin**, so a row matching AR2020 is not
corroborated by AR2021 disagreeing with it — it is dated.

SEVEN of the eleven clusters REFUTE a duplicate hypothesis (A, C, D, E, H, I, J). That is
deliberate: an unrecorded refutation gets re-raised by the next sweep, and four of them
(A's 149.30-vs-149.10, E's identical 1,585 km, H's 302.6-vs-302.4, A's 70.8-vs-70.0) look
like textbook duplicates on the numbers alone.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

CSV = "data/GGIT_gas_snapshot_20260811.csv"
OO_CSV = "data/GEM_operators_owners_snapshot_20260811.csv"
OUT = Path(__file__).resolve().parent
REPO = OUT.parents[3]

ORDER_350 = "https://adilet.zan.kz/rus/docs/G23JVM00350"
KMG_AR2021 = ("https://ar2021.kmg.kz/pdf/ar/en/"
              "strategic-report_operating-review_gas-transportation-and-marketing.pdf")
KMG_AR2020 = ("https://ar2020.kmg.kz/pdf/ar/en/"
              "strategic-report_operating_gas-transportation.pdf")
ECOPORTAL_AKTAU = "https://ecoportal.kz/Public/PubHearings/LoadFile/182922"
MANGISTAU_PLAN = "https://adilet.zan.kz/rus/docs/P2100000784#z12"

# (concern_type, recommendation, researcher_notes, severity)
CLUSTERS: dict[str, dict] = {
    # ---------------------------------------------------------------- A
    "A": {
        "title": "Zhanaozen(Uzen)-Zhetybay-Aktau: the ~149 km 'P3948 is an aggregate of "
                 "P5776 + P5777 + P5783' double count is REFUTED — two official sources "
                 "name P3948 as its own 720 mm / 149.1 km trunk parallel to the 529/530 mm "
                 "one; the fold recommendation is withdrawn",
        "refs": [ECOPORTAL_AKTAU, MANGISTAU_PLAN, KMG_AR2021],
        "rows": {
            "P3948": (
                "duplicate",
                "KEEP THIS ROW AS IT STANDS — do NOT fold it, and do not shorten it. An "
                "earlier pass of this same leg recommended folding P3948 into "
                "P5776 + P5777 + P5783 as a ~149 km double count; that recommendation is "
                "WITHDRAWN on the sourcing below, and this record exists so the next sweep "
                "does not re-raise it. Its name, diameter and length are all corroborated "
                "at high tier by two independent official sources and need no change. Two "
                "residual items, neither of them a duplication: (1) the 4.54 bcm/y that "
                "Intergas's 2023 AR states for the corridor's strings TOGETHER sits on all "
                "four rows — it belongs on PipelineNetworkGrouping, with per-row throughput "
                "or a blank + ResearcherNotes on each row (the 3.60 bcm/y that kt.kz 2008 "
                "and Neft i Gaz 2019 give is a separate open spec question, since Intergas "
                "dates the pre-repair figure at 2.68); (2) the 529/530 mm trunk measures "
                "131.50 km (P5777 60.70 + P5783 70.80) against this row's 149.10 km for "
                "nominally the same endpoints — establish what accounts for the ~18 km, "
                "because that difference is now a real spec question rather than the "
                "arithmetic of a rollup.",
                "MEASURED, THEN REFUTED — this is the reversal of an earlier verdict in "
                "this very leg, kept in full because the refuted reading is genuinely "
                "compelling on the numbers. What was measured is real and reproducible: "
                "P3948's own drawn route measures 137.85 km (Uzen 52.843,43.358 -> Aktau "
                "51.197,43.659) and is EXACTLY the concatenation of two other rows' "
                "traces — P5777 (Uzen-Zhetybay) 58.22 km + P5783 (Zhetybay-Aktau) "
                "79.63 km = 137.85, each lying 100% inside P3948's 2 km corridor. The "
                "sheet's length column appeared to say the same: P5776 17.80 + P5777 60.70 "
                "+ P5783 70.80 = 149.30 against P3948's 149.10, i.e. P3948 exceeding "
                "Uzen->Aktau (131.50 by its own segment rows) by almost exactly the "
                "17.80 km Kaz-GPP stub. WHAT REFUTES IT: two INDEPENDENT official "
                "Russian-language documents describe this corridor as carrying "
                "separately-NAMED, separately-DIAMETERED trunk lines, and P3948 is one of "
                "them by name, diameter AND length. Intergas Central Asia's own "
                "environmental-permit filing for its Aktau branch (ecoportal.kz "
                "public-hearings portal, 'Краткое нетехническое резюме' for МГ "
                "'Жанаозен-Актау' 2025-2030 — a PDF, so url_verifier's substring check is a "
                "documented false negative; read locally with pdftotext -layout) states "
                "verbatim: 'Магистральный газопровод высокого давления Ду 720 мм "
                "«Жанаозен - Жетыбай - Актау» протяженностью 149,1 км'. The Mangistau "
                "regional development plan item 116 states verbatim: 'Капитальный ремонт "
                "3-х ниток магистрального газопровода \"Жанаозен – Жетыбай – Актау\" "
                "Ду 720 мм, магистрального газопровода \"КазГПЗ-КС \"Жанаозен\" Ду 720 мм, "
                "магистрального газопровода \"Жанаозен – Жетыбай – Актау\" Ду 529/530 мм' "
                "(one joint repair programme, Q4 2022-Q2 2024). So GEM's rows map 1:1 onto "
                "real physical lines: P3948 = the 720 mm trunk at 149.1 km, P5776 = the "
                "KazGPP-KS Zhanaozen feeder (720 mm, 17.8 km), P5777 + P5783 = the "
                "529/530 mm trunk split at Zhetybay (530 mm on Zhanaozen-Zhetybay, 529 mm "
                "on Zhetybay-Aktau, per ecoportal's segment table), P5789 = the fourth "
                "thread under construction. An aggregate row would not have its own "
                "diameter class stated in an operator's permit filing at its own stated "
                "length. WHY THE EVIDENCE THAT LOOKED DECISIVE IS NOT: the 0.20 km "
                "near-identity is a coincidence of two parallel trunks of similar length "
                "plus a feeder, and the geometric identity is exactly what you get if the "
                "segment routes were digitized by CUTTING the parent's trace — the same "
                "shared-right-of-way convention six other Kazakh systems follow (see the "
                "top of this builder). Geometry cannot distinguish parallel strings here, "
                "and that cuts both ways. WHAT STAYS OPEN: (a) the 131.50-vs-149.10 km "
                "difference for nominally the same endpoints; (b) 4.54 bcm/y on all four "
                "rows; (c) whether '3-х ниток' enumerates the three named lines — in which "
                "case GEM's SegmentName numerals I / II / III / III are CORRECT rather than "
                "mislabelled, since the two rows numbered III are the two stretches of the "
                "third line — or means three threads of the 720 mm line ALONE, in which "
                "case GEM is missing parallel pipe. Both readings are grammatically "
                "available in the Russian and neither is settled here; do not decide it on "
                "the numerals. Either way P3948 is a real line, so the fold is withdrawn "
                "under both. It stays an escalation because a withdrawn structural "
                "recommendation is something Baird must see, not a silent edit.",
                "escalate",
            ),
            "P5776": (
                "spec",
                "KEEP — a distinct 720 mm feeder, not a segment of P3948 (which is itself "
                "no longer proposed for folding). Three open items of its own: (1) both "
                "official sources treat 'KazGPZ-KS Zhanaozen' as a separately-NAMED trunk "
                "pipeline rather than segment 'II' of Zhanaozen-Zhetybay-Aktau, so Update "
                "should reconsider the PipelineName/SegmentName framing; (2) it is the one "
                "operating Kazakh gas row with RouteAccuracy='no route' and "
                "RouteType='Not mapped (but could be...)', so it is the natural §8 "
                "route-creation candidate for this system (Kazakh GPP compressor station -> "
                "Zhanaozen/Uzen, ~17.8 km, its start point already pinned by P3948's own "
                "trace start); (3) its 4.54 bcm/y is the three-string system figure, not "
                "this 17.8 km stub's throughput.",
                "EXISTENCE CONFIRMED at high tier by two independent official sources (the "
                "Mangistau regional development plan and Intergas Central Asia's 2023 "
                "Annual Report), both of which name it as its own trunk line. SegmentName "
                "'II Kaz GPP-KS - Zhanaozen' — a thread number attached to an endpoint pair "
                "covering only the upstream feeder, which is why the numeral scheme reads "
                "as suspect even where it may be correct (see P3948). Its missing geometry "
                "is also why P3948's trace is 11 km "
                "shorter than P3948's own stated length. Its Operator is separately "
                "questioned: the sheet says KazTransGaz Aimak, while Intergas claims this "
                "line as its own (flagged in the operating leg, not overwritten).",
                "flag",
            ),
            "P5777": (
                "spec",
                "KEEP. One open item: 4.54 bcm/y is the THREE-STRING SYSTEM figure restated "
                "on this row (Intergas AR 2023, 2.68 -> 4.54 post-repair) — it needs a "
                "per-row throughput, or a blank with the system figure explained in "
                "ResearcherNotes. Its own length, start year and cost are the "
                "best-corroborated in the cluster and need no change.",
                "THE UPSTREAM HALF OF THE 529/530 mm TRUNK. Three independent "
                "Russian-language sources "
                "(kt.kz 2008, Osmanov/Klimov 2019, Intergas's own AR 2023) match its exact "
                "stretch, ~60 km against the sheet's 60.70, the 2008 start year and the "
                "$30M cost, and the ecoportal permit filing puts 530 mm on precisely this "
                "Zhanaozen-Zhetybay stretch — so it is a real consecutive piece of a real "
                "line that runs PARALLEL to P3948's 720 mm trunk, not a slice of it. The "
                "same AR gives 4.54 bcm/y for the corridor's strings together, which "
                "is what makes the capacity a system figure rather than a copy. SegmentName "
                "'III Zhanaozen-Zhetybay'; 58.22 km drawn against 60.70 stated (within "
                "tolerance). Its trace concatenates with P5783's into P3948's — a "
                "digitization artifact of cutting the corridor trace, not evidence that "
                "P3948 is their sum (see P3948).",
                "info",
            ),
            "P5783": (
                "spec",
                "KEEP. Same system-capacity item as P5777, and its 70.80 km length and 1968 "
                "start year remain UNRESOLVED at segment level (unconfirmed, not "
                "contradicted). The sheet's 529 mm diameter is NOT a transcription slip: "
                "ecoportal's segment table puts 529 mm on precisely this Zhetybay-Aktau "
                "stretch and 530 mm on P5777's Zhanaozen-Zhetybay stretch, so the two "
                "figures are a real along-the-length change, and an earlier reading of "
                "529-vs-530 as one being a mistyping of the other is withdrawn.",
                "THE DOWNSTREAM HALF OF THE 529/530 mm TRUNK. SegmentName "
                "'III Zhetybay-Aktau' — the SECOND row numbered III, which under the "
                "three-named-lines reading is CORRECT rather than a mislabel (both stretches "
                "belong to the third line). 70.80 km "
                "on the sheet vs 79.63 km drawn. Its trace concatenates with P5777's into "
                "P3948's — a digitization artifact, not a rollup (see P3948). NOT a "
                "duplicate of P5784: that row is the separate "
                "Zhetybay-Kuryk branch, confirmed on its own 2020 procurement spec.",
                "info",
            ),
            "P5789": (
                "duplicate",
                "KEEP — thread IV is REAL and its existence is no longer in question, but "
                "three of its cells are. (1) Status: the in-dev leg recommends "
                "proposed -> construction on dated evidence (46 km of pipe laid as of "
                "2024-08-03, contractor named), so it should not still read 'proposed'. "
                "(2) LengthKnownKm and Capacity are both '--' while LengthMergedKm reads "
                "137.85 — a number this row does not own (see below); give it its own "
                "sourced length, but do not let 137.85 enter a total as thread IV's "
                "length. (3) RouteAccuracy 'medium' was inherited with the copied "
                "geometry, not earned — a re-grade, not a route problem, because the copied "
                "trace itself is now defensible (see below).",
                "IDENTITY AND GEOMETRY BOTH RESOLVED; THREE CELLS STILL OPEN. Existence is "
                "well "
                "corroborated in Russian-language press independent of GEM (Turan Times "
                "2023-02: construction of the 4th thread of the Zhanaozen-Aktau trunk line "
                "begins 2023; InAktau 2023 and 2024-08-03 tracking progress, 46 km "
                "installed, contractor TOO 'Trans Azia Konstrakshn'; Intergas Central "
                "Asia's own network list carries the line as 'Узень-Жетыбай-Актау'). It is "
                "specifically the NEW fourth thread, distinct from the 2023 capital repair "
                "of the three existing ones — so P5789 is neither a phantom nor a duplicate "
                "of P3948, and an earlier framing of it as a copied 'segment' is withdrawn. "
                "Its route file P5789.geojson is BYTE-IDENTICAL to "
                "P3948's — the same three vertices [52.84349,43.35762] -> "
                "[52.17066,43.54285] -> [51.19745,43.6588] — and that copy is LEGITIMATE: "
                "thread IV runs Uzen->Aktau along the same right-of-way the corridor trace "
                "describes, which is exactly the shared-right-of-way convention documented "
                "at the top of this builder (six systems do it). What the copy does NOT "
                "give it is a length or an accuracy grade of its own: the 137.85 km it "
                "yields is the corridor's length, and RouteAccuracy='medium' describes the "
                "drawing P3948 got. Contrast P5776, whose geojson exists but holds "
                "`geometry: null` — the honest placeholder for a row with no route of its "
                "own. Note also that GulfPub independently carries a Tenge-Aktau line as "
                "OPERATING at 152.89 km, which may be this corridor under another name.",
                "escalate",
            ),
            "P5784": (
                "duplicate",
                "KEEP BOTH — the Zhetybay-Kuryk branch is NOT a duplicate of P5783 "
                "Zhetybay-Aktau, despite 70.00 km against 70.80 km. No action from this "
                "cluster beyond the 529/530 mm diameter question noted on P5783.",
                "REFUTED on geometry. The two traces share only 3-5% of their length: "
                "both leave Zhetybay (52.171,43.543) but P5783 runs north-west to Aktau "
                "(51.197,43.659) while P5784 runs south-west to Kuryk (51.678,43.180), "
                "56.77 km drawn. Two different coastal destinations ~60 km apart. The "
                "matching lengths are a coincidence, and each is independently consistent "
                "with its own drawn route. Recorded so the next sweep does not re-raise "
                "it.",
                "info",
            ),
        },
    },
    # ---------------------------------------------------------------- B
    "B": {
        "title": "Central Asia-Center: one 60.20 bcm/y system capacity stamped on three "
                 "separate strings",
        "refs": [KMG_AR2021, KMG_AR2020],
        "rows": {
            "P2291": (
                "spec",
                "Replace the 60.20 bcm/y with this string's OWN throughput, or blank it "
                "and state the system figure in ResearcherNotes. Do not leave the same "
                "number on three rows. Also reconcile the length: 2,662.00 km on the "
                "sheet against 2,895.01 km drawn, and the drawn trace is shared "
                "byte-for-byte with P5771 (CAC-5).",
                "SYSTEM-CAPACITY RESTATEMENT, the same defect India carries with "
                "107.00 MMSCMD on five HVJ rows. CAC-2 (P2291), CAC-4 (P5770) and CAC-5 "
                "(P5771) all read exactly 60.20 bcm/y while CAC-3 (P2292) reads 5.00 — a "
                "value that cannot be each string's own capacity and cannot be summed. "
                "60.20 is close to the system's historical design throughput, so the "
                "reading is that one system figure was copied onto each string as it was "
                "entered. Summing the CAC rows as tracked therefore triple-counts "
                "~120 bcm/y of Kazakh transit capacity. KMG's own Annual Report gives "
                "Central Asia-Centre as ONE system (4,149.2 km in AR2021, 5,306 km in "
                "AR2019/2020 — a scope redefinition, and two vintages of one publisher "
                "are ONE origin, so neither corroborates the other). Note GEM does not "
                "carry CAC-1 at all, so the row set is not a complete decomposition "
                "either.",
                "escalate",
            ),
            "P5770": (
                "spec",
                "Same per-string capacity question as P2291. Additional length item: "
                "3,700.00 km on the sheet is the LONGEST figure of any CAC row and "
                "exceeds KMG AR2021's whole-system 4,149.2 km by 89% of it, while the "
                "drawn trace measures 2,222.22 km and is a proper SUBSET of P2291's "
                "corridor (100% of P5770 lies inside it). Verify against a "
                "string-specific source before keeping 3,700.",
                "CAC-4. The subset relationship means the drawn geometry cannot "
                "distinguish this string from CAC-2; the 3,700 km claim is unsupported by "
                "the route and by KMG.",
                "flag",
            ),
            "P5771": (
                "spec",
                "Same per-string capacity question. LengthKnownKm is blank ('--') while "
                "LengthMergedKm reads 2,895.01 from the drawn route — which is the SAME "
                "trace as P2291's. So this row's only length evidence is a corridor it "
                "shares with another row: it needs a string-specific length or an "
                "explicit note that none exists.",
                "CAC-5. Blank LengthKnownKm is honest; the risk is that the merged column "
                "makes a shared corridor look like a measured length for this string.",
                "flag",
            ),
            "P2292": (
                "spec",
                "No capacity action — 5.00 bcm/y is the one CAC row NOT carrying the "
                "system figure, and is named here as the contrast that proves the other "
                "three are restatements. Its own open item is length: 2,600.00 km on the "
                "sheet against 1,568.57 km drawn (a 1.66x route-integrity flag), and its "
                "trace shares only ~10-16% with P2291's.",
                "CAC-3. Also carries the do-not-re-flag from cluster C on diameter units.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- C
    "C": {
        "title": "Central Asia-China Lines A/B/C at 1,833 km each: NOT a triple count "
                 "(refuted, and the sheet is corroborated)",
        "refs": [ORDER_350],
        "rows": {
            "P2299": (
                "duplicate",
                "KEEP all three — Lines A, B and C are three physically separate parallel "
                "strings, and the identical 1,833 km is the shared transit length, not a "
                "copied value. No action from this cluster. Do NOT re-flag "
                "Diameter=42.00 with DiameterUnits='in' as 'inches in a millimetre "
                "column': 42in = 1,067 mm is correct for Lines A and B (Line C is "
                "1,219 mm, and GEM records that one in mm).",
                "REFUTED, and the row set is positively corroborated rather than merely "
                "not-disproved. Order of the Minister of Energy No.350 (29.09.2023) para "
                "44 describes the Kazakhstan-China gas pipeline as 'do 1300 km' with "
                "capacity 'do 55 mlrd m3/god'. GEM's three rows carry 15.00 + 15.00 + "
                "25.00 = 55.00 bcm/y — i.e. the three strings SUM to the system figure "
                "the regulator states, which is the opposite of the CAC pattern in "
                "cluster B where one system figure sits on each row. And the 1,833 km is "
                "consistent with the Kazakh 'up to 1,300 km' plus the ~530 km Uzbek "
                "section: it is the Turkmen-border-to-Khorgos transit length that all "
                "three strings share, which is why the three drawn traces are identical "
                "(1,841.45 km, 64.755,38.612 -> 80.441,44.069). Under this country's "
                "shared-corridor convention that identity is expected. An earlier flag on "
                "the 42.00/'in' pair is WITHDRAWN.",
                "info",
            ),
            "P2300": (
                "duplicate",
                "KEEP — see P2299. No action.",
                "Line B. Named here so the refutation is visible from every row it "
                "covers.",
                "info",
            ),
            "P1124": (
                "duplicate",
                "KEEP — see P2299. No action. Line C's 1,219 mm is the correctly-recorded "
                "larger diameter and is not in conflict with A/B's 42in.",
                "Line C. Same trace as A and B; capacity 25.00 is the increment that "
                "completes Order No.350's 55 bcm/y.",
                "info",
            ),
        },
    },
    # ---------------------------------------------------------------- D
    "D": {
        "title": "Bukhara-Ural I/II: two real strings, but II's length is a KMG "
                 "whole-system figure from a superseded vintage",
        "refs": [KMG_AR2021, KMG_AR2020],
        "rows": {
            "P5695": (
                "spec",
                "KEEP as a distinct string, but re-source the length. 2,382.00 km is "
                "EXACTLY KMG's AR2019/AR2020 figure for the WHOLE Bukhara-Ural system, "
                "which AR2021 restates as 1,567.8 km; the drawn corridor measures "
                "1,928.22 km and is shared byte-for-byte with P2289 (string I). So this "
                "row's length is a system total of a superseded vintage, sitting on one of "
                "two strings. Recommended: cite the vintage explicitly or replace with a "
                "string-specific figure. Note that AR2019/2020 and AR2021 are ONE origin "
                "(same publisher), so the disagreement dates the value — it does not give "
                "two independent sources to choose between.",
                "REFUTED as a duplicate of P2289 — Bukhara-Ural is genuinely a two-string "
                "system and both rows carry the same 1,000/1,020 mm and 21.00 bcm/y, "
                "consistent with parallel strings on one right-of-way. What survives is a "
                "length-provenance defect plus the capacity-restatement pattern of "
                "cluster B (21.00 on both rows = one system figure twice). Endpoints "
                "differ correctly: I terminates in Chelyabinsk Oblast, II in Sverdlovsk "
                "Oblast, ~360 km further north, which is consistent with II being the "
                "longer string — but 2,382 - 2,200 = 182 km, not 360.",
                "flag",
            ),
            "P2289": (
                "spec",
                "KEEP. Its own open item is Owner: the cell reads '--' while P5695, the "
                "sibling string on the same corridor, reads 'Gazprom PJSC [100.%]'. One "
                "of the two is wrong; the operators/owners tab should carry the answer for "
                "both.",
                "String I, 2,200.00 km. Named here so the refutation and the shared-"
                "corridor convention are visible from both rows.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- E
    "E": {
        "title": "Bukhara-Tashkent-Bishkek-Almaty I/II both 1,585 km: parallel strings "
                 "(refuted), with the system length on each",
        "refs": [KMG_AR2021],
        "rows": {
            "P0739": (
                "spec",
                "KEEP BOTH — string I and string II of the BGR-TBA system are not one "
                "asset entered twice. The real item is that 1,585.00 km appears on BOTH "
                "rows: it is the system length, so tracked length for this corridor is "
                "double what exists. Recommended: keep the system figure on one row (or "
                "on PipelineNetworkGrouping) and give each string its own length, noting "
                "KMG AR2021 gives BGR-TBA + Gazli-Shymkent together as 1,903.4 km against "
                "AR2019/2020's 2,462 km.",
                "REFUTED as a duplicate: the two rows differ where two real strings should "
                "differ — StartYear1 1971 vs 1999, capacity 12.00 vs 3.90 bcm/y, and "
                "diameter sets 700/720/820/1000/1020 mm vs 720/1015 mm. A 1971 Soviet "
                "trunk plus a 1999 second string on the same route is a coherent history. "
                "The identical 1,270.28 km drawn trace is this country's shared-corridor "
                "convention (see the module docstring), not evidence of duplication — but "
                "note the drawn corridor is 315 km SHORTER than the 1,585 km both rows "
                "claim, so the length question is open on both sides.",
                "flag",
            ),
            "P5810": (
                "spec",
                "KEEP — see P0739. Same length-on-both-rows item. Its own additional "
                "flag: route integrity reports an endpoint outside the row's declared "
                "start/end countries.",
                "String II, commissioned 1999 at 3.90 bcm/y. Named here so the refutation "
                "is visible from both rows.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- F
    "F": {
        "title": "Bukhara-Ural CS14-Aktobe I and II: two byte-identical rows, "
                 "UNRESOLVED",
        "refs": [],
        "rows": {
            "P5927": (
                "duplicate",
                "UNRESOLVED — do not delete either row on this evidence, and do not keep "
                "both without a source. The two rows are identical in every attribute "
                "that could distinguish them: LengthKnownKm 158.00, Diameter 530 mm, "
                "Capacity 1.96 bcm/y, Owner QazaqGaz [100.%], RouteAccuracy high, both "
                "StartYear1 BLANK, and the same drawn trace. Recommended action is a "
                "targeted source hunt: does the CS14 -> Aktobe branch of Bukhara-Ural "
                "have two strings? If yes, string II needs its own StartYear1 and its own "
                "length/capacity; if no, retire one row. Until then treat this as one "
                "asset for any total.",
                "The ONLY cluster here where identical geometry is not immediately "
                "explained away by the shared-corridor convention, because unlike every "
                "other multi-string pair in this country these two rows do not differ on "
                "ANY attribute — not year, not capacity, not diameter. Kazakhstan has no "
                "line-wise public register (see source_roster.md), and QazaqGaz's IGO 2024 "
                "lists Intergas lines by NAME ONLY with no lengths, so the ordinary "
                "resolution path is closed. Two further facts to weigh: LengthKnownKm "
                "158.00 disagrees with the shared drawn route's 138.79 km on both rows "
                "identically, and 1.96 + 1.96 = 3.92 bcm/y of tracked capacity rests on "
                "the two-string reading being true. Blank StartYear1 on both is itself "
                "notable — these are 2 of only 3 operating Kazakh gas rows with no start "
                "year (the third is P6835).",
                "escalate",
            ),
            "P5928": (
                "duplicate",
                "UNRESOLVED — see P5927. Whichever row survives, the other's attributes "
                "carry no independent information.",
                "String II. Named here so the open question is visible from both rows.",
                "escalate",
            ),
        },
    },
    # ---------------------------------------------------------------- G
    "G": {
        "title": "Almaty-Bayserke-Talgar I/II: II is sourced, I is not",
        "refs": [],
        "rows": {
            "P6830": (
                "duplicate",
                "UNRESOLVED, leaning toward P6830 being the unsupported row. Its "
                "64.40 km, 2.40 bcm/y and BLANK diameter have no source found in this "
                "pass, while the sibling P6831's 62.40 km / 530 mm are corroborated by "
                "QazaqGaz's IGO 2024 Intergas description. Recommended: hunt for a source "
                "distinguishing a phase I from a phase II on this line before either "
                "retiring P6830 or filling its diameter — and note that filling the "
                "diameter from P6831 would be copying, not sourcing.",
                "The pair is suspicious on attributes rather than on geometry: the two "
                "rows share one drawn trace (83.21 km, 76.747,43.291 -> 77.229,43.298), "
                "which the shared-corridor convention permits, but that trace matches "
                "NEITHER stated length (64.40 / 62.40) and the capacities differ by 3.7x "
                "(2.40 vs 8.80 bcm/y) for what is described as the same short Almaty-area "
                "line. StartYear1 2014 vs 2024 is the one clean phase signal and is why "
                "this is not being called a duplicate outright. Different researchers "
                "entered the two rows.",
                "flag",
            ),
            "P6831": (
                "spec",
                "KEEP — this is the sourced row of the pair (62.40 km / 530 mm per "
                "QazaqGaz IGO 2024). Open item of its own: 8.80 bcm/y on a 530 mm, 62 km "
                "line is implausibly high and should be re-checked against the same "
                "source.",
                "String II, StartYear1 2024. Named here so the pair reads from both "
                "sides.",
                "flag",
            ),
        },
    },
    # ---------------------------------------------------------------- H
    "H": {
        "title": "Almaty-Taldykorgan 302.6 km vs Taldykorgan-Usharal 302.4 km: distinct "
                 "end-to-end lines (refuted), but the matching lengths are NOT a "
                 "coincidence after all",
        "refs": [],
        "rows": {
            "P3964": (
                "duplicate",
                "KEEP BOTH — they are two different pipelines, confirmed twice over (see "
                "notes). But the near-identical lengths are NOT innocent: the operating "
                "leg found two independent primary sources putting THIS line at 264.8 km, "
                "so P3964's 302.60 needs resolving, and 302.60 vs P5901's 302.40 is the "
                "likeliest explanation. Route to Update together with two endpoint "
                "questions this cluster raises on the same row: StartLocation reads "
                "'Almaty' while its RouteAccuracy='high' trace terminates at "
                "76.159,43.311, ~61 km WEST of Almaty city centre (near "
                "Uzynagash/Targap), which looks like a tie-in to the "
                "Bukhara-Tashkent-Bishkek-Almaty trunk rather than the city. Settle "
                "whether the 264.8 km figure and the 303.78 km trace are measuring the "
                "same span before changing either the length or the endpoint.",
                "DUPLICATE REFUTED TWICE, LENGTH CLAIM WITHDRAWN. The refutation is solid "
                "from two directions. On geometry the two traces share 1.5% / 0.8% of "
                "their length and meet end-to-end at Taldykorgan: P3964 runs Taldykorgan "
                "(78.373,45.027) south-west to 76.159,43.311, 303.78 km drawn; P5901 runs "
                "Taldykorgan (78.398,44.927) north-east to Usharal (80.977,46.101), "
                "300.25 km drawn — consecutive links of one corridor in opposite "
                "directions from a shared node, the classic shape that looks like a "
                "duplicate in a length column and cannot be one on a map. Independently, "
                "the operating leg found Intergas Central Asia's own asset list naming "
                "'MG Almaty-Taldykorgan' and 'MG Taldykorgan-Usharal' as two separate "
                "operated lines, and a Kazakhstanskaya Pravda piece framing "
                "Taldykorgan-Usharal as the NEXT project after Almaty-Taldykorgan was "
                "already built. Status differs correctly too (operating 2017 vs "
                "construction 2025). WITHDRAWN: this cluster previously said GulfPub's "
                "263.93 km was the outlier because GEM's own trace measures 303.78 km. "
                "That was wrong on method — a GEM-drawn route is not an independent source "
                "— and wrong on the evidence: KazTAG (2012-09-29, quoting the implementing "
                "company TOO KATEK) and Kazakhstanskaya Pravda (2018-04-02) both give "
                "264.8 km, six years and two institutions apart, and GulfPub's 263.93 km "
                "agrees with them to within 1 km while separately putting "
                "Taldykorgan-Usharal at 302.56 km. Three sources at ~264 km against one "
                "in-house drawing at 303.78 km. The 39 km gap is roughly the westward run "
                "from Almaty to that 76.159,43.311 terminus, so a scope/endpoint "
                "difference is a live alternative to a copied value — which is exactly why "
                "this goes to Update rather than getting decided here.",
                "flag",
            ),
            "P5901": (
                "duplicate",
                "KEEP — see P3964. Two open items of its own, neither about redundancy: "
                "status timing (Status=construction with StartYear1=2025, now past — the "
                "in-dev leg recommends construction -> operating), and its 302.40 km is "
                "the value P3964's 302.60 most likely got copied from, so leave it alone "
                "while P3964's length is resolved rather than 'harmonising' the two.",
                "Taldykorgan-Usharal, the north-east continuation, 300.25 km drawn against "
                "302.40 stated and independently matched by GulfPub at 302.56 km — i.e. "
                "THIS row's length is the well-supported one of the pair. Named here so "
                "the refutation, and the direction of the suspected copy, are visible from "
                "both rows.",
                "info",
            ),
        },
    },
    # ---------------------------------------------------------------- I
    "I": {
        "title": "Okarem-Beyneu vs Beyneu-Zhanaozen II: distinct lines (refuted), but "
                 "the second is filed under the first's name",
        "refs": [],
        "rows": {
            "P5772": (
                "classification",
                "KEEP as a distinct pipeline, but fix its identity: PipelineName reads "
                "'Okarem-Beyneu Gas Pipeline' while SegmentName, geometry and endpoints "
                "are all Beyneu-Zhanaozen. Recommended: give it its own PipelineName "
                "(Beyneu-Zhanaozen) and keep the Okarem-Beyneu relationship, if any, in "
                "PipelineNetworkGrouping — which already reads 'CAC Gas Pipeline System' "
                "for this row, a third and different parent claim.",
                "REFUTED as a duplicate of P2492. The two traces share only 3% / 10% of "
                "their length and join at Beyneu: P2492 runs Okarem (53.867,37.803) north "
                "to Beyneu (55.246,45.309), 1,009.71 km drawn against 999.00 stated; "
                "P5772 runs Beyneu (55.234,45.311) south-west to Zhanaozen "
                "(52.878,43.365), 286.47 km drawn against 308.00 stated. Two different "
                "lines meeting at a node, both route-supported. What is wrong is purely "
                "nominal — and it matters, because a row named for the wrong parent is "
                "how aggregate-vs-segment double counts get created in the "
                "first place, and how they get wrongly INFERRED later (cluster A). Note "
                "also this row is one of the country's two "
                "'very low (straight line/schematic)' operating routes.",
                "flag",
            ),
            "P2492": (
                "duplicate",
                "KEEP — see P5772. No action from this cluster.",
                "Okarem-Beyneu proper. Named here so the refutation reads from both "
                "rows.",
                "info",
            ),
        },
    },
    # ---------------------------------------------------------------- J
    "J": {
        "title": "Makat-North Caucasus and its looping line: a real loop (refuted), with "
                 "capacity possibly restated rather than incremental",
        "refs": [],
        "rows": {
            "P3999": (
                "spec",
                "KEEP as a distinct row — a 130 km loop IS new physical pipe, so the "
                "expansion rule (LengthKnown=0, Diameter blank) does NOT apply here. The "
                "open item is capacity: 13.15 bcm/y on the loop against 21.90 on the "
                "944 km parent. If 13.15 is the post-loop system throughput it is a "
                "restatement and double-counts; if it is the loop's own increment it "
                "should be stated as such in ResearcherNotes. Resolve before any capacity "
                "total is computed for Kazakhstan.",
                "REFUTED as a duplicate: the loop is real and correctly modelled as its "
                "own row. Geometry confirms the relationship rather than an identity — "
                "35.5% of P3999's 118.18 km drawn trace lies inside P1476's corridor "
                "(both in Atyrau, 53.344,47.677 -> 51.850,47.352), which is what a "
                "partial loop along a trunk should look like, and only 5.1% of the parent "
                "lies inside the loop. Diameters are consistent with a loop of a larger "
                "trunk (1,020 mm against 1,200/1,400/1,420 mm). The capacity question is "
                "the same family as cluster B: one system figure appearing where an "
                "increment belongs.",
                "flag",
            ),
            "P1476": (
                "spec",
                "KEEP. Named here for the capacity-additivity question only — 21.90 "
                "bcm/y plus the loop's 13.15 needs an explicit reading before either is "
                "summed.",
                "Makat-North Caucasus trunk, 944.00 km stated / 980.22 km drawn. Owner "
                "Gazprom PJSC [100.%] on the parent against 'Gazprom PJSC; QazaqGaz' on "
                "the loop is a second, smaller inconsistency worth resolving in the same "
                "pass.",
                "info",
            ),
        },
    },
    # ---------------------------------------------------------------- K
    "K": {
        "title": "Soyuz filed under the Brotherhood pipeline system",
        "refs": [KMG_AR2021, KMG_AR2020],
        "rows": {
            "P0761": (
                "classification",
                "Fix the parenting: PipelineNetworkGrouping reads 'Brotherhood pipeline "
                "system' but Soyuz (Orenburg-Uzhhorod) is a separate 1975-80 export "
                "system from Bratstvo/Brotherhood, which predates it and follows a "
                "different route. Recommended: blank the grouping or set it to a Soyuz/"
                "Orenburg-Uzhhorod grouping. Two related items on the same row: (1) "
                "Status=mothballed with ShelvedCancelledType BLANK and no shelved or "
                "cancelled year — a mothballed row needs the type set (the vocab is "
                "lowercase inferred/confirmed) and a date — the cancelled-review leg "
                "staged 'confirmed' / 2022 off the Sokhranivka transit halt, apply that "
                "rather than re-researching it; (2) LengthKnownKm 2,750.00 needs NO "
                "change — see the notes.",
                "CLASSIFICATION, not duplication — nothing suggests Soyuz duplicates "
                "another GEM row; the grouping is simply wrong, and a wrong grouping is "
                "how segments and parents get conflated. Brotherhood/Bratstvo is a "
                "separate, parallel Urengoy-origin export line. **The length worry is "
                "RESOLVED and withdrawn:** the cancelled-review leg established with "
                "independent RU+EN sources that 2,750 km is correctly the whole "
                "Orenburg->Uralsk->Aleksandrov Gai->Novopskov->Uzhhorod system, which is "
                "what this multi-country row models (the Kazakh section via Uralsk is "
                "~300 km of it). KMG's 805 / 1,147 km is a DIFFERENT, Kazakhstan-only "
                "two-pipeline accounting, not a smaller estimate of the same thing — so "
                "the two figures never conflicted. Owner spanning three national operators "
                "is consistent with the full-system reading. The one live spec item from "
                "that leg is capacity: four independent sources give ~26 / 26.1 bcm/y "
                "against the sheet's 25.20.",
                "flag",
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
                "country": "Kazakhstan",
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
                "row-by-row by kazakhstan-gas/{ref-sweep-operating,annual,"
                "cancelled-review}, the GulfPub + OSM recons and the source survey. "
                "Read-and-flag only; no edits staged. READ THIS FIRST: in Kazakhstan gas "
                "IDENTICAL DRAWN GEOMETRY IS NOT EVIDENCE OF DUPLICATION — six "
                "multi-string systems share one corridor geojson across all their strings "
                "(P0739/P5810, P2289/P5695, P2291/P5771 with P5770 a subset, "
                "P1124/P2299/P2300, P5927/P5928, P6830/P6831), which is a defensible "
                "convention for parallel strings on one right-of-way. What geometry DOES "
                "decide is the aggregate-vs-segment double count, and exactly one cluster "
                "had that signature: cluster A, where P3948's 137.85 km trace is the "
                "exact concatenation of P5777's 58.22 km and P5783's 79.63 km. That "
                "double count is now REFUTED and the recommendation to fold P3948 is "
                "WITHDRAWN: two independent official sources (Intergas's own "
                "environmental-permit filing on ecoportal.kz and the Mangistau regional "
                "development plan, item 116) name P3948 as its own 720 mm / 149.1 km trunk "
                "running parallel to a separately-named 529/530 mm trunk (P5777 + P5783) "
                "and a 720 mm feeder (P5776), so the rows map 1:1 onto real lines and the "
                "geometric identity is a digitization artifact of cutting the corridor "
                "trace. The earlier reading that GEM was MISSING ~280 km of parallel pipe "
                "is also withdrawn, though whether '3-х ниток' counts the three named lines "
                "or three threads of the 720 mm line alone is left open. SEVEN of "
                "the eleven clusters REFUTE a duplicate hypothesis (A, C, D, E, H, I, J) "
                "— recorded deliberately so the next sweep does not "
                "re-raise them; C additionally CORROBORATES the sheet (Order No.350's "
                "55 bcm/y = 15+15+25 across Lines A/B/C) and H refutes a GulfPub finding "
                "in GEM's favour. Kazakhstan's other motif is capacity restated at system "
                "level on every string (B, D, E, J), the same defect India carries with "
                "107.00 MMSCMD on five HVJ rows. Because the country has no line-wise "
                "public register, several lengths trace to the KMG Annual Report, whose "
                "2019/2020 and 2021 vintages differ materially — TWO VINTAGES OF ONE "
                "PUBLISHER ARE ONE ORIGIN, so a row matching AR2020 is dated, not "
                "corroborated."
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
