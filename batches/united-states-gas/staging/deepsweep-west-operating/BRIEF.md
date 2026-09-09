SCOPE: THE US WEST — Rockies, Northern Plains, Southwest, West Coast (Colorado / Wyoming /
Montana / North Dakota / Minnesota / Kansas / New Mexico / Arizona / California / Oregon /
Washington), plus the seven rows whose route crosses into Canada (Alberta, British Columbia,
Saskatchewan, Manitoba) or Mexico (Chihuahua/Sonora/Baja). OPERATING gas pipelines,
LastUpdated <= 2023. 46 rows = batch 4 of the US stale-operating cohort (batch 1 Texas 45,
batch 2 Gulf Coast 50, batch 3 Appalachian/Mid-Atlantic 46). 30 rows remain after this one.
The slice was cut by the DERIVED state from the 2026-09-04 route-geometry audit, not by the
sheet's StartState/Province column, which is blank, a basin name, or a region name on a
meaningful share of this batch.

CALIBRATION — THIS COHORT HAS **ZERO** FILLED `[ref]` CELLS.
663 owed units, **0 of them already cited**. Not 1.7% (batch 3), not 3.5% (Gulf Coast) — zero.
Nobody has ever put a source on any of these 46 rows. Read this the way India and Ukraine were
read, NOT the way Pakistan was: `UNRESOLVED` here is UNFINISHED, not the correct outcome.
Every mainline in this batch is a FERC-certificated interstate pipeline with a public docket,
an EIA entry, a Wikipedia article and decades of trade coverage — Kern River, Ruby, Rockies
Express, Northern Border, Transwestern, NGPL, Panhandle Eastern, Great Lakes, Alliance, GTN.
If you cannot source an operating Rockies trunk's diameter, capacity or in-service year, you
have not reached the right register yet. **But the citation POOL is healthy: 410 external
citations were harvested from these 46 wiki pages, all 46 fetched OK.** The sources exist and
GEM already found many of them — they were simply never written into the backend. Much of this
batch is transcription-plus-verification on top of a real pool, not a blind search.

THE THEME OF THIS BATCH IS STALE OWNERSHIP. Read this section before you plan your row.
Nearly every row carries an `Owner` string frozen somewhere between 2012 and 2023, and the
`Operator` column is **blank on all 46 rows** (41 `Operator [ref]` units are owed). The western
interstates have churned hands repeatedly. The following are LEADS TO VERIFY, not answers —
if a lead is wrong, say so in `researcher_notes` and stage what the sources actually support:
- **`TC PipeLines LP` is a dissolved entity.** TC Energy rolled up the remaining public units
  in 2021. It still appears as an owner on **P0275 Tuscarora [100%]**, **P3601 Tuscarora XPress
  [100%]**, and as 46.45% of **P0194 Great Lakes** (alongside TC Energy 53.55%). Settle each
  with a dated source; a corporate rollup is exactly the kind of fact a 10-K states plainly.
- **`El Paso Corp` is a dissolved entity** — Kinder Morgan acquired it in 2012. It is still the
  100% owner on **P0166 Cheyenne Plains** and **P0219 Mojave**, while **P3190 El Paso Gas /
  Carlsbad South** on the same batch already reads Kinder Morgan. That internal inconsistency
  is itself the flag. Note that the 2012 KM/El Paso merger forced FTC divestitures — do not
  assume every El Paso asset went to Kinder Morgan; check where each one actually landed.
- **P0151 Alliance's owner reads `Alliance USA [50%]; Alliance Canada [50%]`.** Those are the
  two halves of the PIPELINE, not two companies — this is a segment split miswritten into the
  ownership column. Find the real corporate owners and their shares. (One of the row's own
  harvested citations is a `pembina.com` Alliance page; start there and corroborate.)
- **P2573 North Mist is attributed to `The Pacific Gas and Electric Co [100%]`.** North Mist is
  an Oregon project on the Mist storage field; PG&E is a California utility with no Oregon gas
  transmission. Settle who owns and operates it, with a ref. High-confidence attribution defect.
- **P0359 Cheyenne Connector reads `Tallgrass 50%; DCP Midstream LLC 50%`** — DCP Midstream was
  taken fully private by Phillips 66 in 2023. Check whether the 50% moved and to whom.
- **P0222 NGPL reads `Kinder Morgan 37.5%; Brookfield 25%; ArcLight 37.5%`.** NGPL Holdings'
  cap table changed after 2023. Verify the current split; a three-way ownership row with stale
  percentages is a `spec` concern even when the names are right.
- **P0239 Panhandle Eastern reads `Southern Union Panhandle LLC; Energy Transfer` with NO
  percentages at all.** Every other multi-owner row in the batch carries bracketed shares.
  Source the shares or file the omission.
- **P0248 Ruby** (`Ruby Pipeline LLC [100%]`) went through Chapter 11 in 2022 and changed hands;
  **P0254 Southern Trails** (`Southern Trails Pipeline Co [100%]`) descends from the Questar
  Pipeline lineage that moved twice after 2016. Both need a current owner AND a hard look at
  status — see the status paragraph below.
- **P3170 Santa Fe Mainline reads `Emera [100%]`** — Emera's New Mexico gas utility was sold in
  the mid-2020s. **P0207 Kern River** reads `Kern River Gas Transmission Co`, a holding name
  that hides its actual parent; batch 3 hit the same pattern on P0176 and the answer was
  Berkshire Hathaway Energy. Name the ultimate parent, with a ref.
Owner/operator work is staged onto the `Gas_OperatorsOwners` tab, not `ResearcherNotes`.
When your evidence disputes a CURRENT owner/operator value, that is a validity `attribution`
concern and the `contested` field must name the backend column (`Owner1`, `Owner2%`,
`Operator`) so the disputed cell — not just the row — gets marked.

STATUS IS LIVE IN THIS BATCH TOO. Three rows are `operating` in the sheet but have plausible
reasons not to be, and a status change is a finding worth as much as any ref:
- **P0266 Trailblazer** — Tallgrass pursued a conversion of Trailblazer out of gas service.
  If the line has been converted to another commodity, an `operating` GAS row is wrong and the
  finding is a `classification` concern, not a length correction.
- **P0248 Ruby** — post-bankruptcy, with public reporting on reduced or suspended service.
- **P0254 Southern Trails** — the western portion has a long history of idling/abandonment
  proposals. Distinguish "the eastern segment operates" from "the pipeline operates".
A line idled, converted or partly abandoned EXISTED — that is a status finding, never an
existence concern. Say which segment your evidence covers.

THE SOURCE LADDER (use it in this order):
1. **FERC** — `elibrary.ferc.gov` and the CP-numbered certificate docket. Almost all of this
   batch is interstate and FERC-jurisdictional: Kern River, Ruby, Rockies Express, Trailblazer,
   Cheyenne Plains, Cheyenne Connector, Colorado Interstate (CIG), Wyoming Interstate (WIC),
   TransColorado, Transwestern, El Paso Natural Gas, Mojave, North Baja, Sierrita, Northern
   Border, Bison, Great Lakes, Viking, Alliance, GTN, Tuscarora, NGPL, Panhandle Eastern,
   Tallgrass Interstate (TIGT), Williston Basin, North Bakken Expansion, Southern Trails.
   A FERC ORDER states mileage by county, diameter, horsepower, added capacity, the cost
   estimate and the in-service date explicitly. The Commission's FINDINGS are one origin
   distinct from the applicant's own filing in the same docket.
2. **Cross-border rows need the OTHER regulator too.** Seven rows cross an international
   border, and the US half is only half the pipeline:
   - **Canada Energy Regulator** (`cer-rec.gc.ca`, 200, fast) for **P0151 Alliance**,
     **P0157 BC/Westcoast**, **P0231 GTN**, **P0278 Viking**, **P2099 Northern Border**,
     **P0316 South Saskatchewan Access**, and the Canadian end of **P0194 Great Lakes**.
     A CER decision is a genuinely INDEPENDENT origin from a FERC order on the same system.
   - **Mexico: CRE / CENAGAS** for **P2568 Norte Crossing**, **P2614 Sierrita Puerto Libertad**,
     **P2615 Sierrita Pima**, and the southern end of **P0226/P2569 North Baja**. A US
     presidential permit / FERC border-crossing order covers only the crossing itself.
3. **STATE regulators** for intrastate lines and for siting — FERC silence is NOT an existence
   concern for an intrastate line. All of these answered 200 when measured (see MEASURED
   CONDITIONS): Colorado PUC `puc.colorado.gov`; ND PSC `psc.nd.gov` (siting jurisdiction over
   ND gas transmission — the right first stop for the Bakken cluster); Montana PSC `psc.mt.gov`;
   Wyoming PSC `psc.wyo.gov`; Arizona Corporation Commission `azcc.gov`; New Mexico PRC
   `nm-prc.org`; CPUC `cpuc.ca.gov`; Oregon PUC `oregon.gov/puc`; Washington UTC `utc.wa.gov`;
   Kansas CC `kcc.ks.gov`; Minnesota PUC `mn.gov/puc`.
4. **PHMSA / NPMS** — use **`www.npms.phmsa.dot.gov`** (200). The bare `npms.phmsa.dot.gov`
   form used in earlier briefs **does not resolve** — do not waste a fetch on it. PHMSA annual
   report mileage by operator ID is a good independent check on a system-length claim.
5. **EIA** — the Natural Gas Pipeline Projects workbook (`.xlsx`) and the state/infrastructure
   pages. It was the single dominant document of batch 3 (41 units) and will be productive
   here. Independent of the operator; good for in-service dates and added capacity.
6. **Operator disclosures** — SEC 10-K/S-1, investor decks, FERC Form 2, tariffs and system
   maps. TC Energy (GTN, Bison, Great Lakes, Northern Border, North Baja, Tuscarora); Kinder
   Morgan (CIG, WIC, TransColorado, EPNG, Mojave, Norte Crossing, Sierrita); Tallgrass (REX,
   Trailblazer, TIGT, Cheyenne Connector); Enbridge (Westcoast); Pembina (Alliance); ONEOK
   (Viking, Northern Border co-owner); WBI Energy / MDU (Williston Basin, Valley Expansion,
   North Bakken Expansion, Doosan Bobcat); Berkshire Hathaway Energy (Kern River); Sempra /
   SoCalGas (Line 1600); NW Natural (North Mist); Xcel Energy (Tungsten to Bobtail); Energy
   Transfer (Transwestern, Panhandle). **One operator is ONE origin across all of its pages,
   microsites and press releases.**
7. Trade press (Natural Gas Intelligence, S&P Global, Reuters, Pipeline & Gas Journal, Hart
   Energy, RBN Energy). Regional papers (Denver Post, Casper Star-Tribune, Bismarck Tribune,
   Williston Herald, Albuquerque Journal, Oregonian) are useful for construction milestones and
   are independent of the operator.

INDEPENDENCE, precisely. FERC's ORDER vs the applicant's own filing IN that docket are ONE
origin — the docket contains the company's numbers. FERC's order vs the company's website IS
two. A CER decision vs a FERC order IS two. A state PUC order vs FERC IS two.
`tcpipelineslp.com` is ONE origin with TC Energy; `pipeline.tallgrassenergylp.com` and
`tallgrassenergylp.com` are ONE origin with Tallgrass; `bisonpipelinellc.com` is ONE origin
with TC Energy; `alliancepipeline.com` is ONE origin with Alliance's owners. The same wire
story republished is one. Anything citing GEM is disqualified.

THE CLUSTERS — get these right before touching anything else:
- **North Bakken Expansion, 5 rows (P3584 / P3585 / P3586 / P3587 / P3588).** One WBI Energy
  FERC project split into five segment rows: Tioga–Elkhorn Creek (62.8 km, 24 in), Line Section
  25 Loop (20.3 km, 12 in), Line Section 30 Loop (9.6 km, 12 in), Tioga Compressor Lateral
  (0.5 km, 20 in), Elkhorn Creek–Northern Border (0.3 km, 24 in). **All five carry the SAME
  `Capacity = 250 MMcf/d`.** That is almost certainly the PROJECT's added capacity restated on
  every segment row — a classic aggregate-on-a-segment `spec` concern. Flag it once, on the
  rows where it is wrong, and do NOT treat the project total as a ref for a segment. All five
  share one FERC docket and one in-service date; the per-segment mileages and diameters come
  from the order's facility description, not from press coverage of "the project".
- **Rockies Express, 2 rows here + 3 already swept in batch 3.** P0246 Main Line
  (1,685 km, 24/36/42 in, 4,050 MMcf/d) and P2517 Cheyenne Hub Enhancement (len 0,
  1,000 MMcf/d). Batch 3 covered P5829 Seneca Lateral, P5830 Zone 3 East-to-West and P5831
  Zone 3 Capacity Enhancement — **P5830's capacity was corrected there from 1800 to 1200
  MMcf/d.** Do not contradict a sibling row without saying so explicitly. P2517's `len 0` is
  correct for a compression-only scope; confirm, do not "fix".
- **Tuscarora, 2 rows.** P0275 Main (305 km, 230 MMcf/d) and P3601 XPress (len 0, 15 MMcf/d).
  The 15 MMcf/d is an INCREMENT; the system figure is not a ref for it.
- **North Baja, 2 rows.** P0226 Main (129 km, 600 MMcf/d) and P2569 NBXP (len 0, 450 MMcf/d,
  2023 in-service). Same increment-vs-system rule.
- **Sierrita, 2 rows here + P2613 already swept in batch 1.** P2614 Puerto Libertad Expansion
  (len 0, 427 MMcf/d) and P2615 Sierrita Pima Expansion (len 0, 320 MMcf/d). **Batch 1 found
  that P2613's `StartState/Province` read `Texas` when the whole route is in ARIZONA** — treat
  any Texas reference on a Sierrita row with suspicion. Both rows here are compression/expansion
  scopes ending in Mexico.
- **The Kinder Morgan Rockies trio: P0168 CIG, P0282 WIC, P0270 TransColorado.** Three separate
  FERC pipelines under one parent, with overlapping geography and interconnects. A CIG system
  document is not a ref for WIC. CIG's `6,920 km` and WIC's `3,900 MMcf/d` are both large
  enough to be system totals — test them.
- **Cheyenne Plains (P0166) and Cheyenne Connector (P0359) are DIFFERENT PIPELINES** that share
  a hub name, a state and a decade. Do not cross-cite them.
- **The Williston/Bakken transmission set: P0158 Bison, P0281 Williston Basin, P2099 Northern
  Border, P0367 Valley Expansion, P3158 Traill County, P0306 Doosan Bobcat, P0316 South
  Saskatchewan Access.** Bison DELIVERS INTO Northern Border; that interconnect is why sources
  discuss them together, and it is not evidence either row duplicates the other.
- **The California import trio: P0207 Kern River, P0219 Mojave, P2552 Line 1600.** Kern River
  and Mojave both terminate in the Bakersfield area and both once sat under El Paso; Line 1600
  is a SoCalGas intrastate line with **blank start AND end states** and a 1949 in-service year.
- **Great Lakes (P0194) and Viking (P0278)** both run US–Canada through Minnesota/Wisconsin
  under different owners. Different systems.

GEOGRAPHY COLUMNS ARE PART OF THIS BATCH, and this slice has the worst of them:
- **P0168 Colorado Interstate: `StartState/Province` = `Rocky Mountains, Anadarko Basin`.**
  Those are BASINS, not states. Same class of scar as batch 3's `New United Kingdom` on P0176,
  and it is NOT a mechanical fix — research the actual origin state and propose that, with a ref.
- **P0273 Transwestern: `EndState/Province` = `Texas-Oklahoma Panhandle, California, Arizona`.**
  "Texas-Oklahoma Panhandle" is a region, not a state, and a pipeline has one terminus per row.
- **P0194 Great Lakes: `EndState/Province` = `Minnesota, Wisconsin, Michigan, Eastern Canada`**
  with a BLANK start state and `StartCountryOrArea = Canada`. "Eastern Canada" is not a state.
- **P2099 Northern Border: `StartState/Province = Montana` but `StartCountryOrArea = Canada`.**
  Montana is not in Canada. One of the two is wrong — settle which with a source that places
  the origin (the border crossing near Port of Morgan is the thing to pin down).
- **Blank state cells: P0208 TIGT (start), P0194 (start), P0222 NGPL (start), P2552 Line 1600
  (both), P2568 Norte Crossing (both), P2614 Sierrita Puerto Libertad (both), P2615 (end).**
- For YOUR row: if either state cell is blank, or holds a basin / region / country instead of a
  state or province, emit a fills[] object with `ref_col: "Location [ref]"`, `value_cols:
  ["StartState/Province", "EndState/Province"]`, the sourced names as values, and a verified ref
  that places the termini (a FERC order's county list, a CER decision, a state siting order, the
  operator's system map). If the cell is filled but your sources disagree, file a validity
  `attribution` concern naming the source and the state it supports — never silently pass it.

LENGTHS THAT LOOK LIKE SYSTEM TOTALS. Several rows carry a `LengthKnown` far larger than the
named route plausibly runs, which is the segment-vs-network defect: **P0222 NGPL 9,100 km**,
**P0168 CIG 6,920 km**, **P0208 TIGT 4,655 km**, **P0273 Transwestern 4,345 km**, **P0151
Alliance 3,848 km**, **P0281 Williston Basin 3,364 km**, **P0157 Westcoast 2,953 km**, **P0194
Great Lakes 2,115 km**. Some of these ARE network rows and the system figure is the RIGHT kind
of ref; others are segment rows carrying a system number. **Decide which kind of row you have
first** (check `SegmentName`, and whether the row is one of several for the same system), then
pick the matching source. Note the sheet stores **kilometres** — batch 3's brief mis-stated a
km value as miles and the agent caught it. Convert explicitly and say so; a mile/km mix-up is
the single most common way a wrong length gets staged.

EXISTENCE / DUPLICATE FLAGS — the bar is high. The likeliest existence/classification questions
in this batch are the small, obscure rows, and "small and obscure" is not evidence of anything:
**P0386 Taproot Baja Pipeline System** (Colorado→Colorado; length, diameter, capacity and start
year ALL blank; owner `Energy Spectrum Securities`, a private-equity name rather than an
operator) is the thinnest row in the batch and the one most likely to be misfiled or misnamed.
**P0306 Doosan Bobcat** (21 km, 12 in, to an industrial customer), **P3158 Traill County**
(63 km at **4-inch** diameter), **P0329 Tungsten to Bobtail** (15 km, 6/8 in, Xcel Energy) and
**P0316 South Saskatchewan Access** (2.0 km) are all small-diameter or very short lines where
the real question is `classification` — transmission vs distribution vs gathering — not
existence. Before you recommend a row be retired, folded or called a phantom:
  (a) NAME THE DOCUMENT you tested and say what it does and does not contain. "The report does
      not mention it" is only evidence if that report would necessarily list it.
  (b) An intrastate line's absence from FERC is EXPECTED and is NOT an existence concern.
      Check the state regulator first (this bites on Line 1600, North Mist, Tungsten to Bobtail,
      Traill County, Doosan Bobcat, Santa Fe Mainline, Taproot Baja).
  (c) Read MAPS, not just full text. A system map or tariff schematic often names a segment the
      prose never does.
  (d) Segment-vs-network granularity: GEM tracks segments and project phases. A source
      describing the whole system is not evidence a phase is duplicated. An aggregate figure
      restated on a phase row is a defect worth flagging, but the PHASE still exists.
  (e) A line idled, converted or partially abandoned EXISTED — status finding, never existence.
State your evidence so a reviewer can check it.

RULES THAT BITE HERE:
- **Never cite GEM.** No gem.wiki / globalenergymonitor.org in any `[ref]`. Visit the wiki page
  for its OUTBOUND citations only.
- **Wikipedia IS citable** as ONE secondary source; an article whose own footnote is GEM cannot
  corroborate. **13 of this batch's 19 harvested `bit.ly` links resolve to en.wikipedia.org** —
  that is 13 pointers to ONE kind of source, not 13 sources.
- **abarrelfull is BANNED** (`abarrelfull.wikidot.com`, `.co.uk`) and so is theodora.com.
  **THREE of this batch's `bit.ly` links resolve to `abarrelfull.wikidot.com`** — on
  **P0266 Trailblazer**, **P0278 Viking** and **P0282 Wyoming Interstate**. The harvester's
  blocklist filters the literal URL and cannot see through a shortener. **Resolve every
  shortener before you open it, and cite the resolved target, never the `bit.ly` form.** If it
  resolves to a banned host, the value it carries is UNSOURCED — chase the footnote instead.
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
  restated on a segment row is a `spec` concern, not a ref. 29 `SegmentCost [ref]` units are
  owed here — expect most of them to end UNRESOLVED honestly rather than filled loosely.
- **Expansion with no new physical pipe -> `LengthKnown = 0`, `Diameter` blank.** Five rows are
  already correct on this (P2517, P2569, P2614, P2615, P3601); CONFIRM rather than "fix".
- **Zero orphan `[ref]` cells in this batch** (there are no filled refs at all), so any orphan
  you create is one you introduced. Never fill a `[ref]` without a paired value.

MEASURED CONDITIONS (2026-09-09) — do not burn budget re-testing these:
  - `elibrary.ferc.gov` returns 200 fast (~0.25 s). `www.ferc.gov` ROOT answers 403 to scripted
    clients, but document paths under `www.ferc.gov/sites/default/files/...pdf` return 200.
  - **`www.eia.gov` answers 503 to a HEAD request but 200 to a GET.** EIA is UP — a 503 from
    `curl -I` is a false negative, do not conclude EIA is down. Fetch it with GET, allow ~8-10 s,
    and batch your EIA reads. `eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects.xlsx`
    is live; download it with `curl -o` and read it locally, never fetch an .xlsx as a page.
  - **`npms.phmsa.dot.gov` DOES NOT RESOLVE. Use `www.npms.phmsa.dot.gov` (200).**
    `www.phmsa.dot.gov` root and its data pages answer 403 to scripted clients — go via Wayback
    or a direct document path.
  - 200 and fast: `cer-rec.gc.ca`, `puc.colorado.gov`, `psc.nd.gov`, `psc.mt.gov`, `psc.wyo.gov`,
    `azcc.gov`, `nm-prc.org`, `cpuc.ca.gov`, `oregon.gov/puc`, `utc.wa.gov`, `kcc.ks.gov`,
    `mn.gov/puc`, `tcenergy.com`, `kindermorgan.com`, `tallgrass.com`, `pembina.com`,
    `enbridge.com`, `nwnatural.com`, `wbienergy.com`, `socalgas.com`.
  - **`bit.ly/2kUPlGj` is DEAD (404)** — it pointed at a retired Kinder Morgan CIG page. That is
    a confirmed 404, so it is genuinely dead rather than blocked; look for the Wayback capture.
  - Existing refs on these rows: **none**. There is no re-verification work in this batch and no
    dead-link triage — every unit is new research.

THE HARVESTED CITATION POOL IS A WORKLIST, NOT A LOOKUP TABLE. 410 citations were harvested
across these 46 wiki pages (321 distinct URLs), and many are 2016-2017 vintage — expect dead
links and go to Wayback rather than dropping the lead. Do not stop at the first sufficient
source and leave the rest of your row's pool unopened. In `researcher_notes`, report HOW MANY of
your row's harvested citations you actually opened, and flag any you could not read and why.

VALUE CONVENTIONS: `*CostUnits` is a BARE currency code (`USD`), never "USD millions".
Controlled vocab is lowercase except `FIDStatus` (`Pre-FID`/`FID`). Capacity is stated in the
sheet's units (`MMcf/d` throughout this batch) — check the worklist unit's column header before
writing a number. Lengths are KILOMETRES. Never fill a `[ref]` without a paired value, or leave
a researched value without a `[ref]`.
No recon legs run for US gas and you never propose route geometry; a route-vs-sheet
disagreement is a validity note, nothing more.
