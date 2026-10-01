"""The three ways an EXISTING `[ref]` can need attention, named for what actually happened.

`DEAD_LINK` used to cover all of them and so told researchers a working page was dead
(neftegaz.ru 660602 for P0734: HTTP 200, the value screen missed, staged DEAD_LINK; Baird
2026-09-30: "a dead link means a link doesn't load, OBVIOUSLY. it should NEVER imply anything
else"). One home for the rule, imported by the seeder, the merge and the workbook builder:

  DEAD_LINK        every current ref is GONE — HTTP 404/410 (the only confirmed deletion).
  REF_BLOCKED      no current ref could be fetched from here and at least one was not gone —
                   401/403/WAF, timeout, connection or TLS error, no status. NOT a deletion:
                   it may load fine for a person (keep the ref, add a Wayback snapshot).
  REF_UNSUPPORTED  at least one current ref LOADED (HTTP 200) but the value/name screen or the
                   agent's read did not support the data point. Re-read the page.

Only `DEAD_LINK` may be painted red as "link did not load"; the other two are amber.
"""
from __future__ import annotations

GONE_STATUSES = {404, 410}
DEAD_LINK = "DEAD_LINK"
REF_BLOCKED = "REF_BLOCKED"
REF_UNSUPPORTED = "REF_UNSUPPORTED"
# every class_out that means "an existing ref needs attention"
ATTENTION = (DEAD_LINK, REF_BLOCKED, REF_UNSUPPORTED)
ATTENTION_SET = frozenset(ATTENTION)


def _status(v) -> int | None:
    try:
        return int(v.get("status"))
    except (TypeError, ValueError, AttributeError):
        return None


def loaded(v: dict) -> bool:
    """One verification: did the page itself load (HTTP 200, not an access-block page)?"""
    if v.get("blocked") or v.get("non_citation"):
        return False
    return _status(v) == 200


def attention_class(checks) -> str:
    """Class for an existing-ref record that is neither REVERIFIED nor sourced, from its
    per-URL verification dicts (`status`, `blocked`, …)."""
    checks = [c for c in (checks or []) if isinstance(c, dict)]
    if checks and all(_status(c) in GONE_STATUSES for c in checks):
        return DEAD_LINK
    if any(loaded(c) for c in checks):
        return REF_UNSUPPORTED
    return REF_BLOCKED


def label(cls: str) -> str:
    return {DEAD_LINK: "link gone (404/410)", REF_BLOCKED: "could not be fetched from here",
            REF_UNSUPPORTED: "page loads but does not support the value"}.get(cls, cls)
