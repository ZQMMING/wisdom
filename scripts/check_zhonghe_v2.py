# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

zhonghe_mismatch=[]
for r in rows:
    qs = r.get('queries','')
    text = r.get('judgment','')
    if '中和' in text and 'ZHONG-HE' not in qs:
        idx = text.find('中和')
        context = text[max(0,idx-10):idx+len('中和')+10]
        if not any(x in context for x in ['俗以', '似乎', '看似']):
            zhonghe_mismatch.append(r)

print(f'中和不匹配: {len(zhonghe_mismatch)}')
print()
for r in zhonghe_mismatch[:15]:
    print(f'{r["chart"]}: root={r["root_class"]}')
    print(f'  queries: {r["queries"][:100]}')
    print(f'  judgment: {r["judgment"][:100]}')
    print()
