"""
Send review_app/gas/ to the Apps Script project (phase 2), without clasp and without a paste.

    python review_app/gas_push.py          # plan: what the project holds vs the repo; writes nothing
    python review_app/gas_push.py --yes    # replace the project's files (ask Baird first, every run)

A standalone Apps Script project is a Drive file, and Drive exports / imports its source as one
JSON document (media type application/vnd.google-apps.script+json). This rebuilds the bundle
(review_app/bundle.py: index.html + Config.gs), reads the project named in review_app/google.json
(`script_id`) with the read-only profile, lists the files that differ, and with --yes uploads the
repo's version with the write profile. Files are matched by name; a project file the repo does not
have is removed.

This changes the project's SOURCE only. The web app people use keeps serving the version it was
deployed with until Baird opens the project and deploys a new version (Deploy > Manage deployments
> edit > Version: New version). Nothing here can deploy, and nothing here runs the script.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT / "scripts", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import bundle  # noqa: E402
import paths  # noqa: E402
import pull as pull_mod  # noqa: E402


def current(script_id, work, gws=pull_mod.gws):
    """The project's files as Drive exports them: {"files": [{id, name, type, source}]}."""
    dest = Path(work) / "gas_project.current.json"
    gws(pull_mod.READ_PROFILE, "drive", "files", "export", "--params",
        json.dumps({"fileId": script_id, "mimeType": bundle.PROJECT_MIME}), "-o", str(dest), parse=False)
    return json.loads(dest.read_text(encoding="utf-8"))


def _same(kind, a, b):
    if kind == "json":      # Drive re-serialises the manifest (and adds an empty "dependencies")
        strip = lambda t: {k: v for k, v in json.loads(t).items() if v not in ({}, [], None)}  # noqa: E731
        return strip(a) == strip(b)
    return a == b


def plan(cur, new):
    """-> (body to upload, [(name, "same" | "changed" | "new" | "removed")]). The body carries the
    project's own file ids, so Drive replaces those files instead of adding twins."""
    have = {f["name"]: f for f in cur.get("files", [])}
    body, states = [], []
    for f in new["files"]:
        old = have.pop(f["name"], None)
        states.append((f["name"], "new" if old is None else "same" if _same(f["type"], old["source"], f["source"]) else "changed"))
        body.append(dict(f, **({"id": old["id"]} if old and old.get("id") else {})))
    states += [(n, "removed") for n in have]
    return {"files": body}, states


def push(cfg, work, yes=False, gws=pull_mod.gws, say=print):
    sid = (cfg or {}).get("script_id") or ""
    if not sid:
        raise SystemExit("review_app/google.json has no script_id: no project to push to")
    html = bundle.bundle()
    config = bundle.config_gs(cfg)
    if not config:
        raise SystemExit("review_app/google.json needs data_folder_id and store_sheet_id before the script can run")
    body, states = plan(current(sid, work, gws), bundle.project(html, config))
    say(f"Apps Script project {sid}:")
    for name, st in states:
        say(f"  {st.upper():8} {name}")
    if all(st == "same" for _, st in states):
        say("the project already holds the repo's files: nothing to push")
        return states
    if not yes:
        say("nothing pushed (plan only). Re-run with --yes once Baird has OK'd this run.")
        return states
    src = Path(work) / "gas_project.push.json"
    src.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
    gws(pull_mod.WRITE_PROFILE, "drive", "files", "update", "--upload", str(src), "--upload-content-type",
        bundle.PROJECT_MIME, "--params", json.dumps({"fileId": sid, "fields": "id,name,modifiedTime"}))
    left = [(n, st) for n, st in plan(current(sid, work, gws), bundle.project(html, config))[1] if st != "same"]
    if left:
        raise SystemExit(f"pushed, but the project does not read back as the repo's files: {left}")
    say("pushed and read back. The web app still serves its deployed version: open the project and "
        "deploy a new version (Deploy > Manage deployments > edit > Version: New version).")
    return states


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--yes", action="store_true", help="actually replace the project's files")
    ap.add_argument("--config", default=None, help="default review_app/google.json")
    a = ap.parse_args(argv)
    work = paths.work_dir() / "review_publish"
    work.mkdir(parents=True, exist_ok=True)
    try:
        return push(pull_mod.config(a.config), work, yes=a.yes)
    except pull_mod.GwsError as e:
        sys.exit(f"gas push failed: {e}")


if __name__ == "__main__":
    main()
