#!/usr/bin/env python3
"""Merge country-discovery vetted shards (discovery/vetted/<slug>.json) -> staged_new.json.

Merge-time QC (subagents are not perfectly consistent; normalize deterministically):
- Strip any ref URL whose verification is not ok && contains_value, and any
  blocklisted host (gem.wiki / globalenergymonitor / theodora / wikidot).
- Drop a value whose paired [ref] ends up empty (no orphan values), and vice versa
  (no orphan refs) — dropped pairs are noted in researcher_notes.
- Downgrade a new_row with zero surviving refs to monitor (the add-threshold needs
  verifiable evidence).
- Fold the consolidator's matched[] list (queue.json) in as matched_existing records.
- Fold queue.json's seed_ledger (country-discovery args.seeds): `monitor` seeds become
  monitor records and `matched` seeds matched_existing records (deduped by slug/PID), and
  the full ledger rides in meta.seed_ledger so every seed's disposition stays visible.

Run AFTER the country-discovery workflow and BEFORE build_discovery_workbook.py:

    python scripts/merge_discovery_shards.py --staging batches/iraq-gas/staging/annual/
"""
import argparse, collections, json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_qc import bad_cost_units, verified_refs, iter_shards, qc_note, independence_qc  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    args = ap.parse_args()
    S = args.staging.rstrip("/")

    ctx_path = os.path.join(S, "discovery_context.json")
    scope = json.load(open(ctx_path))["scope"] if os.path.exists(ctx_path) else {}

    candidates = []
    for p, d in iter_shards(os.path.join(S, "discovery", "vetted", "*.json")):
        cls = d.get("class", "monitor")
        notes = d.get("researcher_notes", "")
        values = dict(d.get("values") or {})
        refs, dropped_pairs = {}, []
        for rc, urls in (d.get("refs") or {}).items():
            kept = verified_refs(urls, d.get("verifications"))
            if kept:
                refs[rc] = kept
            else:
                dropped_pairs.append(rc)
        # no orphan values: a value whose ref cluster lost all its URLs is dropped too
        for rc in dropped_pairs:
            stem = rc.replace(" [ref]", "")
            doomed = [c for c in values if c == stem or c.startswith(stem)]
            for c in doomed:
                values.pop(c, None)
            if doomed:
                notes = qc_note(notes, f"dropped {'/'.join(doomed)} (ref did not verify).")
        if cls == "new_row" and not refs:
            cls = "monitor"
            notes = qc_note(notes, "new_row with zero verified refs -> monitor.")
        for col, val in bad_cost_units(values).items():
            print(f"  WARN {os.path.basename(p)}: {col}={val!r} — units must be a bare "
                  "currency code; put the magnitude in the cost number (fix the shard)")
        d_tier, d_indep, notes = independence_qc(
            refs, d.get("tier", ""), d.get("independent", False), notes)
        candidates.append({
            "slug": d.get("slug", os.path.basename(p)[:-5]), "class": cls,
            "name": d.get("name", ""), "matched_project_id": d.get("matched_project_id", ""),
            "values": values, "refs": refs,
            "verifications": d.get("verifications", []) or [],
            "tier": d_tier, "independent": d_indep,
            "source_language": d.get("source_language", "en"),
            "monitor_reason": d.get("monitor_reason", ""), "researcher_notes": notes,
        })

    # consolidator-level matches (never reached vetting) ride along as matched_existing
    q_path = os.path.join(S, "discovery", "queue.json")
    queue = json.load(open(q_path)) if os.path.exists(q_path) else {}
    seen_matches = {c["matched_project_id"] for c in candidates if c["class"] == "matched_existing"}

    def add_match(name, pid, notes):
        if pid and pid in seen_matches:
            return
        seen_matches.add(pid)
        candidates.append({
            "slug": "", "class": "matched_existing", "name": name,
            "matched_project_id": pid, "values": {}, "refs": {},
            "verifications": [], "tier": "", "independent": False, "source_language": "en",
            "monitor_reason": "", "researcher_notes": notes,
        })

    for m in queue.get("matched", []) or []:
        add_match(m.get("name", ""), m.get("matched_project_id", ""),
                  (m.get("reason", "") +
                   (f" OtherEnglishNames suggestion: {m['other_names_suggestion']}"
                    if m.get("other_names_suggestion") else "")).strip())

    # seed ledger: a seed that never reached vetting still ends as a visible record
    ledger = queue.get("seed_ledger", []) or []
    slugs = {c["slug"] for c in candidates}
    for e in ledger:
        disp, sid = e.get("disposition", ""), e.get("seed_id", "")
        tag = f"seed {sid}: {e.get('reason', '')}".strip()
        if disp == "matched":
            add_match(e.get("name", ""), e.get("matched_project_id", ""), tag)
        elif disp == "monitor" and not (e.get("slug") and e["slug"] in slugs):
            candidates.append({
                "slug": e.get("slug", ""), "class": "monitor", "name": e.get("name", ""),
                "matched_project_id": "", "values": {}, "refs": {},
                "verifications": [], "tier": "", "independent": False, "source_language": "",
                "monitor_reason": e.get("reason", ""), "researcher_notes": tag,
            })
    unled = [e.get("seed_id") for e in ledger if e.get("disposition") == "queued"
             and e.get("slug") and e["slug"] not in slugs]
    if unled:
        print(f"  WARN seed_ledger: {len(unled)} seeds 'queued' with no vetted shard: {unled}")

    meta = {"scope": scope,
            "class_counts": dict(collections.Counter(c["class"] for c in candidates)),
            "n_candidates": len(candidates)}
    if ledger:
        meta["seed_ledger"] = ledger
        meta["seed_dispositions"] = dict(collections.Counter(e.get("disposition", "") for e in ledger))
    out_path = os.path.join(S, "staged_new.json")
    json.dump({"meta": meta, "candidates": candidates}, open(out_path, "w"), indent=1)
    print(f"wrote {out_path}: {meta['class_counts']}")


if __name__ == "__main__":
    main()
