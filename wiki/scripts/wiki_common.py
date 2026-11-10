#!/usr/bin/env python3
"""Helpers shared by the wiki page scripts (generate_pages, network_pages, china_networks_page, patch_wiki_backgrounds):
reference URLs and titles, route reading, map status colors, the route note under every map, Parent text, segment
titles, ref de-duplication and sentence-case headings.

Moved here from scripts/build_wiki_pages.py on 2026-11-10, when that file's old bullet-list page builder was retired
(every page is now built by generate_pages.py). Paths are relative to the repo root, so callers chdir there first.
"""
import argparse, json, os, re, sys, time
from urllib.parse import urlparse
import pandas as pd

import glob
SNAP = sorted(glob.glob('data/GGIT_gas_snapshot_2*.csv'))[-1]            # newest pull; --snap overrides
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

WAYBACK_FOR = {
    'https://www.pipelinesafetyinfo.com/user/file/Nevada/Great%20Basin%20Gas%20Transmission%20Company.pdf':
    'http://web.archive.org/web/20250927030050/https://www.pipelinesafetyinfo.com/user/file/Nevada/Great%20Basin%20Gas%20Transmission%20Company.pdf',
}  # origin now redirects to a dead host; cite the copy that was read

def num(x):
    try:
        f = float(str(x).replace(',', ''))
    except ValueError:
        return None
    return f

def fmt(f):
    return f'{f:,.0f}' if abs(f - round(f)) < 0.005 else f'{f:,.2f}'.rstrip('0').rstrip('.')

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

# a note under every map's legend, on every page with a map: the drawn routes are simplified, the full ones are in
# the tracker's download (Baird 2026-11-10). Oil pages link GOIT's download, gas pages GGIT's.
DOWNLOAD_URL = {'gas': 'https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/',
                'oil': 'https://globalenergymonitor.org/projects/global-oil-infrastructure-tracker/'}
NOTE_START = "Note: some pipeline routes are simplified"

# styled like the tables' unit captions ("Dth/d = dekatherms per day"): 85%, bold, the skin's caption grey (Baird 2026-11-10)
NOTE_STYLE = "font-size: 85%; font-weight: bold; color: #95a5a6;"

def route_note(tracker='gas'):
    return (f'<div class="gem-routenote" style="{NOTE_STYLE}">{NOTE_START} for easier visualization on wiki pages, '
            f"and route accuracy varies. Full route and accuracy information is available for download "
            f"[{DOWNLOAD_URL[tracker]} here].</div>")

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

def public_segment(s):
    # SYSTEM/NETWORK INFO is an internal backend marker, never shown on a wiki page (Baird 2026-11-09)
    s = (s or '').strip()
    m = re.match(r'SYSTEM/NETWORK INFO\s*\((.*)\)', s, re.I)
    if m: return m.group(1).strip() or 'Main Line'
    return 'Full system/network info' if s.upper().startswith('SYSTEM/NETWORK') else s

def seg_title(r, single=False):
    # a row with no SegmentName on a page with several segments is the system's main line
    return 'Main Line' if single else (public_segment(r['SegmentName']) or 'Main Line')

def cite(url, title, site, date=None):
    if title == site or not title: title = _known_titles().get(url) or url.replace('|', '%7C')
    return '<ref>{{Cite web|url=%s|title=%s|website=%s|access-date=%s}}</ref>' % (url, title, site, ACCESS)

import hashlib
_REF = re.compile(r'<ref>(\{\{Cite web\|url=([^|]+)\|.*?\}\})</ref>')

def dedupe_refs(text, seen):
    # first use of a URL defines a named ref; later uses point at it
    def sub(m):
        name = 'r' + hashlib.md5(m.group(2).encode()).hexdigest()[:6]
        if name in seen: return f'<ref name="{name}" />'
        seen.add(name); return f'<ref name="{name}">{m.group(1)}</ref>'
    return _REF.sub(sub, text)

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
