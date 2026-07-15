# Research backlog — unfinished / ongoing projects

Inventory of started-but-unfinished research threads, as of **2026-07-15** (full-repo
audit). Update this file when a thread closes or a new one opens; per-country detail
stays in `docs/country_notes/`, and this file just tracks what's open and where.

---

## 1. The big one — global GGIT Stage A/B/C rollout (planned, never executed)

Plan: `docs/plans/ggit_update_2026-07.md` (decisions locked 2026-06-10; target
end-June / early-July 2026 — now past its own deadline).

- **Stage A** (in-dev status sweep, Baird's #2, runs first): ~998 rows / 137 countries
  (China 326, US 131, Russia 70, Brazil 28, India 24, Saudi Arabia 21, …).
- **Stage B** (stale tier-1 refs < 2024, Baird's #1): ~1,854 rows / 127 countries
  (China 288, US 256, Russia 127, Italy 126, Australia 84, Pakistan 63, …).
- **Stage C** (sweep-up, Baird's #3): ~1,495 rows, incl. 9 broken-status rows
  (8 blank `Status`, 1 "mixed status") flagged as data bugs.

Never built/created: `scripts/build_backfill_worklist.py` (Process B tooling) and the
`batches/staging/ggit-update-2026-07/ledger.json` ledger. Only 4 of 137 queued
countries (Iraq, Iran, Saudi Arabia, Egypt) were processed — and via the separate
`campaigns/ggit-2026` annual-packet mechanism, not this machinery.
**Needs: restart the plan (build the tooling + ledger) or explicitly retire the doc.**

## 2. Research legs started but not finished

| Thread | State | Source |
|---|---|---|
| **Egypt gas discovery (Leg B)** | 6 vetted candidates staged in `batches/staging/annual-gas-egypt/discovery/vetted/`; **workbook never built** — closest-to-done item in the repo | `docs/country_notes/egypt.md`; roster `discovery_status = pending` |
| **Egypt oil (GOIT)** | never swept | `docs/country_notes/egypt.md` |
| **Saudi oil ref-sweep** | 3-row validation slice (2026-06-08) + 10-row batch staged; partial toward intended 50-row run | `batches/staging/ref-sweep-saudi-arabia{,-10row}/`; `docs/country_notes/saudi-arabia.md` |
| **Saudi GulfPub route-consistency pass** | low/medium-accuracy matches not finished; route-replacement candidates not staged | `docs/country_notes/saudi-arabia.md` |
| **Nigeria divestiture ownership sweep** | not started | `docs/country_notes/nigeria.md` |
| **United States** | deepwater-export terminal open item; 131-row Stage A queue slot unstarted | `docs/country_notes/united-states.md`; plan doc |
| **Iraq oil open items** | Grand Faw third offshore line (Esta/Micoperi) length/diameter/route; P0544 Basra–Haditha status review | `docs/country_notes/iraq.md`; CLAUDE.md |
| **Iran general open items** | P6074 verify-before-removal; P5367 reclassify as Neka–Ray segment | `docs/country_notes/iran.md`; CLAUDE.md |
| **LNG carrier quarterly reconciliation** | "designed and partially executed" vs SFOC data; referenced `instructions.md` methodology is **not in this repo** — orphaned | `docs/PROJECT_SETUP_AND_CONTEXT.md` §9/§11 |

## 3. Staged, awaiting Baird's manual application (research complete)

Roster `applied` column is blank for all four countries — log the date when pasted.
Iraq/Iran xlsx deliverables are already pruned from disk, so file presence is not a
signal of application status.

- **Iraq gas** — full packet staged 2026-07-05 (+ OPEC-ASB ref-harvest re-pass
  2026-07-07, 68 refs). 37.5% status-change rate **tripped the >30% escalation gate**.
  `docs/country_notes/iraq.md`.
- **Iran gas** — full packet staged 2026-07-05 (+ re-pass 2026-07-07, 35 refs).
  62.5% in-dev change rate (gate tripped); class-wide Owner NIOC→NIGC/IGTC fix on
  ~27 operating rows. `docs/country_notes/iran.md`.
- **Saudi gas** — full packet staged 2026-07-08 (discovery 2026-07-13). In-dev clean
  (22/22 confirm); hinges on the P1897–P1925 class decision (§4). xlsx on disk.
  `docs/country_notes/saudi-arabia.md`.
- **Egypt gas** — in-dev 2026-07-09 + operating deep sweep 2026-07-13. No escalation
  gate. xlsx on disk. `docs/country_notes/egypt.md`.
- **US oil: Delaware Express** (P7995/P0354, researched 2026-06-12) and
  **Permian Express I–IV** (P0113/P2581/P2660/P2661, researched 2026-06-11) —
  `batches/staging/{delaware,permian}-express/staged_updates.json`.
- **Saudi oil ref-sweep 10-row batch** (108 units: 67 REFS_ADDED / 25 DEAD_LINK /
  10 REVERIFIED / 6 UNRESOLVED) — `batches/staging/ref-sweep-saudi-arabia-10row/`.

## 4. Decisions needed from Baird

- **P1897–P1925 (Saudi gas, 29 rows):** the 2026-06-19 escalation memo
  (`notes/escalation-2026-06-19-saudi-gas-opec-block.md`) requested a class-level
  decision (provenance of the 2022 GIS/km-post family, disposition of synthetic rows,
  dup-merge approval, re-citation) and was never answered; the identical question
  resurfaced in the 2026-07-08 packet. One decision closes both.
- **Roster `applied` dates:** confirm whether the Iraq/Iran packets were actually
  applied to the live Sheet, and record dates in `campaigns/ggit-2026/roster.csv`.
- **Retire or restart** the Stage A/B/C plan (§1).
