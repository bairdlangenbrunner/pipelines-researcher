#!/usr/bin/env python3
"""Generate sample pipeline wiki pages from the tracker, following the page template.

The template is `wiki/template/pipeline_page_template.md` (pushed to the Google Doc
"Wiki page template - gas pipelines (draft)"). This is a stand-in for the data team's GEMwiki
generator, so the template can be tried on real pages before it goes to them. It posts nothing
(except `--push-styles`, which saves the two stylesheet pages: the tabbed table's and the map popup's).

A page with SEG_TABLE_MIN (5) or more segments gets ONE segment table under Project details instead
of the five tables (route, details, timeline, cost, ownership): rows are segments, every column is
tagged with its group (`col-route`, `col-details`, ...), and a tab strip shows one group at a time.
The tabs are plain anchor links: the stylesheet `Template:Segment table/styles.css` (TemplateStyles,
text in SEG_CSS below) shows the group whose anchor is the page's URL fragment (`:target`), so no
JavaScript is involved and a reader without the stylesheet sees every column. Baird 2026-11-06.

For each page name it writes, under `wiki/out/samples/<stamp>/`:
  <page>.txt        the generated page (first line is the page name, as GEMwiki writes it)
  <page>.orig.txt   the live page text it was built from
  <page>.html       the page rendered by gem.wiki's parse API (no save)
  report.md         what the generator logged per page (dropped refs, undefined named refs, ...)

  python wiki/scripts/generate_pages.py --tracker gas "Ruby Gas Pipeline" "Transcontinental Gas Pipeline"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "..", "goit-ggit-data-ops", "gem-wiki"))
os.chdir(REPO)  # build_wiki_pages reads data/ paths relative to the repo

import _common as C  # noqa: E402
import build_wiki_pages as B  # noqa: E402  (urls, ref_title, coords_of: shared with the hand-built pages)
import gemwiki as GW  # noqa: E402

from shapely.geometry import LineString, MultiLineString  # noqa: E402
from shapely.ops import linemerge  # noqa: E402

ACCESS = time.strftime("%Y-%m-%d")

# GEMwiki generic/wiki_util.py COMMENT1-3, word for word
COMMENT1 = ("COMMENT 1: THIS PAGE'S SOURCE CODE IS PARTIALLY GENERATED USING SCRIPTING CODE.\n\t\tCHANGES TO THE WIKI PAGE MAY BE OVERWRITTEN UNLESS MADE IN DESIGNATED AREAS.\n\t\tIF CHANGES WITHIN THE SCRIPT-GENERATED SECTIONS NEED TO BE MADE, PLEASE REACH OUT TO THE DATA TEAM.")
COMMENT2 = ("COMMENT 2: CHANGES MADE IN SECTIONS BETWEEN THIS AND \"COMMENT 3\" WILL NOT BE OVERWRITTEN.\n\t\tPLEASE ENSURE NO DUPLICATE SECTION HEADERS.")
COMMENT3 = ("COMMENT 3: CHANGES MADE BELOW THIS COMMENT WILL BE OVERWRITTEN.\n\t\tPLEASE DO NOT MANUALLY EDIT BELOW THIS COMMENT.")

# headings the generator owns; every spelling seen live (template: "Copied as-is")
GENERATED = {"introduction", "location", "project details", "pipeline details", "ownership",
             "articles and resources", "resources and articles"}
# subsections of Articles and Resources the generator rebuilds; any other subsection there is kept
GENERATED_SUBS = {"references", "additional data"}

STATUS_PHRASE = {"construction": "under construction"}
MAP_GREY, STATUS_COLORS, STATUS_ORDER = B.MAP_GREY, B.STATUS_COLORS, B.STATUS_ORDER


def status_color(pg, status):
    return STATUS_COLORS[pg.tracker].get(status, MAP_GREY)


DOT_RE = re.compile(r'<span class="gem-statusdot" style="[^"]*"></span>')


def status_dot(pg, status):
    """A dot in the map's color for the status, set before the status word in the tables (Baird 2026-11-06).
    Inline style, so it shows on every page whatever stylesheets the page loads."""
    return (f'<span class="gem-statusdot" style="display:inline-block;width:8px;height:8px;margin:0 5px 1px 0;'
            f'border-radius:50%;vertical-align:middle;background:{status_color(pg, status)}"></span>')


THE_COUNTRIES = {"United States", "United Kingdom", "Netherlands", "Philippines", "United Arab Emirates",
                 "Czech Republic", "Democratic Republic of the Congo", "Republic of the Congo",
                 "Dominican Republic", "Central African Republic", "Bahamas", "Gambia"}
UNIT_GLOSS = {"MMcf/d": "MMcf/d = million cubic feet per day", "Dth/d": "Dth/d = dekatherms per day",
              "bcm/y": "bcm/y = billion cubic meters per year", "MMSCMD": "MMSCMD = million standard cubic meters per day",
              "mill.Sm3/day": "mill.Sm3/day = million standard cubic meters per day",
              "bcf/d": "bcf/d = billion cubic feet per day", "mi": "mi = miles", "km": "km = kilometers",
              "in": "in = inches", "mm": "mm = millimeters", "bpd": "bpd = barrels per day",
              "mtpa": "mtpa = million tonnes per year"}
NAVBAR = {"gas": "{{Navbar-Global Gas Infrastructure Tracker}}", "oil": "{{Navbar-Global Oil Infrastructure Tracker}}"}
TRACKER_LINK = {
    "gas": ("gas", "[https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/ Global Gas Infrastructure Tracker]"),
    "oil": ("oil and NGL", "[https://globalenergymonitor.org/projects/global-oil-infrastructure-tracker/ Global Oil Infrastructure Tracker]"),
}


CHINA_SEE_ALL = "See all Chinese pipeline network groupings [[Chinese Gas Pipeline Networks|here]]."


class Page:
    """Per-page state: named refs and a log of what the generator had to decide."""

    def __init__(self, name, tracker="gas"):
        self.name = name
        self.tracker = tracker
        self.url_name = {}      # url -> ref name, for URLs already defined on the page
        self.defined = set()
        self.log = []
        self.dorm = []
        self.shapes = {}        # wiki file name -> svg text for the route-shape column
        self.bg = set()         # ProjectIDs with a row in the Background table (linked both ways, link_background)
        self.carried = []       # citations from replaced sections, or an old 'Other sources' section, added to Background (lost_refs)
        self.lost = []          # live citations the generated page no longer carries (audit_refs); blocks --save
        # self.dorm: (row, sentence, ref cell) for a segment's Background entry

    def cite(self, cell):
        out = []
        for u in B.urls(cell):
            u = B.WAYBACK_FOR.get(u, u)
            name = self.url_name.get(u) or "r" + hashlib.md5(u.encode()).hexdigest()[:6]
            if name in self.defined:
                out.append(f'<ref name="{name}" />')
                continue
            self.defined.add(name)
            self.url_name[u] = name
            host = urlparse(u).netloc.replace("www.", "")
            out.append(f'<ref name="{name}">{{{{Cite web|url={u}|title={B.ref_title(u)}|website={host}|access-date={ACCESS}}}}}</ref>')
        return "".join(out)


# ---------- small formatters ----------

def num(x):
    try:
        return float(str(x).replace(",", ""))
    except ValueError:
        return None


def fmt(x):
    f = num(x)
    if f is None:
        return str(x).strip()
    return f"{f:,.0f}" if abs(f - round(f)) < 0.005 else f"{f:,.2f}".rstrip("0").rstrip(".")


EST_NOTE = "* Length is estimated based on route, rather than known from research."


def length_est(r):
    """The route-based estimate (km) as a starred figure, or '' when the row has none."""
    v = (r.get("LengthEstimateKm") or "").strip()
    return f"{fmt(v)} km*" if num(v) else ""


def money(x, cur):
    f = num(x)
    if not f:
        return ""
    for div, word in ((1e9, "billion"), (1e6, "million")):
        if f >= div:
            v = f / div
            s = f"{v:,.2f}".rstrip("0").rstrip(".")
            break
    else:
        s, word = f"{f:,.0f}", ""
    lead = "US$" if cur in ("USD", "") else cur + " "
    return f"{lead}{s} {word}".strip()


def pct(x):
    s = (x or "").strip()
    if not s:
        return ""
    if s.endswith("%"):
        f = num(s[:-1])
    else:
        f = num(s)
        f = f * 100 if f is not None and f <= 1 else f
    return "" if f is None else (f"{f:.2f}".rstrip("0").rstrip(".") + "%")


def a_an(word):
    return "an" if word[:1].lower() in "aeiou" else "a"


def country_name(c):
    return f"the {c}" if c in THE_COUNTRIES else c


def countries(cell):
    return [c.strip() for c in re.split(r"[,;]", cell or "") if c.strip()]


def place(*parts):
    seen, out = set(), []
    for p in parts:
        p = (p or "").strip()
        if p and p.lower() not in seen:
            seen.add(p.lower())
            out.append(p)
    return ", ".join(out)


SYSTEM_LABEL = "Full system/network info"
MAINISH = re.compile(r"main\s*-?\s*line|trunk\s*-?\s*line|\bmain\s+(system|pipeline|segment|trunk)\b|\btrunk\b", re.I)


def is_main_line(r, rows):
    """The "Main Line" rule (Baird 2026-11-09): a blank SegmentName is the pipeline's Main Line when its
    PipelineName has more than one row, this is the only blank one, and no other segment is already named as
    a main line or trunk line ("South Mainline Expansion Project" on El Paso). A one-row pipeline stays blank.
    The gas tab was filled this way the same day (117 rows); the check keeps new and oil rows consistent."""
    if (r["SegmentName"] or "").strip():
        return False
    same = [q for q in rows if q["PipelineName"] == r["PipelineName"]]
    if len(same) < 2 or sum(1 for q in same if not (q["SegmentName"] or "").strip()) != 1:
        return False
    return not any(MAINISH.search(q["SegmentName"] or "") for q in same)


def label(r, rows):
    s = (r["SegmentName"] or "").strip()
    m = re.match(r"SYSTEM/NETWORK INFO\s*\((.*)\)", s, re.I)
    if m:
        s = m.group(1).strip() or "Main Line"
    elif s.upper().startswith("SYSTEM/NETWORK"):
        # SYSTEM/NETWORK INFO is an internal backend marker and never appears on a wiki page (Baird 2026-11-09)
        s = SYSTEM_LABEL
    if not s and is_main_line(r, rows):
        s = "Main Line"
    s = s or r["PipelineName"]
    if sum(1 for q in rows if (q["SegmentName"] or q["PipelineName"]) == (r["SegmentName"] or r["PipelineName"])) > 1:
        s += f" ({r['ProjectID']})"
    return s


def order(rows):
    return sorted(rows, key=lambda r: (num(r["StartYear1"]) or 9999, r["ProjectID"]))


# ---------- sections ----------

def fuel_phrase(rows, tracker):
    vals = sorted({(r["Fuel"] or "").strip().lower() for r in rows if r["Fuel"]})
    if tracker == "gas":
        return "gas and hydrogen" if any("hydrogen" in v for v in vals) else "gas"
    return "crude oil"  # oil mapping not needed for the gas samples


def location_phrase(rows):
    cs = sorted({c for r in rows for c in countries(r["CountriesOrAreas"])})
    if len(cs) == 1:
        provs = {(r["StartState/Province"], r["EndState/Province"]) for r in rows}
        if len(provs) == 1:
            a, z = next(iter(provs))
            if a and a == z:
                return f"in {a}, {country_name(cs[0])}"
        return f"in {country_name(cs[0])}"
    r = rows[0]
    a, z = r["StartCountryOrArea"], r["EndCountryOrArea"]
    mid = [c for c in countries(r["CountriesOrAreas"]) if c not in (a, z)]
    return f"running from {country_name(a)} to {country_name(z)}" + (f" through {', '.join(mid)}" if mid else "")


def intro(pg, rows, tracker):
    names = []
    # on a many-segment page a segment's aliases name that segment, not the pipeline: only the
    # system row (or rows with no segment name) speak for the whole page
    whole = [r for r in rows if not r["SegmentName"].strip() or r["SegmentName"].upper().startswith("SYSTEM/NETWORK")] or rows[:1]
    for col in ("OtherEnglishNames", "OtherLanguageAlternativePipelineNames"):
        for r in whole:
            for n in re.split(r"[;,]", r[col] or ""):
                n = n.strip()
                if n and n != pg.name and n not in names:
                    names.append(n)
    bold = [f"'''{n}'''" for n in names]   # "A and B", "A, B, and C" (Baird 2026-11-07)
    joined = "" if not bold else bold[0] if len(bold) == 1 else (" and ".join(bold) if len(bold) == 2 else ", ".join(bold[:-1]) + ", and " + bold[-1])
    aka = (", also known as " + joined + ",") if names else ""
    local = rows[0]["OtherLanguagePrimaryPipelineName"].strip() if len(rows) == 1 else ""
    local = f" (local name: '''{local}''')" if local else ""
    fuel, loc = fuel_phrase(rows, tracker), location_phrase(rows)
    # a page called a network is introduced as one: "is a ... pipeline network" (Baird 2026-11-08)
    kind = "pipeline network" if re.search(r"\bnetwork\b", pg.name, re.I) else "pipeline"
    if len(rows) == 1:
        st = STATUS_PHRASE.get(rows[0]["Status"], rows[0]["Status"])
        s = f"'''{pg.name}'''{aka}{local} is {a_an(st)} {st} {fuel} {kind} {loc}.{pg.cite(rows[0]['Status [ref]'])}"
    else:
        sts = []
        for r in rows:
            p = STATUS_PHRASE.get(r["Status"], r["Status"])
            if p and p not in sts:
                sts.append(p)
        rank = ["operating", "under construction", "proposed", "shelved", "cancelled", "idled", "mothballed", "retired"]
        sts.sort(key=lambda x: rank.index(x) if x in rank else 99)
        if len(sts) == 1:   # every segment has one status: say it like a one-row page (Baird 2026-11-07, Kern River)
            s = f"'''{pg.name}'''{aka}{local} is {a_an(sts[0])} {sts[0]} {fuel} {kind} {loc}."
        else:
            lst = join_list(sts)
            s = f"'''{pg.name}'''{aka}{local} is {a_an(fuel)} {fuel} {kind} {loc} with segments that are {lst}."
    dorm = []
    for r in rows:
        if r["ShelvedCancelledType"] != "inferred":
            continue
        st = r["Status"]
        yr = num(r["ShelvedYear"] if st == "shelved" else r["CancelledYear"])
        if yr is None:
            pg.log.append(f"{r['ProjectID']}: inferred {st} with no year; dormancy sentence left out")
            continue
        rc = r["Shelved [ref]"] if st == "shelved" else r["Cancelled [ref]"]
        # the lead only says the status; when and why go in the Background (Baird 2026-11-09, Delmarva)
        what = "pipeline" if len(rows) == 1 else "project"
        pg.dorm.append((r, f"With no development reported on the {what}, it was considered {st} as of {int(yr)}.", rc))
    return s


def table(num_, title, header, body, caption="", collapsed=False, sortable=False, footnote=""):
    # every column is shown on every page, empty or not, so the tables read the same on every page (Baird 2026-11-08)
    keep = list(range(len(header)))
    cls = "wikitable" + (" sortable" if sortable and len(body) > 1 else "") + (" mw-collapsible mw-collapsed" if collapsed else "")
    t = [f"==== '''Table {num_}:''' {title} ====", "", f'{{| class="{cls}"']
    t.append("|+" + (f" {caption}" if caption else ""))
    t += [f"!{header[i]}" for i in keep]
    for row in body:
        t.append("|-")
        # an empty route-shape cell stays blank; every other empty cell gets a dash
        t += [f"|{row[i] if row[i].strip() else ('' if header[i].endswith('|Route') else '–')}" for i in keep]
    if footnote:   # stays at the bottom when the table is sorted
        t += ['|- class="sortbottom"', f'|colspan="{len(keep)}"|{footnote}']
    t.append("|}")
    return "\n".join(t)


class Counter:
    def __init__(self):
        self.n = 0

    def __call__(self):
        self.n += 1
        return self.n


def join_near(parts, tol):
    """Join pieces of one route whose ends lie within tol degrees, reversing a piece when needed.
    A routes-repo trace can come as hundreds of two-point pieces with tiny gaps (Gulf South's Main Line:
    293), and the Maps extension draws lines with no stacking order, so past about 450 lines Google Maps
    draws some white edges over the colored lines (Baird 2026-11-09). Fewer, longer lines avoid it."""
    parts = [list(p) for p in parts if len(p) >= 2]
    near = lambda a, b: abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol
    done = False
    while not done:
        done = True
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                a, b = parts[i], parts[j]
                if near(a[-1], b[0]):
                    parts[i] = a + b
                elif near(a[-1], b[-1]):
                    parts[i] = a + b[::-1]
                elif near(a[0], b[-1]):
                    parts[i] = b + a
                elif near(a[0], b[0]):
                    parts[i] = b[::-1] + a
                else:
                    continue
                del parts[j]
                done = False
                break
            if not done:
                break
    return parts


def thin_lines(pid, tol):
    raw = B.coords_of(pid)
    if not raw:
        return []
    merged = linemerge(MultiLineString([LineString(l) for l in raw if len(l) >= 2]))
    parts = join_near([list(g.coords) for g in (merged.geoms if hasattr(merged, "geoms") else [merged])], tol)
    parts = [LineString(c) for c in parts]
    out = []
    for g in parts:
        s = g.simplify(tol, preserve_topology=False)
        if s.length < tol * 2 and len(parts) > 1:
            continue  # stubs shorter than the simplify tolerance add points but nothing visible
        out.append(list(s.coords))
    return out


MAP_EDGE, LINE_W = "#FFFFFF", 4   # the white edge under each map line, and the colored line's width in pixels


def map_block(pg, rows):
    mapped = [r for r in rows if r["RouteType"].startswith("Mapped route")]
    if not mapped:
        return "The route of this pipeline has not been mapped.", 0
    allp, lines, edges = [], [], []
    # a map that opens at zoom 4 or 5 (span over 6 degrees, about a continent) gets a coarser simplification:
    # at those zooms one pixel is 0.04 to 0.09 degrees, so the dropped points are invisible, and Transco's 450 lines
    # were slow to zoom and pan on a phone (Baird 2026-11-09)
    raw = [p for r in mapped for l in (B.coords_of(r["ProjectID"]) or []) for p in l]
    rspan = max(max(p[1] for p in raw) - min(p[1] for p in raw), max(p[0] for p in raw) - min(p[0] for p in raw)) if raw else 0
    tol = 0.025 if rspan > 12 else 0.015 if rspan > 6 else 0.01 if len(rows) > 1 else 0.003
    for r in mapped:
        ls = thin_lines(r["ProjectID"], tol)
        if not ls:
            pg.log.append(f"{r['ProjectID']}: RouteType says mapped but the routes repo has no geometry")
            continue
        color = status_color(pg, r["Status"])
        for l in ls:
            allp += l
            pts = ":".join(f"{p[1]:.5f}, {p[0]:.5f}" for p in l)
            title = label(r, rows) if len(rows) > 1 else pg.name
            dot = f'<span class="gem-mapdot gem-mapdot-{r["Status"].replace(" ", "-")}"></span>'
            pop = f"{pts}~{title}~{dot}{STATUS_PHRASE.get(r['Status'], r['Status']).capitalize()}"
            edges.append(f"{pts}~~~{MAP_EDGE}~1~{LINE_W + 5}")
            lines.append(f"{pop}~{color}~1~{LINE_W}")
    # every line gets a white edge, drawn first under all the colored lines, so a status color reads on any
    # background (Baird 2026-11-09, after oilandgaswatch.org's bordered lines). The edge has no label or pop-up text:
    # only the colored line carries it, which halves the repeated text on big maps (Baird 2026-11-09)
    lines = edges + lines
    if not lines:
        return "The route of this pipeline has not been mapped.", 0
    lats, lons = [p[1] for p in allp], [p[0] for p in allp]
    span = max(max(lats) - min(lats), max(lons) - min(lons))
    zoom = 4 if span > 12 else 5 if span > 6 else 6 if span > 3 else 7 if span > 1.5 else 8 if span > .7 else 9
    text = ""   # no "The map below shows ..." sentence on a one-segment page (Baird 2026-11-08)
    # a legend under every map, one segment or many (Baird 2026-11-09)
    sts = sorted({r["Status"] for r in mapped}, key=lambda x: STATUS_ORDER.index(x) if x in STATUS_ORDER else 99)
    legend = "\n\n" + " &nbsp; ".join(f'<span style="color:{status_color(pg, s)}">■</span> {STATUS_PHRASE.get(s, s).capitalize()}'
                                        for s in sts)
    if len(rows) > 1:
        # one plain count on multi-segment pages (Baird 2026-11-06)
        text = f"{len(mapped)} of {len(rows)} segments have a mapped route in the database."
    body = ";".join(lines)
    mid = f"{(max(lats) + min(lats)) / 2:.5f}, {(max(lons) + min(lons)) / 2:.5f}"
    return ((f'{text}\n\n' if text else "") + f'<templatestyles src="{MAP_STYLES_PAGE}" />\n'
            f"{{{{#display_map:\n|lines={body}|center={mid}|width=100%|height=400|type=map|zoom={zoom}}}}}{legend}",
            len(allp))


def join_list(xs):
    # serial (Oxford) comma from three items up (GEM style guide, Baird 2026-11-08)
    return xs[0] if len(xs) == 1 else xs[0] + " and " + xs[1] if len(xs) == 2 else ", ".join(xs[:-1]) + ", and " + xs[-1]


SHAPE_W, SHAPE_H, SHAPE_PAD = 120, 60, 4


def shape_file(pid):
    return f"Route shape {pid}.svg"


def route_shape_svg(pid, color=MAP_GREY):
    """The unit's route drawn as a bare line (no map) in its status color, fitted to a small box; None when it has no route."""
    import math
    lines = [l for l in B.coords_of(pid) if len(l) >= 2]
    if not lines:
        return None
    lat0 = sum(p[1] for l in lines for p in l) / sum(len(l) for l in lines)
    k = math.cos(math.radians(lat0))
    xy = [[(p[0] * k, -p[1]) for p in l] for l in lines]
    xs = [x for l in xy for x, _ in l]; ys = [y for l in xy for _, y in l]
    w, h = (max(xs) - min(xs)) or 1e-9, (max(ys) - min(ys)) or 1e-9
    sc = min((SHAPE_W - 2 * SHAPE_PAD) / w, (SHAPE_H - 2 * SHAPE_PAD) / h)
    ox = (SHAPE_W - w * sc) / 2 - min(xs) * sc
    oy = (SHAPE_H - h * sc) / 2 - min(ys) * sc
    paths = []
    for l in xy:
        g = LineString([(x * sc + ox, y * sc + oy) for x, y in l]).simplify(0.3)
        pts = list(g.coords)
        if len(pts) >= 2:
            paths.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SHAPE_W}" height="{SHAPE_H}" viewBox="0 0 {SHAPE_W} {SHAPE_H}">'
            f'<path d="{" ".join(paths)}" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg>\n')


# ---------- per-segment cells (shared by the separate tables and the tabbed segment table) ----------

END_RULE = '<div style="border-top:1px solid #c8ccd1;margin-top:0.25em;padding-top:0.25em">'   # a thin rule between start and end


def route_cells(pg, r):
    """start/end (with the Location ref) and countries. No length here: the Route details table carried an
    unreferenced copy of it, and the referenced figure already sits in the Pipeline details table (Baird
    2026-11-06, Ruby). The tabbed table's Route tab shows the referenced Pipeline details cell instead."""
    a = place(r["StartLocation"], r["StartState/Province"]) or "–"
    z = place(r["EndLocation"], r["EndState/Province"]) or "–"
    rf = pg.cite(r["Location [ref]"])
    rf = f'<span style="float:right;margin-left:0.4em">{rf}</span>' if rf else ""   # the refs sit at the right end of the End line
    return [f"'''Start:''' {a}{END_RULE}{rf}'''End:''' {z}</div>",
            ", ".join(countries(r["CountriesOrAreas"]))]


def detail_cells(pg, r, units):
    """status, fuel, capacity, length, diameter, pressure, each with its ref; `units` collects the unit
    abbreviations used, for the caption."""
    cap = f"{fmt(r['Capacity'])} {r['CapacityUnits']}".strip() if r["Capacity"].strip() else ""
    ln = r["LengthKnown"].strip()
    if ln:
        ln = "0 (expansion with no new pipe)" if num(ln) == 0 else f"{fmt(ln)} {r['LengthKnownUnits']}"
    est = "" if ln else length_est(r)
    dia = f"{', '.join(fmt(x) for x in r['Diameter'].split(','))} {r['DiameterUnits']}".strip() if r["Diameter"].strip() else ""
    units |= {r["CapacityUnits"] if cap else "", r["LengthKnownUnits"] if ln and num(r["LengthKnown"]) else "",
              r["DiameterUnits"] if dia else ""}
    p = f"{r['Pressure']} {r['PressureUnits']}".strip() if r.get("Pressure", "").strip() else ""
    return [status_dot(pg, r["Status"]) + r["Status"] + pg.cite(r["Status [ref]"]),
            r["Fuel"] + (pg.cite(r["Fuel [ref]"]) if r["Fuel"] else ""),
            cap + (pg.cite(r["Capacity [ref]"]) if cap else ""),
            (ln + pg.cite(r["Length [ref]"])) if ln else est,
            dia + (pg.cite(r["Diameter [ref]"]) if dia else ""),
            p + (pg.cite(r["Pressure [ref]"]) if p else "")]


def timeline_cells(pg, r):
    """proposal year, FID, construction year, start year, each with its ref. No inactive year column (Baird 2026-11-08)."""
    st = r["Status"]
    fid = ""
    if r["FIDYear"].strip() or r["FIDStatus"].strip():
        fid = " ".join(x for x in (r["FIDYear"].strip(), f"({r['FIDStatus']})" if r["FIDStatus"].strip() else "") if x)
        fid += pg.cite(r["FID [ref]"])
    start = ""
    if r["StartYear1"].strip():
        start = r["StartYear1"].strip()
        if st in ("proposed", "construction"):
            start += " (planned)"
        extra = [f"{r[c].strip()} (phase {i})" for i, c in ((2, "StartYear2"), (3, "StartYear3")) if r[c].strip()]
        if extra:
            start = ", ".join([start] + extra)
        start += pg.cite(r["Start [ref]"])
        if r["Delayed"].strip().lower() == "yes":
            start += " (delayed)" + pg.cite(r["Delay [ref]"])
    prop = r["ProposalYear"].strip()
    cons = r["ConstructionYear"].strip()
    return [prop + (pg.cite(r["Proposal [ref]"]) if prop else ""), fid,
            cons + (pg.cite(r["Construction [ref]"]) if cons else ""), start]


def cost_cell(pg, r):
    """One Cost cell: the project-level cost when the row has one, otherwise the segment cost (Baird
    2026-11-06). Money words (million, billion) do not sort; the hidden sort key is the full amount in
    USD where known."""
    if r["ProjectLevelCost"].strip() and num(r["ProjectLevelCost"]):
        val, cur, rc = r["ProjectLevelCost"], r["ProjectLevelCostUnits"].strip(), r["ProjectLevelCost [ref]"]
    else:
        val, cur, rc = r["SegmentCost"], r["SegmentCostUnits"].strip(), r["SegmentCost [ref]"]
    c = money(val, cur)
    if c and cur not in ("", "USD") and num(r["CostUSD"]):
        c += f" ({money(r['CostUSD'], 'USD')})"
    key = num(r["CostUSD"]) if cur not in ("", "USD") and num(r["CostUSD"]) else num(val)
    return (f'data-sort-value="{key:.0f}"|' if c and key else "") + c + (pg.cite(rc) if c else "")


def owner_cells(pg, r, owners):
    """operator, owner (names with shares) and parent, in that column order (Baird 2026-11-06): operator and owner
    from the operators/owners tab, each with its ref, and the parent as the tracker tab's Parent column states it
    (shares kept where known; no ref column)."""
    o = owners.get(r["ProjectID"])
    if o is None:
        pg.log.append(f"{r['ProjectID']}: no operators/owners row; Owner taken from the tracker tab")
        return ["", r["Owner"], parent_cell(r)]
    names = []
    for i in range(1, 12):
        n = (o.get(f"Owner{i}") or "").strip()
        if n:
            p = pct(o.get(f"Owner{i}%"))
            names.append(f"{n} ({p})" if p else n)
    own = "; ".join(names) + (pg.cite(o.get("Owner [ref]")) if names else "")
    opr = (o.get("Operator") or "").strip()
    opr += pg.cite(o.get("Operator [ref]")) if opr else ""
    return [opr, own, parent_cell(r)]


def parent_cell(r):
    return B.parent_text(r.get("Parent"))


def shape_cells(pg, rows):
    """ProjectID -> route-shape image cell (or '' when the row has no route); {} when no row has one."""
    shapes = {r["ProjectID"]: route_shape_svg(r["ProjectID"], status_color(pg, r["Status"])) for r in rows}
    if not any(shapes.values()):
        return {}
    out = {}
    for r in rows:
        sv = shapes[r["ProjectID"]]
        if sv:
            pg.shapes[shape_file(r["ProjectID"])] = sv
        out[r["ProjectID"]] = f"[[File:{shape_file(r['ProjectID'])}|{SHAPE_W // 2 + 30}px|link=|alt=Route shape of {label(r, rows)}]]" if sv else ""
    return out


FID_GLOSS = "FID = final investment decision, used by some developers to indicate a project will move forward"
COST_NOTE = "The project-level cost where the segment has one, otherwise the segment's own cost."


def gloss(units):
    return "; ".join(UNIT_GLOSS[u] for u in sorted(u for u in units if u in UNIT_GLOSS))


# ---------- the tabbed segment table (pages with SEG_TABLE_MIN or more segments) ----------

SEG_TABLE_MIN = 5    # five or more segments get the tabbed table (Baird 2026-11-06; was ten)
STYLES_PAGE = "Segment table/styles.css"       # Template:Segment table/styles.css, content model sanitized-css
MAP_STYLES_PAGE = "Pipeline map/styles.css"    # Template:Pipeline map/styles.css: the click popup on the route map

# The Maps extension hands Google Maps `<b><p>title</p></b><p>status</p>` for a clicked line, and Google's info
# window adds a 48 px header row for its close button, 12 px padding and scrollbars, so the popup was mostly
# empty space (Baird 2026-11-06). This collapses the header, shrinks the close button into the corner, drops the
# paragraph margins and sets the two lines as name over status. The inline sizes Google sets need !important.
MAP_CSS = """\
/* Click popup on the route map of pipeline pages. Generated by the GEM pipeline page builder
   (pipelines-researcher, wiki/scripts/generate_pages.py); edit it there, not here. */
.gm-style .gm-style-iw-c { padding: 7px 10px 8px 11px !important; min-width: 0 !important; border-radius: 6px; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3); }
.gm-style .gm-style-iw-chr { position: absolute; top: 0; right: 0; height: auto; min-height: 0; }
.gm-style .gm-style-iw-ch { display: none; }
.gm-style .gm-style-iw-chr button { width: 22px !important; height: 22px !important; margin: 2px 2px 0 0 !important; opacity: 0.55; }
.gm-style .gm-style-iw-chr button:hover { opacity: 1; }
.gm-style .gm-style-iw-chr button span { width: 14px !important; height: 14px !important; margin: 4px !important; }
.gm-style .gm-style-iw-d { overflow: auto !important; padding-right: 18px; font-size: 12px; line-height: 1.35; color: #202122; }
.gm-style .gm-style-iw-d p { margin: 0; padding: 0; line-height: inherit; white-space: nowrap; }
.gm-style .gm-style-iw-d b p { font-size: 13px; margin: 0 0 1px; }
.gm-style .gm-style-iw-d p + p { color: #54595d; }
.gem-mapdot { display: inline-block; width: 8px; height: 8px; margin: 0 5px 1px 0; border-radius: 50%; vertical-align: middle; background: """ + MAP_GREY + """; }
/* phones: the map takes about half the screen, so a thumb finds page above or below it to keep scrolling; never taller than the 400 px desktop map, never under 260 px (Baird 2026-11-09). The Maps extension sets the height inline, so it needs !important */
@media (max-width: 767px) { .maps-map.maps-googlemaps3 { height: 50vh !important; max-height: 400px; min-height: 260px; } }
""" + "".join(f".gem-mapdot-{s.replace(' ', '-')} {{ background: {c}; }}\n" for s, c in STATUS_COLORS["gas"].items())
SEG_GROUPS = ("route", "details", "timeline", "cost", "ownership")
SEG_TAB_LABEL = {"route": "Route", "details": "Details", "timeline": "Timeline", "cost": "Cost",
                 "ownership": "Ownership", "all": "All columns"}
# the stylesheet: every rule is prefixed with .mw-parser-output by TemplateStyles. No tab in the URL
# shows the route group; #seg-<group> in the URL shows that group; #seg-all shows every column.
_CSS_HEAD = """\
/* Tabbed segment table on pipeline pages with many segments. Generated by the GEM pipeline page
   builder (pipelines-researcher, wiki/scripts/generate_pages.py); edit it there, not here. */
/* the table scrolls inside a box a bit shorter than the window, with the tab strip and the column headers fixed at its top (Baird 2026-11-06) */
.gem-segments { overflow: auto; max-height: 80vh; margin-top: 0.6em; }
.gem-segtabs { position: sticky; top: 0; left: 0; z-index: 3; height: 34px; margin: 0; padding-top: 4px; box-sizing: border-box; white-space: nowrap; overflow-x: auto; overflow-y: hidden; background: #fff; line-height: 1.2; }
/* the strip scrolls sideways on its own on a narrow screen, so it never makes the box wider than the table */
/* the headers tuck 3px under the tab strip, or a sliver of the rows shows between the two */
.gem-segments th { position: sticky; top: 31px; z-index: 4; border-top: 0; box-shadow: inset 0 1px #a2a9b1, inset 0 -1px #a2a9b1; }
/* a fixed header's own border scrolls away with the table, so its top and bottom lines are drawn as shadows that stay; the tab strip draws no line of its own, so no line runs wider than the table (Baird 2026-11-06) */
.gem-segtabs a { display: inline-block; padding: 0.35em 0.9em; margin: 0 0.15em -1px 0; border: 1px solid #a2a9b1; border-radius: 4px 4px 0 0; background: #eaecf0; color: #202122; font-size: 95%; text-decoration: none; }
.gem-segtabs a:hover { background: #f8f9fa; }
/* the anchors sit fixed at the top of the window, always in view, so a tab click does not scroll the page */
#seg-route, #seg-details, #seg-timeline, #seg-cost, #seg-ownership, #seg-all { position: fixed; top: 0; left: 0; width: 0; height: 0; overflow: hidden; }
/* a segment link lands its row near the top of the window in both tables */
.gem-anchor { display: inline-block; width: 0; height: 0; scroll-margin-top: 4.5em; }
.gem-segments .gem-anchor { scroll-margin-top: 7em; }
/* the Background table on the same pages: its own box, header fixed at the top */
.gem-bgbox { overflow: auto; max-height: 80vh; }
.gem-bgbox table { margin: 0; }
.gem-bgbox th { position: sticky; top: 0; z-index: 2; border-top: 0; box-shadow: inset 0 1px #a2a9b1, inset 0 -1px #a2a9b1; }
.gem-bgbox .gem-anchor { scroll-margin-top: 3.5em; }   /* below the column header */
.gem-segments table { margin-top: 0; }
/* the phone skin makes a table a block that scrolls sideways on its own, which breaks the fixed headers; the box does the scrolling instead */
.gem-segments table, .gem-bgbox table { display: table; overflow: visible; border-top: 0; }
/* the Ownership tab: Operator, Owner and Parent share the width equally (Baird 2026-11-06) */
#seg-ownership:target ~ .gem-segments table { display: table; table-layout: fixed; width: 100%; }   /* display: the phone skin makes tables blocks, which ignores fixed layout */
#seg-ownership:target ~ .gem-segments th.col-ownership { width: 26%; }
#seg-ownership:target ~ .gem-segments td { overflow-wrap: break-word; }
/* phones: the tables scroll sideways inside their boxes rather than squeeze into the screen width; a Background cell is most of a screen wide, names keep room, and the Ownership tab drops its fixed equal widths (Baird 2026-11-09) */
@media (max-width: 767px) {
.gem-segments, .gem-bgbox { max-height: 67vh; }   /* about two thirds of the screen, so there is page to scroll on above or below (Baird 2026-11-09) */
.gem-bgbox td:last-child { min-width: 85vw; }
.gem-bgbox td:nth-last-child(3), .gem-segments td:nth-child(2) { min-width: 9em; }
#seg-ownership:target ~ .gem-segments table { table-layout: auto; width: auto; }
#seg-ownership:target ~ .gem-segments th.col-ownership { width: auto; }
#seg-ownership:target ~ .gem-segments td.col-ownership { min-width: 11em; }
}
.gem-segments .cap-details, .gem-segments .cap-timeline, .gem-segments .cap-cost, .gem-segments .cap-ownership, .gem-segments .cap-all { display: none; }
"""


def seg_css():
    css = [_CSS_HEAD]
    hide = lambda pre, gs: ", ".join(f"{pre} .gem-segments .col-{g}".strip() for g in gs) + " { display: none; }\n"
    # default: the route group
    css.append(hide("", [g for g in SEG_GROUPS if g != "route"]))
    css.append(".gem-segments .col-route { display: table-cell; }\n.gem-segments tr.col-route { display: table-row; }\n")
    css.append('.gem-segtabs a[href="#seg-route"] { background: #fff; font-weight: bold; }\n')
    for g in SEG_GROUPS[1:] + ("all",):
        t = f"#seg-{g}:target ~"
        css.append(f"/* {g} */\n")
        if g == "all":
            css.append(", ".join(f"{t} .gem-segments .col-{x}" for x in SEG_GROUPS) + " { display: table-cell; }\n")
            css.append(", ".join(f"{t} .gem-segments tr.col-{x}" for x in SEG_GROUPS) + " { display: table-row; }\n")
        else:
            css.append(hide(t, [x for x in SEG_GROUPS if x != g]))
            css.append(f"{t} .gem-segments .col-{g} {{ display: table-cell; }}\n{t} .gem-segments tr.col-{g} {{ display: table-row; }}\n")
        css.append(f"{t} .gem-segments .cap-{g} {{ display: inline; }}\n")
        css.append(f'{t} .gem-segments .gem-segtabs a[href="#seg-route"] {{ background: #eaecf0; font-weight: normal; }}\n')
        css.append(f'{t} .gem-segments .gem-segtabs a[href="#seg-{g}"] {{ background: #fff; font-weight: bold; }}\n')
    return "".join(css)


SEG_CSS = seg_css()


def segment_table(pg, rows, owners):
    """One sortable table, a row per segment, every column tagged with its group(s) so the stylesheet
    can show one group at a time. Every column and every tab is shown on every page, empty or not, so the
    tables read the same on every page (Baird 2026-11-08). Old heading anchors (Table 1 ... Ownership) are kept as empty spans."""
    units = set()
    shapes = shape_cells(pg, rows)
    # (header, groups, unsortable) in table order: one order serves every tab
    cols = [("Route", ["route"], True), ("Start/end", ["route"], False), ("Countries/areas", ["route"], False),
            ("Status", ["details", "timeline"], False), ("Fuel", ["details"], False), ("Capacity", ["details"], False),
            ("Length", ["route", "details"], False), ("Diameter", ["details"], False), ("Pressure", ["details"], False),
            ("Proposal year", ["timeline"], False), ("FID", ["timeline"], False), ("Construction year", ["timeline"], False),
            ("Start year", ["timeline"], False),
            ("Cost", ["cost"], False), ("Operator", ["ownership"], False), ("Owner", ["ownership"], False), ("Parent", ["ownership"], False)]
    body = []
    for r in rows:
        rt = route_cells(pg, r)
        dt = detail_cells(pg, r, units)
        tl = timeline_cells(pg, r)
        cells = [shapes.get(r["ProjectID"], "")] + rt[:2] + [dt[0], dt[1], dt[2], dt[3], dt[4], dt[5]] + tl + [cost_cell(pg, r)] + owner_cells(pg, r, owners)
        body.append((label(r, rows), cells))
    keep = list(range(len(cols)))
    groups = [g for g in SEG_GROUPS if any(g in cols[i][1] for i in keep)]
    est = any(cells[6].endswith("*") for _, cells in body) and 6 in keep
    caps = {"details": gloss(units), "timeline": FID_GLOSS if 10 in keep else "", "cost": COST_NOTE if 13 in keep else ""}
    caps["all"] = "; ".join(c for c in (caps["details"], caps["timeline"], caps["cost"].rstrip(".")) if c)
    t = [f'<templatestyles src="{STYLES_PAGE}" />',
         '<span id="Table_1:_Route_details"></span><span id="Table_2:_Pipeline_details"></span><span id="Table_3:_Project_timeline"></span>'
         '<span id="Table_4:_Cost"></span><span id="Table_5:_Ownership"></span><span id="Ownership"></span>']
    t += [f'<div id="seg-{g}"></div>' for g in groups + ["all"]]
    t += ['<div class="gem-segments">',
          '<div class="gem-segtabs">' + " ".join(f"[[#seg-{g}|{SEG_TAB_LABEL[g]}]]" for g in groups + ["all"]) + "</div>",
          '{| class="wikitable sortable"',
          "|+ " + "".join(f'<span class="cap-{g}">{c}</span>' for g, c in caps.items() if c and (g == "all" or g in groups)),
          "!#", "!Segment"]   # a running number counts the segments (Baird 2026-11-08)
    for i in keep:
        h, gs, uns = cols[i]
        t.append(f'!class="{"unsortable " if uns else ""}{" ".join("col-" + g for g in gs)}"|{h}')
    for n, ((lab, cells), r) in enumerate(zip(body, rows), 1):
        pid = r["ProjectID"]
        # each segment name is an anchor, and links down to its Background row when it has one (Baird 2026-11-06)
        t += ["|-", f"|{n}", f'|style="background-color:{UNIT_GRAY}"|<span id="row-{pid}" class="gem-anchor"></span>' + (f'<span title="Click for project background">[[#bg-{pid}|{lab}]]</span>' if pid in pg.bg else lab)]
        for i in keep:
            v = cells[i].strip()
            cls = f'class="{" ".join("col-" + g for g in cols[i][1])}"'
            m = re.match(r'(data-sort-value="[^"]*")\|(.*)', v, re.S)   # a cost cell carries its sort key as an attribute
            if m:
                cls, v = f"{cls} {m.group(1)}", m.group(2)
            t.append(f'|{cls}|{v if v else ("" if i == 0 else "–")}')
    if est:
        t += ['|- class="sortbottom col-route col-details"', f'|colspan="{len(keep) + 2}"|{EST_NOTE}']
    t += ["|}", "</div>"]
    pg.log.append(f"tabbed segment table: {len(rows)} segments, {len(keep) + 2} columns, tabs {', '.join(groups)}")
    return "\n".join(t)


# ---------- sections ----------

def location(pg, rows, tab, tabbed=False):
    # no sentence here, ever: just the route table and the map (Baird 2026-11-09). The location refs sit in the
    # table's Start/end cells (or the tabbed table's Route tab), so none is lost.
    out = ["==Location=="]
    if not tabbed:
        # the Route details table, the five-table pages' version of the tabbed table's Route tab. A one-segment page
        # gets it too, open and with no route picture, since the map sits right below (Baird 2026-11-06)
        shapes = shape_cells(pg, rows) if len(rows) > 1 else {}
        body = [([shapes[r["ProjectID"]]] if shapes else []) + [label(r, rows)] + route_cells(pg, r) for r in rows]
        out += [table(tab(), "Route details", (['class="unsortable"|Route'] if shapes else []) + ["Segment", "Start/end", "Countries/areas"], body,
                          sortable=True)]   # always open, never collapsed (Baird 2026-11-08)
    m, npts = map_block(pg, rows)
    out += (["", m] if len(out) > 1 else [m])
    pg.log.append(f"map points: {npts}")
    return "\n".join(out)


def details(pg, rows, tab):
    out = ["==Project details=="]
    units = set()
    body = []
    for r in rows:
        d = detail_cells(pg, r, units)
        body.append([label(r, rows)] + d)
    head = ["Segment", "Status", "Fuel", "Capacity", "Length", "Diameter", "Pressure"]
    out.append(table(tab(), "Pipeline details", head, body, gloss(units), sortable=True,
                     footnote=EST_NOTE if any(b[4].endswith("*") for b in body) else ""))

    # timeline
    # no Status column: the Pipeline details table right above already shows it (Baird 2026-11-06, Ruby)
    body = [[label(r, rows)] + timeline_cells(pg, r) for r in rows]
    cap = FID_GLOSS if any(r["FIDStatus"].strip() or r["FIDYear"].strip() for r in rows) else ""
    out += ["", table(tab(), "Project timeline", ["Segment", "Proposal year", "FID", "Construction year",
                                                  "Start year"], body, cap, sortable=True)]

    # cost
    body = [[label(r, rows), cost_cell(pg, r)] for r in rows]
    out += ["", table(tab(), "Cost", ["Segment", "Cost"], body, sortable=True)]   # the table even with no cost, like every other
    return "\n".join(out)


def ownership(pg, rows, owners, tab):
    """Table 5: Ownership, a table under Project details after Cost, not a section of its own (Baird 2026-11-07)."""
    body = [[label(r, rows)] + owner_cells(pg, r, owners) for r in rows]
    return table(tab(), "Ownership", ["Segment"] + [f'width="26%"|{h}' for h in ("Operator", "Owner", "Parent")], body)


# ---------- preserved sections ----------

def strip_generated_comments(txt):
    return re.sub(r"<!---.*?-->", lambda m: "" if "COMMENT" in m.group(0) else m.group(0), txt, flags=re.S)


def split_sections(txt):
    """[(heading or None, level, body)] for level-2 sections; body keeps its subsections."""
    parts = re.split(r"(?m)^(==[^=].*?[^=]==)\s*$", txt)
    out = [(None, 0, parts[0])]
    for i in range(1, len(parts), 2):
        h = parts[i].strip("= ").strip()
        out.append((h, 2, parts[i + 1]))
    return out


def preserved(pg, live):
    """(kept sections, kept Articles-and-Resources subsections, replaced text). The replaced text is
    everything the generator rebuilds, scanned later so none of its references are lost."""
    if not live:
        return "", "", ""
    txt = strip_generated_comments(live).replace("__NOTOC__", "")
    secs = split_sections(txt)
    keep, extra_ar, replaced = [], [], [secs[0][2]]  # the lead (intro) is always regenerated
    for h, _, body in secs[1:]:
        if h.lower() in GENERATED:
            replaced.append(body)
            if h.lower() in ("articles and resources", "resources and articles"):
                for sh, sb in re.findall(r"(?ms)^===\s*(.*?)\s*===\s*$(.*?)(?=^===|\Z)", body):
                    if sh.lower() not in GENERATED_SUBS and sb.strip():
                        extra_ar.append(f"==={sh}===\n{sb.strip()}")
                        pg.log.append(f"kept Articles and Resources subsection: {sh}")
            continue
        keep.append(f"=={h}==\n{body.strip()}")
        pg.log.append(f"kept section: {h}")
    return "\n\n".join(keep), "\n\n".join(extra_ar), "\n\n".join(replaced)


URL_RE = re.compile(r"https?://[^\s|\]}<>\"']+")
REF_ANY = re.compile(r"<ref(?:\s+name\s*=\s*\"?([^\">/]+?)\"?)?\s*>(.*?)</ref>", re.S)
OWN_LINK = re.compile(r"globalenergymonitor\.org/projects/|gem\.wiki/|maps\.google", re.I)


def norm_url(u):
    u = u.strip().rstrip(".,;)")
    u = re.sub(r"^https?://(www\.)?", "", u, flags=re.I)
    return u.rstrip("/").lower()


def lost_refs(pg, replaced, new_text):
    """Every <ref> and bare external link in the replaced sections whose source the new page no
    longer cites. Returns the citations, which add_sources puts in Background, so nothing is dropped."""
    have = {norm_url(u) for u in URL_RE.findall(new_text)}
    flat = re.sub(r"\s+", " ", new_text)
    out, seen = [], set()
    body = replaced
    for m in REF_ANY.finditer(replaced):
        c = m.group(2).strip()
        if not c:
            continue
        us = [u for u in URL_RE.findall(c) if not OWN_LINK.search(u)]
        key = tuple(sorted(norm_url(u) for u in us)) or (re.sub(r"\s+", " ", c),)
        if key in seen:
            continue
        seen.add(key)
        if us and all(norm_url(u) in have for u in us):
            continue
        if not us and re.sub(r"\s+", " ", c) in flat:
            continue
        out.append(c)
    body = REF_ANY.sub("", body)
    for u in URL_RE.findall(body):  # external links written outside <ref> tags
        if OWN_LINK.search(u) or norm_url(u) in have or (norm_url(u),) in seen:
            continue
        seen.add((norm_url(u),))
        out.append(f"[{u.rstrip('.,;)')}]")
    if out:
        pg.log.append(f"{len(out)} sources cited only in replaced sections; added to Background")
    return out


OTHER_SOURCES_INTRO = re.compile(r"(?im)^\s*Sources cited on earlier versions of this page\.?\s*$")
ADDITIONAL = re.compile(r"(?m)^Additional sources:(.*)$")


def pop_other_sources(pg, kept):
    """(kept without its 'Other sources' section, the section's citations). There is never an Other sources
    section (Baird 2026-11-07, Los Ramones): its citations go into Background through add_sources."""
    secs = split_sections(kept)
    if not any(h and h.lower() == "other sources" for h, _, _ in secs[1:]):
        return kept, []
    cites, rest = [], [secs[0][2].strip()] if secs[0][2].strip() else []
    for h, _, body in secs[1:]:
        if h.lower() != "other sources":
            rest.append(f"=={h}==\n{body.strip()}")
            continue
        body = OTHER_SOURCES_INTRO.sub("", body)
        for m in REF_ANY.finditer(body):   # refs written inside the section
            if m.group(2).strip():
                cites.append(m.group(2).strip())
        body = REF_ANY.sub("", body)
        for line in body.splitlines():
            line = re.sub(r"^\s*[*#:]+\s*", "", line).strip()
            if line:
                cites.append(line)
    pg.log.append(f"Other sources section removed; {len(cites)} citations to Background")
    return "\n\n".join(rest), cites


def add_sources(pg, kept, cites, new_text):
    """Citations that no longer sit beside a fact go on one line at the very bottom of Background, 'Additional
    sources: ' then the refs, a space after the colon (Baird 2026-11-07). A line already there is extended, never repeated. Citations
    the page already cites elsewhere are skipped. Placing a citation beside the fact it supports is a hand edit."""
    kept = re.sub(r"(?m)^Additional sources:(?=\S)", "Additional sources: ", kept)   # a space before the refs (Baird 2026-11-07)
    have = {norm_url(u) for u in URL_RE.findall(new_text)}
    out, seen = [], set()
    for c in cites:
        us = [u for u in URL_RE.findall(c) if not OWN_LINK.search(u)]
        key = tuple(sorted(norm_url(u) for u in us)) or (re.sub(r"\s+", " ", c),)
        if key in seen or (us and all(norm_url(u) in have for u in us)) or (not us and c in new_text):
            continue
        seen.add(key)
        out.append(c)
    pg.carried = list(out)
    if not out:
        return kept
    refs = "".join(f"<ref>{c}</ref>" for c in out)
    secs = split_sections(kept)
    i = next((k for k, (h, _, _) in enumerate(secs) if h and h.lower() == "background"), None)
    if i is None:
        bg_body = f"Additional sources: {refs}"
        parts = [s[2].strip() for s in secs[:1] if s[2].strip()] + [f"=={h}==\n{b.strip()}" for h, _, b in secs[1:]]
        return "\n\n".join(parts + [f"==Background==\n{bg_body}"])
    h, _, body = secs[i]
    body = body.rstrip()
    if ADDITIONAL.search(body):
        m = list(ADDITIONAL.finditer(body))[-1]
        body = body[:m.end()] + refs + body[m.end():]
    else:
        body = body + "\n\nAdditional sources: " + refs
    secs[i] = (h, 2, "\n" + body.strip() + "\n")
    parts = [secs[0][2].strip()] if secs[0][2].strip() else []
    parts += [f"=={h}==\n{b.strip()}" for h, _, b in secs[1:]]
    pg.log.append(f"{len(out)} citations added to the Additional sources line in Background")
    return "\n\n".join(parts)


def audit_refs(pg, live, text):
    """Every citation on the live page must still be on the generated page: a <ref> with URLs by each URL, a
    <ref> without one by its text, and a bare external link by its URL. Returns the citations that are not,
    and logs each one. The run never saves a page with a lost citation (Baird 2026-11-06)."""
    if not live:
        pg.lost = []
        return []
    src = strip_generated_comments(live)
    have = {norm_url(u) for u in URL_RE.findall(text)}
    flat = re.sub(r"\s+", " ", text)
    lost, seen = [], set()
    for m in REF_ANY.finditer(src):
        c = m.group(2).strip()
        if not c:
            continue
        us = [u for u in URL_RE.findall(c) if not OWN_LINK.search(u)]
        key = tuple(sorted(norm_url(u) for u in us)) or (re.sub(r"\s+", " ", c),)
        if key in seen:
            continue
        seen.add(key)
        if us:
            missing = [u for u in us if norm_url(u) not in have]
            if missing:
                lost.append(c)
        elif re.sub(r"\s+", " ", c) not in flat:
            lost.append(c)
    for u in URL_RE.findall(REF_ANY.sub("", src)):
        if OWN_LINK.search(u) or norm_url(u) in have or (norm_url(u),) in seen:
            continue
        seen.add((norm_url(u),))
        lost.append(f"[{u.rstrip('.,;)')}]")
    pg.lost = lost
    for c in lost:
        pg.log.append(f"LOST REF (on the live page, not on the generated page): {c[:200]}")
    return lost


NAMED_DEF = re.compile(r'<ref\s+name\s*=\s*"?([^">/]+?)"?\s*>(.*?)</ref>', re.S)
NAMED_USE = re.compile(r'<ref\s+name\s*=\s*"?([^">/]+?)"?\s*/>')


def fix_named_refs(pg, kept, live, generated):
    """Preserved text may reuse a named ref whose definition sat in a replaced section. Copy the
    definition from the live page into the first reuse, so the citation still renders."""
    defs_live = {m.group(1).strip(): m.group(2) for m in NAMED_DEF.finditer(live or "")}
    have = {m.group(1).strip() for m in NAMED_DEF.finditer(kept + generated)}
    fixed = set()

    def sub(m):
        n = m.group(1).strip()
        if n in have or n in fixed:
            return m.group(0)
        if n in defs_live:
            fixed.add(n)
            return f'<ref name="{n}">{defs_live[n]}</ref>'
        pg.log.append(f"UNDEFINED named ref in kept text, no definition on the live page either: {n}")
        return m.group(0)

    out = NAMED_USE.sub(sub, kept)
    for n in sorted(fixed):
        pg.log.append(f"named ref '{n}' was defined only in a replaced section; definition copied into kept text")
    return out


def seed_url_names(pg, kept):
    # a URL already cited by a named ref in kept text is reused by the generated tables (one entry, not two)
    for m in NAMED_DEF.finditer(kept):
        um = re.search(r"\|\s*url\s*=\s*([^|}\s]+)", m.group(2)) or re.search(r"\[(https?://\S+)", m.group(2))
        if um:
            pg.url_name.setdefault(um.group(1), m.group(1).strip())


# ---------- page ----------

def _key(x):
    x = re.sub(r"\(P\d{4}\)", "", x.lower())
    x = re.sub(r"\b(project|projects|expansion|gas|pipelines?|phase|the)\b", " ", x)
    x = re.sub(r"\bii\b", "2", re.sub(r"\biii\b", "3", re.sub(r"\bi\b", "1", x)))
    return re.sub(r"[^a-z0-9]+", "", x)


def main_line_key(rows, pid=False):
    """A Background subsection called "Main Line" (or "Main System", "Mainline") is the one row whose SegmentName
    is blank, when there is exactly one (hand-built pages label that row Main Line; 10 US pages, 2026-11-06).
    Returns {key: Status} or, with pid, {key: ProjectID}."""
    blank = [r for r in rows if not (r["SegmentName"] or "").strip()]
    if len(blank) != 1:
        return {}
    r = blank[0]
    return {_key(k): (r["ProjectID"] if pid else r["Status"]) for k in ("Main Line", "Mainline", "Main System")}


def background_table(pg, kept, rows):
    """On a many-segment page, a Background written as one === subsection per segment becomes a
    table (Segment | Status | Background). Text before the first subsection stays as prose; a
    deeper heading inside a subsection becomes a bold line in its cell. Nothing else changes, refs
    included. A Background that is already a table, or has fewer than two subsections, is left alone."""
    m = re.search(r"(?ms)^==\s*Background\s*==\s*\n(.*?)(?=^==[^=]|\Z)", kept)
    if not m or len(rows) < 2:
        return kept
    body = m.group(1)
    parts = re.split(r"(?m)^===\s*([^=].*?)\s*===\s*$", body)
    if len(parts) < 5:
        return kept
    lead, subs = parts[0].strip(), [(parts[i].strip(), parts[i + 1].strip()) for i in range(1, len(parts), 2)]
    # an exact name wins; a loose key counts only when it points at one row ("Phase I" and "Phase I Expansion"
    # share the loose key "1", and Power of Siberia's operating Phase I showed as cancelled, 2026-11-07)
    exact = {n.strip().lower(): r["Status"] for r in rows for n in (label(r, rows), r["SegmentName"]) if n.strip()}
    loose = {}
    for r in rows:
        for k in {_key(label(r, rows)), _key(r["SegmentName"])} - {""}:
            loose.setdefault(k, set()).add(r["ProjectID"])
    by_pid = {r["ProjectID"]: r["Status"] for r in rows}
    status = {k: by_pid[next(iter(p))] for k, p in loose.items() if len(p) == 1}
    status.update(main_line_key(rows))
    def st_of(h):
        st = exact.get(h.strip().lower()) or status.get(_key(h), "")
        if not st and _key(h):                     # "Phase II" for "Phase II Kovykta-Chayanda": a unique prefix
            hit = {next(iter(p)) for k, p in loose.items() if len(p) == 1 and k.startswith(_key(h))}
            st = by_pid[hit.pop()] if len(hit) == 1 else ""
        return st
    # only subsections that name a segment go in the table; the others ("Technical description", "Route",
    # "Ownership") stay as prose subsections after it (Baird 2026-11-07)
    seg = [(h, txt, st_of(h)) for h, txt in subs]
    rows_in = [x for x in seg if x[2]]
    other = [(h, txt) for h, txt, st in seg if not st]
    if len(rows_in) < 2:
        if other:
            pg.log.append(f"Background left as prose: fewer than two subsections name a segment ({', '.join(h for h, _ in other)})")
        return kept
    t = ['{| class="wikitable"', "!Segment", "!Status", "!Background"]
    for h, txt, st in rows_in:
        txt = re.sub(r"(?m)^====+\s*(.*?)\s*=+\s*$", "'''\\1'''", txt)
        txt = re.sub(r"(?m)^([|!])", r"<nowiki>\1</nowiki>", txt)  # a line starting | or ! would break the table
        t += ["|-", f"|{h}", f"|{STATUS_PHRASE.get(st, st)}", "|\n" + (txt or "–")]
    t.append("|}")
    if other:
        pg.log.append(f"Background: kept as prose subsections, no segment matched: {', '.join(h for h, _ in other)}")
    pg.log.append(f"Background: {len(rows_in)} segment subsections turned into a table")
    new = (lead + "\n\n" if lead else "") + "\n".join(t) + "\n\n" + "".join(f"==={h}===\n{txt}\n\n" for h, txt in other)
    return kept[:m.start(1)] + new + kept[m.end(1):]


BG_TABLE = re.compile(r"(?ms)(?:^<div class=\"gem-bgbox\">\n)?^\{\|[^\n]*\n!(?:Segment|Unit)\n!Status\n!Background\n(.*?)^\|\}(?:\n</div>)?")


def background_subsections(pg, kept):
    """Below SEG_TABLE_MIN segments the Background holds no table: one === subsection per segment (Baird 2026-11-07,
    Iroquois). A Background table an earlier run built is turned back into subsections; the status column goes,
    since the tables above carry it, and a bold-only line in a cell goes back to a ==== heading."""
    m = re.search(r"(?ms)^==\s*Background\s*==\s*\n(.*?)(?=^==[^=]|\Z)", kept)
    tm = BG_TABLE.search(m.group(1)) if m else None
    if not tm:
        return kept
    subs = []
    for part in re.split(r"(?m)^\|-\s*\n", tm.group(1))[1:]:
        cm = re.match(r"(?s)\|(?:style=\"[^\"]*\"\|)?([^\n]*)\n\|[^\n]*\n\|\n?(.*)", part)
        if not cm:
            pg.log.append(f"BACKGROUND TABLE ROW NOT PARSED, table left in place: {part[:60]!r}")
            return kept
        name = re.sub(r"<span[^>]*></span>", "", BG_LINKED.sub(r"\1", cm.group(1))).strip()
        txt = cm.group(2).strip()
        txt = re.sub(r"(?m)^'''([^'\n]+)'''\s*$", r"====\1====", txt)
        txt = re.sub(r"(?m)^<nowiki>([|!])</nowiki>", r"\1", txt)
        subs.append(f"==={name}===\n" + ("" if txt in ("", "–") else txt))
    body = m.group(1)
    new = body[:tm.start()].rstrip() + "\n\n" + "\n\n".join(subs) + "\n\n" + body[tm.end():].lstrip()
    pg.log.append(f"Background: table of {len(subs)} rows turned back into subsections (under {SEG_TABLE_MIN} segments)")
    return kept[:m.start(1)] + new.lstrip() + kept[m.end(1):]


def dormancy_into_subsection(pg, kept, rows, r, sent, rc):
    """Below SEG_TABLE_MIN: the dormancy sentence ends the segment's Background subsection, or gets one of its own."""
    text = sent + pg.cite(rc)
    m = re.search(r"(?ms)^==\s*Background\s*==\s*\n(.*?)(?=^==[^=]|\Z)", kept)
    if not m:
        kept = kept.rstrip() + ("\n\n" if kept.strip() else "") + f"==Background==\n==={label(r, rows)}===\n{text}\n"
        pg.log.append(f"{r['ProjectID']}: dormancy sentence put in a new Background subsection")
        return kept
    body = m.group(1)
    if sent.split(",")[0] in body:
        return kept   # an earlier run put it there
    find = segment_matcher(rows)
    heads = list(re.finditer(r"(?m)^===\s*([^=].*?)\s*===\s*$", body))
    hit = next((i for i, h in enumerate(heads) if find(h.group(1)) == r["ProjectID"]), None)
    if hit is None:
        body = body.rstrip() + f"\n\n==={label(r, rows)}===\n{text}\n\n"
    else:
        end = heads[hit + 1].start() if hit + 1 < len(heads) else len(body)
        body = body[:end].rstrip() + "\n\n" + text + "\n\n" + body[end:].lstrip()
    pg.log.append(f"{r['ProjectID']}: dormancy sentence put in its Background subsection")
    return kept[:m.start(1)] + body + kept[m.end(1):]


EXPANSION_HEAD = re.compile(r"(?ms)^==\s*(expansions?(?: projects?)?|expansion and extension projects?|extensions?)\s*==\s*\n(.*?)(?=^==[^=]|\Z)", re.I)
DATA_BULLET = re.compile(r"(?m)^\*+\s*(?:'''[^'\n]{1,60}?:?\s*'''|(?:operator|owners?|parent(?: company)?|(?:current |proposed )?capacity|diameter|length|cost|status|start year|proposal year|construction year|financing|associated infrastructure)\s*:).*\n?", re.I)


def segment_matcher(rows):
    """name -> ProjectID: an exact SegmentName or label first, then the loose key, then a unique loose-key prefix."""
    exact = {n.strip().lower(): r["ProjectID"] for r in rows for n in (label(r, rows), r["SegmentName"]) if n.strip()}
    loose = {}
    for r in rows:
        for k in {_key(label(r, rows)), _key(r["SegmentName"])} - {""}:
            loose.setdefault(k, set()).add(r["ProjectID"])

    def find(h):
        if h.strip().lower() in exact:
            return exact[h.strip().lower()]
        k = _key(h)
        if not k:
            return None
        if len(loose.get(k, ())) == 1:
            return next(iter(loose[k]))
        hit = {next(iter(p)) for kk, p in loose.items() if len(p) == 1 and (kk.startswith(k) or k.startswith(kk))}
        return hit.pop() if len(hit) == 1 else None
    return find


def fold_expansions(pg, kept, rows):
    """An "Expansion projects" section mixes background and project details (Baird 2026-11-07, Iroquois). Its
    data bullets (Operator, Owner, Capacity, Status ...) go, since the tables carry them; its narrative moves to
    Background, one subsection per expansion, each checked against the tracker segments. Returns (kept, removed
    text); the removed text is scanned like a replaced section, so no citation is lost."""
    m = EXPANSION_HEAD.search(kept)
    if not m:
        return kept, ""
    bullets = DATA_BULLET.findall(m.group(2))
    removed = "\n".join(bullets)
    body = DATA_BULLET.sub("", m.group(2)).strip()
    find = segment_matcher(rows)
    parts = re.split(r"(?m)^===\s*([^=].*?)\s*===\s*$", body)
    lead, subs = parts[0].strip(), [(parts[i].strip(), parts[i + 1].strip()) for i in range(1, len(parts), 2)]
    unmatched = [h for h, _ in subs if not find(h)]
    pg.log.append(f"Expansion section '{m.group(1)}': {len(subs)} subsections moved to Background, {len(bullets)} data bullets removed")
    if unmatched:
        pg.log.append(f"EXPANSION NOT IN TRACKER: {', '.join(unmatched)}")
    pg.unmatched_expansions = unmatched
    moved = ((lead + "\n\n") if lead else "") + "".join(f"==={h}===\n{t}\n\n" for h, t in subs)
    kept = (kept[:m.start()] + kept[m.end():]).strip()
    bg = re.search(r"(?ms)^==\s*Background\s*==\s*\n(.*?)(?=^==[^=]|\Z)", kept)
    if bg:
        kept = kept[:bg.end(1)].rstrip() + "\n\n" + moved.strip() + "\n\n" + kept[bg.end(1):].lstrip()
    else:
        kept = "==Background==\n" + moved.strip() + ("\n\n" + kept if kept else "")
    return kept.strip(), removed


DETAILS_HEAD = re.compile(r"(?mi)^(=+)\s*(?:project\s+)?(?:expansion\s+)?(?:project\s+)?details\s*\1\s*\n")


def drop_data_bullets(pg, kept):
    """A Background list of project data (Owner, Capacity, Length, Diameter, Status ...), often under a "Project
    expansion details" heading, goes: the tables carry those values (Baird 2026-11-09, DeRuyter). A run of two or
    more data bullets is removed, and a details heading goes too. Returns (kept, removed
    text); the removed text is scanned like a replaced section, so its citations move to Additional sources and a
    named ref reused elsewhere keeps its definition (fix_named_refs)."""
    m = re.search(r"(?ms)^==\s*Background\s*==\s*\n(.*?)(?=^==[^=]|\Z)", kept)
    if not m:
        return kept, ""
    body, removed = m.group(1), []

    def run(mm):
        if len(DATA_BULLET.findall(mm.group(0))) < 2:
            return mm.group(0)
        removed.append(mm.group(0))
        return ""
    body = re.sub(r"(?m)(?:^\*[^\n]*(?:\n|\Z))+", run, body)
    if not removed:
        return kept, ""
    # a "Project expansion details" heading goes too; any prose under it joins the subsection above
    body = DETAILS_HEAD.sub("", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    pg.log.append(f"Background: {len(removed)} project-data bullet list(s) removed, citations kept as Additional sources")
    return kept[:m.start(1)] + body + kept[m.end(1):], "\n".join(removed)


MEDIA_OPEN = re.compile(r"\[\[\s*(?:File|Image|Media)\s*:", re.I)
MEDIA_BLOCK = re.compile(r"<gallery\b.*?</gallery>|<video\b.*?</video>|<embedvideo\b.*?</embedvideo>|<youtube\b.*?</youtube>"
                         r"|\{\{\s*#(?:ev|evt|evu|evp|evl)\s*:.*?\}\}|\{\{\s*EmbedVideo\b.*?\}\}", re.I | re.S)
OWN_MEDIA = re.compile(r"Route shape P\d+\.svg", re.I)   # the generator's own route-shape pictures


def find_media(txt):
    """[(start, end, markup)] for every image, gallery or video in txt, file links matched with their nested
    [[...]] captions."""
    out = [(m.start(), m.end(), m.group(0)) for m in MEDIA_BLOCK.finditer(txt)]
    for m in MEDIA_OPEN.finditer(txt):
        if any(a <= m.start() < b for a, b, _ in out):
            continue
        depth, i = 0, m.start()
        while i < len(txt) - 1:
            if txt.startswith("[[", i):
                depth += 1; i += 2; continue
            if txt.startswith("]]", i):
                depth -= 1; i += 2
                if depth == 0:
                    break
                continue
            i += 1
        out.append((m.start(), i, txt[m.start():i]))
    return sorted(o for o in out if not OWN_MEDIA.search(o[2]))


def media_key(markup):
    m = re.match(r"\[\[\s*(?:File|Image|Media)\s*:\s*([^|\]]+)", markup, re.I)
    return re.sub(r"[\s_]+", " ", m.group(1)).strip().lower() if m else re.sub(r"\s+", " ", markup)


def gather_media(pg, kept, replaced, extra_ar):
    """Images, galleries and videos a person put anywhere but Background (above the map, in the lead, in a rebuilt
    section, under Articles and resources) move to the top of Background (Baird 2026-11-08, China–Russia East).
    Media already in Background stays where it is. Returns (kept, extra_ar)."""
    have = {media_key(t) for _, _, t in find_media(kept)}
    moved = []
    for _, _, t in find_media(replaced):
        k = media_key(t)
        if k not in have:
            have.add(k); moved.append(t.strip())
    for a, b, t in reversed(find_media(extra_ar)):
        extra_ar = extra_ar[:a] + extra_ar[b:]
        k = media_key(t)
        if k not in have:
            have.add(k); moved.insert(0, t.strip())
    if not moved:
        return kept, extra_ar
    pg.log.append(f"{len(moved)} images or videos moved to the top of Background")
    block = "\n".join(moved)
    secs = split_sections(kept)
    i = next((k for k, (h, _, _) in enumerate(secs) if h and h.lower() == "background"), None)
    if i is None:
        secs.append(("Background", 2, "\n" + block + "\n"))
    else:
        h, _, body = secs[i]
        secs[i] = (h, 2, "\n" + block + "\n\n" + body.strip() + "\n")
    parts = [secs[0][2].strip()] if secs[0][2].strip() else []
    parts += [f"=={h}==\n{b.strip()}" for h, _, b in secs[1:]]
    return "\n\n".join(parts), extra_ar


def fold_other_sections(pg, kept):
    """A page has four sections, Location, Project details, Ownership and Background (Baird 2026-11-07, Kern River;
    no Other sources section, Los Ramones). Any other kept section (Environmental impact, Opposition, Financing ...)
    moves into Background as a subsection, its own subsections one level down, in page order."""
    secs = split_sections(kept)
    bg, moved = [], []
    for h, _, body in secs[1:]:
        hl = h.lower()
        if hl == "background":
            bg.append(body.strip())
        else:
            moved.append((h, re.sub(r"(?m)^(===+)([^=].*?[^=])(===+)\s*$", r"=\1\2\3=", body.strip())))
    if not moved:
        return kept
    pg.log.append(f"sections moved into Background: {', '.join(h for h, _ in moved)}")
    lead = secs[0][2].strip()
    if lead:   # text above the first heading in kept: keep it at the top of Background
        bg.insert(0, lead)
    body = "\n\n".join([b for b in bg if b] + [f"==={h}===\n{t}" for h, t in moved if t])
    return "==Background==\n" + body


BG_LINKED = re.compile(r'<span id="bg-P\d+" class="gem-anchor"></span>(?:<span title="[^"]*">)?\[\[#row-P\d+\|(.*?)\]\](?:</span>)?')


def link_background(pg, kept, rows):
    """On a tabbed page, each Background table row whose segment name matches a tracker row (same name key as
    background_table) gets an anchor and a link up to that segment's row in the segment table; the segment
    table links back down (pg.bg). Re-running on an already linked page relinks from the plain name."""
    m = re.search(r"(?ms)^==\s*Background\s*==\s*\n(.*?)(?=^==[^=]|\Z)", kept)
    if not m:
        return kept
    keys = {}
    for r in rows:
        for k in {_key(label(r, rows)), _key(r["SegmentName"])} - {""}:
            keys.setdefault(k, set()).add(r["ProjectID"])
    for k, pid in main_line_key(rows, pid=True).items():
        keys.setdefault(k, set()).add(pid)
    unmatched, used = [], set()

    by_pid = {r["ProjectID"]: r for r in rows}

    def cell(mo):
        pre, name = mo.group(1), BG_LINKED.sub(r"\1", mo.group(2)).strip()
        # a row already linked to a segment stays with it under that segment's current name, so a renamed
        # segment (SYSTEM/NETWORK INFO to Main Line on Northwest, 2026-11-09) is not left as a stray row
        old = re.search(r'id="bg-(P\d+)"', mo.group(2))
        if old and old.group(1) in by_pid and old.group(1) not in used:
            pid = old.group(1); used.add(pid); name = label(by_pid[pid], rows)
            return f'{pre}<span id="bg-{pid}" class="gem-anchor"></span><span title="Click for project details">[[#row-{pid}|{name}]]</span>'
        pids = keys.get(_key(name), set())
        if len(pids) != 1 or next(iter(pids)) in used:
            unmatched.append(name)
            return pre + name
        pid = pids.pop(); used.add(pid)
        return f'{pre}<span id="bg-{pid}" class="gem-anchor"></span><span title="Click for project details">[[#row-{pid}|{name}]]</span>'

    # the first cell after each row separator: "|name" or "|style=...|name"
    body = re.sub(r'(?m)(^\|-\s*\n\|(?:[^|\n]*?=\s*"[^"\n]*"\s*\|)?)([^\n]+)$', cell, m.group(1))
    # the Background table scrolls in its own box with its header fixed, like the segment table (Baird 2026-11-06)
    body = body.replace('\n<div class="gem-segtail"></div>', "")  # the blank spacer an earlier version put under the table
    if 'class="gem-bgbox"' not in body:
        body = re.sub(r"(?ms)^(\{\|[^\n]*\n!Segment\n.*?^\|\})", r'<div class="gem-bgbox">\n\1\n</div>', body, count=1)
    pg.bg |= used
    pg.log.append(f"Background links: {len(used)} rows linked to the segment table" + (f"; no single segment matched {', '.join(unmatched)}" if unmatched else ""))
    return kept[:m.start(1)] + body + kept[m.end(1):]


def blank_background_rows(pg, kept, rows):
    """On a tabbed page every segment has a row in the Background table (Baird 2026-11-07, Kern River): a segment
    with no background text gets a row with the Background cell left blank. Each missing row goes before the next
    segment, in tracker order, that already has a row; run after link_background, so the row is linked both ways."""
    tm = re.search(r"(?ms)^\{\|[^\n]*\n!Segment\n!Status\n!Background\n(.*?)^\|\}", kept)
    if not tm:
        return kept
    parts = re.split(r"(?m)(?=^\|-\s*$)", tm.group(1))
    head, rws = parts[0], parts[1:]
    ordered = list(rows)
    missing = [r for r in ordered if r["ProjectID"] not in pg.bg and not any(f'id="bg-{r["ProjectID"]}"' in w for w in rws)]
    if not missing:
        return kept
    for r in missing:
        pid, name = r["ProjectID"], label(r, rows)
        row = (f'|-\n|<span id="bg-{pid}" class="gem-anchor"></span><span title="Click for project details">[[#row-{pid}|{name}]]</span>\n'
               f'|{STATUS_PHRASE.get(r["Status"], r["Status"])}\n|\n')
        later = {x["ProjectID"] for x in ordered[ordered.index(r) + 1:]}
        at = next((i for i, w in enumerate(rws) if any(f'id="bg-{q}"' in w for q in later)), len(rws))
        rws.insert(at, row)
        pg.bg.add(pid)
    pg.log.append(f"Background: {len(missing)} segments with no background text added as blank rows ({', '.join(r['ProjectID'] for r in missing)})")
    return kept[:tm.start(1)] + head + "".join(w if w.endswith("\n") else w + "\n" for w in rws) + kept[tm.end(1):]


BG_SECTION = re.compile(r"(?ms)^==\s*Background\s*==\s*\n(.*?)(?=^==[^=]|\Z)")


def _bg_insert_at(body):
    """Where a new Background entry goes: before the Additional sources line, else at the end."""
    m = ADDITIONAL.search(body)
    return m.start() if m else len(body)


def ensure_background(pg, kept, rows):
    """Every page has a Background, and every segment of a multi-segment page has its own entry in it, empty when
    nothing is written yet, so others can fill it in (Baird 2026-11-08). A tabbed page gets an empty Background
    table when it has none (blank_background_rows then gives every segment its row); below SEG_TABLE_MIN each
    segment with no === subsection gets an empty one, in tracker order. A one-segment page gets the heading only."""
    m = BG_SECTION.search(kept)
    if not m:
        kept = kept.rstrip() + ("\n\n" if kept.strip() else "") + "==Background==\n"
        m = BG_SECTION.search(kept)
        pg.log.append("Background: empty section added")
    if len(rows) < 2:
        return kept
    body = m.group(1)
    if len(rows) >= SEG_TABLE_MIN:
        if re.search(r"(?m)^\{\|[^\n]*\n!(?:Segment|Unit)\n!Status\n!Background\n", body):
            return kept
        # after the prose lead, before any subsection and the Additional sources line
        h = re.search(r"(?m)^===\s*[^=]", body)
        at = min(h.start() if h else len(body), _bg_insert_at(body))
        tbl = '{| class="wikitable"\n!Segment\n!Status\n!Background\n|}\n\n'
        body = body[:at].rstrip() + ("\n\n" if body[:at].strip() else "") + tbl + body[at:].lstrip()
        pg.log.append("Background: empty segment table added")
        return kept[:m.start(1)] + body + kept[m.end(1):]
    find = segment_matcher(rows)
    heads = [(hm, find(hm.group(1))) for hm in re.finditer(r"(?m)^===\s*([^=].*?)\s*===\s*$", body)]
    have = {pid for _, pid in heads if pid}
    missing = [r for r in rows if r["ProjectID"] not in have]
    if not missing:
        return kept
    for r in missing:
        later = [x["ProjectID"] for x in rows[rows.index(r) + 1:]]
        heads = [(hm, find(hm.group(1))) for hm in re.finditer(r"(?m)^===\s*([^=].*?)\s*===\s*$", body)]
        nxt = next((hm.start() for hm, pid in heads if pid in later), None)
        at = nxt if nxt is not None else _bg_insert_at(body)
        body = body[:at].rstrip() + ("\n\n" if body[:at].strip() else "") + f"==={label(r, rows)}===\n\n" + body[at:].lstrip()
    pg.log.append(f"Background: {len(missing)} segments with no background text added as empty subsections ({', '.join(r['ProjectID'] for r in missing)})")
    return kept[:m.start(1)] + body.rstrip() + "\n\n" + kept[m.end(1):]


def dormancy_into_background(pg, kept, rows):
    """Put each segment's dormancy sentence at the end of its row in the Background table, or add a
    row for the segment when it has none. Skipped when the sentence is already there (a re-run). Below
    SEG_TABLE_MIN segments there is no table: the sentence goes in the segment's subsection instead."""
    if len(rows) == 1:
        for r, sent, rc in pg.dorm:   # one-row page: the sentence ends the Background
            m = re.search(r"(?ms)^==\s*Background\s*==\s*\n(.*?)(?=^==[^=]|^<!---|\Z)", kept)
            text = sent + pg.cite(rc)
            if m and sent.split(",")[0] in m.group(1):
                continue
            if m:
                body = m.group(1).rstrip()
                tail = re.search(r"(?s)\n+Additional sources:.*\Z", body)   # before an "Additional sources" line
                at = tail.start() if tail else len(body)
                kept = kept[:m.start(1)] + body[:at].rstrip() + "\n\n" + text + body[at:] + "\n" + kept[m.end(1):]
            else:
                kept = kept.rstrip() + ("\n\n" if kept.strip() else "") + f"==Background==\n{text}\n"
            pg.log.append(f"{r['ProjectID']}: dormancy sentence put at the end of the Background")
        return kept
    if len(rows) < SEG_TABLE_MIN:
        for r, sent, rc in pg.dorm:
            kept = dormancy_into_subsection(pg, kept, rows, r, sent, rc)
        return kept
    for r, sent, rc in pg.dorm:
        tm = re.search(r"(?ms)^\{\|[^\n]*\n!Segment\n!Status\n!Background\n(.*?)^\|\}", kept)
        if not tm:
            pg.log.append(f"{r['ProjectID']}: no Background table; dormancy sentence left out of the page")
            continue
        text = sent + pg.cite(rc)
        rows_iter = list(re.finditer(r"(?ms)^\|-\n\|(?:style=\"[^\"]*\"\|)?([^\n]+)\n\|[^\n]*\n\|\n(.*?)(?=^\|-|^\|\}|\Z)", tm.group(1)))   # \Z: the group stops before "|}", so the last row ends there
        # the segment's row: the one linked to it, else the one with its name
        hit = next((m for m in rows_iter if f'id="bg-{r["ProjectID"]}"' in m.group(1)), None) \
            or next((m for m in rows_iter if _key(BG_LINKED.sub(r"\1", m.group(1))) == _key(label(r, rows))), None)
        base = tm.start(1)
        if hit and sent.split(",")[0] in hit.group(2):
            # an earlier run already put it in this segment's entry; drop a stand-alone row an older run added for it
            orphan = re.compile(r'(?m)^\|-\n\|(?:style="[^"]*"\|)?' + re.escape(label(r, rows)) + r'\n\|[^\n]*\n\|\n' + re.escape(sent) + r'(?:<ref[^\n]*)?\n')
            if not hit.group(1).endswith(label(r, rows)):
                kept = kept[:base] + orphan.sub("", kept[base:tm.end(1)], count=1) + kept[tm.end(1):]
            continue
        if not hit and text in tm.group(1):
            continue  # a row an earlier run added
        if hit:
            end = base + hit.end(2)
            cell = kept[base + hit.start(2):end].rstrip("\n")
            kept = kept[:base + hit.start(2)] + cell + "\n\n" + text + "\n" + kept[end:]
        else:
            row = f"|-\n|{label(r, rows)}\n|{STATUS_PHRASE.get(r['Status'], r['Status'])}\n|\n{text}\n"
            kept = kept[:tm.end(1)] + row + kept[tm.end(1):]
        pg.log.append(f"{r['ProjectID']}: dormancy sentence put in its Background entry")
    return dedupe_background(kept)


def color_background_status(pg, kept):
    """Put the map-colored status dot before each status in the Background table; a re-run replaces the old dot."""
    tm = re.search(r"(?ms)^\{\|[^\n]*\n!Segment\n!Status\n!Background\n(.*?)^\|\}", kept)
    if not tm:
        return kept
    word = {v: k for k, v in STATUS_PHRASE.items()}

    def dot(mo):
        st = DOT_RE.sub("", mo.group(2)).strip()
        return mo.group(1) + (status_dot(pg, word.get(st, st)) + st if st and st != "–" else st)

    body = re.sub(r"(?m)(^\|-\s*\n\|[^\n]*\n\|)([^\n]*)$", dot, tm.group(1))
    return kept[:tm.start(1)] + body + kept[tm.end(1):]


def dedupe_background(kept):
    """Drop a Background table row that repeats an earlier row word for word (an older run could add one twice)."""
    tm = re.search(r"(?ms)^\{\|[^\n]*\n!Segment\n!Status\n!Background\n(.*?)^\|\}", kept)
    if not tm:
        return kept
    parts = re.split(r"(?m)(?=^\|-\s*$)", tm.group(1))
    seen, out = set(), []
    for part in parts:
        key = BG_LINKED.sub(r"\1", part).strip()
        if key.startswith("|-") and key in seen:
            continue
        seen.add(key); out.append(part)
    return kept[:tm.start(1)] + "".join(out) + kept[tm.end(1):]


TABLE_FONT = "85%"      # table text a step smaller than the page body
UNIT_GRAY = "#eaecf0"     # the wikitable header-cell gray, on the unit-name cells
HEAD_GRAY = "#d4d8de"     # one step darker, on the column-title cells
SHADES = (UNIT_GRAY, HEAD_GRAY)


BG_HEAD = r"(?ms)^(\{\|[^\n]*\n)%s(!Segment\n!Status\n!Background\n)(.*?)^\|\}"


def number_background(text):
    """A running number in the Background table's first column, like the segment table's (Baird 2026-11-08).
    It is added last and stripped again by strip_background_numbers when a live page is read back in."""
    def f(m):
        n = [0]

        def row(_):
            n[0] += 1
            return f'|-\n|{n[0]}\n|style="background-color:{UNIT_GRAY}"|'
        return m.group(1) + "!#\n" + m.group(2) + re.sub(r"(?m)^\|-\n\|", row, m.group(3)) + "|}"
    return re.sub(BG_HEAD % "", f, text)


def strip_background_numbers(text):
    return re.sub(BG_HEAD % r"!#\n", lambda m: m.group(1) + m.group(2) + re.sub(r"(?m)^\|-\n\|\d+\n\|", "|-\n|", m.group(3)) + "|}", text)


def unshade(text):
    """Strip the shading this generator adds, so kept text is matched and re-shaded the same way."""
    alt = "|".join(c.lstrip("#") for c in SHADES)
    text = re.sub(rf'(?m)^([|!])style="background-color:#(?:{alt})"\|', r"\1", text)
    return re.sub(rf' style="background-color:#(?:{alt})"', "", text)


def shade_first_column(text):
    """In every wikitable: column-title cells get HEAD_GRAY, and the unit-name cell of each body row
    (its first cell that is not a route-shape image) gets UNIT_GRAY. A cell already styled is left alone."""
    out, in_tab, want, skip, shape_col, first_head = [], False, False, False, False, False
    for line in text.split("\n"):
        if line.startswith('{| class="wikitable'):
            in_tab, shape_col, first_head = True, False, True
            if "style=" not in line:
                line = re.sub(r'"$', f'" style="font-size:{TABLE_FONT}"', line.rstrip())
        elif line.startswith("|}"):
            in_tab = want = False
        elif in_tab and line.startswith("|-"):
            want, skip = True, shape_col
        elif in_tab and line.startswith("!") and first_head and line.endswith("|Route"):
            shape_col, first_head = True, False   # the route-shape column: body cells start one later
            if "style=" not in line:
                line = line.replace('|Route', f' style="background-color:{HEAD_GRAY}"|Route', 1)
        elif in_tab and line.startswith("!") and "style=" not in line.split("|")[0]:
            first_head = False
            m = re.match(r'!([^|\[]*=[^|\[]*)\|(.*)', line)
            line = f'!{m.group(1)} style="background-color:{HEAD_GRAY}"|{m.group(2)}' if m else f'!style="background-color:{HEAD_GRAY}"|{line[1:]}'
        elif in_tab and want and line.startswith("|") and not line.startswith(("|+", "|}")):
            cell = line[1:]
            if cell.startswith("colspan"):
                want = skip = False   # a footnote row
            elif skip:
                skip = False   # the route-shape cell (an image or a dash)
            else:
                if not re.match(r"\s*style=", cell):
                    line = f'|style="background-color:{UNIT_GRAY}"|{cell}'
                want = False
        out.append(line)
    return "\n".join(out)


# ---------- Background vs lead: status check (Baird 2026-11-09, Delmarva) ----------

# a kept Background sentence that states a status: "is considered to be shelved", "remains on hold", "was cancelled"
_ST = r"(shelved|cancell?ed|on hold|operating|operational|in operation|in service|under construction|proposed|retired|mothballed|idled?|abandoned)"
_CLAIM_NOW = re.compile(r"\b(?:considered|presumed|deemed|classified|listed)\s+(?:to\s+be\s+|as\s+)?(?:being\s+)?" + _ST + r"\b"
                        r"|\b(?:is|are|remains?)\s+(?:now\s+|currently\s+|still\s+|officially\s+)?(?:an?\s+)?" + _ST + r"\b", re.I)
_CLAIM_PAST = re.compile(r"\b(?:was|were|has\s+been|have\s+been)\s+(?:officially\s+|formally\s+)?"
                         r"(shelved|cancell?ed|retired|mothballed|abandoned|placed\s+in(?:to)?\s+service|put\s+in(?:to)?\s+service)\b", re.I)
_CANON = {"canceled": "cancelled", "on hold": "shelved", "operational": "operating", "in operation": "operating",
          "in service": "operating", "under construction": "construction", "idle": "idled", "abandoned": "retired"}
_SAME = {("mothballed", "idled"), ("idled", "mothballed")}


def _canon(w):
    w = re.sub(r"\s+", " ", w.lower())
    return "operating" if re.match(r"(placed|put) in", w) else _CANON.get(w, w)


def _claims(text):
    """(status, sentence, present-tense?) for every status claim in prose, refs, comments and markup stripped."""
    t = re.sub(r"<ref[^>]*/>", "", text)
    t = re.sub(r"(?s)<ref[^>]*>.*?</ref>|<!--.*?-->", "", t)
    t = re.sub(r"(?m)^Additional sources:.*$", "", t)
    out = []
    for sent in re.split(r"(?<=[.!?])\s+|\n+", t):
        if not sent.strip() or sent.lstrip()[:1] in "|{!=":
            continue
        for m in sorted(list(_CLAIM_NOW.finditer(sent)) + list(_CLAIM_PAST.finditer(sent)), key=lambda m: m.start()):
            w = next(g for g in m.groups() if g)
            out.append((_canon(w), sent.strip(), m.re is _CLAIM_NOW))
    return out


def status_conflicts(pg, kept, rows):
    """A Background that says one status while the lead says another is held, never saved (Baird 2026-11-09:
    Delmarva's lead said cancelled, its Background said shelved). Each segment's Background text (the whole
    Background on a one-row page, its === subsection, or its row of the Background table) is read for status
    claims. A present-tense or "considered" claim that differs from the tracker status is a conflict wherever it
    sits; a past-tense one ("was shelved") only when it is the last claim in that text. Returns the conflicts."""
    m = re.search(r"(?ms)^==\s*Background\s*==\s*\n(.*?)(?=^==[^=]|\Z)", kept)
    if not m:
        return []
    bg = m.group(1)
    units = []   # (row, text)
    if len(rows) == 1:
        units.append((rows[0], bg))
    else:
        names = {_key(label(r, rows)): r for r in rows} | {_key(r["SegmentName"]): r for r in rows if r["SegmentName"]}
        for h, body in re.findall(r"(?ms)^===\s*(.*?)\s*===\s*$(.*?)(?=^===?[^=]|\Z)", bg):
            r = names.get(_key(BG_LINKED.sub(r"\1", h)))
            if r:
                units.append((r, body))
        tm = re.search(r"(?ms)^\{\|[^\n]*\n(?:!#\n)?!Segment\n!Status\n!Background\n(.*?)^\|\}", bg)
        if tm:
            for part in re.split(r"(?m)^\|-\s*\n", tm.group(1))[1:]:
                pid = re.search(r'id="bg-(P\d+)"', part)
                r = next((q for q in rows if pid and q["ProjectID"] == pid.group(1)), None)
                if r:
                    units.append((r, "\n".join(part.split("\n")[2:])))
    out = []
    for r, text in units:
        st = r["Status"]
        cl = _claims(text)
        for i, (c, sent, now) in enumerate(cl):
            if c == st or (c, st) in _SAME or (c == "proposed" and st in ("shelved", "cancelled")):
                continue
            if now or i == len(cl) - 1:
                out.append(f"{r['ProjectID']}: tracker status {st}, Background says {c}: {sent[:160]}")
    for o in out:
        pg.log.append(f"STATUS CONFLICT between the lead and Background, {o}")
    return out


_WIKILINK = re.compile(r"\[\[([^\]\|#:]+)(?:#[^\]\|]*)?(?:\|([^\]]*))?\]\]")
_LINK_CACHE = {}


_EMPTY_SUB = re.compile(r"^(===+)([^=\n]+)\1[ \t]*\n(?:[ \t]*\n)*(?=(?:==)|\Z|<!--)", re.M)


def drop_empty_subsections(pg, kept):
    """A Background subsection heading with nothing under it reads as a broken page (Baird 2026-11-09)."""
    def fix(m):
        nxt = re.match(r"=+", kept[m.end():])
        if nxt and len(nxt.group(0)) > len(m.group(1)):   # a deeper heading follows: not empty
            return m.group(0)
        pg.log.append(f"empty Background subsection removed: {m.group(2).strip()}")
        return ""
    return _EMPTY_SUB.sub(fix, kept)


def unlink_missing(pg, kept):
    """Turn [[links]] to gem.wiki pages that do not exist into plain text (Baird 2026-11-09, Arkoma).
    A red link in kept text reads as a broken page; the label stays, only the brackets go."""
    targets = {m.group(1).strip() for m in _WIKILINK.finditer(kept)} - set(_LINK_CACHE)
    if targets:
        try:
            s = _LINK_CACHE.setdefault("_session", GW.session())
            ts = sorted(targets)
            for i in range(0, len(ts), 40):
                d = GW.get(s, action="query", titles="|".join(ts[i:i + 40]))["query"]
                norm = {n["from"]: n["to"] for n in d.get("normalized", [])}
                pages = d["pages"].values() if isinstance(d["pages"], dict) else d["pages"]
                have = {p["title"] for p in pages if "missing" not in p and "invalid" not in p}
                for t in ts[i:i + 40]:
                    _LINK_CACHE[t] = norm.get(t, t) in have
        except Exception as e:  # never block a build on the check; say it did not run
            pg.log.append(f"LINK CHECK NOT RUN ({type(e).__name__}); red links in kept text not looked for")
            return kept

    def fix(m):
        t = m.group(1).strip()
        if _LINK_CACHE.get(t, True):
            return m.group(0)
        pg.log.append(f"unlinked a link to a page that does not exist: [[{t}]]")
        return (m.group(2) or m.group(1)).strip()
    return _WIKILINK.sub(fix, kept)


def build(name, rows, owners, live, tracker):
    pg = Page(name, tracker)
    rows = order(rows)
    kept, extra_ar, replaced = preserved(pg, live)
    kept = strip_background_numbers(unshade(kept))
    kept, gone = fold_expansions(pg, kept, rows)
    kept, gone2 = drop_data_bullets(pg, kept)
    replaced = replaced + "\n\n" + gone + "\n\n" + gone2
    kept, old_other = pop_other_sources(pg, kept)
    kept = fold_other_sections(pg, kept)
    # a Background table only on a tabbed page; below SEG_TABLE_MIN it is one subsection per segment (Baird 2026-11-07)
    if len(rows) >= SEG_TABLE_MIN:
        kept = background_table(pg, kept, order(rows))
        kept = ensure_background(pg, kept, rows)
        kept = link_background(pg, kept, rows)
        kept = blank_background_rows(pg, kept, rows)
    else:
        kept = background_subsections(pg, kept)
        kept = ensure_background(pg, kept, rows)
    # a Background table built on the 2026-11-06 run says "Unit"; the row label is "Segment" (Baird 2026-11-06)
    kept = kept.replace("!Unit\n!Status\n!Background", "!Segment\n!Status\n!Background")
    seed_url_names(pg, kept)
    # names the kept text defines are cited bare by the tables, never redefined
    pg.defined |= {m.group(1).strip() for m in NAMED_DEF.finditer(kept)}
    tab = Counter()
    # every Chinese pipeline page carries, after its opening paragraph, a pointer to the page that explains the groupings (Baird 2026-11-08)
    china = [CHINA_SEE_ALL, ""] if tracker == "gas" and any("China" in (r.get("Countries/Areas") or "").split(", ") or r.get("StartCountryOrArea") == "China" for r in rows) else []
    head = [name, "", f"<!---\n\t{COMMENT1}\n-->", NAVBAR[tracker], intro(pg, rows, tracker), ""] + china
    tabbed = len(rows) >= SEG_TABLE_MIN
    if tabbed:   # one tabbed segment table instead of the five separate tables (Baird 2026-11-06)
        body = location(pg, rows, tab, tabbed=True) + "\n\n==Project details==\n" + segment_table(pg, rows, owners)
    else:
        body = location(pg, rows, tab) + "\n\n" + details(pg, rows, tab) + "\n\n" + ownership(pg, rows, owners, tab)   # Ownership is Table 5 inside Project details
    gen = "\n".join(head) + "\n" + body + "\n"
    # the generated part defines its refs before kept text uses them; named refs the kept text
    # defines itself are reused above
    pg.defined |= {m.group(1).strip() for m in NAMED_DEF.finditer(kept)}
    kept = dormancy_into_background(pg, kept, rows)
    kept = unlink_missing(pg, kept)
    kept = drop_empty_subsections(pg, kept)
    pg.status_conflicts = status_conflicts(pg, kept, rows)
    kept = color_background_status(pg, kept)
    kept = fix_named_refs(pg, kept, live, gen)
    kept, extra_ar = gather_media(pg, kept, replaced, extra_ar)
    # in Background, the human-kept zone, so the data team's generator also keeps them; never an Other sources section
    kept = add_sources(pg, kept, old_other + lost_refs(pg, replaced, gen + kept + extra_ar), gen + kept + extra_ar)
    # an Additional sources line right under a Background table gets an empty line above it, or it renders flush
    # against the table (Baird 2026-11-08); the extra blank line renders as <br />
    kept = re.sub(r"(?m)^(\|\}|</div>)\n+(?=Additional sources:)", r"\1\n\n\n", kept)
    word, link = TRACKER_LINK[tracker]
    # no categories on a page; category lines in kept text are dropped too (Baird 2026-11-08)
    strip_cat = lambda t: re.sub(r"\n*\[\[\s*Category\s*:[^\]]+\]\]", "", t).strip()
    kept, extra_ar = strip_cat(kept), strip_cat(extra_ar)
    extra_ar = "\n\n".join(b for b in re.split(r"\n\n(?====)", extra_ar) if b.strip() and "\n" in b.strip())
    tail = ["==Articles and resources==", "", "===References===", "<references />", ""]
    if extra_ar:
        tail += [extra_ar, ""]
    tail += ["===Additional data===",
             f"To access additional data, including an interactive map of {word} pipelines, a downloadable dataset, and summary data, please visit the {link} on the Global Energy Monitor website.",
             ]
    text = gen + f"<!---\n\t{COMMENT2}\n-->\n" + (kept + "\n" if kept else "") + f"<!---\n\t{COMMENT3}\n-->\n" + "\n".join(tail) + "\n"
    text = B.sentence_case_headings(shade_first_column(number_background(text)))
    if not kept:
        text += "\n__NOTOC__\n"
    return text, pg


def page_body(text):
    """The wiki text to save: the .txt minus the page-name line and blank line GEMwiki puts first. Saving the .txt
    as it stands prints the name as a stray first line above the intro (Transcontinental and Ruby, 2026-11-06)."""
    first, _, rest = text.partition("\n")
    return rest.lstrip("\n")


def render(s, title, text):
    body = page_body(text)
    d = GW.post(s, action="parse", title=title, text=body, contentmodel="wikitext", prop="text|headhtml",
                disablelimitreport=1, pst=1)
    t = d["parse"]["text"]
    html = t["*"] if isinstance(t, dict) else t
    errs = re.findall(r'<span class="cite-error">(.*?)</span>', html, re.S)
    return html, (lambda h: h["*"] if isinstance(h, dict) else h or "")(d["parse"].get("headhtml")), [re.sub("<[^>]+>", "", e)[:160] for e in errs]


def upload_shapes(s, folder, page):
    """Upload each route-shape SVG in folder/shapes, skipping files whose bytes the wiki already has."""
    done = []
    d = os.path.join(folder, "shapes")
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        data = open(os.path.join(d, f), "rb").read()
        info = GW.get(s, action="query", titles="File:" + f, prop="imageinfo", iiprop="sha1")
        pgs = info["query"]["pages"]
        ii = next(iter(pgs.values())).get("imageinfo") if isinstance(pgs, dict) else (pgs[0].get("imageinfo"))
        if ii and ii[0].get("sha1") == hashlib.sha1(data).hexdigest():
            continue
        GW.throttle()
        r = s.post(GW.API, data={"action": "upload", "filename": f, "format": "json", "ignorewarnings": 1,
                                 "comment": f"route shape for [[{page}]]",
                                 "text": f"Route shape of one segment of [[{page}]], drawn from the pipeline's route line with no map background.",
                                 "token": GW.csrf_token(s)},
                   files={"file": (f, data, "image/svg+xml")}).json()
        if r.get("upload", {}).get("result") != "Success":
            raise RuntimeError(f"{f}: {r}")
        done.append(f)
    return done


def ensure_styles(s):
    """Save SEG_CSS to Template:Segment table/styles.css and MAP_CSS to Template:Pipeline map/styles.css when the
    live copy differs (TemplateStyles gives a Template-namespace .css page the sanitized-css content model itself).
    Returns what happened, one line per stylesheet."""
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import wiki_save
    out = []
    for page, css in ((STYLES_PAGE, SEG_CSS), (MAP_STYLES_PAGE, MAP_CSS)):
        title = "Template:" + page
        try:
            live = GW.page_text(s, title) or ""
        except GW.WikiError:   # not created yet
            live = ""
        if live.strip() == css.strip():
            out.append(f"{title}: unchanged")
            continue
        wiki_save.save(s, title, text=css, summary="pipeline page stylesheet from generate_pages.py")
        info = GW.get(s, action="query", titles=title, prop="info")["query"]["pages"]
        pg = next(iter(info.values())) if isinstance(info, dict) else info[0]
        model = pg.get("contentmodel")
        if model != "sanitized-css":
            raise RuntimeError(f"{title} saved with content model {model!r}, not sanitized-css; fix with action=changecontentmodel")
        out.append(f"{title}: saved ({'created' if not live else 'updated'}, content model sanitized-css)")
    return "\n".join(out)


def oil_columns(df):
    """Give the oil tab the gas tab's column names where the two differ, so the page code reads one schema:
    oil keeps separate start and end location refs (joined into `Location [ref]`, start first, no repeats)
    and one Cost column (read as the segment cost; oil has no project-level cost). Oil has no pressure.
    Oil routes live in the routes repo's liquid-pipelines folder, not gas-pipelines."""
    B.ROUTES = B.ROUTES.replace("/gas-pipelines/", "/liquid-pipelines/")
    def join(a, b):
        seen = []
        for u in B.urls(a) + B.urls(b):
            if u not in seen:
                seen.append(u)
        return ", ".join(seen)
    df["Location [ref]"] = [join(a, b) for a, b in zip(df["StartLocation [ref]"], df["EndLocation [ref]"])]
    df["SegmentCost"], df["SegmentCostUnits"], df["SegmentCost [ref]"] = df["Cost"], df["CostUnits"], df["Cost [ref]"]
    for c in ("ProjectLevelCost", "ProjectLevelCostUnits", "ProjectLevelCost [ref]"):
        df[c] = ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pages", nargs="*")
    ap.add_argument("--tracker", default="gas", choices=["gas", "oil"])
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--save", action="store_true", help="upload the route shapes and save each page via wiki_save (page-name line dropped)")
    ap.add_argument("--allow-status-conflicts", action="store_true", help="save a page even when its Background states a status other than the tracker's (the conflict is still logged)")
    ap.add_argument("--push-styles", action="store_true", help="save the tabbed-table and map-popup stylesheet pages on the wiki if they differ")
    ap.add_argument("--pages-file", help="a text file with one page name per line, added to the page names given")
    ap.add_argument("--resume", action="store_true", help="skip pages already in --out's refs_ledger.json and append to its report")
    ap.add_argument("--rate", type=float, default=3.0, help="gem.wiki requests per second for this run (the client's ceiling is 5)")
    a = ap.parse_args()
    GW.MAX_CALLS_PER_SECOND = min(a.rate, GW.MAX_CALLS_PER_SECOND)
    if a.pages_file:
        a.pages += [l.strip() for l in open(a.pages_file) if l.strip() and not l.startswith("#")]
    if a.push_styles:
        print(ensure_styles(GW.session(login=True)))
        if not a.pages:
            return
    elif not a.pages:
        ap.error("no pages given")
    df = C.load(a.tracker)
    if a.tracker == "oil":
        oil_columns(df)
    df["page"] = df["Wiki"].map(C.page_name)
    B.fill_unknown_parents(df)
    own = C.load("owners").drop_duplicates("ProjectID").set_index("ProjectID")
    owners = {pid: row.to_dict() for pid, row in own.iterrows()}
    out = a.out or os.path.join(C.OUT, "samples", time.strftime("%Y%m%d_%H%M"))
    os.makedirs(out, exist_ok=True)
    s = GW.session()
    report = [f"# Sample pages, {time.strftime('%Y-%m-%d %H:%M')}", "", f"Snapshot: `{os.path.basename(df.attrs['path'])}`", ""]
    ledger = {}   # page -> what happened to the live page's citations (refs_ledger.json)
    if a.resume and os.path.exists(os.path.join(out, "refs_ledger.json")):
        ledger = json.load(open(os.path.join(out, "refs_ledger.json")))
        old = open(os.path.join(out, "report.md")).read().split("\n## Totals")[0].rstrip("\n")
        report = old.split("\n") + ["", f"Resumed {time.strftime('%Y-%m-%d %H:%M')}: {len(ledger)} pages already built", ""]
    for name in a.pages:
        # with --save, a page counts as done only once it saved (an entry written before a crash says saved: False);
        # an entry from before the flag existed has no key and is taken as done
        if a.resume and name in ledger and (not a.save or ledger[name].get("saved", True)):
            continue
        rows = [r.to_dict() for _, r in df[df["page"] == name].iterrows()]
        if not rows:
            report += [f"## {name}", "", "No tracker rows point at this page.", ""]
            continue
        live = GW.page_text(s, name) or ""
        text, pg = build(name, rows, owners, live, a.tracker)
        lost = audit_refs(pg, live, text)
        fn = re.sub(r"[^\w.-]+", "_", name)
        open(os.path.join(out, fn + ".txt"), "w").write(text)
        open(os.path.join(out, fn + ".orig.txt"), "w").write(live)
        ledger[name] = {"file": fn, "rows": len(rows), "live_chars": len(live),
                        "live_refs": len(REF_ANY.findall(strip_generated_comments(live))),
                        "live_urls": len({norm_url(u) for u in URL_RE.findall(live)}),
                        "carried_to_background": pg.carried, "lost": lost, "saved": False}
        json.dump(ledger, open(os.path.join(out, "refs_ledger.json"), "w"), indent=1, ensure_ascii=False)
        if pg.shapes:
            os.makedirs(os.path.join(out, "shapes"), exist_ok=True)
            for f, svg in pg.shapes.items():
                open(os.path.join(out, "shapes", f), "w").write(svg)
            pg.log.append(f"route shapes: {len(pg.shapes)} files in shapes/ (upload them before saving the page)")
        errs = []
        if not a.no_render:
            html, headhtml, errs = render(s, name, text)
            open(os.path.join(out, fn + ".html"), "w").write(html)
            if "#display_map" in text and "maps.googleapis.com" not in headhtml:
                pg.log.append("parse head has no Google Maps script (expected for a parse preview; check after a real save)")
        report += [f"## {name}", "", f"- rows: {len(rows)}; generated text {len(text):,} characters (live page {len(live):,})",
                   f"- cite errors in the rendered preview: {len(errs)}",
                   f"- live citations: {ledger[name]['live_refs']} refs, {ledger[name]['live_urls']} distinct URLs; added to Background: {len(pg.carried)}; LOST: {len(lost)}"]
        report += [f"  - {e}" for e in errs[:20]]
        if a.save:
            if pg.status_conflicts and not a.allow_status_conflicts:
                pg.log.append("NOT SAVED: Background states a status other than the tracker's (see STATUS CONFLICT); fix the text or the sheet, or re-run with --allow-status-conflicts")
            elif lost or errs:
                pg.log.append(f"NOT SAVED: {len(lost)} lost citations, {len(errs)} cite errors; fix and re-run")
            else:
                import wiki_save
                ls = ls if "ls" in dir() else GW.session(login=True)
                try:
                    up = upload_shapes(ls, out, name)
                    r = wiki_save.save(ls, name, text=page_body(text), summary="generated from the tracker by generate_pages.py")
                    pg.log.append(f"saved: {r.get('result')}, map {'BROKEN' if r.get('map', {}).get('broken') else 'ok'}, {len(up)} shapes uploaded")
                    ledger[name]["saved"] = r.get("result") == "Success" and not r.get("map", {}).get("broken")
                except Exception as e:  # one failed save is logged and retried by --resume, never the end of the run
                    pg.log.append(f"SAVE FAILED: {type(e).__name__}: {e}")
                json.dump(ledger, open(os.path.join(out, "refs_ledger.json"), "w"), indent=1, ensure_ascii=False)
        report += [f"- {l}" for l in pg.log] + [""]
        open(os.path.join(out, "report.md"), "w").write("\n".join(report))
    n_lost = sum(1 for v in ledger.values() if v["lost"])
    n_carried = sum(1 for v in ledger.values() if v["carried_to_background"])
    report += ["## Totals", "", f"- pages: {len(ledger)}; pages with citations added to Background: {n_carried}; pages with LOST citations: {n_lost}",
               f"- citation ledger: `refs_ledger.json` in this folder; the live text of every page is beside its draft as `.orig.txt`", ""]
    open(os.path.join(out, "report.md"), "w").write("\n".join(report))
    print(out)
    print("\n".join(report[-4:]))


if __name__ == "__main__":
    main()
