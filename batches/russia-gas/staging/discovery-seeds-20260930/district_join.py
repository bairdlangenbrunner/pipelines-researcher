"""District join for the Russia discovery seed list: assigns each reference trace to the federal district
holding the largest share of its length (same Natural Earth admin-1 + district mapping as the state audit,
state-audit-20260914/audit_russia.py — NE's own `region` column is stale for Buryatia/Zabaykalsky).
Importable: district_shares(geojson_geometry) -> {district: km}."""
import os, pandas as pd, geopandas as gpd
from shapely.geometry import shape
NE = os.path.expanduser('~/Dropbox/_gis-data/_natural_earth_data/ne_10m_admin_1_states_provinces/'
                        'ne_10m_admin_1_states_provinces.shp')
adm = gpd.read_file(NE)[['name', 'name_en', 'iso_a2', 'type_en', 'geometry']].to_crs(4326)
adm.loc[(adm.iso_a2 == 'RU') & (adm.name == 'Altay'), 'name_en'] = 'Altai Krai'   # NE mislabels the krai
adm.loc[(adm.iso_a2 == 'RU') & (adm.name == 'Chita'), 'name_en'] = 'Zabaykalsky Krai'
adm['name_en'] = adm['name_en'].fillna(adm['name'])
adm = adm[adm['name_en'].notna()].copy()
adm['canon'] = adm.apply(lambda r: r['name_en'] if r['iso_a2'] == 'RU' else f"{r['name_en']} ({r['iso_a2']})", axis=1)
RU_SUBJECTS = set(adm[adm.iso_a2 == 'RU']['canon'])
sidx = adm.sindex
NEIGHBOURS = ['RU', 'NO', 'FI', 'SE', 'DK', 'EE', 'LV', 'LT', 'PL', 'DE', 'BY', 'UA', 'GE', 'AZ', 'AM', 'TR',
              'BG', 'RO', 'KZ', 'UZ', 'TM', 'IR', 'MN', 'CN', 'KP', 'KR', 'JP']
adm_p = adm[adm.iso_a2.isin(NEIGHBOURS)].to_crs(3576).reset_index(drop=True)  # North Pole LAEA Russia — metres;
sidx_p = adm_p.sindex                                                           # neighbours only (Antarctica explodes in 3576)

DISTRICT = {}
for d, names in {
    'Central': ['Belgorod', 'Bryansk', 'Vladimir', 'Voronezh', 'Ivanovo', 'Kaluga', 'Kostroma', 'Kursk',
                'Lipetsk', 'Moscow Oblast', 'Moscow', 'Oryol', 'Ryazan', 'Smolensk', 'Tambov', 'Tver', 'Tula',
                'Yaroslavl'],
    'Northwestern': ['Arkhangelsk', 'Vologda', 'Kaliningrad', 'Republic of Karelia', 'Komi', 'Leningrad',
                     'Murmansk', 'Nenets', 'Novgorod', 'Pskov', 'Saint Petersburg'],
    'Southern': ['Republic of Adygea', 'Astrakhan', 'Volgograd', 'Republic of Kalmykia', 'Krasnodar',
                 'Rostov', 'Autonomous Republic of Crimea', 'Sevastopol'],
    'North Caucasian': ['Republic of Dagestan', 'Republic of Ingushetia', 'Kabardino-Balkar',
                        'Karachay-Cherkess', 'Republic of North Ossetia-Alania', 'Chechen', 'Stavropol'],
    'Volga': ['Republic of Bashkortostan', 'Kirov', 'Mari El', 'Republic of Mordovia', 'Nizhny Novgorod',
              'Orenburg', 'Penza', 'Perm', 'Samara', 'Saratov', 'Republic of Tatarstan', 'Udmurt',
              'Ulyanovsk', 'Chuvash'],
    'Ural': ['Kurgan', 'Sverdlovsk', 'Tyumen', 'Khanty-Mansi', 'Chelyabinsk', 'Yamalo-Nenets'],
    'Siberian': ['Altai Republic', 'Altai Krai', 'Irkutsk', 'Kemerovo', 'Krasnoyarsk', 'Novosibirsk', 'Omsk',
                 'Tomsk', 'Tuva', 'Republic of Khakassia'],
    'Far Eastern': ['Amur', 'Republic of Buryatia', 'Jewish', 'Zabaykalsky', 'Kamchatka', 'Magadan',
                    'Primorsky', 'Sakha', 'Sakhalin', 'Khabarovsk', 'Chukotka'],
}.items():
    for n in names:
        hits = [c for c in RU_SUBJECTS if c == n or c.startswith(n + ' ') or c.startswith(n + '-')]
        if n == 'Moscow': hits = ['Moscow']
        for h in hits: DISTRICT[h] = d
unmapped = RU_SUBJECTS - set(DISTRICT)
assert not unmapped, f'subjects without a district: {unmapped}'

_ru = adm[adm.iso_a2 == 'RU'].copy()
_ru['district'] = _ru['canon'].map(DISTRICT)
_ru_m = _ru.to_crs(3576)
_sidx = _ru_m.sindex

def district_shares(geom):
    """km of the trace inside each RU district (traces outside RU polygons -> 'OUTSIDE')."""
    g = gpd.GeoSeries([shape(geom)], crs=4326).to_crs(3576).iloc[0]
    out, used = {}, 0.0
    for i in _sidx.query(g, predicate='intersects'):
        seg = g.intersection(_ru_m.geometry.iloc[i])
        if seg.length > 0:
            d = _ru_m['district'].iloc[i]; out[d] = out.get(d, 0) + seg.length / 1000; used += seg.length / 1000
    tot = g.length / 1000
    if tot - used > 0.5: out['OUTSIDE'] = tot - used
    return out
