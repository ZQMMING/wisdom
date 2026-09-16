# -*- coding: utf-8 -*-
"""Detailed SFTK section recon on current edition. Dump all bare-short-title candidates
+ volume markers + TOC/body boundary so the generator can build a clean section plan."""
import re, hashlib

P = "D:/shuntian/data/classics/original/SFTK_神峰通考_完整全文.md"
raw = open(P, encoding="utf-8").read()
lines = raw.splitlines()
h = hashlib.sha256(raw.encode()).hexdigest()
print("SFTK hash", h[:16], "lines", len(lines))

# volume markers
print("\n=== 卷N markers (line: text) ===")
volre = re.compile(r'^\s*神峰通考\s*卷([一二三四五六])')
vols = []
for i, ln in enumerate(lines, 1):
    m = volre.match(ln.strip())
    if m: vols.append((i, m.group(1)))
seen = set(); uniq = []
for i, v in vols:
    if v not in seen:
        seen.add(v); uniq.append((i, v))
print("first-occurrence per 卷:", uniq[:8])
print("total 卷 marker lines:", len(vols))

# canonical section titles (bare, short, non-case, non-vol, non-page)
CANON = ("叙","說類","類$","格$","論$","訣$","法$","編$","詠$","圖$","詳辨","舉要","摘錦","定局","繩尺","骨髓","類象","泛論","人鑑","賦$","集說","歌$","篇$","論諸","星$")
body_start = None
for i in range(300, len(lines)):
    if '神峰通考' in lines[i] and '卷一' in lines[i]:
        body_start = i + 1; break
print("\nbody_start ~ line:", body_start)

def is_case(label):
    return bool(re.match(r'^[甲乙丙丁戊己庚辛壬癸一二三四五六七八九十]', label.strip())) or \
           bool(re.match(r'^[甲乙丙丁戊己庚辛壬癸].*年', label.strip()))

cands = []
for i in range(body_start or 360, len(lines) + 1):
    s = lines[i-1].strip()
    if not s or s.startswith("#") or s.startswith(">") or s.startswith("=="):
        continue
    if re.match(r'www\.', s): continue
    if re.match(r'^第\s*\d+\s*页\s*/\s*共', s): continue
    if s in ("神峰通考", "卷一", "卷二", "卷三", "卷四", "卷五", "卷六") or "神峰通考" in s: continue
    if len(s) <= 16 and not is_case(s):
        cands.append((i, s))
# dedupe consecutive
out = []
for i, s in cands:
    if out and out[-1][1] == s and i - out[-1][0] < 6:
        continue
    out.append((i, s))
print("\n=== candidate section titles: %d ===" % len(out))
for i, s in out[:60]:
    print("  L%d: %s" % (i, s))
print("  ... total %d, last 10:" % len(out))
for i, s in out[-10:]:
    print("  L%d: %s" % (i, s))

# tail
print("\n=== tail (last 15 lines) ===")
for i in range(len(lines)-15, len(lines)+1):
    print("  L%d: %s" % (i, lines[i-1][:60]))
