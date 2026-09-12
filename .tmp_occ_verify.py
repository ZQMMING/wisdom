# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
from src.tongshu.engines.blind_themes import aggregate_blind_themes
from src.tongshu.engines.blind_judgment import judge_blind
be = BaziEngine(); bb = BlindBaziEngine(be)
ch = be.compute((1980,6,22,10), gender="male")
br = bb.compute((1980,6,22,10), gender="male")
print("1980 occupation_candidate:", json.dumps(br.occupation_candidate, ensure_ascii=False))
# 15例 occupation 变化
cases = [(1912,11,12,12,"male"),(2027,3,22,2,"female"),(2028,8,3,10,"male"),(1974,12,24,8,"female"),(1948,2,4,18,"male"),(2010,2,18,4,"male"),(1968,7,22,14,"male"),(1965,9,4,14,"male"),(1913,3,18,22,"male"),(1968,10,21,4,"female"),(1950,9,20,10,"female"),(1947,4,20,4,"female"),(1964,6,24,8,"female"),(1985,5,22,22,"female"),(2015,9,21,2,"female")]
for i,(y,m,d,h,g) in enumerate(cases, 1):
    br2 = bb.compute((y,m,d,h), gender=g)
    oc = br2.occupation_candidate or {}
    print(f"#{i} occupation_name: {oc.get('occupation_name')}")
