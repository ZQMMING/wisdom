# -*- coding: utf-8 -*-
import sys, inspect
sys.path.insert(0, r"D:\shuntian")
import tongshu.engines.blind_judgment as bj
print([m for m in dir(bj) if not m.startswith("_") and callable(getattr(bj, m))])
for n in ["BlindJudgmentEngine", "analyze", "judge"]:
    if hasattr(bj, n):
        try: print(n, inspect.signature(getattr(bj, n)))
        except: pass
