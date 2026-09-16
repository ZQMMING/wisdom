# -*- coding: utf-8 -*-
"""v2: fix YHZP dedupe bug + SFTK title matching; emit clean plans."""
import re, hashlib, json, os

ROOT = "D:/shuntian"
YHZP = os.path.join(ROOT, "data/classics/original/YHZP_渊海子平_完整全文.md")
SFTK = os.path.join(ROOT, "data/classics/original/SFTK_神峰通考_完整全文.md")

def load(path):
    raw = open(path, encoding="utf-8").read()
    return raw, raw.splitlines(), hashlib.sha256(raw.encode()).hexdigest()

def norm(s): return re.sub(r"\s+", "", s)

def is_noise(s):
    st = s.strip()
    if not st: return True
    if "www.luckclub" in st: return True
    if re.match(r"^第\s*\d+\s*页\s*/\s*共\s*\d+\s*页", st): return True
    if "古籍典藏" in st: return True
    if st in ("《》", "----", "==="): return True
    return False

# ================= YHZP =================
yraw, yl, yh = load(YHZP)
print("YHZP frozen:", yh[:12], "lines:", len(yl))

def num_of(m):
    return re.sub(r"\s+", "", m.group(1)).translate(str.maketrans("０１２３４５６７８９", "0123456789"))

chap_re = re.compile(r"^第\s*([0-9０-９ ]{1,5})\s*章\s*$")
raw_chaps = []
for i, ln in enumerate(yl, 1):
    m = chap_re.match(ln.strip())
    if m:
        title = ""
        for k in range(i, min(i + 5, len(yl) + 1)):
            t = yl[k - 1].strip()
            if t and t != ln.strip() and not is_noise(t):
                title = t; break
        raw_chaps.append((i, num_of(m), title))

# dedupe keeping FIRST occurrence per number, then sort
seen = set(); chapters = []
for row in raw_chaps:
    if row[1] in seen: continue
    seen.add(row[1]); chapters.append(row)
chapters.sort(key=lambda x: int(x[1]))
print("YHZP chapters:", len(raw_chaps), "unique:", len(chapters))

# volume banner -> chapter mapping (nearest banner before chapter line)
volre = re.compile(r"渊海子平卷([一二三四五1-5])")
volmap = {}
for i in range(1, len(yl) + 1):
    m = volre.search(yl[i - 1])
    if m:
        volmap.setdefault(m.group(1), i)
volmap = {("一二三四五".index(k)): v for k, v in volmap.items()}
print("YHZP vol banners:", sorted(volmap.items()))

def vol_of_ch(i):
    last = "一"
    for idx, v in sorted(volmap.items()):
        tag = "一二三四五"[idx]
        if v < i: last = tag
    return last

def next_ch_line(i0):
    for i1 in [c[0] for c in chapters if c[0] > i0]:
        return i1 - 1
    return len(yl)

def orig_marker_line(i0, e):
    for k in range(i0, min(e, i0 + 60) + 1):
        if norm(yl[k - 1]) in ("原文", "原 文"):
            return k
    return i0 + 1

def later_marker_line(i0, e):
    for k in range(i0, e + 1):
        s = norm(yl[k - 1])
        if s.startswith("白话译文") or s == "现代启示" or s == "关键词":
            return k
    return None

TARGET = 100
per = (len(chapters) + TARGET - 1) // TARGET
orig_blocks, later_blocks = [], []
for bi in range(TARGET):
    grp = chapters[bi * per: (bi + 1) * per]
    if not grp: break
    f, lch = grp[0], grp[-1]
    e = next_ch_line(lch[0])
    o_s = orig_marker_line(f[0], e)
    o_e = later_marker_line(f[0], e)
    o_e = (o_e - 1) if o_e else e
    l_s = later_marker_line(f[0], e)
    if l_s is None:
        l_s = later_marker_line(f[0] + 40, e)  # maybe first ch of group lacks 白话
    vol = vol_of_ch(f[0])
    orig_blocks.append({
        "bi": bi + 1, "vol": vol,
        "ch_from": f[1], "ch_to": lch[1],
        "title": "第%s章·%s 至 第%s章·%s" % (f[1], norm(f[2])[:14], lch[1], norm(lch[2])[:14]),
        "line_start": o_s, "line_end": o_e, "text_layer": "ORIGINAL"})
    if l_s:
        later_blocks.append({
            "bi": bi + 1, "vol": vol,
            "ch_from": f[1], "ch_to": lch[1],
            "title": "第%s章 白话译文·%s 至 第%s章" % (f[1], norm(f[2])[:10], lch[1]),
            "line_start": l_s, "line_end": e, "text_layer": "LATER_COMMENTARY"})

print("YHZP blocks: orig=%d later=%d total=%d" % (len(orig_blocks), len(later_blocks), len(orig_blocks) + len(later_blocks)))
for b in orig_blocks[:2]: print("  sample:", b)
yhzp_plan = {"sha256": yh, "lines": len(yl), "chapters": len(chapters),
             "orig_blocks": orig_blocks, "later_blocks": later_blocks}
json.dump(yhzp_plan, open(os.path.join(ROOT, "_tmp_yhzp/yhzp_plan.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("wrote _tmp_yhzp/yhzp_plan.json")

# ================= SFTK =================
sraw, sl, sh = load(SFTK)
print("\nSFTK frozen:", sh[:12], "lines:", len(sl))

volre2 = re.compile(r"^\s*神峰通考\s*卷([一二三四五六])")
vols_first = {}
for i, ln in enumerate(sl, 1):
    m = volre2.match(ln)
    if m and m.group(1) not in vols_first:
        vols_first[m.group(1)] = i
print("SFTK vols first-line:", vols_first)

xu_i = None; toc_i = None; body_i = None
for i, ln in enumerate(sl, 1):
    s = sl[i - 1].strip()
    if xu_i is None and s == "叙":
        xu_i = i
    if "目錄" in s and "神峰通考" in norm(s):
        toc_i = i
    if body_i is None and i > 300 and "神峰通考" in s and "卷一" in norm(s):
        body_i = i
print("叙@", xu_i, "目录@", toc_i, "正文@", body_i)

# candidate section titles (繁体, OCR实际写法); match as: bare short line OR '## ' line
TITLE_CANDIDATES = [
    "五星正說類", "五星謬說類", "男子合婚說", "女子合婚說", "動靜說", "蓋頭說", "六親說",
    "病藥說類", "雕枯旺弱四病說類", "損益生長四藥說類", "總論子平謬說類",
    "正官格", "七殺格", "偏官格", "偏財格", "月支正財格", "雜氣財官印綬格", "正印格", "偏印格",
    "食神格", "傷官格", "建祿格", "陽刃格", "金神格", "專祿格", "日祿歸時格",
    "六乙鼠貴格", "壬騎龍背格", "子遙巳格", "潤下格", "稼穡格", "曲直仁壽格",
    "從革格", "炎上格", "從化格", "刑合格", "六陰朝陽格", "井欄叉格", "丑遙巳格",
    "飛天祿馬格", "夾丘拱財格", "專財格", "日貴格", "六壬趨艮格", "勾陳得位格",
    "財官雙美格", "天元一氣格", "年時上官星格", "時上一位貴格",
    "古純雜有制類", "古殺爲用神雜官有制例", "古官爲用神雜殺有制例",
    "喜忌篇", "繼善篇", "子平諸格正說類", "子平諸格謬說類", "人命見驗說",
    "陽順陰逆生旺死絕圖", "地支造化圖", "陰陽通變妙訣", "定格局訣", "子平泛論",
    "十干從化定訣", "身弱論", "棄命從殺格", "渭涇論", "太乙妙指法",
    "金不換看命繩尺", "金不換骨髓歌斷", "十天干體象全編", "總詠",
    "淵源集說", "妖祥賦", "幽微天干賦", "人元消息賦", "五行元理消息賦",
    "一行禪師天元賦", "崖泉男命賦", "崖泉女命賦", "五言獨步", "四言獨步",
    "講命捷徑賦", "萬尙書瓊璣三盤賦", "取格指訣歌斷", "節氣歌斷", "人鑑論"
]

def find_title(t):
    ts = norm(t)
    # first: as a bare short line (exact, ignoring case-label noise)
    for i in range(body_i or 303, len(sl) + 1):
        s = sl[i - 1]
        ns = norm(s)
        if ns == ts and len(s.strip()) <= 24:
            return i
    # second: with '## ' prefix
    for i in range(body_i or 303, len(sl) + 1):
        s = sl[i - 1]
        if s.startswith("## ") and norm(s[3:]) == ts:
            return i
    return None

body_end = len(sl) - 30
sections, missed = [], []
for ti, t in enumerate(TITLE_CANDIDATES):
    li = find_title(t)
    if li is None:
        missed.append(t); continue
    vol = "一"
    for v, vl in sorted(vols_first.items(), key=lambda x: x[1]):
        if li >= vl: vol = v
    sections.append({"ti": ti, "title": t, "line": li, "vol": vol})
sections.sort(key=lambda s: s["line"])
for i, s in enumerate(sections):
    s["end"] = sections[i + 1]["line"] - 1 if i + 1 < len(sections) else body_end
    s["code"] = "L-%03d" % (s["ti"] + 1)

print("SFTK sections matched:", len(sections), "missed:", len(missed))
print("missed titles:", missed)
sftk_plan = {"sha256": sh, "lines": len(sl), "xu_line": xu_i, "toc_line": toc_i,
             "body_line": body_i, "vols_first": vols_first, "sections": sections,
             "body_end": body_end, "missed": missed}
json.dump(sftk_plan, open(os.path.join(ROOT, "_tmp_sftk/sftk_plan.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("wrote _tmp_sftk/sftk_plan.json")
print("SFTK first 5:", [(s["title"], s["line"], s["end"]) for s in sections[:5]])
print("SFTK last 5:", [(s["title"], s["line"], s["end"]) for s in sections[-5:]])
