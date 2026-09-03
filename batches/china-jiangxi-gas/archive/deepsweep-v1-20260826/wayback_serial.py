#!/usr/bin/env python3
"""Serial Wayback lookup for the 17 unreachable/deleted citation URLs.

REPLACES `cdx_snapshots.py`, whose "0/17 usable captures" output was an ARTIFACT: a
17-query CDX sweep rate-limited our own IP, after which archive.org itself
ConnectTimeout'ed. That is the sweep SOP's own rule (`docs/sops/sweep.md:200`) — never
fan out verification at web.archive.org. So: one request at a time, PAUSE between every
one, availability API first (cheap) and CDX only as a fallback, and never in parallel.

A returned snapshot is not trusted until its bytes are fetched through the `id_` raw
modifier and found non-trivial — CLAUDE.md's archiving rule, which exists because SPN's
interstitial returns HTTP 200 while capturing nothing.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from url_verifier import _UA  # noqa: E402

PAUSE = 5.0          # between archive.org requests; deliberately generous
H = {"User-Agent": _UA}


def get(url, **kw):
    time.sleep(PAUSE)
    return requests.get(url, headers=H, timeout=30, **kw)


def availability(url):
    r = get("https://archive.org/wayback/available", params={"url": url})
    r.raise_for_status()
    snap = (r.json().get("archived_snapshots") or {}).get("closest") or {}
    return snap.get("url") if snap.get("available") else None


def cdx(url):
    r = get("http://web.archive.org/cdx/search/cdx",
            params={"url": url, "output": "json", "limit": "-5",
                    "filter": "statuscode:200", "collapse": "digest"})
    r.raise_for_status()
    rows = r.json()
    if len(rows) < 2:
        return None
    ts, orig = rows[-1][1], rows[-1][2]
    return f"https://web.archive.org/web/{ts}/{orig}"


def confirm(snap_url):
    """Fetch the capture's RAW bytes (`id_`) and require real content."""
    raw = snap_url.replace("/web/", "/web/", 1)
    parts = raw.split("/web/", 1)
    if len(parts) == 2:
        ts, rest = parts[1].split("/", 1)
        raw = f"{parts[0]}/web/{ts}id_/{rest}"
    try:
        r = get(raw, allow_redirects=True)
    except Exception as e:
        return False, f"raw fetch failed: {type(e).__name__}", None
    n = len(r.content or b"")
    return (r.status_code == 200 and n > 1500), f"raw {r.status_code}, {n}B", n


def main():
    dead = json.loads(Path("retry_dead_urls.json").read_text())
    urls = [u for u in dead if not u.startswith("https://web.archive.org/save/")]
    out = {}
    outp = Path("wayback_serial.json")
    for i, u in enumerate(urls, 1):
        rec = {"url": u, "prior_class": dead[u].get("klass")}
        try:
            snap = availability(u)
            rec["via"] = "availability"
            if not snap:
                snap = cdx(u)
                rec["via"] = "cdx"
            rec["snapshot"] = snap
            if snap:
                okb, detail, nbytes = confirm(snap)
                rec.update(usable=okb, confirm=detail, bytes=nbytes)
            else:
                rec.update(usable=False, confirm="no capture in either index")
        except Exception as e:
            rec.update(snapshot=None, usable=False,
                       confirm=f"LOOKUP FAILED ({type(e).__name__}) — not a finding, retry")
        out[u] = rec
        print(f"{i:2d}/{len(urls)} usable={str(rec.get('usable')):5s} "
              f"{rec.get('confirm','')[:34]:36s} {u[:70]}", flush=True)
        outp.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    n = sum(1 for r in out.values() if r.get("usable"))
    print(f"\n{n}/{len(urls)} URLs have a CONFIRMED usable Wayback capture")


if __name__ == "__main__":
    main()
