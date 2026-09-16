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
birth = (1984,7,23,12)
chart = be.compute(birth, "male")
bb = BlindBaziEngine().compute(birth, "male")
yr = BlindYingqiEngine(be).analyze(birth, "male", target_year=2026)
jdg = BlindJudgmentEngine().judge(chart, bb, yr)
thm = BlindThemeEngine().aggregate(chart, bb, yr, jdg)
res = interpret_blind(thm, jdg, bb)
print("themes:", len(res.themes))
for t in res.themes:
    tid = t.get("theme_id"); tname = t.get("theme_name")
    entries = t.get("entries", [])
    print(f"\n=== {tid} {tname} ({len(entries)}条) ===")
    for e in entries[:5]:
        print(f"  src={e.get('source','')[:40]}")
        print(f"  original={e.get('original','(无)')[:80]}")
        print(f"  modern={e.get('modern','(无)')[:80]}")
