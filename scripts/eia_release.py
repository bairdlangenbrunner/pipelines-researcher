#!/usr/bin/env python3
"""The newest EIA Natural Gas Pipeline Projects release, and refs that cite an older one.

RULE (Baird 2026-10-08): a sheet value is CHANGED on EIA's pipeline-projects workbook only when
the NEWEST release states a different value, and the change cites that release. When the newest
release states the sheet's value, or no longer lists the project, nothing changes and no ref is
owed. An older release may sit beside the newest one (history: the first release showing
`Completed` bounds the in-service year), never in place of it. P5905 Blackfin showed why: a start
year read from an older release (2026) would have overwritten the Aug-2026 value (2027).

A project that DROPS OFF the list is itself a finding: EIA keeps even cancelled projects listed,
so one missing from the newest release with no renamed successor there (`dropped()`) is an
existence question for its GEM row (a validity concern, possibly a deletion), never silence.

    python scripts/eia_release.py            # newest local release, and whether EIA has a newer one
    python scripts/eia_release.py --fetch    # download any newer release, record it, re-run prepare.py
    python scripts/eia_release.py --offline  # local only, no network
    python scripts/eia_release.py --dropped  # projects missing from the newest release with no successor there

Exit 1 when EIA lists a release that is not in sources/eia_pipeline_projects/raw/ (without --fetch).
Imported by check_shard_coverage.py (blocking), sweep_gates.py (gate P) and eia_crosswalk.py
(fetches before matching).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote

SRC = Path(__file__).resolve().parent.parent / "sources" / "eia_pipeline_projects"
RAW = SRC / "raw"
VINTAGES = RAW / "vintages.csv"
BASE_URL = "https://www.eia.gov/naturalgas/pipelines/"
INDEX_URL = "https://www.eia.gov/naturalgas/data.php"
UNDATED = "EIA-NaturalGasPipelineProjects.xlsx"
_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
# dated file names are irregular: _Aug2018, _July2019, _March2020, ProjectsAug2026 (no underscore)
_FILE = re.compile(r"EIA-NaturalGasPipelineProjects_?([A-Za-z]+)(\d{4})\.xlsx", re.I)
_MONTHS = {m: i for i, m in enumerate(
    ("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}
_MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July", "August",
                "September", "October", "November", "December")


def release_of_file(name: str) -> str | None:
    """'2026-08' for EIA-NaturalGasPipelineProjectsAug2026.xlsx; None for the undated or any other file."""
    m = _FILE.search(name or "")
    if not m:
        return None
    mon = _MONTHS.get(m.group(1)[:3].lower())
    return f"{m.group(2)}-{mon:02d}" if mon else None


def release_of_url(url: str) -> str | None:
    """The release a ref cites ('2026-08'), Wayback-wrapped or not; None if not a dated EIA projects file."""
    u = unquote(url or "")
    if "eia.gov" not in u.lower():
        return None
    return release_of_file(u.rsplit("/", 1)[-1].split("#")[0].split("?")[0])


def local_releases() -> list[dict]:
    """vintages.csv rows for the dated releases, oldest first."""
    if not VINTAGES.exists():
        return []
    with VINTAGES.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if re.fullmatch(r"\d{4}-\d{2}", r.get("release") or "")]
    return sorted(rows, key=lambda r: r["release"])


@lru_cache(maxsize=1)
def latest() -> dict:
    """{'file', 'release', 'url', 'label'} for the newest local release ({} when none is recorded)."""
    rows = local_releases()
    if not rows:
        return {}
    r = rows[-1]
    y, m = r["release"].split("-")
    return {"file": r["file"], "release": r["release"], "url": r["url"],
            "label": f"{_MONTH_NAMES[int(m) - 1]} {y}"}


def stale_refs(rec: dict, changes_value: bool = True) -> list[str]:
    """Older-release EIA refs on a record that CHANGES a sheet value without citing the newest
    release. A record that only adds a ref to the sheet's own value is never stale: an older
    release that states that value is a fine ref, and the newest one is not owed. [] when fine."""
    lt = latest()
    if not lt or not changes_value:
        return []
    refs = [u for u in (rec.get("proposed_refs") or []) if isinstance(u, str)]
    cited = {release_of_url(u) for u in refs} - {None}
    if not cited or lt["release"] in cited:
        return []
    return [u for u in refs if (release_of_url(u) or "9999") < lt["release"]]


def stale_reason(rec: dict, changes_value: bool = True) -> str | None:
    """The blocking message for check_shard_coverage.py, or None."""
    old = stale_refs(rec, changes_value)
    if not old:
        return None
    lt = latest()
    names = ", ".join(sorted({u.rsplit("/", 1)[-1] for u in old}))
    return (f"changes a sheet value on an older EIA release ({names}) without the newest, {lt['file']}. "
            f"Change a value from EIA only when the {lt['label']} release states a different value from the "
            f"sheet; then stage that value and cite {lt['url']}. If the {lt['label']} release states the "
            f"sheet's value or no longer lists the project, nothing changes (a project that dropped off the "
            f"list is an existence question: stage a validity concern). If another source supports the "
            f"change, cite that source and leave the older EIA release out")


_NAME_NOISE = re.compile(r"\b(?:project|pipeline|expansion|the|phase|formerly|see|and)\b|[^a-z0-9 ]")
_GENERIC = {"gas", "natural", "lateral", "loop", "storage", "header", "compressor", "station", "line",
            "system", "upgrade", "interconnect", "connector", "extension", "mainline", "energy", "hub",
            "i", "ii", "iii", "north", "south", "east", "west", "texas", "louisiana", "new", "co", "llc"}


def _clean(s: str) -> str:
    """Lowercased name without noise words; parenthesized text is KEPT ("(formerly Warrior Pipeline)")."""
    return " ".join(_NAME_NOISE.sub(" ", str(s or "").lower()).split())


def _dockets(s: str) -> set[str]:
    return {re.sub(r"\s|-000$", "", d.upper()) for d in re.findall(r"\b(?:CP|RP|PF)\s?\d{2}-\d+(?:-000)?", str(s or ""), re.I)}


def _states(s: str) -> set[str]:
    return {x.strip().upper() for x in re.split(r"[,;/ ]+", str(s or "")) if x.strip()}


def _same_project(a: str, b: str) -> bool:
    """Near-identical names, or one name's distinctive words all inside the other's."""
    from rapidfuzz import fuzz
    if not a or not b:
        return False
    if fuzz.ratio(a, b) >= 85:                      # Kosci Junction ~ Kosciusko Junction
        return True
    ta, tb = set(a.split()) - _GENERIC, set(b.split()) - _GENERIC
    small, big = sorted((ta, tb), key=len)
    return bool(small) and small <= big            # Warrior ~ Hugh Brinson (formerly Warrior)


def dropped(lat=None) -> dict:
    """{project_key: last_release} for EIA projects missing from the newest release with no
    successor there: no project in the newest release shares a FERC docket, or a near-identical
    name in an overlapping state. EIA re-keys rows constantly ("Warrior Pipeline" became "Hugh
    Brinson Pipeline (formerly Warrior Pipeline)", "Kosci Junction" became "Kosciusko Junction",
    a project splits into phases), so a plain key diff overstates drop-offs about tenfold.
    `lat` is data/eia_projects_latest.csv as records (read when None)."""
    if lat is None:
        with (SRC / "data" / "eia_projects_latest.csv").open(newline="", encoding="utf-8") as f:
            lat = list(csv.DictReader(f))
    newest = max(r["last_release"] for r in lat)
    cur = [(_clean(r["project_name"]), _states(r["state_s"])) for r in lat if r["last_release"] == newest]
    cur_dk = set().union(*(_dockets(r["docket_number"]) for r in lat if r["last_release"] == newest))
    out = {}
    for r in lat:
        if r["last_release"] == newest or _dockets(r["docket_number"]) & cur_dk:
            continue
        q, st = _clean(r["project_name"]), _states(r["state_s"])
        if any(_same_project(q, n) and (not st or not s or st & s) for n, s in cur):
            continue
        out[r["project_key"]] = r["last_release"]
    return out


# ---------------------------------------------------------------- remote
def _get(url: str, out: Path | None = None) -> tuple[int, str, bytes]:
    """(status, content_type, body) via curl with a browser UA (HEAD 503s and range requests 403 at EIA)."""
    cmd = ["curl", "-sL", "-A", _UA, "-H", "Accept-Language: en-US,en;q=0.9", "--max-time", "120",
           "-w", "\n%{http_code} %{content_type}"]
    if out is not None:
        cmd += ["-o", str(out)]
    p = subprocess.run(cmd + [url], capture_output=True)
    tail = p.stdout.rsplit(b"\n", 1)
    status, _, ctype = tail[-1].decode(errors="replace").partition(" ")
    body = tail[0] if out is None and len(tail) > 1 else b""
    return int(status or 0), ctype, body


def remote_files() -> list[str]:
    """Dated pipeline-projects file names linked from EIA's natural gas data page."""
    status, _, body = _get(INDEX_URL)
    if status != 200:
        raise RuntimeError(f"{INDEX_URL} returned {status}")
    names = set(re.findall(r"EIA-NaturalGasPipelineProjects_?[A-Za-z]+\d{4}\.xlsx", body.decode(errors="replace")))
    return sorted((n for n in names if release_of_file(n)), key=release_of_file)


def missing_releases() -> list[str]:
    """Files EIA lists that are newer than the newest local release."""
    lt = latest()
    have = {r["file"] for r in local_releases()}
    return [n for n in remote_files() if n not in have and release_of_file(n) > (lt.get("release") or "")]


def fetch(names: list[str]) -> list[str]:
    """Download each release into raw/, record it in vintages.csv (and the undated twin), re-run prepare.py."""
    got = []
    for n in names:
        dest = RAW / n
        status, ctype, _ = _get(BASE_URL + n, dest)
        if status != 200 or "html" in ctype.lower():        # EIA's 404 comes back as text/html
            dest.unlink(missing_ok=True)
            print(f"  could not download {n}: HTTP {status} {ctype}", file=sys.stderr)
            continue
        data = dest.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        with VINTAGES.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        rows = [r for r in rows if r["file"] not in (n, UNDATED)]
        rows.append({"file": n, "release": release_of_file(n), "url": BASE_URL + n,
                     "bytes": str(len(data)), "sha256": sha})
        rows.append({"file": UNDATED, "release": "current", "url": BASE_URL + UNDATED,
                     "bytes": str(len(data)), "sha256": sha})
        (RAW / UNDATED).write_bytes(data)
        with VINTAGES.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["file", "release", "url", "bytes", "sha256"])
            w.writeheader()
            w.writerows(rows)
        got.append(n)
        print(f"  downloaded {n} ({len(data):,} bytes)")
    if got:
        latest.cache_clear()
        subprocess.run([sys.executable, str(SRC / "prepare.py")], check=True)
    return got


def ensure_current(do_fetch: bool = True, quiet: bool = False) -> dict:
    """Check EIA for a newer release (and fetch it). A network failure warns, never blocks:
    the local newest release is still the rule's reference. -> latest()."""
    try:
        new = missing_releases()
    except Exception as e:      # noqa: BLE001 -- offline / EIA down
        print(f"warning: could not check EIA for a newer pipeline-projects release ({e}); "
              f"using the newest local one, {latest().get('file')}", file=sys.stderr)
        return latest()
    if new and do_fetch:
        fetch(new)
    elif new:
        print(f"EIA has a newer release not in raw/: {', '.join(new)} (run scripts/eia_release.py --fetch)",
              file=sys.stderr)
    elif not quiet:
        print(f"EIA pipeline projects: the newest release is local, {latest().get('file')}")
    return latest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fetch", action="store_true", help="download any newer release and re-run prepare.py")
    ap.add_argument("--offline", action="store_true", help="report the newest local release only")
    ap.add_argument("--dropped", action="store_true",
                    help="list projects missing from the newest release with no successor there")
    a = ap.parse_args()
    if a.dropped:
        with (SRC / "data" / "eia_projects_latest.csv").open(newline="", encoding="utf-8") as f:
            lat = {r["project_key"]: r for r in csv.DictReader(f)}
        d = dropped(list(lat.values()))
        for k, last in sorted(d.items(), key=lambda t: t[1], reverse=True):
            r = lat[k]
            print(f"{last}\t{r['status']}\t{r['project_name']} -- {r['pipeline_operator_name']} "
                  f"({r['state_s']}; docket {r['docket_number'] or '-'})")
        print(f"{len(d)} projects missing from {latest().get('label')} with no successor", file=sys.stderr)
        return 0
    if a.offline:
        print(latest().get("file") or "no local release recorded")
        return 0
    try:
        new = missing_releases()
    except Exception as e:      # noqa: BLE001
        print(f"could not reach EIA ({e}); newest local release: {latest().get('file')}", file=sys.stderr)
        return 1
    if new and a.fetch:
        fetch(new)
        new = missing_releases()
    lt = latest()
    print(f"newest local release: {lt.get('file')} ({lt.get('label')})")
    if new:
        print(f"EIA lists newer: {', '.join(new)} -- run with --fetch", file=sys.stderr)
        return 1
    print("EIA lists nothing newer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
