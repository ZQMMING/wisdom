# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine

CASES = [
    ("#2 丁未癸卯庚子丁丑", 2027,3,22,2,"female"),
    ("#3 戊申己未庚申辛巳", 2028,8,3,10,"male"),
    ("#4 甲寅丙子己亥戊辰", 1974,12,24,8,"female"),
    ("#7 戊申己未癸巳己未", 1968,7,22,14,"male"),
    ("#8 乙巳甲申辛酉乙未", 1965,9,4,14,"male"),
    ("#9 癸丑乙卯戊戌癸亥", 1913,3,18,22,"male"),
    ("#10 戊申壬戌甲子丙寅", 1968,10,21,4,"female"),
]
be = BaziEngine(); bb = BlindBaziEngine(be)
for name, y, m, d, h, g in CASES:
    ch = be.compute((y,m,d,h), gender=g)
    br = bb.compute((y,m,d,h), gender=g)
    print("=== %s" % name)
    print("  方法:", list(zip(br.zuo_gong_methods, br.zuo_gong_attributions)))
    print("  效率:", br.work_efficiency, "| 制净:", br.control_completeness)
    print("  官:", br.official_event_structure)
    print("  婚姻:", br.marriage_event_structure)
    print("  财:", br.wealth_event_structure)
    print("  身:", br.body_event_candidate)
    print("  反局:", br.zheng_fan_ju, "|", br.zheng_fan_ju_detail[:120])
    print()
