#!/usr/bin/env python3
"""Assemble the 18-partial RETRY results (§8, 2026-07-30 afternoon pass).

Reads the six retry_results_*.json files (second-pass subagent output on the 18
ROUTE_PARTIAL PIDs; every URL re-verified via scripts/url_verifier.py in the main
session, with two documented manual confirmations: the World Bank ICR PDF is a
3.9MB scan — large-PDF substring false-negative, confirmed via pdftotext — and
ueepc.com is Arabic-only, 'الكريمات' present) and:

  - resolved PIDs (P8013, P8021, P8014) -> scripts/build_route_candidate.py
    --method endpoints, accuracy `very low (straight line/schematic)`;
    build_route_candidate's upsert replaces each PID's ROUTE_PARTIAL record with
    the new ROUTE_CANDIDATE. P8014 was adjudicated resolved in the main session:
    the same WB ICR that resolved P8021 names the 162km Zafarana-Kureimat line
    (completed Nov 1995), closing the gap the research agent couldn't.
  - the 15 still-unresolved PIDs -> their existing ROUTE_PARTIAL records are
    refreshed in place (corridor_desc / proposed_refs / endpoint halves /
    researcher_notes) with the second-pass findings, keeping the NO GEOMETRY
    STAGED framing (standing rule 2 — coordinates are never fabricated).
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
ACC_VLOW = "very low (straight line/schematic)"
GROUPS = ["westdesert2", "upper2", "cairo2", "sokhna2", "sinai2", "delta2"]


def _notes(r: dict) -> str:
    bits = [(r.get("notes") or "").strip()]
    sc = (r.get("sheet_conflicts") or "").strip()
    if sc:
        bits.append(f"SHEET CONFLICT: {sc}")
    for col, val in (r.get("spelling_fixes") or {}).items():
        bits.append(f"Suggest {col} -> '{val}'.")
    return " ".join(b for b in bits if b)


def _coord(p: dict | None):
    p = p or {}
    lon, lat = p.get("lon"), p.get("lat")
    return (lon, lat) if lon is not None and lat is not None else None


def main() -> None:
    results = []
    for g in GROUPS:
        results += json.loads((HERE / f"retry_results_{g}.json").read_text())
    assert len(results) == 18, f"expected 18 records, got {len(results)}"

    sr_path = HERE / "staged_resolutions.json"

    candidates, updated, failures = [], [], []
    for r in results:
        pid = r["project_id"]
        start, end = _coord(r.get("start")), _coord(r.get("end"))

        if r.get("resolved") and start and end and start != end:
            s, e = r["start"], r["end"]
            cmd = [sys.executable, "scripts/build_route_candidate.py", "--pid", pid,
                   "--commodity", "gas", "--staging", str(HERE),
                   "--method", "endpoints",
                   "--start", f"{start[0]},{start[1]}", "--end", f"{end[0]},{end[1]}",
                   "--start-name", s.get("name", ""), "--end-name", e.get("name", ""),
                   "--start-ref", s.get("evidence_url", ""),
                   "--end-ref", e.get("evidence_url", ""),
                   "--accuracy", ACC_VLOW,
                   "--notes", " ".join(x for x in (
                       _notes(r),
                       f"Start coord basis: {s.get('coord_basis', '')}.",
                       f"End coord basis: {e.get('coord_basis', '')}.") if x.strip())]
            extra = [u for u in dict.fromkeys(r.get("route_refs") or [])
                     if u not in (s.get("evidence_url"), e.get("evidence_url"))]
            for u in extra:
                cmd += ["--route-ref", u]
            p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
            print(p.stdout.strip())
            if p.returncode != 0:
                failures.append((pid, p.stderr.strip()))
                print(p.stderr.strip(), file=sys.stderr)
            else:
                candidates.append(pid)
                if p.stderr.strip():
                    print(p.stderr.strip(), file=sys.stderr)
            continue

        # ---- refresh the existing ROUTE_PARTIAL record in place ------------- #
        data = json.loads(sr_path.read_text())
        recs = data["resolutions"]
        matches = [x for x in recs if x.get("project_id") == pid]
        assert len(matches) == 1 and matches[0]["class_out"] == "ROUTE_PARTIAL", \
            f"{pid}: expected exactly one ROUTE_PARTIAL record"
        rec = matches[0]
        s, e = r.get("start") or {}, r.get("end") or {}
        sc, ec = _coord(s), _coord(e)
        degenerate = sc and ec and sc == ec
        refs = list(dict.fromkeys(r.get("route_refs") or []))
        rec.update({
            "start_name": s.get("name", "") or rec.get("start_name", ""),
            "start_lon": sc[0] if sc and not degenerate else None,
            "start_lat": sc[1] if sc and not degenerate else None,
            "end_name": e.get("name", "") or rec.get("end_name", ""),
            "end_lon": ec[0] if ec and not degenerate else None,
            "end_lat": ec[1] if ec and not degenerate else None,
            "corridor_desc": (r.get("notes") or "").strip(),
            "proposed_refs": refs,
            "verifications": [{"url": x, "ok": True} for x in refs],
            "tier": "low" if refs else "",
            "independent": len(refs) >= 2,
            "researcher_notes": " ".join(x for x in (
                "NO GEOMETRY STAGED after a second research pass (2026-07-30): "
                "endpoint(s) still not publicly coordinated -- coordinates are "
                "never fabricated (standing rule 2).",
                _notes(r)) if x),
        })
        sr_path.write_text(json.dumps(data, indent=1, ensure_ascii=False))
        updated.append(pid)

    print(f"\n{len(candidates)} candidates assembled: {', '.join(candidates)}")
    print(f"{len(updated)} ROUTE_PARTIAL records refreshed: {', '.join(updated)}")
    for pid, err in failures:
        print(f"  FAILED {pid}: {err[:300]}", file=sys.stderr)
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
