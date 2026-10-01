"""Phase 2: review_app/pull.py mirrors the Google decision store into the staging dirs. The store
is a list of cell texts handed in through `reader`; nothing here calls gws."""
import json

import pytest

import pull
import review_data
import review_fixture
import store


@pytest.fixture
def scope(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    s["dataset"], s["dirs"] = data, store.dir_paths(data, tmp_path)
    return s


def rec(l, n, **kw):
    return dict({"key": l["key"], "dir": l["dir"], "pid": "P9002", "sheet_row": l.get("sheet_row"), "ref_col": "",
                 "kind": l["kind"], "decision": "accept", "suggested_value": "", "note": "",
                 "reviewer": "aiganym@globalenergymonitor.org", "ts": "2099-01-01T01:00:0%d-05:00" % n,
                 "undecided": False, "basis": "abc", "id": "id%d" % n, "scope": "russia-gas", "batch": "b",
                 "snapshot": "s.csv", "origin": "gas"}, **kw)


def a_line(data):
    return next(l for p in data["pipelines"] if p["pid"] == "P9002" for l in p["lines"] if l["kind"] == "fill")


def test_no_store_configured_is_cursor_one_and_reads_nothing():
    def boom(sheet):
        raise AssertionError("read the store with none configured")
    res = pull.pull({"store_sheet_id": ""}, reader=boom)
    assert (res["configured"], res["cursor"], res["new"]) == (False, 1, 0)
    assert "nothing to pull" in pull.report(res)
    assert pull.pull({"store_sheet_id": "x"}, reader=lambda s: [])["cursor"] == 1          # no log tab yet


def test_parse_rows_numbers_rows_and_reports_the_unreadable():
    good = {"id": "1", "key": "k", "dir": "d"}
    cells = ["json", json.dumps(good), "", "not json", json.dumps({"key": "k"}), json.dumps([1]), json.dumps(dict(good, id="2"))]
    recs, cursor, bad = pull.parse_rows(cells)
    assert [(r["id"], r["row"]) for r in recs] == [("1", 2), ("2", 7)] and cursor == 7 and bad == [4, 5, 6]
    assert pull.parse_rows(["json"]) == ([], 1, []) and pull.parse_rows([]) == ([], 1, [])


def test_mirror_appends_once_in_sheet_order_and_regenerates_the_derived_file(scope, tmp_path):
    l = a_line(scope["dataset"])
    cells = ["json", json.dumps(rec(l, 1, decision="hold")), json.dumps(rec(l, 2))]
    res = pull.pull({"store_sheet_id": "x"}, root=tmp_path, reader=lambda s: cells)
    assert (res["cursor"], res["rows"], res["new"], res["by_dir"]) == (3, 2, 2, {l["dir"]: 2})
    d = scope["dirs"][l["dir"]]
    log = store.read_log(d)
    assert [r["id"] for r in log] == ["id1", "id2"] and all("row" not in r for r in log)
    assert log[1] == rec(l, 2, reviewer="A")    # as the sheet holds it, but for the initials
    assert "aiganym" not in (d / "review_log.jsonl").read_text() + (d / "review_decisions.json").read_text()
    assert res["emails"] == {"id1": "aiganym@globalenergymonitor.org", "id2": "aiganym@globalenergymonitor.org"}
    assert res["shared"] == {} and "SHARED" not in pull.report(res)
    derived = json.loads((d / "review_decisions.json").read_text())["decisions"]
    assert derived[l["key"]]["decision"] == "accept" and derived[l["key"]]["reviewer"] == "A"
    cells.append(json.dumps(rec(l, 3, undecided=True)))
    res = pull.pull({"store_sheet_id": "x"}, root=tmp_path, reader=lambda s: cells)
    assert (res["cursor"], res["new"]) == (4, 1) and len(store.read_log(d)) == 3
    assert pull.pull({"store_sheet_id": "x"}, root=tmp_path, reader=lambda s: cells)["new"] == 0
    store.overlay(scope["dataset"], scope["dirs"])
    assert l["decision"] is None and l["reviewed"] is False             # the undo is the latest word


def test_dry_run_writes_nothing(scope, tmp_path):
    l = a_line(scope["dataset"])
    res = pull.pull({"store_sheet_id": "x"}, root=tmp_path, dry_run=True, reader=lambda s: ["json", json.dumps(rec(l, 1))])
    assert res["new"] == 1 and not (scope["dirs"][l["dir"]] / "review_log.jsonl").exists()
    assert "would append 1" in pull.report(res, dry_run=True)


def test_a_record_is_only_ever_written_under_batches(scope, tmp_path):
    l = a_line(scope["dataset"])
    (tmp_path / "elsewhere").mkdir()
    bad = ["elsewhere", "../" + tmp_path.name + "/elsewhere", "batches/russia-gas/staging/no-such-dir",
           "batches/../elsewhere", "/etc", "batches"]
    cells = ["json"] + [json.dumps(rec(l, i, dir=d)) for i, d in enumerate(bad)] + [json.dumps(rec(l, 9))]
    res = pull.pull({"store_sheet_id": "x"}, root=tmp_path, reader=lambda s: cells)
    assert res["new"] == 1 and set(res["skipped"]) == set(bad) and res["by_dir"] == {l["dir"]: 1}
    assert not list((tmp_path / "elsewhere").iterdir()) and "SKIPPED" in pull.report(res)


def test_initials_are_first_and_last_and_leave_machines_alone():
    assert store.initials("baird.langenbrunner@globalenergymonitor.org") == "BL"
    assert store.initials("Baird Langenbrunner") == "BL" and store.initials("Mary Ann de la Cruz") == "MC"
    assert store.initials("Aiganym@GlobalEnergyMonitor.org") == "A"              # a one-part address: its first letter
    assert store.initials("x_y-z+tag@a.org") == "XT" and store.initials("BL") == "BL"   # applying it twice is a no-op
    for name in ("backend sync", "push", "", None):
        assert store.initials(name) == name


def test_two_reviewers_behind_one_set_of_initials_are_reported_and_machines_are_left_alone(scope, tmp_path):
    l = a_line(scope["dataset"])
    cells = ["json", json.dumps(rec(l, 1)), json.dumps(rec(l, 2, reviewer="alex@globalenergymonitor.org")),
             json.dumps(rec(l, 3, reviewer="backend sync"))]
    res = pull.pull({"store_sheet_id": "x"}, root=tmp_path, reader=lambda s: cells)
    assert res["shared"] == {"A": ["aiganym@globalenergymonitor.org", "alex@globalenergymonitor.org"]}
    assert "SHARED INITIALS A stand for 2 reviewers" in pull.report(res)
    assert [r["reviewer"] for r in store.read_log(scope["dirs"][l["dir"]])] == ["A"] * 2 + ["backend sync"]
    assert set(res["emails"]) == {"id1", "id2"}
