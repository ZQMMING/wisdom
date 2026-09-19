# -*- coding: utf-8 -*-
"""用已提取的513命例, 从DTS原文中定位用神/喜忌断言, 与引擎输出对齐."""
import re
import csv

dts_path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
csv_path = r'D:\shuntian-ziping-p0\scripts\dts_513_output.csv'

# 读取DTS原文
with open(dts_path, encoding='utf-8') as f:
    content = f.read()

# 读取引擎输出(513命例)
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    engine_rows = list(reader)

print('引擎输出命例数:', len(engine_rows))

# 对每个命例, 在原文中搜索chart, 提取用神断言
yongshen_cases = []
no_match = 0

for row in engine_rows:
    chart = row['chart']
    # 在原文中搜索chart (可能有空格分隔)
    chart_spaced = chart[:2] + ' ' + chart[2:4] + ' ' + chart[4:6] + ' ' + chart[6:8]
    # 尝试多种格式
    found_pos = -1
    for pattern in [chart, chart_spaced, chart.replace('', ' ')[1:-1]]:
        pos = content.find(pattern)
        if pos >= 0:
            found_pos = pos
            break

    if found_pos < 0:
        no_match += 1
        continue

    # 提取后800字上下文
    ctx_end = min(len(content), found_pos + 1000)
    context = content[found_pos:ctx_end]

    # 提取用神相关句子
    sentences = re.split(r'[。；！？\n]', context)
    ys_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s) > 5 and any(k in s for k in ['用神', '喜神', '忌神', '喜用', '所喜', '所忌', '宜用', '取用']):
            ys_sentences.append(s)

    if ys_sentences:
        yongshen_cases.append({
            'chart': chart,
            'sentences': ys_sentences[:3],
            'engine_primary': row.get('ys_primary', ''),
            'engine_secondary': row.get('ys_secondary', ''),
            'engine_avoid': row.get('ys_avoid', ''),
        })

print('原文中未找到的命例:', no_match)
print('有用神/喜忌断言的命例:', len(yongshen_cases))
print()
print('=== 前30个样例(原文vs引擎) ===')
for i, c in enumerate(yongshen_cases[:30]):
    print('[%d] %s' % (i+1, c['chart']))
    print('  原文: %s' % c['sentences'][0][:120])
    print('  引擎: primary=%s, secondary=%s, avoid=%s' % (c['engine_primary'], c['engine_secondary'], c['engine_avoid']))
    print()
