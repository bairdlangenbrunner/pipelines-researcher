#!/usr/bin/env python3
"""Three orchestrator findings on P4788: coordinate transcription, length tension, FuelSource.

(a) The existing __VALIDITY__ hands MZ redraw coordinates rendered from DMS as if decimal.
    'E114.49/N25.26' for the Xinfeng station is 38.7 km from the document's actual
    E114 deg 49'21.19"/N25 deg 26'8.07" = 114.82255/25.43558. Ruijin's 'E116.01/N25.95'
    happens to land 0.4 km off the true 116.00923/25.94623, so only one is materially wrong --
    but a 38.7 km error in a redraw anchor is worth correcting before MZ uses it.

(b) The batch refuted the aggregate-length hypothesis because the document attributes
    340.3 km to the 信丰-瑞金段 specifically. That attribution finding stands. What does NOT
    follow is the batch's stronger conclusion that the sheet length is therefore correct and
    only the route is wrong: the two named terminal stations are 131.8 km apart great-circle,
    so 340.3 km implies 2.58x sinuosity against the 1.1-1.4x typical of a trunk corridor.
    Both figures are now in question. Recorded as tension, not as a value change.

(c) FuelSource conflict (see file_fuelsource_conflict.py for the evidence).

Idempotent.
"""
import json
from pathlib import Path

P = Path("shards/batch_03.json")
DOC = json.loads(P.read_text())
recs = DOC["resolutions"]

COORD_FIX = (
 " || ORCHESTRATOR CORRECTION 2026-08-26 -- REDRAW ANCHORS, read before using the coordinates "
 "above. Those coordinates were transcribed from the document's DMS as if they were decimal "
 "degrees. The document reads 信丰分输站 E114°49'21.19\"/N25°26'8.07\" and 瑞金分输站 "
 "E116°0'33.24\"/N25°56'46.44\". Correct decimals: Xinfeng 114.82255, 25.43558; Ruijin "
 "116.00923, 25.94623. The stated 'E114.49/N25.26' is 38.7 km from the true Xinfeng station; "
 "'E116.01/N25.95' happens to fall 0.4 km from the true Ruijin station. Use the decimals given "
 "here. || SECOND CORRECTION, same session -- the length conclusion above is too strong. That "
 "the document attributes 340.3 km to the 信丰-瑞金段 itself (and not to another segment or to "
 "the 537.5 km four-branch total) is confirmed and stands. But the two named terminal stations "
 "are only 131.8 km apart great-circle, so 340.3 km implies a sinuosity of 2.58x, well above the "
 "1.1-1.4x typical of a trunk corridor -- even allowing for the documented detours (沿赣龙铁路绕行"
 "城市规划区, 经河坑村/七堡村, 先向北再向东). So 'the sheet is right, only the route is wrong' is NOT "
 "established: the 31.75 km GEM route is wrong either way, but 340.3 km is itself now open. A "
 "redraw to the documented corridor should be expected to measure roughly 140-190 km, and if it "
 "does, LengthKnown needs its own source rather than this document alone. Not adjudicated here."
)

n = 0
for r in recs:
    if (r.get("project_id") == "P4788" and r.get("ref_col") == "__VALIDITY__"
            and "NAME CORRUPTION" in (r.get("researcher_notes") or "")):
        if "ORCHESTRATOR CORRECTION" not in r["researcher_notes"]:
            r["researcher_notes"] = r["researcher_notes"].rstrip() + COORD_FIX
            n += 1

FUEL = next((r for r in recs if r.get("project_id") == "P4788"
             and r.get("ref_col") == "FuelSource [ref]"), None)
already = any(r.get("project_id") == "P4788" and r.get("ref_col") == "__VALIDITY__"
              and "GAS-SOURCE CONFLICT" in (r.get("researcher_notes") or "") for r in recs)
m = 0
if FUEL and not already:
    recs.append({
        "project_id": "P4788",
        "sheet_row": FUEL.get("sheet_row"),
        "ref_col": "__VALIDITY__",
        "value_cols": [], "values": {}, "proposed_refs": [], "verifications": [],
        "class_out": "UNRESOLVED", "tier": "presumed",
        "researcher_notes": (FUEL.get("researcher_notes") or "").split(" || ", 1)[-1] + (
          " || Filed by the orchestrator, not by the batch-03 subagent: the shard had staged a "
          "paraphrased value ('West-East Gas Pipeline') rather than the sheet's actual cell and "
          "classed the unit REFS_ADDED, which would have implied the sheet value was confirmed. "
          "The staged value has been realigned to the sheet's actual text; no value change is "
          "proposed. Source is the local copy quannan_ganzhounan.pdf (11,461,354 bytes, author "
          "赣安 谢玉锦, created 2024-11-14); the live URL 403s today, an access failure not a deletion."),
    })
    m = 1

P.write_text(json.dumps(DOC, ensure_ascii=False, indent=2))
print(f"coordinate/length correction appended: {n}")
print(f"FuelSource __VALIDITY__ filed:         {m}")
print(f"records now:                           {len(recs)}")
