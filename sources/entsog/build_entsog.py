"""Extract ENTSOG SYSCAP 2026 pipeline geometry to three status-split GeoJSONs."""
import fitz, numpy as np, pyproj, json, re, collections

SRC = "ENTSOG_GIE_SYSCAP_2026_1600x1200_FULL_016_FLAT.pdf"
a = np.load('affine_icp.npz'); W, v = a['W'], a['v']  # page-pt -> EPSG:3857 affine (coastline ICP fit)
to_ll = pyproj.Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)


def page2ll(p):
    m = np.asarray(p, float) @ W + v
    lo, la = to_ll.transform(m[:, 0], m[:, 1])
    return np.column_stack([lo, la])


BUILT = {'= PIPELINES-LARGE =': 'DN900+ (36" and over)',
         '= PIPELINES-MEDIUM =': 'DN600-900 (24" to 36")',
         '= PIPELINES-SMALL =': 'DN600 (under 24")'}
PROJ = {'= PIPELINES-PROJ =', '= PIPELINES PROJ LEGACY (2022)', '2024 PROJ /// TRA'}


def dash_kind(s):
    """legend: solid | even dash = project | dash-dot-dot = not operational"""
    nums = [float(x) for x in re.findall(r'[\d.]+', s or '')]
    nums = [n for n in nums if n > 0]
    if not nums:
        return 'solid'
    if len(nums) >= 4 and max(nums) / min(nums) >= 2.5:
        return 'dash_dot_dot'
    return 'even_dash'


def subpaths(x):
    cur = []
    for it in x['items']:
        if it[0] == 'l':
            p, q = it[1], it[2]
            if not cur:
                cur = [(p.x, p.y)]
            cur.append((q.x, q.y))
        elif it[0] == 'c':
            p, c1, c2, e = it[1], it[2], it[3], it[4]
            if not cur:
                cur = [(p.x, p.y)]
            for i in range(1, 9):
                t = i / 8; m = 1 - t
                cur.append((m**3*p.x + 3*m*m*t*c1.x + 3*m*t*t*c2.x + t**3*e.x,
                            m**3*p.y + 3*m*m*t*c1.y + 3*m*t*t*c2.y + t**3*e.y))
        else:
            if len(cur) > 1:
                yield cur
            cur = []
    if len(cur) > 1:
        yield cur


doc = fitz.open(SRC)
drawings = doc[0].get_drawings()

# pipeline name labels, isolated via their own optional-content layer
d2 = fitz.open(SRC)
cfg = {c['text']: c['number'] for c in d2.layer_ui_configs()}
for n in cfg.values():
    d2.set_layer_ui_config(n, action=2)
d2.set_layer_ui_config(cfg['--- TEXT // PIPELINES'], action=1)
labels = []
for blk in d2.reload_page(d2[0]).get_text("dict")['blocks']:
    for ln in blk.get('lines', []):
        t = " ".join(s['text'] for s in ln['spans']).strip()
        if t:
            labels.append((t, (ln['bbox'][0]+ln['bbox'][2])/2, (ln['bbox'][1]+ln['bbox'][3])/2))
LP = np.array([[x, y] for _, x, y in labels])
LN = [t for t, _, _ in labels]

out = collections.defaultdict(list)
for x in drawings:
    layer = x.get('layer')
    if layer not in BUILT and layer not in PROJ:
        continue
    kind = dash_kind(x.get('dashes'))
    if kind == 'dash_dot_dot':
        status, basis = 'not_operational', 'legend dash-dot-dot'
    elif layer in PROJ:
        status, basis = 'project', 'layer'
    elif kind == 'even_dash':
        status, basis = 'project', 'legend dash (on a built layer - verify)'
    else:
        status, basis = 'operational', 'solid on built layer'

    for sp in subpaths(x):
        arr = np.array(sp)
        ll = page2ll(arr)
        d = np.hypot(LP[:, 0] - arr[:, 0].mean(), LP[:, 1] - arr[:, 1].mean())
        j = int(d.argmin())
        out[status].append({
            "type": "Feature",
            "properties": {
                "status": status,
                "status_basis": basis,
                "pdf_layer": layer,
                "size_class": BUILT.get(layer),
                "stroke_width_pt": round(x.get('width') or 0, 2),
                "dash_pattern": (x.get('dashes') or '[] 0').strip(),
                "name_nearest": LN[j] if d[j] < 30 else None,
                "name_dist_pt": round(float(d[j]), 1) if d[j] < 30 else None,
                "n_vertices": len(sp),
            },
            "geometry": {"type": "LineString",
                         "coordinates": [[round(p, 6), round(q, 6)] for p, q in ll]},
        })

PROV = {
    "source_pdf": SRC,
    "source_title": "ENTSOG/GIE System Capacity Map 2026 (version January 2026)",
    "source_page": 1,
    "extraction": "PyMuPDF get_drawings(); optional-content (Illustrator layer) attributed",
    "classification": ("map legend 'Transport by pipeline': solid = operational (by size "
                       "class), even dash = project, dash-dot-dot = not operational"),
    "georeferencing": ("page -> EPSG:3857 affine (map states 'WGS 84 / Pseudo-Mercator "
                       "projection'), fitted by trimmed ICP of the PDF's own "
                       "'ne_10m_coastline' layer against Natural Earth 1:10m coastline; "
                       "median residual 1 m, p90 2 m; scale 2707.9 m/pt, rotation 0.0000 deg"),
    "crs": "EPSG:4326",
    "caveats": ("cartographic centrelines, not surveyed routes; casing strokes may draw a "
                "line more than once; name_nearest is an unverified proximity join"),
    "generated_from": "sources/entsog/ + scripts in session scratchpad",
}

stem = "ENTSOG_GIE_SYSCAP_2026_pipelines"
for status in ('operational', 'project', 'not_operational'):
    fc = {"type": "FeatureCollection", "name": f"{stem}_{status}",
          "provenance": dict(PROV, status_subset=status), "features": out[status]}
    fn = f"{stem}_{status}_wgs84.geojson"
    json.dump(fc, open(fn, 'w'))
    tot = 0.0
    for f in out[status]:
        c = np.array(f['geometry']['coordinates'])
        dd = np.diff(c, axis=0)
        tot += float(np.sum(np.hypot(dd[:, 0]*111.32*np.cos(np.radians(c[:-1, 1])),
                                     dd[:, 1]*110.57)))
    named = sum(1 for f in out[status] if f['properties']['name_nearest'])
    print(f"{fn:62}  {len(out[status]):5d} lines  {tot:9.0f} km  {named:5d} name-tagged")
