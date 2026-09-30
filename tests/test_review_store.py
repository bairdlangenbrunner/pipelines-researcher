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
    # a concern with a call releases the lock (see test_dismissing_a_concern_unlocks...)
    for i in next(p for p in d["pipelines"] if p["pid"] == "P9001")["items"]:
        if i["kind"] == "concern":
            i["call"] = "dismissed"
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


# ---- milestone 4: items, bulk, backend sync ----------------------------------------

ITEM_KEYS = ("key", "dir", "pid", "kind", "call", "note", "reviewer", "ts", "undecided")


def items_of(data, kind):
    return [i for p in data["pipelines"] for i in p["items"] if i["kind"] == kind]


def call(s, recs, who="Baird"):
    return store.record_items(recs, s["dataset"], who, dirs=s["dirs"])


def test_item_call_writes_same_sidecars_with_item_shape(scope):
    it = next(i for i in items_of(scope["dataset"], "wikidiff") if i["dir"].endswith("deepsweep-x"))
    log, derived = sidecars(scope, it)
    saved = call(scope, [{"key": it["key"], "call": "todo", "note": "check the wiki"}])
    recs = logrecs(log)
    assert recs == saved and tuple(recs[0]) == ITEM_KEYS
    assert (recs[0]["pid"], recs[0]["kind"], recs[0]["call"], recs[0]["undecided"]) == (next(p["pid"] for p in scope["dataset"]["pipelines"] if it in p["items"]), "wikidiff", "todo", False)
    # a line decision in the same dir lands in the same file, keyed separately
    l = next(l for p in scope["dataset"]["pipelines"] for l in p["lines"]
             if l["dir"] == it["dir"] and not l["in_backend"])
    dec(scope, [{"key": l["key"], "decision": "hold"}])
    assert len(logrecs(log)) == 2
    d = json.loads(derived.read_text())["decisions"]
    assert d[it["key"]]["call"] == "todo" and d[l["key"]]["decision"] == "hold"
    store.overlay(scope["dataset"], scope["dirs"])
    assert (it["call"], it["call_note"], it["reviewed"], it["decided_by"]) == ("todo", "check the wiki", True, "Baird")
    assert it["decided_at"]


def test_item_vocabulary_per_kind_enforced(scope):
    d = scope["dataset"]
    assert store.ITEM_CALLS["concern"] == ("confirmed", "dismissed", "needs_research")
    for k in store.ITEM_KINDS:
        if k != "concern":
            assert store.ITEM_CALLS[k] == ("noted", "todo", "dismissed")
    concern, wiki = items_of(d, "concern")[0], items_of(d, "wikidiff")[0]
    for bad in ({"key": concern["key"], "call": "noted"}, {"key": wiki["key"], "call": "confirmed"},
                {"key": wiki["key"], "call": ""}, {"key": wiki["key"]}):
        with pytest.raises(store.Invalid, match="call"):
            call(scope, [bad])
    with pytest.raises(store.Invalid, match="is a line"):
        call(scope, [{"key": line(d, "P9002", "fill")["key"], "call": "noted"}])
    with pytest.raises(store.Invalid, match="unknown key"):
        call(scope, [{"key": "nope", "call": "noted"}])
    with pytest.raises(store.Invalid):
        call(scope, [])
    assert not any((p / "review_log.jsonl").exists() for p in scope["dirs"].values())
    for c in store.ITEM_CALLS["concern"]:
        assert call(scope, [{"key": concern["key"], "call": c}])[0]["call"] == c


def test_dismissing_a_concern_unlocks_the_contested_line(scope):
    d = scope["dataset"]
    l = line(d, "P9001", "ref", "Status")
    concern = items_of(d, "concern")[0]
    with pytest.raises(store.Contested):
        dec(scope, [{"key": l["key"], "decision": "accept"}])
    call(scope, [{"key": concern["key"], "call": "dismissed"}])
    store.overlay(d, scope["dirs"])                       # what server.App does before validating
    assert concern["call"] == "dismissed" and store.locked_by(next(p for p in d["pipelines"] if p["pid"] == "P9001"), l) == []
    assert dec(scope, [{"key": l["key"], "decision": "accept"}])[0]["decision"] == "accept"
    # undoing the call re-locks (an existing accept stays; a new one is refused)
    call(scope, [{"key": concern["key"], "undo": True}])
    store.overlay(d, scope["dirs"])
    assert concern["call"] is None
    with pytest.raises(store.Contested):
        dec(scope, [{"key": l["key"], "decision": "accept"}])
    call(scope, [{"key": concern["key"], "call": "confirmed"}])      # confirmed also has a call
    store.overlay(d, scope["dirs"])
    assert dec(scope, [{"key": l["key"], "decision": "accept"}])[0]["decision"] == "accept"


def test_item_undo(scope):
    it = items_of(scope["dataset"], "flag")[0]
    log, derived = sidecars(scope, it)
    call(scope, [{"key": it["key"], "call": "noted"}])
    out = call(scope, [{"key": it["key"], "undo": True}])
    assert out[0]["undecided"] is True and out[0]["call"] == "" and len(logrecs(log)) == 2
    assert json.loads(derived.read_text())["decisions"][it["key"]]["undecided"] is True
    store.overlay(scope["dataset"], scope["dirs"])
    assert (it["call"], it["reviewed"], it["decided_by"], it["decided_at"]) == (None, False, None, None)


def test_item_write_failure_rolls_back(scope, monkeypatch):
    it = items_of(scope["dataset"], "flag")[0]
    log, _ = sidecars(scope, it)
    monkeypatch.setattr(store, "atomic_write", lambda p, t: (_ for _ in ()).throw(OSError("full")))
    with pytest.raises(OSError):
        call(scope, [{"key": it["key"], "call": "noted"}])
    assert not log.exists()


def test_bulk_with_a_locked_line_refuses_everything(scope):
    d = scope["dataset"]
    ok = line(d, "P9002", "fill")
    locked = line(d, "P9001", "ref", "Status")
    with pytest.raises(store.Contested):
        dec(scope, [{"key": ok["key"], "decision": "accept"}, {"key": locked["key"], "decision": "accept"}])
    assert not any((p / "review_log.jsonl").exists() for p in scope["dirs"].values())
    out = dec(scope, [{"key": ok["key"], "decision": "accept"}, {"key": line(d, "P9002", "status")["key"], "decision": "accept"}])
    assert [r["decision"] for r in out] == ["accept", "accept"]


def test_sync_backend_stamps_machine_records_only_where_no_person_decided(scope):
    d = scope["dataset"]
    held = line(d, "P9005", "fill")                 # in_backend in the fixture snapshot
    assert held["in_backend"]
    person = line(d, "P9002", "fill")
    person["in_backend"] = True                     # pretend the refresh now holds it too
    dec(scope, [{"key": person["key"], "decision": "reject"}])
    store.overlay(d, scope["dirs"])
    out = store.sync_backend(d, scope["dirs"], "GGIT_gas_snapshot_X.csv")
    assert {r["key"] for r in out} == {l["key"] for p in d["pipelines"] for l in p["lines"]
                                         if l["in_backend"] and l["key"] != person["key"]}
    assert all(r["reviewer"] == "backend sync" and r["decision"] == "accept" and not r["undecided"]
               and r["note"] == "already in backend after refresh GGIT_gas_snapshot_X.csv" for r in out)
    store.overlay(d, scope["dirs"])
    assert (held["decision"], held["reviewed"], held["decided_by"]) == ("accept", False, "backend sync")
    assert (person["decision"], person["decided_by"]) == ("reject", "Baird")      # a person's call is never touched
    assert store.sync_backend(d, scope["dirs"], "x") == []                        # idempotent
    dec(scope, [{"key": held["key"], "decision": "hold"}])                        # a person can still override
    store.overlay(d, scope["dirs"])
    assert (held["decision"], held["reviewed"]) == ("hold", True)


def test_api_item_roundtrip_and_errors(live):
    base, s = live
    it = items_of(s["dataset"], "unresolved")[0]
    st, body = post(base + "/api/item", [{"key": it["key"], "call": "dismissed", "note": "n/a",
                                          "reviewer": "someone else"}])
    assert st == 200 and body["saved"][0]["reviewer"] == "tester" and body["saved"][0]["call"] == "dismissed"
    got = next(i for p in get_json(base + "/api/data")["pipelines"] for i in p["items"] if i["key"] == it["key"])
    assert (got["call"], got["call_note"], got["reviewed"], got["decided_by"]) == ("dismissed", "n/a", True, "tester")
    st, body = post(base + "/api/item", [{"key": it["key"], "undo": True}])
    assert st == 200 and body["saved"][0]["undecided"] is True
    for bad in ([{"key": it["key"], "call": "confirmed"}], [{"key": "nope", "call": "noted"}],
                [{"key": line(s["dataset"], "P9002", "fill")["key"], "call": "noted"}], {"x": 1}, b"not json"):
        assert post(base + "/api/item", bad)[0] == 400, bad


def test_api_dismiss_concern_then_accept_contested_line(live):
    base, s = live
    l = line(s["dataset"], "P9001", "ref", "Status")
    assert post(base + "/api/decide", [{"key": l["key"], "decision": "accept"}])[0] == 409
    concern = items_of(s["dataset"], "concern")[0]
    assert post(base + "/api/item", [{"key": concern["key"], "call": "dismissed"}])[0] == 200
    # no GET /api/data in between: the server overlays before it validates
    assert post(base + "/api/decide", [{"key": l["key"], "decision": "accept"}])[0] == 200


def test_api_bulk_decide_with_a_locked_line_is_409_and_writes_nothing(live):
    base, s = live
    ok = line(s["dataset"], "P9002", "fill")
    locked = line(s["dataset"], "P9001", "ref", "Status")
    st, body = post(base + "/api/decide", [{"key": ok["key"], "decision": "accept"},
                                           {"key": locked["key"], "decision": "accept"}])
    assert st == 409
    assert not any((p / "review_log.jsonl").exists() for p in s["dirs"].values())
    st, body = post(base + "/api/decide", [{"key": ok["key"], "decision": "accept"},
                                           {"key": locked["key"], "decision": "hold"}])
    assert st == 200 and len(body["saved"]) == 2


# ---- /api/refresh with a stubbed pull ----------------------------------------------

NEWER = "GGIT_gas_snapshot_21000101.csv"


def _stub(tmp_path, data_dir, body):
    """A refresh command that 'pulls' a newer snapshot: copies a prepared CSV into the data dir."""
    sh = tmp_path / "fake_refresh.sh"
    sh.write_text(body.replace("{data}", str(data_dir)).replace("{src}", str(tmp_path / "newer.csv")))
    sh.chmod(0o755)
    return [str(sh)]


def _newer_csv(s):
    """The fixture snapshot with P9002's proposed Capacity fill now on the sheet (row 5)."""
    import csv
    src = s["data"] / review_fixture.SNAP_NAME
    rows = list(csv.reader(open(src, encoding="utf-8", newline="")))
    h = rows[2]
    for r in rows[3:]:
        if r[h.index("ProjectID")] == "P9002":
            r[h.index("Capacity")], r[h.index("CapacityUnits")] = "7.5", "bcm/y"
            r[h.index("Capacity [ref]")] = "http://new.example/b"
    out = s["tmp"] / "newer.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def built_app(s, tmp_path, cmd):
    path = tmp_path / "review_data.json"
    argv = ["--country", "Russia", "--commodity", "gas", "--dirs", str(s["qc"]), str(s["deep"]),
            "--batches-root", str(s["root"]), "--data-dir", str(s["data"]), "--out", str(path)]
    review_data.main(argv)
    return server.App(path, "tester", batches_root=s["root"], build_argv=argv, refresh_cmd=cmd)


def serve(app):
    httpd = server.make_server(app, "127.0.0.1", 0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def test_refresh_rebuilds_and_backend_syncs(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    _newer_csv(s)
    app = built_app(s, tmp_path, _stub(tmp_path, s["data"], '#!/bin/sh\ncp "{src}" "{data}/' + NEWER + '"\n'))
    httpd, base = serve(app)
    try:
        assert get_json(base + "/api/whoami")["caps"]["refresh"] is True
        before = get_json(base + "/api/data")
        fill = line(before, "P9002", "fill")
        assert fill["in_backend"] is False and before["scope"]["snapshot"] == review_fixture.SNAP_NAME
        st, body = post(base + "/api/refresh", b"{}")
        assert st == 200, body
        assert body["snapshot"] == NEWER and body["synced"] >= 1 and body["lines"] == sum(len(p["lines"]) for p in before["pipelines"])
        after = get_json(base + "/api/data")
        fill = line(after, "P9002", "fill")
        assert fill["in_backend"] is True
        assert (fill["decision"], fill["decided_by"], fill["reviewed"]) == ("accept", "backend sync", False)
        log = logrecs(store.dir_paths(after, tmp_path)[fill["dir"]] / "review_log.jsonl")
        mine = [r for r in log if r["key"] == fill["key"]]
        assert mine and mine[-1]["reviewer"] == "backend sync" and mine[-1]["note"] == f"already in backend after refresh {NEWER}"
        # a second refresh stamps nothing new
        assert post(base + "/api/refresh", b"{}")[1]["synced"] == 0
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_refresh_failure_and_no_build(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    app = built_app(s, tmp_path, _stub(tmp_path, s["data"], "#!/bin/sh\necho 'auth expired' >&2\nexit 3\n"))
    httpd, base = serve(app)
    try:
        st, body = post(base + "/api/refresh", b"{}")
        assert st == 502 and "auth expired" in body["error"]
        assert not any((p / "review_log.jsonl").exists() for p in (s["deep"], s["qc"]))
    finally:
        httpd.shutdown()
        httpd.server_close()
    nb = server.App(tmp_path / "review_data.json", "tester", batches_root=s["root"])
    assert nb.whoami()["caps"]["refresh"] is False
    with pytest.raises(server.Refusal) as e:
        nb.refresh()
    assert e.value.status == 409


# ---- milestone 5: suggest --------------------------------------------------------------

def test_api_suggest_roundtrip_counts_as_reviewed_and_undoes(live):
    base, s = live
    l = line(s["dataset"], "P9002", "fill")
    st, body = post(base + "/api/decide", [{"key": l["key"], "decision": "suggest",
                                            "suggested_value": "8.25", "note": "2025 annual report"}])
    assert st == 200
    r = body["saved"][0]
    assert (r["decision"], r["suggested_value"], r["note"], r["undecided"]) == ("suggest", "8.25", "2025 annual report", False)
    assert r["reviewer"] and r["ts"] and set(KEYS) <= set(r)
    # on reload the line carries the suggestion and is reviewed (a person's call)
    got = line(get_json(base + "/api/data"), "P9002", "fill")
    assert (got["decision"], got["reviewed"], got["suggested_value"], got["decision_note"]) == \
        ("suggest", True, "8.25", "2025 annual report")
    assert store.reviewed(r)
    # a note-only suggestion is valid; a bare one is a 400
    assert post(base + "/api/decide", [{"key": l["key"], "decision": "suggest", "note": "look again"}])[0] == 200
    assert post(base + "/api/decide", [{"key": l["key"], "decision": "suggest"}])[0] == 400
    # undo takes it back
    assert post(base + "/api/decide", [{"key": l["key"], "undo": True}])[0] == 200
    assert line(get_json(base + "/api/data"), "P9002", "fill")["reviewed"] is False
