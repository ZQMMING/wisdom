# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.wuxing_power import build_wuxing_power, BRANCH_WX

pillars = {'year': ('丁', '巳'), 'month': ('癸', '丑'), 'day': ('丁', '卯'), 'hour': ('丙', '午')}
facts = build(pillars)
wpo = build_wuxing_power(pillars, facts)

print('=== 丁巳癸丑丁卯丙午 调试 ===')
print('day_master:', facts['day_stem'])
print('month_branch:', pillars['month'][1])
print()

# 输出每个五行的详细信息
for wx in ['金', '木', '水', '火', '土']:
    d = wpo['detail'].get(wx, {})
    print(f'{wx}:')
    print(f'  stem_count: {d.get("stem_count", "N/A")}')
    print(f'  ben_count: {d.get("ben_count", "N/A")}')
    print(f'  zhong_count: {d.get("zhong_count", "N/A")}')
    print(f'  yu_count: {d.get("yu_count", "N/A")}')
    print(f'  ling: {d.get("ling", "N/A")}')
    print(f'  keys: {list(d.keys())}')
    print()
