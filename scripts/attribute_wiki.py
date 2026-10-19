#!/usr/bin/env python3
"""Per-section wiki citation attribution for multi-segment wiki pages.

`harvest_wiki_citations.py` is PAGE-level: it returns every outbound citation on the
page plus a `backlinks` count. On a province-network page that is not enough — one
citation can carry 54 backlinks, and the count says a citation is used 54 times, not
WHERE. When N rows of a scope share one page, page-level output hands every row the same
candidate list, and a ref leg cannot tell which citation is about which segment.

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

Pages come from the worklist itself (each unit carries its row's `Wiki` URL), so a
scope spanning a province-network page AND several national-trunk pages is attributed
in one run. `--page` overrides that with a single explicit page.

    python scripts/attribute_wiki.py --worklist $STG/worklist.json --out $STG/wiki_attributed.json \
        [--html-dir $STG/wiki_pages]

Single-segment pages (2026-10-17): a page with no h3 per segment states its details directly
under the "Project details" h2; that list is attributed to the row whose own page it is
(`wiki_section` = "(page)"). Each candidate also carries `value_parts`, the figure each
footnote supports when a bullet lists several (`1200 mm [2], 800 [5]`).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

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
    "fuel":           {"ref_col": "Fuel [ref]"},
    "pipeline type":  {"ref_col": "PipelineType [ref]"},
    # "parent company" has no GEM ref column of its own — recorded, never emitted.
}

# Label spellings seen on gem.wiki pages, folded onto the LABEL_MAP keys (2026-10-17: Russia
# pages write `Start Year`, `Current capacity`, `Owners`, `Project cost`, `Proposed start year`).
# A label with no entry is kept on the field (so the value is still visible) and emits nothing.
LABEL_ALIASES = {
    "operators": "operator", "operator(s)": "operator",
    "owners": "owner", "owner(s)": "owner", "ownership": "owner",
    "current status": "status", "project status": "status",
    "total length": "length", "pipeline length": "length", "length (km)": "length",
    "pipe diameter": "diameter", "pipeline diameter": "diameter",
    "current capacity": "capacity", "design capacity": "capacity", "throughput": "capacity",
    "capacity (bcm/y)": "capacity",
    "start date": "start year", "start": "start year", "proposed start year": "start year",
    "expected start year": "start year", "commissioning year": "start year",
    "project cost": "cost", "estimated cost": "cost", "total cost": "cost",
    "fuel type": "fuel", "type": "pipeline type",
}


def canon_label(label: str) -> str:
    lab = re.sub(r"\s+", " ", (label or "").strip().lower().rstrip(":")).strip()
    return LABEL_ALIASES.get(lab, lab)


# The details list sits directly under this h2 on a single-segment page; multi-segment pages
# put one h3 per segment between the h2 and each list.
_DETAILS_H2 = re.compile(r"^(?:project|pipeline)\s+details?$", re.I)
PAGE_LEVEL = "(page)"       # the `h3` label of the single-segment details section

# gem.wiki is VISITED here, never cited (standing rule 1). Fetches use WIKI_UA — the
# token GEM's infra admin knows in the firewall logs; see CLAUDE.md.
_PAUSE = 1.0


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

    def _fields(ul) -> list[dict]:
        fields = []
        for li in ul.select(":scope > li"):
            txt = li.get_text(" ", strip=True)
            m = re.match(r"\s*([A-Za-z][A-Za-z0-9 /'\-()]{1,34}?)\s*:", txt)
            if not m:
                continue
            label = canon_label(m.group(1))
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
                           "unresolved_cites": missing, "parts": _parts(li, cite)})
        return fields

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
        sections.append({"h3": title, "norm": _norm(title), "fields": _fields(ul)})

    # Single-segment page: the details list follows the "Project details" h2 directly, with
    # no h3 in between. Emitted as the PAGE_LEVEL section so a row whose own page has no
    # joinable h3 is attributed from it (2026-10-17: every Russia single-line page is this shape).
    for h2 in body.select("h2"):
        if not _DETAILS_H2.match(h2.get_text(" ", strip=True)):
            continue
        for sib in h2.next_siblings:
            name = getattr(sib, "name", None)
            if name == "ul":
                sections.append({"h3": PAGE_LEVEL, "norm": "", "fields": _fields(sib),
                                 "page_level": True})
                break
            if name in ("h2", "h3"):
                break
        break
    return sections


def _parts(li, cite: dict) -> list[dict]:
    """Split a bullet's value at its superscripts: `1200 mm [2], 800 [5]` ->
    [{text: '1200 mm', urls: [u2]}, {text: '800', urls: [u5]}]. A value with one citation
    is one part; a value with none has one part with no urls. Lets a candidate be verified
    against the figure its OWN footnote supports, not the whole bullet."""
    parts: list[dict] = []
    buf: list[str] = []
    urls: list[str] = []

    def flush():
        text = _strip_sups(" ".join(" ".join(buf).split()))
        text = re.sub(r"^[A-Za-z][A-Za-z0-9 /'\-()]{1,34}?\s*:\s*", "", text, count=1).strip(" ,;·")
        if text or urls:
            parts.append({"text": text, "urls": list(dict.fromkeys(urls))})
        buf.clear(); urls.clear()

    for node in li.children:
        name = getattr(node, "name", None)
        if name == "sup":
            for a in node.select("a"):
                cid = (a.get("href") or "").lstrip("#")
                if cite.get(cid):
                    urls.append(cite[cid])
            # a run of several sups closes one part; text after them starts the next
            nxt = node.next_sibling
            if getattr(nxt, "name", None) != "sup":
                flush()
            continue
        if name in ("ul", "ol"):
            continue           # nested lists are their own bullets
        buf.append(node.get_text(" ", strip=True) if name else str(node))
    flush()
    return parts


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worklist", required=True)
    ap.add_argument("--page", help="attribute this ONE page against every row in the "
                                   "worklist (default: each row against its own Wiki URL)")
    ap.add_argument("--html-dir", help="directory of <PID>.html saved by harvest_wiki_citations.py "
                                       "--save-html; pages found there are parsed offline")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    import requests

    wl = json.loads(Path(a.worklist).read_text())
    units = wl["units"]

    # ProjectID -> segment name, wiki page, and the ref_cols actually owed on that row
    seg_of: dict[str, str] = {}
    name_of: dict[str, str] = {}
    wiki_of: dict[str, str] = {}
    owed: dict[str, set] = {}
    for u in units:
        pid = u["project_id"]
        seg_of.setdefault(pid, u.get("segment_name") or "")
        name_of.setdefault(pid, u.get("pipeline_name") or "")
        wiki_of.setdefault(pid, (u.get("wiki") or "").strip())
        owed.setdefault(pid, set()).add(u["ref_col"])

    # page -> the PIDs to attribute against it
    pages: dict[str, list[str]] = {}
    no_wiki: list[str] = []
    for pid in sorted(seg_of):
        page = a.page or wiki_of.get(pid, "")
        if not page:
            no_wiki.append(pid)
            continue
        pages.setdefault(page, []).append(pid)

    # Fetch every page BEFORE attributing any of them: a GEM row often points at a stub
    # page (created for the branch, no field bullets) while the section that actually
    # describes it lives on the parent network page in the same scope. Holding all
    # sections lets an own-page miss fall back to the run's whole pool.
    sections_by_page: dict[str, list[dict]] = {}
    page_stats = []
    fetched = 0
    for page, pids in sorted(pages.items()):
        html = None
        if a.html_dir:
            for pid in pids:
                f = Path(a.html_dir) / f"{pid}.html"
                if f.exists():
                    html = f.read_text(encoding="utf-8")
                    break
        if html is None:
            if fetched:
                time.sleep(_PAUSE)   # GEM asked for a gentle rate against its own wiki
            fetched += 1
            try:
                r = requests.get(page, timeout=30, headers={"User-Agent": WIKI_UA})
                r.raise_for_status()
                html = r.text
            except Exception as e:                                  # noqa: BLE001
                # A fetch failure is a TOOLING result, never evidence about the page.
                page_stats.append({"page": page, "pids": pids, "error": str(e)})
                print(f"  FETCH FAILED {page}: {e}", file=sys.stderr)
                continue
        sections_by_page[page] = parse_sections(html)
        page_stats.append({"page": page, "pids": pids,
                           "n_sections": len(sections_by_page[page]), "attributions": 0})

    out, unmatched_pids, container, barren = [], [], [], []
    used_by_page: dict[str, set] = {p: set() for p in sections_by_page}
    stat_of = {p["page"]: p for p in page_stats}
    for page, pids in sorted(pages.items()):
        if page not in sections_by_page:
            continue
        n_before = len(out)
        miss: list[str] = []
        attribute_page(page, sections_by_page[page], pids, seg_of, owed,
                       out, miss, container, used_by_page[page], barren=barren, name_of=name_of)
        for pid in miss:
            # Cross-page fallback: try every OTHER page fetched in this run. Recorded as
            # `matched_via_page` so a reviewer can see the row was described elsewhere.
            hit = any(b["project_id"] == pid for b in barren)
            for other, secs in sections_by_page.items():
                if other == page or hit:
                    continue
                before, n_barren = len(out), len(barren)
                attribute_page(other, secs, [pid], seg_of, owed,
                               out, [], container, used_by_page[other],
                               home_page=page, barren=barren, name_of=name_of)
                if len(out) > before or len(barren) > n_barren:
                    hit = True
                    break
            if not hit:
                unmatched_pids.append((pid, seg_of.get(pid, "")))
        stat_of[page]["attributions"] = len(out) - n_before

    unused = [{"page": pg, "h3": sec["h3"]}
              for pg, secs in sections_by_page.items() for sec in secs
              if sec["norm"] and sec["norm"] not in used_by_page[pg] and not sec.get("page_level")]

    Path(a.out).write_text(json.dumps(
        {"pages": page_stats, "attributions": out,
         "unmatched_project_ids": unmatched_pids,
         "rows_without_wiki_page": no_wiki,
         "container_rows": container,
         "uncited_sections": barren,
         "unused_sections": unused},
        ensure_ascii=False, indent=2))

    print(f"wrote {a.out}")
    print(f"  pages fetched: {sum(1 for p in page_stats if 'error' not in p)}/{len(page_stats)}"
          f"   attributions: {len(out)}")
    print(f"  PIDs attributed: {len({r['project_id'] for r in out})}/{len(seg_of)}")
    print(f"  owed-on-row: {sum(1 for r in out if r['owed_on_row'])}"
          f"   already-cited-or-not-owed: {sum(1 for r in out if not r['owed_on_row'])}")
    if no_wiki:
        print(f"  rows with NO wiki page: {','.join(no_wiki)}")
    if barren:
        print("  UNCITED wiki sections (values stated, no citations to harvest):")
        for b in barren:
            via = f" via {b['matched_via_page'].split('/')[-1]}" if b.get("matched_via_page") else ""
            print(f"    {b['project_id']}  {b['wiki_section']}{via}")
    if container:
        print("  CONTAINER (network-granularity) rows:")
        for c in container:
            print(f"    {c['project_id']}  h3={c['wiki_section']!r}")
    if unmatched_pids:
        print("  UNMATCHED PIDs (no h3 joined — the row's own page names it differently):")
        for pid, seg in unmatched_pids:
            print(f"    {pid}  {seg!r}")


def attribute_page(page: str, sections: list[dict], pids: list[str],
                   seg_of: dict, owed: dict,
                   out: list, unmatched_pids: list, container: list,
                   used: set | None = None, home_page: str | None = None,
                   barren: list | None = None, name_of: dict | None = None) -> set:
    """Join this page's h3 sections onto `pids` and append their candidates to `out`.

    Join order: exact on `PipelineName SegmentName` ("TurkStream Gas Pipeline 1" vs the h3
    "TurkStream 1 Gas Pipeline" normalizes differently, so this is tried as a token set too),
    exact on the segment name, then substring (longest h3 wins). A bare numeric segment name
    ("1") joins only through the name+segment form, never by substring (2026-10-17)."""
    by_norm = {s["norm"]: s for s in sections if s["norm"]}
    # `Phase I` / `Phase II` normalize to "" (the phase token is deliberately stripped so
    # "Phase I, Fengcheng-Fuzhou" joins to the "Fengcheng-Fuzhou" h3). Keep them reachable
    # under a phase-preserving key: on these pages they are CONTAINER headings whose <ul>
    # is a list of constituent segment names and which carry no field bullets at all. A GEM
    # row whose segment_name is bare "Phase I" is therefore a network-granularity parent
    # row, and matching it here records that fact instead of reporting a false UNMATCHED.
    for sec in sections:
        k = re.sub(r"[^a-z0-9]+", "", (sec["h3"] or "").lower())
        if k and k not in by_norm:
            by_norm[k] = sec

    used = set() if used is None else used
    tokens_of = {k: set(re.findall(r"[a-z]+|\d+", (s["h3"] or "").lower())) for k, s in by_norm.items()}
    for pid in pids:
        seg = seg_of.get(pid, "")
        pname = (name_of or {}).get(pid, "")
        n = _norm(seg) or re.sub(r"[^a-z0-9]+", "", (seg or "").lower())
        sec = None
        if pname and seg:
            full = _norm(f"{pname} {seg}")
            sec = by_norm.get(full)
            if sec is None:
                want = set(re.findall(r"[a-z]+|\d+", f"{pname} {seg}".lower()))
                hits = [k for k, t in tokens_of.items() if t and t == want]
                sec = by_norm[hits[0]] if len(hits) == 1 else None
        if sec is None and n:
            sec = by_norm.get(n)
        if sec is None and n and not n.isdigit():  # substring fallback, longest match wins
            cands = [s for k, s in by_norm.items() if (n in k or k in n)]
            sec = max(cands, key=lambda s: len(s["norm"])) if cands else None
        if sec is None and home_page is None:
            # The row's OWN page with no h3 to join: a single-segment page states its details
            # directly under the "Project details" h2, and those describe this row.
            sec = next((s for s in sections if s.get("page_level")), None)
        if sec is None:
            unmatched_pids.append(pid)
            continue
        used.add(sec["norm"])
        if not sec["fields"]:
            container.append({"project_id": pid, "segment_name": seg, "page": page,
                              "wiki_section": sec["h3"],
                              "note": "wiki h3 is a CONTAINER heading (lists constituent "
                                      "segments, carries no field bullets) — this GEM row is "
                                      "network-granularity, not a segment"})
            continue
        n_before_sec = len(out)
        for f in sec["fields"]:
            mp = LABEL_MAP.get(f["label"])
            if not mp or not f["value"] or not f["urls"]:
                continue
            rec = {
                "project_id": pid,
                "ref_col": mp["ref_col"],
                "page": page,
                "wiki_section": sec["h3"],
                "wiki_label": f["label"],
                "wiki_value": f["value"],
                "candidate_urls": f["urls"],
                # which figure each footnote supports when the bullet lists several
                "value_parts": [pt for pt in f.get("parts") or [] if pt.get("urls")],
                "owed_on_row": mp["ref_col"] in owed.get(pid, set()),
            }
            if home_page:
                rec["matched_via_page"] = page
                rec["page"] = home_page
            if mp.get("tab"):
                rec["tab"] = mp["tab"]
            out.append(rec)
        if len(out) == n_before_sec and barren is not None:
            # The section EXISTS and states values — it just cites nothing for them.
            # That is a finding about GEM's own wiki page (uncited assertions a
            # researcher may be tempted to trust), not a failure of this join.
            barren.append({"project_id": pid, "segment_name": seg,
                           "page": home_page or page,
                           "matched_via_page": page if home_page else None,
                           "wiki_section": sec["h3"],
                           "stated_values": {f["label"]: f["value"] for f in sec["fields"]
                                             if f["value"]},
                           "note": "wiki section matched and states values, but carries NO "
                                   "citations — nothing to harvest, and the wiki's own "
                                   "numbers here are unsourced"})
    return used


if __name__ == "__main__":
    main()
