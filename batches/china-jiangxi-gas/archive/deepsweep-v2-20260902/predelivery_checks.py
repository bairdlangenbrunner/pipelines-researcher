#!/usr/bin/env python3
"""SUPERSEDED 2026-09-03 by scripts/sweep_gates.py (same gates A-H, generic --staging, + I relevance / J owed blanks / K single-source). Kept for the v2 record only.

Pre-delivery gates for the Jiangxi v2 deep sweep. Read-only: reports, never edits.

v1 shipped 98 REFS_ADDED that looked comprehensive until you counted ORIGINS: three
documents carried 71 of them, and 4 of 18 rows rested on a single host. Ref COUNT is not
ref DIVERSITY, and the tier column is what a researcher trusts when deciding to paste. So
these gates count origins, not URLs.

    python predelivery_checks.py [--json]

Gates:
  A  SOURCE DIVERSITY   -- a row whose sourced units all trace to <2 distinct hosts.
  B  FALSE HIGH         -- a `high` unit (tier means 2+ independent) whose verified refs
                           share one host, or number fewer than 2.
  C  DOMINANT DOCUMENT  -- a single URL carrying >=15 units batch-wide cannot be the second
                           source for a `high`: one origin restated is still one origin.
  D  INDEPENDENCE FLAG  -- `independent: true` on a unit with <2 verified refs. The field
                           means the rubric's >=2-agreeing, NOT "independent of GEM"; 13
                           Uzbekistan units shipped wrong on exactly this.
  E  ORPHAN REFS        -- a ref with no paired value, or a proposed value with no ref.
  F  BANNED / GEM       -- gem.wiki, globalenergymonitor.org, abarrelfull anywhere.
  G  HARVEST COVERAGE   -- pool URLs never opened on a row that still reports UNRESOLVED.
  H  RECOVERED SPN       -- 18 harvested citations point at web.archive.org/save/<url>, the
                           Save Page Now INSTRUCTION endpoint, not a snapshot. url_verifier
                           rightly fails them, so they never entered the live pool and gate G
                           is blind to them -- but the origin is embedded in the URL and 10
                           of the 18 are live. Same family as the Egypt navigation-surface
                           defect: the citation FORM is wrong, the document is fine.

Exit code is always 0: these inform the delivery note, they do not block a human decision.
"""
from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
DOMINANT_MIN = 15
BANNED = ("gem.wiki", "globalenergymonitor.org", "abarrelfull.wikidot.com",
          "abarrelfull.co.uk")
SOURCED = {"REFS_ADDED", "REVERIFIED", "CONFIRMED"}


def host(u: str) -> str:
    h = (urlparse(u).netloc or "").lower()
    return h[4:] if h.startswith("www.") else h


def verified(r: dict) -> list[str]:
    """Refs the merge would actually KEEP: ok && contains_value. Counting proposed_refs
    instead would credit a row for URLs that get dropped at merge -- which is precisely
    how a row ends up looking two-sourced in the workbook and single-sourced in fact."""
    ok = {v.get("url") for v in (r.get("verifications") or [])
          if v.get("ok") and v.get("contains_value")}
    return [u for u in (r.get("proposed_refs") or []) if u in ok]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    store = json.loads((HERE / "staged_resolutions.json").read_text())
    res = store["resolutions"]
    pool = json.loads((HERE / "harvest_screen.json").read_text())

    by_pid = collections.defaultdict(list)
    for r in res:
        by_pid[r.get("project_id")].append(r)

    url_units = collections.Counter()
    for r in res:
        for u in set(verified(r)):
            url_units[u] += 1
    dominant = {u for u, n in url_units.items() if n >= DOMINANT_MIN}

    A, B, C, D, E, F, G, H = [], [], [], [], [], [], [], []
    for pid, recs in sorted(by_pid.items()):
        hosts = {host(u) for r in recs if r.get("class_out") in SOURCED
                 for u in verified(r)} - {""}
        sourced_n = sum(1 for r in recs if r.get("class_out") in SOURCED)
        if sourced_n and len(hosts) < 2:
            A.append((pid, sourced_n, sorted(hosts)))
        for r in recs:
            vr = verified(r)
            vh = {host(u) for u in vr} - {""}
            tier = (r.get("tier") or "").lower()
            col = r.get("ref_col")
            if tier == "high" and (len(vr) < 2 or len(vh) < 2):
                B.append((pid, col, len(vr), sorted(vh)))
            if tier == "high" and len(vh) == 2 and dominant & set(vr) and \
                    len([u for u in vr if u not in dominant]) < 2:
                C.append((pid, col, sorted(set(vr) & dominant)))
            if r.get("independent") and len(vr) < 2:
                D.append((pid, col, len(vr)))
            has_val = any(str(v).strip() for v in (r.get("values") or {}).values())
            if vr and not has_val and not str(col).startswith("__"):
                E.append((pid, col, "ref without a paired value"))
            if has_val and not vr and r.get("class_out") in SOURCED:
                E.append((pid, col, "value marked sourced with no verified ref"))
            for u in (r.get("proposed_refs") or []):
                if any(b in u.lower() for b in BANNED):
                    F.append((pid, col, u))

    # harvest_screen.json is a FLAT LIST of {ok, status, reason, url, project_ids}.
    live_by_pid = collections.defaultdict(set)
    for e in pool:
        if e.get("ok"):
            for p in e.get("project_ids") or []:
                live_by_pid[p].add(e["url"])
    # "Opened" is any URL the shard cites OR records a verification for -- a URL an agent
    # read and REJECTED was still opened, and counting only proposed_refs would report
    # honest negative work as a coverage gap.
    opened = {u for r in res for u in (r.get("proposed_refs") or [])}
    opened |= {v.get("url") for r in res for v in (r.get("verifications") or []) if v.get("url")}
    for pid, recs in sorted(by_pid.items()):
        if not any(r.get("class_out") == "UNRESOLVED" for r in recs):
            continue
        live = live_by_pid.get(pid, set())
        unopened = live - opened
        if unopened:
            G.append((pid, len(unopened), len(live)))

    # H -- origins recovered from Save-Page-Now citations (see the module docstring).
    # Written by the recovery pass; absent on a batch that never ran one.
    spn_path = HERE / "spn_recovered_origins.json"
    spn = json.loads(spn_path.read_text()) if spn_path.exists() else []
    spn_by_pid = collections.defaultdict(set)
    for e in spn:
        if e.get("ok"):
            for p in e.get("project_ids") or []:
                spn_by_pid[p].add(e["origin"])
    for pid, recs in sorted(by_pid.items()):
        if not any(r.get("class_out") == "UNRESOLVED" for r in recs):
            continue
        unopened = spn_by_pid.get(pid, set()) - opened
        if unopened:
            H.append((pid, len(unopened), sorted(unopened)[0]))

    out = {"A_single_host_rows": A, "B_false_high": B, "C_dominant_document": C,
           "D_independence_flag": D, "E_orphan_refs": E, "F_banned_sources": F,
           "G_unopened_pool_on_unresolved_rows": G,
           "H_recovered_spn_origins_unopened": H,
           "dominant_documents": sorted(((n, u) for u, n in url_units.items()
                                         if n >= DOMINANT_MIN), reverse=True)}
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return

    def sec(k, rows, ok_msg, fmt):
        print(f"\n{k}  ({len(rows)})")
        if not rows:
            print(f"    PASS — {ok_msg}")
        for r in rows[:40]:
            print("    " + fmt(r))
        if len(rows) > 40:
            print(f"    … {len(rows) - 40} more")

    print(f"pre-delivery checks — {len(res)} records, {len(by_pid)} rows")
    sec("A  source diversity (<2 distinct hosts on a sourced row)", A,
        "every sourced row rests on 2+ origins",
        lambda r: f"{r[0]}: {r[1]} sourced unit(s), hosts={r[2] or ['(none)']}")
    sec("B  tier `high` without 2 verified refs on 2 hosts", B,
        "every high tier has 2+ independent origins",
        lambda r: f"{r[0]} {r[1]}: {r[2]} verified ref(s), hosts={r[3]}")
    sec(f"C  `high` leaning on a dominant document (>={DOMINANT_MIN} units)", C,
        "no high tier rests on one restated origin",
        lambda r: f"{r[0]} {r[1]}: dominant {r[2]}")
    sec("D  independent=true with <2 verified refs", D,
        "the independence flag matches the rubric",
        lambda r: f"{r[0]} {r[1]}: {r[2]} verified ref(s)")
    sec("E  orphan refs / unsourced sourced-values", E,
        "no orphans in either direction",
        lambda r: f"{r[0]} {r[1]}: {r[2]}")
    sec("F  banned or GEM sources", F, "0 GEM surfaces, 0 abarrelfull",
        lambda r: f"{r[0]} {r[1]}: {r[2]}")
    sec("G  live pool URLs never opened on a row still UNRESOLVED", G,
        "the harvested pool was worked to exhaustion",
        lambda r: f"{r[0]}: {r[1]} of {r[2]} live pool URL(s) unopened")
    sec("H  live origins behind Save-Page-Now citations, unopened on an UNRESOLVED row", H,
        "no recoverable SPN origin is left unread",
        lambda r: f"{r[0]}: {r[1]} unopened, e.g. {r[2][:78]}")
    if out["dominant_documents"]:
        print("\ndominant documents (one origin carrying many units):")
        for n, u in out["dominant_documents"]:
            print(f"    {n:3d}  {u[:100]}")


if __name__ == "__main__":
    main()
