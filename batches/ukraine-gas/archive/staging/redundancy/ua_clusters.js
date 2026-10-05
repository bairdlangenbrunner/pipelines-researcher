export const meta = {
  name: 'ua-gas-redundancy-clusters',
  description: 'Ukraine gas §9 step 4 — adjudicate eight duplicate/redundancy clusters against sources',
  phases: [{ title: 'Adjudicate', detail: 'one researcher per structural cluster' }],
}

const REPO = '/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher'
const OUT = `${REPO}/batches/ukraine-gas/staging/redundancy/clusters`
const MODEL = (typeof args !== 'undefined' && args && args.model) || 'sonnet'

const COMMON = `
You are adjudicating ONE structural cluster in Global Energy Monitor's gas pipeline tracker
(GGIT) for UKRAINE. Read-and-report only: you NEVER edit the tracker, the sheet, or any repo file
other than your own output JSON.

## The question you are answering
Do these GEM rows describe ONE physical pipeline recorded more than once (a double count), or
distinct physical pipelines that merely look alike? Decide it on SOURCES, not on structure.

## Discipline that matters more than the answer
1. **Only sourcing decides duplication.** A compelling structural signature — identical lengths,
   one row's length equalling the sum of others, shared endpoints, identical diameters — is a
   HYPOTHESIS. In a comparable Kazakh cluster the sheet's lengths agreed to 0.20 km AND one row's
   drawn route was exactly the concatenation of two others', and the duplicate reading was still
   REFUTED, because two official documents named the row as its own separately-diametered trunk.
   Soviet practice was to build multiple independently-operated parallel strings in one
   right-of-way for hundreds of km. Parallel strings are NOT duplicates.
2. **A REFUTATION is a first-class result.** If you conclude these are distinct lines, say so
   with the same rigour and detail you would use to confirm a duplicate. An unrecorded refutation
   gets re-raised by the next sweep, which is waste.
3. **Corroborate with 2+ INDEPENDENT sources.** The same wire story republished, several outlets
   tracing to one original, two vintages of one publisher's annual report, and anything citing GEM
   all count as ONE origin. Russian state/occupation media reprinting one announcement is ONE
   origin, tier medium at best.
4. **NEVER cite GEM.** Do not use gem.wiki, globalenergymonitor.org, or any GEM surface as a
   source in your output. You MAY read gem.wiki to see what GEM currently claims and to harvest
   the OUTBOUND citations on its pages — then go read and cite those originals directly.
5. **BANNED source: abarrelfull** (abarrelfull.wikidot.com / abarrelfull.co.uk), the wider
   wikidot.com platform, and theodora.com. Never cite them, not even alongside corroboration. If a
   value appears only there, treat it as unsourced and chase the primary source it footnotes.
6. **Never fabricate a URL.** Every URL you report must be one you actually fetched successfully.
   If you cannot verify a source, describe it precisely in prose instead.

## Already fetched for you — do not re-fetch it
Moldovatransgaz's own trunk-line asset list (the pivot source for the Izmail and Ananiv
corridors) is saved verbatim at
${REPO}/batches/ukraine-gas/staging/redundancy/moldovatransgaz_trunks.md — read that file
instead of fetching moldovatransgaz.md. Note the caveat recorded at the top of it: the
lengths there are MOLDOVAN-TERRITORY PORTIONS only, while diameters and capacities are
line properties that carry across the border.

Four more evidence files sit in that same directory and were written by the main loop from
uk.wikipedia and search — read whichever are named in your cluster brief BEFORE searching,
and treat them as leads to corroborate independently, not as settled fact:
- \`kzu_evidence.md\` — «Київ – Захід України»: KZU-1 1970/1020 mm/367 km, KZU-2 1973/1220 mm/506 km (cluster A)
- \`kab_achb_evidence.md\` — «Кременчук–Ананьїв–Богородчани»: 532 km/1020 mm/1986/8.7 bcm (cluster C)
- \`ivatsevichy_evidence.md\` — Торжок–Івацевичі–Долина is a documented THREE-string system (cluster G)
- \`yelets_family_evidence.md\` — «Єлець–Курськ–Диканька» 1220 mm/1984 vs «Єлець–Курськ–Київ» 1982 (clusters F, H)
- \`route_geometry_findings.md\` — vertex counts + drawn-length findings for every clustered row.
  Ukrainian routes are 2–5 vertex SCHEMATICS: a drawn-vs-stated gap is meaningless unless the
  drawn span EXCEEDS the stated length by a wide margin (a schematic is a lower bound on extent).

## Operational note on fetching
Prefer WebSearch + WebFetch. WebFetch CANNOT reach web.archive.org — if you need an archived
copy, use Bash curl with a browser User-Agent instead. Do not spend more than a few attempts
on any single unreachable source: record it as unreachable in prose and move down the ladder.
Return your JSON even if the evidence is thin — UNRESOLVED with a clear account of what you
could and could not establish is a valid, useful result.

## Search technique for Ukraine
Search in Ukrainian AND Russian — the sheet's English transliterations are Soviet-era and English
search finds almost nothing. Useful forms: «газопровід <name>» (uk), «газопровод <name>» (ru), and
the diameter as «Ду 1220» / «DN 1220». Key spellings: Київ/Kyiv; Диканька; Ананьїв; Богородчани;
Шебелинка; Слов'янськ; Кременчук; Ужгород; Роздільна; Ізмаїл; Кривий Ріг; Долина; Єлець (Yelets,
in Russia); Курськ/Курск.

## Source ladder — work down it, do not start with a generic web search
1. **Gas TSO of Ukraine (tsoua.com)** — technical capacity docs, network maps, the ten-year network
   development plan (План розвитку ГТС). NOTE: tsoua.com frequently returns HTTP 403 to automated
   fetches; if so, say so explicitly and recover content via search snippets or an archived copy —
   do NOT treat a 403 as evidence the page is gone.
2. **Ukrtransgaz's own construction chronology** (the operator's line-by-line record of the network
   build, 1960s–1990s) — the single best source for Soviet-era trunk names, lengths and diameters.
3. **ENTSOG** transparency platform and the ENTSOG/GIE System Capacity Map (a copy is in this repo
   at sources/entsog/); Energy Community Secretariat (energy-community.org).
4. **Counterpart TSOs** for cross-border lines: eustream (SK), Gaz-System (PL), Transgaz (RO),
   FGSZ (HU), Moldovatransgaz / Vestmoldtransgaz (MD). Moldovatransgaz's asset list is unusually
   good for the Izmail/Odessa corridors.
5. Ukrainian official: zakon.rada.gov.ua, mev.gov.ua, NEURC/НКРЕКП decisions, ProZorro tenders
   (procurement records name pipelines with km markers and diameters — very high value here).
6. Soviet-era engineering literature for 1950s–1980s build facts.
7. Trade press: Interfax-Ukraine, ExPro Consulting, archived Naftogaz/Ukrtransgaz releases.

## Ownership context you will need
Ukraine's transmission system is STATE-owned; since 1 Jan 2020 the operator is the Gas TSO of
Ukraine (TSOU), not Naftogaz's old Ukrtransgaz. **Gazprom owns no Ukrainian section.** Russian
transit ended 1 Jan 2025, but that is NOT a reason to change any row's Status — the GTS still runs
domestic transmission, storage cycling and reverse-flow imports.

## Verify every URL before you report it
Run, from ${REPO}:
    python scripts/url_verifier.py --url "<url>" --name "<pipeline name>"
A PDF whose text you read locally but which fails the substring check is a documented false
negative — say so. A 403/geo-block/WAF is NOT a dead link; only 404/410 is.

## Output — call StructuredOutput exactly once
Then write the SAME object to ${OUT}/<CLUSTER_ID>.json with the Write tool. Your final text is a
return value, not a message to a human.
`

const SCHEMA = {
  type: 'object',
  required: ['cluster_id', 'title', 'verdict', 'rows', 'sources', 'summary'],
  properties: {
    cluster_id: { type: 'string' },
    title: { type: 'string', description: 'One line naming the cluster and its outcome' },
    verdict: {
      type: 'string',
      enum: ['DUPLICATE_CONFIRMED', 'DUPLICATE_REFUTED', 'PARTIAL_OVERLAP', 'UNRESOLVED'],
    },
    summary: {
      type: 'string',
      description:
        'The structural hypothesis, what you found, and what decided it. If refuted, state plainly '
        + 'what looked compelling and why it is not decisive. 200-600 words.',
    },
    rows: {
      type: 'array',
      description: 'One entry per implicated ProjectID',
      items: {
        type: 'object',
        required: ['project_id', 'concern_type', 'recommendation', 'notes', 'severity'],
        properties: {
          project_id: { type: 'string' },
          concern_type: {
            type: 'string',
            enum: ['duplicate', 'spec', 'attribution', 'classification', 'existence', 'none'],
          },
          recommendation: {
            type: 'string',
            description: 'What Update should DO with this row. Imperative, specific, self-contained.',
          },
          notes: {
            type: 'string',
            description: 'The evidence trail, with the verbatim source wording that decided it.',
          },
          severity: { type: 'string', enum: ['escalate', 'flag', 'info'] },
        },
      },
    },
    sources: {
      type: 'array',
      description: 'Every URL you actually fetched and verified',
      items: {
        type: 'object',
        required: ['url', 'what', 'verified'],
        properties: {
          url: { type: 'string' },
          what: { type: 'string' },
          verified: { type: 'boolean' },
          tier: { type: 'string' },
        },
      },
    },
    open_questions: { type: 'array', items: { type: 'string' } },
  },
}

const CLUSTERS = [
  {
    id: 'A',
    label: 'kyiv-western-border',
    brief: `
## Cluster A — "Kyiv–Western Border": P0777 vs P1480

GEM sheet values:
- **P0777** "Kyiv–Western Border Pipeline" | Kyiv -> Uzhhorod | 1,112.00 km | 1020, 1220 mm |
  capacity blank | StartYear1 1970 | operating. Its own record describes String I = 522 km and
  String II = 590 km.
- **P1480** "Kyiv–Western Border of Ukraine Gas Pipeline" | Kyiv -> (EndLocation BLANK) |
  399.90 km | 1020, 1220 mm | capacity blank | StartYear1 1970 | operating. Its own record
  describes String I = 183.6 km and String II = 216.3 km.

THE HYPOTHESIS (from the operating sweep, both rows independently): these are the same real
system — the Soviet Київ–Західний кордон / КЗУ corridor — recorded twice. Both are two-string
systems with the SAME pattern (String I 1020 mm / 1970, String II 1220 mm / ~1972-73), which
matches КЗУ-1 (1020 mm, 1970) and КЗУ-2 (1220 mm, 1973).

THREE mutually inconsistent totals are in circulation for something of this name:
1,112 km (P0777) / 873 km (367 + 506, per a Ukrainian encyclopaedic article on КЗУ) /
399.9 km (P1480 — and these 399.9 / 1020,1220 mm / 1970,1972 figures reportedly match Ukrtransgaz's
own construction chronology exactly).

WHAT TO SETTLE:
1. What did Ukrtransgaz's chronology actually record for КЗУ-1 and КЗУ-2 — the verbatim lengths
   and diameters? Is 183.6 / 216.3 km in it?
2. Is "Київ–Західний кордон" one system, or a designation reused for more than one corridor?
3. P1480's gem.wiki page claims an endpoint at **Drozdovychi** (Ukraine/Poland border). That is a
   different corridor from Uzhhorod, and it matches this roster's separate P0778
   Komarno–Drozdovychi (800 mm, 80 km). Is the Drozdovychi endpoint corroborated by ANY source, or
   is it an anachronism imported from a modern Poland-interconnector project? P1480's sheet
   EndLocation is blank, so this is a caveat for a future fill, not a live sheet error.
4. If both rows are real, what non-overlapping physical extents do they have? 1,112 + 399.9 =
   1,511.9 km cannot both be full non-overlapping distances if the whole system is 873 km.

Give a specific recommendation for EACH of P0777 and P1480 — including, if you can support it,
which row's numbers should survive.`,
  },
  {
    id: 'B',
    label: 'izmail-corridor',
    brief: `
## Cluster B — the Izmail corridor: P0784 vs P0786 vs P0787

GEM sheet values:
- **P0784** "Shebelinka-Dnipropetrovsk–Kryvyi Rih–Rozdilna-Izmail Gas Pipeline" | Shebelinka ->
  Izmail | **164.00 km** | 1200 mm | 24.00 bcm/y | StartYear1 blank | operating.
- **P0786** "Anan'iv-Tiraspol-Izmail Gas Pipeline" | (start blank) -> Izmail | 257.00 km |
  1200 mm | 23.70 bcm/y | 1968 | operating.
- **P0787** "Rozdilna-Izmail Gas Pipeline" | Rozdilna -> Izmail | 230.00 km | 820 mm | 7.30 bcm/y |
  1975 | operating.

THE HYPOTHESIS (from the operating sweep, raised independently on P0784 and P0787): **P0784 as
recorded is a data-entry artifact straddling three real lines.** The reconstruction offered was:
- 164 km is implausible for a route spanning Shebelinka (Kharkiv Oblast) to Izmail (Odesa Oblast) —
  that is roughly 900 km of country.
- The real corridor's actual named lines are (a) Шебелинка–Дніпропетровськ–Одеса (ШДО/ШДО-2),
  (b) Роздільна–Ізмаїл, 820 mm, commissioned Oct 1973, and (c) Шебелинка–Дніпропетровськ–Кривий
  Ріг–Ізмаїл (ШДКРІ), commissioned 1975 with TWO threads of 800 mm each. GEM's P0784 name is a
  fusion of (c)'s route with (b)'s endpoint.
- P0784's 1200 mm / 24 bcm/y match **P0786** (Anan'iv-Tiraspol-Izmail) almost exactly, not ШДКРІ's
  800 mm.
- The 24 bcm/y traces to an academic table (Gainutdinova 2012) whose row reads «Ананьев - тирасполь
  - Измаил, Шебелинка - Измаил (три нитки) 24» — i.e. an AGGREGATE across BOTH systems, not one
  pipeline's capacity.
- Moldovatransgaz's own asset list gives its transiting section of «Шебелинка-Днепропетровск-Кривой
  Рог-Измаил (ШДКРИ)» a diameter of **820 mm** and **7.3 bcm/y** over 91.817 km — i.e. identical
  specs to GEM's P0787 Rozdilna–Izmail (820 mm / 7.3 bcm/y, Moldovan segment 92.24 km). It gives
  «Ананьев-Тирасполь-Измаил (АТИ)» **1220 mm / 20 bcm/y** separately.

WHAT TO SETTLE:
1. Get Moldovatransgaz's asset list (or the Moldovan gasification-programme document) FIRST HAND
   and quote it verbatim. It is the pivot of this whole cluster.
2. Is ШДКРІ the same physical line as Rozdilna–Izmail over their shared tail, or two lines? If
   Moldovatransgaz assigns the SAME 820 mm / 7.3 bcm/y to both names, GEM's P0784 and P0787 are
   partially or wholly the same pipe.
3. Where does P0784's 164 km come from, and does any source support a 164 km line of that name?
4. Is P0786 genuinely independent of both? (The sweep found it matches a distinct Moldovatransgaz
   line item and does NOT overlap P0787.) Note GEM records P0786 at 1200 mm / 23.70 bcm/y while
   Moldovatransgaz reportedly says 1220 mm / 20 bcm/y — resolve that discrepancy too.

This is the cluster most likely to end in a real DELETE-or-rewrite recommendation. Be correspondingly
careful: a recommendation to delete a row needs sourcing that positively identifies what the row was
built from, not merely an absence of confirmation.`,
  },
  {
    id: 'C',
    label: 'ananiv-bohorodchany',
    brief: `
## Cluster C — Anan'iv–Bohorodchany: P1481 vs P1485

GEM sheet values:
- **P1481** "Ananjiv-Bohorodchani Gas Pipeline" | Ananjiv -> Bohorodchani | 333.00 km | 1020 mm |
  9.10 bcm/y | StartYear1 1987 | operating | Owner: Gas TSO of Ukraine.
- **P1485** "Kremenchuk-Anan'iv-Bohorodchany Gas Pipeline" | Kremenchug -> Ananiev | 532.00 km |
  1020 mm | 8.70 bcm/y | StartYear1 1985 | operating | Owner: **Gazprom PJSC [100%]**.

THE HYPOTHESIS (raised independently on both rows): segment-vs-network double count. P1481's
endpoints are a strict SUBSET of P1485's route, the diameters are identical (1020 mm), the
capacities are near-identical (9.1 vs 8.7 bcm/y), and 532.6 − 333 ≈ 199.6 km is a plausible
Kremenchuk–Anan'iv segment length.

KEY EVIDENCE ALREADY FOUND, which points BOTH ways:
- Ukrtransgaz's own construction chronology names exactly ONE event for this corridor:
  «магістральний газопровід Кременчук - Ананьїв - Богородчани довжиною 532,6 км, ∅1020 мм»
  (1986-87), and records NO separate "Ananiv–Bohorodchany" pipeline anywhere. That argues P1481
  is the duplicate.
- BUT Moldovatransgaz reportedly names «Ананьев-Черновцы-Богородчаны» as ONE specific complete
  cross-border trunk with capacity **9.1 bcm/y** — exactly P1481's capacity — which argues P1481
  is a real, separately-documented line (note the middle waypoint is CHERNIVTSI, which GEM records
  for neither row).

WHAT TO SETTLE:
1. Get the Ukrtransgaz chronology entry first hand and quote it verbatim. Does it mention threads
   or a second line?
2. Get the Moldovatransgaz "Ананьев-Черновцы-Богородчаны" line item first hand. Is it the same pipe
   as the Kremenchuk trunk's western leg, or a distinct line?
3. Is there a real «Ананьїв–Чернівці–Богородчани» trunk distinct from «Кременчук–Ананьїв–
   Богородчани»? Soviet naming often extended a line's name as it was lengthened — which would make
   these one pipe under two names at two dates (1985 vs 1987).
4. P1485 records **Gazprom PJSC at 100%** on a route lying wholly inside Ukraine (Kremenchuk →
   Anan'iv → Bohorodchany are all Ukrainian). That is an ownership-attribution defect independent
   of the duplicate question — report it as its own concern on P1485.
5. P1485's EndLocation is "Ananiev" though its NAME ends at Bohorodchany. Is the row's extent the
   full 532 km trunk or only the Kremenchuk–Anan'iv leg? That single question may resolve the whole
   cluster.`,
  },
  {
    id: 'D',
    label: 'shebelinka-slovyansk',
    brief: `
## Cluster D — Shebelinka–Slovyansk: P3381 vs P3382

GEM sheet values — the two rows carry the IDENTICAL PipelineName:
- **P3381** "Shebelinka–Slovyansk Gas Pipeline" | Shebelinka -> Slovyansk | 70.00 km | **700 mm** |
  StartYear1 **1969** | operating.
- **P3382** "Shebelinka–Slovyansk Gas Pipeline" | (start blank) -> Slovyansk | 54.00 km |
  **500 mm** | StartYear1 **2022** | operating.

WHAT THE SWEEP ESTABLISHED (and it is unusually precise): the Gas TSO of Ukraine's own investment
project replaces the original Ду 700 pipe with a NEW Ду 500 pipe laid PARALLEL to the existing
route («заміна труби Ду 700 ... на трубу Ду 500 ... шляхом прокладки паралельно існуючий трасі»),
in tendered sections UT-1 (km 1.1–13.6), UT-2 (13.6–26.1), UT-3 (26.1–39.9), UT-4 (39.9–55.1) and
UT-5 (55.1–68.0/68.6). The UT-1..UT-4 arithmetic is 12.5 + 12.5 + 13.8 + 15.2 = **54.0 km**, an
exact match to P3382's LengthKnown and its 500 mm diameter. TSOU states the old Ду 700 pipe is to
be DISMANTLED only after the Ду 500 section is commissioned («демонтування існуючого газопроводу
ДУ 700 після прийняття в експлуатацію ділянки Ду 500»).

So this is not a plain duplicate — it is ONE corridor at two points in its life, and both rows are
recorded 'operating'.

WHAT TO SETTLE — the whole cluster turns on one factual question:
1. **Has the Ду 700 dismantling actually happened, and is the Ду 500 replacement complete?** Look
   for ProZorro tender records (e.g. UA-2020-06-10-007174-b for UT-5 construction;
   UA-2019-09-30-000369-a for UT-4/UT-5 supervision), TSOU annual/investment reports for
   2022–2025, and NEURC decisions approving the investment programme. Note this corridor is in
   Kharkiv/Donetsk Oblast, so war damage and occupation may have suspended it — dated evidence
   either way is the deliverable.
2. If the replacement is COMPLETE over km 1.1–55.1, then P3381's 70 km overlaps 54 km of pipe that
   no longer physically exists, and P3381's Status/Length need revising to the surviving stretches
   (roughly km 0–1.1 and km 55.1–70). Say so explicitly if the evidence supports it.
3. If the replacement is PARTIAL or suspended, both rows may legitimately be 'operating' over
   different stretches — but GEM has no km-marker model, so recommend how the two rows should be
   distinguished (SegmentName? ResearcherNotes?).
4. Note P3382's StartYear1 = 2022 against a project tendered from 2019: check what 2022 refers to.
5. Whichever way it goes, the pair currently double-counts length in any roll-up (70 + 54 = 124 km
   of pipe on a 68.6 km corridor). Say so plainly.`,
  },
  {
    id: 'E',
    label: 'taganrog-family',
    brief: `
## Cluster E — the Taganrog family: P1457, P7817, P7818, P5989 (and P1488)

FIVE GEM rows sit on one stretch of occupied-territory coast:
- **P1457** "Taganrog-Mariupol-Berdyansk Gas Pipeline" | Taganrog -> Berdyansk | 516.00 km merged |
  1000 mm | **retired** (2009) — the original Soviet trunk.
- **P7817** same name, SegmentName "Reconstructed Segment (Taganrog-Mariupol)" | Taganrog ->
  Mariupol | 104.50 km merged | 700 mm | **construction**.
- **P7818** same name, SegmentName "Reconstructed Segment (Mariupol-Berdyansk)" | Mariupol ->
  Berdyansk | 68.93 km merged | 500 mm | **proposed**.
- **P5989** "Taganrog-Melitopol-Berdyansk Gas Pipeline" | Taganrog -> Melitopol | 272.73 km merged |
  diameter blank | **operating** since 2024 | Owner blank.
- **P1488** "Kramatorsk-Donetsk-Mariupol Gas Pipeline" | Kramatorsk -> Mariupol | 185.73 km merged |
  1000 mm | operating | 1999.

THE HYPOTHESIS (raised on both P5989 and P7818): P5989's route (Taganrog → Melitopol) necessarily
transits the Mariupol/Berdyansk coastal corridor, so P5989 may double-count the SAME restored trunk
that P7817 + P7818 record as reconstruction segments — under a second, broader-named row, at a
different status.

WHAT IS KNOWN: Russia's plan had TWO parts — (1) restore the pre-existing, then-INACTIVE
(«недействующий») Soviet trunk Taganrog–Mariupol–Berdyansk, and (2) build a genuinely NEW section
Berdyansk–Melitopol, reported at >100 km. Gas reportedly reached Berdyansk 2022-10-25 and Melitopol
2022-10-31. P5989's citations name only Taganrog and Melitopol — neither names Mariupol or
Berdyansk — so the overlap cannot be proved mechanically from them.

WHAT TO SETTLE:
1. Is P5989 the SAME asset as P7817+P7818 (one restored trunk plus a new Berdyansk–Melitopol
   extension, recorded twice at two statuses), or is it a genuinely distinct through-route? Compare
   endpoints, lengths and construction dates side by side. 104.50 + 68.93 = 173.43 km against
   P5989's 272.73 km — is the ~99 km difference the new Berdyansk–Melitopol section?
2. If yes, GEM has one physical corridor recorded as 'construction' + 'proposed' + 'operating'
   simultaneously. That is a status contradiction as much as a duplicate. Recommend the fold.
3. What is P1457's relationship to the others now? A 'retired' 516 km 1000 mm trunk whose route the
   reconstruction reuses — is 516 km even right for Taganrog→Berdyansk (roughly 200 km of coast)?
4. **SOURCE DISCIPLINE IS THE HARD PART HERE.** The only reporting is Russian state or
   occupation-administration output (TASS, RIA, neftegaz.ru, DAN, regional occupation press).
   Those outlets reprint ONE announcement: two of them agreeing is ONE origin, tier medium at best,
   and you must say so in every note. A second INDEPENDENT origin means Ukrainian government,
   Western agency (Reuters/AP), ISW, or Western energy trade press. Report honestly if no second
   origin exists — 'single-origin, medium' is the correct answer where it is true.
5. P5989 has a BLANK Owner and blank diameter while being 'operating'. Flag what a defensible
   Owner would be (the occupying operator is not the Ukrainian TSO, and GEM should not silently
   attribute it to either).`,
  },
  {
    id: 'F',
    label: 'kremenchuk-tail',
    brief: `
## Cluster F — the Kremenchuk tail: P0783 vs P1460 (and P1485)

GEM sheet values:
- **P0783** "Yelets-Kremenchuk–Kryvyi Rih Gas Pipeline" | Yelets -> Kryvyi Rih | 771.00 km |
  1420 mm | 34.68 bcm/y | StartYear1 1986 | operating | Owner includes **Gazprom PJSC**.
- **P1460** "Dikanka-Kremenchuk–Krivyi Rih Gas Pipeline" | Dikanka -> Kryvyi Rih | 272.20 km |
  700 mm | 3.20 bcm/y | operating | Owner: Gas TSO of Ukraine.
- (adjacent) **P1485** "Kremenchuk-Anan'iv-Bohorodchany" | 532.00 km | 1020 mm — see cluster C.

THE HYPOTHESIS: P0783 and P1460 share an IDENTICAL Kremenchuk → Kryvyi Rih tail. Different origins
(Yelets, in Russia, vs Dykanka UGS in Poltava Oblast) and very different diameters (1420 vs 700 mm)
argue against a straight duplicate — but the shared tail routing means GEM may be counting one
right-of-way twice, or P1460 may itself be mislabelled.

Complicating evidence already found:
- A Ukrainian list of the southern transit corridor's main pipelines names Єлець–Кременчук–Кривий
  Ріг, Шебелинка–Дніпропетровськ–Кривий Ріг–Роздільна–Ізмаїл, Кременчук–Ананьїв–Богородчани,
  Ананьїв–Тирасполь–Ізмаїл and Роздільна–Ізмаїл — but NOT a "Диканька–Кременчук–Кривий Ріг" line,
  which is odd if P1460 is a fully separate named trunk.
- GulfPub's reconciliation independently flags a segment "Kremenchuk - Ananyev" (321.9 km) as
  AMBIGUOUS between P0783 and P1485 (composites 0.498 vs 0.465, neither clearing the threshold) —
  the automated matcher cannot separate which GEM row the continuation past Kremenchuk belongs to.

WHAT TO SETTLE:
1. Does a pipeline named «Диканька–Кременчук–Кривий Ріг» exist in any operator or official
   document, at 700 mm / 272.2 km? If it does, P1460 is a real parallel small-bore line and the
   cluster refutes. If it appears nowhere, ask what P1460 was built from.
2. Is Єлець–Кременчук–Кривий Ріг a single 1420 mm trunk of ~771 km? Where does 771 km end — does it
   include the Russian section (Yelets is in Lipetsk Oblast, Russia)? If GEM's length spans both
   countries while the row's own CountriesOrAreas or capacity is Ukraine-only, say so.
3. Note P0783's Owner includes Gazprom PJSC. On a genuinely cross-border row the defensible reading
   is a SPLIT (Russian section Gazprom, Ukrainian section the Ukrainian state) — check what the row
   actually claims and flag if it attributes the whole line to Gazprom.
4. Give a clear recommendation for the shared-tail accounting even if you refute the duplicate.`,
  },
  {
    id: 'G',
    label: 'ivatsevichy-dolyna',
    brief: `
## Cluster G — Ivatsevichy-Kobryn-Dolyna I and II: P3484 vs P5938 (plus the Dolyna hub)

GEM sheet values — these two rows are BYTE-IDENTICAL on every spec except SegmentName and year:
- **P3484** "Ivatsevichy-Kobryn-Dolyna Gas Pipeline" | SegmentName **"I"** | Ivatsevichy -> Dolyna |
  292.00 km | 1220 mm | 29.00 bcm/y | StartYear1 **1976** | operating | Owner: Gazprom PJSC; Gas TSO
  of Ukraine.
- **P5938** same name | SegmentName **"II"** | Ivatsevichy -> Dolyna | 292.00 km | 1220 mm |
  29.00 bcm/y | StartYear1 **1981** | operating | same Owner.

THE HYPOTHESIS: this is the tracker's canonical PARALLEL-STRINGS shape — two independently-built
threads of one Soviet corridor, five years apart, sharing a right-of-way. If so it is NOT a
duplicate and the cluster should REFUTE. But two things need checking before you say so:
1. **Is 29.00 bcm/y a per-string figure or the SYSTEM figure restated on both rows?** This is the
   single most common defect of this shape across the tracker (the same 107.00 MMSCMD appeared on
   five Indian rows; a Kazakh system figure sat on four). If the corridor's total is 29 bcm/y, then
   each string carries roughly half and GEM currently double-counts 29 bcm/y of capacity.
2. **Is 292.00 km genuinely the same for both threads?** Identical to the centimetre for two lines
   built five years apart is possible (same corridor) but worth one source.
3. Ivatsevichy and Kobryn are in **BELARUS**; Dolyna is in Ivano-Frankivsk Oblast, Ukraine. So both
   rows are cross-border. Owner is recorded as "Gazprom PJSC; Gas TSO of Ukraine" — check whether
   the split is stated per-section or whether Gazprom is attributed the whole line. Belarus's
   section belongs to Gazprom Transgaz Belarus (Beltransgaz), which is a THIRD party the rows do not
   name. Flag the attribution.

ALSO IN SCOPE — the **Dolyna hub**. Four other rows terminate at Dolyna:
- **P1462** "Bilche-Wolitz-Dolyna" | Bliche -> Dolyna | 68.00 km | 1400 mm
- **P1463** "Bohorodchany-Dolyna" | Bohorodchany -> Dolyna | 42.00 km | 1400 mm
- **P0779** "Torzhok-Smolensk-Mazyr-Dolyna" | Torzhok -> Dolyna | 1,300.00 km | 1420 mm
Check briefly whether any of these overlaps P3484/P5938 or each other (in particular whether
P0779's 1,300 km Torzhok→Dolyna route subsumes the Ivatsevichy–Kobryn–Dolyna corridor, since
Ivatsevichy sits on the Torzhok–Dolyna path). Do not over-invest here — the I/II question is the
cluster's core; the hub is a secondary check.`,
  },
  {
    id: 'H',
    label: 'yelets-kursk',
    brief: `
## Cluster H — the Yelets–Kursk family: P0775 vs P0776

GEM sheet values:
- **P0775** "Yelets-Kursk-Dykanka Gas Pipeline" | Yelets -> **Dykanka** | **298.00 km** | 1220 mm |
  23.73 bcm/y | StartYear1 **1984** | operating | Owner: **Gazprom PJSC [48.6%]**; Gas TSO of Ukraine.
- **P0776** "Yelets-Kursk-Kyiv Gas Pipeline" | Yelets -> **Kyiv** | **297.00 km** | 1220 mm |
  16.43 bcm/y | StartYear1 **1981** | operating | Owner: **Gazprom PJSC [100%]**; Gas TSO of Ukraine.

THE HYPOTHESIS: two rows sharing an origin (Yelets, Lipetsk Oblast, Russia), a transit node (Kursk),
a diameter (1220 mm) and — most suspiciously — a length that differs by **1 km** while their
destinations are hundreds of kilometres apart. Yelets → Kyiv is roughly 700 km; Yelets → Dykanka
(Poltava Oblast) is roughly 450 km. Neither is ~297 km.

THE MOST LIKELY BENIGN EXPLANATION, which you should test FIRST: 297/298 km is the **Ukrainian-
territory portion** of each line, not the full route length. If GEM's convention here is
in-country length, both rows may be correct and the near-identity is because both cross the border
at roughly the same place. Establish what the 297/298 figures actually measure before calling
anything a duplicate.

WHAT TO SETTLE:
1. Do «Єлець–Курськ–Київ» and «Єлець–Курськ–Диканька» both exist as separately-named Soviet trunks?
   Get lengths and diameters from an operator or official source. (Yelets–Kursk–Kyiv is a
   well-known line; Yelets–Kursk–Dykanka needs confirming.)
2. What do the 297.00 and 298.00 km figures measure — full route, Ukrainian section, or something
   else? Check the rows' own CountriesOrAreas and whether LengthKnownKm here is an in-country
   convention.
3. The capacities differ substantially (23.73 vs 16.43 bcm/y) — is either corroborated?
4. **Ownership is a separate, real concern on both rows.** P0775 records Gazprom at **48.6%** and
   P0776 at **100%**. A precise minority percentage like 48.6% on a Soviet-era trunk is unusual —
   find what it is derived from, if anything. Gazprom owns no Ukrainian section, so on a
   cross-border line the defensible reading is a per-section split, and 100% is wrong for the
   Ukrainian part outright. Report this as its own concern regardless of the duplicate verdict.
5. Adjacent context, worth one check: P0783 "Yelets-Kremenchuk–Kryvyi Rih" (1420 mm, 771 km) shares
   the Yelets origin, and P1453 "Efremovka-Dikanka-Kiev" (1000 mm, 477 km) shares the Dykanka node.
   Say whether either changes the picture; do not adjudicate them here (P0783 is cluster F).`,
  },
]

// `args.only` selects a subset, e.g. {only: ['B','C','D']} — the eight-at-once
// fan-out stalled wholesale on 2026-08-14, so clusters now dispatch in batches.
const ONLY = (typeof args !== 'undefined' && args && args.only) || null
const TODO = ONLY ? CLUSTERS.filter((c) => ONLY.includes(c.id)) : CLUSTERS

phase('Adjudicate')
const results = await parallel(
  TODO.map((c) => () =>
    agent(
      `${COMMON}\n\nYour cluster id is **${c.id}**. Write your output to ${OUT}/${c.id}.json\n${c.brief}`,
      {
        label: `cluster:${c.id}-${c.label}`,
        phase: 'Adjudicate',
        agentType: 'general-purpose',
        model: MODEL,
        schema: SCHEMA,
      },
    ),
  ),
)

const ok = results.filter(Boolean)
log(`clusters adjudicated: ${ok.length}/${TODO.length}`)
return {
  adjudicated: ok.length,
  total: TODO.length,
  verdicts: ok.map((r) => `${r.cluster_id}: ${r.verdict}`),
}
