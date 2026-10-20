import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import merge_qc  # noqa: E402


def test_inferred_cancelled_year_is_newest_source_plus_four():
    v, ch, cls, notes = merge_qc.status_qc("stale", {"ShelvedCancelledType": "inferred"}, ["u"], "",
                                           evidence_date="2018-10", current_status="cancelled")
    assert ch["CancelledYear"] == "2022" and ch["ShelvedCancelledType"] == "inferred"


def test_inferred_shelved_year_is_newest_source_plus_two():
    _, ch, _, _ = merge_qc.status_qc("stale", {"Status": "shelved", "ShelvedCancelledType": "inferred"}, ["u"], "",
                                     evidence_date="2023-07")
    assert ch["ShelvedYear"] == "2025"


def test_year_equal_to_the_evidence_year_is_corrected_and_another_year_is_kept():
    _, ch, _, _ = merge_qc.status_qc("stale", {"Status": "shelved", "ShelvedCancelledType": "inferred",
                                               "ShelvedYear": "2023"}, ["u"], "", evidence_date="2023-07")
    assert ch["ShelvedYear"] == "2025"
    _, ch, _, _ = merge_qc.status_qc("stale", {"Status": "cancelled", "CancelledYear": "2020",
                                               "ShelvedCancelledType": "inferred"}, ["u"], "",
                                     evidence_date="2018-10")
    assert ch["CancelledYear"] == "2020"
