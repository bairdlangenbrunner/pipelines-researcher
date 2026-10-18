"""Write staged_resolutions.json (P7861, P7862 fixes) and staged_new.json (the interstate service row)."""
import json, pathlib
HERE = pathlib.Path(__file__).parent
FERC = "https://www.ferc.gov/sites/default/files/2026-03/CP25-531-000.pdf"
FR_APP = "https://www.federalregister.gov/d/2025-15873"
FR_AMD = "https://www.federalregister.gov/d/2026-00407"
ED = "https://eastdaley.com/the-burner-tip/company-plans-project-to-convert-permian-line-to-interstate-service"
PGJ = "https://pgjonline.com/news/2025/july/producers-midstream-to-convert-permian-pipeline-for-interstate-gas-service"
CO = "https://producersmidstream.com/palo-duro-pipeline-project-notice-of-binding-open-season/"
OGJ = "https://www.ogj.com/pipelines-transportation/pipelines/article/55300432/producers-midstream-launches-open-season-for-service-on-palo-duro-pipeline"
SUMM = "https://www.ferc.gov/news-events/news/summaries-march-2026-commission-meeting"
NOTE = {
    FERC: "The FERC order issuing certificates for docket CP25-531, dated March 19, 2026 (194 FERC 61,220). It describes the 150 mile, 16 and 20 inch Header Pipeline from Washita County, Oklahoma, to Roberts County, Texas, as part of the gathering system that Palo Duro Pipelines (Texas Gathering) owns and operates. It describes the 275 mile, 16 inch PD Pipeline from Nolan County to Wheeler County, Texas, as currently operating and gathering gas. It approves interstate service on the northern 61 miles of the PD Pipeline plus 80,000 dekatherms a day of leased Header capacity.",
    FR_APP: "The Federal Register notice of the application, published August 20, 2025. It says the application was filed August 1, 2025, as the Lease Agreement Project.",
    FR_AMD: "The Federal Register notice of the amended application, published January 13, 2026.",
    ED: "An East Daley Analytics note from July 2025. It says the Palo Duro Pipeline is already operational, gives 80 million cubic feet a day of design capacity, and says the line could support 125 to 150 megawatts of data center load if fully dedicated.",
    PGJ: "A Pipeline and Gas Journal article from July 2025, citing East Daley Analytics, on the conversion to interstate service and its data center angle.",
    CO: "The Producers Midstream notice of the binding open season, dated June 30, 2025.",
    OGJ: "An Oil and Gas Journal article from June 30, 2025, on the open season.",
    SUMM: "The FERC summary of its March 2026 meeting, which lists the Palo Duro Transmission certificate order.",
}
def ver(urls):
    return [{"url": u, "ok": True, "contains_value": True, "name_found": True, "note": NOTE[u]} for u in urls]
def res(pid, row, seg, ref_col, values, refs, notes, class_in="FILL", class_out="REFS_ADDED", tier=None, current=""):
    pub = {u.split("/")[2] for u in refs}
    return {"project_id": pid, "pipeline_name": "Producers Midstream Gas Pipeline", "wiki": "", "sheet_row": row,
            "segment_name": seg, "ref_col": ref_col, "value_cols": list(values), "primary_value_col": list(values)[0],
            "values": values, "primary_value": list(values.values())[0], "current_ref": current,
            "class_in": class_in, "class_out": class_out, "proposed_refs": refs, "verifications": ver(refs),
            "tier": tier or ("high" if len(pub) > 1 else "medium"), "independent": len(pub) > 1,
            "source_language": "en", "researcher_notes": notes}
H, P = "Residue Header", "Palo Duro Gas Pipeline"
R = [
 res("P7861", 4248, H, "Status [ref]", {"Status": "operating"}, [FERC],
     "Status stays operating. The FERC order of March 19, 2026, says Palo Duro Pipelines (Texas Gathering) owns and operates the Header Pipeline today.", class_out="REFS_ADDED", tier="high"),
 res("P7861", 4248, H, "PipelineType [ref]", {"PipelineType": "gathering"}, [FERC],
     "Changed from transmission to gathering. The FERC order calls the Header Pipeline part of the non-jurisdictional Anadarko Gathering System, which has more than 3,000 miles of pipe and about 2,750 connected wells. Only a leased slice of its capacity becomes interstate service, and that slice is the new row for the interstate project."),
 res("P7861", 4248, H, "Length [ref]", {"LengthKnown": "150", "LengthKnownUnits": "mi"}, [FERC],
     "Changed from 275 miles to 150 miles. The 275 miles belonged to the Palo Duro line in P7862 and was copied here by mistake, so the same pipe was counted twice. The FERC order gives the Header Pipeline as about 150 miles. The current route file for this row measures about 142 miles, which agrees."),
 res("P7861", 4248, H, "Diameter [ref]", {"Diameter": "16, 20", "DiameterUnits": "in"}, [FERC],
     "Changed from 16 to 16 and 20 inches, as the FERC order gives both sizes. Units changed from inches to in, the form the rest of the sheet uses, so the millimeter column fills."),
 res("P7861", 4248, H, "Location [ref]", {"StartLocation": "Washita County", "StartState/Province": "Oklahoma", "EndLocation": "Roberts County", "EndState/Province": "Texas"}, [FERC],
     "The old start and end, Waha in the Permian Basin to Wheeler County, described the Palo Duro line, not this one. The FERC order says the Header Pipeline runs from Washita County, Oklahoma, to Roberts County, Texas. The current route file already runs between those two counties. The pipe crosses into Oklahoma, so the state columns change."),
 res("P7861", 4248, H, "Proposal [ref]", {"ProposalYear": "", "ProposalMonth": "", "StartYear1": ""}, [FERC],
     "Cleared the proposal date of June 2025 and the start year of 2026. Those are the dates of the interstate service project, which now has its own row. The Header Pipeline was already operating when the project was proposed. No source found gives the year it was built, so the start year is left blank."),
 res("P7861", 4248, H, "DataCenter [ref]", {"DataCenter": "", "DataCenter [ref]": "", "DataCenterNotes": ""}, [PGJ],
     "Data center tag removed. The data center news is about the interstate service project, which now has its own row and carries the tag. Keeping the tag here as well would count the same demand twice."),
 res("P7861", 4248, H, "Owner [ref]", {"Owner1": "Palo Duro Pipelines (Texas Gathering) LP"}, [FERC],
     "Owner changed from Tailwater Capital to Palo Duro Pipelines (Texas Gathering) LP. The FERC order says this company owns and operates the Header Pipeline. Tailwater Capital is an investor further up the chain, not the company that holds the pipe. The share stays at 100 percent."),
 res("P7862", 4249, P, "Status [ref]", {"Status": "operating", "ProposalYear": "", "StartYear1": ""}, [FERC, ED],
     "Changed from proposed to operating. The FERC order says PD Transmission operates the 275 mile line today and that it currently gathers gas. An East Daley Analytics note from July 2025 says the pipeline is already operational. Two publishers agree. The proposal year of 2025 and start year of 2026 belonged to the interstate service project, which now has its own row, so they are cleared. No source found gives the year the line was built.", tier="high"),
 res("P7862", 4249, P, "Location [ref]", {"StartLocation": "Nolan County", "EndLocation": "Wheeler County"}, [FERC],
     "Start and end were blank. The FERC order says the line runs from Nolan County to Wheeler County, Texas. The open season names a receipt meter near the southern end in Nolan County, and the route file ends within a fraction of a mile of it."),
 res("P7862", 4249, P, "PipelineType [ref]", {"PipelineType": "both transmission and gathering"}, [FERC],
     "Changed from transmission to both transmission and gathering. The FERC order says the line currently gathers gas. Under the amended plan the northern 61 miles, in Childress, Collingsworth and Wheeler counties, become interstate transmission, and the southern part is to be sold to an affiliate and kept as gathering. The row stays whole rather than being split in two."),
]
meta = {"commodity": "gas", "mode": "update",
        "scope": {"csv": "GGIT_gas_snapshot_20261018.csv", "country": "United States", "province": None,
                  "include_pids": ["P7861", "P7862"], "rows": 2, "project_ids": 2},
        "n_units": len(R), "created": "2026-10-17", "requested_by": "BL",
        "purpose": "Palo Duro fixes: P7861 Residue Header to gathering, 150 miles, Washita County OK to Roberts County TX, data center tag removed; P7862 Palo Duro to operating; interstate service project staged as a new row in staged_new.json"}
json.dump({"meta": meta, "resolutions": R}, open(HERE / "staged_resolutions.json", "w"), indent=1)

new = {"slug": "palo-duro-lease-agreement-project", "class": "new_row", "name": "Palo Duro Lease Agreement Project (Palo Duro Transmission)", "matched_project_id": "",
 "values": {"PipelineName": "Producers Midstream Gas Pipeline", "SegmentName": "Palo Duro Lease Agreement Project", "Status": "proposed", "Fuel": "Gas",
  "PipelineType": "transmission", "CountriesOrAreas": "United States", "StartCountryOrArea": "United States", "EndCountryOrArea": "United States",
  "StartLocation": "Childress County", "StartState/Province": "Texas", "EndLocation": "Washita County", "EndState/Province": "Oklahoma",
  "ProposalYear": "2025", "ProposalMonth": "6", "Capacity": "80000", "CapacityUnits": "Dth/d",
  "LengthKnown": "0", "LengthKnownUnits": "mi", "Diameter": "16", "DiameterUnits": "in",
  "RouteType": "Capacity expansion only", "RouteAccuracy": "no route",
  "Owner": "Palo Duro Transmission LP",
  "DataCenter": "yes", "DataCenterNotes": "A Pipeline and Gas Journal article from July 2025, citing East Daley Analytics, says the project targets demand from data centers, petrochemical plants and power generators. It says that if the line were fully dedicated to data center use it could support 125 to 150 megawatts of load. The company notice mentions behind the meter uses tied to artificial intelligence. No specific data center is named."},
 "refs": {"Status [ref]": [FERC, SUMM], "Proposal [ref]": [CO, OGJ, FR_APP], "Capacity [ref]": [FERC, ED], "Location [ref]": [FERC, FR_AMD],
          "Length [ref]": [FERC], "Diameter [ref]": [FERC], "PipelineType [ref]": [FERC], "DataCenter [ref]": [PGJ, ED]},
 "verifications": ver([FERC, SUMM, CO, OGJ, FR_APP, FR_AMD, ED, PGJ]),
 "tier": "high", "independent": True, "source_language": "en", "monitor_reason": "",
 "researcher_notes": "This row is the project that turns existing Palo Duro pipe into interstate service. It builds no new pipe. Producers Midstream opened a binding open season on June 30, 2025, and Palo Duro Transmission and Palo Duro Pipelines (Texas Gathering) applied to FERC on August 1, 2025, under docket CP25-531. They amended the plan on December 22, 2025. FERC issued the certificates on March 19, 2026, and the companies accepted them on April 7, 2026. Under the approved plan, Palo Duro Transmission offers interstate service on the northern 61 miles of the Palo Duro line in P7862, in Childress, Collingsworth and Wheeler counties, plus 80,000 dekatherms a day of capacity leased for ten years on the Header Pipeline in P7861. The Header Pipeline connects to eight interstate pipelines, including Northern Natural, Transwestern, Natural Gas Pipeline Company of America, ANR and Panhandle Eastern. The only shipper is Scurry Downstream, an affiliate of Producers Midstream, holding all of the capacity. Length is 0 because the pipe is already counted in P7861 and P7862. Status is proposed because no sign was found that interstate service has started. A search of the FERC eLibrary on October 17, 2026, found no tariff filing or start of service notice after the April acceptance, and FERC requires a filing within ten days of taking over the leased capacity. The company had aimed for the first quarter of 2026, so start year is left blank. End location is the Oklahoma end of the Header Pipeline. Gas can be delivered at interconnects along its length, so Washita County is the far end, not a single delivery point.",
 "project_id": ""}
json.dump({"meta": {**meta, "mode": "discovery", "purpose": "the Palo Duro interstate service project as a new row (CP25-531)", "n_units": 1}, "candidates": [new], "converted_to_alias": []},
          open(HERE / "staged_new.json", "w"), indent=1)
print(len(R), "resolutions; 1 new row")
