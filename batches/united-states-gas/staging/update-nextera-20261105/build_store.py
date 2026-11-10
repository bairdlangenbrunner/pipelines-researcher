"""Write staged_resolutions.json: NextEra pipeline fixes found while answering a landowner question (2026-11-05).

P4457 Lowman owner moved to the project company, P8328 MVP Boost Owner1% filled, two unrelated Chinese government refs on P4457 flagged, and P8161 Florida Southeast Connection owner (added once its research is in).
Sheet rows: owners tab = snapshot index + 3, gas tab = snapshot index + 4 (snapshots of 2026-11-05). push.py matches by ProjectID before any write.
"""
import json, pathlib
HERE = pathlib.Path(__file__).parent

PSC = "https://www.pscpublicaccess.alabama.gov/pscpublicaccess/ViewFile.aspx?Id=551e03df-819c-494d-bbab-c36f60b16006"
LOWMAN_WB = "https://web.archive.org/web/20230713140710/https://www.lowmanpipeline.com/project.html"
EQT_BOOST = "https://ir.eqt.com/investor-relations/news/news-release-details/2025/Mountain-Valley-Pipeline-LLC-Files-Formal-Application-Requesting-FERC-Authorization-to-Construct-MVP-Boost/default.aspx"
LINCANG_1 = "https://www.lincang.gov.cn/info/1138/332572.htm"
LINCANG_2 = "https://www.lincang.gov.cn/info/1095/12144.htm"
FR_2014 = "https://www.govinfo.gov/content/pkg/FR-2014-10-24/pdf/2014-25325.pdf"
NEE_2016 = "https://web.archive.org/web/2016/https://www.investor.nexteraenergy.com/news-and-events/news-releases/2016/02-03-2016-202012609"

NOTE = {
    PSC: "A notice filed with the Alabama Public Service Commission in docket 32978. NextEra Energy Pipeline Holdings (Lowman), Inc. says it applied to own, construct and operate an intrastate gas pipeline of about 51 miles and 16 inches to the Lowman Energy Center.",
    LOWMAN_WB: "The Lowman Pipeline project page, as saved by the Wayback Machine in July 2023. It says the pipeline will be developed, constructed, owned and operated by a subsidiary of NextEra Energy Resources, LLC.",
    FR_2014: "A Federal Register notice of October 24, 2014 (FERC docket CP14-554). It says Florida Southeast Connection, LLC applied for authorization to construct, own and operate about 126 miles of new pipe from near Intercession City to the Martin Clean Energy Center near Indiantown, Florida. Read from the PDF with pdftotext, since the verifier missed the phrase across a line break.",
    NEE_2016: "A NextEra Energy news release from February 3, 2016, as saved by the Wayback Machine (the live link no longer loads). It calls Florida Southeast Connection a wholly owned subsidiary of NextEra Energy, Inc.",
    EQT_BOOST: "An EQT news release from 2025. It says Mountain Valley Pipeline, LLC filed its application with the Federal Energy Regulatory Commission to build the MVP Boost expansion.",
}


def ver(urls):
    return [{"url": u, "ok": True, "contains_value": True, "name_found": True, "note": NOTE[u]} for u in urls]


LOWMAN = {"project_id": "P4457", "pipeline_name": "Lowman Pipeline", "wiki": "https://www.gem.wiki/Lowman_Pipeline",
          "segment_name": "", "source_language": "en"}
BOOST = {"project_id": "P8328", "pipeline_name": "Mountain Valley Gas Pipeline (MVP)",
         "wiki": "https://www.gem.wiki/Mountain_Valley_Gas_Pipeline_(MVP)", "segment_name": "MVP Boost Expansion",
         "source_language": "en"}

FSC = {"project_id": "P8161", "pipeline_name": "Florida Southeast Connection Pipeline",
       "wiki": "https://www.gem.wiki/Florida_Southeast_Connection_Pipeline", "segment_name": "Main Line",
       "source_language": "en"}

R = [
    {**LOWMAN, "tab": "operators_owners", "sheet_row": 3323, "ref_col": "Owner [ref]",
     "value_cols": ["Owner1", "Owner1%"], "primary_value_col": "Owner1",
     "values": {"Owner1": "NextEra Energy Pipeline Holdings (Lowman) Inc", "Owner1%": 1},
     "primary_value": "NextEra Energy Pipeline Holdings (Lowman) Inc",
     "current_ref": f"{LOWMAN_WB}, {PSC}",
     "class_in": "HAS_REF", "class_out": "REFS_ADDED", "proposed_refs": [PSC, LOWMAN_WB], "verifications": ver([PSC, LOWMAN_WB]),
     "tier": "high", "independent": True, "evidence_date": "2019-10",
     "researcher_notes": "Owner changed from NextEra Energy Resources LLC to its project company, NextEra Energy Pipeline Holdings (Lowman) Inc. The owner column takes the company that holds the pipeline itself. The Alabama Public Service Commission filing names this company as the one that will own, build and run the line. The project page says a subsidiary of NextEra Energy Resources owns and runs it. The Operator column already names the same company. Both refs were already on the row and both back the new owner."},
    {**BOOST, "tab": "operators_owners", "sheet_row": 6671, "ref_col": "Owner [ref]",
     "value_cols": ["Owner1", "Owner1%"], "primary_value_col": "Owner1",
     "values": {"Owner1": "Mountain Valley Pipeline LLC", "Owner1%": 1},
     "primary_value": "Mountain Valley Pipeline LLC", "current_ref": EQT_BOOST,
     "class_in": "HAS_REF", "class_out": "REFS_ADDED", "proposed_refs": [EQT_BOOST], "verifications": ver([EQT_BOOST]),
     "tier": "high", "independent": False,
     "researcher_notes": "Owner1% was blank. Mountain Valley Pipeline LLC is the company that applied to build MVP Boost, so it holds the whole segment, as on the other four Mountain Valley rows. The ref stays as it is."},
    {**LOWMAN, "sheet_row": 2902, "ref_col": "Proposal [ref]", "value_cols": ["ProposalYear", "ProposalMonth"],
     "primary_value_col": "ProposalYear", "values": {"ProposalYear": "2019", "ProposalMonth": "10"}, "primary_value": "2019",
     "current_ref": f"{PSC}, https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx, {LINCANG_1}",
     "class_in": "HAS_REF", "class_out": "REF_UNSUPPORTED", "proposed_refs": [], "verifications": [],
     "tier": "low", "independent": False,
     "researcher_notes": "One ref in this cell has nothing to do with the pipeline. It is a 2022 spending report by the development commission of Lincang, a city in Yunnan, China, read as a Wayback copy from May 2025. The page does not mention Lowman. It looks like a link pasted onto the wrong row. The other two refs back the value. A person should decide whether to remove it."},
    {**LOWMAN, "sheet_row": 2902, "ref_col": "Diameter [ref]", "value_cols": ["Diameter", "DiameterUnits"],
     "primary_value_col": "Diameter", "values": {"Diameter": "16", "DiameterUnits": "in"}, "primary_value": "16",
     "current_ref": f"{PSC}, https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx, {LINCANG_2}",
     "class_in": "HAS_REF", "class_out": "REF_UNSUPPORTED", "proposed_refs": [], "verifications": [],
     "tier": "low", "independent": False,
     "researcher_notes": "One ref in this cell is on the website of Lincang, a city in Yunnan, China. The page did not load from here and has no Wayback copy. A second Lincang page on the same row is an unrelated city spending report, so this one is very likely pasted onto the wrong row too. The other two refs back the 16 inch value. A person should open it and decide whether to remove it."},
    {**FSC, "tab": "operators_owners", "sheet_row": 6504, "ref_col": "Owner [ref]",
     "value_cols": ["Owner1", "Owner1%"], "primary_value_col": "Owner1",
     "values": {"Owner1": "Florida Southeast Connection LLC", "Owner1%": 1},
     "primary_value": "Florida Southeast Connection LLC",
     "current_ref": "https://newsroom.fpl.com/2013-07-26-FPL-selects-Sabal-Trail-Transmission-and-Florida-Southeast-Connection-to-build-new-natural-gas-pipeline-system-into-Florida, https://rbnenergy.com/daily-posts/blog/miami-2017-marcellus-gas-heading-florida",
     "class_in": "HAS_REF", "class_out": "REFS_ADDED", "proposed_refs": [FR_2014, NEE_2016], "verifications": ver([FR_2014, NEE_2016]),
     "tier": "high", "independent": True, "evidence_date": "2016-02",
     "researcher_notes": "Owner changed from NextEra Energy Inc to Florida Southeast Connection LLC, the company that holds the pipeline. Owner1% was blank and is now 100 percent. The 2014 application notice in the Federal Register says Florida Southeast Connection, LLC will build, own and run the line. NextEra's 2016 release calls it a wholly owned subsidiary of NextEra Energy. The old refs name the project but not the owning company, so they are replaced."},
    {**FSC, "tab": "operators_owners", "sheet_row": 6504, "ref_col": "Operator [ref]",
     "value_cols": ["Operator"], "primary_value_col": "Operator",
     "values": {"Operator": "Florida Southeast Connection LLC"}, "primary_value": "Florida Southeast Connection LLC",
     "current_ref": "", "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [FR_2014], "verifications": ver([FR_2014]),
     "tier": "medium", "independent": False, "evidence_date": "2014-10",
     "researcher_notes": "Operator was blank. The 2014 application notice says Florida Southeast Connection, LLC will build, own and run the line. No later source names a different operator."},
]

meta = {"commodity": "gas", "mode": "update",
        "scope": {"csv": "GGIT_gas_snapshot_20261105.csv", "owners_csv": "GEM_operators_owners_snapshot_20261105.csv",
                  "country": "United States", "province": None, "include_pids": ["P4457", "P8328", "P8161"],
                  "rows": 3, "project_ids": 3},
        "n_units": len(R), "created": "2026-11-05", "requested_by": "BL",
        "purpose": "NextEra pipelines after a landowner question: Lowman owner to its project company, MVP Boost Owner1% filled, two unrelated Chinese refs on Lowman flagged, Florida Southeast Connection owner and operator set to its project company"}
json.dump({"meta": meta, "resolutions": R}, open(HERE / "staged_resolutions.json", "w"), indent=1)
print(len(R), "resolutions")
