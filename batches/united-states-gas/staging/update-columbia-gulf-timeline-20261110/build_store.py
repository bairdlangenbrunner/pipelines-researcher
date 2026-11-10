"""Write staged_resolutions.json: timeline cells for the four Columbia Gulf Transmission rows (P6533 Main Line, P8124 Maysville, P8125 Pulaski, P8126 Vicksburg Lateral), researched 2026-11-10 on Baird's request."""
import json, pathlib
HERE = pathlib.Path(__file__).parent
EIA = "https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsOct2026.xlsx"
FR = "https://www.govinfo.gov/content/pkg/FR-2000-11-16/pdf/00-29347.pdf"
OGJ = "https://www.ogj.com/pipelines-transportation/article/17252151/columbia-to-serve-two-more-power-plants"
NGI = "https://www.naturalgasintel.com/news/columbia-lateral-gets-green-light/"
PHMSA = "https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/2021-07/2008-0066-Columbia-Gulf-Transmission-SP-Analysis-and-Findings-TN.pdf"
NOTE = {
    EIA: "EIA Natural Gas Pipeline Projects workbook, October 2026 release, the newest. It lists the Maysville Expansion Project (application filed November 17, 2025, status Applied, in service 2029), the Pulaski Expansion Project (application filed October 15, 2025, approved October 15, 2026, in service 2029), and on its Historical Projects tab the CGT Vicksburg Lateral, completed September 1, 2001.",
    FR: "Federal Register notice of November 16, 2000. It says Columbia Gulf filed on November 3, 2000, under docket CP01-28, to build the Vicksburg Lateral, about 37 miles of 20-inch pipe from its mainline in Richland Parish, Louisiana, to Warren County, Mississippi.",
    OGJ: "Oil & Gas Journal article of November 14, 2000. Columbia Gulf will build a 37-mile lateral from its mainline near Delhi, Louisiana, to two power plants south of Vicksburg, Mississippi, expected in service by May 2001.",
    NGI: "Natural Gas Intelligence article of February 12, 2001. FERC approved the Vicksburg lateral, docket CP01-28, the week before.",
    PHMSA: "PHMSA special permit analysis for Columbia Gulf's Mainline 100, 200 and 300 in Tennessee. It gives the year each Mainline 100 segment was built as 1953, 1953/1954 or 1954.",
}
def ver(urls):
    return [{"url": u, "ok": True, "contains_value": True, "name_found": True, "note": NOTE[u]} for u in urls]
def base(pid, row, seg):
    return {"project_id": pid, "pipeline_name": "Columbia Gulf Transmission Pipeline", "wiki": "Columbia Gulf Transmission Pipeline",
            "sheet_row": row, "segment_name": seg, "source_language": "en", "class_in": "FILL", "class_out": "REFS_ADDED", "independent": False}
ML, MV, PU, VK = base("P6533", 3666, "Main Line"), base("P8124", 4373, "Maysville Project"), base("P8125", 4374, "Pulaski Project"), base("P8126", 4375, "Vicksburg Lateral")
def rec(b, ref_col, values, refs, tier, note, current=""):
    first = next(iter(values))
    return {**b, "ref_col": ref_col, "value_cols": list(values), "primary_value_col": first, "values": values,
            "primary_value": str(values[first]), "current_ref": current, "proposed_refs": refs, "verifications": ver(refs),
            "tier": tier, "researcher_notes": note}
R = [
 rec(MV, "Proposal [ref]", {"ProposalYear": "2025", "ProposalMonth": 11}, [EIA], "high",
     "Added November as the proposal month. EIA's October 2026 workbook says Columbia Gulf filed its application with FERC on November 17, 2025.",
     "https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx"),
 rec(MV, "Start [ref]", {"StartYear1": "2029"}, [EIA], "high",
     "Start year 2029. EIA's October 2026 workbook gives 2029 as the in-service year."),
 rec(MV, "FID [ref]", {"FIDStatus": "Pre-FID"}, [EIA], "medium",
     "Added a source for Pre-FID. EIA's October 2026 workbook lists the project as Applied, still waiting on FERC, so no investment decision has been taken."),
 rec(PU, "Proposal [ref]", {"ProposalYear": "2025", "ProposalMonth": 10}, [EIA], "high",
     "Added October as the proposal month. EIA's October 2026 workbook says Columbia Gulf filed its application with FERC on October 15, 2025.",
     "https://public-inspection.federalregister.gov/2025-23711.pdf, https://www.ferc.gov/news-events/events/scoping-meeting-pulaski-project-cp26-11-000-somerset-ky-11242025"),
 rec(PU, "Start [ref]", {"StartYear1": "2029"}, [EIA], "high",
     "Start year 2029. EIA's October 2026 workbook gives 2029 as the in-service year."),
 rec(PU, "FID [ref]", {"FIDStatus": "Pre-FID"}, [EIA], "medium",
     "Pre-FID. EIA's October 2026 workbook says FERC approved the project on October 15, 2026. A FERC approval is not an investment decision, and no decision by TC Energy or Columbia Gulf was found."),
 rec(VK, "Proposal [ref]", {"ProposalYear": "2000", "ProposalMonth": 11}, [FR, OGJ], "high",
     "Proposed November 2000. A Federal Register notice says Columbia Gulf filed on November 3, 2000, under docket CP01-28, and an Oil & Gas Journal article of November 14, 2000 reported the plan."),
 rec(VK, "Construction [ref]", {"ConstructionYear": "2001"}, [NGI, EIA], "medium",
     "Construction year 2001, worked out from two dates. FERC approved the lateral in early February 2001, Natural Gas Intelligence reported, and EIA lists it as completed on September 1, 2001. No source gives the start of construction."),
 rec(VK, "Start [ref]", {"StartYear1": "2001", "StartMonth1": 9}, [EIA], "high",
     "Start September 2001. EIA's October 2026 workbook, Historical Projects tab, lists the CGT Vicksburg Lateral as completed on September 1, 2001."),
 rec(ML, "Construction [ref]", {"ConstructionYear": "1953"}, [PHMSA], "medium",
     "Construction year 1953. A PHMSA special permit analysis gives 1953 and 1954 as the construction years of Mainline 100 segments in Tennessee. The line was built by Gulf Interstate Gas Co. No source on when it was proposed was found."),
 rec(ML, "Start [ref]", {"StartYear1": "1954"}, [PHMSA], "medium",
     "Start year 1954. A PHMSA special permit analysis gives 1954 as the construction year of most Mainline 100 segments. No source gives the date of first gas, so this is inferred from the end of construction. Mainline 200 (1958 to 1963) and Mainline 300 (1968 to 1969) were added later."),
]
meta = {"commodity": "gas", "mode": "update",
        "scope": {"csv": "GGIT_gas_snapshot_20261109.csv", "country": "United States", "province": None,
                  "include_pids": ["P6533", "P8124", "P8125", "P8126"], "rows": 4, "project_ids": 4},
        "n_units": len(R), "created": "2026-11-10", "requested_by": "BL",
        "purpose": "Columbia Gulf Transmission timeline cells (proposal, FID, construction, start) for the wiki page"}
json.dump({"meta": meta, "resolutions": R}, open(HERE / "staged_resolutions.json", "w"), indent=1, ensure_ascii=False)
print(len(R), "units")
