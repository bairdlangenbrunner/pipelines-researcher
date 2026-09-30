"""Consumer-side lookup (review_app/decisions.py): a staged record finds its decision by
(pid, colid), with sheet_row only breaking ties."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for p in (ROOT / "review_app", ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from decisions import Decisions, parse_key  # noqa: E402


def _rec(key, decision, undecided=False, reviewer="tester"):
    return {"key": key, "decision": decision, "undecided": undecided, "reviewer": reviewer}


def _write(d, recs):
    (d / "review_decisions.json").write_text(json.dumps({"generated": "x", "decisions": {r["key"]: r for r in recs}}))


def test_parse_key_strips_dedupe_suffix():
    assert parse_key("batches/x/staging/y::P1|357|Capacity [ref]#FILL2") == ("batches/x/staging/y", "P1", "357", "Capacity [ref]")


def test_lookup_by_pid_and_colid_ignores_row_drift(tmp_path):
    _write(tmp_path, [_rec("d::P1|357|Capacity [ref]", "accept")])
    dec = Decisions(tmp_path)
    staged = {"project_id": "P1", "sheet_row": 340, "ref_col": "Capacity [ref]", "class_in": "MISSING_REF",
              "class_out": "REFS_ADDED", "proposed_refs": ["https://x"]}
    assert dec.decision(staged) == "accept" and dec.accepted(staged)
    assert dec.counts([staged]) == {"accept": 1, "hold": 0, "reject": 0, "suggest": 0, "undecided": 0}


def test_ties_broken_by_sheet_row_else_none(tmp_path):
    _write(tmp_path, [_rec("d::P1|357|Capacity [ref]", "accept"), _rec("d::P1|358|Capacity [ref]", "hold")])
    dec = Decisions(tmp_path)
    base = {"project_id": "P1", "ref_col": "Capacity [ref]", "class_in": "MISSING_REF", "class_out": "REFS_ADDED"}
    assert dec.decision(dict(base, sheet_row=358)) == "hold"
    assert dec.decision(dict(base, sheet_row=999)) is None


def test_undone_and_machine_records(tmp_path):
    _write(tmp_path, [_rec("d::P1|1|__STATUS__", "accept", undecided=True),
                      _rec("d::P2|2|__STATUS__", "accept", reviewer="backend sync")])
    dec = Decisions(tmp_path)
    s1 = {"project_id": "P1", "sheet_row": 1, "ref_col": "__STATUS__", "class_in": "STATUS", "class_out": "CHANGE_PROPOSED"}
    s2 = dict(s1, project_id="P2", sheet_row=2)
    assert dec.decision(s1) is None
    assert dec.decision(s2) == "accept" and dec.person_decision(s2) is None


def test_falls_back_to_log_when_derived_missing(tmp_path):
    (tmp_path / "review_log.jsonl").write_text(json.dumps(_rec("d::P1|1|__STATUS__", "hold")) + "\n"
                                               + json.dumps(_rec("d::P1|1|__STATUS__", "reject")) + "\n")
    s1 = {"project_id": "P1", "sheet_row": 1, "ref_col": "__STATUS__", "class_in": "STATUS", "class_out": "CHANGE_PROPOSED"}
    assert Decisions(tmp_path).decision(s1) == "reject"
    assert not Decisions(tmp_path / "nowhere")
