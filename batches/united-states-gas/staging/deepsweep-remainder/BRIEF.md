SCOPE: THE COHORT REMAINDER — batch 5 of the US gas stale-operating campaign, and the batch that
closes slice 1. 45 rows in two parts:
- **30 OPERATING rows, LastUpdated <= 2023** — everything the first four batches (Texas 45, Gulf
  Coast 50, Appalachian/Mid-Atlantic 46, West 46) did not cover. Geographically scattered: the
  Midcontinent (Oklahoma / Arkansas / Kansas / Missouri / Illinois / Wisconsin / Indiana), the
  Southeast (Tennessee / Alabama / Mississippi / Georgia / South Carolina), and New England
  (Maine / New Hampshire / Massachusetts / Vermont). "East" is a misnomer; there is no theme
  of geography here.
- **15 rows with a BLANK LastUpdated**, added by Baird 2026-09-10: 14 CANCELLED rows (P0170
  Commonwealth, P0171 Constitution, P0233 NYMarc, P0292 Prairie State, P0303 Granite Bridge,
  P0314 Permian Katy, P0315 Sooner Trails, P0317 Montour Lateral, P0321 Downeast, P0322
  Renaissance, P0328 Island Gas Connector, P0376 Muskogee, P0380 SK Pipeline, P2008 TETCO TEMAX)
  and one operating row, **P2041 Taproot Baja / Rattlesnake Extension**. A blank LastUpdated
  means nobody has touched the row since load. Treat every value on these 15 as unverified.

CALIBRATION — 666 owed units, **3 of them already cited** (0.45%). Read this the way India and
Ukraine were read, NOT the way Pakistan was: `UNRESOLVED` here is UNFINISHED, not the correct
outcome. Nearly every operating row is a FERC-certificated interstate pipeline or a FERC
project with a public docket, an EIA entry and trade coverage. Every cancelled row was a
PROPOSED FERC or state project with a filing, a withdrawal, and press on both. If you cannot
source a FERC project's in-service year or a cancelled project's withdrawal date, you have not
reached the right register yet. The harvested pool is thinner than batch 4's (314 citations,
242 distinct, all 45 pages fetched) and uneven: P2496 has 38, P2008 23, P1997 25; eight rows
have 2 or fewer (P0321 has 1). Thin pool = open-web and regulator work, not an existence flag.

THE THREE EXISTING REFS:
- **P2495 and P2541 `SegmentCost [ref]` = `https://www.eia.gov/naturalgas/data.php#pipelines`.**
  That is a NAVIGATION PAGE, not a document; it does not state 16.2M or 145M and never will.
  The seed has it as DEAD_LINK. Find the document that states each cost (the EIA Natural Gas
  Pipeline Projects workbook row for the project, the FERC certificate's cost estimate) and stage
  it as the replacement; if nothing states the figure, the unit is UNRESOLVED and says so.
- **P2565 `Location [ref]` = spireenergy.com MoGas page** — re-verified 200 with the name. Keep
  it; the second source is still owed.

STATUS REVIEW IS ON FOR EVERY ROW, and it means two different things here:
- **OPERATING rows (31):** confirm `operating` with a dated source NEWER than LastUpdated, or
  find the change. Idled, converted or partly abandoned is a status finding, not existence.
- **CANCELLED rows (14): the question is whether the cancellation is RIGHT and SOURCED, not
  whether the project is dormant.** The dormancy rules (2y->shelved, 4y->cancelled) are for
  proposed/shelved rows; do not apply them to a row already cancelled. For each:
  - Find the dated cancellation/withdrawal evidence: a FERC order vacating/terminating the
    certificate or granting withdrawal of the application, the sponsor's announcement, a state
    permit denial, press. That evidence is the `Cancelled [ref]` (13 owed) and, where the row
    has a ShelvedYear, the `Shelved [ref]` (10 owed).
  - Check `CancelledYear` / `ShelvedYear` against it. A wrong year is a `spec` concern.
  - `ShelvedCancelledType`: nine rows read `inferred` (P0170, P0233, P0315, P0317, P0322,
    P0328, P0376, P0380, P2008). If you find a DATED, SOURCED cancellation, the row's type
    should become `confirmed` — emit a status_reviews verdict `change` with
    `proposed_changes: {"ShelvedCancelledType": "confirmed", "CancelledYear": "<yyyy>"}` and the
    refs. `inferred` stays only when nothing dated exists.
  - **P0314 Permian Katy has a BLANK ShelvedCancelledType AND blank Shelved/Cancelled years.**
    Fill both from the record (Loews/Boardwalk + Sempra; the P2K project), or state what is
    missing.
  - **A "cancelled" project that was actually BUILT is a status `change` to operating** — the
    most valuable finding this half of the batch can make. **P2008 TETCO TEMAX** in particular:
    Texas Eastern ran a series of Appalachia-to-market expansions in this corridor
    (Clarington OH -> Delta PA), and a project re-scoped and built under a different name is
    not cancelled. Same test for **P0376 Muskogee** (Enable) and **P0380 SK Pipeline** (Kinder
    Morgan). Name the successor project and its docket if one exists; if the successor is
    already a separate GEM row, say which (a `duplicate` concern naming both PIDs).
  - A cancelled row still needs its specs sourced: length, capacity, endpoints, owner as
    PROPOSED. A withdrawn FERC application states them. Sources dated during the proposal are
    the right ones; do not demand a construction-era document for a pipe that never got built.

P2041 TAPROOT BAJA / RATTLESNAKE EXTENSION — READ THIS BEFORE TOUCHING THE ROW.
It is a segment of **P0386 Taproot Baja Pipeline System, swept in batch 4.** Batch 4 found P0386
REAL (Weld County CO, DJ Basin, in service 2018, operator Taproot Rockies Midstream LLC, owner
affiliate Energy Spectrum) but filed a **`classification` concern: independent sources
(Pipeline News Oct-2018 project list, Rigzone Jun-2020, OGJ Sep-2019, energyspectrum.com)
describe a crude-oil / produced-water / fresh-water GATHERING system, with gas at most a minor
gathering component, not gas transmission.** It also flagged Owner `Energy Spectrum Securities`
vs the firm's own `Energy Spectrum Capital` (single source; SEC EDGAR was blocked then — see
MEASURED CONDITIONS, it now works with a declared User-Agent). **P2041's own sheet row reads
`Fuel = Oil` on the GAS tracker.** So the question for P2041 is: what does the Rattlesnake
Extension carry, and does the row belong on the gas tracker at all? If it is an oil or water
line, that is a `classification` concern with `contested: {"Fuel": "<what it carries>"}` and a
recommendation to move or retire it from GGIT — **do NOT research it as an oil pipeline beyond
settling that question** (oil is out of scope this cycle). Do not contradict batch 4's P0386
findings silently; if your evidence differs, say so and name P0386.

THE CLUSTERS — get these right before touching anything else:
- **Carolina Gas Transmission, 3 rows + one stray: P3221 system (1,500 mi, no capacity, no
  diameter), P4381 "Columbia to Eastover Pipeline" (29 mi, 8 in, 18 MMcf/d, 2016), P4382
  "Transco to Charleston Project" (55 mi, 12 in, 80 MMcf/d, 2018), and P2649
  "Columbia-to-Eastover Gas Pipeline" (45 km, 8 in, 18 MMcf/d, 2016, same owner).** 29 mi =
  46.7 km. **P2649 and P4381 are very likely the SAME PHYSICAL PIPE** filed twice under two
  names; test it and, if so, file `duplicate` on BOTH rows naming the other PID. Owner is
  Berkshire Hathaway Energy (lead: SCANA -> Dominion 2019, then Dominion's sale of its gas
  transmission business to BHE — verify the date and the chain with sources); the SC PSC and FERC both have dockets. P3221 is a SYSTEM row; its
  1,500 mi is a system figure and the right kind of ref for it — and not for P4381/P4382.
- **Gulf Coast Southbound (NGPL), 3 rows here + P2555 Lockridge swept in batch 1 + the P0222
  NGPL system row swept in batch 4.** P2039 Phase I (Chicago -> Agua Dulce, 460 MMcf/d, 2017,
  length AND length-units BLANK), P2541 Phase II (length 0, 300 MMcf/d, 2021), P2495 134th Street
  Lateral (1.4 mi, 20 in, 70 MMcf/d, 2021). These are NGPL projects that reversed flow on
  existing mainline — `LengthKnown = 0` with blank Diameter is plausibly RIGHT for a
  compression/reversal scope; confirm, don't "fix". P2039's Chicago -> Agua Dulce endpoints
  describe the FLOW PATH of the whole NGPL system, not new pipe — test whether the row's
  endpoints are a system description on a project row. P2495 is a real lateral in Chicago
  (134th Street, Illinois), NOT Indiana (see GEOGRAPHY).
- **PNGTS, 4 rows: P0242 mainline (295 mi, 24 in, 210 MMcf/d, 1999), P2588 Portland XPress
  (len 0, 24 MMcf/d, 2020), P2631 Westbrook XPress Phase 2 (len 0, 63 MMcf/d, 2021), P3280
  Westbrook XPress Phase 3 (len 0, 18 MMcf/d, 2021).** The XPress rows are compression-only
  INCREMENTS; the system figure is not a ref for any of them, and len 0 is correct. The
  mainline's 210 MMcf/d is plausibly pre-expansion; if current system capacity is higher, that
  is a `spec` concern on P0242 only. PNGTS ownership changed hands (TC PipeLines / Northern New
  England Investment Co / later TC Energy sale) — verify the CURRENT split with a dated source.
  **P2588 and P2631 end-state `Quebec`** — PNGTS's northern end is at Pittsburg NH connecting to
  TQM; a US FERC-jurisdictional row ending in Quebec is questionable. Settle where each project's
  facilities physically are (PNGTS XPress was largely compression in NH/ME plus upstream TQM and
  TC Mainline work in Canada).
- **Black Bear Transmission, 2 rows: P0185 AlaTenn and P0236 Ozark,** both
  `Black Bear Transmission LLC [100%]`, parent `Project Tarpon Holdco LLC`. Black Bear's
  ownership has changed since the rows were written — verify the current owner with a date.
  (Harvested `blackbearllc.com` is live.)
- **Kinder Morgan / Energy Transfer 50-50 JVs: P0189 Fayetteville Express and P0213
  Midcontinent Express.** Both list `ETP Legacy` as an owner. `ETP Legacy` is not an entity
  name you should reproduce without a source — check how Energy Transfer's interest is actually
  held today. Do not cross-cite: FEP (Arkansas -> Mississippi) and MEP (Oklahoma -> Alabama) are
  different pipelines that share owners.
- **The Joliet trio: P0195 Guardian, P0201 Horizon, P0214 Midwestern.** All three touch Joliet
  IL. Guardian (ONEOK) runs Joliet -> Wisconsin; Horizon (NGPL/Nicor JV) runs Joliet -> McHenry
  County IL; Midwestern (ONEOK) runs Portland TN -> Joliet. Interconnects are not duplicates.
- **Spire, 2 rows: P0255 Spire STL and P2565 MoGas.** Spire STL's FERC certificate was vacated
  by the DC Circuit in 2021 and the line ran under temporary certificates until the Commission
  re-issued its authorization — a STATUS history worth recording with dates (it never stopped
  operating). MoGas (Fort Leonard Wood MO <-> Alton/Wood River IL) changed hands before reaching Spire
  (lead: CorEnergy owned it, then sold it to Spire — verify the dates).
- **Enable -> Energy Transfer (merged Dec 2021): P2510 Canton (owner already reads Energy
  Transfer), P2560 Enable Gas Transmission MASS Expansion (len 0, 100 MMcf/d, 2022), P0376
  Muskogee (cancelled).** Batch 1 swept the P0161 Enable Gas Transmission system row. The
  MASS Expansion is a compression project on the EGT system; a system document is not a ref
  for its 100 MMcf/d.
- **Singletons on swept systems.** P2496 TGP 261 Upgrade Project (TGP system P0259 swept in
  batch 1); P1997 Atlantic Bridge Phase II (an Algonquin + Maritimes & Northeast expansion —
  Algonquin P0149/P0150 swept in batch 3); P2617 El Paso South Mainline Expansion (EPNG system
  P0184 swept in batch 1); P3295 Elba Express (connects to SNG, P0252 swept in batch 1); P2008
  TETCO TEMAX. The system rows' findings are context, not refs for these project rows.
- **P0179 East Tennessee "Main Line" (2,456 km, 1,860 MMcf/d)** is a SYSTEM row labelled as a
  segment; ETNG runs from Tennessee into Virginia and North Carolina. Decide which kind of row
  it is before choosing sources.

GEOGRAPHY COLUMNS (state cells) — the defects the 2026-09-04 route audit found on this batch:
- **Typos: P2495 `EndState` = `Inidiana` (and the lateral is in ILLINOIS, not Indiana — settle
  it); P1997 `StartState` = `Masschusetts`; P0380 `EndState` = `Teaxs`.**
- **Blank: P2617 El Paso South Mainline Expansion (BOTH states; route runs Texas -> Arizona);
  P3995 Addison Natural Gas (BOTH; the project is in Addison County, Vermont).**
- **Multi-value: P0185 AlaTenn `EndState` = `Mississippi, Alabama`.** One terminus per row.
- **Disagrees with the route geometry — research, do not assume either side is right:**
  - P3221 Carolina Gas Transmission end `Georgia` (route ends South Carolina).
  - P2039 Gulf Coast Southbound Phase I end `Louisiana` (route ends Texas; the EndLocation
    Agua Dulce Hub IS in Texas, so the state cell contradicts its own row).
  - P0236 Ozark end `Missouri` (route ends Arkansas).
  - P0179 East Tennessee start `Tennessee` (route starts North Carolina; plausibly a route
    orientation artefact — ETNG begins in Tennessee — but confirm).
  - P0214 Midwestern and P2565 MoGas: the sheet reads start Tennessee / start Missouri while the
    geometry starts in Illinois. The sheet's own Start/EndLocation agree with the sheet states,
    so this is almost certainly a REVERSED ROUTE orientation, and the sheet is right. Confirm the
    termini and note it; it is not an attribution defect.
- **Routeless rows** (no geometry, so no audit check): P1997, P2495, P2541, P2560, P2588, P2631,
  P3280, P4381, P4382. Their state cells are unchecked — source them.
- For YOUR row: if either state cell is blank, misspelled, multi-valued, or disagrees with the
  sources, emit a fills[] object with `ref_col: "Location [ref]"`, `value_cols:
  ["StartState/Province", "EndState/Province"]`, the sourced names as values (spelled
  correctly), and a verified ref that places the termini (a FERC order's county list, a state
  siting order, the operator's system map). If the cell is filled but your sources disagree,
  also file a validity `attribution` concern with `contested: {"EndState/Province": "<state>"}`.
  Location [ref] is owed on 44 rows: most are simple confirmations — do them.

LENGTHS — UNITS VARY BY ROW. This batch mixes miles (18 rows) and kilometres (24 rows), and
three rows have BLANK `LengthKnownUnits` (P0170, P0171, P2039 — all with a blank length, so a
length fill there must also fill the unit). Read YOUR row's `LengthKnownUnits` before writing a
number, state the unit explicitly in `values`, and convert explicitly in researcher_notes. Five
rows carry `LengthKnown = 0` (P2541, P2560, P2588, P2631, P3280): expansion with no new
physical pipe -> `LengthKnown = 0`, `Diameter` blank is the RULE; confirm, don't "fix". Rows
whose length looks like a system total: P0179 (2,456 km), P0186 KPC (1,817 km), P3221 (1,500
mi) — decide network vs segment row first.

OWNERSHIP IS STALE ACROSS THE BATCH. `Operator` is blank on 37 rows (37 owed), `Owner [ref]` on
all 45. Leads to verify, not answers: SCANA -> Dominion -> Berkshire Hathaway (Carolina Gas); Enable -> Energy Transfer (2021); PNGTS stake changes; Black Bear's
successor; `ETP Legacy`; KPC Pipeline / `MV Pipelines LLC`; Midship's Cheniere/EIG split (no
percentages on the sheet); P0317 Montour Lateral `Riverstone Holdings` with parent `unknown`.
Owner/operator work is staged onto the `Gas_OperatorsOwners` tab. When evidence disputes a
CURRENT owner value, that is an `attribution` concern with `contested` naming `Owner1`/`Owner2%`
/`Operator`.

THE SOURCE LADDER (use it in this order):
1. **FERC** — `elibrary.ferc.gov` and the CP-numbered docket. A certificate ORDER states mileage
   by county, diameter, horsepower, added capacity, the cost estimate and the in-service
   requirement; for the cancelled rows, an ORDER vacating a certificate or a NOTICE of withdrawal
   dates the end. The Commission's findings are one origin distinct from the applicant's filing.
   `federalregister.gov` publishes FERC notices (8 harvested) and is a separate publisher, but a
   Federal Register notice of an application restates the APPLICANT's numbers — same origin as
   the filing.
2. **STATE regulators and permitting agencies** — FERC silence is NOT an existence concern for an
   intrastate line (SK Pipeline, Canton, P0292 Prairie State — an Illinois project, P0303
   Granite Bridge — a New Hampshire LDC project, P3995 Addison — a Vermont PUC project, P0315
   Sooner Trails and P0376 Muskogee in Oklahoma). Measured:
   - 200: Illinois CC `icc.illinois.gov`; Oklahoma CC `oklahoma.gov/occ`; SC PSC `psc.sc.gov` and
     its docket system `dms.psc.sc.gov`; Vermont PUC `puc.vermont.gov` and ePUC
     `epuc.vermont.gov`; Maine PUC `maine.gov/mpuc`; Missouri PSC `psc.mo.gov`; Tennessee PUC
     `tn.gov/tpuc`; Texas RRC `rrc.texas.gov`; TCEQ; Georgia PSC `psc.ga.gov`; Alabama PSC
     `psc.alabama.gov`; Arkansas PSC `apsc.arkansas.gov`; Indiana URC `in.gov/iurc`; NJ DEP;
     PA DEP; Kansas CC; Wisconsin PSC; NY DEC applications `extapps.dec.ny.gov`.
   - **403 to scripted clients: NH PUC (`puc.nh.gov`, all forms), `mass.gov` (all of it), NY
     DEC `dec.ny.gov` root.** Not dead. Use Wayback captures of the specific document, or the
     secondary channels (MA DPU fileroom `eeaonline.eea.state.ma.us/DPU/Fileroom` answers 200).
     For **P0171 Constitution** (lead) the NY DEC Section 401 water-quality certificate denial
     is the pivotal document, followed by litigation, a FERC waiver fight and the sponsors'
     abandonment — date each step from the source, not from this brief.
3. **PHMSA / NPMS** — `www.npms.phmsa.dot.gov` (200); `primis.phmsa.dot.gov` (200, 5 harvested).
   Operator mileage is an independent check on a system-length claim.
4. **EIA** — the Natural Gas Pipeline Projects workbook
   `eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects.xlsx` (200, ~8 s). **Download it
   with `curl -o` and read it locally**; it is the likely answer for most in-service years,
   added capacities and project costs on the post-2010 project rows (P1997, P2039, P2041?,
   P2495, P2496, P2510, P2541, P2560, P2588, P2617, P2631, P2649, P3280, P3995, P4381, P4382,
   P0255, P0284) — and for the cancelled rows, which EIA lists with their final status. When you
   cite it, cite the workbook URL and name the sheet/row in `note`. EIA's `data.php` page is a
   navigation surface — never cite it.
5. **Operator disclosures** — SEC 10-K/S-1, investor decks, tariffs, system maps. **SEC EDGAR
   answers 200 to a DECLARED User-Agent** (`-A "Baird Langenbrunner research
   langenbrunner@gmail.com"`) and 403 to a browser UA — use the declared one for
   `sec.gov/cgi-bin/browse-edgar` and full-text search `efts.sec.gov/LATEST/search-index`.
   Operators: Kinder Morgan (TGP, EPNG, Elba Express, NGPL, FEP/MEP co-owner, SK); Enbridge
   (ETNG, TETCO, Algonquin/Atlantic Bridge, Renaissance?); TC Energy (PNGTS, NYMarc co-sponsor);
   Energy Transfer (Enable, Canton, MASS, FEP/MEP co-owner); ONEOK (Guardian, Midwestern); Spire
   (STL, MoGas); BHE GT&S `bhegts.com` (Carolina Gas); Cheniere (Midship); Williams
   (Constitution, Island Gas Connector); Vermont Gas (Addison); Liberty/Algonquin Power (Granite
   Bridge); NextEra (Sooner Trails); Tallgrass (Prairie State); Tellurian (Downeast); Boardwalk
   /Loews and Sempra (Permian Katy). **One operator is ONE origin across all its pages,
   microsites and press releases** (`pipeline2.kindermorgan.com` = kindermorgan.com;
   `tcpipelineslp.com` = TC Energy; `constitutionpipeline.com` = Williams).
6. **Trade and regional press** — NGI, S&P Global, Reuters, RBN, P&GJ, OGJ, Utility Dive, E&E
   News; regional: Portland Press Herald, Bangor Daily News, NHPR / Concord Monitor / Union
   Leader (Granite Bridge), VTDigger / Vermont Public (Addison — 4 harvested), Post and Courier
   (Carolina), Oklahoman / Tulsa World, St. Louis Post-Dispatch (Spire STL), Press & Sun-Bulletin
   / Albany Times Union (Constitution), Seattle Times / Times Colonist (Island Gas Connector).
   `fractracker.org` (9 harvested) is an independent NGO mapper — citable as one secondary.

INDEPENDENCE, precisely. FERC's ORDER vs the applicant's filing IN that docket = ONE origin;
FERC's order vs the company's website = TWO; a state PUC order vs FERC = TWO; a Federal
Register notice of an application = the applicant's numbers. The same wire story republished
(businesswire / prnewswire / globenewswire / seekingalpha reposting a press release) is the
OPERATOR's origin, not a second source. Anything citing GEM is disqualified.

EXISTENCE / DUPLICATE FLAGS — the bar is high. Before you recommend retiring, folding or calling a
row a phantom:
  (a) NAME THE DOCUMENT you tested and say what it does and does not contain.
  (b) An intrastate line's absence from FERC is EXPECTED — check the state regulator first.
  (c) Read MAPS, not just full text.
  (d) Segment-vs-network granularity: an aggregate restated on a phase row is a `spec` defect,
      but the PHASE still exists.
  (e) A line idled, converted or partly abandoned EXISTED — status finding, never existence.
  (f) A CANCELLED project "existing" means it was genuinely PROPOSED — a filing, an open season,
      an announcement. A cancelled row with no trace of ever having been proposed is the
      existence flag; a cancelled row that was built is a status change.
State your evidence so a reviewer can check it.

RULES THAT BITE HERE:
- **Never cite GEM.** No gem.wiki / globalenergymonitor.org in any `[ref]`.
- **abarrelfull is BANNED, and SIX of this batch's shortened links resolve to it.** 16 `bit.ly`
  entries in the pool (13 distinct). Resolved 2026-09-10:
  - -> `abarrelfull.wikidot.com` (BANNED — the value is UNSOURCED, chase the footnote):
    P0170 (`2sl9gSY`), P0189 (`2sn9PM9`), P0213 (`2sGERz2`), P0233 (`2sYgxIL`), P0242 / P2588 /
    P2631 / P3280 (all `2rZk38H`), **P2560 (`2skHnKP` -> a CenterPoint Energy Gas Transmission
    page — it is not even about the MASS Expansion)**.
  - -> Wikipedia: P0185 (`2ku9DXs` -> "Enbridge Pipelines", not about AlaTenn), P2496
    (`2kQI0ua`), P2617 (`2jPLWXM`). One Wikipedia article = one secondary source; an article
    whose footnote is GEM cannot corroborate.
  - -> P0171 `constitutionpipeline.com` (200, Williams' project site); P0236 / P2008 (`2rDChwc`)
    -> an Enbridge interactive map URL (a mutable map surface, not a citable document).
  - -> P0179 (`2snwnfJ`) -> a retired spectraenergy.com ETNG page, **404 — genuinely dead**; look
    for the Wayback capture.
  **Resolve every shortener before you open it and cite the resolved target, never the bit.ly.**
- **Never fabricate a URL.** Every URL goes through `scripts/url_verifier.py --name`.
- **A blocked fetch is not a deletion.** 403 / Cloudflare / timeout = access failure; only a
  confirmed 404/410 may retire a ref. A blocked origin gets its Wayback snapshot ADDED.
- **Cite the ARTICLE, never a navigation surface** (a site root, a search results page, an
  eLibrary query URL, an interactive map, EIA's data.php).
- **SegmentCost: half of batch 1's researched cost values did not survive primary sources.** A
  cost is `REFS_ADDED` only when a primary source states THAT figure for THAT scope. 43 cost
  units are owed (19 uncited, 24 blank); expect many to end UNRESOLVED honestly.
- **Pressure is owed on all 45 rows** (MISSING_VALUE). A FERC order or the operator's tariff
  states MAOP for most interstate lines; do not force it, but do look.
- **Never fill a `[ref]` without a paired value.** No orphan refs exist on these rows, so any
  orphan you create is one you introduced.

MEASURED CONDITIONS (2026-09-10) — do not burn budget re-testing these:
  - `elibrary.ferc.gov` 200 fast. `www.ferc.gov` root 403s scripted clients; document paths under
    `www.ferc.gov/sites/default/files/...pdf` return 200.
  - **`www.eia.gov` answers 503 to HEAD, 200 to GET.** The pipeline-projects xlsx is live (~8 s).
  - `www.npms.phmsa.dot.gov` 200; the bare `npms.phmsa.dot.gov` does not resolve.
  - **SEC EDGAR: 200 with a declared UA, 403 with a browser UA** (see ladder step 5).
  - 403 (blocked, not dead): `puc.nh.gov`, `mass.gov`, `dec.ny.gov` root.
  - 200: every operator host listed in step 5, `blackbearllc.com`, `pngts.com`, `bhegts.com`,
    `vermontgas.com`, `spireenergy.com`, `federalregister.gov`, `fractracker.org`,
    `web.archive.org`.
  - `en.wikipedia.org/wiki/Constitution_Pipeline` is 404 under that title — search Wikipedia for
    the real title rather than guessing.

THE HARVESTED CITATION POOL IS A WORKLIST, NOT A LOOKUP TABLE. Many links are 2016-2017 vintage;
expect rot and go to Wayback rather than dropping the lead. In researcher_notes, report HOW MANY
of your row's harvested citations you opened, and flag any you could not read and why.

VALUE CONVENTIONS: `*CostUnits` is a BARE currency code (`USD`). Controlled vocab lowercase
except `FIDStatus` (`Pre-FID`/`FID`); `ShelvedCancelledType` is `inferred` / `confirmed`
lowercase. Capacity in the sheet's units (`MMcf/d` throughout this batch). Lengths in YOUR row's
`LengthKnownUnits` (mixed mi/km — see LENGTHS). No recon legs run for US gas and you never
propose route geometry; a route-vs-sheet disagreement is a validity note, nothing more.
