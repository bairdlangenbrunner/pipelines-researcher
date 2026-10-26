"""check_findings: a `confirm` on an old `proposed` row must apply the 2-/4-year dormancy rules
(Baird 2026-10-16, P4449)."""
import datetime
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_shard_coverage as c  # noqa: E402

THIS = datetime.date.today().year


def sheet(py):
    row = {"ProposalYear": str(py)}
    return SimpleNamespace(backend={("P1", 5): row}, single={"P1": row}, owners={})


def run(py, **kw):
    rec = {"verdict": "confirm", "current_status": "proposed", "sheet_row": 5, **kw}
    return c.check_findings({"status_reviews": [rec]}, sheet(py), "P1")


def test_old_confirm_blocks_and_names_the_rule():
    assert "shelved" in run(THIS - 2)[0]["why"]
    assert "cancelled" in run(THIS - 5)[0]["why"]


def test_young_row_recent_evidence_or_dormancy_note_passes():
    assert run(THIS - 1) == []
    assert run(THIS - 5, evidence_date=f"{THIS}-03") == []
    assert run(THIS - 5, researcher_notes="Shelved rule considered; a June filing shows work continuing.") == []
    assert run("") == []
