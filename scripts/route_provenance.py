"""
How a staged route candidate was made, for the review app (gem-review-app docs/plan.md, "Geo": `line.provenance`).

    summary(rec)                          -> {"text", "facts"} from the record alone; build_route_candidate stamps it as rec["provenance"]
    files(rec, staging_dir, root, cache)  -> {"images", "control_points"} read from the staging dir's map and trace files
    describe(rec, staging_dir, root, ...) -> the stamped (or freshly made) text and facts plus the files; None when all empty

Everything a person reads is plain English. Images are copied for the page by review_core.assets.prepare, which lives
in the sibling gem-review-app repo (on sys.path when review_data runs; GEM_REVIEW_APP overrides the location).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".tif", ".tiff"}
MAX_MAPS = 3
NOTES_CHARS = 300

METHOD_WORDS = {
    "endpoints_greatcircle": "Straight line between the two ends",
    "gis_vector": "Copied from a published vector dataset",
    "digitized": "Traced by hand from a map",
    "gulfpub_sidecar": "Taken from the Petroleum Economist map data",
    "corridor_follow_osm": "Follows an OpenStreetMap way",
    "osm": "Copied from OpenStreetMap",
}


def _s(v):
    return str(v).strip() if v is not None else ""


def _is_url(v):
    return bool(re.match(r"^https?://\S+$", _s(v)))


def _num(v, nd=1):
    try:
        v = float(v)
        return f"{v:.{nd + 1 if 0 < v < 0.1 else nd}f}"   # 0.098 shows as 0.10, not 0.1
    except (TypeError, ValueError):
        return ""


def _georef_phrase(g):
    if not isinstance(g, dict):
        return ""
    n, rmse, loo = g.get("n_gcps"), _num(g.get("rmse_km")), _num(g.get("loo_rmse_km"))
    bits = []
    if n:
        bits.append(f"{n} control points")
    if rmse:
        bits.append(f"fit error {rmse} km")
    if loo:
        bits.append(f"held-out error {loo} km")
    return ", ".join(bits)


def _grade(name):
    m = re.search(r"\b(low|medium|high)[ -]resolution\b", name or "", re.I)
    return f"{m.group(1).lower()} resolution" if m else ""


def summary(rec):
    """{"text", "facts"} from the record alone."""
    method = _s(rec.get("method"))
    src = rec.get("source") or {}
    sname = _s(src.get("name"))
    g = rec.get("georef")
    notes = _s(rec.get("researcher_notes"))
    start, end = _s(rec.get("start_name")), _s(rec.get("end_name"))
    paras = []
    if method == "gis_vector":
        t = "The route was copied from a published vector dataset"
        if sname:
            t += f", {sname}"
            grade = _grade(sname)
            if grade and grade not in sname.lower():
                t += f", at {grade}"
        paras.append(t + ".")
    elif method == "digitized":
        t = "The route was traced by hand from a map in a document"
        if g:
            ph = _georef_phrase(g)
            if ph:
                t += f". The map was fitted to the ground with {ph}"
        paras.append(t + ".")
        paras.append("The route is only as accurate as the map it was traced from.")
    elif method == "gulfpub_sidecar":
        paras.append("The route was taken from the Petroleum Economist world pipeline map data.")
    elif method == "endpoints_greatcircle":
        if start and end:
            paras.append(f"No route was found. This line is a straight placeholder drawn between {start} and {end}.")
        else:
            paras.append("No route was found. This line is a straight placeholder drawn between the two ends.")
    elif method == "corridor_follow_osm":
        t = "The route follows an OpenStreetMap way"
        paras.append(t + (f", {sname}." if sname and sname.lower() != "openstreetmap" else "."))
    elif method == "osm":
        paras.append("The route was copied from OpenStreetMap.")
    else:
        paras.append("How this route was made was not recorded.")
        if notes:
            cut = notes[:NOTES_CHARS].rstrip()
            paras.append(f"The researcher notes say: {cut}{'...' if len(notes) > NOTES_CHARS else ''}")
    facts = []
    if method in METHOD_WORDS:
        facts.append(["Method", METHOD_WORDS[method]])
    if sname:
        facts.append(["Source", sname, src["url"]] if _is_url(src.get("url")) else ["Source", sname])
    rr = _s((rec.get("proposed_sheet") or {}).get("Route [ref]"))
    if rr:
        facts.append(["Route reference", rr, rr] if _is_url(rr) else ["Route reference", rr])
    ph = _georef_phrase(g)
    if ph:
        facts.append(["Georeferencing", ph])
    if _s(src.get("license")):
        facts.append(["License", _s(src["license"])])
    fetched = _s(src.get("fetched_utc"))[:10]
    if fetched:
        facts.append(["Fetched", fetched])
    if rec.get("qc_passed") is not None:
        facts.append(["Quality check", "passed" if rec["qc_passed"] else "failed"])
    if _s(rec.get("suggested_route_accuracy")):
        facts.append(["Suggested accuracy", _s(rec["suggested_route_accuracy"])])
    return {"text": " ".join(paras), "facts": facts}


# ---------------------------------------------------------------- files
def _json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _is_image(p):
    return Path(p).suffix.lower() in IMAGE_SUFFIXES


def _single(staging_dir):
    """True when the staging dir holds exactly one route candidate record (the flat single-PID layouts)."""
    d = _json(Path(staging_dir) / "staged_resolutions.json")
    recs = (d or {}).get("resolutions") if isinstance(d, dict) else None
    return sum(1 for r in recs or [] if r.get("class_out") == "ROUTE_CANDIDATE") == 1


def _caption(f):
    title = re.sub(r"\s+", " ", _s(f.get("document_title")))
    if len(title) > 160:
        title = title[:157].rstrip() + "..."
    bits = [f"Map from {title}" if title else "Map"]
    page = _s(f.get("page"))
    if page:
        bits.append(f"page {page}")
    if _s(f.get("date_read")):
        bits.append(f"read {_s(f['date_read'])}")
    return ", ".join(bits)


def _resolve(staging_dir, root, rel):
    """A route_provenance local_copy path, relative to the staging dir or to the repo."""
    for base in (Path(staging_dir), Path(root)):
        p = base / rel
        if p.is_file():
            return p
    return None


def _map_candidates(rec, staging_dir, pid, rp):
    """[(path, caption, source_url)] in order, before any image is prepared."""
    sd = Path(staging_dir)
    out = []
    sj = _json(sd / "maps" / pid / "source.json") if pid else None
    for f in (sj or {}).get("files") or []:
        rel = _s(f.get("file"))
        if rel and _is_image(rel):
            out.append((sd / "maps" / pid / rel, _caption(f), _s(f.get("source_url"))))
    if out:
        return out
    root_src = (rp or {}).get("root_source") or {}
    if _s(root_src.get("local_copy")):
        out.append((("rp", root_src["local_copy"]), "Map the route was traced from"
                    + (f", {_s(root_src.get('name'))}" if _s(root_src.get("name")) else ""),
                    _s(root_src.get("page_url") or root_src.get("image_url"))))
    gi = _s((rec.get("georef") or {}).get("image")).split(" ", 1)[0]
    if gi and _is_image(gi):
        for sub in ("traces", "maps"):
            if pid and (sd / sub / pid / gi).is_file():
                out.append((sd / sub / pid / gi, "Map the route was traced from", ""))
                break
    if not out and _single(sd):
        for d in (sd / "maps", sd):
            if d.is_dir():
                for p in sorted(d.iterdir()):
                    if p.is_file() and _is_image(p):
                        out.append((p, "Map the route was traced from", ""))
                if out:
                    break
    return out


def _points(rec, staging_dir, pid, rp):
    sd = Path(staging_dir)
    gcps = rep = None
    for base in (sd / "traces" / pid, sd / "packets" / pid) if pid else ():
        gcps = gcps or _json(base / "gcps.json")
        rep = rep or _json(base / "georef_report.json")
    if gcps is None and _single(sd):
        gcps = _json(sd / "traces" / "gcps.json")
        rep = rep or _json(sd / "traces" / "georef_report.json")
    if gcps is None and isinstance(((rp or {}).get("georef") or {}).get("gcps"), list):
        gcps = rp["georef"]["gcps"]
    if not isinstance(gcps, list):
        return []
    res = ((rep or {}).get("residuals_km") or (rec.get("georef") or {}).get("residuals_km") or [])
    out = []
    for i, p in enumerate(gcps):
        if not isinstance(p, dict):
            continue
        pt = {}
        if _s(p.get("name")):
            pt["name"] = _s(p["name"])
        px = p.get("px")
        if isinstance(px, (list, tuple)) and len(px) == 2:
            pt["px"] = list(px)
        ll = p.get("lonlat")
        if isinstance(ll, (list, tuple)) and len(ll) == 2:
            pt["lon"], pt["lat"] = ll[0], ll[1]
        if _s(p.get("source_ref")):
            pt["ref"] = _s(p["source_ref"])
        if i < len(res) and isinstance(res[i], (int, float)):
            pt["residual_km"] = round(res[i], 2)
        if pt:
            out.append(pt)
    return out


def _asset_prepare():
    try:
        from review_core import assets
    except ImportError:
        env = os.environ.get("GEM_REVIEW_APP")
        here = Path(__file__).resolve().parent.parent.parent / "gem-review-app"
        for p in filter(None, (env, str(here))):
            if p not in sys.path and Path(p).is_dir():
                sys.path.insert(0, p)
        from review_core import assets
    return assets.prepare


def files(rec, staging_dir, root, cache=None):
    """{"images": [...], "control_points": [...]} from the staging dir's map and trace files."""
    pid = _s(rec.get("project_id"))
    sd, root = Path(staging_dir), Path(root)
    rp_all = _json(sd / "route_provenance.json")
    rp = rp_all.get(pid) if isinstance(rp_all, dict) and isinstance(rp_all.get(pid), dict) else None
    cands = []
    for p, cap, url in _map_candidates(rec, sd, pid, rp):
        if isinstance(p, tuple):
            p = _resolve(sd, root, p[1])
        if p is not None:
            cands.append(("map", Path(p), cap, url))
    cands = cands[:MAX_MAPS]
    ov = sd / "traces" / pid / "overlay_trace.png" if pid else None
    if ov and ov.is_file():
        cands.append(("overlay", ov, "The traced route drawn over the map", ""))
    images = []
    if cands:
        prepare = _asset_prepare()
        for role, p, cap, url in cands:
            got = prepare(p, root, cache)
            if not got:
                continue
            try:
                rel = p.resolve().relative_to(root.resolve()).as_posix()
            except ValueError:
                rel = str(p)
            img = {"role": role, "caption": cap, "asset": got["asset"], "path": rel,
                   "width": got["width"], "height": got["height"]}
            if url:
                img["source_url"] = url
            images.append(img)
    return {"images": images, "control_points": _points(rec, sd, pid, rp)}


def describe(rec, staging_dir, root, cache=None):
    """The record's provenance (stamped text and facts win) plus its files; None when nothing is known."""
    stamped = rec.get("provenance") if isinstance(rec.get("provenance"), dict) else None
    base = stamped if stamped and (stamped.get("text") or stamped.get("facts")) else summary(rec)
    out = {"text": base.get("text") or "", "facts": base.get("facts") or []}
    out.update(files(rec, staging_dir, root, cache))
    out = {k: v for k, v in out.items() if v}
    return out or None
