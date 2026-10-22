"""apply_route_candidates --decisions: only the PID-list sourcing (never the sheet / plan / apply path)."""
import argparse

import pytest

import apply_route_candidates as arc
import review_data
import review_fixture
import store


@pytest.fixture
def scope(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    s["dataset"], s["dirs"] = data, store.dir_paths(data, tmp_path)
    s["route"] = next(l for p in data["pipelines"] for l in p["lines"] if l["kind"] == "route")
    return s


def args(s, **kw):
    return argparse.Namespace(**{"staging": str(s["deep"]), "pids": None, "decisions": True, "replace": False, **kw})


def test_accepted_route_lines_source_the_pids(scope):
    store.decide([{"key": scope["route"]["key"], "decision": "accept"}], scope["dataset"], "Baird", dirs=scope["dirs"])
    assert arc.pids_from_decisions(scope["deep"]) == ["P9004"]
    a = args(scope)
    arc.resolve_pid_source(a)
    assert a.pids == "P9004"


@pytest.mark.parametrize("decision", ["hold", "reject", "suggest"])
def test_only_accept_counts(scope, decision):
    store.decide([{"key": scope["route"]["key"], "decision": decision, "note": "n"}], scope["dataset"], "Baird", dirs=scope["dirs"])
    with pytest.raises(SystemExit) as e:
        arc.pids_from_decisions(scope["deep"])
    assert e.value.code not in (0, None) and "no accepted route lines" in str(e.value.code)


def test_no_decisions_and_undone_accept_are_refused(scope):
    with pytest.raises(SystemExit):
        arc.pids_from_decisions(scope["deep"])
    store.decide([{"key": scope["route"]["key"], "decision": "accept"}], scope["dataset"], "Baird", dirs=scope["dirs"])
    store.decide([{"key": scope["route"]["key"], "undo": True}], scope["dataset"], "Baird", dirs=scope["dirs"])
    with pytest.raises(SystemExit):
        arc.pids_from_decisions(scope["deep"])


def test_pids_and_decisions_together_are_refused(scope):
    store.decide([{"key": scope["route"]["key"], "decision": "accept"}], scope["dataset"], "Baird", dirs=scope["dirs"])
    with pytest.raises(SystemExit) as e:
        arc.resolve_pid_source(args(scope, pids="P9004"))
    assert "not both" in str(e.value.code)


def test_pids_alone_is_untouched(scope):
    a = args(scope, decisions=False, pids="P1,P2")
    arc.resolve_pid_source(a)
    assert a.pids == "P1,P2"


def test_an_accepted_line_already_added_is_left_out(scope, capsys):
    import json
    store.decide([{"key": scope["route"]["key"], "decision": "accept"}], scope["dataset"], "Baird", dirs=scope["dirs"])
    f = scope["deep"] / "staged_resolutions.json"
    d = json.loads(f.read_text())
    for r in d["resolutions"]:
        if r.get("class_out") == "ROUTE_CANDIDATE":
            r["applied"] = {"date": "2026-10-22", "by": "apply_route_candidates"}
    f.write_text(json.dumps(d))
    with pytest.raises(SystemExit):
        arc.pids_from_decisions(scope["deep"])
    assert "already added, left out: P9004" in capsys.readouterr().out


def test_apply_marks_the_record_and_writes_a_machine_record_under_the_page_key(scope, monkeypatch):
    import json
    import pull
    f = scope["deep"] / "staged_resolutions.json"
    f.write_text(json.dumps(json.loads(f.read_text()), indent=2) + "\n")
    monkeypatch.setattr(arc, "routes_commit", lambda pid, commodity: "abc1234")
    plan = [{"pid": "P9004", "sheet_row": 7, "before": {}, "after": {}, "backup": "sheet-write-x.csv"}]
    arc.mark_applied(scope["deep"], plan, "gas", False)
    text = f.read_text()
    assert text.endswith("}\n") and '\n  "resolutions"' in text          # indent and trailing newline kept
    marked = [r for r in json.loads(text)["resolutions"] if r.get("applied")]
    assert [(r["project_id"], r["class_out"]) for r in marked] == [("P9004", "ROUTE_CANDIDATE")]
    assert marked[0]["applied"] == {"date": marked[0]["applied"]["date"], "by": "apply_route_candidates",
                                    "sheet_row": 7, "commit": "abc1234", "backup": "sheet-write-x.csv"}

    monkeypatch.setattr(pull, "config", lambda: {})                       # no store: the staging dir's log only
    arc.record_ledger(scope["deep"], plan, "gas", "snap.csv", root=scope["root"].parent)
    data, _ = review_data.build([scope["qc"], scope["deep"]], "Russia", "gas", data_dir=scope["data"], root=scope["root"])
    line = next(l for p in data["pipelines"] for l in p["lines"] if l["kind"] == "route")
    assert line["key"] == scope["route"]["key"]
    log = [json.loads(x) for x in (scope["deep"] / store.LOG_NAME).read_text().splitlines() if x.strip()]
    assert [(r["key"], r["reviewer"], r["decision"]) for r in log] == [(line["key"], "apply_route_candidates", "accept")]
