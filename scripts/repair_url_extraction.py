#!/usr/bin/env python3
"""Re-verify worklist units whose `[ref]` URLs were mis-extracted before the fix.

`_extract_urls` captured `a.com/x,https://b.com/y` (a comma-delimited ref cell with no
space after the comma) as ONE fused URL, and let a trailing Arabic comma ride into the
path. Both produce a request that 404s against live pages — and the fused case never
checks the second URL at all. A false 404 is the worst kind of false positive here: the
standing rule says only a confirmed 404/410 may drop out of a `[ref]` cell, so a parser
bug could get a working reference deleted.

Re-extracts each HAS_REF unit's URLs and, where the list changed, re-runs the HTTP
screen (status units excluded from the substring test, per url_verifier's contract).

  python scripts/repair_url_extraction.py --staging <dir> [--apply]
  python scripts/repair_url_extraction.py --all [--apply]
"""
import argparse, glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ref_worklist as B          # noqa: E402
import normalize as N                   # noqa: E402
from url_verifier import surface_forms, verify_many  # noqa: E402


def repair(path, apply=False, verbose=True):
    wl = json.load(open(path))
    changed = 0
    for u in wl.get("units", []):
        if u.get("class") != "HAS_REF":
            continue
        old = [c["url"] for c in (u.get("existing_ref_checks") or [])]
        new = B._extract_urls(u.get("current_ref") or "")
        if old == new or not new:
            continue
        value = (u.get("primary_value") or "").strip()
        is_status = value.lower() in N.GEM_STATUSES
        any_of = surface_forms(value) if (B._numericish(value) or is_status) else None
        res = verify_many(new, any_of=any_of)
        checks = [{"url": x, **res.get(x, {"ok": False, "status": None,
                                           "reason": "not checked"})} for x in new]
        if is_status:
            for c in checks:
                if (not c.get("ok") and c.get("status") == 200
                        and "data value not found" in (c.get("reason") or "")):
                    c["ok"] = True
                    c["status_token_absent"] = True
                    c["reason"] = ("200, live; status token not present verbatim "
                                   "(expected — status is inferred from prose)")
        u["existing_ref_checks"] = checks
        changed += 1
        if verbose:
            print(f"  {u['project_id']} {u['ref_col']}: {len(old)}->{len(new)} url(s); "
                  f"ok={sum(1 for c in checks if c.get('ok'))}/{len(checks)}")
    if apply and changed:
        wl.setdefault("summary", {})["url_extraction_repaired"] = changed
        json.dump(wl, open(path, "w"), indent=1, ensure_ascii=False)
    return changed


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--staging")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    paths = (sorted(glob.glob("batches/*/staging/*/worklist.json")) if a.all
             else [os.path.join(a.staging, "worklist.json")])
    total = 0
    for p in paths:
        n = repair(p, a.apply)
        if n:
            print(f"{'wrote' if a.apply else 'would fix'} {p}: {n} unit(s)")
            total += n
    print(f"\nTOTAL {total} unit(s) re-verified"
          f"{'' if a.apply else '  (dry run — pass --apply)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
