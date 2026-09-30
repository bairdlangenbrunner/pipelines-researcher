#!/usr/bin/env python3
"""Name forms per ProjectID for the relevance check (`verify_url(..., name=[forms])`).

A ref must NAME the pipeline (standing rule 4a). A Chinese approval names 丰城-抚州输气干线,
never "Phase I, Fengcheng-Fuzhou Gas Pipeline", so the check needs every identity the row
carries: the Latin pipeline + segment names and the `OtherLanguage*` names, plus the A-B
endpoint pair in the punctuation variants Chinese prose actually uses (-, —, –, －, 至).

`OtherLanguageSegmentName` is NOT used on the Jiangxi network rows: on P4780/P4785–P4790 it
holds fragments of one multi-row string (an MZ-lane name defect, recorded in v2), and on
P4795 it names a Hebei LNG terminal line. Only P4649/P4657 carry a trustworthy value there.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
_SEG_OK = {"P4649", "P4657"}
_SPLIT = re.compile(r"[,，、;；]")
_SEP = r"\s*[-—–－~]\s*"
_TAIL = r"(?:输气|输配|支干线|支线|干线|管道|管线|线|段|\)|$)"
# Endpoint pairs, stopping BEFORE a generic tail: 丰城-抚州输气干线 -> (丰城, 抚州), not
# (丰城, 抚州输气). Endpoints are 2-3 chars (井开区, 金沙湾, 景德镇 are 3).
_PAIR = re.compile(r"([一-鿿]{2,3})" + _SEP + r"([一-鿿]{2,3}?)(?=" + _TAIL + ")")
_CHAIN = re.compile(r"(?:[一-鿿]{2,3}" + _SEP + r"){2,}[一-鿿]{2,3}")
_GENERIC_LATIN = {"phase i", "phase ii", "phase iii", "trunk line", "east section", "middle section"}
_PHASE = re.compile(r"^(一|二|三)期工程[，,]?\s*")


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip()


def name_forms_for(row: dict) -> dict:
    """{"segment": [forms naming THIS row], "system": [forms naming only the network/trunk]}.
    A match on a `system` form says the page is about the parent system, not the A-B line --
    the exact failure MZ flagged -- so callers report it as `name_level: system`, and on a
    row that HAS a segment identity it counts as a relevance re-read, not a pass."""
    pid = str(row.get("ProjectID", "")).strip()
    forms: list[str] = []

    def add(x):
        x = _clean(x)
        if x and x not in forms:
            forms.append(x)

    pn, sn = _clean(row.get("PipelineName")), _clean(row.get("SegmentName"))
    if sn:
        add(f"{pn} {sn}")
        if sn.lower() not in _GENERIC_LATIN:
            add(sn)
        # "Phase I, Fengcheng-Fuzhou Gas Pipeline" -> "Fengcheng-Fuzhou"
        for m in re.finditer(r"([A-Z][A-Za-z'\u2019]+)\s*[-–—]\s*([A-Z][A-Za-z'\u2019]+)", sn):
            if m.group(1).lower() not in ("district",):
                add(f"{m.group(1)}-{m.group(2)}"); add(f"{m.group(1)}–{m.group(2)}")
    # bare phase-parent rows ("Phase I", "Phase II"): the Chinese identity below the system
    # name is 一期/二期 -- without these the parent row can only ever match at system level
    m = re.fullmatch(r"Phase\s+(I{1,3}|IV|V)", sn or "")
    if m:
        zh_phase = {"I": "一期", "II": "二期", "III": "三期", "IV": "四期", "V": "五期"}[m.group(1)]
        for stem in ("江西省天然气管网", "省天然气管网", "天然气管网"):
            add(f"{stem}{zh_phase}")
        add(f"管网{zh_phase}工程")
    zh_primary = _clean(row.get("OtherLanguagePrimaryPipelineName"))
    zh_alt = _clean(row.get("OtherLanguageAlternativePipelineNames"))
    zh_seg = _clean(row.get("OtherLanguageSegmentName")) if pid in _SEG_OK else ""
    zh_parts = []
    for raw in (zh_alt, zh_seg):
        for part in _SPLIT.split(raw):
            part = _PHASE.sub("", _clean(part))
            part = part.replace("（", "(").replace("）", ")")
            if part:
                zh_parts.append(part)
                inner = re.findall(r"\(([^)]+)\)", part)
                outer = re.sub(r"\([^)]*\)", "", part).strip()
                if outer:
                    zh_parts.append(outer)
                zh_parts.extend(inner)
    for zp in zh_parts:
        if zp == zh_primary:
            continue
        add(zp)
        pairs = set(_PAIR.findall(zp))
        for ch in _CHAIN.findall(zp):
            pts = [x for x in re.split(_SEP, ch) if x]
            if len(pts) >= 3:
                pairs.add((pts[0], pts[-1]))
        for a, b in pairs:
            for sep in ("-", "至"):          # dash variants are unified by the verifier
                add(f"{a}{sep}{b}")
    system = [f for f in (pn, zh_primary) if f]
    # A Chinese system name is usually quoted by its stem: 川气东送输气管道 is "川气东送" in
    # every article (P4657's agent found the fuzzy match missing all of them, 2026-09-04).
    # Strip one generic pipeline suffix when the stem is a real name (>= 4 chars) and does
    # not itself end in 天然气 -- 江西省天然气管网 -> 江西省天然气 would match the operator's
    # name on every page in the province, which is exactly the system-level false positive
    # this module exists to prevent.
    m = re.fullmatch(r"(.+?)(输气管道|天然气管道|输气管线|管道|管网)", zh_primary or "")
    if m and len(m.group(1)) >= 4 and not m.group(1).endswith("天然气"):
        system.append(m.group(1))
    return {"trunk": is_trunk(row), "segment": [f for f in forms if f not in system], "system": system}


def load_forms(csv_name: str, pids) -> dict[str, dict]:
    df = pd.read_csv(REPO / "data" / csv_name, header=2, low_memory=False,
                     keep_default_na=False, na_values=[])
    sub = df[df["ProjectID"].astype(str).isin(set(pids))]
    return {str(r["ProjectID"]): name_forms_for(r) for _, r in sub.iterrows()}


def all_forms(f: dict) -> list[str]:
    """Segment forms first, system forms last -- the verifier reports the FIRST match."""
    return list(f.get("segment", [])) + list(f.get("system", []))


_TRUNK_RE = re.compile(r"trunk|main\s*line|主干线|干线$", re.I)


def is_trunk(row: dict) -> bool:
    """A trunk-parent row (P4657 'Trunk line'; P4934/P4947 with no SegmentName) has no
    identity below the system name, so a system-level match is a segment-level match."""
    seg = (row.get("SegmentName") or "").strip()
    return not seg or bool(_TRUNK_RE.search(seg))


def name_level(matched: str | None, f: dict) -> str:
    if not matched:
        return ""
    if f.get("trunk") or matched in f.get("segment", []):
        return "segment"
    return "system"


if __name__ == "__main__":
    wl = json.loads((HERE / "worklist.json").read_text())
    pids = sorted({u["project_id"] for u in wl["units"]})
    forms = load_forms(wl["scope"]["csv"], pids)
    (HERE / "name_forms.json").write_text(json.dumps(forms, ensure_ascii=False, indent=1))
    for p in pids:
        print(p, forms[p])
