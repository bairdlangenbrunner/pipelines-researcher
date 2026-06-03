"""Central path resolution — so nothing hard-codes /Users/baird/... .

Repo layout is fixed relative to this file (scripts/paths.py). Sibling repos
(the GEM route mirror, the scrape repo) default to siblings of this repo and can be
overridden by env vars (see .env.example).
"""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# commodity -> routes-repo subdir
ROUTE_SUBDIRS = {
    "oil": "liquid-pipelines",
    "ngl": "liquid-pipelines",
    "gas": "gas-pipelines",
    "hydrogen": "hydrogen-pipelines",
}
_ALL_ROUTE_SUBDIRS = ("liquid-pipelines", "gas-pipelines", "hydrogen-pipelines")


def repo_root() -> Path:
    return REPO_ROOT


def _sibling(name: str, env: str) -> Path:
    override = os.environ.get(env)
    if override:
        return Path(override).expanduser().resolve()
    return (REPO_ROOT.parent / name).resolve()


def routes_repo() -> Path:
    """Local mirror of GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes."""
    return _sibling("GOIT-GGIT-pipeline-routes", "GEM_ROUTES_REPO")


def scraping_repo() -> Path:
    """Local GOIT-GGIT-scraping repo (GulfPub PE World Map, etc.)."""
    return _sibling("GOIT-GGIT-scraping", "GEM_SCRAPING_REPO")


def sources_dir() -> Path:
    return REPO_ROOT / "sources"


def source_dir(name: str) -> Path:
    return sources_dir() / name


def routes_cache() -> Path:
    d = REPO_ROOT / "routes_cache"
    d.mkdir(exist_ok=True)
    return d


def gem_route_path(project_id: str, commodity: str | None = None) -> Path | None:
    """Resolve a GEM route GeoJSON in the local mirror. Tries the commodity's
    subdir first, then the others. Returns None if not present locally (caller can
    fall back to scripts/fetch_route.sh)."""
    base = routes_repo() / "data" / "individual-routes"
    order: list[str] = []
    if commodity and commodity in ROUTE_SUBDIRS:
        order.append(ROUTE_SUBDIRS[commodity])
    order += [s for s in _ALL_ROUTE_SUBDIRS if s not in order]
    for sub in order:
        p = base / sub / f"{project_id}.geojson"
        if p.exists():
            return p
    return None
