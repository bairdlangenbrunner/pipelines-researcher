SCOPE: RUSSIA gas, batch R3 of 8 — NORTHWESTERN FEDERAL DISTRICT, IN-DEVELOPMENT LINES
(Komi, Vologda, Leningrad Oblast, Karelia, Pskov, Murmansk) — 27 rows / 413 owed units:
22 proposed, 3 construction (P2313 Gryazovets–Volkhov, P4085 Olonets–Pitkyaranta, P4210
Sheksna…Pudozh Stage IV), 1 shelved (P2437 Ukhta–Cheboksary), 1 cancelled (P5584
Belousovo–Leningrad looping). R1 (Far Eastern, the pilot) and R2 (NW operating) are DONE;
their defects are encoded here as hard rules. R2 swept the OPERATING trunks of this same
district — this batch is the pipe that does not exist yet.

**THIS IS A DIFFERENT KIND OF BATCH FROM R1 AND R2, AND THE DIFFERENCE DECIDES YOUR METHOD.**
R2 was 28 operating Gazprom trunks documented by the operator. R3 is 16 `газопровод-отвод`
branch lines and ГРС feeders off the regional GASIFICATION PROGRAMMES plus 11 transmission
projects, and **14 of the 27 rows carry NOT ONE existing `[ref]` on any researched column.**
The document set is the regional gasification programme, the federal territorial-planning
decree, the oblast government's press service and the Gazprom gasification map — NOT
gazprom.ru project pages, most of which do not exist for a 36-km отвод. Do not go looking
for the R2 source set and conclude a row is undocumented when you have not opened the
Pskov / Karelia / Vologda / Komi programme.

Baird chose 2026-09-14 to deep-sweep every Russia row ONCE with status review ON, sliced by
federal district — this is the ONLY pass these rows get this cycle: do the status work and the
data work together.

THE VERIFICATION OBJECT IS THE DELIVERABLE — THE PILOT'S ONE BIG DEFECT, DO NOT REPEAT IT.
In R1, ~110 fully-researched sourced records shipped as UNRESOLVED and their refs were silently
thrown away, because the `verifications` array was missing or wrongly encoded. The merge keeps a
proposed ref ONLY if some verification object says BOTH `ok: true` AND `contains_value: true` for
that exact URL. A missing key reads as false. `null` reads as false. So:
- Write ONE verification object per proposed ref, every time:
  `{"url": "<exact proposed_refs url>", "ok": true|false, "status": <int>,
    "contains_value": true|false, "name_found": true|false,
    "name_matched": "<the string as it appears on the page>", "note": "<what you saw>"}`
- **`contains_value` means the page STATES the value in any equivalent form — NOT that the literal
  substring appears.** "около 36 км" supports 36 (say "rounding" in the note). "70 млн куб. м в
  год" supports a 0.07 bcm/y cell (show the conversion). "ввод в 2026 году" supports StartYear
  2026. "два отвода общей протяжённостью 82 км" supports NEITHER row's length by itself — say so.
  A note that says the value is supported next to a flag that says false is a DEFECT.
- **`ok` means YOU read the document.** A `url_verifier` name-matcher FAIL on a Cyrillic page that
  you then open and read by hand is `ok: true` with `status: 200`. `ok: false` is reserved for a
  document nobody could open at all.
- `name_found` is owed on every `ok` verification — true or false, never absent, with the matched
  Cyrillic string in `name_matched`. Since 2026-09-15 the verifier romanizes a Cyrillic page and
  requires only the DISTINCTIVE name tokens, so a TRANSLITERATED name (Пустошка ->
  Pustoshka) now matches — but a TRANSLATED one never will, and **a ГРС name is the distinctive
  token on most of these rows** (`ГРС «Пушкинские Горы»` -> Pushkinskiye Gory). Pass the Cyrillic
  name as a `name=` form, and never mark a Russian page "does not name the pipeline" off a
  Latin-name miss you did not check by eye.
- **YOUR STATUS REVIEW WALKS THE SAME FILTER.** The `status_reviews[]` record needs
  `proposed_refs` + one verification object each, keyed exactly as above. If nothing survives the
  filter the merge rewrites your verdict to `unclear` and your proposed Status change is gone. In
  R1, two rows staged live on-point status refs with `contains_value` unset and lost them, and one
  row (P6710) proposed `operating` <- `construction` off four named outlets while staging NO URL at
  all — it named them only in prose. Naming an outlet in `researcher_notes` is not staging a ref.
  A verdict of `change` or `stale`, or any `proposed_changes` on the status record, REQUIRES
  verified URLs. (`validity[]` concerns are different: their refs are carried through unfiltered,
  so an unkeyed validity ref is not lost — but key them anyway, the evidence tab reads them.)
- **A `values` / `proposed_changes` entry is CELL CONTENT, never a recommendation about the cell.**
  R2 shipped `RouteAccuracy: "low — downgrade from high, the stored geometry is a fragment"` into
  a pasteable backend cell. The cell takes `low (subnational, imprecise, or unranked)` and nothing
  else; the reasoning goes in `researcher_notes`. Gate M now blocks this at delivery.
- `scripts/check_shard_coverage.py --pid <PID>` BLOCKS on all of these, `status_reviews[]`
  included. Run it before you finish; a clean run is your finish condition, not your own judgment
  that the row is done.

CALIBRATION — 413 owed units over 27 rows: MISSING_VALUE 172 / MISSING_REF 151 / HAS_REF 90
(54 of the 413 are operator/owner units). **The citation base of this batch is THIN and unevenly
distributed, and that is the single most important number here.** Fourteen rows carry ZERO
HAS_REF units — P3990, P3991, P3992, P4080, P4083, P4085, P4092, P4093, P4109, P4156, P4166,
P4167, P4171, P4172 — and P4149/P4150 carry one apiece. Their gem.wiki pages harvested 2–5
citations each. **Read UNRESOLVED on these rows the way India and Ukraine were read, never the way
Pakistan was: a blank ref here means nobody has looked, not that nothing exists.** The Pskov,
Karelia, Vologda and Komi gasification programmes name these отводы individually, with length,
diameter and commissioning year, in one table. Find the programme and you fill six rows at once.
An UNRESOLVED on one of these rows is only honest if your note names the programme document you
opened and says what it does and does not state.

The builder's up-front HTTP check on the 90 HAS_REF units found 50 all-live, 40 with at least one
failing link, 9 live-but-name-absent (a Cyrillic relevance read is owed on each).
**UNLIKE R2, THIS BATCH HAS FOUR GENUINE 404s** — they are the only refs you may retire:
  P2313 `Fuel [ref]` asninfo.ru/news/101750-…-pervyy-stykk — note the doubled `kk`. The same path
    ending `-pervyy-styk` answers **200** (measured 2026-09-15) and is already cited on P2313's
    `Construction [ref]`. This is a TYPO in the sheet cell, so the fix is the corrected URL, not a
    deletion — re-verify it yourself, then stage it as REFS_ADDED with the typo described.
  P2437 `Fuel [ref]` and `PipelineType [ref]` fzakon.ru/rasporyazheniya-pravitelstva/…-2915-r/
    (fzakon.ru itself answers 200, so the host is fine and the article is gone. The act is
    Распоряжение Правительства РФ от 22.12.2018 N 2915-р — find it on one of the live legal
    mirrors (legalacts.ru, sudact.ru, consultant.ru, base.garant.ru) by SEARCHING the mirror for
    the act number rather than guessing a URL path, then replace. Do not just drop the ref.)
  P4210 `Start [ref]` neftegazpro.ru/genpodryadchiki/… (host answers 200; the article is gone —
    check Wayback, then replace.)
A fifth apparent 404, P2707 `Status [ref]`, is **a malformed cell**: two URLs concatenated without
a separator (`legalacts.ru/doc/rasporjazhenie-…-3302-r-ob-utverzhdenii/` + `://neftegaz.ru/news/
transport-and-storage/866655-13-gazoprovodov-gazproma-…`). Both halves resolve **200**
(measured 2026-09-15); the first is Распоряжение Правительства РФ от 16.11.2024 N 3302-р. Stage the two separated URLs as the corrected refs and say in the note that the stored
cell was malformed — that is REFS_ADDED, not DEAD_LINK.
Every other failing check is an ACCESS FAILURE or a value-screen miss, never a deletion:
403 e-disclosure.ru (7 — deep links only; the root is 200), 401 rbc.ru (6), ConnectTimeout
proektirovanie.gazprom.ru (6) / nadymdobycha.gazprom.ru (2) / ukhta-tr.gazprom.ru (1) /
cher-is.com (1), 403 tass.ru (3 — `tass.com` answers), sudact.ru (4 — the host is 200, retry).
**Fourteen more are `200 but data value not found` — those are AMBER, "re-read this page", not
red.** They are exactly where a prose/unit equivalence lives:
  P2313 Construction (asninfo, 2022), P2313 Diameter (nangs.org, 1420), P2346 Capacity
  (sudact 816-р, 41.2), P2707 + P7537 Length (a Wayback capture of severgazprom.ru, 972.6),
  P4096 Length (rk.karelia.ru, 219 — the check saw only 273 chars of body, the page is
  JS-rendered; re-fetch it properly), P4210 Capacity/Length/Diameter/SegmentCost,
  P5584 Cancelled (2024), P6635 Capacity/Length/Diameter.
Open every one of them and grade it on content.

Fills owed: 172 — by column Pressure 27, FuelSource 25, SegmentCost 24, Construction 24,
Start 19, Operator 17, Diameter 12, Length 11, Capacity 7, Proposal 4, Owner 2; by status
proposed 141, construction 14, cancelled 9, shelved 8. **Pressure is blank on all 27 rows.**
For the 11 transmission rows a Glavgosexpertiza / Gazprom Invest design document states it
(7.5 / 9.8 / 11.8 MPa classes). For the 16 отводы it is often 5.4 or 7.5 MPa and is stated in
the programme table or the ГРС design brief — but if the document set genuinely does not state
pressure for a branch line, UNRESOLVED naming the documents is the correct answer, and saying so
for a whole family once is better than 16 empty notes. **FuelSource is blank on 25 of 27** —
only P2707 and P7537 carry it (`Urengoy gas field, Bovanenkovo gas field`). For a NW отвод the
honest sourced answer is the stream the trunk it taps carries (Vuktyl / Yamal-Bovanenkovo /
Urengoy), which means you must first source WHICH trunk it taps — that is the same research that
fills Location and Operator, so do it once per row. **SegmentCost owed on 24**, and RUB is the
unit: three rows already carry one (P2346 500,000,000,000 RUB; P4094 49,980,000 RUB;
P4210 22,000,000,000 RUB). A programme or a tender notice states these; `SegmentCostUnits`
takes the bare code `RUB`, never "RUB million", with the magnitude in the number.
Harvested pool: 179 citations over 27 of 27 gem.wiki pages fetched.

THE LANGUAGE IS RUSSIAN. There is no FERC/EIA analogue; the record is Gazprom's, the oblast
governments' and the Russian trade press's, almost all in Russian. Search in Russian FIRST — the
sheet's `OtherLanguagePrimaryPipelineName` carries the Cyrillic name for 22 of 27 rows:
  P2313 Газопровод "Грязовец - Волхов"; P2346 Газопровод "Волхов - Мурманск - Белокаменка";
  P2437 Газопровод "Ухта - Чебоксары"; P2707 Газопровод Ухта - Торжок - 3 (III) (Ямал);
  P4080 Газопровод-отвод к г. Устюжна, Вологодская область;
  P4083 Газопровод-отвод ГРС Сокол - ГРС Харовск; P4085 Газопровод-отвод Олонец - ГРС Питкяранта;
  P4092 Газопровод-отвод Приозерск - ГРС «Ихала»;
  P4093 Газопровод-отвод ГРС «Ихала» - ГРС «Сортавала»;
  P4094 Газопровод "Волхов - Медвежьегорск"; P4095 Газопровод "Медвежьегорск - Сегежа";
  P4096 Газопровод "Сегежа - Костомукша"; P4109 Газопровод-отвод и ГРС «Усть-Луга»;
  P4149 Газопровод-отвод Бежаницы - ГPC «Новоржев» Псковской области;
  P4150 Газопровод-отвод ГPC «Новоржев» - ГРС «Пушкинские Горы» Псковской области;
  P4156 Газопровод-отвод ГРС «Пушкинские Горы» - ГРС «Опочка» Псковской области;
  P4166 Газопровод-отвод ГРС Новосокольники - ГРС «Пустошка» Псковской области;
  P4171 Газопровод-отвод Псков - ГРС «Струги Красные» Псковской области;
  P4172 Газопровод-отвод ГРС «Гдов» Псковской области - Сланцы Завод Ленинградской области;
  P4210 Газопровод-отвод к ГРС Pudozh; P6635 Газопровод-отвод Вологда - Череповец;
  P7537 Газопровод Ухта - Торжок - 3 (III) (Ямал).
**Two of those strings are themselves defects you should stage as fills.** P4210's reads
`ГРС Pudozh` — Latin letters inside a Cyrillic name; the correct form is `Газопровод-отвод к ГРС
Пудож`. P4149 and P4150 read `ГPC` with a LATIN capital P and C instead of Cyrillic `ГРС` — so a
site search on the stored string finds nothing. Search the corrected forms, and stage the
corrected `OtherLanguagePrimaryPipelineName` where a source confirms the spelling.
Five rows have NO Cyrillic name — transliterate and search these forms:
  P3990 `КС-12 Усть-Вымь — Часово — Зеленец — Сыктывкар` (КС-12 is КС Микунь);
  P3991 `Выльгорт — Пажга`; P3992 `Пажга — Визинга`; P4167 `Пустошка — Идрица`;
  P5584 `Белоусово — Ленинград` (лупинг / вторая нитка).
Vocabulary that finds the documents: `газопровод-отвод`, `ГРС` (газораспределительная станция),
`межпоселковый газопровод`, `программа развития газоснабжения и газификации` +
`<Псковской|Вологодской|Ленинградской> области` / `Республики Карелия` / `Республики Коми`,
`схема территориального планирования`, `протяжённость … км`, `диаметр … мм`,
`рабочее давление … МПа`, `производительность … млн куб. м в год`, `ввод в эксплуатацию`,
`Главгосэкспертиза`, `положительное заключение`, `распоряжение Правительства РФ`,
`синхронизация`, `догазификация`, `сдан в эксплуатацию`, `построен`.

EVERY WORKLIST UNIT IS OWED A RECORD — INCLUDING THE ALREADY-CITED ONES. 90 of this batch's units
already carry a `[ref]` (class `HAS_REF`). `check_shard_coverage.py` lists a HAS_REF unit with no
record exactly like a skipped blank. For each HAS_REF unit:
- Open the cited URL(s) (the worklist's `current_ref`, and `existing_ref_checks` where the builder
  already HTTP-checked them). Does it resolve, NAME this pipeline/отвод/stage, and STATE the value?
  - Yes -> `class_out: "REVERIFIED"`, `values` = the recorded value, `proposed_refs` = the existing
    ref(s) you re-verified PLUS the second independent source if you found one (the second source
    is still owed — rule 4d), `verifications` for each.
  - Resolves but does not state the value, or does not name the pipeline (a programme's headline
    total on a single-отвод row, a ГРС page, a district news item about "газификация" generally)
    -> the cell is effectively UNCITED: find the document that does state it and stage it as
    REFS_ADDED; if nothing states it, UNRESOLVED saying so. Keep the old ref in `researcher_notes`,
    never silently dropped.
  - Confirmed 404/410 -> `class_out: "DEAD_LINK"` with the Wayback capture if one exists, plus a
    replacement source. **There are exactly four in this batch, named in CALIBRATION, and three of
    them have a live corrected or mirrored URL.** Any other failure — a timeout on a
    `*.gazprom.ru` host, a 403 on `e-disclosure.ru` / `pskov.ru` / `gge.ru`, a 401 on `rbc.ru` —
    is an ACCESS FAILURE: read the page through Wayback or a mirror and grade it on content.
  - The source DISAGREES with the recorded value -> stage the sourced value AND a `spec` concern.
- Where one document re-verifies several HAS_REF cells across SEVERAL ROWS — and in this batch one
  programme table routinely does — say so once, stage it on each unit, and use `cross_row_leads`
  naming the sibling PIDs.
- **The 2015 federal territorial-planning scheme is the most-cited document in this batch and the
  weakest.** `Распоряжение Правительства РФ от 06.05.2015 N 816-р` (mirrored on sudact.ru,
  legalacts.ru, consultant.ru, garant.ru — 20 + 12 + 3 existing refs here) is where P2346's
  41.2 bcm/y, P4210's 0.74 bcm/y, P6635's 4.5 bcm/y and P5584's 2024 come from. It is a PLANNING
  SCHEME from 2015, amended many times since. It is a legitimate ref for a planned figure — cite
  it with its date — but it is **not** current evidence of status, and a 2015 planned capacity that
  no later document repeats is `medium` at best with the vintage stated. Where you use it, check
  whether a later `распоряжение` amends the row's entry (`о внесении изменений в распоряжение …
  816-р`) and cite the amending act too. Several of these rows' statuses hinge on exactly that.

STATUS REVIEW IS ON FOR EVERY ROW (one status_reviews object per row). The whole batch is
in-development, so the question is the same on almost every row: **has this project moved, been
quietly built, or been quietly dropped, since the row was last touched?** LastUpdated on these
rows runs 2023-07 to 2025-08, and 16 of them were last touched in JULY 2023. Three years is long
enough for a 36-km отвод to be built and commissioned without anyone updating the tracker. A
`confirm` verdict needs a source DATED LATER than the row's LastUpdated saying the project is
still where the sheet says it is — say which and give its date. These are the rows carrying a
specific question you must answer, not re-open:
- **P2437 Ukhta–Cheboksary (`shelved`, ShelvedYear 2024, type `confirmed`) — the researcher's own
  note says "Still shelved. Move to Cancelled in the next update" (NF 8/21/25) and, earlier,
  "looks like it was cancelled — excluded from Minenergo's List of the Planned Pipelines."** This
  is the one row in the batch where a status CHANGE is pre-flagged by GEM's own researcher. Settle
  it with documents: is the 920-km Ухта — Чебоксары line absent from the current Minenergo general
  scheme / Gazprom investment programme, and does any act formally cancel it? If yes ->
  `verdict: "change"`, Status `cancelled`, `CancelledYear` + `ShelvedCancelledType` owed with it
  (`confirmed` only if an act says so; `inferred` otherwise, with NO fabricated URL). If the
  documents only show continued silence, that is `confirm` with the silence described — absence
  from a list is evidence, but say which list and which edition.
- **P5584 Belousovo–Leningrad looping (`cancelled`, CancelledYear 2024).** Its only cancellation
  ref is the 2015 planning scheme, which cannot state a 2024 cancellation (the checker flagged
  exactly that: "200 but 2024 not found"). Source the cancellation, or say it is unsourced.
  `ShelvedCancelledType` is BLANK on a cancelled row — it is owed. Note also that **Belousovo is
  in KALUGA OBLAST**, not Leningrad: see STATE CELLS.
- **P2346 Murmansk–Volkhov (`proposed`, StartYear1 2028, ProposalYear 2008, 500 bn RUB).** This is
  the Волхов — Мурманск — Белокаменка line, whose entire rationale is Novatek's Murmansk LNG and
  the Belokamenka yard. Sanctions on Arctic LNG 2 and the Murmansk LNG schedule are the live
  question. Find the newest DATED statement — Gazprom's investment programme, Novatek's
  disclosures, Minenergo, Interfax/TASS/Kommersant — on whether the line is still funded and what
  the current commissioning target is. Do not infer a status from the sanctions narrative; if the
  newest primary statement is 2023, cite it, date it, grade `medium`, and `confirm`.
- **P2313 Gryazovets–Volkhov (`construction`, StartYear1 2023).** GEM's own note says construction
  was "almost complete in Feb 2024" (NF 6/28/24) and that status depends on Ust-Luga. Two years on:
  is it in service? A commissioning announcement moves this to `operating` and is a real change —
  chase it. The Ust-Luga gas processing/LNG complex's own troubles are context, not the pipe's
  status.
- **P4085 Olonets–Pitkyaranta (`construction`, StartYear1 2023) and P4210 Sheksna…Pudozh Stage IV
  (`construction`, StartYear1 2025).** Both are Karelia/Vologda gasification objects with a stated
  commissioning year now in the past. The regional government announces commissioning of each ГРС
  by name — if Питкяранта or Пудож has been gasified, the status is `operating` and the change is
  sourced by the oblast press service. `rk.karelia.ru` and `stolicaonego.ru` answer from here.
- **The 14 zero-ref rows are where a silent completion is most likely.** Пустошка, Идрица,
  Новоржев, Опочка, Струги Красные, Гдов (Pskov); Вылгорт, Пажга, Визинга (Komi); Устюжна, Сокол,
  Харовск (Vologda); Ихала, Сортавала (Karelia). Every one of these is a town whose gasification
  is a local news event. Search `газификация <town>` + `ГРС <town>` + `запущен|введён в
  эксплуатацию` before you write `confirm` on a 2023-vintage `proposed`.
- For every row with a status change, put the new Status in BOTH `status_reviews[].proposed_changes`
  and the Status fill (the two must agree — never stage the old Status as REVERIFIED while your
  status review proposes a new one). A `proposed_changes` value is the bare vocabulary token.

STATE CELLS AND ROUTES — the state audit (`batches/russia-gas/staging/state-audit-20260914/
region_audit.csv`) joined every row's routes-repo geometry to Natural Earth admin-1. **Every row
in this batch came back `OK`** (one `OK_REVERSED`), so unlike R2 there is no geometry-vs-sheet
fight to adjudicate here — but there are two things that still need your judgment:
1. **Spelling typos the audit caught, owed as `Location [ref]` fills.** `Republic of Komi` ->
   `Komi Republic` (P2437, P2707, P3990, P3991, P3992, P7537); `Republic of Chuvashia` ->
   `Chuvash Republic` (P2437 end); `Leningrad region` -> `Leningrad Oblast` (P5584, BOTH cells).
   The spelling is mechanical but the ref is still owed: stage a `Location [ref]` fill with
   `value_cols: ["StartState/Province", "EndState/Province"]` (or just the one that moves) and a
   source that places the termini. Canonical English forms for this batch: `Komi Republic`,
   `Vologda Oblast`, `Leningrad Oblast`, `Republic of Karelia`, `Pskov Oblast`, `Murmansk Oblast`,
   `Chuvash Republic`, `Kirov Oblast`, `Mari El Republic`, `Kaluga Oblast`, `Saint Petersburg`.
2. **P5584 Belousovo–Leningrad is the one probable error.** Both state cells read `Leningrad
   region`, but **Белоусово is a town in Kaluga Oblast** — the Белоусово — Ленинград trunk is a
   ~1,000 km line from the Moscow ring north-west to Leningrad, and its looping cannot start and
   end in Leningrad Oblast. The stored geometry runs Leningrad Oblast -> Saint Petersburg, i.e.
   it is a short segment, not the line. Judge the geometry first, describe its first and last
   points in plain words, then either (a) source the real termini and stage the corrected start
   cell (`Kaluga Oblast`, most likely) as a `Location [ref]` fill, or (b) if the sources show the
   looping really is only the Leningrad-end section, say so and fix the spelling only. If the
   geometry is a fragment of the whole line, that is a `RouteAccuracy` downgrade —
   `contested: {"RouteAccuracy": "<your grade>"}` in a validity concern with "route candidate for
   §8" and the sourced termini. Never edit a state cell to match a bad route, never propose
   coordinates. A route digitized in the reverse direction (P2346 — the audit read it
   Leningrad -> Murmansk against a sheet Murmansk -> Leningrad) is NOT a mismatch; say so once.
3. **`very low (straight line/schematic)` is the honest grade on 12 of these rows and is already
   set.** Do not "upgrade" a route you have not looked at. But where a programme document or the
   Gazprom gasification map shows a real corridor for an отвод currently drawn as a straight line,
   that IS a §8 route-candidate lead — record it in `researcher_notes` with the sourced corridor
   description, never as coordinates.

DUPLICATES AND FAMILIES — get these right before anything else. The sheet itself carries two
explicit duplicate questions in `ResearcherNotes`, and there is a third the notes have not caught:
- **P2707 "Ukhta-Torzhok (Yamal) 3" and P7537 "Ukhta-Torzhok (Yamal) 4" CARRY THE SAME CYRILLIC
  NAME — `Газопровод Ухта - Торжок - 3 (III) (Ямал)` — and the same 972.60 km length.** This is
  the highest-value duplicate suspect in the batch and nobody has flagged it. Either P7537's
  Cyrillic name is simply wrong (it should read `Ухта — Торжок — 4 (IV)`), or the two rows are one
  pipe entered twice. Establish from documents how many Ухта — Торжок strings of the YAMAL
  (Bovanenkovo–Ukhta–Torzhok) system are planned or built beyond the operating pair, and which
  ordinal each row is. Then either (a) stage the corrected `OtherLanguagePrimaryPipelineName` on
  P7537 with its source, or (b) file a `duplicate` validity concern naming both PIDs. Do not
  cross-cite a figure between them until this is settled — and note that R2 already swept the
  OPERATING Ukhta–Torzhok strings (P0767 Yamal I, P1439 Yamal II) and the separate VUKTYL-system
  trio (P5541/P5542/P5543). A source saying "Ухта — Торжок" with no system and no ordinal supports
  NONE of them.
- **P3990 / P3991 / P3992 — GEM's own note on all three says "Look into combining the following 3
  pipelines: CS-12-Ust-Vym-Chasovo-Zelenets-Syktyvkar, Vylgort-Pazhga, Pazhga-Vizinga."** This is
  a live adjudication assigned to this pass. They are the Komi gasification chain south of
  Syktyvkar off КС-12 (КС Микунь) on the Ukhta–Torzhok trunk. Answer it with documents: is the
  Komi programme describing ONE object (`Усть-Вымь — Сыктывкар — Вильгорт — Пажга — Визинга`) or
  three separately-approved отводы with their own lengths and commissioning dates? Whichever it
  is, file it as a `duplicate` validity concern naming all three PIDs with the recommendation, and
  do NOT merge or blank rows yourself. Note P3990's route is graded `low` and the other two
  `very low` — three different grades on what may be one object is itself a signal.
- **P4094 / P4095 / P4096 Volkhov–Segezha–Kostomuksha Stages I / II / III** (Волхов —
  Медвежьегорск 239 km, Медвежьегорск — Сегежа 229 km, Сегежа — Костомукша 219 km). **All three
  carry `CapacityBcm/y = 40.00` and `Diameter = 1400`.** Forty bcm/y is Nord-Stream scale and
  cannot be a Karelia gasification trunk's throughput, and one capacity restated identically on
  three sequential stages is the classic system-figure-on-a-string-row defect this campaign keeps
  finding. Establish what the project's actual design throughput is; if the 40 is a mis-seeded or
  mis-scoped figure, stage the sourced value as a fill AND file a `spec` concern naming all three
  PIDs — and if no document states a per-stage capacity, say so rather than propagating the 40.
  Two further facts on this family: GEM's note cites a Gazprom Invest EPA document
  (`proektirovanie.gazprom.ru/d/textpage/e6/230/proektnaya-dokumentatsiya-10-6.pdf`) putting
  stages I+II at **532 km** against the sheet's 239+229 = 468 km — that host connect-times-out
  from here, so pull the PDF through Wayback and reconcile the discrepancy explicitly. And P4096's
  note records that the project was **not included in Karelia's 2022–2030 gasification programme**
  — check the current programme edition before you `confirm` all three as `proposed`.
- **P4210 Sheksna–Kirillov–Lipin Bor–Vytegra–Pudozh Stage IV is the fourth stage of a family whose
  Stages I / II / III (P4076 Кириллов, P4077 Липин Бор, P4078 Вытегра) WERE SWEPT IN R2** and are
  excluded from this batch. Its gem.wiki page is still titled `Vologda-20-Vytegra_Gas_Pipeline`.
  Stage IV crosses from Vologda Oblast into Karelia to ГРС Пудож, which is why GEM's note says
  "the map is under a different region." One Vologda-programme document usually states all four
  stages — use it, but stage only STAGE IV's own figures on this row, and record the sibling PIDs
  in `cross_row_leads` rather than editing rows that are out of scope. GEM's note also records a
  Yandex Disk folder of detailed schemes (`disk.yandex.kz/d/RJgJwNUQmTj5wQ`); `disk.yandex.ru`
  answers from here. A scheme is a map, not a citation for a number — read it, then cite the
  document that states the number.
- **P4092 Приозерск — ГРС «Ихала» and P4093 ГРС «Ихала» — ГРС «Сортавала»** are consecutive links
  of one Karelia chain (114.5 km and 46 km), as are **P4149 Бежаницы — Новоржев / P4150 Новоржев —
  Пушкинские Горы / P4156 Пушкинские Горы — Опочка** in Pskov and **P4166 Новосокольники —
  Пустошка / P4167 Пустошка — Идрица**. These are NOT duplicates — they are genuine consecutive
  segments of a programme route, each terminating at its own ГРС. One programme table states all
  of them; stage each row's OWN figure, cross-reference by `cross_row_leads`, and never let the
  chain's total length become a segment's length.
- **P4083 ГРС Сокол — ГРС Харовск, P4080 отвод к г. Устюжна, P6635 Вологда — Череповец** are three
  unrelated Vologda objects; P6635 is the biggest (176 km, `700, 1000` multi-diameter, 4.5 bcm/y)
  and is a transmission line, not an отвод.

DISTRIBUTION VS TRANSMISSION — 16 of these 27 rows are `PipelineType = distribution` and this is
the batch where the campaign's open classification question is concentrated (the country note
flags 46 distribution rows tracker-wide). **Flag, do not reclassify.** GEM's researchers have
already written "this is a distribution pipeline as it starts at a gas distribution station"
(P4085), "seems like a distribution pipeline" (P4092), "distribution pipeline" (P4093) — those are
opinions in a notes field, not adjudications. The Russian distinction is crisp and documented: a
`магистральный газопровод` and a `газопровод-отвод` off it are both TRUNK (transmission) assets,
operated by a Gazprom Transgaz subsidiary, running at 5.4–7.5 MPa and terminating AT a ГРС; the
`межпоселковый` and `внутрипоселковый` networks DOWNSTREAM of the ГРС are distribution, operated
by Gazprom Gazoraspredeleniye. A row named "<X> — ГРС <Y>" is the отвод, i.e. the upstream side.
Where the sheet's `distribution` label looks wrong under that test, file a `classification`
validity concern with `contested: {"PipelineType": "transmission"}` and the document that draws
the line — do not stage a PipelineType fill unless a source explicitly classifies the object.
Note that `PipelineType` is also blank on some Russia rows tracker-wide; none in this batch.

LENGTHS AND UNITS. Everything is metric: LengthKnown in km, Diameter in mm (1,420 mm = 56 in;
1,400 = 55; 1,000 = 40; 700 = 28; 500 = 20; 325/300 = 12), Capacity normally in bcm/y (a Russian
source's `млрд куб. м в год`), Pressure in MPa. **Read YOUR row's `CapacityUnits` cell before you
write a capacity — two rows in this batch do not use bcm/y.** P3991 (0.09) and P3992 (0.07) carry
`CapacityUnits = mill.Sm3/day`, so their numbers are million standard m³/DAY, not bcm/year; every
other row in the batch reads `bcm/y`. Converting one into the other silently is the exact defect
that produced GulfPub's miles-as-km error. If a source states `70 млн куб. м в год` for a row
whose units are bcm/y, that is 0.07 bcm/y — show the arithmetic in the note. `млн куб. м в сутки`
-> bcm/y by ×0.365; `тыс. куб. м/ч` by ×0.00876. Multi-value diameters (P6635's `700, 1000`) are
the sheet's convention for a line with sections of different size — a source stating one of them
supports the cell with the other noted, and is not a contradiction.

OWNERSHIP — 54 of the 413 units, and the single most mechanical block of work in the batch.
`Owner` reads `Gazprom PJSC [100.%]` on 25 of 27 rows and is BLANK on exactly two — **P2437
Ukhta–Cheboksary and P5584 Belousovo–Leningrad, the shelved and the cancelled row.** Those are the
two Owner MISSING_VALUE units; a Gazprom investment-programme or planning-scheme entry naming the
проектная организация / заказчик settles them. Sixteen `Owner [ref]` units are MISSING_REF — the
value is there, the citation is not, and rule 4(e) says that is owed exactly as a blank is.
`Operator` is blank on 17 rows and uncited on 10 more. **Leads to verify, not answers:** the
operator of a NW отвод is the Gazprom Transgaz subsidiary whose system it hangs off —
**Gazprom Transgaz Ukhta** for Komi and Vologda (formerly Severgazprom; `severgazprom.ru` is its
predecessor site and connect-times-out, `ukhta-tr.gazprom.ru` likewise — use Wayback) and
**Gazprom Transgaz Saint Petersburg** for Leningrad Oblast, Karelia, Pskov and Murmansk. The
customer-facing regional companies (**Gazprom Mezhregiongaz <region>**, **Gazprom
Gazoraspredeleniye <region>**) own and run the networks PAST the ГРС and are NOT the отвод's
operator — naming one of them as Operator on a trunk row is a defect, so say which side of the
ГРС your source is describing. `mrg.gazprom.ru` connect-times-out; the regional companies'
own sites and the oblast governments answer. Owner/operator work stages onto the
`Gas_OperatorsOwners` tab, ProjectID-keyed, `[ref]` preceding its values; a disputed CURRENT owner
is an `attribution` concern with `contested` naming `Owner1` / `Owner2%` / `Operator`.

THE SOURCE LADDER (in this order — and note it is NOT R2's ladder, because gazprom.ru has no
project page for a 36-km отвод):
1. **The regional gasification programme** — the single highest-yield document set in this batch.
   `Программа развития газоснабжения и газификации <субъекта> на 2021–2025` (and the 2026–2030
   successor) is a Gazprom–region agreement published as a table of named objects with length,
   diameter, ГРС and commissioning year. Get the current edition AND the one in force when the row
   was created: **Pskov** (`pskov.ru` 403 from here — use Wayback and the oblast's
   `Комитет по строительству и ЖКХ` releases), **Karelia** (`gov.karelia.ru` times out but
   `rk.karelia.ru` — the official republic news portal — answers 200 and is already cited on
   P4096), **Vologda** (`vologda-oblast.ru` times out; `newsvo.ru`, `vologda.mk.ru` and
   `vytegra.news` answer), **Leningrad Oblast** (`lenobl.ru` 200), **Komi** (`rkomi.ru` times out;
   `bnkomi.ru` 200). Gazprom's own gasification map **`gazprommap.ru` answers 200 and is the most
   frequently harvested host in this batch (27 citations)** — per-region pages listing the objects.
2. **Federal acts and approvals** — `Распоряжение Правительства РФ … 816-р` (the territorial-
   planning scheme, with its amendments), the Minenergo general scheme, Glavgosexpertiza
   (`gge.ru` 403 — Wayback) per-project approvals naming length/diameter/pressure, and Gazprom
   Invest's project documentation (`proektirovanie.gazprom.ru` times out — Wayback; it holds the
   EPA PDFs, including the P4094/P4095 532-km figure). **The decree texts are mirrored on hosts
   that all answer 200 from here — `legalacts.ru`, `sudact.ru`, `consultant.ru`, `base.garant.ru`,
   `fzakon.ru` — so a `publication.pravo.gov.ru` or `docs.cntd.ru` timeout is never a dead end:
   find the same act on a mirror.** Cite the act by its number and date.
3. **Gazprom corporate** — the annual report's gasification chapter, the investment programme,
   `e-disclosure.ru` (root 200, deep links 403 — Wayback), press releases (`gazprom.ru` times out
   — Wayback, cite live + capture).
4. **Russian trade and regional press** — `neftegaz.ru` (10 refs here, 200), `interfax.ru` (8, 200),
   `tass.ru`/`tass.com`, `dp.ru` (St Petersburg, 200), `asninfo.ru` (construction trade, 200),
   `lentv24.ru` (Leningrad Oblast TV, 200), `stolicaonego.ru` (Karelia, 200), `newsvo.ru` and
   `vologda.mk.ru` (Vologda, 200), `bnkomi.ru` (Komi, 200), `rossaprimavera.ru` (200),
   `nangs.org` (200), `gsprom.ru` (200), `energybase.ru` (200, verifier-checked), `dzen.ru` (200 —
   but Dzen is a BLOG PLATFORM: cite the underlying publisher, not a Dzen repost).
   `rbc.ru` 401 and `rbc.ru` regional subdomains — Wayback. Grade each on what it actually states.
5. **International** — Reuters, Bloomberg, Interfax.com, Upstream, OGJ, S&P/Argus, IEA, OIES.
   For P2346 specifically the Arctic-LNG / Murmansk-LNG coverage is where a dated English second
   source exists. For the отводы there is essentially no English record; do not expect one and do
   not let its absence become UNRESOLVED.
**Weak surfaces already in these cells, to be replaced where you can:** `ppt-online.org`
(P6635 Length + Diameter — a scraped slide deck; find the presentation's source),
`docviewer.yandex.com` (P4210 Length + Diameter — a transient Yandex viewer session URL, not a
stable document; cite the underlying file), `globaldata.com` (a paywalled aggregator).
Cite the ARTICLE or the DOCUMENT, never a navigation surface (site root, search page, tag page,
an interactive map's home page).

INDEPENDENCE, precisely. A Gazprom press release and the Gazprom annual report = ONE origin. The
gasification programme is a JOINT Gazprom–region document, so the programme and a Gazprom release
about it = ONE origin; the programme and the oblast government's own construction-committee
reporting on progress = TWO. Gazprom vs Glavgosexpertiza = TWO. Gazprom vs a federal decree = TWO.
A regional-press piece quoting the governor's press service is the government's origin unless it
adds its own reporting; two regional outlets running the same press-service text are ONE. A Dzen
repost of a TASS item is TASS. Anything citing GEM is disqualified. Sanctions-era thinning: when
the newest primary source is 2021–2023, cite it, state the date, grade `medium` — never
`UNRESOLVED` for a value a dated primary source states.

EXISTENCE / DUPLICATE FLAGS — the bar is high, and this batch is where a wrong flag is cheapest to
file and most damaging. (a) Name the document you tested and what it does and does not contain.
(b) **A small отвод's absence from gazprom.ru is expected and is NOT evidence of non-existence** —
it is evidence you have not opened the regional programme. (c) Read maps and schemes, not just
text (gazprommap.ru, the Yandex Disk schemes on P4210). (d) A programme's headline total restated
on a single-object row is a `spec` defect, but the object exists. (e) An object dropped from a
LATER programme edition is a real status finding (shelved/cancelled), not an existence flag —
P4096 is exactly this case. (f) Two consecutive ГРС-to-ГРС links are not a duplicate; one object
entered under two names is. Flag a duplicate only when the documents describe ONE pipe.

RULES THAT BITE:
- Never cite GEM. abarrelfull, theodora and yingdodo are BANNED (url_verifier rejects them).
- Never fabricate a URL. Every URL goes through `scripts/url_verifier.py --name`. For a Cyrillic
  page pass the Cyrillic name (`--name "Пушкинские Горы"`) and a Cyrillic expected token.
- A blocked fetch is not a deletion; only a confirmed 404/410 retires a ref, and the four in this
  batch are named in CALIBRATION. Add Wayback captures alongside, never swapped in.
- `energybase.ru` serves a 200 geo-block page to some clients — the verifier detects the block
  family; if it flags one, read the Wayback capture and add it ALONGSIDE, never swap.
- SegmentCost (24 owed): REFS_ADDED only when a source states THAT figure for THAT scope in the
  row's currency. `SegmentCostUnits` is the bare code `RUB` (never "RUB million"); a figure given
  in millions goes in as the full number. A USD figure on a RUB row is a `spec` concern with the
  conversion and the rate date noted, not a silent swap. `SegmentCostYear` is owed with a cost.
- An inferred status change gets `ShelvedCancelledType = inferred` and **no URL at all** — never a
  fabricated one.
- Never fill a `[ref]` without a paired value. Never propose a route edit; never write any live
  sheet. Never propose coordinates.

TIMEOUTS. Put a hard timeout on every fetch (`curl --max-time 30`, the verifier's own timeout);
never let one slow host stall the row — the gazprom.ru zone and several `*.gov.ru` hosts hang to
the connect timeout, so go to Wayback FIRST for any `*.gazprom.ru` / `gazprom.com` /
`publication.pravo.gov.ru` / `docs.cntd.ru` URL, and go to a LEGAL MIRROR first for any federal
act. (Shard-saving cadence is Step 0 of your instructions — open the shard before any research and
upsert as you go.)

MEASURED CONDITIONS (2026-09-15, from this machine's US IP, measured against THIS batch's hosts):
- CONNECT-TIMEOUT (no answer; Wayback or a mirror FIRST, cite live + capture):
  `ukhta-tr.gazprom.ru`, `proektirovanie.gazprom.ru`, `mrg.gazprom.ru`, all other `*.gazprom.ru`
  and `gazprom.ru` / `gazprom.com`, `severgazprom.ru`, `gov.karelia.ru`, `vologda-oblast.ru`,
  `rkomi.ru`, `publication.pravo.gov.ru`, `docs.cntd.ru`, `gks.ru`, `cher-is.com`,
  `nadymdobycha.gazprom.ru`, `fas.gov.ru`, `rosneft.ru` (`rosneft.com` answers).
- 403 / 401 (blocked, NOT dead — browser UA, then Wayback): `pskov.ru` 403, `gge.ru` 403,
  `e-disclosure.ru` 403 on deep links (root 200), `rbc.ru` 401, `rg.ru` 401, `tass.ru` 403 on some
  article URLs (`tass.com` answers), `reuters.com` 401, `spglobal.com` 403.
- 200 (read directly): **`gazprommap.ru`**, `neftegaz.ru`, `interfax.ru`, `interfax-russia.ru`,
  `tass.ru` (most), `legalacts.ru`, `sudact.ru`, `consultant.ru`, `base.garant.ru`, `fzakon.ru`,
  `government.ru`, `minenergo.gov.ru`, **`rk.karelia.ru`**, `lenobl.ru`, `bnkomi.ru`,
  `stolicaonego.ru`, `newsvo.ru`, `vytegra.news`, `mk.ru` / `vologda.mk.ru`, `dp.ru`, `asninfo.ru`,
  `lentv24.ru`, `rossaprimavera.ru`, `nangs.org`, `gsprom.ru`, `neftegazpro.ru`, `ppt-online.org`,
  `dzen.ru`, `energybase.ru`, `disk.yandex.ru`, `web.archive.org`, `kommersant.ru`, `ria.ru`,
  `1prime.ru`, `oilcapital.ru`, `iea.org`, `oxfordenergy.org`, `ogj.com`, `themoscowtimes.com`.
- Wayback: check per-page with the CDX API
  (`http://web.archive.org/cdx/search/cdx?url=<url>&limit=5&fl=timestamp,statuscode`), ONE call
  per URL, never a fan-out; the availability API rate-limits after a handful of calls (a 429 or
  empty body is the rate limit, retry later in the run, not a missing capture).

THE HARVESTED CITATION POOL (`wiki_citations.json`, 179 citations over 27 pages) IS A WORKLIST,
NOT A LOOKUP TABLE — and in this batch it is SHORT: 20 rows have five citations or fewer, and
eleven have three or fewer. Opening all of yours is the floor, not the job. Report in
`researcher_notes` how many of your row's harvested citations you opened, which you could not
read, and — because the pool is this thin — what you searched beyond it.

VALUE CONVENTIONS: `*CostUnits` = bare currency code (`RUB` / `USD` / `EUR`). Controlled vocab
lowercase except `FIDStatus` (`Pre-FID` / `FID`); `ShelvedCancelledType` = `inferred` /
`confirmed`; `Status` tokens are lowercase (`proposed`, `construction`, `shelved`, `cancelled`,
`operating`). Capacity, length and diameter in the sheet's units FOR YOUR ROW (check
`CapacityUnits` — P3991 and P3992 are `mill.Sm3/day`, not bcm/y). Federal-subject names in their
English canonical form (above). A GulfPub recon ran standalone for Russia
(`batches/russia-gas/staging/recon-gulfpub-20260914/`); it is NOT an input to your row and
GulfPub is never a `[ref]`.
