"""Build the 2026-10-19 ruling 10 re-vet: three monitor leads that the location leg alone, or nearly alone, held back (run from repo root).

Ruling 10 (Baird 2026-10-19, docs/plans/2026-10-16_us-gas-datacenter-subfloor.md): a data center pipeline row needs only a
sourced pipeline project tied to a data center or its power supply; endpoints and the state are not needed, and the state
is filled when it can be inferred, with a note. The three leads are Woodway, the Nexus Fulcrum lateral, and the Stratos
Ruby lateral. There is no search or consolidate step: the queue is written here, and one vetting agent per lead follows
the vetContract in .claude/workflows/country-discovery.js with this run's args.
"""
import glob, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
from build_slice_args import ST  # noqa: E402
from build_recheck_args import SCOPE_1019, VET_1019  # noqa: E402

DATE = '20261019'
RECHECK = f'{ST}/discovery-datacenter-recheck-{DATE}'
WEST = f'{ST}/discovery-datacenter-west-ne-ak-20261016'


def queue_item(run, slug):
    q = json.load(open(f'{run}/discovery/queue.json'))
    return next(x for x in q['queue'] if x['slug'] == slug)


def last_verdict(run, slug):
    p = f'{run}/discovery/vetted/{slug}.json'
    if os.path.exists(p):
        v = json.load(open(p))
        return f"last verdict ({os.path.basename(run)}): {v['class']}. Reason: {v.get('monitor_reason', '')} Notes: {v.get('researcher_notes', '')}"
    q = json.load(open(f'{run}/discovery/queue.json'))
    e = next(x for x in q['seed_ledger'] if x.get('slug') == slug or x['seed_id'].endswith(slug.split('-', 1)[-1]))
    return f"last verdict ({os.path.basename(run)}): {e['disposition']}. Reason: {e.get('reason', '')}"


def main():
    stg = f'{ST}/discovery-datacenter-ruling10-{DATE}'
    os.makedirs(f'{stg}/discovery/vetted', exist_ok=True)
    os.makedirs(f'{stg}/work', exist_ok=True)
    subprocess.run([sys.executable, 'scripts/build_discovery_context.py', '--tracker', 'gas', '--country', 'United States',
                    '--staging', stg, '--out', f'{stg}/args.json'], capture_output=True, text=True, check=True)
    a = json.load(open(f'{stg}/args.json'))

    picks = [
        (RECHECK, 'woodway-hyperscale-data-center-pipeline', 'survey:woodway-hyperscale-line', RECHECK),
        (RECHECK, 'nexus-fulcrum-great-basin-lateral', 'recheck:nexus-fulcrum-lateral', RECHECK),
        (WEST, 'stratos-ruby-lateral', 'recheck:stratos-ruby-lateral', RECHECK),
    ]
    queue, ledger = [], []
    for run, slug, sid, verdict_run in picks:
        item = dict(queue_item(run, slug))
        item['seed_ids'] = [sid]
        item['note'] = (item.get('note', '') + ' RULING 10 RE-VET: ' +
                        last_verdict(verdict_run, slug if verdict_run == run else 'stratos-ruby-lateral'))
        queue.append(item)
        ledger.append({'seed_id': sid, 'name': item['name'], 'disposition': 'queued', 'slug': slug,
                       'reason': 'NEW_ROW candidate under ruling 10 (2026-10-19), re-vetted by one agent.'})
    json.dump({'queue': queue, 'matched': [], 'dropped': [], 'seed_ledger': ledger},
              open(f'{stg}/discovery/queue.json', 'w'), ensure_ascii=False, indent=1)

    prior = sorted(d for d in glob.glob(f'{ST}/discovery-datacenter-*') if 'seeds' not in d and d != stg)
    a.update(staging=stg, scopeRule=SCOPE_1019, vetRule=VET_1019, strategies=[], seeds=[], seedsOnly=True, minKm=0,
             priorStaging=prior, country='United States', commodity='gas')
    json.dump(a, open(f'{stg}/args.json', 'w'), ensure_ascii=False)
    print(stg, len(queue), 'queued', len(a['roster']), 'roster', len(prior), 'prior runs')


if __name__ == '__main__':
    main()
