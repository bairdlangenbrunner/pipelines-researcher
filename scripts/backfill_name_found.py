#!/usr/bin/env python3
"""Stamp `name_found` onto shard verifications that were written without it.

`merge_qc.relevance_qc` (added 2026-09-03 off MZ's Jiangxi v2 feedback) enforces that a
`[ref]` is ABOUT the pipeline, not merely a page containing its value. It reads
`name_found` off each verification record. A research brief that predates the field — or
an agent that omits it — leaves every record annotated "relevance unrecorded", which is
noise where the answer is mechanically checkable: re-fetch the URL and ask whether the
page names the pipeline.

That is exactly what `url_verifier.verify_url(url, name=[...])` already does, so this
backfills the field from EVIDENCE rather than assuming it. It never flips `ok` or
`contains_value` and never drops a ref — a `name_found: False` only caps the tier at
`low` downstream, which is the intended "the researcher decides" outcome.

Run BEFORE merge_ref_shards.py / merge_deepsweep_shards.py so the gate sees real data.
Idempotent: verifications that already carry `name_found` are left alone.

Usage:
    python scripts/backfill_name_found.py --staging batches/<scope>/staging/<dir>/ \
        --csv data/GGIT_gas_snapshot_<date>.csv
    python scripts/backfill_name_found.py --staging <dir> --shards rows      # deep-sweep shards
    python scripts/backfill_name_found.py --staging <dir> --shards store     # after a merge:
        the CARRIED ref records (reverified at worklist build, before this field existed)
"""
import argparse, glob, json, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from url_verifier import verify_url  # noqa: E402


_TYPE_SUFFIXES = (" gas pipeline", " oil pipeline", " pipeline system", " pipeline",
                  " system", " project")


def name_variants(pipeline_name, aliases=()):
    """Every name the SOURCE might use for this row, not just the one GEM files it under.

    Three layers, because a name miss is indistinguishable from a relevance failure
    downstream and only one of those is real:
      * the row's own name;
      * the bare stem — GEM names carry a trailing type word sources drop
        ('Valley Crossing Gas Pipeline' -> 'Valley Crossing');
      * `OtherEnglishNames` from the tracker, which is precisely the column that exists
        to record what everyone else calls it. Williams' own page calls P0271 'Transco',
        never 'Transcontinental Gas Pipeline', so without the alias the operator's
        own site reads as a page about some other pipeline.
    """
    out, seen = [], set()
    for raw in [pipeline_name, *(aliases or [])]:
        n = (raw or "").strip()
        if not n:
            continue
        cands = [n]
        low = n.lower()
        for suffix in _TYPE_SUFFIXES:
            if low.endswith(suffix):
                stem = n[: -len(suffix)].strip()
                if len(stem) >= 4:
                    cands.append(stem)
                break
        for c in cands:
            if c.lower() not in seen:
                seen.add(c.lower())
                out.append(c)
    return out


def alias_map(csv_path):
    """{ProjectID: [OtherEnglishNames...]} from a tracker snapshot (header at row 2)."""
    if not csv_path:
        return {}
    import csv as _csv
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as fh:
        rows = list(_csv.reader(fh))
    hdr = rows[2]
    try:
        i_pid = hdr.index("ProjectID")
    except ValueError:
        return {}
    # OtherEnglishNames is split on , ; -- the OtherLanguage* columns are NOT: a Cyrillic or
    # CJK name is one token that routinely contains commas and quotes ('Газопровод
    # "Мастах-Берге", 1-ая нитка'), and a Russian page names the line in Cyrillic, so
    # without these columns every Russian ref reads as "does not name the pipeline"
    # (2026-09-14, Russia R1: 128 units flagged by gate I' on a Latin-only variant list).
    i_alt = hdr.index("OtherEnglishNames") if "OtherEnglishNames" in hdr else None
    i_ol = [hdr.index(c) for c in ("OtherLanguagePrimaryPipelineName", "OtherLanguageSegmentName",
                                   "OtherLanguageAlternativePipelineNames") if c in hdr]
    out = {}
    for r in rows[3:]:
        if len(r) <= i_pid or not r[i_pid].strip():
            continue
        alts = []
        if i_alt is not None and len(r) > i_alt:
            alts += [a.strip() for a in r[i_alt].replace(";", ",").split(",") if a.strip()]
        for i in i_ol:
            if len(r) > i and r[i].strip():
                raw = r[i].strip()
                alts.append(raw)
                # the bare name inside the quotes is what a source prints ('Мастах-Берге')
                for q in ('"', '«'):
                    if q in raw:
                        inner = raw.split(q)[1].split('"')[0].split('»')[0].strip()
                        if len(inner) >= 4:
                            alts.append(inner)
        if alts:
            out[r[i_pid].strip()] = alts
    return out


def units(doc, kind):
    """Every contract, one iterator: the ref-gap shards and the merged store keep units
    in `resolutions[]`, the deep-sweep shards in `fills[]`."""
    return doc.get("fills" if kind == "rows" else "resolutions", []) or []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True)
    ap.add_argument("--shards", default="ref_shards",
                    choices=["ref_shards", "rows", "store"],
                    help="ref_shards/rows = per-PID shards; store = the merged "
                         "staged_resolutions.json, whose CARRIED ref records predate the "
                         "field and are what gate I' flags after a merge")
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    ap.add_argument("--sleep", type=float, default=1.0, help="pause between fetches")
    ap.add_argument("--csv", help="tracker snapshot, to pick up OtherEnglishNames + OtherLanguage* aliases")
    ap.add_argument("--recheck-false", action="store_true",
                    help="ALSO re-evaluate verifications already stamped name_found=false. "
                         "For use when the MATCHER changed, not routinely: a false stamped "
                         "by an older matcher is not evidence (2026-09-15, url_verifier "
                         "learned to romanize Cyrillic pages and to stop requiring a name's "
                         "generic descriptor tail, which no Russian-language page carries). "
                         "A true is never re-checked.")
    args = ap.parse_args()

    S = args.staging.rstrip("/")
    if args.shards == "store":
        paths = [os.path.join(S, "staged_resolutions.json")]
        if not os.path.exists(paths[0]):
            raise SystemExit(f"no staged store at {paths[0]}")
    else:
        paths = [p for p in sorted(glob.glob(os.path.join(S, args.shards, "*.json")))
                 if not os.path.basename(p).startswith("_")]
        if not paths:
            raise SystemExit(f"no shards in {os.path.join(S, args.shards)}")

    aliases = alias_map(args.csv)
    cache, stamped, named, unnamed, skipped, noname = {}, 0, 0, 0, 0, 0
    flipped = 0
    unknown = 0
    for p in paths:
        doc = json.load(open(p))
        nm = doc.get("pipeline_name") or ""
        doc_variants = name_variants(nm, aliases.get(doc.get("project_id") or "", ()))
        changed = False
        for u in units(doc, args.shards):
            variants = doc_variants
            if u.get("pipeline_name"):
                variants = name_variants(u["pipeline_name"],
                                         aliases.get(u.get("project_id") or "", ()))
            for v in u.get("verifications", []) or []:
                recheck = args.recheck_false and v.get("name_found") is False
                if (("name_found" in v and not recheck) or not v.get("ok")):
                    skipped += 1
                    continue
                url = v.get("url") or ""
                if not url or not variants:
                    noname += 1
                    continue
                key = (url, variants[0])
                if key not in cache:
                    try:
                        res = verify_url(url, name=variants)
                        # ONLY a verdict the verifier actually rendered. An absent key means
                        # it could not read the document (unextractable PDF, unreadable
                        # workbook, block page) — that is UNKNOWN, never False. Stamping the
                        # absence as False manufactures "this page does not name the
                        # pipeline" out of a parser failure and caps a good ref at `low`;
                        # it did exactly that to 22 EIA .xlsx refs on 2026-09-04, before
                        # url_verifier could read spreadsheets at all.
                        cache[key] = res["name_found"] if "name_found" in res else None
                        if cache[key] is None:
                            print(f"  UNKNOWN (not stamped) {url}: {res.get('reason')}")
                    except Exception as e:
                        print(f"  WARN {url}: {e}")
                        cache[key] = None
                    time.sleep(args.sleep)
                if cache[key] is None:
                    unknown += 1
                    continue
                if recheck and v.get("name_found") == cache[key]:
                    skipped += 1
                    continue
                if recheck and cache[key]:
                    flipped += 1
                v["name_found"] = cache[key]
                changed = True
                stamped += 1
                named += cache[key]
                unnamed += not cache[key]
        if changed and args.apply:
            json.dump(doc, open(p, "w"), indent=1, ensure_ascii=False)

    verb = "stamped" if args.apply else "would stamp (dry-run)"
    print(f"{verb} name_found on {stamped} verification(s) across {len(paths)} shard(s): "
          f"{named} name the pipeline, {unnamed} do not")
    if flipped:
        print(f"  {flipped} of them were previously stamped name_found=false and the "
              f"page DOES name the pipeline (re-checked under the current matcher)")
    if skipped:
        print(f"  {skipped} already carried the field (or were not ok) — untouched")
    if unknown:
        print(f"  {unknown} verification(s) left UNSTAMPED — the document could not be "
              f"read, which is unknown, not a miss")
    if noname:
        print(f"  WARN {noname} verification(s) had no pipeline_name on the shard to test")
    if not args.apply and stamped:
        print("Re-run with --apply to write, then merge.")


if __name__ == "__main__":
    main()
