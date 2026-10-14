"""Read-only audit: sheet LengthKnown stored in km although the length refs cite miles.

For every US-gas row with LengthKnownUnits = km and a Length [ref], fetch each ref and look for
(a) a mile figure whose km conversion matches the sheet value, (b) a km figure equal to the sheet value.
Writes a CSV for a person to review. Never writes the sheet and never stages anything.

    python scripts/audit_km_to_mi.py --snapshot data/GGIT_gas_snapshot_YYYYMMDD.csv --out work/km-to-mi-us-gas/audit.csv
"""
import argparse, csv, re, sys, json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from fetch import fetch_page
from url_verifier import BLOCKLIST_HOSTS

KM = 1.609344
NUM = r"(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
MI_RE = re.compile(NUM + r"\s*[-‐-– ]?\s*(?:statute\s+)?(?:miles?|mi)\b", re.I)
KM_RE = re.compile(NUM + r"\s*[-‐-– ]?\s*(?:kilomet(?:er|re)s?|km)\b", re.I)


def nums(rx, text):
    return [float(m.group(1).replace(",", "")) for m in rx.finditer(text)]


def check(text, v):
    mi = nums(MI_RE, text)
    km = nums(KM_RE, text)
    mi_hit = sorted({m for m in mi if abs(m * KM - v) <= max(0.006 * v, 0.6 * KM)})
    km_hit = sorted({k for k in km if abs(k - v) <= max(0.003 * v, 0.5)})
    return mi_hit, km_hit


def scan(url, v, names, cache):
    low = url.lower()
    if any(b in low for b in BLOCKLIST_HOSTS) or "gem.wiki" in low or "globalenergymonitor" in low:
        return dict(url=url, status="skipped", mi_hit="", km_hit="", name_found="")
    try:
        p = fetch_page(url, timeout=40)
    except Exception as e:  # noqa
        return dict(url=url, status=f"error {e}", mi_hit="", km_hit="", name_found="")
    text = re.sub(r"\s+", " ", p.text or "")
    mi_hit, km_hit = check(text, v)
    tl = text.lower()
    nf = any(n and n.lower() in tl for n in names)
    return dict(url=url, status=p.status, mi_hit=";".join(map(str, mi_hit)), km_hit=";".join(map(str, km_hit)),
                name_found=nf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    d = pd.read_csv(a.snapshot, header=2, low_memory=False, keep_default_na=False, na_values=[])
    d = d[d["CountriesOrAreas"].str.contains("United States") & (d.Status != "N/A") & (d.LengthKnownUnits == "km")]
    jobs = []
    for _, r in d.iterrows():
        try:
            v = float(str(r.LengthKnown).replace(",", ""))
        except ValueError:
            continue
        urls = re.findall(r"https?://[^\s,]+", r["Length [ref]"])
        names = [r.PipelineName, r.SegmentName]
        for u in urls:
            jobs.append((r.ProjectID, r.PipelineName, r.SegmentName, v, u, names))
    print(len(d), "km rows,", len(jobs), "ref fetches", file=sys.stderr)
    with ThreadPoolExecutor(a.workers) as ex:
        res = list(ex.map(lambda j: scan(j[4], j[3], j[5], None), jobs))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ProjectID", "PipelineName", "SegmentName", "sheet_km", "url", "status", "mi_figures_matching", "km_figures_matching", "name_found"])
        for j, r in zip(jobs, res):
            w.writerow([j[0], j[1], j[2], j[3], r["url"], r["status"], r["mi_hit"], r["km_hit"], r["name_found"]])


if __name__ == "__main__":
    main()
