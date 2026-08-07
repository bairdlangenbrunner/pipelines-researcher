#!/usr/bin/env python3
"""Shared merge-time QC helpers for the shard-merge CLIs.

Used by merge_ref_shards.py / merge_deepsweep_shards.py / merge_discovery_shards.py —
one rule set, one implementation: no orphan or unverified ref survives a merge, and
GEM / blocklisted hosts are stripped (defense in depth; url_verifier rejects them too).
"""
import glob
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from url_verifier import BLOCKLIST_HOSTS, GEM_HOSTS  # noqa: E402

BLOCK = tuple(GEM_HOSTS + BLOCKLIST_HOSTS)

STATUS_VERDICT_CLASS = {"confirm": "CONFIRMED", "change": "CHANGE_PROPOSED",
                        "stale": "STALE"}


def verified_refs(urls, verifs):
    """Keep only http(s) URLs whose verification is ok && contains_value, minus
    blocklisted hosts; deduped, order-preserving. With no verifications at all,
    clean/blocklist-filter only (the caller decides whether that's acceptable)."""
    okset = {v.get("url") for v in (verifs or []) if v.get("ok") and v.get("contains_value")}
    out, seen = [], set()
    for u in urls or []:
        u = (u or "").strip()
        low = u.lower()
        if not low.startswith("http") or any(h in low for h in BLOCK):
            continue
        if verifs and u not in okset:
            continue
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def iter_shards(pattern):
    """Yield (path, parsed-dict) for every shard matching the glob, sorted;
    print a WARN and skip any unreadable one (a bad shard never kills a merge)."""
    for p in sorted(glob.glob(pattern)):
        try:
            yield p, json.load(open(p))
        except Exception as e:
            print(f"  WARN unreadable shard {p}: {e}")


def qc_note(notes, msg):
    """Append a ' [QC] <msg>' annotation to a researcher_notes string."""
    return ((notes or "") + f" [QC] {msg}").strip()


_COST_MULTIPLIER_WORDS = ("million", "billion", "thousand", "mn", "bn",
                          "(millions)", "(billions)")


def bad_cost_units(values):
    """Cost-units convention: a *CostUnits cell holds a bare currency code (USD, EGP,
    EUR ...) and the magnitude lives in the cost number itself — never 'EGP million' /
    'USD (millions)'. Returns {col: value} for offending cells (WARN, human fixes —
    auto-multiplying would guess at the writer's intent)."""
    bad = {}
    for col, val in (values or {}).items():
        if col.endswith("CostUnits") and any(
                w in str(val).lower() for w in _COST_MULTIPLIER_WORDS):
            bad[col] = val
    return bad


def _norm_value(v):
    """Normalize one cell for equality: numbers compare numerically (so '1814' ==
    '1814.00' == '1,814'), everything else case- and whitespace-insensitively."""
    s = str(v if v is not None else "").strip()
    try:
        return ("num", round(float(s.replace(",", "")), 6))
    except ValueError:
        return ("str", " ".join(s.lower().split()))


def is_ref_only(proposed_values, current_values):
    """True when a shard fill proposes exactly the values already on the sheet — i.e.
    it is REF work, not a value change.

    A unit whose `[ref]` is blank but whose value is present (class MISSING_REF) comes
    back from a deep-sweep subagent as a fills[] entry: the agent researched the cell
    and found a source for the value that is already there. Staging that as a FILL
    would tint the value cell on the paste surface, telling the researcher to paste
    over a cell that is not changing (the workbook legend reserves a tinted value cell
    for a *proposed* value). Folding it onto its ref record instead yields the
    documented ref-only rendering: colored `[ref]`, untinted value.

    Requires a non-empty current value to compare against — a genuinely blank field is
    a real fill and must stay one.
    """
    cur = current_values or {}
    prop = proposed_values or {}
    if not prop or not cur:
        return False
    if not any(str(v).strip() for v in cur.values()):
        return False
    return all(_norm_value(prop[c]) == _norm_value(cur.get(c)) for c in prop)


def status_qc(verdict, changes, refs, notes):
    """Merge-time QC for one status_reviews[] record: a 'change' with zero verified
    refs -> 'unclear'; a 'stale' shelved/cancelled inference always gets
    ShelvedCancelledType=inferred (standing rule 2 — inferred, no fabricated URL).
    Returns (verdict, changes, class_out, notes).

    NB the value is lowercase `inferred`, not `Presumed`: verified 2026-08-07 against
    both live tabs, where ShelvedCancelledType holds only `inferred` (84 gas / 63 oil)
    and `confirmed` (83 / 52). `Presumed` appears nowhere in either tracker."""
    verdict = (verdict or "").strip().lower()
    changes = dict(changes or {})
    # Vocab normalization: subagents write the Title-Case `Presumed`/`Confirmed` the old
    # docs specified; the live column holds only lowercase `inferred`/`confirmed`.
    sct = (changes.get("ShelvedCancelledType") or "").strip().lower()
    if sct:
        fixed = {"presumed": "inferred", "inferred": "inferred",
                 "confirmed": "confirmed"}.get(sct)
        if fixed and fixed != changes["ShelvedCancelledType"]:
            notes = qc_note(notes, f"ShelvedCancelledType {changes['ShelvedCancelledType']!r}"
                                   f" -> {fixed!r} (live-column vocab).")
            changes["ShelvedCancelledType"] = fixed
    if verdict == "change" and not refs:
        verdict = "unclear"
        notes = qc_note(notes, "change proposed without a verified ref -> unclear.")
    if verdict == "stale":
        if (changes.get("Status") or "").lower() in ("shelved", "cancelled") \
                and (changes.get("ShelvedCancelledType") or "").lower() != "inferred":
            changes["ShelvedCancelledType"] = "inferred"
            notes = qc_note(notes, "set ShelvedCancelledType=inferred (dormancy-rule change).")
    return verdict, changes, STATUS_VERDICT_CLASS.get(verdict, "UNRESOLVED"), notes
