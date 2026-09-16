# -*- coding: utf-8 -*-
import sys, inspect, json
sys.path.insert(0, r"D:\shuntian")
import tongshu.engines.blind_interpretation as bi
print([m for m in dir(bi) if not m.startswith("_") and callable(getattr(bi, m))])
