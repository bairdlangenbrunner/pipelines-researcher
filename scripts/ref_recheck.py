#!/usr/bin/env python3
"""Re-open every proposed ref ourselves; never trust a shard's own `verifications`.

A shard's `verifications[]` block is written by the research agent, and nothing downstream
re-ran it. On Russia R2 P0753 (2026-09-15) the agent wrote `"status": 200, "ok": true` for
`nord-stream.com/press-info/press-releases/nord-stream-s-project-costs-remain-74-billion-euros-367/`
while its own note on the same entry said the live page "blocked/times out" and it had read a
Wayback copy instead. The whole old nord-stream.com site had been replaced by a one-page stub,
so every deep link on it was a 404. The review page showed the line as high, and ten cells
with dead nord-stream.com links reached the sheet on 2026-10-15 (Baird caught it 2026-10-17).

This module is the independent check. A URL is DEAD only on HTTP 404 or 410 through the full
`fetch.py` ladder (browser UA, curl_cffi impersonation, clearance cookie), so a bot wall, a
geo-block or a timeout is never called dead. Results are cached in `work/ref_recheck_cache.json`
for a week, so the blocking callers stay cheap:

  - `scripts/check_shard_coverage.py` blocks a shard that proposes a dead ref (per shard, before
    a subagent finishes);
  - `review_app/push.py` skips any line that would write a dead ref to the sheet;
  - this CLI audits a staging dir (or every pending one) and, with `--fix-wayback`, swaps each
    dead proposed ref for its newest Internet Archive capture that loads.

    python scripts/ref_recheck.py --staging batches/<scope>/staging/<run>/ [--fix-wayback [--apply]]
    python scripts/ref_recheck.py --all-pending [--fix-wayback [--apply]]
    python scripts/ref_recheck.py --urls U [U ...]

A dead ref with no usable capture is listed for a person: find another source for the value.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urlparse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

CACHE = ROOT / "work" / "ref_recheck_cache.json"
TTL = timedelta(days=7)
DEAD = {"404", "410"}
_MIN_INTERVAL = 1.0
_lock = threading.Lock()


def _now():
    return datetime.now(timezone.utc)


def _load_cache() -> dict:
    try:
        return json.loads(CACHE.read_text())
    except Exception:
        return {}


def _save_cache(c: dict) -> None:
    CACHE.parent.mkdir(exist_ok=True)
    tmp = CACHE.with_suffix(".tmp")
    tmp.write_text(json.dumps(c, indent=1, sort_keys=True))
    tmp.replace(CACHE)


def _fresh(e: dict) -> bool:
    try:
        return _now() - datetime.fromisoformat(e["checked"]) < TTL
    except Exception:
        return False


def _is_archive(u: str) -> bool:
    return "web.archive.org/web/" in u or "archive.org/details/" in u or "archive.ph/" in u


def _probe(url: str) -> dict:
    from fetch import fetch_page
    try:
        p = fetch_page(url, timeout=30)
        st = str(p.status)
    except Exception as e:      # missing curl and the like: unknown, never dead
        return {"status": "000", "dead": False, "note": f"{type(e).__name__}"}
    if st in DEAD:              # a 404 is deterministic, but one retry costs little and rules out a flaky edge
        time.sleep(1)
        try:
            st = str(fetch_page(url, timeout=30).status)
        except Exception:
            pass
    return {"status": st, "dead": st in DEAD, "note": ", ".join(p.notes)}


def liveness(urls, refresh: bool = False, workers: int = 8, quiet: bool = True) -> dict:
    """{url: {"status", "dead", "checked", "note"}} for every http(s) URL, cached a week."""
    uniq = [u for u in dict.fromkeys(str(u).strip() for u in urls) if u.lower().startswith("http")]
    cache = _load_cache()
    todo = [u for u in uniq if refresh or not _fresh(cache.get(u) or {})]
    if todo:
        os.environ.setdefault("LNGCT_NO_BROWSER", "1")
        next_ok: dict[str, float] = {}

        def one(u):
            dom = urlparse(u).netloc.lower()
            with _lock:
                t = max(time.monotonic(), next_ok.get(dom, 0.0))
                next_ok[dom] = t + _MIN_INTERVAL
            d = t - time.monotonic()
            if d > 0:
                time.sleep(d)
            return u, _probe(u)

        n = 0
        with ThreadPoolExecutor(max_workers=max(1, min(workers, len(todo)))) as ex:
            for u, r in ex.map(one, todo):
                r["checked"] = _now().isoformat(timespec="seconds")
                cache[u] = r
                n += 1
                if not quiet and n % 50 == 0:
                    print(f"  checked {n}/{len(todo)}", file=sys.stderr)
                    _save_cache(cache)
        _save_cache(cache)
    return {u: cache[u] for u in uniq if u in cache}


def wayback_capture(url: str) -> str | None:
    """Newest Internet Archive capture of `url` that answered 200 and still loads, or None."""
    from fetch import fetch_page
    api = ("https://web.archive.org/cdx/search/cdx?url=" + quote(url, safe="")
           + "&filter=statuscode:200&output=json&fl=timestamp,original&limit=-5")
    rows = None
    for attempt in range(4):        # a 429 is a rate limit, not a ban: back off and retry
        p = fetch_page(api, timeout=40)
        if str(p.status) == "200":
            try:
                rows = json.loads(p.text)
            except json.JSONDecodeError:
                rows = None
            break
        time.sleep(5 * (attempt + 1))
    if not rows or len(rows) < 2:
        return None
    for ts, orig in reversed(rows[1:]):
        snap = f"https://web.archive.org/web/{ts}/{orig}"
        raw = fetch_page(f"https://web.archive.org/web/{ts}id_/{orig}", timeout=40)
        if str(raw.status) == "200" and len(raw.text) > 500:
            return snap
    return None


# -- staged JSON ---------------------------------------------------------------------------

SKIP_FILES = {"review_decisions.json", "worklist.json", "wiki_citations.json", "deepsweep_args.json"}


def staged_files(staging: Path):
    for p in sorted(staging.rglob("*.json")):
        if p.name in SKIP_FILES or p.name.endswith(".prior.json") or ".colmap" in p.name:
            continue
        yield p


def records(obj, path=()):
    """Every dict carrying a `proposed_refs` list, with where it sits."""
    if isinstance(obj, dict):
        if isinstance(obj.get("proposed_refs"), list):
            yield path, obj
        for k, v in obj.items():
            yield from records(v, path + (k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from records(v, path + (i,))


def _pid_of(rec, file_path: Path):
    return rec.get("project_id") or rec.get("pid") or (file_path.stem if file_path.stem.startswith("P") else "")


def self_reported_ok(rec, url) -> bool:
    for v in rec.get("verifications") or []:
        if isinstance(v, dict) and v.get("url") == url and (v.get("ok") is True or str(v.get("status")) == "200"):
            return True
    return False


def audit(staging_dirs, refresh=False):
    found = []          # (file, path, rec, pid)
    urls = []
    for s in staging_dirs:
        for f in staged_files(s):
            try:
                d = json.loads(f.read_text())
            except Exception:
                continue
            for path, rec in records(d):
                pid = _pid_of(rec, f) or (path and isinstance(d, dict) and d.get("project_id")) or ""
                found.append((f, path, rec, pid))
                urls += [u for u in rec["proposed_refs"] if isinstance(u, str) and not _is_archive(u)]
    live = liveness(urls, refresh=refresh, quiet=False)
    dead = []
    for f, path, rec, pid in found:
        for u in rec["proposed_refs"]:
            e = live.get(str(u).strip())
            if e and e["dead"]:
                dead.append({"file": f, "path": path, "pid": pid, "unit": rec.get("ref_col") or rec.get("concern_type")
                             or rec.get("verdict") or "", "url": u, "status": e["status"],
                             "self_reported_ok": self_reported_ok(rec, u)})
    return dead, len(set(urls))


def _dump_like(original: str, data) -> str | None:
    """Re-serialize `data` the way `original` was written, or None if no format round-trips."""
    probe = json.loads(original)
    for ind, ea, nl in itertools.product((1, 2, None), (False, True), ("\n", "")):
        if json.dumps(probe, ensure_ascii=ea, indent=ind) + nl == original:
            return json.dumps(data, ensure_ascii=ea, indent=ind) + nl
    return None


def fix_wayback(dead, apply=False):
    snaps, fixed, unfixed = {}, [], []
    for u in sorted({d["url"] for d in dead}):
        snaps[u] = wayback_capture(u)
        print(f"  {'capture ' + snaps[u] if snaps[u] else 'NO usable capture'}  <-  {u}")
    by_file = {}
    for d in dead:
        by_file.setdefault(d["file"], []).append(d)
    for f, ds in by_file.items():
        text = f.read_text()
        data = json.loads(text)
        changed = False
        for _, rec in records(data):
            for i, u in enumerate(list(rec["proposed_refs"])):
                if u not in snaps or not any(d["url"] == u for d in ds):
                    continue
                snap = snaps[u]
                if not snap:
                    unfixed.append((f, _pid_of(rec, f), rec.get("ref_col") or "", u))
                    continue
                if snap in rec["proposed_refs"]:
                    rec["proposed_refs"].pop(i)
                else:
                    rec["proposed_refs"][i] = snap
                for v in rec.get("verifications") or []:
                    if isinstance(v, dict) and v.get("url") == u:
                        v["url"], v["dead_origin"] = snap, u
                        v["status"], v["ok"] = 200, True
                        v["note"] = (v.get("note") or "") + (f" [ref_recheck {datetime.now().date()}: the live page "
                                                              f"returns 404, so its Internet Archive copy is cited.]")
                host = urlparse(u).netloc.removeprefix("www.")
                rec["researcher_notes"] = (rec.get("researcher_notes") or "").rstrip() + (
                    f" The {host} page cited here no longer exists (it returns 404), so its Internet Archive "
                    f"copy is cited instead.")
                changed = True
                fixed.append((f, _pid_of(rec, f), rec.get("ref_col") or "", u, snap))
        if changed:
            out = _dump_like(text, data)
            if out is None:
                print(f"  NOT WRITTEN {f}: its formatting does not round-trip; fix by hand", file=sys.stderr)
            elif apply:
                f.write_text(out)
    return fixed, unfixed


def pending_dirs():
    out = []
    for s in sorted((ROOT / "batches").glob("*/staging/*")):
        if s.is_dir() and any(s.glob("*.json")):
            out.append(s)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--staging", action="append", help="a staging dir (repeatable)")
    g.add_argument("--all-pending", action="store_true", help="every dir under batches/*/staging/")
    g.add_argument("--urls", nargs="+", help="just check these URLs")
    ap.add_argument("--refresh", action="store_true", help="ignore the week-long cache")
    ap.add_argument("--fix-wayback", action="store_true", help="swap dead proposed refs for their newest capture")
    ap.add_argument("--apply", action="store_true", help="with --fix-wayback: write the staged files")
    a = ap.parse_args()
    if a.urls:
        for u, e in liveness(a.urls, refresh=a.refresh).items():
            print(f"{'DEAD' if e['dead'] else 'ok  '} {e['status']}  {u}")
        return
    dirs = pending_dirs() if a.all_pending else [Path(s).resolve() for s in a.staging]
    dead, n = audit(dirs, refresh=a.refresh)
    print(f"{n} distinct proposed ref(s) checked in {len(dirs)} staging dir(s); "
          f"{len({d['url'] for d in dead})} dead, on {len(dead)} staged unit(s).")
    for d in dead:
        flag = "  [the shard said it loaded]" if d["self_reported_ok"] else ""
        print(f"  DEAD {d['status']} {d['pid']:6} {str(d['unit'])[:28]:28} {d['url']}{flag}"
              f"  ({d['file'].relative_to(ROOT)})")
    if a.fix_wayback and dead:
        fixed, unfixed = fix_wayback(dead, apply=a.apply)
        print(f"\n{len(fixed)} unit ref(s) {'swapped' if a.apply else 'would be swapped'} for a capture; "
              f"{len(unfixed)} have no usable capture and need another source:")
        for f, pid, col, u in unfixed:
            print(f"  NEEDS A SOURCE {pid} {col} {u}  ({f.relative_to(ROOT)})")
        if not a.apply:
            print("(dry run: pass --apply to write)")
    sys.exit(1 if dead and not (a.fix_wayback and a.apply) else 0)


if __name__ == "__main__":
    main()
