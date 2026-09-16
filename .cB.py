# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.blind_yingqi import BlindYingqiEngine
from tongshu.engines.blind_interpretation import interpret_blind_events
be = BaziEngine()
yr = BlindYingqiEngine(be).analyze((1984, 7, 23, 12), "male", target_year=2026)
entries = interpret_blind_events(yr)
print(f"== 解层条目 {len(entries)} 条 ==")
for i, e in enumerate(entries, 1):
    print(f"\n--- [{i}] ---")
    print(json.dumps(e, ensure_ascii=False, indent=1))
