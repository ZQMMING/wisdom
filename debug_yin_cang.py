#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug印藏支检查"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import STEM_WUXING, BRANCH_CANGGAN

day_wx = "木"
yin_wx_map = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
yin_wx = yin_wx_map[day_wx]
print(f"日主={day_wx}, 印星={yin_wx}")

branches = ["子", "巳", "子", "午"]
has_yin_cang = False
for b in branches:
    canggan = BRANCH_CANGGAN.get(b, [])
    for cg in canggan:
        if cg and STEM_WUXING.get(cg) == yin_wx:
            print(f"  {b}藏{cg}({STEM_WUXING.get(cg)}) == 印{yin_wx}")
            has_yin_cang = True
            break

print(f"印藏支? {has_yin_cang}")
