#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug F3从儿减项"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import shi, calc_root_qi, STEM_WUXING
from engines.cong_ge_gates import cong_ge_pan, WUXING_OF, _demote_count, SHISHEN_CLASSES

# 丙午 丁巳 甲戌 戊辰
day_stem = "甲"
branches = ["午", "巳", "戌", "辰"]
stems = ["丙", "丁", "甲", "戊"]

day_wx = STEM_WUXING[day_stem]
cong_wx = WUXING_OF[day_wx]
shi_dict = {}
for family, wx in cong_wx.items():
    shi_dict[family] = shi(branches, stems, wx, branches[1])

print(f"势字典: {shi_dict}")
print(f"日主五行: {day_wx}")
print(f"十神分类: {SHISHEN_CLASSES[day_wx]}")

# 算从儿族减项
demote = _demote_count(shi_dict, "食伤", branches[1], day_wx, stems)
print(f"\n从儿减项数: {demote}")

# 手动算
print("\n手动算:")
print(f"不当令? 巳月火食伤当令 → {shi_dict.get('食伤', 0)}")
print(f"官杀泄气? 官杀势={shi_dict.get('官杀', 0)}")
print(f"财星泄气? 财势={shi_dict.get('财', 0)}")

# 天干透逆神检查
print("\n天干透逆神检查:")
reverse_shen = ["印", "官杀"]
for shen in reverse_shen:
    cls = SHISHEN_CLASSES[day_wx][shen]
    print(f"  {shen}={cls}")
    for i, s in enumerate(stems):
        if i == 2: continue
        wuxing = STEM_WUXING.get(s)
        hit = wuxing in cls
        print(f"    stems[{i}]={s}({wuxing}) in {cls} → {hit}")
