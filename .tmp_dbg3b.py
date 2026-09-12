# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
be = BaziEngine()
bb = BlindBaziEngine(be)
ch = be.compute((2028,8,3,10), gender="male")
br = bb.compute((2028,8,3,10), gender="male")
for m, a, d in zip(br.zuo_gong_methods, br.zuo_gong_attributions, br.zuo_gong_detail):
    if "官杀制比劫" in m or "SHEN" in d or "SI" in d:
        print(m, "|", a, "|", d[:110])
