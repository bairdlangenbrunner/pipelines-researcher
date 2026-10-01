"""The decision ledger (review_app/ledger.py): every decision lands in the Google store FIRST, in the
exact row shape Code.gs writes, then in the staging-dir sidecars. A fake gws stands in for the sheet."""
import json
import re
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

import ledger
import publish
import pull
import review_data
import review_fixture
import server
import store

ME = "baird.langenbrunner@globalenergymonitor.org"
SHEET = "store-sheet"


class FakeStore:
    """The store spreadsheet's `log` tab as gws would serve it: rows (header first) + every call."""

    def __init__(self, fail=None, clobber=0, email=ME):
        self.rows = [list(ledger.COLS)]
        self.calls = []
        self.fail = fail            # an exception class to raise on `append`
        self.clobber = clobber      # how many appends another writer "overwrites" (race simulation)
        self.email = email

    def __call__(self, profile, *args, parse=True):
        self.calls.append((profile, args))
        if args[:2] == ("drive", "about"):
            return {"user": {"emailAddress": self.email}}
        verb = args[3]
        params = json.loads(args[args.index("--params") + 1])
        if verb == "append":
            assert profile == pull.WRITE_PROFILE
            assert params["valueInputOption"] == "RAW" and params["range"].startswith("log!A:")
            if self.fail:
                raise self.fail("boom")
            values = json.loads(args[args.index("--json") + 1])["values"]
            first = len(self.rows) + 1
            for v in values:
                assert len(v) == len(ledger.COLS) and all(isinstance(x, str) for x in v)
                self.rows.append(list(v))
            if self.clobber:
                self.clobber -= 1
                for r in self.rows[first - 1:]:
                    r[ledger.COLS.index("id")] = "someone-else"
            return {"updates": {"updatedRange": f"log!A{first}:S{first + len(values) - 1}"}}
        if verb == "get":
            assert profile == pull.READ_PROFILE
            m = re.match(r"log!([A-Z]+)(\d+):([A-Z]+)(\d+)$", params["range"])
            if m:
                col = ledger.COLS.index(ledger.pull._col_letter(0)) if False else None
                c = ord(m.group(1)) - 65 if len(m.group(1)) == 1 else None
                return {"values": [[r[c]] for r in self.rows[int(m.group(2)) - 1:int(m.group(4))]]}
            if params["range"] == "log!1:1":
                return {"values": [self.rows[0]]}
            m = re.match(r"log!([A-Z]+)1:([A-Z]+)$", params["range"])
            c = ord(m.group(1)) - 65
            return {"values": [[r[c]] for r in self.rows]}
        raise AssertionError(args)

    def records(self):
        j = ledger.COLS.index("json")
        return [json.loads(r[j]) for r in self.rows[1:]]

    def json_cells(self):
        j = ledger.COLS.index("json")
        return [r[j] for r in self.rows]


@pytest.fixture
def scope(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    s["dataset"] = data
    s["dirs"] = store.dir_paths(data, tmp_path)
    return s


def line(data, pid, kind):
    for p in data["pipelines"]:
        if p["pid"] == pid:
            for l in p["lines"]:
                if l["kind"] == kind:
                    return l
    raise AssertionError((pid, kind))


def logrecs(d):
    return [json.loads(x) for x in (Path(d) / store.LOG_NAME).read_text().splitlines()]


def made(fake, data, origin="local"):
    return ledger.Ledger(SHEET, *ledger.scope_of(data), origin, reviewer_email=ME, gws=fake)


# ---- the row shape is Code.gs's -----------------------------------------------------------

def test_cols_are_code_gs_cols_verbatim():
    gs = (Path(ledger.HERE) / "gas" / "Code.gs").read_text(encoding="utf-8")
    m = re.search(r"var COLS = \[(.*?)\];", gs, re.S)
    assert m
    assert re.findall(r"'([a-z_]+)'", m.group(1)) == ledger.COLS


def test_row_for_mirrors_append_and_cell():
    rec = {"key": "batches/x::P1|5|c", "dir": "batches/x", "pid": "P1", "sheet_row": 5, "ref_col": "Status [ref]",
           "kind": "ref", "decision": "accept", "suggested_value": "", "note": "=SUM(1)", "reviewer": ME,
           "ts": "t", "undecided": True, "via": "-v", "batch": "b", "snapshot": "s.csv", "id": "i", "scope": "sc"}
    row = ledger.row_for(rec)
    assert len(row) == len(ledger.COLS)
    got = dict(zip(ledger.COLS, row))
    assert got["rec"] == "line" and got["undecided"] == "undone" and got["note"] == "'=SUM(1)" and got["via"] == "'-v"
    assert got["sheet_row"] == "5" and got["call"] == "" and json.loads(got["json"]) == rec
    item = ledger.row_for({"key": "k", "call": "noted", "kind": "flag", "sheet_row": None, "note": "x" * 2500})
    g = dict(zip(ledger.COLS, item))
    assert g["rec"] == "item" and g["sheet_row"] == "" and g["decision"] == "" and len(g["note"]) == 2001
    with pytest.raises(ledger.StoreError):
        ledger.row_for({"key": "k", "note": "x" * 50000})


def test_stamp_fields_fills_what_is_missing_and_keeps_an_id():
    recs = [{"key": "a", "ts": None}, {"key": "b", "id": "old~rekey", "snapshot": "older.csv", "ts": "2001"}]
    ledger.stamp_fields(recs, "russia-gas", "snap.csv", "chat")
    a, b = recs
    assert len(a["id"]) == 36 and b["id"] == "old~rekey" and a["batch"] == b["batch"]
    assert (a["scope"], a["snapshot"], a["origin"]) == ("russia-gas", "snap.csv", "chat")
    assert b["snapshot"] == "older.csv" and b["ts"] == "2001" and a["ts"]
    with pytest.raises(ValueError):
        ledger.stamp_fields([{"key": "c"}], "s", "", "typo")


def test_scope_of_matches_publish():
    assert ledger.scope_of({"scope": {"countries": ["Russia", "United States"], "commodity": "gas"}}) == ("russia-united-states-gas", "")
    assert ledger.scope_of({"scope": {"countries": ["Russia"], "commodity": "gas", "batch": True, "snapshot": "x.csv"}}) == ("review-app-gas", "x.csv")
    assert publish.scope_id(["Russia"], "gas") == ledger.scope_id(["Russia"], "gas")


# ---- append: write, verify, retry -----------------------------------------------------------

def test_append_writes_rows_and_verifies_ids():
    fake = FakeStore()
    recs = [{"key": "k1", "id": "id1", "ts": "t"}, {"key": "k2", "id": "id2", "ts": "t"}]
    assert ledger.append(recs, SHEET, gws=fake) == (2, 3)
    assert [r["row"] for r in recs] == [2, 3] and [r["key"] for r in fake.records()] == ["k1", "k2"]
    assert [a[3] for _, a in fake.calls] == ["append", "get"]


def test_append_retries_once_when_another_writer_lands_on_the_rows_then_refuses():
    fake = FakeStore(clobber=1)
    assert ledger.append([{"key": "k", "id": "i", "ts": "t"}], SHEET, gws=fake) == (3, 3)      # 2nd attempt, next row
    assert [a[3] for _, a in fake.calls] == ["append", "get", "append", "get"]
    with pytest.raises(ledger.StoreError, match="another writer"):
        ledger.append([{"key": "k", "id": "j", "ts": "t"}], SHEET, gws=FakeStore(clobber=5))


def test_append_turns_a_gws_failure_into_a_store_error():
    with pytest.raises(ledger.StoreError, match="could not be written"):
        ledger.append([{"key": "k", "id": "i"}], SHEET, gws=FakeStore(fail=pull.GwsError))


# ---- the sink: store first, sidecars second ----------------------------------------------------

def test_decide_through_the_ledger_lands_in_store_then_sidecar(scope):
    fake = FakeStore()
    led = made(fake, scope["dataset"])
    l = line(scope["dataset"], "P9002", "fill")
    saved = store.decide([{"key": l["key"], "decision": "accept", "note": "ok"}], scope["dataset"], "Baird Langenbrunner",
                         dirs=scope["dirs"], sink=led.sink)
    assert len(saved) == 1 and saved[0]["row"] == 2 and led.written == 1 and led.last_row == 2
    srec = fake.records()[0]
    assert srec["reviewer"] == ME and srec["key"] == l["key"] and srec["origin"] == "local"
    assert srec["scope"] == "russia-gas" and srec["snapshot"] == review_fixture.SNAP_NAME and srec["basis"] == l["basis"]
    local = logrecs(scope["dirs"][l["dir"]])
    assert len(local) == 1 and local[0]["reviewer"] == "BL" and local[0]["id"] == srec["id"] and "row" not in local[0]
    assert {k: v for k, v in local[0].items() if k != "reviewer"} == {k: v for k, v in srec.items() if k not in ("reviewer", "row")}
    assert dict(zip(ledger.COLS, fake.rows[1]))["reviewer"] == ME
    # the overlay reads the record a pull would have written
    store.overlay(scope["dataset"], scope["dirs"])
    assert line(scope["dataset"], "P9002", "fill")["decided_by"] == "BL"


def test_a_pull_of_the_same_store_rows_writes_nothing_twice(scope, tmp_path):
    fake = FakeStore()
    led = made(fake, scope["dataset"])
    l = line(scope["dataset"], "P9002", "fill")
    store.decide([{"key": l["key"], "decision": "reject"}], scope["dataset"], "BL", dirs=scope["dirs"], sink=led.sink)
    res = pull.pull({"store_sheet_id": SHEET}, root=tmp_path, reader=lambda s: fake.json_cells())
    assert res["rows"] == 1 and res["new"] == 0 and len(logrecs(scope["dirs"][l["dir"]])) == 1


def test_store_failure_refuses_the_decision_and_writes_no_sidecar(scope):
    led = made(FakeStore(fail=pull.GwsError), scope["dataset"])
    l = line(scope["dataset"], "P9002", "fill")
    with pytest.raises(ledger.StoreError):
        store.decide([{"key": l["key"], "decision": "accept"}], scope["dataset"], "BL", dirs=scope["dirs"], sink=led.sink)
    assert not (scope["dirs"][l["dir"]] / store.LOG_NAME).exists()
    assert not store._LOCK.locked()


def test_an_unknown_dir_is_refused_before_the_store_is_touched(scope):
    fake = FakeStore()
    led = made(fake, scope["dataset"])
    with pytest.raises(store.Invalid):
        led.sink([{"key": "x::y", "dir": "batches/nowhere", "reviewer": "BL"}], scope["dirs"])
    assert fake.calls == []


def test_item_calls_and_machine_records_go_through_too(scope):
    fake = FakeStore()
    led = made(fake, scope["dataset"])
    key = next(i["key"] for p in scope["dataset"]["pipelines"] for i in p["items"] if i["kind"] == "concern")
    store.record_items([{"key": key, "call": "dismissed", "note": "n"}], scope["dataset"], "BL", dirs=scope["dirs"], sink=led.sink)
    led.origin = "sync"
    synced = store.sync_backend(scope["dataset"], scope["dirs"], review_fixture.SNAP_NAME, sink=led.sink)
    recs = fake.records()
    assert recs[0]["call"] == "dismissed" and recs[0]["reviewer"] == ME and dict(zip(ledger.COLS, fake.rows[1]))["rec"] == "item"
    assert synced and all(r["reviewer"] == store.SYNC_REVIEWER and r["origin"] == "sync" for r in recs[1:])


def test_to_store_restores_the_original_decider_for_a_copy():
    led = ledger.Ledger(SHEET, "s", "", "publish", reviewer_email=ME, gws=FakeStore(),
                        emails={"id-1": "other.person@globalenergymonitor.org"})
    assert led.to_store({"id": "id-1~rekey", "reviewer": "OP"})["reviewer"] == "other.person@globalenergymonitor.org"
    assert led.to_store({"id": "fresh", "reviewer": "BL"})["reviewer"] == ME
    assert led.to_store({"id": "fresh", "reviewer": "push"})["reviewer"] == "push"


def test_whoami_reads_the_store_account():
    assert ledger.whoami(gws=FakeStore()) == ME
    assert ledger.whoami(gws=FakeStore(fail=pull.GwsError, email="")) == ""      # about is not append: still ME? no -> ''
    def down(profile, *a, parse=True):
        raise pull.GwsError("auth")
    assert ledger.whoami(gws=down) == ""


# ---- the server with a ledger -------------------------------------------------------------------

def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def served(scope, tmp_path, fake):
    path = tmp_path / "review_data.json"
    path.write_text(json.dumps(scope["dataset"]), encoding="utf-8")
    led = made(fake, scope["dataset"])
    app = server.App(path, "Baird Langenbrunner", batches_root=scope["root"], ledger=led)
    httpd = server.make_server(app, "127.0.0.1", 0)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}", app


def test_server_decide_writes_the_store_and_reports_it(scope, tmp_path):
    fake = FakeStore()
    httpd, base, app = served(scope, tmp_path, fake)
    try:
        with urllib.request.urlopen(base + "/api/whoami") as r:
            assert json.loads(r.read())["store"] is True
        l = line(scope["dataset"], "P9002", "fill")
        st, body = post(base + "/api/decide", [{"key": l["key"], "decision": "accept"}])
        assert st == 200 and body["saved"][0]["row"] == 2 and fake.records()[0]["reviewer"] == ME
        assert logrecs(scope["dirs"][l["dir"]])[0]["reviewer"] == "BL"
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_server_refuses_with_502_when_the_store_is_down(scope, tmp_path):
    httpd, base, app = served(scope, tmp_path, FakeStore(fail=pull.GwsError))
    try:
        l = line(scope["dataset"], "P9002", "fill")
        st, body = post(base + "/api/decide", [{"key": l["key"], "decision": "accept"}])
        assert st == 502 and "nothing saved" in body["error"]
        assert not (scope["dirs"][l["dir"]] / store.LOG_NAME).exists()
        st, body = post(base + "/api/decide", [{"key": l["key"], "decision": "accept"}])      # the lock was released
        assert st == 502
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_server_without_a_ledger_says_so(scope, tmp_path):
    path = tmp_path / "review_data.json"
    path.write_text(json.dumps(scope["dataset"]), encoding="utf-8")
    assert server.App(path, "TR", batches_root=scope["root"]).whoami()["store"] is False


# ---- publish writes its carry-forwards and syncs to the store ---------------------------------

def test_publish_carries_forward_through_the_ledger_and_advances_the_cursor(scope, tmp_path):
    d, dirs = scope["dataset"], scope["dirs"]
    l = line(d, "P9002", "fill")
    old = l["key"].replace(f"|{l['sheet_row']}|", "|4|")
    rec = {"key": old, "dir": l["dir"], "pid": "P9002", "sheet_row": 4, "ref_col": l.get("ref_col") or "", "kind": l["kind"],
           "decision": "accept", "suggested_value": "", "note": "", "reviewer": "OP", "ts": "2099-01-01T01:00:00-05:00",
           "undecided": False, "basis": l["basis"], "id": "s1", "scope": "russia-gas", "batch": "b1",
           "snapshot": review_fixture.SNAP_NAME, "origin": "gas"}
    store.append_records([rec], dirs)
    fake = FakeStore()
    led = ledger.Ledger(SHEET, "", "", "publish", reviewer_email=ME, gws=fake, emails={"s1": "other.person@globalenergymonitor.org"})
    entry, rep = publish.publish(["Russia"], "gas", tmp_path / "out", dirs=[scope["qc"], scope["deep"]],
                                 batches_root=scope["root"], data_dir=scope["data"], cursor=1, led=led)
    assert [r["rekeyed_from"] for r in rep["carried"]] == [old]
    srec = fake.records()
    assert len(srec) == 1 and srec[0]["id"] == "s1~rekey" and srec[0]["origin"] == "publish"
    assert srec[0]["reviewer"] == "other.person@globalenergymonitor.org" and srec[0]["key"] == l["key"]
    assert entry["store_cursor"] == 2 == led.last_row
