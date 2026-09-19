# -*- coding: utf-8 -*-
import csv
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')

# 读取CSV
with open(r'D:\shuntian-ziping-p0\scripts\dts_513_output.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# 统计不匹配类型
mismatch_types = {
    '引擎SUPPORT原文JI': 0,
    '引擎SUPPORT原文XI(多标签)': 0,
    '引擎SUPPRESS原文XI': 0,
    '引擎SUPPRESS原文JI(多标签)': 0,
    '引擎NEUTRAL原文XI': 0,
    '引擎NEUTRAL原文JI': 0,
    '其他': 0,
}

# 读取原文提取结果
from scripts.calc_dayun_xiji_accuracy import extract_dayun_xiji
dts_path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
with open(dts_path, encoding='utf-8-sig') as f:
    dts_text = f.read()

results = extract_dayun_xiji(dts_text)

# 统计不匹配
for case in results:
    chart = case['chart']
    for dy in case['dayun_xiji']:
        ganzhi = dy['ganzhi']
        expected = dy['xiji']
        # 查找引擎输出
        engine_label = None
        for row in rows:
            if row.get('chart', '').replace(' ', '') == chart.replace(' ', ''):
                dx = row.get('dayun_xiji', '')
                if ganzhi in dx:
                    # 解析引擎标签
                    parts = dx.split(';')
                    for p in parts:
                        if p.startswith(ganzhi + ':'):
                            engine_label = p.split(':')[1] if ':' in p else ''
                            break
                break
        if engine_label is None:
            continue
        # 判断不匹配类型
        engine_has_xi = 'SUPPORT' in engine_label
        engine_has_ji = 'SUPPRESS' in engine_label
        expected_xi = expected == 'XI'
        expected_ji = expected == 'JI'
        if engine_has_xi and not engine_has_ji and expected_ji:
            mismatch_types['引擎SUPPORT原文JI'] += 1
        elif engine_has_xi and expected_xi and engine_has_ji:
            mismatch_types['引擎SUPPORT原文XI(多标签)'] += 1
        elif engine_has_ji and not engine_has_xi and expected_xi:
            mismatch_types['引擎SUPPRESS原文XI'] += 1
        elif engine_has_ji and expected_ji and engine_has_xi:
            mismatch_types['引擎SUPPRESS原文JI(多标签)'] += 1
        elif not engine_has_xi and not engine_has_ji and expected_xi:
            mismatch_types['引擎NEUTRAL原文XI'] += 1
        elif not engine_has_xi and not engine_has_ji and expected_ji:
            mismatch_types['引擎NEUTRAL原文JI'] += 1
        else:
            mismatch_types['其他'] += 1

print('=== 不匹配类型分布 ===')
for k, v in sorted(mismatch_types.items(), key=lambda x: -x[1]):
    print(f'{k}: {v}')
print(f'总计: {sum(mismatch_types.values())}')
