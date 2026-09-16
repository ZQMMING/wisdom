# -*- coding: utf-8 -*-
import sys, inspect, json
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.blind_themes import BlindThemeEngine
e = BlindThemeEngine()
for m in dir(e):
    if not m.startswith("_") and callable(getattr(e, m)):
        try: print(m, inspect.signature(getattr(e, m)))
        except: pass
