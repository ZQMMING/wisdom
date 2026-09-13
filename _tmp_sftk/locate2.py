# -*- coding: utf-8 -*-
"""Locate SFTK 7358-line OCR body-section headings, excluding:
   - TOC block (lines 1..358, before '神峰通考 卷一')
   - case labels starting with a 天干 (甲乙丙丁戊己庚辛壬癸 or 一..九)
   - '##', '=====', page-number, indented lines
Emit ordered (name,line) list to _tmp_sftk/sftk_body_sections.json"""
import re, hashlib, json

P = "D:/shuntian/data/classics/original/SFTK_神峰通考_完整全文.md"
raw = open(P, encoding="utf-8").read()
lines = raw.splitlines()
h = hashlib.sha256(raw.encode()).hexdigest()
print("sha256:", h[:16], "lines:", len(lines))

GANZH = set("甲乙丙丁戊己庚辛壬癸")
def ends_ok(s):
    return re.search(r"(類|說$|格$|論$|訣$|法$|編$|詠$|圖$|詳辨$|定局$|入式$|摘錦$|類象$|泛論$|人鑑$|賦$|集說$|星論|干支|支中|所藏|总论|總論|叙|續)", s[-12:])

# body start: first '神峰通考 卷一' after line 300
body0 = 359
for i in range(300, len(lines)+1):
    if "神峰通考" in lines[i-1] and "卷一" in lines[i-1]:
        body0 = i; break
print("body0:", body0)

seen = set(); out = []
for i in range(body0, len(lines)+1):
    s = lines[i-1]
    t = s.strip()
    if not t: continue
    if t.startswith("==") or t.startswith("#") or "页 / 共" in t or "第 " in t[:6] and "页" in t: continue
    if s[0] in " \t": continue            # indented
    if len(t) > 24: continue
    if t[0] in GANZH: continue            # case label
    if t[0] in "0123456789": continue
    if t == "神峰通考" or t.startswith("第 "): continue
    # must end with a structural suffix
    if not re.search(r"(類|說|格|論|訣|法|編|詠|圖|詳辨|定局|入式|摘錦|類象|泛論|人鑑|賦|集說|星|所藏|叙)$", t): continue
    key = re.sub(r"\s+", "", t)
    if key in seen: continue
    seen.add(key); out.append((i, t[:30]))

print("\nlocated body sections:", len(out))
for i, t in out:
    print(i, t)
with open("D:/shuntian/_tmp_sftk/sftk_body_sections.json", "w", encoding="utf-8") as f:
    json.dump({"sha256": h, "lines": len(lines), "body0": body0,
               "sections": out}, f, ensure_ascii=False, indent=1)
print("wrote _tmp_sftk/sftk_body_sections.json")
