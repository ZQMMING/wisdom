# -*- coding: utf-8 -*-
"""验证M3-B输出"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build
from engines.common.daymaster_tian_he import build_tian_he

# 测试案例: 庚午 乙酉 甲子 乙亥(两乙合庚,甲日隔之→隔位不争妒)
p = {'year': '庚午', 'month': '乙酉', 'day': '甲子', 'hour': '乙亥'}
f = l0build(p)
th = build_tian_he(p, f)
print('案例: 庚午 乙酉 甲子 乙亥(两乙合庚,甲日隔之)')
for pair in th['he_pairs']:
    print('  {}↔{}:'.format(pair['stems'][0], pair['stems'][1]))
    print('    目标: {}({})'.format(pair['he_target'], pair['he_target_pos']))
    print('    有竞争者: {}'.format(pair['has_rival']))
    print('    竞争者: {}'.format(pair['rival_stems']))
    print('    是争合: {}'.format(pair['is_competition']))
    print('    争合类型: {}'.format(pair['competition_type']))
