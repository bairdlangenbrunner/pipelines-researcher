# Escalation — two spreadsheet `[ref]` sources cannot be archived (2026-08-12)

Batch: archive every spreadsheet (`.xls`/`.xlsx`) URL cited in a `[ref]` column and
repoint the cells at the backups. Scope came from a fresh 2026-08-12 pull of all three
tabs: **12 unique spreadsheet URLs across 131 cells / 56 rows**.

**Outcome: 89 cells repointed and verified; 42 cells left untouched** across the two
sources below. Neither is a case where a `[ref]` may be dropped (standing rule: only a
confirmed 404/410 may leave a `[ref]` cell; an access failure never can). Both are
escalated here rather than edited.

Applied writes, both `--mode replace`:
- `notes/backup-20260812_0915_ET-archive-ref-xlsx-replace.csv` — 84 cells, Wayback
  snapshots (9 files).
- `notes/backup-20260812_0925_ET-archive-ref-xlsx-replace.csv` — 5 cells, archive.org
  items (2 files; see §3–4 below, now resolved).

Repointing to a Wayback URL is not a loss of provenance — `web.archive.org/web/<ts>/<original-url>`
carries the original URL verbatim inside it. An **item** URL does not, so those uploads
carry the origin in the item's own `source`/`originalurl` metadata instead.

| source | cells | rows | why it failed |
|---|---|---|---|
| Gazprom Orenburg | 29 | 7 | origin geo-blocks non-RU IPs; never captured |
| JOGMEC Japan 2022 | 13 | 9 | soft-404, document gone; never captured |
| ~~CNPC Dec-2019 disclosure~~ | 3 | 3 | SPN `520` — **RESOLVED** via IA item upload |
| ~~gsprom.ru tenders~~ | 2 | 2 | SPN `520` — **RESOLVED** via IA item upload |

---

## 1. Gazprom Orenburg — geo-blocked, never captured (29 cells, 7 rows)

`https://orenburg-dobycha.gazprom.ru/d/textpage/14/20/lch-god-2.xls`

- **Live status: unreachable from here.** DNS resolves (CNAME `constructor.gazprom.ru`
  → 109.234.11.121) but TCP connect times out at 40 s, repeatedly. This is a
  network-level block on non-Russian IPs, not a deletion — the document may well be
  perfectly alive for a Russian client.
- **Wayback: never captured.** Exact-URL CDX returns `[]`. The host has captures going
  back to 2014, so the domain is not excluded from the archive — this particular file
  simply was never crawled.
- **Save Page Now cannot help**: IA's crawler has to reach the origin, and the origin is
  what's blocking. We also never hold the bytes, so an IA-item upload is not available
  either.

**Cells affected** — Oil/NGL tab: `Fuel`, `Status`, `Start`, `Length`, `Route [ref]`
across P6110, P6111, P6114, P6115, P6116, P6117, P6118; operators/owners tab
`Owner [ref]` × 2 (U4830, U4831). 21 of the 29 cells hold this URL alongside other refs,
so those rows retain independent sourcing; the 8 single-ref cells do not.

**Recommendation:** leave all 29 cells as they are. Two ways forward, both needing a
decision:
1. Have someone on a Russian-routed connection (or a VPN exit) fetch the file once and
   submit it to Wayback — then this becomes a normal repoint.
2. Treat the Orenburg values as single-sourced-and-unverifiable and re-source them from
   the corroborating refs already in the multi-ref cells (`sudact.ru` arbitration doc,
   the `orenburg-dobycha.gazprom.ru/press/news/...` items, `kniga-khronika-ogkhk.pdf`).

Do **not** delete the URL on the strength of a timeout.

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

**Recommendation — this is an Update decision, not a mechanical repoint.** The cited
edition is the **2022** file; the successor holds **2024** data. Swapping them silently
would re-source existing values to a document that may state something different. So:
- route the 13 cells to Update (§5) for a value-by-value re-check against the 2024
  edition, then repoint;
- do not fold this into the mechanical archive batch.

**Cells affected** — Gas tab `Status [ref]` × 9 (P1025, P1034, P1044, P1050, P1054,
P1060, P1063, P4272, P6838), plus `Location [ref]` and `Route [ref]` on P6838;
operators/owners tab `Owner [ref]` × 2 (P1050, P6838). Every one is a **single-ref
cell**, so all 13 are currently sourced solely to a dead document.

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
