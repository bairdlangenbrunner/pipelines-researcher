#!/usr/bin/env python3
"""Verify a [ref] URL before it goes in a workbook: resolves (HTTP 200) and (optionally)
contains expected substrings. ALWAYS rejects GEM surfaces — never self-cite (standing
rule 1) — and blocklisted tertiary aggregators (theodora.com; A Barrel Full /
abarrelfull.wikidot.com and the wider wikidot.com platform) which are never acceptable
references, plus `web.archive.org/save/` links (Save Page Now instructions, not snapshots).
Importable:
`from url_verifier import verify_url, verify_many, surface_forms`.

    python scripts/url_verifier.py "https://example.com/x" "Pipeline Name" "2025"

A FAIL is NOT proof the source is dead, and — critically — a "value not found" FAIL is NOT proof
the page fails to support the data point. The substring check is a SCREEN, not the verdict; the
agent reads the page and makes the final call. Two false-negative families:

Liveness false-negatives (rule out before calling a link blocked or unsupported; DEAD_LINK means 404/410 only — Iraq gas sweep: 6 of 27 "dead
links" were false):
  * 401 bot-walls — live pages (e.g. iraq-businessnews.com) reject this UA; confirm manually and
    cite the Wayback snapshot (which passes) instead.
  * ligature-encoded (esp. Arabic) PDFs — the "contains value" substring check can't read
    contiguous Arabic; verify with `pdftotext` before discarding.
  * LARGE PDFs — the extractor does not reach the whole document. The OPEC ASB2012 Wayback
    PDF (7.7 MB, ~200pp) passes on "OPEC" and FAILS on "Jakhira", a token that is provably
    in it. On a big PDF, a content FAIL says nothing; download it and `pdftotext -layout`.
  * SSL cert-chain errors (e.g. pgjonline.com, adilet.zan.kz) — HANDLED SINCE 2026-08-11: an
    SSLError now triggers one automatic retry with `verify=False`, and the verdict carries
    `insecure_tls: True` plus a note in `reason`. So these no longer reach you as failures at
    all; an `insecure_tls` pass means the bytes are real, not that the host's identity was
    confirmed. A remaining SSL failure means BOTH attempts died — then confirm via `curl -k`.

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
import codecs
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
# `yingdodo.com` is 小柱工程, a commercial construction-LEADS database, added 2026-09-10
# off the Jiangxi v3 sweep. The page it kept offering
# (`/html/news/201852592751.html`) is an explicit marketing SAMPLE -- it carries
# `项目样例1类` and `备注：以下样例非最新项目，仅表示内容格式`, redacted owner phone
# numbers, and zero attribution (来源/转载/出处/责任编辑/数据来源/信息来源 all absent).
# Same class as A Barrel Full: it restates someone else's filing without saying whose.
# It matters that this is enforced HERE rather than per-run, because the URL is on
# GEM's OWN gem.wiki citation list for 27 Jiangxi PIDs, so harvest_wiki_citations.py
# (which imports this tuple) re-offers it as a seed citation to every future agent --
# 8 of 9 Jiangxi agents opened it and correctly declined to cite it, but one scored it
# `independent: true` while its own note called it a "project-database listing". Its
# figures (97 km / DN200 / 6.3 MPa) are a LEAD to the underlying 立项备案 filing, never
# a citation.
BLOCKLIST_HOSTS = ("theodora.com", "theodora", "abarrelfull", "abarrellfull", "wikidot.com",
                   "yingdodo.com", "yingdodo")

# URL shorteners. A shortener is never a citable reference — it is an opaque,
# revocable indirection whose target can be repointed after we cite it — and worse, it
# BYPASSES the blocklist, because GEM_HOSTS/BLOCKLIST_HOSTS are string tests against the
# submitted URL. Measured 2026-09-04 on the US-gas harvest: 9 of 20 harvested bit.ly
# links resolve to abarrelfull.wikidot.com, and `bit.ly/2sYGqrY` verified `ok=True,
# 200 + expected content present` while serving the banned source. Resolve it and cite
# the target, or drop it.
SHORTENER_HOSTS = ("bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co", "buff.ly",
                   "is.gd", "rebrand.ly", "cutt.ly", "shorturl.at", "trib.al")
_UA = "Mozilla/5.0 (compatible; pipelines-researcher/1.0)"

# UA for fetching gem.wiki itself (harvest_wiki_citations.py, wiki_alignment.py) —
# NOT for external sites, which need the browser-ish _UA above to get past their own
# bot walls. The leading "baird-wiki" token is GEM's firewall identity for this
# traffic, and the WAF-bypass key whenever the zone runs Cloudflare Under Attack Mode
# (it did 2026-08-07 → ~08-11; off again since, but the token stays — if gem.wiki
# starts 403ing "cf-mitigated: challenge", check the UA first). Deliberately
# byte-identical to goit-ggit-data-ops/gem-wiki/gemwiki.py's USER_AGENT so both repos
# present as one client in GEM's firewall logs — keep them in sync, and see that repo's
# gem-wiki/README.md → Auth for the full writeup.
WIKI_UA = "baird-wiki/1.0 (baird.langenbrunner@globalenergymonitor.org)"

# per-domain politeness floor for verify_many (seconds between hits to one host)
_MIN_INTERVAL = 1.0

# Opt-in in-process response cache. A sweep that verifies ONE document against many rows'
# names (carry_prior re-checking 22 units sourced from a 4 MB bond PDF, one row at a time)
# otherwise downloads that document once per row. Set `url_verifier.RESPONSE_CACHE = {}`
# before calling verify_url/verify_many and every fetch of the same (url, verify) is served
# from the dict after the first. Default None = no caching (a verification run must see
# the live page). Never persisted; never shared across processes.
RESPONSE_CACHE: dict | None = None


def _wall_fallback(url: str, r, timeout):
    """A bot wall (Cloudflare firewall/JS challenge, AWS WAF, Imperva) is a
    tooling failure, not a fact about the page. Re-fetch through the shared
    ladder in scripts/fetch.py (curl → curl_cffi Chrome-TLS impersonation →
    real-Chrome clearance cookie via cf_clearance.py; LNGCT_NO_BROWSER=1 stops
    before the browser) and hand back a Response built from what it got, with
    `fetch_notes` naming the route. The original response is returned when the
    ladder cannot clear the wall either. Text is re-encoded as utf-8 (fetch.py
    already decoded it charset-aware) and a PDF comes back as its extracted
    text under text/plain, so the branches below need no special case."""
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from fetch import _is_cf_wall, fetch_page
    if not _is_cf_wall(str(r.status_code), r.content or b""):
        return r
    page = fetch_page(url, timeout=timeout)
    if page.status == "000" or _is_cf_wall(page.status, page.text.encode("utf-8", "replace")):
        return r
    import requests
    out = requests.Response()
    out.status_code = int(page.status) if page.status.isdigit() else 0
    out._content = page.text.encode("utf-8", "replace")
    out.encoding = "utf-8"
    base = "text/plain" if page.is_pdf else (page.content_type.split(";")[0].strip() or "text/html")
    out.headers["Content-Type"] = f"{base}; charset=utf-8"
    out.url = page.final_url or url
    out.request = r.request
    out.fetch_notes = list(page.notes)
    return out


def _http_get(url: str, timeout, headers, verify: bool = True):
    import requests
    key = (url, verify, headers.get("User-Agent", ""))
    if RESPONSE_CACHE is not None and key in RESPONSE_CACHE:
        return RESPONSE_CACHE[key]
    r = requests.get(url, timeout=timeout, headers=headers, verify=verify)
    r = _wall_fallback(url, r, timeout)
    if RESPONSE_CACHE is not None:
        RESPONSE_CACHE[key] = r
    return r
# A 200 whose body is shorter than this, when we were checking for content, is treated as a
# likely block page / cookie wall / archive interstitial / truncated fetch — not a real article.
# Flagged so the agent re-fetches the FULL text rather than banking a false "value not found".
_MIN_BODY_CHARS = 1500

# Markup that is never citable prose. Stripped before any content match, because a
# numeric value collides with coordinate/hash digit-runs inside it. Ukraine gas
# 2026-08-12: `verify_url("https://energybase.ru/pipeline/stavropol-moskva", "1262")`
# returned "200 + expected content present" against a 13,560-char geo-block
# interstitial — the only "1262" on the page was inside the SVG path coordinate
# `589.126229`, part of the block page's decorative graphic. The body cleared
# _MIN_BODY_CHARS, so the stub heuristic never fired. `<script>` is deliberately NOT
# stripped: real values do live in JSON-LD blocks.
_NOISE_MARKUP_RE = re.compile(r"<(svg|style|template)\b.*?</\1\s*>", re.S | re.I)

# Script blocks are stripped ONLY for the block-phrase check, not for content matching:
# JS-rendered pages carry their article text in <script> JSON (`__NEXT_DATA__`, ld+json),
# so a value/name check must still see it. But a block phrase inside a script is never the
# page's verdict — it is a widget's validation string. Found 2026-09-04 on the Jiangxi v3
# sweep: jdzmc.com and chinanews.com.cn article pages ship a comment form whose JS says
# `alert("请输入验证码！")`, and the verifier called every one of them a captcha
# interstitial (false `blocked=True` on real, 40 KB articles).
_SCRIPT_MARKUP_RE = re.compile(r"<(script|noscript)\b.*?</\1\s*>", re.S | re.I)

# URL shapes that are navigation surfaces rather than documents — see the check in
# `verify_url` for why these can never be a `[ref]`. Category/tag matching deliberately
# requires the path to END at the listing (or at a /page/N/), so a real article that
# merely lives under /category/<x>/<slug> is untouched. `/topic/<slug>` is deliberately
# NOT here: Britannica uses it as its ARTICLE path (8 Saudi oil refs cite
# britannica.com/topic/Trans-Arabian-Pipeline, all legitimate). Nor is a bare `?q=`,
# which sites use for plenty besides search — only the search engines' own wrappers.
_NON_CITATION_RE = re.compile(
    r"(?:"
    r"[?&](?:s|search|query)="
    r"|/search/?(?:[?#]|$)"
    r"|/page/\d+/?(?:[?#]|$)"
    r"|/(?:category|reports_category|tag|author)/[^/?#]*/?(?:[?#]|$)"
    r"|(?:google|bing|duckduckgo|yandex)\.[a-z.]+/(?:search|url)\?"
    r")", re.I)

# A 200 that is really an access-denied / bot-challenge / geo-block interstitial. Checked
# regardless of body length — a block page padded with inline graphics is not short.
# NOT a deletion: standing rule is that a blocked origin gets its Wayback snapshot ADDED
# alongside, never a ref deleted, so the reason says so explicitly.
_BLOCK_PHRASES = (
    "доступ ограничен", "использование vpn", "вы робот", "проверка браузера",
    "checking your browser", "attention required", "access denied", "access to this page",
    "verify you are human", "are you a human", "enable javascript and cookies",
    "request blocked", "unusual traffic", "cf-error-details", "ddos protection",
    "your access to this site has been limited", "why have i been blocked",
    # Chinese-language WAF/challenge wording. The list was English+Russian only until
    # 2026-08-26, so every Chinese block page served under HTTP 200 verified as clean
    # prose — the same false-PASS family as the energybase.ru case above, and it matters
    # because the China province sweeps cite provincial-government and registry hosts
    # almost exclusively. Found on the Jiangxi gas sweep: qcc.com (企查查, the company
    # registry behind 33 of that batch's wiki citations) serves
    # "由于您访问的链接有可能对网站造成安全威胁，您的访问被阻断" from its WAF.
    "访问被阻断", "拒绝访问", "对网站造成安全威胁", "人机验证", "滑动验证",
    "请输入验证码", "访问频率过高", "请求过于频繁", "网站防火墙", "该页面禁止访问",
)


def _match_surface(body: str) -> str:
    """The lowercased text a content check is allowed to match against.

    Not the raw HTML — see _NOISE_MARKUP_RE. Returns lowercase because every caller
    compares lowercased needles.
    """
    return _NOISE_MARKUP_RE.sub(" ", body or "").lower()


def _blocked_as(text: str) -> str | None:
    """The block-page phrase this body matches, if any."""
    for p in _BLOCK_PHRASES:
        if p in text:
            return p
    return None


def _contains(text: str, needle: str) -> bool:
    """Substring test, except that a PURELY NUMERIC needle must match as a whole number.

    A bare `"1262" in text` also matches inside `589.126229`, `41262`, a build hash or a
    timestamp — the false-positive family that let a geo-block page verify clean. Digits
    are the shape most refs are checked on (lengths, diameters, capacities, years), so
    they get boundaries; alphabetic needles keep plain substring semantics, since a
    genuine phrase match rarely collides and word boundaries would break
    partial-word/inflected matches (Russian/Ukrainian case endings especially).
    """
    n = (needle or "").lower()
    if not n:
        return True
    if re.fullmatch(r"[\d][\d,.\s]*", n):
        return re.search(rf"(?<![\d.,]){re.escape(n)}(?![\d.,])", text) is not None
    return n in text


# ---- range midpoint (cost columns only) -------------------------------------------------
# The pipelines manual (Cost, CostUnits): "If a range of costs is given in a source, calculate
# the average or midpoint ... and record that in the sheet." So a recorded cost is SUPPORTED by
# a page that states the RANGE, never the midpoint itself (neftegaz 660602: «от 4,5 до 13,6 млрд
# долл.» -> 9.05 bn recorded). A substring screen for the midpoint can never see that; this
# looks for "A–B" / "from A to B" / "от A до B" pairs whose average is the value. Opt-in
# (`midpoint_of=`), cost columns only: for years or lengths "2019 to 2021" would wrongly
# support 2020.
_NUM = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:[.,]\d+)?"
_RANGE_RE = re.compile(
    rf"(?P<a>{_NUM})\s*(?P<ua>млрд|млн|тыс|billion|million|thousand|bn|mn|[bmk])?\.?\s*"
    rf"(?:[-\u2010-\u2015]|\bto\b|\bthrough\b|\bдо\b|\band\b|\bи\b)\s*"
    rf"(?P<b>{_NUM})\s*(?P<ub>млрд|млн|тыс|billion|million|thousand|bn|mn|[bmk])?\b",
    re.I)
_SCALE = {"млрд": 1e9, "billion": 1e9, "bn": 1e9, "b": 1e9, "млн": 1e6, "million": 1e6, "mn": 1e6,
          "m": 1e6, "тыс": 1e3, "thousand": 1e3, "k": 1e3}


def _num(tok: str) -> float:
    if re.fullmatch(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", tok):
        return float(tok.replace(",", ""))
    return float(tok.replace(",", "."))


def range_midpoint_match(text: str, value, rel_tol: float = 0.005):
    """The stated range ("4,5 до 13,6 млрд") whose midpoint equals `value` (a cost, in base
    units), or None. The magnitude word after either end scales both ends; a pair with no
    magnitude word is read at face value."""
    try:
        target = float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return None
    if not target:
        return None
    for m in _RANGE_RE.finditer(text or ""):
        try:
            a, b = _num(m.group("a")), _num(m.group("b"))
        except ValueError:
            continue
        unit = (m.group("ub") or m.group("ua") or "").lower()
        scale = _SCALE.get(unit, 1.0)
        if a == b or a <= 0 or b <= 0:
            continue
        mid = (a + b) / 2 * scale
        if abs(mid - target) <= rel_tol * abs(target):
            return m.group(0).strip()
    return None


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


_NON_LATIN_RE = re.compile(r"[\u0370-\u03ff\u0400-\u052f\u0530-\u058f\u0590-\u05ff\u0600-\u06ff"
                           r"\u0900-\u0dff\u0e00-\u0e7f\u1100-\u11ff\u3040-\u30ff\u3400-\u4dbf"
                           r"\u4e00-\u9fff\uac00-\ud7af\uf900-\ufaff]")
_META_CHARSET_RE = re.compile(
    rb"""<meta[^>]+charset\s*=\s*["']?\s*([A-Za-z0-9_\-]+)""", re.I)

# gb2312 and gbk are PROPER SUBSETS of gb18030, and Chinese pages routinely declare the
# narrow one while serving characters outside it -- decoding such a page as gb2312 raises
# or drops characters mid-document. Decoding as gb18030 is always safe for all three, so
# widen rather than honor the narrow declaration literally. Same for the big5 family.
_CHARSET_WIDEN = {"gb2312": "gb18030", "gbk": "gb18030", "gb_2312-80": "gb18030",
                  "euc-cn": "gb18030", "big5": "big5hkscs", "big5-hkscs": "big5hkscs"}


def _meta_charset(content: bytes):
    """The charset the HTML DECLARES about itself, read from the raw bytes.

    Used only when the server omitted a charset from Content-Type. A declaration beats
    `requests.apparent_encoding`, which is a statistical guess that mistakes GB2312 for
    the Cyrillic codepage `ptcp154` (see the call site). Returns None when no meta tag is
    present or Python has no codec for it, so the caller falls back to the guess.
    """
    m = _META_CHARSET_RE.search((content or b"")[:4096])
    if not m:
        return None
    name = m.group(1).decode("ascii", "ignore").strip().lower()
    name = _CHARSET_WIDEN.get(name, name)
    try:
        codecs.lookup(name)
    except (LookupError, ValueError):
        return None
    return name


_DASHES_RE = re.compile(r"[\-\u2010-\u2015\u2212\uff0d~\uff5e]")


def _cjk_norm(s: str) -> str:
    """Match surface for a non-Latin name: NFKC (full-width -> ASCII), lowercase, all
    whitespace removed (CJK prose is unspaced; extraction inserts spaces at random),
    every dash variant -> '-' (丰城—抚州 / 丰城－抚州 / 丰城-抚州 are one name), a RUN of
    dashes -> one (news prose writes 永修——武宁——修水 with doubled em-dashes; caught on
    P4784 2026-09-09, where the verifier failed a page that names the row), and the
    connector 至 -> '-' (丰城至抚州 IS the 丰城-抚州 name; 到 is left alone as prose)."""
    s = unicodedata.normalize("NFKC", str(s or "")).lower()
    s = _DASHES_RE.sub("-", s)
    s = re.sub(r"\s+", "", s)
    s = s.replace("至", "-")
    return re.sub(r"-{2,}", "-", s)


_CYRILLIC_RE = re.compile(r"[\u0400-\u04ff]")


def _cyr_lat(s: str) -> str:
    """Romanize Cyrillic so a Latin name can be matched against a Cyrillic-language page.

    Delegates to `normalize.translit_cyrillic` — the same table the reconciler's name axis
    uses since the 2026-08-14 fix (`notes/escalation-2026-08-14-cyrillic-names-invisible-to-matcher.md`),
    so the two matchers agree on what a Russian name looks like in Latin. The direction
    matters: Cyrillic -> Latin is near-deterministic, while guessing which Cyrillic
    spelling an English name was transliterated FROM is not (y -> ы/й/и, e -> е/э/ё);
    the per-token fuzz then absorbs the residual scheme differences (-skoye/-skoe, -iy/-y, kh/h).
    Returns the text unchanged if normalize is unimportable."""
    try:
        from normalize import translit_cyrillic
    except Exception:
        return str(s or "")
    return translit_cyrillic(str(s or ""))


# Descriptor words GEM appends to a name that a source in another language expresses with
# one of its own (ГКМ for "gas condensate field", газопровод for "gas pipeline"). Local to
# this module on purpose: `normalize._NAME_STOP` feeds the reconciler's name axis, and
# widening a shared stoplist would move already-committed recon runs in other countries.
_DESCRIPTOR_EXTRA = frozenset({
    "condensate", "field", "fields", "terminal", "branch", "trunk", "spur", "main",
    "mainline", "network", "segment", "section", "lateral", "extension", "loop",
    "transmission", "distribution", "interconnector", "connector", "link", "route",
})


def _required_tokens(name: str) -> list[str]:
    """The tokens of `name` a page must actually carry — the DISTINCTIVE ones.

    GEM names carry a generic descriptor tail ("… Gas Pipeline", "… Gas Condensate
    Field") that a source in another language renders as one of its own words
    (газопровод, 输气管道), so requiring `gas` and `pipeline` verbatim fails every
    non-English page that names the line perfectly well. Stoplist shared with the
    reconciler (`normalize._NAME_STOP`) plus `_DESCRIPTOR_EXTRA` — kept local so widening
    it here never moves a committed reconciliation run. If a name is ALL descriptor the
    full token list stands, exactly as `normalize_name(drop_stopwords=True)` does."""
    toks = _fold(name).split()
    try:
        from normalize import _NAME_STOP as _stop
    except Exception:
        _stop = frozenset()
    stop = set(_stop) | _DESCRIPTOR_EXTRA
    kept = [t for t in toks if t not in stop]
    return kept or toks


def _name_present(text: str, name: str, cutoff: float = 0.86) -> bool:
    """True if `name` appears in `text` allowing minor transliteration variation. Exact
    (folded) substring first; else per-significant-token difflib against the page's word
    list (tokens < 4 chars are too ambiguous to fuzzy-match and must appear exactly)."""
    if not name:
        return True
    # `_fold` keeps only [a-z0-9], so a Chinese, Cyrillic or Arabic name folds to NOTHING
    # -- and an empty token list made the loop below return True vacuously: every
    # non-Latin name "matched" every page. Caught 2026-09-03 wiring `--name` into the
    # Jiangxi v3 carry-forward (江西支线 passed against a 404 body). Names in a script the
    # fold cannot represent are matched as exact substrings on a normalised surface
    # (NFKC, lowercase, whitespace removed, dash variants unified) -- no fuzz, since there
    # is no transliteration noise to tolerate in the page's own script.
    if _NON_LATIN_RE.search(str(name)) or not _fold(name):
        return _cjk_norm(name) in _cjk_norm(text)
    if _match_latin(text, name, cutoff):
        return True
    # A Latin name against a Cyrillic page: romanize the PAGE and retry (see `_cyr_lat`).
    if _CYRILLIC_RE.search(text or ""):
        return _match_latin(_cyr_lat(text), name, cutoff)
    return False


def _match_latin(text: str, name: str, cutoff: float = 0.86) -> bool:
    """The Latin-surface half of `_name_present`: folded substring, else per-token fuzz."""
    folded_text = _fold(text)
    if any(_fold(f) and _fold(f) in folded_text for f in name_forms(name)):
        return True
    words = folded_text.split()
    if not words:
        return False
    for tok in _required_tokens(name):
        if len(tok) < 4:
            if tok not in words:
                return False
            continue
        if tok in words:
            continue
        if not difflib.get_close_matches(tok, words, n=1, cutoff=cutoff):
            return False
    return True


def _pdf_text(content: bytes, max_pages: int = 400) -> tuple[str, str]:
    """Text layer of a PDF, or ("", why) when none could be read.

    `requests.text` on a PDF is binary soup, so every content/name check against it is a
    false negative — the Jiangxi v2 sweep's three dominant documents (a DRC plan, a bond
    prospectus and a county EIA, all PDFs) FAILED the verifier on values provably in them
    and had to be hand-confirmed one by one. Under the mandatory `--name` rule that false
    negative would cap every PDF-sourced unit at `low`. pypdf first (in-process), pdftotext
    as the fallback; a scanned PDF with no text layer reports as such rather than as a miss."""
    err = ""
    try:
        import io
        from pypdf import PdfReader
        rd = PdfReader(io.BytesIO(content))
        parts = []
        for pg in rd.pages[:max_pages]:
            try:
                parts.append(pg.extract_text() or "")
            except Exception:                                   # noqa: BLE001
                continue
        txt = "\n".join(parts)
        if txt.strip():
            return txt, ""
        err = "pypdf found no text layer"
    except Exception as e:                                      # noqa: BLE001
        err = f"pypdf: {type(e).__name__}"
    try:
        import shutil, subprocess, tempfile
        if shutil.which("pdftotext"):
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as fh:
                fh.write(content)
                tmp = fh.name
            out = subprocess.run(["pdftotext", "-layout", tmp, "-"], capture_output=True,
                                 timeout=120)
            txt = out.stdout.decode("utf-8", "replace")
            if txt.strip():
                return txt, ""
            err += "; pdftotext found no text layer (scanned image?)"
        else:
            err += "; pdftotext not installed"
    except Exception as e:                                      # noqa: BLE001
        err += f"; pdftotext: {type(e).__name__}"
    return "", err.strip("; ")


def _sheet_text(content: bytes, max_cells: int = 400_000) -> tuple[str, str]:
    """Cell text of an XLSX/XLS workbook, or ("", why) when none could be read.

    Same lesson as _pdf_text, learned again 2026-09-04: an .xlsx body is a ZIP, so
    `requests.text` is binary soup and EVERY content/name check against it is a false
    negative. EIA's `EIA-NaturalGasPipelineProjects_*.xlsx` — the single most-cited
    document in the US gas cohort — was reporting `name_found: False` for pipelines
    listed by name in its own rows, which under the relevance gate would have capped
    those units at `low` on the strength of a parser failure.

    openpyxl (read_only, values only) for the modern format; pandas/xlrd for legacy .xls.
    Cell values are flattened to one tab-separated line per row, which is enough for the
    substring and name checks and keeps big workbooks cheap."""
    err = ""
    try:
        import io
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        parts, n = [], 0
        for ws in wb.worksheets:
            parts.append(str(ws.title))
            for row in ws.iter_rows(values_only=True):
                cells = [str(c) for c in row if c is not None]
                n += len(cells)
                if cells:
                    parts.append("\t".join(cells))
                if n >= max_cells:
                    break
            if n >= max_cells:
                break
        wb.close()
        txt = "\n".join(parts)
        if txt.strip():
            return txt, ""
        err = "openpyxl found no cell values"
    except Exception as e:                                      # noqa: BLE001
        err = f"openpyxl: {type(e).__name__}"
    try:
        import io
        import pandas as pd
        sheets = pd.read_excel(io.BytesIO(content), sheet_name=None, header=None,
                               dtype=str)
        txt = "\n".join(df.fillna("").astype(str).agg("\t".join, axis=1).str.cat(sep="\n")
                        for df in sheets.values())
        if txt.strip():
            return txt, ""
        err += "; pandas read no rows"
    except Exception as e:                                      # noqa: BLE001
        err += f"; pandas: {type(e).__name__}"
    return "", err.strip("; ")


def verify_url(url: str, *expected: str, any_of=None, name=None, fuzzy: bool = True,
               timeout: int = 20, midpoint_of=None) -> dict:
    """Return {ok, status, reason}. The page must HTTP-200, contain ALL `expected`
    substrings (AND), and — if `any_of` is given — contain AT LEAST ONE of them (OR).
    Use `any_of` for a data value's surface forms (see `surface_forms`); use `expected`
    for context that must always be present. `expected`/`any_of` matching is exact,
    case-insensitive substring (never fuzzy — fuzzing numeric surface forms would corrupt
    them). Pass a proper NAME via `name=` to require the page mention it with
    transliteration tolerance (`fuzzy`, default on: Chelavend matches a page's
    'Chelavand'). For STATUS, don't demand the status token as a substring — a status
    `any_of` miss is expected; the agent infers status from the page's prose. `midpoint_of=<cost>`
    (cost columns only) also lets a page that states a RANGE whose midpoint is that cost satisfy
    `any_of` (`range_midpoint_match`); the result then carries `midpoint_range`."""
    low = (url or "").lower()
    if not low.startswith("http"):
        return {"ok": False, "status": None, "reason": "not an http(s) URL"}
    if any(h in low for h in GEM_HOSTS):
        return {"ok": False, "status": None, "reason": "GEM surface — never self-cite (standing rule 1)"}
    hit = next((h for h in BLOCKLIST_HOSTS if h in low), None)
    if hit:
        return {"ok": False, "status": None, "reason": f"{hit} — blocklisted tertiary aggregator, never an acceptable reference"}
    # Save Page Now's INSTRUCTION endpoint, not a snapshot address: it triggers a fresh
    # capture of the live origin instead of serving the archive, so it is never evidence.
    # Use web.archive.org/web/<timestamp>/<url>. 348 of these had accumulated in the
    # backend before the 2026-08-05 repair (notes/wayback-save-repair-20260805/).
    from urllib.parse import urlparse as _up
    _h = _up(low).netloc.removeprefix("www.")
    if _h in SHORTENER_HOSTS:
        return {"ok": False, "status": None,
                "reason": f"{_h} is a URL shortener, not a citable address — resolve it "
                          f"and cite the target document"}
    if "web.archive.org/save/" in low:
        return {"ok": False, "status": None,
                "reason": "web.archive.org/save/ is the Save Page Now instruction endpoint, "
                          "not a snapshot — cite web.archive.org/web/<timestamp>/<url>"}
    # A site-search query, a paginated archive index or a bare category/tag listing is
    # NAVIGATION, not a document. It cannot support a data value at all: its content is
    # whatever the site published most recently, so a value "found" on it today is gone
    # next month, and the page 200s for ANY query (egyptoil-gas.com/?s=<nonsense> returns
    # 172 KB of chrome). Worse, it passes a naive substring screen whenever the digits
    # happen to land in a result snippet — which is exactly how 104 of Egypt's 560 filled
    # ref units (18.6%, 16 rows across BOTH trackers) came to rest on just two such URLs,
    # 81 of them scored `ok` (2026-08-27). Flag the shape and make the unit owed, so the
    # researcher chases the underlying article/report instead of re-citing the index.
    if _NON_CITATION_RE.search(url or ""):
        return {"ok": False, "status": None,
                "reason": "search/index page, not a document — cite the underlying "
                          "article or report, not a mutable navigation surface"}
    try:
        import requests
    except ImportError:
        return {"ok": False, "status": None, "reason": "requests not installed (pip install -r requirements.txt)"}
    # An incomplete/self-signed cert chain is a TRANSPORT defect on our side of the
    # handshake, never evidence the page is gone — and a whole country's dominant source
    # can sit behind one (adilet.zan.kz, Kazakhstan's legal-acts portal, served 51 of 105
    # "failing" refs in the 2026-08-11 KZ gas sweep; every one was SSLError, none a 404).
    # So retry once with chain verification off and label the pass loudly, instead of
    # handing the sweep 51 phantom dead links to re-verify by hand. The label matters:
    # `insecure_tls` says the bytes are real but the identity was not cryptographically
    # confirmed, so treat the page as live and readable, not as authenticated.
    insecure = False
    is_pdf = False
    try:
        r = _http_get(url, timeout, {"User-Agent": _UA})
    except Exception as e:
        is_ssl = "SSL" in type(e).__name__ or "certificate" in str(e).lower()
        if not is_ssl:
            return {"ok": False, "status": None, "reason": f"request failed: {type(e).__name__}"}
        try:
            import urllib3
            urllib3.disable_warnings()
        except Exception:
            pass
        try:
            r = _http_get(url, timeout, {"User-Agent": _UA}, verify=False)
            insecure = True
        except Exception as e2:
            return {"ok": False, "status": None,
                    "reason": f"request failed: {type(e).__name__}; retry without cert "
                              f"verification also failed: {type(e2).__name__}"}
    # The bans above are string tests on the SUBMITTED url, so any redirect — a
    # shortener, a vanity domain, an aggregator's own 301 — walks straight through them.
    # Re-apply them to where we actually landed, and to every hop on the way.
    _chain = [h.url for h in (getattr(r, "history", None) or [])] + [getattr(r, "url", url) or url]
    for _u in _chain:
        _low = _u.lower()
        if any(h in _low for h in GEM_HOSTS):
            return {"ok": False, "status": None,
                    "reason": f"redirects to a GEM surface ({_u}) — never self-cite "
                              f"(standing rule 1)"}
        _hit = next((h for h in BLOCKLIST_HOSTS if h in _low), None)
        if _hit:
            return {"ok": False, "status": None,
                    "reason": f"redirects to {_hit} ({_u}) — blocklisted tertiary "
                              f"aggregator, never an acceptable reference"}

    def _fin(d: dict) -> dict:
        """Stamp the insecure-TLS retry onto whatever verdict the checks reach, so the
        provenance travels with the result instead of vanishing into a bare ok=True."""
        if insecure:
            d["insecure_tls"] = True
            d["reason"] = (d.get("reason", "") +
                           " [cert chain unverified — retried with TLS verification off; "
                           "page is live, identity not cryptographically confirmed]")
        if is_pdf:
            d["pdf"] = True
        if getattr(r, "fetch_notes", None):
            d["fetch_route"] = r.fetch_notes
        if sec_retry:
            d["sec_ua_retry"] = True
            d["reason"] = (d.get("reason", "") +
                           " [sec.gov 403'd the default UA; retried with an identifying "
                           "UA per SEC's fair-access policy]")
        return d

    # sec.gov enforces its fair-access policy by UA content, not rate alone: it 403s the
    # generic `_UA` string outright (no contact info in it) regardless of pace, while a UA
    # carrying a name + email passes immediately — confirmed 2026-09-02 auditing P0162
    # (Mississippi River Transmission), where every EDGAR filing URL (Energy Transfer's
    # EX-21.1 subsidiaries list, CenterPoint/Enable 10-Ks) 403'd on the first try and 200'd
    # on retry with an identifying UA. This is a transport-policy defect on our side, same
    # family as the insecure_tls retry above — not evidence the filing is gone — so retry
    # once, loudly labeled, instead of leaving every SEC citation in the US batch unusable.
    sec_retry = False
    if r.status_code == 403 and "sec.gov" in (url or "").lower():
        try:
            r2 = requests.get(url, timeout=timeout,
                               headers={"User-Agent": "pipelines-researcher (research contact: baird.langenbrunner@globalenergymonitor.org)"})
            if r2.status_code == 200:
                r = r2
                sec_retry = True
        except Exception:
            pass
    if r.status_code != 200:
        return _fin({"ok": False, "status": r.status_code, "reason": f"HTTP {r.status_code}"})
    # requests falls back to ISO-8859-1 (the HTTP default for text/*) whenever the server
    # omits an explicit charset in Content-Type — common on Chinese gov/news sites that DO
    # serve utf-8 but don't declare it. Left uncorrected this mangles the body into
    # mojibake and produces false "value not found" negatives on real, live pages (e.g.
    # ndrc.gov.cn). Only override the generic default, never a charset the server actually
    # declared, so a genuine non-utf-8 declaration (e.g. real GBK) is left alone.
    # Prefer the page's OWN <meta charset> over apparent_encoding: the meta is a
    # declaration, apparent_encoding is a statistical guess, and the guess is wrong in a
    # way that matters. Measured 2026-09-10 on the 9 chinanews.com.cn URLs cited by the
    # Jiangxi v3 sweep: before this change 8 of the 9 failed a `name=` check on a name the
    # page demonstrably contains; after it, all 9 pass against their own row's name. Two
    # (cj/2016/12-12/8091414, ny/2012/10-22/4264426) had apparent_encoding=`ptcp154` -- a
    # CYRILLIC codepage, picked because GB2312 Chinese and Cyrillic have similar byte
    # statistics -- while declaring `gb2312` in their own meta tag. This produced false
    # `name_found: false` on real, on-topic articles, and the P4934 agent had to
    # hand-decode and work around it. (Watch the probe name when re-testing: P4657's two
    # URLs are 川气东送, not 西气东输, and fail correctly against the wrong one.)
    if (r.encoding or "").lower() in ("iso-8859-1", "ascii"):
        r.encoding = _meta_charset(r.content) or r.apparent_encoding or r.encoding
    body = r.text or ""
    ctype = (r.headers.get("Content-Type") or "").lower()
    is_pdf = "pdf" in ctype or (r.content or b"")[:5] == b"%PDF-"
    if is_pdf:
        body, pdf_err = _pdf_text(r.content or b"")
        if not body.strip():
            # No text layer readable — that is NOT a content miss. Say so; the researcher
            # reads it another way (OCR, a mirror) rather than banking a false negative.
            return _fin({"ok": False, "status": 200, "pdf": True,
                         "reason": f"200 PDF but no text could be extracted ({pdf_err}) — "
                                   f"not a content miss; read it another way"})
    raw = r.content or b""
    is_sheet = ("spreadsheet" in ctype or "excel" in ctype
                or raw[:4] == b"PK\x03\x04" and low.split("?")[0].endswith((".xlsx", ".xlsm"))
                or raw[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
                or low.split("?")[0].endswith((".xlsx", ".xlsm", ".xls")))
    if is_sheet and not is_pdf:
        body, xl_err = _sheet_text(raw)
        if not body.strip():
            # Identical rule to the PDF branch: an unreadable workbook is not a miss.
            return _fin({"ok": False, "status": 200, "spreadsheet": True,
                         "reason": f"200 spreadsheet but no cells could be read ({xl_err}) "
                                   f"— not a content miss; read it another way"})
    # Match against prose, not markup — and with whole-number semantics for numeric
    # needles. See _match_surface / _contains.
    text = _match_surface(body)
    # A content check against a suspiciously short body is not a trustworthy negative — it is
    # almost always a block page / cookie wall / archive interstitial / truncated fetch, NOT
    # the real article (this is the eurasianet-stub failure). Flag it so the agent re-fetches
    # the FULL text (rendered/browser, another mirror, or Wayback) instead of banking a false
    # "value not found". Only matters when we are actually checking for content.
    stub = len(body.strip()) < _MIN_BODY_CHARS
    checking = bool(expected or any_of or name)
    # A block/challenge interstitial is a 200 that proves nothing, at any body length, and
    # regardless of whether we were asked to match content. It is NOT evidence the page is
    # gone, so never let this read as a deletion.
    #
    # This deliberately does NOT depend on `checking`. It used to (`blocked and checking`),
    # which meant the commonest call shape in this repo — a bare `verify_url(url)` reachability
    # check with no needle, which is how every `[ref]` cell gets screened — sailed straight
    # past the interstitial and returned a bare `ok=True, reason='200'`. That is the worst
    # possible verdict: a hard PASS on a page we never saw. Caught 2026-08-16 on
    # energybase.ru, which serves «Доступ ограничен» (naming the caller's IP and ASN) under
    # HTTP 200 — the 2026-08-12 repair fixed the phrase list and the match surface but left
    # this gate in place, so the no-needle path stayed broken.
    blocked = _blocked_as(_match_surface(_SCRIPT_MARKUP_RE.sub(" ", body or "")))
    if blocked:
        tail = ("anything 'found' on it is a false positive"
                if checking else "the 200 says nothing about whether the page still exists")
        return _fin({"ok": False, "status": 200, "blocked": True,
                     "reason": f"200 but this is an access-block/challenge interstitial "
                               f"(matched {blocked!r}), not the page — {tail}. NOT a deletion: "
                               f"keep the ref and ADD a Wayback snapshot alongside; only a "
                               f"confirmed 404/410 may drop a ref."})
    missing = [e for e in expected if e and not _contains(text, e)]
    if missing:
        if stub:
            return _fin({"ok": False, "status": 200,
                    "reason": f"200 but body only {len(body.strip())} chars (likely block/stub) — re-fetch full text; expected missing: {missing}"})
        return _fin({"ok": False, "status": 200, "reason": f"200 but missing expected: {missing}"})
    if any_of:
        forms = [a for a in any_of if a]
        mid_hit = None
        if forms and not any(_contains(text, a) for a in forms) and midpoint_of not in (None, ""):
            mid_hit = range_midpoint_match(text, midpoint_of)
        if forms and not any(_contains(text, a) for a in forms) and not mid_hit:
            tail = f" — re-fetch full text (body only {len(body.strip())} chars, likely block/stub)" if stub else ""
            return _fin({"ok": False, "status": 200, "reason": f"200 but data value not found (none of {forms}){tail}"})
    # `text`, not `body` — a name must appear in prose too, not in an svg/style block.
    # `name_found` travels with the verdict whenever a name was asked for, so a caller (and
    # the merge-time relevance gate) can tell "the page names this pipeline" apart from
    # "the page merely contains the number" — the keyword-match failure where a page about
    # endpoint A or endpoint B gets cited for the A–B line.
    # `name` may be ONE string or a LIST of forms (Latin name, segment name, the
    # OtherLanguage* names): a Chinese approval notice names 丰城-抚州输气干线, never
    # "Phase I, Fengcheng-Fuzhou Gas Pipeline", so a single-form check against a CJK page
    # is a guaranteed false negative. Any form present = the page names the line; the
    # matched form is reported so the researcher can see WHICH identity carried it.
    name_list = [n for n in ([name] if isinstance(name, str) else (name or [])) if n]
    matched = next((n for n in name_list
                    if (_name_present(text, n) if fuzzy else _contains(text, n))), None)
    if name_list and matched is None:
        tail = f" — re-fetch full text (body only {len(body.strip())} chars, likely block/stub)" if stub else ""
        shown = name_list[0] if len(name_list) == 1 else name_list
        return _fin({"ok": False, "status": 200, "name_found": False,
                     "reason": f"200 but name not found (fuzzy): {shown!r}{tail}"})
    named = {"name_found": True, "name_matched": matched} if name_list else {}
    if stub and checking:
        # Matched inside a stub is not to be trusted either — surface it, don't silently pass.
        return _fin({"ok": True, "status": 200, **named,
                "reason": f"200 + content present, BUT body only {len(body.strip())} chars — verify against full text"})
    mid = {"midpoint_range": mid_hit} if any_of and mid_hit else {}
    return _fin({"ok": True, "status": 200, **named, **mid,
                 "reason": (f"200 + a stated range ({mid_hit!r}) whose midpoint is the value"
                            if mid else "200 + expected content present") if checking else "200"})


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
                timeout: int = 20, max_workers: int = 6, midpoint_of=None) -> dict:
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
        return u, verify_url(u, *expected, any_of=any_of, name=name, fuzzy=fuzzy, timeout=timeout,
                                midpoint_of=midpoint_of)

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
    ap.add_argument("--name", action="append",
                    help="proper name the page must mention (fuzzy/transliteration-tolerant); "
                         "repeatable — any one form present counts (Latin name, segment name, "
                         "OtherLanguage* name)")
    ap.add_argument("--exact-name", action="store_true", help="require --name as an exact substring")
    args = ap.parse_args()
    res = verify_url(args.url, *args.expected, name=args.name, fuzzy=not args.exact_name)
    print(("OK   " if res["ok"] else "FAIL ") + f"{args.url}  — {res['reason']}")
    sys.exit(0 if res["ok"] else 1)


if __name__ == "__main__":
    main()
