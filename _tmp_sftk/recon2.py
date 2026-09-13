# -*- coding: utf-8 -*-
"""Recon both REPLACED full-version originals; emit structure maps."""
import re, hashlib, collections

def report(tag, path, out):
    raw = open(path, encoding="utf-8").read()
    lines = raw.splitlines()
    h = hashlib.sha256(raw.encode()).hexdigest()
    print("\n" + "="*70)
    print(tag, "lines:", len(lines), "sha256:", h[:16])
    with open(out, "w", encoding="utf-8") as f:
        def w(*a):
            print(*a); f.write(" ".join(str(x) for x in a) + "\n")
        w("### chapter / section marker line numbers ###")
        chap = []
        for i, ln in enumerate(lines, 1):
            m = re.match(r"^第\s*(\d+)\s*章", ln)
            if m: chap.append((i, int(m.group(1)), ln.strip()[:40]))
        w("total 第N章 markers:", len(chap))
        for c in chap[:60]:
            w(c)
        if len(chap) > 60:
            w("... +%d more" % (len(chap)-60))
            for c in chap[-10:]:
                w(c)
        w("\n### 原文 / 白话 / 译文 markers (count + first 20) ###")
        for pat in [r"^原\s*文", r"白话", r"译文", r"^（原文）", r"原文：", r"译注"]:
            hits = [i for i, ln in enumerate(lines, 1) if re.search(pat, ln)]
            w("  pat=%r -> %d hits, first=%s" % (pat, len(hits), hits[:8]))
        w("\n### web / noise patterns (count) ###")
        for pat in [r"www\.luckclub", r"第\s*\d+\s*页\s*/\s*共", r"古籍典藏", r"^《》", r"^《》\s*$"]:
            hits = sum(1 for ln in lines if re.search(pat, ln))
            w("  pat=%r -> %d" % (pat, hits))
        w("\n### SFTK / special section markers ###")
        # detect generic structural heading style
        for pat in [r"^##\s", r"^={4,}\s*第", r"^《.*》\s*$", r"^(卷|第卷)"]:
            hits = [(i, lines[i-1].strip()[:40]) for i in range(1, len(lines)+1) if re.match(pat, lines[i-1])]
            w("  pat=%r -> %d, first=%s" % (pat, len(hits), hits[:15]))
    print("map ->", out)

report("YHZP(luckclub)", "D:/shuntian/data/classics/original/YHZP_渊海子平_完整全文.md",
       "D:/shuntian/_tmp_yhzp/map_yhzp_new.txt")
report("SFTK(OCR7358)", "D:/shuntian/data/classics/original/SFTK_神峰通考_完整全文.md",
       "D:/shuntian/_tmp_sftk/map_sftk_new.txt")
