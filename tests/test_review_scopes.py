"""review_app/scopes.py: the review-app batch manifest."""
import json

import scopes
from review_fixture import make_scope


def test_check_set_and_included(tmp_path):
    s = make_scope(tmp_path)
    m = tmp_path / "manifest.json"
    run = lambda *a: scopes.main([*a, "--manifest", str(m), "--batches-root", str(s["root"])])
    assert run("check", "--country", "Russia", "--commodity", "gas") == scopes.ASK      # never asked
    assert run("set", "later", "--country", "Russia", "--commodity", "gas") == 0
    assert run("check", "--country", "russia", "--commodity", "gas") == scopes.ASK     # later asks again
    assert scopes.included("gas", m) == []
    assert run("set", "--country", "Russia", "--commodity", "gas", "y") == 0
    assert run("check", "--country", "Russia", "--commodity", "gas") == 0
    assert scopes.included("gas", m) == ["Russia"] and scopes.included("oil", m) == []
    run("set", "no", "--country", "Russia", "--commodity", "gas")
    assert run("check", "--country", "Russia", "--commodity", "gas") == 0                # declined: not asked
    assert [x["state"] for x in json.loads(m.read_text())["scopes"]] == ["declined"]    # one entry per scope


def test_cannot_include_an_unresearched_scope(tmp_path):
    s = make_scope(tmp_path)
    import pytest
    with pytest.raises(SystemExit):
        scopes.set_state("Narnia", "gas", "yes", tmp_path / "m.json", s["root"])


def test_tracker_wide_scope_is_researched_for_both_commodities(tmp_path):
    s = make_scope(tmp_path)
    m = tmp_path / "manifest.json"
    run = lambda *a: scopes.main([*a, "--manifest", str(m), "--batches-root", str(s["root"])])
    rs = scopes.researched(s["root"], "gas")
    assert rs[("*", "both")]["dirs"] == [s["style"]] and ("*", "both") in scopes.researched(s["root"], "oil")
    assert run("check", "--country", "*", "--commodity", "both") == scopes.ASK
    assert run("set", "yes", "--country", "*", "--commodity", "both") == 0
    assert run("check", "--country", "*", "--commodity", "both") == 0
    assert scopes.included("gas", m) == ["*"] and scopes.included("oil", m) == ["*"]   # joins every batch
    run("set", "yes", "--country", "Russia", "--commodity", "gas")
    assert scopes.included("gas", m) == ["*", "Russia"] and scopes.included("oil", m) == ["*"]
    assert run("list") == 0
