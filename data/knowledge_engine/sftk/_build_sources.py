# -*- coding: utf-8 -*-
"""SFTK final builder: clean, split by curated titles, join lines, emit sources.jsonl."""
import re, io, json, os

SRC = r"D:\顺天系统资料\豆包资料\六部经典校对版\SFTK_神峰通考_OCR校对版.md"
OUTDIR = r"D:\shuntian\data\knowledge_engine\sftk"

raw = io.open(SRC, "r", encoding="utf-8").readlines()
lines = [l.rstrip("\n").rstrip("\r") for l in raw]
assert len(lines) == 7358

PAGE_MARK = re.compile(r"^\s*={3,}\s*第\s*\d+\s*页\s*={3,}\s*$")
HDR1 = re.compile(r"^\s*神\s*峰\s*通\s*考\s*[　 ]?(卷[一二三四五六七八九十]+[終終]?)?\s*$")
HDR2 = re.compile(r"^\s*卷\s*[一二三四五六七八九十]+\s*$")
HDR3 = re.compile(r"^\s*神\s*峰\s*通\s*考\s*[叙目錄錄]*\s*$")
HDR4 = re.compile(r"^\s*神\s*峰\s*[通考]*[攷]*\s*卷?[之一二三四五六七八九十]*\s*[終終]?\s*$")
IMG = re.compile(r"^\s*!\[[^\]]*\]\([^)]*\)\s*$")
RULER = re.compile(r"^\s*-{3,}\s*$")
CN_NUM = set("零一二三四五六七八九十百千〇0123456789")
def is_cn_page(s):
    t = s.strip()
    return 1 <= len(t) <= 4 and all(ch in CN_NUM for ch in t)
PUB = re.compile(r"上海.*書.*局發行|上海.*文明書局|全一冊|全一册|全二冊|全八冊|定價|定价|本書特色|一、詞句|二、注釋|三、版式|四、校勘|著作權|翻印必究|分售處|發行所|校勘者|中華書局|中華.*書局|楹聯|古今楹聯|東萊博議|呂氏博議|當代名人尺牘|歷代名家尺牘|著錄各家|經售|經銷|上海圖書館|圖書館藏|A541|D0226|明[六]\(|六月\(|民國|初版|再版|刷者|行者|勘者")

def norm(s):
    t = s.strip()
    t = re.sub(r"^#+\s*", "", t)
    t = t.replace("　", " ")
    t = re.sub(r"\s+", "", t)  # collapse ALL whitespace for matching
    return t

# Curated titles (normalized, whitespace-free)
T = set()
for x in [
 "叙",
 "五星參悅頌","男女合婚說","總論子平謬說類",
 "動靜說","六親說","蓋頭說","病藥說類","雕枯旺弱四病說類","損益生長四藥說類",
 "正官格","古純雜有制類","近時純雜有制類","古殺爲用神雜官有制例","古官爲用神雜殺有制例",
 "古時偏官雜正官有制例","古時純偏官有制例","時上一位貴格","月支正財格附棄命從財格","附傷官十論",
 "卍綬格","印綬格","陽刃格附比刦建祿格","喜見財官例","古見殺有制例","古會殺爲凶例",
 "專祿格","雜氣財官印綬格附時墓格","金神格","飛天祿馬格附倒沖祿馬格","子遥巳格","丑遙巳格",
 "壬騎龍背格","井欄乂格","井欄叉格","六乙鼠貴格","六陰朝陽格","刑合格","合祿格","曲直仁壽格",
 "稼穡格","炎上格","潤下格","從革格","年時上官星格","從化格","歲德扶殺格","日德格","日貴格",
 "魁罡正格","魁罡格","六壬趨艮格","六甲趨乾格","勾陳得位格","玄武當權格","財官雙美格",
 "拱祿拱貴二格","日祿歸時格","四位純全格","天元一氣格","三合聚集格","福德格","神趣八法類象",
 "屬象","從象","化象","照象","返象","鬼象","伏象","論大運","論太歲","論格局生死總歌",
 "五星論","金星論","木星論","水星論","火星論","土星論","不換金骨髓歌斷","餘財不足格",
 # vol2
 "十天干體象全編論",
 "甲木詩曰","乙木詩曰","丙火詩曰","丁火詩曰","戊土詩曰","己土詩曰","庚金詩曰","辛金詩曰","壬水詩曰","癸水詩曰",
 "十二支咏","子宮詩曰","丑宮詩曰","寅宮詩曰","卯宮詩曰","辰宮詩曰","巳宮詩曰","午宮詩曰","未宮詩曰",
 "申宮詩曰","酉宮詩曰","戌宮詩曰","亥宮詩曰","總咏","干支所屬",
 "地支合局","五行相生","十干祿","五行發用","天德","月德","學堂","官貴學館","華蓋",
 "吊客","勾神","絞神","咸池","隔角","寡宿","孤神","劫殺","破軍","懸針","紅艷殺","五鬼殺",
 "流霞殺","紫暗星","二三坵五墓","三丘五墓","天羅地網","馬前神煞","流年星耀","太白星","斧劈星","孤虛神",
 "起八字訣","年上遁月","日上遁時","看命入式","起大運法陽男陰女","起大運法陰男陽女","子平舉要","江湖摘錦",
 "男命小運定局","女命小運定局","乙日定格","丙日定格","丁日定格","戊日定格","子平泛論",
 "十干從化定訣","十段錦","十段化氣","甲己歌","乙庚歌","丙辛歌","月建生尅",
 "正月建寅歌","二月癸卯歌","七月建申歌","八月建酉歌","九月建戌歌","十月建亥歌","十一月建子歌",
 "正官格歌","七殺格歌","用財歌","印綬歌","氣象篇","渭涇論","渭涇篇","定真篇",
 "一行禪師壬二元賦","相心賦","仙機賦","人鑑論","渊源集說","地支賦","病源賦",
]:
    T.add(norm(x))

def is_title(t):
    return norm(t) in T

# ---- Build kept stream ----
toc_start=toc_end=None
kept=[]
reset_cur=False
for i, ln in enumerate(lines):
    no=i+1; s=ln.strip()
    if no<=10: continue
    if s=="神峰通考目錄":
        toc_start=no; reset_cur=True
    if s=="神峰通考目錄終": toc_end=no
    if toc_start and toc_end is None and no>=toc_start: continue
    if s in ("神峰通考目錄終","神峰通考目錄終 "): continue
    # strip leading markdown #'s then re-test against noise
    s2 = re.sub(r"^#+\s*", "", s).strip()
    if not s2: continue
    if PAGE_MARK.match(s2): continue
    if IMG.match(s2): continue
    if RULER.match(s2): continue
    if HDR1.match(s2) or HDR2.match(s2) or HDR3.match(s2) or HDR4.match(s2): continue
    if is_cn_page(s2): continue
    if PUB.search(s2): continue
    kept.append((no,s2,reset_cur)); reset_cur=False

print("kept lines:", len(kept))

# ---- Segment ----
segments=[]
cur=None
for no,t,rst in kept:
    if rst:
        cur=None
    if is_title(t):
        cur={"title":norm(t),"start":no,"lines":[]}
        segments.append(cur)
    else:
        if cur is None:
            cur={"title":"卷一開篇","start":no,"lines":[]}
            segments.append(cur)
        cur["lines"].append((no,t))

segments=[sg for sg in segments if "".join(x for _,x in sg["lines"]).strip()]
print("segments:", len(segments))

sources=[]
for chap_idx, sg in enumerate(segments, 1):
    CHAP=f"{chap_idx:03d}"
    body="".join(t for _,t in sg["lines"])
    body=re.sub(r"\s+","",body)
    if len(body)<8: continue
    IDX="001"
    sources.append({
        "source_id": f"SFTK-{CHAP}-{IDX}",
        "engine": "SHENFENG_TONGKAO",
        "book": "神峰通考",
        "chapter": sg["title"],
        "text_id": f"SFTK-T-{CHAP}-{IDX}",
        "text_layer": "ORIGINAL",
        "source_text": body,
        "resource_id": f"SRC-SFTK-{CHAP}",
        "logical_uri": f"source://sftk/{CHAP}/{IDX}",
        "relative_path": f"sources/sftk/chapter_{CHAP}.md",
        "version": "1.0.0",
        "status": "CANDIDATE",
    })

with io.open(os.path.join(OUTDIR,"sources.jsonl"),"w",encoding="utf-8",newline="") as f:
    for s in sources:
        f.write(json.dumps(s,ensure_ascii=False)+"\n")

with io.open(os.path.join(OUTDIR,"_segments.txt"),"w",encoding="utf-8") as f:
    for i,sg in enumerate(segments,1):
        body="".join(t for _,t in sg["lines"])
        f.write(f"{i:03d}\tline{sg['start']}\t{sg['title']}\tlen={len(body)}\t{body[:50]}\n")

print("sources:", len(sources))
