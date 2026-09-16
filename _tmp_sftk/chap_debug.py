# -*- coding: utf-8 -*-
"""Pin down why gen_all's chap_re matches 0 but the structural-check regex matches 305.
Direct A/B on the live file."""
import re

P = "D:/shuntian/data/classics/original/YHZP_渊海子平_完整全文.md"
b = open(P, "rb").read()
text = b.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
lines = text.split("\n")
print("file lines:", len(lines))

re1 = re.compile(r"^第\s*([0-9０-９ ]{1,5})\s*章\s*$")   # gen_all's chap_re (with capture group)
re2 = re.compile(r"^第\s*[0-9０-９ ]{1,5}\s*章\s*$")      # _struct_ok's regex (no capture)

n1 = sum(1 for ln in lines if re1.match(ln.strip()))
n2 = sum(1 for ln in lines if re2.match(ln.strip()))
print("chap_re (with group)  matches:", n1)
print("_struct_ok (no group) matches:", n2)

# which lines does re2 match that re1 does NOT?
diff_lines = []
for ln in lines:
    s = ln.strip()
    if re2.match(s) and not re1.match(s):
        diff_lines.append(s)
print("\nre2-only (no re1 match): %d lines" % len(diff_lines))
for s in diff_lines[:5]:
    print("  re2-only:", repr(s))

# show first 5 lines that match re1
m1 = [ln for ln in lines if re1.match(ln.strip())][:5]
print("\nre1-only matches (first 5):")
for s in m1:
    print("  re1:", repr(s))

# also test without strip()
n1_nostrip = sum(1 for ln in lines if re1.match(ln))
print("\nchap_re WITHOUT .strip():", n1_nostrip)
# show 5 lines matching without strip
m1ns = [ln for ln in lines if re1.match(ln)][:5]
for s in m1ns:
    print("  ns:", repr(s))
