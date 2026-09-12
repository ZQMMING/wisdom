# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = io.open("src/tongshu/engines/blind_bazi_engine.py", encoding="utf-8").read()
i = src.find("occupation_candidate")
print("=== 出现位置 ===")
import re
for m in re.finditer(r"occupation_candidate", src):
    print(m.start())
j = src.find("occupation_name")
print("occupation_name 位置:", j)
if j >= 0:
    print(src[max(0,j-3000):j+800])
