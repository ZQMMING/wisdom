# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.blind_yingqi import BlindYingqiEngine
be = BaziEngine()
yr = BlindYingqiEngine(be).analyze((1984, 7, 23, 12), "male", target_year=2026)
print("== key_signals (7) ==")
for s in yr.key_signals:
    print(" ", json.dumps(s, ensure_ascii=False))
print("\n== triggers (13) ==")
for t in yr.triggers:
    print(" ", json.dumps(t, ensure_ascii=False))
print("\n== yingqi_events (7) ==")
for e in yr.yingqi_events:
    print(" ", json.dumps(e, ensure_ascii=False))
