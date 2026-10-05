"""US gas discovery seeds: EIA Natural Gas Pipeline Projects with no GEM match (run from repo root).

Input: the EIA crosswalk re-run on the 2026-10-02 snapshot (eia_crosswalk_20261002.json) +
sources/eia_pipeline_projects/data/eia_projects_latest.csv. An EIA project is unmatched when no GEM
row lists it as a candidate at any tier. Baird 2026-10-02: all history, >=25 km floor (15.5 mi), five
regional slices. Seeds = unmatched, not a reversal/abandonment, and miles >= 15.5 (or miles blank on a
new pipeline / lateral / conversion). Everything else unmatched is written to below_floor.csv, not seeded.
"""
import json, re, pandas as pd
D = 'batches/united-states-gas/staging/discovery-seeds-20261002'
X = json.load(open(f'{D}/eia_crosswalk_20261002.json'))
matched = {c['project_key'] for r in X['rows'].values() for c in r['candidates']}
e = pd.read_csv('sources/eia_pipeline_projects/data/eia_projects_latest.csv', low_memory=False, dtype=str).fillna('')
um = e[~e.project_key.isin(matched)].copy()
um['mi'] = pd.to_numeric(um.miles.str.replace(',', ''), errors='coerce')
REGION = {
 'tx-permian': 'TX NM',
 'gulf': 'LA MS AL FL GM',
 'appalachian-se': 'PA OH WV VA MD DE DC KY TN GA SC NC',
 'midcon-north': 'OK KS NE IA MO AR IL IN MI WI MN ND SD',
 'west-ne-ak': 'CA NV UT AZ CO WY MT ID OR WA AK NY NJ CT MA RI NH VT ME',
}
ST2R = {s: r for r, ss in REGION.items() for s in ss.split()}
def states(r):
    return [s for s in re.split(r'[^A-Z]+', (r.beg_state + ',' + r.state_s).upper()) if len(s) == 2]
def region(r):
    for s in states(r):
        if s in ST2R: return ST2R[s]
    return 'west-ne-ak' if 'ALASKA' in r.project_name.upper() else 'unassigned'
um['region'] = um.apply(region, axis=1)
seedable = (~um.project_type.isin(['Reversal', 'Abandonment'])) & (
    (um.mi >= 15.5) | (um.mi.isna() & um.project_type.isin(['New Pipeline', 'Lateral', 'Conversion'])))
um[~seedable].to_csv(f'{D}/below_floor.csv', index=False)
s = um[seedable].copy()
s['nkey'] = s.project_name.str.lower().str.replace(r'[^a-z0-9]+', ' ', regex=True).str.strip()
seeds = []
for nkey, g in s.groupby('nkey', sort=False):
    r = g.sort_values('last_release').iloc[-1]
    ops = '; '.join(dict.fromkeys(g.pipeline_operator_name))
    mi = r.miles or 'blank'
    hint = [f"EIA {r.project_type}", f"EIA status {r.status}" + (f" ({r.status_history})" if r.status_history else ''),
            f"in service {r.year_in_service_date or '?'}", f"states {r.state_s}", f"diameter {r.pipeline_diameter_inches or '?'} in",
            f"capacity +{r.additional_capacity_mmcf_d or '?'} MMcf/d", f"{r.pipeline_type}",
            f"docket {r.docket_number}" if r.docket_number else '',
            f"EIA cite: {r.last_file} sheet '{r.last_sheet}' row {r.last_excel_row}",
            f"EIA notes: {r.notes_latest[:220]}" if r.notes_latest else '']
    seeds.append({'seed_id': 'eia:' + re.sub(r'[^a-z0-9]+', '-', nkey)[:60].strip('-'), 'name': r.project_name,
                  'length': f"EIA: {mi} mi", 'operator': ops, 'kind': r.project_type,
                  'name_hint': ' | '.join(h for h in hint if h), 'region': r.region})
ids = [x['seed_id'] for x in seeds]; assert len(ids) == len(set(ids))
json.dump({'seeds': seeds}, open(f'{D}/seeds_by_region.json', 'w'), indent=1)
print(len(um), 'unmatched;', len(seeds), 'seeds;', (~seedable).sum(), 'below floor')
print(pd.Series([x['region'] for x in seeds]).value_counts().to_dict())
