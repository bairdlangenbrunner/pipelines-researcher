#!/usr/bin/env python3
"""Verify a [ref] URL before it goes in a workbook: resolves (HTTP 200) and (optionally)
contains expected substrings. ALWAYS rejects GEM surfaces — never self-cite (standing
rule 1) — and theodora.com (never an acceptable reference). Importable:
`from url_verifier import verify_url, verify_many, surface_forms`.

    python scripts/url_verifier.py "https://example.com/x" "Pipeline Name" "2025"
"""
from __future__ import annotations

import argparse
import sys

GEM_HOSTS = ("gem.wiki", "globalenergymonitor")
# Never an acceptable reference (per Baird). Enforced at the verifier, not just the
# harvester, so a theodora URL can never slip into a workbook by any path.
BLOCKLIST_HOSTS = ("theodora.com", "theodora")
_UA = "Mozilla/5.0 (compatible; pipelines-researcher/1.0)"

# per-domain politeness floor for verify_many (seconds between hits to one host)
_MIN_INTERVAL = 1.0


def verify_url(url: str, *expected: str, any_of=None, timeout: int = 20) -> dict:
    """Return {ok, status, reason}. The page must HTTP-200, contain ALL `expected`
    substrings (AND), and — if `any_of` is given — contain AT LEAST ONE of them (OR).
    Use `any_of` for a data value's surface forms (see `surface_forms`); use `expected`
    for context that must always be present. Matching is case-insensitive substring."""
    low = (url or "").lower()
    if not low.startswith("http"):
        return {"ok": False, "status": None, "reason": "not an http(s) URL"}
    if any(h in low for h in GEM_HOSTS):
        return {"ok": False, "status": None, "reason": "GEM surface — never self-cite (standing rule 1)"}
    if any(h in low for h in BLOCKLIST_HOSTS):
        return {"ok": False, "status": None, "reason": "theodora — never an acceptable reference"}
    try:
        import requests
    except ImportError:
        return {"ok": False, "status": None, "reason": "requests not installed (pip install -r requirements.txt)"}
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": _UA})
    except Exception as e:
        return {"ok": False, "status": None, "reason": f"request failed: {type(e).__name__}"}
    if r.status_code != 200:
        return {"ok": False, "status": r.status_code, "reason": f"HTTP {r.status_code}"}
    text = r.text.lower()
    missing = [e for e in expected if e and e.lower() not in text]
    if missing:
        return {"ok": False, "status": 200, "reason": f"200 but missing expected: {missing}"}
    if any_of:
        forms = [a for a in any_of if a]
        if forms and not any(a.lower() in text for a in forms):
            return {"ok": False, "status": 200, "reason": f"200 but data value not found (none of {forms})"}
    return {"ok": True, "status": 200, "reason": "200 + expected content present" if (expected or any_of) else "200"}


def surface_forms(value) -> list[str]:
    """Candidate substrings (OR-matched via `any_of`) for one GEM data value, so a real
    200 that states the value differently isn't a false negative. e.g. '450' →
    ['450', '450,000']; '1,200' → ['1,200', '1200']. Numbers only get reformatted —
    a 200-but-none-present result is exactly the 'link no longer supports the data
    point' case worth flagging. NB substrings can match inside larger numbers; the
    agent makes the final call, so keep these as a screen, not proof."""
    if value is None:
        return []
    raw = str(value).strip()
    if not raw:
        return []
    forms = {raw, raw.lower(), raw.replace(",", "")}
    try:
        from normalize import parse_number
        n = parse_number(raw)
    except Exception:
        n = None
    if n is not None:
        if float(n).is_integer():
            i = int(n)
            forms.add(str(i))
            forms.add(f"{i:,}")
        else:
            forms.add(repr(n).rstrip("0").rstrip("."))
    return [f for f in forms if f]


def verify_many(urls, expected=(), any_of=None, timeout: int = 20, max_workers: int = 6) -> dict:
    """Verify many URLs concurrently — bounded pool + per-domain politeness (≥
    `_MIN_INTERVAL`s between hits to the same host). Returns {url: verify_url result}.
    Deterministic per URL; ordering of hits within a domain is serialized for courtesy."""
    import threading
    import time
    from concurrent.futures import ThreadPoolExecutor
    from urllib.parse import urlparse

    uniq = list(dict.fromkeys(u for u in urls if u))
    lock = threading.Lock()
    next_ok: dict[str, float] = {}  # domain -> earliest monotonic time we may hit it

    def _one(u: str):
        dom = urlparse(u).netloc.lower()
        with lock:
            now = time.monotonic()
            sched = max(now, next_ok.get(dom, 0.0))
            next_ok[dom] = sched + _MIN_INTERVAL
        delay = sched - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        return u, verify_url(u, *expected, any_of=any_of, timeout=timeout)

    out: dict[str, dict] = {}
    if not uniq:
        return out
    with ThreadPoolExecutor(max_workers=min(max_workers, len(uniq))) as ex:
        for u, res in ex.map(_one, uniq):
            out[u] = res
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url")
    ap.add_argument("expected", nargs="*", help="substrings the page must contain")
    args = ap.parse_args()
    res = verify_url(args.url, *args.expected)
    print(("OK   " if res["ok"] else "FAIL ") + f"{args.url}  — {res['reason']}")
    sys.exit(0 if res["ok"] else 1)


if __name__ == "__main__":
    main()
