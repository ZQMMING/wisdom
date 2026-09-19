# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')

rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

wangji_mismatch=[]
for r in rows:
    qs = r.get('queries','')
    text = r.get('judgment','')
    if '旺极' in text and 'JIWANG-HUAIJI' not in qs:
        idx = text.find('旺极')
        context = text[max(0,idx-10):idx+len('旺极')+10]
        if not any(x in context for x in ['俗以', '似乎', '看似', '地旺极', '火旺极', '土旺极', '金旺极', '水旺极', '木旺极', '财旺极', '印旺极', '官旺极', '杀旺极', '偏财旺极', '伤官旺极', '食神旺极', '比劫旺极', '羊刃旺极', '旺极反衰', '旺极所化', '旺极矣']):
            wangji_mismatch.append(r)

print(f'旺极不匹配: {len(wangji_mismatch)}')
print()
for r in wangji_mismatch:
    print(f'{r["chart"]}: root={r["root_class"]}')
    print(f'  queries: {r["queries"][:120]}')
    print(f'  judgment: {r["judgment"][:120]}')
    print()
