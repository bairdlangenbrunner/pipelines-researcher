#!/usr/bin/env python3
"""Re-screen already-built worklists against the non-citation URL detector.

A site-search query, a paginated archive index or a bare category/tag listing is
navigation, not a document — `url_verifier._NON_CITATION_RE` now refuses them (see the
check in `verify_url`). Worklists built before that landed scored such URLs on liveness
plus a substring screen, and a search page passes both whenever the digits happen to
appear in a result snippet. Egypt was the case that exposed it: 104 of 560 filled ref
units (18.6%) rested on just two egyptoil-gas.com navigation URLs and 81 scored `ok`.

This only rewrites `existing_ref_checks`, flipping a matching URL's `ok` to False with
the detector's reason. No value, class or proposed ref is touched — the effect is that
the unit becomes OWED again, so the ref leg chases the underlying article.

  python scripts/repair_noncitation_screen.py --staging <dir>     # dry run
  python scripts/repair_noncitation_screen.py --all --apply
"""
import argparse, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from url_verifier import _NON_CITATION_RE as NON_CITATION

_REASON = ("search/index page, not a document — cite the underlying "
           "article or report, not a mutable navigation surface")


def repair(path, apply=False, verbose=False):
    try:
        wl = json.load(open(path, encoding="utf-8"))
    except (ValueError, OSError):
        return 0, 0
    flipped = newly_owed = 0
    for u in wl.get("units", []):
        checks = u.get("existing_ref_checks") or []
        was_clean = bool(checks) and all(c.get("ok") for c in checks)
        touched = False
        for c in checks:
            if NON_CITATION.search(c.get("url") or "") and c.get("ok"):
                c["ok"] = False
                c["non_citation"] = True
                c["reason"] = _REASON
                flipped += 1
                touched = True
        if touched and was_clean:
            newly_owed += 1
            if verbose:
                print("  %s %s" % (u["project_id"], u["ref_col"]))
    if flipped and apply:
        wl.setdefault("summary", {})["noncitation_screen_repaired"] = {
            "urls_flipped": flipped, "units_newly_owed": newly_owed}
        json.dump(wl, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return flipped, newly_owed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    paths = (sorted(glob.glob("batches/*/staging/*/worklist.json")) if a.all
             else [os.path.join(a.staging, "worklist.json")])
    tf = tu = 0
    for p in paths:
        f, u = repair(p, a.apply, a.verbose)
        if f:
            print("%s: %d url check(s) flipped, %d unit(s) newly owed" % (p, f, u))
        tf, tu = tf + f, tu + u
    print("\nTOTAL %d url check(s), %d unit(s) newly owed%s"
          % (tf, tu, "" if a.apply else "  [dry run — pass --apply]"))


if __name__ == "__main__":
    main()
