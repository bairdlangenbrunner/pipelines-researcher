#!/usr/bin/env python3
"""Structural validation of deep-sweep shards, run BEFORE split_shards. Read-only.

Catches contract violations while they are still cheap to fix -- a malformed shard that
reaches the merge chain either crashes it or, worse, is silently DROPPED (that is exactly
how the __STATUS__ leg would have vanished before split_shards.py was patched to route it).

Shard shape (as the agents actually emit it):
    {"batch": int, "harvest_opened": int, "resolutions": [ {...}, ... ]}
Record shape: project_id, sheet_row, ref_col, value_cols[], values{}, proposed_refs[],
verifications[{url, ok, contains_value, note}], class_out, tier, independent,
researcher_notes.  Sentinel records set ref_col to __VALIDITY__/__REDUNDANCY__/__STATUS__.

    python validate_shards.py
"""
from __future__ import annotations
import json, collections, re
from urllib.parse import urlparse
from pathlib import Path

HERE = Path(__file__).resolve().parent
REF_CLASSES = {"REFS_ADDED", "REVERIFIED", "UNRESOLVED", "DEAD_LINK"}
SENTINEL_CLASSES = {"CONFIRMED", "CONCERN", "OPEN", "REFUTED", "UNRESOLVED", "INFO"}
SENTINELS = {"__VALIDITY__", "__REDUNDANCY__", "__STATUS__"}
SOURCED = {"REFS_ADDED", "REVERIFIED"}
TIERS = {"high", "medium", "low", "inferred", "presumed", ""}

scope = set()
for name in ("in_scope_pids.txt", "worklist.json"):
    p = HERE / name
    if not p.exists():
        continue
    if name.endswith(".txt"):
        scope = {l.split("#")[0].strip() for l in p.read_text().splitlines() if l.split("#")[0].strip()}
    else:
        w = json.loads(p.read_text())
        rows = w.get("units") or w.get("rows") or (w if isinstance(w, list) else [])
        scope = {r.get("project_id") for r in rows if isinstance(r, dict) and r.get("project_id")}
    if scope:
        break

problems = collections.defaultdict(list)
soft = collections.defaultdict(list)
seen_units = collections.defaultdict(list)
n_rec = 0
by_class = collections.Counter()
harvest = {}
shards = sorted((HERE / "shards").glob("batch_*.json"))

for sp in shards:
    try:
        d = json.loads(sp.read_text())
    except Exception as e:
        problems["unparseable shard"].append(f"{sp.name}: {type(e).__name__}: {e}")
        continue
    recs = d.get("resolutions")
    if not isinstance(recs, list):
        problems["no resolutions[] list"].append(sp.name)
        continue
    if not isinstance(d.get("harvest_opened"), int):
        problems["missing harvest_opened count"].append(sp.name)
    else:
        harvest[sp.name] = d["harvest_opened"]

    for i, r in enumerate(recs):
        n_rec += 1
        where = f"{sp.name}#{i}"
        pid = r.get("project_id") or ""
        col = r.get("ref_col") or ""
        cls = r.get("class_out") or ""
        by_class[cls] += 1
        if not pid:
            problems["missing project_id"].append(where)
        elif scope and pid not in scope:
            problems["PID out of scope"].append(f"{where} {pid}")
        if not col:
            problems["missing ref_col"].append(f"{where} {pid}")
        if r.get("tier") not in TIERS and col not in SENTINELS:
            # A tier grades the SOURCING of a value. An UNRESOLVED unit found no
            # source, so it has nothing to grade -- a null tier there is correct,
            # not a defect, and merge_ref_shards reads it as `(tier or "").strip()`.
            # Only a tier missing from a unit that DID propose refs is a real problem.
            if cls == "UNRESOLVED" and not (r.get("proposed_refs") or []):
                soft["null tier on UNRESOLVED (expected -- nothing to grade)"].append(
                    f"{where} {pid} {col}")
            else:
                problems["bad tier"].append(f"{where} {pid} {col} -> {r.get('tier')!r}")

        # A ref unit whose class_out is not one of build_ref_workbook._ORDER falls into
        # NO workbook bucket and is dropped silently -- research done, then discarded.
        # Sentinels are exempt: the harvester rewrites their class_out by design.
        if col and col not in SENTINELS and cls not in REF_CLASSES:
            problems["class_out not in _ORDER -> SILENTLY DROPPED from workbook"].append(
                f"{where} {pid} {col} -> {cls!r}")

        if col in SENTINELS:
            # class_out and tier on a sentinel are NORMALIZED downstream:
            # harvest_sentinel_findings rewrites class_out to UNRESOLVED (an agent's
            # redundancy verdict is evidence for Baird, never the decision) and coerces a
            # null tier to "n/a". So a wrong value here is cosmetic, not data loss --
            # report it as a note, not a problem.
            if cls not in SENTINEL_CLASSES:
                soft["sentinel class_out normalized to UNRESOLVED downstream"].append(
                    f"{where} {pid} {col} -> {cls!r}")
            if col == "__STATUS__":
                v = (r.get("verdict") or "").strip().lower()
                notes = (r.get("researcher_notes") or "").lower()
                if v not in ("confirm", "change", "stale", "unclear") and not notes:
                    problems["__STATUS__ with no verdict and no notes"].append(f"{where} {pid}")
            continue

        if cls not in REF_CLASSES:
            problems["bad class_out"].append(f"{where} {pid} {col} -> {cls!r}")
        # Key includes the LANE. A cluster can legitimately carry BOTH a ref-leg record
        # and a `kind: FILL` twin -- split_shards sends them to different destinations
        # (ref_shards/ vs rows/) and build_ref_workbook._merge_ref_unit unions them on
        # purpose: the FILL carries the proposed VALUE (which is what earns the tier color
        # on Gas_Backend), the ref record carries the current values as context, and both
        # records' refs land on the one [ref] cell. Keying on (pid, col) alone read that
        # designed pair as an ambiguous collision.
        lane = "FILL" if (r.get("kind") or "").upper() == "FILL" else "REF"
        seen_units[(pid, col, lane)].append(where)

        vals = r.get("values") or {}
        vcols = r.get("value_cols") or []
        refs = r.get("proposed_refs") or []
        ver = {v.get("url") for v in (r.get("verifications") or [])
               if v.get("ok") and v.get("contains_value")}
        kept = [u for u in refs if u in ver]

        # A citation must be a RESOLVABLE URL. Agents have twice written a prose
        # DESCRIPTION into proposed_refs / verifications[].url ("https://www.sohu.com
        # (…roster, item 25)", "<CCXI report, host/path.pdf>"). Those reach the [ref]
        # cell as unusable text and cannot be re-verified by anyone downstream.
        # Also catch a BARE HOST: a site root is a mutable navigation surface, never a
        # citation (see notes/escalation-2026-08-27-egypt-eog-navigation-surface-citations.md).
        for u in list(refs) + [v.get("url") for v in (r.get("verifications") or [])]:
            u = str(u or "")
            if not u:
                continue
            pu = urlparse(u)
            if not u.startswith("http") or " " in pu.netloc or not pu.netloc:
                problems["ref is not a resolvable URL (prose in a citation field)"].append(
                    f"{where} {pid} {col} -> {u[:90]!r}")
            elif (pu.path in ("", "/")) and not pu.query:
                problems["ref is a BARE HOST (navigation surface, not a document)"].append(
                    f"{where} {pid} {col} -> {u}")

        # Orphans, both directions. Only meaningful on a SOURCED class: an UNRESOLVED
        # legitimately carries a value with no ref (the sheet's own, still unsupported).
        if cls in SOURCED:
            if not refs:
                problems["sourced class with no proposed_refs"].append(f"{where} {pid} {col}")
            # value_cols enumerates EVERY column the ref covers (Owner [ref] spans
            # Owner2..Owner11), so blanks are the norm. An orphan is a ref paired with
            # NO value at all -- requiring every listed column to be filled would flag
            # a correctly-sourced single-owner row 20 times over.
            if vcols and not any(str(vals.get(c, "")).strip() for c in vcols):
                problems["ref with NO paired value (orphan)"].append(
                    f"{where} {pid} {col}: all of {vcols[:4]}{'…' if len(vcols) > 4 else ''} blank")
            if not vcols:
                problems["sourced class with empty value_cols"].append(f"{where} {pid} {col}")
        if refs and not kept and cls in SOURCED:
            problems["refs proposed but NONE verified-and-containing"].append(
                f"{where} {pid} {col}: {len(refs)} ref(s), 0 kept")
        if r.get("tier") == "high" and len(kept) < 2:
            problems["tier=high with <2 verified refs"].append(f"{where} {pid} {col}: {len(kept)}")
        if r.get("independent") and len(kept) < 2:
            problems["independent=true with <2 verified refs"].append(f"{where} {pid} {col}: {len(kept)}")

# Reciprocal __REDUNDANCY__ filings: two agents naming each other's row from opposite
# ends of the fan-out. That is CORROBORATION, not duplication -- but the pair must reach
# Baird as ONE cluster, or the same question gets adjudicated twice.
red = collections.defaultdict(list)
for sp in shards:
    try:
        d = json.loads(sp.read_text())
    except Exception:
        continue
    for i, r in enumerate(d.get("resolutions") or []):
        if r.get("ref_col") == "__REDUNDANCY__":
            a = r.get("project_id")
            # Agents name the counterpart either in related_project_id OR only in the
            # prose. Both must count, or a reciprocal pair reads as two separate findings
            # and the same question gets adjudicated twice.
            partners = {r.get("related_project_id")} if r.get("related_project_id") else set()
            partners |= {m for m in re.findall(r"\bP\d{4}\b",
                                               r.get("researcher_notes") or "")
                         if m != a and (not scope or m in scope)}
            for b in partners:
                red[frozenset((a, b))].append(f"{sp.name}#{i} ({a}->{b})")
for pair, hits in red.items():
    if len(hits) > 1:
        soft["RECIPROCAL redundancy filing — corroborated, deliver as ONE cluster"].append(
            f"{' <-> '.join(sorted(pair))}: {', '.join(hits)}")

# A unit appearing in several shards is only a defect if it is AMBIGUOUS. The followup
# batches (15+) deliberately re-research units first covered by the v1 batches, and
# merge_ref_shards indexes by (pid, ref_col, sheet_row) walking shards in lexicographic
# order -- so the highest-numbered followup lands last and wins, which is the intent.
# Report that as a note. What matters is WHO WINS, not how many passes there were: a unit
# can legitimately be worked three times (v1 -> followup -> a later recovery shard, e.g.
# batch_20 re-reading a Wayback capture that was access-blocked on the followup pass).
# A duplicate whose LAST writer is NOT a followup is the real collision -- which record
# reaches the workbook then depends on filename luck.
FOLLOWUP = ("batch_15", "batch_16", "batch_17", "batch_18", "batch_19", "batch_20")
twins = collections.defaultdict(set)
for pid, col, lane in seen_units:
    twins[(pid, col)].add(lane)
for k, lanes in sorted(twins.items()):
    if len(lanes) > 1:
        soft["FILL twin on a ref-leg cluster — designed pair (FILL carries the value)"].append(
            f"{k[0]} {k[1]}")

for k, v in seen_units.items():
    if len(v) < 2:
        continue
    winner = v[-1]
    if winner.startswith(FOLLOWUP) and not any(w.startswith(FOLLOWUP) and w != winner
                                               for w in v[:-1] if w.split("#")[0] == winner.split("#")[0]):
        soft["re-researched unit — followup shard supersedes earlier pass (last shard wins)"].append(
            f"{k[0]} {k[1]}: {' -> '.join(v)}")
    else:
        problems["AMBIGUOUS duplicate unit (winner decided by filename order)"].append(
            f"{k[0]} {k[1]}: {', '.join(v)}")

print(f"{len(shards)} shard(s), {n_rec} record(s), {len(seen_units)} distinct ref unit(s), "
      f"{len({p for p, _, _ in seen_units})} row(s)"
      + (f", scope={len(scope)} PIDs" if scope else ", scope=UNKNOWN (no worklist found)"))
print("classes: " + ", ".join(f"{k or '(blank)'}={v}" for k, v in by_class.most_common()))
print("harvest_opened: " + ", ".join(f"{k.replace('batch_','b').replace('.json','')}={v}"
                                     for k, v in sorted(harvest.items())))
for k in sorted(soft):
    print(f"\nnote: {k}  ({len(soft[k])})")
    for line in soft[k][:10]:
        print("    " + line)
if not problems:
    print("\nPASS — no structural problems")
for k in sorted(problems):
    print(f"\n{k}  ({len(problems[k])})")
    for line in problems[k][:15]:
        print("    " + line)
    if len(problems[k]) > 15:
        print(f"    … {len(problems[k]) - 15} more")
