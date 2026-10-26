"""check_shard_coverage.check_findings: a status `change` carries the date of the event it reports
(Baird 2026-10-16, P0241: operating staged with no start month though the ref gave June 2026)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_shard_coverage as c  # noqa: E402

BASE = {"verdict": "change", "proposed_refs": ["https://x.example/a"],
        "verifications": [{"url": "https://x.example/a", "ok": True, "contains_value": True}]}


def review(**kw):
    return c.check_findings({"status_reviews": [dict(BASE, **kw)]})


def test_change_without_its_date_column_blocks():
    out = review(proposed_status="operating", proposed_changes={"Status": "operating"})
    assert len(out) == 1 and "StartYear1" in out[0]["why"]
    assert "ConstructionYear" in review(proposed_status="construction", proposed_changes={"Status": "construction"})[0]["why"]


def test_change_with_its_date_or_a_not_found_note_passes():
    assert review(proposed_status="operating", proposed_changes={"Status": "operating", "StartYear1": "2026", "StartMonth1": 6}) == []
    assert review(proposed_status="cancelled", proposed_changes={"Status": "cancelled"},
                  researcher_notes="The cancellation year was not stated in the filing.") == []
    assert review(verdict="confirm", proposed_changes={}) == []
