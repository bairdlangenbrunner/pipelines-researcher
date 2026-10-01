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
 'D5': ('discovery-d5-volga-central-20260930', ('Volga', 'Central'), 'VOLGA Federal District (Nizhny Novgorod, Tatarstan, Bashkortostan, Samara, Saratov, Orenburg, Perm, Udmurtia, Kirov, Mari El, Chuvashia, Mordovia, Penza, Ulyanovsk) + CENTRAL Federal District (Moscow city/oblast, Tver, Yaroslavl, Vladimir, Ivanovo, Kostroma, Smolensk, Kaluga, Tula, Ryazan, Bryansk, Oryol, Kursk, Belgorod, Lipetsk, Voronezh, Tambov)',
   'regional gasification trunks and inter-regional branches >=25 km (Gazprom Mezhregiongaz gasification programmes 2021-2025 / 2026-2030), Moscow ring (KGMO) loops and bypasses, Tuchevo-Tver-Mikulino (GulfPub candidate), Orenburg/Bashkortostan/Tatarstan field and GPP links, Saratov/Samara UGS connectors, Kursk/Belgorod/Bryansk border-region branches, Perm/Kirov branches'),
 'D6': ('discovery-d6-south-caucasus-20260930', ('Southern', 'North Caucasian'), 'SOUTHERN Federal District (Krasnodar, Rostov, Volgograd, Astrakhan, Kalmykia, Adygea) + NORTH CAUCASIAN Federal District (Stavropol, Dagestan, Chechnya, Ingushetia, North Ossetia, Kabardino-Balkaria, Karachay-Cherkessia) + the cross-border lines starting there',
   'TurkStream / Blue Stream onshore feeders (Russkaya KS, Southern Corridor strings), Krasnodar-Crimea (GGIT has NO row; RU-UA cross-border per naming conventions, UKR terminus) and any other new line into occupied Ukraine (Donetsk/Luhansk/Zaporizhzhia/Kherson: RU-UA cross-border; lines wholly inside occupied Ukraine are Ukraine-internal - report them flagged out_of_slice, do not vet as Russia), Russia-Abkhazia and Russia-South Ossetia lines (RU-GE per naming conventions), Mozdok-Kazimagomed / Russia-Azerbaijan, North-South via Georgia to Armenia, Astrakhan GPP links, Dagestan/Chechnya gasification trunks, Nevinnomyssk-Mozdok second string'),
}
def line(s):
    km = s.get('total_km'); n = s['name']
    bits = [f"{n}", f"~{km} km merged OSM" if km else "length unknown"]
    for k, l in (('kind_hint', 'kind'), ('operator', 'operator'), ('name_hint', 'name_hint (existing row? match first)')):
        if s.get(k): bits.append(f"{l}: {s[k]}")
    return '- ' + '; '.join(bits)
def slice_args(key):
    slug, dist, scope, leads = SLICES[key]
    a = json.load(open(f'{ST}/discovery-d1-fareast-20260930/args.json'))
    seeds = [s for s in D if s['slice'] == key and s['bucket'] in ('seed', 'seed_length_unknown')]
    dists = dist if isinstance(dist, tuple) else (dist,)
    store = [s for s in STORE if s['district'] in dists and s['seed_id'] not in {x['seed_id'] for x in seeds}]
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


def seeds_rerun(keys, slug):
    """Seeds-only coverage re-run (country-discovery args.seeds): every seed + store lead of the
    given slices becomes a structured seed that must end with a seed_ledger disposition."""
    a = json.load(open(f'{ST}/discovery-d1-fareast-20260930/args.json'))
    seeds, prior = [], []
    for key in keys:
        run, dist, _, _ = SLICES[key]
        prior.append(f'{ST}/{run}')
        dists = dist if isinstance(dist, tuple) else (dist,)
        ss = [s for s in D if s['slice'] == key and s['bucket'] in ('seed', 'seed_length_unknown')]
        for s in ss:
            hint = [h for h in (s.get('name_hint'),
                                s.get('nearest_geom_pid') and f"nearest roster route {s['nearest_geom_pid']}",
                                s.get('diameter_mm') and f"OSM diameter {s['diameter_mm']}",
                                s.get('coverage_by_roster_routes') and f"{s['coverage_by_roster_routes']:.0%} under roster routes",
                                f"district {s['district']}") if h]
            seeds.append({'seed_id': s['seed_id'], 'name': s['name'], 'km': s.get('total_km'),
                          'kind': s.get('kind_hint'), 'operator': s.get('operator'), 'name_hint': '; '.join(hint)})
        ids = {x['seed_id'] for x in ss}
        for s in STORE:
            if s['district'] in dists and s['seed_id'] not in ids:
                seeds.append({'seed_id': s['seed_id'], 'name': s['name'], 'km': s.get('km'),
                              'name_hint': f"store lead: {s['note']}; district {s['district']}"})
    prior += [f'{ST}/discovery-d1-d4-merged-20260930', f'{ST}/discovery-d5-d6-merged-20260930']
    a.update(staging=f'{ST}/{slug}', seeds=seeds, seedsOnly=True, priorStaging=prior, seedChunk=8,
             modelSearch='sonnet', modelVet='sonnet', modelConsolidate='opus')
    a['extra'] = '\n'.join([
        f"## This run: Russia gas SEED COVERAGE re-run (slices {', '.join(keys)})",
        "The earlier discovery runs handed these seeds to a search agent that reported only some of them. Each seed now gets an explicit disposition.",
        "Window: announcements from the last ~3 years PLUS operating/built lines GEM never captured. Length rule: >=25 km with a sourced length -> new row; shorter or unsourced length -> monitor.",
        "Territory naming follows docs/reference/gem_naming_conventions/ (occupied Ukraine = Ukraine; Abkhazia/South Ossetia = Georgia).",
        "Roster PIDs in a seed's hints (name ~ P####, nearest roster route) are match candidates to check FIRST, not conclusions.",
        "Owner convention: Gazprom-system lines -> Owner 'Gazprom PJSC [100.%]', Parent 'Gazprom PJSC [100.00%]'.",
    ])
    os.makedirs(a['staging'], exist_ok=True)
    json.dump(a, open(f"{a['staging']}/args.json", 'w'), ensure_ascii=False)
    print(slug, len(seeds), 'seeds', len(prior), 'prior dirs', len(json.dumps(a, ensure_ascii=False)), 'bytes')


if __name__ == '__main__':
    if sys.argv[1] == '--seeds':
        seeds_rerun(sys.argv[3:], sys.argv[2])
    else:
        for key in sys.argv[1:]:
            slice_args(key)
