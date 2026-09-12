# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine
be = BaziEngine()
bb = BlindBaziEngine(be)
br = bb.compute((1968,7,22,14), gender="male")  # #7
for m, a, d in zip(br.zuo_gong_methods, br.zuo_gong_attributions, br.zuo_gong_detail):
    if "财制印" in m or "合正官" in m:
        print(m, "|", a, "|", d[:120])
