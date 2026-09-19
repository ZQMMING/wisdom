# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.wuxing_power import build_wuxing_power
from engines.common.l0_fact_builder import build as build_l0

with open(r'D:\shuntian-ziping-p0\scripts\dts_513_output.csv', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

ratios = []
for i, row in enumerate(rows[:200]):  # 分析前200个
    chart = row['chart']
    if not chart or len(chart) < 8:
        continue
    pillars = {
        'year': [chart[0], chart[1]],
        'month': [chart[2], chart[3]],
        'day': [chart[4], chart[5]],
        'hour': [chart[6], chart[7]],
    }
    try:
        facts = build_l0(pillars)
        wpo = build_wuxing_power(pillars, facts)
        wp = wpo.get('wuxing_power', {})
        total_all = sum(v.get('total', 0) for v in wp.values())
        primary = row.get('ys_primary', '')
        if primary and total_all > 0:
            ratio = wp.get(primary, {}).get('total', 0) / total_all
            ratios.append(ratio)
    except Exception as e:
        pass

print(f'样本数: {len(ratios)}')
if ratios:
    print(f'最小值: {min(ratios):.3f}')
    print(f'最大值: {max(ratios):.3f}')
    print(f'平均值: {sum(ratios)/len(ratios):.3f}')
    print()
    print('分布:')
    bins = [(0, 0.1), (0.1, 0.15), (0.15, 0.2), (0.2, 0.25), (0.25, 0.3), (0.3, 0.35), (0.35, 0.4), (0.4, 1.0)]
    for low, high in bins:
        count = sum(1 for r in ratios if low <= r < high)
        print(f'  {low:.2f}-{high:.2f}: {count} ({count/len(ratios)*100:.1f}%)')
