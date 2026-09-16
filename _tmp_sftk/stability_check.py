# -*- coding: utf-8 -*-
"""Definitive stability check BEFORE regenerating. Sample raw-byte hash 6x over 20s
for each original. Only if each is stable (all 6 identical) do we proceed, and we
record the exact raw on-disk hash to bind. Reports the current authoritative state."""
import hashlib, os, time

ROOT = "D:/shuntian"
FILES = {
    "YHZP": "data/classics/original/YHZP_渊海子平_完整全文.md",
    "SFTK": "data/classics/original/SFTK_神峰通考_完整全文.md",
}

def raw_hash(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

report = {}
for tag, rel in FILES.items():
    p = os.path.join(ROOT, rel)
    hashes = [raw_hash(p) for _ in range(6)]
    hashes = []
    for _ in range(6):
        hashes.append(raw_hash(p))
        time.sleep(3.3)
    distinct = sorted(set(hashes))
    stable = len(distinct) == 1
    lines = len(open(p, encoding="utf-8").read().splitlines())
    report[tag] = {"stable": stable, "distinct": distinct, "lines": lines,
                   "final_hash": hashes[-1]}
    print("%s: %s | distinct=%d | lines=%d | final=%s" % (
        tag, "STABLE" if stable else "STILL MOVING (%d variants)" % len(distinct),
        len(distinct), lines, hashes[-1][:16]))

# Also re-check my EXISTING data bindings
import json, collections
for tag, rel in [("YHZP", "data/sources/yhzp_sources.jsonl"),
                 ("SFTK", "data/sources/sftk_sources.jsonl")]:
    fp = os.path.join(ROOT, rel)
    fh = collections.Counter()
    for line in open(fp, encoding="utf-8"):
        if line.strip():
            fh[json.loads(line)["source_location"]["file_hash"][:12]] += 1
    print("%s existing-data file_hash binding: %s  (disk now: %s -> %s)" % (
        tag, dict(fh), report[tag]["final_hash"][:12],
        "MATCH" if report[tag]["final_hash"][:12] in fh else "STALE"))

all_stable = all(v["stable"] for v in report.values())
print("\nPROCEED:", all_stable, " (all originals currently stable)")
