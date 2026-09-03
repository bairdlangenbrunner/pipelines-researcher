"""Ukraine gas §9 step 4 — redundancy / duplicate adjudication.

Takes the duplicate-flagged validity records raised row-by-row across
ukraine-gas/{ref-sweep-operating,annual,cancelled-review}, the GulfPub + OSM recons
and the source survey, resolves them into structural clusters, and stages one
`__VALIDITY__` record per implicated row. Read-and-flag only; no edits staged.

READ THIS FIRST — Ukraine's method lesson
-----------------------------------------
**Ukraine's duplicates are CARTOGRAPHIC, not bibliographic.** The country has no
line-wise public register, but it has something India and Kazakhstan did not: a dense
Soviet-era engineering record, preserved in the operator's own construction chronology
and reproduced in Ukrainian-language reference works, that names each trunk with its
per-string length, diameter and commissioning year. Where that record can be reached,
it settles a cluster outright. Where it cannot — utg.ua returns HTTP 403 to automated
fetches and web.archive.org was returning 503 across CDX and snapshots on 2026-08-15 —
the honest verdict is UNRESOLVED. **Neither a 403 nor a 503 is evidence a page is gone.**
The archive came back later the same day, which is why cluster A is corrected below: an
`UNRESOLVED` written under an access failure has to be revisited the moment access
returns, not left standing as a finding.

Three structural motifs recur, and only the first is a true double count:

1. **One system entered twice under two spellings of its own name.** Cluster A is the
   type case: «Київ – Західний кордон» is a documented TWO-string system, and GEM carries
   it as both P0777 (1,112.00 km) and P1480 (399.90 km) — two rows for one system.
   **CORRECTED 2026-08-15 (see the cluster-A override below): the per-string figures are
   183.6 km/∅1020 mm/1970 and 216.3 km/∅1220 mm/1972, summing to exactly P1480's 399.90.
   The 367/506 = 873 km pair this leg first credited to the operator's chronology is NOT
   in that document** — it appears in a uk.wikipedia article that cites the chronology
   page, and the chronology itself, saved to this run directory as `utg_chronology.html`
   at 01:31 on the day of the run, contains neither number. So P1480's length is sourced
   and P0777's 1,112.00 km is the one that is not.
2. **Consecutive lines meeting at a shared hub.** Dykanka, Ananiv, Kremenchuk and Kryvyi
   Rih are junctions where genuinely distinct trunks hand off to one another. A shared
   endpoint is a NODE, not shared pipe. This already refuted the P1452/P1453/P1454 flag
   in the leg-1 sweep and it governs cluster F.
3. **Parallel strings in one right-of-way.** Soviet practice was to lay multiple
   independently-operated strings along one corridor for hundreds of km. These are not
   duplicates, and — critically — **they share one drawn geojson**, exactly the
   convention six Kazakh multi-string systems follow. Clusters D and G both have
   byte-identical traces across their rows; in G that is legitimate.

**Identical drawn geometry is therefore NOT evidence of duplication in Ukraine either.**
And the converse trap is worse here than elsewhere: most Ukrainian gas routes are
**2-5 vertex schematics**, so a drawn-vs-stated length gap is usually meaningless. A
schematic bounds the CORRIDOR EXTENT and nothing finer. It is quoted below only where
the gap is so large that even the schematic minimum contradicts the stated value —
P0784, whose 5-vertex trace spans 759 km against a stated 164.00 km. Details and the
full vertex-count table: `route_geometry_findings.md` in this directory.

Pre-fetched source extracts live alongside this script and are cited by the clusters:
`moldovatransgaz_trunks.md`, `kab_achb_evidence.md`, `kzu_evidence.md`,
`ivatsevichy_evidence.md`, `yelets_family_evidence.md`, `route_geometry_findings.md`.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
CSV = "data/GGIT_gas_snapshot_20260812.csv"
OO_CSV = "data/GEM_operators_owners_snapshot_20260812.csv"

# --- sources cited across clusters -------------------------------------------------
WIKI_KZU = ("https://uk.wikipedia.org/wiki/"
            "%D0%9A%D0%B8%D1%97%D0%B2_-_%D0%97%D0%B0%D1%85%D1%96%D0%B4_"
            "%D0%A3%D0%BA%D1%80%D0%B0%D1%97%D0%BD%D0%B8_"
            "%28%D0%B3%D0%B0%D0%B7%D0%BE%D1%82%D1%80%D0%B0%D0%BD%D1%81%D0%BF%D0%BE"
            "%D1%80%D1%82%D0%BD%D0%B0_%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0%29")
WIKI_KAB = ("https://uk.wikipedia.org/wiki/"
            "%D0%9A%D1%80%D0%B5%D0%BC%D0%B5%D0%BD%D1%87%D1%83%D0%BA_%E2%80%93_"
            "%D0%90%D0%BD%D0%B0%D0%BD%D1%8C%D1%97%D0%B2_%E2%80%93_"
            "%D0%91%D0%BE%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D1%87%D0%B0%D0%BD%D0%B8")
WIKI_EKD = ("https://uk.wikipedia.org/wiki/"
            "%D0%84%D0%BB%D0%B5%D1%86%D1%8C_-_%D0%9A%D1%83%D1%80%D1%81%D1%8C%D0%BA_"
            "%E2%80%93_%D0%94%D0%B8%D0%BA%D0%B0%D0%BD%D1%8C%D0%BA%D0%B0")
WIKI_BRAT = ("https://uk.wikipedia.org/wiki/"
             "%D0%91%D1%80%D0%B0%D1%82%D1%81%D1%82%D0%B2%D0%BE_"
             "%28%D1%81%D0%B8%D1%81%D1%82%D0%B5%D0%BC%D0%B0_"
             "%D0%B3%D0%B0%D0%B7%D0%BE%D0%BF%D1%80%D0%BE%D0%B2%D0%BE%D0%B4%D1%96%D0%B2%29")
MTG_TRUNKS = ("https://moldovatransgaz.md/ru/content/magistralnye-gazoprovody-dlya-"
              "peredachi-prirodnogo-gaza-po-territorii-respubliki-moldova")

# --- how the clusters are assembled ------------------------------------------------
# Unlike Kazakhstan's build script, the cluster bodies are NOT transcribed into this
# file by hand: each adjudicating subagent wrote `./clusters/<id>.json` and this script
# reads them, so the recommendation and notes prose reaches the workbook verbatim with
# no transcription drift. What stays hand-curated here is (a) the ref allow-list, since
# every URL has to clear `url_verifier` before it can be staged, and (b) OVERRIDES,
# where main-loop research corrected or extended an agent's reading.
CLUSTER_DIR = OUT / "clusters"

# URLs an agent proposed that this pass will NOT stage, with the reason. Blocked URLs
# are dropped from `proposed_refs`; the prose that cites them is left untouched, because
# an unreachable page is not a disproven one.
REF_BLOCKLIST = {
    "https://moldovatransgaz.md/ru/content/magistralnye-gazoprovody-dlya-peredachi-"
    "prirodnogo-gaza-po-territorii-respubliki-moldova":
        "SSLError + ConnectionError on 2026-08-15, both with and without cert "
        "verification; the same content verifies 200 at the mtg.md mirror, which is "
        "staged instead",
    "https://tsoua.com/pro-nas/novyny-dlya-spivrobitnykiv/davajte-znovu-poznajomymosya-"
    "bogorodchanske-lvumg/": "HTTP 403 (operator WAF) — cited in prose as a lead, not "
                             "staged as a ref; a 403 is not evidence the page is gone",
    "https://utg.ua/utg/about-company/history/xronologya-storichnogo-rozvitku.html":
        "HTTP 403 (operator WAF) — same; the Ukrtransgaz chronology is the source that "
        "would settle clusters A and C and it could not be read in this pass",
}

_A_NOTE_CORRECTION = (
    "MAIN-LOOP CORRECTION 2026-08-15, after this cluster was first adjudicated: the "
    "operator's chronology became readable through Wayback "
    "(web.archive.org/web/20250615033715/https://utg.ua/utg/about-company/history/"
    "xronologya-storichnogo-rozvitku.html) and it does NOT say what this cluster reported. "
    "Its «Київ – Західний кордон України» entries are: 1970, I нитка, 183,6 км, ∅1020 мм; "
    "1972, II нитка, 216,3 км, ∅1220 мм; 1973, a «ІІ черга» second construction stage with "
    "no length given, commissioned alongside Шебелинка–Диканька–Київ; and 1974, a further "
    "42,8 км, ∅1200 мм. The strings 367 and 506 do not occur anywhere in the document. "
    "They come from a uk.wikipedia article that CITES the chronology page, and this leg "
    "credited them to the operator on that article's word — the chronology itself was "
    "already saved into this run directory as utg_chronology.html and would have refuted "
    "it. WITHDRAWN: 'the only verifiable figures are 367 + 506 = 873 km' and 'neither GEM "
    "length is supported'. STANDS: the duplicate verdict itself, and the Drozdovychi "
    "endpoint finding. WHAT CHANGES: P1480's 399.90 km is now the SOURCED length — "
    "183.6 + 216.3 = 399.90 exactly, and the row's own Diameter cell already reads "
    "'1020, 1220', the two strings' diameters — so the surviving row of the fold should "
    "carry 399.90 km, not a figure to be researched. P0777's 1,112.00 km stays unsourced "
    "(its VTG citation is a genuine 404). Two caveats a human still owns: 399.90 counts "
    "the two strings AS COMMISSIONED, so the undocumented 1973 second stage and the 1974 "
    "42.8 km addition are on top of it, and the chronology describes the 1970 build as the "
    "first stage of the CONTINUATION of the separate Єфремівка–Долина–Київ trunk, which is "
    "the most likely origin of P0777's much larger number."
)

# Main-loop corrections to a cluster's own adjudication. `rows` entries here REPLACE the
# agent's tuple for that ProjectID; `extra_notes` is appended to the cluster note.
OVERRIDES: dict[str, dict] = {
    "A": {
        "title": ("Cluster A — Kyiv–Western Border (P0777 vs P1480): DUPLICATE CONFIRMED, "
                  "one system (КЗУ); length RESOLVED to P1480's 399.90 km on the operator's "
                  "own chronology"),
        "extra_notes": _A_NOTE_CORRECTION,
        "extra_refs": [
            "https://web.archive.org/web/20250615033715/https://utg.ua/utg/"
            "about-company/history/xronologya-storichnogo-rozvitku.html",
        ],
        "rows": {
            "P0777": (
                "duplicate",
                "Fold into ONE surviving GEM row for the Kyiv–Western Border of Ukraine "
                "system (КЗУ), and do NOT carry P0777's 1,112.00 km / 522+590 km figures "
                "onto it. Those rest on VTG (vtg.com.ua/experience/main/gts.html), which is "
                "a genuine 404 ('Сторінку не знайдено', confirmed live) — so they are "
                "unsourced, not merely unverified. The operator's own construction "
                "chronology, read through Wayback after this cluster was first adjudicated, "
                "gives the system as 183.6 km (1970, ∅1020) + 216.3 km (1972, ∅1220) = "
                "399.90 km, which is exactly what P1480 already carries; use P1480's value "
                "on the surviving row whichever PID survives. P0777's diameters "
                "(1020/1220 mm) and StartYear1 (1970) are corroborated and can be kept. "
                "One thing for the human to decide rather than assume: the chronology calls "
                "the 1970 build the first stage of the CONTINUATION of the separate "
                "Yefremivka–Dolyna–Kyiv trunk, so 1,112 km may be a conflation of KЗУ with "
                "that upstream trunk rather than a simple error — if so the fix is a scope "
                "statement in ResearcherNotes, not just a smaller number.",
                "[main-loop correction 2026-08-15] This row's verdict is unchanged — it is "
                "the same system as P1480 — but the reasoning that 'neither length is "
                "supported' is withdrawn. P1480's is supported; P0777's is not. See the "
                "cluster note for the primary-source reading.",
                "escalate",
            ),
            "P1480": (
                "duplicate",
                "Fold into the same single surviving row as P0777, and carry P1480's "
                "LengthKnownKm = 399.90 forward — it is the sourced value, not a candidate "
                "for replacement. The operator's construction chronology (Wayback "
                "20250615033715 of utg.ua's «Хронологія сторічного розвитку»; the live "
                "origin 403s behind the operator WAF, which is a block and not a deletion) "
                "records «Київ – Західний кордон України (І нитка) довжиною 183,6 км, "
                "∅1020 мм» in 1970 and «(II нитка) довжиною 216,3 км, ∅1220 мм» in 1972 — "
                "summing to 399.90 km and matching the row's own Diameter cell '1020, 1220'. "
                "The competing 367 + 506 = 873 km pair is WITHDRAWN: it is a uk.wikipedia "
                "figure attributed to this same chronology page, and the page does not "
                "contain either number. Stage the Wayback snapshot as `Length [ref]`, which "
                "is filled on only one of Ukraine's 47 rows today. Two caveats to record in "
                "ResearcherNotes rather than silently absorb: 399.90 is the AS-COMMISSIONED "
                "two-string total, so the chronology's undated 1973 «ІІ черга» stage and its "
                "1974 42.8 km ∅1200 mm addition sit on top of it; and P1480's gem.wiki "
                "route narrative places the endpoint at 'Drozdovychi, Ukraine/Poland border', "
                "which remains UNCORROBORATED and is almost certainly a conflation with the "
                "separate Komarno–Drozdovychi corridor (GEM's own P0778) or with the "
                "post-2006 Poland interconnection project. P1480's sheet EndLocation is "
                "blank, so that is a caveat for whoever sets EndLocation on the surviving "
                "row, not a live sheet error today.",
                "[main-loop correction 2026-08-15] Upgraded from 'combined length "
                "unresolved' to RESOLVED on the primary source. The drawn route's 561 km "
                "span still exceeds the stated 399.90, but Ukrainian routes are 2-5 vertex "
                "schematics and P1480's own trace bends toward the Polish border rather "
                "than Uzhhorod — that is evidence about the DRAWING (and circumstantial "
                "support for how the Drozdovychi label crept in), not against a length that "
                "the operator's construction record states to two decimals.",
                "escalate",
            ),
        },
    },
}

# Standing rule 1: GEM's own surfaces are READ for identity (a gem.wiki title carrying the
# «КЗУ» acronym is how cluster A knows GEM already identifies that row as the historical
# system) but are NEVER staged as a ref. `url_verifier` rejects them too; this is the
# belt-and-braces filter so a GEM URL cannot reach `proposed_refs` even if that changed.
BANNED_HOSTS = ("gem.wiki", "globalenergymonitor.org", "abarrelfull.wikidot.com",
                "abarrelfull.co.uk", "wikidot.com", "theodora.com")


def _banned(url: str) -> bool:
    return any(h in url for h in BANNED_HOSTS)


def _clean_url(url: str) -> str:
    """Strip MediaWiki fetch artifacts an agent left on the URL it reported.

    Cluster F reported both of its uk.wikipedia sources with `&action=raw` still
    attached — the form it used to pull wikitext, not a readable page. Those 404 in
    `url_verifier`, which would have dropped two live, load-bearing articles as dead
    links. Strip the artifact and verify the real page instead; if the page is
    genuinely gone the verifier still catches it.
    """
    u = url.strip()
    for suffix in ("&action=raw", "?action=raw", "&action=edit", "&printable=yes"):
        if u.endswith(suffix):
            u = u[: -len(suffix)]
    return u


def _pid(key: str) -> str:
    """Rows appearing in more than one cluster carry a `_suffix` to keep keys unique."""
    return key.split("_")[0]


_VERIFY_CACHE = OUT / "url_verifications.json"


def _verify(url: str) -> dict:
    """`url_verifier` every candidate ref, cached to disk so re-runs are cheap.

    Hard requirement: every URL clears the verifier before it goes in the xlsx, even one
    that worked in a prior batch. A failure here drops the URL from `proposed_refs` and
    is recorded in `refs_dropped` with its reason — it never silently disappears, and the
    prose that cites it is left alone (a 403 or an SSL failure is not a deletion).
    """
    cache = json.loads(_VERIFY_CACHE.read_text()) if _VERIFY_CACHE.exists() else {}
    if url not in cache:
        import sys
        sys.path.insert(0, str(REPO / "scripts"))
        from url_verifier import verify_url
        r = verify_url(url)
        cache[url] = {"ok": bool(r.get("ok")), "status": r.get("status"),
                      "reason": r.get("reason") or r.get("note") or ""}
        _VERIFY_CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False))
    return cache[url]


def _tally(vals) -> dict[str, int]:
    d: dict[str, int] = {}
    for v in vals:
        d[v] = d.get(v, 0) + 1
    return d


def load_clusters() -> dict[str, dict]:
    """Read ./clusters/*.json into the CLUSTERS shape `main()` consumes."""
    out: dict[str, dict] = {}
    for path in sorted(CLUSTER_DIR.glob("*.json")):
        d = json.loads(path.read_text())
        cid = d["cluster_id"]
        refs, dropped = [], []
        for s in d.get("sources", []):
            u = _clean_url(s.get("url") or "")
            if not u or u in refs or any(u == x for x, _ in dropped):
                continue
            if _banned(u):
                dropped.append((u, "GEM or banned source — standing rules 1 and 5"))
            elif u in REF_BLOCKLIST:
                dropped.append((u, REF_BLOCKLIST[u]))
            else:
                res = _verify(u)
                if res.get("ok"):
                    refs.append(u)
                else:
                    dropped.append((u, f"url_verifier: status={res.get('status')} "
                                       f"{res.get('reason') or ''}".strip()))
        rows = {}
        for r in d.get("rows", []):
            ctype = r.get("concern_type") or "none"
            # `severity` is optional in the agents' schema and cluster F omitted it.
            # Default it from the concern rather than to "info": a row carrying a real
            # concern_type is at minimum a flag, and only a cleared row is info.
            sev = r.get("severity") or ("info" if ctype == "none" else "flag")
            rows[r["project_id"]] = (
                ctype,
                r.get("recommendation", ""),
                r.get("notes", ""),
                sev,
            )
        cl = {
            "title": d.get("title", ""),
            "verdict": d.get("verdict", "UNRESOLVED"),
            "summary": d.get("summary", ""),
            "open_questions": d.get("open_questions", []),
            "refs": refs,
            "refs_dropped": dropped,
            "rows": rows,
        }
        ov = OVERRIDES.get(cid)
        if ov:
            # `extra_refs` exists because a cluster's live source can 403 (utg.ua does)
            # and the Wayback snapshot that DOES read is a different URL the adjudicating
            # agent never had. It goes through the same verifier as any other ref.
            for u in ov.get("extra_refs", []):
                if u in refs or _banned(u):
                    continue
                res = _verify(u)
                if res.get("ok"):
                    refs.append(u)
                else:
                    dropped.append((u, f"url_verifier: status={res.get('status')} "
                                       f"{res.get('reason') or ''}".strip()))
            cl["refs"] = refs
            cl["rows"].update(ov.get("rows", {}))
            if ov.get("title"):
                cl["title"] = ov["title"]
            if ov.get("verdict"):
                cl["verdict"] = ov["verdict"]
            if ov.get("extra_notes"):
                cl["summary"] = (cl["summary"] + " " + ov["extra_notes"]).strip()
        out[cid] = cl
    return out


def main() -> None:
    gas = pd.read_csv(REPO / CSV, header=2, low_memory=False,
                      keep_default_na=False, na_values=[])
    gas["_sheet_row"] = gas.index + 4
    by_pid = {r["ProjectID"]: r for _, r in gas.iterrows()}

    CLUSTERS = load_clusters()
    resolutions = []
    for key, cl in CLUSTERS.items():
        for rowkey, (ctype, rec, notes, severity) in cl["rows"].items():
            p = _pid(rowkey)
            row = by_pid.get(p)
            if row is None:
                raise SystemExit(f"{p} not found in {CSV} — snapshot drift, re-check")
            resolutions.append({
                "project_id": p,
                "sheet_row": int(row["_sheet_row"]),
                "pipeline_name": str(row.get("PipelineName") or ""),
                "segment_name": str(row.get("SegmentName") or ""),
                "ref_col": "__VALIDITY__",
                "value_cols": [],
                "primary_value_col": "",
                "primary_value": "",
                "values": {},
                "current_ref": "",
                "class_in": "VALIDITY",
                # A row the cluster examined and CLEARED carries concern_type "none";
                # `staged_store` drops those from the concerns pile but still records the
                # PID as audited, which is the point — the next sweep should see that the
                # question was asked and answered, not re-raise it.
                "class_out": "CONFIRMED" if ctype == "none" else "UNRESOLVED",
                "verdict": "confirmed" if ctype == "none" else "concern",
                "concern_type": ctype,
                "severity": severity,
                "recommendation": rec,
                "proposed_refs": cl.get("refs", []),
                "verifications": [],
                "tier": "n/a",
                "independent": False,
                "source_language": "uk",
                "wiki": str(row.get("Wiki") or ""),
                "redundancy_cluster": key,
                "redundancy_cluster_title": cl["title"],
                "redundancy_verdict": cl["verdict"],
                "researcher_notes": (f"[cluster {key} — {cl['verdict']}: {cl['title']}] "
                                     f"{notes}"),
            })

    ctypes: dict[str, int] = {}
    sev: dict[str, int] = {}
    for r in resolutions:
        ctypes[r["concern_type"]] = ctypes.get(r["concern_type"], 0) + 1
        sev[r["severity"]] = sev.get(r["severity"], 0) + 1

    out = {
        "meta": {
            "commodity": "gas",
            "mode": "redundancy",
            "scope": {
                "csv": Path(CSV).name,
                "oo_csv": Path(OO_CSV).name,
                "country": "Ukraine",
                "rows": len({r["project_id"] for r in resolutions}),
                "clusters": len(CLUSTERS),
            },
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "n_units": len(resolutions),
            "n_validity_flags": len(resolutions),
            "n_fills": 0,
            "n_status_reviews": 0,
            "n_route_suggestions": 0,
            "class_in_counts": {"VALIDITY": len(resolutions)},
            "class_out_counts": _tally(r["class_out"] for r in resolutions),
            "verdict_counts": _tally(r["verdict"] for r in resolutions),
            "concern_counts": ctypes,
            "severity_counts": sev,
            "cluster_titles": {k: v["title"] for k, v in CLUSTERS.items()},
            "cluster_verdicts": {k: v["verdict"] for k, v in CLUSTERS.items()},
            "verdict_tally": _tally(v["verdict"] for v in CLUSTERS.values()),
            "refs_dropped": {k: v["refs_dropped"] for k, v in CLUSTERS.items()
                             if v["refs_dropped"]},
            "open_questions": {k: v["open_questions"] for k, v in CLUSTERS.items()
                               if v["open_questions"]},
            "note": NOTE,
        },
        "resolutions": resolutions,
    }
    (OUT / "staged_resolutions.json").write_text(json.dumps(out, indent=1))
    print(f"wrote {len(resolutions)} validity records across {len(CLUSTERS)} clusters")
    for k, v in CLUSTERS.items():
        print(f"  {k}: {len(v['rows'])} row(s) — {v['title']}")
    print(f"  concern types: {ctypes}")
    print(f"  severity:      {sev}")


NOTE = (
    "Cluster-level adjudication of duplicate/overlap questions raised row-by-row by "
    "ukraine-gas/{ref-sweep-operating,annual,cancelled-review}, the GulfPub + OSM recons and "
    "the source survey. Read-and-flag only; no edits staged. READ THIS FIRST — TWO geometry "
    "rules govern Ukraine and they pull in opposite directions. (1) Most Ukrainian gas routes "
    "are 2-5 vertex SCHEMATICS, so a drawn span is a LOWER BOUND on corridor extent: a "
    "drawn-vs-stated gap proves nothing unless the drawn span EXCEEDS the stated length by a "
    "wide margin (it does in exactly two places — P0784, 759.1 km drawn against 164.00 km "
    "stated, and P1481, whose 333.00 km cannot span an Ananiv-Bohorodchany corridor that is "
    "~424 km great-circle). (2) IDENTICAL DRAWN GEOMETRY IS NOT EVIDENCE OF DUPLICATION — "
    "parallel Soviet strings share one right-of-way trace, the same convention Kazakhstan "
    "carries. THREE of the eight clusters REFUTE a duplicate hypothesis (F, G, H), recorded "
    "deliberately so the next sweep does not re-raise them; two CONFIRM one (A, E) and two are "
    "PARTIAL_OVERLAP (B, D). Ukraine's own method lesson is that ONLY SOURCING DECIDES: cluster "
    "G looked like a textbook double count (two rows, one corridor, both 292.00 km, both 29.00 "
    "bcm/y) and the duplicate is still REFUTED, because UTG's chronology names 'Ivatsevychi-"
    "Dolyna (I nytka)' 1976 at 357.7 km and '(II nytka)' 1977 at 366.7 km as two physically "
    "distinct 1220 mm strings — while simultaneously falsifying BOTH of GEM's numbers, since "
    "292.00 km matches neither string and 29.00 bcm/y is the SYSTEM total restated twice "
    "(GEM's own note says so; ISANS 2023 puts the corridor near 30). A refuted duplicate is "
    "therefore not a clean row. The country's two cross-cutting defects, both escalated: "
    "GAZPROM ATTRIBUTED OWNERSHIP OF UKRAINIAN PIPE (P1485, P0783, P0775 at 48.6%, P0776 at "
    "'Gazprom 100%' beside a second co-owner) — Gazprom owns no Ukrainian section, the "
    "post-2019 unbundling put the GTS under GTSOU; and SYSTEM/AGGREGATE CAPACITY RESTATED AS A "
    "LINE'S OWN (P0784's 24.00 bcm/y is verbatim an aggregate over three threads that "
    "double-counts capacity P0786 already carries; both G rows at 29.00), the same shape India "
    "and Kazakhstan carry. ON THE OWNERSHIP DEFECT, READ THE NARROW VERSION, NOT THE BROAD "
    "ONE: a full-tab count run 2026-08-15 puts Gazprom in `Owner` on 20 of the 47 rows, and "
    "for 14 of them the unweighted pair 'Gazprom PJSC; Gas Transmission System Operator of "
    "Ukraine' on a genuinely transnational Russia+Ukraine row is the DEFENSIBLE convention, "
    "not a defect — so the earlier reading that P0783 is an instance is WITHDRAWN. What "
    "survives is two narrow classes. (i) A percentage of [100.%] recorded alongside a second "
    "named owner, which is arithmetically impossible and is NOT Gazprom-specific — P0768 and "
    "P0776 put Gazprom at 100% beside GTSOU, and P0761 puts GTSOU at 100% beside Gazprom AND "
    "QazaqGaz. That is a notation question for a human: if [100.%] is meant as '100% of the "
    "section in that party's own country' the convention needs stating, and if it is meant as "
    "a share of the whole line all three cells are wrong. (ii) A sole non-Ukrainian owner on "
    "a row that lists Ukraine — P0791 (Gazprom; QazaqGaz), P0793, P1471, P2387 and P1485 "
    "(all Gazprom PJSC [100.%]), plus P5935 (Moldovatransgaz [100.%]). P1485 is the "
    "unambiguous one, because its CountriesOrAreas is Ukraine ALONE. Separately P1487 still "
    "names Ukrtransgaz, the pre-2020 entity. Cluster A confirms P0777 and P1480 are one "
    "system — the Soviet KZU, a documented two-string build — and it is ALSO this pass's "
    "own correction, so read the corrected version: the operator's construction chronology "
    "became readable through Wayback after the cluster was first adjudicated and gives the "
    "two strings as 183.6 km/∅1020 mm (1970) and 216.3 km/∅1220 mm (1972), summing to "
    "exactly P1480's 399.90 km. The 367 + 506 = 873 km pair this leg first called 'the only "
    "verifiable figures' is WITHDRAWN — it is a uk.wikipedia figure attributed to that same "
    "chronology page, which contains neither number, and the page was already saved into "
    "the run directory when the cluster was written. So P1480's length is SOURCED and "
    "should be carried onto the surviving row; P0777's 1,112.00 km is the unsourced one "
    "(its VTG citation is a genuine 404), and may be a conflation with the upstream "
    "Yefremivka-Dolyna-Kyiv trunk that the chronology says KZU continues. Unchanged: "
    "P1480's Drozdovychi endpoint is anachronistic (it belongs to the older Komarno-"
    "Drozdovychi corridor and the post-2006 Poland interconnection, not to the 1970s KZU). "
    "The method lesson is narrow and worth carrying: an UNRESOLVED written while a source "
    "was unreachable must be revisited when access returns — and a figure a secondary "
    "article attributes to a primary document is not that document's figure until the "
    "document says it. "
    "Cluster E is confirmed at MEDIUM only: P5989 minus P7817+P7818 leaves 99.30 km against a "
    "reported '>100 km' new Berdyansk-Melitopol section, but every source is Russian state or "
    "occupation media tracing to one July 2022 directive, so the arithmetic is stronger than "
    "the sourcing. Cluster C stays UNRESOLVED because no source says whether ACHB is P1485's "
    "western half or a separate parallel string. TWO OPEN QUESTIONS THAT NEED A HUMAN: the "
    "Ivatsevychi corridor may be a THREE-string system — this pass's own evidence file describes "
    "Torzhok-Ivatsevychi-Dolyna with three strings while cluster G sourced Ivatsevychi-Dolyna "
    "with two, which are different corridors, so whether GEM is missing a string is still open "
    "and belongs to Discovery, not here; and P0775/P0776's 298.00/297.00 km near-coincidence is "
    "unexplained even though the duplicate is refuted (Gazprom's own 65 vs 45 Mm3/day table "
    "converts to 23.725/16.425 bcm/y, matching GEM almost exactly, which makes it GEM's likely "
    "ORIGIN rather than corroboration). Three load-bearing sources could not be read in this "
    "pass and are NOT deletions: utg.ua's chronology and tsoua.com both 403 behind the "
    "operator's WAF, and moldovatransgaz.md fails TLS (its mtg.md mirror is staged instead) — "
    "the UTG chronology is the source that would settle clusters A and C."
)


if __name__ == "__main__":
    main()
