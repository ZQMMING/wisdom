# -*- coding: utf-8 -*-
"""SFTK stage-1: clean source, detect candidate chapter titles, dump for review."""
import re, json, sys, io

SRC = r"D:\顺天系统资料\豆包资料\六部经典校对版\SFTK_神峰通考_OCR校对版.md"

with io.open(SRC, "r", encoding="utf-8") as f:
    raw = f.readlines()
# normalize: strip trailing newline only
lines = [l.rstrip("\n").rstrip("\r") for l in raw]
N = len(lines)
assert N == 7358, f"line count {N} != 7358"

# ---- Step 1: line-level mechanical filtering ----
PAGE_MARK = re.compile(r"^\s*={3,}\s*第\s*\d+\s*页\s*={3,}\s*$")
# header lines: 神峰通考 卷X / 神峰通考卷X / 神峰通考 叙 / 神峰通考 目錄 / 神峰通考 alone / 卷X alone
HDR1 = re.compile(r"^\s*神\s*峰\s*通\s*考\s*[　 ]?(卷[一二三四五六七八九十]+)?\s*$")
HDR2 = re.compile(r"^\s*卷\s*[一二三四五六七八九十]+\s*$")
HDR3 = re.compile(r"^\s*神\s*峰\s*通\s*考\s*[叙目錄錄]+\s*$")
IMG = re.compile(r"^\s*!\[[^\]]*\]\([^)]*\)\s*$")
# standalone Chinese page number: 1-4 chars, only Chinese numerals / 〇
CN_NUM = set("零一二三四五六七八九十百千〇0123456789")
def is_cn_page(s):
    t = s.strip()
    if not (1 <= len(t) <= 4): return False
    return all(ch in CN_NUM for ch in t)
# publisher advertisement markers
PUB_STOP = re.compile(r"上海.*(書|局)發行|全一冊|全一册|定價|定价|本書特色|一、詞句|二、注釋|三、版式|四、校勘|著作權|翻印必究|分售處|發行所|校勘者|中華書局|楹聯|古今楹聯|東萊博議|呂氏博議")

clean_flags = []  # (lineno, keep, kind, text)
toc_start = None
toc_end = None
body_start = None
pub_start = None

for i, ln in enumerate(lines):
    no = i + 1
    s = ln.strip()
    if no <= 10:
        clean_flags.append((no, False, "file_header", s)); continue
    if s == "神峰通考目錄":
        toc_start = no
    if s == "神峰通考目錄終":
        toc_end = no
    if toc_start is not None and toc_end is None and no >= toc_start:
        clean_flags.append((no, False, "toc", s)); continue
    if toc_end is not None and body_start is None and ("神峰通考" in s and "卷一" in s):
        # line 292 "神峰通考卷一"
        body_start = no
    if not s:
        clean_flags.append((no, False, "blank", "")); continue
    if PAGE_MARK.match(s):
        clean_flags.append((no, False, "page_mark", s)); continue
    if IMG.match(s):
        clean_flags.append((no, False, "image", s)); continue
    if HDR1.match(s) or HDR2.match(s) or HDR3.match(s):
        clean_flags.append((no, False, "header", s)); continue
    if is_cn_page(s):
        clean_flags.append((no, False, "cn_page", s)); continue
    if PUB_STOP.search(s):
        pub_start = no if pub_start is None else pub_start
        clean_flags.append((no, False, "publisher", s)); continue
    clean_flags.append((no, True, "body", s))

# When publisher started, drop everything after
if pub_start:
    clean_flags = [(no,k,kind,t) for (no,k,kind,t) in clean_flags if not (kind=="body" and no >= pub_start)]

kept = [(no,t) for (no,k,kind,t) in clean_flags if k]
print("body_start", body_start, "toc", toc_start, toc_end, "pub_start", pub_start)
print("kept lines:", len(kept))

# ---- Step 2: candidate chapter titles ----
# A kept line is a candidate title if len <= 15 (stripped) and no sentence-ending punctuation
SENT_PUNCT = set("。，；：、？！.,;:!?")
cands = []
for no, t in kept:
    ts = t.strip()
    if len(ts) <= 15 and not any(p in ts for p in SENT_PUNCT):
        cands.append((no, ts))

with io.open(r"D:\shuntian\data\knowledge_engine\sftk\_cand_titles.txt", "w", encoding="utf-8") as f:
    for no, t in cands:
        f.write(f"{no}\t{t}\n")
print("candidate short-title lines:", len(cands))
