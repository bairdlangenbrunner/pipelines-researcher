#!/usr/bin/env python3
"""Index the dominant documents (local text in the scratchpad) against every in-scope row's
name forms -> doc_index.json {url: {"local_text": path, "chars": n, "mentions": {pid: [forms]}}}.
The exhaustion pass then knows which documents actually NAME which rows, so an agent reads
a document for its row only when the row is in it (and the orchestrator can see what each
document can serve). Hand-maintained URL->file map (the files were fetched 2026-09-04)."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[3] / "scripts")); sys.path.insert(0, str(HERE))
from url_verifier import _name_present
DOCS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/private/tmp/claude-501/-Users-baird-Dropbox--git-ALL--github-repos-gem-pipelines-researcher/1e248ea3-f7e1-4f21-8197-55d7be11209f/scratchpad/docs")
MAP = {
 "https://img9.qianzhan.com/policy/202307/14/20230714-d7d735aa6fb9eae9.pdf": "qianzhan_drcplan.txt",
 "https://static.sse.com.cn/disclosure/bond/announcement/company/c/new/2025-04-03/242696_20250403_SXBW.pdf": "sse_242696.txt",
 "https://www.quannan.gov.cn/qnxxxgk/wrfz/202411/b3adaed1adfe445db29769eaf2f7002b/files/faad1fb7c1214b8a8394299531ab10a8.pdf": "quannan_2024.txt",
 "https://www.quannan.gov.cn/qnxxxgk/qnxfgw/202108/t20210830_2028305.shtml": "quannan_2021.txt",
 "https://en.wikipedia.org/wiki/West%E2%80%93East_Gas_Pipeline": "wiki_wep.txt",
 "https://www.huaon.com/channel/trend/624729.html": "huaon_624729.txt",
 "http://www.petrobest.com/success_info.php?cid=74": "petrobest_74.txt",
 "https://web.archive.org/web/20230902105154/http://jxgajc.com/Hr/show-10438.aspx": "jxgajc_10438.txt",
 "https://web.archive.org/web/20230902005946/http://jxgajc.com/Hr/show-11456.aspx": "jxgajc_11456.txt",
 "http://www.nea.gov.cn/2012-11/05/c_131957190.htm": "nea_2012.txt",
 "https://www.mee.gov.cn/gkml/sthjbgw/spwj1/201612/t20161222_369429.htm": "mee_2016.txt",
 "https://www.mee.gov.cn/xxgk2018/xxgk/xxgk11/202509/t20250925_1128127.html": "mee_2025.txt",
 "https://www.pipechina.com.cn/front/tzgg/2001801.html": "pipechina_2001801.txt",
 "https://news.sina.com.cn/o/2011-08-29/193423070729.shtml": "sina_2011_p4776.txt",
}
DOC_TITLES = {
 "quannan_2024.txt": "江西省天然气集团管道分公司《赣州南（信丰-瑞金段）、（龙南-全南段）等4条支线突发环境事件应急预案》2024-09-20 (321 pp; OPERATOR disclosure: states each branch's length, 管径 DN250/400/450, 设计压力, stations)",
 "quannan_2021.txt": "SOFT-404: the URL now serves the county homepage (200, no article text); no Wayback capture (CDX empty 2026-09-04). Not a citable page any more; do not carry it.",
 "sse_242696.txt": "江西省天然气集团 corporate bond tracking report 2025-04-03 (35 pp) — SYSTEM-LEVEL ONLY (省管网一期/二期 totals), names no segment except P4789",
 "qianzhan_drcplan.txt": "Jiangxi DRC provincial pipeline plan PDF (24 pp): Phase I 870 km built; Phase II 98 km; 江西专线 53 km (2010-06); 72 new provincial segments ~2260 km",
 "sina_2011_p4776.txt": "Sina 2011-08-29: 丰城至抚州段 trial commissioning; states Phase I network 2008-10 start, 825 km, 预计总投资31亿元 (= P4777 Length/Construction/SegmentCost)",
 "nea_2012.txt": "NEA 2012-11-05 notice: WEP1 3840 km, WEP2 8704 km, WEP3 started 2012-10 — system level only",
}
forms = json.loads((HERE / "name_forms.json").read_text())
out = {}
for url, fn in MAP.items():
    p = DOCS / fn
    if not p.exists() or p.stat().st_size < 200:
        out[url] = {"local_text": None, "chars": 0, "mentions": {}, "note": "fetch failed / empty"}
        continue
    txt = p.read_text(errors="ignore")
    digest = p.with_name(p.stem + ".digest.txt")
    men = {}
    for pid, f in forms.items():
        hit = [n for n in f.get("segment", []) if _name_present(txt, n)]
        sys_hit = [n for n in f.get("system", []) if _name_present(txt, n)]
        if hit or sys_hit:
            men[pid] = {"segment": hit, "system": sys_hit}
    out[url] = {"local_text": str(p), "chars": len(txt), "mentions": men,
                "digest": str(digest) if digest.exists() else None, "title": DOC_TITLES.get(fn, "")}
(HERE / "doc_index.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
for url, d in out.items():
    seg = [p for p, m in d["mentions"].items() if m["segment"]]
    sy = [p for p, m in d["mentions"].items() if not m["segment"] and m["system"]]
    print(f"{d['chars']:7} chars  seg-named {len(seg):2} {seg}  system-only {len(sy):2}  {url[:70]}")
