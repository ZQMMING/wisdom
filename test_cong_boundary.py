#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从格族交界对照例——只变一个变量，定F0判据"""
import sys
sys.path.insert(0, '.')

from engines.axis_xiuqi import xiuqi_axis
from engines.axis_fude import fude_axis
from engines.special_merge import merge


def run_case(name, pillars_str, expect_reason):
    pillars = {}
    stems = pillars_str.split()
    pillars['year'] = stems[0]
    pillars['month'] = stems[1]
    pillars['day'] = stems[2]
    pillars['hour'] = stems[3]
    month_branch = stems[1][1]
    facts = {"month_branch": month_branch}

    x = xiuqi_axis(pillars, facts, [])
    f = fude_axis(pillars, facts, [])
    result = merge(x, f, pillars_str)

    print(f"\n=== {name} ===")
    print(f"四柱: {pillars_str}")
    print(f"预期原因: {expect_reason}")
    print(f"输出: {result[0]} / {result[1]} / {result[2]}")
    print(f"b5(化神局全): {x.b5}, b3(逢龙): {x.b3}")
    return result


# 主对：巳亥冲 vs 巳子无冲
C1 = run_case("C1(有冲·巳亥冲)", "癸巳 乙卯 己亥 癸酉", "亥冲巳→印根俱废→可从")
C2 = run_case("C2(无冲·巳子无冲)", "癸巳 乙卯 己亥 癸子", "子不冲巳→巳中丙戊俱在→根犹存")

# 副对：余气根是否算根
C3 = run_case("C3(有微根·未中乙)", "庚申 辛酉 甲午 辛未", "未中乙木余气→算不算根？")
C4 = run_case("C4(无微根·巳中无木)", "庚申 辛酉 甲午 辛巳", "巳中无木→从杀")

print("\n\n=== 决策表 ===")
print(f"C1(有冲): {C1[2]}")
print(f"C2(无冲): {C2[2]}")
print(f"C3(有余气根): {C3[2]}")
print(f"C4(无余气根): {C4[2]}")
