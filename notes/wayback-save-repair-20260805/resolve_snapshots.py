#!/usr/bin/env python3
"""Resolve each web.archive.org/save/<target> into a VERIFIED snapshot URL.

Uses ONLY the anonymous Wayback playback endpoint — https://web.archive.org/web/<ts>/<url>
redirects to the capture nearest <ts>, so the FINAL url after redirects *is* the working
snapshot link, and a target with no captures returns HTTP 404. (The availability + CDX
APIs 429'd hard under earlier attempts; playback is not rate-limited the same way. One
request per target instead of two, sequential, with backoff.)

Ladder per target: newest capture first, then progressively older years if the newest
capture is a Wayback error page / captured origin error.

Resumable: appends one JSON record per target to resolved.jsonl. No sheet writes here.
"""
import json, os, re, sys, time
import requests

REPO = "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher"
DIR = f"{REPO}/notes/wayback-save-repair-20260805"
UA = "Mozilla/5.0 (compatible; pipelines-researcher/1.0)"

GAP = float(os.environ.get("GAP", "2.0"))
COOLDOWN = int(os.environ.get("COOLDOWN", "0"))
BACKOFF = [20, 45, 90, 180]
READ_BYTES = 32768          # Wayback injects a large JS banner before page body
LADDER = ["29991231235959", "2024", "2021", "2017"]   # newest first, then older

# Wayback's own failure pages (HTTP 200 but not the content) — specific strings only
BAD_MARKERS = (
    "Got an HTTP 30", "Got an HTTP 40", "Got an HTTP 50",
    "response at crawl time",
    "This content is not available in the Wayback Machine",
    "The Wayback Machine has not archived that URL",
    "Wayback Machine doesn't have that page archived",
    "Wayback Machine has not archived",
)
_last = [0.0]


def throttle():
    w = GAP - (time.monotonic() - _last[0])
    if w > 0:
        time.sleep(w)
    _last[0] = time.monotonic()


def fetch(url):
    """One throttled playback GET, reading only the first READ_BYTES."""
    for i in range(len(BACKOFF) + 1):
        throttle()
        try:
            with requests.get(url, headers={"User-Agent": UA}, timeout=60,
                              stream=True, allow_redirects=True) as r:
                if r.status_code == 429 or r.status_code in (500, 502, 503, 504):
                    if i < len(BACKOFF):
                        print(f"      {r.status_code} — backing off {BACKOFF[i]}s", flush=True)
                        time.sleep(BACKOFF[i])
                        continue
                    return None, f"HTTP {r.status_code} after retries"
                chunk = b""
                try:
                    for part in r.iter_content(8192):
                        chunk += part
                        if len(chunk) >= READ_BYTES:
                            break
                except Exception:
                    pass
                return dict(http=r.status_code, final=r.url, head=chunk,
                            memento=r.headers.get("memento-datetime"),
                            src=r.headers.get("x-archive-src"),
                            ctype=r.headers.get("content-type")), None
        except Exception as e:
            if i < len(BACKOFF):
                print(f"      {type(e).__name__} — backing off {BACKOFF[i]}s", flush=True)
                time.sleep(BACKOFF[i])
                continue
            return None, f"{type(e).__name__}: {e}"
    return None, "exhausted"


TS_RE = re.compile(r"/web/(\d{4,14})(?:[a-z_]*)/", re.I)


def try_ts(target, ts):
    r, err = fetch(f"https://web.archive.org/web/{ts}/{target}")
    if r is None:
        return dict(ok=False, reason=err, ts_req=ts)
    body = r["head"].decode("utf-8", "replace")
    marker = next((m for m in BAD_MARKERS if m in body), None)
    m = TS_RE.search(r["final"] or "")
    got_ts = m.group(1) if m else None
    ok = r["http"] == 200 and marker is None and got_ts is not None
    return dict(ok=ok, ts_req=ts, http=r["http"], final=r["final"], got_ts=got_ts,
                memento=r["memento"], archive_src=r["src"], ctype=r["ctype"],
                bytes=len(r["head"]), marker=marker,
                reason=None if ok else (marker or f"HTTP {r['http']}" if r["http"] != 200
                                        else "no-timestamp-in-final"))


def live_probe(target):
    """Is the ORIGINAL page still up? Not archive.org — outside the throttle."""
    try:
        with requests.get(target, headers={"User-Agent": UA}, timeout=20,
                          stream=True, allow_redirects=True) as r:
            for _ in r.iter_content(2048):
                break
            return dict(http=r.status_code)
    except Exception as e:
        return dict(http=None, error=type(e).__name__)


def resolve(target):
    rec = dict(target=target, tried=[])
    seen_ts = set()
    for ts in LADDER:
        a = try_ts(target, ts)
        rec["tried"].append({k: a.get(k) for k in
                             ("ts_req", "http", "got_ts", "ok", "reason")})
        if a["ok"]:
            rec.update(bucket="RESOLVED", snapshot=a["final"], snapshot_ts=a["got_ts"],
                       memento=a["memento"], archive_src=a["archive_src"],
                       ctype=a["ctype"], head_bytes=a["bytes"],
                       ladder_step=ts)
            return rec
        # a 404 from playback means "nothing archived at all" — no point walking the ladder
        if a.get("http") == 404:
            rec.update(bucket="NO_CAPTURE", live=live_probe(target))
            return rec
        if a.get("got_ts"):
            if a["got_ts"] in seen_ts:      # ladder converged on the same bad capture
                break
            seen_ts.add(a["got_ts"])
        # A 5xx is often a property of THAT capture (a poisoned WARC record), not a
        # transient outage — keep walking the ladder to older captures instead of bailing.
        # Only a total failure across every rung falls through to LOOKUP_ERROR below.
    if rec["tried"] and all((t.get("http") is None or t.get("http", 0) >= 500)
                            for t in rec["tried"]):
        rec.update(bucket="LOOKUP_ERROR", live=live_probe(target))
    else:
        rec.update(bucket="CAPTURES_BUT_UNVERIFIED", live=live_probe(target))
    return rec


def main():
    raw = json.load(open(f"{DIR}/raw_targets.json"))
    norm = lambda t: t.strip().rstrip(",;)\"' ").strip()
    targets = sorted({norm(t) for t in raw if norm(t)})
    jl = f"{DIR}/resolved.jsonl"
    have = {}
    if os.path.exists(jl):
        for line in open(jl):
            line = line.strip()
            if line:
                r = json.loads(line)
                if r.get("bucket") != "LOOKUP_ERROR":
                    have[r["target"]] = r
    todo = [t for t in targets if t not in have]
    print(f"targets: {len(targets)}; cached: {len(have)}; to do: {len(todo)}", flush=True)
    if COOLDOWN and todo:
        print(f"cooling down {COOLDOWN}s...", flush=True)
        time.sleep(COOLDOWN)
    with open(jl, "a") as fh:
        for n, t in enumerate(todo, 1):
            r = resolve(t)
            fh.write(json.dumps(r) + "\n")
            fh.flush()
            have[t] = r
            extra = r.get("snapshot_ts") or (r.get("live") or {}).get("http") or ""
            print(f"  [{n}/{len(todo)}] {r['bucket']:24s} {str(extra):14s} {t[:80]}", flush=True)
    out = [have[t] for t in targets if t in have]
    json.dump(out, open(f"{DIR}/resolved.json", "w"), indent=1)
    from collections import Counter
    print("\n=== buckets ===", flush=True)
    for b, c in Counter(r["bucket"] for r in out).most_common():
        print(f"  {b}: {c}")


if __name__ == "__main__":
    main()
