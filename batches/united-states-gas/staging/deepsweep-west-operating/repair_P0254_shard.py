#!/usr/bin/env python3
"""Re-encode the P0254 shard onto the contract. NO research is added or changed.

The subagent for P0254 wrote good research in a schema it invented: `column` instead of
`ref_col`, `class_out: "FILLED"` (not one of the four `build_ref_workbook.py` accepts),
`proposed_refs` as objects instead of URL strings, and validity `contested` as a prose
narrative instead of the {column: proposed value} map the Backend paste surface reads.
The object-shaped refs crashed `merge_deepsweep_shards.py` outright
(`merge_qc.origin_host` -> 'dict' object has no attribute 'strip'); the rest would have
been dropped silently at build.

Every mapping below is mechanical and reversible:
  * proposed_refs [{url, verified, verifier_result, note}] -> ["<url>"] plus a matching
    verifications[] built from the fields the agent already recorded. `verified: true`
    with a "ok=true, status=200" verifier_result is transcribed as ok/contains_value,
    and name_found only where the string says so.
  * fills[].column -> ref_col, from the worklist's own unit list for P0254.
  * class_out "FILLED" -> "REFS_ADDED" (a sourced value with verified refs; the merge sets
    class_in="FILL" itself). UNRESOLVED records keep their class and notes verbatim.
  * validity[].contested prose -> researcher_notes (prepended, verbatim); `contested`
    becomes {} because the agent proposed no replacement cell value in any of the four
    findings — it explicitly declined to on Length and Owner. `verdict` is set to
    "concern", which is what all four say in prose.
The pre-repair shard is kept beside it as P0254.json.preraw.
"""
import json
import re
import shutil
from pathlib import Path

STG = Path(__file__).resolve().parent
SHARD = STG / "rows" / "P0254.json"

REF_COL = {
    "ProposalYear / ProposalMonth": "Proposal [ref]",
    "ConstructionYear / ConstructionMonth": "Construction [ref]",
    "Pressure / PressureUnits": "Pressure [ref]",
    "FuelSource": "FuelSource [ref]",
    "Operator [ref] (operators_owners tab)": "Operator [ref]",
}


def split_refs(items):
    """[{url,...}] or ["url"] -> (["url"], [verification]) — verifications only from dicts."""
    urls, verifs = [], []
    for it in items or []:
        if isinstance(it, str):
            urls.append(it)
            continue
        url = (it.get("url") or "").strip()
        if not url:
            continue
        urls.append(url)
        vr = it.get("verifier_result") or ""
        verifs.append({
            "url": url,
            "ok": bool(it.get("verified")) and "ok=true" in vr.lower(),
            "contains_value": bool(it.get("verified")),
            "name_found": "name_found=true" in vr.lower(),
            "note": " | ".join(x for x in (it.get("note"), vr) if x),
        })
    return urls, verifs


def main():
    j = json.loads(SHARD.read_text())
    if not SHARD.with_suffix(".json.preraw").exists():
        shutil.copy2(SHARD, str(SHARD) + ".preraw")

    units = {u["ref_col"]: u for u in json.loads((STG / "worklist.json").read_text())["units"]
             if u["project_id"] == "P0254"}

    for v in j.get("validity") or []:
        urls, verifs = split_refs(v.get("proposed_refs"))
        v["proposed_refs"] = urls
        if verifs:
            v["verifications"] = (v.get("verifications") or []) + verifs
        prose = v.pop("contested", None)
        if isinstance(prose, str) and prose.strip():
            col = v.pop("column", "") or ""
            head = f"CONTESTED ({col}): " if col else "CONTESTED: "
            v["researcher_notes"] = head + prose.strip() + "\n\n" + (v.get("researcher_notes") or "")
        v.pop("column", None)
        v["contested"] = {}
        v.setdefault("verdict", "concern")

    for f in j.get("fills") or []:
        col = f.pop("column", "")
        ref_col = REF_COL.get(col)
        if not ref_col:
            raise SystemExit(f"unmapped fills[] column {col!r} — extend REF_COL")
        u = units[ref_col]
        urls, verifs = split_refs(f.get("proposed_refs"))
        f["proposed_refs"] = urls
        if verifs:
            f["verifications"] = (f.get("verifications") or []) + verifs
        f["ref_col"] = ref_col
        f["sheet_row"] = u["sheet_row"]
        f["value_cols"] = u["value_cols"]
        f["primary_value_col"] = u["primary_value_col"]
        vals = f.pop("value", None)
        f["values"] = vals if isinstance(vals, dict) else {}
        f["primary_value"] = f["values"].get(u["primary_value_col"], "")
        if f.get("class_out") == "FILLED":
            f["class_out"] = "REFS_ADDED" if urls else "UNRESOLVED"

    SHARD.write_text(json.dumps(j, indent=1, ensure_ascii=False) + "\n")
    print(f"repaired {SHARD}: {len(j.get('validity') or [])} validity, "
          f"{len(j.get('fills') or [])} fills")


if __name__ == "__main__":
    main()
