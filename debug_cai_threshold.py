#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""debug财势阈值"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import shi, calc_root_qi, STEM_WUXING
from engines.cong_ge_gates import WUXING_OF


def debug(name, day_stem, branches, stems):
    day_wx = STEM_WUXING[day_stem]
    cong_wx = WUXING_OF[day_wx]
    
    shis = {}
    for family, wx in cong_wx.items():
        shis[family] = shi(branches, stems, wx, branches[1])
    
    max_family = max(shis.items(), key=lambda kv: kv[1])[0]
    max_val = shis[max_family]
    second_val = sorted(shis.values(), reverse=True)[1]
    
    ratio = max_val / second_val if second_val > 0 else 999
    
    print(f"{name}: 主势={max_family}({max_val:.2f}) 第二={second_val:.2f} 比值={ratio:.2f}")
    return max_family, ratio


print("=== 财势阈值分析 ===")
# 真从财——侍郎从财
debug("侍郎从财", "壬", ["寅", "寅", "午", "巳"], ["丙", "庚", "壬", "乙"])

# 误判——正财格
debug("正财格(甲)", "甲", ["子", "辰", "子", "戌"], ["甲", "戊", "甲", "癸"])

# 误判——偏财格
debug("偏财格(甲)", "甲", ["子", "戌", "子", "辰"], ["甲", "戊", "甲", "癸"])

# 真从杀——李侍郎
debug("李侍郎从杀", "乙", ["酉", "酉", "酉", "申"], ["乙", "乙", "乙", "甲"])
