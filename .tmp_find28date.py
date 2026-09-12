# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
be = BaziEngine()
bb = BlindBaziEngine(be)
# 扫 1989-11-07 ~ 12-06（乙亥月）找壬申日（日柱 REN-SHEN）
found = None
for d in range(7, 31):
    ch = be.compute((1989,11,d,4), gender="male")
    if ch.day_pillar.heavenly_stem == "REN" and ch.day_pillar.earthly_branch == "SHEN":
        found = (1989,11,d); break
if not found:
    for d in range(1, 7):
        ch = be.compute((1989,12,d,4), gender="male")
        if ch.day_pillar.heavenly_stem == "REN" and ch.day_pillar.earthly_branch == "SHEN":
            found = (1989,12,d); break
print("D28日期:", found)
if found:
    y,m,d2 = found
    ch = be.compute((y,m,d2,4), gender="male")
    print("四柱:", f"{ch.year_pillar.heavenly_stem}{ch.year_pillar.earthly_branch}", f"{ch.month_pillar.heavenly_stem}{ch.month_pillar.earthly_branch}", f"{ch.day_pillar.heavenly_stem}{ch.day_pillar.earthly_branch}", f"{ch.hour_pillar.heavenly_stem}{ch.hour_pillar.earthly_branch}")
    br = bb.compute((y,m,d2,4), gender="male")
    print("反局:", br.zheng_fan_ju, "|", br.zheng_fan_ju_detail[:130])
