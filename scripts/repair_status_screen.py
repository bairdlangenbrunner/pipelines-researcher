#!/usr/bin/env python3
"""Apply the status-token screen correction to worklists built before the fix.

`build_ref_worklist.py --verify-existing` used to substring-test STATUS values, so a
live page that describes a line carrying gas but never types the word "operating" came
back `ok: False` — "200 but data value not found". That contradicts `url_verifier`'s own
contract ("STATUS is inferable, not literal ... treat a status any_of miss as expected")
and it propagated: `seed_resolutions_from_worklist` reads "not all live" and classes the
unit DEAD_LINK, and the workbook paints the live URL red. A researcher then sees a
working page presented as a dead link, which is exactly what the standing rule forbids.

This rewrites the stored `existing_ref_checks` for status units in place: a 200 whose
only complaint was the missing status token flips to ok, tagged `status_token_absent`.
Nothing else is touched — no value, no class, no ref.

  python scripts/repair_status_screen.py --staging <dir> [--apply]
  python scripts/repair_status_screen.py --all [--apply]
"""
import argparse, glob, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import normalize as N  # noqa: E402

_NEW_REASON = ("200, live; status token not present verbatim "
               "(expected — status is inferred from prose, not matched)")


def _is_token_miss(c):
    return (not c.get("ok") and c.get("status") == 200
            and "data value not found" in (c.get("reason") or ""))


def repair(path, apply=False):
    doc = json.load(open(path))
    units = doc.get("units")
    if units is None:
        return None
    flipped = un_owed = 0
    for u in units:
        if u.get("class") != "HAS_REF":
            continue
        if (u.get("primary_value") or "").strip().lower() not in N.GEM_STATUSES:
            continue
        checks = u.get("existing_ref_checks") or []
        misses = [c for c in checks if _is_token_miss(c)]
        if not misses:
            continue
        was_owed = not all(c.get("ok") for c in checks)
        for c in misses:
            c["ok"] = True
            c["status_token_absent"] = True
            c["reason"] = _NEW_REASON
            flipped += 1
        if was_owed and all(c.get("ok") for c in checks):
            un_owed += 1
    if apply and flipped:
        doc.setdefault("summary", {})["status_screen_repaired"] = {
            "urls_flipped": flipped, "units_un_owed": un_owed}
        json.dump(doc, open(path, "w"), indent=1, ensure_ascii=False)
    return flipped, un_owed, len(units)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--staging")
    g.add_argument("--all", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    paths = (sorted(glob.glob("batches/*/staging/*/worklist.json")) if a.all
             else [os.path.join(a.staging, "worklist.json")])
    tf = tu = 0
    for p in paths:
        r = repair(p, a.apply)
        if not r or not r[0]:
            continue
        f, un, n = r
        tf, tu = tf + f, tu + un
        print(f"{'wrote' if a.apply else 'would fix'} {p}: {f} url check(s), "
              f"{un} unit(s) no longer owed (of {n})")
    print(f"\nTOTAL {tf} url checks, {tu} units un-owed"
          f"{'' if a.apply else '  (dry run — pass --apply)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
