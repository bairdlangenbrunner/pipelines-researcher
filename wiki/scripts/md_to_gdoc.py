"""Push a markdown template into a Google Doc through the gws CLI.

Converts `wiki/template/*.md` into Docs API batchUpdate requests: Calibri 10 body, bold headings a little larger, plain bullets, numbered lists, monospace for code blocks, and a yellow highlight on every «ColumnName» token because the data team's prep doc asks for tracker column names to be highlighted. Markdown tables are flattened to one line per row (no Docs tables).

The doc is REPLACED: everything after the first character is deleted first. Writes need the `gws-gem-write` profile and Baird's OK for that doc.

    python wiki/scripts/md_to_gdoc.py wiki/template/pipeline_page_template.md <docId> [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

FONT = "Calibri"
MONO = "Courier New"
HIGHLIGHT = {"color": {"rgbColor": {"red": 1.0, "green": 0.95, "blue": 0.6}}}


def parse(md: str):
    """Yield (text, kind, inline_runs) per paragraph. kind: h1/h2/h3/p/bullet/number/code/quote."""
    out = []
    in_code = False
    for raw in md.splitlines():
        line = raw.rstrip("\n")
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            out.append((line, "code"))
            continue
        if not line.strip():
            continue
        if line.strip() == "---":
            continue
        m = re.match(r"^(#{1,3})\s+(.*)", line)
        if m:
            out.append((m.group(2), f"h{len(m.group(1))}"))
            continue
        if re.match(r"^\|\s*-{2,}", line):
            continue
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            out.append((" | ".join(cells), "table"))
            continue
        m = re.match(r"^\s*[-*]\s+(.*)", line)
        if m:
            out.append((m.group(1), "bullet"))
            continue
        m = re.match(r"^\s*\d+\.\s+(.*)", line)
        if m:
            out.append((m.group(1), "number"))
            continue
        m = re.match(r"^>\s?(.*)", line)
        if m:
            out.append((m.group(1), "quote"))
            continue
        out.append((line, "p"))
    return out


def inline(text: str):
    """Strip markdown inline marks; return plain text plus (start, end, style) runs."""
    runs = []
    plain = ""
    i = 0
    pattern = re.compile(r"\*\*(.+?)\*\*|`([^`]+)`|\[([^\]]+)\]\([^)]+\)")
    for m in pattern.finditer(text):
        plain += text[i:m.start()]
        if m.group(1) is not None:
            s = len(plain); plain += m.group(1); runs.append((s, len(plain), "bold"))
        elif m.group(2) is not None:
            s = len(plain); plain += m.group(2); runs.append((s, len(plain), "mono"))
        else:
            plain += m.group(3)
        i = m.end()
    plain += text[i:]
    for m in re.finditer(r"«[^»]+»", plain):
        runs.append((m.start(), m.end(), "highlight"))
    return plain, runs


def build_requests(paras, doc_len: int):
    reqs = []
    if doc_len > 2:
        reqs.append({"deleteContentRange": {"range": {"startIndex": 1, "endIndex": doc_len - 1}}})
    text = ""
    spans = []  # (start, end, kind, runs)
    for raw, kind in paras:
        plain, runs = (raw, []) if kind == "code" else inline(raw)
        s = len(text) + 1
        text += plain + "\n"
        spans.append((s, s + len(plain), kind, runs))
    reqs.append({"insertText": {"location": {"index": 1}, "text": text}})
    end = len(text) + 1
    # Named style first: applying it resets inline text styles, so the font must come after it
    reqs.append({"updateParagraphStyle": {"range": {"startIndex": 1, "endIndex": end}, "paragraphStyle": {"namedStyleType": "NORMAL_TEXT", "spaceAbove": {"magnitude": 0, "unit": "PT"}, "spaceBelow": {"magnitude": 4, "unit": "PT"}}, "fields": "namedStyleType,spaceAbove,spaceBelow"}})
    reqs.append({"updateTextStyle": {"range": {"startIndex": 1, "endIndex": end}, "textStyle": {"weightedFontFamily": {"fontFamily": FONT}, "fontSize": {"magnitude": 10, "unit": "PT"}, "bold": False, "italic": False}, "fields": "weightedFontFamily,fontSize,bold,italic"}})
    size = {"h1": 14, "h2": 12, "h3": 11}
    for s, e, kind, runs in spans:
        rng = {"startIndex": s, "endIndex": e + 1}
        if e == s:
            continue
        if kind in size:
            reqs.append({"updateTextStyle": {"range": {"startIndex": s, "endIndex": e}, "textStyle": {"bold": True, "fontSize": {"magnitude": size[kind], "unit": "PT"}}, "fields": "bold,fontSize"}})
            reqs.append({"updateParagraphStyle": {"range": rng, "paragraphStyle": {"spaceAbove": {"magnitude": 10, "unit": "PT"}}, "fields": "spaceAbove"}})
        elif kind == "code" or kind == "table":
            reqs.append({"updateTextStyle": {"range": {"startIndex": s, "endIndex": e}, "textStyle": {"weightedFontFamily": {"fontFamily": MONO}, "fontSize": {"magnitude": 9, "unit": "PT"}}, "fields": "weightedFontFamily,fontSize"}})
            reqs.append({"updateParagraphStyle": {"range": rng, "paragraphStyle": {"spaceBelow": {"magnitude": 0, "unit": "PT"}, "indentStart": {"magnitude": 18, "unit": "PT"}}, "fields": "spaceBelow,indentStart"}})
        elif kind == "quote":
            reqs.append({"updateParagraphStyle": {"range": rng, "paragraphStyle": {"indentStart": {"magnitude": 18, "unit": "PT"}}, "fields": "indentStart"}})
        for rs, re_, st in runs:
            r = {"startIndex": s + rs, "endIndex": s + re_}
            if st == "bold":
                reqs.append({"updateTextStyle": {"range": r, "textStyle": {"bold": True}, "fields": "bold"}})
            elif st == "mono":
                reqs.append({"updateTextStyle": {"range": r, "textStyle": {"weightedFontFamily": {"fontFamily": MONO}}, "fields": "weightedFontFamily"}})
            elif st == "highlight":
                reqs.append({"updateTextStyle": {"range": r, "textStyle": {"backgroundColor": HIGHLIGHT, "bold": True}, "fields": "backgroundColor,bold"}})
    # Bullets last, in reverse document order, so the leading-character consumption does not shift earlier ranges
    for s, e, kind, _ in reversed(spans):
        if kind in ("bullet", "number"):
            preset = "BULLET_DISC_CIRCLE_SQUARE" if kind == "bullet" else "NUMBERED_DECIMAL_ALPHA_ROMAN"
            reqs.append({"createParagraphBullets": {"range": {"startIndex": s, "endIndex": e + 1}, "bulletPreset": preset}})
    return reqs


def gws(args, body=None, write=False):
    env = dict(os.environ, GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser("~/.config/gws-gem-write" if write else "~/.config/gws-gem"), GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file")
    cmd = ["gws", *args]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    p = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if p.returncode:
        sys.exit(p.stderr or p.stdout)
    return json.loads(p.stdout) if p.stdout.strip().startswith("{") else p.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown")
    ap.add_argument("doc_id")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    paras = parse(open(a.markdown, encoding="utf-8").read())
    doc = gws(["docs", "documents", "get", "--params", json.dumps({"documentId": a.doc_id})])
    doc_len = doc["body"]["content"][-1]["endIndex"]
    reqs = build_requests(paras, doc_len)
    print(f"{len(paras)} paragraphs, {len(reqs)} requests, doc currently {doc_len} chars")
    if a.dry_run:
        return
    out = gws(["docs", "documents", "batchUpdate", "--params", json.dumps({"documentId": a.doc_id})], {"requests": reqs}, write=True)
    print("done", len(out.get("replies", [])), "replies")


if __name__ == "__main__":
    main()
