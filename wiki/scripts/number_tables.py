"""One-off 2026-11-08 (Baird): add the running-number "#" column to the segment table and the Background table of
every page edited since Friday, and put the serial comma in the lead's status list. Patches live text in place.
Usage: python wiki/scripts/number_tables.py [--save]   (dry run prints what would change)"""
import os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))
import network_pages as N
import wiki_save
G = N.G
HG, UG = 'style="background-color:#d4d8de"', 'style="background-color:#eaecf0"'


def number_table(blk, header_re, first_cell_re):
    """blk is one table's text. Insert a '#' header before the Segment header and a number cell before each row's first cell."""
    h = re.search(r"(?m)^!(?:style=\"[^\"]*\"\|)?Segment$", blk)
    if not h or re.search(r"(?m)^!(?:style=\"[^\"]*\"\|)?#$", blk[:h.start()][-80:]):
        return blk, 0
    blk = blk[:h.start()] + f"!{HG}|#\n" + blk[h.start():]
    n = [0]

    def row(m):
        n[0] += 1
        return f"|-\n|{UG}|{n[0]}\n|"
    blk = re.sub(r"(?m)^\|-\n\|(?!colspan)", row, blk)
    blk = re.sub(r'(\|colspan=")(\d+)(")', lambda m: m.group(1) + str(int(m.group(2)) + 1) + m.group(3), blk)
    return blk, n[0]


def patch(x):
    log = []
    # segment table: inside <div class="gem-segments">
    a = x.find('<div class="gem-segments">')
    if a >= 0:
        b = x.index("\n|}", a)
        blk, n = number_table(x[a:b], None, None)
        if n:
            x = x[:a] + blk + x[b:]; log.append(f"segment table {n}")
    # Background table: the gem-bgbox table, or a bare wikitable headed Segment/Status/Background
    for m in re.finditer(r"(?ms)^\{\|[^\n]*\n(?:\|\+[^\n]*\n)?!(?:style=\"[^\"]*\"\|)?Segment\n!(?:style=\"[^\"]*\"\|)?Status\n!(?:style=\"[^\"]*\"\|)?Background\n.*?^\|\}", x):
        blk, n = number_table(m.group(0), None, None)
        if n:
            x = x[:m.start()] + blk + x[m.end():]; log.append(f"background table {n}")
            break
    # no "Its N segments are in ..." or segment-table pointer sentence (Baird 2026-11-08)
    y = re.sub(r" Its \d+ segments are in [^\n]*?(?:\.)(?= The segment table under| ?\n)", "", x)
    y = re.sub(r" The segment table under Project details lists each segment's start and end points on its Route tab\.", "", y)
    if y != x:
        x = y; log.append("shorter location")
    # See-all line goes after the opening paragraph, not before it
    m = re.search(r"(?m)^(See all Chinese pipeline network groupings \[\[Chinese Gas Pipeline Networks\|here\]\]\.)\n\n(.+)\n", x)
    if m and not m.group(2).startswith("=="):
        x = x[:m.start()] + m.group(2) + "\n\n" + m.group(1) + "\n" + x[m.end():]; log.append("see-all moved")
    # an empty line above Additional sources under a table
    y = re.sub(r"(?m)^(\|\}|</div>)\n+(?=Additional sources:)", r"\1\n\n\n", x)
    if y != x:
        x = y; log.append("blank before sources")
    # serial comma in the lead's status list
    def sc(m):
        items = m.group(2).split(", ")
        if len(items) >= 2 and " and " in items[-1] and ", and " not in m.group(2):
            return m.group(1) + m.group(2).replace(" and ", ", and ", 1) + m.group(3)
        return m.group(0)
    y = re.sub(r"(with segments that are )([^.\n]*?)(\.)", sc, x, count=1)
    if y != x:
        x = y; log.append("serial comma")
    return x, log


def main():
    save = "--save" in sys.argv
    titles = [t for t in open("/tmp/_edited.txt").read().split("\n") if t]
    s = N.GW.session(); ls = N.GW.session(login=True) if save else None
    res = {"changed": [], "skipped": [], "unchanged": 0}
    for t in titles:
        try:
            x = N.GW.page_text(s, t)
        except Exception as e:
            res["skipped"].append((t, f"fetch {e}")); continue
        if not x or x.lstrip().lower().startswith("#redirect"):
            continue
        y, log = patch(x)
        if not log:
            res["unchanged"] += 1; continue
        if save:
            h, hd, errs = G.render(s, t, "x\n\n" + y)
            if errs:
                res["skipped"].append((t, f"cite errors {len(errs)}")); continue
            r = wiki_save.save(ls, t, text=y, summary="number the segments in the tables; shorter location text; see-all line after the lead; serial comma").get("result")
            log.append(str(r))
        res["changed"].append((t, log)); print(t, log, flush=True)
    json.dump(res, open(os.path.join(HERE, "..", "out", "numbering", "result.json"), "w"), indent=1)
    print("changed", len(res["changed"]), "skipped", len(res["skipped"]), "unchanged", res["unchanged"])


main()
