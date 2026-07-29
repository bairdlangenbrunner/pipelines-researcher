# Review: NA's Egypt gas additions P8004–P8019 (2026-07-27/28)

Scope: the 16 new rows at the bottom of the GGIT gas tab (SheetRows 4277–4292,
`P8004`–`P8019`, all Egypt, `LastUpdated` 2026-07-27/28), plus three pre-existing
rows she edited with petro-mag citations (`P0473`, `P6033`, `P6686`). Triggered by
BL's doubt about "SUMED Gas Pipeline" (`P8005`).

**Attribution: `NA`** — confirmed 2026-07-29 by reading `Researcher` (col J) on the
live sheet, which now carries `NA` on all 16 rows (plus `P8001`–`P8003`). The column
was **blank** in the 2026-07-28 snapshot this review was built from; the first draft
of this memo guessed the initials from a first name and wrote `NF`, which is a
**different researcher** (NF has 289 gas rows, NA has 428). Corrected throughout.
Rule: never infer a `Researcher` code — read col J, and if it is blank say blank.

Verdict in one line: **most of the pipe is real, but almost none of the rows are
right as entered** — the underlying source is legitimate and I have parsed it, but
the names, several numbers, one whole citation, and the entity boundaries are wrong.

---

## 1. What the cited source actually is

`https://petro-mag.org/ar/Magazine/v?id=<uuid>` is an **issue landing page** for
*مجلة البترول* (Petroleum Magazine), the Egyptian Ministry of Petroleum & Mineral
Resources' own house magazine. The page embeds one link to the full issue PDF.
Two issues are cited across her rows:

| Issue | Landing-page `id` | Direct PDF | Pages | Relevant section |
|---|---|---|---|---|
| **Nov 2025** ("اليوبيل الذهبى" golden-jubilee special, 4th series no. 1) | `b505c5e8-6d88-447d-959d-270acf864417` | `https://petro-mag.org/Uploads/Files/8485d495-066a-4039-af4c-1eb97a28c3ef.pdf` | 146 | GASCO corporate report, **PDF pp. 55–57** (printed pp. 53–54) |
| **Dec 2024** | `d48e45eb-4902-4efe-b07e-c2bee996c9e1` | `https://petro-mag.org/Uploads/Files/1db11fff-b2e2-445c-aa2f-a1c78dbd7c9b.pdf` | 146 | GASCO corporate report, **PDF p. 94** |

Note: her `ResearcherNotes` on `P7325`/`P7914` (oil tracker) call the second one the
"2023/December edition" / "49 edition". It is **December 2024** — the page footer
reads `البترول - ديسمبر 2024`. A third `id=2a56865d-…` is cited on `P6033`, and
`P0473` cites `https://petro-mag.org/ar/Home/Index`, which is the magazine
**homepage** and cites nothing at all.

### How to pull and parse it

```bash
# 1. landing page -> direct PDF link
curl -sL -A "Mozilla/5.0" "https://petro-mag.org/ar/Magazine/v?id=<uuid>" -o issue.html
grep -oE 'href="/Uploads/Files/[^"]+\.pdf"' issue.html

# 2. download (needs a referer; ~25-50 MB per issue)
curl -sL -A "Mozilla/5.0" -e "https://petro-mag.org/" \
  "https://petro-mag.org/Uploads/Files/<file>.pdf" -o issue.pdf

# 3. text layer is good (InDesign, not scanned) -- but RTL + kashida
pdftotext -layout issue.pdf issue.txt
```

**The parsing gotcha:** searching the extracted text for plain Arabic fails. The
magazine justifies text with **kashida/tatweel** (`ـ`, U+0640) inserted *inside*
words — `سونكر` is stored as `ســـونكر`. Strip U+0640, normalize alef/ya/ta-marbuta,
and drop bidi control chars (`unicodedata.category(c) == 'Cf'`) before searching:

```python
def norm(s):
    s = s.replace('ـ', '')
    s = re.sub('[آأإٱ]', 'ا', s)
    s = s.replace('ى', 'ي').replace('ة', 'ه')
    return re.sub('[ً-ْ]', '', s)
```

(Incidentally, the kashida is preserved verbatim in her
`OtherLanguagePrimaryPipelineName` cells — `خط غاز ســـونكر`, `خط غاز أطسـا` — which
is how I confirmed the values were copy-pasted straight out of this PDF. Those
should be de-kashida'd before they go in the sheet.)

---

## 2. What the source actually says

### Nov 2025 issue, GASCO section (PDF pp. 55–56)

**مشروعات التوسع بالشبكة القومية — National-network expansion projects, completed:**

- «الانتهاء من تنفيذ **خط استيراد الغاز من ميناء سوميد بالعين السخنة** قطر 32 بوصة
  بطول 6.1 كم، وتم تدفيع الغاز بتاريخ 2025/6/18»
  → *Completed: the **gas import line from SUMED port at Ain Sokhna**, 32 in,
  6.1 km; gas flowed 18 Jun 2025.*
- «الانتهاء من المرحلة الأولى من **خط استيراد الغاز من رصيف سونكر بالعين السخنة**
  قطر 36 بوصة بطول 9 كم وتدفيع الغاز بتاريخ 2025/7/10، وجارى الانتهاء من المرحلة
  الثانية **بطول 8 كم**»
  → *Phase 1 of the gas import line from the **Sonker jetty at Ain Sokhna**, 36 in,
  9 km, gas flowed 10 Jul 2025; **Phase 2, 8 km**, underway.*
- «الانتهاء من تنفيذ **خط استيراد الغاز من ميناء دمياط** قطر 36 بوصة بطول 3.5 كم
  وتدفيع الغاز بتاريخ 2025/10/23» → *Damietta port gas import line, 36 in, 3.5 km,
  gas flowed 23 Oct 2025.* **Not in GEM.**
- «خط شربين/بلقاس قطر 6 بوصة بطول 0.5 كم … 2025/8/28» → Sherbin/Belqas, 6 in,
  0.5 km. Below any sane add-threshold; correctly skipped.

**المشروعات الجارية — underway:**

- «خط السليمانية شمال الجيزة بطول 20 كم وقطر 42 بوصة» → Solaimaneyah–North Giza,
  42 in, 20 km (= `P6685`).
- «**المشروع الرئاسى حياة كريمة** لتغذية الفيوم الجديدة (قطر 24 بوصة بطول 18.5 كم)،
  ومدينة أطسا (قطر 16 بوصة بطول 9.5 كم)، و**تدعيم** الفيوم القديمة بطول 12 كم»
  → *The presidential **Hayah Karima** ("Decent Life") project: **feeder** to New
  Fayoum (24 in, 18.5 km), Atsa city (16 in, 9.5 km), and **reinforcement** of Old
  Fayoum (12 km).* — **one project, three components** (= `P6686`, `P8011`, `P8012`).
- «خط **ازدواج** عبر سيناء قطر 36 بوصة بطول 27 كم» → *Trans-Sinai **looping**
  ("izdiwāj" = twinning/duplication) line, 36 in, 27 km.*

**المشروعات المستقبلية — future:**

- «خط تغذية محطة بلبيس الجديدة قطر 12 بوصة بطول 505 كم» → New Bilbeis station
  feeder, 12 in, **505 km**. 505 km at 12 in is not credible — almost certainly a
  typo in the magazine (5.05 / 50.5). Correctly not added.
- «إنشاء خط **ازدواج جمصة – إدكو** قطر 42 بوصة بطول 121 كم» → *Gamasa–Edku
  **looping** line, 42 in, 121 km* (= `P8010`).

**Also, decisive for scope:** «تجهيز **موانئ استيراد الغاز المسال** (سوميد – سونكر –
دمياط) بأنظمة اتصالات تبادلية لحظية» → *Equipping the **LNG import ports** (SUMED –
Sonker – Damietta) with real-time comms.* All three "import lines" are **FSRU
send-out connectors**, not standalone transmission pipelines.

Network context worth capturing elsewhere: grid length **8,219 km**, capacity
**270 Mm³/d**; 46.77 bcm delivered in the year, 26.6 bcm to 52 power stations (57%).

### Dec 2024 issue (PDF p. 94) — the cross-check that breaks things

- «تم الانتهاء من تنفيذ مشروع **خط إزدواج عبر سيناء** قطر 36 بوصة بطول **15 كم**
  وتدفيع الغاز فى **2024/6/8**» → completed trans-Sinai loop, 36 in, **15 km**,
  gas 8 Jun 2024.
- «خط ازدواج عبر سيناء بقطر ٣٦ بوصة بطول **٢٨ كم**» (starting) → a *second*
  trans-Sinai loop, 36 in, **28 km**.
- Solaimaneyah, Hayah Karima/New Fayoum/Atsa/Old Fayoum: **word-for-word identical**
  to the Nov 2025 text — i.e. these have been "underway" for ≥11 months with no
  reported progress.
- Grid length **8,279 km**, capacity 262 Mm³/d at end-Sep 2024 — note the Nov 2025
  issue reports 8,219 km, i.e. the network *shrank* 60 km. One of the two is a typo.

---

## 3. Row-by-row verdict

| SheetRow | PID | As entered | Verdict |
|---|---|---|---|
| 4277 | P8004 | Gulf of Suez–SUMED Offshore, 24 in / 12 km, **construction** | ⚠️ Source is `zafmarine.com` (contractor project page, single Tier-3 self-promotion), which says **completed March 2025** → status should not be `construction`. **Duplicate risk with P8005**: likely the subsea leg of the same SUMED-port import system. Adjudicate before keeping both. |
| 4278 | P8005 | **SUMED Gas Pipeline**, 32 in / 6.1 km, operating Jun 2025 | ❌ **Name is wrong, pipe is real.** Numbers all check out against the source. "SUMED" here is the *port/jetty*; SUMED proper is the Arab Petroleum Pipelines Co. **crude** line (the magazine's only other use of سوميد is a 1976 staff biography). Rename → *Ain Sokhna (SUMED Port) Gas Import Pipeline*; it is an FSRU send-out line. BL's `ResearcherNotes` flag stands. |
| 4279 | P8006 | Sonker Ph 1, 36 in / 9 km, operating Jul 2025 | ✅ Values match exactly. Rename to reflect "gas import line from Sonker jetty, Ain Sokhna". |
| 4280 | P8007 | Sonker Ph 2, 36 in / **7 km** | ❌ **Source says 8 km.** Fix `LengthKnown`. |
| 4281 | P8008 | **Sinia** Gas Pipeline 1, 36 in / **15.5 km**, operating 2024-06 | ❌ Three errors: `Sinia`→**Sinai** (also in `StartState/Province`); **15 km** not 15.5; and it is a **loop/twinning** (ازدواج) of the trans-Sinai line, which the name hides. Date 8 Jun 2024 ✓. |
| 4282 | P8009 | Sinia Gas Pipeline 2, 36 in / 27 km, construction | ⚠️ Same naming problems. **27 km (Nov 2025) vs 28 km (Dec 2024)** — unrecorded conflict; she cites the 2025 issue for length and the 2024 issue for `ConstructionYear`, mixing vintages silently. |
| 4283 | P8010 | Edku–Gamasa, 42 in / 121 km, proposed | ✅ Values match. Source names it **Gamasa–Edku** and calls it a **loop**. |
| 4284 | P8011 | Atsa, 16 in / 9.5 km, construction | ✅ Values match, but it is a **Hayah Karima city feeder**, one of three components of one project with `P6686`/`P8012` — needs a `PipelineNetworkGrouping`. `StartLocation = EndLocation = Atsa` conveys nothing. |
| 4285 | P8012 | Old Fayoum, 12 km, no diameter, construction | ⚠️ Source word is **تدعيم = reinforcement** of the existing Old Fayoum network, not a new named pipeline. Diameter correctly left blank. Questionable as a standalone entity — likelier a capacity upgrade. |
| 4286–4292 | **P8013–P8019** | Trans Gulf; Zaafarana–Korimat; Zeit Bay–Ras Shukheir; Ras Shukheir–Suez Trunkline; Suez–Cairo Ring; Suez–Port Said; Damanhur–Tanta | ❌ **Citation is not a source.** `https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt` is a **site search-results page** — unstable, and contains no pipeline data. See §4. |

### §4 — the P8013–P8019 citation problem

The article she was actually working from is **"Egypt's Gas Distribution Network, An
Intricate Economic Web"** (Egypt Oil & Gas, 15 Jul 2024):
`https://egyptoil-gas.com/features/egypts-gas-distribution-network-an-intricate-economic-web/`

I read it in full. It is prose, with **no table**. Everything it contains at
pipeline level is:

- Gulf of Suez→Sinai: "**seven** natural gas pipelines with a total capacity of
  approximately **835.8 mmcf/d**", of which it *names* only Trans Gulf Gas and
  Zaafarana–Korimat, feeding Ras Bakr Transmission Station and Korimat Power Station.
- Nile Delta/Cairo/Nile Valley: "**10** main pipelines, total length **612 km**,
  total capacity **2,200 mmcf/d**", naming Abu Madi-Talkha I & II, Talkha-Tanta-Cairo,
  Abu Madi-Damietta, Meadia-Damanhur, Alexandria Network-Damanhur, Damanhur-Tanta,
  **Cairo Ring-Port Said Line**, Korimat-Al Tebbin, Korimat-Beni Suef.
  "The **Damanhur-Tanta** line has the largest natural capacity with **700.1 mmcf/d**."
- Western Desert: seven pipelines, 514 km, 2,892 mmcf/d; Tarek-Amerya 950 mmcf/d,
  231 km.
- All aggregates attributed upstream to **Wood Mackenzie** via an internal
  "Egypt Oil & Gas Research & Analysis report".

So of her seven rows, **exactly one number is traceable** to the cited work:
`P8019` Damanhur–Tanta = 700.1 mmcf/d. Every other length, diameter and capacity
(`P8013` 110/75 km, `P8014` 105/163 km, `P8015` 140/40 km, `P8016` 160/256 km,
`P8017` 90/150 km, `P8018` 230.3/160 km) **is not in the source**.

Two further problems:

- Her six Gulf-of-Suez capacities sum to **835.3 mmcf/d** against the article's
  **835.8** for *seven* pipelines. That is too close to be coincidence: there is an
  **unstated breakdown source** (presumably the Wood Mackenzie / EOG R&A table), and
  one pipeline of the seven is missing. That source needs to be named and cited, or
  the values pulled.
- The article has **one** "Cairo Ring-Port Said Line"; she created **two** rows
  (`P8017` Suez–Cairo Ring, `P8018` Suez–Port Said) under names that appear nowhere
  in it. "Zeit Bay" and "Ras Shukheir" are not in the article at all.

None of P8013–P8019 duplicates an existing GEM row by name, so they are probably
genuine additions — but they are currently **unsourced as entered**.

---

## 4. Systemic problems (fix the process, not just the rows)

1. **`Researcher` was blank on all 16 new rows** in the 2026-07-28 snapshot — nothing
   was attributable and there was no way to route questions back. **RESOLVED
   2026-07-29:** the live sheet now carries `NA` on all 16 (and on `P8001`–`P8003`).
   No action needed; the residual lesson is that a blank `Researcher` on fresh rows
   invites downstream mis-attribution (this memo's own first draft got it wrong).
2. **Refs are landing in `LengthDoubleCounting`, not `Length [ref]`.** These columns
   are adjacent (58 `LengthKnown`, 59 `LengthKnownUnits`, 60 `LengthDoubleCounting`,
   61 `Length [ref]`). **45 gas rows** now hold a URL in a numeric column, and in 42
   of them `Length [ref]` is empty. This is **not only NA** — `P3620`/`P3657`
   (Israel), `P6041`, and the OPEC-ASB rows are hit too, so it is a shared
   paste-offset trap worth a one-off tracker-wide sweep. The gas tab has no such
   column in the oil tab, so this is GGIT-only. Affected ProjectIDs:

   > P6041, P1873, P3620, P3657, P6035, P0473, P0751, P3928, P0484, P1855, P0460,
   > P4401, P3939, P6703, P0474, P3932, P6709, P6714, P6713, P1858, P3343, P3346,
   > P3366, P3659, P3929, P3931, P3987, P6032, P6033, P6034, P6613, P6697, P6698,
   > P6699, P6700, P6701, P6702, P6704, P6705, P6707, P6708, P6715, P6716, P7447,
   > P7574
3. **Search-result and homepage URLs used as citations** — `?s=Gas+Pipelines+Egypt`
   (7 rows), `petro-mag.org/ar/Home/Index` (`P0473`). Neither is a reference; both
   will drift or die. Rule: a `[ref]` must resolve to a *fixed document*.
4. **Issue-level URLs with no page pointer** for a 146-page PDF. Cite the direct
   `/Uploads/Files/<uuid>.pdf` plus page number, and archive it — the landing pages
   are CMS-generated and will not survive a site rebuild.
5. **Single-sourcing throughout**, against the ≥2-independent-sources rule. Note that
   *two issues of the same ministry magazine are one source*, not two.
6. **Untranslated project semantics.** ازدواج (loop/twinning), تدعيم (reinforcement),
   تغذية (feeder), خط استيراد (import line), رصيف/ميناء (jetty/port) all change what
   the entity *is*. Dropping them turned two loops and one network upgrade into three
   ordinary new pipelines.
7. **Scope call needed on FSRU send-out lines.** SUMED, Sonker Ph1/Ph2 and the
   (missing) Damietta import line are 3.5–9 km jetty connectors to LNG import
   terminals. Decide whether GGIT tracks them; if yes, cross-link to the GEM LNG
   terminal entries rather than leaving them as free-floating transmission lines.
8. **ProjectID collision.** Our Israel gas batch (2026-07-23) reserved `P8001`/`P8003`
   for two new INGL rows; both IDs are now occupied by her Egypt rows. The Israel
   staging needs re-numbering before it is applied.
9. **No `Owner`/`Operator` on any of the 16** (all `unknown`), despite the source
   being GASCO's own report — GASCO is the stated operator throughout.
10. **Typos in committed values**: `Sinia` (×4 cells), `Poert Said`, `Ras Baker
    Transmissin Station`, trailing spaces in several `PipelineName` values.
11. **`P0473` (Cyprus–Egypt)**: `Capacity = 8.0 MMcf/d` for a 280 km export line is
    implausible by ~2 orders of magnitude — check whether this was meant to be
    8 bcm/y. Its length claim (280 km, "April & May 2026 edition") is cited only to
    the magazine homepage and is therefore unverifiable as entered; her note
    correctly records that media sources say 170 km, so this is a live conflict.

---

## 5. Missing from GEM but supported by the source

- **Damietta port gas import line** — 36 in, 3.5 km, gas flowed 23 Oct 2025.
  (She edited `P6033` Damietta–SEGAS instead, which carries 42 in / 12 km — a
  different line. The 3.5 km import connector is still absent.)
- The **7th Gulf-of-Suez pipeline** implied by the 835.8 mmcf/d aggregate.
- The other nine Nile Delta lines named in the EOG article (Abu Madi-Talkha I & II,
  Talkha-Tanta-Cairo, Abu Madi-Damietta, Meadia-Damanhur, Alexandria
  Network-Damanhur, Korimat-Al Tebbin, Korimat-Beni Suef) — check against existing
  GEM rows before treating as discoveries.

---

## 6. How to assess a source like this — reusable rules

- **Classify the source before the value.** Petro-mag is a *first-party government
  house organ*: strong on existence, dimensions and commissioning dates of state
  projects; weak as independent verification, because it is the operator reporting on
  itself in a promotional annual. Tier it accordingly — it can carry a value to
  `medium`, never to `high` on its own.
- **Same publisher ≠ corroboration.** Nov 2025 + Dec 2024 issues are one source.
- **Use cross-issue drift as a dating tool, not an averaging problem.** The same
  project reappears each year with revised numbers (15 → 15.5, 27 → 28 km, grid
  8,279 → 8,219 km). Take the latest, record the earlier value and the conflict in
  `ResearcherNotes` — never silently pick one.
- **Read the status verb, don't guess the status.** الانتهاء من تنفيذ = completed →
  `operating`; جارى / المشروعات الجارية = underway → `construction`; المشروعات
  المستقبلية = future → `proposed`. She got these right; it's the one part of the
  work that is consistently correct.
- **Translate the noun that defines the entity**, per §4.6 above — that is where the
  data model breaks, not in the numbers.
- **Sanity-check magnitudes against the aggregate.** 505 km of 12-inch feeder, 8
  mmcf/d on a 280 km export line, and six capacities summing to a published
  seven-pipeline total are all caught by arithmetic before any web search.
- **A `[ref]` must be a fixed document.** No search URLs, no homepages, no
  landing pages without a page number. Archive PDFs.

---

## 7. Recommended next step

None of this should be edited in place by us. The right shape is a **§5 Update
batch** scoped to `egypt-gas`, staging: 1 rename + 1 status fix + 3 length fixes +
4 typo fixes, a `PipelineNetworkGrouping` for the three
Hayah Karima components, the P8004/P8005 duplicate adjudication, the FSRU-scope
question and the P8001/P8003 ID collision as escalations, and a re-citation pass on
P8013–P8019 that either finds the Wood Mackenzie/EOG breakdown table or drops the
unsupported values. See `docs/country_notes/egypt.md`.
