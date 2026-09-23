#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug稼穑格root_qi"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import calc_root_qi

# 戊辰 己未 戊戌 癸丑
day_stem = "戊"
branches = ["辰", "未", "戌", "丑"]

root_qi = calc_root_qi(day_stem, branches, [])
print(f"戊日主root_qi: {root_qi}")

# 手动算
from spec.root_qi import CANGGAN, STEM_WUXING
day_wx = STEM_WUXING[day_stem]
print(f"日主五行: {day_wx}")
for b in branches:
    print(f"  {b}: {CANGGAN.get(b, [])}")
