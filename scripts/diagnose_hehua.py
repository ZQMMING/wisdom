# -*- coding: utf-8 -*-
"""诊断: 非日主天干合化的影响面统计
"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build
from engines.common.daymaster_tian_he import build_tian_he
import json
from collections import defaultdict

with open('scripts/dts_cases_extracted.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

total = 0
has_he = 0
has_nondm_he = 0
has_huashen_on_month = 0

he_by_pair = defaultdict(int)
nondm_he_examples = []

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
        
        dm = p['day'][0]
        pairs = th.get('he_pairs', [])
        
        if not pairs:
            continue
        
        has_he += 1
        
        # 检查是否有非日主参与的合化
        has_nondm = False
        for pair in pairs:
            stems = pair.get('stems', [])
            pillars_pos = pair.get('pillars', [])
            
            # 判断是否有非日主参与
            for i, pos in enumerate(pillars_pos):
                if pos != 'day':
                    has_nondm = True
                    break
            
            # 统计合对类型
            pair_key = '-'.join(sorted(stems))
            he_by_pair[pair_key] += 1
            
            # 记录非日主合化案例
            if has_nondm and len(nondm_he_examples) < 10:
                nondm_he_examples.append({
                    'case_id': f"L{case.get('src_line', '?')}",
                    'pillars': f"{p['year']} {p['month']} {p['day']} {p['hour']}",
                    'pair': f"{stems[0]}-{stems[1]}",
                    'positions': f"{pillars_pos[0]}-{pillars_pos[1]}",
                    'huashen': pair.get('huashen_wuxing'),
                    'on_month': pair.get('huashen_on_month_qi'),
                })
        
        if has_nondm:
            has_nondm_he += 1
        
        # 统计化神得月令的案例
        for pair in pairs:
            if pair.get('huashen_on_month_qi'):
                has_huashen_on_month += 1
                break
        
        total += 1
        
    except Exception as e:
        continue

print('=' * 70)
print('诊断: 非日主天干合化的影响面统计')
print('=' * 70)
print()
print(f'总案例数: {total}')
print(f'有天干合化的案例: {has_he} ({has_he/total*100:.1f}%)')
print(f'有非日主天干合化的案例: {has_nondm_he} ({has_nondm_he/total*100:.1f}%)')
print(f'化神得月令的案例: {has_huashen_on_month} ({has_huashen_on_month/total*100:.1f}%)')
print()
print('合对类型分布:')
for pair, count in sorted(he_by_pair.items(), key=lambda x: -x[1]):
    print(f'  {pair}: {count}例')
print()
print('非日主合化典型案例(前10):')
for ex in nondm_he_examples:
    print(f"  {ex['case_id']}: {ex['pillars']}")
    print(f"    合对: {ex['pair']} ({ex['positions']}) | 化神: {ex['huashen']} | 得月令: {ex['on_month']}")
print()
print('=' * 70)
print('初步判断:')
if has_nondm_he / total < 0.1:
    print('  影响面<10%, 非日主天干合化修正优先级低')
elif has_nondm_he / total < 0.2:
    print('  影响面10-20%, 可考虑修正层')
else:
    print('  影响面>20%, 需要系统处理')
print('=' * 70)
