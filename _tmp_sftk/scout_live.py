# -*- coding: utf-8 -*-
"""Re-scout BOTH live originals: stability + YHZP chapter map + SFTK section map.
Dumps machine-readable plans for the generator. Abort-safe: reports hash not hard-fails."""
import re, hashlib, json, os, time

ROOT = "D:/shuntian"
Y = os.path.join(ROOT, "data/classics/original/YHZP_渊海子平_完整全文.md")
S = os.path.join(ROOT, "data/classics/original/SFTK_神峰通考_完整全文.md")

def h(p): return hashlib.sha256(open(p, encoding="utf-8").read().encode()).hexdigest()

# stability: 4 reads over ~20s
y = [h(Y) for _ in range(4)]
s = [h(S) for _ in range(4)]
time.sleep(15)
y2 = [h(Y)]
s2 = [h(S)]
yhzp_stable = len(set(y + y2)) == 1
sftk_stable = len(set(s + s2)) == 1
print("YHZP stable=%s hash=%s" % (yhzp_stable, y[0][:12]))
print("SFTK stable=%s hash=%s" % (sftk_stable, s[0][:12]))

yl = open(Y, encoding="utf-8").read().splitlines()
sl = open(S, encoding="utf-8").read().splitlines()
print("YHZP lines=%d SFTK lines=%d" % (len(yl), len(sl)))

def norm(x): return re.sub(r"\s+", "", x)

# ---- YHZP chapters ----
chre = re.compile(r"^第\s*([0-9０-９ ]{1,5})\s*章\s*$")
chaps = []
for i, ln in enumerate(yl, 1):
    m = chre.match(ln.strip())
    if m:
        num = norm(m.group(1)).translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        chaps.append((i, int(num)))
seen, chaps2 = set(), []
for i, n in chaps:
    if n in seen: continue
    seen.add(n); chaps2.append((i, n))
chaps2.sort(key=lambda x: x[1])
print("YHZP chapters: total=%d unique=%d min=%s max=%s" % (
    len(chaps), len(chaps2), chaps2[0][1] if chaps2 else None, chaps2[-1][1] if chaps2 else None))

# per-chapter: 原文 marker line, 白话译文 marker line, volume
volmap = {}
for i, ln in enumerate(yl, 1):
    m = re.search(r"渊海子平卷([一二三四五1-5])", ln)
    if m: volmap.setdefault(m.group(1), i)
def vol_of(line):
    last = "一"
    for v, vl in sorted(volmap.items(), key=lambda x: x[1]):
        if vl < line: last = "一二三四五"[list(volmap).index(v)] if False else v
    return last
plan_y = {"hash": y[0], "lines": len(yl), "vols": volmap, "chapters": chaps2,
          "n_unique": len(chaps2)}
json.dump(plan_y, open(os.path.join(ROOT, "_tmp_sftk/plan_yhzp.json"), "w"), ensure_ascii=False)

# ---- SFTK sections: dynamic content-match ----
# body start: first '神峰通考 卷一' after line 300
body = None
for i in range(290, len(sl)):
    if "神峰通考" in sl[i] and "卷一" in norm(sl[i]):
        body = i + 1; break
print("SFTK body start @ %s" % body)

# candidate section titles (OCR-actual 繁体 forms), matched by exact short line OR '## '
TITLES = [
 "五星正說類","五星謬說類","總論子平謬說類","動靜說","蓋頭說","六親說",
 "病藥說類","雕枯旺弱四病說類","損益生長四藥說類","正官格","偏官格","建祿格",
 "陽刃格","食神格","傷官格","正印格","偏印格","偏財格","月支正財格",
 "雜氣財官印綬格","金神格","專祿格","日祿歸時格","六乙鼠貴格","壬騎龍背格",
 "子遙巳格","潤下格","稼穡格","曲直仁壽格","從革格","炎上格","從化格",
 "刑合格","六陰朝陽格","井欄叉格","丑遙巳格","飛天祿馬格","夾丘拱財格",
 "專財格","日貴格","六壬趨艮格","勾陳得位格","財官雙美格","天元一氣格",
 "年時上官星格","時上一位貴格","古純雜有制類","喜忌篇","繼善篇",
 "定格局訣","子平泛論","十干從化定訣","身弱論","棄命從殺格","太乙妙指法",
 "金不換看命繩尺","不換金骨髓歌斷","十天干體象全編論","陰陽通變妙訣",
 "陽順陰逆生旺死絕圖","人鑑論","淵源集說","妖祥賦","幽微天干賦",
 "人元消息賦","五行元理消息賦","一行禪師天元賦","崖泉男命賦","崖泉女命賦",
 "五言獨步","四言獨步","講命捷徑賦","萬尙書瓊璣三盤賦","取格指訣歌斷",
 "節氣歌斷","論諸格有救","男命小運定局","女命小運定局","天干五陽通變",
 "天干五陰通變","十段錦","十段化氣","天元一字歌","運通歌","運晦歌",
 "五陰歌","戊癸歌","丁壬歌","丙辛歌","刑尅歌","看命捷歌","正官格歌",
 "七殺格歌","用財歌","印綬歌","尩子歌","壽元歌","女命歌","飄蕩歌",
 "月建生尩歌","羊刃歌","三奇格歌","喜忌歌",
]
def find(t):
    ts = norm(t)
    for i in range(body or 303, len(sl) + 1):
        s = sl[i]
        ns = norm(s).rstrip("。．")
        if s.strip().startswith("## ") and ns == norm(t):
            return i + 1
        if (not s.strip().startswith("## ")) and len(s.strip()) <= 22 and ns == ts:
            return i + 1
    return None

found = []
for t in TITLES:
    li = find(t)
    if li: found.append((li, t))
found.sort()
dedup = []
for li, t in found:
    if dedup and li == dedup[-1][0]: continue
    dedup.append((li, t))
found = dedup
missed = [t for t in TITLES if not any(f[1] == t for f in found)]
print("SFTK sections matched=%d missed=%d" % (len(found), len(missed)))
print("  first 6:", found[:6])
print("  last 6:", found[-6:])
plan_s = {"hash": s[0], "lines": len(sl), "body": body, "sections": found, "missed": missed}
json.dump(plan_s, open(os.path.join(ROOT, "_tmp_sftk/plan_sftk.json"), "w"), ensure_ascii=False)
print("wrote plan_yhzp.json + plan_sftk.json")
