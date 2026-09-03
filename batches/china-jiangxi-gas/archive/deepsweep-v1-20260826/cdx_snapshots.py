#!/usr/bin/env python3
"""Enumerate Wayback captures via the CDX API for every citation URL we could not read.

`archive.org/wayback/available` returns at most one "closest" snapshot and answered for
only 2 of 14 unread URLs. The CDX index is the thorough query: it lists every capture with
its status code, so a URL the availability API calls unarchived often has usable 200
captures. Origin-blocked-from-here + a real Wayback capture = cite the origin AND add the
snapshot alongside (never swap it in).
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path

BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")


def cdx(url: str) -> list[dict]:
    import requests
    # strip a replay wrapper so we query the ORIGIN, not the archive address
    if "web.archive.org/web/" in url:
        tail = url.split("web.archive.org/web/", 1)[1]
        url = tail.split("/", 1)[1] if "/" in tail else tail
    if "web.archive.org/save/" in url:
        url = url.split("web.archive.org/save/", 1)[1]
    try:
        r = requests.get("https://web.archive.org/cdx/search/cdx",
                         params={"url": url, "output": "json", "limit": "40",
                                 "fl": "timestamp,original,statuscode,digest,length",
                                 "collapse": "digest"},
                         timeout=20, headers={"User-Agent": BROWSER_UA})
        if r.status_code != 200 or not r.text.strip():
            return []
        rows = r.json()
        if not rows or len(rows) < 2:
            return []
        hdr, *data = rows
        return [dict(zip(hdr, row)) for row in data]
    except Exception as e:
        return [{"error": f"{type(e).__name__}"}]


def main() -> None:
    retry = json.load(open("retry_dead_urls.json"))
    out = {}
    for u, rec in retry.items():
        caps = cdx(u)
        good = [c for c in caps if c.get("statuscode") in ("200", "-")]
        out[u] = {"klass": rec["klass"], "n_captures": len(caps), "usable": good[:6]}
        print(f"{rec['klass']:15s} {u[:70]}")
        if caps and "error" in caps[0]:
            print(f"    CDX error: {caps[0]['error']}")
        elif not caps:
            print("    no captures in the CDX index")
        else:
            print(f"    {len(caps)} captures, {len(good)} with status 200")
            for c in good[:3]:
                print(f"      {c['timestamp']}  len={c.get('length','?'):>7}  "
                      f"https://web.archive.org/web/{c['timestamp']}/{c['original']}"[:120])
        Path("cdx_snapshots.json").write_text(json.dumps(out, ensure_ascii=False, indent=2))
        time.sleep(0.5)
    n = sum(1 for v in out.values() if v["usable"])
    print(f"\n{n}/{len(out)} unread URLs have a usable Wayback capture")
    print("wrote cdx_snapshots.json")


if __name__ == "__main__":
    main()
