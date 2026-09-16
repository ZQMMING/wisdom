# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.bazi_engine import BaziEngine
from tongshu.engines.blind_bazi_engine import BlindBaziEngine
be = BaziEngine()
bb = BlindBaziEngine().compute((1984,7,23,12), "male")
print("work_efficiency:", bb.work_efficiency)
print("work_level:", bb.work_level)
print("structure_clarity:", bb.structure_clarity)
print("eff_path_direct:", bb.eff_path_direct)
print("eff_power_concentrated:", bb.eff_power_concentrated)
print("eff_target_effective:", bb.eff_target_effective)
print("control_completeness:", bb.control_completeness)
print("zuo_gong:", bb.zuo_gong, bb.zuo_gong_type)
print("zuo_gong_methods:", bb.zuo_gong_methods)
print("zuo_gong_attributions:", bb.zuo_gong_attributions)
