#!/usr/bin/env python3
"""Draft gem.wiki pages for newly added US gas pipelines (read-only: writes local .wiki drafts).

Groups the new rows by PipelineName. A name with no wiki page gets a new page; a name whose page
already exists gets its new segments as subsections under Project Details. Nothing is sent to
gem.wiki here; see publish_wiki_pages.py for that step.
"""
import argparse, json, os, re, sys, time
from urllib.parse import urlparse
import pandas as pd

import glob
SNAP = sorted(glob.glob('data/GGIT_gas_snapshot_2*.csv'))[-1]            # newest pull; --snap overrides
OWN = sorted(glob.glob('data/GEM_operators_owners_snapshot_2*.csv'))[-1]
ROUTES = '../goit-ggit-pipeline-routes/data/individual-routes/gas-pipelines/'
BANNED = ('abarrelfull', 'theodora.com', 'yingdodo', 'gem.wiki', 'globalenergymonitor')
ACCESS = time.strftime('%Y-%m-%d')                                         # --access overrides

def urls(cell):
    return [u for u in (x.strip().rstrip(',;') for x in re.findall(r'https?://[^\s,;]+', cell or ''))
            if not any(b in u for b in BANNED) and u not in _unreadable()]

def _unreadable():
    # refs that do not load and have no archived copy are left off wiki pages (data/wiki_unreadable_refs.json); the sheet keeps them
    try: return json.load(open('data/wiki_unreadable_refs.json'))
    except Exception: return {}

def pdf_title(u):
    # titles of PDF refs come from data/wiki_pdf_titles.json (url -> title), filled by scripts/wiki_pdf_titles.py
    try: return json.load(open('data/wiki_pdf_titles.json')).get(u)
    except Exception: return None

def _known_titles():
    try: return {v['url']: v['title'] for v in json.load(open('data/wiki_backgrounds.json')).get('_refs', {}).values()}
    except Exception: return {}

def ref_title(u):
    # a real document title when one is known (PDF first page, hand-written _refs); otherwise the full URL,
    # never the bare hostname, so the reference list shows which page it is (Baird 2026-11-05)
    t = (pdf_title(u) if u.lower().split('?')[0].endswith('.pdf') else None) or _known_titles().get(u)
    return t or u.replace('|', '%7C')

def ref(u):
    host = urlparse(u).netloc.replace('www.', '')
    title = ref_title(u)
    return f'<ref>{{{{Cite web|url={u}|title={title}|website={host}|access-date={ACCESS}}}}}</ref>'

WAYBACK_FOR = {
    'https://www.pipelinesafetyinfo.com/user/file/Nevada/Great%20Basin%20Gas%20Transmission%20Company.pdf':
    'http://web.archive.org/web/20250927030050/https://www.pipelinesafetyinfo.com/user/file/Nevada/Great%20Basin%20Gas%20Transmission%20Company.pdf',
}  # origin now redirects to a dead host; cite the copy that was read

def refs(cell):
    return ''.join(ref(WAYBACK_FOR.get(u, u)) for u in urls(cell))

def num(x):
    try:
        f = float(str(x).replace(',', ''))
    except ValueError:
        return None
    return f

def fmt(f):
    return f'{f:,.0f}' if abs(f - round(f)) < 0.005 else f'{f:,.2f}'.rstrip('0').rstrip('.')

def place(loc, st):
    return ', '.join(p for p in (loc, st) if p)

def coords_of(pid):
    f = ROUTES + pid + '.geojson'
    if not os.path.exists(f):
        return []
    lines = []
    def walk(g):
        if not g: return
        t, c = g['type'], g['coordinates']
        if t == 'LineString': lines.append(c)
        elif t == 'MultiLineString': lines.extend(c)
    gj = json.load(open(f))
    # the routes repo holds FeatureCollections, bare Features (P7715) and null stubs; a Feature read through
    # .get('features') silently gave no map, so Shedgum-Riyadh 2 was posted without one (2026-11-06)
    if gj.get('type') == 'FeatureCollection':
        for ft in gj.get('features', []): walk(ft.get('geometry'))
    elif gj.get('type') == 'Feature':
        walk(gj.get('geometry'))
    elif 'coordinates' in gj:
        walk(gj)
    geoms = [ft.get('geometry') for ft in gj.get('features', [])] if gj.get('type') == 'FeatureCollection' else [gj.get('geometry', gj if 'coordinates' in gj else None)]
    if not lines and any(g for g in geoms):  # a stub whose features all carry null geometry is just "no route"
        raise ValueError(f'{pid}: route file has geometry the reader did not parse: {f}')
    return lines

def thin(line, maxpts=60):
    if len(line) <= maxpts: return line
    step = (len(line) - 1) / (maxpts - 1)
    return [line[round(i * step)] for i in range(maxpts)]

# Status colors of GEM's tracker maps on the website (GlobalEnergyMonitor/maps, gitpages-production:
# trackers/ggit/config.js and trackers/GOIT/config.js `color`, hex from site-config.js `colors`), Baird 2026-11-06
MAP_RED, MAP_BLUE, MAP_GREEN, MAP_GREY = "#c74a48", "#5c62cf", "#4c9d4f", "#8f8f8e"
STATUS_COLORS = {
    "gas": {"operating": MAP_RED, "construction": MAP_BLUE, "proposed": MAP_GREEN, "shelved": MAP_GREY,
            "cancelled": MAP_GREY, "retired": MAP_GREY, "idled": MAP_GREY, "mothballed": MAP_GREY,
            "mixed status": MAP_GREY},
    "oil": {"operating": MAP_RED, "construction": MAP_BLUE, "proposed": MAP_BLUE, "mothballed": MAP_GREEN,
            "cancelled": MAP_GREEN, "shelved": MAP_GREY, "retired": MAP_GREY, "idled": MAP_GREY,
            "mixed status": MAP_GREY},
}
STATUS_ORDER = ["operating", "construction", "proposed", "shelved", "mothballed", "idled", "cancelled",
                "retired", "mixed status"]


def map_block(pids, maxpts=60, status=None, label=' '):
    """The page map. With status (ProjectID -> Status), each line takes its status color from GEM's website
    tracker map and a row of colored squares under the map names the statuses shown."""
    status = status or {}
    segs = [(p, thin(l, maxpts)) for p in pids for l in coords_of(p)]
    lines = [l for _, l in segs]
    if not lines: return ''
    allp = [pt for l in lines for pt in l]
    clat = sum(p[1] for p in allp) / len(allp); clon = sum(p[0] for p in allp) / len(allp)
    span = max(max(p[1] for p in allp) - min(p[1] for p in allp), max(p[0] for p in allp) - min(p[0] for p in allp))
    zoom = 4 if span > 12 else 5 if span > 6 else 6 if span > 3 else 7 if span > 1.5 else 8 if span > .7 else 9 if span > .3 else 10
    lab = (label or ' ').replace('~', '-').replace(';', ',').replace('|', '/')  # a blank label tripped the site firewall once (2026-11-07)
    col = lambda p: STATUS_COLORS['gas'].get(status.get(p, ''), MAP_GREY)
    # never write ~~~ in a line's style: on save it becomes the editor's signature
    body = ';'.join(':'.join(f'{q[1]:.5f}, {q[0]:.5f}' for q in l) + (f'~{lab}~ ~{col(p)}~1~3' if status else '') for p, l in segs)
    out = f'{{{{#display_map:\n|lines={body}|center={clat:.5f}, {clon:.5f}|width=100%|height=400|type=normal|zoom={zoom}}}}}\n'
    shown = sorted({status[p] for p, _ in segs if p in status}, key=lambda x: STATUS_ORDER.index(x) if x in STATUS_ORDER else 99)
    if len(set(pids)) > 1 and shown:
        out += '\n' + legend_html(shown) + '\n'
    return out

def legend_html(statuses, tracker='gas'):
    phrase = {'construction': 'under construction'}
    return ' &nbsp; '.join(f'<span style="color:{STATUS_COLORS[tracker].get(s, MAP_GREY)}">■</span> {phrase.get(s, s).capitalize()}' for s in statuses)

def details(r, own):
    st = r['Status']
    b = []
    o = own.get(r['ProjectID'], {})
    if o.get('Operator'):
        b.append(f"*'''Operator: '''{o['Operator']}{refs(o.get('Operator [ref]'))}")
    if o.get('Owner1'):
        owners = '; '.join(x for x in (o.get(f'Owner{i}') for i in range(1, 12)) if x)
        b.append(f"*'''Owner: '''{owners}{refs(o.get('Owner [ref]'))}")
    par = parent_text(r.get('Parent'))
    if par:
        b.append(f"*'''Parent: '''{par}")
    cap = num(r['Capacity'])
    if cap is not None:
        b.append(f"*'''Capacity: '''{fmt(cap)} {r['CapacityUnits']}{refs(r['Capacity [ref]'])}")
    ln = num(r['LengthKnown'])
    if ln is not None and ln > 0:
        b.append(f"*'''Length: '''{fmt(ln)} {r['LengthKnownUnits']}{refs(r['Length [ref]'])}")
    if r['Diameter']:
        b.append(f"*'''Diameter: '''{r['Diameter'].replace(',', ', ').replace(',  ', ', ')} {r['DiameterUnits']}{refs(r['Diameter [ref]'])}")
    b.append(f"*'''Status: '''{st.capitalize()}{refs(r['Status [ref]'])}")
    if r['StartYear1']: b.append(f"*'''Start year: '''{r['StartYear1']}{refs(r['Start [ref]'])}")
    cost = num(r['ProjectLevelCost']) or num(r['SegmentCost'])
    if cost:
        cu = r['ProjectLevelCostUnits'] or r['SegmentCostUnits']
        cr = r['ProjectLevelCost [ref]'] or r['SegmentCost [ref]']
        b.append(f"*'''Cost: '''{'US$' if cu == 'USD' else cu + ' '}{fmt(cost)}{refs(cr)}")
    return '\n'.join(b)

def parent_text(cell):
    # the gas tab's Parent cell as the backend has it, shares kept where known (Baird 2026-11-06): parents are the
    # ownership team's research, the page only shows them. 'Williams Companies Inc [unknown %]; X [59.10%]' gives
    # 'Williams Companies Inc; X (59.1%)'.
    out = []
    for part in (cell or '').split(';'):
        m = re.match(r'\s*(.*?)\s*(?:\[([^\]]*)\])?\s*$', part)
        n, p = m.group(1), num((m.group(2) or '').replace('unknown', '').replace('%', '').strip())
        if n and n.lower() != 'unknown':
            out.append(f"{n} ({fmt(p)}%)" if p is not None else n)
    return '; '.join(out)

def fill_unknown_parents(df):
    # a Parent the ownership team has not linked yet reads 'unknown [unknown %]'; take the parent the backend gives
    # for the identical Owner cell on other rows, when there is exactly one
    # a blank or placeholder Owner ('--', 'unknown') is no company: never fill from it (Baird 2026-11-08: 541
    # '--' rows took P3959's Samruk-Kazyna parent)
    unk = df['Parent'].str.strip().str.match(r'^(unknown\b|$)')
    real = ~df['Owner'].str.strip().str.lower().isin(['', '--', '-', 'unknown', 'n/a'])
    known = df[~unk & real].groupby('Owner')['Parent'].agg(lambda x: x.iloc[0] if x.nunique() == 1 else '')
    df.loc[unk, 'Parent'] = df.loc[unk & real, 'Owner'].map(known).reindex(df.index).fillna('')
    return df

def verb(st):
    if st == 'construction': return 'is being built'
    if st == 'proposed': return 'is proposed to run'
    if st in ('cancelled', 'shelved'): return 'was proposed to run'
    return 'runs'

def route_sentence(r, what='pipeline'):
    a = place(r['StartLocation'], r['StartState/Province']); z = place(r['EndLocation'], r['EndState/Province'])
    if a and z and a != z: return f"The {what} {verb(r['Status'])} from {a} to {z}.{refs(r['Location [ref]'])}"
    if a or z: return f"The {what} is located in {a or z}.{refs(r['Location [ref]'])}"
    return ''

def seg_title(r, single=False):
    # a row with no SegmentName on a page with several segments is the system's main line
    return 'Main Line' if single else (r['SegmentName'] or 'Main Line')

def cite(url, title, site, date=None):
    if title == site or not title: title = _known_titles().get(url) or url.replace('|', '%7C')
    return '<ref>{{Cite web|url=%s|title=%s|website=%s|access-date=%s}}</ref>' % (url, title, site, ACCESS)

BG_OVERRIDE = {}   # ProjectID -> live Background text kept when a page is rebuilt

def background_text(r):
    # hand-written prose lives in data/wiki_backgrounds.json, keyed by ProjectID
    if r['ProjectID'] in BG_OVERRIDE: return BG_OVERRIDE[r['ProjectID']]
    try: bg = json.load(open('data/wiki_backgrounds.json'))
    except Exception: bg = {}
    txt = bg.get(r['ProjectID'])
    if txt:
        for k, v in bg.get('_refs', {}).items(): txt = txt.replace('{' + k + '}', cite(v['url'], pdf_title(v['url']) or v['title'], v['site']))
        d = dormancy(r)
        return txt + ('\n\n' + d if d and 'no development on' not in txt else '')
    return dormancy(r)

def dormancy(r):
    t = r['SegmentName'] or r['PipelineName']
    if r['ShelvedCancelledType'] == 'inferred':
        if r['Status'] == 'cancelled' and r['CancelledYear']:
            return f"As of {r['CancelledYear']}, no development on the {t} has been reported for over 4 years, and it is considered cancelled.{refs(r['Cancelled [ref]'] or r['Status [ref]'])}"
        if r['Status'] == 'shelved' and r['ShelvedYear']:
            return f"As of {r['ShelvedYear']}, no development on the {t} has been reported for over 2 years, and it is considered shelved.{refs(r['Shelved [ref]'] or r['Status [ref]'])}"
    return ''

TAIL = ['==Articles and resources==', '', '===References===', '<references />', '', '===Additional data===',
        'To access additional data, including an interactive map of gas pipelines, a downloadable dataset, and summary data, please visit the [https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/ Global Gas Infrastructure Tracker] on the Global Energy Monitor website.']   # no categories on a page (Baird 2026-11-08)

import hashlib
_REF = re.compile(r'<ref>(\{\{Cite web\|url=([^|]+)\|.*?\}\})</ref>')

def dedupe_refs(text, seen):
    # first use of a URL defines a named ref; later uses point at it
    def sub(m):
        name = 'r' + hashlib.md5(m.group(2).encode()).hexdigest()[:6]
        if name in seen: return f'<ref name="{name}" />'
        seen.add(name); return f'<ref name="{name}">{m.group(1)}</ref>'
    return _REF.sub(sub, text)

_NAMED = re.compile(r'<ref name="([^"]+)">(.*?)</ref>', re.S)

def merge_named_defs(text):
    # a name defined twice (kept Background text plus regenerated details) keeps one definition, the one with
    # a real title over a URL-only one; the others become reuses
    defs = {}
    for m in _NAMED.finditer(text):
        body = m.group(2); tm = re.search(r'\|title=([^|}]*)', body)
        score = 0 if (not tm or tm.group(1).startswith('http')) else 1
        if m.group(1) not in defs or score > defs[m.group(1)][0]: defs[m.group(1)] = (score, body)
    done = set()
    def sub(m):
        n = m.group(1)
        if n in done: return f'<ref name="{n}" />'
        done.add(n); return f'<ref name="{n}">{defs[n][1]}</ref>'
    return _NAMED.sub(sub, text)

def live_background(text):
    m = re.search(r'\n==\s*Background\s*==[^\n]*\n', text, re.I)
    if not m: return ''
    nxt = re.search(r'\n==[^=\n]', text[m.end():])
    return text[m.end(): m.end() + nxt.start() if nxt else len(text)].strip('\n')

def country_phrase(rows):
    # the page's country (or countries) from the rows; the US pilot's wording was hardcoded until 2026-11-06
    cs = []
    for r in rows:
        for c in re.split(r'\s*,\s*', r.get('CountriesOrAreas', '') or ''):
            if c and c not in cs: cs.append(c)
    if not cs: return 'the United States'
    if cs == ['United States']: return 'the United States'
    return cs[0] if len(cs) == 1 else ', '.join(cs[:-1]) + ' and ' + cs[-1]

def new_page(name, rows, own):
    first = rows[0]; single = len(rows) == 1; ctry = country_phrase(rows)
    sts = {r['Status'] for r in rows}
    if len(sts) == 1:
        st = next(iter(sts)); art = 'an' if st[0] in 'aeiou' else 'a'
        if st == 'construction':
            lead = f"'''{name}''' is a natural gas pipeline under construction in {ctry}.{refs(first['Status [ref]'])}"
        else:
            lead = f"'''{name}''' is {art} {st} natural gas pipeline in {ctry}.{refs(first['Status [ref]'])}"
    else:
        lead = f"'''{name}''' is a natural gas pipeline in {ctry}, with {len(rows)} segments."
    out = ['{{Navbar-Global Gas Infrastructure Tracker}}', lead, '', '==Location==']
    for r in rows:
        s = route_sentence(r)
        if s: out.append((f"{seg_title(r)}: " if not single and r['SegmentName'] else '') + s)
    mb = map_block([r['ProjectID'] for r in rows], status={r['ProjectID']: r['Status'] for r in rows})
    if mb: out += ['', mb.rstrip()]
    out += ['', '==Project details==']
    for r in rows:
        out += ([] if single else [f"==={seg_title(r)}==="]) + [details(r, own), '']
    bgs = [(r, background_text(r)) for r in rows]
    bgs = [(r, b) for r, b in bgs if b.strip()]   # a row with no prose gets no empty heading
    if bgs: out += ['==Background==']
    for r, b in bgs:
        out += ([] if single else [f"==={seg_title(r)}==="]) + [b, '']
    return merge_named_defs(dedupe_refs('\n'.join(out + TAIL) + '\n', set()))

def segments_block(rows, own):
    out = []
    for r in rows:
        out += [f"\n==={seg_title(r)}===", details(r, own)]
    return '\n'.join(out) + '\n'

def background_block(rows):
    out = []
    for r in rows:
        b = background_text(r)
        if b.strip(): out += [f"\n==={seg_title(r)}===", b]
    return '\n'.join(out) + '\n' if out else ''

# section headings are sentence case, "Project details", "Articles and resources" (Baird 2026-11-06). A heading
# changes only when every word, the first included, is a generic one, so a project's name ("Heartland Project",
# "Sunrise Pipeline Project") and a name inside a heading a person wrote keep their capitals. Only the case changes.
HEADING_WORDS = set("""details data resources articles sources projects project history background information references
ownership cost costs timeline expansion expansions related external other and of the further reading news status
opposition financing finance notes links see also map maps location overview additional pipeline pipelines route routes
segment segments proposed existing research reports report documents media coverage controversy controversies impact
impacts environmental regulatory approval approvals construction capacity contractors technical specifications
description summary in on for to""".split())

def sentence_case_headings(text):
    def fix(m):
        h = m.group(2)
        w = h.split(' ')
        if len(w) < 2 or not all(x.lower() in HEADING_WORDS for x in w):
            return m.group(0)
        return m.group(0).replace(h, ' '.join([w[0]] + [x.lower() for x in w[1:]]), 1)
    return re.sub(r'(?m)^(={2,3})(?!=)[ \t]*([^=\n]*?[^=\s])[ \t]*\1[ \t]*$', fix, text)

def _insert(text, head, block, before):
    m = re.search(r'\n==\s*' + head + r'\s*==[^\n]*\n', text, re.I)
    if m:
        nxt = re.search(r'\n==[^=\n]', text[m.end():])
        pos = m.end() + nxt.start() + 1 if nxt else len(text)
        return text[:pos].rstrip('\n') + '\n' + block + '\n' + text[pos:]
    nxt = re.search(r'\n==\s*(' + before + r')\s*==', text, re.I)
    if not nxt: raise ValueError('no place to insert ' + head)
    pos = nxt.start() + 1
    return text[:pos] + f'=={head}==\n' + block + '\n' + text[pos:]

def wiki_key(u):
    from urllib.parse import unquote
    return unquote(str(u)).split('gem.wiki/')[-1].replace('_', ' ').strip().lower()

LEGEND_RE = r'(?:\n*<span style="color:#[0-9a-f]{6}">■</span>[^\n]*\n?)?'

def update_map(text, pids, status=None, label=None):
    # an existing page's main map (the first display_map) is redrawn from the routes repo for every pipeline on the page,
    # with the status legend that follows it; sub-project maps under their own headings stay. No map yet: add one after
    # the Location text. No routes: leave alone.
    if label is None:
        m = re.search(r"'''(.+?)'''", text); label = m.group(1) if m else ' '
    blk = map_block(pids, 100, status, label)
    if not blk: return text
    m = re.search(r'\{\{#display_map:.*?\}\}\n?' + LEGEND_RE, text, re.S)
    if m: return sentence_case_headings(text[:m.start()] + blk + text[m.end():])
    loc = re.search(r'\n==\s*Location\s*==[^\n]*\n', text, re.I)
    if not loc: return text
    nxt = re.search(r'\n==[^=\n]', text[loc.end():])
    pos = loc.end() + nxt.start() + 1 if nxt else len(text)
    return sentence_case_headings(text[:pos].rstrip('\n') + '\n\n' + blk + '\n' + text[pos:])

def pull_expansion(text):
    # an 'Expansion projects' section is folded into Project Details: its subsections move, the heading goes
    m = re.search(r'\n==\s*Expansion projects?\s*==[ \t]*\n', text, re.I)
    if not m: return text, ''
    nxt = re.search(r'\n==[^=\n]', text[m.end():])
    end = m.end() + nxt.start() if nxt else len(text)
    return text[:m.start()] + '\n' + text[end:].lstrip('\n'), text[m.end():end].strip('\n')

def merge_details_headings(text):
    # wiki pages carry one 'Project Details' section, never 'Pipeline details' (Baird 2026-11-06): a page with only
    # Pipeline details gets it renamed; a page with both keeps the first heading and loses the second
    pat = re.compile(r'^==\s*(Pipeline|Project) details\s*==[ \t]*$', re.I | re.M)
    ms = list(pat.finditer(text))
    if not ms: return text
    out, last = [], 0
    for i, m in enumerate(ms):
        out.append(text[last:m.start()])
        if i == 0: out.append('==Project details==')
        else: out.append('')
        last = m.end()
    out.append(text[last:])
    return re.sub(r'\n{3,}', '\n\n', ''.join(out))

def insert_segments(text, rows, own, map_pids=None):
    text = merge_details_headings(text)
    seen = set()
    if map_pids: text = update_map(text, map_pids, {r['ProjectID']: r['Status'] for r in rows})
    # idempotent: a segment whose heading is already on the page was inserted by an earlier run (Oasis got it twice, 2026-11-04)
    rows = [r for r in rows if f"==={seg_title(r)}===" not in text.replace('=== ', '===').replace(' ===', '===')]
    if not rows: return text
    text, exp = pull_expansion(text)
    block = segments_block(rows, own) + (('\n' + exp + '\n') if exp else '')
    text = _insert(text, 'Project details', dedupe_refs(block, seen), 'Background|Articles and resources')
    bb = background_block(rows)
    if bb: text = _insert(text, 'Background', dedupe_refs(bb, seen), 'Articles and resources')
    if '{{reflist' not in text.lower() and '<references' not in text.lower():
        text = text.rstrip('\n') + '\n\n==References==\n<references />\n'
    text = re.sub(r"\n*\[\[\s*Category\s*:[^\]]+\]\]", "", text).rstrip('\n') + '\n'   # existing category lines dropped too (Baird 2026-11-08)
    return sentence_case_headings(text)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--scope', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--snap', default=SNAP); ap.add_argument('--own', default=OWN); ap.add_argument('--access', default=ACCESS)
    a = ap.parse_args(); SNAP, OWN, ACCESS = a.snap, a.own, a.access
    sys.path.insert(0, '../goit-ggit-data-ops/gem-wiki'); import gemwiki
    d = fill_unknown_parents(pd.read_csv(SNAP, header=2, low_memory=False, keep_default_na=False))
    o = pd.read_csv(OWN, header=1, low_memory=False, keep_default_na=False)
    own = {r['ProjectID']: r.to_dict() for _, r in o.iterrows()}
    scope = json.load(open(a.scope)); s = gemwiki.session()
    os.makedirs(a.out + '/new', exist_ok=True); os.makedirs(a.out + '/edit', exist_ok=True)
    man = []
    for name, v in scope.items():
        rows = [r.to_dict() for _, r in d[d.ProjectID.isin(v['pids'])].iterrows()]
        rows.sort(key=lambda r: r['ProjectID'])
        w = v['wiki']
        if v.get('rebuild'):
            # a single-segment page this workflow made, edited by no one else, gains segments: regenerate it whole from
            # every row on the page, keeping each existing segment's live Background text
            title = v['rebuild']; cur = gemwiki.page_text(s, title)
            path = f"{a.out}/edit/{title.replace('/', '_')}.wiki"; open(path + '.orig', 'w').write(cur)
            for p in v.get('keep_background', []): BG_OVERRIDE[p] = live_background(cur)
            allp = sorted(set(v['pids']) | set(v.get('keep_background', [])))
            rows = [r.to_dict() for _, r in d[d.ProjectID.isin(allp)].iterrows()]; rows.sort(key=lambda r: r['ProjectID'])
            open(path, 'w').write(new_page(title, rows, own)); kind = 'rebuild'
            man.append(dict(name=name, title=title, kind=kind, pids=v['pids'], path=path, url='https://www.gem.wiki/' + title.replace(' ', '_')))
            continue
        if w == 'MISSING':
            title = name; path = f"{a.out}/new/{title.replace('/', '_')}.wiki"
            open(path, 'w').write(new_page(name, rows, own)); kind = 'new'
        else:
            title = w[7:] if w.startswith('EXISTS:') else __import__('urllib.parse', fromlist=['x']).unquote(w.split('gem.wiki/')[1]).replace('_', ' ')
            for att in range(6):
                try: cur = gemwiki.page_text(s, title); break
                except Exception as e: print('retry', title, e); time.sleep(20)
            path = f"{a.out}/edit/{title.replace('/', '_')}.wiki"
            open(path + '.orig', 'w').write(cur)
            mp = sorted(set(v['pids']) | set(d[d.Wiki.map(wiki_key) == title.lower()].ProjectID))
            # link_only rows are already described on the page: they join the map but get no new section
            rows = [r for r in rows if r['ProjectID'] not in v.get('link_only', [])]
            try: open(path, 'w').write(insert_segments(cur, rows, own, None) if rows else update_map(cur, mp, dict(zip(d.ProjectID, d.Status)))); kind = 'edit'
            except ValueError as e: kind = 'EDIT-FAILED:' + str(e)
            time.sleep(0.5)
        man.append(dict(name=name, title=title, kind=kind, pids=v['pids'], path=path, url='https://www.gem.wiki/' + title.replace(' ', '_')))
    json.dump(man, open(a.out + '/manifest.json', 'w'), indent=1)
    print({k: sum(1 for m in man if m['kind'] == k) for k in {m['kind'] for m in man}})
