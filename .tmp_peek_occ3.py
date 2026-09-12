# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = io.open("src/tongshu/engines/blind_bazi_engine.py", encoding="utf-8").read()
j = src.find("occupation_name", 90000)
# 找到 occupation_candidate 赋值处（约99163）
k = 99163
print(src[k-400:k+2500])
