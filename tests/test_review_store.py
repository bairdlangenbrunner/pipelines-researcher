"""Decisions (milestone 3): store.py, /api/decide, the two sidecars, contested linking, overlay,
and the newest-snapshot default. Fixture staging dirs only, never a real batch."""
import json
import shutil
import threading
import urllib.error
import urllib.request

import pytest

import review_data
import review_fixture
import server
import store

KEYS = ("key", "dir", "pid", "sheet_row", "ref_col", "kind", "decision", "suggested_value",
        "note", "reviewer", "ts", "undecided")


@pytest.fixture
def scope(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    s["dataset"] = data
    s["dirs"] = store.dir_paths(data, tmp_path)
    return s


def line(data, pid, kind, col=None):
    for p in data["pipelines"]:
        if p["pid"] == pid:
            for l in p["lines"]:
                if l["kind"] == kind and (col is None or l["column"] == col):
                    return l
    raise AssertionError((pid, kind))


def item_key(data, kind):
    return next(i["key"] for p in data["pipelines"] for i in p["items"] if i["kind"] == kind)


def sidecars(s, l):
    d = s["dirs"][l["dir"]]
    return d / "review_log.jsonl", d / "review_decisions.json"


def logrecs(path):
    return [json.loads(x) for x in path.read_text().splitlines()]


def dec(s, recs, who="Baird"):
    return store.decide(recs, s["dataset"], who, dirs=s["dirs"])


def test_decide_writes_both_sidecars_with_exact_shape(scope):
    l = line(scope["dataset"], "P9002", "fill")          # no contested column on P9002
    saved = dec(scope, [{"key": l["key"], "decision": "hold", "note": "wait"}])
    log, derived = sidecars(scope, l)
    recs = logrecs(log)
    assert recs == saved and len(recs) == 1
    r = recs[0]
    assert tuple(r) == KEYS
    assert (r["pid"], r["sheet_row"], r["ref_col"], r["kind"]) == ("P9002", l["sheet_row"], l["ref_col"], "fill")
    assert r["decision"] == "hold" and r["note"] == "wait" and r["suggested_value"] == ""
    assert r["reviewer"] == "Baird" and r["undecided"] is False
    assert r["ts"][-6] in "+-" and r["ts"][-3] == ":"                      # ISO-8601 with a timezone offset
    d = json.loads(derived.read_text())
    assert set(d) == {"generated", "decisions"} and d["decisions"] == {l["key"]: r}


def test_latest_wins_and_undo_unreviews(scope):
    l = line(scope["dataset"], "P9002", "fill")
    log, derived = sidecars(scope, l)
    dec(scope, [{"key": l["key"], "decision": "accept"}])
    dec(scope, [{"key": l["key"], "decision": "reject"}])
    assert json.loads(derived.read_text())["decisions"][l["key"]]["decision"] == "reject"
    store.overlay(scope["dataset"], scope["dirs"])
    assert (l["decision"], l["reviewed"], l["decided_by"]) == ("reject", True, "Baird") and l["decided_at"]
    dec(scope, [{"key": l["key"], "undo": True}])
    recs = logrecs(log)
    assert len(recs) == 3 and recs[-1]["undecided"] is True          # appended, nothing deleted
    assert json.loads(derived.read_text())["decisions"][l["key"]]["undecided"] is True
    store.overlay(scope["dataset"], scope["dirs"])
    assert (l["decision"], l["reviewed"], l["decided_by"], l["decided_at"]) == (None, False, None, None)


def test_machine_reviewer_is_not_reviewed(scope):
    assert store.MACHINE_REVIEWERS == {"backend sync", "push"}
    l = line(scope["dataset"], "P9002", "fill")
    dec(scope, [{"key": l["key"], "decision": "accept"}], who="backend sync")
    assert not store.reviewed(store.latest(store.read_log(scope["dirs"][l["dir"]]))[l["key"]])
    store.overlay(scope["dataset"], scope["dirs"])
    assert l["reviewed"] is False and l["decision"] == "accept" and l["decided_by"] == "backend sync"
    dec(scope, [{"key": l["key"], "decision": "accept"}], who="Baird")
    store.overlay(scope["dataset"], scope["dirs"])
    assert l["reviewed"] is True


def test_rollback_restores_log_byte_for_byte(scope, monkeypatch):
    l = line(scope["dataset"], "P9002", "fill")
    log, derived = sidecars(scope, l)
    dec(scope, [{"key": l["key"], "decision": "accept"}])
    before_log, before_derived = log.read_bytes(), derived.read_bytes()

    def boom(path, text):
        raise OSError("disk full")
    monkeypatch.setattr(store, "atomic_write", boom)
    with pytest.raises(OSError):
        dec(scope, [{"key": l["key"], "decision": "hold"}])
    assert log.read_bytes() == before_log and derived.read_bytes() == before_derived
    # first-ever write failing leaves no log behind at all
    l2 = line(scope["dataset"], "P9001", "oo")
    log2, derived2 = sidecars(scope, l2)
    if not log2.exists():
        with pytest.raises(OSError):
            dec(scope, [{"key": l2["key"], "decision": "hold"}])
        assert not log2.exists() and not derived2.exists()


def test_validate_rejects_bad_requests(scope):
    d = scope["dataset"]
    l = line(d, "P9002", "fill")
    bad = [
        ([{"key": "nope::P1|1|x", "decision": "accept"}], "unknown key"),
        ([{"key": l["key"], "decision": "maybe"}], "decision"),
        ([{"key": l["key"]}], "no decision given"),                    # a bare key never defaults to accept
        ([{"key": l["key"], "decision": "suggest"}], "suggested_value or a note"),
        ([{"key": item_key(d, "unresolved"), "decision": "hold"}], "item"),
        ([], "non-empty"),
        (["x"], "not an object"),
    ]
    for recs, msg in bad:
        with pytest.raises(store.Invalid, match=msg):
            dec(scope, recs)
    assert not any((p / "review_log.jsonl").exists() for p in scope["dirs"].values())   # nothing written
    # a suggestion with a value, or with only a note, is accepted
    out = dec(scope, [{"key": l["key"], "decision": "suggest", "suggested_value": "9"}])
    assert out[0]["suggested_value"] == "9"
    out = dec(scope, [{"key": l["key"], "decision": "suggest", "note": "use the 2025 figure"}])
    assert out[0]["decision"] == "suggest"
    # one bad record refuses the whole request
    with pytest.raises(store.Invalid):
        dec(scope, [{"key": l["key"], "decision": "hold"}, {"key": "x", "decision": "hold"}])
    assert len(logrecs(sidecars(scope, l)[0])) == 2


def test_overlay_on_a_rebuilt_dataset(scope):
    l = line(scope["dataset"], "P9002", "fill")
    dec(scope, [{"key": l["key"], "decision": "accept"}])
    rebuilt, _ = review_data.build([scope["qc"], scope["deep"]], "Russia", "gas",
                                   data_dir=scope["data"], root=scope["root"])
    l2 = line(rebuilt, "P9002", "fill")
    assert (l2["decision"], l2["reviewed"]) == ("accept", True)
    assert l2["decided_by"] == "Baird" and l2["decided_at"]
    other = line(rebuilt, "P9001", "ref")
    assert (other["decision"], other["reviewed"], other["decided_by"]) == (None, False, None)
    for p in rebuilt["pipelines"]:
        for i in p["items"]:
            assert i["reviewed"] is False and i["decided_by"] is None


def test_contested_line_refuses_accept_but_allows_hold(scope):
    d = scope["dataset"]
    l = line(d, "P9001", "ref", "Status")         # the P9001 concern contests Status
    with pytest.raises(store.Contested, match="Status"):
        dec(scope, [{"key": l["key"], "decision": "accept"}])
    assert dec(scope, [{"key": l["key"], "decision": "hold"}])[0]["decision"] == "hold"
    assert dec(scope, [{"key": l["key"], "decision": "reject"}])[0]["decision"] == "reject"
    # a concern with a call releases the lock (item calls are milestone 4: simulate the dataset field)
    for i in next(p for p in d["pipelines"] if p["pid"] == "P9001")["items"]:
        if i["kind"] == "concern":
            i["call"] = "disagree"
    assert dec(scope, [{"key": l["key"], "decision": "accept"}])[0]["decision"] == "accept"


@pytest.fixture
def live(scope, tmp_path):
    path = tmp_path / "review_data.json"
    path.write_text(json.dumps(scope["dataset"]), encoding="utf-8")
    app = server.App(path, "tester", batches_root=scope["root"])
    httpd = server.make_server(app, "127.0.0.1", 0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}", scope
    httpd.shutdown()
    httpd.server_close()


def post(url, body):
    req = urllib.request.Request(url, data=body if isinstance(body, bytes) else json.dumps(body).encode(),
                                 method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def get_json(url):
    with urllib.request.urlopen(url) as r:
        return json.loads(r.read())


def test_api_decide_roundtrip_undo_and_server_side_stamps(live):
    base, s = live
    l = line(s["dataset"], "P9002", "fill")
    # the client cannot choose reviewer or ts
    st, body = post(base + "/api/decide", [{"key": l["key"], "decision": "accept",
                                            "reviewer": "someone else", "ts": "1999-01-01"}])
    assert st == 200
    r = body["saved"][0]
    assert r["reviewer"] == "tester" and r["ts"].startswith("20")
    data = get_json(base + "/api/data")                      # reload shows the decision
    got = line(data, "P9002", "fill")
    assert (got["decision"], got["reviewed"], got["decided_by"]) == ("accept", True, "tester")
    assert get_json(base + "/api/decisions?dir=" + l["dir"])["decisions"][l["key"]] == r
    st, body = post(base + "/api/decide", [{"key": l["key"], "undo": True}])
    assert st == 200 and body["saved"][0]["undecided"] is True
    assert line(get_json(base + "/api/data"), "P9002", "fill")["reviewed"] is False


def test_api_decide_refuses_contested_accept_server_side(live):
    base, s = live
    l = line(s["dataset"], "P9001", "ref", "Status")
    st, body = post(base + "/api/decide", [{"key": l["key"], "decision": "accept"}])
    assert st == 409 and "Status" in body["error"]
    assert not (s["dirs"][l["dir"]] / "review_log.jsonl").exists()
    st, _ = post(base + "/api/decide", [{"key": l["key"], "decision": "hold"}])
    assert st == 200


def test_api_decide_bad_requests_are_400_and_write_nothing(live):
    base, s = live
    l = line(s["dataset"], "P9002", "fill")
    for body in ([{"key": "nope", "decision": "accept"}], [{"key": l["key"], "decision": "x"}],
                 [{"key": l["key"], "decision": "suggest"}], {"not": "a list"}, b"not json"):
        st, _ = post(base + "/api/decide", body)
        assert st == 400, body
    assert not any((p / "review_log.jsonl").exists() for p in s["dirs"].values())
    assert get_json(base + "/api/decisions?dir=" + l["dir"]) == {"dir": l["dir"], "decisions": {}}
    with pytest.raises(urllib.error.HTTPError) as e:
        get_json(base + "/api/decisions?dir=batches/elsewhere")
    assert e.value.code == 404


def test_snapshot_default_is_newest_and_recorded_is_kept(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    shutil.copy(s["data"] / review_fixture.SNAP_NAME, s["data"] / "GGIT_gas_snapshot_21000101.csv")
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    assert data["scope"]["snapshot"] == "GGIT_gas_snapshot_21000101.csv"
    assert data["scope"]["recorded_snapshot"] == review_fixture.SNAP_NAME
    # --snapshot still overrides
    old = s["data"] / review_fixture.SNAP_NAME
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", snapshot=old,
                                data_dir=s["data"], root=s["root"])
    assert data["scope"]["snapshot"] == review_fixture.SNAP_NAME
    assert data["scope"]["recorded_snapshot"] == review_fixture.SNAP_NAME
