# -*- coding: utf-8 -*-
"""Locate SFTK real section headings in the 7358-line OCR version.
Emits an ordered list of (name, line) for the generator to consume."""
import re, hashlib, json

P = "D:/shuntian/data/classics/original/SFTK_神峰通考_完整全文.md"
raw = open(P, encoding="utf-8").read()
lines = raw.splitlines()
h = hashlib.sha256(raw.encode()).hexdigest()
print("sha256:", h[:16], "lines:", len(lines))
assert len(lines) > 7000, "expect 7358 OCR version, got %d" % len(lines)

def norm(s): return re.sub(r"\s+", "", s)

# Curated whitelist of REAL 神峰通考 section headings (in expected order).
# 干支-leading case labels (乙巳 制夫星格 etc.) are deliberately excluded.
WL = [
 "叙","五星正说类","五星谬说类","男女合婚说","总论子平谬说类","动静说","盖头说",
 "六亲说","病药说类","雕枯旺弱四病说类","损益生长四药说类",
 "正官格","古纯杂有制类","月支正财格","时上偏财格","伤官食神格","伤官十论",
 "印绶格","阳刃格","专禄格","杂气财官印绶格","金神格","飞天禄马格","井栏叉格",
 "六乙鼠贵格","六阴朝阳格","刑合格","合禄格","曲直仁寿格","稼穑格","炎上格",
 "润下格","从革格","年时上官星格","从化格","夹丘拱财格","来兵拱财格","岁德扶杀格",
 "专财格","日德格","日贵格","魁罡格","六壬趋艮格","六甲趋乾格","勾陈得位格",
 "玄武当权格","财官双美格","拱禄拱贵二格","日禄归时格","四位纯全格","天元一气格",
 "三合聚集格","福德格","神趣八法","五星论","金不换看命绳尺","金不换骨髓歌断",
 "十天干体象全编论","干支所属","十二支咏","总咏","十二支中所藏法","吉神类","凶神类",
 "起八字诀","看命入式","起大运法","月令详辨","子平举要","江湖摘锦","男命小运定局",
 "女命小运定局","阳顺阴逆生旺死绝图","地支造化图","阴阳通变妙诀","定格局诀",
 "子平泛论","十干从化定诀","身弱论","弃命从杀格","渭泾论","五行元理消息赋",
 "五行生克赋","一行禅师天元赋","捷驰千里马赋","络绎赋","玄机赋","憎爱赋",
 "万金赋","相心赋","仙机赋","金玉赋","人鉴论","渊源集说","妖祥赋","幽微天干赋",
 "人元消息赋","地支赋","病源赋","万尚书琼玑三盘赋","崖泉男命赋","崖泉女命赋",
 "讲命捷径赋","太乙妙指法",
]
# OCR variant spellings to also accept
ALIAS = {
 "井栏叉格":"井欄乂格","夹丘拱财格":"夾丘拱財格","来兵拱财格":"來兵拱財格",
 "万尚书琼玑三盘赋":"萬何書瓊璣三盤賦","神趣八法":"神趣八法類象",
 "五行生克赋":"五行生尅賦","讲命捷径赋":"講命捷徑賦","地支造化图":"地支造化之圖",
 "阳顺阴逆生旺死绝图":"生旺死絕圖","起大运法":"起大運法",
}
norms = [norm(wl) for wl in WL]

# body region starts after the TOC block. TOC ends ~ line 358; body from 359.
# Find body start: first "总论子平谬说类" after line 300.
body_start = 359
res = {}
for i, wl in enumerate(WL):
    target = norm(wl)
    target2 = norm(ALIAS.get(wl, wl))
    found = None
    for j in range(body_start, len(lines)+1):
        ln = norm(lines[j-1].strip().lstrip("#"))
        if ln == target or (len(ln) <= 20 and ln.startswith(target2) and len(target2) >= 2):
            found = j; break
    res[wl] = found

missing = [w for w, v in res.items() if v is None]
print("located:", sum(1 for v in res.values() if v), "/", len(WL))
print("MISSING:", missing)
# ordered dump of located (skip None), in document order
ordered = [(w, v) for w, v in res.items() if v is not None]
ordered.sort(key=lambda x: x[1])
print("\n--- ordered located sections ---")
for w, v in ordered:
    print(v, w)
with open("D:/shuntian/_tmp_sftk/sftk_sections.json", "w", encoding="utf-8") as f:
    json.dump({"sha256": h, "lines": len(lines), "body_start": body_start,
               "located": res, "ordered": ordered, "missing": missing}, f,
              ensure_ascii=False, indent=1)
print("wrote _tmp_sftk/sftk_sections.json")
