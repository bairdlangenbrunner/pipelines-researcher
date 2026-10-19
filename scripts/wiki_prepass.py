#!/usr/bin/env python3
"""Mechanical pre-pass over a sweep's harvested gem.wiki citations, before any agent runs.

    python scripts/wiki_prepass.py --staging <dir> [--verify] [--write-worklist] [--init-shards]
        [--workers 6] [--pids P0765,P2380]

Reads, in `<dir>`: `worklist_full.json` (every unit on the scope), `wiki_citations.json`
(harvest_wiki_citations.py, one page per ProjectID, each citation with its `inline` body
context) and `wiki_attributed.json` (attribute_wiki.py, each details bullet joined to a
ref column with its `value_parts`). Writes `wiki_prepass.json` and, on request, the lean
`worklist.json` + `deferred_units.json` pair and one shard per ProjectID with the
mechanical `wiki_citations_read` records already in it.

Why (2026-10-17, P0765 TurkStream): the wiki page said `Cost: US$7.8 billion` with an RFE/RL
citation that states the figure and passes every check, and the harvest carried that URL
all along, but nothing told the agent WHICH unit it backed; the agent closed the cost from
an open-web search at low. This script does the joining and the first verification pass
by machine, so an agent starts each citation knowing the wiki value it supports, whether
the page still loads, whether it names the pipeline, and whether the sheet's value (or the
wiki's) already appears in its text.

What it does per citation:

1. Join. A citation attributed to a ref column (`wiki_attributed.json`) joins every unit of
   that ProjectID on that column; a citation with inline body context but no bullet joins
   the row as prose (`prose` bucket); a geometry-only link (openstreetmap.org, a map tile)
   is pre-marked `no_value` in the ledger and needs no agent read.
2. Compare. The wiki value is compared to the sheet's value for the unit (status, capacity,
   length, diameter, start year, entities via wiki_alignment's comparers; numbers otherwise).
3. Verify (`--verify`). Each URL is fetched ONCE through url_verifier (so the fetch.py ladder
   runs on a bot wall), screened for the pipeline's name forms (PipelineName, SegmentName,
   OtherEnglishNames), the sheet value's surface forms, and the wiki value's surface forms.
   A URL that does not load is run through the Wayback CDX index (`ref_recheck.wayback_capture`);
   a capture is kept as `read_via` so the agent reads the archived copy. No capture → the
   ledger record is pre-written as `dead` or `blocked` with the full `tried` ladder.
4. Bucket. `verifying` (loads, names the pipeline, states the sheet value), `wiki_differs`
   (loads, states the wiki value, which is not the sheet's), `loads_unchecked` (loads, but
   the screen found neither value: an agent reads it), `prose`, `dead`, `blocked`, `geometry`.

Nothing here stages a fill: the agent still opens every readable citation and writes the
record. The pre-pass only decides which citations are machine-settled (dead with no
capture, blocked with no capture, pure geometry) and gives the agent the rest with the
screening attached. Standing rule 1 holds: gem.wiki is visited, never cited.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_shard_coverage import _norm_url  # noqa: E402
from url_verifier import BLOCKLIST_HOSTS, GEM_HOSTS, name_forms, surface_forms, verify_many  # noqa: E402

GEOMETRY_HOSTS = ("openstreetmap.org", "osm.org", "tile.", "arcgis.com/apps", "google.com/maps",
                  "maps.google", "overpass")
_VALUE_COL_OF_REF = {
    "Status [ref]": "Status", "Capacity [ref]": "Capacity", "Length [ref]": "LengthKnown",
    "Diameter [ref]": "Diameter", "Start [ref]": "StartYear1", "SegmentCost [ref]": "SegmentCost",
    "ProjectLevelCost [ref]": "ProjectLevelCost", "Operator [ref]": "Operator", "Owner [ref]": "Owner",
    "Parent [ref]": "Parent", "Fuel [ref]": "Fuel", "PipelineType [ref]": "PipelineType",
    "Proposal [ref]": "ProposalYear", "Construction [ref]": "ConstructionYear",
    "Cancelled [ref]": "CancelledYear", "Shelved [ref]": "ShelvedYear",
}


# -- comparison --------------------------------------------------------------------------------

def _s(v) -> str:
    return "" if v is None else str(v).strip()


def compare(ref_col: str, wiki_value: str, unit: dict) -> dict:
    """{match: True|False|None, sheet: <sheet rendering>, wiki: <wiki rendering>} for one
    attributed wiki bullet against one unit's sheet values. None = not comparable (a blank
    on either side, or no parser for the column)."""
    from wiki_alignment import (_cmp_capacity, _cmp_diameter, _cmp_entities, _cmp_length,
                                _cmp_start_year, _cmp_status)
    from normalize import parse_number
    vals = unit.get("values") or {}
    pseudo_row = dict(vals)
    oo = {}
    if ref_col == "Capacity [ref]":
        fn = _cmp_capacity
    elif ref_col == "Length [ref]":
        fn = _cmp_length
        km = parse_number(vals.get("LengthKnown"))
        if km is not None and _s(vals.get("LengthKnownUnits")).lower().startswith("mi"):
            km = km * 1.609344
        pseudo_row["LengthKnownKm"] = "" if km is None else f"{km:g}"
    elif ref_col == "Diameter [ref]":
        fn = _cmp_diameter
    elif ref_col == "Start [ref]":
        fn = _cmp_start_year
    elif ref_col == "Status [ref]":
        fn = _cmp_status
    elif ref_col in ("Operator [ref]", "Owner [ref]", "Parent [ref]"):
        col = ref_col.split(" ")[0]
        fn = _cmp_entities(col)
        if col == "Owner":
            owners = [_s(v) for k, v in vals.items() if re.fullmatch(r"Owner\d*", k) and _s(v)]
            pseudo_row["Owner"] = "; ".join(owners)
        oo = {col: _s(vals.get(col))}
    else:
        sheet_col = _VALUE_COL_OF_REF.get(ref_col)
        sheet = _s(vals.get(sheet_col)) if sheet_col else ""
        if not sheet or not wiki_value:
            return {"match": None, "sheet": sheet, "wiki": wiki_value}
        a, b = parse_number(sheet), parse_number(wiki_value)
        if a is None or b is None:
            return {"match": (sheet.lower() == wiki_value.lower()), "sheet": sheet, "wiki": wiki_value}
        if ref_col in ("SegmentCost [ref]", "ProjectLevelCost [ref]"):
            # the wiki writes "US$7.8 billion"; the sheet holds the full figure
            scale = 1e9 if re.search(r"\bb(?:illio)?n\b", wiki_value, re.I) else \
                1e6 if re.search(r"\bm(?:illio)?n\b|mln", wiki_value, re.I) else 1.0
            b = b * scale
        return {"match": abs(a - b) <= 0.01 * max(abs(a), abs(b), 1.0), "sheet": sheet, "wiki": wiki_value}
    try:
        m, sn, wn = fn(pseudo_row, wiki_value, oo)
    except Exception:   # noqa: BLE001 — a parser hiccup is "not comparable", never a crash
        return {"match": None, "sheet": "", "wiki": wiki_value}
    return {"match": m, "sheet": sn, "wiki": wn}


# -- needles -----------------------------------------------------------------------------------

def unit_needles(unit: dict) -> list[str]:
    """Surface forms of every value the unit carries (the sheet's figures)."""
    out: list[str] = []
    for k, v in (unit.get("values") or {}).items():
        if k.endswith("Units") or not _s(v):
            continue
        out.extend(surface_forms(v))
    return _drop_year_commas(list(dict.fromkeys(out)))


def _drop_year_commas(forms: list[str]) -> list[str]:
    """surface_forms writes 2020 as '2,020' too; a year is never written that way."""
    return [f for f in forms if not re.fullmatch(r"(?:19|20),\d{3}", f)]


def wiki_needles(wiki_value: str) -> list[str]:
    forms = list(surface_forms(wiki_value))
    for m in re.findall(r"\d[\d,]*(?:\.\d+)?", wiki_value or ""):
        forms.extend(surface_forms(m))
    return _drop_year_commas(list(dict.fromkeys(f for f in forms if f)))


def row_name_forms(unit: dict, sheet_row: dict | None) -> list[str]:
    names = [unit.get("pipeline_name") or ""]
    seg = unit.get("segment_name") or ""
    if seg:
        names.append(f"{unit.get('pipeline_name') or ''} {seg}".strip())
    if sheet_row:
        for col in ("OtherEnglishNames", "OtherLanguagePrimaryPipelineName", "OtherLanguageSegmentName",
                    "OtherLanguageAlternativePipelineNames"):
            for alt in re.split(r"[;,/]| \| ", _s(sheet_row.get(col))):
                if len(alt.strip()) > 3:
                    names.append(alt.strip())
    out: list[str] = []
    for n in names:
        out.extend(name_forms(n))
        # the name without the "Gas Pipeline" tail: pages say "TurkStream", not the GEM label
        bare = re.sub(r"\b(gas|oil|ngl|crude)?\s*(pipeline|gas pipeline)\b", "", n, flags=re.I).strip(" -")
        if len(bare) > 3:
            out.extend(name_forms(bare))
    return list(dict.fromkeys(o for o in out if o and len(o) > 3))


def _text_has(text: str, needles: list[str]) -> list[str]:
    low = text.lower()
    return [n for n in needles if n and n.lower() in low]


# -- the pass ----------------------------------------------------------------------------------

def is_geometry(url: str) -> bool:
    low = (url or "").lower()
    return any(h in low for h in GEOMETRY_HOSTS)


def load_sheet_rows(staging: Path, wl: dict) -> dict[str, dict]:
    """ProjectID -> first backend row (for alias columns); empty when the CSV is missing."""
    try:
        from merge_qc import load_sheet
        sheet = load_sheet(wl.get("scope"))
    except Exception:   # noqa: BLE001
        return {}
    if sheet is None:
        return {}
    out: dict[str, dict] = {}
    for (pid, _row), rec in sheet.backend.items():
        out.setdefault(pid, rec)
    return out


def build(staging: Path, pids_filter: set[str] | None, verify: bool, workers: int,
          wayback: bool = True, timeout: int = 25) -> dict:
    wl = json.loads((staging / "worklist_full.json").read_text())
    cites = json.loads((staging / "wiki_citations.json").read_text()).get("pages") or {}
    attr_path = staging / "wiki_attributed.json"
    attributions = json.loads(attr_path.read_text()).get("attributions") or [] if attr_path.exists() else []
    sheet_rows = load_sheet_rows(staging, wl)

    units_by_pid: dict[str, list[dict]] = collections.defaultdict(list)
    for u in wl.get("units") or []:
        units_by_pid[u["project_id"]].append(u)

    # (pid, norm_url) -> [attribution]
    attr_by: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    for a in attributions:
        for url in a.get("candidate_urls") or []:
            attr_by[(a["project_id"], _norm_url(url))].append(a)

    cands: list[dict] = []          # one per (pid, citation)
    for pid, page in sorted(cites.items()):
        if pids_filter and pid not in pids_filter:
            continue
        units = units_by_pid.get(pid) or []
        if not units:
            continue
        row = sheet_rows.get(pid)
        names = row_name_forms(units[0], row)
        for c in page.get("citations") or []:
            url = c.get("url") or ""
            key = _norm_url(url)
            attrs = attr_by.get((pid, key), [])
            joined: list[dict] = []
            for a in attrs:
                for u in units:
                    if u.get("ref_col") != a["ref_col"]:
                        continue
                    # which figure THIS footnote supports when the bullet lists several
                    wiki_value = a.get("wiki_value") or ""
                    for pt in a.get("value_parts") or []:
                        if any(_norm_url(x) == key for x in pt.get("urls") or []):
                            wiki_value = pt.get("text") or wiki_value
                            break
                    cmp = compare(a["ref_col"], wiki_value, u)
                    joined.append({
                        "ref_col": a["ref_col"], "sheet_row": u.get("sheet_row"),
                        "tab": u.get("tab", "backend"), "unit_class": u.get("class"),
                        "wiki_label": a.get("wiki_label"), "wiki_value": wiki_value,
                        "wiki_section": a.get("wiki_section"),
                        "sheet_values": u.get("values") or {}, "compare": cmp,
                        "sheet_needles": unit_needles(u), "wiki_needles": wiki_needles(wiki_value),
                    })
            cand = {
                "project_id": pid, "url": url, "cite_id": c.get("cite_id"),
                "link_text": c.get("link_text") or "", "context": c.get("context") or "",
                "inline": c.get("inline") or [], "units": joined,
                "name_forms": names,
                "bucket": "geometry" if is_geometry(url) else ("attributed" if joined else "prose"),
            }
            cands.append(cand)

    if verify:
        _verify(cands, workers=workers, wayback=wayback, timeout=timeout)

    summary = collections.Counter(c["bucket"] for c in cands)
    return {
        "generated": time.strftime("%Y-%m-%d %H:%M"),
        "staging": str(staging), "verified": verify,
        "summary": dict(summary), "n_candidates": len(cands),
        "n_pids": len({c["project_id"] for c in cands}),
        "candidates": cands,
    }


def _verify(cands: list[dict], workers: int, wayback: bool, timeout: int,
            wayback_attempts: int = 4) -> None:
    """Fetch every distinct URL once; screen the text for name, sheet-value and wiki-value
    needles per candidate; run the Wayback ladder on failures."""
    from fetch import fetch_page
    from ref_recheck import wayback_lookup

    urls = list(dict.fromkeys(c["url"] for c in cands if c["bucket"] != "geometry"))
    print(f"  verifying {len(urls)} distinct URLs ({workers} workers)...", file=sys.stderr)
    results = verify_many(urls, timeout=timeout, max_workers=workers)

    # url_verifier does not hand back the page text, so re-read loaded pages through
    # fetch.py (cached per URL here) for the needle screen.
    text_cache: dict[str, str] = {}

    def page_text(u: str) -> str:
        if u in text_cache:
            return text_cache[u]
        try:
            p = fetch_page(u, timeout=timeout + 10)
            txt = p.text or ""
            if not p.is_pdf:
                txt = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", txt, flags=re.S | re.I)
                txt = re.sub(r"<[^>]+>", " ", txt)
            txt = " ".join(txt.split())
        except Exception:   # noqa: BLE001
            txt = ""
        text_cache[u] = txt
        return txt

    capture_cache: dict[str, str | None] = {}
    capture_state: dict[str, str] = {}
    for c in cands:
        if c["bucket"] == "geometry":
            c["ledger"] = {"url": c["url"], "outcome": "no_value",
                           "note": "Map or geometry link only (no data values on the page); "
                                   "route evidence belongs to the routes repo, not a [ref] cell."}
            continue
        r = results.get(c["url"]) or {}
        c["verify"] = {k: r.get(k) for k in ("ok", "status", "reason", "blocked", "js_shell", "pdf",
                                             "fetch_route", "final_url")}
        loads = bool(r.get("ok")) or (str(r.get("status")) == "200" and not r.get("blocked") and not r.get("js_shell"))
        read_url = c["url"]
        if not loads:
            snap = None
            if wayback:
                if c["url"] not in capture_cache:
                    # a lookup that ERRORED (index unreachable, 429) is not "no capture": retry it
                    # with a pause before giving up, and record the state so a later --retry-failed
                    # pass knows which failures were never really answered (P0765: the Reuters
                    # citation had a 2022 capture that the first lookup missed).
                    snap, state = wayback_lookup(c["url"], attempts=wayback_attempts)
                    if state == "error":
                        time.sleep(3)
                        snap, state = wayback_lookup(c["url"], attempts=wayback_attempts)
                    capture_cache[c["url"]] = snap
                    capture_state[c["url"]] = state
                snap = capture_cache[c["url"]]
            tried = ["url_verifier (requests → scripts/fetch.py ladder: curl → curl_cffi → clearance cookie)",
                     "Wayback CDX index (statuscode:200, newest first)" if wayback else "Wayback not attempted"]
            if snap:
                c["read_via"] = snap
                read_url = snap
            else:
                status = r.get("status")
                blocked = bool(r.get("blocked") or r.get("js_shell") or str(status) in ("401", "403", "429"))
                c["bucket"] = "blocked" if blocked else "dead"
                c["wayback_state"] = capture_state.get(c["url"], "not_attempted")
                c["ledger"] = {"url": c["url"], "outcome": c["bucket"], "tried": tried,
                               "note": f"{'Blocked' if blocked else 'Does not load'} (status {status}, "
                                       f"{_s(r.get('reason'))[:160]}); no Wayback capture answering 200."}
                continue
        text = page_text(read_url)
        if not text:
            c["bucket"] = "loads_unchecked"
            c["screen"] = {"name": [], "sheet": {}, "wiki": {}, "text_chars": 0}
            continue
        name_hits = _text_has(text, c["name_forms"])
        sheet_hits: dict[str, list[str]] = {}
        wiki_hits: dict[str, list[str]] = {}
        for i, u in enumerate(c["units"]):
            sheet_hits[str(i)] = _text_has(text, u["sheet_needles"])
            wiki_hits[str(i)] = _text_has(text, u["wiki_needles"])
        c["screen"] = {"name": name_hits[:5], "sheet": sheet_hits, "wiki": wiki_hits,
                       "text_chars": len(text)}
        if c["units"]:
            any_sheet = any(sheet_hits.values())
            any_wiki = any(wiki_hits.values())
            differs = any(u["compare"].get("match") is False for u in c["units"])
            if any_sheet and name_hits:
                c["bucket"] = "verifying"
            elif any_wiki and differs:
                c["bucket"] = "wiki_differs"
            elif any_sheet or any_wiki:
                c["bucket"] = "verifying" if not differs else "wiki_differs"
            else:
                c["bucket"] = "loads_unchecked"
        else:
            c["bucket"] = "prose"


def _definitive(c: dict) -> bool:
    """A failure that was really answered: a 404/410 and an archive index that said no capture."""
    st = str((c.get("verify") or {}).get("status"))
    return st in ("404", "410") and c.get("wayback_state") == "none"


def _restore(sub: list[dict], originals: dict | None) -> None:
    """A killed chunk was never answered: put its candidates back exactly as they were."""
    for c in sub:
        o = (originals or {}).get(id(c))
        if o is not None:
            c.clear()
            c.update(o)


def _verify_isolated(cands: list[dict], workers: int, timeout: int, wayback_attempts: int,
                     chunk_urls: int = 6, deadline: int = 600, originals: dict | None = None) -> None:
    """Run `_verify` over chunks of URLs, each in a forked child with a hard deadline.

    A socket that hangs with no read timeout froze the whole retry for hours (2026-10-18); a child
    that overruns its deadline is killed and its candidates keep their failed bucket for the next round."""
    import multiprocessing as mp
    import tempfile
    urls = list(dict.fromkeys(c["url"] for c in cands))
    for i in range(0, len(urls), chunk_urls):
        group = set(urls[i:i + chunk_urls])
        sub = [c for c in cands if c["url"] in group]
        snap = json.dumps(sub, ensure_ascii=False)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
            tmp = tf.name

        def child(tmp=tmp, sub=sub):
            _verify(sub, workers=workers, wayback=True, timeout=timeout, wayback_attempts=wayback_attempts)
            Path(tmp).write_text(json.dumps(sub, ensure_ascii=False))

        pr = mp.get_context("fork").Process(target=child, daemon=True)
        pr.start()
        pr.join(deadline)
        if pr.is_alive():
            pr.kill()
            pr.join()
            print(f"  chunk {i // chunk_urls + 1}: killed after {deadline}s; {len(group)} URLs stay failed",
                  file=sys.stderr)
            _restore(sub, originals)
        else:
            try:
                new = json.loads(Path(tmp).read_text())
                for c, n in zip(sub, new):
                    c.clear()
                    c.update(n)
            except (OSError, json.JSONDecodeError):
                print(f"  chunk {i // chunk_urls + 1}: child gave no result", file=sys.stderr)
                _restore(sub, originals)
        Path(tmp).unlink(missing_ok=True)
        print(f"  chunk {i // chunk_urls + 1}/{-(-len(urls) // chunk_urls)} done", file=sys.stderr, flush=True)


# hosts Baird confirmed are blocked for his IP (2026-10-19): they stay in the failed list, never retried
RETRY_SKIP_HOSTS = ("energybase.ru", "gazprom.com")


def _skip_retry(url: str, hosts) -> bool:
    h = (urlsplit(url).hostname or "").lower()
    return any(h == x or h.endswith("." + x) for x in hosts)


def retry_failed(pre: dict, workers: int, timeout: int, rounds: int, pause: int,
                 save_to: Path | None = None, skip_hosts=RETRY_SKIP_HOSTS) -> dict:
    """Re-open every dead/blocked citation whose failure may be transient, with growing patience.

    Each round resets the failed candidates to their pre-verify bucket, re-runs the live check
    (fresh cache) and the Wayback ladder with 8 attempts each, and stops early when nothing is left
    that could still change. A 404/410 with an archive index that answered "no capture" is a real
    answer and is not retried."""
    for rnd in range(1, rounds + 1):
        failed = [c for c in pre["candidates"]
                  if c["bucket"] in ("dead", "blocked") and not _definitive(c)
                  and not _skip_retry(c["url"], skip_hosts)]
        print(f"retry round {rnd}/{rounds}: {len(failed)} failed citations "
              f"({len({c['url'] for c in failed})} distinct URLs)", file=sys.stderr)
        if not failed:
            break
        before = collections.Counter(c["bucket"] for c in failed)
        originals = {id(c): json.loads(json.dumps(c)) for c in failed}
        for c in failed:
            c["bucket"] = "attributed" if c["units"] else "prose"
            c.pop("ledger", None)
            c.pop("read_via", None)
        _verify_isolated(failed, workers=workers, timeout=timeout, wayback_attempts=3, originals=originals)
        after = collections.Counter(c["bucket"] for c in failed)
        recovered = sum(v for k, v in after.items() if k not in ("dead", "blocked"))
        still = {k: v for k, v in after.items() if k in ("dead", "blocked")}
        print(f"  round {rnd}: {recovered} of {len(failed)} recovered; was {dict(before)}, still failing {still}",
              file=sys.stderr)
        if save_to:   # progress survives a stall or a killed run
            pre["summary"] = dict(collections.Counter(c["bucket"] for c in pre["candidates"]))
            save_to.write_text(json.dumps(pre, ensure_ascii=False, indent=1))
        if rnd < rounds and any(c["bucket"] in ("dead", "blocked") and not _definitive(c) for c in failed):
            time.sleep(pause * rnd)
    pre["summary"] = dict(collections.Counter(c["bucket"] for c in pre["candidates"]))
    pre["retried"] = time.strftime("%Y-%m-%d %H:%M")
    return pre


# -- outputs -----------------------------------------------------------------------------------

def write_worklist(staging: Path, pre: dict) -> dict:
    """Lean worklist: units with at least one readable wiki candidate on their ref column
    stay owed; every other unit is deferred with `defer_reason: no_wiki_candidate`."""
    wl = json.loads((staging / "worklist_full.json").read_text())
    owed_keys: set[tuple] = set()
    for c in pre["candidates"]:
        if c["bucket"] in ("dead", "blocked", "geometry"):
            continue
        for u in c["units"]:
            owed_keys.add((c["project_id"], u["ref_col"], str(u.get("sheet_row"))))
    owed, deferred = [], []
    for u in wl["units"]:
        k = (u["project_id"], u["ref_col"], str(u.get("sheet_row")))
        if k in owed_keys:
            owed.append(u)
        else:
            deferred.append({**u, "defer_reason": "no_wiki_candidate"})
    scope = dict(wl.get("scope") or {})
    scope["lean"] = True
    scope["wiki_only"] = True
    out = {"scope": scope, "summary": {**(wl.get("summary") or {}), "lean_owed": len(owed),
                                       "lean_deferred": len(deferred), "lean_mode": "wiki_only"},
           "units": owed}
    (staging / "worklist.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    (staging / "deferred_units.json").write_text(json.dumps(
        {"scope": scope, "units": deferred}, ensure_ascii=False, indent=1))
    summ = {"full_units": len(wl["units"]), "owed_units": len(owed), "deferred_units": len(deferred),
            "owed_pids": len({u["project_id"] for u in owed}),
            "all_pids": len({u["project_id"] for u in wl["units"]}),
            "owed_by_ref_col": dict(collections.Counter(u["ref_col"] for u in owed)),
            "mode": "wiki_only"}
    (staging / "lean_summary.json").write_text(json.dumps(summ, indent=1))
    return summ


def init_shards(staging: Path, pre: dict) -> dict:
    """One shard per ProjectID on the scope (worklist_full), with the machine-settled
    ledger records (dead / blocked with no capture, geometry) upserted."""
    import shard_upsert as su
    wl = json.loads((staging / "worklist_full.json").read_text())
    pids = sorted({u["project_id"] for u in wl["units"]})
    ledger_by_pid: dict[str, list[dict]] = collections.defaultdict(list)
    for c in pre["candidates"]:
        if c.get("ledger"):
            ledger_by_pid[c["project_id"]].append(c["ledger"])
    rows = staging / "rows"
    rows.mkdir(exist_ok=True)
    n_new = n_rec = 0
    for pid in pids:
        path = rows / f"{pid}.json"
        existed = path.exists()
        shard = su._read(path, staging, pid)
        shard.setdefault(su.WIKI_KEY, [])
        recs = ledger_by_pid.get(pid, [])
        if recs:
            a, r = su.upsert(shard, su.WIKI_KEY, recs)
            n_rec += a + r
        su._write(path, shard)
        n_new += 0 if existed else 1
    return {"shards": len(pids), "new": n_new, "ledger_records": n_rec}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True)
    ap.add_argument("--pids", help="comma-separated ProjectIDs (debug)")
    ap.add_argument("--verify", action="store_true", help="fetch and screen every citation URL")
    ap.add_argument("--no-wayback", action="store_true", help="skip the Wayback CDX ladder on failures")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=25)
    ap.add_argument("--write-worklist", action="store_true",
                    help="write worklist.json / deferred_units.json / lean_summary.json")
    ap.add_argument("--init-shards", action="store_true",
                    help="create rows/<PID>.json for every PID with the machine-settled ledger records")
    ap.add_argument("--out", help="default <staging>/wiki_prepass.json")
    ap.add_argument("--retry-failed", action="store_true",
                    help="load the existing wiki_prepass.json and re-open every dead/blocked citation "
                         "persistently (live check + Wayback with 8 attempts each, several rounds)")
    ap.add_argument("--retry-rounds", type=int, default=4)
    ap.add_argument("--retry-pause", type=int, default=90, help="seconds before round 2 (grows per round)")
    a = ap.parse_args()

    staging = Path(a.staging)
    pids = {p.strip() for p in a.pids.split(",") if p.strip()} if a.pids else None
    out = Path(a.out) if a.out else staging / "wiki_prepass.json"
    if a.retry_failed:
        pre = retry_failed(json.loads(out.read_text()), workers=min(a.workers, 3), timeout=a.timeout,
                           rounds=a.retry_rounds, pause=a.retry_pause, save_to=out)
    else:
        pre = build(staging, pids, verify=a.verify, workers=a.workers, wayback=not a.no_wayback,
                    timeout=a.timeout)
    out.write_text(json.dumps(pre, ensure_ascii=False, indent=1))
    print(f"wrote {out}: {pre['n_candidates']} candidates on {pre['n_pids']} PIDs")
    for k, v in sorted(pre["summary"].items()):
        print(f"  {k:16s} {v}")
    if a.write_worklist:
        s = write_worklist(staging, pre)
        print(f"worklist.json: {s['owed_units']} owed on {s['owed_pids']}/{s['all_pids']} PIDs; "
              f"{s['deferred_units']} deferred (no_wiki_candidate)")
    if a.init_shards:
        s = init_shards(staging, pre)
        print(f"shards: {s['shards']} ({s['new']} new), {s['ledger_records']} ledger records upserted")


if __name__ == "__main__":
    main()
