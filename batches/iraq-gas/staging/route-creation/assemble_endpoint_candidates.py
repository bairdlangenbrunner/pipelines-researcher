#!/usr/bin/env python3
"""Assemble audited Iraq endpoint candidates from the 2026-07-28 route research.

Only routes whose two named endpoints are independently supported and whose URLs
were re-verified on 2026-07-31 are admitted here.  Inferred/derived endpoints are
left for ROUTE_PARTIAL staging instead of being turned into geometry.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ROW_DIR = REPO / "batches/iraq-gas/staging/ref-sweep-operating/rows"
PIDS = ("P2231", "P4054", "P5855", "P7471")
ACCURACY = "very low (straight line/schematic)"


def main() -> None:
    failures: list[tuple[str, str]] = []
    for pid in PIDS:
        row = json.loads((ROW_DIR / f"{pid}.json").read_text())
        route = row["routes"][0]
        refs = list(dict.fromkeys(route.get("proposed_refs") or []))
        if len(refs) < 2:
            raise SystemExit(f"{pid}: fewer than two endpoint/corridor refs")
        cmd = [
            sys.executable,
            "scripts/build_route_candidate.py",
            "--pid", pid,
            "--commodity", "gas",
            "--staging", str(HERE),
            "--method", "endpoints",
            "--start", f'{route["start_lon"]},{route["start_lat"]}',
            "--end", f'{route["end_lon"]},{route["end_lat"]}',
            "--start-name", route["start_name"],
            "--end-name", route["end_name"],
            "--start-ref", refs[0],
            "--end-ref", refs[1],
            "--accuracy", ACCURACY,
            "--notes", " ".join((route["corridor_desc"], route["researcher_notes"])),
        ]
        for ref in refs[2:]:
            cmd += ["--route-ref", ref]
        result = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        print(result.stdout.strip())
        if result.returncode:
            failures.append((pid, result.stderr.strip()))
        elif result.stderr.strip():
            print(result.stderr.strip(), file=sys.stderr)
    if failures:
        for pid, error in failures:
            print(f"{pid}: {error}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
