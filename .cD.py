# -*- coding: utf-8 -*-
import sys, inspect
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.blind_judgment import BlindJudgmentEngine, judge_blind
print("BlindJudgmentEngine methods:", [m for m in dir(BlindJudgmentEngine) if not m.startswith("_")])
print("judge_blind:", inspect.signature(judge_blind))
e = BlindJudgmentEngine()
for m in dir(e):
    if not m.startswith("_") and callable(getattr(e, m)):
        try: print(m, inspect.signature(getattr(e, m)))
        except: pass
