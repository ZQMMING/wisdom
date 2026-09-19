# -*- coding: utf-8 -*-
"""从DTS原文中提取用神/喜忌断言, 与引擎输出对齐."""
import re
import csv

dts_path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
csv_path = r'D:\shuntian-ziping-p0\scripts\dts_513_output.csv'

# 读取DTS原文
with open(dts_path, encoding='utf-8') as f:
    content = f.read()

# 读取引擎输出
with open(csv_path, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    engine_rows = {r['chart']: r for r in reader}

# 提取命例: 查找四柱模式
# 命例格式通常是: 某造/某命/乾造/坤造 + 四柱 + 大运 + 断语
chart_pattern = re.compile(r'([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]\s*){4}')

# 按命例分割
# 先找所有四柱位置
charts = []
for m in chart_pattern.finditer(content):
    chart = re.sub(r'\s+', '', m.group())
    if len(chart) == 8:
        charts.append((m.start(), m.end(), chart))

print('找到四柱位置:', len(charts))

# 对每个命例, 提取前后文(断语)
yongshen_cases = []
xiji_cases = []

for i, (start, end, chart) in enumerate(charts):
    # 提取命例上下文: 前200字 + 后500字
    ctx_start = max(0, start - 200)
    ctx_end = min(len(content), end + 800)
    context = content[ctx_start:ctx_end]

    # 检查是否有用神断言
    if '用神' in context or '喜神' in context or '忌神' in context:
        # 提取用神相关句子
        sentences = re.split(r'[。；！？\n]', context)
        ys_sentences = [s.strip() for s in sentences if any(k in s for k in ['用神', '喜神', '忌神', '喜用', '忌神', '所喜', '所忌'])]
        if ys_sentences:
            yongshen_cases.append({
                'chart': chart,
                'sentences': ys_sentences[:5],
                'engine_primary': engine_rows.get(chart, {}).get('ys_primary', ''),
                'engine_secondary': engine_rows.get(chart, {}).get('ys_secondary', ''),
                'engine_avoid': engine_rows.get(chart, {}).get('ys_avoid', ''),
            })

print('有用神/喜忌断言的命例:', len(yongshen_cases))
print()
print('=== 前20个样例 ===')
for i, c in enumerate(yongshen_cases[:20]):
    print('[%d] %s' % (i+1, c['chart']))
    print('  原文: %s' % c['sentences'][0][:100])
    print('  引擎: primary=%s, secondary=%s, avoid=%s' % (c['engine_primary'], c['engine_secondary'], c['engine_avoid']))
    print()
