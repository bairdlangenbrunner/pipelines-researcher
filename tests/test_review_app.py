"""Review app server tests (read routes; decisions are in test_review_store.py). Real server on an ephemeral loopback port."""
import gzip
import json
import threading
import urllib.error
import urllib.request

import pytest

import review_data
import review_fixture
import server


@pytest.fixture
def live(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    path = tmp_path / "review_data.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    app = server.App(path, "tester", batches_root=s["root"])
    httpd = server.make_server(app, "127.0.0.1", 0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"
    yield base, data, s
    httpd.shutdown()
    httpd.server_close()


def get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def post(url, body=b"{}"):
    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_binds_loopback(live):
    base, _, _ = live
    assert base.startswith("http://127.0.0.1:")


def test_refuses_non_loopback():
    for h in ("0.0.0.0", "192.168.1.5", "example.com"):
        with pytest.raises(ValueError):
            server.ensure_loopback(h)
    with pytest.raises(SystemExit):
        server.main(["--host", "0.0.0.0", "--no-open"])
    server.ensure_loopback("localhost")
    server.ensure_loopback("127.0.0.1")


def test_api_data_matches_fixture(live):
    base, data, _ = live
    st, body, _h = get(base + "/api/data")
    assert st == 200
    assert json.loads(body) == data
    st, body, h = get(base + "/api/data", {"Accept-Encoding": "gzip"})
    assert h.get("Content-Encoding") == "gzip"
    assert json.loads(gzip.decompress(body)) == data


def test_whoami(live):
    base, _, _ = live
    st, body, _h = get(base + "/api/whoami")
    w = json.loads(body)
    assert st == 200 and w["reviewer"] == "tester"
    assert w["caps"] == {"decide": True, "refresh": False, "push": False}


def test_absent_routes_and_refresh_refused_without_build(live):
    base, _, _ = live
    for p in ("/api/push/plan", "/api/push"):
        assert post(base + p)[0] == 404
        assert get(base + p)[0] == 404
    assert get(base + "/api/refresh")[0] == 404          # POST only
    st, body = post(base + "/api/refresh")               # this App was not built (= --no-build)
    assert st == 409 and "no-build" in body["error"]


def test_static_files(live):
    base, _, _ = live
    st, body, h = get(base + "/")
    assert st == 200 and b'<script src="app.js">' in body and "text/html" in h["Content-Type"]
    assert get(base + "/app.js")[0] == 200
    assert get(base + "/style.css")[0] == 200
    assert get(base + "/nope.js")[0] == 404


def test_path_traversal_refused(live):
    base, _, _ = live
    for p in ("/../server.py", "/%2e%2e/server.py", "/..%2fserver.py", "/%2e%2e%2f%2e%2e%2fCLAUDE.md",
              "/geo/../../data/x.json"):
        assert get(base + p)[0] == 404, p


def test_geo_serves_only_json_under_batches(live):
    base, _, s = live
    f = s["root"] / "g.geojson"
    f.write_text('{"type":"FeatureCollection","features":[]}')
    (s["root"] / "x.txt").write_text("no")
    assert get(base + "/geo/g.geojson")[0] == 200
    assert get(base + "/geo/x.txt")[0] == 404


def test_bad_host_header_refused(live):
    base, _, _ = live
    st, _b, _h = get(base + "/api/data", {"Host": "evil.example"})
    assert st == 403
