"""Phase 2, in a browser: the bundled Google page against Code.gs under the node fakes
(review_app/gas_dev/dev_server.js), two reviewers at once. Fixture scope, loopback only, never
Google. Skipped without node or playwright's chromium."""
import json
import socket
import subprocess
import time
import urllib.request

import pytest

import bundle
import gas_harness as H
import review_data
import review_fixture
import store

sync_api = pytest.importorskip("playwright.sync_api")
pytestmark = pytest.mark.skipif(H.node() is None, reason="node is not installed")

A, B = "baird@globalenergymonitor.org", "aiganym@globalenergymonitor.org"


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def browser():
    with sync_api.sync_playwright() as pw:
        try:
            b = pw.chromium.launch()
        except Exception as e:                       # the browser binary is not installed
            pytest.skip(f"chromium is not available: {e}")
        yield b
        b.close()


@pytest.fixture
def app(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    s["dataset"], s["dirs"] = data, store.dir_paths(data, tmp_path)
    out = tmp_path / "published"
    s["entry"] = H.publish_fixture(s, out)
    page = tmp_path / "index.html"
    page.write_text(bundle.bundle(), encoding="utf-8")          # web/ as it is now; the repo's bundle is not touched
    port = free_port()
    proc = subprocess.Popen([H.node(), str(H.ROOT / "review_app" / "gas_dev" / "dev_server.js"), "--data", str(out),
                             "--store", str(tmp_path / "store.json"), "--fresh", "--port", str(port),
                             "--no-bundle", "--page", str(page)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    base = f"http://127.0.0.1:{port}"
    for _ in range(100):
        try:
            urllib.request.urlopen(base + "/store", timeout=1).read()
            break
        except OSError:
            time.sleep(0.1)
    else:
        proc.kill()
        raise AssertionError(proc.stderr.read().decode()[-2000:])
    s["base"], s["out"] = base, out
    yield s
    proc.kill()
    proc.wait()


def rows(s):
    body = json.loads(urllib.request.urlopen(s["base"] + "/store").read())
    return [dict(zip(body[0], r)) for r in body[1:]] if body else []


def open_page(browser, s, user, errors):
    pg = browser.new_context(viewport={"width": 1400, "height": 900}).new_page()
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(f"{s['base']}/?user={user}")
    pg.wait_for_function("window.ReviewApp && ReviewApp.data && ReviewApp.data.pipelines.length > 0")
    return pg


LINE = """(key) => { for (const p of ReviewApp.data.pipelines) for (const l of p.lines) if (l.key === key)
  return {i: l._i, decision: l.decision || null, by: l.decided_by || null, reviewed: !!l.reviewed}; return null; }"""


def press(pg, pid, key, what):
    pg.evaluate("(pid) => { location.hash = '#/' + pid; }", pid)
    i = pg.evaluate(LINE, key)["i"]
    pg.wait_for_selector(f"#line-{i} [data-decide={what}]")
    pg.click(f"#line-{i} [data-decide={what}]")


def wait_line(pg, key, decision, by):
    pg.wait_for_function("([key, d, by]) => { const l = (%s)(key); return l && l.decision === d && l.by === by; }" % LINE,
                         arg=[key, decision, by])


def fill_line(data, pid, n=0):
    return [l for p in data["pipelines"] if p["pid"] == pid for l in p["lines"]
            if not l.get("in_backend") and not l.get("locked")][n]


def test_two_reviewers_share_one_store(browser, app):
    errors = []
    d = app["dataset"]
    l1, l2 = fill_line(d, "P9002", 0), fill_line(d, "P9002", 1)
    a, b = open_page(browser, app, A, errors), open_page(browser, app, B, errors)
    assert a.inner_text("#whoami") == A and b.inner_text("#whoami") == B
    assert a.evaluate("getComputedStyle(document.getElementById('sync')).display") == "none"      # no refresh, no push here
    assert a.evaluate("JSON.stringify(GasStore.caps)") == '{"decide":true,"refresh":false,"push":false}'
    assert "scope=russia-gas" in a.url

    # A holds a line: one row in the store, stamped by the server with A's login
    press(a, "P9002", l1["key"], "hold")
    wait_line(a, l1["key"], "hold", A)
    (r,) = rows(app)
    assert (r["reviewer"], r["decision"], r["key"], r["rec"], r["scope"]) == (A, "hold", l1["key"], "line", "russia-gas")

    # B hears about it on the next poll, without reloading
    assert b.evaluate(LINE, l1["key"])["decision"] is None
    b.evaluate("GasStore.poll()")
    wait_line(b, l1["key"], "hold", A)

    # A rejects another line; B's page has not polled since and presses accept on it:
    # refused, nothing stored, A's call shown, and the banner says who
    press(a, "P9002", l2["key"], "reject")
    wait_line(a, l2["key"], "reject", A)
    press(b, "P9002", l2["key"], "accept")
    wait_line(b, l2["key"], "reject", A)
    b.wait_for_function("!document.getElementById('banner').hidden")
    assert A in b.inner_text("#banner") and "nothing was saved" in b.inner_text("#banner")
    assert [(x["reviewer"], x["decision"]) for x in rows(app)] == [(A, "hold"), (A, "reject")]

    # having seen it, B may overrule: the log keeps both calls
    press(b, "P9002", l2["key"], "accept")
    wait_line(b, l2["key"], "accept", B)
    assert [(x["reviewer"], x["decision"]) for x in rows(app)] == [(A, "hold"), (A, "reject"), (B, "accept")]
    a.evaluate("GasStore.poll()")
    wait_line(a, l2["key"], "accept", B)

    # a reload rebuilds the same picture from the published files plus the store
    a.reload()
    a.wait_for_function("window.ReviewApp && ReviewApp.data && ReviewApp.data.pipelines.length > 0")
    wait_line(a, l1["key"], "hold", A)
    wait_line(a, l2["key"], "accept", B)
    by = a.evaluate("[...document.getElementById('f-by').options].map(o => o.value)")
    assert A in by and B in by                                      # the decided-by filter knows both reviewers
    assert errors == []


def test_a_republish_reloads_the_open_page_in_place(browser, app):
    errors = []
    d = app["dataset"]
    l1 = fill_line(d, "P9002", 0)
    a = open_page(browser, app, A, errors)
    press(a, "P9002", l1["key"], "hold")
    wait_line(a, l1["key"], "hold", A)
    H.publish_fixture(app, app["out"], ver="20990102T000000")        # same cursor: the store rows still overlay
    urllib.request.urlopen(urllib.request.Request(app["base"] + "/expire-cache", data=b"", method="POST")).read()
    a.evaluate("GasStore.state.lastPoll = 0")                        # the next tick polls, sees the new version, reloads
    a.wait_for_function("GasStore.state.scope && GasStore.state.scope.ver === '20990102T000000' && !GasStore.state.reloading")
    wait_line(a, l1["key"], "hold", A)
    assert errors == []
