# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.blind_bazi_engine import BlindBaziEngine
from tongshu.engines.blind_yingqi import BlindYingqiEngine
from tongshu.engines.blind_judgment import BlindJudgmentEngine
from tongshu.engines.blind_themes import BlindThemeEngine
from tongshu.engines.blind_interpretation import interpret_blind

be = BaziEngine()
birth = (1984, 7, 23, 12)
chart = be.compute(birth, "male")
bb = BlindBaziEngine().compute(birth, "male")
yr = BlindYingqiEngine(be).analyze(birth, "male", target_year=2026)
jdg = BlindJudgmentEngine().judge(chart, bb, yr)
thm = BlindThemeEngine().aggregate(chart, bb, yr, jdg)
print("== BlindThemeResult 字段 ==")
for k in dir(thm):
    if not k.startswith("_"):
        v = getattr(thm, k)
        if not callable(v):
            if isinstance(v, list): print(f"[{k}] list len={len(v)}")
            elif isinstance(v, dict): print(f"[{k}] dict keys={list(v.keys())[:20]}")
            else: print(f"  {k} = {v}")
res = interpret_blind(thm, jdg, bb)
print("\n== interpret_blind 返回字段 ==")
for k in dir(res):
    if not k.startswith("_"):
        v = getattr(res, k)
        if not callable(v):
            if isinstance(v, list): print(f"[{k}] list len={len(v)}")
            elif isinstance(v, dict): print(f"[{k}] dict keys={list(v.keys())[:20]}")
            else: print(f"  {k} = {v}")
