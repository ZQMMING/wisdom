# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

shuaiji_mismatch=[]
for r in rows:
    qs = r.get('queries','')
    text = r.get('judgment','')
    if '衰极' in text and 'JISHUAI-CONGSHENG' not in qs:
        idx = text.find('衰极')
        context = text[max(0,idx-10):idx+len('衰极')+10]
        if not any(x in context for x in ['俗以', '似乎', '看似', '天衰极', '火衰极', '土衰极', '金衰极', '水衰极', '木衰极']):
            shuaiji_mismatch.append(r)

print(f'衰极不匹配: {len(shuaiji_mismatch)}')
print()
for r in shuaiji_mismatch:
    print(f'{r["chart"]}: root={r["root_class"]}')
    print(f'  queries: {r["queries"][:120]}')
    print(f'  judgment: {r["judgment"][:120]}')
    print()
