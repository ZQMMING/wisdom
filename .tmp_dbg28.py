# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine, STEM_HE
from src.tongshu.reasoning.bazi_ten_gods import ten_god, CONTROLS, STEM_ELEMENT
from src.tongshu.engines.bazi_engine import STEM_ELEMENT as SE
be = BaziEngine()
bb = BlindBaziEngine(be)
ch = be.compute((1989,10,21,4), gender="male")
dm = ch.day_pillar.heavenly_stem
stems = [ch.year_pillar.heavenly_stem, ch.month_pillar.heavenly_stem, ch.day_pillar.heavenly_stem, ch.hour_pillar.heavenly_stem]
print("日主:", dm, "天干:", stems)
print("十神:", [ten_god(dm, s) for s in stems])
# 天干伤官明克正官
for i in range(4):
    for j in range(4):
        if abs(i-j) > 1: continue
        tgi = ten_god(dm, stems[i]); tgj = ten_god(dm, stems[j])
        if tgi == "伤官" and tgj == "正官":
            print(f"  伤官{stems[i]}@{i} vs 正官{stems[j]}@{j}: CONTROLS[{SE[stems[i]]}]={CONTROLS.get(SE[stems[i]])} vs {SE[stems[j]]} -> {CONTROLS.get(SE[stems[i]])==SE[stems[j]]}")
# 日主合
for idx, s in enumerate(stems):
    if idx == 2: continue
    if (dm, s) in STEM_HE or (s, dm) in STEM_HE:
        print("日主合:", s, ten_god(dm, s))
