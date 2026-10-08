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
