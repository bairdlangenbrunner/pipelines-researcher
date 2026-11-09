#!/usr/bin/env python3
"""Keep the `wiki-overhaul` tab of the backend sheet listing every gem.wiki page the agent has saved.

One row per page: pipelinename (the page title), wiki (its URL), last updated (YYYY-MM-DD, Eastern), reason
(plain words for what the edits did, newest first). Baird asked for it 2026-11-09 and gave standing permission
to update this one tab on every wiki save; it covers that tab only, upsert only, nothing else in the sheet.

wiki_save.save() calls record() after every save, so nothing needs to be done by hand. A failed sheet write
never fails the wiki save: the entry goes to work/wiki_log_pending.jsonl and the next record() (or --flush)
writes it.

    python scripts/wiki_log.py --rebuild --since 2026-07-01            # plan the tab from the account's edit history
    python scripts/wiki_log.py --rebuild --since 2026-07-01 --apply    # write it
    python scripts/wiki_log.py --flush                                 # write entries a failed save left behind

The rebuild counts an edit as the agent's when it is in the main namespace, on or after --since, and its edit
summary is not empty and not only MediaWiki's automatic "/* Section */" label (those are hand edits in the
browser), and the page is a pipeline page (terminal, FSRU and power plant pages saved by the terminal repos
under the same account are left out). The account is Baird's own, so edits before July 2026 are his.
"""
import argparse, json, os, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

SHEET_ID = '1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek'
TAB = 'wiki-overhaul'
HEADER = ['pipelinename', 'wiki', 'last updated', 'reason']
PENDING = Path(__file__).resolve().parents[1] / 'work' / 'wiki_log_pending.jsonl'
ET = ZoneInfo('America/New_York')

_REASONS = [
    (r'moved page', 'page renamed'),
    (r'^Redirected page|Changed redirect target', 'redirect'),
    (r'^new (gas pipeline )?page|^new page|^Created (blank )?page|^network page', 'new page'),
    (r'restore orphaned ref', 'restored missing citations'),
    (r'full-width map|sentence-case|map colors', 'layout update'),
    (r'self-evident|table pointer|segment-count', 'removed the segment table sentence'),
    (r'links to missing pages|empty subsections', 'removed links to missing pages'),
    (r'^add background', 'added Background text'),
    (r'tense|status|grammar', 'status, tense and grammar fixes'),
    (r'dead|archive|links? moved|moved .*links|shortlink|giignl|banned|a barrel full|wayback|sohu|unbracket|citation|\bref', 'fixed citation links'),
    (r'^generated from the tracker|^regenerate|^rebuild|generated from the tracker', 'page rebuilt from the tracker'),
    (r'new segments|add segments', 'added segments and redrew the map'),
    (r'map|route', 'route map update'),
    (r'table|heading|column|font|location wording|number the segments|lead|Ownership|stylesheet|see-all', 'layout update'),
]


def reason(summary):
    for pat, words in _REASONS:
        if re.search(pat, summary or '', re.I):
            return words
    return (summary or 'edit').strip()[:80]


# Pages the terminal researcher repos edit under the same account; they are not pipeline pages.
NOT_PIPELINE = re.compile(r'Terminal|FSRU|FLNG|Power Plant|Offshore Port|Deepwater Port|Offshore Oil Port|'
                          r'^LNG |LNG$| LNG (Hub|Cluster|Project|\()', re.I)


def is_pipeline_page(title):
    return ':' not in title.split(' ')[0] and not (NOT_PIPELINE.search(title) and 'Pipeline' not in title)


def is_agent_summary(summary):
    s = (summary or '').strip()
    return bool(s) and not re.fullmatch(r'/\*.*?\*/\s*', s)


def url(title):
    return 'https://www.gem.wiki/' + title.replace(' ', '_')


def _gws(config, *args):
    env = dict(os.environ, GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser(f'~/.config/{config}'),
               GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND='file')
    p = subprocess.run(['gws', 'sheets', 'spreadsheets', 'values', *args], capture_output=True, text=True, env=env)
    if p.returncode != 0:
        raise RuntimeError(f'gws {args[0]} failed: {p.stderr.strip()[:300]}')
    out = p.stdout
    return json.loads(out[out.index('{'):])


def read_tab():
    r = _gws('gws-gem', 'get', '--params', json.dumps({'spreadsheetId': SHEET_ID, 'range': f"'{TAB}'!A:D",
                                                        'valueRenderOption': 'FORMULA'}))
    return r.get('values', [])


def merge(entries, rows):
    """entries: [{'title','date','reason'}] newest last. Returns (updates {rownum: row}, appends [row])."""
    index = {r[0]: i + 1 for i, r in enumerate(rows) if r and i > 0}   # title -> 1-based sheet row
    cur = {r[0]: (list(r) + ['', '', '', ''])[:4] for r in rows[1:] if r}
    updates, appends, fresh = {}, [], {}
    for e in entries:
        t = e['title']
        row = fresh.get(t) or updates.get(index.get(t)) or cur.get(t) or [t, url(t), '', '']
        reasons = [x.strip() for x in str(row[3]).split(';') if x.strip()]
        if e['reason'] in reasons:
            reasons.remove(e['reason'])
        row = [t, url(t), max(str(row[2]), e['date']), '; '.join([e['reason']] + reasons)]
        if t in index:
            updates[index[t]] = row
        else:
            fresh[t] = row
    appends = list(fresh.values())
    return updates, appends


def write(updates, appends, header_ok=True):
    data = [{'range': f"'{TAB}'!A{n}:D{n}", 'values': [row]} for n, row in sorted(updates.items())]
    if not header_ok:
        data.insert(0, {'range': f"'{TAB}'!A1:D1", 'values': [HEADER]})
    if data:
        _gws('gws-gem-write', 'batchUpdate', '--params', json.dumps({'spreadsheetId': SHEET_ID}),
             '--json', json.dumps({'valueInputOption': 'RAW', 'data': data}))
    for i in range(0, len(appends), 500):
        _gws('gws-gem-write', 'append', '--params', json.dumps({
            'spreadsheetId': SHEET_ID, 'range': f"'{TAB}'!A:D", 'valueInputOption': 'RAW',
            'insertDataOption': 'INSERT_ROWS'}), '--json', json.dumps({'values': appends[i:i + 500]}))


def upsert(entries):
    rows = read_tab()
    if any(str(c).startswith('=') for r in rows for c in r):   # never write over a formula
        raise RuntimeError(f'{TAB} holds a formula cell; not writing')
    updates, appends = merge(entries, rows)
    write(updates, appends, header_ok=bool(rows) and rows[0][:4] == HEADER)
    return updates, appends


def _pending():
    if not PENDING.exists():
        return []
    return [json.loads(l) for l in PENDING.read_text().splitlines() if l.strip()]


def record(title, summary):
    """Called by wiki_save.save() after a successful save. Never raises."""
    if ':' in title.split(' ')[0]:   # MediaWiki:, File:, Template: pages are not pipeline pages
        return
    entry = {'title': title, 'date': datetime.now(ET).strftime('%Y-%m-%d'), 'reason': reason(summary)}
    entries = _pending() + [entry]
    try:
        upsert(entries)
        if PENDING.exists():
            PENDING.unlink()
    except Exception as e:  # the wiki save already happened; keep the entry for the next call
        PENDING.parent.mkdir(exist_ok=True)
        with PENDING.open('a') as f:
            f.write(json.dumps(entry) + '\n')
        print(f'WARNING: {TAB} tab not updated for {title} ({e}); queued in {PENDING}', file=sys.stderr)


def from_history(since):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'goit-ggit-data-ops' / 'gem-wiki'))
    import gemwiki as g
    s = g.session(login=True)
    contribs = g.user_contribs(s, 'Baird Langenbrunner', end=f'{since}T00:00:00Z')
    edits = sorted((c for c in contribs if c.get('ns', 0) == 0 and is_agent_summary(c.get('comment'))
                    and is_pipeline_page(c['title'])),
                   key=lambda c: c['timestamp'])
    out = []
    for c in edits:
        ts = datetime.strptime(c['timestamp'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
        out.append({'title': c['title'], 'date': ts.astimezone(ET).strftime('%Y-%m-%d'),
                    'reason': reason(c['comment'])})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--rebuild', action='store_true')
    ap.add_argument('--since', default='2026-07-01')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--flush', action='store_true')
    a = ap.parse_args()
    if a.flush:
        p = _pending()
        if p:
            upsert(p); PENDING.unlink()
        print(f'flushed {len(p)} entries')
        return
    if not a.rebuild:
        ap.error('--rebuild or --flush')
    entries = from_history(a.since)
    rows = read_tab()
    updates, appends = merge(entries, rows)
    print(f'{len(entries)} agent edits on {len({e["title"] for e in entries})} pages; '
          f'{len(updates)} rows to update, {len(appends)} to add')
    for r in (list(updates.values()) + appends)[:15]:
        print(' | '.join(r))
    if a.apply:
        write(updates, appends, header_ok=bool(rows) and rows[0][:4] == HEADER)
        after = read_tab()
        print(f'{TAB} now holds {len(after) - 1} pages')


if __name__ == '__main__':
    main()
