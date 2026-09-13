# -*- coding: utf-8 -*-
"""Diagnose YHZP luckclub 21122-line structure: real chapter count, block layout, noise ratio."""
import re, hashlib, json
from collections import Counter

P = "D:/shuntian/data/classics/original/YHZP_渊海子平_完整全文.md"
raw = open(P, encoding="utf-8").read()
lines = raw.splitlines()
h = hashlib.sha256(raw.encode()).hexdigest()
N = len(lines)
print("YHZP hash", h[:16], "lines", N, "(if hash != 4f225cc0 the file swapped again)")

def norm(s): return re.sub(r"\s+", "", s)

# 1) chapter markers: 第 N 章  where N digits may be space-separated ("第 1 0 章")
chap_re = re.compile(r"^第\s*([0-9]{1,3}(?:\s*[0-9]{1,2}){0,2})\s*章\s*$")
chapters = []
for i, ln in enumerate(lines, 1):
    s = ln.strip()
    m = chap_re.match(s)
    if m:
        num = norm(m.group(1))
        # title = next non-noise, non-marker line
        title = ""
        for k in range(i, min(i+5, N+1)):
            t = lines[k-1].strip()
            if t and not chap_re.match(t) and "luckclub" not in t and "古籍典藏" not in t and t != "《》":
                title = t; break
        chapters.append((i, num, title))
nums = [c[1] for c in chapters]
print("chapter markers:", len(chapters), "num range:", nums[0] if nums else None, "..", nums[-1] if nums else None)
dup = [n for n, c in Counter(nums).items() if c > 1]
print("dup chapter nums:", dup)

# 2) block-marker counts
def count(pat):
    c = 0
    for ln in lines:
        if re.match(pat, ln.strip()): c += 1
    return c
marks = {
 "原文": count(r"^原\s*文\s*$"),
 "白话译文": count(r"^白\s*话\s*译\s*文"),
 "现代启示": count(r"^现代启示"),
 "关键词": count(r"^关键词"),
 "思考": count(r"^\*\*思考"),
}
print("block markers:", marks)

# 3) noise ratio
noise = 0
for ln in lines:
    s = ln.strip()
    if not s: continue
    if "www.luckclub" in s or "古籍典藏" in s or s == "《》" or re.match(r"^第\s*\d+\s*页\s*/\s*共\s*\d+\s*页", s):
        noise += 1
nonblank = sum(1 for ln in lines if ln.strip())
print("noise lines: %d / %d nonblank = %.0f%%" % (noise, nonblank, 100.0*noise/nonblank))

# 4) sample a mid chapter (find chapter #50 region)
if len(chapters) > 50:
    ln, num, title = chapters[50]
    print("\n=== sample chapter #%s @line %d : %s ===" % (num, ln, title[:30]))
    for k in range(ln, min(ln+25, N+1)):
        print(k, "|", lines[k-1][:70])

# 5) last chapter end
print("\nlast chapter:", chapters[-1])
json.dump({"sha256": h, "lines": N, "chapters": chapters, "marks": marks,
           "noise": noise, "nonblank": nonblank},
          open("D:/shuntian/_tmp_yhzp/yhzp_diag.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("wrote _tmp_yhzp/yhzp_diag.json")
