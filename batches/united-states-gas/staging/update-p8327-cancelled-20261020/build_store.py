"""Write staged_resolutions.json: P8327 Ellendale lateral dropped from the Bakken East design (cancelled), with its March 2026 length and diameter."""
import json, pathlib
HERE = pathlib.Path(__file__).parent
FOOL = "https://www.fool.com/earnings/call-transcripts/2026/05/07/mdu-mdu-q1-2026-earnings-call-transcript/"
APR = "https://elibrary.ferc.gov/eLibrary/filedownload?fileid=05195FAF-D749-CCB9-9E51-9D9B54A00000"
MAR = "https://elibrary.ferc.gov/eLibrary/filedownload?fileid=D5DC66BB-2D81-CDC1-9DA6-9CE8E2400000"
NOTE = {
    FOOL: "The Motley Fool transcript of the MDU Resources call on first quarter 2026 results, May 7, 2026. The chief financial officer, Jason Vollmer, says the Ellendale lateral is not on the updated map, that the open season found no interest at that location, and that the lateral is currently not contemplated in the design.",
    APR: "WBI Energy's updated project description filed with the Federal Energy Regulatory Commission (FERC) on April 16, 2026, accession 20260417-5001, docket PF26-4. It says the binding open season changed the project from the March draft and lists about 353 miles of mainline and about 21 miles of laterals: Spring Creek, North Bakken, Stanton, Center and Mapleton. There is no Ellendale lateral.",
    MAR: "WBI Energy's draft Resource Reports 1 and 10 filed with FERC on March 13, 2026, accession 20260313-5242, docket PF26-4. It describes the Ellendale Lateral as 81.6 miles of 20-inch pipe through Barnes, LaMoure and Dickey counties, North Dakota. Figure 1.1.2-1 on page 9 maps it.",
}
def ver(urls, name):
    return [{"url": u, "ok": True, "contains_value": True, "name_found": u != APR, "note": NOTE[u]} for u in urls]
ID = {"project_id": "P8327", "pipeline_name": "Bakken East Pipeline", "wiki": "", "sheet_row": 4581,
      "segment_name": "Jamestown to Ellendale Lateral", "source_language": "en"}
R = [
 {**ID, "ref_col": "__STATUS__", "value_cols": ["Status", "ShelvedCancelledType", "CancelledYear"],
  "primary_value_col": "Status", "values": {"Status": "cancelled", "ShelvedCancelledType": "confirmed", "CancelledYear": "2026"},
  "primary_value": "cancelled", "current_ref": "", "class_in": "STATUS", "class_out": "CHANGE_PROPOSED",
  "current_status": "proposed", "verdict": "change", "proposed_status": "cancelled", "evidence_date": "2026-05",
  "staleness_rule": "", "proposed_refs": [FOOL, APR], "verifications": ver([FOOL, APR], "Ellendale"),
  "tier": "medium", "independent": False,
  "researcher_notes": "Changed from proposed to cancelled. WBI Energy dropped the Ellendale lateral from the Bakken East design after its binding open season. Its updated project description, filed with FERC on April 16, 2026, lists five laterals and no Ellendale lateral. On the MDU Resources earnings call of May 7, 2026, the chief financial officer said the open season found no interest at that location and the lateral is currently not contemplated in the design. He said gas will still reach the Ellendale site through demand along the mainline. Both sources come from the company, so this is medium, not high. A North Dakota Farm Bureau page from 2026 still says extensions to the Spiritwood and Ellendale area are under consideration, and the company said more laterals may come later, so the lateral could return. Cancelled year is 2026, the year of the April filing and the May call."},
 {**ID, "ref_col": "Cancelled [ref]", "value_cols": ["CancelledYear"], "primary_value_col": "CancelledYear",
  "values": {"CancelledYear": "2026"}, "primary_value": "2026", "current_ref": "", "class_in": "FILL", "class_out": "REFS_ADDED",
  "proposed_refs": [FOOL, APR], "verifications": ver([FOOL, APR], "Ellendale"), "tier": "medium", "independent": False,
  "researcher_notes": "Cancelled year 2026. The lateral is in WBI Energy's March 13, 2026, FERC draft and gone from its April 16, 2026, filing. The MDU Resources call of May 7, 2026, confirms it was dropped."},
 {**ID, "ref_col": "Length [ref]", "value_cols": ["LengthKnown", "LengthKnownUnits"], "primary_value_col": "LengthKnown",
  "values": {"LengthKnown": "81.6", "LengthKnownUnits": "mi"}, "primary_value": "81.6",
  "current_ref": "https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx",
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [MAR], "verifications": ver([MAR], "Ellendale Lateral"),
  "tier": "high", "independent": False,
  "researcher_notes": "Changed from 90 miles to 81.6 miles. WBI Energy's March 13, 2026, FERC draft gives the Ellendale Lateral as 81.6 miles: 29.7 miles in Barnes County, 32.4 in LaMoure County and 19.5 in Dickey County. The 90 miles on the sheet appears to add the separate 8.8 mile Spiritwood Lateral near Jamestown. The EIA August 2026 workbook lists only the whole Bakken East project at 350 miles and says nothing about this lateral, so its ref is replaced."},
 {**ID, "ref_col": "Diameter [ref]", "value_cols": ["Diameter", "DiameterUnits"], "primary_value_col": "Diameter",
  "values": {"Diameter": "20", "DiameterUnits": "in"}, "primary_value": "20", "current_ref": "",
  "class_in": "FILL", "class_out": "REFS_ADDED", "proposed_refs": [MAR], "verifications": ver([MAR], "Ellendale Lateral"),
  "tier": "high", "independent": False,
  "researcher_notes": "Diameter was blank. WBI Energy's March 13, 2026, FERC draft gives the Ellendale Lateral as 20-inch pipe."},
 {**ID, "ref_col": "Location [ref]", "value_cols": ["StartLocation", "StartPrefecture/District", "EndPrefecture/District"],
  "primary_value_col": "StartLocation",
  "values": {"StartLocation": "Bakken East mainline valve site MLV24", "StartPrefecture/District": "Barnes County", "EndPrefecture/District": "Dickey County"},
  "primary_value": "Bakken East mainline valve site MLV24",
  "current_ref": "https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx, https://industrialinfo.com/news/article/north-dakotas-500-million-pipeline-funding-paves-way-for-industrial-development--357127, https://pgjonline.com/news/2025/november/wbi-energy-advances-plans-for-bakken-east-gas-pipeline-to-serve-power-data-center-growth",
  "class_in": "FILL", "class_out": "CHANGE_PROPOSED", "proposed_refs": [MAR], "verifications": ver([MAR], "Ellendale Lateral"),
  "tier": "high", "independent": False,
  "researcher_notes": "Start changed from Jamestown to the Bakken East mainline in Barnes County. WBI Energy's March 13, 2026, FERC draft puts the lateral's first valve and pig launcher at milepost 0.0 in Barnes County, in the same site as mainline valve MLV24, and its last one at milepost 81.6 in Dickey County. Jamestown is about 60 km west, in Stutsman County. The route mapped in the same filing starts on the mainline about 14 km from Valley City and ends about 2 km from Ellendale, so the end location stays Ellendale. The EIA August 2026 workbook still describes the lateral as running from Jamestown to Ellendale, which is loose wording for the project as a whole."},
]
meta = {"commodity": "gas", "mode": "update",
        "scope": {"csv": "GGIT_gas_snapshot_20261019.csv", "country": "United States", "province": None,
                  "include_pids": ["P8327"], "rows": 1, "project_ids": 1},
        "n_units": len(R), "created": "2026-10-20", "requested_by": "BL",
        "purpose": "P8327 Ellendale lateral dropped from the Bakken East design after the 2026 open season: status to cancelled (confirmed, 2026), length 81.6 mi, diameter 20 in and start location from the March 2026 FERC draft"}
json.dump({"meta": meta, "resolutions": R}, open(HERE / "staged_resolutions.json", "w"), indent=1)
print(len(R), "resolutions")
