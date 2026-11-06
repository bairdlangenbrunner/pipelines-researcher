#!/usr/bin/env python3
"""Open gem.wiki pages in a real (headless) Chrome and say whether each map renders.

    python scripts/wiki_map_check.py https://www.gem.wiki/Some_Gas_Pipeline [more urls]

A working map's text starts "Map Satellite" and the page holds a .gm-style element; a broken one shows
"Your browser is not compatible with Google Maps v3". The API check in wiki_save.py is the routine one; this
is the pilot-page confirmation (docs/sops/wiki_pages.md). The browser carries the GEMWIKI_USER_AGENT identity,
without which Cloudflare serves a challenge page and the check reads as "no map" (2026-11-06).
Exit 1 if any page's map is broken or a mapped page could not be loaded.
"""
import os, sys
from playwright.sync_api import sync_playwright

urls = sys.argv[1:]
ua = os.environ.get('GEMWIKI_USER_AGENT')
if not ua:
    sys.exit('GEMWIKI_USER_AGENT is not set; Cloudflare will challenge the browser')
bad = 0
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", headless=True)
    ctx = b.new_context(user_agent=ua)
    for u in urls:
        pg = ctx.new_page(); logs = []
        pg.on("console", lambda m: logs.append(f"{m.type}: {m.text[:200]}") if m.type in ('error', 'warning') else None)
        pg.on("pageerror", lambda e: logs.append(f"PAGEERROR: {str(e)[:300]}"))
        try:
            pg.goto(u, wait_until="domcontentloaded", timeout=90000)
        except Exception as e:
            print("\n##", u, "LOAD FAILED", str(e)[:80]); bad += 1; pg.close(); continue
        try:
            pg.wait_for_selector(".gm-style", timeout=30000)
        except Exception:
            pass
        pg.wait_for_timeout(3000)
        title = pg.title()
        m = pg.query_selector(".maps-map")
        text = m.inner_text()[:150] if m else None
        gm = len(pg.query_selector_all(".gm-style"))
        challenged = 'Just a moment' in title or 'challenges.cloudflare.com' in pg.content()[:20000] and not m
        verdict = ('CHALLENGED' if challenged else 'BROKEN' if (m and (gm == 0 or 'not compatible' in (text or '')))
                   else 'ok' if m else 'no map')
        if verdict in ('BROKEN', 'CHALLENGED'):
            bad += 1
        print(f"\n## {verdict} | {u}\n   title: {title}\n   map text: {text!r} | gm-style: {gm}")
        for l in [l for l in logs if 'data:,' not in l and 'OTS parsing' not in l][:6]:
            print("  ", l)
        pg.close()
    b.close()
sys.exit(1 if bad else 0)
