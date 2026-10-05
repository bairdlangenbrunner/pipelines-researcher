#!/usr/bin/env python3
"""Edit string values inside a JSON file WITHOUT re-serializing it, so a hand-written or
oddly-indented staged file keeps its exact formatting and the git diff shows only the cells
that moved (restyle_staged_owners.py, 2026-10-05: a re-dump churned 268 files).

    text = patch_text(text, [
        (("fills", 3, "values", "Owner1"), "Kinder Morgan Inc"),          # replace a string value
        (("fills", 3, "researcher_notes"), "…"),                           # same; inserted if the key is missing
    ])

A path is the sequence of object keys / array indexes from the root to a STRING value (or
to a missing key of an existing object, which is then appended as the object's last member,
on its own line when the object is multi-line). Anything else raises."""
from __future__ import annotations

import json
import re

_TOKEN = re.compile(r'''
    (?P<ws>\s+) |
    (?P<str>"(?:[^"\\]|\\.)*") |
    (?P<num>-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?) |
    (?P<lit>true|false|null) |
    (?P<p>[{}\[\]:,])
''', re.X)


def _tokens(text: str):
    pos = 0
    n = len(text)
    while pos < n:
        m = _TOKEN.match(text, pos)
        if not m:
            raise ValueError(f"bad JSON at {pos}: {text[pos:pos + 20]!r}")
        kind = m.lastgroup
        if kind != "ws":
            yield kind, m.start(), m.end()
        pos = m.end()


def _index(text: str):
    """-> {path: (start, end)} for every string VALUE, and {path: (open, close)} for every
    object, where path is a tuple of keys/indexes from the root."""
    strings: dict[tuple, tuple[int, int]] = {}
    objects: dict[tuple, tuple[int, int]] = {}
    stack: list[list] = []        # [kind, path, state, key, open_pos]; state: 'key'|'colon'|'value'|'sep'
    path: tuple = ()

    def cur_path(frame):
        if frame[0] == "obj":
            return frame[1] + (frame[3],)
        return frame[1] + (frame[3],)

    for kind, s, e in _tokens(text):
        tok = text[s:e]
        top = stack[-1] if stack else None
        if top is not None and top[0] == "obj" and top[2] == "key":
            if tok == "}":
                objects[top[1]] = (top[4], e)
                stack.pop()
                if stack:
                    stack[-1][2] = "sep"
                continue
            if kind != "str":
                raise ValueError(f"expected a key at {s}")
            top[3] = json.loads(tok)
            top[2] = "colon"
            continue
        if top is not None and top[0] == "obj" and top[2] == "colon":
            if tok != ":":
                raise ValueError(f"expected ':' at {s}")
            top[2] = "value"
            continue
        if top is not None and top[2] == "sep":
            if tok == ",":
                if top[0] == "obj":
                    top[2] = "key"
                else:
                    top[3] += 1
                    top[2] = "value"
                continue
            if (tok == "}" and top[0] == "obj") or (tok == "]" and top[0] == "arr"):
                if top[0] == "obj":
                    objects[top[1]] = (top[4], e)
                stack.pop()
                if stack:
                    stack[-1][2] = "sep"
                continue
            raise ValueError(f"expected ',' or a closer at {s}")
        # a value position (root, after ':' in an object, or in an array)
        if top is None:
            vpath = ()
        elif top[0] == "arr" and top[2] == "value" and tok == "]":   # empty array
            stack.pop()
            if stack:
                stack[-1][2] = "sep"
            continue
        else:
            vpath = cur_path(top)
        if tok == "{":
            stack.append(["obj", vpath, "key", None, s])
            continue
        if tok == "[":
            stack.append(["arr", vpath, "value", 0, s])
            continue
        if kind == "str":
            strings[vpath] = (s, e)
        if top is not None:
            top[2] = "sep"
    if stack:
        raise ValueError("unterminated JSON")
    return strings, objects


def patch_text(text: str, edits: list[tuple[tuple, str]]) -> str:
    strings, objects = _index(text)
    ops: list[tuple[int, int, str]] = []            # (start, end, replacement)
    for path, new in edits:
        path = tuple(path)
        if path in strings:
            s, e = strings[path]
            ops.append((s, e, json.dumps(new, ensure_ascii=_ascii_style(text, s, e))))
            continue
        parent, key = path[:-1], path[-1]
        if parent not in objects or not isinstance(key, str):
            raise KeyError(f"no string value and no object to insert into at {path}")
        o, c = objects[parent]
        body = text[o + 1:c - 1]
        if not body.strip():                       # empty object
            ops.append((o + 1, c - 1, json.dumps(key) + ": " + json.dumps(new, ensure_ascii=False)))
            continue
        # indentation of the object's last member, and whether it sits on its own line
        m = re.search(r"\n([ \t]*)\S[^\n]*\s*$", body)
        last_ws = body[len(body.rstrip()):]
        if m:
            ins = "," + "\n" + m.group(1) + json.dumps(key) + ": " + json.dumps(new, ensure_ascii=False)
        else:
            ins = ", " + json.dumps(key) + ": " + json.dumps(new, ensure_ascii=False)
        at = c - 1 - len(last_ws)
        ops.append((at, at, ins))
    ops.sort(key=lambda t: t[0], reverse=True)
    for i in range(len(ops) - 1):
        if ops[i + 1][1] > ops[i][0]:
            raise ValueError("overlapping edits")
    out = text
    for s, e, rep in ops:
        out = out[:s] + rep + out[e:]
    return out


def _ascii_style(text: str, s: int, e: int) -> bool:
    """Keep the file's own escaping: a string that already carries \\uXXXX escapes and no raw
    non-ASCII stays ASCII-escaped."""
    tok = text[s:e]
    return "\\u" in tok and tok.isascii()


if __name__ == "__main__":
    import sys
    t = open(sys.argv[1], encoding="utf-8").read()
    strs, objs = _index(t)
    print(f"{len(strs)} string values, {len(objs)} objects; round-trip parse ok: {json.loads(t) is not None}")
