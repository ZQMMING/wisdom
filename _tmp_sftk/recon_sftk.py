# -*- coding: utf-8 -*-
"""Recon SFTK 7358-line OCR edition: locate section headings + volume markers."""
import re, hashlib

P = "D:/shuntian/data/classics/original/SFTK_神峰通考_完整全文.md"
raw = open(P, encoding="utf-8").read()
lines = raw.splitlines()
h = hashlib.sha256(raw.encode()).hexdigest()
print("SFTK hash", h[:16], "lines", len(lines))
print("frozen-target check: 0091619f" if h.startswith("0091619f") else "!! NOT the 0091619f edition, still in flux")

# volume markers
vol = [(i, lines[i-1]) for i in range(1, len(lines)+1) if re.match(r'^神峰通考\s*卷[一二三四五六]', lines[i-1].strip())]
print("\n=== 卷 markers ===")
for i, t in vol[:12]:
    print("  L%d: %s" % (i, t.strip()[:30]))

# ## headings
heads = [(i, lines[i-1]) for i in range(1, len(lines)+1) if lines[i-1].startswith("## ")]
print("\n=== ## headings: %d total ===" % len(heads))
for i, t in heads[:15]:
    print("  L%d: %s" % (i, t.strip()[:50]))
print("  ...")
for i, t in heads[-8:]:
    print("  L%d: %s" % (i, t.strip()[:50]))

# bare (non-##) short lines that look like section titles in body (line>360)
import collections
body = [ (i, lines[i-1]) for i in range(360, len(lines)+1) ]
bare = [(i,t) for i,t in body if t.strip() and not t.startswith("#") and not t.startswith(">") and not t.startswith("==") and len(t.strip())<=14 and not re.match(r'^[甲乙丙丁戊己庚辛壬癸一二三四五六七八九十]', t.strip())]
print("\n=== bare short lines in body (>360): %d ===" % len(bare))
for i,t in bare[:30]:
    print("  L%d: %s" % (i, t.strip()))
