# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.blind_bazi_engine import BlindBaziEngine
from tongshu.engines.blind_yingqi import BlindYingqiEngine
from tongshu.engines.blind_judgment import BlindJudgmentEngine
from tongshu.engines.blind_themes import BlindThemeEngine
be = BaziEngine()
birth = (1984, 7, 23, 12)
chart = be.compute(birth, "male")
bb = BlindBaziEngine().compute(birth, "male")
yr = BlindYingqiEngine(be).analyze(birth, "male", target_year=2026)
jdg = BlindJudgmentEngine().judge(chart, bb, yr)
thm = BlindThemeEngine().aggregate(chart, bb, yr, jdg)
for i, t in enumerate(thm.themes, 1):
    print(f"--- [{i}] ---")
    print(json.dumps(t, ensure_ascii=False, indent=1))
