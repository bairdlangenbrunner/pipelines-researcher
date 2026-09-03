#!/usr/bin/env python3
"""Second-pass liveness for the citation URLs the first screen could not read.

The first pass used url_verifier's `_UA` ("Mozilla/5.0 (compatible; pipelines-researcher/1.0)")
with no inter-request delay. Against Chinese provincial-government and news hosts that
produces exactly the documented liveness false-negative family: HTTP 567/403 bot-walls,
ConnectionError, and ConnectTimeout — none of which is a deletion. So retry with a real
browser UA, serially, with a delay and a second attempt, and for anything still unread ask
the Wayback availability API for a snapshot to cite ALONGSIDE (never instead of) the origin.

Only HTTP 404/410 may ever drop a ref. Everything else that stays unread is an ACCESS
FAILURE, recorded as such.
"""
from __future__ import annotations
import json, sys, time
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
import url_verifier as UV
from url_verifier import _match_surface, _blocked_as

BROWSER_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36")
HDRS = {"User-Agent": BROWSER_UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}


def try_get(url: str, timeout: int = 30):
    import requests
    for verify in (True, False):
        try:
            r = requests.get(url, timeout=timeout, headers=HDRS, verify=verify,
                             allow_redirects=True)
            return r, verify
        except Exception as e:
            last = e
            if not ("SSL" in type(e).__name__ or "certificate" in str(e).lower()):
                break
    return last, None


def wayback(url: str) -> dict | None:
    import requests
    try:
        r = requests.get("https://archive.org/wayback/available",
                         params={"url": url}, timeout=30,
                         headers={"User-Agent": BROWSER_UA})
        if r.status_code != 200:
            return None
        snap = (r.json().get("archived_snapshots") or {}).get("closest")
        return snap if snap and snap.get("available") else None
    except Exception:
        return None


def main() -> None:
    d = json.load(open("wiki_attributed_verified.json"))
    dead = [u for u, f in d["url_checks"].items() if not f["live"]]
    print(f"retrying {len(dead)} unread URLs with a browser UA, serially\n")
    res = {}
    for u in dead:
        r, verify = try_get(u)
        rec: dict = {"url": u}
        if not hasattr(r, "status_code"):
            rec.update(live=False, status=None, klass="ACCESS_FAILURE",
                       reason=f"request failed: {type(r).__name__}")
        else:
            rec["status"] = r.status_code
            rec["insecure_tls"] = (verify is False)
            if r.status_code in (404, 410):
                rec.update(live=False, klass="DELETED", reason=f"HTTP {r.status_code} — confirmed deletion")
            elif r.status_code != 200:
                rec.update(live=False, klass="ACCESS_FAILURE", reason=f"HTTP {r.status_code}")
            else:
                if (r.encoding or "").lower() in ("iso-8859-1", "ascii") and r.apparent_encoding:
                    r.encoding = r.apparent_encoding
                text = _match_surface(r.text or "")
                blocked = _blocked_as(text)
                if blocked:
                    rec.update(live=False, klass="ACCESS_FAILURE",
                               reason=f"200 block interstitial ({blocked!r})")
                else:
                    rec.update(live=True, klass="LIVE", chars=len(text),
                               stub=len(text) < UV._MIN_BODY_CHARS, reason="200")
        if not rec["live"] and rec["klass"] != "DELETED":
            time.sleep(1.0)
            snap = wayback(u)
            if snap:
                rec["wayback"] = {"url": snap.get("url"), "timestamp": snap.get("timestamp")}
        elif rec["klass"] == "DELETED":
            time.sleep(1.0)
            snap = wayback(u)
            if snap:
                rec["wayback"] = {"url": snap.get("url"), "timestamp": snap.get("timestamp")}
        res[u] = rec
        wb = rec.get("wayback")
        print(f"  {rec['klass']:15s} {str(rec.get('status') or '-'):>4}  {u[:66]}")
        if wb:
            print(f"      wayback {wb['timestamp']}  {wb['url'][:88]}")
        time.sleep(1.5)

    Path("retry_dead_urls.json").write_text(json.dumps(res, ensure_ascii=False, indent=2))
    import collections
    print("\n=== second-pass classes ===")
    for k, n in collections.Counter(v["klass"] for v in res.values()).most_common():
        print(f"  {k:16s} {n}")
    print(f"  with a Wayback snapshot available: {sum(1 for v in res.values() if v.get('wayback'))}")
    print("\nwrote retry_dead_urls.json")


if __name__ == "__main__":
    main()
