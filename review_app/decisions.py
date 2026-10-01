"""
Consumer-side reader for a staging dir's review decisions (milestone 5).

Producers (`store.py`) key every record by the dataset key
`<dir>::<pid>|<sheet_row>|<colid>` where `sheet_row` is the row RESOLVED against the snapshot the
app was built from and `colid` is `review_data._colid(record, kind)` (+ `#<class>n` when one
(dir, pid, row, colid) held several records). Consumers hold a staged record, not a key, so the
lookup here matches on (pid, colid) first and uses sheet_row only to break ties: the row drifts,
the column does not.

    dec = Decisions(staging_dir)                 # reads <dir>/review_decisions.json (empty if absent)
    d = dec.for_record(rec)                      # latest live line record for a staged record, or None
    dec.decision(rec)                            # 'accept' | 'hold' | 'reject' | 'suggest' | None
    dec.accepted(rec) / dec.counts()             # counts: {'accept': n, 'hold': n, ..., 'undecided': n}

A record is LIVE when it is not undone. A machine record (backend sync / push) is live but not a
person's call; `decision()` returns it anyway (the sheet already holds the value), so a consumer
that wants "clicked accepts only" checks `person_decision()`.
"""
import json
from pathlib import Path

from store import DERIVED_NAME, LOG_NAME, MACHINE_REVIEWERS, latest, read_jsonl

try:                                     # the key's colid comes from the same function the builder uses
    from review_data import _colid, classify
except ImportError:                      # pragma: no cover
    _colid = classify = None


def parse_key(key):
    """'<dir>::<pid>|<row>|<colid>' -> (dir, pid, row_str, colid_base). The '#…' dedupe suffix
    is stripped from colid_base."""
    d, _, rest = key.partition("::")
    pid, _, rest = rest.partition("|")
    row, _, colid = rest.partition("|")
    return d, pid, row, colid.split("#", 1)[0]


def _new_key(rec):
    """(pid, colid) of a staged_new.json discovery candidate (review_data._load_dir keys them
    by slug, not by ref_col), or None for a staged_resolutions record."""
    if rec.get("ref_col") or rec.get("class") not in ("new_row", "matched_existing", "monitor"):
        return None
    slug = rec.get("slug") or (rec.get("name") or "").lower().replace(" ", "-")
    if not slug:
        return None
    return (rec.get("matched_project_id") or rec.get("project_id") or f"new:{slug}", f"new:{slug}")


class Decisions:
    def __init__(self, staging_dir):
        self.dir = Path(staging_dir)
        derived = self.dir / DERIVED_NAME
        if derived.exists():
            self.records = json.loads(derived.read_text(encoding="utf-8")).get("decisions", {})
        else:                                  # derived file missing: derive from the log, same rule
            self.records = latest(read_jsonl(self.dir / LOG_NAME))
        self.by_pid_col = {}
        for key, rec in self.records.items():
            _, pid, row, colid = parse_key(key)
            self.by_pid_col.setdefault((pid, colid), []).append((row, rec))

    def __bool__(self):
        return bool(self.records)

    def _candidates(self, rec, kind=None):
        nk = _new_key(rec)
        if nk:                                 # a staged_new.json candidate, keyed as review_data does
            return self.by_pid_col.get(nk, [])
        pid = rec.get("project_id") or ""
        if kind is None:
            _, kind = classify(rec)
        colid = _colid(rec, kind)
        hit = self.by_pid_col.get((pid, colid), [])
        if not hit and "+" in colid:
            # a fill decided before 2026-10-01 was keyed by its first value column alone
            # (`…|Capacity` for today's `…|Capacity+CapacityUnits`); a sidecar nobody has
            # republished still holds that key, and the decision still applies to this record
            # when exactly one of the fill's columns carries one.
            legacy = [self.by_pid_col[(pid, c)] for c in colid.split("+") if (pid, c) in self.by_pid_col]
            hit = legacy[0] if len(legacy) == 1 else []
        return hit

    def for_record(self, rec, kind=None):
        """The live record for a staged record: unique (pid, colid) match, else the one whose
        sheet_row equals the staged one, else None (ambiguous or undecided)."""
        cands = self._candidates(rec, kind)
        live = [(row, r) for row, r in cands if not r.get("undecided")]
        if len(live) == 1:
            return live[0][1]
        want = str(rec.get("sheet_row", "")).strip()
        same = [r for row, r in live if row == want]
        return same[0] if len(same) == 1 else None

    def decision(self, rec, kind=None):
        r = self.for_record(rec, kind)
        return r.get("decision") if r else None

    def person_decision(self, rec, kind=None):
        r = self.for_record(rec, kind)
        return r.get("decision") if r and r.get("reviewer") not in MACHINE_REVIEWERS else None

    def accepted(self, rec, kind=None):
        return self.decision(rec, kind) == "accept"

    def counts(self, records):
        """Tally of a list of staged records by their decision ('undecided' when none)."""
        out = {"accept": 0, "hold": 0, "reject": 0, "suggest": 0, "undecided": 0}
        for rec in records:
            out[self.decision(rec) or "undecided"] += 1
        return out
