#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug从财减项"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import shi, calc_root_qi, STEM_WUXING
from engines.cong_ge_gates import cong_ge_pan, WUXING_OF, _demote_count, SHISHEN_CLASSES

# 戊丑 己丑 甲丑 戊丑
day_stem = "甲"
branches = ["丑", "丑", "丑", "丑"]
stems = ["戊", "己", "甲", "戊"]

day_wx = STEM_WUXING[day_stem]
cong_wx = WUXING_OF[day_wx]
shi_dict = {}
for family, wx in cong_wx.items():
    shi_dict[family] = shi(branches, stems, wx, branches[1])

print(f"势字典: {shi_dict}")

demote = _demote_count(shi_dict, "财", branches[1], day_wx, stems)
print(f"\n从财减项数: {demote}")

# 手动拆
print("\n手动拆:")
print(f"不当令? 丑月土当令 → 0")
print(f"官杀泄气? 官杀势={shi_dict.get('官杀', 0)} >0.5? {shi_dict.get('官杀', 0) > 0.5}")

print("\n天干透逆神检查:")
reverse_shen = ["比", "印", "官杀"]
for shen in reverse_shen:
    cls = SHISHEN_CLASSES[day_wx][shen]
    hit = False
    for i, s in enumerate(stems):
        if i == 2: continue
        wuxing = STEM_WUXING.get(s)
        if wuxing in cls:
            hit = True
            print(f"  {shen}={cls}: stems[{i}]={s}({wuxing}) 透干 → +1")
            break
    if not hit:
        print(f"  {shen}={cls}: 无透干")
