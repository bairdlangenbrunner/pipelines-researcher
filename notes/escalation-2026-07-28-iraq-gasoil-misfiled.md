# Escalation — P6824 is a **diesel** pipeline in the gas tracker (Arabic `زيت الغاز` false friend)

**Date:** 2026-07-28 · **Scope:** GGIT, Iraq, gas · **Ruling needed from Baird**
**Staged:** `batches/iraq-gas/staging/ref-gap-repass/staged_resolutions.json`
(1 `__VALIDITY__` record, `concern_type: classification`)

## The claim

**P6824 "Shouibah-Khor Al-Zubair Gas Pipeline" is a gas oil (diesel) export pipeline.**
It is a refined-liquid-products line and does not belong in GGIT at all.

This is not a `Fuel` mislabel to be corrected in place. GGIT tracks gas transmission
infrastructure; a diesel export line is out of scope for the tracker, so the row should
be **removed from GGIT and referred to GOIT** with its specs preserved.

## Evidence — the row's own source proves it

al-Mirbad (Basra), 19 July 2024. Headline:

> شركة خطوط الأنابيب النفطية تعلن عن إنجاز تأهيل أنبوب تصدير **زيت الغاز** (شعيبة - ميناء خور الزبير)
>
> *"The Oil Pipelines Company announces completion of the rehabilitation of the **gas oil**
> export pipeline (Shuaiba – Khor al-Zubair port)"*

Body: `أنجاز أعمال تأهيل أنبوب تصدير زيت الغاز 8 - 10 عقدة، وبمسافة 46 كم` — completion of
rehabilitation works on the **gas oil export pipeline, 8–10 inch, over a distance of
46 km**. Purpose: `يهدف إلى زيادة الطاقة التصديرية لوقود زيت الغاز عبر المنفذ الجنوبي` —
*to increase the export capacity of **gas oil fuel** through the southern outlet.*

**The match to GEM is exact, and that is what makes it dangerous:**

| attribute | al-Mirbad | GEM P6824 |
|---|---|---|
| route | Shuaiba → Khor al-Zubair port | Shouibah → Khor Al-Zubair |
| length | 46 km | 46 km |
| diameter | 8–10 inch | `10,8` |
| operator | Oil Pipelines Company | Oil Projects Co. |
| status | completed (`إنجاز`) July 2024 | operating |

Every spec agrees. The row is **perfectly sourced and completely misfiled**. Its
`Status [ref]` verifies correctly — the *status* is right; the *tracker* is wrong.

## The mechanism: a two-word translation trap

Arabic **`زيت الغاز`** is literally *"oil of the gas"* / **"gas oil"** and means
**diesel / gasoil** — a refined liquid petroleum product. Natural gas is
**`غاز طبيعي`**, and dry gas is **`الغاز الجاف`** (which is what Iraq's genuine gas rows
cite, e.g. P7435's `أنبوب نقل الغاز الجاف`).

Reading `الغاز` out of the phrase `زيت الغاز` produces exactly this error, and once made,
nothing downstream contradicts it: the operator is a pipeline company, the route is real,
the date is real, the specs transcribe cleanly. There is no internal inconsistency to
catch it. **The only way to catch it is to read the fuel word as a phrase.**

English has the same trap — "gas oil" is a British term for diesel — so this is not
purely an Arabic-language problem.

## Three corroborating details, all pointing at liquids

1. **The destination is an oil port.** `ميناء خور الزبير النفطية` — the Khor al-Zubair
   **oil** port, a liquids export terminal. A gas pipeline terminating at a crude/products
   export berth makes no sense; there is no gas offtake there.
2. **8–10 inch is a products diameter.** Small for gas transmission (Iraq's real dry-gas
   trunks in GGIT are 16–42″), normal for a refined-products line.
3. **The purpose is export of a fuel.** Iraq's dry gas is consumed domestically in power
   stations — it is not exported. Only liquids leave through the southern outlet.

Independent structural confirmation from the recovered JCCP presentation (Nihad A. Moosa,
Director General, Iraqi Ministry of Oil / Oil Pipelines Company, 2013), which inventories
Iraq's **product** pipelines as `shaiba - doura 10 inch` and `shaiba - karkh 14 inch`.
**Shuaiba is the origin node of Iraq's refined-products pipeline system** — which is
precisely where this row starts, on a 10-inch line.

## Recommended action

1. **Remove P6824 from GGIT.** Do not merely re-label `Fuel`.
2. **Refer to GOIT** as a refined-products (gas oil / diesel) export line, preserving:
   46 km · 8–10″ (GEM holds `10,8`) · Shuaiba pump station → Khor al-Zubair oil port ·
   Oil Pipelines Company / Oil Projects Co. · rehabilitation completed July 2024 ·
   `[ref]` = the al-Mirbad URL below.
3. Check whether GOIT already carries this line under another name before creating a row
   (`entity_lookup.py`; standing rule against duplicate entities).

Note this also **removes P6824 from the ASB length-defect discussion** — it was one of
the four rows that memo explicitly *rejected* from the mi→km match (46 km/8-10″ matched
neither diameter nor name). That rejection was correct, and now has a second reason.

## Scope: this is the second country with this exact class

The Libya gas pass (2026-07-28) escalated **three condensate lines misfiled in GGIT**
(`docs/country_notes/libya.md`). Iraq now adds a diesel line. Two countries, four rows,
same failure mode: **a liquids pipeline entering the gas tracker because one word in the
source was read as "gas."**

### A second Iraqi candidate was examined and **rejected** — the screen needs a guard

`docs/country_notes/iraq.md` carries a standing finding from the 2026-07-07 ref-harvest
re-pass that **P4067 (Al-Ahdab–Al-Zubaydia)** is likewise misfiled: *"crude oil → belongs
in GOIT, not GGIT"*, sourced to Iraq Business News and BBC Arabic establishing that
Al-Ahdab is a **crude-oil field**. **That finding is retracted** (see the P4067
classification record in `batches/iraq-gas/staging/qc/`), and the reason is worth stating
here because it is the failure mode this screen will produce if run naively:

**Inferring a pipeline's fluid from its source field's principal product is invalid.**
An oil field produces associated gas; P4067's destination is a **power station**
(`Al-Zubaydia PWR St`); and a gas line from an oil field to a power plant is the most
ordinary object in Iraq's gas network — Majnoon, Gharraf, Faiha, West Qurna and Buzergan
rows are all exactly that shape. OPEC moreover lists the Ahdab corridor's crude and gas
lines as **separate rows in separate tables** (ASB2017 Table 6.9 crude, Table 9.9 gas),
so it distinguished them deliberately. P4067 stays in GGIT.

So the screen below must key on **what the source says the pipe carries**, never on what
its origin field produces. P6824 qualifies because its own headline names the *fluid*
(`زيت الغاز` — gas oil); P4067 never did.

*(Al-Jibawi's 2025 report does describe a genuinely new 16″/76 km **crude** line from
Ahdab to Zubaidiya completed in early 2024 — that is a **GOIT discovery candidate**, not
a GGIT removal, and it is logged as such.)*

**Recommended tracker-wide screen** (out of scope for this pass, worth its own task):
flag GGIT rows whose sourcing describes a liquid. High-yield signals —

- Arabic-sourced rows containing `زيت الغاز`, `المكثفات` (condensate), `النفط الخام`
  (crude), or `المشتقات` (derivatives/products);
- any row whose destination is a **port, berth, terminal, or refinery** rather than a
  power station, processing plant, city gate, or another pipeline;
- rows under ~12″ where the source uses the word *export*.

Arabic- and Russian-sourced rows are the highest risk, since the fuel word is least
likely to be checked as a phrase.

## Sources

- al-Mirbad, 19 July 2024 — `https://www.al-mirbad.com/detail/163145`
  (HTTP 200. This ref was previously written off as `DEAD_LINK`; the re-pass found it
  live under a browser User-Agent, which is the only reason the misclassification was
  caught. Arabic quoted verbatim above.)
- JCCP seminar presentation, Nihad A. Moosa (DG, Iraqi MoO / Oil Pipelines Company),
  March 2013 — product-pipeline inventory listing Shuaiba as the origin node.
  `http://web.archive.org/web/20231114092911/https://www.jccp.or.jp/international/conference/docs/s2-3_simminar_oil_final1_130307.pdf`
  (origin 404s; Wayback snapshot 2023-11-14, 7.9 MB, read with `pdftotext`.)

## Companion memos

- `notes/escalation-2026-07-28-iraq-capacity-units.md` — the other defect surfaced by the
  same ref re-pass.
- `notes/escalation-2026-07-28-asb-iraq-length-units.md` — §Evidence 2 lists P6824 among
  the four rows rejected from the ASB length match.
