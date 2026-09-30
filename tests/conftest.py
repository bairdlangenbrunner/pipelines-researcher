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
