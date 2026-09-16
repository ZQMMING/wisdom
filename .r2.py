# -*- coding: utf-8 -*-
import io, re
s = io.open(r"src/tongshu/engines/blind_bazi_engine.py", encoding="utf-8").read()
# 看 result 数据类有哪些字段
i = s.find("class BlindBaziResult")
j = s.find("def __init__", i)
print(s[i:i+3000])
