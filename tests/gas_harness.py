"""Shared by the phase 2 tests: publish a fixture scope into a local mirror and drive
review_app/gas/Code.gs against it under the node fakes (review_app/gas_dev/). No network, no Google."""
import gzip
import json
import os
import shutil
import subprocess
from pathlib import Path

import publish
import store

ROOT = Path(__file__).resolve().parent.parent
RUN_JS = ROOT / "review_app" / "gas_dev" / "run.js"
NOW = 4070930400000        # 2099-01-01T06:00:00Z (01:00 ET): a fixed clock, so timestamps are comparable
SID = "russia-gas"
VER = "20990101T000000"


def node():
    hit = shutil.which("node")
    if hit:
        return hit
    cands = sorted(Path(os.path.expanduser("~/.nvm/versions/node")).glob("*/bin/node"))
    return str(cands[-1]) if cands else None


def publish_fixture(s, out, ver=VER, cursor=1, sid=SID, target=publish.PART_BYTES):
    """Publish the in-memory dataset s["dataset"] (so a test may mutate it first). -> scopes.json entry."""
    publish.stamp_basis(s["dataset"], s["dirs"])
    entry = publish.write_scope(s["dataset"], out, sid, cursor, s["tmp"], ver=ver, target=target)
    publish.write_scopes(out, publish.merge_scopes(publish.read_scopes(Path(out) / "scopes.json"), entry))
    return entry


def read_parts(out, entry):
    data = None
    for name in entry["parts"]:
        part = json.loads(gzip.decompress((Path(out) / name).read_bytes()))
        if data is None:
            data = part
        else:
            data["pipelines"] += part["pipelines"]
    return data


def run(out, ops, sheets=None, now=NOW, backend=None):
    """-> (results, sheets, stats). `sheets` carries the fake store between runs."""
    job = {"dataDir": str(out), "now": now, "ops": ops}
    if sheets is not None:
        job["sheets"] = sheets
    if backend is not None:
        job["backend"] = backend
    p = subprocess.run([node(), str(RUN_JS)], input=json.dumps(job), capture_output=True, text=True, timeout=120)
    assert p.returncode == 0, p.stderr[-3000:]
    body = json.loads(p.stdout)
    return body["results"], body["sheets"], body["stats"]


def op(user, fn, *args):
    return {"user": user, "fn": fn, "args": list(args)}


def json_cells(sheets):
    """The log tab's `json` column as pull.read_store returns it (header first)."""
    rows = (sheets.get("log") or {}).get("rows") or []
    if not rows:
        return []
    c = rows[0].index("json")
    return [r[c] if len(r) > c else "" for r in rows]
