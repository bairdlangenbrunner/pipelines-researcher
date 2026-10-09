import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_no_staged_record_names_a_column_the_sheet_lacks():
    # exits 1 while any staged `values` key or label is not a real header (known slips repair with --apply)
    r = subprocess.run([sys.executable, str(ROOT / "scripts/fix_staged_columns.py")], capture_output=True, text=True)
    assert "would change" in r.stdout and r.stdout.count("\nvalues ") == 0, r.stdout[-2000:]
    assert not [l for l in r.stdout.splitlines() if l.startswith("values ")], r.stdout[-2000:]
