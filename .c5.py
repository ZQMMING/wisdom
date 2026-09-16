# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.bazi_engine import BaziEngine
be = BaziEngine()
r = be.compute((1984, 7, 23, 13), "male")
print("== BaziChart 字段 ==")
for k in dir(r):
    if not k.startswith("_"):
        v = getattr(r, k)
        if not callable(v):
            print(f"  {k} = {v}")
