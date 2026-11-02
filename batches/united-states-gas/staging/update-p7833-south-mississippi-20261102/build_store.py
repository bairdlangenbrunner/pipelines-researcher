"""Write staged_resolutions.json: P7833 South Mississippi Project after Energy Transfer's binding open season of October 28, 2026 (215 mi, 42 or 36 in, Richland Parish LA to George County MS, in service by March 1, 2030)."""
import json, pathlib
HERE = pathlib.Path(__file__).parent
PGJ = "https://pgjonline.com/news/2026/october/energy-transfer-launches-binding-open-season-for-215-mile-south-mississippi-natural-gas-pipeline"
NOTE = {
    PGJ: "A Pipeline & Gas Journal news story from late October 2026. It says Energy Transfer Interstate Holdings launched a binding open season for the South Mississippi Project on October 28, 2026, closing November 25. The pipeline would run about 215 miles from a proposed receipt point in Richland Parish, Louisiana, to a new delivery point in the George County, Mississippi, area. It would be either 42-inch or 36-inch pipe. The company has binding commitments from anchor shippers, plans to seek FERC approval, and expects service on or before March 1, 2030.",
}
def ver(urls):
    return [{"url": u, "ok": True, "contains_value": True, "name_found": True, "note": NOTE[u]} for u in urls]
ID = {"project_id": "P7833", "pipeline_name": "South Mississippi Project", "wiki": "", "sheet_row": 4221,
      "segment_name": "", "source_language": "en"}
OS24 = "https://pipelines.energytransfer.com/InfoPost/resources/documents/ETIH_South_Mississippi_Project_Open_Season.pdf"
EDA = "https://eastdaley.com/the-burner-tip/midstream-projects-compete-for-new-demand-in-southeast"
EIA = "https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx"
R = [
 {**ID, "ref_col": "Status [ref]", "value_cols": ["Status"], "primary_value_col": "Status",
  "values": {"Status": "proposed"}, "primary_value": "proposed", "current_ref": f"{OS24}, {EDA}",
  "class_in": "HAS_REF", "class_out": "REFS_ADDED", "proposed_refs": [PGJ], "verifications": ver([PGJ]),
  "tier": "high", "independent": True, "evidence_date": "2026-10",
  "researcher_notes": "Status stays proposed. Energy Transfer opened a binding open season on October 28, 2026, and says it has binding commitments from anchor shippers. It has not yet decided to build and has not filed with FERC. The Pipeline & Gas Journal story is added beside the existing refs."},
 {**ID, "ref_col": "Length [ref]", "value_cols": ["LengthKnown", "LengthKnownUnits"], "primary_value_col": "LengthKnown",
  "values": {"LengthKnown": "215", "LengthKnownUnits": "mi"}, "primary_value": "215",
  "current_ref": f"https://www.eia.gov/naturalgas/data.php#pipelines, {EIA}",
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [PGJ], "verifications": ver([PGJ]),
  "tier": "high", "independent": False,
  "researcher_notes": "Changed from 150 miles to 215 miles. The binding open season of October 2026 describes about 215 miles of new pipe from Richland Parish, Louisiana, to George County, Mississippi. The 150 miles came from the EIA August 2026 workbook, which lists 100 to 150 miles from the 2024 non-binding open season. That figure is older than the redesign, so its ref is replaced."},
 {**ID, "ref_col": "Diameter [ref]", "value_cols": ["Diameter", "DiameterUnits"], "primary_value_col": "Diameter",
  "values": {"Diameter": "36, 42", "DiameterUnits": "in"}, "primary_value": "36, 42", "current_ref": "",
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [PGJ], "verifications": ver([PGJ]),
  "tier": "high", "independent": False,
  "researcher_notes": "Diameter was blank. The binding open season says the pipe will be either 42-inch or 36-inch, so both sizes are recorded until the company picks one (Baird 2026-11-02)."},
 {**ID, "ref_col": "Location [ref]",
  "value_cols": ["StartPrefecture/District", "StartState/Province", "EndPrefecture/District", "EndState/Province"],
  "primary_value_col": "StartState/Province",
  "values": {"StartPrefecture/District": "Richland Parish", "StartState/Province": "Louisiana",
             "EndPrefecture/District": "George County", "EndState/Province": "Mississippi"},
  "primary_value": "Louisiana",
  "current_ref": f"https://www.eia.gov/naturalgas/data.php#pipelines, {OS24}, {EIA}",
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [PGJ], "verifications": ver([PGJ]),
  "tier": "high", "independent": False,
  "researcher_notes": "Start changed from Texas to Richland Parish, Louisiana. End filled as George County, Mississippi. The 2024 non-binding open season named receipt points around Carthage, Texas, and EIA still lists Texas as the start. The binding open season of October 2026 names a receipt point in Richland Parish, Louisiana, and a new delivery point in the George County, Mississippi, area. The old refs describe the earlier design, so they are replaced."},
 {**ID, "ref_col": "Start [ref]", "value_cols": ["StartYear1", "StartMonth1"], "primary_value_col": "StartYear1",
  "values": {"StartYear1": "2030", "StartMonth1": "3"}, "primary_value": "2030",
  "current_ref": f"{OS24}, {EDA}",
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [PGJ], "verifications": ver([PGJ]),
  "tier": "high", "independent": False,
  "researcher_notes": "Start changed from April 2028 to March 2030. The 2024 non-binding open season expected service in the second quarter of 2028. The binding open season of October 2026 expects service on or before March 1, 2030."},
 {**ID, "ref_col": "Status [ref]", "value_cols": ["OtherEnglishNames"], "primary_value_col": "OtherEnglishNames",
  "values": {"OtherEnglishNames": "South Mississippi Project"}, "primary_value": "South Mississippi Project",
  "current_ref": f"{OS24}, {EDA}",
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [PGJ], "verifications": ver([PGJ]),
  "tier": "high", "independent": False,
  "researcher_notes": "South Mississippi Project, the company's project name, moves to OtherEnglishNames. The 2024 Energy Transfer open season notice already in Status [ref] and the Pipeline & Gas Journal story added here both use it. This also adds the October 2026 story beside the status refs."},
 {**ID, "ref_col": "", "value_cols": ["PipelineName"], "primary_value_col": "PipelineName",
  "values": {"PipelineName": "South Mississippi Gas Pipeline"},
  "primary_value": "South Mississippi Gas Pipeline", "current_ref": "",
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [], "verifications": [],
  "tier": "high", "independent": False,
  "researcher_notes": "Renamed to the short form South Mississippi Gas Pipeline (Baird 2026-11-02). The company's project name, South Mississippi Project, moves to OtherEnglishNames. The Energy Transfer open season notices and the Pipeline & Gas Journal story in Status [ref] use that name."},
 {**ID, "ref_col": "", "value_cols": ["RouteType", "RouteAccuracy"], "primary_value_col": "RouteType",
  "values": {"RouteType": "Not mapped (but could be — route or endpoints are known)", "RouteAccuracy": "no route"},
  "primary_value": "Not mapped (but could be — route or endpoints are known)", "current_ref": "",
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [], "verifications": [],
  "tier": "high", "independent": False,
  "researcher_notes": "Route type changed from Unavailable to Not mapped (Baird 2026-11-02). The binding open season names both ends, Richland Parish, Louisiana, and the George County, Mississippi, area, so a route can be drawn. No route map was found."},
 {**ID, "ref_col": "", "value_cols": ["ResearcherNotes"], "primary_value_col": "ResearcherNotes",
  "values": {"ResearcherNotes": "Energy Transfer held a non-binding open season in late 2024 for a line of 100 to 150 miles from the Carthage, Texas, area, with 1 billion cubic feet per day of capacity that could grow past 2 billion. A binding open season ran from October 28 to November 25, 2026 for a redesigned line of about 215 miles from Richland Parish, Louisiana, to the George County, Mississippi, area. The pipe will be 36-inch or 42-inch, and service is expected on or before March 1, 2030. Anchor shippers have signed binding commitments. As of November 2026 there was no final investment decision and no FERC filing. The binding notice gives no capacity, so the capacity is still the 2024 figure. No route map found."},
  "primary_value": "", "current_ref": "",
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [], "verifications": [],
  "tier": "high", "independent": False,
  "researcher_notes": "ResearcherNotes rewritten for the October 2026 binding open season (Baird 2026-11-02)."},
]
meta = {"commodity": "gas", "mode": "update",
        "scope": {"csv": "GGIT_gas_snapshot_20261026.csv", "country": "United States", "province": None,
                  "include_pids": ["P7833"], "rows": 1, "project_ids": 1},
        "n_units": len(R), "created": "2026-11-02", "requested_by": "BL",
        "purpose": "P7833 South Mississippi Project after the October 28, 2026 binding open season: length 215 mi, diameter 36, 42 in, renamed South Mississippi Gas Pipeline, route type Not mapped, notes rewritten, Richland Parish LA to George County MS, start March 2030, status ref added"}
json.dump({"meta": meta, "resolutions": R}, open(HERE / "staged_resolutions.json", "w"), indent=1)
print(len(R), "resolutions")
