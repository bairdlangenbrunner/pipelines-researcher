"""Write staged_resolutions.json: dormancy fixes found in the 2026-11-08 wiki page audit (P3184 Alliance Capacity Expansion, P2524 Transco Diamond East)."""
import json, pathlib
HERE = pathlib.Path(__file__).parent
SEC = "https://www.sec.gov/Archives/edgar/data/1546066/000127956918001596/ex991.htm"
NDOIL = "https://www.ndoil.org/alliance-pipeline-announces-open-season-for-additional-2021-capacity/"
EIA = "https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx"
WP = "https://www.worldpipelines.com/business-news/27082014/Williams-announces-open-season-for-Diamond-East-Project"
NOTE = {
    SEC: "Pembina Pipeline's report on its second quarter of 2018, filed with the SEC in August 2018. It says that on June 15, 2018, Alliance announced the expansion open season, which closed May 30, 2018, did not reach its 400 million cubic feet per day target, and that Alliance was assessing alternatives and next steps.",
    NDOIL: "North Dakota Petroleum Council news item from March 2018 announcing the Alliance open season for added capacity from 2021.",
    EIA: "EIA Natural Gas Pipeline Projects workbook, August 2026 release, Historical Projects tab. It lists the Diamond East Project with status Cancelled, last updated July 1, 2025, and the note: no information since 2013/2014, cancelled, no FERC application active as of 2025.",
    WP: "World Pipelines news item of August 27, 2014. Williams Partners opened a binding open season for Transco's Diamond East Project from August 26 to September 23, 2014, for up to 1 billion cubic feet per day, about 50 miles of looping, with service targeted for mid-2018.",
}
def ver(urls, name):
    return [{"url": u, "ok": True, "contains_value": True, "name_found": True, "note": NOTE[u]} for u in urls]
A = {"project_id": "P3184", "pipeline_name": "Alliance Gas Pipeline", "wiki": "Alliance Gas Pipeline", "sheet_row": 2219,
     "segment_name": "Capacity Expansion", "source_language": "en"}
T = {"project_id": "P2524", "pipeline_name": "Transcontinental Gas Pipeline", "wiki": "Transcontinental Gas Pipeline", "sheet_row": 1860,
     "segment_name": "Diamond East Project", "source_language": "en"}
R = [
 {**A, "ref_col": "Cancelled [ref]", "value_cols": ["CancelledYear"], "primary_value_col": "CancelledYear",
  "values": {"CancelledYear": "2022"}, "primary_value": "2022", "current_ref": f"{SEC}, {NDOIL}",
  "class_in": "FILL", "class_out": "REFS_ADDED", "evidence_date": "2018-06", "proposed_refs": [SEC, NDOIL],
  "verifications": ver([SEC, NDOIL], "Alliance"), "tier": "high", "independent": False,
  "researcher_notes": "Changed the cancelled year from 2018 to 2022. The newest news on this expansion is from June 2018, when Alliance said its open season fell short of the 400 million cubic feet per day target. Pembina's second quarter 2018 report says so. With no news since, the project counts as cancelled four years later, in 2022. The 2018 year on the sheet was the year of the last news, not the year the rule takes effect. A web search found nothing on this expansion after 2018. Alliance opened a separate open season in March 2026 for deliveries into Alberta's Industrial Heartland. That is a different project and has been sent to discovery."},
 {**T, "ref_col": "__STATUS__", "value_cols": ["Status", "ShelvedCancelledType", "CancelledYear"], "primary_value_col": "Status",
  "values": {"Status": "cancelled", "ShelvedCancelledType": "inferred", "CancelledYear": "2018"}, "primary_value": "cancelled",
  "current_ref": EIA, "class_in": "STATUS", "class_out": "CHANGE_PROPOSED", "current_status": "shelved", "verdict": "change",
  "proposed_status": "cancelled", "evidence_date": "2014-09", "staleness_rule": "cancelled: no news for 4 years",
  "proposed_refs": [EIA, WP], "verifications": ver([EIA, WP], "Diamond East"), "tier": "medium", "independent": False,
  "researcher_notes": "Changed from shelved to cancelled. The EIA workbook cited for the status, its August 2026 release, lists the project as cancelled, with a note that there has been no information since 2013 or 2014 and no FERC application as of 2025. EIA reached that from silence, not from a company statement, so the type stays inferred. The last news is the open season Williams Partners held in August and September 2014. Four years later gives a cancelled year of 2018. Williams has never announced a cancellation. One source for a status change, so this is medium."},
 {**T, "ref_col": "Cancelled [ref]", "value_cols": ["CancelledYear"], "primary_value_col": "CancelledYear",
  "values": {"CancelledYear": "2018"}, "primary_value": "2018", "current_ref": "",
  "class_in": "FILL", "class_out": "REFS_ADDED", "evidence_date": "2014-09", "proposed_refs": [WP, EIA],
  "verifications": ver([WP, EIA], "Diamond East"), "tier": "medium", "independent": False,
  "researcher_notes": "Cancelled year 2018. The last news is the open season of August and September 2014, and the four year rule gives 2018. EIA says there has been no information since 2013 or 2014."},
 {**T, "ref_col": "Shelved [ref]", "value_cols": ["ShelvedYear"], "primary_value_col": "ShelvedYear",
  "values": {"ShelvedYear": ""}, "primary_value": "", "current_ref": EIA,
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [], "verifications": [], "tier": "medium", "independent": False,
  "researcher_notes": "Cleared the shelved year of 2014. It was the year of the last news, not a shelving date, and the project is now staged as cancelled."},
 {**T, "ref_col": "Proposal [ref]", "value_cols": ["ProposalYear", "ProposalMonth"], "primary_value_col": "ProposalYear",
  "values": {"ProposalYear": "2014", "ProposalMonth": 8}, "primary_value": "2014",
  "current_ref": "https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects_May2018.xlsx",
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [WP], "verifications": ver([WP], "Diamond East"),
  "tier": "high", "independent": False,
  "researcher_notes": "Changed the proposal year from 2017 to 2014 and added August. Williams Partners announced the project with a binding open season from August 26 to September 23, 2014. The 2017 year came from the May 2018 EIA workbook, and EIA itself says there has been no information since 2013 or 2014."},
]
meta = {"commodity": "gas", "mode": "update",
        "scope": {"csv": "GGIT_gas_snapshot_20261107.csv", "country": "United States", "province": None,
                  "include_pids": ["P3184", "P2524"], "rows": 2, "project_ids": 2},
        "n_units": len(R), "created": "2026-11-08", "requested_by": "BL",
        "purpose": "dormancy fixes from the 2026-11-08 wiki page audit: P3184 cancelled year 2018 to 2022; P2524 shelved to cancelled (inferred, 2018) and proposal year 2017 to 2014"}
json.dump({"meta": meta, "resolutions": R}, open(HERE / "staged_resolutions.json", "w"), indent=1, ensure_ascii=False)
print(len(R), "units")
