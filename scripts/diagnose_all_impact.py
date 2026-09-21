# -*- coding: utf-8 -*-
"""全面检测: 互动级/格局识别/大运分看影响面统计
"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build, WUXING
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.special_pattern import build_special_patterns
from engines.common.climate_structure import build_climate_structure
from engines.common.wuxing_power import build_wuxing_power
import json
from collections import defaultdict

with open('scripts/dts_cases_extracted.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

total = 0
has_special = 0
has_hehua = 0
has_sanhe = 0
has_sanhui = 0

special_types = defaultdict(int)
hehua_types = defaultdict(int)

for case in cases:
    pillars = case.get('pillars', [])
    if len(pillars) < 4:
        continue
    
    p = {
        'year': pillars[0],
        'month': pillars[1],
        'day': pillars[2],
        'hour': pillars[3],
    }
    
    try:
        f = l0build(p)
        th = build_tian_he(p, f)
        wp = build_wuxing_power(p, f, th)
        cls = build_climate_structure(p, f, th)
        spp = build_special_patterns(p, f, wp, th, cls)
        
        zhuanwang = spp.get('zhuanwang', '')
        cong_type = spp.get('cong_type', '')
        
        if zhuanwang:
            has_special += 1
            special_types[zhuanwang] += 1
        elif cong_type:
            has_special += 1
            special_types['从格-' + cong_type] += 1
        
        # 天干合化
        he_pairs = th.get('he_pairs', [])
        if he_pairs:
            has_hehua += 1
            for pair in he_pairs:
                huashen = pair.get('huashen_wuxing', '')
                on_month = pair.get('huashen_on_month_qi', False)
                hehua_types[huashen + ('(得月令)' if on_month else '(不得月令)')] += 1
        
        # 地支三合/三会
        cf = f.get('combination_facts', {})
        sanhe = cf.get('sanhe', [])
        sanhui = cf.get('sanhui', [])
        if sanhe:
            has_sanhe += 1
        if sanhui:
            has_sanhui += 1
        
        total += 1
        
    except Exception as e:
        continue

print('=' * 70)
print('全面检测: 影响面统计')
print('=' * 70)
print()
print(f'总案例数: {total}')
print()

print('--- 特殊格局 ---')
print(f'有特殊格局的案例: {has_special} ({has_special/total*100:.1f}%)')
for stype, count in sorted(special_types.items(), key=lambda x: -x[1]):
    print(f'  {stype}: {count}例 ({count/total*100:.1f}%)')
print()

print('--- 天干合化 ---')
print(f'有天干合化的案例: {has_hehua} ({has_hehua/total*100:.1f}%)')
print('合化类型分布:')
for htype, count in sorted(hehua_types.items(), key=lambda x: -x[1]):
    print(f'  {htype}: {count}例')
print()

print('--- 地支三合/三会 ---')
print(f'有三合局的案例: {has_sanhe} ({has_sanhe/total*100:.1f}%)')
print(f'有三会局的案例: {has_sanhui} ({has_sanhui/total*100:.1f}%)')
print()

print('=' * 70)
print('影响面评估:')
print('  特殊格局: ' + f'{has_special/total*100:.1f}%')
print('  天干合化: ' + f'{has_hehua/total*100:.1f}%')
print('  地支三合: ' + f'{has_sanhe/total*100:.1f}%')
print('  地支三会: ' + f'{has_sanhui/total*100:.1f}%')
print('=' * 70)
