# -*- coding: utf-8 -*-
import csv
rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))
exclude=['俗以','俗见','俗论','俗','似乎','看似','地旺极','火旺极','土旺极','金旺极','水旺极','木旺极','财旺极','印旺极','官旺极','杀旺极','偏财旺极','伤官旺极','食神旺极','比劫旺极','羊刃旺极','旺极反衰','旺极所化','旺极矣','极旺极衰','身印旺地','天元太弱','七杀当旺','官星旺运','乘权当令','林注','身旺极贫','旺极之象征']
for r in rows:
    text=r['judgment']
    if '旺极' not in text:
        continue
    idx=text.find('旺极')
    context=text[max(0,idx-10):idx+len('旺极')+10]
    if any(ex in context for ex in exclude):
        continue
    if 'JIWANG-HUAIJI' not in r['queries']:
        print('chart:', r['chart'])
        print('context:', repr(context))
        print('full context: ...'+text[max(0,idx-30):idx+len('旺极')+30]+'...')
        break
