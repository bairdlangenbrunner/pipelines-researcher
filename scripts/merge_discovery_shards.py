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

Run AFTER the country-discovery workflow and BEFORE build_discovery_workbook.py:

    python scripts/merge_discovery_shards.py --staging batches/staging/annual-gas-iraq/
"""
import argparse, collections, glob, json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from url_verifier import BLOCKLIST_HOSTS, GEM_HOSTS  # noqa: E402

BLOCKLIST = GEM_HOSTS + BLOCKLIST_HOSTS


def _clean_refs(urls, verifs):
    okset = {v.get("url") for v in (verifs or []) if v.get("ok") and v.get("contains_value")}
    out = []
    for u in urls or []:
        if any(b in u.lower() for b in BLOCKLIST):
            continue
        if verifs and u not in okset:
            continue
        out.append(u)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    args = ap.parse_args()
    S = args.staging.rstrip("/")

    ctx_path = os.path.join(S, "discovery_context.json")
    scope = json.load(open(ctx_path))["scope"] if os.path.exists(ctx_path) else {}

    candidates = []
    for p in sorted(glob.glob(os.path.join(S, "discovery", "vetted", "*.json"))):
        try:
            d = json.load(open(p))
        except Exception as e:
            print(f"  WARN unreadable shard {p}: {e}")
            continue
        cls = d.get("class", "monitor")
        notes = d.get("researcher_notes", "")
        values = dict(d.get("values") or {})
        refs, dropped_pairs = {}, []
        for rc, urls in (d.get("refs") or {}).items():
            kept = _clean_refs(urls, d.get("verifications"))
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
                notes = (notes + f" [QC] dropped {'/'.join(doomed)} (ref did not verify).").strip()
        if cls == "new_row" and not refs:
            cls = "monitor"
            notes = (notes + " [QC] new_row with zero verified refs -> monitor.").strip()
        candidates.append({
            "slug": d.get("slug", os.path.basename(p)[:-5]), "class": cls,
            "name": d.get("name", ""), "matched_project_id": d.get("matched_project_id", ""),
            "values": values, "refs": refs,
            "verifications": d.get("verifications", []) or [],
            "tier": d.get("tier", ""), "independent": d.get("independent", False),
            "source_language": d.get("source_language", "en"),
            "monitor_reason": d.get("monitor_reason", ""), "researcher_notes": notes,
        })

    # consolidator-level matches (never reached vetting) ride along as matched_existing
    q_path = os.path.join(S, "discovery", "queue.json")
    if os.path.exists(q_path):
        seen_matches = {c["matched_project_id"] for c in candidates if c["class"] == "matched_existing"}
        for m in json.load(open(q_path)).get("matched", []) or []:
            pid = m.get("matched_project_id", "")
            if pid and pid in seen_matches:
                continue
            candidates.append({
                "slug": "", "class": "matched_existing", "name": m.get("name", ""),
                "matched_project_id": pid, "values": {}, "refs": {},
                "verifications": [], "tier": "", "independent": False, "source_language": "en",
                "monitor_reason": "",
                "researcher_notes": (m.get("reason", "") +
                    (f" OtherEnglishNames suggestion: {m['other_names_suggestion']}"
                     if m.get("other_names_suggestion") else "")).strip(),
            })

    meta = {"scope": scope,
            "class_counts": dict(collections.Counter(c["class"] for c in candidates)),
            "n_candidates": len(candidates)}
    out_path = os.path.join(S, "staged_new.json")
    json.dump({"meta": meta, "candidates": candidates}, open(out_path, "w"), indent=1)
    print(f"wrote {out_path}: {meta['class_counts']}")


if __name__ == "__main__":
    main()
