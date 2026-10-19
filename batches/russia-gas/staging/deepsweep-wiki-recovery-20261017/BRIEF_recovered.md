
## Recovered-citation wave (2026-10-19): read ONLY the reopened citations

This row was already worked in this store. Its shard holds a record for every owed unit, a status review and a validity record. A later full-ladder re-check found that some citations an earlier agent logged as dead or blocked do load (through the live site, a complete Wayback capture or archive.today). Those ledger records were removed, so `--remaining` now lists them as `WIKI` lines. That list is your whole job.

- Run `--remaining` first. Read ONLY the citations it lists as `WIKI`. Do not re-open citations already in the ledger, and do not search the open web.
- Each reopened candidate in `wiki_prepass.json` carries `read_via` when the live URL does not load: read that copy. Read the WHOLE document (download a PDF with `curl -sL -o` and run `pdftotext -layout`; strip tags from HTML) and search it for every figure on the row.
- Read the shard's existing `fills`, `status_reviews` and `validity` first. A reopened page changes a record only when it states the value. If it does, re-write that record with `--fill` (same `ref_col`, so it replaces the old one) and KEEP every ref the old record already proposed. For example, an `UNRESOLVED` unit becomes `REFS_ADDED` with this page as its ref. A low or medium record gains this ref and is re-tiered by the normal rules. A sheet value that the page contradicts goes through standing rule 4, exactly as the main brief says. A status review is re-written only if the page changes the verdict or adds a dated source the review lacked.
- Cite what you read. A page read as a Wayback copy is cited as the Wayback URL, with the live URL named in the note. For a pravo.gov.ru document read through its `doc_itself` view, cite the harvested URL, since both are the same live page on the same site.
- Log every reopened citation with `--wiki-read` (used, no_value or not_this_row; dead or blocked only after the full ladder fails again, with every rung listed). Never set LNGCT_NO_BROWSER.
- Finish with `check_shard_coverage.py` passing for each of your rows, then a one-line summary per row saying what the reopened pages changed, or that they changed nothing.
