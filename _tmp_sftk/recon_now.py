# -*- coding: utf-8 -*-
"""Recon YHZP + SFTK current structure."""
import re, hashlib, os, collections

def recon(tag, path):
    print("=" * 64)
    print(tag, "->", path)
    raw = open(path, encoding="utf-8").read()
    L = raw.splitlines()
    h = hashlib.sha256(raw.encode()).hexdigest()
    print("hash:", h[:16], "lines:", len(L))

    if "YHZP" in path:
        chap = []
        for i, ln in enumerate(L, 1):
            s = ln.strip()
            m = re.match(r'^第\s*([0-9０-９ ]{1,5})\s*章\s*$', s)
            if m:
                digits = re.sub(r'\s+', '', m.group(1)).translate(str.maketrans("０-９", "0-9"))
                chap.append((i, digits))
        print("chapters:", len(chap), "range:", chap[0][1] if chap else None, "..", chap[-1][1] if chap else None)
        dup = [n for n, c in collections.Counter([c[1] for c in chap]).items() if c > 1]
        print("dup nums:", dup)
        print("first 12:", chap[:12])
        print("last 4:", chap[-4:])
        # marker counts
        for pat, lbl in [
            (r'^原\s*文\s*$', '原文 marker'),
            (r'^白\s*话\s*译\s*文', '白话译文'),
            (r'^现代启示', '现代启示'),
            (r'^关键词', '关键词'),
            (r'^\*\*思考', '**思考'),
            (r'^眉批', '眉批'),
            (r'^附注', '附注'),
            (r'===== 第', '===== 第 N 页'),
            (r'www\.luckclub', 'www.luckclub'),
            (r'^《》$', '《》'),
        ]:
            c = sum(1 for ln2 in L if re.match(pat, ln2.strip()))
            print("  %-24s %d" % (lbl, c))
        # sample chapter 15
        for ln0, num in chap:
            if num == "15":
                print("\n=== chapter 15 @ line %d ===" % ln0)
                for k in range(max(1, ln0 - 2), min(ln0 + 25, len(L) + 1)):
                    print("%d | %s" % (k, L[k - 1][:60]))
                break

    if "SFTK" in path:
        # body region starts at '神峰通考 卷一'
        body_start = None
        for i, ln in enumerate(L, 1):
            if '神峰通考' in ln and '卷一' in ln and i > 300:
                body_start = i
                break
        print("\nbody region (卷一) starts @ line:", body_start)
        # TOC region
        print("TOC region 1..%d" % ((body_start or 400) - 1))
        # sample around body start
        if body_start:
            for k in range(body_start, min(body_start + 40, len(L) + 1)):
                print("%d | %s" % (k, L[k - 1][:60]))

recon("YHZP", "D:/shuntian/data/classics/original/YHZP_渊海子平_完整全文.md")
recon("SFTK", "D:/shuntian/data/classics/original/SFTK_神峰通考_完整全文.md")
