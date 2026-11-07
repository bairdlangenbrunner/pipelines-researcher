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
VERB = {"operating": "runs", "idled": "runs", "mothballed": "runs", "proposed": "is proposed to run",
        "construction": "is proposed to run", "shelved": "was proposed to run",
        "cancelled": "was proposed to run", "retired": "ran"}
CAPTION = {"very high (within meters)": "the exact route", "high": "the exact route",
           "medium": "the approximate route", "low": "the approximate route",
           "very low (straight line/schematic)": "a sketch of the route"}
MAP_GREY, STATUS_COLORS, STATUS_ORDER = B.MAP_GREY, B.STATUS_COLORS, B.STATUS_ORDER


def status_color(pg, status):
    return STATUS_COLORS[pg.tracker].get(status, MAP_GREY)


DOT_RE = re.compile(r'<span class="gem-statusdot" style="[^"]*"></span>')


def status_dot(pg, status):
    """A dot in the map's color for the status, set before the status word in the tables (Baird 2026-11-06).
    Inline style, so it shows on every page whatever stylesheets the page loads."""
    return (f'<span class="gem-statusdot" style="display:inline-block;width:8px;height:8px;margin:0 5px 1px 0;'
            f'border-radius:50%;vertical-align:middle;background:{status_color(pg, status)}"></span>')


STATUS_CATEGORY = {"operating": "Existing", "proposed": "Proposed", "construction": "Under construction",
                   "shelved": "Shelved", "cancelled": "Cancelled", "retired": "Retired",
                   "idled": "Idled", "mothballed": "Mothballed"}
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
CATS = {"gas": ["Global Gas Infrastructure Tracker", "Gas and Hydrogen Pipelines"],
        "oil": ["Global Oil Infrastructure Tracker", "Oil and NGL Pipelines"]}


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


def label(r, rows):
    s = (r["SegmentName"] or "").strip()
    m = re.match(r"SYSTEM/NETWORK INFO\s*\((.*)\)", s, re.I)
    if m:
        s = m.group(1).strip() or "Main Line"
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
    aka = (", also known as " + ", ".join(f"'''{n}'''" for n in names) + ",") if names else ""
    local = rows[0]["OtherLanguagePrimaryPipelineName"].strip() if len(rows) == 1 else ""
    local = f" (local name: '''{local}''')" if local else ""
    fuel, loc = fuel_phrase(rows, tracker), location_phrase(rows)
    if len(rows) == 1:
        st = STATUS_PHRASE.get(rows[0]["Status"], rows[0]["Status"])
        s = f"'''{pg.name}'''{aka}{local} is {a_an(st)} {st} {fuel} pipeline {loc}.{pg.cite(rows[0]['Status [ref]'])}"
    else:
        sts = []
        for r in rows:
            p = STATUS_PHRASE.get(r["Status"], r["Status"])
            if p and p not in sts:
                sts.append(p)
        rank = ["operating", "under construction", "proposed", "shelved", "cancelled", "idled", "mothballed", "retired"]
        sts.sort(key=lambda x: rank.index(x) if x in rank else 99)
        lst = sts[0] if len(sts) == 1 else ", ".join(sts[:-1]) + " and " + sts[-1]
        s = f"'''{pg.name}'''{aka}{local} is {a_an(fuel)} {fuel} pipeline {loc} with segments that are {lst}."
    dorm = []
    for r in rows:
        if r["ShelvedCancelledType"] != "inferred":
            continue
        st = r["Status"]
        yr = num(r["ShelvedYear"] if st == "shelved" else r["CancelledYear"])
        if yr is None:
            pg.log.append(f"{r['ProjectID']}: inferred {st} with no year; dormancy sentence left out")
            continue
        last = int(yr) - (2 if st == "shelved" else 4)
        rc = r["Shelved [ref]"] if st == "shelved" else r["Cancelled [ref]"]
        if len(rows) > 1:
            # too specific for the intro of a many-unit page: it goes in that unit's Background entry
            pg.dorm.append((r, f"No development on the project has been reported since {last}, and it is considered {st}.", rc))
            continue
        dorm.append(f"No development on the pipeline has been reported since {last}, and it is considered {st}." + pg.cite(rc))
    return s + ("\n\n" + " ".join(dorm) if dorm else "")


def table(num_, title, header, body, caption="", collapsed=False, sortable=False, footnote=""):
    # drop columns that are empty in every row (GEMwiki exclude_empty_columns=True); first column always kept
    keep = [0] + [i for i in range(1, len(header)) if any(row[i].strip() for row in body) or header[i] == "Segment"]
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


def thin_lines(pid, tol):
    raw = B.coords_of(pid)
    if not raw:
        return []
    merged = linemerge(MultiLineString([LineString(l) for l in raw if len(l) >= 2]))
    parts = list(merged.geoms) if hasattr(merged, "geoms") else [merged]
    out = []
    for g in parts:
        s = g.simplify(tol, preserve_topology=False)
        if s.length < tol * 2 and len(parts) > 1:
            continue  # stubs shorter than the simplify tolerance add points but nothing visible
        out.append(list(s.coords))
    return out


def map_block(pg, rows):
    mapped = [r for r in rows if r["RouteType"].startswith("Mapped route")]
    if not mapped:
        return "The route of this pipeline has not been mapped.", 0
    allp, lines = [], []
    tol = 0.01 if len(rows) > 1 else 0.003
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
            lines.append(f"{pts}~{title}~{dot}{STATUS_PHRASE.get(r['Status'], r['Status']).capitalize()}~{color}~1~3")
    if not lines:
        return "The route of this pipeline has not been mapped.", 0
    lats, lons = [p[1] for p in allp], [p[0] for p in allp]
    span = max(max(lats) - min(lats), max(lons) - min(lons))
    zoom = 4 if span > 12 else 5 if span > 6 else 6 if span > 3 else 7 if span > 1.5 else 8 if span > .7 else 9
    accs = {r["RouteAccuracy"] for r in mapped}
    cap = CAPTION.get(next(iter(accs)), "the approximate route") if len(accs) == 1 else "the approximate route"
    where = "of the pipeline" if len(rows) == 1 else "of its mapped segments"
    text = f"The map below shows {cap} {where}."
    legend = ""
    if len(rows) > 1:
        sts = sorted({r["Status"] for r in mapped}, key=lambda x: STATUS_ORDER.index(x) if x in STATUS_ORDER else 99)
        legend = "\n\n" + " &nbsp; ".join(f'<span style="color:{status_color(pg, s)}">■</span> {STATUS_PHRASE.get(s, s).capitalize()}'
                                            for s in sts)
        # one plain count on multi-segment pages (Baird 2026-11-06)
        text = f"{len(mapped)} of {len(rows)} segments have a mapped route in the database."
    body = ";".join(lines)
    mid = f"{(max(lats) + min(lats)) / 2:.5f}, {(max(lons) + min(lons)) / 2:.5f}"
    return (f'{text}\n\n<templatestyles src="{MAP_STYLES_PAGE}" />\n'
            f"{{{{#display_map:\n|lines={body}|center={mid}|width=100%|height=400|type=map|zoom={zoom}}}}}{legend}",
            len(allp))


def end_place(loc, prov, country=""):
    loc = (loc or "").strip()
    if loc.lower() == "offshore" and prov:
        return place(f"offshore {prov}", country)
    return place(loc, prov, country)


def join_list(xs):
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def overview_sentence(pg, rows, tabbed=False):
    """One sentence on where a many-segment pipeline is, so the page says it even with the
    route table collapsed: the system row's end points if there is one, then where the segments are.
    On a tabbed page the table sits under Project details, open, so the pointer says that instead."""
    sysr = [r for r in rows if r["SegmentName"].upper().startswith("SYSTEM/NETWORK")]
    cs = sorted({c for r in rows for c in countries(r["CountriesOrAreas"])})
    out = []
    if sysr:
        r = sysr[0]
        same_c = r["StartCountryOrArea"] == r["EndCountryOrArea"]
        a = end_place(r["StartLocation"], r["StartState/Province"], "" if same_c else r["StartCountryOrArea"])
        z = end_place(r["EndLocation"], r["EndState/Province"], r["EndCountryOrArea"])
        if a and z:
            out.append(f"The main pipeline {VERB.get(r['Status'], 'runs')} from {a} to {z}.{pg.cite(r['Location [ref]'])}")
    provs = sorted({p.strip() for r in rows for p in (r["StartState/Province"], r["EndState/Province"]) if p.strip()})
    if len(cs) == 1 and provs:
        word = "states" if cs[0] == "United States" else "provinces or states"
        n = f"{len(provs)} {word}" if len(provs) > 1 else provs[0]
        out.append(f"Its {len(rows)} segments are in {n}" + (f": {join_list(provs)}." if len(provs) > 1 else "."))
    elif len(cs) > 1:
        out.append(f"Its {len(rows)} segments are in {len(cs)} countries: {join_list([country_name(c) for c in cs])}.")
    if tabbed:
        out.append("The segment table under Project details lists each segment's start and end points on its Route tab.")
    else:
        out.append("The table below lists each segment's start and end points; click Expand to show it.")
    return " ".join(out)


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
    """proposal year, FID, construction year, start year, inactive year, each with its ref."""
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
    inactive = ""
    col = {"shelved": ("ShelvedYear", "Shelved [ref]"), "cancelled": ("CancelledYear", "Cancelled [ref]"),
           "retired": ("StopYear", "Stop [ref]"), "mothballed": ("StopYear", "Stop [ref]"),
           "idled": ("StopYear", "Stop [ref]")}.get(st)
    if col and r[col[0]].strip():
        inactive = f"{r[col[0]].strip()} ({st}{', inferred' if r['ShelvedCancelledType'] == 'inferred' else ''})" + pg.cite(r[col[1]])
    prop = r["ProposalYear"].strip()
    cons = r["ConstructionYear"].strip()
    return [prop + (pg.cite(r["Proposal [ref]"]) if prop else ""), fid,
            cons + (pg.cite(r["Construction [ref]"]) if cons else ""), start, inactive]


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
    can show one group at a time. Columns empty in every row are left out, and a tab whose columns are
    all gone is not offered. Old heading anchors (Table 1 ... Ownership) are kept as empty spans."""
    units = set()
    shapes = shape_cells(pg, rows)
    # (header, groups, unsortable) in table order: one order serves every tab
    cols = [("Route", ["route"], True), ("Start/end", ["route"], False), ("Countries/areas", ["route"], False),
            ("Status", ["details", "timeline"], False), ("Fuel", ["details"], False), ("Capacity", ["details"], False),
            ("Length", ["route", "details"], False), ("Diameter", ["details"], False), ("Pressure", ["details"], False),
            ("Proposal year", ["timeline"], False), ("FID", ["timeline"], False), ("Construction year", ["timeline"], False),
            ("Start year", ["timeline"], False), ("Inactive year", ["timeline"], False),
            ("Cost", ["cost"], False), ("Operator", ["ownership"], False), ("Owner", ["ownership"], False), ("Parent", ["ownership"], False)]
    body = []
    for r in rows:
        rt = route_cells(pg, r)
        dt = detail_cells(pg, r, units)
        tl = timeline_cells(pg, r)
        cells = [shapes.get(r["ProjectID"], "")] + rt[:2] + [dt[0], dt[1], dt[2], dt[3], dt[4], dt[5]] + tl + [cost_cell(pg, r)] + owner_cells(pg, r, owners)
        body.append((label(r, rows), cells))
    keep = [i for i in range(len(cols)) if any(cells[i].strip() for _, cells in body)]
    groups = [g for g in SEG_GROUPS if any(g in cols[i][1] for i in keep)]
    est = any(cells[6].endswith("*") for _, cells in body) and 6 in keep
    caps = {"details": gloss(units), "timeline": FID_GLOSS if 10 in keep else "", "cost": COST_NOTE if 14 in keep else ""}
    caps["all"] = "; ".join(c for c in (caps["details"], caps["timeline"], caps["cost"].rstrip(".")) if c)
    t = [f'<templatestyles src="{STYLES_PAGE}" />',
         '<span id="Table_1:_Route_details"></span><span id="Table_2:_Pipeline_details"></span><span id="Table_3:_Project_timeline"></span>'
         '<span id="Table_4:_Cost"></span><span id="Table_5:_Ownership"></span><span id="Ownership"></span>']
    t += [f'<div id="seg-{g}"></div>' for g in groups + ["all"]]
    t += ['<div class="gem-segments">',
          '<div class="gem-segtabs">' + " ".join(f"[[#seg-{g}|{SEG_TAB_LABEL[g]}]]" for g in groups + ["all"]) + "</div>",
          '{| class="wikitable sortable"',
          "|+ " + "".join(f'<span class="cap-{g}">{c}</span>' for g, c in caps.items() if c and (g == "all" or g in groups)),
          "!Segment"]
    for i in keep:
        h, gs, uns = cols[i]
        t.append(f'!class="{"unsortable " if uns else ""}{" ".join("col-" + g for g in gs)}"|{h}')
    for (lab, cells), r in zip(body, rows):
        pid = r["ProjectID"]
        # each segment name is an anchor, and links down to its Background row when it has one (Baird 2026-11-06)
        t += ["|-", f'|<span id="row-{pid}" class="gem-anchor"></span>' + (f'<span title="Click for project background">[[#bg-{pid}|{lab}]]</span>' if pid in pg.bg else lab)]
        for i in keep:
            v = cells[i].strip()
            cls = f'class="{" ".join("col-" + g for g in cols[i][1])}"'
            m = re.match(r'(data-sort-value="[^"]*")\|(.*)', v, re.S)   # a cost cell carries its sort key as an attribute
            if m:
                cls, v = f"{cls} {m.group(1)}", m.group(2)
            t.append(f'|{cls}|{v if v else ("" if i == 0 else "–")}')
    if est:
        t += ['|- class="sortbottom col-route col-details"', f'|colspan="{len(keep) + 1}"|{EST_NOTE}']
    t += ["|}", "</div>"]
    pg.log.append(f"tabbed segment table: {len(rows)} segments, {len(keep) + 1} columns, tabs {', '.join(groups)}")
    return "\n".join(t)


# ---------- sections ----------

def location(pg, rows, tab, tabbed=False):
    out = ["==Location=="]
    if len(rows) == 1:
        r = rows[0]
        same_c = r["StartCountryOrArea"] == r["EndCountryOrArea"]
        a = place(r["StartLocation"], r["StartState/Province"], "" if same_c else r["StartCountryOrArea"])
        z = place(r["EndLocation"], r["EndState/Province"], r["EndCountryOrArea"])
        v = VERB.get(r["Status"], "runs")
        out.append(f"The pipeline {v} from {a} to {z}.{pg.cite(r['Location [ref]'])}")
    elif tabbed:
        out.append(overview_sentence(pg, rows, tabbed=True))
    else:
        out.append(overview_sentence(pg, rows))
    if not tabbed:
        # the Route details table, the five-table pages' version of the tabbed table's Route tab. A one-segment page
        # gets it too, open and with no route picture, since the map sits right below (Baird 2026-11-06)
        shapes = shape_cells(pg, rows) if len(rows) > 1 else {}
        body = [([shapes[r["ProjectID"]]] if shapes else []) + [label(r, rows)] + route_cells(pg, r) for r in rows]
        out += ["", table(tab(), "Route details", (['class="unsortable"|Route'] if shapes else []) + ["Segment", "Start/end", "Countries/areas"], body,
                          collapsed=len(rows) > 1, sortable=True)]
    m, npts = map_block(pg, rows)
    out += ["", m]
    pg.log.append(f"map points: {npts}")
    return "\n".join(out)


def details(pg, rows, tab):
    out = ["==Project details=="]
    units = set()
    has_pressure = any(r.get("Pressure", "").strip() for r in rows)
    body = []
    for r in rows:
        d = detail_cells(pg, r, units)
        body.append([label(r, rows)] + (d if has_pressure else d[:5]))
    head = ["Segment", "Status", "Fuel", "Capacity", "Length", "Diameter"] + (["Pressure"] if has_pressure else [])
    out.append(table(tab(), "Pipeline details", head, body, gloss(units), sortable=True,
                     footnote=EST_NOTE if any(b[4].endswith("*") for b in body) else ""))

    # timeline
    # no Status column: the Pipeline details table right above already shows it (Baird 2026-11-06, Ruby)
    body = [[label(r, rows)] + timeline_cells(pg, r) for r in rows]
    cap = FID_GLOSS if any(r["FIDStatus"].strip() or r["FIDYear"].strip() for r in rows) else ""
    out += ["", table(tab(), "Project timeline", ["Segment", "Proposal year", "FID", "Construction year",
                                                  "Start year", "Inactive year"], body, cap, sortable=True)]

    # cost
    body = [[label(r, rows), cost_cell(pg, r)] for r in rows]
    out.append("")
    if any(b[1] for b in body):
        out.append(table(tab(), "Cost", ["Segment", "Cost"], body, sortable=True))
    else:
        out.append("====Cost====\nNo cost data available.")
    return "\n".join(out)


def ownership(pg, rows, owners, tab):
    body = [[label(r, rows)] + owner_cells(pg, r, owners) for r in rows]
    return "==Ownership==\n" + table(tab(), "Ownership", ["Segment"] + [f'width="26%"|{h}' for h in ("Operator", "Owner", "Parent")], body)


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
    longer cites. Returns citation lines for an 'Other sources' section, so nothing is dropped."""
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
        pg.log.append(f"{len(out)} sources cited only in replaced sections; carried into 'Other sources'")
    return "\n".join(f"* {c}" for c in out)


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
    status = {_key(label(r, rows)): r["Status"] for r in rows}
    status.update({_key(r["SegmentName"]): r["Status"] for r in rows if r["SegmentName"].strip()})
    t = ['{| class="wikitable"', "!Segment", "!Status", "!Background"]
    unmatched = []
    for h, txt in subs:
        txt = re.sub(r"(?m)^====+\s*(.*?)\s*=+\s*$", "'''\\1'''", txt)
        txt = re.sub(r"(?m)^([|!])", r"<nowiki>\1</nowiki>", txt)  # a line starting | or ! would break the table
        st = status.get(_key(h), "")
        if not st:
            unmatched.append(h)
        t += ["|-", f"|{h}", f"|{STATUS_PHRASE.get(st, st) or '–'}", "|\n" + (txt or "–")]
    t.append("|}")
    if unmatched:
        pg.log.append(f"Background table: no tracker status matched for {', '.join(unmatched)}")
    pg.log.append(f"Background: {len(subs)} segment subsections turned into a table")
    new = (lead + "\n\n" if lead else "") + "\n".join(t) + "\n\n"
    return kept[:m.start(1)] + new + kept[m.end(1):]


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
    unmatched, used = [], set()

    def cell(mo):
        pre, name = mo.group(1), BG_LINKED.sub(r"\1", mo.group(2)).strip()
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


def dormancy_into_background(pg, kept, rows):
    """Put each segment's dormancy sentence at the end of its row in the Background table, or add a
    row for the segment when it has none. Skipped when the sentence is already there (a re-run)."""
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


def build(name, rows, owners, live, tracker):
    pg = Page(name, tracker)
    rows = order(rows)
    kept, extra_ar, replaced = preserved(pg, live)
    kept = unshade(kept)
    kept = background_table(pg, kept, order(rows))
    if len(rows) >= SEG_TABLE_MIN:
        kept = link_background(pg, kept, rows)
    # a Background table built on the 2026-11-06 run says "Unit"; the row label is "Segment" (Baird 2026-11-06)
    kept = kept.replace("!Unit\n!Status\n!Background", "!Segment\n!Status\n!Background")
    seed_url_names(pg, kept)
    # names the kept text defines are cited bare by the tables, never redefined
    pg.defined |= {m.group(1).strip() for m in NAMED_DEF.finditer(kept)}
    tab = Counter()
    head = [name, "", f"<!---\n\t{COMMENT1}\n-->", NAVBAR[tracker], intro(pg, rows, tracker), ""]
    tabbed = len(rows) >= SEG_TABLE_MIN
    if tabbed:   # one tabbed segment table instead of the five separate tables (Baird 2026-11-06)
        body = location(pg, rows, tab, tabbed=True) + "\n\n==Project details==\n" + segment_table(pg, rows, owners)
    else:
        body = location(pg, rows, tab) + "\n\n" + details(pg, rows, tab) + "\n\n" + ownership(pg, rows, owners, tab)
    gen = "\n".join(head) + "\n" + body + "\n"
    # the generated part defines its refs before kept text uses them; named refs the kept text
    # defines itself are reused above
    pg.defined |= {m.group(1).strip() for m in NAMED_DEF.finditer(kept)}
    kept = dormancy_into_background(pg, kept, rows)
    kept = color_background_status(pg, kept)
    kept = fix_named_refs(pg, kept, live, gen)
    carried = lost_refs(pg, replaced, gen + kept + extra_ar)
    if carried:
        # in the human-kept zone, so the data team's generator also keeps it
        kept = (kept + "\n\n" if kept else "") + "==Other sources==\nSources cited on earlier versions of this page.\n\n" + carried
    word, link = TRACKER_LINK[tracker]
    cats = [f"[[Category:{c}]]" for c in CATS[tracker]]
    for r in rows:
        for c in countries(r["CountriesOrAreas"]):
            sc = STATUS_CATEGORY.get(r["Status"])
            cat = f"[[Category:{sc} pipelines in {country_name(c)}]]" if sc else ""
            if cat and cat not in cats:
                cats.append(cat)
    # category lines inside kept text move to the category block at the end
    for blk in (kept, extra_ar):
        for c in re.findall(r"\[\[\s*Category\s*:\s*([^\]]+?)\s*\]\]", blk):
            if f"[[Category:{c}]]" not in cats:
                cats.append(f"[[Category:{c}]]")
    strip_cat = lambda t: re.sub(r"\n*\[\[\s*Category\s*:[^\]]+\]\]", "", t).strip()
    kept, extra_ar = strip_cat(kept), strip_cat(extra_ar)
    extra_ar = "\n\n".join(b for b in re.split(r"\n\n(?====)", extra_ar) if b.strip() and "\n" in b.strip())
    tail = ["==Articles and resources==", "", "===References===", "<references />", ""]
    if extra_ar:
        tail += [extra_ar, ""]
    tail += ["===Additional data===",
             f"To access additional data, including an interactive map of {word} pipelines, a downloadable dataset, and summary data, please visit the {link} on the Global Energy Monitor website.",
             ""] + cats
    text = gen + f"<!---\n\t{COMMENT2}\n-->\n" + (kept + "\n" if kept else "") + f"<!---\n\t{COMMENT3}\n-->\n" + "\n".join(tail) + "\n"
    text = B.sentence_case_headings(shade_first_column(text))
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pages", nargs="*")
    ap.add_argument("--tracker", default="gas", choices=["gas"])
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--save", action="store_true", help="upload the route shapes and save each page via wiki_save (page-name line dropped)")
    ap.add_argument("--push-styles", action="store_true", help="save the tabbed-table and map-popup stylesheet pages on the wiki if they differ")
    a = ap.parse_args()
    if a.push_styles:
        print(ensure_styles(GW.session(login=True)))
        if not a.pages:
            return
    elif not a.pages:
        ap.error("no pages given")
    df = C.load(a.tracker)
    df["page"] = df["Wiki"].map(C.page_name)
    B.fill_unknown_parents(df)
    own = C.load("owners").drop_duplicates("ProjectID").set_index("ProjectID")
    owners = {pid: row.to_dict() for pid, row in own.iterrows()}
    out = a.out or os.path.join(C.OUT, "samples", time.strftime("%Y%m%d_%H%M"))
    os.makedirs(out, exist_ok=True)
    s = GW.session()
    report = [f"# Sample pages, {time.strftime('%Y-%m-%d %H:%M')}", "", f"Snapshot: `{os.path.basename(df.attrs['path'])}`", ""]
    for name in a.pages:
        rows = [r.to_dict() for _, r in df[df["page"] == name].iterrows()]
        if not rows:
            report += [f"## {name}", "", "No tracker rows point at this page.", ""]
            continue
        live = GW.page_text(s, name) or ""
        text, pg = build(name, rows, owners, live, a.tracker)
        fn = re.sub(r"[^\w.-]+", "_", name)
        open(os.path.join(out, fn + ".txt"), "w").write(text)
        open(os.path.join(out, fn + ".orig.txt"), "w").write(live)
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
                   f"- cite errors in the rendered preview: {len(errs)}"]
        report += [f"  - {e}" for e in errs[:20]]
        if a.save:
            import wiki_save
            ls = ls if "ls" in dir() else GW.session(login=True)
            up = upload_shapes(ls, out, name)
            r = wiki_save.save(ls, name, text=page_body(text), summary="generated from the tracker by generate_pages.py")
            pg.log.append(f"saved: {r.get('result')}, map {'BROKEN' if r.get('map', {}).get('broken') else 'ok'}, {len(up)} shapes uploaded")
        report += [f"- {l}" for l in pg.log] + [""]
    open(os.path.join(out, "report.md"), "w").write("\n".join(report))
    print(out)
    print("\n".join(report))


if __name__ == "__main__":
    main()
