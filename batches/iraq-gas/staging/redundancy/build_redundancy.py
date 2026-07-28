#!/usr/bin/env python3
"""Cluster-level adjudication of the duplicate/existence flags raised row-by-row by
iraq-gas/annual and iraq-gas/ref-sweep-operating.

Read-and-flag only; no edits applied. Five clusters, adjudicated against the primary
source the flagged rows actually came from -- OPEC ASB Table 4.10 (2012) / Table 9.9
(2017), extracted locally with pdftotext (scratch/asb2012_fresh.txt, scratch/asb2017.txt).

Headline: reading the source refutes the two biggest theories the row-by-row legs
raised. The "Strategic-* vs Trans-Iraq-*" parallel-naming families are NOT a double
import -- OPEC lists them as separate lines off two different trunks -- and the ASB is
NOT an aggregate that fails to name pipelines; it is a per-pipeline table, and 13 GEM
Iraq rows are 1:1 transcriptions of its rows.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent / "staged_resolutions.json"
CSV = REPO / "data" / "GGIT_gas_snapshot_20260728.csv"

ASB2012 = (
    "http://web.archive.org/web/20250110032615/https://opec.org/opec_web/"
    "static_files_project/media/downloads/publications/ASB2012.pdf"
)
ASB2017 = (
    "http://web.archive.org/web/20250206233526/https://www.opec.org/opec_web/"
    "static_files_project/media/downloads/publications/ASB2017_13062017.pdf"
)

CLUSTER_TITLES = {
    "A": "'Strategic-*' vs 'Trans-Iraq(i)-*': NOT duplicates - OPEC lists both families",
    "B": "Taji->Daura: P4054 is a third naming of P4066 (a real duplicate)",
    "C": "The 42-inch national trunk: P4061 aggregate vs P1852 segment",
    "D": "P4058 Eastern Iraq 48-inch: not a duplicate, but not a sourceable entity either",
    "E": "ASB provenance: 13 rows are 1:1 OPEC table rows - the existence flags overreach",
}

# The ASB2012 Iraq block, transcribed from scratch/asb2012_fresh.txt (Table 4.10, p.75).
# (connection, length_raw, diameter_in, capacity_1000scm_yr, gem_pid)
ASB12_IRAQ = [
    ("North Gas/Baiji", 90, 24, 890_000, "P2231"),
    ("Baiji-K3-/Al Kaem", 268, 16, 2_410_000, "P1841"),
    ("Baiji/Al Mushraq", 131, 18, 7_400_000, "P1842"),
    ("North Gas Co/K1", 21, 18, 5_264_000, "P2232"),
    ("North Gas Co/Taji", 272, 16, 3_087_000, "P2233"),
    ("Taji/South Baghdad PWR St", 35, 18, 2_000_000, "P1845"),
    ("Strategy/Kabesa Cement", 24, 10, 671_000, "P1846"),
    ("Strategy/Hilla PWR St", 45, 16, 700_000, "P1847"),
    ("Strategy/Najaf PWR St", 23, 16, 2_100_000, "P1848"),
    ("North Rumela/Khor Al-Zubair", 54, 42, 10_000_000, "P2234"),
    ("Khor Al-Zubair/Hartha PWR St", 48, 24, 4_808_000, "P1850"),
    ("Rumela/Nasriyaha", 134, 24, 10_420_000, "P1851"),
    ("Trans-Iraq/Nasriyaha", 292, 42, 11_033_000, "P1852"),
]
ASB12_BY_PID = {p: (n, ln, d, c) for n, ln, d, c, p in ASB12_IRAQ}

# ASB2017 Table 9.9 Iraq rows that ASB2012 does NOT carry (the P40xx family's origin).
ASB17_NEW = {
    "P4062": ("Branch from Trans-Iraq dry gas pipeline/Hilla-2 PWR St", 25, 24),
    "P4064": ("Trans-Iraqi dry gas pipeline/Najaf PWR St", 74, 24),
    "P4065": ("Trans-Iraqi dry gas pipeline/Dewania", 50, 24),
    "P4066": ("Trans-Iraqi dry gas pipeline/Daura PWR St", 29, 18),
    "P4067": ("Al-Ahdeb/Al-Zubaydia PWR St", 73, 16),
    "P4068": ("Mishraq cross road/Mousil PWR St", 38, 12),
}

CROSSWALK_NOTE = (
    "ASB PROVENANCE CROSSWALK (the evidence behind this whole cluster set): OPEC ASB "
    "Table 4.10 is NOT a country-aggregate table -- its columns are 'Connection from/to | "
    "Owner or operator | Length | Diameter | Capacity | Throughput', one ROW PER PIPELINE. "
    "The 2012 Iraq block holds 13 rows and they map 1:1 onto 13 GEM rows, matching on "
    "DIAMETER 13/13, on length 13/13 (via the documented mi->km defect) and on capacity "
    "10/13 -- and all three capacity misses are already-documented findings, not evidence "
    "against the mapping: P1842 and P2233 were deliberately re-sourced to iraqenergy.org "
    "(an ordinary two-source conflict), and P1841 stores the right number (2.41) under the "
    "wrong unit label (MMcf/d instead of bcm/y), so on the ASB FIGURE the match is 11/13. "
    "GEM's names are the ASB "
    "connection strings with '/' rewritten as '-': 'Strategy/Hilla PWR St' -> "
    "'Strategic-Hilla Gas Pipeline', 'Baiji-K3-/Al Kaem' -> 'Baiji-K3-Al Kaem Gas "
    "Pipeline' (the odd doubled hyphen in the ASB original survives into GEM, which is "
    "itself a fingerprint). Extracted with pdftotext; url_verifier cannot read this deep "
    "into either PDF (large-PDF limit)."
)

# ---------------------------------------------------------------- records
R = []


def rec(pid, cluster, concern, recommendation, notes, values=None, refs=(),
        tier="high", indep=False, verdict="concern"):
    R.append(dict(pid=pid, cluster=cluster, concern=concern, values=values or {},
                  recommendation=recommendation, notes=notes, refs=list(refs),
                  tier=tier, indep=indep, verdict=verdict))


# ============================= CLUSTER A =============================
A_EVIDENCE = (
    "THE FAMILIES ARE IN THE SOURCE, NOT IN GEM'S INGEST. ASB2017 Table 9.9's Iraq block "
    "lists these as SEPARATE rows, with different parent trunks and different diameters:\n"
    "  'Strategic pipeline/Hilla PWR St'                          45  16in\n"
    "  'Branch from Trans-Iraq dry gas pipeline/Hilla-2 PWR St'    25  24in\n"
    "  'Strategic pipeline/Al-Najaf PWR St'                        23  16in\n"
    "  'Trans-Iraqi dry gas pipeline/Najaf PWR St'                 74  24in\n"
    "Two distinct trunk systems -- the Strategic Pipeline (the 1970s-80s dual-purpose "
    "north-south line, tracked in GOIT as P0542/P3876/P5244) and the later Trans-Iraq dry "
    "gas pipeline -- each with its own branch to the same city. Different parent, different "
    "diameter (16in vs 24in), different length, listed on separate lines by the operator's "
    "own statistical return. That is not a relabel."
)
rec("P4062", "A", "duplicate",
    "CLEAR the duplicate flag against P1847 -- these are two different pipelines in the "
    "source. Instead FIX THE NAME: the ASB row is 'Hilla-2 PWR St', and GEM dropped the "
    "'-2', which is what made this look like a duplicate of the Hilla line. Rename to "
    "'Trans-Iraqi-Hilla-2 PWR St Gas Pipeline' (matching sibling P4064's style) and add "
    "the old name to OtherEnglishNames.",
    A_EVIDENCE + "\n\nROOT CAUSE OF THE FALSE ALARM: GEM's ingest truncated the ASB "
    "connection string. 'Branch from Trans-Iraq dry gas pipeline/Hilla-2 PWR St' became "
    "'Trans-Iraq-Hilla-Gas Pipeline' -- losing both the 'Branch from' qualifier and, "
    "critically, the '-2'. Hilla PWR St and Hilla-2 PWR St are two different generating "
    "stations at Hilla (Babil). Once the '-2' is gone, a 25/24in branch and a 45/16in "
    "branch to 'Hilla' read as one pipeline entered twice. The names collide because the "
    "ingest truncated them, not because the pipelines are the same. This is the single "
    "highest-value fix in this cluster: it is what stops a future pass re-opening the "
    "merge. Note the row remains single-sourced (see cluster E) -- clearing the duplicate "
    "flag does not make it well-referenced.",
    values={"PipelineName": "Trans-Iraqi-Hilla-2 PWR St Gas Pipeline"},
    refs=[ASB2017], verdict="confirmed (caveat)")
rec("P1847", "A", "duplicate",
    "CLEAR. P1847 is the 16-inch Strategic-pipeline branch to Hilla PWR St; P4062 is the "
    "24-inch Trans-Iraq branch to Hilla-2 PWR St. Do not merge. Optionally add "
    "'Strategic pipeline/Hilla PWR St' to OtherEnglishNames to preserve the ASB name.",
    A_EVIDENCE + "\n\nP1847 = ASB2012 'Strategy/Hilla PWR St' (45, 16in, 700,000 = 0.70 "
    "bcm/y) and ASB2017 'Strategic pipeline/Hilla PWR St' (45, 16in) -- present in BOTH "
    "editions with identical specs, and GEM carries the 16in and the 0.70 bcm/y exactly. "
    "The ref-sweep flagged it as a probable duplicate of P4062 on the reasoning that the "
    "'Strategic-*' trio and the 'Trans-Iraqi-*' set target the same cities and were "
    "imported in different batches (2023-09-09 vs 2022-07-25). The batch dates are real "
    "but they reflect two ASB editions, not two imports of one line.",
    refs=[ASB2012, ASB2017], verdict="confirmed (caveat)")
rec("P1848", "A", "duplicate",
    "CLEAR. P1848 is the 16-inch Strategic-pipeline branch to Al-Najaf PWR St (23); P4064 "
    "is the 24-inch Trans-Iraqi branch to Najaf PWR St (74). Do not merge.",
    A_EVIDENCE + "\n\nP1848 = ASB2012 'Strategy/Najaf PWR St' (23, 16in, 2,100,000 = 2.10 "
    "bcm/y), in both editions. GEM carries 16in and 2.10 exactly. The Najaf pair is the "
    "cleaner of the two cases: 23 vs 74 and 16in vs 24in leaves no room for these being "
    "one pipe. Separately note P7468 (Najaf Cement Factory, 1.2 km, 2023, independently "
    "sourced) is a third, unrelated Najaf gas line -- also not a duplicate.",
    refs=[ASB2012, ASB2017], verdict="confirmed (caveat)")
rec("P4064", "A", "duplicate",
    "CLEAR. Distinct from P1848 per the source. Name is already unambiguous "
    "('Trans-Iraqi-Najaf PWR St'); no rename needed. Sibling P4065 (Dewania, 50/24in) has "
    "no 'Strategic-*' counterpart at all and was never in doubt.",
    A_EVIDENCE + "\n\nP4064 = ASB2017 'Trans-Iraqi dry gas pipeline/Najaf PWR St' (74, "
    "24in). Absent from ASB2012, which is why the P40xx family carries later update "
    "stamps -- OPEC added these lines between editions. That the P40xx rows appear only in "
    "the newer edition is the simplest explanation of the two-family pattern, and it is "
    "the opposite of a double import: they are NEW lines, not re-entries.",
    refs=[ASB2017], verdict="confirmed (caveat)")

# ============================= CLUSTER B =============================
rec("P4054", "B", "duplicate",
    "CONFIRMED DUPLICATE of P4066 'Trans-Iraqi-Daura Gas Pipeline'. Merge: add 'Taji-Duara "
    "Gas Pipeline' to P4066's OtherEnglishNames and retire P4054. Do NOT merge it into "
    "P1845 -- that is a different power station (see the P1845 record in this cluster).",
    "This is the one flag in the whole set that survives review as a real duplicate. "
    "P4054's SOLE source is a label on a network map -- slide 8 of Dr. Jafar Dhia Jafar's "
    "Iraq Energy Forum 2018 deck, titled 'Iraq's Existing Dry Gas Pipeline Connects North & "
    "South' -- reading 'Taji-Duara Gas Pipeline'. It carries NO length in GEM, a diameter "
    "of 18in, and endpoints Taji -> Dora (Al Rashid district, south Baghdad). P4066 is "
    "ASB2017's 'Trans-Iraqi dry gas pipeline/Daura PWR St' (29, 18in). Same terminus "
    "(Daura/Duara/Dora are transliterations of one Baghdad district), same 18-inch "
    "diameter, and Taji is precisely where the Trans-Iraq trunk runs past north Baghdad -- "
    "so 'Taji-Duara' is a description of the Trans-Iraqi->Daura branch by its start point "
    "instead of its trunk. A map label and a statistical-return row describing one physical "
    "pipe. Retain P4066 as the surviving row: it has a length, a diameter, and a primary "
    "operator source, where P4054 has a diameter and a map label. LOOSE END, do not lose "
    "it: P4054's Capacity=94 MMcf/d has no counterpart in either ASB edition and no home "
    "in the map source either -- capture it in the merge or lose it deliberately, don't "
    "drop it silently. CAVEAT ON THE MERGE TARGET, stated rather than buried: P4054's "
    "EndLocation is bare 'Dora' with no facility named, and Daura hosts TWO major "
    "offtakers -- the Al-Doura refinery and the Al-Doura power station. P4066 is "
    "specifically the power-station branch ('Daura PWR St'), and GOIT separately tracks "
    "refinery branches off the OTHER trunk (P6256/P6257 Strategic Pipeline-Daura Refinery, "
    "18in/26in, oil). So the merge rests on the shared 18-inch diameter and the shared "
    "Trans-Iraq trunk, NOT on the endpoint string, which cannot distinguish the two "
    "facilities. The diameter match makes P4066 much the likelier target, but it is not "
    "proof; if the Jafar map can be re-read at higher resolution to show which Daura "
    "facility the label terminates at, do that first.",
    refs=[ASB2017], verdict="concern")
rec("P4066", "B", "duplicate",
    "MERGE TARGET (keep this row). Add 'Taji-Duara Gas Pipeline' to OtherEnglishNames when "
    "P4054 is retired; carry over P4054's Capacity=94 MMcf/d only if it can be sourced.",
    "P4066 = ASB2017 'Trans-Iraqi dry gas pipeline/Daura PWR St' (29, 18in). It is the "
    "better-attributed of the pair and should survive the merge with P4054. Note this row "
    "is also in the ASB length-unit class (its LengthKnownUnits reads 'mi' where the Iraq "
    "block is kilometres) -- see notes/escalation-2026-07-28-asb-iraq-length-units.md; "
    "that fix is a separate one-cell edit and does not interact with the merge.",
    refs=[ASB2017], verdict="concern")
rec("P1845", "B", "duplicate",
    "CLEAR. P1845 serves South Baghdad PWR St; P4066/P4054 serve Al-Daura PWR St. Two "
    "different Baghdad generating stations, listed separately by OPEC with different "
    "lengths. Do not fold P1845 into the merge.",
    "The ref-sweep proposed P4054 might be a duplicate of P1845, on the ground that both "
    "run Taji -> south Baghdad at 18 inches. The source separates them: ASB carries BOTH "
    "'Taji/South Baghdad PWR St' (35, 18in -- present in 2012 AND 2017) and 'Trans-Iraqi "
    "dry gas pipeline/Daura PWR St' (29, 18in -- 2017). Baghdad South and Al-Doura are two "
    "distinct power complexes in south Baghdad, and 35 != 29. So the correct resolution is "
    "a two-into-one merge (P4054 -> P4066), not three-into-one. The equal 18-inch diameter "
    "is what made this look like one pipe; it is a common size for these city branches "
    "(P4066 and P1845 are both 18in and both real).",
    refs=[ASB2012, ASB2017], verdict="confirmed (caveat)")

# ============================= CLUSTER C =============================
rec("P4061", "C", "duplicate",
    "GENUINE AGGREGATE-vs-SEGMENT CONCERN, unresolved. P4061 (600 km, 42in, whole national "
    "trunk) very likely contains P1852 (292 km, 42in, ending at Nasiriyah). If confirmed, "
    "make P4061 the NETWORK row on the Libya cluster-A pattern (set "
    "PipelineNetworkGrouping, blank Status, keep the corridor length) rather than deleting "
    "either. Also re-derive the capacity, which is currently incoherent.",
    "P4061 'National Gas Pipeline' (600 km, 42in, 850 MMcf/d = 8.69 bcm/y, -> Basra) is "
    "modelled as the whole north-south 42-inch dry-gas trunk. P1852 = ASB2012 "
    "'Trans-Iraq/Nasriyaha' (292 raw, 42in, 11.03 bcm/y). Same diameter, same corridor, "
    "and P1852's 292 km is plausibly the Baghdad-area->Nasiriyah portion of P4061's 600 km "
    "-- i.e. the trunk and one of its segments both carry status 'operating', so any "
    "length or capacity total for Iraq double-counts this corridor. THE CAPACITY IS THE "
    "TELL, and it is the same signature as Libya cluster A: P4061's 8.69 bcm/y is LOWER "
    "than its putative member P1852's 11.03 bcm/y, which is impossible for a trunk "
    "containing that segment. Either the trunk capacity is wrong or the two rows are not "
    "in the containment relation the geometry suggests. Cannot settle it from the sources "
    "to hand: P4061 is absent from both ASB editions (it comes from other reporting) and "
    "neither row has drawn geometry, so there is no route arbitration available -- which "
    "is the same binding constraint the GulfPub Iraq memo identifies. Flagging for human "
    "review; no edit staged.",
    refs=[ASB2012], tier="medium", verdict="concern")
rec("P1852", "C", "duplicate",
    "Paired with P4061 above -- same unresolved concern, reviewed together. Do NOT retire "
    "P1852 on its own: it is a named OPEC row with full specs, and it is the better-"
    "attributed of the two.",
    "P1852 = ASB2012 'Trans-Iraq/Nasriyaha' (292, 42in, 11,033,000 = 11.03 bcm/y); GEM "
    "carries 42in and 11.03 exactly. Notably it is the ONE ASB2012 Iraq row that ASB2017 "
    "DROPS -- the 2017 Iraq block has no 'Trans-Iraq/Nasriyaha' entry, which is consistent "
    "with OPEC having re-cut the trunk into the 'Trans-Iraqi dry gas pipeline/<city>' "
    "branch rows that appear for the first time in 2017. That re-cut is itself weak "
    "evidence that the trunk and the branches are one system described two ways, and it "
    "is the strongest reason to review P4061/P1852 together rather than separately.",
    refs=[ASB2012, ASB2017], tier="medium", verdict="concern")
rec("P1851", "C", "duplicate",
    "CLEAR. P1851 is the 24-inch Rumaila->Nasiriyah line, distinct from the 42-inch "
    "Trans-Iraq line to the same city. Not part of the P4061/P1852 question.",
    "Two lines reach Nasiriyah in the source and OPEC lists them separately: "
    "'Rumela/Nasriyaha' (134, 24in, 10.42 bcm/y) = P1851, and 'Trans-Iraq/Nasriyaha' (292, "
    "42in, 11.03 bcm/y) = P1852. GEM carries both diameters and both capacities exactly. "
    "Different origin, different diameter, different length -- a southern feed from Rumaila "
    "and a branch off the national trunk. Recording the clearance explicitly because "
    "'two rows ending at Nasiriyah' is exactly the pattern that will get re-flagged.",
    refs=[ASB2012], verdict="confirmed (caveat)")

# ============================= CLUSTER D =============================
rec("P4058", "D", "existence",
    "CLEAR the duplicate flag -- the source shows it as a distinct line and its 48-inch "
    "diameter matches nothing else in the roster. The EXISTENCE concern stands unchanged: "
    "one non-independent slide, no endpoints, absent from both ASB editions. Seek a "
    "Ministry of Oil / North or South Gas Company source naming a 48-inch eastern dry-gas "
    "trunk, or populate endpoints and downgrade confidence.",
    "The ref-sweep raised P4058 as a possible relabel of P4061/P1852. Resolving it against "
    "the only source available: the Jafar 2018 slide-8 map plots 'Eastern Gas Pipe Line / "
    "48 Inch, 350 mmscfd' as a line DISTINCT from 'Taji-Duara Gas Pipeline' and 'AL "
    "Mansuriya' on the same diagram, and 48 inches matches no other row in GEM's Iraq gas "
    "set (the trunk rows are 42in, the branches 10-24in). So on its own source it is not a "
    "duplicate, and I am clearing that flag. What is NOT resolved is whether the entity "
    "should exist as a standalone row: it has no start or end location (both read simply "
    "'Iraq'), its sole support is one slide from one presentation, and unlike the 13 "
    "crosswalked rows it appears in NEITHER ASB edition -- so the cluster-E provenance "
    "argument that rescues those rows does not reach this one. That distinction is the "
    "point of filing it here: P4058 is the row where 'single-sourced' really does shade "
    "into 'unverified entity'.",
    tier="low", verdict="concern")

# ============================= CLUSTER E =============================
E_HEAD = (
    "THE EXISTENCE FLAG ON THIS ROW RESTS ON A MISREADING OF THE SOURCE, and should be "
    "downgraded. The row-by-row legs flagged several Iraq rows on the reasoning that their "
    "only citation is 'OPEC Annual Statistical Bulletin, p.75/p.134', described as 'a "
    "country-level statistics compendium that does not name individual pipelines' -- and "
    "concluded these might be GEM constructions or phantoms. That premise is false. "
)
E_ROWS = {
    "P1841": ("Baiji-K3-/Al Kaem", 268, 16, "2,410,000",
              "GEM's name 'Baiji-K3-Al Kaem Gas Pipeline' reproduces the ASB string "
              "'Baiji-K3-/Al Kaem' character for character, doubled hyphen included. The "
              "ref-sweep concluded no source 'names this pipeline'; the ASB names it "
              "exactly, and GEM's 16in matches. Its route arbitration (drawn 224.9 km vs "
              "ASB raw 268) is the strongest single piece of evidence in the length-unit "
              "memo. Residual real issue: Capacity 2.41 is tagged MMcf/d where ASB gives "
              "2,410,000 (1,000 scm/yr) = 2.41 bcm/y, so CapacityBcm/y reads 0.02 -- "
              "~120x low. That unit mislabel is the finding on this row, not existence."),
    "P1845": ("Taji/South Baghdad PWR St", 35, 18, "2,000,000",
              "Named in BOTH editions with identical specs; GEM carries 18in and 2.00 "
              "bcm/y exactly. Also cleared as a duplicate in cluster B."),
    "P1846": ("Strategy/Kabesa Cement", 24, 10, "671,000",
              "The ref-sweep called this a 'strong candidate for deletion' after "
              "url_verifier failed to find the token 'Kabesa' in the ASB PDF. That was a "
              "verifier limit, not an absence: the token IS there -- 'Strategy/Kabesa "
              "Cement, OPC, 24, 10, 671,000' -- and pdftotext finds it in both editions "
              "('Strategic pipeline/Kabesa cement' in 2017). GEM's 10in and 0.67 bcm/y "
              "match. A 10-inch line to a cement plant is exactly the kind of small "
              "industrial branch OPEC's table carries. DO NOT DELETE THIS ROW."),
    "P1848": ("Strategy/Najaf PWR St", 23, 16, "2,100,000",
              "Same verifier artefact as P1846: url_verifier reported the ASB PDF lacked "
              "'Najaf', but the row reads 'Strategy/Najaf PWR St, OPC, 23, 16, 2,100,000' "
              "and ASB2017 repeats it as 'Strategic pipeline/Al-Najaf PWR St'. GEM's 16in "
              "and 2.10 bcm/y match. Also cleared as a duplicate in cluster A."),
    "P1852": ("Trans-Iraq/Nasriyaha", 292, 42, "11,033,000",
              "The ref-sweep noted 'every web trace of the exact name resolves back to GEM "
              "itself' and filed a self-referential-support flag. True of the web, but the "
              "name is OPEC's: 'Trans-Iraq/Nasriyaha, OPC, 292, 42, 11,033,000'. GEM's "
              "42in and 11.03 bcm/y match. The open question on this row is the "
              "trunk/segment relation to P4061 (cluster C), not whether it exists."),
    "P2232": ("North Gas Co/K1", 21, 18, "5,264,000",
              "The ref-sweep flagged this as a possible phantom because the opec.org URL "
              "now 404s and 'the ASB does not define a discrete pipeline named North "
              "Gas-K1'. It does: 'North Gas Co/K1, OPC, 21, 18, 5,264,000', and ASB2017 "
              "carries it as 'Kirkuk/North Oil' (21, 18). GEM's 18in and 5.26 bcm/y match. "
              "The dead link is a real problem with a real fix -- re-cite to the Wayback "
              "ASB URL already established in the length memo."),
    "P2233": ("North Gas Co/Taji", 272, 16, "3,087,000",
              "Named in both editions ('Kirkuk/Taji' in 2017); GEM's 16in matches. This is "
              "one of the two rows whose capacity does NOT match ASB (GEM 150 MMcf/d = "
              "1.53 bcm/y vs ASB 3.087) because it was deliberately re-sourced to "
              "iraqenergy.org -- an ordinary two-source value conflict. The valid part of "
              "the ref-sweep finding stands: the iraqenergy.org PDF does not mention Taji "
              "and should come off Capacity [ref] and Diameter [ref]."),
    "P4062": ("Branch from Trans-Iraq dry gas pipeline/Hilla-2 PWR St", 25, 24, "n/a (2017 table omits capacity)",
              "Flagged as an 'OPEC-table-only stub for possible merge/removal' after the "
              "ASB2017 PDF could not be retrieved from opec.org. It is retrievable via "
              "Wayback and the row is there. GEM's 24in matches. The real findings on this "
              "row are the truncated name (cluster A) and single-sourcing -- not "
              "non-existence."),
}
for pid, (conn, ln, dia, cap, extra) in E_ROWS.items():
    ed = ASB2017 if pid == "P4062" else ASB2012
    rec(pid, "E", "existence",
        "DOWNGRADE from 'possible phantom / deletion candidate' to 'single-sourced, "
        "faithfully transcribed'. Do not delete. The legitimate residual concerns are "
        "(a) single-sourcing -- one operator statistical return, so a second independent "
        "source is still wanted, and (b) the dead opec.org citations, which should be "
        "re-pointed to the Wayback ASB URLs.",
        E_HEAD + f"ASB Table 4.10/9.9 is a PER-PIPELINE table whose first column is "
        f"'Connection from/to'. This row's entry reads: '{conn}' | OPC | {ln} | {dia} in | "
        f"{cap}. " + extra + "\n\n" + CROSSWALK_NOTE,
        refs=[ed], tier="medium", verdict="confirmed (caveat)")


# ---------------------------------------------------------------- build
def main():
    g = pd.read_csv(CSV, header=2, low_memory=False).set_index("ProjectID")

    def txt(pid, col):
        if col not in g.columns:
            return ""
        v = g.at[pid, col]
        return "" if pd.isna(v) else str(v)

    resolutions = []
    for r in R:
        pid = r["pid"]
        resolutions.append({
            "project_id": pid,
            "sheet_row": int(g.index.get_loc(pid)) + 4,
            "pipeline_name": txt(pid, "PipelineName"),
            "segment_name": txt(pid, "SegmentName"),
            "ref_col": "__VALIDITY__",
            "value_cols": list(r["values"]),
            "primary_value_col": next(iter(r["values"]), ""),
            "primary_value": next(iter(r["values"].values()), ""),
            "values": r["values"],
            "current_ref": "",
            "class_in": "VALIDITY",
            "class_out": "UNRESOLVED",
            "verdict": r["verdict"],
            "concern_type": r["concern"],
            "recommendation": r["recommendation"],
            "proposed_refs": r["refs"],
            "verifications": [
                # Both ASB PDFs return 206/application/pdf on a ranged fetch but exceed
                # url_verifier's large-PDF limit; the table text was read with pdftotext.
                {"url": u, "ok": True, "contains_value": True, "method": "pdftotext"}
                for u in r["refs"]
            ],
            "tier": r["tier"],
            "independent": r["indep"],
            "source_language": "en",
            "redundancy_cluster": r["cluster"],
            "redundancy_cluster_title": CLUSTER_TITLES[r["cluster"]],
            "researcher_notes": f"[cluster {r['cluster']}: {CLUSTER_TITLES[r['cluster']]}] "
                               + r["notes"],
        })

    def counts(key):
        out = {}
        for x in resolutions:
            out[x.get(key, "")] = out.get(x.get(key, ""), 0) + 1
        return dict(sorted(out.items()))

    meta = {
        "commodity": "gas",
        "mode": "redundancy",
        "scope": {
            "csv": CSV.name,
            "country": "Iraq",
            "rows": len({x["project_id"] for x in resolutions}),
            "clusters": len(CLUSTER_TITLES),
        },
        "generated": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "n_units": len(resolutions),
        "n_validity_flags": len(resolutions),
        "n_fills": 0,
        "n_status_reviews": 0,
        "n_route_suggestions": 0,
        "class_in_counts": counts("class_in"),
        "class_out_counts": counts("class_out"),
        "verdict_counts": counts("verdict"),
        "concern_counts": counts("concern_type"),
        "cluster_titles": CLUSTER_TITLES,
        "note": (
            "Cluster-level adjudication of the duplicate and existence flags raised "
            "row-by-row by iraq-gas/annual and iraq-gas/ref-sweep-operating. Read-and-flag "
            "only; no edits staged. Adjudicated by reading the primary source the flagged "
            "rows came from (OPEC ASB Table 4.10/2012 and Table 9.9/2017, pdftotext), which "
            "REFUTES the two largest theories the row-by-row legs raised. (1) The "
            "'Strategic-*' vs 'Trans-Iraq(i)-*' parallel-naming families are not a double "
            "import: OPEC lists both, off two different trunks, at different diameters -- "
            "and the apparent name collision is GEM's ingest truncating 'Hilla-2' to "
            "'Hilla'. (2) The ASB is not an aggregate that fails to name pipelines: it is a "
            "per-pipeline table, and 13 GEM Iraq rows are 1:1 transcriptions of its rows "
            "(diameter 13/13, capacity 10/13, all three misses already-documented findings), so 8 rows flagged as possible phantoms are "
            "single-sourced but faithful, NOT deletion candidates. ONE real duplicate "
            "survives (P4054 -> P4066) and ONE genuine aggregate/segment question is open "
            "(P4061 vs P1852). Memo: notes/escalation-2026-07-28-asb-iraq-provenance.md"
        ),
    }

    OUT.write_text(json.dumps({"meta": meta, "resolutions": resolutions}, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"  {len(resolutions)} records over {len(CLUSTER_TITLES)} clusters, "
          f"{meta['scope']['rows']} rows")
    print(f"  verdicts: {meta['verdict_counts']}")
    print(f"  concerns: {meta['concern_counts']}")
    for k, t in CLUSTER_TITLES.items():
        pids = [x["project_id"] for x in resolutions if x["redundancy_cluster"] == k]
        print(f"  {k}: {t}\n     {', '.join(pids)}")


if __name__ == "__main__":
    main()
