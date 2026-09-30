# R4b defect log (lean pass — logged, not fixed mid-batch unless they would corrupt this delivery)

1. **FIXED — DeadLinks note told the researcher a kept ref was "being replaced".**
   `build_ref_workbook._resolve_superseded` annotated every HAS_REF baseline shadowed by a fill as
   "the existing [ref] being replaced", even when the fill was UNRESOLVED with no refs. On P2357/P5745
   (energybase geo-block, no Wayback) that read as an instruction to delete a once-working ref. Wording
   now says the ref is KEPT when nothing verified replaces it.

2. **OPEN — gate M does not screen `contested` on validity records.** Four concerns (P2357, P5745
   Operator; P2429, P5686 OtherEnglishNames) carried prose in `contested`, which lands on the Backend
   paste surface as the candidate. Fixed by hand in the shards. Fix: extend gate M (or the merge) to
   the `contested` map, same test as `values{}`.

3. **OPEN — some agents write validity prose under `summary`, leaving `recommendation` empty**
   (P2429, P5686). The Validity tab reads `recommendation`. Fix: the merge should fall back to
   `summary`/`researcher_notes` the way R5's `notes` fix did.
