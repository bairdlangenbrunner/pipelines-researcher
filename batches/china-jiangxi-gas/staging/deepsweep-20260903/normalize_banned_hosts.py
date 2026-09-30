#!/usr/bin/env python3
"""Strip refs whose host is a banned tertiary aggregator, and re-adjudicate the tier.

WHY THIS EXISTS (jiangxi v3, 2026-09-10)
----------------------------------------
`url_verifier.BLOCKLIST_HOSTS` blocks abarrelfull + theodora.com, so an agent that
runs a URL through the verifier cannot cite those. It does NOT block
`yingdodo.com`, which is 小柱工程 -- a commercial construction-LEADS database. The
page four P4791 records cited (`/html/news/201852592751.html`) is explicitly a
MARKETING SAMPLE: it carries `项目样例1类` and `备注：以下样例非最新项目，仅表示内容
格式`, redacted owner phone numbers, and zero attribution (来源/转载/出处/责任编辑/
数据来源/信息来源 all absent). That is the same source class as abarrelfull -- a
tertiary aggregator republishing someone else's filing without saying whose --
and standing rule 5 bars it outright, "not even alongside corroborating sources."

It reached the agents because it is on GEM'S OWN gem.wiki citation list (present in
`wiki_citations.json` for 27 Jiangxi PIDs under link text `乐平-德兴-婺源支线工程`),
so every future Jiangxi agent is handed it as a seed. Eight other shards opened it
and correctly declined to cite it ("opened, no match"); only P4791 counted it, and
its recovery record even wrote "小柱工程 project-database listing (independent of the
news outlet)" -- naming the site and still scoring it independent.

The value it states is not wrong -- 97 km / 德兴境内9.9 km / DN200 / 6.3 MPa /
投资2亿元 / 开工 2018-06-13 is clearly lifted from a Jiangxi 立项备案 filing. Per rule
5 that makes it a LEAD to chase to the primary record, never a ref. Chasing it is
logged in orchestrator_notes.md; this script only removes the citation.

WHAT IT DOES
------------
For every record in a shard dir: drop banned hosts from `proposed_refs` and the
matching `verifications[]` entry, then RE-ADJUDICATE rather than leaving a stale
tier -- a strip that removes the only corroborating origin makes a `high` claim a
single-source claim, and `independent: true` a falsehood. High/2+ survives only if
2+ refs remain; otherwise tier -> medium and independent -> False. It never touches
`values`/`class_out`: the value is still sourced by what remains, so a REFS_ADDED
stays REFS_ADDED (demoting it to UNRESOLVED would violate rule 4(e) -- something WAS
found). A record left with ZERO refs is NOT silently downgraded; it is reported as
an error for hand adjudication, because that is an orphan `[ref]` (hard requirement)
and only a human should decide whether to re-research or drop the unit.

Every change appends a sentence to `researcher_notes` so the audit trail carries the
reason, not just the smaller ref list.

Dry-run by default; `--apply` writes. Idempotent -- a second run is a 0-change no-op
(the note sentence is keyed and not re-appended). `--dir` because a recovery pass's
output lands in ref_shards_recovery/, which split_shards.py never regenerates, so a
shards/-only glob never reaches it.
"""
import argparse, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent

# Host substrings that may never appear in a `[ref]`. The first two mirror
# url_verifier.BLOCKLIST_HOSTS (standing rule 5); yingdodo is this run's addition,
# and is being reported upstream for BLOCKLIST_HOSTS -- see the docstring.
BANNED = ("yingdodo.com", "yingdodo", "abarrelfull", "abarrellfull", "theodora.com", "wikidot.com")

NOTE_KEY = "[banned-source strip 2026-09-10]"


def is_banned(url):
    u = (url or "").lower()
    return any(b in u for b in BANNED)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    ap.add_argument("--dir", default="shards", metavar="SUBDIR",
                    help="shard subdir to normalize (default shards/). Run again with "
                         "--dir ref_shards_recovery: that dir is outside split_shards.py's "
                         "control, so the shards/ glob never reaches it.")
    a = ap.parse_args()

    changed = errors = 0
    for path in sorted((HERE / a.dir).glob("*.json")):
        doc = json.loads(path.read_text())
        if not isinstance(doc, dict):
            continue
        # Walk EVERY list-of-dicts container, not just `resolutions`. A shard in shards/ or
        # ref_shards*/ keys its records under `resolutions`, but split_shards.py's output in
        # rows/ keys them under `fills` / `validity` / `status_reviews` -- so a
        # `resolutions`-only reader silently reports "0 changes" on rows/ while a banned ref
        # sits in `fills[1]` (exactly what happened on the first run of this script,
        # 2026-09-10). rows/ is regenerated from shards/ by split_shards.py, so a re-split
        # would have cleaned it anyway; a normalizer that quietly no-ops on a whole shape is
        # the defect regardless of whether something downstream happens to cover for it.
        recs = [(k, i, r) for k, v in doc.items() if isinstance(v, list)
                for i, r in enumerate(v) if isinstance(r, dict)]
        dirty = False
        for key, i, r in recs:
            i = f"{key}[{i}]"
            refs = r.get("proposed_refs") or []
            bad = [u for u in refs if is_banned(u)]
            if not bad:
                continue
            kept = [u for u in refs if not is_banned(u)]
            vers = [v for v in (r.get("verifications") or [])
                    if not (isinstance(v, dict) and is_banned(v.get("url")))]

            tier_before, indep_before = r.get("tier"), r.get("independent")
            demoted = ""
            if len(kept) == 0:
                # Orphan [ref] -- never auto-resolve this. Report and leave it alone.
                print(f"  !! ERROR {path.name}#{i} {r.get('ref_col')}: stripping "
                      f"{bad} leaves ZERO refs. Hand-adjudicate (re-research or drop "
                      f"the unit) -- an orphan [ref] is a hard-requirement violation.")
                errors += 1
                continue
            if len(kept) < 2:
                # The strip removed the only corroborating origin: a single-source
                # claim cannot be `high`, and `independent` is now false by arithmetic.
                if r.get("tier") == "high":
                    r["tier"] = "medium"
                    demoted += " tier high->medium (strip leaves a single source)."
                if r.get("independent") is True:
                    r["independent"] = False
                    demoted += " independent true->false."

            r["proposed_refs"] = kept
            if "verifications" in r:
                r["verifications"] = vers
            note = (r.get("researcher_notes") or "").rstrip()
            if NOTE_KEY not in note:
                hosts = ", ".join(sorted({re.sub(r"^www\.", "", (re.match(r"https?://([^/]+)", u) or [None, u])[1]) for u in bad}))
                note += (f" {NOTE_KEY} Dropped {len(bad)} ref(s) on banned tertiary-aggregator "
                         f"host(s) ({hosts}) per standing rule 5. yingdodo.com is 小柱工程, a "
                         f"commercial construction-leads database, and the cited page is an "
                         f"explicit marketing sample (项目样例…以下样例非最新项目，仅表示内容格式) "
                         f"with no attribution -- the abarrelfull/theodora source class, barred "
                         f"even alongside corroborating sources. Its figures are a LEAD to the "
                         f"underlying Jiangxi 立项备案 filing, not a citation.{demoted} "
                         f"Refs remaining: {len(kept)}.")
                r["researcher_notes"] = note.strip()
            print(f"  {path.name}#{i} {r.get('ref_col')}: -{len(bad)} ref "
                  f"({len(refs)}->{len(kept)}), tier {tier_before}->{r.get('tier')}, "
                  f"indep {indep_before}->{r.get('independent')}")
            dirty = True
            changed += 1
        if dirty and a.apply:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")

    verb = "changed" if a.apply else "would change"
    print(f"{verb} {changed} record(s) in {a.dir}/" + (f"; {errors} NEED HAND ADJUDICATION" if errors else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
