# -*- coding: utf-8 -*-
import sys, inspect, json
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.bazi_engine import BaziEngine
print(inspect.signature(BaziEngine.compute))
be = BaziEngine()
r = be.compute((1984, 7, 23, 13), "male", location="中山")
print("== 顶层 ==")
for k in r:
    v = r[k]
    if isinstance(v, (list, dict)):
        print(f"[{k}] {type(v).__name__} len={len(v)}")
    else:
        print(f"  {k} = {v}")
