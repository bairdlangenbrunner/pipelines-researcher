#!/usr/bin/env python3
"""Verify a [ref] URL before it goes in a workbook: resolves (HTTP 200) and (optionally)
contains expected substrings. ALWAYS rejects GEM surfaces — never self-cite (standing
rule 1) — and blocklisted tertiary aggregators (theodora.com; A Barrel Full /
abarrelfull.wikidot.com and the wider wikidot.com platform) which are never acceptable
references. Importable:
`from url_verifier import verify_url, verify_many, surface_forms`.

    python scripts/url_verifier.py "https://example.com/x" "Pipeline Name" "2025"

A FAIL is NOT proof the source is dead, and — critically — a "value not found" FAIL is NOT proof
the page fails to support the data point. The substring check is a SCREEN, not the verdict; the
agent reads the page and makes the final call. Two false-negative families:

Liveness false-negatives (rule out before classing DEAD_LINK — Iraq gas sweep: 6 of 27 "dead
links" were false):
  * 401 bot-walls — live pages (e.g. iraq-businessnews.com) reject this UA; confirm manually and
    cite the Wayback snapshot (which passes) instead.
  * ligature-encoded (esp. Arabic) PDFs — the "contains value" substring check can't read
    contiguous Arabic; verify with `pdftotext` before discarding.
  * LARGE PDFs — the extractor does not reach the whole document. The OPEC ASB2012 Wayback
    PDF (7.7 MB, ~200pp) passes on "OPEC" and FAILS on "Jakhira", a token that is provably
    in it. On a big PDF, a content FAIL says nothing; download it and `pdftotext -layout`.
  * SSL cert-chain errors (e.g. pgjonline.com) — confirm via `curl`/the www form/Wayback.

Content false-negatives (a 200 the screen marks "value not found" that DOES support the value):
  * STATUS is inferable, not literal. Do NOT require the status token ('operating', etc.) as a
    substring. A page that describes the line carrying gas, an expansion/throughput, an
    inauguration, or export volumes CONFIRMS 'operating' by context even if the word never
    appears. Pass status context via `expected`/`any_of` if you like, but treat a status
    `any_of` miss as expected — the agent infers status from the prose (see confidence_tiers.md).
  * NAME spelling varies by transliteration (Chelavend↔Chelavand, Kordkuy↔Kordkoy). Pass the
    pipeline/entity name via `name=` so it is matched with fuzzy tolerance (`name_forms` +
    difflib), instead of a brittle exact substring.
No mode is a fabricated-URL exception (standing rule 2): still confirm the page is real and
contains/supports the value by another route before keeping the ref.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
import unicodedata

GEM_HOSTS = ("gem.wiki", "globalenergymonitor")
# Never an acceptable reference (per Baird) — tertiary wiki/aggregator surfaces that
# merely restate other sources. Enforced at the verifier, not just the harvester, so a
# blocklisted URL can never slip into a workbook by any path (harvest_wiki_citations.py
# imports this tuple). A Barrel Full lives at abarrelfull.wikidot.com; "abarrellfull"
# covers the common double-l misspelling, "wikidot.com" the wider free-wiki platform.
BLOCKLIST_HOSTS = ("theodora.com", "theodora", "abarrelfull", "abarrellfull", "wikidot.com")
_UA = "Mozilla/5.0 (compatible; pipelines-researcher/1.0)"

# per-domain politeness floor for verify_many (seconds between hits to one host)
_MIN_INTERVAL = 1.0
# A 200 whose body is shorter than this, when we were checking for content, is treated as a
# likely block page / cookie wall / archive interstitial / truncated fetch — not a real article.
# Flagged so the agent re-fetches the FULL text rather than banking a false "value not found".
_MIN_BODY_CHARS = 1500


def _fold(s: str) -> str:
    """Lowercase, strip diacritics, collapse non-alphanumerics to single spaces — so
    transliteration/punctuation noise doesn't defeat a match."""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def name_forms(name) -> list[str]:
    """Spelling/transliteration variants of a proper name, so a page that renders it
    differently (Chelavend vs Chelavand, Kordkuy vs Kordkoy) isn't a false negative.
    Returns OR-match candidates; transliteration is lossy, so this is a screen, not
    proof — pair with the fuzzy check and the agent's own read of the page."""
    if not name:
        return []
    raw = str(name).strip()
    forms = {raw, raw.lower(), _fold(raw)}
    return [f for f in forms if f]


def _name_present(text: str, name: str, cutoff: float = 0.86) -> bool:
    """True if `name` appears in `text` allowing minor transliteration variation. Exact
    (folded) substring first; else per-significant-token difflib against the page's word
    list (tokens < 4 chars are too ambiguous to fuzzy-match and must appear exactly)."""
    if not name:
        return True
    folded_text = _fold(text)
    if any(_fold(f) and _fold(f) in folded_text for f in name_forms(name)):
        return True
    words = folded_text.split()
    if not words:
        return False
    for tok in _fold(name).split():
        if len(tok) < 4:
            if tok not in words:
                return False
            continue
        if tok in words:
            continue
        if not difflib.get_close_matches(tok, words, n=1, cutoff=cutoff):
            return False
    return True


def verify_url(url: str, *expected: str, any_of=None, name=None, fuzzy: bool = True,
               timeout: int = 20) -> dict:
    """Return {ok, status, reason}. The page must HTTP-200, contain ALL `expected`
    substrings (AND), and — if `any_of` is given — contain AT LEAST ONE of them (OR).
    Use `any_of` for a data value's surface forms (see `surface_forms`); use `expected`
    for context that must always be present. `expected`/`any_of` matching is exact,
    case-insensitive substring (never fuzzy — fuzzing numeric surface forms would corrupt
    them). Pass a proper NAME via `name=` to require the page mention it with
    transliteration tolerance (`fuzzy`, default on: Chelavend matches a page's
    'Chelavand'). For STATUS, don't demand the status token as a substring — a status
    `any_of` miss is expected; the agent infers status from the page's prose."""
    low = (url or "").lower()
    if not low.startswith("http"):
        return {"ok": False, "status": None, "reason": "not an http(s) URL"}
    if any(h in low for h in GEM_HOSTS):
        return {"ok": False, "status": None, "reason": "GEM surface — never self-cite (standing rule 1)"}
    hit = next((h for h in BLOCKLIST_HOSTS if h in low), None)
    if hit:
        return {"ok": False, "status": None, "reason": f"{hit} — blocklisted tertiary aggregator, never an acceptable reference"}
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
    # requests falls back to ISO-8859-1 (the HTTP default for text/*) whenever the server
    # omits an explicit charset in Content-Type — common on Chinese gov/news sites that DO
    # serve utf-8 but don't declare it. Left uncorrected this mangles the body into
    # mojibake and produces false "value not found" negatives on real, live pages (e.g.
    # ndrc.gov.cn). Only override the generic default, never a charset the server actually
    # declared, so a genuine non-utf-8 declaration (e.g. real GBK) is left alone.
    if (r.encoding or "").lower() in ("iso-8859-1", "ascii") and r.apparent_encoding:
        r.encoding = r.apparent_encoding
    body = r.text or ""
    text = body.lower()
    # A content check against a suspiciously short body is not a trustworthy negative — it is
    # almost always a block page / cookie wall / archive interstitial / truncated fetch, NOT
    # the real article (this is the eurasianet-stub failure). Flag it so the agent re-fetches
    # the FULL text (rendered/browser, another mirror, or Wayback) instead of banking a false
    # "value not found". Only matters when we are actually checking for content.
    stub = len(body.strip()) < _MIN_BODY_CHARS
    checking = bool(expected or any_of or name)
    missing = [e for e in expected if e and e.lower() not in text]
    if missing:
        if stub:
            return {"ok": False, "status": 200,
                    "reason": f"200 but body only {len(body.strip())} chars (likely block/stub) — re-fetch full text; expected missing: {missing}"}
        return {"ok": False, "status": 200, "reason": f"200 but missing expected: {missing}"}
    if any_of:
        forms = [a for a in any_of if a]
        if forms and not any(a.lower() in text for a in forms):
            tail = f" — re-fetch full text (body only {len(body.strip())} chars, likely block/stub)" if stub else ""
            return {"ok": False, "status": 200, "reason": f"200 but data value not found (none of {forms}){tail}"}
    if name and not (_name_present(body, name) if fuzzy else name.lower() in text):
        tail = f" — re-fetch full text (body only {len(body.strip())} chars, likely block/stub)" if stub else ""
        return {"ok": False, "status": 200, "reason": f"200 but name not found (fuzzy): {name!r}{tail}"}
    if stub and checking:
        # Matched inside a stub is not to be trusted either — surface it, don't silently pass.
        return {"ok": True, "status": 200,
                "reason": f"200 + content present, BUT body only {len(body.strip())} chars — verify against full text"}
    return {"ok": True, "status": 200, "reason": "200 + expected content present" if checking else "200"}


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


def verify_many(urls, expected=(), any_of=None, name=None, fuzzy: bool = True,
                timeout: int = 20, max_workers: int = 6) -> dict:
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
        return u, verify_url(u, *expected, any_of=any_of, name=name, fuzzy=fuzzy, timeout=timeout)

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
    ap.add_argument("expected", nargs="*", help="substrings the page must contain (exact)")
    ap.add_argument("--name", help="proper name the page must mention (fuzzy/transliteration-tolerant)")
    ap.add_argument("--exact-name", action="store_true", help="require --name as an exact substring")
    args = ap.parse_args()
    res = verify_url(args.url, *args.expected, name=args.name, fuzzy=not args.exact_name)
    print(("OK   " if res["ok"] else "FAIL ") + f"{args.url}  — {res['reason']}")
    sys.exit(0 if res["ok"] else 1)


if __name__ == "__main__":
    main()
