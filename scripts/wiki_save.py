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

save() repoints every [[link]] to a redirect at the page's current title (resolve_links; Baird 2026-11-10).

save() previews the text first and refuses (CiteError) any page that would show a Cite error (Baird 2026-11-10).

save() refuses any page that is not a pipeline page (Baird 2026-11-10: this repo edits pipeline wiki pages and
nothing else): the title must be one the GOIT/GGIT snapshots name (Wiki cell, PipelineName, network columns) or one
of the pipeline pages' own stylesheets. No override. One narrow case passes: a redirect that already leads to a pipeline
page through another redirect may be pointed straight at it (redirect_repair_ok).
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


class NotAPipelinePage(RuntimeError):
    pass


class CiteError(RuntimeError):
    pass


_CITE_ERR = re.compile(r'<(span|strong|div)[^>]*class="[^"]*\bcite-error\b[^"]*"[^>]*>(.*?)</\1>', re.S)


def cite_errors(s, title, text):
    """The Cite errors the page would show, from a preview parse of the text (nothing is saved). Both error
    classes MediaWiki uses (cite-error, mw-ext-cite-error) count, plus any bare 'Cite error:' text."""
    p = _retry(lambda: g.post(s, action='parse', title=title, text=text, contentmodel='wikitext', prop='text', pst=1,
                              disablelimitreport=1))['parse']['text']
    html = p['*'] if isinstance(p, dict) else p
    errs = [re.sub('<[^>]+>', '', m.group(2))[:160] for m in _CITE_ERR.finditer(html)]
    if not errs and 'Cite error:' in re.sub('<[^>]+>', '', html):
        errs = ['Cite error text on the page']
    return errs


_LINK = re.compile(r'\[\[([^\[\]|#\n]+)(#[^\[\]|\n]*)?(\|[^\[\]\n]*)?\]\]')
_NS = re.compile(r'^\s*:|^\s*(file|image|media|category|template|help|special|user|w|wikipedia|gem|mediawiki)\s*:', re.I)


def resolve_links(s, text):
    """(text, changes): every [[link]] to a redirect points at the page's current title instead (Baird 2026-11-10:
    links go to the current name, never the old one that redirects). The shown words stay the same, and a
    redirect to a section keeps that section. Namespaced links (File:, Category: ...) are left alone."""
    targets = sorted({m.group(1).strip() for m in _LINK.finditer(text) if not _NS.match(m.group(1))})
    to = {}
    for i in range(0, len(targets), 40):
        q = _retry(lambda: g.get(s, action='query', titles='|'.join(targets[i:i + 40]), redirects=1))['query']
        norm = {n['from']: n['to'] for n in q.get('normalized', [])}
        red = {r['from']: (r['to'], r.get('tofragment', '')) for r in q.get('redirects', [])}
        for t in targets[i:i + 40]:
            n = norm.get(t, t)
            if n in red:
                to[t] = red[n]
    changes = []

    def sub(m):
        t = m.group(1).strip()
        if t not in to:
            return m.group(0)
        new, frag = to[t]
        frag = m.group(2) or (f'#{frag}' if frag else '')
        label = m.group(3) or f'|{m.group(1)}'
        changes.append(f'{t} -> {new}{frag}')
        return f'[[{new}{frag}{label}]]'
    return _LINK.sub(sub, text), changes


# The only non-article pages this repo may save: the pipeline pages' own stylesheets (generate_pages.ensure_styles).
PIPELINE_TEMPLATES = {'Template:Segment table/styles.css', 'Template:Pipeline map/styles.css'}
_PIPELINE_TITLES = None


def pipeline_titles():
    """Every page title the GOIT and GGIT snapshots point at or name: the Wiki cell's page, PipelineName, and the
    network columns. A page outside this set is not a pipeline page."""
    global _PIPELINE_TITLES
    if _PIPELINE_TITLES is None:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'wiki' / 'scripts'))
        import _common as C
        out = set()
        for tracker in ('gas', 'oil'):
            df = C.load(tracker)
            out |= {C.page_name(u) for u in df.get('Wiki', [])}
            for col in ('PipelineName', 'PrimaryNetwork', 'SecondaryNetworks', 'PipelineNetworkGrouping'):
                for v in df.get(col, []):
                    out |= {x.strip() for x in str(v).split(',' if col == 'SecondaryNetworks' else '\x00')}
        out.add('Chinese Gas Pipeline Networks')   # network_pages.OVERVIEW_PAGE
        _PIPELINE_TITLES = {t.replace('_', ' ') for t in out if t}
    return _PIPELINE_TITLES


def check_pipeline_page(title):
    """Baird 2026-11-10: this repo edits pipeline wiki pages and nothing else. Raises NotAPipelinePage."""
    t = title.replace('_', ' ').strip()
    if t in PIPELINE_TEMPLATES or t in pipeline_titles():
        return
    raise NotAPipelinePage(f'{title}: not a pipeline page in the GOIT/GGIT snapshots; this repo saves only pipeline pages')


_REDIRECT_ONLY = re.compile(r'^\s*#REDIRECT\s*\[\[([^\]|#]+)(#[^\]|]*)?\]\]\s*((\[\[Category:[^\]]*\]\]\s*)*)$', re.I)


def redirect_repair_ok(s, title, text):
    """True when saving `text` on a non-pipeline title only shortens a redirect chain into a pipeline page
    (Baird 2026-11-10, "Guangdong Gas Pipeline Network Phase I": a redirect to a redirect strands readers). The
    page must already be a redirect, the chain it starts must end at a pipeline page, and the new text must be a
    bare #REDIRECT to that same page (categories it already had may stay)."""
    m = _REDIRECT_ONLY.match(text or '')
    if not m or m.group(1).strip() not in pipeline_titles():
        return False
    q = _retry(lambda: g.get(s, action='query', titles=title, redirects=1, prop='info'))['query']
    chain = q.get('redirects', [])
    if chain:
        return chain[-1]['to'] == m.group(1).strip()
    # a redirect written without its # ("Redirect [[Tianjin Gas Pipeline Network]]") shows as text and sends no
    # one anywhere (Baird 2026-11-10); making it a real #REDIRECT to the same pipeline page, or to where that
    # page now redirects, is the same repair
    cur = _retry(lambda: g.get(s, action='query', prop='revisions', titles=title, rvprop='content', rvslots='main'))['query']['pages'][0]
    old = ((cur.get('revisions') or [{}])[0].get('slots', {}).get('main', {}).get('content') or '')
    bm = re.search(r'(?mi)^[^\S\n]*redirect\s*(?:to)?\s*:?\s*\[\[([^\]|#]+)', old)
    if not bm or old.lstrip().upper().startswith('#REDIRECT'):
        return False
    t = _retry(lambda: g.get(s, action='query', titles=bm.group(1).strip(), redirects=1))['query']
    final = (t.get('redirects') or [{'to': (t.get('normalized') or [{'to': bm.group(1).strip()}])[-1]['to']}])[-1]['to']
    return final == m.group(1).strip()


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
    if text and '~~~' in re.sub(r'(?s)<nowiki>.*?</nowiki>', '', text):
        # MediaWiki turns ~~~ into the editor's signature on save; in a map's lines= it breaks the map (2026-11-10)
        raise ValueError(f'{title}: text holds ~~~, which saves as a signature; refusing to save')
    if not redirect_repair_ok(s, title, text):
        check_pipeline_page(title)
    relinked = []
    if text and not text.lstrip().upper().startswith('#REDIRECT'):
        # links point at current titles, never at a redirect (Baird 2026-11-10)
        text, relinked = resolve_links(s, text)
        # a page that would show a Cite error is never saved, whichever script built it (Baird 2026-11-10)
        errs = cite_errors(s, title, text)
        if errs:
            raise CiteError(f'{title}: {len(errs)} Cite error(s) in the preview, not saved: {errs[:3]}')
    r = g.edit_page(s, title, text=text, summary=summary, bot=False, **kw)  # the account has no bot right
    r['map'] = purge_until_ok(s, title)
    r['relinked'] = relinked
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
