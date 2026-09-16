# -*- coding: utf-8 -*-
"""Rigorous moving-target diagnostic for both originals.
Samples hash + a content fingerprint over ~45s. If the file oscillates between
two variants (same line count, different hash), we CANNOT bind to a stable hash
and must report that to Human instead of shipping stale-bound records."""
import hashlib, os, time, re, json, collections

ROOT = "D:/shuntian"
Y = os.path.join(ROOT, "data/classics/original/YHZP_渊海子平_完整全文.md")
S = os.path.join(ROOT, "data/classics/original/SFTK_神峰通考_完整全文.md")
chap_re = re.compile(r"^第\s*([0-9０-９ ]{1,5})\s*章\s*$")

def fingerprint(path):
    raw = open(path, encoding="utf-8").read()
    lines = raw.splitlines()
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    nchap = sum(1 for ln in lines if chap_re.match(ln.strip()))
    return {"hash": h, "lines": len(lines), "nchap": nchap}

def watch(path, tag, samples=15, gap=3.0):
    rows = []
    for t in range(samples):
        f = fingerprint(path)
        rows.append((t, f["hash"], f["lines"], f["nchap"]))
        print("%s t=%02d %s lines=%d chap=%d" % (tag, t, f["hash"][:12], f["lines"], f["nchap"]))
        if t < samples - 1:
            time.sleep(gap)
    distinct = collections.defaultdict(list)
    for t, h, ln, nc in rows:
        distinct[(h, ln, nc)].append(t)
    print("\n=== %s: %d distinct states over %d samples ===" % (tag, len(distinct), samples))
    for key, ts in sorted(distinct.items(), key=lambda x: x[1][0]):
        print("  state hash=%s lines=%d chap=%d  at t=%s  (first-seen t=%d, %d samples)"
              % (key[0][:12], key[1], key[2], ",".join(str(t) for t in ts), ts[0], len(ts)))
    verdict = "FROZEN" if len(distinct) == 1 else "OSCILLATING (%d states)" % len(distinct)
    print("  VERDICT:", verdict)
    return verdict, distinct

print("======== YHZP ========")
vy, dy = watch(Y, "YHZP")
print("\n======== SFTK ========")
vs, ds = watch(S, "SFTK")

summary = {
    "YHZP": {"verdict": vy, "states": {str(k): {"hash": k[0], "lines": k[1], "nchap": k[2]} for k in dy}},
    "SFTK": {"verdict": vs, "states": {str(k): {"hash": k[0], "lines": k[1], "nchap": k[2]} for k in ds}},
}
json.dump(summary, open(os.path.join(ROOT, "_tmp_sftk/oscillation_report.json"), "w"),
          ensure_ascii=False, indent=1)
print("\nwrote _tmp_sftk/oscillation_report.json")
