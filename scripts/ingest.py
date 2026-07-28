#!/usr/bin/env python3
"""Ingest a registered reference dataset into canonical records.

    python scripts/ingest.py --source gulfpub --commodity both --out batches/<scope>/staging/recon-<source>-<date>/

Reads sources/<source>/manifest.yml (validated against the manifest schema), runs
the declarative loader (or the source's adapter.py), and writes:
  - canonical_records.json   (list of CanonicalSegment dicts)
  - geometry_sidecar.json    ({ref_id: geojson geometry})  [derived; gitignored]

No network, no credentials. Output is consumed by reconcile.py.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))  # make adapter_base / normalize importable by source adapters

import paths  # noqa: E402
from adapter_base import DeclarativeAdapter  # noqa: E402

# commodity request -> dataset commodity_default values it includes
_FAMILY = {"oil": {"oil", "ngl"}, "ngl": {"ngl", "oil"}, "gas": {"gas"}, "hydrogen": {"hydrogen"}}


def load_manifest(source: str) -> tuple[dict, Path]:
    src_dir = paths.source_dir(source)
    mpath = src_dir / "manifest.yml"
    if not mpath.exists():
        sys.exit(f"error: no manifest at {mpath}  (sources/{source}/manifest.yml)")
    try:
        import yaml
    except ImportError:
        sys.exit("error: pyyaml not installed — run `pip install -r requirements.txt`")
    manifest = yaml.safe_load(mpath.read_text())
    _validate(manifest)
    return manifest, src_dir


def _validate(manifest: dict) -> None:
    schema_path = paths.sources_dir() / "_schema" / "manifest.schema.json"
    try:
        import jsonschema
    except ImportError:
        print("warn: jsonschema not installed — skipping manifest validation", file=sys.stderr)
        return
    schema = json.loads(schema_path.read_text())
    jsonschema.validate(manifest, schema)


def load_adapter(manifest: dict, src_dir: Path):
    spec = manifest.get("adapter")
    if not spec:
        return DeclarativeAdapter(manifest, src_dir)
    file_part, _, cls_name = spec.partition(":")
    mod_file = src_dir / file_part
    modspec = importlib.util.spec_from_file_location(f"{manifest['source']}_adapter", mod_file)
    mod = importlib.util.module_from_spec(modspec)
    modspec.loader.exec_module(mod)
    return getattr(mod, cls_name)(manifest, src_dir)


def select_datasets(manifest: dict, commodity: str) -> list[dict]:
    datasets = manifest["datasets"]
    if commodity == "both":
        return datasets
    fam = _FAMILY.get(commodity, {commodity})
    sel = [d for d in datasets if d.get("commodity_default") in fam or d.get("name") == commodity]
    if not sel:
        sys.exit(f"error: no dataset in source matches --commodity {commodity} "
                 f"(have: {[d['name'] for d in datasets]})")
    return sel


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True)
    ap.add_argument("--commodity", default="both", choices=["oil", "ngl", "gas", "hydrogen", "both"])
    ap.add_argument("--country", help="optional: keep only this country (normalized match)")
    ap.add_argument("--out", required=True, help="output dir (created if needed)")
    ap.add_argument("--limit", type=int, help="cap records per dataset (debugging)")
    args = ap.parse_args()

    manifest, src_dir = load_manifest(args.source)
    adapter = load_adapter(manifest, src_dir)
    if manifest.get("provenance", {}).get("oid_stability") == "unstable":
        print(f"warn: {args.source} OID is marked unstable — ref_ids are stable within a "
              f"scrape but may differ across scrapes (see sources/{args.source}/NOTES.md)",
              file=sys.stderr)

    import normalize as N
    want_country = N.normalize_country(args.country) if args.country else None

    records: list[dict] = []
    sidecar: dict[str, dict] = {}
    per_dataset: dict[str, int] = {}
    geom_count = 0
    # ref_id is the sidecar key, so a collision does not merely duplicate an id — the
    # second record OVERWRITES the first record's geometry and both are then scored
    # against one trace. OSM's osm_id_key is built from a merged way's contributing ids
    # and is not unique across differently-merged features (Iraq gas 2026-07-28: 3
    # colliding pairs, e.g. w1526687293_1526687294 carrying both a 0.476 km and a
    # 0.095 km trace). Suffix the duplicates and say so.
    seen: dict[str, int] = {}
    collisions: list[str] = []

    for dataset in select_datasets(manifest, args.commodity):
        n = 0
        for raw in adapter.iter_raw(dataset):
            rec = adapter.to_canonical(raw, dataset)
            if rec is None:
                continue
            if want_country and rec.country != want_country:
                continue
            base = rec.ref_id
            seen[base] = seen.get(base, 0) + 1
            if seen[base] > 1:
                collisions.append(base)
                rec.ref_id = f"{base}#{seen[base]}"
                rec.geometry_ref = rec.ref_id
            geom = rec.__dict__.pop("_geometry", None)
            if geom is not None:
                sidecar[rec.geometry_ref] = geom
                geom_count += 1
            records.append(rec.to_dict())
            n += 1
            if args.limit and n >= args.limit:
                break
        per_dataset[dataset["name"]] = n

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "canonical_records.json").write_text(json.dumps(records, indent=1, ensure_ascii=False))
    (out / "geometry_sidecar.json").write_text(json.dumps(sidecar, ensure_ascii=False))

    # summary
    print(f"ingested {len(records)} records from '{args.source}' "
          f"({', '.join(f'{k}={v}' for k, v in per_dataset.items())})"
          f"{f' [country={args.country}]' if args.country else ''}")
    print(f"  with geometry: {geom_count}/{len(records)}")
    if collisions:
        uniq = sorted(set(collisions))
        print(f"  !! {len(collisions)} ref_id collision(s) on {len(uniq)} id(s) — suffixed #2.. to keep "
              f"geometries distinct. The manifest's provenance.oid_field is NOT unique for this "
              f"dataset; cross-scrape identity is unreliable until it is fixed: "
              f"{', '.join(uniq[:5])}{' …' if len(uniq) > 5 else ''}", file=sys.stderr)
    if records:
        import collections
        st = collections.Counter(r["status"] for r in records)
        print(f"  status: {dict(st)}")
        no_status = [r for r in records if r["status"] is None]
        if no_status:
            unmapped = collections.Counter(r["status_raw"] for r in no_status)
            print(f"  UNMAPPED status ({len(no_status)}): {dict(unmapped)}")
    print(f"  -> {out/'canonical_records.json'}")


if __name__ == "__main__":
    main()
