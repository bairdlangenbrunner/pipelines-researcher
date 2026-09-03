#!/usr/bin/env python3
"""Split the Leg-3 worklist into nine briefs for the research fan-out.

    python batches/ukraine-gas/staging/qc/build_leg3_briefs.py

`build_qc_staging.py` emits `worklist.json` — 30 rows, 44 flags — as a flat list. In
Ukraine those flags collapse into two questions plus a short tail:

  * **`Operator` blank while gem.wiki names one (22 rows — three quarters of the
    worklist).** In Ukraine this is very nearly ONE question with ONE answer: since the
    1 January 2020 unbundling every trunk line inside government-controlled Ukraine is
    operated by Gas TSO of Ukraine LLC (ТОВ «Оператор ГТС України», GTSOU), which took
    the transmission function off Ukrtransgaz. That makes this the single most
    answerable thing in the packet — the opposite of a per-string spec — but it still
    needs a citation that says so, and it does NOT extend to the rows in occupied
    territory or to the Russian-side lines, which get their own briefs.
  * **`length_ratio` (14 rows).** GEM's own drawn route disagrees with `LengthKnownKm`
    by more than the accuracy band allows. **Most Ukrainian gas routes are 2-5 vertex
    schematics**, so a drawn span is a LOWER BOUND on corridor extent: a shortfall
    proves nothing, and only a drawn span far EXCEEDING the stated length is evidence.
    Ten of the fourteen sit on rows the redundancy leg already adjudicated, so those
    briefs say what is closed.
  * Tail: two `countries` flags, two `endpoint_country` flags, two `Date_logic` rows
    (`operating` with no `StartYear1`), and one `Owner`/`Parent` union on P5938.

Rows that share a source ladder are briefed TOGETHER — one agent's find on a corridor
answers every string in it. Each brief carries its rows' flags verbatim plus the current
sheet values, so the agent answers a specific question rather than re-deriving the flag.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BRIEFS = OUT / "rows" / "_briefs"
CSV = ROOT / "data" / "GGIT_gas_snapshot_20260812.csv"

# key -> (title, source-ladder hint, [PIDs])
GROUPS: list[tuple[str, str, str, list[str]]] = [
    (
        "gtsou-core-operator",
        "The government-controlled trunk network: ten rows whose only real question is who operates them",
        "Ten domestic trunk lines inside government-controlled Ukraine — the Shebelinka "
        "and Dikanka corridors to Kyiv, the Carpathian lines around Dolyna and "
        "Bilche-Volytsia, the Uzhhorod-Berehove and Vojany-Uzhhorod western links, and "
        "Novopskov-Shebelinka. All ten carry a blank `Operator`. This is ONE question "
        "with ONE answer and it is the highest-value hour in the packet: since "
        "1 January 2020 the transmission system operator is Gas TSO of Ukraine LLC "
        "(ТОВ «Оператор ГТС України», GTSOU), which took the function off Ukrtransgaz "
        "under the unbundling required by the Energy Community. Establish the exact "
        "legal name GEM should carry, source it, and apply it to all ten, saying in each "
        "shard that you did. TWO rows add a second question: P1453 "
        "(Efremovka-Dikanka-Kiev) and P1463 (Bohorodchany-Dolyna) are `operating` with "
        "no `StartYear1` — Soviet-era commissioning years, findable in operator "
        "chronologies but not guaranteed. Ladder: the Energy Community Secretariat and "
        "ENTSOG member/TSO listings (both name GTSOU in English and are reachable), "
        "NEURC/НКРЕКП licence decisions (nerc.gov.ua), Ukraine's Ministry of Energy, "
        "Naftogaz group disclosures, and the operator's own tsoua.com and utg.ua — but "
        "SEE GOTCHA 1: both 403 behind a WAF and must be read through Wayback, and a 403 "
        "is not evidence a page is gone.",
        ["P0780", "P1452", "P1453", "P1454", "P1455", "P1460", "P1462", "P1463",
         "P1483", "P1489"],
    ),
    (
        "kyiv-western-border",
        "Kyiv–Western Border (P0777 / P1480): the КЗУ two-string system",
        "The redundancy leg CONFIRMED these two rows are one system — the Soviet КЗУ "
        "(«Київ – Західний кордон»), a documented two-string build, 1020 mm in 1970 and "
        "1220 mm in 1972-73 — and found that NEITHER GEM length is supported: the only "
        "verifiable figures are 367 + 506 = 873 km against the sheet's 1,112.00 and "
        "399.90. It also found P1480's Drozdovychi endpoint anachronistic (Drozdovychi "
        "belongs to the older Komarno-Drozdovychi corridor and to the post-2006 Poland "
        "interconnection, not to the 1970s КЗУ). Do NOT re-litigate any of that — it is "
        "cluster A and it is staged. Your live items are the blank `Operator` on P0777 "
        "(same GTSOU answer as the core brief — say so and cite it) and the two "
        "`length_ratio` flags, which you should treat as a question about WHAT EACH "
        "LENGTH COUNTS rather than as a number to fix. The one thing that would close "
        "cluster A is the Ukrtransgaz historical chronology — it 403s live, so try "
        "Wayback captures of utg.ua/utg/about-company/history/. Ladder: that chronology "
        "via Wayback, Ukrainian technical and historical literature on the ГТС, ENTSOG "
        "transparency data for the Ukraine-Slovakia and Ukraine-Poland points, "
        "Ukrainian-language academic and industry sources.",
        ["P0777", "P1480"],
    ),
    (
        "yelets-kursk-family",
        "Yelets-Kursk-Dykanka and Yelets-Kursk-Kyiv (P0775 / P0776)",
        "The redundancy leg REFUTED the duplicate here: Kursk Oblast administration and "
        "Gazprom Transgaz Moskva both name the two lines separately, and the drawn routes "
        "share a 189.3 km prefix then split at Kursk (239.0 km on to Dykanka vs 417.5 km "
        "on to Kyiv). Two things it could NOT explain and hands to you. (1) Both rows "
        "carry almost the same length — 298.00 and 297.00 km — against drawn spans of "
        "429 km and 607 km. Since these routes run mostly through Russia and the sheet "
        "rows may be scoped to only part of the corridor, establish WHAT the 298/297 "
        "count before treating either as wrong. (2) An ownership-attribution defect is "
        "already staged as its own concern: P0775 shows Gazprom at 48.6% and P0776 shows "
        "'Gazprom 100%' alongside a second co-owner, and Gazprom owns no Ukrainian "
        "section. Do not restate that finding, but anything you learn about who owns and "
        "operates the UKRAINIAN section of each line is directly useful. Note also that "
        "Gazprom's own capacity table (65 vs 45 Mm³/day = 23.725 / 16.425 bcm/y) matches "
        "GEM almost exactly, which makes it GEM's likely ORIGIN rather than independent "
        "corroboration — do not cite it as a second source for those numbers. Ladder: "
        "Kursk Oblast administration material, Gazprom Transgaz Moskva "
        "(moskva-tr.gazprom.ru — one page failed to connect on 2026-08-15, retry and use "
        "Wayback), Russian-language trade press, Ukrainian sources for the Dykanka and "
        "Kyiv ends.",
        ["P0775", "P0776"],
    ),
    (
        "southwest-export-izmail",
        "The southwestern export corridor: P0784 (Shebelinka–Izmail family) and P5935 (Odessa-Chisinau)",
        "P0784 was adjudicated in cluster B as a FRANKENSTEIN ROW — three distinct "
        "pipelines exist (Moldovatransgaz lists РИ, ШДКРІ and АТИ as separate assets) so "
        "the whole-row duplicate is refuted, but P0784's four fields trace to four "
        "unrelated origins: its 24.00 bcm/y is verbatim an aggregate over three threads "
        "that double-counts capacity P0786 already carries, and its 164.00 km is "
        "contradicted by a 759.1 km drawn schematic. That is staged; do not restate it. "
        "What IS yours: P0784's blank `Operator`, its `countries` flag (the route makes "
        "landfall in a country the sheet never lists — for a corridor that runs to Izmail "
        "along the Moldovan border, check whether this is Moldova and whether the "
        "boundary is a Natural Earth artifact before calling it a defect), and the "
        "length_ratio read as 'what does 164 km count'. P5935 Odessa-Chisinau is a "
        "separate, simpler question: one length_ratio on a cross-border line to Moldova. "
        "Ladder: Moldovatransgaz — GOTCHA 2, moldovatransgaz.md fails TLS, use the mtg.md "
        "mirror which serves the same content and verifies 200 — Vestmoldtransgaz, "
        "ANRE Moldova, Ukrainian GTS material, ENTSOG transparency for the "
        "Ukraine-Moldova points.",
        ["P0784", "P5935"],
    ),
    (
        "western-interconnectors",
        "The western border links: Komarno-Drozdovychi, Hust–Satu Mare, and two cancelled interconnectors",
        "Four rows facing Poland, Romania and Hungary. P0778 Komarno-Drozdovychi is the "
        "most flagged row in the packet — blank `Operator`, a `countries` flag, an "
        "`endpoint_country` flag AND a length_ratio — and it is genuinely a short "
        "cross-border line whose route legitimately ends in Poland, so decide per flag "
        "whether a correctly-drawn partial/transnational route explains it rather than a "
        "data defect. Note cluster A found Drozdovychi to be THIS corridor's endpoint and "
        "not the КЗУ's, so P0778 is the row that endpoint properly belongs to. P1451 "
        "Hust–Satu Mare is a Ukraine-Romania link with the same operator + length_ratio "
        "pair. P1487 (Poland-Ukraine Interconnector) and P1773 (Romania-Ukraine "
        "Interconnector) are CANCELLED — the cancelled-status review already ran over "
        "them, so do not re-open status; P1487 needs only an operator judgement (for a "
        "cancelled project the honest answer may be that no operator was ever appointed, "
        "which is a legitimate `validity` finding rather than a fill) and P1773 a "
        "length_ratio read against an indicative route for an unbuilt line. **Do not "
        "propose new coordinates.** Ladder: GAZ-SYSTEM (Poland) and Transgaz (Romania) "
        "disclosures, ENTSOG transparency and the TYNDP project pages, the Energy "
        "Community Secretariat, FGSZ for the Hungarian side, GTSOU/Ukrtransgaz via "
        "Wayback (gotcha 1).",
        ["P0778", "P1451", "P1487", "P1773"],
    ),
    (
        "ivatsevychi-dolyna",
        "Ivatsevychi-Kobryn-Dolyna I and II (P3484 / P5938)",
        "Cluster G REFUTED the duplicate but falsified both of GEM's numbers, and the "
        "refutation is the interesting part: UTG's own chronology names 'Івацевичі-Долина "
        "(І нитка)' 1976 at 357.7 km and '(ІІ нитка)' 1977 at 366.7 km, both 1220 mm — "
        "two physically distinct strings — while BOTH GEM rows carry an unsourced "
        "292.00 km that matches neither, and 29.00 bcm/y appears on both as the SYSTEM "
        "total restated twice (GEM's own note says so; ISANS 2023 puts the corridor near "
        "30). P5938's `StartYear1` 1981 is also unsupported. Do not re-adjudicate the "
        "duplicate. Your job is the two length_ratio flags — which the above largely "
        "answers, so the deliverable is a sourced statement of what each string's own "
        "length is — plus P5938's blank `Operator` and its `Owner`/`Parent` multi-segment "
        "union (the wiki page describes the whole cross-border system while the GEM row "
        "is one string; decide once whether the row should carry the system's value set "
        "or its own, and say which — that judgement belongs in `validity`, not a fill). "
        "ONE OPEN QUESTION worth a look if you have time: this pass's own evidence file "
        "describes a THREE-string Торжок–Івацевичі–Долина system while cluster G sourced "
        "a TWO-string Івацевичі–Долина. Those are different corridors. If you can "
        "establish which is which, say so — but do not stage a Discovery candidate here. "
        "Ladder: the UTG chronology via Wayback (gotcha 1), Beltransgaz/Gazprom Transgaz "
        "Belarus for the Belarusian section, cdu.ru, ISANS and Belarusian/Ukrainian "
        "technical literature.",
        ["P3484", "P5938"],
    ),
    (
        "shebelinka-slovyansk",
        "Shebelinka–Slovyansk I and II (P3381 / P3382): a corridor mid-rebuild",
        "Cluster D adjudicated this as PARTIAL_OVERLAP, not a duplicate: it is one "
        "corridor caught mid-reconstruction. Ministry Order No.445 (12.07.2013) covers "
        "km 1.1–68.0; Nashi Groshi (2015) documents a parallel Ду500 replacing the Ду700; "
        "and ProZorro tender UA-2020-04-01-000023-c, titled RESIDUAL WORKS, proves the "
        "rebuild overran. The arithmetic problem is that 70 + 54 = 124 km is recorded "
        "against a corridor that is roughly 67–68.6 km. That is staged — do not re-open "
        "it. Yours are the two blank `Operator` cells (same GTSOU answer as the core "
        "brief, unless you find that this specific corridor sits with a different "
        "entity — parts of the Kharkiv/Donetsk network changed hands) and the two "
        "length_ratio flags, which you should answer as 'what does each row's length "
        "count — the original line, the replacement, or the corridor' rather than by "
        "picking a number. Ladder: the ProZorro tender record (prozorro.gov.ua), Ministry "
        "of Energy orders on zakon.rada.gov.ua, Nashi Groshi and Ukrainian investigative "
        "press, GTSOU regional material via Wayback.",
        ["P3381", "P3382"],
    ),
    (
        "occupied-southeast",
        "The occupied southeast: Taganrog-Mariupol-Berdyansk family (P1457/P7817/P7818) and Kramatorsk-Donetsk-Mariupol (P1488)",
        "Four rows in or facing occupied territory, and the brief where sourcing "
        "discipline matters most. Cluster E CONFIRMED that P5989 double-counts P7817 + "
        "P7818 — that is staged and not yours — but capped confidence at MEDIUM for a "
        "reason you must carry: every source describing the 2022 Russian-built "
        "Taganrog-Mariupol-Berdyansk works is Russian state or occupation media tracing "
        "back to ONE July 2022 directive, so five outlets repeating it is ONE origin, not "
        "corroboration. Cap your tiers accordingly and say so. Your questions are the "
        "blank `Operator` on P7817, P7818 and P1488, and P1457's length_ratio (its 516 km "
        "was already noted as unconfirmed). The operator answer here is NOT GTSOU: for "
        "the Russian-built lines it is a Russian entity or occupation utility, and for "
        "P1488 Kramatorsk-Donetsk-Mariupol the honest answer may be that operatorship is "
        "contested or unknown since 2014-2022 — a documented 'contested, unresolved' in "
        "`validity` is a better result than a confident wrong name. **Never present an "
        "occupation authority as the legitimate operator without saying that is what it "
        "is.** Ladder: Russian state and occupation media (treat as one origin), Gazprom "
        "and its transgaz subsidiaries, Ukrainian government statements on occupied "
        "infrastructure, satellite/OSINT reporting, GTSOU statements on lost assets.",
        ["P1457", "P1488", "P7817", "P7818"],
    ),
    (
        "russian-side-transit",
        "Russian-side lines: Stavropol-Moscow (P0793, retired) and Novopskov-Aksai-Mozdok (P1471)",
        "Two rows whose pipe is mostly or wholly outside Ukraine. P0793 "
        "Stavropol-Moscow is `retired` and carries a blank `Operator`; the answer is a "
        "Gazprom transgaz subsidiary rather than any Ukrainian entity, and for a retired "
        "Soviet line the correct answer may be the last known operator with an explicit "
        "note that it is historical. P1471 Novopskov-Aksai-Mozdok has an "
        "`endpoint_country` flag: a route endpoint lands in a country that is neither "
        "`StartCountryOrArea` nor `EndCountryOrArea`. For a transit line crossing the "
        "Russia-Ukraine border a route drawn only to the border is a correctly-drawn "
        "PARTIAL route rather than an error — decide which and say so. **Do not propose "
        "new coordinates.** Ladder: Gazprom transgaz subsidiary sites (Stavropol, "
        "Volgograd, Moscow) and Wayback copies, Russian-language technical literature and "
        "trade press, cdu.ru, Ukrainian GTS material for the Novopskov end.",
        ["P0793", "P1471"],
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
        (BRIEFS / f"{key}.json").write_text(json.dumps(brief, indent=1,
                                                       ensure_ascii=False))
        written.append((key, len(rows), sorted(brief["questions"])))

    (BRIEFS / "_index.json").write_text(json.dumps({
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_briefs": len(GROUPS),
        "n_rows": len(grouped),
        "briefs": [{"brief": k, "n_rows": n, "questions": q} for k, n, q in written],
    }, indent=1))

    print(f"wrote {len(written)} briefs covering {len(grouped)}/{len(by_pid)} worklist rows")
    for k, n, q in written:
        print(f"  {n:2d}  {k:26s} {','.join(q)}")


if __name__ == "__main__":
    main()
