#!/usr/bin/env python3
"""Verify the wiki-attributed citation candidates (step 3 of the Jiangxi batch plan).

26 distinct URLs carry all 100 attributions, so fetching per-attribution would hit the
same page up to 33 times. This fetches each URL ONCE and evaluates every attribution
against the cached text, reusing url_verifier's own internals (`_match_surface`,
`_blocked_as`, `_contains`, `surface_forms`) so the verdict semantics are identical to
`verify_url` — including the block-interstitial gate, the ISO-8859-1 mojibake fix that
matters on undeclared-charset Chinese gov/news pages, and the TLS retry.

Per-column check policy, following the SOP's content false-negative families:
  * Status  -> LIVENESS ONLY. Status is inferable from prose, never a literal token.
  * Operator/Owner -> fuzzy NAME match on the Latin half of the wiki value.
  * everything else -> `any_of` over surface_forms() of the value's numeric core.

Output is a screen, not a verdict: a NOT_SUPPORTED here is a candidate for the subagent
to read and rule on, and a once-working existing ref is never dropped off an access
failure (standing rule; only a confirmed 404/410 may drop one).
"""
from __future__ import annotations
import json, re, sys, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
import url_verifier as UV
from url_verifier import surface_forms, _match_surface, _blocked_as, _contains, _UA

LIVENESS_ONLY = {"Status [ref]"}
NAME_COLS = {"Operator [ref]", "Owner [ref]"}


def numeric_core(v: str) -> str | None:
    """'138 km'->'138'; 'DN300'->'300'; '0.31 bcm/year'->'0.31'; '598 million RMB'->'598'."""
    m = re.search(r"\d[\d,]*(?:\.\d+)?", v or "")
    return m.group(0) if m else None


def latin_name(v: str) -> str | None:
    """Latin half of 'Jiangxi Natural Gas Pipeline Co., Ltd(江西省天然气...)'."""
    s = re.split(r"[（(]", v or "")[0]
    s = re.sub(r"\s*\(\d+%\)", "", s).strip(" ,.;")
    return s if len(s) >= 6 and re.search(r"[A-Za-z]", s) else None


def fetch(url: str) -> dict:
    import requests
    insecure = False
    try:
        r = requests.get(url, timeout=25, headers={"User-Agent": _UA})
    except Exception as e:
        if not ("SSL" in type(e).__name__ or "certificate" in str(e).lower()):
            return {"live": False, "reason": f"request failed: {type(e).__name__}", "text": ""}
        try:
            import urllib3; urllib3.disable_warnings()
        except Exception:
            pass
        try:
            r = requests.get(url, timeout=25, headers={"User-Agent": _UA}, verify=False)
            insecure = True
        except Exception as e2:
            return {"live": False, "reason": f"request failed twice: {type(e).__name__}/{type(e2).__name__}", "text": ""}
    if r.status_code != 200:
        return {"live": False, "status": r.status_code, "reason": f"HTTP {r.status_code}",
                "deletion": r.status_code in (404, 410), "text": ""}
    if (r.encoding or "").lower() in ("iso-8859-1", "ascii") and r.apparent_encoding:
        r.encoding = r.apparent_encoding
    body = r.text or ""
    text = _match_surface(body)
    blocked = _blocked_as(text)
    if blocked:
        return {"live": False, "status": 200, "blocked": True, "text": "",
                "reason": f"200 but access-block/challenge interstitial (matched {blocked!r}) — NOT a deletion"}
    return {"live": True, "status": 200, "text": text, "chars": len(body.strip()),
            "stub": len(body.strip()) < UV._MIN_BODY_CHARS, "insecure_tls": insecure,
            "reason": "200"}


def main() -> None:
    d = json.load(open("wiki_attributed.json"))
    A = d["attributions"]
    urls = sorted({u for r in A for u in r["candidate_urls"]})
    print(f"fetching {len(urls)} distinct URLs …\n")
    cache = {}
    for u in urls:
        cache[u] = fetch(u)
        f = cache[u]
        tag = "LIVE " if f["live"] else "DEAD "
        extra = ""
        if f.get("blocked"): extra = " [BLOCKED interstitial]"
        elif f.get("stub"): extra = f" [stub {f.get('chars')}c]"
        elif f.get("insecure_tls"): extra = " [insecure_tls]"
        print(f"  {tag}{f.get('status') or '-':>4}  {u[:84]}{extra}")

    out = []
    for r in A:
        best = None
        for u in r["candidate_urls"]:
            f = cache[u]
            if not f["live"]:
                v = {"verdict": "UNREACHABLE", "detail": f["reason"],
                     "deletion": bool(f.get("deletion")), "blocked": bool(f.get("blocked"))}
            elif r["ref_col"] in LIVENESS_ONLY:
                v = {"verdict": "LIVE_STATUS_INFERRED", "detail": "liveness only; status is inferable, not literal"}
            elif r["ref_col"] in NAME_COLS:
                nm = latin_name(r["wiki_value"])
                if not nm:
                    v = {"verdict": "LIVE_UNCHECKED", "detail": "no Latin name to match"}
                elif UV._name_present(f["text"], nm):
                    v = {"verdict": "SUPPORTED", "detail": f"name present (fuzzy): {nm!r}"}
                else:
                    v = {"verdict": "NOT_SUPPORTED", "detail": f"200 but name not found (fuzzy): {nm!r}"}
            else:
                core = numeric_core(r["wiki_value"])
                forms = surface_forms(core) if core else []
                if not forms:
                    v = {"verdict": "LIVE_UNCHECKED", "detail": "no numeric core to match"}
                elif any(_contains(f["text"], x) for x in forms):
                    v = {"verdict": "SUPPORTED", "detail": f"value present: {core}"}
                else:
                    v = {"verdict": "NOT_SUPPORTED", "detail": f"200 but value not found (none of {forms})"}
            v["url"] = u
            rank = {"SUPPORTED": 0, "LIVE_STATUS_INFERRED": 1, "LIVE_UNCHECKED": 2,
                    "NOT_SUPPORTED": 3, "UNREACHABLE": 4}[v["verdict"]]
            if best is None or rank < best[0]:
                best = (rank, v)
        rec = dict(r); rec["check"] = best[1] if best else {"verdict": "NO_URL"}
        out.append(rec)

    Path("wiki_attributed_verified.json").write_text(
        json.dumps({"url_checks": cache and {u: {k: v for k, v in f.items() if k != "text"}
                                             for u, f in cache.items()},
                    "attributions": out}, ensure_ascii=False, indent=2))
    print("\n=== verdicts (all 100) ===")
    for k, n in collections.Counter(r["check"]["verdict"] for r in out).most_common():
        print(f"  {k:22s} {n}")
    print("\n=== verdicts on the OWED units (the batch's actual gap) ===")
    owed = [r for r in out if r["owed_on_row"]]
    for k, n in collections.Counter(r["check"]["verdict"] for r in owed).most_common():
        print(f"  {k:22s} {n}   / {len(owed)} owed")
    print("\n=== NOT_SUPPORTED / UNREACHABLE detail (owed only) ===")
    for r in owed:
        if r["check"]["verdict"] in ("NOT_SUPPORTED", "UNREACHABLE"):
            print(f"  {r['project_id']:7s} {r['ref_col']:20s} {r['wiki_value'][:34]!r}")
            print(f"        {r['check']['verdict']}: {r['check']['detail'][:110]}")
    print("\nwrote wiki_attributed_verified.json")


if __name__ == "__main__":
    main()
