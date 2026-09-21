# -*- coding: utf-8 -*-
"""诊断: 真正合化成功案例(得月令+四支局全)
《子平真诠》: 化出之物, 得时乘令, 四支局全……方为大贵
"""
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build
from engines.common.daymaster_tian_he import build_tian_he
import json
from collections import defaultdict

# 化神五行对应的地支局
HUASHEN_JU = {
    '土': {'辰', '戌', '丑', '未'},  # 土局
    '金': {'巳', '酉', '丑'},  # 巳酉丑金局
    '水': {'申', '子', '辰'},  # 申子辰水局
    '木': {'亥', '卯', '未'},  # 亥卯未木局
    '火': {'寅', '午', '戌'},  # 寅午戌火局
}

with open('scripts/dts_cases_extracted.json', 'r', encoding='utf-8') as f:
    cases = json.load(f)

total = 0
on_month_count = 0
full_ju_count = 0
truly_success = 0  # 得月令+四支局全

examples = []

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
        
        pairs = th.get('he_pairs', [])
        if not pairs:
            continue
        
        dm = p['day'][0]
        all_zhi = [p[k][1] for k in ('year', 'month', 'day', 'hour')]
        
        case_on_month = False
        case_full_ju = False
        case_truly = False
        
        for pair in pairs:
            huashen = pair.get('huashen_wuxing')
            on_month = pair.get('huashen_on_month_qi', False)
            
            # 检查四支局全
            ju_zhi = HUASHEN_JU.get(huashen, set())
            ju_count = sum(1 for z in all_zhi if z in ju_zhi)
            has_full_ju = ju_count >= 3  # 至少3个地支在化神局中
            
            if on_month:
                case_on_month = True
            if has_full_ju:
                case_full_ju = True
            if on_month and has_full_ju:
                case_truly = True
                
                # 记录真正合化成功的案例
                if len(examples) < 15:
                    stems = pair.get('stems', [])
                    positions = pair.get('pillars', [])
                    examples.append({
                        'case_id': f"L{case.get('src_line', '?')}",
                        'pillars': f"{p['year']} {p['month']} {p['day']} {p['hour']}",
                        'dm': dm,
                        'pair': f"{stems[0]}-{stems[1]}",
                        'positions': f"{positions[0]}-{positions[1]}",
                        'huashen': huashen,
                        'ju_count': ju_count,
                    })
        
        if case_on_month:
            on_month_count += 1
        if case_full_ju:
            full_ju_count += 1
        if case_truly:
            truly_success += 1
        
        total += 1
        
    except Exception as e:
        continue

print('=' * 70)
print('诊断: 真正合化成功案例(得月令+四支局全)')
print('=' * 70)
print()
print(f'总案例数: {total}')
print(f'化神得月令: {on_month_count} ({on_month_count/total*100:.1f}%)')
print(f'四支局全(化神局≥3支): {full_ju_count} ({full_ju_count/total*100:.1f}%)')
print(f'真正合化成功(得月令+四支局全): {truly_success} ({truly_success/total*100:.1f}%)')
print()
print('真正合化成功典型案例(前15):')
for ex in examples:
    print(f"  {ex['case_id']}: {ex['pillars']}")
    print(f"    日主:{ex['dm']} | 合对:{ex['pair']}({ex['positions']}) | 化神:{ex['huashen']} | 局支数:{ex['ju_count']}")
print()
print('=' * 70)
print('结论:')
pct = truly_success / total * 100
if pct < 5:
    print(f'  真正合化成功案例仅{truly_success}例({pct:.1f}%), 影响面极小')
    print('  → 非日主天干合化修正价值有限, 标记为低优先级')
elif pct < 10:
    print(f'  真正合化成功案例{truly_success}例({pct:.1f}%), 影响面较小')
    print('  → 可考虑修正层, 但优先级低')
else:
    print(f'  真正合化成功案例{truly_success}例({pct:.1f}%), 影响面较大')
    print('  → 需要系统处理')
print('=' * 70)
