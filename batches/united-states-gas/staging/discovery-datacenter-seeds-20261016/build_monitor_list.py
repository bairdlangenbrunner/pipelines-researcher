"""US gas data center monitor list, ready to paste into a Google Sheet (run from repo root).

Reads every `discovery-datacenter-*` run under the US staging dir (any date, so later rounds are picked up), takes each
seed's latest disposition (runs ordered by staged_new.json / found_seeds mtime, later wins) plus the candidates a run
classed `monitor`, and writes one row per lead that is still `monitor`. Seeds a later run queued or matched drop off.
Plain-language columns per the notes style rule; the reason text is the researcher's own.

    python batches/united-states-gas/staging/discovery-datacenter-seeds-20261016/build_monitor_list.py [--next-check 2027-01-15]

Writes batches/united-states-gas/deliverables/US_gas_datacenter_monitor_<date>.xlsx (tabs: Watch list, Gas arrives
without new pipe, About) and a CSV of the watch list beside it.
"""
import argparse, datetime as dt, glob, json, os, re
import pandas as pd

ST = 'batches/united-states-gas/staging'
OUT = 'batches/united-states-gas/deliverables'
STATE = {'TX': 'Texas', 'NM': 'New Mexico', 'LA': 'Louisiana', 'MS': 'Mississippi', 'AL': 'Alabama', 'FL': 'Florida',
         'PA': 'Pennsylvania', 'OH': 'Ohio', 'WV': 'West Virginia', 'VA': 'Virginia', 'MD': 'Maryland', 'KY': 'Kentucky',
         'TN': 'Tennessee', 'GA': 'Georgia', 'SC': 'South Carolina', 'NC': 'North Carolina', 'OK': 'Oklahoma',
         'KS': 'Kansas', 'NE': 'Nebraska', 'IA': 'Iowa', 'MO': 'Missouri', 'AR': 'Arkansas', 'IL': 'Illinois',
         'IN': 'Indiana', 'MI': 'Michigan', 'WI': 'Wisconsin', 'MN': 'Minnesota', 'ND': 'North Dakota',
         'SD': 'South Dakota', 'CA': 'California', 'NV': 'Nevada', 'UT': 'Utah', 'AZ': 'Arizona', 'CO': 'Colorado',
         'WY': 'Wyoming', 'MT': 'Montana', 'ID': 'Idaho', 'OR': 'Oregon', 'WA': 'Washington', 'AK': 'Alaska',
         'NY': 'New York', 'NJ': 'New Jersey', 'DE': 'Delaware'}
# Behind the meter means the power skips the grid, not that the gas skips a pipe, so it is not a no-new-pipe signal.
NO_PIPE = re.compile(r'no new (gas )?(pipe|pipeline|lateral)|(served|supplied|fed) (by|from) (an? |the )?existing|'
                     r'(tap|taps|tapping|connects?|interconnect(s|ion)?) (on|into|off|to|with) (an? |the )?existing|'
                     r'existing (on.site )?(gas )?(supply|lateral|interconnect|delivery point)|already (has|connected|served)|'
                     r'own (nearby )?(wells|fields)|field gas|associated gas from', re.I)
NO_TIE = re.compile(r'NO_DC_TIE|no (us )?data center (tie|named|or large)|no validated ref .*data center|not tied to (a )?data center|'
                    r'data center tie (is )?(not|un)', re.I)
NO_STEP = re.compile(r'concrete.step|no concrete|endpoints? (unknown|not found)|no filing|no route|no length|length unknown|'
                     r'on length|compression.only|falls inside P\d', re.I)
NOT_FOUND = re.compile(r'NOT_FOUND|not found|no source (names|says|on)|no (dedicated )?(gas )?(lateral|supplier|pipeline) '
                       r'(found|named)|no gas supplier', re.I)
# State names that are also inside pipeline company names; stripped before reading a state out of free text.
PIPE_CO = re.compile(r'Texas (Eastern|Gas)|Tennessee Gas|Florida Gas|Colorado Interstate|Mississippi River( Transmission)?|'
                     r'Alabama.Tennessee|Ohio Valley|Southern Star|Kern River|Northwest Pipeline|Arkansas.Oklahoma|'
                     r'Gulf South|Iroquois|Wyoming Interstate|Oklahoma Natural', re.I)
GOGPT = '../gem-db-ops/gogpt/gem_export_gogpt.csv'
CATS = {
    'no_pipe': ('Gas arrives without a new pipeline so far',
                'A source announcing a new lateral, header or supply line instead of the on-site or existing-line supply'),
    'no_tie': ('Pipeline known, data center tie not shown',
               'A source tying the pipeline, or the power plant it feeds, to data center demand'),
    'no_step': ('Pipeline named, few public details',
                'Any filing, permit, route, length or contract for the pipeline itself'),
    'not_found': ('Supply pipeline not identified yet',
                  'A named lateral or supply pipeline: a FERC filing or prior notice, a state permit, or a company statement'),
}
RECHECK = ('Ruling 2026-10-18: a tie through a power plant counts and a data center pipeline is added even when its '
           'endpoints are not public. Re-checked in the next round.')
RECHECKED = 'Checked {} under the 2026-10-18 rulings. Still a monitor item.'


def norm(name):
    return ' '.join(re.sub(r'\b(gas|supply|pipeline|project|power|station|plant)\b', ' ',
                           re.sub(r'\((?!group)[^)]*\)|[^a-z0-9 ]', ' ', (name or '').lower())).split())


def where_to_watch(state, cat):
    w = ['company earnings calls and releases']
    if state.startswith('Texas'):
        w.insert(0, 'Texas Railroad Commission T-4 pipeline permits')
    else:
        w.insert(0, 'FERC eLibrary (new CP dockets and prior notices)')
    w.append('state siting board and air permit dockets for the power plant' if cat in ('not_found', 'no_pipe')
             else 'state utility commission dockets')
    return '; '.join(w)


def hint_field(hint, pat):
    m = re.search(pat, hint or '')
    return m.group(1).strip() if m else ''


def load():
    seeds, ledger, cands = {}, {}, {}
    runs = []
    for d in glob.glob(f'{ST}/discovery-datacenter-*'):
        if d.endswith('-seeds-20261016') or not os.path.isdir(d):
            continue
        f = f'{d}/staged_new.json'
        files = [f] if os.path.exists(f) else glob.glob(f'{d}/discovery/found_seeds-*.json')
        if files:
            runs.append((max(os.path.getmtime(x) for x in files), d, files))
    for _, d, files in sorted(runs):
        if os.path.exists(f'{d}/args.json'):
            for s in json.load(open(f'{d}/args.json')).get('seeds', []):
                seeds.setdefault(s['seed_id'], s)
        run_date = dt.date.fromtimestamp(max(os.path.getmtime(x) for x in files)).isoformat()
        for f in files:
            j = json.load(open(f))
            led = j.get('meta', {}).get('seed_ledger') if 'meta' in j else j.get('seed_ledger')
            for e in led or []:
                ledger[e['seed_id']] = dict(e, run=os.path.basename(d), checked=run_date)
            for c in j.get('candidates', []):
                key = c.get('slug') or c.get('name')
                cands[key] = dict(c, run=os.path.basename(d), checked=run_date)
    return seeds, ledger, cands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--next-check', default=(dt.date.today() + dt.timedelta(days=91)).isoformat())
    o = ap.parse_args()
    seeds, ledger, cands = load()
    rows = []
    for sid, e in ledger.items():
        if e.get('disposition') != 'monitor':
            continue
        s = seeds.get(sid, {})
        hint = s.get('name_hint', '')
        src = sid.split(':')[0]
        st = STATE.get(s.get('state', ''), '') or hint_field(hint, r'location ([A-Z][a-z]+(?: [A-Z][a-z]+)?) \(-?\d')
        if not st:
            st = hint_field(hint, r'states? ([A-Z]{2})')
            st = STATE.get(st, st)
        rows.append({'lead_id': sid, 'name': e.get('name') or s.get('name', ''),
                     'kind': {'plant': 'Data center gas plant: how does the gas arrive?', 'eia': 'EIA pipeline project',
                              'lead': 'Named lead', 'monitor': 'Earlier monitor item', 'survey': 'Named lead',
                              'recheck': 'Earlier monitor item', 'utility': 'Utility gas plants by owner'}.get(src, src),
                     'state': st, 'developer': s.get('operator', ''),
                     'plant_mw': hint_field(hint, r'(\d[\d,]*) MW'), 'plant_status': hint_field(hint, r'status ([a-z/ -]+?)(?: \||$)'),
                     'plant_start': hint_field(hint, r'start ([\d/?]+)'), 'gem_plant_id': hint_field(hint, r'GEM location (\S+)'),
                     'nearest_ggit': hint_field(hint, r'nearest GGIT routes: ([^|]+)'),
                     'reason': (e.get('reason') or '').strip(), 'evidence': [x.get('url') for x in e.get('evidence', []) if x.get('url')],
                     'checked': e['checked'], 'run': e['run']})
    seen = {r['name'].lower() for r in rows}
    for k, c in cands.items():
        if c.get('class') != 'monitor' or (c.get('name') or '').lower() in seen:
            continue
        v = c.get('values', {})
        ln = f"{v.get('LengthKnown')} {v.get('LengthKnownUnits', '')}".strip() if v.get('LengthKnown') else ''
        rows.append({'lead_id': 'candidate:' + str(k), 'name': c.get('name', ''), 'kind': 'Pipeline found by search',
                     'state': v.get('StartState/Province', ''), 'developer': v.get('Owner', ''), 'length': ln,
                     'reason': (c.get('monitor_reason') or '').strip() + ('. ' + c['researcher_notes'] if c.get('researcher_notes') else ''),
                     'evidence': sum(c.get('refs', {}).values(), []) if isinstance(c.get('refs'), dict) else [],
                     'checked': c['checked'], 'run': c['run']})
    # A lead a later run queued, matched or dropped (a re-check seed, or a search candidate that became a row) leaves the list.
    mt = lambda r: os.path.getmtime(f'{ST}/{r}')
    resolved = {}
    for e in ledger.values():
        if e.get('disposition') in ('queued', 'matched', 'dropped'):
            # A re-check seed names the lead it re-checks in its hint ("seed eia:..."), so match on that ID as well.
            hint = seeds.get(e['seed_id'], {}).get('name_hint', '')
            for k in [norm(e.get('name') or seeds.get(e['seed_id'], {}).get('name'))] + re.findall(r'seed ([a-z]+:[\w-]+)', hint):
                resolved[k] = max(resolved.get(k, 0), mt(e['run']))
    for c in cands.values():
        if c.get('class') in ('new_row', 'matched_existing'):
            resolved[norm(c.get('name'))] = max(resolved.get(norm(c.get('name')), 0), mt(c['run']))
    n0 = len(rows)
    rows = [r for r in rows if max(resolved.get(norm(r['name']), 0), resolved.get(r['lead_id'], 0)) <= mt(r['run'])]
    print(n0 - len(rows), 'leads resolved by a later run')
    for r in rows:
        if 'utility' in r['run'] and r['kind'] == 'Pipeline found by search':
            r['kind'] = 'Utility gas plants by owner'
    df = pd.DataFrame(rows)
    # One row per lead: the same plant or pipeline can come back as a plant seed and as a search candidate, or under
    # two slugs. Keep the latest check's reason and fill blank fields from the other copies.
    df['key'] = df.name.map(norm)
    df['_m'] = df.run.map(mt)
    df = df.sort_values('_m', ascending=False)
    df = df.groupby('key', sort=False).agg(lambda s: next((x for x in s if isinstance(x, list) and x or
                                                            not isinstance(x, list) and pd.notna(x) and x != ''), s.iloc[0]))
    df = df.reset_index(drop=True).drop(columns=['_m'])
    df['name'] = df.name.str.replace(r'\s*\(gas supply\)', '', regex=True)
    # Fill blank states from GOGPT (by location ID, then plant name), then the first state the name or reason mentions.
    if os.path.exists(GOGPT):
        g = pd.read_csv(GOGPT, dtype=str, usecols=['GEM location ID', 'Plant name', 'State/Province', 'Country/Area'])
        g = g[g['Country/Area'] == 'United States']
        by_id = dict(zip(g['GEM location ID'].str.upper(), g['State/Province']))
        by_nm = dict(zip(g['Plant name'].str.lower(), g['State/Province']))
        df['state'] = [s if s else by_id.get(str(i).upper()) or by_nm.get(re.sub(r' power (station|plant)$', '', nm.lower()))
                       or by_nm.get(nm.lower()) or '' for s, i, nm in
                       zip(df.state.fillna(''), df.gem_plant_id.fillna(''), df.name)]
    pat = re.compile(r'\b(' + '|'.join(sorted(STATE.values(), key=len, reverse=True)) + r')\b')

    def first_state(txt):
        m = pat.search(PIPE_CO.sub('', txt))
        return m.group(1) if m else ''
    df['state'] = [s or (first_state(f'{nm}. {r}') + ' (read from notes, check)').lstrip(' ')
                   if not s and first_state(f'{nm}. {r}') else s for s, nm, r in zip(df.state.fillna(''), df.name, df.reason)]

    def cat(r):
        t = r['reason']
        # The vetting agent's own labels come first: ONSITE_NO_PIPE (unless unconfirmed) and NOT_FOUND.
        if 'ONSITE_NO_PIPE' in t[:40] and 'not confirmed' not in t[:80] or NO_PIPE.search(t) and 'NOT_FOUND' not in t[:12]:
            return 'no_pipe'
        if 'NOT_FOUND' in t[:12]:
            return 'not_found'
        if NO_TIE.search(t):
            return 'no_tie'
        if NO_STEP.search(t):
            return 'no_step'
        return 'not_found'
    df['cat'] = df.apply(cat, axis=1)
    df['Why it is on the list'] = df.cat.map(lambda c: CATS[c][0])
    df['What would make it a GGIT row'] = df.cat.map(lambda c: CATS[c][1])
    df['Where to watch'] = [where_to_watch(s, c) for s, c in zip(df.state, df.cat)]
    df['Re-check under new rulings'] = df.apply(
        lambda r: RECHECKED.format(r['checked']) if r['checked'] >= '2026-10-19' else
        RECHECK if r['cat'] in ('no_tie', 'no_step') or re.search(r'Apollo North|Aristotle North|Clarington|Polaris',
                                                                  r['name'], re.I) else '', axis=1)
    df['Researcher reason (last check)'] = df.reason.str.replace(r'\s+', ' ', regex=True)
    df['Links the researcher cited (not re-checked)'] = df.evidence.map(lambda u: ' ; '.join(dict.fromkeys(u))[:1500])
    df['Next check'] = o.next_check
    df['Outcome'] = ''
    cols = {'lead_id': 'Lead ID', 'name': 'Lead', 'kind': 'Kind', 'state': 'State', 'developer': 'Developer or owner',
            'plant_mw': 'Plant MW', 'plant_status': 'Plant status (GOGPT)', 'plant_start': 'Plant start year',
            'gem_plant_id': 'GOGPT location ID', 'length': 'Length (if known)', 'nearest_ggit': 'Nearest GGIT pipelines',
            'checked': 'Last checked', 'run': 'Staging run'}
    df = df.rename(columns=cols)
    order = ['Lead', 'Kind', 'State', 'Developer or owner', 'Why it is on the list', 'What would make it a GGIT row',
             'Where to watch', 'Re-check under new rulings', 'Plant MW', 'Plant status (GOGPT)', 'Plant start year',
             'Length (if known)', 'Nearest GGIT pipelines', 'Researcher reason (last check)',
             'Links the researcher cited (not re-checked)', 'Last checked', 'Next check', 'Outcome', 'GOGPT location ID',
             'Lead ID', 'Staging run']
    for c in order:
        if c not in df:
            df[c] = ''
    df = df[order + ['cat']].fillna('')
    rank = {'no_tie': 0, 'no_step': 1, 'not_found': 2, 'no_pipe': 3}
    df = df.sort_values(['cat', 'State', 'Lead'], key=lambda s: s.map(rank) if s.name == 'cat' else s.str.lower())
    watch, nopipe = df[df.cat != 'no_pipe'].drop(columns='cat'), df[df.cat == 'no_pipe'].drop(columns='cat')
    stamp = dt.date.today().isoformat()
    os.makedirs(OUT, exist_ok=True)
    xl = f'{OUT}/US_gas_datacenter_monitor_{stamp}.xlsx'
    about = pd.DataFrame({'About this list': [
        'Leads from the US gas data center discovery that are not GGIT rows yet. One row per lead, latest check only.',
        'Watch list: leads that could become a GGIT row. Gas arrives without new pipe: plants that so far get gas on site '
        'or through a tap on an existing line; they move to the watch list if a new supply line is announced.',
        'Fill Outcome when you check a lead (still waiting, became a row with its P-ID, dropped and why).',
        'Rebuilt from the staging runs by batches/united-states-gas/staging/discovery-datacenter-seeds-20261016/'
        'build_monitor_list.py. Plan: docs/plans/2026-10-16_us-gas-datacenter-subfloor.md.',
        f'Built {stamp}. {len(watch)} watch list leads, {len(nopipe)} plants with no new pipe so far.']})
    with pd.ExcelWriter(xl, engine='openpyxl') as w:
        watch.to_excel(w, sheet_name='Watch list', index=False)
        nopipe.to_excel(w, sheet_name='Gas arrives without new pipe', index=False)
        about.to_excel(w, sheet_name='About', index=False)
    from openpyxl import load_workbook
    from openpyxl.styles import Font
    wb = load_workbook(xl)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                c.font = Font(name='Calibri', size=10, bold=c.row == 1)
        ws.freeze_panes = 'B2'
    wb.save(xl)
    watch.to_csv(xl.replace('.xlsx', '_watch.csv'), index=False)
    print(xl, '|', len(watch), 'watch,', len(nopipe), 'no new pipe')
    print(df.groupby('cat').size())


if __name__ == '__main__':
    main()
