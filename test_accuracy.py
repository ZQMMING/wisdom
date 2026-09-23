#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""引擎准确度统计"""
import sys
sys.path.insert(0, '.')

from engines.special_pan import special_pan


cases = [
    # 全量回归41条（已知正确）
    ("李侍郎从杀", "乙", ["酉", "酉", "酉", "申"], ["乙", "乙", "乙", "甲"], "从杀·CONFIRMED"),
    ("一品夫人从儿", "癸", ["卯", "卯", "卯", "卯"], ["甲", "丁", "癸", "乙"], "从儿·CONFIRMED"),
    ("朱元璋从儿", "丁", ["辰", "戌", "丑", "未"], ["戊", "壬", "丁", "丁"], "从儿·MID_1"),
    ("侍郎从财", "壬", ["寅", "寅", "午", "巳"], ["丙", "庚", "壬", "乙"], "从财·MID_2"),
    
    # Golden cases 6条
    ("七杀成格", "甲", ["子", "申", "子", "辰"], ["甲", "壬", "甲", "丙"], "正格·官杀"),
    ("正官成格", "甲", ["子", "酉", "子", "辰"], ["甲", "癸", "甲", "壬"], "正格·官杀"),
    ("正官破格", "甲", ["子", "酉", "子", "辰"], ["甲", "癸", "甲", "丁"], "正格·官杀"),
    ("食神成格", "甲", ["子", "巳", "子", "辰"], ["甲", "己", "甲", "戊"], "正格·食伤"),
    ("食神破格", "甲", ["子", "巳", "子", "辰"], ["甲", "己", "甲", "壬"], "正格·食伤"),
]

correct = 0
total = len(cases)

print("=== 引擎准确度抽查 ===")
print()
for name, day, branches, stems, expect in cases:
    result = special_pan(stems, branches, day)
    got = f"{result[0]}·{result[1]}"
    match = expect in got
    status = "✅" if match else "❌"
    if match: correct += 1
    print(f"{status} {name}: expect={expect} | got={got}")

print()
print(f"准确率：{correct}/{total} = {correct/total*100:.1f}%")
