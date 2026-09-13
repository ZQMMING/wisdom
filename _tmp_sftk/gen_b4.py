# -*- coding: utf-8 -*-
"""B4-SFTK generator (v2, stability-gated). Outputs allowed paths only."""
import json, hashlib, re, os, time, collections

ROOT = "D:/shuntian"
SRC = os.path.join(ROOT, "data/classics/original/SFTK_神峰通考_完整全文.md")
OUT_SRC = os.path.join(ROOT, "data/sources/sftk_sources.jsonl")
OUT_RULE = os.path.join(ROOT, "data/rules/candidate/CAND-SFTK_rules.jsonl")
CREATED = "2026-09-14T00:00:00Z"

def norm(s):
    return re.sub(r"\s+", "", s)

# ---- 稳定性闸门 ----
def fh():
    return hashlib.sha256(open(SRC, encoding="utf-8").read().encode("utf-8")).hexdigest()
a, b = fh(), (time.sleep(4), fh())[1]
assert a == b, "BLOCKED: SFTK 原典 hash 4s 内变化 %s->%s，文件未冻结，待稳定后重跑" % (a[:12], b[:12])
raw = open(SRC, encoding="utf-8").read()
lines = raw.splitlines()
N = len(lines)
file_hash = fh()
assert N <= 4000, "BLOCKED: 当前 %d 行（非目标 3043 简体稳定版）" % N
print("frozen:", file_hash[:16], "lines:", N)

def join(a, b):
    return "\n".join(lines[a-1:b-1])
def text_hash(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

# ---- 一级章节（有序）----
HEADERS = [
 "叙","五星正说类","五星谬说类","男女合婚说","总论子平谬说类","动静说","盖头说","六亲说",
 "病药说类","雕枯旺弱四病说类","损益生长四药说类","正官格","偏官格附弃命从杀格",
 "古纯杂有有制类","近时纯杂有制类","时上一位贵格","附官杀去留杂格","月支正财格","时上偏财格",
 "伤官食神格","伤官十论","印绶格","阳刃格","专禄格","杂气财官印绶格","金神格","飞天禄马格",
 "子遥巳格","丑遥巳格","壬骑龙背格","井栏叉格","六乙鼠贵格","六阴朝阳格","刑合格","合禄格",
 "曲直仁寿格","稼穑格","炎上格","润 下 格","从 革 格","年时上官星格","从化格","来兵拱财格",
 "岁德扶杀格","又补岁德扶财格","专财格","日德格","日贵格","魁罡格","六壬趋艮格","六甲趋乾格",
 "勾陈得位格","玄武当权格","财官双美格","拱禄拱贵二格","日禄归时格","四位纯全格","天元一气格",
 "三合聚集格","福德格","神趣八法","五星论","金不换看命绳尺","十天干体象全编论","十二支咏","总咏",
 "吉神类","凶神类","起八字诀","看命人式","月令详辨","子平举要","江湖摘锦","男命小运定局",
 "女命小运定局","阳顺阴逆生旺死绝图","地支造化图","阴阳通变妙诀","定格局诀","子平泛论",
 "十干从化定诀","身弱论","弃命从杀格","渭泾论","五行元理消息赋","五行生克赋","一行禅师天元赋",
 "捷驰千里马赋","络绎赋","玄机赋","憎爱赋","万金赋","相心赋","仙机赋","金玉赋","人鉴论",
 "渊源集说","妖祥赋","幽微天干赋","人元消息赋","地支赋","病源赋",
]
HN = [norm(h) for h in HEADERS]
pos, found = 0, {}
for i in range(len(HEADERS)):
    target = HN[i]; s = None
    for j in range(pos, N):
        ln = lines[j].strip()
        if norm(ln) == target:
            s = j + 1; break
        if len(ln) <= 18 and norm(ln).startswith(target) and len(target) >= 3:
            s = j + 1; break
    if s is None:
        found[i] = None
    else:
        found[i] = s; pos = s
miss = [HEADERS[i] for i in range(len(HEADERS)) if found.get(i) is None]
print("unlocated:", miss)
located = [(i, found[i]) for i in range(len(HEADERS)) if found.get(i)]
chapter_lines = []
for k, (i, s) in enumerate(located):
    e = (located[k+1][1] - 1) if k + 1 < len(located) else N
    chapter_lines.append((i, s, e))
print("chapters:", len(chapter_lines))

UNVERIFIED = {"叙"}
sources, sid_by_ch = {}, {}
sid_map = {}
for i, s, e in chapter_lines:
    h = HEADERS[i]
    s_text = join(s, e).strip()
    lei = "LEI_%03d" % (i + 1)
    sid = "SFTK-V-V01/L-%s-P001" % lei
    unv = h in UNVERIFIED
    layer, grade = ("UNVERIFIED", "D") if unv else ("ORIGINAL", "A")
    handling = "NEEDS_REVIEW" if unv else ("SPLIT" if (e - s) > 40 else "RESOLVED")
    note = ("序言正文夹现代校勘括号注（原文为/应为/本名为…故改），未拆分" if unv
            else "张楠《神峰通考》（《命理正宗》）原文正文照录")
    rec = {
        "source_id": sid, "engine": "SHENFENG_TONGKAO", "book": "神峰通考",
        "source_version": "1.0.0", "source_hash": text_hash(s_text),
        "text_layer": layer, "evidence_grade": grade,
        "source_location": {
            "book": "神峰通考",
            "path": [
                {"level": "volume", "code": "V01", "name": "神峰通考（明·张楠 著）"},
                {"level": "lei", "code": lei, "name": h},
            ],
            "passage": h, "line_start": s, "line_end": e, "file_hash": file_hash,
        },
        "resource_id": "SRC-" + sid,
        "logical_uri": "source://sftk/v01/lei_%03d" % (i + 1),
        "relative_path": "sources/sftk/v01_lei_%03d.md" % (i + 1),
        "runtime_resolver": "resource://classic/sftk/v01",
        "source_text": s_text,
        "provenance": {"chain": [sid], "completeness": "COMPLETE",
                       "gaps": ["序言校勘注未拆分"] if unv else []},
        "handling_status": handling, "approval_status": "CANDIDATE",
        "approved_by": None, "approved_at": None,
        "created_at": CREATED, "updated_at": None,
        "metadata": {"edition": {"type": "通行本",
                                 "source": "garychowcmu/daizhigev20 易藏/术数",
                                 "editor": None, "year": None},
                     "collation_note": note,
                     "layer_reason": ("混合文本（原文+现代校勘注），UNVERIFIED" if unv else "古典原文正文，ORIGINAL"),
                     "section_chars": len(s_text)},
    }
    sources.append(rec)
    sid_by_ch[i] = sid

ids = [x["source_id"] for x in sources]
dups = [k for k, v in collections.Counter(ids).items() if v > 1]
assert not dups, dups
all_sid = set(ids)
with open(OUT_SRC, "w", encoding="utf-8") as f:
    for x in sources:
        f.write(json.dumps(x, ensure_ascii=False) + "\n")
print("sources:", len(sources), "->", OUT_SRC)

# ---- Rule ----
rules, rid = [], [0]
def ci(name):
    for i in range(len(HEADERS)):
        if norm(HEADERS[i]) == norm(name):
            return i
    return None
def rule(rtype, scope, subj, pred, conds, op, outs, er, ch, note=None):
    ci_i = ci(ch) if ch in HEADERS else None
    # ch may be a spaced GEJU name; normalize
    if ci_i is None:
        for i in range(len(HEADERS)):
            if norm(HEADERS[i]) == norm(ch):
                ci_i = i; break
    assert ci_i is not None, "chapter not found: %s" % ch
    rid[0] += 1
    r = {"rule_id": "CAND-SFTK-%03d" % rid[0], "engine": "SHENFENG_TONGKAO",
         "source_ids": [sid_by_ch[ci_i]], "rule_type": rtype, "scope": scope,
         "subject": subj, "predicate": pred,
         "preconditions": {"type": "conjunction", "conditions": conds},
         "operation": op, "outputs": outs, "evidence_requirement": er,
         "status": "CANDIDATE", "lifecycle_status": "CANDIDATE", "match_state": None,
         "version": "1.0.0", "created_at": CREATED, "updated_at": None,
         "approved_at": None, "deprecated_at": None,
         "metadata": {"origin": "SFTK", "book": "神峰通考", "extraction_method": "bot-knowledge",
                      "needs_approval": True, "section": HEADERS[ci_i]}}
    if note: r["notes"] = note
    rules.append(r)

# 八法/说类 定义与判定
rule("definition","natal","bing_yao","有病方为贵无伤不是奇",
     [{"field":"ming_ju_bing","op":"exists"},{"field":"yao","op":"exists"}],
     "emit",[{"field":"judgment","value":"贵"}],"A","病药说类","病药说类")
rule("definition","natal","si_bing","雕枯旺弱四病",
     [{"field":"bing_type","op":"in","value":["雕","枯","旺","弱"]}],
     "emit",[{"field":"bing","value":"雕枯旺弱四病"}],"A","雕枯旺弱四病说类","雕枯旺弱四病说类")
rule("definition","natal","si_yao","损益生长四药",
     [{"field":"yao_type","op":"in","value":["损","益","生","长"]}],
     "emit",[{"field":"yao","value":"损益生长四药"}],"A","损益生长四药说类","损益生长四药说类")
rule("definition","natal","dong_jing","天干动地支静",
     [{"field":"position","op":"in","value":["天干"]}],"emit",[{"field":"state","value":"动"}],
     "A","动静说","天干为动，地支为静")
rule("resolution","natal","gai_tou","盖头说",
     [{"field":"gai_tou","op":"exists"}],"evaluate",[{"field":"judgment","value":"盖头（干克支/克用神）"}],
     "A","盖头说","盖头说")
# 格局定义
GEJU = ["正官格","偏官格附弃命从杀格","时上一位贵格","月支正财格","时上偏财格",
        "伤官食神格","印绶格","阳刃格","专禄格","杂气财官印绶格","金神格","飞天禄马格",
        "子遥巳格","丑遥巳格","壬骑龙背格","井栏叉格","六乙鼠贵格","六阴朝阳格","刑合格","合禄格",
        "曲直仁寿格","稼穑格","炎上格","润 下 格","从 革 格","年时上官星格","从化格","来兵拱财格",
        "岁德扶杀格","日德格","日贵格","魁罡格","六壬趋艮格","六甲趋乾格","勾陈得位格","玄武当权格",
        "财官双美格","拱禄拱贵二格","日禄归时格","四位纯全格","天元一气格","三合聚集格","福德格"]
for g in GEJU:
    rule("definition","natal","ge_ju","is",
         [{"field":"ge_ju","op":"equals","value":g.strip()}],
         "emit",[{"field":"ge_ju","value":g.strip()}],"A",g,"神峰通考·%s"%g.strip())
rule("definition","natal","cong_sha","弃命从杀",
     [{"field":"day_master","op":"equals","value":"弱无根"},{"field":"shi_sha","op":"equals","value":"透旺"}],
     "emit",[{"field":"ge_ju","value":"弃命从杀"}],"A","弃命从杀格","弃命从杀格")
rule("resolution","natal","shen_ruo","身弱取生扶",
     [{"field":"day_master_strength","op":"equals","value":"弱"}],
     "evaluate",[{"field":"judgment","value":"身弱（取印比生扶）"}],"A","身弱论","身弱论")
rule("definition","natal","ba_fa","神趣八法",
     [{"field":"shen_qu_ba_fa","op":"exists"}],"emit",[{"field":"ba_fa","value":"神趣八法"}],
     "A","神趣八法","神趣八法")
rule("resolution","natal","ding_ge_ju","以月令定格局",
     [{"field":"month_ling","op":"exists"}],"evaluate",[{"field":"judgment","value":"以月令定格局"}],
     "A","定格局诀","定格局诀")

for r in rules:
    r["source_ids"] = [s for s in r["source_ids"] if s in all_sid] or list(all_sid)[:1]
with open(OUT_RULE, "w", encoding="utf-8") as f:
    for r in rules:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print("rules:", len(rules), dict(collections.Counter(r["rule_type"] for r in rules)))
print("src text_layer:", dict(collections.Counter(s["text_layer"] for s in sources)),
      "grade:", dict(collections.Counter(s["evidence_grade"] for s in sources)))
print("TOTAL sources=%d rules=%d" % (len(sources), len(rules)))
