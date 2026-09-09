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

Each brief carries a `contract` block (standing rule 4e). The deep-sweep leg's per-unit
emit obligation lives in `.claude/workflows/critical-deep-sweep.js`; THIS leg has no saved
workflow, so its contract was whatever the dispatching orchestrator happened to write —
which is exactly the hole that let the four 2026-09 US gas batches drop 218 MISSING_REF
units. Putting it in the brief means the obligation ships with the work, not with the
prompt. Pass it to the subagent verbatim.

Usage:
    python scripts/build_refsweep_briefs.py --staging batches/iraq-gas/staging/annual/
"""
import argparse, json, os, collections

OUT_SUB = "ref_shards"


# Standing rule 4(e), verbatim in every brief so the obligation travels with the work
# rather than with whatever prompt happens to dispatch it (see the module docstring).
CONTRACT = [
    "EVERY unit below is OWED a record — there is no such thing as a unit that needed "
    "no work. The sheet already holds the value; its [ref] cell is empty; sourcing it is "
    "what this leg is FOR.",
    "Sources AGREEING with the recorded value is the deliverable, not a no-op: emit "
    "class_out='REFS_ADDED' carrying the SAME value plus the verified ref(s) that state "
    "it. 'Confirmed as recorded' in your summary and nowhere machine-readable is "
    "indistinguishable from never having checked it.",
    "A source agreeing within rounding IS a ref (51.97 mi + 0.5 mi against a recorded 52; "
    "38.5 against 39): REFS_ADDED at medium/high with the discrepancy in researcher_notes, "
    "plus a validity `spec` concern if the gap is material. UNRESOLVED means nothing was "
    "found — never that something slightly different was found.",
    "UNRESOLVED is a legitimate outcome ONLY with researcher_notes saying what you "
    "searched. An empty UNRESOLVED reads exactly like a dropped unit and is treated as one.",
    "Read every document you open to exhaustion, for EVERY column and sibling row — one "
    "FERC notice routinely sources Length, Diameter, Cost, Construction and Start at once.",
    "Two independent sources per data point is the target; the same wire story republished "
    "does not count, and NEVER cite GEM (gem.wiki, globalenergymonitor.org) or the banned "
    "aggregators (abarrelfull, theodora.com). Never fabricate a URL.",
    "Key every record with `ref_col` and a `class_out` of REFS_ADDED / REVERIFIED / "
    "UNRESOLVED / DEAD_LINK. Anything else is dropped without a word at workbook build — "
    "the research is done and vanishes.",
    "BEFORE YOU FINISH run the coverage_gate command above. It names every unit you left "
    "unreported and every record that cannot merge. It is blocking: do not finish red.",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    ap.add_argument("--classes", default="UNRESOLVED,DEAD_LINK",
                    help="comma list of class_out values to research (default gap classes)")
    ap.add_argument("--from-coverage", metavar="JSON",
                    help="recovery mode: scope to exactly the units `check_shard_coverage.py "
                         "--all --json` reports as unreported for this staging dir, instead "
                         "of the class_out gap classes. Use this to re-run what a sweep "
                         "dropped — it targets the dropped units only, so the agent is not "
                         "sent to redo research that is already staged.")
    args = ap.parse_args()
    S = args.staging.rstrip("/")
    want = {c.strip() for c in args.classes.split(",") if c.strip()}

    # (pid, ref_col) pairs the coverage checker says were never reported on. `sheet_row` is
    # deliberately NOT part of the key: owner/operator units live on the operators-owners tab
    # and the seeder drops their oo_sheet_row, so the pair is what both sides can agree on.
    only = None
    if args.from_coverage:
        only = {(r["pid"], u.get("ref_col", ""))
                for r in json.load(open(args.from_coverage))
                for u in (r.get("unreported") or [])}

    res = json.load(open(os.path.join(S, "staged_resolutions.json")))["resolutions"]
    wc_path = os.path.join(S, "wiki_citations.json")
    cites = {}
    if os.path.exists(wc_path):
        cites = json.load(open(wc_path)).get("pages", {})

    if only is not None:
        gaps = [r for r in res
                if (r.get("project_id", ""), r.get("ref_col", "")) in only]
        seen = {(r.get("project_id", ""), r.get("ref_col", "")) for r in gaps}
        # MISSING_VALUE units are never seeded into the store (seed_resolutions_from_worklist.py
        # seeds MISSING_REF only), so a dropped blank has no record to scope from. Take it
        # straight off the worklist instead — dropping it here would silently re-lose exactly
        # the units gate J just caught.
        missing = only - seen
        if missing:
            wl = json.load(open(os.path.join(S, "worklist.json")))["units"]
            by_key = {(u.get("project_id", ""), u.get("ref_col", "")): u for u in wl}
            for key in sorted(missing):
                u = by_key.get(key)
                if u is None:
                    print(f"  WARN {key[0]} {key[1]} is in neither the store nor the "
                          f"worklist — not briefed")
                    continue
                gaps.append({"project_id": u["project_id"], "ref_col": u["ref_col"],
                             "sheet_row": u.get("oo_sheet_row") or u.get("sheet_row", ""),
                             "segment_name": u.get("segment_name", ""),
                             "pipeline_name": u.get("pipeline_name", ""),
                             "wiki": u.get("wiki", ""),
                             "value_cols": u.get("value_cols", []),
                             "values": u.get("values", {}),
                             "primary_value": u.get("primary_value", ""),
                             "current_ref": u.get("current_ref", ""),
                             "class_out": "UNREPORTED_BLANK"})
            gaps.sort(key=lambda r: (r.get("project_id", ""), r.get("ref_col", "")))
    else:
        gaps = [r for r in res
                if r.get("class_in") in ("HAS_REF", "MISSING_REF") and r.get("class_out") in want]

    by_pid = collections.OrderedDict()
    for r in gaps:
        by_pid.setdefault(r.get("project_id", ""), []).append(r)

    # A recovery pass must not write over the original leg's shards (4 of tx's 41 would
    # have gone, 2026-09-09). Its output is a sibling dir both merge_ref_shards.py
    # (--shard-dir) and check_shard_coverage.py already read alongside ref_shards/.
    global OUT_SUB
    OUT_SUB = "ref_shards_recovery" if only is not None else "ref_shards"
    out_dir = os.path.join(S, OUT_SUB, "_briefs")
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
        # Documents this row already yielded. A recovery agent that starts from a blank
        # search re-opens the FERC notice its predecessor already read; the dropped unit is
        # usually stated in a document that is right here.
        already = collections.OrderedDict()
        for r in res:
            if r.get("project_id") != pid:
                continue
            for u in (r.get("proposed_refs") or []):
                if isinstance(u, str) and u.strip():
                    already.setdefault(u.strip(), []).append(r.get("ref_col", ""))

        brief = {
            "contract": CONTRACT,
            "write_shard_to": os.path.join(S, OUT_SUB, f"{pid}.json"),
            "refs_already_on_this_row": [{"url": u, "sourced": sorted(set(c))}
                                         for u, c in already.items()],
            "coverage_gate": (f"python scripts/check_shard_coverage.py --staging {S} "
                              f"--pid {pid}"),
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

    json.dump({"staging": S, "shard_dir": OUT_SUB,
               "classes": sorted(want), "n_pids": len(manifest),
               "n_units": len(gaps), "briefs": manifest},
              open(os.path.join(S, OUT_SUB, "_manifest.json"), "w"), indent=1)
    print(f"wrote {len(manifest)} briefs to {out_dir}")
    print(f"  {len(gaps)} gap units | classes={sorted(want)}")
    for m in manifest:
        print(f"    {m['project_id']} | {m['pipeline_name'][:40]:40} | {m['n_units']} units | {m['n_seed_citations']} seed cites")


if __name__ == "__main__":
    main()
