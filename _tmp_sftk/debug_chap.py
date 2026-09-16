# -*- coding: utf-8 -*-
"""Pin down the chapter-matching bug: compare raw-bytes decode vs text-mode read,
and verify working tree == HEAD for the originals (so we know what's authoritative)."""
import hashlib, os, re, subprocess

ROOT = "D:/shuntian"
Y = os.path.join(ROOT, "data/classics/original/YHZP_渊海子平_完整全文.md")
chap_re = re.compile(r"^第\s*([0-9０-９ ]{1,5})\s*章\s*$")
chap_re_simple = re.compile(r"第\s*\d+\s*章")

b = open(Y, "rb").read()
print("raw bytes:", len(b), "hash12:", hashlib.sha256(b).hexdigest()[:12])
text = b.decode("utf-8")
print("  after utf-8 decode, has \\r:", "\r" in text, "  len:", len(text))
text_lf = text.replace("\r\n", "\n").replace("\r", "\n")
lines_lf = text_lf.split("\n")
print("  split(\\n) lines:", len(lines_lf), " trailing-empty:", lines_lf[-1] == "")
nc1 = sum(1 for ln in lines_lf if chap_re.match(ln.strip()))
nc2 = sum(1 for ln in lines_lf if chap_re_simple.search(ln))
print("  full-line regex matches: %d" % nc1)
print("  anywhere-in-line 第N章 matches: %d" % nc2)

# text-mode read (universal newlines)
text2 = open(Y, encoding="utf-8").read()
lines2 = text2.splitlines()
print("text-mode splitlines:", len(lines2))
print("  full-line regex matches:", sum(1 for ln in lines2 if chap_re.match(ln.strip())))

# show first few chapter-looking lines
print("--- sample lines containing 章 (first 8) ---")
cnt = 0
for i, ln in enumerate(lines_lf, 1):
    if "章" in ln and len(ln.strip()) < 12:
        print("  L%d: %r" % (i, ln[:40]))
        cnt += 1
        if cnt >= 8:
            break

# working tree vs HEAD
print("=== git: originals clean vs HEAD? ===")
res = subprocess.run(["git", "status", "--porcelain", "data/classics/original/"],
                     cwd=ROOT, capture_output=True, text=True)
print("porcelain:", res.stdout.strip() or "(clean)")
# committed hash
headblob = subprocess.run(["git", "show", "HEAD:data/classics/original/YHZP_渊海子平_完整全文.md"],
                          cwd=ROOT, capture_output=True)
print("HEAD blob hash12:", hashlib.sha256(headblob.stdout).hexdigest()[:12],
      "bytes:", len(headblob.stdout))
print("worktree == HEAD bytes?", headblob.stdout == b.replace(b"\r\n", b"\n").replace(b"\r", b"\n"))
