# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.blind_yingqi import BlindYingqiEngine
be = BaziEngine()
yr = BlindYingqiEngine(be).analyze((1984, 7, 23, 12), "male", target_year=2026)
print("== YingqiResult 字段 ==")
for k in dir(yr):
    if not k.startswith("_"):
        v = getattr(yr, k)
        if not callable(v):
            if isinstance(v, list):
                print(f"[{k}] list len={len(v)}")
            elif isinstance(v, dict):
                print(f"[{k}] dict keys={list(v.keys())[:12]}")
            else:
                print(f"  {k} = {v}")
