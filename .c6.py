# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.bazi_engine import BaziEngine
be = BaziEngine()
print("== 北京时间 13:00 (未时) ==")
r1 = be.compute((1984, 7, 23, 13), "male")
print(f"  四柱: {r1.year_pillar.heavenly_stem}{r1.year_pillar.earthly_branch} {r1.month_pillar.heavenly_stem}{r1.month_pillar.earthly_branch} {r1.day_pillar.heavenly_stem}{r1.day_pillar.earthly_branch} {r1.hour_pillar.heavenly_stem}{r1.hour_pillar.earthly_branch}")
print("== 真太阳时 12:33 -> 午时 (12点) ==")
r2 = be.compute((1984, 7, 23, 12), "male")
print(f"  四柱: {r2.year_pillar.heavenly_stem}{r2.year_pillar.earthly_branch} {r2.month_pillar.heavenly_stem}{r2.month_pillar.earthly_branch} {r2.day_pillar.heavenly_stem}{r2.day_pillar.earthly_branch} {r2.hour_pillar.heavenly_stem}{r2.hour_pillar.earthly_branch}")
print(f"  时柱十神: {r2.hour_pillar.stem_ten_god}, 十二长生: {r2.twelve_growth}")
