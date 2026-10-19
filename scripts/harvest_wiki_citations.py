#!/usr/bin/env python3
"""Reference-sweep step 2: harvest the OUTBOUND citation URLs from each row's gem.wiki
page, so the agent starts research from sources GEM already used. We are allowed to
VISIT gem.wiki (we fetch it directly here) but must NEVER cite it (standing rule 1) —
so this returns only the *underlying* external URLs the page links to, with gem.wiki /
globalenergymonitor and the url_verifier blocklist (theodora, A Barrel Full / wikidot.com)
filtered out. Expect many to be dead; the agent verifies each with url_verifier before use.

Harvested ONCE per ProjectID (one fetch serves every ref cell on the row).

    python scripts/harvest_wiki_citations.py --worklist .../worklist.json --out .../wiki_citations.json [--save-html .../wiki_pages]
    python scripts/harvest_wiki_citations.py --wiki "https://www.gem.wiki/East-West_Crude_Oil_Pipeline"

Each citation carries `inline`: the body bullet(s) or sentence(s) the footnote is attached to,
with the section heading (`Cost: US$7.8 billion` under `Project details` / `TurkStream`), so a
reader can see which data point GEM cited the source FOR, not only what the source is
(2026-10-17). `attribute_wiki.py` turns those bullets into per-ref-column candidates.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urldefrag, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from url_verifier import BLOCKLIST_HOSTS, GEM_HOSTS, WIKI_UA, _MIN_INTERVAL  # noqa: E402

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


_SUP_MARK_RE = re.compile(r"\[\s*\d+\s*\]")
_INLINE_PARENTS = ["li", "p", "td", "th", "dd", "h2", "h3", "caption", "div"]
_INLINE_CHARS = 300


def inline_contexts(content) -> dict[str, list[dict]]:
    """cite_note id -> where that footnote sits in the BODY: one {section, heading, text} per
    superscript, with `text` the bullet / sentence it is attached to.

    The reference-list entry says what a citation IS; this says what it was cited FOR. On a
    gem.wiki project page the details bullets read `Cost: US$7.8 billion [3]`, so the inline
    text names the field and the value the footnote supports (2026-10-17, P0765: the cost ref
    was in the harvest all along, but nothing said it backed the cost, and the agent closed the
    unit from an open-web search at low)."""
    out: dict[str, list[dict]] = {}
    for sup in content.select("sup.reference"):
        a = sup.find("a", href=True)
        if a is None:
            continue
        target = (a["href"] or "").split("#")[-1]
        if not target.startswith("cite_note"):
            continue
        parent = sup.find_parent(_INLINE_PARENTS)
        if parent is None:
            continue
        text = _SUP_MARK_RE.sub("", " ".join(parent.get_text(" ", strip=True).split()))
        text = " ".join(text.split()).strip(" ,;·")
        if parent.name == "div" and len(text) > 2 * _INLINE_CHARS:
            text = ""           # a whole page section, not a sentence: say nothing rather than noise
        h3 = parent.find_previous("h3")
        h2 = parent.find_previous("h2")
        # the h3 belongs to this spot only when it comes AFTER the nearest h2
        heading = h3 if (h3 is not None and (h2 is None or h3.sourceline is None or h2.sourceline is None
                                             or h3.sourceline > h2.sourceline)) else None
        rec = {
            "section": " ".join(h2.get_text(" ", strip=True).split()) if h2 is not None else "",
            "heading": " ".join(heading.get_text(" ", strip=True).split()) if heading is not None else "",
            "text": text[:_INLINE_CHARS],
        }
        if rec not in out.setdefault(target, []):
            out[target].append(rec)
    return out


def harvest_html(html: str) -> list[dict]:
    """Parse one gem.wiki page's HTML into its outbound citations (no fetching). Each
    citation: {url, link_text, context, cite_id, backlinks, section, inline:[{section,
    heading, text}]}. `inline` is where the footnote is used in the body — empty for a
    reference never cited inline and for the body-link fallback."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one("#mw-content-text") or soup
    inline = inline_contexts(content)
    seen: dict[str, dict] = {}
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
                # the same source cited under two footnotes: keep one citation, merge where it is used
                prev = seen[key]
                for rec in inline.get(cite_id, []):
                    if rec not in prev["inline"]:
                        prev["inline"].append(rec)
                prev["backlinks"] += backlinks
                continue
            rec = {
                "url": href,
                "link_text": " ".join(a.get_text(" ", strip=True).split())[:160],
                "context": ctx,
                "cite_id": cite_id,
                "backlinks": backlinks,
                "section": "references",
                "inline": list(inline.get(cite_id, [])),
            }
            seen[key] = rec
            cites.append(rec)

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
            parent = a.find_parent(_INLINE_PARENTS)
            text = " ".join(parent.get_text(" ", strip=True).split())[:_INLINE_CHARS] if parent is not None else ""
            rec = {
                "url": href,
                "link_text": " ".join(a.get_text(" ", strip=True).split())[:160],
                "context": "",
                "cite_id": "",
                "backlinks": 0,
                "section": "body",
                "inline": [{"section": "", "heading": "", "text": text}] if text else [],
            }
            seen[key] = rec
            cites.append(rec)
    return cites


def harvest_page(url: str, timeout: int = 25) -> dict:
    """Fetch one gem.wiki page and return {ok, status, citations:[...]} (see harvest_html)."""
    if not (url or "").lower().startswith("http"):
        return {"ok": False, "status": None, "reason": "not an http(s) URL", "citations": []}
    try:
        import requests
        import bs4  # noqa: F401
    except ImportError as e:
        return {"ok": False, "status": None, "reason": f"missing dep: {e.name} (pip install -r requirements.txt)", "citations": []}
    try:
        # WIKI_UA, not _UA: this fetches gem.wiki, where the agreed
        # token is our firewall identity. See url_verifier.WIKI_UA.
        r = requests.get(url, timeout=timeout, headers={"User-Agent": WIKI_UA})
    except Exception as e:
        return {"ok": False, "status": None, "reason": f"request failed: {type(e).__name__}", "citations": []}
    if r.status_code != 200:
        return {"ok": False, "status": r.status_code, "reason": f"HTTP {r.status_code}", "citations": []}
    return {"ok": True, "status": 200, "reason": "ok", "citations": harvest_html(r.text), "html": r.text}


def harvest_worklist(worklist_path: str, save_html: str | None = None) -> dict:
    """One fetch per ProjectID. With `save_html`, each page's HTML is saved as
    `<dir>/<PID>.html` so attribute_wiki.py / the pre-pass can re-parse it without
    fetching gem.wiki again (the JSON never embeds the HTML)."""
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
        html = res.pop("html", None)
        if html and save_html:
            d = Path(save_html)
            d.mkdir(parents=True, exist_ok=True)
            (d / f"{pid}.html").write_text(html, encoding="utf-8")
            res["html_file"] = str(d / f"{pid}.html")
        out[pid] = res
        print(f"  {pid}: {'ok' if res['ok'] else res['reason']} — "
              f"{len(res['citations'])} citation(s)", file=sys.stderr)
    return {"generated_from": Path(worklist_path).name, "pages": out}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--worklist", help="worklist.json from build_ref_worklist.py")
    ap.add_argument("--wiki", help="single gem.wiki URL (debug)")
    ap.add_argument("--out", help="output JSON (required with --worklist)")
    ap.add_argument("--save-html", help="directory to keep each fetched page as <PID>.html "
                                        "(lets attribute_wiki.py --html-dir re-parse offline)")
    ap.add_argument("--html", help="parse this saved HTML file instead of fetching (debug)")
    args = ap.parse_args()

    if args.html:
        print(json.dumps(harvest_html(Path(args.html).read_text(encoding="utf-8")),
                         indent=2, ensure_ascii=False))
        return
    if args.wiki:
        res = harvest_page(args.wiki)
        res.pop("html", None)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return
    if not args.worklist or not args.out:
        ap.error("provide --worklist and --out (or --wiki for a single page)")

    data = harvest_worklist(args.worklist, save_html=args.save_html)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    npages = len(data["pages"])
    nok = sum(1 for p in data["pages"].values() if p["ok"])
    ncites = sum(len(p["citations"]) for p in data["pages"].values())
    print(f"wrote {out}")
    print(f"  pages: {npages} ({nok} fetched ok) — {ncites} external citations harvested "
          f"(gem.wiki/theodora/abarrelfull/wikidot excluded)")


if __name__ == "__main__":
    main()
