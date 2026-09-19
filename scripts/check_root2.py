# -*- coding: utf-8 -*-
import csv
rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))
for r in rows:
    if r['chart']=='甲午乙未丙申丁酉':
        print('root_class:', repr(r['root_class']))
        print('queries:', r['queries'][:200])
        print('HEAVY-ROOT in qs:', 'HEAVY-ROOT' in r['queries'])
        break
