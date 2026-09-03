#!/usr/bin/env python3
"""Decode the map's obfuscated text layer.

Each embedded subset font remaps character codes through an /Encoding
/Differences array of glyph names of the form /MT<n>, where n is the real
Unicode codepoint (/MT72 -> 'H'). Building code->char per font recovers the
text exactly -- no OCR involved. Cross-checked against the /Widths array:
for the Arial fonts the decoded characters must reproduce the known Arial
advance widths.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import fitz

PDF = Path("/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher/"
           "sources/middle-east/energy-map-of-the-middle-east-2026-peregrine-bush.pdf")

# Arial / Arial Bold advance widths (units/1000) for the width self-check.
ARIAL = {' ': 278, '!': 278, '"': 355, '#': 556, '$': 556, '%': 889, '&': 667,
         "'": 191, '(': 333, ')': 333, '*': 389, '+': 584, ',': 278, '-': 333,
         '.': 278, '/': 278, '0': 556, '1': 556, '2': 556, '3': 556, '4': 556,
         '5': 556, '6': 556, '7': 556, '8': 556, '9': 556, ':': 278, ';': 278,
         'A': 667, 'B': 667, 'C': 722, 'D': 722, 'E': 667, 'F': 611, 'G': 778,
         'H': 722, 'I': 278, 'J': 500, 'K': 667, 'L': 556, 'M': 833, 'N': 722,
         'O': 778, 'P': 667, 'Q': 778, 'R': 722, 'S': 667, 'T': 611, 'U': 722,
         'V': 667, 'W': 944, 'X': 667, 'Y': 667, 'Z': 611, 'a': 556, 'b': 556,
         'c': 500, 'd': 556, 'e': 556, 'f': 278, 'g': 556, 'h': 556, 'i': 222,
         'j': 222, 'k': 500, 'l': 222, 'm': 833, 'n': 556, 'o': 556, 'p': 556,
         'q': 556, 'r': 333, 's': 500, 't': 278, 'u': 556, 'v': 500, 'w': 722,
         'x': 500, 'y': 500, 'z': 500}
ARIAL_BOLD = dict(ARIAL, **{
    'A': 722, 'B': 722, 'C': 722, 'D': 722, 'E': 667, 'F': 611, 'G': 778,
    'H': 722, 'I': 278, 'J': 556, 'K': 722, 'L': 611, 'M': 833, 'N': 722,
    'O': 778, 'P': 667, 'Q': 778, 'R': 722, 'S': 667, 'T': 611, 'U': 722,
    'V': 667, 'W': 944, 'X': 667, 'Y': 667, 'Z': 611, 'a': 556, 'b': 611,
    'c': 556, 'd': 611, 'e': 556, 'f': 333, 'g': 611, 'h': 611, 'i': 278,
    'j': 278, 'k': 556, 'l': 278, 'm': 889, 'n': 611, 'o': 611, 'p': 611,
    'q': 611, 'r': 389, 's': 556, 't': 333, 'u': 611, 'v': 556, 'w': 778,
    'x': 556, 'y': 556, 'z': 500, "'": 238, '-': 333, '.': 278, ',': 278,
    '(': 333, ')': 333, '/': 278, '&': 722})


def build_maps(doc):
    """{font_basename: {code: char}} plus per-font /Widths for validation."""
    maps, widths = {}, {}
    for xref in range(1, doc.xref_length()):
        try:
            obj = doc.xref_object(xref)
        except Exception:
            continue
        if "/Type /Font" not in obj or "/Subtype /Type1" not in obj:
            continue
        base = re.search(r"/BaseFont /(\S+)", obj)
        enc = re.search(r"/Encoding (\d+) 0 R", obj)
        first = re.search(r"/FirstChar (\d+)", obj)
        w = re.search(r"/Widths \[([^\]]*)\]", obj, re.S)
        if not (base and enc):
            continue
        name = base.group(1).split("+")[-1]
        diffs = doc.xref_object(int(enc.group(1)))
        m = re.search(r"/Differences \[(.*?)\]", diffs, re.S)
        if not m:
            continue
        cmap, code = {}, 0
        for tok in m.group(1).split():
            if tok.isdigit():
                code = int(tok)
            elif tok.startswith("/MT"):
                cp = tok[3:]
                if cp.isdigit():
                    n = int(cp)
                    # 0x80-0x9F are unassigned in Unicode; the producer means
                    # the cp1252 glyph at that byte (150 -> en dash, 146 -> ').
                    cmap[code] = (bytes([n]).decode("cp1252", "replace")
                                  if 0x80 <= n <= 0x9F else chr(n))
                code += 1
            elif tok.startswith("/"):
                code += 1
        maps[name] = cmap
        if w and first:
            widths[name] = (int(first.group(1)),
                            [float(v) for v in w.group(1).split()])
    return maps, widths


def validate(maps, widths):
    """Decoded chars must reproduce the real Arial advance widths."""
    report = []
    for name, table in (("Gen_Arial", ARIAL), ("Gen_Arial_Bold", ARIAL_BOLD)):
        if name not in maps or name not in widths:
            continue
        first, ws = widths[name]
        ok = bad = 0
        misses = []
        for code, ch in sorted(maps[name].items()):
            i = code - first
            if not (0 <= i < len(ws)) or ch not in table:
                continue
            if abs(ws[i] - table[ch]) <= 1:
                ok += 1
            else:
                bad += 1
                misses.append((code, ch, ws[i], table[ch]))
        report.append((name, ok, bad, misses[:8]))
    return report


def main():
    doc = fitz.open(PDF)
    maps, widths = build_maps(doc)
    for name, ok, bad, misses in validate(maps, widths):
        print(f"width check {name}: {ok} match, {bad} mismatch {misses if misses else ''}")

    by24 = {}
    for k, v in maps.items():
        key = k[:24]
        if key in by24 and by24[key] != v:
            raise SystemExit(f"font name collision at 24 chars: {key!r}")
        by24[key] = v

    page = doc[0]
    out, unmatched = [], set()
    for b in page.get_text("dict")["blocks"]:
        for line in b.get("lines", []):
            # Emit one record per LINE: the producer splits a label like
            # "East-West (Petroline) [56]" across several spans.
            parts, fonts, sizes = [], [], []
            x0 = y0 = 1e9
            x1 = y1 = -1e9
            for s in line["spans"]:
                fam = s["font"]
                # Span font names are truncated to 24 chars. Key the lookup on
                # the same truncation and match EXACTLY -- a prefix match makes
                # "Gen_Arial_Bold" collide with "Gen_Arial" and decode to mush.
                cmap = by24.get(fam)
                if cmap is None:
                    unmatched.add(fam)
                    continue
                parts.append("".join(cmap.get(ord(c), c) for c in s["text"]))
                fonts.append(fam)
                sizes.append(s["size"])
                bx0, by0, bx1, by1 = s["bbox"]
                x0, y0, x1, y1 = min(x0, bx0), min(y0, by0), max(x1, bx1), max(y1, by1)
            txt = "".join(parts).strip()
            if not txt:
                continue
            dom = max(set(fonts), key=fonts.count)
            out.append({"text": txt, "font": dom,
                        "size": round(max(sizes), 2),
                        "bbox": [round(v, 2) for v in (x0, y0, x1, y1)],
                        "center": [round((x0 + x1) / 2, 2), round((y0 + y1) / 2, 2)]})
    Path("traces/labels.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"\ndecoded {len(out)} spans; unmatched fonts: {sorted(unmatched)}")
    for s in out[:40]:
        print(f"  {s['text']!r:45s} {s['font'][:22]:24s} {s['size']}")


if __name__ == "__main__":
    main()
