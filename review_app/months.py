"""
Month numbers, shared by push.py (what a month cell is written as) and review_data.py (what a
staged month value is read as). Month columns hold the NUMBER 1-12, never the name or a number
stored as text (Baird 2026-10-08).
"""
import re

MONTHS = {m: i for i, m in enumerate(("january", "february", "march", "april", "may", "june", "july", "august",
                                      "september", "october", "november", "december"), 1)}


def month_number(v):
    """1-12 for 'July', 'Mar', 'Sept.', '11' or 11; None when it is not a month."""
    s = str(v).strip().lower().rstrip(".")
    if re.fullmatch(r"\d{1,2}(\.0+)?", s):
        n = int(float(s))
        return n if 1 <= n <= 12 else None
    if len(s) >= 3:
        hits = [n for m, n in MONTHS.items() if m.startswith(s)]
        if len(hits) == 1:
            return hits[0]
    return None
