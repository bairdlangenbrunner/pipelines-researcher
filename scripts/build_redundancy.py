#!/usr/bin/env python3
"""Stage a redundancy-cluster adjudication (§3 `validity` leg, cluster level) from a data file.

Promoted 2026-09-03 from six per-batch copies (iraq, libya, india, ukraine, kazakhstan,
uzbekistan `staging/redundancy/build_redundancy.py`). Every copy was the same ~80-line
emitter wrapped around a country-specific CLUSTERS table, so the emitter lives here and
the clusters stay where they belong: in the run dir, as data. Read-and-flag only — one
`__VALIDITY__` record per implicated row carrying the CLUSTER-level recommendation, never
an edit (QC detects, Update fixes). Rules: Sweep SOP → "Two follow-on passes".

    python scripts/build_redundancy.py --staging batches/<scope>/staging/redundancy/ \
        --country "<Country>" [--commodity gas|oil] [--csv data/GGIT_gas_snapshot_<date>.csv] \
        [--clusters clusters.json | clusters/ | clusters.py] [--note note.md] \
        [--exclude-pids @batches/<scope>/carried_from_<other>.txt] [--verify-refs] [--out ...]

Cluster data — three accepted shapes, all normalised to one:
  * `clusters.json` (or a `clusters/` dir of one JSON per cluster — the shape the
    adjudicating agents write, from Ukraine): objects with `cluster_id`, `title`,
    optional `verdict` / `summary` / `open_questions`, `sources: [{url, ...}]`, and
    `rows: [{project_id, concern_type, severity, recommendation, notes}]`.
  * `clusters.py`: a module defining `CLUSTERS = {id: {"title", "refs", "rows": {pid:
    (concern_type, recommendation, notes[, severity])}}}` — the in-code shape of the
    kazakhstan / india / libya / uzbekistan copies, so those still load unchanged. An
    optional module-level `NOTE` string is the meta note.
  A row key may carry a `_suffix` (`P5533_E`) when one PID sits in two clusters.
  A row whose concern_type is `none` was examined and CLEARED: it stages as
  CONFIRMED/confirmed so the next sweep sees the question was asked and answered.
  Rows without a severity default to `flag` (`info` when cleared).

Refs: every cluster URL is stripped of MediaWiki fetch artifacts (`&action=raw`), dropped
if it hits a banned/GEM host (standing rules 1 and 5), and — with `--verify-refs` — run
through `url_verifier` (cached in `<staging>/url_verifications.json`). A dropped URL is
recorded in `meta.refs_dropped` with its reason, never silently lost; the prose citing it
is left alone (a 403 is not a deletion).

Output `<staging>/staged_resolutions.json` has the same record + meta shape the six
copies produced (verified identical on the Kazakhstan and Uzbekistan runs, `generated`
aside), so `build_ref_workbook.py`, `staged_summary.py` and the handoff read it as before.
"""
from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]

BANNED_HOSTS = ("gem.wiki", "globalenergymonitor.org", "abarrelfull.wikidot.com",
                "abarrelfull.co.uk", "wikidot.com", "theodora.com")

SNAPSHOT_GLOB = {"gas": "GGIT_gas_snapshot_*.csv", "oil": "GOIT_oil_ngl_snapshot_*.csv"}


# ----------------------------------------------------------------------------- helpers
def _pid(key: str) -> str:
    """`P5533_E` -> `P5533` (a PID in two clusters carries a suffix to keep keys unique)."""
    return str(key).split("_")[0].strip()


def _banned(url: str) -> bool:
    return any(h in url for h in BANNED_HOSTS)


def _clean_url(url: str) -> str:
    u = str(url or "").strip()
    for suffix in ("&action=raw", "?action=raw", "&action=edit", "&printable=yes"):
        if u.endswith(suffix):
            u = u[: -len(suffix)]
    return u


def _tally(vals) -> dict[str, int]:
    d: dict[str, int] = {}
    for v in vals:
        d[v] = d.get(v, 0) + 1
    return d


def _latest_snapshot(commodity: str) -> Path:
    hits = sorted(glob.glob(str(REPO / "data" / SNAPSHOT_GLOB[commodity])))
    if not hits:
        raise SystemExit(f"no {SNAPSHOT_GLOB[commodity]} in data/ — run scripts/refresh_csvs.sh")
    return Path(hits[-1])


def _matching_oo_csv(csv: Path) -> Path | None:
    stamp = csv.stem.rsplit("_", 1)[-1]
    cand = csv.parent / f"GEM_operators_owners_snapshot_{stamp}.csv"
    return cand if cand.exists() else None


def _load_pids(spec: str | None) -> set[str]:
    if not spec:
        return set()
    if spec.startswith("@"):
        return set(Path(spec[1:]).read_text().split())
    return {p.strip() for p in spec.split(",") if p.strip()}


class RefScreen:
    """Banned-host + optional url_verifier screen with an on-disk cache."""

    def __init__(self, staging: Path, verify: bool):
        self.verify = verify
        self.cache_path = staging / "url_verifications.json"
        self.cache = (json.loads(self.cache_path.read_text())
                      if verify and self.cache_path.exists() else {})

    def _verify(self, url: str) -> dict:
        if url not in self.cache:
            sys.path.insert(0, str(REPO / "scripts"))
            from url_verifier import verify_url  # noqa: WPS433 (lazy: network module)
            r = verify_url(url)
            self.cache[url] = {"ok": bool(r.get("ok")), "status": r.get("status"),
                               "reason": r.get("reason") or r.get("note") or ""}
            self.cache_path.write_text(json.dumps(self.cache, indent=1, ensure_ascii=False))
        return self.cache[url]

    def screen(self, urls) -> tuple[list[str], list[tuple[str, str]]]:
        refs: list[str] = []
        dropped: list[tuple[str, str]] = []
        for raw in urls:
            u = _clean_url(raw)
            if not u or u in refs or any(u == x for x, _ in dropped):
                continue
            if _banned(u):
                dropped.append((u, "GEM or banned source — standing rules 1 and 5"))
            elif self.verify:
                res = self._verify(u)
                if res.get("ok"):
                    refs.append(u)
                else:
                    dropped.append((u, f"url_verifier: status={res.get('status')} "
                                       f"{res.get('reason') or ''}".strip()))
            else:
                refs.append(u)
        return refs, dropped


# ----------------------------------------------------------------------------- loaders
def _norm_rows(rows) -> dict[str, tuple[str, str, str, str]]:
    """Both row shapes -> {rowkey: (concern_type, recommendation, notes, severity)}."""
    out: dict[str, tuple[str, str, str, str]] = {}
    if isinstance(rows, dict):                      # in-code shape: {pid: tuple}
        for key, tup in rows.items():
            tup = tuple(tup)
            if len(tup) == 3:
                ctype, rec, notes = tup
                sev = "info" if ctype == "none" else "flag"
            elif len(tup) == 4:
                ctype, rec, notes, sev = tup
            else:
                raise SystemExit(f"row {key}: expected (concern, recommendation, notes[, severity]), got {len(tup)} items")
            out[str(key)] = (ctype, rec, notes, sev)
    else:                                            # agent shape: [{project_id, ...}]
        for r in rows:
            ctype = r.get("concern_type") or "none"
            sev = r.get("severity") or ("info" if ctype == "none" else "flag")
            out[str(r.get("row_key") or r["project_id"])] = (
                ctype, r.get("recommendation", ""), r.get("notes", ""), sev)
    return out


def _from_json_obj(d: dict, screen: RefScreen) -> tuple[str, dict]:
    cid = str(d.get("cluster_id") or d.get("id") or d.get("key"))
    urls = [s.get("url") if isinstance(s, dict) else s for s in d.get("sources", d.get("refs", []))]
    refs, dropped = screen.screen(urls)
    return cid, {
        "title": d.get("title", ""),
        "verdict": d.get("verdict"),
        "summary": d.get("summary", ""),
        "open_questions": d.get("open_questions", []),
        "refs": refs,
        "refs_dropped": dropped,
        "rows": _norm_rows(d.get("rows", [])),
    }


def load_clusters(src: Path, screen: RefScreen) -> tuple[dict[str, dict], str | None]:
    """Return ({cluster_id: cluster}, module NOTE or None) from .py / .json / dir."""
    if src.is_dir():
        clusters: dict[str, dict] = {}
        for path in sorted(src.glob("*.json")):
            cid, cl = _from_json_obj(json.loads(path.read_text()), screen)
            clusters[cid] = cl
        return clusters, None
    if src.suffix == ".json":
        data = json.loads(src.read_text())
        items = data.values() if isinstance(data, dict) and "cluster_id" not in data else data
        if isinstance(data, dict) and "cluster_id" not in data:
            items = [{"cluster_id": k, **v} if "cluster_id" not in v else v for k, v in data.items()]
        clusters = {}
        for obj in items:
            cid, cl = _from_json_obj(obj, screen)
            clusters[cid] = cl
        return clusters, None
    if src.suffix == ".py":
        spec = importlib.util.spec_from_file_location("_clusters_mod", src)
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        raw = getattr(mod, "CLUSTERS", None)
        if not isinstance(raw, dict):
            raise SystemExit(f"{src} defines no CLUSTERS dict")
        clusters = {}
        for cid, cl in raw.items():
            refs, dropped = screen.screen(cl.get("refs", []))
            clusters[str(cid)] = {
                "title": cl.get("title", ""),
                "verdict": cl.get("verdict"),
                "summary": cl.get("summary", ""),
                "open_questions": cl.get("open_questions", []),
                "refs": refs,
                "refs_dropped": dropped,
                "rows": _norm_rows(cl.get("rows", {})),
            }
        return clusters, getattr(mod, "NOTE", None)
    raise SystemExit(f"unrecognised clusters source {src} (want .json, .py or a directory)")


def _default_clusters(staging: Path) -> Path:
    for name in ("clusters.json", "clusters", "clusters.py"):
        p = staging / name
        if p.exists():
            return p
    raise SystemExit(f"no clusters.json / clusters/ / clusters.py in {staging} — pass --clusters")


# ----------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", required=True, help="the redundancy run dir")
    ap.add_argument("--country", required=True)
    ap.add_argument("--commodity", choices=("gas", "oil"), default="gas")
    ap.add_argument("--csv", help="tracker snapshot (default: newest in data/ for the commodity)")
    ap.add_argument("--oo-csv", help="operators/owners snapshot to record in meta (default: same stamp as --csv)")
    ap.add_argument("--clusters", help="clusters.json | clusters/ dir | clusters.py (default: found in --staging)")
    ap.add_argument("--note", help="markdown/text file whose body is meta.note (default: <staging>/note.md, else the module NOTE)")
    ap.add_argument("--exclude-pids", help="comma list or @file of PIDs that are another scope's rows — a cluster naming one is an error")
    ap.add_argument("--source-language", default="en")
    ap.add_argument("--verify-refs", action="store_true", help="run every cluster URL through url_verifier (cached)")
    ap.add_argument("--out", help="output path (default: <staging>/staged_resolutions.json)")
    args = ap.parse_args()

    staging = Path(args.staging)
    csv = Path(args.csv) if args.csv else _latest_snapshot(args.commodity)
    if not csv.is_absolute() and not csv.exists():
        csv = REPO / csv
    oo_csv = Path(args.oo_csv) if args.oo_csv else _matching_oo_csv(csv)
    excl = _load_pids(args.exclude_pids)
    screen = RefScreen(staging, args.verify_refs)
    clusters, module_note = load_clusters(Path(args.clusters) if args.clusters else _default_clusters(staging), screen)

    note = None
    note_path = Path(args.note) if args.note else staging / "note.md"
    if note_path.exists():
        note = note_path.read_text().strip()
    elif module_note:
        note = module_note.strip()
    if not note:
        note = (f"Cluster-level adjudication of the duplicate/overlap questions raised row-by-row "
                f"by the {args.country} {args.commodity} sweep legs. Read-and-flag only; no edits staged.")

    df = pd.read_csv(csv, header=2, low_memory=False, keep_default_na=False, na_values=[])
    df["_sheet_row"] = df.index + 4
    by_pid = {r["ProjectID"]: r for _, r in df.iterrows()}

    resolutions = []
    for key, cl in clusters.items():
        for rowkey, (ctype, rec, notes, severity) in cl["rows"].items():
            pid = _pid(rowkey)
            if pid in excl:
                raise SystemExit(f"{pid} is in --exclude-pids (another scope's row) — out of scope for the research legs")
            row = by_pid.get(pid)
            if row is None:
                raise SystemExit(f"{pid} not found in {csv.name} — snapshot drift, re-check")
            cleared = ctype == "none"
            record = {
                "project_id": pid,
                "sheet_row": int(row["_sheet_row"]),
                "pipeline_name": str(row.get("PipelineName") or ""),
                "segment_name": str(row.get("SegmentName") or ""),
                "ref_col": "__VALIDITY__",
                "value_cols": [],
                "primary_value_col": "",
                "primary_value": "",
                "values": {},
                "current_ref": "",
                "class_in": "VALIDITY",
                # A cleared row (concern_type "none") is CONFIRMED: `staged_store` drops it
                # from the concerns pile but still records the PID as audited.
                "class_out": "CONFIRMED" if cleared else "UNRESOLVED",
                "verdict": "confirmed" if cleared else "concern",
                "concern_type": ctype,
                "severity": severity,
                "recommendation": rec,
                "proposed_refs": cl.get("refs", []),
                "verifications": [],
                "tier": "n/a",
                "independent": False,
                "source_language": args.source_language,
                "wiki": str(row.get("Wiki") or ""),
                "redundancy_cluster": key,
                "redundancy_cluster_title": cl["title"],
            }
            if cl.get("verdict"):
                record["redundancy_verdict"] = cl["verdict"]
                record["researcher_notes"] = f"[cluster {key} — {cl['verdict']}: {cl['title']}] {notes}"
            else:
                record["researcher_notes"] = f"[cluster {key}: {cl['title']}] {notes}"
            resolutions.append(record)

    ctypes = _tally(r["concern_type"] for r in resolutions)
    sev = _tally(r["severity"] for r in resolutions)
    scope = {
        "csv": csv.name,
        **({"oo_csv": oo_csv.name} if oo_csv else {}),
        "country": args.country,
        "rows": len({r["project_id"] for r in resolutions}),
        "clusters": len(clusters),
        **({"excluded_carried_rows": len(excl)} if args.exclude_pids else {}),
    }
    meta = {
        "commodity": args.commodity,
        "mode": "redundancy",
        "scope": scope,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_units": len(resolutions),
        "n_validity_flags": len(resolutions),
        "n_fills": 0,
        "n_status_reviews": 0,
        "n_route_suggestions": 0,
        "class_in_counts": {"VALIDITY": len(resolutions)},
        "class_out_counts": _tally(r["class_out"] for r in resolutions),
        "verdict_counts": _tally(r["verdict"] for r in resolutions),
        "concern_counts": ctypes,
        "severity_counts": sev,
        "cluster_titles": {k: v["title"] for k, v in clusters.items()},
    }
    if any(v.get("verdict") for v in clusters.values()):
        meta["cluster_verdicts"] = {k: v.get("verdict") or "UNRESOLVED" for k, v in clusters.items()}
        meta["verdict_tally"] = _tally(v.get("verdict") or "UNRESOLVED" for v in clusters.values())
    dropped = {k: v["refs_dropped"] for k, v in clusters.items() if v["refs_dropped"]}
    if dropped:
        meta["refs_dropped"] = dropped
    open_q = {k: v["open_questions"] for k, v in clusters.items() if v.get("open_questions")}
    if open_q:
        meta["open_questions"] = open_q
    meta["note"] = note

    out_path = Path(args.out) if args.out else staging / "staged_resolutions.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"meta": meta, "resolutions": resolutions}, indent=1, ensure_ascii=False))
    print(f"wrote {len(resolutions)} validity records across {len(clusters)} clusters -> {out_path}")
    for k, v in clusters.items():
        print(f"  {k}: {len(v['rows'])} row(s) — {v['title'][:96]}")
    print(f"  concern types: {ctypes}")
    print(f"  severity:      {sev}")
    if dropped:
        print(f"  refs dropped:  {sum(len(x) for x in dropped.values())} (see meta.refs_dropped)")


if __name__ == "__main__":
    main()
