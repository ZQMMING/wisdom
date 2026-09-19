# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')
rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

exclude=['俗以','俗见','俗论','俗','似乎','看似','地旺极','火旺极','土旺极','金旺极','水旺极','木旺极','财旺极','印旺极','官旺极','杀旺极','偏财旺极','伤官旺极','食神旺极','比劫旺极','羊刃旺极','旺极反衰','旺极所化','旺极矣','极旺极衰','身印旺地','天元太弱','七杀当旺','官星旺运','乘权当令']

mismatch=[]
for r in rows:
    text=r['judgment']
    if '旺极' not in text:
        continue
    idx=text.find('旺极')
    context=text[max(0,idx-20):idx+len('旺极')+20]
    if any(ex in context for ex in exclude):
        continue
    if 'JIWANG-HUAIJI' not in r['queries']:
        mismatch.append(r)

print(f'旺极不匹配: {len(mismatch)}')
for r in mismatch:
    print(f"\n{'='*60}")
    print(f"chart: {r['chart']}")
    print(f"root_class: {r['root_class']}")
    print(f"queries: {r['queries'][:200]}")
    idx=r['judgment'].find('旺极')
    print(f"旺极上下文: ...{r['judgment'][max(0,idx-40):idx+len('旺极')+40]}...")
