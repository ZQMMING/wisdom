# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziChart, Pillar
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine, STEM_HE
from src.tongshu.reasoning.bazi_ten_gods import ten_god, CONTROLS
from src.tongshu.engines.bazi_engine import STEM_ELEMENT

# D28 己巳 乙亥 壬申 丁未（段建业原文：原局大反局——左边伤官制官乙克己，右边合财壬合丁=牢狱）
def mk(s, b): return Pillar(s, b)
chart = BaziChart(
    year_pillar=mk("JI","SI"), month_pillar=mk("YI","HAI"),
    day_pillar=mk("REN","SHEN"), hour_pillar=mk("DING","WEI"),
    day_master="REN", luck_pillars=[], gender="male",
)
dm = "REN"
stems = ["JI","YI","REN","DING"]
print("十神:", [ten_god(dm, s) for s in stems])
print("日主合:", [(s, ten_god(dm,s)) for s in ["JI","YI","DING"] if (dm,s) in STEM_HE or (s,dm) in STEM_HE])
zt = False
for i in range(4):
    for j in range(4):
        if abs(i-j) > 1: continue
        if ten_god(dm, stems[i])=="伤官" and ten_god(dm, stems[j])=="正官" and CONTROLS.get(STEM_ELEMENT[stems[i]])==STEM_ELEMENT[stems[j]]:
            zt = True
            print("  天干明克:", stems[i], "克", stems[j])
print("zhi_tiangan:", zt)
bb = BlindBaziEngine()
try:
    br = bb.compute_chart(chart)
    print("反局:", br.zheng_fan_ju, "|", br.zheng_fan_ju_detail[:120])
except Exception as e:
    print("compute_chart err:", e)
    br = bb.compute_from_chart(chart) if hasattr(bb, "compute_from_chart") else None
    if br: print("反局:", br.zheng_fan_ju, "|", br.zheng_fan_ju_detail[:120])
