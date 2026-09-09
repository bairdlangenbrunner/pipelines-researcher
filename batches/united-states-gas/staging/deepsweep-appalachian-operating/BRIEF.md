SCOPE: US APPALACHIAN BASIN + MID-ATLANTIC (Ohio / Pennsylvania / West Virginia / New York /
Michigan / New Jersey / Maryland / Delaware / Virginia / Indiana, plus two rows whose route
crosses into Ontario). OPERATING gas pipelines, LastUpdated <= 2023. 46 rows = batch 3 of the
US stale-operating cohort (batch 1 Texas, batch 2 Gulf Coast). The slice was cut by the
DERIVED state from the 2026-09-04 route-geometry audit, not by the sheet's StartState/Province
column, which is blank or wrong on a meaningful share of the cohort.

CALIBRATION — a blank means NOBODY LOOKED, not that nothing exists.
This cohort's citation base is **11 filled `[ref]` cells against 663 owed (1.7%)** — thinner
than the Gulf Coast batch's 3.5%. Read it the way India and Ukraine were read, NOT the way
Pakistan was: `UNRESOLVED` here is UNFINISHED, not the correct outcome. Nearly every line in
this batch is a FERC-certificated interstate pipeline with a public docket, an EIA entry and
years of trade coverage. If you cannot source an operating Appalachian line's diameter,
capacity or in-service year, you have not reached the right register yet.

THE SOURCE LADDER (use it in this order):
1. **FERC** — `elibrary.ferc.gov` and the CP-numbered certificate docket. Almost all of this
   batch is interstate and FERC-jurisdictional: Rover (CP15-93), NEXUS (CP16-22), Leach XPress
   and Mountaineer XPress (Columbia/TC Energy), Rockies Express, Atlantic Sunrise (Transco),
   Leidy South, Access South, Millennium, Algonquin/AIM, Empire, Iroquois, Vector, Eastern Gas
   Transmission & Storage (EGTS, ex-Dominion Transmission), Columbia Gas Transmission,
   Appalachian Gateway, WB Xpress, Gulf Xpress, Buckeye Xpress, Central Corridor, Sunbury.
   A FERC ORDER states mileage by county, diameter, horsepower, added capacity, the cost
   estimate and the in-service date explicitly. The Commission's FINDINGS are one origin
   distinct from the applicant's own filing in the same docket.
2. **STATE regulators for intrastate lines and for siting** — FERC silence is not an existence
   concern for an intrastate line. Ohio Power Siting Board (`opsb.ohio.gov`) for Ohio gas
   transmission siting; PA PUC (`puc.pa.gov`) + PA DEP chapter 105/102 permits for
   Pennsylvania (Revolution, Birdsboro, Sunbury are PA-jurisdictional in whole or part);
   WV PSC (`psc.state.wv.us`) for Mountaineer Gas Company's Phase I/II (an intrastate LDC
   project, NOT a FERC project); NY DPS (`documents.dps.ny.gov/public/`, the DMM docket
   system) for Article VII certificates; Michigan PSC (`michigan.gov/mpsc`); NJ BPU
   (`nj.gov/bpu`); Virginia SCC (`scc.virginia.gov`).
3. **PHMSA / NPMS** — `npms.phmsa.dot.gov` for route and operator identity; PHMSA annual
   report mileage by operator ID.
4. **EIA** — the Natural Gas Pipeline Projects workbook and state/infrastructure pages;
   independent of the operator and good for in-service dates and added capacity.
5. **Operator disclosures** — SEC 10-K/S-1, investor decks, tariffs and system maps.
   TC Energy/Columbia (Columbia Gas Transmission, Leach XPress, Mountaineer XPress, WB Xpress,
   Gulf Xpress, Buckeye Xpress, Central Corridor); Energy Transfer (Rover); Enbridge (Algonquin,
   Texas Eastern, Vector, NEXUS co-owner); DT Midstream (NEXUS co-owner, Millennium);
   Williams (Atlantic Sunrise, Leidy South); Tallgrass (Rockies Express); National Fuel Gas
   (Empire); Berkshire/Eastern Gas Transmission & Storage (EGTS, ex-Dominion); Chesapeake
   Utilities (Eastern Shore); Mountaineer Gas Company (WV LDC); Iroquois Gas Transmission.
   One operator is ONE origin across all of its pages and microsites.
6. Trade press (Natural Gas Intelligence, S&P Global, Reuters, Pipeline & Gas Journal,
   Marcellus Drilling News, Kallanish). Local Ohio/PA/WV newspapers are useful for
   construction milestones and are independent of the operator.

INDEPENDENCE, precisely. FERC's ORDER vs the applicant's own filing IN that docket are ONE
origin — the docket contains the company's numbers. FERC's order vs the company's website IS
two. A state PUC's order vs FERC's order IS two. `roverpipelinefacts.com` is Energy Transfer's
own microsite and is ONE origin with Energy Transfer; `esng.com` is ONE origin with Chesapeake
Utilities. The same wire story republished is one. Anything citing GEM is disqualified.

THE NAME-COLLISION AND PHASE CLUSTERS — this batch is a duplicate/granularity minefield and
that is deliberate. Get these right before touching anything else:
- **Rover, 4 rows.** P0392 Phase 1 (711 mi, 42 in, 1700 MMcf/d), P2438 Phase 2 (len 0,
  1550 MMcf/d), P2604 Rover Expansion (len 0, 175), P2635 Wick Meter Station Expansion (len 0,
  300, WV->WV). Phases 1 and 2 are ADDITIVE halves of one ~3.25 Bcf/d system — Rover's system
  total is NEVER a ref for a phase row, and finding "3.25 Bcf/d" does not make either phase
  wrong. The three len-0 rows are compression/meter-station scopes: `LengthKnown = 0` and blank
  `Diameter` is CORRECT for them (expansion with no new physical pipe), so do not "fix" it.
  P2635 is a meter station in West Virginia while the mainline runs Ohio->Michigan; that is a
  real difference of scope, not a state error.
- **Rockies Express, 3 rows.** P5829 Seneca Lateral (14 mi, 24 in), P5830 Zone 3 East-to-West
  (blank length, 1800), P5831 Zone 3 Capacity Enhancement (blank length, 800). Zone 3
  East-to-West is a FLOW REVERSAL on existing pipe — if the FERC order confirms no new mainline
  pipe, the owed length is `0`, not a number scraped off the system. Both blanks are owed.
- **Eastern Shore, 3 rows.** P0182 (732 mi, 100 MMcf/d, 1959), P2003 2017 Expansion (40 mi),
  P6003 Del-Mar Energy Pathway (20 mi). **P0182's 732 mi is the number to test hardest** —
  Eastern Shore Natural Gas is commonly described as a system of a few hundred miles, so either
  732 is wrong or it counts something the description does not. Name the document either way.
- **Mountaineer — a NAME COLLISION, not a duplicate.** P0221 Mountaineer XPress (171 mi,
  2700 MMcf/d) is TC Energy/Columbia Gas Transmission's FERC project. P0307 Phase I and P2040
  Phase II "Mountaineer Gas Pipeline" belong to **Mountaineer Gas Company**, a West Virginia
  LDC, and are state-regulated (WV PSC), not FERC. Different companies, different projects.
  Do not merge them and do not cite one for the other.
- **Empire, 2 rows.** P0288 Main Line (269 mi, Ontario->Pennsylvania, 300 MMcf/d) and P2531
  North Expansion (40.2 mi, Pennsylvania->Ontario, 300 MMcf/d). The identical 300 and the
  reversed endpoints are both suspicious: check whether the expansion's capacity is the SYSTEM
  figure restated on a segment row (that is a `spec` concern) and which direction each actually
  flows after the North Expansion.
- **Vector, 2 rows.** P2505 Blue Water Energy Center lateral (1.25 mi, 24 in) and P3202 Blue
  Water Compressor (len 0, recorded Michigan->Wisconsin). Verify P3202's endpoints — a
  compressor project ending in Wisconsin on a Michigan lateral needs an explanation or is an
  attribution concern.
- **Algonquin, 2 rows.** P0149 Main Line (1131 mi) and P0150 Algonquin Incremental Market /
  AIM (37 mi, 42 in). AIM's numbers are not the main line's.
- **Columbia Gas Transmission, 2 rows.** P0169 carries SegmentName `SYSTEM/NETWORK INFO`,
  19,312 mi and a blank start state — it is a NETWORK row, not a segment, so a system figure IS
  the right kind of ref for it and a segment figure is not. P2516 Central Virginia Connector
  (len 0) is a discrete project.
- **Dominion / EGTS, 2 rows.** P0176 (6,059 mi) and P2630 West Loop Expansion (5.1 mi). See the
  next paragraph about P0176's end state.

STATE COLUMNS ARE PART OF THIS BATCH.
- **P0176 carries `New United Kingdom` in `EndState/Province`. This is a find-and-replace scar
  ("New England" -> "New United Kingdom") and it is NOT a mechanical fix.** The column holds
  individual STATES everywhere else in the tracker, and `New England` appears ZERO times in
  either tracker, so restoring it would introduce an unprecedented value. Research the row's
  real terminus state and propose THAT, with a ref. Same treatment if you meet it elsewhere.
- **P0169 and P0176 have a blank `StartState/Province`**; P2551 and P2531 and P0288 have an
  end-state the route geometry disputes; P0156 (Atlantic Sunrise) and P2502 (Appalachian
  Gateway) have a start-state the geometry disputes.
- For YOUR row: if either state cell is blank or is not a US state / Canadian province, emit a
  fills[] object with `ref_col: "Location [ref]"`, `value_cols: ["StartState/Province",
  "EndState/Province"]`, the sourced state names as values, and a verified ref that places the
  termini (a FERC order's county list, a state siting order, the operator's system map). If the
  cell is filled but your sources disagree with it, file a validity `attribution` concern naming
  the source and the state it supports — never silently pass it.

RULES THAT BITE HERE:
- **Never cite GEM.** No gem.wiki / globalenergymonitor.org in any `[ref]`. Visit the wiki page
  for its OUTBOUND citations only.
- **Wikipedia IS citable** as ONE secondary source; an article whose own footnote is GEM cannot
  corroborate.
- **abarrelfull is BANNED** (`abarrelfull.wikidot.com`, `.co.uk`) and so is theodora.com.
- **Never fabricate a URL.** Every URL goes through `scripts/url_verifier.py --name`.
- **A blocked fetch is not a deletion.** 403 / Cloudflare / timeout = access failure; only a
  confirmed 404/410 may retire a ref. A blocked origin gets its Wayback snapshot ADDED
  alongside, never swapped in.
- **Cite the ARTICLE, never a navigation surface.** A site root, a search-results page, an
  eLibrary query URL or a bare host is a MUTABLE surface and fails validation. Cite the
  accession-numbered FERC document, not the search that found it.
- **SegmentCost: half of batch 1's researched cost values did not survive primary sources.**
  A cost is `REFS_ADDED` only when a primary source (FERC order estimate, 10-K capitalized cost,
  dated financing) states THAT figure for THAT project scope. A total-project or system figure
  restated on a segment row is a `spec` concern, not a ref.
- **Expansion with no new physical pipe -> `LengthKnown = 0`, `Diameter` blank.** Several rows
  here are already correct on this; confirm rather than "fix".
- **Two orphan `[ref]` cells on blank values: P0149 and P0150 `Pressure [ref]`.** A ref with no
  value is a defect — either source the pressure value to pair with it, or flag the ref.

EXISTENCE / DUPLICATE FLAGS — the bar is high. Before you recommend a row be retired, folded or
called a phantom:
  (a) NAME THE DOCUMENT you tested and say what it does and does not contain. "The report does
      not mention it" is only evidence if that report would necessarily list it.
  (b) An intrastate line's absence from FERC is EXPECTED and is NOT an existence concern.
      Check the state regulator first (this bites on Mountaineer Gas, Revolution, Birdsboro,
      Sunbury, Risberg, DeRuyter, Marquette Connector, Saginaw Trail).
  (c) Read MAPS, not just full text. A system map or tariff schematic often names a segment the
      prose never does.
  (d) Segment-vs-network granularity: GEM tracks segments and project phases. A source
      describing the whole system is not evidence a phase is duplicated. An aggregate figure
      restated on a phase row is a defect worth flagging, but the PHASE still exists.
  (e) A line idled, converted or partially abandoned EXISTED and is a status finding, never an
      existence concern.
State your evidence so a reviewer can check it.

MEASURED CONDITIONS (2026-09-08) — do not burn budget re-testing these:
  - `elibrary.ferc.gov` returns 200 fast (~0.15 s). `www.ferc.gov` ROOT answers 403 to scripted
    clients, but document paths under `www.ferc.gov/sites/default/files/...pdf` return 200 and
    pass url_verifier.
  - `dps.ny.gov` ROOT answers 403, but `documents.dps.ny.gov/public/` (the DMM docket system)
    returns 200 — go straight there for New York.
  - `dis.puc.pa.gov` does NOT resolve (NXDOMAIN). Use `www.puc.pa.gov` (200) and find the
    docket path from there.
  - 200 and usable: `opsb.ohio.gov` (~1.1 s), `psc.state.wv.us`, `michigan.gov/mpsc`,
    `nj.gov/bpu`, `scc.virginia.gov`, `roverpipelinefacts.com`, `esng.com`.
  - `www.eia.gov` returns 200 but takes ~10 s per fetch, and the pipeline-projects workbook is
    an .xlsx — download with curl and read it, do not fetch it as a page. Batch your EIA reads.
  - **The 18 distinct `bit.ly` links in this batch's harvested pool all redirect to
    en.wikipedia.org.** They are ONE secondary source each, not 18 sources — resolve a shortener
    before citing it, and cite the resolved target, never the `bit.ly` form.
  - Existing refs on these rows: 6 units all-live, 5 with dead links, 4 live but the page never
    names the pipeline (`name_found` false) — those 4 are attribution work, not re-verification.

THE HARVESTED CITATION POOL IS A WORKLIST, NOT A LOOKUP TABLE. 570 citations were harvested
across these 46 wiki pages. Do not stop at the first sufficient source and leave the rest of
your row's pool unopened. In `researcher_notes`, report HOW MANY of your row's harvested
citations you actually opened, and flag any you could not read and why.

VALUE CONVENTIONS: `*CostUnits` is a BARE currency code (`USD`), never "USD millions".
Controlled vocab is lowercase except `FIDStatus` (`Pre-FID`/`FID`). Capacity is stated in the
sheet's units — check the worklist unit's column header before writing a number. Never fill a
`[ref]` without a paired value, or leave a researched value without a `[ref]`.
No recon legs run for US gas and you never propose route geometry; a route-vs-sheet
disagreement is a validity note, nothing more.
