# -*- coding: utf-8 -*-
"""验证M2-A/M2-B输出
"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build
from engines.common.daymaster_tian_he import build_tian_he

# 测试案例
test_cases = [
    ('紧贴', {'year': '甲子', 'month': '己巳', 'day': '庚午', 'hour': '戊寅'}),
    ('隔一位', {'year': '甲子', 'month': '丁卯', 'day': '己亥', 'hour': '戊辰'}),
    ('遥隔', {'year': '甲子', 'month': '丙寅', 'day': '庚午', 'hour': '己巳'}),
    ('阻隔', {'year': '甲申', 'month': '丙寅', 'day': '庚午', 'hour': '己卯'}),
]

print('=' * 70)
print('M2-A/M2-B 验证')
print('=' * 70)

for name, p in test_cases:
    print(f'\n--- {name}: {p["year"]} {p["month"]} {p["day"]} {p["hour"]} ---')
    f = l0build(p)
    th = build_tian_he(p, f)
    for pair in th.get('he_pairs', []):
        print(f'  {pair["stems"][0]}↔{pair["stems"][1]} ({pair["pillars"][0]}↔{pair["pillars"][1]}):')
        print(f'    位置距离: {pair["position_distance"]}')
        print(f'    间干: {pair["intervening_stems"]}')
        print(f'    有阻隔: {pair["has_blocking_intervening"]}')
        if pair['blocking_stems']:
            print(f'    阻隔神: {pair["blocking_stems"]}')

print('\n' + '=' * 70)
print('验证完成')
print('=' * 70)
