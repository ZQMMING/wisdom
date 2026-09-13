# -*- coding: utf-8 -*-
"""Stability monitor: sample each original's hash over a window.
Verdict: CONVERGED (one distinct hash) vs IN_FLUX (multiple distinct)."""
import hashlib, time, os, json

FILES = {
    "YHZP": "D:/shuntian/data/classics/original/YHZP_渊海子平_完整全文.md",
    "SFTK": "D:/shuntian/data/classics/original/SFTK_神峰通考_完整全文.md",
}
SAMPLES = 16
GAP = 5  # seconds

def h(path):
    return hashlib.sha256(open(path, encoding="utf-8").read().encode("utf-8")).hexdigest()

result = {}
# do all files in parallel by sampling both on each tick
seq = []
for t in range(SAMPLES):
    row = {}
    for name, p in FILES.items():
        try:
            hx = h(p)
            row[name] = (hx[:12], len(open(p, encoding="utf-8").read().splitlines()))
        except Exception as e:
            row[name] = ("ERR:%s" % e, 0)
    seq.append(row)
    print("t=%02d  %s" % (t, "  ".join("%s=%s/%s行" % (k, v[0], v[1]) for k, v in row.items())))
    if t < SAMPLES - 1:
        time.sleep(GAP)

for name, p in FILES.items():
    hashes = [r[name][0] for r in seq if r[name][0].startswith("ERR") is False]
    lines = [r[name][1] for r in seq]
    distinct = sorted(set(hashes))
    verdict = "CONVERGED" if len(distinct) == 1 else "IN_FLUX"
    result[name] = {"verdict": verdict, "distinct_hashes": distinct,
                    "lines": lines[0], "sample_count": len(seq)}
    print("\n=== %s: %s ===" % (name, verdict))
    print("  distinct:", distinct)
    print("  final hash:", hashes[-1], "lines:", lines[-1])

json.dump(result, open("D:/shuntian/_tmp_sftk/stability.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nwrote _tmp_sftk/stability.json")
