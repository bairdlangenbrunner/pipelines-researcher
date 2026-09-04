#!/usr/bin/env python3
"""Promote `CONCERN:` prose in ref-gap shards into real validity records.

The ref-gap brief tells a research subagent that finds a DATA problem — a source that
contradicts the sheet, a row that looks duplicated or misclassified — to record it in
`researcher_notes` prefixed `CONCERN:` and change nothing. That is the right instruction
(it keeps a citation pass from silently rewriting values), but it leaves the finding
inside a `[ref]` record's notes, where the deliverable renders it as ref detail and the
Validity tab — the surface a researcher actually triages concerns from — never shows it.
That is how a real finding gets buried: three sources disagreeing with the sheet's Length
is not a footnote about a citation, it is a spec concern about the row.

This lifts each one into the `validity[]` array of the matching `rows/<PID>.json`, so the
normal `merge_deepsweep_shards.py` fold puts it on the Validity tab with its refs
attached. It NEVER changes a value, a class_out, or the ref record itself — the concern
stays in the ref notes too, and the promoted record is `verdict: concern` with a
recommendation to adjudicate, not to apply.

Run AFTER the ref-gap shards land and BEFORE merge_deepsweep_shards.py. Idempotent: a
promoted record is stamped `promoted_from` and is not re-promoted.

Usage:
    python scripts/promote_ref_concerns.py --staging batches/<scope>/staging/<dir>/ --apply
"""
import argparse, glob, json, os, re, collections

_CONCERN_RE = re.compile(r"CONCERN:\s*(.+?)(?=\s*(?:\[QC\]|CONCERN:)|$)", re.S)

# Which concern_type a promoted finding gets. `spec` is the fallback because a value
# conflict is the overwhelmingly common case; the others need their own words present.
_TYPE_WORDS = (
    ("duplicate", ("duplicate", "same pipeline as", "already tracked", "dupe of")),
    ("existence", ("does not exist", "never built", "no evidence the", "nonexistent",
                   "not a real")),
    ("classification", ("misclassified", "wrong tracker", "belongs in goit",
                        "belongs in ggit", "gathering line", "not a transmission")),
    ("attribution", ("owner", "operator", "ownership", "parent company", "acquired by")),
)


# `CONCERN: none` is a NO-concern marker, not a finding. Subagents answer the brief's
# concern prompt literally, so ~15% of CONCERN: blocks open with "none", "none.",
# "none -- <rationale>", or "none on this unit". Promoting those manufactures Validity
# rows that assert a problem the researcher explicitly said is absent. Only a bare
# leading `none` counts: "none of the three sources states ..." is a real sentence and
# stays.
_NO_CONCERN_RE = re.compile(r"^none\s*(?:[.\-\u2013\u2014;:]|on this unit\b|found\b|$)", re.I)


def is_no_concern(text):
    return bool(_NO_CONCERN_RE.match((text or "").strip()))


def concern_type(text):
    low = text.lower()
    for kind, words in _TYPE_WORDS:
        if any(w in low for w in words):
            return kind
    return "spec"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    args = ap.parse_args()
    S = args.staging.rstrip("/")

    found = collections.defaultdict(list)
    no_concern = []
    for p in sorted(glob.glob(os.path.join(S, "ref_shards", "*.json"))):
        if os.path.basename(p).startswith("_"):
            continue
        d = json.load(open(p))
        pid = d.get("project_id") or os.path.basename(p)[:-5]
        for u in d.get("resolutions", []) or []:
            notes = u.get("researcher_notes") or ""
            for m in _CONCERN_RE.finditer(notes):
                txt = m.group(1).strip()
                if is_no_concern(txt):
                    no_concern.append((pid, u.get("ref_col", "")))
                    continue
                found[pid].append((u, txt))

    if no_concern:
        print(f"skipped {len(no_concern)} 'CONCERN: none' marker(s) (not findings): "
              + ", ".join(f"{a} {b}" for a, b in no_concern[:8])
              + (" ..." if len(no_concern) > 8 else ""))
    if not found:
        print("no CONCERN: prose in any ref shard")
        return

    promoted = skipped = norow = 0
    for pid, items in sorted(found.items()):
        rowp = os.path.join(S, "rows", f"{pid}.json")
        if not os.path.exists(rowp):
            print(f"  WARN {pid}: no rows/{pid}.json to promote into ({len(items)} concern(s))")
            norow += len(items)
            continue
        doc = json.load(open(rowp))
        vals = doc.setdefault("validity", [])
        have = {v.get("promoted_from") for v in vals if isinstance(v, dict)}
        changed = False
        for u, text in items:
            col = u.get("ref_col", "")
            key = f"{col}|{text[:60]}"
            if key in have:
                skipped += 1
                continue
            vals.append({
                "segment_name": u.get("segment_name", ""),
                "verdict": "concern",
                "concern_type": concern_type(text),
                "recommendation": (
                    f"Adjudicate the {col.replace(' [ref]', '') or 'value'} conflict raised "
                    f"during the ref pass — sourced evidence disagrees with the sheet. "
                    f"No value changed."),
                "researcher_notes": f"{col}: {text}",
                "proposed_refs": u.get("proposed_refs", []) or [],
                "verifications": u.get("verifications", []) or [],
                "tier": u.get("tier", "") or "medium",
                "independent": bool(u.get("independent", False)),
                "source_language": u.get("source_language", "en"),
                "promoted_from": key,
            })
            promoted += 1
            changed = True
        if changed and args.apply:
            json.dump(doc, open(rowp, "w"), indent=1, ensure_ascii=False)

    verb = "promoted" if args.apply else "would promote (dry-run)"
    print(f"{verb} {promoted} CONCERN(s) to validity across {len(found)} PID(s)")
    if skipped:
        print(f"  {skipped} already promoted — untouched")
    if norow:
        print(f"  WARN {norow} concern(s) had no row shard to promote into")
    if not args.apply and promoted:
        print("Re-run with --apply, then re-run merge_deepsweep_shards.py")


if __name__ == "__main__":
    main()
