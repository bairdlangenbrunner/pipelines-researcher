"""
Local review server: the phase 1 backend behind review_app/web/ (milestone 4: items, refresh).

    python review_app/server.py [--commodity gas] [--include-done]       # the review-app batch
    python review_app/server.py --country Russia [--country "United States" ...] --commodity gas [--dirs DIR ...]
        [--exclude-pids P1,P2] [--data PATH] [--reviewer NAME] [--port 8766] [--no-open] [--no-build]

Standard library only; binds 127.0.0.1 and refuses anything but loopback (the data is
unreleased). Without --no-build it first runs review_data.main to (re)build the dataset
for --country/--commodity -- or, with no --country, for the countries the review-app batch
includes (review_app/scopes.py; all-decided ones dropped) -- into --data (default
work/review_data.json); with --no-build it serves that file as it is. /api/refresh rebuilds the
same way, so countries added to the batch since startup come in on the next refresh.

    GET  /                 static front end (review_app/web/)
    GET  /api/data         the dataset JSON (gzip when the browser accepts it)
    GET  /api/whoami       {"reviewer": ..., "caps": {"decide": true, "refresh": false, "push": false}}
    GET  /api/decisions?dir=<label>   that staging dir's current latest-per-key records (review_decisions.json)
    GET  /geo/<path>       a *.geojson / *.json under batches/ (the route lines' candidate geometry)
    POST /api/decide       [{key, decision, suggested_value?, note?} | {key, rival: <concern key>} | {key, undo: true}, ...]
                           -> {"saved": [record, ...]}; reviewer and ts are stamped here, never taken
                           from the client. An accept that self-resolves an open concern (its proposed
                           value equals the concern's contested value) also saves that concern's
                           `dismissed` item record, and a `rival` request (the concern's candidate taken
                           instead of the proposal, stored as a suggest) saves its `confirmed` record,
                           after the line records (item records carry `call`; store.decide). Appends to
                           <dir>/review_log.jsonl and regenerates <dir>/review_decisions.json.
                           400 = refused, nothing written.
    POST /api/item         [{key, call, note?} | {key, undo: true}, ...] -> {"saved": [record, ...]};
                           the call must be in store.ITEM_CALLS[kind]; same sidecars as /api/decide.
                           400 = refused, nothing written.
    POST /api/refresh      runs scripts/refresh_csvs.sh (App.refresh_cmd; pulls the LIVE sheet, read-only,
                           ~1 min), rebuilds the dataset with the startup build args, then stamps a
                           `backend sync` record on every line the new snapshot already holds and no
                           person decided -> {"snapshot", "lines", "synced"}. 409 when the server
                           was started with --no-build; 502 / 504 when the pull fails / times out.

    POST /api/push/plan    pull.py (store -> sidecars, read-only on Google), then push.build_plan (reads the live
                           sheet, writes nothing there) -> {token, cells: [{tab, cell, ProjectID, column, before,
                           after}], skipped: [[key, why]], stale}. Only with a decision store (not --no-store).
    POST /api/push         {token} -> push.apply of exactly that plan (backup CSV, RAW cell-scoped write, read-back,
                           `push` records) -> {cells, log, refreshed|refresh_error}. 409 when the token is not the last plan or the sheet
                           moved since it; the page asks the person to confirm the cell list first.
Accepted cells reach the sheet only through push.py's plan/apply, here or on the command line.

Every decision goes to the Google decision store FIRST (review_app/ledger.py: the `log` tab of the
store spreadsheet in review_app/google.json, origin 'local') and to the staging dir's sidecars second;
the store is the single source of truth the served Google page, pull.py, publish.py and push.py all
share. A store that cannot be written refuses the decision (502, nothing recorded anywhere).
--no-store (tests, dev) writes the sidecars alone and says so. Otherwise the only things written are
the two decision sidecars inside the staging dirs named by the dataset (and, on refresh, data/
snapshots by the pull script and the rebuilt dataset file).
"""
import argparse
import gzip
import ipaddress
import json
import mimetypes
import subprocess
import sys
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WEB = HERE / "web"
for p in (ROOT / "scripts", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import contextlib  # noqa: E402
import io  # noqa: E402

import ledger  # noqa: E402
import paths  # noqa: E402
import pull  # noqa: E402
import review_data  # noqa: E402
import store  # noqa: E402

# what this server can do; the front end reads these and hides/disables the matching controls
CAPS = {"decide": True, "refresh": False, "push": False}    # refresh: per App (built, not --no-build); push: per App (has a store)
REFRESH_CMD = [str(ROOT / "scripts" / "refresh_csvs.sh")]
REFRESH_TIMEOUT = 600


def ensure_loopback(host):
    """Raise ValueError unless `host` is a loopback address."""
    if host == "localhost":
        return
    try:
        if ipaddress.ip_address(host).is_loopback:
            return
    except ValueError:
        pass
    raise ValueError(f"refusing to bind {host!r}: the review server is loopback-only")


class Refusal(Exception):
    """A refresh that cannot run or failed: (HTTP status, message)."""

    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


class App:
    """Server state: the dataset bytes (plus a gzipped copy) and who is reviewing."""

    def __init__(self, data_path, reviewer, batches_root=None, build_argv=None, refresh_cmd=None,
                 refresh_timeout=REFRESH_TIMEOUT, ledger=None):
        self.data_path = Path(data_path)
        self.reviewer = store.initials(reviewer)     # people are recorded by initials
        self.ledger = ledger                         # ledger.Ledger (store first) or None (sidecars alone)
        self.batches_root = Path(batches_root) if batches_root else ROOT / "batches"
        self.build_argv = list(build_argv) if build_argv else None    # review_data.main args; None = --no-build
        self.refresh_cmd = list(refresh_cmd) if refresh_cmd else list(REFRESH_CMD)
        self.refresh_timeout = refresh_timeout
        self.lock = threading.Lock()
        self.refreshing = threading.Lock()
        self.pushing = threading.Lock()
        self.load()

    def load(self):
        raw = self.data_path.read_bytes()
        json.loads(raw.decode("utf-8"))            # refuse to serve a file that is not JSON
        self.data = json.loads(raw.decode("utf-8"))

    def current(self):
        """(raw, gz) of the dataset with every staging dir's sidecars laid over it right now,
        so a page reload (or a rebuilt dataset) shows the decisions made so far."""
        with self.lock:
            store.overlay(self.data, self.dirs())
            raw = json.dumps(self.data, ensure_ascii=False).encode("utf-8")
        return raw, gzip.compress(raw, 6)

    def dirs(self):
        return store.dir_paths(self.data, self.batches_root.parent)

    def sink(self, origin="local"):
        """The write path for store.*: the ledger's (store first), or None = sidecars alone."""
        if self.ledger is None:
            return None
        self.ledger.origin = origin
        self.ledger.scope, self.ledger.snapshot = ledger.scope_of(self.data)
        return self.ledger.sink

    def decide(self, records):
        """store.decide under this server's lock; the dataset on disk is never rewritten (the
        page overlays the returned records; a rebuild overlays the sidecars). The overlay runs
        first so the contested lock sees item calls made since the last /api/data."""
        with self.lock:
            store.overlay(self.data, self.dirs())
            return store.decide(records, self.data, self.reviewer, self.dirs(), sink=self.sink())

    def item(self, records):
        with self.lock:
            return store.record_items(records, self.data, self.reviewer, self.dirs(), sink=self.sink())

    def refresh(self):
        """Pull the live sheet via refresh_cmd, rebuild, reload, backend-sync. Raises Refusal
        (status, message) when it cannot run; returns {"snapshot", "lines", "synced"}."""
        if not self.build_argv:
            raise Refusal(409, "server started with --no-build: nothing to rebuild the dataset from")
        if not self.refreshing.acquire(blocking=False):
            raise Refusal(409, "a refresh is already running")
        try:
            try:
                r = subprocess.run(self.refresh_cmd, cwd=ROOT, capture_output=True, text=True,
                                   timeout=self.refresh_timeout)
            except subprocess.TimeoutExpired:
                raise Refusal(504, f"refresh timed out after {self.refresh_timeout} s")
            except OSError as e:
                raise Refusal(502, f"could not run {self.refresh_cmd[0]}: {e}")
            if r.returncode != 0:
                tail = (r.stderr or r.stdout or "").strip().splitlines()[-3:]
                raise Refusal(502, f"refresh failed (exit {r.returncode}): " + " / ".join(tail))
            with self.lock:
                review_data.main(self.build_argv)
                self.load()
                store.overlay(self.data, self.dirs())
                snap = self.data.get("scope", {}).get("snapshot", "")
                synced = store.sync_backend(self.data, self.dirs(), snap, sink=self.sink("sync"))
                store.overlay(self.data, self.dirs())
                n = sum(len(p.get("lines", [])) for p in self.data.get("pipelines", []))
            return {"snapshot": snap, "lines": n, "synced": len(synced)}
        finally:
            self.refreshing.release()

    def push_plan(self):
        """Pull the store into the sidecars, then plan the push against the live sheet (no sheet write)."""
        import push                                  # imports gws helpers; only needed when pushing
        if self.ledger is None:
            raise Refusal(409, "no decision store on this server (--no-store): push from the command line")
        if not self.pushing.acquire(blocking=False):
            raise Refusal(409, "a push is already running")
        try:
            commodity = (self.data.get("scope") or {}).get("commodity") or "gas"
            try:
                with self.lock:
                    pull.pull(pull.config())
                plan, skipped, meta = push.build_plan(commodity)
            except (pull.GwsError, SystemExit) as e:
                raise Refusal(502, f"could not plan the push: {e}")
            push.save_plan(plan, meta, commodity)
            return {"token": push.token(plan), "stale": len(meta.get("__stale__", [])), "skipped": skipped,
                    "cells": [{k: p.get(k) for k in ("tab", "cell", "ProjectID", "column", "before", "after", "replaces")} for p in plan]}
        finally:
            self.pushing.release()

    def push_apply(self, token):
        """Write exactly the last saved plan if its token is `token` (push.apply re-checks every cell)."""
        import push
        if self.ledger is None:
            raise Refusal(409, "no decision store on this server (--no-store): push from the command line")
        plan_path = ROOT / "work" / "push_plan.json"
        if not plan_path.exists() or json.loads(plan_path.read_text()).get("token") != token:
            raise Refusal(409, "that plan is no longer the current one: build the plan again")
        if not self.pushing.acquire(blocking=False):
            raise Refusal(409, "a push is already running")
        out = io.StringIO()
        try:
            with self.lock, contextlib.redirect_stdout(out):
                try:
                    push.apply(plan_path)
                except SystemExit as e:
                    raise Refusal(409, f"nothing more was written: {e}")
            log = out.getvalue()
            res = {"cells": len(json.loads(plan_path.read_text())["plan"]), "log": log}
        finally:
            self.pushing.release()
        # the dataset's backend comparison is the pre-push snapshot until the sheet is re-pulled
        if self.build_argv:
            try:
                res["refreshed"] = self.refresh()
            except Refusal as e:
                res["refresh_error"] = str(e)
        return res

    def decisions(self, label):
        d = self.dirs().get(label)
        if d is None:
            return None
        return store.latest(store.read_log(d))

    def whoami(self):
        return {"reviewer": self.reviewer, "caps": dict(CAPS, refresh=bool(self.build_argv), push=self.ledger is not None),
                "store": self.ledger is not None}


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        server_version = "review_app/1"

        def log_message(self, fmt, *args):
            sys.stderr.write("%s %s\n" % (self.command, self.path))

        def _host_ok(self):
            # DNS-rebinding guard: only answer requests addressed to a loopback host
            host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
            try:
                ensure_loopback(host)
                return True
            except ValueError:
                return False

        def _send(self, body, ctype, status=HTTPStatus.OK, extra=None):
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def _json(self, obj, status=HTTPStatus.OK):
            self._send(json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                       "application/json; charset=utf-8", status)

        def _file(self, base, rel, suffixes=None):
            """Serve base/rel if it resolves inside base (no traversal, no symlink escape)."""
            base = base.resolve()
            try:
                f = (base / rel).resolve()
            except (OSError, ValueError):
                return self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            if base not in f.parents or not f.is_file() or (suffixes and f.suffix.lower() not in suffixes):
                return self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            ctype = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
            if f.suffix.lower() == ".geojson":
                ctype = "application/geo+json"
            if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
                ctype += "; charset=utf-8"
            self._send(f.read_bytes(), ctype)

        def do_GET(self):
            if not self._host_ok():
                return self._json({"error": "bad host"}, HTTPStatus.FORBIDDEN)
            path = unquote(self.path.split("?", 1)[0])
            if path == "/api/data":
                raw, gz = app.current()
                if "gzip" in (self.headers.get("Accept-Encoding") or ""):
                    return self._send(gz, "application/json; charset=utf-8",
                                      extra={"Content-Encoding": "gzip"})
                return self._send(raw, "application/json; charset=utf-8")
            if path == "/api/whoami":
                return self._json(app.whoami())
            if path == "/api/decisions":
                label = (parse_qs(urlsplit(self.path).query).get("dir") or [""])[0]
                recs = app.decisions(label)
                if recs is None:
                    return self._json({"error": "unknown dir"}, HTTPStatus.NOT_FOUND)
                return self._json({"dir": label, "decisions": recs})
            if path.startswith("/geo/"):
                return self._file(app.batches_root, path[len("/geo/"):], {".geojson", ".json"})
            if path.startswith("/api/"):
                return self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return self._file(WEB, "index.html" if path in ("/", "") else path.lstrip("/"))

        def do_POST(self):
            if not self._host_ok():
                return self._json({"error": "bad host"}, HTTPStatus.FORBIDDEN)
            path = unquote(self.path.split("?", 1)[0])
            if path == "/api/refresh":
                try:
                    return self._json(app.refresh())
                except Refusal as e:
                    return self._json({"error": str(e)}, e.status)
                except (Exception, SystemExit) as e:
                    print(f"review app: refresh failed: {e!r}", file=sys.stderr)
                    return self._json({"error": f"refresh failed: {e}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            if path in ("/api/push/plan", "/api/push"):
                try:
                    if path == "/api/push/plan":
                        return self._json(app.push_plan())
                    n = int(self.headers.get("Content-Length") or 0)
                    body = json.loads(self.rfile.read(n).decode("utf-8") or "null") or {}
                    return self._json(app.push_apply(str(body.get("token") or "")))
                except Refusal as e:
                    return self._json({"error": str(e)}, e.status)
                except (ValueError, UnicodeDecodeError):
                    return self._json({"error": "body is not JSON"}, HTTPStatus.BAD_REQUEST)
                except Exception as e:
                    print(f"review app: push failed: {e!r}", file=sys.stderr)
                    return self._json({"error": f"push failed: {e}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            if path in ("/api/decide", "/api/item"):
                try:
                    n = int(self.headers.get("Content-Length") or 0)
                    body = json.loads(self.rfile.read(n).decode("utf-8") or "null")
                except (ValueError, UnicodeDecodeError):
                    return self._json({"error": "body is not JSON"}, HTTPStatus.BAD_REQUEST)
                try:
                    return self._json({"saved": (app.decide if path == "/api/decide" else app.item)(body)})
                except store.Invalid as e:
                    return self._json({"error": str(e)}, HTTPStatus.BAD_REQUEST)
                except ledger.StoreError as e:     # the store refused: nothing recorded anywhere
                    print(f"review app: store write failed: {e!r}", file=sys.stderr)
                    return self._json({"error": f"decision store unreachable, nothing saved: {e}"}, HTTPStatus.BAD_GATEWAY)
                except Exception as e:     # a failed write (the log was rolled back): say so loudly
                    print(f"review app: write failed: {e!r}", file=sys.stderr)
                    return self._json({"error": f"write failed: {e}"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    return Handler


def make_server(app, host="127.0.0.1", port=8766):
    ensure_loopback(host)
    return ThreadingHTTPServer((host, port), make_handler(app))


def git_user():
    try:
        return subprocess.run(["git", "config", "user.name"], capture_output=True, text=True,
                              cwd=ROOT).stdout.strip() or "reviewer"
    except OSError:
        return "reviewer"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--country", action="append", default=None,
                    help="repeat (or comma-separate) for several countries; omit for the review-app batch")
    ap.add_argument("--commodity", choices=["gas", "oil"], help="required with --country; review-app batch default gas")
    ap.add_argument("--include-done", action="store_true", help="review-app batch: keep all-decided countries")
    ap.add_argument("--dirs", nargs="*", default=None, help="explicit staging dirs (skips discovery)")
    ap.add_argument("--exclude-pids", default="", help="comma-separated ProjectIDs to drop")
    ap.add_argument("--data", default=None, help="dataset path (default work/review_data.json)")
    ap.add_argument("--reviewer", default=None,
                    help="default: git config user.name; recorded as initials (store.initials)")
    ap.add_argument("--reviewer-email", default=None,
                    help="the address written on this person's rows in the Google decision store "
                         "(default: the gws-gem-write account's address)")
    ap.add_argument("--no-store", action="store_true",
                    help="DEV/TESTS ONLY: write the staging-dir sidecars alone, skipping the Google decision store")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8766)
    ap.add_argument("--no-open", action="store_true", help="do not open the browser")
    ap.add_argument("--no-build", action="store_true", help="serve --data as it is; do not rebuild")
    args = ap.parse_args(argv)
    try:
        ensure_loopback(args.host)
    except ValueError as e:
        raise SystemExit(str(e))
    data_path = Path(args.data) if args.data else paths.work_dir() / "review_data.json"
    if not args.no_build:
        if args.country and not args.commodity:
            raise SystemExit("--commodity is required with --country")
        build = [x for c in args.country or () for x in ("--country", c)]
        build += ["--commodity", args.commodity or "gas", "--out", str(data_path)]
        if args.include_done:
            build += ["--include-done"]
        if args.dirs:
            build += ["--dirs", *args.dirs]
        if args.exclude_pids:
            build += ["--exclude-pids", args.exclude_pids]
        review_data.main(build)
    elif not data_path.exists():
        raise SystemExit(f"{data_path} not found: run without --no-build, or pass --data")
    led = None
    if args.no_store:
        print("review app: --no-store: decisions go to the staging-dir sidecars ONLY and will not be in the "
              "Google decision store (the served page, publish.py and push.py will not see them)", file=sys.stderr)
    else:
        cfg = pull.config()
        if not cfg.get("store_sheet_id"):
            raise SystemExit("no decision store configured (review_app/google.json: store_sheet_id); "
                             "pass --no-store only for dev/tests")
        email = args.reviewer_email or ledger.whoami()
        if not email:
            raise SystemExit("cannot read the store account's address (gws-gem-write auth?): pass --reviewer-email, "
                             "or run `gws-gem-write auth login` yourself (needs a browser)")
        data0 = json.loads(data_path.read_text(encoding="utf-8"))
        led = ledger.Ledger(cfg["store_sheet_id"], *ledger.scope_of(data0), "local", reviewer_email=email)
    app = App(data_path, args.reviewer or git_user(), build_argv=None if args.no_build else build, ledger=led)
    httpd = make_server(app, args.host, args.port)
    url = f"http://{args.host}:{httpd.server_address[1]}/"
    where = (f"decisions write to the Google decision store ({led.scope}, as {led.reviewer_email}) then to each "
             "staging dir's review_log.jsonl" if led else "decisions write to each staging dir's review_log.jsonl ONLY")
    print(f"review app: {url}  (reviewer: {app.reviewer}; {where}; Ctrl-C to stop)", file=sys.stderr)
    if not args.no_open:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
