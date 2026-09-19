# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))
rows=rows[:100]
print(f'案例数: {len(rows)}')

checks = [
    ('身旺', ['HEAVY-ROOT', 'YIN-PARTY', 'BIJIE-PARTY'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '身旺者', '身旺逢', '必要身旺']),
    ('身强', ['HEAVY-ROOT', 'YIN-PARTY', 'BIJIE-PARTY'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '身强者']),
    ('身弱', ['LIGHT-ROOT', 'JIRUO-WUGEN'], ['俗以', '俗见', '俗论', '俗', '财多', '煞重', '泄重', '似乎', '看似', '弱中', '弱变', '弱不', '非身弱', '不论身', '身弱者']),
    ('日主旺', ['HEAVY-ROOT', 'YIN-PARTY', 'BIJIE-PARTY'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似']),
    ('日主弱', ['LIGHT-ROOT'], ['俗以', '俗见', '俗论', '俗', '财多', '煞重', '泄重', '似乎', '看似', '弱中', '弱变', '弱不', '非身弱', '不论身']),
    ('中和', ['ZHONG-HE'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似']),
    ('旺极', ['JIWANG-HUAIJI'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '地旺极', '火旺极', '土旺极', '金旺极', '水旺极', '木旺极']),
    ('衰极', ['JISHUAI-CONGSHENG'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似', '天衰极', '火衰极', '土衰极', '金衰极', '水衰极', '木衰极']),
    ('弱极', ['JIRUO-WUGEN'], ['俗以', '俗见', '俗论', '俗', '似乎', '看似']),
]

match = 0
total = 0
mismatches = []

for r in rows:
    qs = r.get('queries','')
    text = r.get('judgment','')
    
    for kw, engine_qs, exclude in checks:
        if kw in text:
            idx = text.find(kw)
            context = text[max(0,idx-20):idx+len(kw)+20]
            if any(ex in context for ex in exclude):
                continue
            total += 1
            if any(eq in qs for eq in engine_qs):
                match += 1
            else:
                mismatches.append((r['chart'], kw, engine_qs, qs[:80], r.get('book','')))

print(f'正面判断匹配: {match}/{total} = {match/total*100:.1f}%' if total>0 else '无对比样本')
print()
print(f'不匹配:')
for m in mismatches:
    print(f'  [{m[4]}] {m[0]}: 原文"{m[1]}" 引擎应有{m[2]} 实际有{m[3][:60]}')
