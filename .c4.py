# -*- coding: utf-8 -*-
import sys, inspect
sys.path.insert(0, r"D:\shuntian")
from tongshu.engines.blind_yingqi import BlindYingqiEngine
print(inspect.signature(BlindYingqiEngine.analyze))
print(inspect.signature(BlindYingqiEngine.__init__))
