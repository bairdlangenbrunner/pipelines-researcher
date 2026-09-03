#!/usr/bin/env python3
"""File P4788's FuelSource conflict: align the staged value to the sheet, flag the delta.

The shard staged values={"FuelSource": "West-East Gas Pipeline"} -- a paraphrase, not the
sheet's actual cell -- and classed it REFS_ADDED, i.e. "value is right, just add a ref".
The live 2026-08-26 snapshot reads 'Sichuan-Shanghai gas pipeline/West-East gas pipeline II',
and the operator's own emergency-response plan CONTRADICTS half of that. Per the standing
rule, ResearcherNotes documents the divergence and defers the recommendation -- we flag,
we do not overwrite. Idempotent.
"""
import json
from pathlib import Path

P = Path("shards/batch_03.json")
DOC = json.loads(P.read_text())
recs = DOC["resolutions"] if isinstance(DOC, dict) else DOC

SHEET_VAL = "Sichuan-Shanghai gas pipeline/West-East gas pipeline II"
EVID = (
 "GAS-SOURCE CONFLICT, FLAGGED NOT APPLIED. Sheet FuelSource reads "
 f"'{SHEET_VAL}' (live 2026-08-26 snapshot). The operator's own emergency-response plan "
 "for exactly this section states verbatim: '本项目赣州南支线从西二线149#阀室或西三线瑞金分输清管站"
 "引出气源' -- this branch draws gas from the West-East Gas Pipeline II valve chamber #149 OR the "
 "West-East Gas Pipeline III Ruijin pig-launcher station. Corroborated by the endpoint sentence, "
 "which terminates the line at 西三线瑞金分输站 (the WEP3 Ruijin station, noted as pre-existing). "
 "Term counts across the full 494,223-char extraction: 西二线 (WEP2) 2, 西三线 (WEP3) 3, "
 "川气东送 (Sichuan-Shanghai) 0, 川气 0, 西气东输 0. So: WEP2 is CORROBORATED; WEP3 is MISSING from "
 "the sheet; and Sichuan-Shanghai is UNSUPPORTED by the most specific source available for this "
 "segment. Caveat stated plainly: absence in one document is not proof of absence in fact -- a "
 "province-level network can be fed from more than one trunk, and this plan describes THIS "
 "branch's feed points, not the whole Jiangxi grid's. That is why this is filed as a question for "
 "the researcher rather than a value change. Suggested value IF confirmed: "
 "'West-East gas pipeline II/West-East gas pipeline III'. NOT staged as an edit."
)

n_val = n_sent = 0
for r in recs:
    if r.get("project_id") == "P4788" and r.get("ref_col") == "FuelSource [ref]":
        if r.get("values", {}).get("FuelSource") != SHEET_VAL:
            r.setdefault("values", {})["FuelSource"] = SHEET_VAL
            n_val += 1
        notes = (r.get("researcher_notes") or "").rstrip()
        if "GAS-SOURCE CONFLICT" not in notes:
            r["researcher_notes"] = (notes + " || " if notes else "") + EVID
        # the ref itself is legitimate: it documents this branch's gas source.
        r["tier"] = "medium"

if not any(x.get("project_id") == "P4788" and x.get("ref_col") == "__VALIDITY__" for x in recs):
    row = next((x.get("sheet_row") for x in recs if x.get("project_id") == "P4788"), None)
    recs.append({
        "project_id": "P4788",
        "sheet_row": row,
        "ref_col": "__VALIDITY__",
        "value_cols": [],
        "values": {},
        "proposed_refs": [],
        "verifications": [],
        "class_out": "UNRESOLVED",
        "tier": "presumed",
        "researcher_notes": EVID + (
          " Filed by the orchestrator, not by the batch-03 subagent: the shard had staged a "
          "paraphrased value ('West-East Gas Pipeline') and classed the unit REFS_ADDED, which "
          "would have implied the sheet value was confirmed. Source document is the local copy "
          "quannan_ganzhounan.pdf (11,461,354 bytes, author 赣安 谢玉锦, created 2024-11-14); the "
          "live URL 403s today, which is an access failure and not a deletion."),
    })
    n_sent = 1

P.write_text(json.dumps(DOC, ensure_ascii=False, indent=2))
print(f"values aligned to sheet: {n_val}")
print(f"__VALIDITY__ filed:      {n_sent}")
print(f"records now:             {len(recs)}")
