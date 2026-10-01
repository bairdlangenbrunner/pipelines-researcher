"""scripts/update_seed.py: suggest lines + concerns called confirmed / needs_research -> a §5 seed.
Fixture scope under tmp only; decisions are written through the real store so the sidecars are real."""
import json

import pytest

import review_data
import review_fixture
import store
import update_seed


@pytest.fixture
def scope(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    s["dataset"], s["dirs"] = data, store.dir_paths(data, tmp_path)
    return s


def _line(data, pid, kind):
    return next(l for p in data["pipelines"] if p["pid"] == pid for l in p["lines"] if l["kind"] == kind)


def _item(data, kind):
    return next(i for p in data["pipelines"] for i in p["items"] if i["kind"] == kind)


def run(s, *extra):
    out = s["tmp"] / "seed" / "staged_updates_seed.json"
    seed = update_seed.main(["--country", "Russia", "--commodity", "gas", "--batches-root", str(s["root"]),
                             "--out", str(out), *extra])
    assert json.loads(out.read_text()) == seed
    return seed


def test_suggest_and_concern_become_units(scope, capsys):
    d = scope["dataset"]
    fill, status, concern = _line(d, "P9002", "fill"), _line(d, "P9002", "status"), _item(d, "concern")
    store.decide([{"key": fill["key"], "decision": "suggest", "suggested_value": "8.0", "note": "use the 2025 figure"},
                  {"key": status["key"], "decision": "accept"}], d, "BL", dirs=scope["dirs"])
    store.record_items([{"key": concern["key"], "call": "needs_research", "note": "check the twin"}],
                       d, "BL", dirs=scope["dirs"])
    seed = run(scope)
    by = {u["unit_type"]: u for u in seed["units"]}
    assert len(seed["units"]) == 2                        # the accepted status line is not a unit
    u = by["update"]
    assert (u["project_id"], u["sheet_row"], u["column"], u["ref_col"]) == ("P9002", 5, "Capacity", "Capacity [ref]")
    assert (u["proposed_value"], u["suggested_value"], u["note"], u["reviewer"]) == ("7.5", "8.0", "use the 2025 figure", "BL")
    assert u["source_dir"].endswith("deepsweep-x")
    r = by["research"]
    assert (r["project_id"], r["concern_type"], r["contested_columns"], r["call"], r["note"]) == \
        ("P9001", "duplicate", ["Status"], "needs_research", "check the twin")
    # update-store shape: rows keyed by PID
    ch = seed["rows"]["P9002"]["changes"]["Capacity"]
    assert ch["new"] == "8.0" and ch["action"] == "suggest" and ch["evidence"] == "use the 2025 figure" and ch["old"] == ""
    assert seed["rows"]["P9001"]["research"][0]["call"] == "needs_research"
    assert seed["meta"]["mode"] == "update-seed" and len(seed["meta"]["source_dirs"]) == 2
    out = capsys.readouterr().out
    assert "1 update unit(s)" in out and "1 research unit(s)" in out


def test_dismissed_concern_undone_suggest_and_machine_record_are_not_units(scope):
    d = scope["dataset"]
    fill, concern = _line(d, "P9002", "fill"), _item(d, "concern")
    store.decide([{"key": fill["key"], "decision": "suggest", "suggested_value": "8"}], d, "BL", dirs=scope["dirs"])
    store.decide([{"key": fill["key"], "undo": True}], d, "BL", dirs=scope["dirs"])
    store.record_items([{"key": concern["key"], "call": "dismissed"}], d, "BL", dirs=scope["dirs"])
    assert run(scope)["units"] == []


def test_confirmed_concern_is_a_research_unit(scope):
    d = scope["dataset"]
    store.record_items([{"key": _item(d, "concern")["key"], "call": "confirmed"}], d, "BL", dirs=scope["dirs"])
    units = run(scope)["units"]
    assert [(u["unit_type"], u["call"]) for u in units] == [("research", "confirmed")]


def test_no_decision_files_is_an_empty_seed_and_exit_zero(scope, capsys):
    seed = run(scope)
    assert seed["units"] == [] and seed["rows"] == {}
    assert "0 update unit(s)" in capsys.readouterr().out
    assert not list(scope["root"].rglob("review_log.jsonl"))          # read-only: nothing written into staging


def test_a_concern_whose_candidate_was_taken_is_answered_not_researched(scope, capsys):
    d = scope["dataset"]
    owner, concern = _line(d, "P9001", "oo"), _item(d, "concern")
    concern["contested"] = {"Status": "operating", "Owner1": "OldCo"}
    review_fixture.relink(d)
    store.decide([{"key": owner["key"], "rival": concern["key"]}], d, "BL", dirs=scope["dirs"])
    seed = run(scope)
    assert [u["unit_type"] for u in seed["units"]] == ["update"]            # confirmed, but answered by the suggest
    u = seed["units"][0]
    assert (u["column"], u["suggested_value"], u["rival_concern"]) == ("Owner1", "OldCo", concern["key"])
    assert u["rival_text"]
    ch = seed["rows"]["P9001"]["changes"]["Owner1"]
    assert ch["new"] == "OldCo" and ch["rival_concern"] == concern["key"] and ch["rival_text"] == u["rival_text"]
    assert seed["rows"]["P9001"].get("research", []) == []
    assert "1 answered by a suggest" in capsys.readouterr().out
    # undo the suggest: the confirmed concern is research again
    store.decide([{"key": owner["key"], "undo": True}], d, "BL", dirs=scope["dirs"])
    assert [u["unit_type"] for u in run(scope)["units"]] == ["research"]
