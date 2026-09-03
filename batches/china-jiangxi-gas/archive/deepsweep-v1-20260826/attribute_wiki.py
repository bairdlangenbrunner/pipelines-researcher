#!/usr/bin/env python3
"""Per-section wiki citation attribution (China province network pages).

`harvest_wiki_citations.py` is PAGE-level: it returns every outbound citation on the
page plus a `backlinks` count. On a province-network page that is not enough — one
citation can carry 54 backlinks, and the count says a citation is used 54 times, not
WHERE. All 17 in-scope grid rows share one page, so page-level output would hand every
row the same 47 candidates.

These pages are structured: one `h3` per named segment, each followed by a field-labeled
bullet list (`Operator:`, `Owner:`, `Length:` …) where each bullet carries its OWN
superscript. That makes attribution mechanical:

    h3 section  --join on worklist segment_name-->  ProjectID
    bullet label --LABEL_MAP-->                     GEM [ref] column
    bullet's <sup> --cite_note id-->                citation URL

Emits one candidate per (project_id, ref_col) with the wiki's own stated value, so the
downstream verifier can require `contains_value` against the RIGHT value, and so the
fills/validity legs can compare wiki value vs sheet value.

Read-and-stage only. Nothing here proposes an applied edit; every candidate still has to
pass url_verifier before it may reach a workbook.

    python attribute_wiki.py --worklist worklist.json --out wiki_attributed.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from url_verifier import WIKI_UA  # noqa: E402

# wiki bullet label -> GEM [ref] column. `tab` marks the operators/owners tab, whose
# units the worklist emits separately (ProjectID-keyed, GID 1489950650).
LABEL_MAP = {
    "operator":       {"ref_col": "Operator [ref]", "tab": "operators_owners"},
    "owner":          {"ref_col": "Owner [ref]",    "tab": "operators_owners"},
    "status":         {"ref_col": "Status [ref]"},
    "length":         {"ref_col": "Length [ref]"},
    "diameter":       {"ref_col": "Diameter [ref]"},
    "capacity":       {"ref_col": "Capacity [ref]"},
    "start year":     {"ref_col": "Start [ref]"},
    "cost":           {"ref_col": "SegmentCost [ref]"},
    # "parent company" has no GEM ref column of its own — recorded, never emitted.
}

NETWORK_PAGE = "https://www.gem.wiki/Jiangxi_Natural_Gas_Pipeline_Network"


def _norm(s: str) -> str:
    """Normalize a segment name for joining: Latin only, lowercase, alphanumeric.

    Drops the Chinese half of a bilingual h3, the `Phase I/II` prefix the worklist
    carries, and every dash/apostrophe/space variant (Gao'an vs Gaoan, en- vs hyphen).
    """
    s = (s or "").lower()
    s = re.sub(r"\bphase\s+(i{1,3}|1|2|3)\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


def _strip_sups(text: str) -> str:
    """Drop the rendered `[ 13 ]` superscript markers from a bullet's visible value."""
    return re.sub(r"\[\s*\d+\s*\]", "", text).strip(" ,;·")


def parse_sections(html: str) -> list[dict]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    body = soup.select_one("#mw-content-text") or soup

    # cite_note id -> external URL (first external link in the reference <li>)
    cite: dict[str, str] = {}
    for li in body.select("li"):
        lid = li.get("id", "")
        if lid.startswith("cite_note"):
            a = li.select_one("a.external")
            if a and a.get("href"):
                cite[lid] = a["href"]

    sections = []
    for h in body.select("h3"):
        title = h.get_text(" ", strip=True)
        ul = None
        for sib in h.next_siblings:
            name = getattr(sib, "name", None)
            if name == "ul":
                ul = sib
                break
            if name in ("h2", "h3"):
                break
        if ul is None:
            continue

        fields = []
        for li in ul.select(":scope > li"):
            txt = li.get_text(" ", strip=True)
            m = re.match(r"\s*([A-Za-z][A-Za-z0-9 /'\-()]{1,34}?)\s*:", txt)
            if not m:
                continue
            label = m.group(1).strip().lower()
            value = _strip_sups(txt[m.end():])
            urls, missing = [], []
            for a in li.select("sup a"):
                cid = (a.get("href") or "").lstrip("#")
                if not cid:
                    continue
                (urls if cite.get(cid) else missing).append(cite.get(cid) or cid)
            # dedup, order-preserving
            urls = list(dict.fromkeys(urls))
            fields.append({"label": label, "value": value, "urls": urls,
                           "unresolved_cites": missing})
        sections.append({"h3": title, "norm": _norm(title), "fields": fields})
    return sections


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worklist", required=True)
    ap.add_argument("--page", default=NETWORK_PAGE)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    import requests

    r = requests.get(a.page, timeout=30, headers={"User-Agent": WIKI_UA})
    r.raise_for_status()
    sections = parse_sections(r.text)

    wl = json.loads(Path(a.worklist).read_text())
    units = wl["units"]

    # ProjectID -> (segment_name, set of ref_cols actually owed on that row)
    seg_of: dict[str, str] = {}
    owed: dict[str, set] = {}
    for u in units:
        pid = u["project_id"]
        seg_of.setdefault(pid, u.get("segment_name") or "")
        owed.setdefault(pid, set()).add(u["ref_col"])

    by_norm = {s["norm"]: s for s in sections if s["norm"]}
    # `Phase I` / `Phase II` normalize to "" (the phase token is deliberately stripped so
    # "Phase I, Fengcheng-Fuzhou" joins to the "Fengcheng-Fuzhou" h3). Keep them reachable
    # under a phase-preserving key: on this page they are CONTAINER headings whose <ul> is
    # a list of constituent segment names and which carry no field bullets at all. A GEM
    # row whose segment_name is bare "Phase I" is therefore a network-granularity parent
    # row, and matching it here records that fact instead of reporting a false UNMATCHED.
    for sec in sections:
        k = re.sub(r"[^a-z0-9]+", "", (sec["h3"] or "").lower())
        if k and k not in by_norm:
            by_norm[k] = sec

    out, unmatched_pids, used, container = [], [], set(), []
    for pid, seg in sorted(seg_of.items()):
        n = _norm(seg) or re.sub(r"[^a-z0-9]+", "", (seg or "").lower())
        sec = by_norm.get(n)
        if sec is None:  # substring fallback, longest match wins
            cands = [s for k, s in by_norm.items() if n and (n in k or k in n)]
            sec = max(cands, key=lambda s: len(s["norm"])) if cands else None
        if sec is None:
            unmatched_pids.append((pid, seg))
            continue
        used.add(sec["norm"])
        if not sec["fields"]:
            container.append({"project_id": pid, "segment_name": seg,
                              "wiki_section": sec["h3"],
                              "note": "wiki h3 is a CONTAINER heading (lists constituent "
                                      "segments, carries no field bullets) — this GEM row is "
                                      "network-granularity, not a segment"})
            continue
        for f in sec["fields"]:
            mp = LABEL_MAP.get(f["label"])
            if not mp or not f["value"] or not f["urls"]:
                continue
            rec = {
                "project_id": pid,
                "ref_col": mp["ref_col"],
                "wiki_section": sec["h3"],
                "wiki_label": f["label"],
                "wiki_value": f["value"],
                "candidate_urls": f["urls"],
                "owed_on_row": mp["ref_col"] in owed.get(pid, set()),
            }
            if mp.get("tab"):
                rec["tab"] = mp["tab"]
            out.append(rec)

    Path(a.out).write_text(json.dumps(
        {"page": a.page, "n_sections": len(sections), "attributions": out,
         "unmatched_project_ids": unmatched_pids,
         "container_rows": container,
         "unused_sections": sorted(s["h3"] for s in sections if s["norm"] not in used)},
        ensure_ascii=False, indent=2))

    print(f"wrote {a.out}")
    print(f"  sections parsed: {len(sections)}   attributions: {len(out)}")
    print(f"  PIDs attributed: {len({r['project_id'] for r in out})}/{len(seg_of)}")
    print(f"  owed-on-row: {sum(1 for r in out if r['owed_on_row'])}"
          f"   already-cited-or-not-owed: {sum(1 for r in out if not r['owed_on_row'])}")
    if container:
        print("  CONTAINER (network-granularity) rows:")
        for c in container:
            print(f"    {c['project_id']}  h3={c['wiki_section']!r}")
    if unmatched_pids:
        print("  UNMATCHED PIDs:")
        for pid, seg in unmatched_pids:
            print(f"    {pid}  {seg!r}")


if __name__ == "__main__":
    main()
