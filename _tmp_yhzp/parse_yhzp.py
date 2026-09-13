# -*- coding: utf-8 -*-
"""Parse YHZP luckclub 21122-line structure -> section plan JSON.
Each section = 第N章 header ... next header. Within: 原文 block (ORIGINAL),
白话译文/现代启示/关键词/思考 (LATER). Emits plan with line spans + text_layer split."""
import re, hashlib, json

P = "D:/shuntian/data/classics/original/YHZP_渊海子平_完整全文.md"
raw = open(P, encoding="utf-8").read()
lines = raw.splitlines()
h = hashlib.sha256(raw.encode()).hexdigest()
assert h[:12] == "4f225cc0b68b", "YHZP not at frozen hash: %s" % h[:12]
print("YHZP frozen:", h[:16], "lines:", len(lines))

def norm(s): return re.sub(r"\s+", "", s)

# section header: 第 N 章  (N may be spaced: 第 1 0 章 / 第10章)
chap_re = re.compile(r"^第\s*([0-9０-９ ]{1,4})\s*章\s*$")
headers = []   # (line_no, title_from_next_nonempty)
for i, ln in enumerate(lines, 1):
    m = chap_re.match(ln.strip())
    if m:
        # title = next non-empty line
        j = i
        title = ""
        for k in range(i, min(i+4, len(lines)+1)):
            t = lines[k-1].strip()
            if t and t != ln.strip():
                title = t; break
        headers.append((i, norm(m.group(1)).strip(), title))
print("chapter headers found:", len(headers))

# classify noise lines
NOISE = re.compile(r"www\.luckclub|第\s*\d+\s*页\s*/\s*共|古籍典藏|^\s*《\s*》\s*$|^《》$|^\s*$")
def is_noise(s):
    st = s.strip()
    if st == "": return True
    if "www.luckclub" in st: return True
    if re.match(r"^第\s*\d+\s*页\s*/\s*共\s*\d+\s*页", st): return True
    if "古籍典藏" in st: return True
    if st == "《》": return True
    return False

# within a section [s,e), find 白话译文 marker (start of LATER block)
later_markers = re.compile(r"^白\s*话\s*译\s*文|^白话译文|^现代启示|^关键词|^\*\*思考")
plan = []
for idx, (ln, num, title) in enumerate(headers):
    e = headers[idx+1][0] - 1 if idx + 1 < len(headers) else len(lines)
    # find first 原文 line and first later-marker line within (ln, e)
    orig_start = None; later_start = None
    for k in range(ln+1, e):
        t = lines[k-1].strip()
        if orig_start is None and (t in ("原 文", "原文", "原 文")):
            orig_start = k
        if later_start is None and later_markers.match(t):
            later_start = k
    # ORIGINAL span: from orig_start to later_start-1 (or section end)
    o_end = (later_start - 1) if later_start else e
    plan.append({
        "num": num, "title": title, "sec_start": ln, "sec_end": e,
        "orig_start": orig_start, "orig_end": o_end,
        "later_start": later_start, "later_end": e,
        "has_original": orig_start is not None,
        "has_later": later_start is not None,
    })

missing_orig = [p["num"] for p in plan if not p["has_original"]]
missing_later = [p["num"] for p in plan if not p["has_later"]]
print("sections:", len(plan), "missing original:", len(missing_orig), "missing later:", len(missing_later))
# show a few
for p in plan[:5]:
    print(p)
print("...")
for p in plan[-5:]:
    print(p)
json.dump({"sha256": h, "lines": len(lines), "sections": plan,
           "missing_orig": missing_orig, "missing_later": missing_later},
          open("D:/shuntian/_tmp_yhzp/yhzp_plan.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("wrote _tmp_yhzp/yhzp_plan.json")
