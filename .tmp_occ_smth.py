# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = io.open("D:/顺天系统资料/shuntian/data/classics/original/SMTH_三命通会_完整全文.md", encoding="utf-8").read()
# 提取含职业象的句子
pat = re.compile(r"[^。\n]{0,45}(?:商贾|技艺|为官|主贵|武职|从事|执业|行业|经商|手艺|吏|军|师|医|匠|贩|农|渔)[^。\n]{0,45}")
seen = set()
for m in pat.finditer(src):
    s = m.group().strip()
    if s not in seen and len(s) > 12:
        seen.add(s)
        print(s)
    if len(seen) >= 60: break
