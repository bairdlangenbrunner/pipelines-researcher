#!/usr/bin/env python3
"""Downgrade `independent=true` claims that only ONE ref actually earns.

`independent` is the machine-readable form of standing rule 4: two INDEPENDENT
sources that each STATE the value. The gates and the `high` tier read this flag,
so an unearned one silently promotes single-source work.

The criterion is the validator's: a ref counts only if it has a verification
with `ok AND contains_value`. Six records in this sweep claimed the flag on one
such ref. The pattern was identical every time -- the corroborating source
establishes something ADJACENT (the segment exists; it was commissioned in year
X; it sits inside Phase I; it names the line in a plan) while the value itself
appears in exactly one document, and in one case the second source states a
DIFFERENT figure (0.492 vs 0.50). That is real evidence and every ref stays;
it is not double-sourcing.

SECOND CRITERION (added 2026-09-10): two URLs can be verified-and-containing and
still be ONE source. Rule 4 disqualifies "multiple outlets tracing to one
original", so the count that matters is distinct ORIGINS, not distinct URLs.
This sweep leaned heavily on five documents that are one origin -- see
ORIGIN_GROUPS, where the grouping is evidenced from the documents themselves
(rating-report serial numbers, an md5 collision, and CCXI's own declaration that
the issuer is responsible for the facts). 23 records claimed independence on two
or more of those five and nothing else.

What this does NOT do: touch values, tiers, refs, or verifications. Every ref
stays -- a single-origin document is still evidence, and the notes already say
what each source supports. Sentinels are exempt -- they carry a verdict, not a
value, so `contains_value` has no meaning for them.

Order: run with the other normalizers, BEFORE split_shards.py.
"""
import json, pathlib, sys

STAMP = "2026-09-10"
HERE = pathlib.Path(__file__).resolve().parent
SHARDS = HERE / "shards"

# Hand-adjudicated reasons. Anything not listed gets the generic reason below,
# which states the ref/verification breakdown and defers to the record's notes.
REASONS = {
 ("P4779", "Status [ref]"):
   "jdzmc.com names the segment and documents its 2009 commissioning, but does not "
   "assert a CURRENT operating status the way the 2023 DRC plan does (the agent's own "
   "caveat, in this record's notes). Existence corroboration is not value corroboration.",
 ("P5886", "Status [ref]"):
   "Exactly one ref is proposed (the Jiujiang municipal 14th-FYP plan). The GEM "
   "archive.org screenshot is correctly excluded as a GEM surface, so nothing "
   "second-sources 'construction' yet -- second_source_owed stays open for this cell.",
 ("P5886", "Owner [ref]"):
   "Of the three refs, only the SSE bond PDF states the 54/46 structure, and it does "
   "not name this segment (name_found false); the two refs that DO name the branch "
   "(jxgajc.com via Wayback, swj.jiujiang.gov.cn) establish its PHASE I placement, not "
   "its ownership. The ownership rests on one stating source plus a hand-confirmed "
   "identity chain -- which is what this record's tier: medium already says.",
 ("P5886", "Operator [ref]"):
   "Same evidentiary shape as Owner [ref]: one source states the operator, the two "
   "segment-naming sources establish Phase I placement.",
 ("P5866", "Capacity [ref]"):
   "The two segment-naming statutory documents give DIFFERENT figures -- the 2021 env "
   "acceptance's 设计最大供气规模 5亿Nm3/a (= the recorded 0.50) and the 2023 safety "
   "acceptance's 设计输气规模 4.92×10^8Nm3/a (= 0.49). One source states 0.50; the "
   "other states a value that does not round to it, and the record already routes that "
   "discrepancy to a __VALIDITY__ decision. Not two agreeing sources.",
 ("P5866", "Proposal [ref]"):
   "The 2014 provincial DRC utilization plan is the only ref that dates the proposal; "
   "the jxgajc acceptance disclosure names the segment but carries the competing 2016 "
   "permitting milestone, which the record flags for merge rather than merging in.",
}

# ---------------------------------------------------------------------------
# Documents that are ONE origin, and why. Keyed by a substring of the URL.
#
# All four rating reports are 中诚信国际 (CCXI) products on one corporate family
# (江西省投资集团 / 江西省天然气集团), identified by their own serial numbers:
#   CCXI-20250789D-01 (2025, hosted on static.sse.com.cn -- SSE is the HOST, not
#                      the author; this sweep's notes repeatedly miscall it an
#                      "SSE bond tracker" and treat it as a separate publisher)
#   CCXI-20262364M-01 (2026, hosted on chinamoney.com.cn)
#   CCXI-20222923M-01 (2022) and the 2022 跟踪评级报告 (both hosted on qixin.com)
# The 2026 chinamoney PDF is md5-IDENTICAL (a47195d52877446d4f6ccb49f5912a9f) to
# the copy fetched from the other host -- literally the same bytes, so those two
# URLs cannot corroborate each other under any reading.
#
# The 2023 募集说明书 is the ISSUER's own prospectus, a different document class
# and publisher. It is grouped anyway, because the CCXI reports declare that they
# rest on it: "本次评级依据发行人提供或已经正式对外公布的信息...相关信息的合法性、
# 真实性、完整性、准确性由发行人负责" -- CCXI disclaims verification and names the
# issuer as responsible for the facts. A rating report and the prospectus it was
# built from are one origin for a fact about the issuer's own assets, even though
# they are two publishers. This is the softer half of the ruling and is labelled
# as such in the note each record receives, so it can be revisited independently
# of the CCXI-vs-CCXI half.
ORIGIN_GROUPS = {
    "JXIG-SELF-DISCLOSURE": {
        "242696_20250403_SXBW.pdf":                "CCXI-20250789D-01 (2025 rating report)",
        "fileDownLoad.do?contentId=3375767":       "CCXI-20262364M-01 (2026 rating report)",
        "85599868a5a6e3c2fc8db704da8180b8.pdf":    "CCXI-20222923M-01 (2022 rating report)",
        "267eb2e9bb8d0f73972210e2a2241bbb.pdf":    "CCXI 2022 跟踪评级报告",
        "240328_20231123_D5XK.pdf":                "2023 募集说明书 (issuer prospectus)",
    },
    # The 2021-04-05 江西发布 / 江西日报 announcement that West-East Line III had started
    # supplying Ganzhou, republished verbatim by two outlets. Rule 4 excludes "the same
    # wire story republished" in as many words, and this is the textbook case: both
    # carry the identical 「省天然气管网瑞金分输站…依次向会昌、寻乌、安远、定南、龙南、全南、
    # 信丰、大余等8个县（市）供气」 passage. No record in this sweep cites both (P4786 and
    # P4788 use jxnews, P4787 uses thepaper) -- this is here so none ever does and counts
    # them as two. Deliberately NOT including pipechina.com.cn/front/news/1914.html: it is
    # 手机江西台, 2021-03-18, a different outlet on a different date reporting the same
    # event, which is a separate report rather than a republication of this text.
    "JXFB-2021-WEP3-GANZHOU": {
        "tt.jxnews.com.cn/news/1266077":    "江西日报/jxnews 2021-04-05",
        "m.thepaper.cn/baijiahao_12058235": "澎湃/江西发布 2021-04-05 (same text)",
    },
}

ORIGIN_WHY = {
    "JXIG-SELF-DISCLOSURE": (
        "all of them trace to the 江西省投资集团/天然气集团 group's own disclosure: "
        "%s. The rating reports are all 中诚信国际 products (serial numbers on their "
        "title pages), and CCXI's own declaration states the rating rests on "
        "issuer-supplied information whose accuracy is 由发行人负责 -- so the reports "
        "and the prospectus are one origin for a fact about the issuer's own assets, "
        "not a third party corroborating it. Rule 4 excludes sources tracing to one "
        "original. (The CCXI-vs-CCXI half of this is unambiguous; the "
        "rating-report-vs-prospectus half is a judgement call recorded here so it "
        "can be revisited on its own.)"),
    "JXFB-2021-WEP3-GANZHOU": (
        "they are one 江西发布/江西日报 announcement of 2021-04-05, republished verbatim by "
        "two outlets (%s). Rule 4 excludes the same wire story republished, so they are one "
        "source for the Ganzhou South Branch's gas sourcing, not two. Both refs stay -- the "
        "provincial announcement is good evidence, it simply cannot corroborate itself."),
    "WIKIPEDIA-INTERWIKI": (
        "they are language editions of one Wikipedia article (%s). source_roster.md's "
        "Wikipedia section is explicit that two language editions are ONE source, not "
        "two, because the interwiki text is usually a translation -- so they cannot "
        "corroborate each other. Both refs stay: Wikipedia is citable (policy reversed "
        "2026-08-27) and tiers as one secondary source."),
}


def origins(urls):
    """Map URLs to distinct origin ids; same-origin documents collapse to one."""
    out, members = {}, {}
    for u in urls:
        oid = u
        # Wikipedia language editions are ONE source. source_roster.md states this
        # outright under the 2026-08-27 citability reversal -- "Two language editions of
        # the same article are ONE source, not two -- the interwiki text is usually a
        # translation" -- but nothing enforced it, and the P4947 recovery record counted
        # en: and zh: as two independent sources for the 9,102 km system length (its own
        # report said "zh/en Wikipedia both INDEPENDENTLY give the same 9,102 km"). It
        # collapses by host family rather than by article title, which is marginally
        # over-strict for the hypothetical record citing two DIFFERENT wiki articles;
        # that direction is the safe one for an independence flag, and no record in this
        # sweep does it.
        if ".wikipedia.org" in u:
            oid = "WIKIPEDIA-INTERWIKI"
            members.setdefault(oid, set()).add(u.split("/")[-1] or u)
            out.setdefault(oid, []).append(u)
            continue
        for gname, docs in ORIGIN_GROUPS.items():
            for frag, label in docs.items():
                if frag in u:
                    oid = gname
                    members.setdefault(gname, set()).add(label)
                    break
            if oid != u:
                break
        out.setdefault(oid, []).append(u)
    return out, members


GENERIC = ("The corroborating ref(s) name the pipeline but no second ref is verified "
           "as STATING this value (see this record's own notes for what each source "
           "supports), so the two-independent-source claim is not machine-supported.")

# Which of the one-origin documents can carry tier `high` ALONE. The rubric earns
# `high` two ways: "2+ independent sources agree, OR one primary/regulatory source"
# (confidence_tiers.md line 16). So losing independence does not by itself cost a
# record its tier -- but only a PRIMARY filing survives the fall.
#
# The 募集说明书 is the issuer's own prospectus, filed on the exchange under
# disclosure rules: primary for a fact about the issuer's own assets.
# A credit rating report is NOT. It is a third-party analytical product that
# explicitly disclaims verification ("相关信息的合法性、真实性、完整性、准确性由
# 发行人负责"), which is a secondary source's own account of itself -- strong, but
# `medium` per the rubric's "a single strong source (company filing, regulator,
# top-tier trade press)".
PRIMARY_FILING = {"2023 募集说明书 (issuer prospectus)"}

TIER_DEMOTE_WHY = (
    "Tier high -> medium at the same time: `high` requires either two independent "
    "sources (now disproven for this record) or ONE primary/regulatory source, and a "
    "credit rating report is not primary -- CCXI's own declaration makes the issuer "
    "responsible for the facts and disclaims verification. Per confidence_tiers.md "
    "that is 'a single strong source' = medium. The value and all refs are unchanged; "
    "only the two claims the evidence does not support were withdrawn.")

TIER_KEPT_WHY = (
    "Tier high is KEPT even though independence was withdrawn: the rubric earns `high` "
    "on '2+ independent sources agree, OR one primary/regulatory source', and this "
    "record's kept refs include the issuer's own 募集说明书 -- a primary filing made "
    "under exchange disclosure rules, which is primary evidence for a fact about the "
    "issuer's own assets. Single-origin, but primary.")


def main(apply=False, subdir="shards"):
    # `subdir` exists for RECOVERY passes. Their output lands in ref_shards_recovery/,
    # which split_shards.py never regenerates, so the shards/ glob never reaches it and a
    # recovery record citing two of the five same-origin documents would keep a bogus
    # `independent: true`. Run this a second time with --dir ref_shards_recovery. The
    # record shape is identical (a `resolutions` list); only the file set differs.
    changed = 0
    for path in sorted((HERE / subdir).glob("*.json")):
        d = json.loads(path.read_text())
        pid_touched = False
        for i, r in enumerate(d.get("resolutions") or []):
            # Sentinels are exempt: they carry a VERDICT, not a value, so
            # `contains_value` has no meaning for them. The marker is `ref_col`
            # (82 records) -- the `sentinel` field is set on only two, and
            # split_shards.py reads `ref_col or sentinel`, in that order.
            rc = (r.get("ref_col") or r.get("sentinel") or "").strip()
            if not r.get("independent") or rc.startswith("__"):
                continue
            refs = r.get("proposed_refs") or []
            ver = {v.get("url") for v in (r.get("verifications") or [])
                   if v.get("ok") and v.get("contains_value")}
            kept = [u for u in refs if u in ver]
            pid, col = r.get("project_id"), rc
            og, members = origins(kept)
            tier_moved = False
            if len(kept) < 2:
                # Criterion 1: fewer than two verified-and-containing refs.
                why = REASONS.get((pid, col), GENERIC)
                tag = "" if (pid, col) in REASONS else "   [GENERIC reason]"
                print(f"  {path.stem} #{i} {pid} {col}: independent True -> False "
                      f"({len(kept)} of {len(refs)} ref(s) verified-and-containing){tag}")
            elif len(og) < 2:
                # Criterion 2: two or more refs, but they are one ORIGIN.
                gname = next(iter(og))
                docs = "; ".join(sorted(members.get(gname, ())))
                why = ("The %d refs that state this value are not independent of each "
                       "other: %s" % (len(kept), ORIGIN_WHY[gname] % docs))
                # Losing independence costs the `high` tier UNLESS the single
                # surviving origin is itself a primary/regulatory filing.
                if (r.get("tier") or "").lower() == "high":
                    if members.get(gname, set()) & PRIMARY_FILING:
                        why += " " + TIER_KEPT_WHY
                        tmsg = "tier high KEPT (primary filing)"
                    else:
                        r["tier"] = "medium"
                        tier_moved = True
                        why += " " + TIER_DEMOTE_WHY
                        tmsg = "tier high -> medium"
                else:
                    tmsg = f"tier {r.get('tier')} unchanged"
                print(f"  {path.stem} #{i} {pid} {col}: independent True -> False "
                      f"({len(kept)} refs collapse to 1 origin: {gname}); {tmsg}")
            else:
                continue
            r["independent"] = False
            tail = ("Refs kept, value kept." if tier_moved
                    else "Refs kept, tier kept, value kept.")
            note = (r.get("researcher_notes") or "").rstrip()
            r["researcher_notes"] = (
                note + f"\n\n[INDEPENDENCE ADJUDICATED at merge {STAMP}, orchestrator: "
                f"independent true -> false. {why} {tail}]")
            changed += 1
            pid_touched = True
        if apply and pid_touched:
            path.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    print(f"\n{changed} record(s) {'REWRITTEN' if apply else 'would change (dry run)'}")

if __name__ == "__main__":
    argv = sys.argv[1:]
    sub = argv[argv.index("--dir") + 1] if "--dir" in argv else "shards"
    main(apply="--apply" in argv, subdir=sub)
