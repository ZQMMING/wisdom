# -*- coding: utf-8 -*-
"""Diagnose the moving-target problem: is YHZP content actually changing or just hash noise?
Compare byte size, chapter-header count, and a content sample across two reads 8s apart."""
import hashlib, os, time, re

Y = "D:/shuntian/data/classics/original/YHZP_渊海子平_完整全文.md"

def snapshot():
    b = open(Y, "rb").read()
    text = b.decode("utf-8")
    lines = text.splitlines()
    chap = re.compile(r"^第\s*([0-9０-９ ]{1,5})\s*章\s*$")
    nchap = sum(1 for ln in lines if chap.match(ln.strip()))
    h = hashlib.sha256(b).hexdigest()
    return {"bytes": len(b), "lines": len(lines), "nchap": nchap,
            "hash": h, "first50": lines[0][:50] if lines else "",
            "l400": lines[399][:40] if len(lines) > 399 else ""}

a = snapshot()
print("T0:", a)
time.sleep(8)
b2 = snapshot()
print("T1:", b2)
changed = a["hash"] != b2["hash"]
print("\nHASH CHANGED in 8s:", changed)
if changed:
    print("  T0 bytes=%d chap=%d | T1 bytes=%d chap=%d" % (a["bytes"], a["nchap"], b2["bytes"], b2["nchap"]))
    print("  T0 l400: %s" % a["l400"])
    print("  T1 l400: %s" % b2["l400"])
    print("  => CONTENT IS GENUINELY CHANGING (parallel rewrite), not just encoding noise")
else:
    print("  => stable; chapter count =", a["nchap"])
