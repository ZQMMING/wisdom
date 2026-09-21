# -*- coding: utf-8 -*-
"""验证M3-A输出"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build
from engines.common.daymaster_tian_he import build_tian_he

# 测试案例1: 乙酉日, 庚在时干(本身之合)
p1 = {'year': '戊寅', 'month': '甲寅', 'day': '乙酉', 'hour': '庚辰'}
f1 = l0build(p1)
th1 = build_tian_he(p1, f1)
print('案例1: 乙酉日, 庚在时干(本身之合)')
for pair in th1['he_pairs']:
    print('  {}↔{}:'.format(pair['stems'][0], pair['stems'][1]))
    print('    日主本身之合: {}'.format(pair['is_daymaster_self_he']))
    print('    主体: {}({})'.format(pair['he_subject'], pair['he_subject_pos']))
    print('    目标: {}({})'.format(pair['he_target'], pair['he_target_pos']))

print()

# 测试案例2: 庚寅年乙酉月(他干合他干)
p2 = {'year': '庚寅', 'month': '乙酉', 'day': '戊午', 'hour': '壬子'}
f2 = l0build(p2)
th2 = build_tian_he(p2, f2)
print('案例2: 庚寅年乙酉月(他干合他干)')
for pair in th2['he_pairs']:
    print('  {}↔{}:'.format(pair['stems'][0], pair['stems'][1]))
    print('    日主本身之合: {}'.format(pair['is_daymaster_self_he']))
    print('    主体: {}({})'.format(pair['he_subject'], pair['he_subject_pos']))
    print('    目标: {}({})'.format(pair['he_target'], pair['he_target_pos']))
