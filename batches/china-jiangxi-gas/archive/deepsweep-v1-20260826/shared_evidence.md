# Shared evidence — Jiangxi gas deep sweep (all batches)

Two primary documents found on batch_01 that bear on rows across **every** batch. They are
handed to you already read so you do not re-find them. Local text is `jx_plan.txt` and
`sse_bond_2025.txt` in this directory — **read those files, do not re-download**.

**Both have a verified, citable URL — use these verbatim, do not go looking for others:**

| document | citable URL | notes |
|---|---|---|
| Jiangxi DRC gas plan | `https://img9.qianzhan.com/policy/202307/14/20230714-d7d735aa6fb9eae9.pdf` | 8.16 MB / 24 pp, HTTP 200. The pipeline passage is on **PDF page 6**, section 省级天然气长输管道. The government's own copy (`nc.gov.cn`) is NXDOMAIN, so this third-party host of the *actual document* is the citable copy. |
| CCXI / SSE bond report | `https://static.sse.com.cn/disclosure/bond/announcement/company/c/new/2025-04-03/242696_20250403_SXBW.pdf` | Shanghai Stock Exchange's own disclosure host — authoritative. |

**Both are large CJK PDFs, which `url_verifier` screens as FAIL.** That is the documented
large-PDF/ligature false-negative family, not a dead link. If you cite either, confirm the value
by hand (`curl` the bytes + `pdftotext -layout`) and record in your `verifications` note that the
automated screen was overridden and how — batch_01 did exactly this and it passed the gate.
A single official government source is **tier `medium`**, not `high`; the DRC plan and the CCXI
report are two *different* origins, so citing both for one value does reach `high`.

## 1. Jiangxi DRC — 江西省天然气利用规划 (2013–2020), 赣发改规划〔2014〕325号

The authoritative provincial planning document. Its 省级天然气长输管道 passage, verbatim:

> 承接**川气东送**工程气源的江西省天然气管网**一期工程已建成管道 870 公里**，主要建成
> **九江—南昌、九江—沙河、九江—景德镇、南昌—丰城、高安—新余、丰城—抚州 6 条干线**和
> **田南—上高支线**。承接**西气东输二线、三线**工程气源的江西省天然气管网**二期工程已建成
> 管道 98 公里**，主要建成**吉安首段、赣州首段、安义段 3 条管线**和**宜春、萍乡对接工程**。

What that gives you, and the exact limits of it:

- **Phase I as-built = 870 km** as of the 2014 plan. This is an INDEPENDENT, official,
  non-GEM source for P4777's aggregate. It **corroborates the parent-row reading**: Phase I is
  a system with named constituent trunks, not a duplicate of them. The sheet says 825.00 km —
  a 5.2% gap that is most likely a **vintage or scope cut**, not an error. Do NOT propose 870
  as a replacement value unless you can date both figures; the defensible move is to cite the
  plan for the *shape and magnitude* and say the exact vintage is unresolved.
- **Existence and operating status** for the six trunks + one branch, by an official 2014
  statement that they are 已建成 (built). That is real `Status [ref]` support for rows whose
  `Status [ref]` is blank — and this batch has many.
- **Supply source**: Phase I off 川气东送 (Sichuan–East Gas), Phase II off 西气东输二线/三线
  (WEP2/WEP3). Useful for grouping and for sanity-checking any row's phase label.
- **Phase II as-built = 98 km** (Ji'an first section, Ganzhou first section, Anyi section +
  Yichun and Pingxiang interconnects). Note how small that is against the Phase II rows'
  stated lengths — see the P4788/P4789 defect below.
- **What it does NOT give: per-trunk lengths.** It names the trunks without measuring them, so
  it cannot fill a blank `LengthKnown`. Do not stretch it into one.

**DRC trunk → GEM row (all 7 matched, verified against the snapshot):**

| DRC name | GEM row | sheet `LengthKnown` |
|---|---|---|
| 九江—南昌 Jiujiang–Nanchang | **P4780** | *blank* |
| 九江—沙河 Jiujiang–Shahe | **P4781** | *blank* |
| 九江—景德镇 Jiujiang–Jingdezhen | **P4779** | 150.00 |
| 南昌—丰城 Nanchang–Fengcheng | **P4782** | *blank* |
| 高安—新余 Gao'an–Xinyu | **P4778** | *blank* |
| 丰城—抚州 Fengcheng–Fuzhou | **P4776** | *blank* |
| 田南—上高 Tiannan–Shanggao (支线) | **P4783** | 29.41 |

**Five of the six blank-`LengthKnown` rows are exactly DRC-named trunks.** So on those rows the
existence question is closed by this document and your budget should go to the *length*.

## 2. CCXI credit rating report — 江西省投资集团有限公司 2025 科技创新可续期公司债券(第一期)

Programme-level frame for the whole provincial network, from a rated bond disclosure:

- Provincial network build-out **3,400+ km** total; **Phase I ~1,600 km planned**,
  **Phase II ~1,800 km planned** (Phase II explicitly off WEP2/WEP3).
- **Total investment 134 亿元**, construction period Jan 2009 onward.
- As of **end-March 2024**: cumulative investment ~133.69 亿元, **~3,182 km built**,
  county-connection (县县通) 3,177 km fully complete, **2,892 km in operation**, ~87 gas
  transmission stations, one 20,000 m³ LNG tank.

Use it as a **`SegmentCost` and `Status` corroboration surface** and as the programme total.
Beware the planned-vs-built distinction: 1,600 km is *planned* Phase I, while the DRC's 870 km
is *as-built* Phase I. Those are not competing figures and must never be reconciled against
each other as if they were.

## 3. Name-cell defects found in the snapshot — route to MZ, do not fix

Confirmed against `GGIT_gas_snapshot_20260826.csv`:

- **P4780** carries `OtherLanguageSegmentName = 上高支线` ("Shanggao Branch") while its
  `SegmentName` is *Phase I, Jiujiang-Nanchang*. 上高 belongs to **P4783** (Tiannan–Shanggao),
  whose Chinese-name cell is **empty**. The Chinese name is on the wrong row.
- **P4788** and **P4789** both hold **fragments of one longer Chinese string, chopped
  mid-phrase**: P4788 = `丰段、进贤段；赣州南支线信丰瑞金段、上犹崇义`, P4789 =
  `段、樟树新干峡江段、井开区吉水永丰段、赣州南`. P4789's begins with a bare `段、` and ends
  truncated at `赣州南`; neither is a valid name for its row. This reads as one multi-segment
  list pasted and split across two rows. **Do not treat either cell as that row's name.**
  It also plausibly explains P4788's length: **340.30 km against a 31.75 km route trace
  (10.7×)** is what you would expect if 340.30 was lifted from a multi-segment aggregate while
  the geometry covers a single section. Test that reading; do not assume it.

All three are **`__VALIDITY__` findings for MZ**, whose lane is the wiki and the names. Record
them, do not repair them.
