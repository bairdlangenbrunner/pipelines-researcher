"""Build country-discovery args for a Russia gas slice from the D1 template + seed list (run from repo root)."""
import json, sys, os
ST = 'batches/russia-gas/staging'
D = json.load(open(f'{ST}/discovery-seeds-20260930/seeds_by_district.json'))['seeds']
STORE = json.load(open(f'{ST}/discovery-seeds-20260930/store_leads.json'))
SLICES = {
 'D2': ('discovery-d2-siberian-20260930', 'Siberian', 'SIBERIAN Federal District (Irkutsk, Krasnoyarsk, Kemerovo/Kuzbass, Novosibirsk, Omsk, Tomsk, Altai Krai/Republic, Khakassia, Tyva, Zabaykalsky/Buryatia only where they feed Siberia)',
   'Kovykta-Irkutsk extensions, Krasnoyarsk, Kuzbass, Altai (Power of Siberia 2 / Soyuz Vostok feeds), Tomsk/Omsk/Novosibirsk trunks and GRS spurs'),
 'D3': ('discovery-d3-ural-20260930', 'Ural', 'URAL Federal District (Yamalo-Nenets, Khanty-Mansi, Tyumen south, Sverdlovsk, Chelyabinsk, Kurgan; Perm/Orenburg only where they feed the Urals)',
   'Arctic LNG 2 / Ob LNG feeds, Kharasavey, Tambey, Gydan, Yamal field-to-KS links, Sverdlovsk/Chelyabinsk GRS spurs >=25 km, Nizhnyaya Tura-Perm III'),
 'D4': ('discovery-d4-northwest-20260930', 'Northwestern', 'NORTHWESTERN Federal District (Leningrad, Novgorod, Pskov, Vologda, Arkhangelsk incl. Nenets, Komi, Karelia, Murmansk, Kaliningrad, St Petersburg)',
   'Ust-Luga complex feed, Volkhov-Murmansk, Kaliningrad, Karelia, Arkhangelsk, Nyuksenitsa-Arkhangelsk, Leningrad-Vyborg-border, Valday-Borovichi (GulfPub candidate), GRS spurs >=25 km'),
}
def line(s):
    km = s.get('total_km'); n = s['name']
    bits = [f"{n}", f"~{km} km merged OSM" if km else "length unknown"]
    for k, l in (('kind_hint', 'kind'), ('operator', 'operator'), ('name_hint', 'name_hint (existing row? match first)')):
        if s.get(k): bits.append(f"{l}: {s[k]}")
    return '- ' + '; '.join(bits)
for key in sys.argv[1:]:
    slug, dist, scope, leads = SLICES[key]
    a = json.load(open(f'{ST}/discovery-d1-fareast-20260930/args.json'))
    seeds = [s for s in D if s['slice'] == key and s['bucket'] in ('seed', 'seed_length_unknown')]
    store = [s for s in STORE if s['district'] == dist and s['seed_id'] not in {x['seed_id'] for x in seeds}]
    mon = [s for s in D if s['slice'] == key and s['bucket'] == 'monitor']
    ex = [f"## This run: Russia gas, slice {key} = {scope}",
          "Search ONLY this district (plus cross-border lines whose Russian end is here). The roster below is the FULL national roster - match against all of it.",
          "Window: announcements from the last ~3 years PLUS operating/built lines GEM never captured. Length rule: >=25 km only; uncertain length -> say so.",
          "Territory naming follows docs/reference/gem_naming_conventions/ (occupied Ukraine = Ukraine; Abkhazia = Georgia).",
          f"Thematic leads: {leads}.",
          "Seed leads from OSM recon (verify, and match-to-existing before anything else; OSM is a lead source only, never a [ref]):"]
    ex += [line(s) for s in seeds]
    for s in store:
        ex.append(f"- STORE LEAD: {s['name']}; length {s.get('km') or 'unknown'}; {s['note']}")
    if mon:
        ex.append("Known SHORT items already on the monitor list (<25 km, do not re-report): " + '; '.join(f"{s['name']} ({s['total_km']} km)" for s in mon))
    a['extra'] = '\n'.join(ex)
    a['staging'] = f'{ST}/{slug}'
    a['modelSearch'] = 'sonnet'; a['modelVet'] = 'sonnet'; a['modelConsolidate'] = 'opus'
    os.makedirs(f'{ST}/{slug}', exist_ok=True)
    json.dump(a, open(f'{ST}/{slug}/args.json', 'w'), ensure_ascii=False)
    print(key, len(seeds), 'seeds', len(store), 'store', len(mon), 'monitor', len(json.dumps(a, ensure_ascii=False)), 'bytes')
