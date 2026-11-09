#!/usr/bin/env python3
"""Save a gem.wiki page the one safe way: edit, purge, prove the map renders.

A page saved through the API is cached WITHOUT the Google Maps script tag, so readers see "Your browser is
not compatible with Google Maps v3" under a map whose markup is fine. A purge re-renders it with the script.
Every save in this repo therefore goes through save() here, never gemwiki.edit_page() directly; the
PreToolUse hook .claude/hooks/guard-wiki-save.py blocks a shell command that calls edit_page outside this
module (Baird 2026-11-06, after Idku-Abu Hummus I and Kuraimat-Al Tebbin were posted by hand with no purge;
about 100 US pages lost their maps the same way on 2026-11-05).

    from wiki_save import save
    r = save(s, title, text=wikitext, summary='new gas pipeline page')   # s = gemwiki.session(login=True)
    r['newrevid'], r['map']   # r['map'] = {'maps': n, 'script': True, 'broken': False}

save() raises MapBroken when three purges still leave a mapped page without the script, so a bulk run
stops instead of leaving a page that looks saved and renders broken.

    python scripts/wiki_save.py --title "X Gas Pipeline" --file draft.wiki --summary "new gas pipeline page"
    python scripts/wiki_save.py --check --since 2026-11-06            # every page the account saved since, API check
    python scripts/wiki_save.py --check --titles "A" "B" --purge      # purge the broken ones and re-check

The check reads the parser cache through action=parse (prop=text|headhtml), the copy readers get. It is not
curl: Cloudflare challenges curl and a challenge page holds no map div, which once read as "0 with a map"
on a day two pages were broken (2026-11-06). The map must also be confirmed in a real browser on a pilot
page: python scripts/wiki_map_check.py <url>.

Every successful save also upserts the page's row in the backend sheet's `Wiki overhaul (Nov 2026)` tab (wiki_log.py;
standing permission, Baird 2026-11-09). A failed sheet write is queued in work/wiki_log_pending.jsonl and
never fails the save.
"""
import argparse, json, re, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'goit-ggit-data-ops' / 'gem-wiki'))
import gemwiki as g
import wiki_log

ACCOUNT = 'Baird Langenbrunner'


class MapBroken(RuntimeError):
    pass


def _retry(fn, n=6, wait=10):
    last = None
    for _ in range(n):
        try:
            return fn()
        except Exception as e:  # 503s and rate limits on a long run
            last = e
            time.sleep(wait)
    raise last


def map_state(s, title):
    """{'maps': n, 'script': bool, 'broken': bool} for the page as the parser cache serves it."""
    p = _retry(lambda: g.get(s, action='parse', page=title, prop='text|headhtml'))['parse']
    maps = len(re.findall(r'class="[^"]*maps-googlemaps3', p['text']))  # map elements, not a stylesheet page that names the class
    script = 'maps.googleapis.com' in p['headhtml']
    return {'title': title, 'maps': maps, 'script': script, 'broken': bool(maps and not script)}


def purge(s, title):
    for wait in (0, 20, 60, 120):  # the purge API rate-limits a long run; back off and retry
        time.sleep(wait)
        resp = _retry(lambda: g.post(s, action='purge', titles=title, forcelinkupdate='1'))
        if 'ratelimit' not in json.dumps(resp).lower():
            return resp
    raise RuntimeError('purge rate-limited: ' + title)


def purge_until_ok(s, title, tries=3):
    st = None
    for _ in range(tries):
        purge(s, title)
        time.sleep(2)
        st = map_state(s, title)
        if not st['broken']:
            return st
    raise MapBroken(f'{title}: map still has no Google Maps script after {tries} purges')


def save(s, title, text=None, summary='', **kw):
    """gemwiki.edit_page + purge + map check. The session must be logged in. Returns the edit dict plus 'map'."""
    r = g.edit_page(s, title, text=text, summary=summary, bot=False, **kw)  # the account has no bot right
    r['map'] = purge_until_ok(s, title)
    if r.get('result') == 'Success' and 'nochange' not in r:
        wiki_log.record(title, summary, text)   # the backend sheet's 'Wiki overhaul (Nov 2026)' tab; never raises
    return r


def saved_since(s, since, user=ACCOUNT):
    return sorted({c['title'] for c in g.user_contribs(s, user, end=f'{since}T00:00:00Z') if c.get('ns', 0) == 0})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--title'); ap.add_argument('--file'); ap.add_argument('--summary', default='')
    ap.add_argument('--check', action='store_true', help='check maps instead of saving')
    ap.add_argument('--since', help='YYYY-MM-DD for --check; default 7 days ago')
    ap.add_argument('--titles', nargs='+'); ap.add_argument('--purge', action='store_true')
    ap.add_argument('--out', help='write the per-page results as JSON')
    a = ap.parse_args()
    if a.check:
        s = g.session(login=True)
        titles = a.titles or saved_since(s, a.since or (datetime.now(timezone.utc) - timedelta(days=7)).strftime('%Y-%m-%d'))
        print(f'checking {len(titles)} pages', flush=True)
        res = []
        for t in titles:
            st = map_state(s, t)
            if st['broken'] and a.purge:
                try:
                    st = purge_until_ok(s, t); st['repaired'] = True
                except MapBroken as e:
                    st['repaired'] = False; print('STILL BROKEN', t, flush=True)
            res.append(st)
            print('BROKEN' if st['broken'] else ('ok' if st['maps'] else 'no map'), '|', t, flush=True)
            time.sleep(0.5)
        broken = [r['title'] for r in res if r['broken']]
        print(f"{len(res)} pages, {sum(1 for r in res if r['maps'])} with a map, {len(broken)} broken {broken}")
        if a.out:
            json.dump(res, open(a.out, 'w'), indent=1)
        sys.exit(1 if broken else 0)
    if not (a.title and a.file):
        ap.error('--title and --file, or --check')
    s = g.session(login=True)
    r = save(s, a.title, text=open(a.file).read(), summary=a.summary)
    print(r['result'], r.get('newrevid'), r['map'], 'https://www.gem.wiki/' + a.title.replace(' ', '_'))


if __name__ == '__main__':
    main()
