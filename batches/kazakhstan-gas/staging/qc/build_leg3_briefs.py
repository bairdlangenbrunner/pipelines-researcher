#!/usr/bin/env python3
"""SUPERSEDED 2026-09-03 by scripts/build_leg3_briefs.py (generic --staging/--groups
emitter, same brief shape; this GROUPS table still loads via `--groups <this file>`).
Kept for the run record only.

Split the Leg-3 worklist into ten system briefs for the research fan-out.

    python batches/kazakhstan-gas/staging/qc/build_leg3_briefs.py

`build_qc_staging.py` emits `worklist.json` — 42 rows, 101 flags — as a flat list, but
in Kazakhstan the flags collapse into three questions plus a handful of singletons, and
all three are *system*-shaped rather than row-shaped:

  * **`Operator` blank while gem.wiki names one (21 rows).** One question per COMPANY,
    not per row: whoever operates the Bukhara-Ural trunk operates all of its strings.
    Unlike the per-string SPEC questions below this one is genuinely answerable —
    QazaqGaz's Integrated Annual Report 2024 lists 25 Intergas Central Asia lines by
    name, which is exactly an operatorship statement even though it carries no specs.
  * **Multi-segment wiki union (Diameter 21, Owner 16, Parent 16, Operator 6).** The
    gem.wiki page covers the WHOLE multi-string system while the GEM row is ONE string,
    so the "union" the flag reports is the system's set of values. That is the same
    shape as the escalation this pass raised (system-level figures restated on every
    string) and usually is NOT a per-row defect — decide, once per system, whether the
    row should carry the system's set or its own value, and say which.
  * **`length_ratio` (10 rows).** GEM's own drawn route disagrees with `LengthKnownKm`
    by more than ±33%, scattering BOTH ways (7 under, 3 over) — so it is not one
    systematic conversion defect. Two of them (P2292 2,600 km, P5770 3,700 km) are
    almost certainly whole-system Central Asia-Center lengths on a Kazakh-portion route.
  * Singletons: three transnational endpoint-country flags, one landfall-country flag
    (P6834), P5927's missing `StartYear1`, and P7819's blank Capacity/Diameter.

Rows that share a source ladder are briefed TOGETHER — one agent's find on a trunk
system answers every string in it. Each brief carries its rows' flags verbatim plus the
current sheet values, so the agent answers a specific question rather than re-deriving
the flag.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BRIEFS = OUT / "rows" / "_briefs"
CSV = ROOT / "data" / "GGIT_gas_snapshot_20260811.csv"

# key -> (title, source-ladder hint, [PIDs])
GROUPS: list[tuple[str, str, str, list[str]]] = [
    (
        "central-asia-center",
        "Central Asia-Center (CAC-2/3/4/5)",
        "The corridor carrying Turkmen and Uzbek gas north across western Kazakhstan to "
        "Russia. The redundancy leg already staged the finding that 60.20 bcm/y is "
        "restated on P2291/P5770/P5771 while P2292 reads 5.00 — do NOT re-litigate that; "
        "it is cluster B. Your questions are the blank Operator (one answer for the whole "
        "system) and the two length ratios: P2292's 2,600 km and P5770's 3,700 km both "
        "look like WHOLE-SYSTEM lengths (KMG AR2019/2020 put CAC at 5,306 km, AR2021 at "
        "4,149.2 km) sitting on a route drawn for the Kazakh portion only — establish "
        "what each length counts rather than 'fixing' it to the route. P2292 also has an "
        "endpoint flag: its route's FIRST endpoint lands in Kazakhstan, which is neither "
        "its start nor its end country — for a transit line that may be a correctly-drawn "
        "partial route. Ladder: QazaqGaz Integrated Annual Report 2024 (operatorship), "
        "Intergas Central Asia (intergas.kz) network material, KMG Annual Report "
        "'Gas Transportation and Marketing' table (system aggregates only, and remember "
        "AR2020 and AR2021 are ONE origin), Order of the Minister of Energy No.350 "
        "(adilet.zan.kz/rus/docs/G23JVM00350).",
        ["P2291", "P2292", "P5770", "P5771"],
    ),
    (
        "bukhara-ural",
        "Bukhara-Ural (I, II) and the CS 14-Aktobe strings",
        "The northbound trunk from Uzbekistan through Aktobe to the Urals, plus three "
        "rows for a CS14-Aktobe loop. Cluster F is the live problem and is NOT yours to "
        "close by fiat: P5927 and P5928 are byte-identical on every attribute (158.00 km, "
        "530 mm, 1.96 bcm/y, blank StartYear1, same trace) while P5696 is filed as "
        "'CS 14-Aktobe III' under construction. Anything you find that distinguishes them "
        "— a commissioning year, a diameter, a separate string — is the single most "
        "valuable result in this packet. P5927's missing StartYear1 is flagged separately "
        "and is the same question. Do not re-open the staged finding that P5695's "
        "2,382 km is KMG AR2019/2020's whole-system length (cluster D). Ladder: QazaqGaz "
        "IGO 2024, Intergas Central Asia asset material, Aktobe regional development "
        "programmes and akimat news, KMG AR2021, Order No.350.",
        ["P2289", "P5695", "P5696", "P5927", "P5928"],
    ),
    (
        "bukhara-tashkent-bishkek-almaty",
        "Bukhara-Tashkent-Bishkek-Almaty (BTBA I and II)",
        "A four-country trunk whose GEM rows carry the system's whole multi-country "
        "value set — Operator 'Uztransgas; Intergas Central Asia; Gazprom Kyrgyzstan', "
        "and the same 1,585.00 km on BOTH strings against a 1,270.28 km drawn corridor "
        "(cluster E, already staged: the strings are real, the shared length is the "
        "defect). Your questions are the multi-segment unions — whether a single GEM row "
        "should carry three countries' operators at once, or only the Kazakh section's — "
        "and P5810's endpoint flag (route's LAST endpoint in Kazakhstan while the sheet "
        "says the line ends elsewhere; for a partial route that may be correct). Ladder: "
        "QazaqGaz IGO 2024, Uztransgaz and Gazprom Kyrgyzstan disclosures, Intergas "
        "Central Asia, Kyrgyz and Uzbek ministry material.",
        ["P0739", "P5810"],
    ),
    (
        "central-asia-china",
        "Central Asia-China Lines A / B / C",
        "The redundancy leg REFUTED the triple-count hypothesis here and CORROBORATED "
        "the sheet: 15 + 15 + 25 = 55 bcm/y is exactly the figure Order No.350 paragraph "
        "44 states. Do not re-open it. What remains is (a) the blank Operator on P1124 "
        "and the union flags on all three — this is a genuinely multi-party system "
        "(PipeChina / Turkmengaz / Uzbekneftegaz / KazTransGas-China JV) so name the "
        "entity that operates the KAZAKH section and say so; and (b) the open question "
        "logged in the country note: all three rows carry 1,833 km, while KMG AR2021 puts "
        "the system at 3,916 km and Order No.350 gives the Kazakh portion as 'do 1300 km'. "
        "Establish what 1,833 refers to — it is probably Turkmen-border-to-Khorgos across "
        "Uzbekistan and Kazakhstan, but that needs a source, not an inference. Ladder: "
        "Order No.350 (adilet), QazaqGaz IGO 2024, Asia Gas Pipeline LLP / KazTransGas-"
        "China material, CNPC and PipeChina disclosures, Chinese-language sources.",
        ["P1124", "P2299", "P2300"],
    ),
    (
        "uzen-zhetybay-aktau",
        "Zhanaozen(Uzen)-Zhetybay-Aktau: the Mangistau corridor",
        "This corridor's redundancy question is CLOSED and must not be re-opened — read "
        "notes/escalation-2026-08-11-kazakhstan-system-level-values-on-strings.md if you "
        "are tempted. Settled: P3948 is the aggregate of P5776 + P5777 + P5783 (a "
        "confirmed ~149 km double count, to be folded); 4.54 bcm/y is Intergas's figure "
        "for the three strings TOGETHER; P5789 (thread IV) is real and under "
        "construction; its byte-identical route copy is legitimate. Your ONLY question is "
        "Diameter — five rows carry the same union off the multi-segment wiki page and "
        "P5789's is blank. Per-string diameters are the kind of number Kazakhstan often "
        "does not publish, so an honest UNRESOLVED is an acceptable outcome here; what is "
        "NOT acceptable is copying a system value onto a string without saying that is "
        "what you did. Ladder: Intergas Central Asia (intergas.kz) capital-repair and "
        "4th-thread material, Mangistau oblast development programmes, KazMunayGas and "
        "Ozenmunaygas procurement notices (goszakup.gov.kz), InAktau and Lada.kz "
        "regional press.",
        ["P3948", "P5776", "P5777", "P5783", "P5784", "P5789"],
    ),
    (
        "beineu-bozoy-shymkent",
        "Beineu-Bozoy-Shymkent (I, II, III capacity expansion)",
        "The domestic south-bound trunk, built in phases with a compressor-station "
        "capacity expansion tracked as its own row. The GulfPub recon flagged P6712 as a "
        "status conflict — that was adjudicated as the segment-vs-network artifact (GEM "
        "tracks the increment, GulfPub maps the corridor), so do NOT flip its status. "
        "Your questions are the Operator/Owner/Parent unions on all three and P6712's "
        "blank Diameter. A capacity-expansion row with no new physical pipe should have "
        "no diameter at all — check whether phase III lays pipe or only adds compression "
        "before proposing one. Ladder: QazaqGaz IGO 2024, Beineu-Shymkent Gas Pipeline "
        "LLP (the JV that owns it) material, Order No.350, KazTransGas/QazaqGaz press "
        "releases, Kazinform and Kapital.kz.",
        ["P3273", "P5788", "P6712"],
    ),
    (
        "saryarka",
        "Saryarka (Phases I-IV: Kyzylorda-Astana and onward)",
        "The flagship domestic gasification line north to Astana, carried as four phase "
        "rows. The in-development leg already reviewed the phase statuses — do not "
        "re-do that. Your questions are the blank Operator on all four and the Diameter "
        "union (P3309's is blank). Phase rows are where a system diameter is most likely "
        "to be wrong: later phases of this line are documented at smaller diameters than "
        "phase I. Ladder: QazaqGaz IGO 2024, Order No.350 and its appendices (NOTE: the "
        "'#z250' anchor lands in Appendices 5-7, which are graphic schemes - MAPS - so a "
        "full-text search miss is not evidence the ref fails), Ministry of Energy press "
        "releases, Astana/Karaganda/Kyzylorda akimat gasification programmes, Kazinform.",
        ["P3300", "P3307", "P3308", "P3309"],
    ),
    (
        "west-transit-gazprom",
        "The western transit lines: Makat-North Caucasus, Okarem-Beyneu, Orenburg-Novopskov",
        "Kazakhstan's Russia- and Turkmenistan-facing transit corridors, where the "
        "operator question is genuinely split between Gazprom entities and Intergas "
        "Central Asia depending on which side of the border the section sits — say which "
        "entity operates the KAZAKH section and cite a source that says so, not one that "
        "merely names the system. Already settled, do not re-open: cluster J (P1476 + "
        "P3999 are a real trunk-and-loop pair, not a duplicate), cluster I (P2492 and "
        "P5772 are distinct lines, though the second is filed under the first's name), "
        "and P0791's 1,230 km being the whole international system rather than the 382 km "
        "Kazakh section. Ladder: Gazprom Transgaz Makhachkala / Gazprom transit "
        "disclosures, QazaqGaz IGO 2024, Intergas Central Asia, KMG AR2021, Order No.350, "
        "Russian-language trade press (Neftegaz.ru, Interfax-Kazakhstan).",
        ["P1476", "P3999", "P2492", "P5772", "P0791"],
    ),
    (
        "north-central-domestic",
        "Northern and central domestic lines (Kostanay, Aktobe, Amangeldy, Tengiz, Gazli-Shymkent)",
        "Five rows whose common flag is a length ratio, and two of them are the largest "
        "in the country: P3955 Kartaly-Rudny-Kostanai draws 600 km against a stated "
        "155.8 km (3.85x) and P6834 Aktobe-Kostanay draws 461 km against 630 km AND makes "
        "landfall in a country the sheet never lists (check Russia — this corridor runs "
        "along and across the Russian border, so a Natural Earth boundary artifact is a "
        "live alternative to a data defect). P3956 Gazli-Shymkent's 877 km vs 575 km is "
        "probably the same whole-system-vs-Kazakh-portion shape as CAC. Decide which side "
        "the evidence supports per row; do not propose new coordinates. Ladder: QazaqGaz "
        "IGO 2024, Order No.350, Kostanay/Aktobe/Zhambyl akimat gasification programmes, "
        "Amangeldy Gas (a KMG subsidiary) and Tengizchevroil material, Kazinform.",
        ["P3955", "P3956", "P3963", "P6834", "P6835"],
    ),
    (
        "almaty-east-and-proposals",
        "Almaty region, the eastern spur, and two proposals (Russia-Kazakhstan-China, Karachaganak-Uralsk II)",
        "A mixed brief of short domestic lines plus two proposals. P6830/P6831 "
        "(Almaty-Bayserke-Talgar I and II) were adjudicated as cluster G: II is sourced "
        "at 62.4 km / 530 mm from QazaqGaz IGO 2024, I's 64.4 km is not — so I's blank "
        "Diameter and II's length ratio are the live items. P6787 Sarybulak-Zimunay is a "
        "small eastern line with a 60 km route against 92.5 km stated. P5410 "
        "(Russia-Kazakhstan-China, proposed) carries a 1,712 km route against 1,000 km "
        "stated plus an endpoint flag — for an unbuilt transit concept the route is "
        "indicative, so say whether either number is sourced at all. P7819 "
        "(Karachaganak-Uralsk thread II, proposed) is separately staged as a THREE-WAY "
        "ROUTE-SYNC violation (real geometry, RouteType 'Not mapped') — that repair is a "
        "sheet write outside this packet, so do not restate it; its blank "
        "Capacity/Diameter are what you can help with. Ladder: QazaqGaz IGO 2024, Order "
        "No.350, Almaty and Abai/East Kazakhstan akimat programmes, Karachaganak "
        "Petroleum Operating (KPO) material, Gazprom and CNPC statements for P5410.",
        ["P6830", "P6831", "P6787", "P5410", "P7819"],
    ),
]


def main() -> None:
    worklist = json.loads((OUT / "worklist.json").read_text())["rows"]
    by_pid = {r["project_id"]: r for r in worklist}

    grouped = [p for _, _, _, pids in GROUPS for p in pids]
    if len(grouped) != len(set(grouped)):
        dupes = {p for p in grouped if grouped.count(p) > 1}
        raise SystemExit(f"PID in two briefs: {sorted(dupes)}")
    missing = sorted(set(by_pid) - set(grouped))
    extra = sorted(set(grouped) - set(by_pid))
    if missing or extra:
        raise SystemExit(
            f"brief coverage is not exactly the worklist — unbriefed: {missing}; "
            f"not in worklist: {extra}"
        )

    gas = pd.read_csv(CSV, header=2, low_memory=False,
                      keep_default_na=False, na_values=[])
    gas["_sheet_row"] = gas.index + 4
    rows_by_pid = {r["ProjectID"]: r for _, r in gas.iterrows()}
    fields = ["PipelineName", "SegmentName", "Status", "StartYear1", "LengthKnownKm",
              "Capacity", "CapacityUnits", "Diameter", "Owner", "RouteAccuracy",
              "StartCountryOrArea", "EndCountryOrArea", "StartLocation", "EndLocation",
              "StartState/Province", "EndState/Province", "FuelSource",
              "PipelineNetworkGrouping"]

    BRIEFS.mkdir(parents=True, exist_ok=True)
    written = []
    for key, title, ladder, pids in GROUPS:
        rows = []
        for p in pids:
            src = rows_by_pid[p]
            rows.append({
                "project_id": p,
                "sheet_row": int(src["_sheet_row"]),
                "current": {f: str(src.get(f, "") or "") for f in fields},
                "flags": by_pid[p]["flags"],
                "wiki": by_pid[p].get("wiki", ""),
            })
        brief = {
            "brief": key,
            "title": title,
            "source_ladder": ladder,
            "n_rows": len(rows),
            "questions": sorted({f["field"] for r in rows for f in r["flags"]}),
            "rows": rows,
        }
        (BRIEFS / f"{key}.json").write_text(json.dumps(brief, indent=1))
        written.append((key, len(rows), sorted(brief["questions"])))

    (BRIEFS / "_index.json").write_text(json.dumps({
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_briefs": len(GROUPS),
        "n_rows": len(grouped),
        "briefs": [{"brief": k, "n_rows": n, "questions": q} for k, n, q in written],
    }, indent=1))

    print(f"wrote {len(written)} briefs covering {len(grouped)}/{len(by_pid)} worklist rows")
    for k, n, q in written:
        print(f"  {n:2d}  {k:32s} {','.join(q)}")


if __name__ == "__main__":
    main()
