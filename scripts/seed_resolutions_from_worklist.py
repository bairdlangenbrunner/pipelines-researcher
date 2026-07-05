#!/usr/bin/env python3
"""Seed a baseline staged_resolutions.json from a ref worklist.

The §6 ref sweep produces staged_resolutions.json as the output of its *research*
pass. The §6b/§7 deep sweep then folds its shards (validity / fills / status) onto
that preserved ref work. In annual-update mode (§7) there is no separate ref-sweep
research pass — the deep sweep IS the research — so there is no prior
staged_resolutions.json for merge_deepsweep_shards.py to preserve.

This seeder bridges that gap: it turns every worklist unit into a ref record
(class_in HAS_REF / MISSING_REF) so the merge has a baseline to fold shards onto.
It records ONLY what the worklist already knows — the existing `[ref]` and its
`--verify-existing` liveness — and performs no research and no fabrication:

- HAS_REF, all existing links live + value-present  -> class_out REVERIFIED
  (proposed_refs = the live URLs, so the backend mirror shows them; colored blue)
- HAS_REF, one or more dead / value-missing links   -> class_out DEAD_LINK
  (proposed_refs empty — the deep-sweep Fills tab carries any replacement)
- MISSING_REF                                        -> class_out UNRESOLVED
- owner/operator units (kind owner/operator)         -> tab="operators_owners"

Run AFTER build_ref_worklist.py and BEFORE the deep-sweep merge. Idempotent per
staging dir, but refuses to clobber an existing staged_resolutions.json unless
--force (so it never overwrites a genuine ref-sweep result).

Usage:
    python scripts/seed_resolutions_from_worklist.py --staging batches/staging/annual-gas-iraq/
"""
import argparse, json, os, collections


def _commodity(scope):
    """Best commodity label for the workbook tab prefix (Gas_/Oil_). The worklist scope
    may not carry it explicitly, so fall back to the snapshot filename."""
    c = (scope.get("commodity") or scope.get("tracker") or "").strip().lower()
    if c in ("gas", "oil"):
        return c
    csv = (scope.get("csv") or "").lower()
    if "gas" in csv or "ggit" in csv:
        return "gas"
    if "oil" in csv or "ngl" in csv or "goit" in csv:
        return "oil"
    return "oil"


def _verifications(unit):
    """Map worklist existing_ref_checks -> the {url, ok, contains_value} shape.
    The verifier's `ok` means HTTP 200 AND the data value was found on the page, so
    contains_value tracks ok; a reachable-but-value-missing check has ok=False."""
    out = []
    for c in unit.get("existing_ref_checks") or []:
        ok = bool(c.get("ok"))
        out.append({"url": c.get("url", ""), "ok": ok, "contains_value": ok})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    ap.add_argument("--force", action="store_true",
                    help="overwrite an existing staged_resolutions.json (default: refuse)")
    args = ap.parse_args()
    S = args.staging.rstrip("/")

    cur = os.path.join(S, "staged_resolutions.json")
    if os.path.exists(cur) and not args.force:
        raise SystemExit(f"{cur} already exists — pass --force to overwrite "
                         "(refusing so a real ref-sweep result is never clobbered).")

    wl = json.load(open(os.path.join(S, "worklist.json")))
    units = wl.get("units", [])

    resolutions = []
    for u in units:
        cls_in = u.get("class", "")
        checks = _verifications(u)
        if cls_in == "MISSING_REF":
            class_out, proposed = "UNRESOLVED", []
        else:  # HAS_REF
            all_live = bool(checks) and all(v["ok"] for v in checks)
            if all_live:
                class_out = "REVERIFIED"
                proposed = [v["url"] for v in checks if v["ok"]]
            else:
                class_out, proposed = "DEAD_LINK", []
        rec = {
            "project_id": u.get("project_id", ""),
            "sheet_row": u.get("sheet_row", ""),
            "pipeline_name": u.get("pipeline_name", ""),
            "segment_name": u.get("segment_name", ""),
            "ref_col": u.get("ref_col", ""),
            "value_cols": u.get("value_cols", []),
            "primary_value_col": u.get("primary_value_col", ""),
            "values": u.get("values", {}),
            "primary_value": u.get("primary_value", ""),
            "current_ref": u.get("current_ref", ""),
            "class_in": cls_in,
            "class_out": class_out,
            "proposed_refs": proposed,
            "verifications": checks,
            "tier": "",
            "independent": False,
            "source_language": "en",
            "researcher_notes": "",
            "wiki": u.get("wiki", ""),
        }
        if u.get("kind") in ("owner", "operator"):
            rec["tab"] = "operators_owners"
        resolutions.append(rec)

    meta = {
        "commodity": _commodity(wl.get("scope", {}) or {}),
        "scope": wl.get("scope", {}),
        "n_units": len(resolutions),
        "seeded_from": "worklist.json",
        "class_in_counts": dict(collections.Counter(r["class_in"] for r in resolutions)),
        "class_out_counts": dict(collections.Counter(r["class_out"] for r in resolutions)),
    }
    json.dump({"meta": meta, "resolutions": resolutions}, open(cur, "w"), indent=1)
    print(f"seeded {cur}: {len(resolutions)} ref records")
    print(f"  class_in:  {meta['class_in_counts']}")
    print(f"  class_out: {meta['class_out_counts']}")


if __name__ == "__main__":
    main()
