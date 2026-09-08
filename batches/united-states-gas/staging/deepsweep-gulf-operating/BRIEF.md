SCOPE: US GULF COAST (Louisiana / Mississippi / Alabama / Florida / offshore Gulf of Mexico)
OPERATING gas pipelines, LastUpdated <= 2023. 50 rows = batch 2 of the US stale-operating
cohort (batch 1 was Texas). The slice was cut by ROUTE GEOMETRY, not by the sheet's
StartState/Province column, because that column is blank or not-a-state on 19 of these 50 rows.

CALIBRATION — a blank means NOBODY LOOKED, not that nothing exists.
This cohort's citation base is 25 filled `[ref]` cells against 715 owed
(3.5%), and the owner/operator tab carries ZERO refs for these 50 rows. Read that the way
India/Ukraine were read, NOT the way Pakistan was: an `UNRESOLVED` here is UNFINISHED, not the
correct outcome. Every one of these lines is FERC-, BOEM- or state-regulated and has a public
docket; if you cannot source an operating line's diameter or in-service year, you have not
reached the right register yet.

THE GULF COAST SOURCE LADDER (use it in this order):
1. **FERC** — `elibrary.ferc.gov` and the CP-numbered certificate dockets for INTERSTATE gas.
   Most of this batch is interstate: Florida Gas Transmission, Transco, Tennessee Gas,
   Southeast Supply Header, Gulfstream, Sabal Trail, Texas Gas Transmission, Destin, Midla,
   Chandeleur, Sea Robin, Garden Banks, Nautilus, Mississippi Canyon, Independence Trail,
   Tiger, Kinetica, Creole Trail, TransCameron, AlaTenn. A FERC ORDER states capacity,
   diameter, mileage, compression, cost estimate and the in-service date explicitly, and
   the Commission's own findings are ONE origin distinct from the applicant's website.
   `ferc.gov/industries-data/natural-gas` for project pages; FERC Form 2 for operator data.
2. **BOEM / BSEE** — `data.boem.gov` (Pipeline Permits / Pipeline Segments queries) for any
   line on the Outer Continental Shelf: Garden Banks, Nautilus, Mississippi Canyon,
   Independence Trail, Sea Robin, Chandeleur, Destin, Southeast Supply Header's offshore
   leg. The BOEM segment record gives segment number, diameter, length, product, status
   (ACT / ABN / OUT), approval and abandonment dates — a regulator register independent of
   the operator. **A BOEM status of abandoned / out-of-service on the row's main segments is
   a status finding: file it as a validity `spec` concern with the date, do NOT change the
   Status value.** Gathering lines on the OCS are BOEM-, not FERC-jurisdictional, so FERC
   silence on an offshore line is expected.
3. **State regulators for INTRASTATE lines** — FERC silence is NOT an existence concern for:
   Louisiana intrastate (Acadian, Bridgeline, Louisiana Intrastate Gas, Regency Intrastate
   Gas / RIGS, Tiger's intrastate portion) -> Louisiana DNR Office of Conservation, SONRIS,
   the LA Public Service Commission; Alabama intrastate (Magnolia Intrastate) -> Alabama
   PSC; Mississippi -> Mississippi PSC. Florida Gas Transmission's in-state work also
   surfaces in Florida PSC / Florida DEP dockets and the Florida Siting Board.
4. **PHMSA / NPMS** — `npms.phmsa.dot.gov` for routes and operator identity; PHMSA annual
   report mileage/diameter by operator ID.
5. **EIA** — the Natural Gas Pipeline Projects table and `eia.gov` state / infrastructure
   pages; independent of the operator, good for in-service dates and capacity.
6. **Operator disclosures** — SEC 10-K / S-1, investor decks, tariffs and system maps
   (Kinder Morgan for FGT + Southeast Supply Header + TGP + Sabal Trail; Energy Transfer for
   FGT + Tiger + Gulf coast intrastates; Williams for Transco + Gulfstream; Boardwalk for
   Texas Gas; Enbridge for Nautilus / Garden Banks / Mississippi Canyon / Sabal Trail /
   Gulfstream; Enterprise for Acadian + Independence Trail; EnLink for Bridgeline; Genesis
   Energy for Sea Robin; Cheniere for Creole Trail; Venture Global for TransCameron;
   Kinetica Partners; Boardwalk / Midla). One operator is ONE origin across all its pages.
7. Trade press (Pipeline & Gas Journal, Natural Gas Intelligence, S&P Global, Reuters,
   Offshore Magazine's annual GoM map for subsea lines).

INDEPENDENCE, precisely. FERC + the applicant's own filing IN that FERC docket are ONE
origin — the docket contains the company's numbers. FERC's ORDER vs the company's website
IS two. BOEM's segment record vs the operator's page IS two. The same wire story republished
is one. Anything citing GEM is disqualified.

THE FLORIDA GAS TRANSMISSION CLUSTER — 17 of the 50 rows are FGT rows, 14 of them expansion
phases (Phase IV, V Stages 1-2 / 3 / 4, VI, VII Phase 1, VIII, East Leg, Western Division,
Jacksonville, Sanford, Putnam, Turkey Point Lateral, Alabama Power Lateral, AE Cooperative
Upgrade, Mobile Bay Lateral, East Louisiana, South Alabama, Southwest Alabama). Each phase
has its own FERC certificate proceeding — find THAT docket and its order; the order gives
the miles of loop/lateral by county, the added compression, the added capacity and the
in-service date. Rules that bite: an expansion with NO new physical pipe (compression only)
gets `LengthKnown = 0` and blank `Diameter`; a phase whose numbers are only ever stated as
part of a later phase's total is a duplicate/relabel candidate — check the roster and NAME
the sibling PID; a SYSTEM figure (FGT's 5,000+ miles, its total capacity) is never a ref
for a phase row. The same logic applies to the Acadian family (P0143 system / P3283 Gillis
Lateral / P5709 Haynesville Extension / P5401 its capacity expansion) and the Transco
Hillabee Phase 1 / Phase 2 pair.

STATE COLUMNS ARE PART OF THIS BATCH. The sheet's `StartState/Province` / `EndState/Province`
are blank on 19 rows here (all 14 FGT expansion phases, P2497 TGP Acadiana Expansion, P5401
Acadian Haynesville capacity expansion, P0251 Sea Robin's start) and not-a-state on others
(P0192 Garden Banks and P0204 Independence Trail read `Gulf of Mexico`; P0223 Nautilus reads
`offshore Louisiana`; P0263 Texas Gas reads `Louisana`). Route geometry also disagrees with
the sheet on P0294 Magnolia (sheet ends Mississippi, route ends Alabama), P0175 Destin
(sheet starts Mississippi, route starts offshore Louisiana), P0199 Gulfstream (sheet starts
Alabama, route starts Mississippi), P0159 Bridgeline and P0244 RIGS (sheet Louisiana, route
first vertex Texas). For YOUR row: if either state cell is blank or not a US state /
Mexican or Canadian province, emit a fills[] object with `ref_col: "Location [ref]"`,
`value_cols: ["StartState/Province", "EndState/Province"]`, the sourced state names as
values, and a verified ref that places the termini (a FERC order's county list, a BOEM
segment record's landfall, the operator's system map). If the cell is filled but your
sources disagree with it, file a validity `attribution` concern naming the source and the
state it supports — never silently pass it. The column holds individual STATES (or
Mexican/Canadian provinces); for offshore lines use the landfall state.

RULES THAT BITE HERE:
- **Never cite GEM.** No gem.wiki / globalenergymonitor.org in any `[ref]`. Visit the wiki
  page for its OUTBOUND citations only.
- **Wikipedia IS citable** as ONE secondary source: two language editions of one article
  are ONE source, and an article whose own footnote is GEM cannot corroborate.
- **abarrelfull is BANNED** (`abarrelfull.wikidot.com`, `.co.uk`) and so is theodora.com —
  never, not even alongside corroboration.
- **Never fabricate a URL.** Every URL goes through `scripts/url_verifier.py --name`.
- **A blocked fetch is not a deletion.** 403 / Cloudflare / timeout / geo-block = access
  failure; only a confirmed 404/410 may retire a ref. A blocked origin gets its Wayback
  snapshot ADDED alongside, never swapped in. FERC eLibrary and data.boem.gov are slow and
  sometimes stall — retry, use `curl -sL` with a browser User-Agent, and cite the document's
  own accession / stable URL, never the search page.
- **Cite the ARTICLE, never a navigation surface.** A site root, a search-results page, an
  eLibrary query URL, a paginated index, or a bare host is a MUTABLE surface and fails
  validation.
- **SegmentCost: half of batch 1's researched cost values did not survive primary sources.**
  A cost is `REFS_ADDED` only when a primary source (FERC order estimate, 10-K capitalized
  cost, dated financing) states THAT figure for THAT project scope. A total-project or
  system figure restated on a segment row is a `spec` concern, not a ref. Never derive a
  segment cost from a system total.

EXISTENCE / DUPLICATE FLAGS — the bar is high. Before you recommend that a row be retired,
folded into another, or called a phantom:
  (a) NAME THE DOCUMENT you tested and say what it does and does not contain. "The report
      does not mention it" is only evidence if that report would necessarily list it.
  (b) An intrastate line's absence from FERC, and an OCS gathering line's absence from FERC,
      are EXPECTED and are NOT existence concerns. Check the state regulator / BOEM first.
  (c) Read MAPS, not just full text. A system map or an operator schematic often names a
      segment the prose never does.
  (d) Segment-vs-network granularity: GEM tracks segments and project phases; a source
      describing the whole system is not evidence a phase is duplicated. An aggregate
      figure restated on a phase row is a defect worth flagging, but the PHASE still exists.
  (e) Decommissioned is not non-existent. A GoM line abandoned after a hurricane or idled
      by its operator EXISTED and is a status finding (see the BOEM rule above), never an
      existence concern.
State your evidence so a reviewer can check it.

MEASURED CONDITIONS (2026-09-04) — do not burn budget re-testing these:
  - www.ferc.gov ROOT answers 403 to scripted clients, but document paths under
    `www.ferc.gov/sites/default/files/...pdf` return 200 and pass url_verifier. elibrary.ferc.gov
    returns 200; cite the accession-number document URL, never the search page.
  - www.eia.gov returns 200 but takes ~10 s per fetch — batch your EIA reads; the
    `naturalgas/data.php#pipelines` navigation page cited on 22 of this batch's cells is a
    navigation page, not a ref for any value: name the specific EIA table/workbook instead.
  - data.boem.gov returns 200 (~6.5 s). Enbridge offshore factsheet PDFs (8+ MB) and
    Kinetica's system map PDF return 200 — download with curl and read with pdftotext.
  - sermessenger.energytransfer.com (Sea Robin / Trunkline informational postings) returns 200.
  - `hienergyebb.azurewebsites.net` (old Gulf South/Hi-Energy EBB) does NOT resolve — NXDOMAIN
    is a dead host, so a Wayback capture is the only route to anything hosted there.
  - Existing refs on these rows: 12 units all-live, 13 with dead links, 9 live but the page
    never names the pipeline (`name_found` false) — those 9 are attribution work, not
    re-verification.

THE HARVESTED CITATION POOL IS A WORKLIST, NOT A LOOKUP TABLE. 542 citations were
harvested across these 50 wiki pages. Do not stop at the first sufficient source and leave
the rest of your row's pool unopened. In `researcher_notes`, report HOW MANY of your row's
harvested citations you actually opened, and flag any you could not read and why.

VALUE CONVENTIONS: `*CostUnits` is a BARE currency code (`USD`), never "USD millions".
Controlled vocab is lowercase except `FIDStatus` (`Pre-FID`/`FID`). Capacity is stated in the
sheet's units — check the worklist unit's column header before writing a number. An
expansion with no new physical pipe gets `LengthKnown = 0` and blank `Diameter`. Never fill
a `[ref]` without a paired value, or leave a researched value without a `[ref]`.
No recon legs run for US gas and you never propose route geometry; a route-vs-sheet
disagreement is a validity note, nothing more.
