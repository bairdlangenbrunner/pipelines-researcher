"""
Local review server: the phase 1 backend behind review_app/web/ (milestone 2: read-only).

    python review_app/server.py --country Russia --commodity gas [--dirs DIR ...]
        [--exclude-pids P1,P2] [--data PATH] [--reviewer NAME] [--port 8766] [--no-open] [--no-build]

Standard library only; binds 127.0.0.1 and refuses anything but loopback (the data is
unreleased). Without --no-build it first runs review_data.main to (re)build the dataset
for --country/--commodity into --data (default work/review_data.json); with --no-build it
serves that file as it is.

    GET  /                 static front end (review_app/web/)
    GET  /api/data         the dataset JSON (gzip when the browser accepts it)
    GET  /api/whoami       {"reviewer": ..., "caps": {"decide": false, "refresh": false, "push": false}}
    GET  /geo/<path>       a *.geojson / *.json under batches/ (the route lines' candidate geometry)
    POST /api/decide       501 {"error": "milestone 3"}
    POST /api/item         501 {"error": "milestone 3"}

/api/refresh, /api/push/plan and /api/push do not exist yet (404). Nothing here writes.
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
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WEB = HERE / "web"
for p in (ROOT / "scripts", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import paths  # noqa: E402
import review_data  # noqa: E402

# what this server can do; the front end reads these and hides/disables the matching controls
CAPS = {"decide": False, "refresh": False, "push": False}
NOT_YET = {"/api/decide", "/api/item"}


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


class App:
    """Server state: the dataset bytes (plus a gzipped copy) and who is reviewing."""

    def __init__(self, data_path, reviewer, batches_root=None):
        self.data_path = Path(data_path)
        self.reviewer = reviewer
        self.batches_root = Path(batches_root) if batches_root else ROOT / "batches"
        self.lock = threading.Lock()
        self.load()

    def load(self):
        raw = self.data_path.read_bytes()
        json.loads(raw.decode("utf-8"))            # refuse to serve a file that is not JSON
        self.raw = raw
        self.gz = gzip.compress(raw, 6)

    def whoami(self):
        return {"reviewer": self.reviewer, "caps": dict(CAPS)}


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
                if "gzip" in (self.headers.get("Accept-Encoding") or ""):
                    return self._send(app.gz, "application/json; charset=utf-8",
                                      extra={"Content-Encoding": "gzip"})
                return self._send(app.raw, "application/json; charset=utf-8")
            if path == "/api/whoami":
                return self._json(app.whoami())
            if path.startswith("/geo/"):
                return self._file(app.batches_root, path[len("/geo/"):], {".geojson", ".json"})
            if path.startswith("/api/"):
                return self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return self._file(WEB, "index.html" if path in ("/", "") else path.lstrip("/"))

        def do_POST(self):
            if not self._host_ok():
                return self._json({"error": "bad host"}, HTTPStatus.FORBIDDEN)
            path = unquote(self.path.split("?", 1)[0])
            if path in NOT_YET:
                return self._json({"error": "milestone 3"}, HTTPStatus.NOT_IMPLEMENTED)
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
    ap.add_argument("--country", help="required unless --no-build")
    ap.add_argument("--commodity", choices=["gas", "oil"], help="required unless --no-build")
    ap.add_argument("--dirs", nargs="*", default=None, help="explicit staging dirs (skips discovery)")
    ap.add_argument("--exclude-pids", default="", help="comma-separated ProjectIDs to drop")
    ap.add_argument("--data", default=None, help="dataset path (default work/review_data.json)")
    ap.add_argument("--reviewer", default=None, help="default: git config user.name")
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
        if not (args.country and args.commodity):
            raise SystemExit("--country and --commodity are required unless --no-build")
        build = ["--country", args.country, "--commodity", args.commodity, "--out", str(data_path)]
        if args.dirs:
            build += ["--dirs", *args.dirs]
        if args.exclude_pids:
            build += ["--exclude-pids", args.exclude_pids]
        review_data.main(build)
    elif not data_path.exists():
        raise SystemExit(f"{data_path} not found: run without --no-build, or pass --data")
    app = App(data_path, args.reviewer or git_user())
    httpd = make_server(app, args.host, args.port)
    url = f"http://{args.host}:{httpd.server_address[1]}/"
    print(f"review app: {url}  (reviewer: {app.reviewer}; read-only; Ctrl-C to stop)", file=sys.stderr)
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
