#!/usr/bin/env python3
"""Reference-sweep step 2: harvest the OUTBOUND citation URLs from each row's gem.wiki
page, so the agent starts research from sources GEM already used. We are allowed to
VISIT gem.wiki (we fetch it directly here) but must NEVER cite it (standing rule 1) —
so this returns only the *underlying* external URLs the page links to, with gem.wiki /
globalenergymonitor / theodora filtered out. Expect many to be dead; the agent verifies
each with url_verifier before use.

Harvested ONCE per ProjectID (one fetch serves every ref cell on the row).

    python scripts/harvest_wiki_citations.py --worklist .../worklist.json --out .../wiki_citations.json
    python scripts/harvest_wiki_citations.py --wiki "https://www.gem.wiki/East-West_Crude_Oil_Pipeline"
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.parse import urldefrag, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from url_verifier import BLOCKLIST_HOSTS, GEM_HOSTS, _MIN_INTERVAL, _UA  # noqa: E402

_DROP_HOSTS = GEM_HOSTS + BLOCKLIST_HOSTS


def _norm_url(u: str) -> str:
    """Normalize for dedup: drop fragment, strip trailing slash, lowercase host."""
    u = urldefrag(u or "")[0].strip()
    p = urlparse(u)
    host = (p.netloc or "").lower()
    path = (p.path or "").rstrip("/")
    return f"{p.scheme}://{host}{path}" + (f"?{p.query}" if p.query else "")


def _keep(url: str) -> bool:
    low = (url or "").lower()
    return low.startswith("http") and not any(h in low for h in _DROP_HOSTS)


def harvest_page(url: str, timeout: int = 25) -> dict:
    """Fetch one gem.wiki page and return {ok, status, citations:[...]}.
    Each citation: {url, link_text, context, cite_id, backlinks, section}."""
    if not (url or "").lower().startswith("http"):
        return {"ok": False, "status": None, "reason": "not an http(s) URL", "citations": []}
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError as e:
        return {"ok": False, "status": None, "reason": f"missing dep: {e.name} (pip install -r requirements.txt)", "citations": []}
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": _UA})
    except Exception as e:
        return {"ok": False, "status": None, "reason": f"request failed: {type(e).__name__}", "citations": []}
    if r.status_code != 200:
        return {"ok": False, "status": r.status_code, "reason": f"HTTP {r.status_code}", "citations": []}

    soup = BeautifulSoup(r.text, "html.parser")
    content = soup.select_one("#mw-content-text") or soup
    seen: set[str] = set()
    cites: list[dict] = []

    # 1) numbered references (the citations GEM actually used)
    for li in content.select("ol.references li[id^=cite_note]"):
        cite_id = li.get("id", "")
        backlinks = len(li.select(".mw-cite-backlink a")) or 1
        ctx = " ".join(li.get_text(" ", strip=True).split())[:300]
        for a in li.select("a.external[href^=http], a[href^=http].external"):
            href = a.get("href", "")
            if not _keep(href):
                continue
            key = _norm_url(href)
            if key in seen:
                continue
            seen.add(key)
            cites.append({
                "url": href,
                "link_text": " ".join(a.get_text(" ", strip=True).split())[:160],
                "context": ctx,
                "cite_id": cite_id,
                "backlinks": backlinks,
                "section": "references",
            })

    # 2) fallback: page-wide external links (External links section / inline) when the
    #    numbered references are thin
    if len(cites) < 2:
        for a in content.select("a.external[href^=http]"):
            href = a.get("href", "")
            if not _keep(href):
                continue
            key = _norm_url(href)
            if key in seen:
                continue
            seen.add(key)
            cites.append({
                "url": href,
                "link_text": " ".join(a.get_text(" ", strip=True).split())[:160],
                "context": "",
                "cite_id": "",
                "backlinks": 0,
                "section": "body",
            })

    return {"ok": True, "status": 200, "reason": "ok", "citations": cites}


def harvest_worklist(worklist_path: str) -> dict:
    wl = json.loads(Path(worklist_path).read_text())
    # unique (project_id -> wiki); one fetch per row
    pages: dict[str, str] = {}
    for u in wl.get("units", []):
        pid, wiki = u.get("project_id", ""), u.get("wiki", "")
        if wiki and pid and pid not in pages:
            pages[pid] = wiki
    out: dict[str, dict] = {}
    first = True
    for pid, wiki in pages.items():
        if not first:
            time.sleep(_MIN_INTERVAL)   # politeness: gem.wiki is one host
        first = False
        res = harvest_page(wiki)
        res["wiki"] = wiki
        out[pid] = res
        print(f"  {pid}: {'ok' if res['ok'] else res['reason']} — "
              f"{len(res['citations'])} citation(s)", file=sys.stderr)
    return {"generated_from": Path(worklist_path).name, "pages": out}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--worklist", help="worklist.json from build_ref_worklist.py")
    ap.add_argument("--wiki", help="single gem.wiki URL (debug)")
    ap.add_argument("--out", help="output JSON (required with --worklist)")
    args = ap.parse_args()

    if args.wiki:
        res = harvest_page(args.wiki)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return
    if not args.worklist or not args.out:
        ap.error("provide --worklist and --out (or --wiki for a single page)")

    data = harvest_worklist(args.worklist)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    npages = len(data["pages"])
    nok = sum(1 for p in data["pages"].values() if p["ok"])
    ncites = sum(len(p["citations"]) for p in data["pages"].values())
    print(f"wrote {out}")
    print(f"  pages: {npages} ({nok} fetched ok) — {ncites} external citations harvested "
          f"(gem.wiki/theodora excluded)")


if __name__ == "__main__":
    main()
