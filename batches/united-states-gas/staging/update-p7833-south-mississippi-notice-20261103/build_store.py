"""Write staged_resolutions.json: add Energy Transfer's own binding open season notice (October 28, 2026) beside the Pipeline & Gas Journal story on P7833's Status, Length, Diameter, Location and Start refs. Values unchanged (Baird 2026-11-02)."""
import json, pathlib
HERE = pathlib.Path(__file__).parent
ET = "https://pipelines.energytransfer.com/InfoPost/resources/documents/ET_Open_Season_Announcement_South_Mississippi_Project%2010_28_2026.pdf"
PGJ = "https://pgjonline.com/news/2026/october/energy-transfer-launches-binding-open-season-for-215-mile-south-mississippi-natural-gas-pipeline"
OS24 = "https://pipelines.energytransfer.com/InfoPost/resources/documents/ETIH_South_Mississippi_Project_Open_Season.pdf"
EDA = "https://eastdaley.com/the-burner-tip/midstream-projects-compete-for-new-demand-in-southeast"
NOTE = ("Energy Transfer's binding open season notice for the South Mississippi Project, a four page PDF posted October 28, 2026 and linked from Florida Gas Transmission notice 74540. "
        "It names a receipt point in Richland Parish, Louisiana, and a new delivery point in the George County, Mississippi, area. It describes about 215 miles of either 42-inch or 36-inch pipe, "
        "says the company will seek FERC approval and has binding commitments from anchor shippers, and expects service on or before March 1, 2030. Page 1 carries a map of the project.")
def ver():
    return [{"url": ET, "ok": True, "status": 200, "contains_value": True, "name_found": True, "note": NOTE}]
ID = {"project_id": "P7833", "pipeline_name": "South Mississippi Gas Pipeline", "wiki": "", "sheet_row": 4221,
      "segment_name": "", "source_language": "en"}
def line(ref_col, values, primary, current_ref, note):
    return {**ID, "ref_col": ref_col, "value_cols": list(values), "primary_value_col": primary,
            "values": values, "primary_value": values[primary], "current_ref": current_ref,
            "class_in": "HAS_REF", "class_out": "REFS_ADDED", "proposed_refs": [ET], "verifications": ver(),
            "tier": "high", "independent": False, "evidence_date": "2026-10-28", "researcher_notes": note}
R = [
 line("Status [ref]", {"Status": "proposed"}, "Status", f"{OS24}, {EDA}, {PGJ}",
      "Status stays proposed. The company's own binding open season notice of October 28, 2026 is added beside the news story. It says the company will decide whether to build after bids close on November 25, 2026."),
 line("Length [ref]", {"LengthKnown": "215", "LengthKnownUnits": "mi"}, "LengthKnown", PGJ,
      "Length stays 215 miles. The company's binding open season notice states about 215 miles of pipe and is added beside the news story."),
 line("Diameter [ref]", {"Diameter": "36, 42", "DiameterUnits": "in"}, "Diameter", PGJ,
      "Diameter stays 36, 42 inches. The company's binding open season notice says either 42-inch or 36-inch pipe and is added beside the news story."),
 line("Location [ref]", {"StartPrefecture/District": "Richland Parish", "StartState/Province": "Louisiana",
                         "EndPrefecture/District": "George County", "EndState/Province": "Mississippi"}, "StartState/Province", PGJ,
      "Start and end stay as recorded. The company's binding open season notice names a receipt point in Richland Parish, Louisiana, and a delivery point in George County, Mississippi, and is added beside the news story."),
 line("Start [ref]", {"StartYear1": "2030", "StartMonth1": "3"}, "StartYear1", PGJ,
      "Start stays March 2030. The company's binding open season notice expects service on or before March 1, 2030 and is added beside the news story."),
]
meta = {"commodity": "gas", "mode": "update",
        "scope": {"csv": "GGIT_gas_snapshot_20261026.csv", "country": "United States", "province": None,
                  "include_pids": ["P7833"], "rows": 1, "project_ids": 1},
        "n_units": len(R), "created": "2026-11-03", "requested_by": "BL",
        "purpose": "P7833: add Energy Transfer's binding open season notice as a second ref on Status, Length, Diameter, Location and Start"}
json.dump({"meta": meta, "resolutions": R}, open(HERE / "staged_resolutions.json", "w"), indent=1)
print(len(R), "resolutions")
