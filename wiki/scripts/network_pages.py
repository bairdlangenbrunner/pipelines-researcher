"""Build a China gas network page (Provincial / Municipal Gas Network, or one of the three groupings) from the live sheet.

Members are the rows whose PrimaryNetwork is the network; connected pipelines are rows that list it in SecondaryNetworks.
Every member pipeline has its own page, so the network page carries no segment tables: a Pipelines table, a Connected
pipelines table, a map (connected lines lighter), and a Background with the network-wide history plus one short
explainer per member pipeline ending "Its page has more details." (docs/plans/2026-11-08_network-pages.md).

When the registry gives the network a `former_name` whose live page is still the old network-style page, that page goes
back to an ordinary pipeline page for its own rows (generate_pages.build), and its network-wide prose moves here.

Dry run by default: writes wiki/out/networks/<page>/ and renders both pages. --save saves through wiki_save.py.
Usage: python wiki/scripts/network_pages.py "Guangxi Provincial Gas Network" [--save]
"""
import collections, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generate_pages as G  # noqa: E402

C, B, GW = G.C, G.B, G.GW
REPO = G.REPO
SID = "1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"
TAB = "Gas pipelines"
ORDER = ["operating", "construction", "proposed", "shelved", "cancelled", "mothballed", "idled", "retired"]
H = "!"
OVERVIEW_PAGE = "Chinese Gas Pipeline Networks"   # the page that explains every China network (china_networks_page.py)
# what each of the three groupings holds, from the 2024 classification checklist (I / N / T)
GROUPING_SCOPE = {
    "China National Gas Pipelines": "China's national trunk gas pipelines, most of them built by PetroChina, PipeChina, and other state-owned companies",
    "China International Gas Pipelines": "the gas pipelines that cross China's borders",
    "China Interprovincial Gas Pipelines": "the gas pipelines that cross provincial borders in China but belong to neither a provincial network nor the national trunk system",
}


def live_rows():
    """The Gas tab as dicts, read through gws-gem (read-only). N/A rows are dropped."""
    env = dict(os.environ, GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser("~/.config/gws-gem"),
               GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file")
    prm = {"spreadsheetId": SID, "range": f"'{TAB}'!A3:ZZ"}
    p = subprocess.run(["gws", "sheets", "spreadsheets", "values", "get", "--params", json.dumps(prm)],
                       env=env, capture_output=True, text=True)
    if "{" not in p.stdout:
        sys.exit("sheet read failed (gws-gem auth?): " + p.stderr[-500:])
    v = json.loads(p.stdout[p.stdout.index("{"):])["values"]
    hdr = v[0]
    import pandas as pd
    df = pd.DataFrame([r + [""] * (len(hdr) - len(r)) for r in v[1:]], columns=hdr, dtype=str).fillna("")
    df = df[df["ProjectID"].str.startswith("P") & (df["Status"].str.strip() != "N/A")].copy()
    B.fill_unknown_parents(df)
    return df


WORDS = "zero one two three four five six seven eight nine".split()


def num(n):
    """Prose numbers: one to nine as words, 10 and up as numerals (Baird 2026-11-08). Table cells stay numerals."""
    return WORDS[n] if 0 <= n <= 9 else str(n)


def km(r):
    for c in ("LengthMergedKm", "LengthKnownKm"):
        try:
            return float(str(r[c]).replace(",", ""))
        except ValueError:
            pass
    return 0.0


def secondaries(r):
    return [x.strip() for x in r["SecondaryNetworks"].split(",") if x.strip()]


def status_rank(s):
    return ORDER.index(s) if s in ORDER else 99


def mix(pg, rows):
    c = collections.Counter(r["Status"] for r in rows)
    return " ".join(f"{G.status_dot(pg, s)}{c[s]} {G.STATUS_PHRASE.get(s, s)}" for s in sorted(c, key=status_rank))


def mix_words(rows):
    c = collections.Counter(r["Status"] for r in rows)
    return G.join_list([f"{c[s]} {G.STATUS_PHRASE.get(s, s)}" for s in sorted(c, key=status_rank)])


def length_cell(rows):
    k = sum(km(r) for r in rows)
    return f'data-sort-value="{k:.0f}"|{k:,.0f} km' if k else "–"


def page_of(rows):
    """The page the rows' Wiki cell points at (the most common one)."""
    names = collections.Counter(C.page_name(r["Wiki"]) for r in rows if C.page_name(r["Wiki"]))
    return names.most_common(1)[0][0] if names else ""


def exists(s, titles):
    out = {}
    titles = [t for t in titles if t]
    for i in range(0, len(titles), 40):
        d = GW.get(s, action="query", titles="|".join(titles[i:i + 40]))
        q = d["query"]
        norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
        pages = q["pages"].values() if isinstance(q["pages"], dict) else q["pages"]
        have = {p["title"] for p in pages if "missing" not in p}
        for t in titles[i:i + 40]:
            out[t] = norm.get(t, t) in have
    return out


FORMER = set()   # pages that are still the old network-style page: their lead names the network, not the pipeline


def local_name(s, page, rows):
    """The local name the pipeline's own page gives in its lead, else the commonest local name on its rows."""
    if page and page not in FORMER:
        try:
            # old pages say "(local name: '''X''')", new ones "'''Name''' (X)" (GOGPT style, 2026-11-10)
            m = (re.search(r"\(local name: '''(.*?)'''", GW.page_text(s, page) or "")
                 or re.search(r"^'''[^'\n]+''' \(([^()\n]*[^\x00-\x7f][^()\n]*)\)", GW.page_text(s, page) or "", re.M))
            if m:
                return m.group(1)
        except Exception:
            pass
    c = collections.Counter(r["OtherLanguagePrimaryPipelineName"].strip() for r in rows if r["OtherLanguagePrimaryPipelineName"].strip())
    return c.most_common(1)[0][0] if c else ""


def group(rows):
    g = collections.OrderedDict()
    for r in sorted(rows, key=lambda r: r["PipelineName"]):
        g.setdefault(r["PipelineName"], []).append(r)
    return collections.OrderedDict(sorted(g.items(), key=lambda kv: -sum(km(r) for r in kv[1])))


def link(name, page, have):
    if page and have.get(page):
        return f"[[{page}]]" if page == name else f"[[{page}|{name}]]"
    return name


def map_section(pg, members, connected):
    lines, edges, allp = [], [], []
    by_pipe = group(members)
    for rows, faint in ((members, False), (connected, True)):
        for r in rows:
            if not r["RouteType"].startswith("Mapped route"):
                continue
            ls = G.thin_lines(r["ProjectID"], 0.01)
            if not ls:
                pg.log.append(f"{r['ProjectID']}: RouteType says mapped but the routes repo has no geometry")
                continue
            sib = by_pipe.get(r["PipelineName"], [r]) if not faint else [q for q in connected if q["PipelineName"] == r["PipelineName"]]
            title = f"{r['PipelineName']}: {G.label(r, sib)}" + (" (connected pipeline)" if faint else "")
            dot = f'<span class="gem-mapdot gem-mapdot-{r["Status"].replace(" ", "-")}"></span>'
            st = G.STATUS_PHRASE.get(r["Status"], r["Status"]).capitalize()
            w = "0.45~2" if faint else f"1~{G.LINE_W}"
            for l in ls:
                if not faint:
                    allp += l
                pts = ":".join(f"{p[1]:.5f}, {p[0]:.5f}" for p in l)
                if not faint:   # a white edge under each member line, same pop-up (generate_pages.map_block); connected lines get none
                    edges.append(f"{pts}~{title}~{dot}{st}~{G.MAP_EDGE}~1~{G.LINE_W + 5}")
                lines.append(f"{pts}~{title}~{dot}{st}~{G.status_color(pg, r['Status'])}~{w}")
    mapped = sum(1 for r in members if r["RouteType"].startswith("Mapped route"))
    text = f"{num(mapped).capitalize() if mapped < 10 else mapped} of {num(len(members))} segments have a mapped route in the database."
    if not allp:
        return text
    lats, lons = [p[1] for p in allp], [p[0] for p in allp]
    span = max(max(lats) - min(lats), max(lons) - min(lons))
    zoom = 4 if span > 12 else 5 if span > 6 else 6 if span > 3 else 7 if span > 1.5 else 8 if span > .7 else 9
    mid = f"{(max(lats) + min(lats)) / 2:.5f}, {(max(lons) + min(lons)) / 2:.5f}"
    sts = sorted({r["Status"] for r in members if r["RouteType"].startswith("Mapped route")}, key=status_rank)
    legend = " &nbsp; ".join(f'<span style="color:{G.status_color(pg, s)}">■</span> {G.STATUS_PHRASE.get(s, s).capitalize()}' for s in sts)
    if connected:
        legend += ' &nbsp; <span style="color:#8f8f8e;opacity:.5">━</span> Connected pipeline (lighter line, not counted)'
    return (f'{text}\n\n<templatestyles src="{G.MAP_STYLES_PAGE}" />\n'
            f"{{{{#display_map:\n|lines={';'.join(edges + lines)}|center={mid}|width=100%|height=400|type=map|zoom={zoom}}}}}\n\n{legend}\n\n{B.route_note(pg.tracker)}")


def region_of(entry):
    nm = entry["PrimaryNetwork"]
    for suf in (" Provincial Gas Network", " Municipal Gas Network"):
        if nm.endswith(suf):
            return nm[: -len(suf)]
    return ""


def explainer(pipe, page, have, rows, old_sub):
    """One or two sentences on a member pipeline, ending with the pointer to its page."""
    if old_sub:
        first = re.split(r"(?<=\.)\s", old_sub.strip(), maxsplit=1)[0]
        if "[[" in first:
            return f"{first} Its page has more details."
    lk = link(pipe, page, have)
    return f"The {lk} has {num(len(rows))} segment{'s' if len(rows) != 1 else ''}: {mix_words(rows)}. Its page has more details."


def sections(txt):
    """{heading: body} for the ===...=== subsections of a text block."""
    return {h.strip(): b for h, b in re.findall(r"(?ms)^===([^=\n]+)===\s*\n(.*?)(?=^==|\Z)", txt)}


def build_network(s, entry, df, old_text=""):
    name = entry["PrimaryNetwork"]
    pg = G.Page(name, "gas")
    members = G.order([r.to_dict() for _, r in df[df["PrimaryNetwork"] == name].iterrows()])
    connected = []   # Connected pipelines are not shown on network pages (Baird 2026-11-08); SecondaryNetworks stays on the sheet
    pipes, cpipes = group(members), group(connected)
    pages = {p: page_of(rs) for p, rs in list(pipes.items()) + list(cpipes.items())}
    nets = sorted({r["PrimaryNetwork"] for r in connected})
    have = exists(s, list(pages.values()) + nets)
    region = region_of(entry)

    # lead: two short sentences (Baird 2026-11-08); GEM spelled out in the lead (Baird 2026-11-09); the grouping phrase links to the page that explains the whole scheme
    loc = f" ({entry['PrimaryNetworkLocalLanguage']})" if entry.get("PrimaryNetworkLocalLanguage") else ""
    what = f"the gas pipelines in {region}, China" if region else GROUPING_SCOPE.get(name, "a set of gas pipelines in China")
    lead = (f"'''{name}'''{loc} groups {what}. It is a [[{OVERVIEW_PAGE}|Chinese pipeline grouping by Global Energy Monitor (GEM)]], not an official Chinese network.")

    # location: the map and its count only; no provinces sentence (Baird 2026-11-08)
    location = ["==Location==", map_section(pg, members, connected)]

    # pipelines
    t = ["==Pipelines==",
         "Each pipeline or group of pipelines in the network has its own page with details.",
         '{| class="wikitable"', H + "Pipeline", H + "Local name", H + "Segments", H + "Length", H + "Status"]
    for p, rs in pipes.items():
        t += ["|-", f"|{link(p, pages[p], have)}", f"|{local_name(s, pages[p] if have.get(pages[p]) else '', rs) or '–'}",
              f"|{len(rs)}", f"|{length_cell(rs)}", f"|{mix(pg, rs)}"]
    t += ["|}"]
    # No Background section (Baird 2026-11-08): a network page holds no history. Its background goes onto the member
    # pipelines' own pages, so the page has no citations and no References section either.
    tail = ["==Articles and resources==", "", "===Additional data===",
            f"To access additional data, including an interactive map of {G.TRACKER_LINK['gas'][0]} pipelines, a downloadable dataset, "
            f"and summary data, please visit the {G.TRACKER_LINK['gas'][1]} on the Global Energy Monitor website.", ""]
    text = "\n".join([name, "", f"<!---\n\t{G.COMMENT1}\n-->", G.NAVBAR["gas"], lead, ""] + location + [""] + t + [""]
                     + [f"<!---\n\t{G.COMMENT3}\n-->"] + tail)
    text = B.sentence_case_headings(G.shade_first_column(text))
    pg.log.append(f"members {len(members)} in {len(pipes)} pipelines; connected {len(connected)} in {len(cpipes)} pipelines")
    return text, pg


def rebuild_former(s, former, df, live):
    """The old network-style page goes back to an ordinary pipeline page for the rows named after it. Its legacy zone
    is cut to the segment Background table and the Additional sources line, which are about this pipeline's own lines."""
    rows = [r.to_dict() for _, r in df[df["PipelineName"] == former].iterrows()]
    owners_df = C.load("owners").drop_duplicates("ProjectID").set_index("ProjectID")
    owners = {pid: row.to_dict() for pid, row in owners_df.iterrows()}
    bgpart = live.split("==Background==", 1)[1].split("<!---\n\tCOMMENT 3", 1)[0]
    subs = sections(bgpart)
    add = re.search(r"(?m)^Additional sources:.*$", subs.get("Network background", ""))
    segtab = re.search(r"(?ms)^<div class=\"gem-bgbox\">.*?^</div>|^\{\|.*?^\|\}", subs.get(f"{former} segments", ""))
    legacy = "\n".join([f"'''{former}'''", "", "==Background==", segtab.group(0) if segtab else "",
                        "", add.group(0) if add else "", ""])
    text, pg = G.build(former, rows, owners, legacy, "gas")
    return text, pg, rows


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    save = "--save" in sys.argv
    reg = json.load(open(os.path.join(REPO, "wiki", "data", "networks.json")))
    entry = next(n for n in reg["networks"] if n["PrimaryNetwork"] == args[0])
    out = os.path.join(REPO, "wiki", "out", "networks", entry["PrimaryNetwork"].replace(" ", "_"))
    os.makedirs(out, exist_ok=True)
    s = GW.session()
    df = live_rows()
    former = entry.get("former_name", "")
    old = GW.page_text(s, former) if former else ""
    old_is_network = bool(old) and "==Pipelines==" in old
    if old_is_network:
        FORMER.add(former)
    net_text, npg = build_network(s, entry, df, old if old_is_network else "")
    pages = [(entry["PrimaryNetwork"], net_text, npg, out)]
    if old_is_network:
        ptext, ppg, prow = rebuild_former(s, former, df, old)
        # the lead gives the pipeline's own local name, never one segment's (the generator's alias fallback)
        own = local_name(s, "", prow)
        q = "'" * 3
        alias = re.compile(r"(\n" + q + re.escape(former) + q + r")(?:, also known as " + q + r"[^\n]*?" + q + ","
                           r"| \(local name: " + q + r"[^\n]*?" + q + r"\)"
                           r"| \([^()\n]*[^\x00-\x7f][^()\n]*\))")
        ptext = alias.sub(lambda m: m.group(1) + (f" ({own})" if own else ""), ptext, count=1)
        lead_end = re.search(r"(\n'''" + re.escape(former) + r"'''[^\n]*?\.)(?= |\n)", ptext)
        if lead_end and entry["PrimaryNetwork"] not in ptext:
            ptext = ptext[:lead_end.end()] + f" It is classified as part of the [[{entry['PrimaryNetwork']}]]." + ptext[lead_end.end():]
        pout = os.path.join(out, "former")
        os.makedirs(pout, exist_ok=True)
        pages.append((former, ptext, ppg, pout))
        # nothing the old page cited may be lost across the two new pages
        U = lambda x: {G.norm_url(u.replace("https://web.archive.org/save/", "")) for u in G.URL_RE.findall(x)
                       if not G.OWN_LINK.search(u)}
        gone = U(old) - U(net_text + ptext)
        print("old page URLs not on either new page:", len(gone), sorted(gone)[:20])
    ok = True
    for title, text, pg, d in pages:
        open(os.path.join(d, "page.txt"), "w").write(text)
        if pg.shapes:
            os.makedirs(os.path.join(d, "shapes"), exist_ok=True)
            for f, svg in pg.shapes.items():
                open(os.path.join(d, "shapes", f), "w").write(svg)
        html, head, errs = G.render(s, title, text)
        open(os.path.join(d, "page.html"), "w").write(html)
        print(f"{title}: {len(text)} chars, cite errors {errs[:5]}, lost {pg.lost}")
        print("  " + "\n  ".join(pg.log[:40]))
        ok = ok and not errs and not pg.lost
    if old_is_network and gone:
        ok = False
    if save:
        if not ok:
            sys.exit("not saved: cite errors or lost citations")
        import wiki_save
        ls = GW.session(login=True)
        for title, text, pg, d in reversed(pages):   # the pipeline page first, so the network page's links land
            up = G.upload_shapes(ls, d, title) if pg.shapes else []
            summ = (f"network page for the China gas network scheme; members from PrimaryNetwork, connected pipelines from SecondaryNetworks"
                    if title == entry["PrimaryNetwork"] else f"back to a pipeline page; its network is now [[{entry['PrimaryNetwork']}]]")
            r = wiki_save.save(ls, title, text=G.page_body(text), summary=summ)
            print("saved", title, r.get("result"), "map", r.get("map"), "shapes", len(up))


if __name__ == "__main__":
    main()
