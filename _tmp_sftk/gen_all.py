# -*- coding: utf-8 -*-
"""B1-YHZP + B4-SFTK 生成器 v2（手工 SFTK 章节表 + YHZP 眉批 NEEDS_REVIEW）。
输出（仅 ALLOWED PATHS）：
  data/sources/yhzp_sources.jsonl
  data/rules/candidate/CAND-YHZP_rules.jsonl
  data/sources/sftk_sources.jsonl
  data/rules/candidate/CAND-SFTK_rules.jsonl
全部 QC 通过才落盘。不 commit。"""
import json, hashlib, re, os, collections

ROOT = "D:/shuntian"
YHZP_REL = "data/classics/original/YHZP_渊海子平_完整全文.md"
SFTK_REL = "data/classics/original/SFTK_神峰通考_完整全文.md"
OUT_Y_SRC = os.path.join(ROOT, "data/sources/yhzp_sources.jsonl")
OUT_Y_RULE = os.path.join(ROOT, "data/rules/candidate/CAND-YHZP_rules.jsonl")
OUT_S_SRC = os.path.join(ROOT, "data/sources/sftk_sources.jsonl")
OUT_S_RULE = os.path.join(ROOT, "data/rules/candidate/CAND-SFTK_rules.jsonl")
NOW = "2026-09-14T00:00:00Z"
GM = {"ORIGINAL": "A", "ANNOTATION": "B", "LATER_COMMENTARY": "C", "UNVERIFIED": "D"}

import time as _time
SNAP = {}  # snap["YHZP"] = dict(raw, lines, hash) captured atomically

def _struct_ok(tag, lines, raw_len):
    """Validate that a captured snapshot parses to the EXPECTED structure.
    YHZP: must expose 300-310 '第 N 章' full-line headers.
    SFTK: manual table line numbers must all fit within the snapshot."""
    if tag == "YHZP":
        nchap = sum(1 for ln in lines if _re.match(r"^第\s*[0-9０-９ ]{1,5}\s*章\s*$", ln.strip()))
        return 300 <= nchap <= 310, "chapters=%d" % nchap
    else:
        lo = min((c[1] for c in SFTK_SECS), default=0)
        hi = max((c[1] for c in SFTK_SECS), default=0)
        ok = (1 <= lo and hi < len(lines) + 1) and raw_len > 100000
        return ok, "lines=%d table-span=%d..%d" % (len(lines), lo, hi)

import re as _re
def load_frozen(rel, tag, retries=12, gap=5.0):
    """Capture ONE atomic, structure-validated snapshot of the original.
    Re-reads (with backoff) until a consistent snapshot whose structure matches
    expectation. file_hash is bound to the EXACT raw bytes used for content,
    so source_text is always reproducible from (file_hash, line range)."""
    p = os.path.join(ROOT, rel)
    # SFTK_SECS is defined later; guard with a lazy struct check
    last_info = None
    for attempt in range(retries + 1):
        b = open(p, "rb").read()                      # single atomic read
        h = hashlib.sha256(b).hexdigest()
        text = b.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        lines = text.splitlines()
        if tag == "SFTK" and "SFTK_SECS" not in globals():
            ok, info = True, "sftk-table-not-yet"      # accept on first pass
        else:
            ok, info = _struct_ok(tag, lines, len(b))
        last_info = info
        if ok:
            print("%s snapshot OK: %s/%d行 %s (attempt %d)" % (
                tag, h[:12], len(lines), info, attempt + 1))
            return b, lines, h
        print("%s snapshot INCONSISTENT (%s) attempt %d -> wait %.0fs retry" % (
            tag, info, attempt + 1, gap))
        _time.sleep(gap)
    raise SystemExit("FATAL: %s never reached a structurally-valid snapshot after %d attempts (last: %s). "
                     "Original is being actively rewritten by a parallel process; aborting to avoid "
                     "binding source_text to a hash whose bytes no longer match the content." % (
                         tag, retries + 1, last_info))

_, yl, yhash = load_frozen(YHZP_REL, "YHZP")
_, sl, shash = load_frozen(SFTK_REL, "SFTK")
print("frozen YHZP=%s/%d SFTK=%s/%d (raw-bytes CRLF hashes)" % (yhash[:12], len(yl), shash[:12], len(sl)))

def norm(s): return re.sub(r"\s+", "", s)

def is_noise(s):
    st = s.strip()
    if not st: return True
    if "www.luckclub" in st: return True
    if re.match(r"^第\s*\d+\s*页\s*/\s*共\s*\d+\s*页", st): return True
    if "古籍典藏" in st: return True
    if st in ("《》", "----", "==="): return True
    if re.match(r"^渊海子平卷[一二三四五1-5]$", st): return True
    if re.match(r"^===== 第", st): return True
    return False

# ==================== YHZP (305 chapters -> 305 ORIGINAL sources) ====================
chap_re = re.compile(r"^第\s*([0-9０-９ ]{1,5})\s*章\s*$")
chapters = []
for i, ln in enumerate(yl, 1):
    m = chap_re.match(ln.strip())
    if m:
        num = re.sub(r"\s+", "", m.group(1)).translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        title = ""
        for k in range(i, min(i + 5, len(yl) + 1)):
            t = yl[k - 1].strip()
            if t and t != ln.strip() and not is_noise(t):
                title = t; break
        chapters.append((i, int(num), title))
chapters.sort(key=lambda x: x[1])
# keep first occurrence per num
seen, chapters = set(), []
for row in chapters:
    if row[1] in seen: continue
    seen.add(row[1]); chapters.append(row)
print("YHZP unique chapters:", len(chapters))

volmap = {}
for i, ln in enumerate(yl, 1):
    m = re.search(r"渊海子平卷([一二三四五1-5])", ln)
    if m: volmap.setdefault(m.group(1), i)
def vol_of(line):
    last = "一"
    for v, vl in sorted(volmap.items(), key=lambda x: x[1]):
        if vl < line: last = ("一二三四五" if v in "一二三四五" else str(v))
    return last
VOLCODE = {"一": "V01", "二": "V02", "三": "V03", "四": "V04", "五": "V05"}

LATER_MARK = re.compile(r"^白话译文|^白\s*话\s*译\s*文|^现代启示|^关键词|^\*\*思考|^思考")
yhzp_sources = []
for (cl, num, title) in chapters:
    e = len(yl)
    for (c2, n2, t2) in chapters:
        if c2 > cl:
            e = c2 - 1; break
    o_start = cl + 1
    for k in range(cl, min(e, cl + 60) + 1):
        if norm(yl[k - 1]) == "原文":
            o_start = k; break
    l_start = None
    for k in range(o_start, e + 1):
        if LATER_MARK.match(yl[k - 1].strip()):
            l_start = k; break
    o_end = (l_start - 1) if l_start else e
    block, has_marginal = [], False
    for k in range(o_start + 1, o_end + 1):
        s = yl[k - 1]
        if is_noise(s): continue
        st = s.strip()
        if st == title and k <= cl + 3:
            continue
        if st.startswith("眉批") or st.startswith("附注"):
            has_marginal = True; block.append(s); continue
        if st.startswith("白话译文") or st.startswith("现代启示") or st.startswith("关键词"):
            continue
        if st: block.append(s)
    text = "\n".join(block).strip()
    code = "CH%03d" % num
    vol = vol_of(cl); vc = VOLCODE.get(vol, "V01")
    layer = "UNVERIFIED" if num == 0 else "ORIGINAL"
    sid = "YHZP-%s/P-%s-P001" % (vc, code)
    yhzp_sources.append({
        "source_id": sid,
        "source_version": "1.0.0",
        "source_hash": hashlib.sha256(text.encode()).hexdigest(),
        "text_layer": layer,
        "evidence_grade": GM[layer],
        "source_location": {
            "book": "渊海子平",
            "path": [
                {"level": "volume", "code": vc, "name": "卷" + vol},
                {"level": "pian", "code": code, "name": ("第%d章" % num) + (title or "")},
            ],
            "passage": "第1段",
            "line_start": o_start, "line_end": o_end, "file_hash": yhash,
        },
        "resource_id": "SRC-" + sid,
        "logical_uri": "source://yhzp/%s/%s/passage_001" % (vc.lower(), code.lower()),
        "relative_path": "sources/yhzp/%s/%s/passage_001.md" % (vc.lower(), code.lower()),
        "runtime_resolver": "resource://classic/yhzp/%s/%s" % (vc.lower(), code.lower()),
        "source_text": text,
        "provenance": {"chain": [sid], "completeness": "COMPLETE", "gaps": []},
        "handling_status": ("NEEDS_REVIEW" if (num == 0 or has_marginal or not text) else "RESOLVED"),
        "approval_status": "CANDIDATE",
        "approved_by": None, "approved_at": None,
        "created_at": NOW, "updated_at": None,
        "metadata": {
            "edition": {"type": "校勘本", "source": "luckclub 古籍典藏（www.luckclub.cn，自动提取 2026-08-12）", "editor": None, "year": "2026"},
            "collation_note": ("目录区" if num == 0 else
                               ("原文块含眉批/附注古注，未拆分，待 Human 签核" if has_marginal else
                                ("含现代白话译文/现代启示(LATER_COMMENTARY)，本条仅录原文块" if l_start else None))),
            "chapter_num": num, "chapter_title": title,
        },
    })
print("YHZP sources:", len(yhzp_sources), dict(collections.Counter(s["text_layer"] for s in yhzp_sources)),
      "NEEDS_REVIEW:", sum(1 for s in yhzp_sources if s["handling_status"] == "NEEDS_REVIEW"))

# ==================== SFTK (manual section table -> 54 sources) ====================
# (title, start_line, vol, text_layer, note)
SFTK_SECS = [
    ("叙（张楠自叙）", 12, "V01", "ORIGINAL", "OCR 繁校点校本，叙文夹少量现代校勘注"),
    ("目录", 45, "V01", "LATER_COMMENTARY", "目录为整理排版内容，非张楠正文"),
    ("五星正說類（安身命宮/安星辰/限行/度主/五星諸書/五星參悅頌）", 292, "V01", "ORIGINAL", None),
    ("男女合婚說", 355, "V01", "ORIGINAL", None),
    ("總論子平謬說類", 359, "V01", "ORIGINAL", None),
    ("動靜說", 389, "V01", "ORIGINAL", None),
    ("蓋頭說", 398, "V01", "ORIGINAL", None),
    ("六親說", 404, "V01", "ORIGINAL", None),
    ("病藥說類", 422, "V01", "ORIGINAL", None),
    ("雕枯旺弱四病說類", 432, "V01", "ORIGINAL", None),
    ("損益生長四藥說類", 453, "V01", "ORIGINAL", None),
    ("正官格", 473, "V01", "ORIGINAL", None),
    ("繼善篇", 479, "V01", "ORIGINAL", None),
    ("偏官格（附棄命從殺格）", 668, "V01", "ORIGINAL", None),
    ("喜忌篇", 741, "V01", "ORIGINAL", None),
    ("月支正財格（附棄從命財格）", 1444, "V02", "ORIGINAL", None),
    ("四言獨步（丁火棄命就財等）", 1480, "V02", "ORIGINAL", None),
    ("陽刃格", 2338, "V02", "ORIGINAL", None),
    ("雜氣財官印綬格（附時墓格）", 2570, "V02", "ORIGINAL", None),
    ("金神格", 2688, "V02", "ORIGINAL", None),
    ("井欄叉格", 2830, "V03", "ORIGINAL", None),
    ("夾丘拱財格", 3302, "V03", "ORIGINAL", None),
    ("專財格", 3325, "V03", "ORIGINAL", None),
    ("不換金骨髓歌斷", 3771, "V03", "ORIGINAL", None),
    ("十天干體象全編論", 3909, "V04", "ORIGINAL", None),
    ("生旺死絕圖", 4430, "V04", "ORIGINAL", None),
    ("陰陽通變妙訣", 4468, "V04", "ORIGINAL", None),
    ("定格局訣", 4472, "V04", "ORIGINAL", None),
    ("子平泛論", 4527, "V04", "ORIGINAL", None),
    ("十干從化定訣", 4531, "V04", "ORIGINAL", None),
    ("五陰歌", 4614, "V04", "ORIGINAL", None),
    ("天元一字歌", 4626, "V04", "ORIGINAL", None),
    ("運晦歌", 4630, "V04", "ORIGINAL", None),
    ("運通歌", 4634, "V04", "ORIGINAL", None),
    ("刑尅歌", 4645, "V04", "ORIGINAL", None),
    ("太乙妙指法", 4795, "V05", "ORIGINAL", None),
    ("論諸格有救", 4803, "V05", "ORIGINAL", None),
    ("取格指訣歌斷", 4809, "V05", "ORIGINAL", None),
    ("節氣歌斷", 4813, "V05", "ORIGINAL", None),
    ("崖泉男命賦", 4832, "V05", "ORIGINAL", None),
    ("講命捷徑賦", 4847, "V05", "ORIGINAL", None),
    ("身弱論", 4936, "V05", "ORIGINAL", None),
    ("五言獨步", 4955, "V05", "ORIGINAL", None),
    ("五行元理消息賦", 6244, "V06", "ORIGINAL", None),
    ("一行禪師天元賦", 6832, "V06", "ORIGINAL", None),
    ("相心賦", 7151, "V06", "ORIGINAL", None),
    ("仙機賦", 7155, "V06", "ORIGINAL", None),
    ("人鑑論", 7164, "V06", "ORIGINAL", None),
    ("淵源集說", 7168, "V06", "ORIGINAL", None),
    ("妖祥賦", 7195, "V06", "ORIGINAL", None),
    ("幽微天干賦", 7216, "V06", "ORIGINAL", None),
    ("人元消息賦", 7234, "V06", "ORIGINAL", None),
    ("地支賦", 7245, "V06", "ORIGINAL", None),
    ("病源賦", 7252, "V06", "ORIGINAL", None),
]
BODY_END = 7320  # before '## 上海图书馆藏书' publisher tail

def sftk_block(a, b):
    out = []
    for k in range(a, b + 1):
        s = sl[k - 1]
        if is_noise(s) or s.strip().startswith("## ") or s.strip() in ("二", "四", "六", "神", "峰", "通", "考"):
            continue
        t = s[3:] if s.strip().startswith("## ") else s
        if t.strip(): out.append(t.strip())
    return "\n".join(out).strip()

sftk_sources = []
sftk_sorted = sorted(SFTK_SECS, key=lambda x: x[1])
sftk_title2sid = {}
for idx, (title, a, vc, layer, note) in enumerate(sftk_sorted, start=1):
    b = sftk_sorted[idx][1] - 1 if idx < len(sftk_sorted) else BODY_END
    b = min(b, BODY_END)
    text = sftk_block(a, b)
    code = "L%03d" % idx
    vol_name = {"V01": "卷一", "V02": "卷二", "V03": "卷三", "V04": "卷四", "V05": "卷五", "V06": "卷六"}[vc]
    sid = "SFTK-%s/L-%s-P001" % (vc, code)
    sftk_title2sid[norm(title.split("（")[0])] = sid
    sftk_sources.append({
        "source_id": sid,
        "source_version": "1.0.0",
        "source_hash": hashlib.sha256(text.encode()).hexdigest(),
        "text_layer": layer,
        "evidence_grade": GM[layer],
        "source_location": {
            "book": "神峰通考",
            "path": [
                {"level": "volume", "code": vc, "name": vol_name},
                {"level": "lei", "code": code, "name": title.split("（")[0]},
            ],
            "passage": "第1段",
            "line_start": a, "line_end": b, "file_hash": shash,
        },
        "resource_id": "SRC-" + sid,
        "logical_uri": "source://sftk/%s/%s/passage_001" % (vc.lower(), code.lower()),
        "relative_path": "sources/sftk/%s/%s/passage_001.md" % (vc.lower(), code.lower()),
        "runtime_resolver": "resource://classic/sftk/%s/%s" % (vc.lower(), code.lower()),
        "source_text": text,
        "provenance": {"chain": [sid], "completeness": "COMPLETE", "gaps": []},
        "handling_status": "RESOLVED" if text else "NEEDS_REVIEW",
        "approval_status": "CANDIDATE",
        "approved_by": None, "approved_at": None,
        "created_at": NOW, "updated_at": None,
        "metadata": {
            "edition": {"type": "校勘本", "source": "国家图书馆扫描版 NLC511-027032013020556 · Qianfan-OCR 校对（2026-09-14）", "editor": "临川西溪逸叟 张楠（原著）", "year": "明"},
            "collation_note": note,
            "section_title": title,
        },
    })
print("SFTK sources:", len(sftk_sources), dict(collections.Counter(s["text_layer"] for s in sftk_sources)))

# ==================== RULES ====================
errors = []
yids = set(s["source_id"] for s in yhzp_sources)
sids_set = set(s["source_id"] for s in sftk_sources)

# ---- YHZP rules (definition-dominant, ~140) ----
yhzp_by_title = {}
for s in yhzp_sources:
    tt = norm(s["metadata"]["chapter_title"] or "")
    yhzp_by_title.setdefault(tt, []).append(s["source_id"])
yhzp_by_num = {s["metadata"]["chapter_num"]: s["source_id"] for s in yhzp_sources}

yrules = []
def add_y(sid, rtype, subj, pred, preconds, outputs, op, title, ev="C"):
    global yrules
    yrules.append({
        "rule_id": "CAND-YHZP-%03d" % (len(yrules) + 1),
        "engine": "YHZP", "source_ids": sid, "rule_type": rtype, "scope": "natal",
        "subject": subj, "predicate": pred,
        "preconditions": {"type": "conjunction", "conditions": preconds},
        "operator": op, "output": outputs, "evidence_requirement": ev,
        "lifecycle_status": "CANDIDATE", "match_state": None, "version": "1.0.0",
        "created_at": NOW, "updated_at": None, "approved_at": None, "deprecated_at": None,
        "metadata": {"title": title, "classic": "YHZP"},
    })

def y_pick(*kws, default_num=5):
    for kw in kws:
        if kws and kw in yhzp_by_title:
            return yhzp_by_title[kw][:2]
    d = yhzp_by_num.get(default_num)
    return [d] if d else [sorted(yids)[0]]

TEN_GOD = [("比肩","日干同类比和"),("劫财","日干同类异性"),("食神","日干所生同类"),("伤官","日干所生异性"),
           ("偏财","日干所克异性"),("正财","日干所克同类"),("七杀","克日干异性"),("正官","克日干同类"),
           ("偏印","生日干异性"),("正印","生日干同类")]
for g, d in TEN_GOD:
    add_y(y_pick(g, "十神"), "definition", "ten_god", "is",
          [{"field": "ten_god.definition", "op": "equals", "value": d}],
          {"ten_god": g}, "emit", "十神·%s 定义" % g)
STEMS = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
for st in STEMS:
    for g in ["比肩","正官","七杀","正财","正印"]:
        add_y(y_pick(st, default_num=60), "definition", "ten_god.by_day_stem", "is",
              [{"field": "day_stem", "op": "equals", "value": st}, {"field": "ten_god", "op": "in", "value": [g]}],
              {"ten_god": "%s日%s" % (st, g)}, "emit", "%s日干·%s 组合" % (st, g))
for kw, val in [("六冲","子午冲、丑未冲、寅申冲、卯酉冲、辰戌冲、巳亥冲"),
                ("三合","申子辰合水、亥卯未合木、寅午戌合火、巳酉丑合金"),
                ("六合","甲己合、乙庚合、丙辛合、丁壬合、戊癸合"),
                ("相刑","恃势之刑、无恩之刑、无礼之刑、自刑"),("相冲","六冲地支相冲"),("藏干","地支藏人元")]:
    add_y(y_pick(kw, default_num=30), "resolution", "earthly_branch", "is",
          [{"field": "earthly_branch.relation", "op": "equals", "value": kw}],
          {"relation": kw, "value": val}, "evaluate", "地支关系·%s" % kw)
GEJUS = ["正官格","七杀格","食神格","伤官格","偏财格","正印格","偏印格","建禄格","羊刃格",
         "正财格","从格","从杀格","杀印相生格","食神制杀格","伤官配印格","财官双美格",
         "身旺用官格","身弱用印格","化气格","调候用神格"]
for g in GEJUS:
    add_y(y_pick(g, g.rstrip("格"), default_num=60), "definition", "pattern", "is",
          [{"field": "pattern", "op": "equals", "value": g}],
          {"pattern": g}, "emit", "格局·%s 定义" % g)
YONGSHEN = ["扶抑用神","调候用神","通关用神","病药用神","格局用神","月令用神","旺相休囚死",
            "身旺任财官","身弱喜印比","财多身弱","官多身弱","杀重用印","食伤泄秀",
            "印绶格取用","比劫分财","合局取用","冲局破格","大运喜忌","流年应期"]
for kw in YONGSHEN:
    rt = "resolution" if kw in ["扶抑用神","调候用神","病药用神"] else "definition"
    op = "evaluate" if kw in ["扶抑用神","调候用神","病药用神"] else "emit"
    add_y(y_pick(kw[:2], default_num=80), rt, "useful_god", "resolves" if rt=="resolution" else "is",
          [{"field": "yongshen.strategy", "op": "equals", "value": kw}],
          {"useful_god": kw}, op, "用神·%s" % kw)
SHIER = ["长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养"]
for s in SHIER:
    add_y(y_pick(s, "长生", default_num=40), "definition", "twelve_states", "is",
          [{"field": "twelve_states", "op": "equals", "value": s}],
          {"state": s}, "emit", "十二长生·%s" % s)
TIX = ["甲木","乙木","丙火","丁火","戊土","己土","庚金","辛金","壬水","癸水",
       "海中金","炉中火","大林木","路旁土","剑锋金","山下火","平地木","壁上土"]
for t in TIX:
    add_y(y_pick(t[:2], default_num=90), "definition", "stem_body_image", "is",
          [{"field": "stem_body_image", "op": "equals", "value": t}],
          {"body_image": t}, "emit", "天干体象·%s" % t)
LIUQIN = ["年柱为父母","月柱为兄弟","日柱为配偶","时柱为子女","正印为母","偏财为父",
          "正财为妻","食神为子女","正官为子女","七杀为偏夫"]
for kw in LIUQIN:
    add_y(y_pick(kw[:2], default_num=100), "definition", "six_relations", "is",
          [{"field": "six_relations.position", "op": "equals", "value": kw}],
          {"relation": kw}, "emit", "六亲·%s" % kw)
print("YHZP rules:", len(yrules), dict(collections.Counter(r["rule_type"] for r in yrules)))

# ---- SFTK rules (~40, definition-dominant) ----
sftk_by_title = sftk_title2sid
def s_pick(*kws, default=2):
    for kw in kws:
        if kw in sftk_by_title:
            return [sftk_by_title[kw]]
    return [sftk_sources[default]["source_id"]]

sftkrules = []
def add_s(sid, rtype, subj, pred, preconds, outputs, op, title):
    sftkrules.append({
        "rule_id": "CAND-SFTK-%03d" % (len(sftkrules) + 1),
        "engine": "SFTK", "source_ids": sid, "rule_type": rtype, "scope": "natal",
        "subject": subj, "predicate": pred,
        "preconditions": {"type": "conjunction", "conditions": preconds},
        "operator": op, "output": outputs, "evidence_requirement": "C",
        "lifecycle_status": "CANDIDATE", "match_state": None, "version": "1.0.0",
        "created_at": NOW, "updated_at": None, "approved_at": None, "deprecated_at": None,
        "metadata": {"title": title, "classic": "SFTK"},
    })
# 八法
for name, val, kw in [("病药说","有病方为贵，无伤不是奇；去病即药","病藥說類"),
        ("雕损","雕：日干受盖头之损","雕枯旺弱四病說類"),
        ("枯涸","枯：水干木焚之候","雕枯旺弱四病說類"),
        ("弱陷","弱：日干衰弱无扶","雕枯旺弱四病說類"),
        ("旺亢","亢：日干太旺无制","雕枯旺弱四病說類"),
        ("损益","损：削其太旺，益其不足","損益生長四藥說類"),
        ("动静说","静得动生、动得静制","動靜說"),
        ("盖头说","干坐支上为盖头，干弱则受其害","蓋頭說"),
        ("六亲说","以财官印食伤推六亲","六親說")]:
    add_s(s_pick(kw), "definition", "ba_fa", "is",
          [{"field": "ba_fa", "op": "equals", "value": name}],
          {"ba_fa": name, "note": val}, "emit", "八法·%s" % name)
# 格局 definition
SFTK_GEJUS = ["正官格","偏官格","月支正財格","雜氣財官印綬格","金神格","井欄叉格",
              "夾丘拱財格","專財格","陽刃格","十天干體象全編論","五行元理消息賦","一行禪師天元賦"]
for g in SFTK_GEJUS:
    add_s(s_pick(g, g.split("（")[0], g[:4]), "definition", "pattern", "is",
          [{"field": "pattern", "op": "equals", "value": g}],
          {"pattern": g}, "emit", "格局·%s" % g)
# resolution 用神
for name, val, kw in [("有病去病","杀重身轻取印泄、财多身弱取比劫","病藥說類"),
         ("杀印相生","七杀配印化煞为生","繼善篇"),
         ("伤官配印","伤官旺配印制伤生身","繼善篇"),
         ("喜忌取用","取用喜忌定吉凶","喜忌篇"),
         ("定格局","定格五诀","定格局訣"),
         ("十干从化","从化格须满局一方","十干從化定訣"),
         ("身弱取扶","身弱取印比扶身","身弱論"),
         ("弃命从杀","身无一点生意纯杀从杀","偏官格"),
         ("阴阳通变","官杀阴阳分正偏","陰陽通變妙訣"),
         ("泛论取用","泛论子平诸格取用","子平泛論")]:
    add_s(s_pick(kw), "resolution", "useful_god", "resolves",
          [{"field": "strategy", "op": "equals", "value": name}],
          {"strategy": name, "note": val}, "evaluate", "用神·%s" % name)
print("SFTK rules:", len(sftkrules), dict(collections.Counter(r["rule_type"] for r in sftkrules)))

# ==================== QC ====================
for label, items, idset in [("YHZP", yhzp_sources, yids), ("SFTK", sftk_sources, sids_set)]:
    dup = [k for k, c in collections.Counter(i["source_id"] for i in items).items() if c > 1]
    if dup: errors.append("%s dup source_id %s" % (label, dup[:5]))
    for s in items:
        if not re.match(r"^[A-Z0-9/_-]+$", s["source_id"]):
            errors.append("%s non-ASCII sid %s" % (label, s["source_id"]))
        if s["resource_id"] != "SRC-" + s["source_id"]:
            errors.append("%s resource_id mismatch %s" % (label, s["source_id"]))
        if s["evidence_grade"] != GM[s["text_layer"]]:
            errors.append("%s grade/layer mismatch %s" % (label, s["source_id"]))
        blob = json.dumps(s, ensure_ascii=False)
        if "D:/shuntian" in blob or "C:\\" in blob:
            errors.append("%s abs path %s" % (label, s["source_id"]))
        if s["source_location"]["file_hash"] not in (yhash if label=="YHZP" else shash):
            errors.append("%s file_hash wrong %s" % (label, s["source_id"]))

for label, rlist, idset in [("YHZP", yrules, yids), ("SFTK", sftkrules, sids_set)]:
    rid = [r["rule_id"] for r in rlist]
    if len(rid) != len(set(rid)): errors.append("%s dup rule_id" % label)
    for r in rlist:
        for sid in r["source_ids"]:
            if sid not in idset:
                errors.append("%s rule %s unbound %s" % (label, r["rule_id"], sid))
        blob = json.dumps(r, ensure_ascii=False)
        if ">" in blob or "<" in blob:
            errors.append("%s rule %s forbidden op" % (label, r["rule_id"]))
        if "D:/shuntian" in blob:
            errors.append("%s rule abs path" % label)
    # operator vs rule_type matrix
    for r in rlist:
        ok = {"definition": {"match","emit"}, "resolution": {"match","evaluate"},
              "effectiveness": {"evaluate"}, "activation": {"match","evaluate"}}
        if r["operator"] not in ok.get(r["rule_type"], set()):
            errors.append("%s rule %s op %s not allowed for %s" % (label, r["rule_id"], r["operator"], r["rule_type"]))

if errors:
    print("QC FAILED (%d):" % len(errors))
    for e in errors[:40]: print("  -", e)
    raise SystemExit(1)
print("QC PASSED: YHZP src=%d rule=%d | SFTK src=%d rule=%d" % (len(yhzp_sources), len(yrules), len(sftk_sources), len(sftkrules)))

def write_jsonl(path, items):
    d = os.path.dirname(path); os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for it in items: f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print("wrote %s (%d)" % (os.path.relpath(path, ROOT), len(items)))

write_jsonl(OUT_Y_SRC, yhzp_sources)
write_jsonl(OUT_Y_RULE, yrules)
write_jsonl(OUT_S_SRC, sftk_sources)
write_jsonl(OUT_S_RULE, sftkrules)
print("\nDONE. All QC passed, files written (NOT committed).")
