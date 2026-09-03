#!/usr/bin/env python3
"""Seed a baseline staged_resolutions.json from a ref worklist.

A Country Sweep's refs leg (workflows.md §3) produces staged_resolutions.json as
the output of its *research* pass; the fan-out merge then folds its shards
(validity / fills / status) onto that preserved ref work. In the in-dev preset
there is no separate refs research pass — the fan-out IS the research — so there
is no prior staged_resolutions.json for merge_deepsweep_shards.py to preserve.

This seeder bridges that gap: it turns every worklist unit into a ref record
(class_in HAS_REF / MISSING_REF) so the merge has a baseline to fold shards onto.
It records ONLY what the worklist already knows — the existing `[ref]` and its
`--verify-existing` liveness — and performs no research and no fabrication:

- HAS_REF, all existing links live + value-present  -> class_out REVERIFIED
  (proposed_refs = the live URLs, so the backend mirror shows them; colored blue)
- HAS_REF, one or more dead / value-missing links   -> class_out DEAD_LINK
  (proposed_refs empty — the deep-sweep Fills tab carries any replacement)
  Each such record also carries `link_live`: True when every cited URL actually
  LOADED and only the value-substring screen missed, False when a URL failed to
  load at all. The distinction is the standing rule — only a page confirmed
  deleted (404/410) may drop out of a `[ref]` cell, so a `link_live` DEAD_LINK is
  "re-read this page", never "this ref is gone", and the workbook must not paint
  it as a dead link.
- MISSING_REF                                        -> class_out UNRESOLVED
- owner/operator units (kind owner/operator)         -> tab="operators_owners"

Run AFTER build_ref_worklist.py and BEFORE merge_deepsweep_shards.py. Idempotent
per staging dir, but refuses to clobber an existing staged_resolutions.json unless
--force (so it never overwrites a genuine refs-leg research result).

Usage:
    python scripts/seed_resolutions_from_worklist.py --staging batches/iraq-gas/staging/annual/
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
        v = {"url": c.get("url", ""), "ok": ok, "contains_value": ok,
             # Carry the HTTP status through. `link_live` below is computed off it, and
             # projecting it away silently made that flag always False — so the workbook's
             # amber-vs-red distinction never fired (found 2026-08-27, Egypt).
             "status": c.get("status")}
        if c.get("non_citation"):
            v["non_citation"] = True
        out.append(v)
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
    n_fills_owed = 0
    for u in units:
        cls_in = u.get("class", "")
        if cls_in == "MISSING_VALUE":
            # An owed FILL (blank value cell, --owe-fills). It has no baseline record: the
            # fills lane is populated by the deep-sweep merge from shard fills[], and an
            # owed-but-unresearched blank must not be seeded as a FILL with no value (the
            # workbook would render an empty tinted cell). Count it so the delivery note can
            # report fills owed vs fills staged.
            n_fills_owed += 1
            continue
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
        # Did every cited URL actually load? A 200 that merely failed the value
        # substring screen is not a dead link (standing rule: only 404/410 is).
        link_live = bool(checks) and all(
            v.get("status") == 200 or v.get("ok") for v in checks)
        # A live navigation page is not a usable ref at all — amber would say
        # "re-read this page", which is wrong advice when the URL is a site search.
        if any(v.get("non_citation") for v in checks):
            link_live = False
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
            "link_live": link_live if cls_in == "HAS_REF" else False,
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
    if n_fills_owed:
        print(f"  fills owed (MISSING_VALUE, not seeded — arrive via merge_deepsweep_shards fills[]): {n_fills_owed}")
    print(f"  class_out: {meta['class_out_counts']}")


if __name__ == "__main__":
    main()
