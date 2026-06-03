#!/usr/bin/env python3
"""Verify a [ref] URL before it goes in a workbook: resolves (HTTP 200) and (optionally)
contains expected substrings. ALWAYS rejects GEM surfaces — never self-cite (standing
rule 1). Importable: `from url_verifier import verify_url`.

    python scripts/url_verifier.py "https://example.com/x" "Pipeline Name" "2025"
"""
from __future__ import annotations

import argparse
import sys

GEM_HOSTS = ("gem.wiki", "globalenergymonitor")
_UA = "Mozilla/5.0 (compatible; pipelines-researcher/1.0)"


def verify_url(url: str, *expected: str, timeout: int = 20) -> dict:
    low = (url or "").lower()
    if not low.startswith("http"):
        return {"ok": False, "status": None, "reason": "not an http(s) URL"}
    if any(h in low for h in GEM_HOSTS):
        return {"ok": False, "status": None, "reason": "GEM surface — never self-cite (standing rule 1)"}
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
    return {"ok": True, "status": 200, "reason": "200 + expected content present" if expected else "200"}


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
