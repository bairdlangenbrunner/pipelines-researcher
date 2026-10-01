"""
Which researched countries the review app shows: the review-app batch.

    python review_app/scopes.py list   [--commodity gas]       # every researched scope + its state
    python review_app/scopes.py pending [--commodity gas]      # researched, never answered or "later"
    python review_app/scopes.py check --country Egypt --commodity gas   # exit 3 = ask Baird
    python review_app/scopes.py set   --country Egypt --commodity gas yes|no|later

The batch is batches/review-app/manifest.json (committed, so everyone who pulls the repo and
runs the app sees the same countries). It holds a decision per country+commodity, nothing
else -- no copied staged data. The staging dirs stay the one pending-state store and the
decision keys keep naming them, so a country added here brings its existing decisions with it.

  yes    included: the app (review_data.py / server.py run without --country) builds over
         every staging dir of the scope, so later batches for it come in on the next rebuild
  later  not now; the researcher asks again at the next delivery for the scope
  no     declined; never asked again (`set ... yes` reverses it)

A scope that is researched (it has a staging dir with store metadata) but has no entry is
"new". At delivery the researcher runs `check`; exit 3 (new / later) means ask Baird
"add <Country> <commodity> to the review app? Y / n / later" and record the answer with `set`.

An included country whose every line and asked item has a person's decision is hidden from the
built dataset automatically (review_data.py --include-done shows it); it is not removed here,
so a new batch for it brings it back without asking.
"""
import argparse
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import normalize as N  # noqa: E402
import staged_store  # noqa: E402

MANIFEST = staged_store.BATCHES_ROOT / "review-app" / "manifest.json"
ANSWERS = {"yes": "included", "y": "included", "no": "declined", "n": "declined", "later": "later"}
ASK = 3   # `check` exit code: ask Baird


def _key(country, commodity):
    return N.normalize_country(country), commodity.lower()


def load(path=None):
    p = Path(path or MANIFEST)
    if not p.exists():
        return {"scopes": []}
    return json.loads(p.read_text(encoding="utf-8"))


def save(m, path=None):
    p = Path(path or MANIFEST)
    p.parent.mkdir(parents=True, exist_ok=True)
    m["scopes"].sort(key=lambda s: (s["commodity"], s["country"]))
    fd, tmp = tempfile.mkstemp(dir=p.parent, prefix=".manifest.")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps(m, indent=1, ensure_ascii=False) + "\n")
    os.replace(tmp, p)


def researched(root=None, commodity=None):
    """{(normalized country, commodity): {"country": display name, "dirs": [Path]}} for every
    staging dir whose store metadata names a scope. Assembled packets count (they are staged
    work too); dirs without scope metadata are left to discovery's scope-dir-name fallback."""
    root = Path(root or staged_store.BATCHES_ROOT)
    out = {}
    for d in sorted(root.glob("*/staging/*")):
        if not d.is_dir():
            continue
        sc = staged_store._dir_scope(d)
        if sc is None or (commodity and sc[1] != commodity.lower()):
            continue
        ent = out.setdefault(sc, {"country": _display(d) or sc[0].title(), "dirs": []})
        ent["dirs"].append(d)
    return out


def _display(d):
    for fn in staged_store._STORE_FILES:
        f = d / fn
        if f.exists():
            try:
                meta = json.loads(f.read_text()).get("meta", {})
            except (json.JSONDecodeError, OSError):
                continue
            c = (meta.get("scope") or {}).get("country") or meta.get("country")
            if c:
                return c
    return ""


def state(m, country, commodity):
    k = _key(country, commodity)
    for s in m["scopes"]:
        if _key(s["country"], s["commodity"]) == k:
            return s["state"]
    return "new"


def included(commodity, path=None):
    """Display names of the included countries for one commodity, manifest order."""
    return [s["country"] for s in load(path)["scopes"]
            if s["commodity"] == commodity.lower() and s["state"] == "included"]


def set_state(country, commodity, answer, path=None, root=None, by=""):
    st = ANSWERS[answer.lower()]
    rs = researched(root, commodity).get(_key(country, commodity))
    if st == "included" and rs is None:
        raise SystemExit(f"{country} {commodity}: no staging dir carries this scope; nothing to show")
    m = load(path)
    k = _key(country, commodity)
    m["scopes"] = [s for s in m["scopes"] if _key(s["country"], s["commodity"]) != k]
    m["scopes"].append({"country": rs["country"] if rs else country, "commodity": commodity.lower(),
                        "state": st, "decided": datetime.now(ZoneInfo("America/New_York")).date().isoformat(),
                        **({"by": by} if by else {})})
    save(m, path)
    return st


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["list", "pending", "check", "set"])
    ap.add_argument("answer", nargs="?", choices=sorted(ANSWERS), help="set only")
    ap.add_argument("--country")
    ap.add_argument("--commodity", choices=["gas", "oil"])
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--batches-root", default=None)
    a = ap.parse_intermixed_args(argv)
    if a.cmd in ("check", "set") and not (a.country and a.commodity):
        ap.error(f"{a.cmd} needs --country and --commodity")
    m = load(a.manifest)
    if a.cmd == "check":
        st = state(m, a.country, a.commodity)
        print(st)
        return ASK if st in ("new", "later") else 0
    if a.cmd == "set":
        if not a.answer:
            ap.error("set needs yes / no / later")
        print(set_state(a.country, a.commodity, a.answer, a.manifest, a.batches_root))
        return 0
    rs = researched(a.batches_root, a.commodity)
    keys = sorted(set(rs) | {_key(s["country"], s["commodity"]) for s in m["scopes"]
                             if not a.commodity or s["commodity"] == a.commodity},
                  key=lambda k: (k[1], k[0]))
    for k in keys:
        name = rs[k]["country"] if k in rs else next(s["country"] for s in m["scopes"]
                                                     if _key(s["country"], s["commodity"]) == k)
        st = state(m, name, k[1])
        if a.cmd == "pending" and st not in ("new", "later"):
            continue
        nd = len(rs[k]["dirs"]) if k in rs else 0
        print(f"{st:9} {k[1]:4} {name}  ({nd} staging dirs{'' if nd else ' -- none left'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
