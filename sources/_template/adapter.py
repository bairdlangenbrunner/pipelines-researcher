"""Template adapter — OPTIONAL.

Most sources need NO adapter: the declarative loader in scripts/ingest.py reads the
manifest and does everything. Add an adapter only when a source needs custom parsing
the manifest can't express (odd geometry joins, a sidecar attribute table,
reconstructing an unstable OID, parsing "(NN%)" owner strings, dropping junk fields).

To enable: set `adapter: adapter.py:MyAdapter` in manifest.yml, then override only
the hooks you need. Everything else falls back to the declarative default.

Contract (see scripts/adapter_base.py for the base class and the default impls):

    class AdapterBase:
        def __init__(self, manifest: dict, dataset: dict, paths): ...
        def iter_raw(self, dataset) -> Iterator[dict]:
            # yield {"properties": {...}, "geometry": <geojson|None>}
        def to_canonical(self, raw: dict, dataset) -> "CanonicalSegment | None":
            # map ONE raw feature -> a CanonicalSegment (or None to skip)
        def normalize_geometry(self, raw, dataset) -> "geojson | None":
            # return WGS84 geometry (reproject if the dataset CRS differs)
"""

from adapter_base import AdapterBase  # scripts/ is put on sys.path by ingest.py


class MyAdapter(AdapterBase):
    """Override only what you need; delete the methods you don't."""

    def to_canonical(self, raw, dataset):
        # Example: start from the declarative mapping, then fix up one field.
        rec = super().to_canonical(raw, dataset)
        if rec is None:
            return None
        # e.g. rec.owners = parse_percent_owners(raw["properties"].get("Shareholde"))
        return rec
