#!/usr/bin/env python3
"""Audit a finished deep-sweep shard for the rules `check_shard_coverage.py` does NOT check.

`check_shard_coverage.py` answers "is every owed unit accounted for, and will it merge?".
This answers "is what the agent wrote actually true to its own evidence?" — standing rule 1,
banned hosts, the EIA URL convention, **tier/independent vs distinct publishers**, UNRESOLVED
discipline, controlled vocabulary, and status-flip/cancellation coherence. The two are
complements; a shard is not finished until both are clean.

THE RULE THIS SCRIPT EXISTS FOR — tier is a claim about evidence, so it is counted over
evidence. A `fills` / `ref_records` / `status_reviews` record records `verifications`, so its
tier is counted over the refs that actually verified (`ok` AND `contains_value`). A `validity`
record carries NO `verifications` by repo convention, so its tier is counted over
`proposed_refs` — which makes `tier: "high"` (or `independent: true`) on an empty
`proposed_refs` list a self-contradiction: a claim of two independent publishers backed by
zero. That shape reached delivery four times in the US gas slice-2 sweep (P7863, P5101, P7782,
and one earlier) because nothing in the per-shard finish gate looked for it. Now something does.

Usage (blocking gate — exits 1 on findings):
    python3 scripts/audit_shard.py <shard.json | staging/rows dir> [...]
    python3 scripts/audit_shard.py --quiet <dir>      # findings only, no "clean" lines

Never pipe this through `tail` — the summary is the last line and the findings scroll past it.
Use `--quiet`, or `grep -v ": clean"`.
"""
import json, sys, glob, os, re
from urllib.parse import urlparse

BAN = ('abarrelfull', 'theodora.com', 'yingdodo')
GEM = ('gem.wiki', 'globalenergymonitor')
BAD_EIA = ('EIA-NaturalGasPipelineProjects.xlsx', 'data.php')
LIVE = ('operating', 'construction', 'proposed')
# The controlled vocabulary columns that are lowercase (CLAUDE.md -> Controlled vocabulary).
LOWER = {'Status', 'RouteAccuracy', 'PipelineType', 'DelayType',
         'ShelvedCancelledType', 'Delayed', 'Opposition'}
SECTIONS = ('fills', 'validity', 'status_reviews', 'ref_records')


def unwrap(u):
    """A Wayback capture is its ORIGIN's publisher, not archive.org's.

    web.archive.org/web/<ts>[id_]/<original url> -> <original url>. Without this the script
    collapses every captured ref to one publisher and reports a false tier=high-on-1 finding
    (first hit: P0404, whose six refs are all captures of monitoreconomico.org / gob.mx /
    ienova.gcs-web.com).
    """
    m = re.search(r'web\.archive\.org/web/[^/]*/(https?://.+)$', u)
    return m.group(1) if m else u


EDGAR_CIK = re.compile(r'/Archives/edgar/data/(\d+)/')


def pubs_of(urls):
    """Distinct publishing ORIGINS behind a list of URLs.

    Two refinements the host alone gets wrong, both learned from real findings:
    - **Every EIA release is ONE origin.** Jan2021 + Aug2026 + the historical sheet are the
      same publisher saying the same thing at different times, never corroboration.
    - **An EDGAR filing's publisher is its FILER, not sec.gov.** Two filings by ONE registrant
      are one origin; two filings by two DIFFERENT registrants are two, even though both sit on
      sec.gov. The filer is the CIK in the `/Archives/edgar/data/<CIK>/` path (P6898 and P7785
      both turn on this: Williams' 10-K plus Southwest Gas Holdings' filing are genuinely two
      independent companies reporting the same ownership).
    """
    out = set()
    for u in urls:
        u = unwrap(u)
        h = urlparse(u).netloc.replace('www.', '').lower()
        if 'eia.gov' in h:
            out.add('eia.gov')
        elif 'sec.gov' in h and EDGAR_CIK.search(u):
            out.add('sec.gov/cik:' + EDGAR_CIK.search(u).group(1))
        else:
            out.add(h)
    return out


def audit(fp):
    s = json.load(open(fp))
    pid = os.path.basename(fp)[:-5]
    p, info = [], []
    for sec in SECTIONS:
        for i, r in enumerate(s.get(sec) or []):
            tag = f'{sec}[{i}]'
            refs = r.get('proposed_refs') or []
            vs = r.get('verifications') or []
            co, tier, ind = r.get('class_out'), r.get('tier'), r.get('independent')

            for u in refs:
                if any(b in u for b in GEM):     p.append(f'{tag} RULE-1: GEM ref {u}')
                if any(b in u for b in BAN):     p.append(f'{tag} BANNED host {u}')
                if any(b in u for b in BAD_EIA): p.append(f'{tag} undated/nav EIA ref {u}')
                if 'browse-edgar' in u:          p.append(f'{tag} EDGAR nav feed {u}')
            for v in vs:
                if v.get('ok') and 'name_found' not in v:
                    info.append(f'{tag} ok verification lacks name_found (backfill pre-merge)')
                # Rule 1 bans CITING GEM, i.e. a GEM URL in a ref/verification/url field.
                # Naming gem.wiki in prose to report what a carried citation says (or that it
                # is not citable) is provenance on an audit-only tab -- not a violation.
                if any(b in (v.get('url') or '') for b in GEM):
                    p.append(f'{tag} RULE-1: GEM verification url {v.get("url")}')

            # --- tier vs evidence -------------------------------------------------------
            # Where verifications are recorded, count over the refs that actually verified.
            # Where they are NOT (validity records, by convention), count over proposed_refs.
            if vs:
                basis = 'verified ref'
                n = len(pubs_of([v.get('url', '') for v in vs
                                 if v.get('ok') and v.get('contains_value')]))
            else:
                basis = 'proposed_ref'
                n = len(pubs_of(refs))
            if tier == 'high' and n < 2:
                p.append(f'{tag} tier=high on {n} {basis} publisher(s)'
                         + (' — an empty evidence list cannot support "high"' if n == 0 else ''))
            if ind and n < 2:
                p.append(f'{tag} independent=True on {n} {basis} publisher(s)'
                         + (' — nothing is independent of nothing' if n == 0 else ''))

            if co == 'UNRESOLVED':
                if refs:          p.append(f'{tag} UNRESOLVED carries {len(refs)} ref(s)')
                if tier != 'low': p.append(f'{tag} UNRESOLVED tier={tier}, must be low')
                if any(v.get('ok') and v.get('contains_value') for v in vs):
                    p.append(f'{tag} UNRESOLVED but a verification is ok+contains_value')
            if co in ('REFS_ADDED', 'REVERIFIED'):
                if not refs:                     p.append(f'{tag} sourced {co} with no refs')
                if not (r.get('values') or {}):  p.append(f'{tag} sourced {co} with empty values')
                if not isinstance(r.get('values'), dict): p.append(f'{tag} values is not a dict')

            # `contested` is {backend column: candidate value} -- the ONLY thing that puts a
            # concern on the paste surface. Prose in `contested` is a defect.
            c = r.get('contested')
            if c is not None and not isinstance(c, dict):
                p.append(f'{tag} contested is not a dict')
            for col, val in (c or {}).items():
                if col in LOWER and isinstance(val, str) and val != val.lower():
                    p.append(f'{tag} contested {col}={val!r} must be lowercase')

    if not isinstance(s.get('validity'), (list, type(None))):
        p.append('validity is not a list')
    for i, sr in enumerate(s.get('status_reviews') or []):
        pc = sr.get('proposed_changes')
        if pc is not None and not isinstance(pc, dict):
            p.append(f'status_reviews[{i}] proposed_changes is not a dict')
        pc = pc or {}
        if sr.get('verdict') == 'change' and not pc:
            p.append(f'status_reviews[{i}] verdict=change with empty proposed_changes')
        for col, val in pc.items():
            if col in LOWER and isinstance(val, str) and val and val != val.lower():
                p.append(f'status_reviews[{i}] {col}={val!r} must be lowercase')
        st = pc.get('Status')
        if st in LIVE:
            for col in ('CancelledYear', 'ShelvedYear', 'ShelvedCancelledType'):
                if pc.get(col):
                    p.append(f'status_reviews[{i}] Status={st} but {col}={pc[col]!r}')
    for l in (s.get('cross_row_leads') or []):
        # older shards write cross_row_leads as bare strings, newer ones as dicts
        u = l.get('url') or '' if isinstance(l, dict) else str(l)
        if any(b in u for b in GEM):
            p.append(f'cross_row_leads RULE-1: GEM url {u}')
    return pid, p, info


def main(argv):
    quiet = '--quiet' in argv or '-q' in argv
    tgt = [a for a in argv if not a.startswith('-')]
    if not tgt:
        print(__doc__)
        return 2
    files = []
    for t in tgt:
        files += sorted(glob.glob(os.path.join(t, '*.json'))) if os.path.isdir(t) else [t]
    bad = 0
    for fp in files:
        pid, probs, info = audit(fp)
        if probs:
            bad += 1
            print(f'{pid}:')
            for x in probs:
                print('   ', x)
        elif not quiet:
            print(f'{pid}: clean'
                  + (f'  [{len(info)} pre-merge backfill note(s)]' if info else ''))
    print(f'\n{len(files)} shard(s), {bad} with findings')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
