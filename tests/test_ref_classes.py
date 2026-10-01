import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from ref_classes import attention_class


def test_all_gone_is_dead():
    assert attention_class([{"status": 404}, {"status": 410}]) == "DEAD_LINK"


def test_loaded_page_is_never_dead():
    assert attention_class([{"status": 200, "ok": False}]) == "REF_UNSUPPORTED"
    assert attention_class([{"status": 404}, {"status": 200}]) == "REF_UNSUPPORTED"


def test_unfetchable_is_blocked():
    assert attention_class([{"status": 403}]) == "REF_BLOCKED"
    assert attention_class([{"status": None}]) == "REF_BLOCKED"
    assert attention_class([]) == "REF_BLOCKED"
