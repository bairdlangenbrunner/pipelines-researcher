# Escalation — two spreadsheet `[ref]` sources cannot be archived (2026-08-12)

Batch: archive every spreadsheet (`.xls`/`.xlsx`) URL cited in a `[ref]` column and
repoint the cells at the backups. Scope came from a fresh 2026-08-12 pull of all three
tabs: **12 unique spreadsheet URLs across 131 cells / 56 rows**.

**Outcome: 130 of 131 cells repointed and verified.** Nothing was dropped on an access
failure (standing rule: only a confirmed 404/410 may leave a `[ref]` cell). What remains
is **one** held cell, `'Pipeline operators/owners'!U923` (P1050) — see §2.

Applied writes, all `--mode replace`:
- `notes/backup-20260812_0915_ET-archive-ref-xlsx-replace.csv` — 84 cells, Wayback
  snapshots (9 files).
- `notes/backup-20260812_0925_ET-archive-ref-xlsx-replace.csv` — 5 cells, archive.org
  items (2 files; see §3–4 below, resolved).
- `notes/backup-20260812_0938_ET-archive-ref-xlsx-replace.csv` — 12 cells, JOGMEC 2022 →
  2024 edition (see §2, resolved except U923).
- `notes/backup-20260812_1022_ET-orenburg-ref-repoint-replace.csv` — 29 cells, Gazprom
  Orenburg `lch-god-2.xls` → the archived 2021 edition `lch-god.xls` (see §1, resolved).

Repointing to a Wayback URL is not a loss of provenance — `web.archive.org/web/<ts>/<original-url>`
carries the original URL verbatim inside it. An **item** URL does not, so those uploads
carry the origin in the item's own `source`/`originalurl` metadata instead.

| source | cells | rows | why it failed |
|---|---|---|---|
| ~~Gazprom Orenburg~~ | 29 | 7 | origin geo-blocks non-RU IPs; never captured — **RESOLVED** via the archived earlier edition of the same file |
| ~~JOGMEC Japan 2022~~ | 13 | 9 | soft-404 — **RESOLVED** 12/13 via the 2024 edition; U923 held |
| ~~CNPC Dec-2019 disclosure~~ | 3 | 3 | SPN `520` — **RESOLVED** via IA item upload |
| ~~gsprom.ru tenders~~ | 2 | 2 | SPN `520` — **RESOLVED** via IA item upload |

---

## 1. Gazprom Orenburg — geo-blocked, RESOLVED via an earlier edition (29 cells, 7 rows)

Cited origin, unreachable: `https://orenburg-dobycha.gazprom.ru/d/textpage/14/20/lch-god-2.xls`

**Repointed 2026-08-12 on Baird's instruction to:**
`https://web.archive.org/web/20220506054715/https://orenburg-dobycha.gazprom.ru/d/textpage/14/20/lch-god.xls`

### Why the origin is unreachable (unchanged, and permanent for us)

- DNS resolves (CNAME `constructor.gazprom.ru` → 109.234.11.121) but ICMP, TCP/80 and
  TCP/443 all time out. **The whole Gazprom estate geo-blocks non-RU IPs** — `gazprom.ru`,
  `gazprom.com` and `gazprom-neft.ru` behave identically, while `transneft.ru` (200) and
  `novatek.ru` (301) answer fine, so this is Gazprom's AS39045 (`GAZTELECOM-MOSCOW`, LLC
  "Gazprom telecom"), not a Russia-wide block. No AAAA record, so no IPv6 route around it.
- **`lch-god-2.xls` was never captured, anywhere.** Wayback exact-URL CDX `[]`; not in
  Common Crawl; Memento aggregator is dead (DNS). Save Page Now returns **520** — IA's
  crawler is blocked by the same wall. Also checked and ruled out: four public fetch
  proxies (`r.jina.ai` 422, allorigins 500, codetabs **522** = origin unreachable,
  corsproxy 403); every RU-exit proxy proxyscrape lists (55 across http/socks4/socks5 —
  **none were even alive**); and Yandex's server-side fetchers, which egress from inside
  Russia but now require signed requests (`docviewer` 400, `translated.turbopages.org` 403).
  Nothing short of a Russian-routed connection we control will reach it.

### The fix: the same document, one edition earlier, and it IS archived

Wayback has the sibling file **without** the `-2` — `lch-god.xls`, captured 2022-05-06,
65,024 b, `application/vnd.ms-excel`, workbook authored 2021-10-11, table dated
**01.01.2021**. Title: *"Технические характеристики газопроводов, газопроводов-отводов…"*;
columns `Наименование ЛЧ` / `Протяженность [км]` / `Год ввода в эксплуатацию` /
`Разрешенный срок эксплуатации` / `Экспертиза ПБ`, ~80 linear sections.

The `-2` suffix is the CMS's collision rename on re-upload, so the two are **editions of
one document**, not different documents. That is not an assumption — it was verified
value-by-value before writing, exactly as the JOGMEC repoint in §2 was:

| PID | GEM `StartYear1` / `LengthKnown` | 2021-edition row | year | km |
|---|---|---|---|---|
| P6110 | 1971 / 214.60 | Продуктопровод ФУМ Оренбург-Салават 1н. | 1971 | 214.6 |
| P6114 | 1974 / 214.60 | Конденсатопровод Оренбург-Салават 2 н. | 1974 | 214.6 |
| P6115 | 1980 / 406.80 | Конденсатопровод Оренбург-Салават-Уфа 3 н. | 1980 | 406.8 |
| P6116 | 2010 / 408.00 | Конденсатопровод Оренбург-Салават-Уфа 4 н. | 1988-**2010** | 408 |
| P6111 | 1982 / 434.60 | Этанопровод Оренбург-Казань | 1982 | 434.6 |
| P6117 | 1986 / 272.18 | Продуктопровод **ШФЛУ** Оренбург-Шкапово | 1986 | 272.18 |
| P6118 | 1987 / 85.60 | Продуктопровод Шкапово-Туймазы | 1987 | 85.6 |

**7/7 on start year and 7/7 on length, matching at two decimals** (272.18, 214.60,
406.80) — GEM's Orenburg values were sourced from this very table. The other cited fields
carry too: `ШФЛУ` (широкая фракция лёгких углеводородов) = NGL, supporting the two
`Fuel [ref]` cells; being listed with a permitted service life and a live Rostechnadzor
`Экспертиза ПБ` certificate supports `Status = operating` on all seven; and the line names
carry the endpoint pairs the `Route [ref]` cells cite. **No cell needed holding** — unlike
JOGMEC's U923, nothing here contradicts GEM.

Note P6117/P6118 are the two halves of `Orenburg-Shkapovo-Tuymazy` and the file lists them
as two separate sections (272.18 + 85.6), which is why the GEM split into segments matches
the source exactly rather than approximately.

### Provenance caveat — the one way this differs from the other 101 cells

Everywhere else in this batch, the Wayback URL embeds the *identical* origin, so a
`--mode replace` loses nothing. Here the inserted URL embeds `lch-god.xls`, not
`lch-god-2.xls`, so replacing does drop the record that these cells once cited the `-2`
edition. Baird chose replace over add-alongside (2026-08-12); this note is where that
substitution is recorded, and the before/after of all 29 cells is in
`notes/backup-20260812_1022_ET-orenburg-ref-repoint-replace.csv`. Nothing was deleted on
the strength of a timeout — the cells gained a working citation to the same document.

**Cells written** — Oil/NGL tab (27): `Status`+`Start`+`Length [ref]` on P6110, P6114,
P6111; those three plus `Route [ref]` on P6115, P6116; those four plus `Fuel [ref]` on
P6117, P6118. Operators/owners tab (2): `Owner [ref]` U4830 (P6117), U4831 (P6118).
Write gates all passed: `valueRenderOption=FORMULA` read found no formula cells, all 29
live cells byte-matched the 2026-08-12 snapshot before writing, `RAW` + cell-scoped
ranges, re-read verified 29/29, and a fresh pull confirms **0 residual `lch-god-2`
occurrences** across all three tabs.

---

## 2. JOGMEC Japan gas pipelines — soft-404, never captured (13 cells, 9 rows)

`https://oilgas-info.jogmec.go.jp/_res/projects/default_project/_page_/001/009/256/2_2_4_Major_gas_pipeline_projects_in_Japan_2022_en.xlsx`

- **The document is gone.** The URL returns **HTTP 200 with HTML**, not a spreadsheet:
  it redirects to `https://journal.jogmec.go.jp/index.html`. JOGMEC moved its oil/gas
  site from `oilgas-info.jogmec.go.jp` to `journal.jogmec.go.jp` and the old
  `_res/projects/...` file paths did not survive. The same path on the new host is a
  hard **404**.
- **Wayback: never captured.** No CDX record for the URL, and no `.xlsx` capture on the
  old host matching this filename. The 2022 edition appears to be lost.
- Because the cited URL answers `200`, this is a **soft 404** and therefore *not* a
  confirmed deletion under the standing rule — the ref cannot simply be removed even
  though the content is demonstrably gone.

**Successor located and archived.** The same table is still published in JOGMEC's
Natural gas and LNG Data Hub:

`https://journal.jogmec.go.jp/content/300516944.xlsx` — "（3）Major gas Pipeline
projects in Japan", sheet `2024`, columns: Company / Project / Route Start / Route End /
Starting year of operation / Diameter (mm) / Distance (km). Snapshot taken this batch
(34,294 b, byte-identical to live):
`https://web.archive.org/web/20260812130924/https://journal.jogmec.go.jp/content/300516944.xlsx`

That is a like-for-like successor carrying exactly the fields these 13 cells cite it for
(`Status`, `Location`, `Route`, `Owner [ref]`).

**Repointed to the 2024 edition on Baird's instruction (2026-08-12), after verifying the
new edition value-by-value rather than swapping it blind.** The cited edition was 2022 and
the successor is 2024, so a silent swap could have re-sourced values to a document that
says something different. It was checked instead: all nine pipelines are present in the
2024 file, and **all nine start years match GEM's `StartYear1` exactly**.

The status check needed care: the file has **no operating/planned section break** — its
header note says *"Projects under construction or planning are included"*, so the only
discriminator is `Starting year of operation`. Future years do appear interleaved (e.g.
Toho Gas Handa–Anjo 2026, Ichinomiya–Bisai 2025). All nine of ours are past years
(1996–2017), so `Status = operating` is supported in every case.

| PID | 2024 row | file company | project | year | dist (km) | GEM len |
|---|---|---|---|---|---|---|
| P1025 | 31 | JAPEX | Northern Koriyama Line | 2015 | 12 | 12 |
| P1034 | 27 | JAPEX | Higashi Niigata-Sendai Line | 1996 | 261.9 | 261 |
| P1044 | 103 | Shizuoka Gas | No. 2 Suruga Trunk Line | 2004 | 28 | 28 |
| P1050 | 32 | **ENEOS** / Tohoku Electric Power | Shiroishi-Koriyama Line | 2007 | 96 | 96 |
| P1054 | 30 | JAPEX | Soma-Iwanuma Line | 2017 | 39.7 | 40 |
| P1060 | 57 | Tohoku Natural Gas | Yamagata Line | 2006 | 30 | 30 |
| P1063 | 72 | Tokyo Gas | Yokohama-Shonan Line | 2002 | 9 | 5 |
| P4272 | 7 | JAPEX | Yufutsu-Sapporo Line | 1996 | 78.7 | 72 |
| P6838 | 96 | TEPCO | Chiba Line | 1996 | 51 | 50 |

**12 of 13 cells repointed** to the archived 2024 edition
(`https://web.archive.org/web/20260812130924/https://journal.jogmec.go.jp/content/300516944.xlsx`):
Gas tab `Status [ref]` × 9 (P1025, P1034, P1044, P1050, P1054, P1060, P1063, P4272,
P6838), `Location [ref]` + `Route [ref]` on P6838 (the file's Futtsu LNG Terminal → Chiba
Thermal Power Station matches GEM's endpoints exactly), and operators/owners `Owner [ref]`
for P6838 (file company TEPCO = GEM `TEPCO [100.%]`).

### The one held cell: P1050 `Owner [ref]` — a possible real ownership change

`'Pipeline operators/owners'!U923` was **not** repointed. The 2024 edition credits the
Shiroishi-Koriyama Line to **"ENEOS / Tohoku Electric Power"**; GEM's `Owner` reads
**`JAPEX [50.%]; Tohoku Electric Power [50.%]`**. Tohoku Electric agrees, JAPEX vs ENEOS
does not. Repointing would attach a citation naming ENEOS to a value naming JAPEX —
manufacturing apparent support for a value the document contradicts, which is worse than
leaving a dead ref in place. Its `Status [ref]` was repointed normally (2007 / 96 km /
400 mm all agree).

**Route to Update (§5): did ENEOS take over JAPEX's 50% stake?** The 2022 edition is gone,
so we cannot diff the two editions to see whether this is a JOGMEC correction or a genuine
transfer. Needs an independent source either way; do not apply the ENEOS name off this
document alone. This is a **finding**, not merely a blocker — if it is a real transfer, GEM
has a stale owner on P1050.

**Length deltas noted, not applied** (out of scope for a ref repoint, and single-source):
P1063 5 → 9 km is the largest, then P4272 72 → 78.7. P1034, P1054, P6838 differ by <1 km
(rounding). P1063's diameter also reads `250-600` against GEM's `600`.

---

## 3 & 4. CNPC Dec-2019 and gsprom.ru — SPN `520`, RESOLVED by IA item upload

| | |
|---|---|
| CNPC | `https://www.cnpc.com.cn/cnpc/yqgwssxwzx/201912/5d7543803da44845b756cc80164d5c65/files/d3e4c46a1d424959a3c2e8218bb27a40.xls` |
| gsprom | `https://gsprom.ru/tenders_2025-05.xlsx` |

- **Both are live and downloadable from here** — CNPC 60,928 b (md5
  `5ec6c99363f18fbf00f22b34995d38bd`), gsprom 61,261 b (md5
  `054ccea227459027c5f11fa933338b1e`), both confirmed real spreadsheets by `file`.
- **Save Page Now refuses both**: `520` on three attempts each, and again on `http://`
  and `capture_all=1` retries (which drew a `523` and a `429`). `520` is IA-side — its
  crawler cannot fetch the origin even though we can. Not a deletion, not a 404.
- The CNPC failure is **not** a domain-wide exclusion: a sibling `202001` disclosure file
  on the same host was captured 2024-11-18, so `cnpc.com.cn` is archivable in principle.
  This specific fetch just keeps failing.

**Resolved the same day by IA *item* upload** — the method that already worked for the
Jan-2020 CNPC file. Uploading the bytes we hold bypasses the `520` entirely because it
never touches the origin. Both files are preserved in-repo as the upload source:

- `notes/unarchivable-2026-08-12/cnpc_201912_d3e4c46a1d424959a3c2e8218bb27a40.xls`
- `notes/unarchivable-2026-08-12/gsprom_tenders_2025-05.xlsx`

| origin | item ref | cells |
|---|---|---|
| CNPC Dec-2019 | `https://archive.org/details/d3e4c46a1d424959a3c2e8218bb27a40` | I2429/I2430/I2431 (P4522–P4524) |
| gsprom.ru | `https://archive.org/details/gsprom_tenders_2025-05` | I1245 (P2425), I2109 (P4111) |

Identifier convention follows existing tracker practice (279 `archive.org/details` refs
already cited): the identifier is the **original filename stem**. Both uploads were
verified by re-reading the item metadata and confirming IA's stored md5 matches the local
bytes — an HTTP 200 on the upload is not by itself proof the file registered.

The CNPC cells were single-ref, so they now cite the item alone; the two gsprom cells kept
their other refs (substring edit inside a multi-ref cell).

**Tooling now in place** (was absent when this batch started): `internetarchive` 5.11.0
installed, `ia` CLI at `~/miniconda3/bin/ia`, S3 keys in `~/.config/internetarchive/ia.ini`
(mode 600, outside the repo — never commit it). Account:
`baird.langenbrunner@globalenergymonitor.org` (`@baird92487`), the same one that owns the
Jan-2020 item. So a future SPN `520` is a solved problem: download the bytes, upload as an
item, repoint. Keys are revocable at `archive.org/account/s3.php` without touching the
account password.

Related: the two CNPC disclosure editions (Dec-2019 vs Jan-2020) differ in exactly 3
cells, all design capacity revised **downward**; P4522–P4524 cite the Dec-2019 edition
and none of the three changed cells affects them.

---

## Method note

Anonymous Save Page Now works, but only in **path form** —
`https://web.archive.org/save/<url>`, which 302s to the new snapshot. The
`?url=`/POST-form variant returns the SPN interstitial page with HTTP 200 and captures
nothing; treating that 200 as success would have produced a batch of fabricated
"backup" links. Every capture in this batch was verified by re-downloading it through
the `id_` raw modifier, confirming the bytes are a spreadsheet (`file` → Microsoft Excel)
**and** that the byte count matches the live file exactly.

Also note: an **archive.org item** (`archive.org/details/<id>`, a user-uploaded copy)
and a **Wayback page capture** (`web.archive.org/web/<ts>/<url>`, a crawler fetch) are
different things reached by different routes. Only the latter is scriptable anonymously;
the former needs an account but works when the crawler is blocked.
