# -*- coding: utf-8 -*-
"""深度交叉对比v3: 精确匹配当前案例断语"""
import csv, re, sys
sys.path.insert(0,'.')

lines=open(r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt',encoding='utf-8').readlines()
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
print(f'总案例: {len(rows)}')

# 找到每个案例的断语范围: 从大运行后开始, 到下一个"八字："或"大运："或"===="为止
def get_case_text(line_no):
    """取当前案例的断语文本"""
    start = line_no + 2  # 大运行后
    end = start
    while end < len(lines):
        l = lines[end].strip()
        if l.startswith('八字：') or l.startswith('大运：') or l.startswith('====') or l.startswith('【'):
            break
        end += 1
    return ''.join(lines[start:end])

checks = [
    ('身旺', ['HEAVY-ROOT', 'DESHI-BUWANG'], ['俗以', '俗见', '俗论', '俗']),
    ('身强', ['HEAVY-ROOT'], ['俗以', '俗见', '俗论', '俗']),
    ('身弱', ['LIGHT-ROOT', 'JIRUO-WUGEN'], ['俗以', '俗见', '俗论', '俗']),
    ('日主旺', ['HEAVY-ROOT'], ['俗以', '俗见', '俗论', '俗']),
    ('日主弱', ['LIGHT-ROOT'], ['俗以', '俗见', '俗论', '俗']),
    ('得地', ['HEAVY-ROOT'], ['俗以', '俗见', '俗论', '俗']),
    ('得时', ['DESHI-BUWANG'], ['俗以', '俗见', '俗论', '俗']),
    ('得令', ['DESHI-BUWANG'], ['俗以', '俗见', '俗论', '俗']),
    ('失令', ['SHISHI-BURUO'], ['俗以', '俗见', '俗论', '俗']),
    ('得势', ['YIN-PARTY', 'BIJIE-PARTY'], ['俗以', '俗见', '俗论', '俗']),
]

match = 0
total = 0
mismatches = []

for r in rows:
    line_no = int(r['line'])
    qs = r.get('queries','')
    text = get_case_text(line_no)
    
    for kw, engine_qs, exclude in checks:
        if kw in text:
            # 排除俗论
            idx = text.find(kw)
            context = text[max(0,idx-15):idx+len(kw)+15]
            if any(ex in context for ex in exclude):
                continue
            total += 1
            if any(eq in qs for eq in engine_qs):
                match += 1
            else:
                mismatches.append((r['chart'], kw, engine_qs, qs[:80]))

print(f'正面判断匹配: {match}/{total} = {match/total*100:.1f}%' if total>0 else '无对比样本')
print()
print(f'不匹配前15个:')
for m in mismatches[:15]:
    print(f'  {m[0]}: 原文"{m[1]}" 引擎应有{m[2]} 实际有{m[3][:60]}')
