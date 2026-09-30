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
