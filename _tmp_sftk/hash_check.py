# -*- coding: utf-8 -*-
"""Settle the hash discrepancy: raw-bytes CRLF hash vs LF-normalized hash.
If they differ exactly as observed (sha256sum=27b7a8c9 vs my python=4f225cc0 for YHZP,
0091619f vs fe4ada08 for SFTK), the file is STABLE and my 'moving target' was a bug."""
import hashlib, os

ROOT = "D:/shuntian"
PAIRS = [
    ("YHZP", "data/classics/original/YHZP_渊海子平_完整全文.md",
     "27b7a8c9", "4f225cc0"),
    ("SFTK", "data/classics/original/SFTK_神峰通考_完整全文.md",
     "0091619f", "fe4ada08"),
]
for tag, rel, on_disk_observed, py_observed in PAIRS:
    p = os.path.join(ROOT, rel)
    raw_bytes = open(p, "rb").read()
    h_bytes = hashlib.sha256(raw_bytes).hexdigest()
    # Python text-mode read (universal newlines: CRLF->LF) then re-encode
    text_lf = open(p, encoding="utf-8").read()
    h_lf = hashlib.sha256(text_lf.encode("utf-8")).hexdigest()
    # manual LF normalization of raw bytes
    h_lf_manual = hashlib.sha256(raw_bytes.replace(b"\r\n", b"\n")).hexdigest()
    print("%s %s" % (tag, rel.split("/")[-1]))
    print("  raw-bytes(CRLF) hash : %s   (sha256sum reports %s)" % (h_bytes[:16], on_disk_observed))
    print("  python-text-mode hash: %s   (gen_all reported %s)" % (h_lf[:16], py_observed))
    print("  manual LF-norm hash  : %s   (matches python-text: %s)" % (
        h_lf_manual[:16], h_lf_manual == h_lf))
    print("  crlf_count=%d lone_cr=%d total_bytes=%d" % (
        raw_bytes.count(b"\r\n"), raw_bytes.count(b"\r") - raw_bytes.count(b"\r\n"), len(raw_bytes)))
    print("  => bytes-hash stable=%s | file is ONE stable variant, discrepancy=CRLF vs LF normalization"
          % (h_bytes[:12] == on_disk_observed))
    print()
