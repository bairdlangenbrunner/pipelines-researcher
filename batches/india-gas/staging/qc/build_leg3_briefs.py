#!/usr/bin/env python3
"""Split the Leg-3 worklist into twelve corridor briefs for the research fan-out.

    python batches/india-gas/staging/qc/build_leg3_briefs.py

`build_qc_staging.py` emits `worklist.json` — 61 rows, 86 flags — as a flat list, but
the flags collapse into TWO questions plus a handful of singletons:

  * **Operator (39 rows).** India records an operator on exactly ONE of its 75 gas
    rows, against 794/4,356 (18.2%) across the GGIT gas tab, so this is a real India
    gap rather than the tracker norm. It is also ONE question per COMPANY, not per
    row: whoever operates GAIL's HVJ system operates all five of its segments. The
    gem.wiki infobox already names an operator on most of them — that is what raised
    the flag — but gem.wiki can never be the citation (standing rule 1), so each
    brief must source the operator independently. PNGRB's line-wise register names
    the AUTHORISATION HOLDER, which is the owner and often but NOT always the
    operator; say which one a source establishes.
  * **length_ratio (37 rows).** GEM's own drawn route disagrees with `LengthKnownKm`
    by more than ±33%. This is half the country, and the ratios scatter BOTH ways
    (24 under, 13 over; median 0.69), so it is not one systematic conversion defect —
    it has to be resolved per corridor. The register gives an authorised length for
    most of these rows, which usually settles which side is wrong.
  * Singletons: two transnational routes whose last endpoint lands outside both
    endpoint countries (P0451, P0766), three operating rows with no `StartYear1`,
    P0906's 350-inch diameter, P3906's capacity, P5413's unlisted landfall country,
    and P6646's thin existence support.

Rows that share a source ladder are briefed TOGETHER — one agent's find on a
corridor answers every row in it. That is the Pakistan lesson (per-row dispatch
fails when 35 rows are really one question) applied to a country where the shared
ladder is a company's own disclosures plus one regulator register.

Each brief carries its rows' flags verbatim plus current sheet values and the
geometry measured in Leg 2, so the agent answers a specific question rather than
re-deriving the flag.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BRIEFS = OUT / "rows" / "_briefs"
CSV = ROOT / "data" / "GGIT_gas_snapshot_20260810.csv"

# key -> (title, source-ladder hint, [PIDs])
GROUPS: list[tuple[str, str, str, list[str]]] = [
    (
        "gail-hvj-system",
        "GAIL's HVJ / DVPL / GREP trunk system",
        "One integrated GAIL system carried as five GEM rows, ALL stamped with the same "
        "107.00 MMSCMD (staged separately as redundancy cluster C). Ladder: GAIL's own "
        "annual report / investor presentations for the system's segment lengths and "
        "who operates it; the PNGRB NGPL MIS register, where this system appears as ONE "
        "authorisation; CAG or MoPNG documents for commissioning detail. Answer the "
        "operator question ONCE for the system and say so.",
        ["P0925", "P0919", "P3298", "P3297", "P3299"],
    ),
    (
        "north-trunk-delhi-ncr",
        "North trunk: Delhi-NCR, Haryana, Punjab, Uttarakhand",
        "GAIL and IOC lines feeding the NCR. Ladder: GAIL/IOC annual reports, PNGRB "
        "register, state CGD authorisations. P3906 additionally has an unsupported "
        "Capacity — it is the one row in this brief where a number, not just an "
        "operator, is in question.",
        ["P0912", "P0916", "P0917", "P3906"],
    ),
    (
        "gail-west-coast-kkbmpl",
        "GAIL west coast: Dabhol-Bangalore and KKBMPL",
        "KKBMPL is the country's strongest single finding and needs care rather than "
        "fresh research: P0934's 44 km is contradicted THREE independent ways (PNGRB "
        "register 675 km operating, OSM 306 km of mapped operating trace, and GEM's "
        "own drawn route at 375 km — an 8.5x ratio, the largest in India). The job "
        "here is to establish the commissioned length of each KKBMPL phase from "
        "sources GEM can cite, and to check whether P0934 and P2746 are split at the "
        "right point. Ladder: PNGRB register (both the OPERATIONAL and UNDER "
        "CONSTRUCTION sections — this line appears in both), GAIL disclosures, "
        "Kerala/Karnataka state filings.",
        ["P0915", "P0934", "P2746"],
    ),
    (
        "gail-east-jhbdpl",
        "GAIL east: JHBDPL, Srikakulam-Angul, Mumbai-Nagpur-Jharsuguda",
        "P0929 is the surviving row of redundancy cluster B (P0907 Barauni-Guwahati is "
        "staged as a probable double-counted SECTION of it — PNGRB's authorisation "
        "name for P0929 literally embeds 'Barauni-Guwahati'). Do not re-litigate that "
        "cluster; answer the operator question and note anything that bears on it. "
        "Ladder: PNGRB register, GAIL annual report, Pradhan Mantri Urja Ganga "
        "programme documents.",
        ["P0929", "P0954", "P2216"],
    ),
    (
        "gail-regional-networks",
        "GAIL regional / basin networks",
        "Aggregate 'network' rows rather than point-to-point lines, which is why their "
        "drawn routes and stated lengths disagree so widely (P0911 ratio 0.30, P0923 "
        "0.28). For a network row the question is WHAT THE LENGTH COUNTS — the whole "
        "regional grid, or the drawn trunk. Say which, and prefer a source that states "
        "a network total explicitly. P0923 additionally has no StartYear1. Ladder: "
        "GAIL annual report segment tables, PNGRB register, state-level gas grid "
        "documents.",
        ["P0904", "P0911", "P0923", "P0943", "P0933"],
    ),
    (
        "rajasthan-and-cancelled-gail",
        "Rajasthan lines and GAIL's cancelled proposals",
        "Includes the three Langtala rows, which the cancelled review already REFUTED "
        "as a duplicate cluster (three rival evacuation proposals off one gas field, "
        "three different owners) — do not merge them; the open items are ownership and "
        "P2215-style unit checks. P1436 and P3905 were separately confirmed distinct "
        "from each other. Ladder: PNGRB bid documents and annulment notices, Focus "
        "Energy / RRVUNL filings, Rajasthan state energy documents.",
        ["P1436", "P3905", "P0936", "P2748", "P2752", "P0955"],
    ),
    (
        "gspl-gujarat-grids",
        "GSPL's Gujarat grids and spurs",
        "Redundancy cluster H already REFUTED the idea that GAIL's and GSPL's Gujarat "
        "networks are one network entered twice — they are two companies' grids. The "
        "live question there is whether P0937's 'Low Pressure' 58 km row is correctly "
        "attributed to GSPL (a high-pressure transmission company) at all. Ladder: "
        "GSPL annual report (its grid length is disclosed yearly), PNGRB register, "
        "Gujarat Gas / GSPL investor material.",
        ["P0927", "P0937", "P0905", "P3909", "P3910"],
    ),
    (
        "bhatinda-corridor",
        "The Bhatinda / Gurdaspur / Jammu corridor (GIGL, GITL, GAIL)",
        "The highest-stakes brief. PNGRB foreclosed GIGL's original 725 km "
        "Bhatinda-Jammu-Srinagar grant and re-let the corridor in pieces; P0908 still "
        "carries the foreclosed framing while P3913/P5533/P5413 carry the successors "
        "(redundancy cluster A). Cluster E adds that P5533+P3913 sum to 392 km against "
        "the register's 261 km — the ONE phase pair in India that does not reconcile — "
        "and that P5411's drawn route (2,317 km) exceeds both Mehsana-Bhatinda phases "
        "combined. Establish, from sources GEM can cite: the current authorisation for "
        "each segment, its holder, and its authorised length. Ladder: PNGRB register "
        "editions (diffing editions is dispositive here — authorisation number, "
        "sponsor and date stay fixed while names change), PNGRB bid documents, GSPL "
        "and GAIL disclosures.",
        ["P0908", "P0941", "P5411", "P3913", "P5533", "P5413"],
    ),
    (
        "dahej-cluster",
        "Dahej / south Gujarat and the private trunk lines",
        "A tight geographic cluster of short spurs around the Dahej LNG complex plus "
        "two privately-held trunk lines. P0920 (East West / EWPL) and P0953 (Shahdol-"
        "Phulpur) are held through SPVs — India Infrastructure Trust and Reliance "
        "respectively — so name the OPERATING entity precisely rather than the parent. "
        "Ladder: Petronet LNG / Swan LNG / Torrent disclosures, PNGRB register, "
        "Pipeline Infrastructure Ltd and RIL filings.",
        ["P2210", "P2211", "P2212", "P3912", "P1435", "P0920", "P0953"],
    ),
    (
        "ongc-offshore-west",
        "ONGC offshore trunks and the Konkan coast",
        "Redundancy cluster I already REFUTED the HUT/MUT duplicate hypothesis (CAG "
        "Report No. 21 of 2016 treats them as two separately-metered lines). Two open "
        "items survive: P0926's FuelSource says 'Mumbai High Gas Field' but the line "
        "is named for and fed from HEERA, and P0926 has no GOIT counterpart to absorb "
        "its oil share (unlike MUT, tracked as GOIT P5191). Ladder: ONGC annual "
        "reports, CAG performance audits, H-Energy/Western Concessions filings for the "
        "Jaigarh lines.",
        ["P0926", "P0944", "P0930", "P0931"],
    ),
    (
        "east-coast-and-h-energy",
        "East coast: H-Energy's West Bengal group and the Ennore/Andhra lines",
        "P0935 and P3334 belong to redundancy cluster J (five H-Energy rows off one "
        "evolving east-coast LNG-evacuation concept); P3334's drawn route measures 599 "
        "km against a stated 115 km, close to P0913's 705 km, which is why the "
        "cluster's identities are entangled. P6538 is the 2024 successor proposal to "
        "the cancelled P0932 (cluster G — NOT a duplicate). P6646 is the thinnest row "
        "in the country: flagged for existence support AND missing StartYear1 AND "
        "missing operator. Ladder: PNGRB bid/authorisation documents and route maps "
        "(the bid maps carry a text layer with endpoints and intermediate towns), "
        "H-Energy and IMC filings, Tamil Nadu / Andhra state documents.",
        ["P0935", "P3334", "P6538", "P1434", "P0922", "P0921", "P6646"],
    ),
    (
        "northeast-and-crossborder",
        "North-east India, the cross-border projects, and eastern singletons",
        "P0906 carries a diameter of 350 INCHES — almost certainly 350 mm (~13.8in) "
        "entered in the wrong unit; confirm the intended figure rather than converting "
        "blind. P0928's 6,900 km is contradicted by its own 893 km drawn route and the "
        "annual leg found the figure traces to a 2016 Hydrocarbon Vision TOTAL, not "
        "this pipeline. P0451 and P0766 are flagged because their drawn routes END in "
        "Pakistan and Afghanistan respectively — for transit pipelines that may be a "
        "correctly-drawn partial route rather than an error, so say which. Ladder: "
        "PNGRB register, IGGL/AGCL disclosures, MoPNG and TAPI-consortium documents.",
        ["P0906", "P1309", "P0928", "P0451", "P0766", "P5412"],
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
              "StartState/Province", "EndState/Province", "FuelSource"]

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
        print(f"  {n:2d}  {k:28s} {','.join(q)}")


if __name__ == "__main__":
    main()
