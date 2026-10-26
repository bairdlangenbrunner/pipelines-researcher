#!/usr/bin/env python3
"""Rewrite month names in staged JSON as numbers 1-12 (Baird 2026-10-14: month cells are NEVER names).

Text-level substitution, so each file keeps its formatting. Touches `"<...Month...>": "July"` pairs only
(not [ref] keys). Skips archive/, worklists, briefs and *.prior.json (inputs / history, not proposals).
Values that are not a month at all (a URL, a year) are listed for a person.

    python scripts/scrub_staged_months.py          # dry run
    python scripts/scrub_staged_months.py --apply
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "review_app"))
import push  # noqa: E402

PAIR = re.compile(r'("(?P<k>[A-Za-z0-9_ ]*Month[A-Za-z0-9_ ]*)"\s*:\s*)"(?P<v>[^"\n]*)"')
SKIP = ("/archive/", "worklist", "/_briefs/", ".prior.json")


def main(apply):
    fixed, odd = 0, []
    for f in sorted((ROOT / "batches").rglob("*.json")):
        s = str(f)
        if any(x in s for x in SKIP):
            continue
        txt = f.read_text()

        def sub(m):
            nonlocal fixed
            v = m["v"].strip()
            if not v or "[ref]" in m["k"]:
                return m[0]
            n = push.month_number(v)
            if n is None:
                odd.append((f.relative_to(ROOT), m["k"], v[:70]))
                return m[0]
            if re.fullmatch(r"\d{1,2}", v):         # a plain number stored as text -> number
                pass
            fixed += 1
            return f'{m[1]}{n}'
        new = PAIR.sub(sub, txt)
        if new != txt and apply:
            f.write_text(new)
    print(f"{'rewrote' if apply else 'would rewrite'} {fixed} month values")
    for o in odd:
        print("  LEFT FOR A PERSON", *o)


if __name__ == "__main__":
    main("--apply" in sys.argv)
