#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""F1-F4测试：从杀用例"""
import sys
sys.path.insert(0, '.')

from spec.root_qi import shi, calc_root_qi, STEM_WUXING
from engines.cong_ge_gates import cong_ge_pan, F0_pass


def run(name, day_stem, branches, stems):
    # 先过F0
    f0 = F0_pass(day_stem, branches, stems)
    if not f0:
        print(f"{name}: F0不通过→正格/REJECT")
        return ("正格", "REJECT", "F0未过")

    # 算势
    day_wx = STEM_WUXING[day_stem]
    from engines.cong_ge_gates import WUXING_OF
    cong_wx = WUXING_OF[day_wx]

    shi_dict = {}
    for family, wx in cong_wx.items():
        shi_dict[family] = shi(branches, stems, wx, branches[1])  # 月支是第二个

    root_qi_val = calc_root_qi(day_stem, branches, stems)
    result = cong_ge_pan(shi_dict, stems, day_stem, branches[1], root_qi_val)

    print(f"{name}: {result}")
    return result


print("=== 从杀用例测试 ===")
# C1: 癸巳 乙卯 己亥 癸酉 → 从杀·MID（食伤制杀）
r = run("C1(癸巳乙卯己亥癸酉)", "己", ["巳", "卯", "亥", "酉"], ["癸", "乙", "己", "癸"])

# C4: 庚申 辛酉 甲子 辛丑 → 从杀·CONFIRMED（印藏不透）
r = run("C4(庚申辛酉甲子辛丑)", "甲", ["申", "酉", "子", "丑"], ["庚", "辛", "甲", "辛"])

# C8: 庚申 辛酉 壬子 辛丑 → 印透→REJECT
r = run("C8(庚申辛酉壬子辛丑·印透)", "甲", ["申", "酉", "子", "丑"], ["庚", "壬", "甲", "辛"])

print("\n=== 从财用例测试 ===")
# C财+: 戊戌 己巳 甲午 己丑 → 从财·CONFIRMED（财局无比印透）
r = run("C财+(戊戌己巳甲午己丑)", "甲", ["戌", "巳", "午", "丑"], ["戊", "己", "甲", "己"])

# C财-: 戊戌 己巳 甲午 乙丑 → 从财·REJECT（乙透比劫争财）
r = run("C财-(戊戌己巳甲午乙丑·比劫透)", "甲", ["戌", "巳", "午", "丑"], ["戊", "己", "甲", "乙"])

print("\n=== 从儿用例测试 ===")
# C儿+: 丙午 丁巳 甲戌 丁丑 → 从儿·CONFIRMED（食伤局无印透）
r = run("C儿+(丙午丁巳甲戌丁丑)", "甲", ["午", "巳", "戌", "丑"], ["丙", "丁", "甲", "丁"])

# C儿-: 丙午 丁巳 甲戌 壬申 → 从儿·REJECT（壬透枭夺食）
r = run("C儿-(丙午丁巳甲戌壬申·枭透)", "甲", ["午", "巳", "戌", "申"], ["丙", "丁", "甲", "壬"])

print("\n=== 从强用例测试 ===")
# F4+: 戊寅 戊午 庚辰 己未 → 从强·CONFIRMED（印星土成局，庚日主无根）
from engines.cong_ge_gates import cong_ge_pan, WUXING_OF
from spec.root_qi import calc_root_qi

branches = ["寅", "午", "辰", "未"]
stems = ["戊", "戊", "庚", "己"]
day_stem = "庚"
day_wx = STEM_WUXING[day_stem]
cong_wx = WUXING_OF[day_wx]
shi_dict = {}
for family, wx in cong_wx.items():
    shi_dict[family] = shi(branches, stems, wx, branches[1])
# 合并印比势
shi_dict["印比"] = shi_dict.get("印", 0) + shi_dict.get("比", 0)
root_qi_val = calc_root_qi(day_stem, branches, stems)
result = cong_ge_pan(shi_dict, stems, day_stem, branches[1], root_qi_val)
print(f"F4+(戊寅戊午庚辰己未): {result}")

# F4-: 戊寅 戊午 庚辰 乙卯 → 从强·MID（乙财星透干破印）
branches = ["寅", "午", "辰", "未"]
stems = ["戊", "戊", "庚", "乙"]
shi_dict = {}
for family, wx in cong_wx.items():
    shi_dict[family] = shi(branches, stems, wx, branches[1])
shi_dict["印比"] = shi_dict.get("印", 0) + shi_dict.get("比", 0)
root_qi_val = calc_root_qi(day_stem, branches, stems)
result = cong_ge_pan(shi_dict, stems, day_stem, branches[1], root_qi_val)
print(f"F4-(戊寅戊午庚辰乙卯·财破印): {result}")
