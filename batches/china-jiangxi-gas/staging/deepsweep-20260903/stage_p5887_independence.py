#!/usr/bin/env python3
"""Set `independent: False` on P5887's __STATUS__ sentinel (was null).

Why this is its own stager rather than a line in normalize_independence.py: that
script's contract is to WITHDRAW an over-claimed `independent: true` (criterion 1,
too few verified refs; criterion 2, one origin behind several refs). This is the
inverse -- a NULL that should read False -- and its own gate makes it invisible to
that pass twice over:

    if not r.get("independent") or rc.startswith("__"): continue

falsy `None` is skipped, and every `__*` sentinel is skipped unconditionally.

The record is the ONE genuinely off-contract independence field in this batch's 44
rows. It carries 1 proposed ref and 1 verification with tier `medium`, but
`independent: None` -- so it is invisible to gate D in BOTH directions (never
flagged as an over-claim, never counted as a single-source record). The other 43
empty-tier/null-independent records have zero refs AND zero verifications, so they
have no independence to claim and are correctly left alone.

The value is not a research judgment: one ref is one publisher, and the sentinel's
own researcher_notes already say the tension rests on a single host with no second
origin ("a single host cannot carry ..."). So this is a schema fix, mechanical and
pre-verified, and it is stamped as one.

Runs at merge-chain step 0e6 -- BEFORE split_shards.py, which regenerates rows/
from shards/ on every run. Re-run with --dir ref_shards_recovery for symmetry with
the other normalizers (P5887 has no recovery shard today; the pass is a no-op there
and stays correct if one appears).
"""
import argparse, json
from pathlib import Path

HERE = Path(__file__).resolve().parent

PID = "P5887"
SENTINEL = "__STATUS__"
STAMP = ("  [INDEPENDENCE SET at merge 2026-09-10, orchestrator: was null on a sentinel "
         "carrying 1 proposed ref and 1 verification, which made it invisible to gate D in "
         "both directions. One ref is one publisher -> independent=False, consistent with the "
         "tier note on this same record. Schema field only; no research finding altered.]")


def main(apply=False, subdir="shards"):
    path = HERE / subdir / f"{PID}.json"
    if not path.exists():
        print(f"  {subdir}/{PID}.json: absent, nothing to do")
        return 0
    d = json.loads(path.read_text())
    changed = 0
    for i, r in enumerate(d.get("resolutions") or []):
        rc = (r.get("ref_col") or r.get("sentinel") or "").strip()
        if rc != SENTINEL:
            continue
        if r.get("independent") is not None:
            print(f"  {subdir}/{PID} #{i} {rc}: independent already "
                  f"{r['independent']!r}, skipped")
            continue
        nrefs = len(r.get("proposed_refs") or [])
        nver = len(r.get("verifications") or [])
        if nrefs == 0 and nver == 0:
            print(f"  {subdir}/{PID} #{i} {rc}: no refs and no verifications -- "
                  f"nothing to claim, left null")
            continue
        r["independent"] = False
        note = (r.get("researcher_notes") or "").rstrip()
        if "INDEPENDENCE SET at merge" not in note:
            r["researcher_notes"] = note + STAMP
        changed += 1
        print(f"  {subdir}/{PID} #{i} {rc}: independent None -> False "
              f"({nrefs} proposed ref(s), {nver} verification(s))")
    if changed and apply:
        path.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
        print(f"  wrote {path.relative_to(HERE)}")
    elif changed:
        print("  DRY RUN -- pass --apply to write")
    return changed


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dir", default="shards")
    a = ap.parse_args()
    n = main(apply=a.apply, subdir=a.dir)
    print(f"{n} record(s) {'updated' if a.apply else 'to update'}")
