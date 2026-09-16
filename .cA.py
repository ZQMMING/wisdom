# -*- coding: utf-8 -*-
import sys, inspect, json
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.blind_yingqi import BlindYingqiEngine
from tongshu.engines.blind_interpretation import interpret_blind_events, interpret_blind
be = BaziEngine()
yr = BlindYingqiEngine(be).analyze((1984, 7, 23, 12), "male", target_year=2026)
print("interpret_blind_events:", inspect.signature(interpret_blind_events))
print("interpret_blind:", inspect.signature(interpret_blind))
res = interpret_blind_events(yr)
print("\n== 解层结果字段 ==")
for k in dir(res):
    if not k.startswith("_"):
        v = getattr(res, k)
        if not callable(v):
            if isinstance(v, list):
                print(f"[{k}] list len={len(v)}")
            else:
                print(f"  {k} = {v}")
