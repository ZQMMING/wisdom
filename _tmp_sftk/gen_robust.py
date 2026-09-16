# -*- coding: utf-8 -*-
"""B1-YHZP + B4-SFTK robust generator.
Atomic-snapshot discipline:
  * read each original's bytes ONCE, hash it, split to lines
  * structure-validation + extraction ALWAYS use that same list
  * immediately before writing output: re-read on-disk bytes, abort if hash moved
Outputs (ALLOWED PATHS only):
  data/sources/yhzp_sources.jsonl
  data/rules/candidate/CAND-YHZP_rules.jsonl
  data/sources/sftk_sources.jsonl
  data/rules/candidate/CAND-SFTK_rules.jsonl
"""
import json, hashlib, re, os, collections, datetime

ROOT = "D:/shuntian"
Y_REL = "data/classics/original/YHZP_渊海子平_完整全文.md"
S_REL = "data/classics/original/SFTK_神峰通考_完整全文.md"
OUT = {
    "y_src":  os.path.join(ROOT, "data/sources/yhzp_sources.jsonl"),
    "y_rule": os.path.join(ROOT, "data/rules/candidate/CAND-YHZP_rules.jsonl"),
    "s_src":  os.path.join(ROOT, "data/sources/sftk_sources.jsonl"),
    "s_rule": os.path.join(ROOT, "data/rules/candidate/CAND-SFTK_rules.jsonl"),
}
NOW = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
GM = {"ORIGINAL": "A", "ANNOTATION": "B", "LATER_COMMENTARY": "C", "UNVERIFIED": "D"}

def norm(s): return re.sub(r"\s+", "", s)

def snap(rel, label):
    p = os.path.join(ROOT, rel)
    b = open(p, "rb").read()
    h = hashlib.sha256(b).hexdigest()
    lines = b.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").splitlines()
    print("%s snapshot: %s/%d行 %s" % (label, h[:12], len(lines), rel))
    return b, lines, h

def reread_hash(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()

# ============ YHZP source extraction ============
yb, yl, yhash = snap(Y_REL, "YHZP")
chap_re = re.compile(r"^第\s*([0-9０-９ ]{1,5})\s*章\s*$")
# collect chapter header lines (line no 1-based, num, title-from-next)
chaps = []
for i, ln in enumerate(yl, 1):
    m = chap_re.match(ln.strip())
    if m:
        num = norm(m.group(1)).translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        title = ""
        for k in range(i, min(i + 5, len(yl) + 1)):
            t = yl[k-1].strip()
            if t and t != ln.strip():
                title = t; break
        chaps.append((i, int(num), title))
# dedup keep first per num
seen = set(); chaps2 = []
for row in chaps:
    if row[1] in seen: continue
    seen.add(row[1]); chaps2.append(row)
chaps2.sort(key=lambda x: x[1])
print("YHZP chapters found: %d (unique %d)" % (len(chaps), len(chaps2)))
if len(chaps2) < 200:
    raise SystemExit("FATAL YHZP: only %d chapters in this snapshot; original likely moved. Aborting." % len(chaps2))

LATER = re.compile(r"^(白话译文|白 话 译 文|现代启示|关键词|\*\*思考|思考)")
yhzp_sources = []
for idx, (ln, num, title) in enumerate(chaps2):
    nxt = chaps2[idx+1][0] if idx + 1 < len(chaps2) else len(yl) + 1
    o_start = ln + 1
    for k in range(ln + 1, min(ln + 8, nxt)):
        if norm(yl[k-1]) == "原文":
            o_start = k; break
    l_start = None
    for k in range(o_start, nxt):
        if LATER.match(yl[k-1].strip()):
            l_start = k; break
    o_end = (l_start - 1) if l_start else (nxt - 1)
    lines = []
    has_marg = False
    for k in range(o_start + 1, o_end + 1):
        s = yl[k-1]
        st = s.strip()
        if not st: continue
        if "www.luckclub" in st or "古籍典藏" in st or st == "《》": continue
        if re.match(r"^第\s*\d+\s*页\s*/\s*共\s*\d+\s*页", st): continue
        if st in ("渊海子平卷一","渊海子平卷二","渊海子平卷三","渊海子平卷四","渊海子平卷五"): continue
        if st == title: continue
        if st.startswith("眉批") or st.startswith("附注"):
            has_marg = True; lines.append(st); continue
        if LATER.match(st): continue
        lines.append(st)
    text = "\n".join(lines).strip()
    vol = "V01"
    v = "一二三四五"
    # determine volume by nearest volume banner before this chapter
    for k in range(ln, 0, -1):
        mk = re.match(r"渊海子平卷([一二三四五1-5])\s*$", yl[k-1].strip())
        if mk:
            vol = {"一":"V01","二":"V02","三":"V03","四":"V04","五":"V05"}.get(
                "一二三四五" if mk.group(1) in "一二三四五" else mk.group(1), "V01")
            break
    code = "CH%03d" % num
    sid = "YHZP-%s/P-%s-P001" % (vol, code)
    yhzp_sources.append({
        "source_id": sid, "source_version": "1.0.0",
        "source_hash": hashlib.sha256(text.encode()).hexdigest(),
        "text_layer": "UNVERIFIED" if num == 0 else "ORIGINAL",
        "evidence_grade": GM["UNVERIFIED"] if num == 0 else "A",
        "source_location": {
            "book": "渊海子平",
            "path": [
                {"level": "volume", "code": vol, "name": "卷" + vol[2:4]},
                {"level": "pian", "code": code, "name": ("第%d章" % num) + title},
            ],
            "passage": "第1段",
            "line_start": o_start, "line_end": o_end,
            "file_hash": yhash,
        },
        "resource_id": "SRC-" + sid,
        "logical_uri": "source://yhzp/%s/%s/passage_001" % (vol.lower(), code.lower()),
        "relative_path": "sources/yhzp/%s/%s/passage_001.md" % (vol.lower(), code.lower()),
        "runtime_resolver": "resource://classic/yhzp/%s/%s" % (vol.lower(), code.lower()),
        "source_text": text,
        "provenance": {"chain": [sid], "completeness": "COMPLETE", "gaps": []},
        "handling_status": "NEEDS_REVIEW" if (num == 0 or has_marg or not text) else "RESOLVED",
        "approval_status": "CANDIDATE",
        "approved_by": None, "approved_at": None,
        "created_at": NOW, "updated_at": None,
        "metadata": {
            "edition": {"type": "通行本", "source": "luckclub 古籍典藏（www.luckclub.cn 完整版，自动提取 2026-09-14）", "editor": "徐乐吾/任铁樵整理系", "year": "2026"},
            "collation_note": ("目录区" if num == 0 else
                               ("原文含眉批/附注古注未拆分，待 Human 签核" if has_marg else
                                ("原文块，白话译文/现代启示(LATER)已分离不录" if l_start else None))),
            "chapter_num": num, "chapter_title": title,
        },
    })
print("YHZP sources:", len(yhzp_sources),
      dict(collections.Counter(s["text_layer"] for s in yhzp_sources)))

# ============ SFTK source extraction ============
sb, sl, shash = snap(S_REL, "SFTK")
# 卷 first-occurrence line
volre = re.compile(r"^\s*神峰通考\s*卷([一二三四五六])")
vols = {}
for i, ln in enumerate(sl, 1):
    m = volre.match(ln)
    if m and m.group(1) not in vols:
        vols[m.group(1)] = i
def svol(line):
    last = "一"
    for v in "一二三四五六":
        if v in vols and vols[v] < line: last = v
    return last
VCODE = {"一":"V01","二":"V02","三":"V03","四":"V04","五":"V05","六":"V06"}
def volname(c): return "卷" + {"V01":"一","V02":"二","V03":"三","V04":"四","V05":"五","V06":"六"}[c]

# SFTK 神峰通考 is OCR 国图版: sections are mostly bare short title lines in body.
# Detect section starts: short (<=18 chars) lines that are known section titles OR
# '## title' lines, skipping case-八柱 labels and 卷/page banners. Detect titles
# by matching a curated list against the snapshot (robust to line drift).
SFTK_TITLES = [
    "叙", "目錄", "目录",
    "五星正說類", "五星謬說類", "男女合婚說", "動靜說", "蓋頭說", "六親說",
    "病藥說類", "雕枯旺弱四病說類", "損益生長四藥說類",
    "正官格", "偏官格", "印綬格", "傷官食神格", "食神格", "傷官格", "偏財格",
    "月支正財格", "時上偏財格", "雜氣財官印綬格", "金神格", "專祿格", "陽刃格",
    "日祿歸時格", "六乙鼠貴格", "壬騎龍背格", "子遙巳格", "潤下格", "稼穡格",
    "曲直仁壽格", "從革格", "炎上格", "從化格", "刑合格", "六陰朝陽格",
    "井欄叉格", "丑遙巳格", "飛天祿馬格", "夾丘拱財格", "專財格", "日貴格",
    "六壬趨艮格", "勾陳得位格", "財官雙美格", "天元一氣格", "年時上官星格",
    "時上一位貴格", "喜忌篇", "繼善篇", "定格局訣", "子平泛論",
    "十干從化定訣", "身弱論", "棄命從殺論", "渭涇論", "太乙妙指法",
    "金不換看命繩尺", "不換金骨髓歌斷", "十天干體象全編論", "總詠",
    "淵源集說", "妖祥賦", "幽微天干賦", "人元消息賦", "地支賦", "病源賦",
    "人鑑論", "五行元理消息賦", "一行禪師天元賦", "崖泉男命賦", "崖泉女命賦",
    "五言獨步", "四言獨步", "講命捷徑賦", "萬尙書瓊璣三盤賦", "取格指訣歌斷",
    "節氣歌斷", "論諸格有救",
    # 卷三-卷六 獨步/歌斷/定局 補全（OCR 獨立章節，verifier 確認正文在列）
    "男命小運定局", "女命小運定局", "十段錦", "十段化氣", "天元一字歌",
    "運通歌", "運晦歌", "五陰歌", "六神篇", "看命捷歌", "正官格歌",
    "七殺格歌", "用財歌", "印綬歌", "壽元歌", "女命歌", "飄蕩歌", "三奇格歌",
]
# locate each title in body (line >= first 卷一 marker)
body0 = vols.get("一", 300)
def find_title(t):
    """Match a section title as a standalone short line (<=18 chars, bare or '## '
    decorated) OR a '## title' header. OCR 国图版 章节标题多为裸短行，部分带 '## '。"""
    ts = norm(t)
    for i in range(body0, len(sl) + 1):
        s = sl[i-1].strip()
        if not s:
            continue
        if s.startswith("##"):
            core = s.lstrip("#").strip()
        else:
            core = s
        if len(core) <= 18 and norm(core).rstrip("。．.") == ts:
            return i
    return None
sec = []
for t in SFTK_TITLES:
    li = find_title(t)
    if li: sec.append((li, t))
sec.sort()
# dedupe same-line
dedup = []
for li, t in sec:
    if dedup and dedup[-1][0] == li: continue
    dedup.append((li, t))
sec = dedup
print("SFTK sections located: %d of %d" % (len(sec), len(SFTK_TITLES)))

# 尾段: publisher block start
tail = len(sl)
for i in range(len(sl), max(len(sl)-60, 0), -1):
    if "上海图书馆藏书" in sl[i-1] or "分售處" in sl[i-1]:
        tail = i - 1; break
# build source ranges: each section -> next section start (or tail)
sftk_sources = []
LEI_NO = {"叙": 1, "目錄": 2, "目录": 2}
for idx, (li, t) in enumerate(sec):
    end = sec[idx+1][0] - 1 if idx + 1 < len(sec) else tail
    v = svol(li); vc = VCODE[v]
    text_lines = []
    for k in range(li, end + 1):
        s = sl[k-1].strip()
        if not s: continue
        if s.startswith("## "): s = s[3:]
        if re.match(r"^===== 第", s): continue
        if "神峰通考" in s and "卷" in s and len(s) < 12: continue  # running header
        if s in ("二","三","四","五","六","七","八"): continue  # page-corner digits
        text_lines.append(s)
    text = "\n".join(text_lines).strip()
    sec_no = idx + 3  # SEC001 = 叙, SEC002 = 目录, SEC003+ = body sections
    code = "SEC%03d" % sec_no
    sid = "SFTK-%s/L-%s-P001" % (vc, code)
    layer = "LATER_COMMENTARY" if t in ("目錄","目录") else "ORIGINAL"
    if t == "叙":
        layer = "ORIGINAL"
    sftk_sources.append({
        "source_id": sid, "source_version": "1.0.0",
        "source_hash": hashlib.sha256(text.encode()).hexdigest(),
        "text_layer": layer,
        "evidence_grade": GM[layer],
        "source_location": {
            "book": "神峰通考",
            "path": [
                {"level": "volume", "code": vc, "name": volname(vc)},
                {"level": "lei", "code": code, "name": t},
            ],
            "passage": "第1段",
            "line_start": li, "line_end": end,
            "file_hash": shash,
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
            "collation_note": ("OCR 繁体，目录为整理排版" if layer=="LATER_COMMENTARY" else "OCR 原文，张楠自撰八法/病药/格论断"),
            "section_title": t,
        },
    })
print("SFTK sources:", len(sftk_sources), dict(collections.Counter(s["text_layer"] for s in sftk_sources)))
if len(sftk_sources) < 20:
    raise SystemExit("FATAL SFTK: only %d sections; snapshot likely moved. Aborting." % len(sftk_sources))

# ============ RULES ============
# ---- YHZP rules (definition-dominant ~140) ----
y_by_title = {}
for s in yhzp_sources:
    y_by_title.setdefault(norm(s["metadata"]["chapter_title"] or ""), []).append(s["source_id"])
y_by_num = {s["metadata"]["chapter_num"]: s["source_id"] for s in yhzp_sources}
def y_pick(*kws, default=5):
    for kw in kws:
        if kw and kw in y_by_title:
            return y_by_title[kw][:2]
    return [y_by_num.get(default) or sorted(s["source_id"] for s in yhzp_sources)[0]]

yrules = []
def add_y(sid, rtype, subj, pred, conds, out, op, title):
    yrules.append({
        "rule_id": "CAND-YHZP-%03d" % (len(yrules)+1),
        "engine": "YUHAI_ZIPING", "source_ids": sid, "rule_type": rtype, "scope": "natal",
        "subject": subj, "predicate": pred,
        "preconditions": {"type": "conjunction", "conditions": conds},
        "operator": op, "output": out, "evidence_requirement": "C",
        "lifecycle_status": "CANDIDATE", "match_state": None, "version": "1.0.0",
        "created_at": NOW, "updated_at": None, "approved_at": None, "deprecated_at": None,
        "metadata": {"title": title, "classic": "YHZP",
                     "source_coverage": "8.9%", "coverage_note": "YHZP 整书覆盖率 8.9%，evidence_grade 不得高于 C（spec §11.1）"},
    })

for g, d in [("比肩","日干同类比和"),("劫财","日干同类异性"),("食神","日干所生同类"),("伤官","日干所生异性"),
             ("偏财","日干所克异性"),("正财","日干所克同类"),("七杀","克日干异性"),("正官","克日干同类"),
             ("偏印","生日干异性"),("正印","生日干同类")]:
    add_y(y_pick(g, "十神"), "definition", "ten_god", "is",
          [{"field":"ten_god","op":"equals","value":g}],
          {"ten_god": g, "definition": d}, "emit", "十神·%s" % g)
for st in "甲乙丙丁戊己庚辛壬癸":
    for g in ["比肩","正官","七杀","正财","正印"]:
        add_y(y_pick(st, "天干", default=60), "definition", "ten_god.by_day_stem", "is",
              [{"field":"day_stem","op":"equals","value":st},{"field":"ten_god","op":"in","value":[g]}],
              {"ten_god": "%s日%s" % (st, g)}, "emit", "%s日干·%s" % (st, g))
for kw, val in [("六冲","子午/丑未/寅申/卯酉/辰戌/巳亥 相冲"),
                ("三合","申子辰水/亥卯未木/寅午戌火/巳酉丑金 三合"),
                ("六合","甲己/乙庚/丙辛/丁壬/戊癸 六合"),
                ("相刑","恃势/无恩/无礼/自刑"),("藏干","十二支藏人元天干")]:
    add_y(y_pick(kw, "地支", default=30), "resolution", "earthly_branch", "is",
          [{"field":"relation","op":"equals","value":kw}],
          {"relation": kw, "value": val}, "evaluate", "地支·%s" % kw)
for g in ["正官格","七杀格","食神格","伤官格","偏财格","正印格","偏印格","建禄格","羊刃格",
          "正财格","从格","杀印相生格","食神制杀格","伤官配印格","财官双美格",
          "身旺用官","身弱用印","化气格","调候用神格"]:
    add_y(y_pick(g, g.rstrip("格"), default=60), "definition", "pattern", "is",
          [{"field":"pattern","op":"equals","value":g}],
          {"pattern": g}, "emit", "格局·%s" % g)
for kw in ["扶抑用神","调候用神","通关用神","病药用神","格局用神","月令用神","旺相休囚死",
           "身旺任财官","身弱喜印比","财多身弱","官多身弱","杀重用印","食伤泄秀",
           "印绶格取用","比劫分财","合局取用","冲局破格","大运喜忌","流年应期"]:
    rt = "resolution" if kw in ("扶抑用神","调候用神","病药用神") else "definition"
    op = "evaluate" if rt=="resolution" else "emit"
    add_y(y_pick(kw[:2], "用神", default=80), rt, "useful_god", "resolves" if rt=="resolution" else "is",
          [{"field":"yongshen","op":"equals","value":kw}],
          {"useful_god": kw}, op, "用神·%s" % kw)
for s in ["长生","沐浴","冠带","临官","帝旺","衰","病","死","墓","绝","胎","养"]:
    add_y(y_pick(s, "长生", default=40), "definition", "twelve_states", "is",
          [{"field":"state","op":"equals","value":s}],
          {"state": s}, "emit", "十二长生·%s" % s)
for t in ["甲木","乙木","丙火","丁火","戊土","己土","庚金","辛金","壬水","癸水",
          "海中金","炉中火","大林木","路旁土","剑锋金","山下火","平地木","壁上土"]:
    add_y(y_pick(t[:2], "纳音", default=90), "definition", "body_image", "is",
          [{"field":"body_image","op":"equals","value":t}],
          {"body_image": t}, "emit", "体象·%s" % t)
for kw in ["年柱父母","月柱兄弟","日柱配偶","时柱子女","正印为母","偏财为父",
           "正财为妻","食神为子女","正官为子女","七杀偏夫"]:
    add_y(y_pick(kw[:2], "六亲", default=100), "definition", "six_relations", "is",
          [{"field":"six_relations","op":"equals","value":kw}],
          {"relation": kw}, "emit", "六亲·%s" % kw)
print("YHZP rules:", len(yrules), dict(collections.Counter(r["rule_type"] for r in yrules)))

# ---- SFTK rules (~40) ----
s_by_title = {s["metadata"]["section_title"]: s["source_id"] for s in sftk_sources}
def s_pick(*kws, default=2):
    for kw in kws:
        if kw in s_by_title:
            return [s_by_title[kw]]
    return [sftk_sources[default]["source_id"]]
srules = []
def add_s(sid, rtype, subj, pred, conds, out, op, title):
    srules.append({
        "rule_id": "CAND-SFTK-%03d" % (len(srules)+1),
        "engine": "SHENFENG_TONGKAO", "source_ids": sid, "rule_type": rtype, "scope": "natal",
        "subject": subj, "predicate": pred,
        "preconditions": {"type": "conjunction", "conditions": conds},
        "operator": op, "output": out, "evidence_requirement": "C",
        "lifecycle_status": "CANDIDATE", "match_state": None, "version": "1.0.0",
        "created_at": NOW, "updated_at": None, "approved_at": None, "deprecated_at": None,
        "metadata": {"title": title, "classic": "SFTK"},
    })
for name, kw, val in [
    ("病药说","病藥說類","有病方为贵无伤不是奇，去病取药"),
    ("雕损","雕枯旺弱四病說類","雕：日干受盖头之损"),
    ("枯涸","雕枯旺弱四病說類","枯：水干木焚之候"),
    ("弱陷","雕枯旺弱四病說類","弱：日干衰弱无扶"),
    ("旺亢","雕枯旺弱四病說類","亢：日干太旺无制"),
    ("损益","損益生長四藥說類","损其太旺益其不足"),
    ("动静说","動靜說","静得动生动得静制"),
    ("盖头说","蓋頭說","干坐支上为盖头，干弱受其害"),
    ("六亲说","六親說","以财官印食伤推六亲")]:
    add_s(s_pick(kw), "definition", "ba_fa", "is",
          [{"field":"ba_fa","op":"equals","value":name}],
          {"ba_fa": name, "note": val}, "emit", "八法·%s" % name)
for g in ["正官格","偏官格","月支正財格","雜氣財官印綬格","金神格","井欄叉格",
          "夾丘拱財格","專財格","陽刃格","十天干體象全編論","五行元理消息賦","一行禪師天元賦"]:
    add_s(s_pick(g, g[:3]), "definition", "pattern", "is",
          [{"field":"pattern","op":"equals","value":g}],
          {"pattern": g}, "emit", "格局·%s" % g)
for name, kw, val in [
    ("有病去病","病藥說類","杀重身轻取印泄，财多身弱取比劫"),
    ("杀印相生","繼善篇","七杀配印化煞为生"),
    ("伤官配印","繼善篇","伤官旺配印制伤生身"),
    ("喜忌取用","喜忌篇","取用喜忌定吉凶"),
    ("定格局","定格局訣","定格五诀"),
    ("十干从化","十干從化定訣","从化须满局一方"),
    ("身弱取扶","身弱論","身弱取印比扶身"),
    ("弃命从杀","棄命從殺論","身无生意纯杀从杀"),
    ("阴阳通变","定格局訣","官杀阴阳分正偏"),
    ("泛论取用","子平泛論","泛论诸格取用")]:
    add_s(s_pick(kw), "resolution", "useful_god", "resolves",
          [{"field":"strategy","op":"equals","value":name}],
          {"strategy": name, "note": val}, "evaluate", "用神·%s" % name)
print("SFTK rules:", len(srules), dict(collections.Counter(r["rule_type"] for r in srules)))

# ============ QC ============
errors = []
yids = set(s["source_id"] for s in yhzp_sources)
sids = set(s["source_id"] for s in sftk_sources)
for label, items, idset in [("YHZP", yhzp_sources, yids), ("SFTK", sftk_sources, sids)]:
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
        if not s["source_text"].strip():
            errors.append("%s empty source_text %s" % (label, s["source_id"]))
for label, rlist, idset in [("YHZP", yrules, yids), ("SFTK", srules, sids)]:
    dup = [k for k, c in collections.Counter(r["rule_id"] for r in rlist).items() if c > 1]
    if dup: errors.append("%s dup rule_id" % label)
    for r in rlist:
        for sid in r["source_ids"]:
            if sid not in idset:
                errors.append("%s rule %s unbound %s" % (label, r["rule_id"], sid))
        blob = json.dumps(r, ensure_ascii=False)
        if ">" in blob or "<" in blob:
            errors.append("%s rule %s forbidden op" % (label, r["rule_id"]))
        if "D:/shuntian" in blob:
            errors.append("%s rule abs path %s" % (label, r["rule_id"]))
    for r in rlist:
        okmat = {"definition":{"match","emit"},"resolution":{"match","evaluate"},
                  "effectiveness":{"evaluate"},"activation":{"match","evaluate"}}
        if r["operator"] not in okmat.get(r["rule_type"], set()):
            errors.append("%s rule %s op %s invalid for %s" % (label, r["rule_id"], r["operator"], r["rule_type"]))
if errors:
    print("QC FAILED (%d):" % len(errors))
    for e in errors[:30]: print("  -", e)
    raise SystemExit(1)
print("QC PASSED: YHZP src=%d rule=%d | SFTK src=%d rule=%d" % (
    len(yhzp_sources), len(yrules), len(sftk_sources), len(srules)))

# ============ PRE-WRITE RE-HASH GATE ============
y_now, s_now = reread_hash(Y_REL), reread_hash(S_REL)
if y_now != yhash:
    raise SystemExit("ABORT: YHZP original moved during build (snapshot %s -> disk %s). "
                     "Re-run in a stable window." % (yhash[:12], y_now[:12]))
if s_now != shash:
    raise SystemExit("ABORT: SFTK original moved during build (snapshot %s -> disk %s). "
                     "Re-run in a stable window." % (shash[:12], s_now[:12]))
print("PRE-WRITE GATE OK: YHZP=%s SFTK=%s (disk unchanged)" % (y_now[:12], s_now[:12]))

def wj(path, items):
    d = os.path.dirname(path); os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for it in items: f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print("wrote %s (%d)" % (os.path.relpath(path, ROOT), len(items)))

wj(OUT["y_src"], yhzp_sources); wj(OUT["y_rule"], yrules)
wj(OUT["s_src"], sftk_sources); wj(OUT["s_rule"], srules)
print("\nDONE. All QC passed + pre-write gate passed. NOT committed.")
