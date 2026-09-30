"""staged_summary: per-dir decided counts (`12a/3h/1r/0s of 40`; an em dash with no decision file)."""
import json

import review_data
import review_fixture
import staged_summary
import store


def _scope(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    return s, data, store.dir_paths(data, tmp_path)


def _lines(data, kind):
    return [l for p in data["pipelines"] for l in p["lines"] if l["kind"] == kind]


def test_no_decision_file_is_a_dash(tmp_path):
    s, _, _ = _scope(tmp_path)
    sm = staged_summary._dir_summary(s["deep"])
    assert sm["decided"] is None and staged_summary._decided_text(None) == "—"
    text = "\n".join(staged_summary._index_lines(s["root"]))
    assert "decided —" in text and "decided=" not in text


def test_counts_by_decision_over_line_records(tmp_path):
    s, data, dirs = _scope(tmp_path)
    ls = [l for l in data["pipelines"][0]["lines"]] + [l for p in data["pipelines"][1:] for l in p["lines"]]
    deep = [l for l in ls if l["dir"].endswith("deepsweep-x")]
    by_kind = {l["kind"]: l for l in deep}
    store.decide([{"key": by_kind["fill"]["key"], "decision": "accept"},
                  {"key": by_kind["status"]["key"], "decision": "hold"},
                  {"key": by_kind["route"]["key"], "decision": "suggest", "suggested_value": "x"},
                  {"key": by_kind["new_row"]["key"], "decision": "reject"}], data, "Baird", dirs=dirs)
    c = staged_summary._dir_summary(s["deep"])["decided"]
    assert (c["accept"], c["hold"], c["reject"], c["suggest"]) == (1, 1, 1, 1)
    assert c["total"] == c["accept"] + c["hold"] + c["reject"] + c["suggest"] + c["undecided"] >= 6
    assert staged_summary._decided_text(c) == f"1a/1h/1r/1s of {c['total']}"
    # the packet dir has no decision file of its own
    assert staged_summary._dir_summary(s["qc"])["decided"] is None
    text = "\n".join(staged_summary._index_lines(s["root"]))
    assert f"decided 1a/1h/1r/1s of {c['total']}" in text and "decided —" in text


def test_undo_and_machine_records_do_not_count(tmp_path):
    s, data, dirs = _scope(tmp_path)
    fill = next(l for l in _lines(data, "fill") if l["dir"].endswith("deepsweep-x"))
    store.decide([{"key": fill["key"], "decision": "accept"}], data, "Baird", dirs=dirs)
    store.decide([{"key": fill["key"], "undo": True}], data, "Baird", dirs=dirs)
    c = staged_summary._dir_summary(s["deep"])["decided"]
    assert c["accept"] == 0 and c["undecided"] == c["total"]
    (s["deep"] / "review_log.jsonl").write_text(json.dumps(
        {"key": fill["key"], "decision": "accept", "reviewer": "backend sync", "undecided": False}) + "\n")
    (s["deep"] / "review_decisions.json").unlink()
    assert staged_summary._dir_summary(s["deep"])["decided"]["accept"] == 0
