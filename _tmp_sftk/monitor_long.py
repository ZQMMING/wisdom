# -*- coding: utf-8 -*-
"""Long-window stability check: 8 samples x 30s, full hash + mtime + line count.
Also compare against the git-committed version of each original."""
import hashlib, os, time, subprocess, sys

ROOT = "D:/shuntian"
FILES = {
    "YHZP": "data/classics/original/YHZP_渊海子平_完整全文.md",
    "SFTK": "data/classics/original/SFTK_神峰通考_完整全文.md",
}

def h(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

# committed version hash
for name, rel in FILES.items():
    blob = subprocess.run(["git", "show", "HEAD:" + rel.replace("/", "\\")],
                          cwd=ROOT, capture_output=True)
    ch = hashlib.sha256(blob.stdout).hexdigest()
    print("COMMITTED %s: %s (%d bytes)" % (name, ch[:16], len(blob.stdout)))
    cur = h(os.path.join(ROOT, rel))
    print("  DISK now   : %s  match_committed=%s" % (cur[:16], ch == cur))

print("\n=== 8 samples x 30s ===")
prev = {}
for t in range(8):
    row = {}
    for name, rel in FILES.items():
        full = os.path.join(ROOT, rel)
        hx = h(full)
        mt = os.path.getmtime(full)
        row[name] = (hx, mt, len(open(full, encoding="utf-8").read().splitlines()))
    print("t=%d %s" % (t, " | ".join("%s=%s/mt=%d/%d行" % (k, v[0][:12], v[1], v[2]) for k, v in row.items())))
    for k, v in row.items():
        if k in prev and prev[k][0] != v[0]:
            print("  !!! %s FLIPPED: %s -> %s" % (k, prev[k][0][:12], v[0][:12]))
        prev[k] = v
    if t < 7:
        time.sleep(30)

# verdict
verdicts = {}
for name in FILES:
    verdicts[name] = "STABLE" if True else "?"
print("\nDone. If no FLIPPED lines above, the window was stable.")
