#!/usr/bin/env python3
"""Emit one per-PID research brief for a *targeted* ref-sweep research pass.

Annual-update mode (§7) seeds a ref baseline from the worklist but runs no ref
*research* — so blank/dead `[ref]` cells stay red (class_out UNRESOLVED / DEAD_LINK).
This script scopes a follow-up ref sweep to exactly those gap units and packages each
pipeline's work into a brief a single research subagent can act on: the units needing a
source (value + current dead ref) plus the gem.wiki outbound citations to start from.

It reads staged_resolutions.json (the merged baseline) + wiki_citations.json and writes
`<staging>/ref_shards/_briefs/<PID>.json` (one per in-scope PID) + `_manifest.json`.
Research is done by subagents; each writes `<staging>/ref_shards/<PID>.json`, which
merge_ref_shards.py then folds back onto staged_resolutions.prior.json.

Default scope = the gap classes (UNRESOLVED, DEAD_LINK). Pass --classes to widen (e.g.
also re-verify REVERIFIED) or narrow.

Usage:
    python scripts/build_refsweep_briefs.py --staging batches/iraq-gas/staging/annual/
"""
import argparse, json, os, collections


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    ap.add_argument("--classes", default="UNRESOLVED,DEAD_LINK",
                    help="comma list of class_out values to research (default gap classes)")
    args = ap.parse_args()
    S = args.staging.rstrip("/")
    want = {c.strip() for c in args.classes.split(",") if c.strip()}

    res = json.load(open(os.path.join(S, "staged_resolutions.json")))["resolutions"]
    wc_path = os.path.join(S, "wiki_citations.json")
    cites = {}
    if os.path.exists(wc_path):
        cites = json.load(open(wc_path)).get("pages", {})

    gaps = [r for r in res
            if r.get("class_in") in ("HAS_REF", "MISSING_REF") and r.get("class_out") in want]

    by_pid = collections.OrderedDict()
    for r in gaps:
        by_pid.setdefault(r.get("project_id", ""), []).append(r)

    out_dir = os.path.join(S, "ref_shards", "_briefs")
    os.makedirs(out_dir, exist_ok=True)

    manifest = []
    for pid, rs in by_pid.items():
        b = rs[0]
        seed = []
        for c in (cites.get(pid, {}) or {}).get("citations", []) or []:
            seed.append({"url": c.get("url", ""), "link_text": c.get("link_text", ""),
                         "context": c.get("context", "")})
        units = [{
            "ref_col": r.get("ref_col", ""),
            "sheet_row": r.get("sheet_row", ""),
            "segment_name": r.get("segment_name", ""),
            "value_cols": r.get("value_cols", []),
            "values": r.get("values", {}),
            "primary_value": r.get("primary_value", ""),
            "current_ref": r.get("current_ref", ""),
            "class_out": r.get("class_out", ""),   # DEAD_LINK = had a ref that died; UNRESOLVED = never had one
        } for r in rs]
        brief = {
            "project_id": pid,
            "pipeline_name": b.get("pipeline_name", ""),
            "wiki": b.get("wiki", ""),
            "n_units": len(units),
            "units": units,
            "seed_citations": seed,   # gem.wiki OUTBOUND links — start here; never cite gem.wiki itself
        }
        json.dump(brief, open(os.path.join(out_dir, f"{pid}.json"), "w"), indent=1, ensure_ascii=False)
        manifest.append({"project_id": pid, "pipeline_name": b.get("pipeline_name", ""),
                         "n_units": len(units), "n_seed_citations": len(seed)})

    json.dump({"staging": S, "classes": sorted(want), "n_pids": len(manifest),
               "n_units": len(gaps), "briefs": manifest},
              open(os.path.join(S, "ref_shards", "_manifest.json"), "w"), indent=1)
    print(f"wrote {len(manifest)} briefs to {out_dir}")
    print(f"  {len(gaps)} gap units | classes={sorted(want)}")
    for m in manifest:
        print(f"    {m['project_id']} | {m['pipeline_name'][:40]:40} | {m['n_units']} units | {m['n_seed_citations']} seed cites")


if __name__ == "__main__":
    main()
