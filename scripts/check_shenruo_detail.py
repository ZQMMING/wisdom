# -*- coding: utf-8 -*-
import csv, sys
sys.path.insert(0,'.')
rows=list(csv.DictReader(open('scripts/all_cases_output.csv',encoding='utf-8-sig')))

# 身弱不匹配案例
targets=['戊辰己巳庚午辛未','丙子丁丑戊寅己卯','丁未丁未己亥丁卯','癸卯庚申庚戌甲申','甲寅癸酉乙酉乙酉']

for r in rows:
    if r['chart'] in targets:
        print(f"\n{'='*60}")
        print(f"chart: {r['chart']}")
        print(f"root_class: {r['root_class']}")
        print(f"queries: {r['queries'][:200]}")
        # 找身弱上下文
        idx=r['judgment'].find('身弱')
        if idx>=0:
            print(f"身弱上下文: ...{r['judgment'][max(0,idx-30):idx+len('身弱')+30]}...")
