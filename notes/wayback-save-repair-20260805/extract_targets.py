#!/usr/bin/env python3
"""Extract every web.archive.org/save/ occurrence in the backend + the unique targets."""
import json, re, sys
import pandas as pd

REPO = "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher"
STAMP = "20260805"
TABS = {
    "gas":  dict(csv=f"{REPO}/data/GGIT_gas_snapshot_{STAMP}.csv", header=2, tab="Gas pipelines"),
    "oil":  dict(csv=f"{REPO}/data/GOIT_oil_ngl_snapshot_{STAMP}.csv", header=2, tab="Oil/NGL pipelines"),
    "oo":   dict(csv=f"{REPO}/data/GEM_operators_owners_snapshot_{STAMP}.csv", header=1, tab=None),
}
# token = any whitespace-delimited chunk containing web.archive.org/save
SAVE_TOK = re.compile(r'\S*web\.archive\.org/save/\S*', re.I)

occ = []
for key, cfg in TABS.items():
    df = pd.read_csv(cfg["csv"], header=cfg["header"], low_memory=False, dtype=str)
    for col in df.columns:
        s = df[col].dropna()
        s = s[s.str.contains("web.archive.org/save", case=False, regex=False)]
        for idx, val in s.items():
            for m in SAVE_TOK.finditer(val):
                occ.append(dict(tab=key, sheet_tab=cfg["tab"], col=col, csv_idx=int(idx),
                                sheet_row=int(idx) + (4 if cfg["header"] == 2 else 3),
                                token=m.group(0), cell=val))
print(f"occurrences: {len(occ)}")

# ---- normalize token -> target url
def split_target(tok):
    m = re.search(r'web\.archive\.org/save/(.*)$', tok, re.I)
    if not m:
        return None, "no-save-suffix"
    rest = m.group(1)
    lead = tok[:m.start()]  # anything before, e.g. https:// or junk
    return rest, lead

shapes = {}
targets = {}
for o in occ:
    rest, lead = split_target(o["token"])
    o["raw_target"] = rest
    o["lead"] = lead
    # classify shape
    if rest is None:
        sh = "UNPARSED"
    elif re.match(r'^https?://', rest, re.I):
        sh = "plain-scheme"
    elif re.match(r'^https?(%3A|%3a)', rest):
        sh = "pct-encoded-scheme"
    elif rest == "":
        sh = "empty-target"
    elif re.match(r'^\d{1,14}/', rest):
        sh = "timestamp-prefixed"
    elif re.match(r'^_embed/', rest):
        sh = "embed-prefixed"
    else:
        sh = "no-scheme"
    o["shape"] = sh
    shapes.setdefault(sh, []).append(o["token"])

print("\ntoken shapes:")
for sh, toks in sorted(shapes.items(), key=lambda kv: -len(kv[1])):
    print(f"  {sh}: {len(toks)}")
    for t in toks[:4]:
        print(f"      {t[:150]}")

# leading junk check
leads = {}
for o in occ:
    leads.setdefault(o["lead"], 0)
    leads[o["lead"]] += 1
print("\nleading prefixes before web.archive.org:")
for l, n in sorted(leads.items(), key=lambda kv: -kv[1]):
    print(f"  {n:4d}  {l!r}")

# cells with >1 token or extra content
multi = [o for o in occ if len(SAVE_TOK.findall(o["cell"])) > 1]
extra = [o for o in occ if o["cell"].strip() != o["token"].strip()]
print(f"\ncells with >1 save-token: {len(multi)}")
print(f"occurrences whose cell has other content besides the token: {len(extra)}")
for o in extra[:8]:
    print(f"    [{o['tab']}/{o['col']} row{o['sheet_row']}] {o['cell'][:220]!r}")

json.dump(occ, open(f"{REPO}/notes/wayback-save-repair-{STAMP}/occurrences.json", "w"), indent=1)
uniq = sorted({o["raw_target"] for o in occ if o["raw_target"]})
print(f"\nunique raw targets: {len(uniq)}")
json.dump(uniq, open(f"{REPO}/notes/wayback-save-repair-{STAMP}/raw_targets.json", "w"), indent=1)
