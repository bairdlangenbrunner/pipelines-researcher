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


def status_qc(verdict, changes, refs, notes):
    """Merge-time QC for one status_reviews[] record: a 'change' with zero verified
    refs -> 'unclear'; a 'stale' shelved/cancelled inference always gets
    ShelvedCancelledType=Presumed (standing rule 2 — inferred, no fabricated URL).
    Returns (verdict, changes, class_out, notes)."""
    verdict = (verdict or "").strip().lower()
    changes = dict(changes or {})
    if verdict == "change" and not refs:
        verdict = "unclear"
        notes = qc_note(notes, "change proposed without a verified ref -> unclear.")
    if verdict == "stale":
        if (changes.get("Status") or "").lower() in ("shelved", "cancelled") \
                and changes.get("ShelvedCancelledType") != "Presumed":
            changes["ShelvedCancelledType"] = "Presumed"
            notes = qc_note(notes, "added ShelvedCancelledType=Presumed (inferred change).")
    return verdict, changes, STATUS_VERDICT_CLASS.get(verdict, "UNRESOLVED"), notes
