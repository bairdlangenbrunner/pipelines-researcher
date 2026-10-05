"""Make the flat scripts/ modules and review_app/ importable from tests.

The scripts import each other with flat names (`from normalize import ...`) because
they run from inside scripts/ at batch time; review_app/ modules are imported the same
way. Neither is an installed distribution, so put both on sys.path here.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for p in (HERE.parent / "scripts", HERE.parent / "review_app", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _review_kinds_enabled(monkeypatch):
    """The review-app skips (route QC, recon dirs) are production defaults; the fixtures here
    exercise the item machinery, so run them with the skips off. test_review_skips turns them on."""
    try:
        import review_data
    except Exception:
        return
    monkeypatch.setattr(review_data, "SKIP_ROUTEQC", False)
    monkeypatch.setattr(review_data, "SKIP_RECON_DIRS", False)
