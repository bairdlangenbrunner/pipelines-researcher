import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "review_app"))

import clean_accepts  # noqa: E402


def pipe(contested):
    return {"pid": "P1", "items": [{"kind": "concern", "concern_type": "attribution", "call": None, "contested": contested}], "lines": []}


def test_attribution_naming_pipeline_name_blocks_owner_operator_lines():
    blk = clean_accepts.blockers([pipe({"PipelineName": "X", "Owner": "Y"})])
    line = {"kind": "oo", "column": "Operator [ref]", "ref_col": "Operator [ref]", "tier": "high"}
    assert clean_accepts.skip_reason({"pid": "P1"}, line, blk).startswith("owner/operator")


def test_attribution_naming_only_owner1_leaves_operator_line_alone():
    blk = clean_accepts.blockers([pipe({"Owner1": "Z"})])
    line = {"kind": "oo", "column": "Operator [ref]", "ref_col": "Operator [ref]", "tier": "high"}
    assert clean_accepts.skip_reason({"pid": "P1"}, line, blk) == ""


def _line(dir_, value, decision=None):
    return {"dir": dir_, "sheet_row": 1797, "decision": decision, "current": {"LengthKnown": "365.00"},
            "proposed_values": {"LengthKnown": value}}


def test_value_change_another_run_contradicts_is_held():
    old, new = _line("a/r7", "469.1"), _line("a/recovery", "365.00", "accept")
    assert "another run proposes 365.00" in clean_accepts.contested_by_other_run({"lines": [old, new]}, old)


def test_value_change_is_not_held_by_a_rejected_or_agreeing_line():
    old = _line("a/r7", "469.1")
    assert not clean_accepts.contested_by_other_run({"lines": [old, _line("a/recovery", "365", "reject")]}, old)
    assert not clean_accepts.contested_by_other_run({"lines": [old, _line("a/other", "469.10")]}, old)
