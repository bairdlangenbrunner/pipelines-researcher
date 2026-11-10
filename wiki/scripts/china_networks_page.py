"""Build the "Chinese Gas Pipeline Networks" page: what the China gas networks are and one table row per network.

Every network page's lead links here ("It is a GEM grouping"). The networks are the registry's China entries
(wiki/data/networks.json); the counts come from the live Gas tab (PrimaryNetwork), read through gws-gem.
Dry run by default: writes wiki/out/networks/Chinese_Gas_Pipeline_Networks/ and renders the page. --save saves it
through wiki_save.py. Rerun after a network page is built so the table links it.
Usage: python wiki/scripts/china_networks_page.py [--save]
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import network_pages as N  # noqa: E402

G, GW, REPO, H = N.G, N.GW, N.REPO, N.H
TITLE = N.OVERVIEW_PAGE
# Mainland China's 22 provinces and five autonomous regions, named as the network registry names them.
PROVINCES = ["Anhui", "Fujian", "Gansu", "Guangdong", "Guizhou", "Hainan", "Hebei", "Heilongjiang", "Henan", "Hubei",
             "Hunan", "Jiangsu", "Jiangxi", "Jilin", "Liaoning", "Qinghai", "Shaanxi", "Shandong", "Shanxi", "Sichuan",
             "Yunnan", "Zhejiang", "Guangxi", "Inner Mongolia", "Ningxia", "Tibet", "Xinjiang"]


def kind(name):
    if name.endswith(" Provincial Gas Network"):
        return "Provincial network"
    if name.endswith(" Municipal Gas Network"):
        return "Municipal network"
    return "Grouping"


def build(s, nets, df):
    pg = G.Page(TITLE, "gas")
    names = [n["PrimaryNetwork"] for n in nets]
    local = {n["PrimaryNetwork"]: n.get("PrimaryNetworkLocalLanguage", "") for n in nets}
    rank = {"Grouping": 0, "Provincial network": 1, "Municipal network": 2}
    names.sort(key=lambda n: (rank[kind(n)], n))
    have = N.exists(s, names)
    lk = lambda n: f"[[{n}]]" if have.get(n) else n
    rows = {n: [r.to_dict() for _, r in df[df["PrimaryNetwork"] == n].iterrows()] for n in names}
    allrows = [r for n in names for r in rows[n]]
    n_prov = sum(kind(n) == "Provincial network" for n in names)
    n_muni = sum(kind(n) == "Municipal network" for n in names)
    have_prov = {n.replace(" Provincial Gas Network", "") for n in names if kind(n) == "Provincial network"}
    missing = [p for p in PROVINCES if p not in have_prov]
    if not missing:
        gap = "Every province and autonomous region has one."
    elif len(missing) == 1:
        gap = f"{missing[0]} is the only one without a provincial network."
    else:
        gap = f"{G.join_list(missing)} are the only ones without a provincial network."

    lead = (f"'''{TITLE}''' are the groups Global Energy Monitor (GEM) uses to sort China's gas pipelines. China has built gas "
            "pipelines on a vast scale, and these groups make the buildout easier to follow. They are GEM's own way of "
            "organizing the pipelines, not official Chinese networks.")
    how = ["==How pipelines are grouped==",
           "Every gas pipeline in China belongs to one network. There are five kinds:",
           f"* '''Provincial gas networks:''' Pipelines that a province builds, or that run within one province or autonomous "
           f"region. There are {N.num(n_prov)}, one for each province or region with gas pipelines. {gap}",
           f"* '''Municipal gas networks:''' The same for the {N.num(n_muni)} cities governed directly by the central government: "
           + G.join_list([n.replace(" Municipal Gas Network", "") for n in names if kind(n) == "Municipal network"]) + ".",
           f"* '''{lk('China National Gas Pipelines')}:''' {N.GROUPING_SCOPE['China National Gas Pipelines'][0].upper()}"
           f"{N.GROUPING_SCOPE['China National Gas Pipelines'][1:]}.",
           f"* '''{lk('China International Gas Pipelines')}:''' Gas pipelines that cross China's borders.",
           f"* '''{lk('China Interprovincial Gas Pipelines')}:''' Gas pipelines that cross provincial borders but belong to "
           "neither a provincial network nor the national trunk system."]
    t = ["==Networks==",
         '{| class="wikitable sortable"', H + "Network", H + "Kind", H + "Pipelines", H + "Segments",
         H + "Length", H + "Status"]
    for n in names:
        rs = rows[n]
        t += ["|-", f"|{lk(n)}", f"|{kind(n)}", f"|{len({r['PipelineName'] for r in rs})}",
              f"|{len(rs)}", f"|{N.length_cell(rs)}", f"|{N.mix(pg, rs) if rs else '–'}"]
    t += ['|- class="sortbottom"', "!Total", "!", f"!{len({r['PipelineName'] for r in allrows})}", f"!{len(allrows)}",
          f"!{N.length_cell(allrows).split('|')[-1]}", f"!{N.mix(pg, allrows)}", "|}"]
    tail = ["==Articles and resources==", "", "===Additional data===",
            f"To access additional data, including an interactive map of {G.TRACKER_LINK['gas'][0]} pipelines, a downloadable dataset, "
            f"and summary data, please visit the {G.TRACKER_LINK['gas'][1]} on the Global Energy Monitor website.", ""]
    text = "\n".join([TITLE, "", f"<!---\n\t{G.COMMENT1}\n-->", G.NAVBAR["gas"], lead, ""] + how + [""] + t + [""] + tail)
    text = N.B.sentence_case_headings(G.shade_first_column(text))
    empty = [n for n in names if not rows[n]]
    pg.log.append(f"{len(names)} networks, {len(allrows)} segments; pages that exist: {sum(have.values())}; empty networks: {empty}")
    return text, pg


def main():
    reg = json.load(open(os.path.join(REPO, "wiki", "data", "networks.json")))
    nets = [n for n in reg["networks"] if any("China" in c for c in n.get("countries") or ["China"])]
    out = os.path.join(REPO, "wiki", "out", "networks", TITLE.replace(" ", "_"))
    os.makedirs(out, exist_ok=True)
    s = GW.session()
    df = N.live_rows()
    text, pg = build(s, nets, df)
    open(os.path.join(out, "page.txt"), "w").write(text)
    html, head, errs = G.render(s, TITLE, text)
    open(os.path.join(out, "page.html"), "w").write(html)
    print(f"{TITLE}: {len(text)} chars, cite errors {errs[:5]}")
    print("  " + "\n  ".join(pg.log))
    if "--save" in sys.argv:
        if errs:
            sys.exit("not saved: cite errors")
        import wiki_save
        r = wiki_save.save(GW.session(login=True), TITLE, text=G.page_body(text),
                           summary="what the China gas pipeline networks are, with one row per network")
        print("saved", TITLE, r.get("result"), "map", r.get("map"))


if __name__ == "__main__":
    main()
