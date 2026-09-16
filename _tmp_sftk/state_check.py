# -*- coding: utf-8 -*-
"""One-shot state check: stability (6x) + CRLF nature + current hashes + my-data binding."""
import hashlib, os, time, collections, json

ROOT = "D:/shuntian"
Y = os.path.join(ROOT, "data/classics/original/YHZP_渊海子平_完整全文.md")
S = os.path.join(ROOT, "data/classics/original/SFTK_神峰通考_完整全文.md")

def h(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

# 6 stability samples over ~20s
ys, ss = [], []
for _ in range(6):
    ys.append(h(Y)); ss.append(h(S))
    time.sleep(3.5)
print("YHZP hashes across 20s:", sorted(set(ys)), "count=%d" % len(set(ys)))
print("SFTK hashes across 20s:", sorted(set(ss)), "count=%d" % len(set(ss)))
y_stable = len(set(ys)) == 1
s_stable = len(set(ss)) == 1
print("YHZP stable=%s (final=%s)" % (y_stable, ys[-1][:16]))
print("SFTK stable=%s (final=%s)" % (s_stable, ss[-1][:16]))

# CRLF nature on full files
for p in (Y, S):
    b = open(p, "rb").read()
    crlf = b.count(b"\r\n"); cr = b.count(b"\r"); lf = b.count(b"\n")
    print("%s: total_bytes=%d  crlf=%d  lone_cr=%d  lone_lf=%d" % (
        os.path.basename(p), len(b), crlf, cr - crlf, lf - crlf))

# line counts via text-mode read
yl = open(Y, encoding="utf-8").read().splitlines()
sl = open(S, encoding="utf-8").read().splitlines()
print("YHZP text-lines=%d  SFTK text-lines=%d" % (len(yl), len(sl)))

# my data bindings
for rel, exp in [("data/sources/yhzp_sources.jsonl", "yhzp"),
                 ("data/sources/sftk_sources.jsonl", "sftk")]:
    fp = os.path.join(ROOT, rel)
    hashes = collections.Counter()
    for line in open(fp, encoding="utf-8"):
        if line.strip():
            d = json.loads(line)
            hashes[d["source_location"]["file_hash"][:12]] += 1
    print("%s file_hash binding: %s" % (exp, dict(hashes)))
