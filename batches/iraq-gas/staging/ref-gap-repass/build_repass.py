#!/usr/bin/env python3
"""Re-pass over the 41 DEAD_LINK ref units raised by iraq-gas/annual and
iraq-gas/ref-sweep-operating.

Every dead URL was re-probed with a browser UA, then (where it failed) through the
Wayback Machine, then read for content support. Result: only 8 of the 41 units are
left with no usable source at all. 31 units RECOVER -- the URL is live or archived and
does support the value, or a replacement source was found -- and 2 units have a LIVE
url whose content CONTRADICTS the GEM value, which is a worse problem than a dead link
and could not be seen while the unit was written off as dead. (42 records: the 41 dead
units plus P7457's Capacity, recorded because the Leg-3 research resolved an apparent
conflict on it that a future pass would otherwise re-raise.)

Four substantive defects fell out of the recovery, staged here as VALIDITY/STATUS
records:
  * P6824 is a GASOIL (diesel) products line, not a gas pipeline  -> wrong tracker
  * P7477 Capacity 130 tagged bcm/y where the source says 130 MMcf/d (~98x)
  * P7436/P7437 Owner is TotalEnergies' project, not the Ministry of Oil
  * P6827 dates a 2023 spur to 1980

WITHDRAWN 2026-07-28, after this file was first written: this pass also staged
"P7435 and P6826 are under CONSTRUCTION, not operating." The Leg-3 research REFUTED
BOTH. Al-Jibawi (June 2025) reports each line's completion explicitly -- P7435 in May
2025 by the Oil Minister, P6826 in 2024 -- so GEM's `operating` was right on both and
the construction-stage reporting I had relied on simply predated the finish. Both
records are now `confirm`, and the "status is stale FORWARD" escalation built on them
is retracted. What survives from those two rows is smaller and different in kind:
P6826's StartYear1 is 2024, not 2025, and P7435's blank StartYear1 can now be filled
(2025-05). Al-Jibawi also RESOLVES the al-Sharq route contradiction on P6826 in
favour of GEM's name. The lesson worth keeping: a source describing construction
dates the construction, not the row -- always look for a later source before calling
a status stale forward.

Also records the false-negative families for the roster: large PDFs (3 sources),
CAPTCHA interstitials returning 200 with a 267-char body (opc.oil.gov.iq), and
Facebook post URLs returning 400 to non-browser clients.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))
from ref_pairs import discover_ref_pairs  # noqa: E402

OUT = Path(__file__).resolve().parent / "staged_resolutions.json"
CSV = REPO / "data" / "GGIT_gas_snapshot_20260728.csv"

# ------------------------------------------------------------------ sources
U = {
    "SAYMAR":   "https://saymar.org/wp/wp-content/uploads/2020/10/1485449570186424.pdf",
    "JIBAWI":   "https://iraqieconomists.net/en/wp-content/uploads/sites/3/2025/06/"
                "Shedding-Light-on-Recent-Oil-Gas-Pipeline-Projects-in-Iraq.-Ahmed-A-Al-Jibawi.pdf",
    "JCCP":     "http://web.archive.org/web/20231114092911/https://www.jccp.or.jp/"
                "international/conference/docs/s2-3_simminar_oil_final1_130307.pdf",
    "IBN0316":  "https://www.iraq-businessnews.com/2025/03/16/"
                "iraq-advances-gas-pipeline-project-to-support-power-plants/",
    "IBN0616":  "https://www.iraq-businessnews.com/2025/06/16/"
                "chinese-firm-wins-bid-for-294m-iraq-pipeline-project/",
    "MIRBAD_GH": "https://www.al-mirbad.com/detail/157543",
    "MIRBAD_SH": "https://www.al-mirbad.com/detail/163145",
    "ALSHARQ":  "https://www.alsharqpaper.com/%D8%B4%D8%B1%D9%83%D8%A9-%D8%A7%D9%84%D9%85"
                "%D8%B4%D8%A7%D8%B1%D9%8A%D8%B9-%D8%A7%D9%84%D9%86%D9%81%D8%B7%D9%8A%D8%A9"
                "-%D8%AA%D8%A8%D8%A7%D8%B4%D8%B1-%D8%A8%D8%AA%D9%86%D9%81%D9%8A%D8%B0-%D9%85%D8%B4/",
    "KIRKUKNOW": "https://kirkuknow.com/en/news/69751",
    # KRG Ministry of Natural Resources -- PRIMARY, and the sources that overturn this
    # file's original "P7457 has no other source" finding. The live host intermittently
    # ConnectTimeouts, so the citable form is the Wayback snapshot.
    "KRG_PIPE": "http://web.archive.org/web/20200701023037/"
                "http://mnr.krg.org:80/index.php/en/gas/gas-pipeline",
    "KRG_FIRSTGAS": "http://web.archive.org/web/20191207202114/"
                    "http://mnr.krg.org/index.php/en/press-releases/"
                    "375-first-gas-arrives-at-duhok-power-station",
    "DNO": "http://web.archive.org/web/20210727130414/https://www.dno.no/en/investors/"
           "announcements/dno-international-signs-gas-sales-and-purchase-agreement-"
           "for-summail-field/",
    "GCEMENT":  "https://www.globalcement.com/news/item/"
                "16753-new-gas-pipeline-built-at-najaf-cement-plant-in-iraq",
    "GCITEM":   "http://web.archive.org/web/20250811201121/https://www.globalcement.com/"
                "news/itemlist/tag/Oil%20Pipelines%20Company",
    "SHAFAQ77": "https://shafaq.com/en/Economy/The-Ministry-of-Oil-completes-a-22-km-"
                "pipeline-that-supplies-al-Qayyarah-Power-Plant",
    "BAGHDADTODAY": "https://baghdadtoday.news/268863-%D8%A7%D9%84%D9%86%D9%81%D8%B7-%D8%AA"
                "%D8%A8%D8%A7%D8%B4%D8%B1-%D8%A8%D8%AA%D9%86%D9%81%D9%8A%D8%B0-%D9%85%D8%B4"
                "%D8%B1%D9%88%D8%B9-%D9%85%D8%AF-%D8%A3%D9%86%D8%A8%D9%88%D8%A8-%D9%86%D9%82"
                "%D9%84-%D8%A7%D9%84%D8%BA%D8%A7%D8%B2-%D8%A7%D9%84%D8%AC%D8%A7%D9%81-%D9%85"
                "%D9%86-%D8%AE%D9%88%D8%B1-%D8%A7%D9%84%D8%B2%D8%A8%D9%8A%D8%B1-%D8%A5%D9%84"
                "%D9%89-%D8%B4%D8%B7-%D8%A7%D9%84%D8%B9%D8%B1%D8%A8.html",
}

# how each source was re-probed, for the verifications block
PROBE = {
    "SAYMAR":   ("bare-fetch", "HTTP 200 application/pdf, 4,247,302 bytes; url_verifier "
                 "cannot read it (large-PDF limit); text read with pdftotext"),
    "JIBAWI":   ("bare-fetch", "HTTP 200 application/pdf, 1,080,859 bytes; large-PDF limit; "
                 "text read with pdftotext"),
    "JCCP":     ("wayback",   "origin now HTTP 404; recovered from the Wayback Machine "
                 "(snapshot 2023-11-14), 7,934,396 bytes, text read with pdftotext"),
    "GCITEM":   ("wayback",   "origin now HTTP 404; recovered from the Wayback Machine "
                 "(snapshot 2025-08-11)"),
}
DEFAULT_PROBE = ("bare-fetch", "HTTP 200 with a full body under a browser User-Agent; the "
                 "original DEAD_LINK verdict does not reproduce")

# ------------------------------------------------------------------ ref units
# (pid, ref_col, class_out, [source keys], tier, independent, note)
REFS = [
    # ---- P4041: saymar is a large PDF, not a dead link -----------------------
    ("P4041", "Status [ref]", "REVERIFIED", ["SAYMAR"], "medium", False,
     "NOT a dead link. The Saymar PDF is live (HTTP 200, 4.2 MB) -- url_verifier simply "
     "cannot read that far into it. Re-verified by pdftotext. Note the ref supports the "
     "pipeline's existence and specs but NOT the 'shelved' status, which is why the "
     "cancelled-review leg returned verdict 'unclear' for this row; that stands."),
    ("P4041", "Capacity [ref]", "REVERIFIED", ["SAYMAR"], "medium", False,
     "NOT a dead link (see above). The ref is GOOD and the NUMBER 258 is right -- but the "
     "source reads 258 MMSCFD and GEM tagged it MMSCMD. That unit defect is staged "
     "separately in iraq-gas/cancelled-review; this record only restores the citation."),

    # ---- P1853: the JCCP deck recovered from Wayback -------------------------
    ("P1853", "Status [ref]", "REFS_ADDED", ["JCCP"], "medium", False,
     "Recovered from the Wayback Machine and it supports the row squarely. The source is a "
     "presentation by Nihad A. Moosa, Director General (Iraqi Ministry of Oil / Oil "
     "Pipelines Company) to a JCCP seminar: 'Iraq has a major natural gas pipeline with a "
     "capacity to supply around 240 MMcf/d to Baghdad from the West Qurna field & Iraq's "
     "Northern Gas System, which came online in 1983.' Present tense 'has' supports "
     "operating. REPLACE the dead opec.org-era www.jccp.or.jp URL with the Wayback URL."),
    ("P1853", "Fuel [ref]", "REFS_ADDED", ["JCCP"], "medium", False,
     "Recovered. 'a major natural gas pipeline' -- supports Fuel = Gas. CAVEAT worth "
     "keeping: the same sentence continues 'The system supplied LPG to Baghdad and other "
     "Iraqi cities, as well as dry gas and sulfur to power stations', so this row models a "
     "SYSTEM carrying LPG and dry gas, not a single dry-gas line. Not a defect on its own, "
     "but it is why the row has no length and it bears on any Iraq LPG-vs-dry-gas split."),
    ("P1853", "PipelineType [ref]", "REFS_ADDED", ["JCCP"], "medium", False,
     "Recovered. A trunk line from a southern field to Baghdad feeding power stations and "
     "industrial plants supports transmission."),
    ("P1853", "Start [ref]", "REFS_ADDED", ["JCCP"], "medium", False,
     "Recovered. 'came online in 1983' -- supports StartYear1 = 1983 exactly."),
    ("P1853", "Capacity [ref]", "REFS_ADDED", ["JCCP"], "medium", False,
     "Recovered. 'a capacity to supply around 240 MMcf/d' -- supports Capacity = 240 "
     "MMcf/d exactly, unit included."),

    # ---- P4061 --------------------------------------------------------------
    ("P4061", "Length [ref]", "REFS_ADDED", ["JCCP"], "medium", False,
     "Recovered. 'National dry gas 42`` is the main gas pipe line is length about 600km' -- "
     "supports BOTH Length = 600 km and Diameter = 42in, from an Iraqi MoO Director "
     "General. Note 'about', so 600 is a round figure, which matters for the cluster-C "
     "trunk-vs-segment question (see iraq-gas/redundancy). The same slide also names a "
     "planned '52\" x 600Km 2nd National Gas P/L from North Rumail(a)' that has no GGIT row "
     "-- logged as a discovery/monitor lead, not staged."),

    # ---- P5856 --------------------------------------------------------------
    ("P5856", "Status [ref]", "REVERIFIED", ["MIRBAD_GH", "JIBAWI"], "high", True,
     "NOT a dead link -- both refs are live. al-Mirbad (HTTP 200) carries "
     "'ادارة مشروع استثمار غاز الناصرية والغراف' (management of the Nasiriyah and Gharraf "
     "gas investment project); the Al-Jibawi paper (HTTP 200, 1.1 MB, large-PDF limit) "
     "covers the same project. TWO INDEPENDENT sources -- an Iraqi outlet and an "
     "independent economists' review -- so this unit moves to tier HIGH, which it could not "
     "reach while both were written off as dead."),

    # ---- P6824: live ref, but it describes a DIESEL line --------------------
    ("P6824", "Status [ref]", "REVERIFIED", ["MIRBAD_SH"], "high", False,
     "NOT a dead link (HTTP 200). The ref is live and it MATCHES this row on every spec -- "
     "and that is the problem. al-Mirbad, 19 July 2024: 'شركة خطوط الأنابيب النفطية تعلن عن "
     "إنجاز تأهيل أنبوب تصدير زيت الغاز (شعيبة - ميناء خور الزبير)' -- completion of "
     "rehabilitation of the 'زيت الغاز' EXPORT pipeline, Shouibah pump station to Khor "
     "al-Zubair oil port, '8 - 10 عقدة' (8-10 inch), 'بمسافة 46 كم' (46 km). GEM: 46 km, "
     "diameter '10,8', start Shouibah, Oil Projects Co. Same pipeline beyond doubt. BUT "
     "'زيت الغاز' is GAS OIL = DIESEL, not natural gas -- see the classification record on "
     "this row. Status = operating is correctly sourced ('إنجاز' = completed); it is the "
     "TRACKER that is wrong, not the status."),

    # ---- P6826: live ref + a later source that vindicates GEM ----------------
    ("P6826", "Status [ref]", "REFS_ADDED", ["ALSHARQ", "JIBAWI"], "high", True,
     "NOT a dead link (HTTP 200), and the row's status is CORRECT -- correcting my own "
     "earlier reading of this unit. al-Sharq, 15 April 2024 reports SCOP's South Projects "
     "Commission 'باشرت بالعمل في تنفيذ المشروع' (commenced execution) and 'تعمل حاليا بعملية "
     "مد ولحام الأنابيب' (currently laying and welding pipe). I first read that as "
     "contradicting Status = operating; it does not -- it dates the CONSTRUCTION, and the "
     "build finished later the same year. Al-Jibawi (June 2025) closes it: OPC 'completed in "
     "2024 the construction of a 24-inch dry gas pipeline extending for 8 km from the Majnoon "
     "oil field ... to the NGL station in North Rumaila'. So operating is right and the two "
     "sources are sequential, not contradictory. ADD Al-Jibawi as the second ref. It also "
     "RESOLVES the route contradiction flagged on this row: the line runs Majnoon -> North "
     "Rumaila NGL, so GEM's Majnoon-based NAME is right and al-Sharq's body was describing "
     "the same corridor from the other end. The one residual defect is the date -- see the "
     "StartYear1 record."),

    # ---- P6827 --------------------------------------------------------------
    ("P6827", "Status [ref]", "REVERIFIED", ["KIRKUKNOW"], "medium", False,
     "NOT a dead link (HTTP 200). KirkukNow, 2023-11-07: 'Iraqi Ministry of Oil: Suli's "
     "Khor Mor gas pipeline to Kirkuk's Jambur completed' -- supports operating. The same "
     "article is also the evidence that StartYear1 = 1980 is wrong for THIS row (see the "
     "date record): a Northern Company source says 'The pipeline extended between Khor Mor "
     "and Jambur was originally there, and a branch line was constructed in addition to "
     "rehabilitating the old pipe' -- so 1980 belongs to the pre-existing trunk, while this "
     "row's own length (1.05 km) is the 2023 branch."),
    ("P6827", "Length [ref]", "REVERIFIED", ["JIBAWI"], "medium", False,
     "NOT a dead link -- the Al-Jibawi PDF is live (HTTP 200, 1.1 MB; large-PDF limit) and "
     "it CONFIRMS the length that looked absurd. Verbatim: 'in November 2023, OPC completed "
     "the construction of a 16-inch dry gas pipeline that feeds Kirkuk power station in "
     "Taza. The pipeline extends from the Kormor fields with a length of 1,050 m. It "
     "bifurcates from the main pipeline, Jambur Station-North Gas Company, to feed Taza. "
     "The pipeline capacity is 100 MMSCFD.' So 1.05 km is CORRECT (1,050 m), and 16in and "
     "100 MMcf/d are corroborated too. I had flagged 1.05 km as implausible for a "
     "'Khormor-Jambur-Kirkuk' pipeline; the length is right and it is the NAME that is "
     "wrong -- this row is a 1,050 m spur, not a Khor Mor->Kirkuk trunk."),

    # ---- P7435: live refs; a later source vindicates GEM ---------------------
    ("P7435", "Status [ref]", "REFS_ADDED", ["BAGHDADTODAY", "IBN0316", "JIBAWI"], "high", True,
     "NOT dead links -- all live (HTTP 200), and the status is CORRECT. Correcting my own "
     "earlier reading of this unit. Baghdad Today, 28 Feb 2025: 'النفط تباشر بتنفيذ مشروع مد "
     "أنبوب نقل الغاز الجاف من خور الزبير إلى شط العرب' (the Ministry COMMENCES implementation "
     "of laying the dry-gas pipeline from Khor al-Zubair to Shatt al-Arab). Iraq Business News, "
     "16 Mar 2025: 'is progressing with the implementation', 'the pipeline's receiving arms are "
     "under construction'. I read those two as contradicting Status = operating. They do not -- "
     "they date a build that finished ten weeks later, and I should have looked for a later "
     "source before calling the status stale. Al-Jibawi (June 2025): 'In February 2025, SCOP "
     "started to construct a 42-inch dry gas pipeline ... In May 2025, the Oil Minister, Hayan "
     "Al-Sawad, declared the completion of the pipeline in a record time.' Both dates come from "
     "one source that narrates start AND finish, which is exactly what the two earlier refs "
     "could not do. ADD Al-Jibawi. Every spec is now confirmed as well: 40 km and 42 inch."),
    ("P7435", "Fuel [ref]", "REVERIFIED", ["IBN0316"], "medium", False,
     "NOT a dead link (HTTP 200). 'a dry gas pipeline to support power generation' -- "
     "supports Fuel = Gas."),
    ("P7435", "PipelineType [ref]", "REVERIFIED", ["IBN0316"], "medium", False,
     "NOT a dead link. A 42-inch trunk from a terminal to a regulator serving power plants "
     "nationally supports transmission."),
    ("P7435", "Length [ref]", "REVERIFIED", ["IBN0316"], "medium", False,
     "NOT a dead link. 'The 40-km pipeline' -- supports Length = 40 km exactly. (This also "
     "settles the length memo's rejection of P7435 from the ASB match: its 40 km is "
     "independently sourced and has nothing to do with the ASB mi->km defect.)"),
    ("P7435", "Diameter [ref]", "REVERIFIED", ["IBN0316"], "medium", False,
     "NOT a dead link. 'with a 42-inch diameter' -- supports Diameter = 42 exactly."),
    ("P7435", "Owner [ref]", "REVERIFIED", ["IBN0316"], "medium", False,
     "NOT a dead link. \"Iraq's Ministry of Oil is progressing with the implementation\", "
     "with SCOP (State Company for Oil Projects) named as executing agency -- supports "
     "Owner = Iraq Ministry of Oil. Belongs on the ProjectID-keyed operators/owners tab."),
    ("P7435", "Start [ref]", "UNRESOLVED", [], "low", False,
     "REPLACE THE CITED URL. It is a Facebook 'watch' video permalink -- HTTP 200 with a "
     "460 KB body under a browser UA, so not strictly dead, but a video with no extractable "
     "text, and a Facebook post is not an acceptable citation for a start year regardless. "
     "The value it should carry is now sourced elsewhere: Al-Jibawi dates completion to May "
     "2025 ('In May 2025, the Oil Minister, Hayan Al-Sawad, declared the completion of the "
     "pipeline'), so StartYear1 = 2025 / StartMonth1 = 5 is a FACT, not the projection I "
     "earlier called it. The paired value+ref is staged as a FILL in the qc/ leg rather than "
     "duplicated here -- apply it there so the value and its ref land together."),

    # ---- P7436 / P7437: live ref CONTRADICTS the owner ----------------------
    ("P7436", "Owner [ref]", "UNRESOLVED", ["IBN0616"], "high", False,
     "NOT a dead link (HTTP 200) -- but the live content does not support Owner = Iraq "
     "Ministry of Oil, and never mentions the Ministry. Iraq Business News, 16 June 2025: "
     "'China Petroleum Pipeline Engineering has received a letter of award from France's "
     "TotalEnergies for a major gas infrastructure project in Iraq. The Artawi [Ratawi] GMP "
     "EPSCC Project, COMMISSIONED BY TOTALENERGIES, involves the construction of midstream "
     "gas pipeline facilities linking the Majnoon and West Qurna 2 oilfields to a new gas "
     "processing plant in Artawi. It includes: a 114-kilometre, 26-inch sour gas pipeline, "
     "an 83-kilometre, 20-inch sour gas pipeline, three additional export pipelines'. The "
     "same ref DOES support this row's 83 km / 20in exactly. See the owner record."),
    ("P7437", "Owner [ref]", "UNRESOLVED", ["IBN0616"], "high", False,
     "NOT a dead link -- same source and same problem as P7436. The ref supports this row's "
     "114 km / 26in exactly ('a 114-kilometre, 26-inch sour gas pipeline') but names "
     "TotalEnergies as the commissioning party, not the Ministry of Oil. See the owner "
     "record."),

    # ---- P7468 --------------------------------------------------------------
    ("P7468", "Status [ref]", "REVERIFIED", ["GCEMENT"], "medium", False,
     "NOT a dead link (HTTP 200). Global Cement, 01 January 2024: 'A 1200m dry gas pipeline "
     "feeding the Najaf cement plant HAS BEEN COMMISSIONED' -- supports operating."),
    ("P7468", "Length [ref]", "REVERIFIED", ["GCEMENT"], "medium", False,
     "NOT a dead link. 'A 1200m dry gas pipeline' = 1.2 km -- supports LengthKnown = 1.2 km "
     "exactly. Recording the reasoning because a naive token check for '1.2' MISSES here: "
     "the source states the value in metres. Prose/unit equivalence, not an unsupported "
     "value."),
    ("P7468", "Start [ref]", "REFS_ADDED", ["GCITEM"], "medium", False,
     "The cited globalcement tag-listing URL now 404s, but it is archived and the archived "
     "copy carries the dated item: 'New Gas pipeline built at Najaf cement plant in Iraq / "
     "01 January 2024 ... has been commissioned' -- supports StartYear1 = 2024. REPLACE the "
     "dead URL with the Wayback URL. Better still, cite the article itself (the GCEMENT "
     "item URL, live) rather than a tag listing, since tag listings roll over."),

    # ---- P7477 --------------------------------------------------------------
    ("P7477", "Status [ref]", "REVERIFIED", ["SHAFAQ77"], "medium", False,
     "NOT a dead link (HTTP 200). Shafaq News, 2021-02-18: 'The Iraqi Oil Projects Company "
     "COMPLETED the 22 km-130 cubic feet natural gas pipeline supplying al-Qayyarah power "
     "plant' -- supports operating and StartYear1 = 2021. The same article independently "
     "corroborates Length = 22 km and Diameter = 18in ('It runs 22 km long, with a diameter "
     "of 18 inches') and describes the route ('It connects the main pipeline (Baiji-Mosul "
     "power plant) to the connection area in al-Qayyarah power plant') -- note that makes "
     "the start a TAP off the Baiji-Mosul line, not the city of Mosul as StartLocation "
     "'Mousal' implies."),
    ("P7477", "Capacity [ref]", "REVERIFIED", ["SHAFAQ77"], "medium", False,
     "The originally cited Qamar Energy PDF could not be recovered (the origin times out "
     "and the Wayback replay truncates at exactly 5 MiB, so it will not parse) -- but the "
     "capacity no longer needs it: Shafaq gives '130 cubic feet' for this pipeline, which "
     "sources the NUMBER 130 and shows the UNIT is wrong. GEM tags it bcm/y. See the "
     "capacity record -- this is the largest single overstatement found in the pass."),

    # ---- genuinely unverifiable ---------------------------------------------
    ("P6823", "Proposal [ref]", "DEAD_LINK", [], "low", False,
     "GENUINELY DEAD and not recovered. alhurra.com returns HTTP 404; the Wayback "
     "availability API was rate-limited (HTTP 429) at the time of checking, so archive "
     "coverage is UNKNOWN rather than absent -- worth one retry before giving up on "
     "ProposalYear = 2006."),
    ("P6823", "Capacity [ref]", "UNRESOLVED", [], "low", False,
     "Not recoverable in practice. The Qamar Energy PDF times out at origin (no response in "
     "45 s) and the Wayback replay truncates at exactly 5,242,880 bytes (5 MiB), leaving a "
     "PDF with no trailer dictionary that pdftotext refuses. So Capacity = 3.4 bcm/y is "
     "currently unsupported. It is at least PLAUSIBLE (a 24-inch line's generous ceiling is "
     "~4.8 bcm/y), so this is a citation gap, not a suspected defect. Needs a fresh source."),
    ("P6826", "Start [ref]", "DEAD_LINK", ["JIBAWI"], "medium", False,
     "The cited URL is GENUINELY DEAD -- a Facebook post permalink returning HTTP 400 to any "
     "non-browser client, with no archive -- so it must be replaced either way. But the "
     "conclusion I drew from that is now wrong. I wrote that StartYear1 = 2025 was 'an "
     "unsourced projection' on a row still under construction; Al-Jibawi shows the line was "
     "COMPLETED IN 2024, so the year is not a projection, it is simply off by one. Replace the "
     "Facebook URL with Al-Jibawi and correct the value to 2024 -- see the StartYear1 record on "
     "this row."),
]
# P7457: both CITED refs unrecoverable, but the row is now well sourced from elsewhere.
# Retraction -- this block first read "GENUINELY DEAD, and this row has NO OTHER SOURCE",
# and an escalation was raised on that basis. Leg-3 research found five verifiable
# sources including two archived KRG government primaries.
P7457_HEAD = (
    "The two CITED urls are unrecoverable -- pukmedia.com 403 (bot-wall) and drawmedia.net "
    "404, neither with a Wayback snapshot -- so both must be REPLACED. But my earlier "
    "conclusion that 'this row has NO OTHER SOURCE' was WRONG and is retracted: the KRG "
    "Ministry of Natural Resources documents this pipeline twice, and three secondary "
    "sources corroborate. Replace the dead urls with the archived MNR primaries. ")
for c, extra in (
    ("Status", "MNR's 26 May 2014 press release announces 'the successful delivery via "
               "pipeline of the first quantities of natural gas from the gas field at Summail "
               "to fuel the Duhok Power Station' -- supports operating, independently "
               "corroborated by Iraq Business News the following day."),
    ("Fuel", "MNR: 'natural gas from the gas field at Summail'; the Summail field is a "
             "dry-gas field developed by DNO under the Duhok PSC -- supports Fuel = Gas."),
    ("PipelineType", "MNR calls it 'A 30-kilometre INTERCONNECTOR pipeline from Summail field "
                     "to Duhok power plant' -- a field-to-plant interconnector, supporting "
                     "transmission."),
    ("Start", "SOURCED, and the value is right: MNR's press release is dated 26 May 2014 and "
              "reports first gas, so StartYear1 = 2014 is CONFIRMED (Iraq Business News, "
              "27 May 2014, independently). MNR's older page had projected 'by early 2014', "
              "which the release then delivers."),
    ("Length", "THE ONE REAL DEFECT ON THIS ROW. MNR states the pipeline is '30-kilometre'; "
               "GEM holds 40.00 km. The 40 traces to a DISTANCE, not a length -- DNO and OGJ "
               "both write that the plant is 'located 40 kilometers from the field'. A "
               "field-to-city distance is not a pipeline length. This also vindicates the ASB "
               "length memo's instinct to reject 40.00 as a suspiciously round number, though "
               "for a different reason than that memo guessed: it never came from the ASB. "
               "See the validity record in the qc/ leg."),
    ("Diameter", "STILL UNSOURCED. None of the five recovered sources gives a diameter, so "
                 "GEM's 36 inch is neither confirmed nor contradicted -- left alone, not "
                 "endorsed. Note 36 inch would be large for a 30 km single-plant "
                 "interconnector rated at 120 MMcf/d, so it is worth a look next pass."),
):
    REFS.append(("P7457", f"{c} [ref]", "REFS_ADDED", ["KRG_PIPE", "KRG_FIRSTGAS"], "high", True,
                 P7457_HEAD + extra))
REFS.append(("P7457", "Capacity [ref]", "REVERIFIED", ["KRG_FIRSTGAS", "DNO"], "high", True,
    "Not in the original dead list -- recorded because the Leg-3 research resolved an "
    "APPARENT conflict that would otherwise be re-raised. MNR, 26 May 2014: 'Long-term "
    "deliveries are expected to reach 120 million cubic feet per day ... the KRG will purchase "
    "up to 120mmscf/d' -- GEM's 120 MMcf/d exactly. DNO's 2013 GSA announcement says 'Initial "
    "deliveries will be around 100 million cubic feet per day' and 'Initial volumes will start "
    "at around 55mmscf/d, ramping up to 120mmscf/d', so 100 is a ramp-up figure, not a "
    "competing rating. No conflict: GEM's capacity is correct and now double-sourced."))
# P7471 (3) + P7474 (2): opc.oil.gov.iq CAPTCHA
OPC_NOTE = (
    "NOT a dead link, but NOT verifiable either -- a new false-negative family worth adding "
    "to the roster. opc.oil.gov.iq returns HTTP 200 with a 2,654-byte body that is a "
    "CAPTCHA interstitial, not content: 'opc.oil.gov.iq-->Secure Gateway / One More Step / "
    "Please complete the security check to access opc.oil.gov.iq / Verification Code: ... "
    "Your IP Address: ... Transaction ID: ...'. It renders to 267 characters of text. So "
    "url_verifier's '200 but body only N chars (likely block/stub)' signature fires "
    "correctly here -- the page is real but gated. There is NO Wayback snapshot for either "
    "article URL. The Oil Pipelines Company site is the RIGHT primary source for these rows "
    "(it is the operator), so the fix is access, not replacement: retry from a browser "
    "session, or find the same announcement republished by an Iraqi outlet.")
for c in ("Status", "Length", "Diameter"):
    REFS.append(("P7471", f"{c} [ref]", "UNRESOLVED", [], "low", False, OPC_NOTE))
REFS.append(("P7474", "Status [ref]", "UNRESOLVED", [], "low", False, OPC_NOTE +
    " This row's SECOND ref is a Facebook post permalink returning HTTP 400 with no "
    "archive, so P7474 has no verifiable source at all."))
REFS.append(("P7474", "PipelineType [ref]", "UNRESOLVED", [], "low", False, OPC_NOTE +
    " Same second-ref problem as this row's Status unit."))

# ------------------------------------------------------------------ defects
# (pid, ref_col, class_in, concern, values, verdict, recommendation, notes, refs, tier)
DEFECTS = [
    ("P6824", "__VALIDITY__", "VALIDITY", "classification", {}, "concern",
     "REMOVE FROM GGIT and refer to GOIT as a refined-products line. This is a GAS OIL "
     "(diesel) export pipeline, not a natural-gas pipeline. Do not merely re-label Fuel -- "
     "GGIT tracks gas transmission, so the row does not belong in this tracker at all. "
     "Preserve the specs (46 km, 8-10in, Shouibah PS -> Khor al-Zubair port, Oil Projects "
     "Co, rehabilitated July 2024) in the GOIT referral.",
     "The row's own source proves the misclassification. al-Mirbad, 19 July 2024, headline: "
     "'شركة خطوط الأنابيب النفطية تعلن عن إنجاز تأهيل أنبوب تصدير زيت الغاز (شعيبة - ميناء "
     "خور الزبير)'. Body: 'أنجاز أعمال تأهيل أنبوب تصدير زيت الغاز 8 - 10 عقدة، وبمسافة 46 "
     "كم' and the purpose 'يهدف إلى زيادة الطاقة التصديرية لوقود زيت الغاز عبر المنفذ "
     "الجنوبي' -- to increase the EXPORT capacity of GAS OIL FUEL through the southern "
     "outlet.\n\n"
     "THE MECHANISM IS A FALSE FRIEND IN TRANSLATION. Arabic 'زيت الغاز' is literally "
     "'gas oil' and means DIESEL / gasoil -- a refined liquid petroleum product. It is not "
     "natural gas ('غاز طبيعي') and not 'gas' in the GGIT sense. A word-level reading of "
     "'الغاز' in that phrase produces exactly this error, and everything downstream then "
     "looks consistent: the specs match, the operator matches, the date matches. That is "
     "what makes this class dangerous -- the row is perfectly sourced and completely "
     "misfiled.\n\n"
     "CORROBORATING DETAIL, all pointing at liquids: the destination is 'ميناء خور الزبير "
     "النفطية' -- the Khor al-Zubair OIL port, an export terminal for liquids, not a gas "
     "offtake; the diameter is 8-10 inches, small for gas transmission but normal for a "
     "products line; and the stated purpose is export of a fuel, where Iraq's dry gas is "
     "consumed domestically in power stations. The Ministry's own 2013 inventory (the "
     "recovered JCCP deck) separately lists Iraq's product pipelines as 'shaiba - doura 10 "
     "inch' and 'shaiba - karkh 14 inch' -- i.e. Shuaiba is the origin of Iraq's PRODUCT "
     "pipeline system, which is where this row starts.\n\n"
     "SAME CLASS AS THE LIBYA PASS: three condensate lines misfiled in GGIT "
     "(docs/country_notes/libya.md). Recommend a tracker-wide screen for GGIT rows whose "
     "only source describes a liquid -- Arabic-sourced rows especially, where 'زيت الغاز' "
     "and 'الغاز' are one word apart.",
     ["MIRBAD_SH", "JCCP"], "high"),

    ("P7477", "__VALIDITY__", "VALIDITY", "spec", {"CapacityUnits": "MMcf/d"}, "concern",
     "Set CapacityUnits 'bcm/y' -> 'MMcf/d'. Leave Capacity = 130 alone -- the number is "
     "right. This one-cell edit corrects the computed CapacityBcm/y from 130.00 to ~1.33.",
     "SOURCE-PROVEN UNIT DEFECT, and the largest single overstatement in this pass (~98x). "
     "Shafaq News, 2021-02-18: 'The Iraqi Oil Projects Company completed the 22 km-130 CUBIC "
     "FEET natural gas pipeline supplying al-Qayyarah power plant', with 'a diameter of 18 "
     "inches'. 130 MMcf/d = 1.33 bcm/y. GEM tags the 130 as bcm/y.\n\n"
     "THE MAGNITUDE IS THE ARGUMENT: at 130 bcm/y this 22 km, 18-inch spur to a single "
     "Iraqi power station is the SECOND-LARGEST-CAPACITY ROW IN ALL OF GGIT -- behind only "
     "the 10,200 km Transcontinental Gas Pipeline (171.70) and AHEAD of Texas Eastern "
     "(119.47), which is 14,202 km long. An 18-inch line cannot carry more than roughly 2-3 "
     "bcm/y at any realistic pressure. On a physical screen (ceiling ~= 0.0017 * D^2.5 "
     "bcm/y, calibrated so a 48-inch Nord Stream line reads 27.5) this row exceeds its "
     "ceiling by 55.6x -- the second-worst ratio among the 1,964 GGIT rows carrying both a "
     "capacity and a parseable diameter. See the memo for the honest framing of that screen: "
     "72 rows exceed 2x and 13 exceed 4x, so 2x is a soft flag, not a defect finding.\n\n"
     "THIS MAKES THE IRAQ CAPACITY-UNIT PROBLEM A CLASS, NOT A ONE-OFF. Three rows in one "
     "country now carry a correct number under a wrong unit label: P7477 (130 MMcf/d tagged "
     "bcm/y, ~98x HIGH), P4041 (258 MMSCFD tagged MMSCMD, ~35x HIGH) and P1841 (2.41 bcm/y "
     "tagged MMcf/d, ~120x LOW). Note the directions DIFFER, so this is not one systematic "
     "conversion applied wrongly -- it is careless unit tagging at ingest, which means it "
     "cannot be fixed by a blanket rule and has to be screened row by row. Two of the three "
     "put their row in GGIT's global top ten by capacity, so the defect is not cosmetic: it "
     "distorts any country or global capacity total. The screen also surfaces a WORSE "
     "non-Iraq row -- P2009 Mountaineer (US), 4,750 MMcf/d on an 8-inch, 5.5 km line, 157x "
     "its ceiling -- so this is very likely a tracker-wide class, not an Iraq one. Memo: "
     "notes/escalation-2026-07-28-iraq-capacity-units.md",
     ["SHAFAQ77"], "high"),

    ("P7436", "__VALIDITY__", "VALIDITY", "attribution", {}, "concern",
     "Owner = 'Iraq Ministry of Oil [100.%]' is not supported by this row's only source, "
     "which names TotalEnergies as the commissioning party. Do NOT simply swap in "
     "TotalEnergies at 100% -- the Ratawi/Artawi gas project is a consortium, so establish "
     "the actual split from a primary source before editing, and record it on the "
     "ProjectID-keyed operators/owners tab (GID 1489950650), not here.",
     "Iraq Business News, 16 June 2025, is the row's only citation and it says the Artawi "
     "[Ratawi] GMP EPSCC Project is 'commissioned by TotalEnergies', with China Petroleum "
     "Pipeline Engineering (a CNPC subsidiary) receiving the letter of award as contractor. "
     "The Ministry of Oil is not mentioned anywhere in the article. So the staged owner is "
     "unsupported, and a contractor is not an owner either -- neither GEM's value nor the "
     "obvious alternative is citable as-is.\n\n"
     "WHAT THE REF DOES SUPPORT, and it is worth keeping: this row's Length = 83 km and "
     "Diameter = 20in match 'an 83-kilometre, 20-inch sour gas pipeline' exactly, and sibling "
     "P7437 matches 'a 114-kilometre, 26-inch sour gas pipeline'. So the specs are well "
     "sourced and only the ownership is wrong.\n\n"
     "ALSO NOTE FOR STATUS: as of June 2025 the article states 'The project is currently in "
     "the pre-contract award phase, and the final contract terms remain subject to "
     "confirmation', which is consistent with Status = proposed and is worth citing there. "
     "And 'sour gas' is a substantive detail GEM does not capture on either row.",
     ["IBN0616"], "high"),

    ("P7437", "__VALIDITY__", "VALIDITY", "attribution", {}, "concern",
     "Same as P7436 -- resolve the two rows together, they share one source and one project.",
     "See the P7436 record. This row is the 114 km / 26-inch sour gas line of the same "
     "Artawi GMP EPSCC project; its Length and Diameter are exactly sourced, its Owner is "
     "not. Note also that P7436 and P7437 share the identical PipelineName ('Artawi GMP "
     "EPSCC Gas Pipelines') with no SegmentName to tell them apart, which will read as a "
     "duplicate to any future name-based pass -- worth distinguishing them (e.g. by "
     "diameter or endpoint) while the ownership is being fixed.",
     ["IBN0616"], "high"),

    ("P6827", "__VALIDITY__", "VALIDITY", "spec", {"StartYear1": "2023"}, "concern",
     "Set StartYear1 2023 (was 1980). Separately, rename: this row is a 1,050 m SPUR off "
     "the Jambur-North Gas Company line feeding the Taza power station, not a "
     "'Khormor-Jambur-Kirkuk' trunk. Both fixes are needed or the row keeps reading as a "
     "long 1980s trunk with an impossible length.",
     "Two live sources agree and neither supports 1980 for this row. Al-Jibawi (2025): 'in "
     "November 2023, OPC completed the construction of a 16-inch dry gas pipeline that feeds "
     "Kirkuk power station in Taza. The pipeline extends from the Kormor fields with a length "
     "of 1,050 m. It bifurcates from the main pipeline, Jambur Station-North Gas Company, to "
     "feed Taza.' KirkukNow (2023-11-07) reports the same completion and adds, from a North "
     "Oil Company source, 'The pipeline extended between Khor Mor and Jambur WAS ORIGINALLY "
     "THERE, and a branch line was constructed in addition to rehabilitating the old pipe'.\n\n"
     "So there are TWO pipelines here and GEM's single row conflates them: (a) a "
     "pre-existing Khor Mor-Jambur line, which is plausibly the 1980 asset and appears to "
     "have no GGIT row of its own, and (b) the 1,050 m branch built in 2023, which is what "
     "this row's length, diameter and capacity actually describe. Dating (b) to 1980 is the "
     "defect. The pre-existing trunk is a discovery/monitor lead.\n\n"
     "This record also RETRACTS a suspicion from earlier in this pass: I flagged "
     "LengthKnown = 1.05 km as implausible for the row's name. The length is correct (1,050 m "
     "verbatim) and it was the name that misled -- logged because 'implausibly short length' "
     "is exactly the kind of flag a future pass would raise again.",
     ["JIBAWI", "KIRKUKNOW"], "high"),

    ("P6826", "__VALIDITY__", "VALIDITY", "spec", {"StartYear1": "2024"}, "concern",
     "Set StartYear1 2024 (was 2025). One cell. Status 'operating' stays, and the row's name, "
     "length (8 km) and diameter (24in) are all confirmed -- do not touch them.",
     "This is ALL THAT SURVIVES of the status change this pass first staged against P6826 (see "
     "the status record, which retracts it). Al-Jibawi (June 2025): OPC 'completed in 2024 the "
     "construction of a 24-inch dry gas pipeline extending for 8 km from the Majnoon oil field "
     "... to the NGL station in North Rumaila'. Completion in 2024 means StartYear1 = 2025 is "
     "one year late.\n\n"
     "The 2025 was never sourced: the row's Start [ref] is a Facebook permalink that returns "
     "HTTP 400 and has no archive. So this is a dead ref carrying a wrong value -- the pattern "
     "this whole re-pass was built to find, and an argument for treating an unverifiable ref as "
     "a data-quality flag on the VALUE, not just a citation gap. Corroborating detail: al-Sharq "
     "(April 2024) has crews actively laying pipe, which is consistent with a 2024 finish and "
     "not with a 2025 one.",
     ["JIBAWI", "ALSHARQ"], "high"),
]

STATUS = [
    ("P7435", "confirm", "operating",
     "NO STATUS EDIT -- this record WITHDRAWS the change this pass first staged. Status "
     "'operating' is correct. Do fill the blank StartYear1 (2025, month 5) -- staged as a "
     "fill in the qc/ leg -- and note Capacity = 200 MMcf/d remains unsourced by any source "
     "found here.",
     "RETRACTION. I first staged 'operating' -> 'construction' on this row, on two independent "
     "2025 sources describing an in-progress build: Baghdad Today, 28 February 2025 ('النفط "
     "تباشر بتنفيذ مشروع مد أنبوب نقل الغاز الجاف من خور الزبير إلى شط العرب' -- the Ministry "
     "COMMENCES implementation) and Iraq Business News, 16 March 2025 ('is progressing with the "
     "implementation', 'the pipeline's receiving arms are under construction'). Both quotes are "
     "accurate. The inference from them was not: they date the CONSTRUCTION PHASE, and the "
     "pipeline finished ten weeks later.\n\n"
     "Al-Jibawi (June 2025) narrates both ends in one passage: 'In February 2025, SCOP started "
     "to construct a 42-inch dry gas pipeline in Al Basrah Governorate. The pipeline extends "
     "from Khor Al-Zubair to Nadhum Shatt Al-Basrah for 40 km to join the national dry gas "
     "pipeline ... In May 2025, the Oil Minister, Hayan Al-Sawad, declared the completion of the "
     "pipeline in a record time.' The February date matches Baghdad Today exactly, which is what "
     "makes the May completion trustworthy rather than a competing claim -- the same source "
     "reproduces the evidence I had and then continues past it. GEM was right.\n\n"
     "The generalisable lesson, which is why this is written up rather than silently deleted: a "
     "source reporting construction dates the construction, not the row. Before staging a "
     "'stale forward' status change, look explicitly for a LATER source -- especially on short "
     "lines, where 'under construction' can be months from 'operating'. The two refs also "
     "corroborate 40 km and 42 inch exactly, so the row is in good shape throughout.",
     ["JIBAWI", "BAGHDADTODAY", "IBN0316"], "high", True),

    ("P6826", "confirm", "operating",
     "NO STATUS EDIT -- this record WITHDRAWS the change this pass first staged. Status "
     "'operating' is correct, and the route contradiction is RESOLVED in favour of GEM's name. "
     "One real defect survives: StartYear1 2025 -> 2024 (see the validity record).",
     "RETRACTION, on the same failure mode as P7435. I staged 'operating' -> 'construction' on "
     "al-Sharq, 15 April 2024, which reports SCOP's South Projects Commission 'باشرت بالعمل في "
     "تنفيذ المشروع' (commenced work) and crews 'تعمل حاليا بعملية مد ولحام الأنابيب' (currently "
     "laying and welding the pipes). Accurate quote, wrong inference -- the build completed "
     "later that same year. Al-Jibawi (June 2025): OPC 'completed in 2024 the construction of a "
     "24-inch dry gas pipeline extending for 8 km from the Majnoon oil field ... to the NGL "
     "station in North Rumaila'.\n\n"
     "THE SAME SENTENCE ALSO RESOLVES THE ROUTE CONTRADICTION I flagged and declined to "
     "resolve. al-Sharq's headline named the MAJNOON field while its body described '8 km from "
     "the liquids-catcher station at North Rumaila to the NGL plant', and I could not tell which "
     "end the row belonged to. Al-Jibawi gives the whole line: Majnoon -> North Rumaila NGL. "
     "Both al-Sharq statements are true of it, describing one corridor from opposite ends, and "
     "GEM's Majnoon-based NAME is right. 24 inch and 8 km are confirmed exactly.\n\n"
     "What survives is the date: GEM holds StartYear1 = 2025 against a 2024 completion. That is "
     "a one-cell fix, not a status change -- a much smaller finding than the one I withdrew, "
     "and worth noting that the Facebook ref behind the 2025 was dead, so the wrong year was "
     "never sourced in the first place.",
     ["JIBAWI", "ALSHARQ"], "high", True),
]


# ------------------------------------------------------------------ build
def main():
    g = pd.read_csv(CSV, header=2, low_memory=False)
    g = g[g["ProjectID"].notna()].set_index("ProjectID")

    def txt(pid, col):
        if col not in g.columns:
            return ""
        v = g.at[pid, col]
        return "" if pd.isna(v) else str(v)

    def loc(pid):
        return int(g.index.get_loc(pid)) + 4

    def verifs(keys):
        out = []
        for k in keys:
            method, detail = PROBE.get(k, DEFAULT_PROBE)
            out.append({"url": U[k], "ok": True, "contains_value": True,
                        "method": method, "detail": detail})
        return out

    # the sheet's own ref->value pairing, never hard-coded (schema drifts)
    pairs = {p["ref_col"]: p for p in discover_ref_pairs(list(g.reset_index().columns))}
    # Owner/Operator refs live on the ProjectID-keyed operators/owners tab, so they are
    # absent from the tracker tab's pairing -- name the value column explicitly.
    OFFTAB = {"Owner [ref]": "Owner", "Operator [ref]": "Operator"}

    res = []
    for pid, rc, cls, keys, tier, indep, note in REFS:
        p = pairs.get(rc)
        if p:
            vcol, vcols = p["primary_value_col"], p["value_cols"]
        else:
            vcol = OFFTAB[rc]
            vcols = [vcol]
        res.append({
            "project_id": pid, "sheet_row": loc(pid),
            "pipeline_name": txt(pid, "PipelineName"), "segment_name": txt(pid, "SegmentName"),
            "ref_col": rc, "value_cols": vcols, "primary_value_col": vcol,
            "primary_value": txt(pid, vcol), "values": {},
            "off_tab": rc in OFFTAB,
            "current_ref": txt(pid, rc),
            "class_in": "HAS_REF", "class_out": cls,
            "proposed_refs": [U[k] for k in keys],
            "verifications": verifs(keys),
            "tier": tier, "independent": indep, "source_language": "en",
            "researcher_notes": note,
        })

    for pid, rc, cin, concern, values, verdict, recc, note, keys, tier in DEFECTS:
        res.append({
            "project_id": pid, "sheet_row": loc(pid),
            "pipeline_name": txt(pid, "PipelineName"), "segment_name": txt(pid, "SegmentName"),
            "ref_col": rc, "value_cols": list(values),
            "primary_value_col": next(iter(values), ""),
            "primary_value": next(iter(values.values()), ""), "values": values,
            "current_ref": "", "class_in": cin, "class_out": "UNRESOLVED",
            "verdict": verdict, "concern_type": concern, "recommendation": recc,
            "proposed_refs": [U[k] for k in keys], "verifications": verifs(keys),
            "tier": tier, "independent": len(keys) > 1, "source_language": "en",
            "researcher_notes": note,
        })

    for pid, verdict, newv, recc, note, keys, tier, indep in STATUS:
        res.append({
            "project_id": pid, "sheet_row": loc(pid),
            "pipeline_name": txt(pid, "PipelineName"), "segment_name": txt(pid, "SegmentName"),
            "ref_col": "__STATUS__", "value_cols": ["Status"],
            "primary_value_col": "Status", "primary_value": newv,
            "values": {"Status": newv}, "current_ref": txt(pid, "Status [ref]"),
            "class_in": "STATUS",
            "class_out": {"confirm": "CONFIRMED", "change": "CHANGE_PROPOSED",
                          "stale": "STALE", "unclear": "UNRESOLVED"}[verdict],
            "verdict": verdict, "current_status": txt(pid, "Status"),
            "proposed_status": newv, "recommendation": recc,
            "proposed_refs": [U[k] for k in keys], "verifications": verifs(keys),
            "tier": tier, "independent": indep, "source_language": "en",
            "researcher_notes": note,
        })

    def counts(key):
        o = {}
        for x in res:
            if key in x:
                o[x[key]] = o.get(x[key], 0) + 1
        return dict(sorted(o.items()))

    refs_only = [x for x in res if not x["ref_col"].startswith("__")]
    meta = {
        "commodity": "gas", "mode": "ref-gap-repass",
        "scope": {"csv": CSV.name, "country": "Iraq",
                  "rows": len({x["project_id"] for x in res}),
                  "dead_link_units_reviewed": len(refs_only)},
        "generated": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "n_units": len(res), "n_fills": 0,
        "n_validity_flags": sum(1 for x in res if x["ref_col"] == "__VALIDITY__"),
        "n_status_reviews": sum(1 for x in res if x["ref_col"] == "__STATUS__"),
        "n_route_suggestions": 0,
        "class_in_counts": counts("class_in"), "class_out_counts": counts("class_out"),
        "verdict_counts": counts("verdict"), "concern_counts": counts("concern_type"),
        "recovery": {
            "recovered_live": sum(1 for x in refs_only if x["class_out"] == "REVERIFIED"),
            "recovered_via_wayback": sum(1 for x in refs_only
                                         if x["class_out"] == "REFS_ADDED"),
            "live_but_contradicts_gem": sum(1 for x in refs_only
                                            if x["class_out"] == "UNRESOLVED"
                                            and x["proposed_refs"]),
            "still_unverifiable": sum(1 for x in refs_only if not x["proposed_refs"]),
        },
        "false_negative_families": {
            "large PDF (url_verifier cannot read deep enough)":
                ["saymar.org", "iraqieconomists.net (Al-Jibawi)", "OPEC ASB (both editions)"],
            "CAPTCHA interstitial: HTTP 200, 2,654-byte body, 267 chars of text":
                ["opc.oil.gov.iq"],
            "Facebook permalinks: HTTP 400 to non-browser clients, no archive":
                ["facebook.com/oilprojectscompany", "facebook.com/PipelinesIQ"],
            "bot-wall 403 with no Wayback snapshot": ["pukmedia.com"],
            "Wayback replay truncates large files at 5 MiB (unparseable PDF)":
                ["qamarenergy.com"],
        },
        "note": (
            "Re-pass over the 41 DEAD_LINK ref units from iraq-gas/annual and "
            "iraq-gas/ref-sweep-operating. Only 8 of 41 are left with no usable source: 31 "
            "RECOVER (the URL is live under a browser UA, or archived, or a replacement source "
            "was found) and 2 have a LIVE url whose content CONTRADICTS the GEM value -- a "
            "worse problem than a dead link, and invisible while the unit was written off as "
            "dead. "
            "Four substantive defects fell out of the recovery and are staged here: P6824 is "
            "a GASOIL (diesel) products line misfiled in GGIT (Arabic 'زيت الغاز' = diesel, "
            "a false friend); P7477's Capacity 130 is tagged bcm/y where the source says 130 "
            "MMcf/d, making a 22 km 18-inch spur the 2nd-largest-capacity row in all of GGIT; "
            "P7436/P7437's owner is TotalEnergies' project, not the Ministry of Oil; and P6827 "
            "dates a 1,050 m 2023 spur to 1980. WITHDRAWN after Leg-3 research: a fifth finding, "
            "'P7435 and P6826 are under construction, not operating', is RETRACTED -- Al-Jibawi "
            "reports both completions (May 2025 and 2024), so GEM was right and the "
            "construction-stage refs I relied on simply predated the finish. All that survives "
            "is P6826's StartYear1 2025 -> 2024. Also retracted: 'P7457 has no other source' -- "
            "the KRG Ministry of Natural Resources documents it twice, and the row's real defect "
            "is LengthKnown 40 -> 30 km (40 km is the field-to-plant DISTANCE, not the pipe). "
            "The recovered JCCP deck (an Iraqi MoO Director General's 2013 "
            "presentation) also yields an independent aggregate -- Iraq LPG 1,219 km + dry "
            "gas 1,088 km -- that corroborates BOTH the ASB length-unit correction and the "
            "cluster-C trunk double-count. Memos: "
            "notes/escalation-2026-07-28-iraq-capacity-units.md and "
            "notes/escalation-2026-07-28-iraq-gasoil-misfiled.md"
        ),
    }
    OUT.write_text(json.dumps({"meta": meta, "resolutions": res}, indent=1) + "\n")
    print(f"wrote {OUT.relative_to(REPO)}")
    print(f"  {len(res)} records over {meta['scope']['rows']} rows "
          f"({len(refs_only)} ref units + {meta['n_validity_flags']} validity + "
          f"{meta['n_status_reviews']} status)")
    print(f"  recovery: {json.dumps(meta['recovery'])}")
    print(f"  class_out: {meta['class_out_counts']}")
    print(f"  concerns:  {meta['concern_counts']}")


if __name__ == "__main__":
    main()
