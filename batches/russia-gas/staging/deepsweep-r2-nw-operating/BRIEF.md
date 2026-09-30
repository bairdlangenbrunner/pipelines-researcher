SCOPE: RUSSIA gas, batch R2 of 8 — NORTHWESTERN FEDERAL DISTRICT, OPERATING AND MOTHBALLED LINES
(Komi, Vologda, Leningrad Oblast, St Petersburg, Karelia, Novgorod, Arkhangelsk, Kaliningrad, Tver)
plus the district's export legs into the Baltic, Belarus/Lithuania, Estonia, Latvia and Finland.
28 rows / 421 owed units: 26 operating and 2 mothballed (P0752 Nord Stream 2, P0753 Nord Stream).
This is the Gazprom Unified System's northwestern corridor — the Yamal and Vuktyl gas streams
coming south-west through Ukhta and Gryazovets to the Baltic and to St Petersburg, plus the
Vologda and Karelia regional gasification branches. R1 (Far Eastern) was the campaign PILOT and
it is done; its defects are encoded in this brief as hard rules (see THE VERIFICATION OBJECT IS
THE DELIVERABLE). Baird chose 2026-09-14 to deep-sweep every Russia row ONCE with status review
ON, sliced by federal district — this is the ONLY pass these rows get this cycle: do the status
work and the data work together.

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
  substring appears.** "1,200 км" supports 1202 km (say "rounding" in the note). "7,5 млрд куб. м
  в год" supports a converted MMcf/d cell (show the conversion). "конец 1960-х" supports
  StartYear 1967. "проектная мощность 55 млрд куб. м" supports Capacity 55. A note that says the
  value is supported next to a flag that says false is a DEFECT.
- **`ok` means YOU read the document.** A `url_verifier` name-matcher FAIL on a Cyrillic page that
  you then open and read by hand is `ok: true` with `status: 200`. `ok: false` is reserved for a
  document nobody could open at all.
- `name_found` is owed on every `ok` verification — true or false, never absent, with the matched
  Cyrillic string in `name_matched`. Since 2026-09-15 the verifier romanizes a Cyrillic page and
  requires only the DISTINCTIVE name tokens, so a TRANSLITERATED name (Средневилюйское ->
  Srednevilyuyskoye) now matches — but a TRANSLATED one never will (`Сила Сибири` is not `Power of
  Siberia` under any fuzz). So pass the Cyrillic name as a `name=` form, and never mark a Russian
  page "does not name the pipeline" off a Latin-name miss you did not check by eye.
- **YOUR STATUS REVIEW WALKS THE SAME FILTER.** The `status_reviews[]` record needs
  `proposed_refs` + one verification object each, keyed exactly as above. If nothing survives the
  filter the merge rewrites your verdict to `unclear` and your proposed Status change is gone. In
  R1, two rows staged live on-point status refs with `contains_value` unset and lost them, and one
  row (P6710) proposed `operating` <- `construction` off four named outlets while staging NO URL at
  all — it named them only in prose. Naming an outlet in `researcher_notes` is not staging a ref.
  A verdict of `change` or `stale`, or any `values` on the status record, REQUIRES verified URLs.
  (`validity[]` concerns are different: their refs are carried through unfiltered, so an unkeyed
  validity ref is not lost — but key them anyway, the evidence tab reads them.)
- `scripts/check_shard_coverage.py --pid <PID>` now BLOCKS on all of these, `status_reviews[]`
  included. Run it before you finish; a clean run is your finish condition, not your own judgment
  that the row is done.

CALIBRATION — 421 owed units over 28 rows: HAS_REF 155 / MISSING_REF 129 / MISSING_VALUE 137
(56 of them operator/owner). The builder's up-front HTTP check on the HAS_REF units found 70
all-live and 84 with at least one failing link — **and NOT ONE of the 95 failed checks is a 404.**
87 are connect-timeouts and 8 are 403s: ukhta-tr.gazprom.ru 40, spb-tr.gazprom.ru 20,
proektirovanie.gazprom.ru 13, krasnodar-dobycha.gazprom.ru 6, cher-is.com 3, vologda-oblast.ru 3,
docs.cntd.ru 1 (timeouts); e-disclosure.ru 8 (403). **Every one of them is an ACCESS FAILURE from
this machine's US IP, not a dead page.** Read them through Wayback or with a browser UA and grade
them on content. `DEAD_LINK` should be close to ZERO in this batch — if you are about to write
one, you are almost certainly retiring a live Gazprom Transgaz page over a connect timeout, which
is forbidden. 33 further checks are live but did not name the pipeline in the Latin fuzzy match —
the Cyrillic relevance read is owed on every one.
Fills owed: 137 (by column: Pressure 28, Proposal 23, SegmentCost 20, FuelSource 18,
Construction 17, Operator 15, Capacity 8, Length 3, Diameter 2, Start 2, Owner 1; by status:
operating 128, mothballed 9). Pressure is blank on all 28 rows — the Gazprom Transgaz Ukhta and
Gazprom Transgaz Saint Petersburg system pages, Glavgosexpertiza approvals and the trunk-line
design documents state it (7.5 / 9.8 / 11.8 MPa classes); this is the single highest-yield fill
column in the batch. FuelSource is blank on 18 — for this corridor the honest answer is usually
`gas` sourced from the field naming the stream (Vuktyl, Yamal/Bovanenkovo, Shtokman where a
document says so), not a guess. Read UNRESOLVED the way India and Ukraine were read, NOT
Pakistan: this is the best-documented Gazprom corridor in Russia and a blank ref means nobody
looked, so UNRESOLVED is unfinished work unless the note names the documents that do not state
the value. Harvested pool: 511 citations over 28 of 28 gem.wiki pages fetched.

THE LANGUAGE IS RUSSIAN. There is no FERC/EIA analogue; the primary record is Gazprom's, its
transgaz subsidiaries', the regional governments' and the Russian trade press's, almost all in
Russian. Search in Russian FIRST — the sheet's `OtherLanguagePrimaryPipelineName` already carries
the Cyrillic name for most of this batch:
  P0746 Газопровод Грязовец–Выборг I нитка; P5585 Газопровод Грязовец–Выборг II нитка;
  P0750 Газопровод "Минск-Вильнюс-Каунас-Калининград"; P0752 Северный Поток - 2;
  P0753 Северный Поток; P0767 Газопровод Ухта - Торжок (Ямал); P1439 Газопровод Ухта - Торжок - 2
  (Ямал); P1456 Газопровод Серпухов - Ленинград; P2312 Кольцевой газопровод Московской области
  (КГМО, вторая нитка); P2326 Газопровод Кохтла-Ярве — Ленинград I нитка;
  P3176 МГП Грязовец - Волхов - Славянская; P4076 Газопровод-отвод к ГРС Кириллов;
  P4077 Газопровод-отвод к ГРС Липин Бор; P4078 Газопровод-отвод к ГРС Вытегра;
  P5534/P5535 Газопровод "Грязовец — Ленинград 1" / "2"; P5539 Газопровод "Пунга — Ухта —
  Грязовец IV"; P5540 Газопровод "Вуктыл - Ухта II"; P7538 Газопровод "Вуктыл - Ухта I";
  P5541/P5542/P5543 Газопровод "Ухта - Торжок 1" / "2" / "3";
  P7559 Газопровод "Волхов-Петрозаводск"; P7560 Газопровод "Петрозаводск-Кондопога".
Three rows have NO Cyrillic name on the sheet — transliterate: P2335/P5590 Ленинград – Выборг –
Госграница (I/II нитка), P5589 Кохтла-Ярве — Ленинград II нитка, P2447 Валдай – Псков – Рига.
Vocabulary that finds the documents: `магистральный газопровод`, `МГ`, `газопровод-отвод`,
`нитка`, `протяжённость … км`, `диаметр 1420 мм` / `DN 1400`, `рабочее давление … МПа`,
`производительность … млрд куб. м в год`, `ввод в эксплуатацию`, `Главгосэкспертиза`,
`положительное заключение`, `компрессорная станция (КС)`, `ГРС` (gas distribution station),
`программа газификации`.

EVERY WORKLIST UNIT IS OWED A RECORD — INCLUDING THE ALREADY-CITED ONES. 155 of this batch's
units already carry a `[ref]` (class `HAS_REF`). `check_shard_coverage.py` lists a HAS_REF unit
with no record exactly like a skipped blank. For each HAS_REF unit:
- Open the cited URL(s) (the worklist's `current_ref`, and `existing_ref_checks` where the builder
  already HTTP-checked them). Does it resolve, NAME this pipeline/segment/нитка, and STATE the value?
  - Yes -> `class_out: "REVERIFIED"`, `values` = the recorded value, `proposed_refs` = the existing
    ref(s) you re-verified PLUS the second independent source if you found one (the second source
    is still owed — rule 4d), `verifications` for each.
  - Resolves but does not state the value, or does not name the pipeline (a system page on a
    нитка row, a field page, a city/ГРС page, an aggregate Gazprom statistic) -> the cell is
    effectively UNCITED: find the document that does state it and stage it as REFS_ADDED; if
    nothing states it, UNRESOLVED saying so. Keep the old ref in `researcher_notes`, never
    silently dropped.
  - Confirmed 404/410 -> `class_out: "DEAD_LINK"` with the Wayback capture if one exists, plus a
    replacement source. **There are no known 404s in this batch** (see CALIBRATION): a timeout on
    `ukhta-tr.gazprom.ru` / `spb-tr.gazprom.ru` / `proektirovanie.gazprom.ru` / any `*.gazprom.ru`
    or `*.gov.ru` host, or a 403 on `e-disclosure.ru`, is an ACCESS FAILURE — read the page
    through Wayback and grade it on its content.
  - The source DISAGREES with the recorded value -> stage the sourced value AND a `spec` concern.
- Where one document re-verifies several HAS_REF cells, say so once and stage it on each.
- The transgaz subsidiary sites (`ukhta-tr.gazprom.ru` 40 refs, `spb-tr.gazprom.ru` 20) are the
  single densest existing-ref source here and they are ALL timing out. Pull their Wayback captures
  early in the run — one CDX call per URL — and work from those; cite the LIVE URL with the
  capture alongside in `proposed_refs`, never swapped in.

STATUS REVIEW IS ON FOR EVERY ROW (one status_reviews object per row).
- **Operating rows (26):** the question is whether each is STILL operating and whether StartYear1
  is right. A clean "still operating" verdict needs a dated source newer than LastUpdated (a
  2024–2026 Gazprom / Gazprom Transgaz Ukhta / Gazprom Transgaz Saint Petersburg page, an annual
  report, a regional gasification report, Interfax/TASS flow reporting) — say which. Post-2022
  disclosure thinning means a 2021–2023 source may be the newest primary one; that is `confirm`
  with the date noted, not `unclear`.
  The export legs need a distinct judgment, because "operating" here means the PIPE, not the flow:
  - **P0746 / P5585 Gryazovets–Vyborg I & II** feed Nord Stream at Portovaya. With Nord Stream
    down since Sept 2022, the pipe is intact and in the system but its export duty is gone. Unless
    a source says the line itself is out of service, it stays `operating` — the flow is NOT the
    status. Say so explicitly in the review so the next pass does not re-litigate it.
  - **P0750 Minsk–Vilnius–Kaunas–Kaliningrad**: Lithuania stopped transit to Kaliningrad in
    2022 and Kaliningrad is supplied by the Marshal Vasilevskiy FSRU. Establish whether the line
    still moves gas at all, and whether that changes its status or only its notes.
  - **P2326 / P5589 Kohtla-Järve–Leningrad I & II**: Estonia ended Russian gas imports in 2022 and
    the Baltic link is disconnected. Is the Russian-side pipe still operating within the domestic
    system? Source it; do not infer a status from the geopolitics.
  - **P2447 Valdai–Pskov–Riga**: Latvia stopped Russian imports Jan 2023. Same question.
  - **P2335 / P5590 Leningrad–Vyborg–State Border I & II**: the Finnish leg (Imatra) stopped
    May 2022. Same question.
  A line that has stopped exporting but remains in the Unified System is `operating`; a line
  physically isolated or abandoned is not. The distinction must come from a document.
- **Mothballed rows (2) — P0753 Nord Stream, P0752 Nord Stream 2:** the highest-stakes status
  judgment in the batch, and the one most likely to be stale. Both were damaged by the Sept 26,
  2022 sabotage. Nord Stream: both strings ruptured. Nord Stream 2: string A ruptured, **string B
  was reported intact and pressurised** — that asymmetry is the fact to source, because it decides
  whether `mothballed` is right for P0752. Nord Stream 2 AG entered Swiss insolvency proceedings
  (moratorium repeatedly extended). Find the newest DATED statement on each: the operator
  (Nord Stream AG / Nord Stream 2 AG), the Danish/Swedish/German investigations, Gazprom's
  disclosures, and the 2024–2026 reporting on the line's legal and physical condition. Then judge
  `mothballed` vs `shelved` vs `cancelled` against the controlled vocab, and if you change it,
  the `ShelvedCancelledType` (`inferred` / `confirmed`) and the year are owed with it. Both rows
  are also missing those cells today — they are owed regardless of whether the status moves.
  Do NOT let a news narrative substitute for a dated source on the pipe's condition.
- For every row with a status change, put the new Status in BOTH `status_reviews[].proposed_changes`
  and the Status fill (the two must agree — never stage the old Status as REVERIFIED while your
  status review proposes a new one).

STATE CELLS AND ROUTES — the state audit (`batches/russia-gas/staging/state-audit-20260914/
region_audit.csv`) joined every row's routes-repo geometry to Natural Earth admin-1. Its findings
are LEADS you must judge, not edits to copy:
1. **Judge the route first.** Is the geometry, at its termini, the right project (not the parent
   system, a sibling нитка, or a different pipeline)? Check it against sourced maps (Gazprom's
   project-page scheme, the transgaz system map, a Glavgosexpertiza approval's route description,
   a regional gasification-programme map). Give the geometry's first and last points in plain
   words in researcher_notes.
2. **Then decide the cells.** Route right + cell wrong -> a fills[] record on `Location [ref]`
   with `value_cols: ["StartState/Province", "EndState/Province"]` and the sourced subjects, plus
   an `attribution` concern with `contested`. Route wrong -> a validity concern
   `contested: {"RouteAccuracy": "<your grade>"}`, the recommendation "route candidate for §8"
   with the sourced termini, and the cells stay as sourced. Both can be wrong. Never edit a state
   cell to match a bad route, never propose coordinates. A route digitized in the reverse
   direction is not a mismatch — say so and move on. EVERY row in this batch is already
   `Mapped route (at any accuracy)` at `high` or `very high`, so a route you find wrong is a
   RouteAccuracy downgrade, which is a real finding — do not wave it through because the grade
   looks confident.
3. **Subject names.** Canonical English federal-subject spellings: `Komi Republic`,
   `Vologda Oblast`, `Leningrad Oblast`, `Saint Petersburg`, `Republic of Karelia`,
   `Novgorod Oblast`, `Arkhangelsk Oblast`, `Kaliningrad Oblast`, `Tver Oblast`,
   `Moscow Oblast`, `Pskov Oblast`, `Khanty-Mansi Autonomous Okrug`. The audit's typos in this
   batch: `Republic of Komi` -> `Komi Republic` (P0767, P1439, P5539, P5540, P5541, P5542, P5543,
   P7538), `Leningrad` -> `Leningrad Oblast` (P0746, P5585), `Leningrad region` ->
   `Leningrad Oblast` (P7559). Stage the corrected spelling as a `Location [ref]` fill with a
   source that places the termini — the spelling is mechanical, the ref is still owed. Foreign
   termini keep their own subject with the country in EndCountry.
This batch's cases:
- **P1456 Serpukhov–Kalinin–Leningrad — BOTH state cells BLANK.** Geometry runs Saint Petersburg
  -> Moscow Oblast through Novgorod, Tver (Kalinin is the Soviet name for Tver) and Kaluga. Source
  the termini and fill both. The name itself tells you the corridor: Serpukhov (Moscow Oblast) ->
  Kalinin/Tver -> Leningrad/St Petersburg.
- **P0750 Minsk–Vilnius–Kaunas–Kaliningrad — start BLANK.** Geometry starts at Minsk (BY) and the
  line traverses Belarus and Lithuania to Kaliningrad Oblast. The Russian row's start is a foreign
  subject (`Minsk Region`/`Grodno Region`, BY) — fill it with StartCountry Belarus if the sources
  place the origin there, and say what the row is scoped to.
- **P0752 / P0753 Nord Stream 2 / Nord Stream — END_MISMATCH.** Sheet says
  `Mecklenburg-Vorpommern`; the audit's geometry terminates back in Leningrad Oblast (P0753's is
  flagged offshore at both ends). These are 1,222/1,230 km OFFSHORE lines from Ust-Luga/Vyborg to
  Lubmin/Greifswald: the sheet's end cell is RIGHT and the audit's read is an offshore-geometry
  artifact. Confirm the landfalls from a source, correct the German spelling to the sheet's
  canonical form only if the sheet's own convention calls for it, and do NOT "fix" the end cell
  to Leningrad Oblast. This is the clearest case in the batch of the audit being wrong and the
  sheet being right — say so in the note.
- **P2326 / P5589 Kohtla-Järve–Leningrad I & II — START_MISMATCH.** Sheet start `Estonia` (a
  COUNTRY in a state cell); geometry starts on the Russian side. Kohtla-Järve is in Ida-Viru
  County, Estonia — so the sourced start subject is `Ida-Viru County` with StartCountry Estonia,
  not the bare string `Estonia`. Fix the cell to the subject, with a source.
- **P2447 Valdai–Pskov–Riga — END_MISMATCH.** Sheet end `Latvia` (again a country in a state cell);
  geometry ends at Riga. The sourced end subject is `Riga` (or the Latvian region the sources
  name), with EndCountry Latvia.
- **P5535 Gryazovets–Leningrad II, P5541/P5542 Ukhta–Torzhok (Vuktyl) I & II, P5585
  Gryazovets–Vyborg II — OK_INTERIOR:** the geometry's endpoints sit inside the traversed set but
  are not the sheet's termini, i.e. the stored route is a SEGMENT of the line, not the whole line.
  Judge whether the geometry is a partial trace (then RouteAccuracy is overstated and the cells
  stay as sourced) or the wrong string. P5534 vs P5535 (Gryazovets–Leningrad 1 vs 2) both carry
  end state BLANK on the sheet — Leningrad Oblast is the sourced answer; fill it.
- **P5540 Vuktyl–Ukhta II and P7538 Vuktyl–Ukhta I — the geometry runs Komi Republic ->
  Khanty-Mansi Autonomous Okrug.** Vuktyl and Ukhta are BOTH in Komi, ~190 km apart. A route
  reaching Khanty-Mansi is the Punga–Vuktyl–Ukhta corridor (the trans-Urals trunk from Western
  Siberia), NOT the 192-km Vuktyl–Ukhta section. Treat this as a probable wrong-route finding:
  grade it, file the validity concern, and source the real termini. The sheet's cells
  (`Komi Republic` -> `Komi Republic`) are likely correct as-is.
- **P5543 Ukhta–Torzhok 3** is the one Ukhta–Torzhok (Vuktyl) string the audit reads as clean
  (Komi -> Tver) — use it as the reference geometry when judging P5541/P5542.

DUPLICATES AND FAMILIES — get these right before anything else. This batch is almost entirely
multi-нитка families, and the pilot's lesson is that a system figure quoted on a string row is the
most common error in Russian sources:
- **Ukhta–Torzhok, TWO DIFFERENT SYSTEMS with confusingly similar names.** (a) **P0767 Ukhta–Torzhok
  (Yamal)** and **P1439 Ukhta–Torzhok 2 (Yamal)**, both 970 km — the Bovanenkovo–Ukhta–Torzhok
  Yamal corridor strings, commissioned 2012 and 2017–2019. (b) **P5541 / P5542 / P5543
  Ukhta–Torzhok (Vuktyl) 1 / 2 / 3** — the older Vuktyl-stream strings, length BLANK on all three
  (and Length is NOT in the owed-fills list for them, so if you source a length it goes in as a
  fill with a `spec` note). Do NOT cross-cite between the Yamal pair and the Vuktyl trio: they
  are different pipe of different vintages sharing a corridor. A source saying "Ухта — Торжок"
  without a system or нитка qualifier supports NEITHER until you establish which it means.
- **Vuktyl–Ukhta: P7538 (I) and P5540 (II), both 192 km, 1982-era.** P5540's Owner cell is EMPTY
  (`--`) while P7538 reads Gazprom PJSC — one of them is wrong or one is genuinely a different
  operator. Owner is an owed fill on exactly one row in this batch; this is it. Source it.
- **Gryazovets–Leningrad: P5534 (I) and P5535 (II), both 609 km.** Identical lengths on I and II —
  confirm each string's OWN year and diameter rather than assuming they match.
- **Gryazovets–Vyborg: P0746 (I, 917 km) and P5585 (II, 680 km).** Different lengths, so the rows
  are not clones; the system feeds Portovaya/Nord Stream. The SYSTEM figure (the ~917-km
  Gryazovets–Vyborg corridor, the 55 bcm/y Nord Stream export capacity) is never a ref for a
  STRING cell.
- **Gryazovets–Volkhov–Slavyanskaya (P3176, 880 km)** is the newer corridor to Ust-Luga (the
  Slavyanskaya CS, built for Nord Stream 2 and the Baltic LNG/GPP complex). Do not cross-cite it
  with the Gryazovets–Vyborg rows.
- **Nord Stream (P0753, 1,222 km) and Nord Stream 2 (P0752, 1,230 km):** two twin-string offshore
  systems, 55 bcm/y each. GEM models each as ONE row for the pair of strings — so a per-string
  figure (27.5 bcm/y, one 1,224-km string) is NOT the row's value; the row carries the system.
  Say which the source states. Owners differ by row and matter: Nord Stream AG (Gazprom 51%,
  Wintershall 15.5%, PEG/E.ON 15.5%, Gasunie 9%, Engie 9%) vs Nord Stream 2 AG (Gazprom 100%, with
  the five European financing partners) — the sheet reads `Gazprom International Projects LLC` on
  P0752; verify the current legal owner given the Swiss insolvency.
- **Kohtla-Järve–Leningrad: P2326 (I, 203 km) and P5589 (II, 114 km).** Different lengths — two
  real strings, not a duplicate.
- **Leningrad–Vyborg–State Border: P2335 (I) and P5590 (II), both 115 km.** Identical lengths;
  this is the Finnish export leg (Vyborg -> Imatra). Confirm each string separately.
- **Sheksna–Kirillov–Lipin Bor–Vytegra–Pudozh: P4076 / P4077 / P4078 = Stages I / II / III**
  (118.4 / 54.8 / 126.5 km) — a Vologda Oblast gasification branch built in stages toward Karelia,
  each stage terminating at its own ГРС (Кириллов, Липин Бор, Вытегра). The stage names are on the
  sheet in Russian; the Vologda government gasification programme and Gazprom Mezhregiongaz
  Vologda are the document set. One programme document usually states all three stages — stage it
  on each sibling via cross_row_leads naming the sibling PID, with each stage's OWN figure.
- **Volkhov–Petrozavodsk–Kondopoga: P7559 (Volkhov–Petrozavodsk, 290 km) and P7560
  (Petrozavodsk–Kondopoga, 56 km)** — the Karelia gasification trunk, two segments of one project.
  Same treatment: one Karelia programme document, two distinct segment figures.
- **P2312 Gryazovets–Ring of the Moscow Region (KGMO), second string, 498 km** — the KGMO ring is a
  Moscow Oblast system; this row is the Gryazovets feed INTO it. A KGMO ring figure is not this
  row's figure.
- **P1456 Serpukhov–Kalinin–Leningrad, 803 km** — a 1950s–60s-era trunk. Its Start year and its
  relationship to the later Gryazovets–Leningrad strings is the thing to establish.

LENGTHS AND UNITS. Everything is metric: LengthKnown in km, Diameter in mm (1,420 mm = 56 in;
1,220 = 48; 1,020 = 40; 720/700 = 28; 530 = 21; 325/300 = 12), Capacity in bcm/y (a Russian
source's `млрд куб. м в год`), Pressure in MPa (7.5 / 9.8 / 11.8 classes — blank on every row in
this batch and the one column a Gazprom/Transgaz page routinely states: look). A source in
`млн куб. м в сутки` converts to bcm/y by ×0.365; `тыс. куб. м/ч` by ×0.00876. Read YOUR row's
units cells before writing a number, and convert into the sheet's unit with the conversion shown
in the note. Multi-value diameters (`1220, 700`) are the sheet's convention for a line with
sections of different size — a source stating one of them supports the cell with the other noted.

OWNERSHIP. Leads to verify, not answers: Gazprom PJSC owns essentially every trunk row here; the
OPERATORS are the transgaz subsidiaries and they differ by corridor — **Gazprom Transgaz Ukhta**
(the Komi/Vuktyl/Yamal corridor: Ukhta–Torzhok, Vuktyl–Ukhta, Punga–Ukhta–Gryazovets, and the
Gryazovets–Vyborg northern leg), **Gazprom Transgaz Saint Petersburg** (Leningrad Oblast, Karelia,
the Baltic export legs, Kohtla-Järve–Leningrad, Leningrad–Vyborg), **Gazprom Transgaz Moscow**
(the KGMO/Serpukhov end). Operator is an owed fill on 15 units — get the right subsidiary per
corridor from the subsidiary's own site (both are timing out; use Wayback) rather than defaulting
to Gazprom PJSC. Special cases: P0753 Nord Stream AG, P0752 Nord Stream 2 AG / Gazprom
International Projects LLC (verify against the Swiss insolvency), P5540 Owner blank (owed).
Owner/operator work stages onto the `Gas_OperatorsOwners` tab; a disputed CURRENT owner is an
`attribution` concern with `contested` naming `Owner1` / `Owner2%` / `Operator`.

THE SOURCE LADDER (in this order):
1. **The operator's own record** — `gazprom.ru` / `gazprom.com` project pages and press releases,
   the transgaz subsidiary sites (`ukhta-tr.gazprom.ru`, `spb-tr.gazprom.ru`,
   `proektirovanie.gazprom.ru` — Gazprom Invest's project pages), Gazprom's annual and
   sustainability reports and IFRS notes (PDFs), Nord Stream AG (`nord-stream.com`) and Nord
   Stream 2 AG (`nord-stream2.com`). **The gazprom.ru zone does not answer from here — read every
   Gazprom page through its Wayback capture**, cite the LIVE URL as the ref with the capture URL
   alongside in `proposed_refs`, and record the capture you read in the verification `note`.
2. **State approvals and programmes** — Glavgosexpertiza (`gge.ru`, per-project approvals naming
   length, diameter, pressure), Minenergo, the FAS tariff orders, and the regional gasification
   programmes and government sites (`vologda-oblast.ru`, `gov.karelia.ru`, `lenobl.ru`,
   `gov.spb.ru`, `rkomi.ru`, `novreg.ru`, `dvinaland.ru`, `gov39.ru` — several blocked from here;
   Wayback). The Gazprom–region gasification agreements (`программа развития газоснабжения и
   газификации`) are the best single source for the Vologda and Karelia branch rows.
3. **Corporate disclosure** — `e-disclosure.ru` (403 on deep links from here; Wayback), Gazprom
   investor presentations, Gazprom Mezhregiongaz regional companies.
4. **Russian trade and regional press** — `neftegaz.ru`, Interfax / interfax-russia.ru, TASS,
   Kommersant, Vedomosti, RBC, RIA, `1prime.ru`, `oilcapital.ru`, `energypolicy.ru`, `peretok.ru`,
   `severpost.ru` and `bnkomi.ru` (Komi), `vologda-poisk.ru` / `newsvo.ru` (Vologda),
   `stolicaonego.ru` (Karelia), `fontanka.ru` and `dp.ru` (St Petersburg), `klops.ru`
   (Kaliningrad). Grade each on what it actually states.
5. **International** — Reuters, Bloomberg, Interfax.com, Upstream, OGJ, S&P/Argus, IEA, OIES
   (the Oxford Institute papers on Nord Stream and Russian gas exports are the best English
   secondary source), and for the Baltic legs the Estonian/Latvian/Lithuanian/Finnish TSOs
   (Elering, Conexus, Amber Grid, Gasgrid) — they document the disconnection dates precisely and
   are genuinely INDEPENDENT of Gazprom, which makes them the best second source in this batch.

INDEPENDENCE, precisely. A Gazprom press release and the Gazprom annual report = ONE origin. A
transgaz subsidiary page and gazprom.ru = ONE origin. Interfax quoting Gazprom's release = the
same origin (say so). Gazprom vs a Glavgosexpertiza approval = TWO. Gazprom vs the Vologda or
Karelia regional government = TWO. Gazprom vs Elering/Conexus/Amber Grid/Gasgrid = TWO, and on
the export legs that pairing is the highest-value `high` tier available. A regional-press piece
quoting the operator's press service is the operator's origin unless it adds its own reporting.
Anything citing GEM is disqualified. Sanctions-era thinning: when the newest primary source is
2021–2023, cite it, state the date, grade `medium` — never `UNRESOLVED` for a value a dated
primary source states.

EXISTENCE / DUPLICATE FLAGS — the bar is high. (a) Name the document you tested and what it does
and does not contain. (b) A Vologda or Karelia gasification branch's absence from gazprom.ru is
expected; look at the regional operator and the regional government. (c) Read maps and schemes,
not just text. (d) Segment-vs-system: an aggregate restated on a нитка row is a `spec` defect,
but the string exists. (e) An identical length on strings I and II is NOT by itself a duplicate
flag — parallel strings genuinely run the same distance. Flag a duplicate only when the documents
describe ONE pipe.

RULES THAT BITE:
- Never cite GEM. abarrelfull, theodora and yingdodo are BANNED (url_verifier rejects them).
- Never fabricate a URL. Every URL goes through `scripts/url_verifier.py --name`. For a Cyrillic
  page pass the Cyrillic name (`--name "Ухта - Торжок"`) and a Cyrillic expected token.
- A blocked fetch is not a deletion; only a confirmed 404/410 retires a ref. Add Wayback captures.
- `energybase.ru` serves a 200 geo-block page to some clients — the verifier detects the block
  family; if it flags one, read the Wayback capture and add it ALONGSIDE, never swap.
- Cite the ARTICLE or the DOCUMENT, never a navigation surface (site root, search results, a tag
  page, an interactive map).
- SegmentCost (20 owed): REFS_ADDED only when a primary source states THAT figure for THAT scope,
  in the sheet's currency — a RUB figure on a USD row is a `spec` concern with the conversion
  noted, not a silent swap.
- Never fill a `[ref]` without a paired value. Never propose a route edit; never write any live sheet.

TIMEOUTS. Put a hard timeout on every fetch (`curl --max-time 30`, the verifier's own timeout);
never let one slow host stall the row — the gazprom.ru zone hangs to the connect timeout, so go to
Wayback FIRST for any `*.gazprom.ru` / `gazprom.com` / `*.gov.ru` URL. (Shard-saving cadence is
Step 0 of your instructions — open the shard before any research and upsert as you go.)

MEASURED CONDITIONS (2026-09-14, from this machine's US IP — measured for R1 and re-checked
against this batch's hosts):
- CONNECT-TIMEOUT (no answer from a US IP; go to Wayback FIRST, cite live + capture):
  www.gazprom.ru, www.gazprom.com, ir.gazprom.ru, **ukhta-tr.gazprom.ru (40 refs here),
  spb-tr.gazprom.ru (20), proektirovanie.gazprom.ru (13)**, krasnodar-dobycha.gazprom.ru,
  gazprominvest.ru, gazprom-invest.ru, www.gazprom-neft.ru, rosneft.ru (rosneft.com 200),
  fas.gov.ru, docs.cntd.ru, rusgasmarket.ru, rostender.info, peretok.ru, cher-is.com,
  www.vologda-oblast.ru, drkuchiev.ru.
- 403 / 401 / 5xx (blocked, NOT dead — browser UA, then Wayback): gge.ru 403, e-disclosure.ru 403
  on deep links (8 refs here), minvr.gov.ru 403, spglobal 403, tass.ru 403 on some article URLs
  (tass.com 200), vedomosti.ru 502, rbc.ru 401, rg.ru 401, reuters.com 401.
- 200 (read directly): interfax.ru, interfax-russia.ru, interfax.com, tass.ru (most), tass.com,
  neftegaz.ru, kommersant.ru, energybase.ru (verifier OK), minenergo.gov.ru, web.archive.org,
  ria.ru, novatek.ru, oilcapital.ru, 1prime.ru, ogj.com, iea.org, oxfordenergy.org, sudact.ru,
  energypolicy.ru, legalacts.ru, upstreamonline.com, forbes.ru, giprogazcentr.com, rosneft.com,
  consultant.ru, garant.ru, themoscowtimes.com, bloomberg.com, argusmedia.com.
- Wayback: check per-page with the CDX API
  (`http://web.archive.org/cdx/search/cdx?url=<url>&limit=5&fl=timestamp,statuscode`), ONE call
  per URL, never a fan-out; the availability API rate-limits after a handful of calls (a 429 or
  empty body is the rate limit, retry later in the run, not a missing capture).

THE HARVESTED CITATION POOL (`wiki_citations.json`, 511 citations over 28 pages) IS A WORKLIST,
NOT A LOOKUP TABLE. Report in researcher_notes how many of your row's harvested citations you
opened, and which you could not read.

VALUE CONVENTIONS: `*CostUnits` = bare currency code (`USD` / `RUB` / `EUR`). Controlled vocab
lowercase except `FIDStatus` (`Pre-FID` / `FID`); `ShelvedCancelledType` = `inferred` /
`confirmed`. Capacity, length and diameter in the sheet's units for your row (km / mm / bcm/y
unless the row says otherwise). Federal-subject names in their English canonical form (above).
A GulfPub recon ran standalone for Russia (`batches/russia-gas/staging/recon-gulfpub-20260914/`);
it is NOT an input to your row and GulfPub is never a `[ref]`.
