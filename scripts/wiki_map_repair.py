#!/usr/bin/env python3
"""Find and repair gem.wiki pages whose route map does not load.

A page saved through the API can be cached without the Google Maps script tag; the browser then
shows "Your browser is not compatible with Google Maps v3" (docs/sops/wiki_pages.md, "Purge and
check the map"). The markup is fine; a purge re-renders the page with the script.

python scripts/wiki_map_repair.py                         # scan pages the wiki account saved in the last 7 days
python scripts/wiki_map_repair.py --since 2026-09-01      # wider window
python scripts/wiki_map_repair.py --titles "Kern River Gas Pipeline" "EPIC NGL Pipeline"
python scripts/wiki_map_repair.py --purge                 # also purge every broken page and re-check it

A page is broken when its rendered HTML has a Maps div (maps-googlemaps3) but no
maps.googleapis.com script. The check reads the page as a reader's browser gets it. Purging changes
no content. Confirm a few in a real browser with scripts/wiki_map_check.py.
"""
import argparse, json, re, subprocess, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'goit-ggit-data-ops' / 'gem-wiki'))
import gemwiki as g

BROWSER_UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/130.0 Safari/537.36')
ACCOUNT = 'Baird Langenbrunner'


def rendered(title):
    url = 'https://www.gem.wiki/' + quote(title.replace(' ', '_'), safe="/()!,;:@$*'")  # MediaWiki's own link form; the %28 form can hit a stale cache copy
    out = subprocess.run(['curl', '-sL', '--compressed', '-A', BROWSER_UA, '-w', '\n%{http_code}', url],
                         capture_output=True, text=True).stdout
    html, _, code = out.rpartition('\n')
    return code, html


def state(title):
    code, html = rendered(title)
    maps = len(re.findall(r'class="maps-map maps-googlemaps3"', html))
    script = 'maps.googleapis.com/maps/api/js' in html
    empty = len(re.findall(r'data-mw-maps-mapdata="[^"]*&quot;centre&quot;:false', html))
    return {'title': title, 'code': code, 'maps': maps, 'script': script,
            'broken': bool(maps and not script), 'empty_maps': empty}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--since', help='YYYY-MM-DD; default 7 days ago')
    ap.add_argument('--user', default=ACCOUNT)
    ap.add_argument('--titles', nargs='+')
    ap.add_argument('--purge', action='store_true')
    ap.add_argument('--out', help='write the per-page results as JSON')
    a = ap.parse_args()

    s = g.session()
    if a.titles:
        titles = a.titles
    else:
        since = a.since or (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d')
        titles = sorted({c['title'] for c in g.user_contribs(s, a.user, end=f'{since}T00:00:00Z')
                         if c.get('ns', 0) == 0})
    print(f'checking {len(titles)} pages', flush=True)

    res = []
    for t in titles:
        r = state(t)
        res.append(r)
        if r['broken']:
            print('BROKEN', t, flush=True)
        time.sleep(1)
    broken = [r for r in res if r['broken']]
    print(f'{len(res)} pages, {sum(1 for r in res if r["maps"])} with a map, {len(broken)} broken')

    if a.purge and broken:
        ws = g.session(login=True)
        for r in broken:
            for wait in (0, 30, 60, 120):  # the purge API rate-limits a long run; back off and retry
                time.sleep(wait)
                resp = g.post(ws, action='purge', titles=r['title'], forcelinkupdate='1')
                if 'rate limit' not in json.dumps(resp.get('warnings', '')):
                    break
            time.sleep(2)
            after = state(r['title'])
            r['after_purge'] = 'fixed' if not after['broken'] else 'STILL BROKEN'
            print(r['after_purge'], r['title'], flush=True)
            time.sleep(1)
        still = [r['title'] for r in broken if r['after_purge'] != 'fixed']
        print(f'purged {len(broken)}: {len(broken) - len(still)} fixed, {len(still)} still broken {still}')

    empty = [r['title'] for r in res if r['empty_maps']]
    if empty:
        print(f'{len(empty)} pages also hold an empty map block (no lines, no center): {empty}')
    if a.out:
        json.dump(res, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
