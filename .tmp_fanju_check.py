# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
be = BaziEngine()
bb = BlindBaziEngine(be)
CASES = [
    ("D28 牢狱 己巳乙亥壬申丁未", 1989,10,21,4,"male"),
    ("D19 反局 乙未丙戌甲子甲戌", 1955,9,11,6,"male"),
    ("#2 丁未癸卯庚子丁丑", 2027,3,22,2,"female"),
    ("#10 戊申壬戌甲子丙寅", 1968,10,21,4,"female"),
    ("乾隆 辛卯丁酉庚午丙子", 1711,9,25,12,"male"),
]
for name, y, m, d, h, g in CASES:
    ch = be.compute((y,m,d,h), gender=g)
    br = bb.compute((y,m,d,h), gender=g)
    print(f"{name} | 反局={br.zheng_fan_ju} | {br.zheng_fan_ju_detail[:100]}")
    eff = [m for m,a in zip(br.zuo_gong_methods, br.zuo_gong_attributions) if a=="EFFECTIVE"]
    print("   EFFECTIVE:", eff)
