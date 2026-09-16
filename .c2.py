# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.bazi_engine import BaziEngine
be = BaziEngine()
print([m for m in dir(be) if not m.startswith("_")])
