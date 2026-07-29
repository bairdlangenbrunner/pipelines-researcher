"""Canonical record + adapter contract for the reference-dataset registry.

`ingest.py` uses `DeclarativeAdapter` by default (manifest-only sources). A source
provides its own `adapter.py:Class` (subclassing `AdapterBase`) ONLY when the
declarative path can't express it; it overrides just the hooks it needs.

Canonical schema: sources/_schema/canonical_record.md
Manifest schema:  sources/_schema/manifest.schema.json
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, fields as dc_fields
from pathlib import Path
from typing import Iterator, Optional

import normalize as N

# CRS strings we treat as WGS84 lon/lat (pass-through, no reprojection)
_WGS84 = {"EPSG:4326", "4326", "urn:ogc:def:crs:OGC:1.3:CRS84", "CRS84", "OGC:CRS84"}


# --------------------------------------------------------------------------- #
# Geometry helpers (geojson dicts in; EPSG:4326 assumed)
# --------------------------------------------------------------------------- #
def _iter_lines(geom: dict | None):
    if not geom:
        return
    t = geom.get("type")
    c = geom.get("coordinates") or []
    if t == "LineString":
        if c:
            yield c
    elif t == "MultiLineString":
        for part in c:
            if part:
                yield part


def geom_endpoints(geom: dict | None):
    """First and last vertices as (lon, lat), or (None, None)."""
    lines = list(_iter_lines(geom))
    if not lines:
        return None, None
    first, last = lines[0][0], lines[-1][-1]
    return [round(first[0], 6), round(first[1], 6)], [round(last[0], 6), round(last[1], 6)]


def geodesic_km(geom: dict | None) -> float | None:
    """Sum of geodesic segment lengths (WGS84) in km. None if no usable geometry.
    This is the reliable length — never trust an embedded projected shape-length."""
    lines = list(_iter_lines(geom))
    if not lines:
        return None
    try:
        from pyproj import Geod
    except Exception:
        return None
    geod = Geod(ellps="WGS84")
    total = 0.0
    for line in lines:
        if len(line) < 2:
            continue
        lons = [p[0] for p in line]
        lats = [p[1] for p in line]
        total += geod.line_length(lons, lats)
    return round(total / 1000.0, 3) if total else None


def _stable_hash(*parts) -> str:
    raw = "||".join("" if p is None else str(p) for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


def _clean_url(u) -> str | None:
    if not u:
        return None
    s = str(u).strip()
    if not s or s in ("-", "--"):
        return None
    low = s.lower()
    if "gem.wiki" in low or "globalenergymonitor" in low:  # never cite GEM (standing rule 1)
        return None
    return s


# --------------------------------------------------------------------------- #
# Canonical record
# --------------------------------------------------------------------------- #
@dataclass
class CanonicalSegment:
    ref_id: str
    source: str
    dataset: str
    source_tier: int
    commodity: str
    country: str = ""
    country_raw: str = ""
    name: str = ""
    name_norm: str = ""
    aliases: list = field(default_factory=list)
    status: Optional[str] = None
    status_raw: str = ""
    start_loc: str = ""
    end_loc: str = ""
    start_pt: Optional[list] = None
    end_pt: Optional[list] = None
    diameter_in: list = field(default_factory=list)
    diameter_raw: str = ""
    length_km: Optional[float] = None
    length_raw: str = ""
    geodesic_km: Optional[float] = None
    capacity: Optional[float] = None
    capacity_units: str = ""
    capacity_raw: str = ""
    operator: str = ""
    owners: list = field(default_factory=list)
    start_year: Optional[int] = None
    description: str = ""
    has_geometry: bool = False
    geometry_ref: str = ""
    source_url: Optional[str] = None
    report_citation: str = ""
    _raw: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in dc_fields(self)}


# --------------------------------------------------------------------------- #
# Adapter base + declarative default
# --------------------------------------------------------------------------- #
class AdapterBase:
    """Override only the hooks a source needs; the rest fall back to declarative."""

    def __init__(self, manifest: dict, source_path: Path):
        self.manifest = manifest
        self.source_path = Path(source_path)
        self.source = manifest["source"]
        self.tier = int(manifest.get("source_tier", 4))
        self.display_name = manifest.get("display_name", self.source)
        prov = manifest.get("provenance", {}) or {}
        self.oid_field = prov.get("oid_field")
        self.oid_stability = prov.get("oid_stability", "stable")
        self.scraped_date = prov.get("scraped_date", "unknown")
        self.default_crs = manifest.get("default_crs", "EPSG:4326")

    # -- hooks ------------------------------------------------------------- #
    def iter_raw(self, dataset: dict) -> Iterator[dict]:
        """Yield {'properties': {...}, 'geometry': <geojson|None>} per source feature."""
        fmt = dataset["format"]
        path = (self.source_path / dataset["path"])
        if fmt == "geojson":
            with open(path) as f:
                gj = json.load(f)
            for feat in gj.get("features", []):
                yield {"properties": dict(feat.get("properties") or {}),
                       "geometry": feat.get("geometry")}
        elif fmt in ("shapefile", "gpkg"):
            import fiona
            with fiona.open(path) as src:
                for feat in src:
                    g = feat.get("geometry")
                    yield {"properties": dict(feat["properties"]),
                           "geometry": dict(g) if g else None}
        elif fmt == "csv":
            import csv
            gcol = dataset.get("geometry_column")
            wkt_mode = dataset.get("geometry") == "wkt_column"
            with open(path, newline="") as f:
                for row in csv.DictReader(f):
                    geom = None
                    if wkt_mode and gcol and row.get(gcol):
                        geom = _wkt_to_geojson(row[gcol])
                    yield {"properties": dict(row), "geometry": geom}
        else:
            raise ValueError(f"unknown dataset format: {fmt}")

    def normalize_geometry(self, raw: dict, dataset: dict) -> dict | None:
        geom = raw.get("geometry")
        if not geom or not geom.get("coordinates"):
            return None
        crs = dataset.get("crs", self.default_crs)
        if crs not in _WGS84:
            geom = _reproject_geom(geom, crs)
        return geom

    def to_canonical(self, raw: dict, dataset: dict) -> Optional[CanonicalSegment]:
        props_all = raw.get("properties", {}) or {}
        garbage = set(dataset.get("ignore_garbage_fields", []) or [])
        props = {k: v for k, v in props_all.items() if k not in garbage}
        cmap = dataset.get("column_map", {}) or {}
        units = dataset.get("units", {}) or {}
        ds_name = dataset["name"]

        def val(field_name: str):
            const_key = field_name + "_const"
            if const_key in cmap:
                return cmap[const_key]
            src_key = cmap.get(field_name)
            return props.get(src_key) if src_key else None

        # commodity
        commodity = dataset.get("commodity_default", "")
        fuel_field = dataset.get("fuel_field")
        fuel_map = dataset.get("fuel_map", {}) or {}
        if fuel_field and props.get(fuel_field) is not None:
            commodity = fuel_map.get(str(props.get(fuel_field)).strip(), commodity)

        name = (val("name") or "").strip()
        country_raw = (val("country") or props.get("country") or "").strip()
        country = N.normalize_country(country_raw)
        # A scraped dataset can tabulate one country's block in different units than the
        # column header claims (GulfPub gas 'Length' is miles everywhere except Canada).
        # units.length_units_by_country overrides the dataset default; keys are matched
        # on the NORMALIZED country, so a manifest may write any alias.
        length_units = units.get("length_units", "km")
        for _ck, _cu in (units.get("length_units_by_country") or {}).items():
            if N.normalize_country(_ck) == country:
                length_units = _cu
                break
        start_loc = (val("start_loc") or "").strip()
        end_loc = (val("end_loc") or "").strip()
        status_raw = (val("status") or "").strip()

        geom = self.normalize_geometry(raw, dataset)
        start_pt, end_pt = geom_endpoints(geom)

        oid = props.get(self.oid_field) if self.oid_field else None
        oid = None if oid in (None, "", " ") else str(oid).strip()
        if oid is not None:
            ref_id = f"{self.source}:{ds_name}:{oid}"
        else:
            ref_id = f"{self.source}:{ds_name}:h{_stable_hash(name, country_raw, start_loc, end_loc)}"

        rec = CanonicalSegment(
            ref_id=ref_id,
            source=self.source,
            dataset=ds_name,
            source_tier=self.tier,
            commodity=commodity,
            country=country,
            country_raw=country_raw,
            name=name,
            name_norm=N.normalize_name(name),
            status=N.map_status(status_raw, dataset.get("status_map")),
            status_raw=status_raw,
            start_loc=start_loc,
            end_loc=end_loc,
            start_pt=start_pt,
            end_pt=end_pt,
            diameter_in=N.parse_diameter_set(val("diameter_raw"), units.get("diameter_units", "in")),
            diameter_raw=str(val("diameter_raw") or "").strip(),
            length_km=N.parse_length_km(val("length_raw"), length_units),
            length_raw=str(val("length_raw") or "").strip(),
            geodesic_km=geodesic_km(geom),
            capacity=N.parse_number(val("capacity")),
            capacity_units=str(val("capacity_units") or "").strip(),
            capacity_raw=str(val("capacity_raw") or "").strip(),
            operator=str(val("operator") or "").strip(),
            owners=N.parse_owners(val("owners")),
            start_year=N.parse_year(val("start_year")),
            description=str(val("description") or "").strip(),
            has_geometry=geom is not None,
            geometry_ref=ref_id,
            source_url=_clean_url(val("source_url")),
            report_citation=f"{self.display_name}, {ds_name}, scraped {dataset.get('scraped_date') or self.scraped_date}",
            _raw=props,
        )
        rec.__dict__["_geometry"] = geom  # transient; ingest moves this to the sidecar
        return rec


class DeclarativeAdapter(AdapterBase):
    """The manifest-only default. Most sources (incl. GulfPub) need nothing more."""
    pass


# --------------------------------------------------------------------------- #
# Optional format helpers (lazy)
# --------------------------------------------------------------------------- #
def _wkt_to_geojson(wkt: str) -> dict | None:
    try:
        from shapely import wkt as shapely_wkt
        from shapely.geometry import mapping
        return mapping(shapely_wkt.loads(wkt))
    except Exception:
        return None


def _reproject_geom(geom: dict, crs: str) -> dict:
    from pyproj import Transformer
    tf = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)

    def reproj_line(line):
        return [list(tf.transform(x, y)) for x, y in line]

    t = geom.get("type")
    if t == "LineString":
        return {"type": t, "coordinates": reproj_line(geom["coordinates"])}
    if t == "MultiLineString":
        return {"type": t, "coordinates": [reproj_line(l) for l in geom["coordinates"]]}
    return geom
