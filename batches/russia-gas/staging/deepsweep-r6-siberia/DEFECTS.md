# R6 defect log (lean pass — logged, not fixed mid-batch; shards hand-fixed so this delivery is clean)

1. **OPEN (repeat of R4b #2) — gate M does not screen `contested` on validity records.** Six concerns
   (P2458, P3369, P3370, P5517, P7615 ×2) carried prose in `contested`. Fix: extend gate M (or the merge)
   to the `contested` map, same test as `values{}`.

2. **OPEN (repeat of R4b #3, wider) — off-schema validity/status records merge silently.** Five
   concerns left `recommendation` empty (text in `researcher_notes`), and the P4056/P4110 agent wrote a
   whole alternative shape: validity `summary`/`severity`/`evidence_refs` with no `verdict`;
   status `recommended_status`/`recommended_fields`. The merge produced verdict `''` concerns and a
   `change` with no proposed status. `evidence_refs` included gem.wiki. Fix: merge falls back to
   `summary`→`recommendation`, `recommended_*`→`proposed_*`, defaults `verdict=concern` when
   `concern_type` is set, and drops GEM URLs; or `check_shard_coverage.py` blocks the shard.

3. **OPEN — the seed REVERIFIES a HAS_REF on a trivial value match.** P5510 Capacity `0.00` "contained"
   on sudact.ru, a page the agent showed never names the line. Fix: `seed_resolutions_from_worklist.py`
   (or the verifier's contains-value test) should not count a zero/placeholder value as contained, and
   should require `name_found`.

4. **OPEN — fill value keys not checked against backend columns.** The Novosibirsk–Barnaul agent wrote
   `Owner`, `Start`, `Construction` (ref-column stems) as value keys; the merge staged them as
   non-folding fills of columns that don't exist. Fix: the merge (or coverage check) rejects a
   `values{}` key that is not a backend/owners-tab column.

5. **Minor — UNRESOLVED fills carrying changed values** (P2705 Status shelved, P3604 locations) reach
   the store with the agent's proposed value. Reverted by hand. Fix: the merge resets values on
   `UNRESOLVED` records to the sheet values (the proposal belongs in notes).
