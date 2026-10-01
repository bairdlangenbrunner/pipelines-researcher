"""A cost recorded as the midpoint of a source's range is supported by the range (manual, Cost)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from url_verifier import range_midpoint_match as rmm  # noqa: E402

PAGE = "по предварительной оценке - от 4,5 до 13,6 млрд долл. США. Высокая сейсмическая"


def test_russian_range_midpoint():
    assert rmm(PAGE, "9050000000.00")


def test_english_and_dash_ranges():
    assert rmm("cost of $4.5-13.6 billion", "9050000000")
    assert rmm("between 1,000 and 2,000 million", "1500000000")


def test_not_the_midpoint():
    assert rmm(PAGE, "9000000000") is None
    assert rmm(PAGE, "") is None
    assert rmm(PAGE, "n/a") is None


def test_verify_url_uses_it_only_when_asked(monkeypatch):
    import url_verifier as uv
    import inspect
    assert "midpoint_of" in inspect.signature(uv.verify_url).parameters
    assert "midpoint_of" in inspect.signature(uv.verify_many).parameters
