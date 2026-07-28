#!/usr/bin/env python3
"""DEPRECATED SHIM — use scripts/build_recon_crosswalk.py.

The crosswalk builder is now source-agnostic: hard-coding GulfPub in the field names is
what left the OSM reconciliation with nowhere to write its answer, so its 52 Iraq
features never reached a workbook. This forwards to build_recon_crosswalk.py so existing
commands and docs keep working.

    python scripts/build_recon_crosswalk.py --match-diff <match_diff.json> \
        --sweep-dir batches/<scope>/staging/<sweep-dir>/

Note the OUTPUT FILENAME changes: build_ref_workbook.py reads recon_<source>_crosswalk.json
(one tab per source) and still reads a legacy gulfpub_crosswalk.json if one is present.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_recon_crosswalk import build_crosswalk  # noqa: E402,F401  (re-exported)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--match-diff", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    print("note: build_gulfpub_crosswalk.py is a shim — prefer "
          "`python scripts/build_recon_crosswalk.py --match-diff ... --sweep-dir ...`",
          file=sys.stderr)
    diff = json.loads(Path(args.match_diff).read_text())
    cw = build_crosswalk(diff)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cw, indent=1, ensure_ascii=False))
    print(f"wrote {out}  (overlaps={len(cw['overlaps'])} unmatched={len(cw['additions'])} "
          f"ambiguous={len(cw['ambiguous'])})")


if __name__ == "__main__":
    main()
