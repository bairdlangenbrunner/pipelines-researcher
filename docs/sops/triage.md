# SOP — Triage (decide what to work on)

Forward-looking chooser. Reads signals, produces a **markdown memo** recommending
the next batch's composition. Stages nothing; builds no xlsx. The user decides scope
before any doer runs.

## Sequence
1. `scripts/refresh_csvs.sh`; load `header=2`; exclude buffer rows.
2. **Gap analysis** (methodology `docs/GOIT_Pipeline_Research_Workflow.md` Phase 1):
   per country/commodity, categorize by `Status`; for each in-development pipeline
   (`proposed`/`construction`/`shelved`) tally missing key columns (`Status [ref]`,
   `Owner`, years, `Capacity`, `LengthKnown`, `Diameter`, endpoints, `Cost`,
   `FIDStatus`, `Opposition`, route fields).
3. **Staleness flags** (per the dormancy rules in `docs/reference/controlled_vocab.md`):
   proposed with no update >2y → inferred-shelved candidate; shelved >4y →
   inferred-cancelled candidate; in-dev rows not refreshed recently → due.
4. **Reconciliation backlog:** any unprocessed Additions / disagreements from a prior
   reconciliation batch; whether a fresh scrape of a registered source has landed.
5. Write the memo to `batches/triage_<YYYYMMDD>_<HHMM>_ET.md`. Each option names the
   **workflow** (reconciliation / update / discovery / qc), the **scope**, and for
   update the **tier**. Present; **stop and ask** before spinning up any batch.
