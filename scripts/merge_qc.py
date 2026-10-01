#!/usr/bin/env python3
"""Shared merge-time QC helpers for the shard-merge CLIs.

Used by merge_ref_shards.py / merge_deepsweep_shards.py / merge_discovery_shards.py —
one rule set, one implementation: no orphan or unverified ref survives a merge, and
GEM / blocklisted hosts are stripped (defense in depth; url_verifier rejects them too).
"""
import glob
import json
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from url_verifier import BLOCKLIST_HOSTS, GEM_HOSTS  # noqa: E402

BLOCK = tuple(GEM_HOSTS + BLOCKLIST_HOSTS)

STATUS_VERDICT_CLASS = {"confirm": "CONFIRMED", "change": "CHANGE_PROPOSED",
                        "stale": "STALE"}


def verified_refs(urls, verifs):
    """Keep only http(s) URLs whose verification is ok && contains_value, minus
    blocklisted hosts; deduped, order-preserving. With no verifications at all,
    clean/blocklist-filter only (the caller decides whether that's acceptable).

    THAT LAST CLAUSE IS AN ASYMMETRY WITH THE DELIVERY GATE, so mind it: with an empty
    `verifs` this returns ALL the urls, while `sweep_gates.verified()` returns NONE (it
    has no lenient branch). A writer that delegates here while a gate applies the strict
    rule produces a store the gate disagrees with -- which is how
    `harvest_sentinel_findings.py` shipped gate-B/D findings the store had already been
    told to fix (2026-09-10). Across a store/gate boundary, spell the strict basis out:
    `{v["url"] for v in verifications if v.get("ok") and v.get("contains_value")}`."""
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


_WAYBACK_RE = re.compile(r"^https?://web\.archive\.org/web/[^/]+/(https?://.*)$", re.I)


def origin_host(url):
    """Publisher host for independence counting. A Wayback capture is the ORIGIN's
    bytes, so `web.archive.org/web/<ts>/<url>` counts as <url>'s host — otherwise a
    live page plus its own snapshot would read as two sources.

    The port is stripped for the same reason: `opec.org` and `opec.org:80` are one
    publisher, and counting them as two let Libya P1859's `Diameter [ref]` pass the
    independence gate on a single OPEC document (found 2026-09-04). Any normalization
    added here must keep asking one question — would a reader call these the same
    publisher?"""
    u = (url or "").strip()
    m = _WAYBACK_RE.match(u)
    if m:
        u = m.group(1)
    host = urlparse(u).netloc.lower().removeprefix("www.")
    return host.rsplit(":", 1)[0] if ":" in host else host


# Hosts that REDISTRIBUTE third-party documents: an exchange disclosure portal, an
# interbank-market filing site, a corporate-data aggregator. On these the host names
# the VENUE, not the author, so it cannot answer origin_host's question ("would a
# reader call these the same publisher?"). Found 2026-09-10 on China/Jiangxi gas: four
# 中诚信国际 (CCXI) credit rating reports on one issuer, served from static.sse.com.cn,
# qxb-pdf-osscache.qixin.com and chinamoney.com.cn, read as three publishers and
# carried 22 records to independent=yes (6 of them tier high) on what is one author —
# and two of those URLs were byte-identical PDFs (md5 a47195d52877446d4f6ccb49f5912a9f).
# Collapsing every venue-hosted ref into ONE bucket is deliberately conservative: it
# can under-credit two genuinely different publishers who happen to share a venue, but
# it never manufactures independence, and the QC note says why so a researcher can
# override with evidence of authorship.
VENUE_HOSTS = (
    "sse.com.cn", "szse.cn", "bse.cn", "neeq.com.cn", "cninfo.com.cn",  # exchanges
    "chinamoney.com.cn",                                               # NAFMII/CFETS
    "qixin.com", "qcc.com", "tianyancha.com",                          # aggregators
)
VENUE_BUCKET = "<venue-hosted: publisher unverified>"


def publisher_key(url):
    """Origin identity for independence counting. Same as `origin_host` except that
    document-redistribution venues collapse to one bucket — see VENUE_HOSTS."""
    h = origin_host(url)
    if not h:
        return ""
    if any(h == v or h.endswith("." + v) for v in VENUE_HOSTS):
        return VENUE_BUCKET
    return h


def independence_qc(refs, tier, independent, notes, high_min=1):
    """`independent` means the rubric's >=2 INDEPENDENT AGREEING sources — not
    "independent of GEM". Agents routinely set it True on a single-source unit whose
    own notes say "single source", and it renders as the yes/no column a researcher
    reads as "two origins agree". Enforce it against the refs the record actually
    carries: a claim of independence needs >=2 surviving refs from >=2 distinct
    PUBLISHERS (two articles on one outlet, a page and its own Wayback snapshot, or
    two documents served from one redistribution VENUE, are one origin).

    The TIER is a separate question (rule 4, Baird 2026-09-30): ONE validated ref is
    sufficient and shows green, so `high` needs only `high_min` surviving publishers —
    1 by default (a `high` with no surviving ref at all is capped), and 2 for a STATUS
    CHANGE, which stays green only on 2+ independent publishers (pass
    `high_min=STATUS_CHANGE_MIN_PUBLISHERS`). Both halves are enforced independently of
    what the flag claims: until 2026-09-10 the tier half hung off `if not independent`,
    which let an honest `false` keep a `high` the over-claiming record lost.

    Returns (tier, independent, notes).
    """
    hosts = {h for h in (publisher_key(u) for u in (refs or [])) if h}
    n, nh = len(refs or []), len(hosts)
    msgs = []
    if independent and nh < 2:
        independent = False
        msgs.append(f"independent=yes claimed on {n} surviving ref(s) from "
                    f"{nh} publisher(s) -> no")
    if tier == "high" and nh < high_min:
        tier = "medium"
        why = ("a status change needs 2+ independent publishers for high"
               if high_min >= 2 else "high needs at least one surviving ref")
        msgs.append(f"tier high -> medium ({n} surviving ref(s) from {nh} publisher(s); {why})")
    if not msgs:
        return tier, independent, notes
    return tier, independent, qc_note(notes, "; ".join(msgs) + ".")


STATUS_CHANGE_MIN_PUBLISHERS = 2


def validated_tier(refs, verifs, tier, notes, cls=None, ref_col=None):
    """Rule 4 as of 2026-09-30: one validated ref is SUFFICIENT and shows green. A record
    the agent tiered `medium` (the old single-source label) is promoted to `high` when it
    carries >=1 surviving ref AND a verification that loaded and names the pipeline
    (`ok` + `name_found: True`) — the machine half of the validation checklist in
    docs/reference/confidence_tiers.md. `low` (weak / partial / conflicting, the agent's
    judgment) is never promoted, and neither is a status change: call this only where
    `high_min` is 1. Run AFTER relevance_qc, which has already capped unnamed refs.

    Nor is an `UNRESOLVED` record or a `__VALIDITY__` concern: a page that names the
    pipeline but does not settle the unit validates nothing (pass `cls` / `ref_col`).

    Returns (tier, notes)."""
    if tier != "medium" or not refs or cls == "UNRESOLVED" or ref_col == "__VALIDITY__":
        return tier, notes
    if not any(v.get("ok") and v.get("name_found") is True for v in (verifs or [])):
        return tier, notes
    return "high", qc_note(notes, "tier medium -> high (one validated ref is sufficient, rule 4).")


def is_status_change(values, sheet, pid, sheet_row):
    """True when a record's `values` propose a Status different from the snapshot's.
    Unknown current status (no snapshot / row not found) counts as a change, so the
    stricter 2+ rule applies when we cannot tell."""
    new = str((values or {}).get("Status") or "").strip().lower()
    if not new:
        return False
    cur = sheet_value(sheet, pid, sheet_row, "Status")
    return cur is None or new != str(cur).strip().lower()


def relevance_qc(verifs, tier, notes):
    """A ref must be ABOUT this pipeline, not merely contain its number. MZ's third
    feedback point on Jiangxi v2 (2026-09-03): pages cited for the "A–B" line that were
    about endpoint A, or endpoint B, or the provincial network — a keyword match on the
    value with no identity check. The shard contract now asks every verification record
    to carry `name_found` (the verifier's `name=` result, or the agent's own read when the
    name is in another script). Enforce what the record says:

      * some verification has `name_found: True`  -> fine.
      * every named verification says `name_found: False` -> the refs do not identify the
        pipeline; cap the tier at `low` and say so (never drop the ref — the page may still
        be the right document under a name form the check missed; the researcher decides).
      * no record carries the field at all -> note it, tier untouched (older shards).

    Returns (tier, notes)."""
    named = [v for v in (verifs or []) if "name_found" in v and v.get("ok")]
    if not named:
        if verifs and any(v.get("ok") for v in verifs):
            notes = qc_note(notes, "relevance unrecorded (no name_found on any verification).")
        return tier, notes
    if any(v.get("name_found") for v in named):
        return tier, notes
    msg = ("no verified ref names this pipeline (name_found=false on all) -> relevance "
           "unconfirmed; tier capped at low")
    if tier in ("high", "medium"):
        tier = "low"
    return tier, qc_note(notes, msg + ".")


def iter_shards(*patterns):
    """Yield (path, parsed-dict) for every shard matching the glob(s), sorted;
    print a WARN and skip any unreadable one (a bad shard never kills a merge).

    Two things are skipped rather than parsed as research:

    * `_`-prefixed sidecars. The brief builders write `_manifest.json` and
      `_groups.json` into the very directory the shards land in, and a shard glob
      picks them up. `_groups.json` is a LIST, which crashed merge_ref_shards on the
      US gas batch (2026-09-04); `_manifest.json` is a dict, so it would not have
      crashed anything — it would have quietly counted as a shard forever. Real
      shards are named for a ProjectID, so no `_` name is ever research.
    * Any payload that is not a dict, for the same reason a bad shard does not kill
      a merge: one malformed file must not cost the batch its other 38.
    """
    for p in sorted(q for pattern in patterns for q in glob.glob(pattern)):
        if os.path.basename(p).startswith("_"):
            continue
        try:
            d = json.load(open(p))
        except Exception as e:
            print(f"  WARN unreadable shard {p}: {e}")
            continue
        if not isinstance(d, dict):
            print(f"  WARN skipping non-dict shard {p} ({type(d).__name__})")
            continue
        yield p, d


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


class Sheet(NamedTuple):
    columns: set
    backend: dict
    owners: dict
    single: dict
    pairs: dict
    primary: dict


def load_sheet(scope):
    """The snapshot a worklist was built from, as a `Sheet`, or None when `scope.csv` can't
    be located.

    `columns` is every backend header plus every operators/owners-tab header, and `pairs`
    maps each `[ref]` column to its value columns (ref_pairs.py): a `values{}` key must be
    one of its record's pair columns (or, off a pair, at least a sheet column), because each
    one lands in a real cell on a paste surface. `backend_rows` is keyed (ProjectID, SheetRow) with SheetRow = data-row index + 4 (the
    tracker header is at CSV row 2); `single_row` maps a ProjectID with exactly one backend
    row to that row (the fallback when a staged sheet_row is stale); `owners_rows` is keyed by ProjectID (header at row 1,
    first row wins). Used to reject off-schema value keys and to put the sheet's own values
    back on an UNRESOLVED fill (Russia R6 DEFECTS #4/#5)."""
    import csv
    from ref_pairs import discover_owner_ref_pairs, discover_ref_pairs
    scope = scope or {}
    data = Path(__file__).resolve().parent.parent / "data"

    def _read(name):
        if not name:
            return None
        p = Path(name) if Path(name).exists() else data / Path(name).name
        if not p.exists():
            return None
        with p.open(newline="") as f:
            return list(csv.reader(f))

    rows = _read(scope.get("csv"))
    if not rows or len(rows) < 3:
        return None
    header = rows[2]
    pid_i = header.index("ProjectID") if "ProjectID" in header else None
    backend = {}
    if pid_i is not None:
        for di, raw in enumerate(rows[3:]):
            pid = raw[pid_i] if pid_i < len(raw) else ""
            backend[(pid, di + 4)] = {c: (raw[i] if i < len(raw) else "")
                                      for i, c in enumerate(header)}
    columns = set(header)
    found = [p for p in discover_ref_pairs(header) if p.get("ref_col")]
    owners = {}
    oo = _read(scope.get("owners_csv"))
    if oo and len(oo) > 2:
        oh = oo[1]
        columns |= set(oh)
        found += discover_owner_ref_pairs(oh)
        if "ProjectID" in oh:
            oi = oh.index("ProjectID")
            for raw in oo[2:]:
                pid = raw[oi] if oi < len(raw) else ""
                if pid and pid not in owners:
                    owners[pid] = {c: (raw[i] if i < len(raw) else "") for i, c in enumerate(oh)}
    columns.discard("")
    per_pid = {}
    for pid, _row in backend:
        per_pid.setdefault(pid, []).append(backend[(pid, _row)])
    single = {pid: rs[0] for pid, rs in per_pid.items() if pid and len(rs) == 1}
    pairs = {p["ref_col"]: set(p["value_cols"]) for p in found}
    primary = {p["ref_col"]: p["primary_value_col"] for p in found}
    return Sheet(columns, backend, owners, single, pairs, primary)


def off_schema_keys(sheet, ref_col, values):
    """`values{}` keys that belong on no paste surface for this record: outside its `[ref]`
    pair's value columns (R6: `Owner` under `Owner [ref]`, whose values are Owner1/Owner1%
    on the owners tab), or — for a record keyed to no known pair — not a sheet column at
    all (`Start`, `Construction`). [] when the snapshot is unavailable."""
    if sheet is None or not isinstance(values, dict):
        return []
    allowed = sheet.pairs.get(ref_col or "") or sheet.columns
    return [k for k in values if k not in allowed]


def sheet_value(sheet, pid, sheet_row, col):
    """The snapshot's current value for one cell, or None when it can't be located."""
    if not sheet:
        return None
    try:
        row = sheet.backend.get((pid, int(sheet_row)))
    except (TypeError, ValueError):
        row = None
    if row is None:
        row = sheet.single.get(pid)
    if row is not None and col in row:
        return row[col]
    oo = sheet.owners.get(pid)
    if oo is not None and col in oo:
        return oo[col]
    return None


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
    if verdict == "change" and not changes:
        # A `change` with an empty `values{}` tints nothing on the Backend paste surface:
        # the researcher reads "this row changed" and has nothing to paste. Either the
        # record states what the new value is or it is not yet a change (Russia R3).
        verdict = "unclear"
        notes = qc_note(notes, "change proposed with no pasteable value -> unclear.")
    if verdict == "stale":
        if (changes.get("Status") or "").lower() in ("shelved", "cancelled") \
                and (changes.get("ShelvedCancelledType") or "").lower() != "inferred":
            changes["ShelvedCancelledType"] = "inferred"
            notes = qc_note(notes, "set ShelvedCancelledType=inferred (dormancy-rule change).")
    return verdict, changes, STATUS_VERDICT_CLASS.get(verdict, "UNRESOLVED"), notes
