#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')

from engines.axis_xiuqi import xiuqi_axis
from engines.axis_fude import fude_axis
from engines.special_merge import merge

# 对照用例：局不全+不见辰
# 乙巳 乙酉 庚寅 甲申：乙庚化金，酉月，巳酉缺丑（局不全），不见辰
key = "乙巳 乙酉 庚寅 甲申"
pillars = {}
stems = key.split()
pillars['year'] = stems[0]
pillars['month'] = stems[1]
pillars['day'] = stems[2]
pillars['hour'] = stems[3]
facts = {"month_branch": stems[1][1]}
x = xiuqi_axis(pillars, facts, [])
f = fude_axis(pillars, facts, [])
result = merge(x, f, key)
print(f"P2对照：{key}")
print(f"  pattern: {result[0]}")
print(f"  type: {result[1]}")
print(f"  conf: {result[2]}")
print(f"  score: {result[3]}")
print(f"  b3(逢龙): {x.b3}")
print(f"  b5(支局全): {x.b5}")
print(f"  gate_debug: {x.gate_debug}")

print()
# Q4：局不全+见辰
key2 = "甲子 丁卯 壬午 甲辰"
pillars2 = {}
stems2 = key2.split()
pillars2['year'] = stems2[0]
pillars2['month'] = stems2[1]
pillars2['day'] = stems2[2]
pillars2['hour'] = stems2[3]
facts2 = {"month_branch": stems2[1][1]}
x2 = xiuqi_axis(pillars2, facts2, [])
f2 = fude_axis(pillars2, facts2, [])
result2 = merge(x2, f2, key2)
print(f"Q4对照：{key2}")
print(f"  pattern: {result2[0]}")
print(f"  type: {result2[1]}")
print(f"  conf: {result2[2]}")
print(f"  score: {result2[3]}")
print(f"  b3(逢龙): {x2.b3}")
print(f"  b5(支局全): {x2.b5}")
