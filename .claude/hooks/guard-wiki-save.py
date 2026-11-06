#!/usr/bin/env python3
"""PreToolUse hook (Bash): a gem.wiki save must go through scripts/wiki_save.py.

A page saved with gemwiki.edit_page() and not purged is cached without the Google Maps script, and readers
see "Your browser is not compatible with Google Maps v3" (docs/sops/wiki_pages.md). wiki_save.save() edits,
purges and checks the render. This hook blocks a shell command that calls edit_page, or posts action=edit
to the API, unless the command goes through wiki_save (Baird 2026-11-06: "make sure this never happens again").
"""
import json, re, sys

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if data.get('tool_name') != 'Bash':
    sys.exit(0)
cmd = data.get('tool_input', {}).get('command', '') or ''
direct = re.search(r'\bedit_page\s*\(|action\s*=\s*["\']?edit\b|\bappendtext\s*=|\bprependtext\s*=', cmd)
if direct and 'wiki_save' not in cmd:
    sys.stderr.write(
        'blocked: a gem.wiki save must go through scripts/wiki_save.py (wiki_save.save(s, title, text=..., '
        'summary=...)), which edits, purges and checks that the map renders. Calling gemwiki.edit_page or '
        'action=edit directly leaves the page cached without the Google Maps script. See docs/sops/wiki_pages.md.\n')
    sys.exit(2)
sys.exit(0)
