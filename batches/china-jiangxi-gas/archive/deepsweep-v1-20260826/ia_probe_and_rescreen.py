#!/usr/bin/env python3
"""Two passes that are possible while web.archive.org is unreachable but archive.org is up.

`web.archive.org` (207.241.237.3) refuses TCP on 443 and 80 from this network — sandboxed and
not — while `archive.org` (207.241.224.2) answers in ~0.3s. CDX and content serving both live
on the dead host, so `cdx_snapshots.py` cannot run; its earlier 0/17 result is void, not
negative. The availability API lives on the LIVE host, so capture EXISTENCE is still provable
even though capture CONTENT is not readable (the Uzbekistan condition, one host further along).

Pass 1 — availability probe over the 17 unreadable wiki-citation URLs.
Pass 2 — origin re-screen of the harvested citations that were never checked at all. No IA
         involved; this is the part with real yield today.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
import requests
from url_verifier import verify_many

BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")


def origin_of(url: str) -> str:
    """Strip a replay/save wrapper so we ask about the ORIGIN, not the archive address."""
    for marker in ("web.archive.org/web/", "web.archive.org/save/"):
        if marker in url:
            tail = url.split(marker, 1)[1]
            if marker.endswith("web/"):
                return tail.split("/", 1)[1] if "/" in tail else tail
            return tail
    return url


def available(url: str) -> dict:
    try:
        r = requests.get("https://archive.org/wayback/available",
                         params={"url": origin_of(url)}, timeout=20,
                         headers={"User-Agent": BROWSER_UA})
        if r.status_code != 200:
            return {"probe": "error", "detail": f"HTTP {r.status_code}"}
        snap = (r.json().get("archived_snapshots") or {}).get("closest") or {}
        if not snap:
            return {"probe": "no_capture"}
        return {"probe": "capture_exists", "timestamp": snap.get("timestamp"),
                "status": snap.get("status"), "url": snap.get("url")}
    except Exception as e:
        return {"probe": "error", "detail": type(e).__name__}


def main() -> None:
    retry = json.load(open("retry_dead_urls.json"))
    harvested = {c["url"] for p in json.load(open("wiki_citations.json"))["pages"].values()
                 for c in p.get("citations", [])}
    checked = set(json.load(open("wiki_attributed_verified.json"))["url_checks"])

    print(f"=== pass 1: availability probe, {len(retry)} unreadable citation URLs")
    avail = {}
    for u, rec in retry.items():
        avail[u] = {"klass": rec["klass"], **available(u)}
        a = avail[u]
        note = a.get("timestamp") or a.get("detail") or ""
        print(f"  {rec['klass']:15s} {a['probe']:15s} {note:16s} {u[:64]}")
        time.sleep(0.4)
    Path("ia_availability.json").write_text(json.dumps(avail, ensure_ascii=False, indent=2))
    n = sum(1 for v in avail.values() if v["probe"] == "capture_exists")
    print(f"  -> {n}/{len(avail)} have at least one capture (existence only; content unreadable)")

    unchecked = sorted(harvested - checked)
    print(f"\n=== pass 2: origin re-screen, {len(unchecked)} never-checked harvested URLs")
    res = verify_many(unchecked, timeout=25)
    Path("harvest_rescreen.json").write_text(json.dumps(res, ensure_ascii=False, indent=2))
    live = [u for u, r in res.items() if r.get("status") == 200]
    dead = [u for u, r in res.items() if r.get("status") in (404, 410)]
    for u in unchecked:
        r = res[u]
        print(f"  {str(r.get('status')):>5}  {r.get('reason','')[:44]:44} {u[:70]}")
    print(f"\n  live(200) {len(live)}  confirmed-deleted(404/410) {len(dead)}  "
          f"other/access-failure {len(unchecked) - len(live) - len(dead)}")
    print("wrote ia_availability.json + harvest_rescreen.json")


if __name__ == "__main__":
    main()
