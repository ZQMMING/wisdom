# -*- coding: utf-8 -*-
import json, sys, csv
sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network
from engines.common.daymaster_power_queries import run_queries

lines=open(r'D:\顺天系统资料\古书独立案例JSONL\all_cases.jsonl',encoding='utf-8').readlines()
print(f'总案例: {len(lines)}')

GZ = '甲乙丙丁戊己庚辛壬癸'
BZ = '子丑寅卯辰巳午未申酉戌亥'

def parse_chart(chart):
    chart=chart.strip()
    if len(chart) < 8:
        return None
    p={}
    keys=['year','month','day','hour']
    for i,k in enumerate(keys):
        s=chart[i*2:i*2+2]
        if s[0] not in GZ or s[1] not in BZ:
            return None
        p[k]=[s[0],s[1]]
    return p

results=[]
ok=0
fail=0
for i,l in enumerate(lines):
    d=json.loads(l)
    chart=d.get('chart','')
    p=parse_chart(chart)
    if not p:
        fail+=1
        continue
    try:
        f=build(p)
        pa=build_power_structure(p)
        hst={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
        rc=build_root_classes(p,hst);tc=build_tou_cang(f);wx=build_wang_xiang(f,f['day_stem'])
        rr=build_root_relations(rc,f['combination_facts']);ts=build_two_side(rc,tc,rr)
        bt=build_branch_tiers(p,f);th=build_tian_he(p,f)
        net=build_power_network(pa,rc,tc,wx,rr,ts,branch_tier=bt,tian_he=th,facts=f)
        qs=run_queries(net)
        supported=[q['query_id'].replace('ZP-160-QUERY-','') for q in qs if q['state']=='SUPPORTED']
        results.append({
            'book': d.get('book',''),
            'id': d.get('id',''),
            'chart': chart,
            'day_stem': f['day_stem'],
            'root_class': net['dimensions']['ROOT'].get('root_weight_class',''),
            'queries': '|'.join(supported),
            'judgment': d.get('judgment','')[:200],
            'wangshuai_kw': d.get('wangshuai_kw',''),
        })
        ok+=1
    except Exception as e:
        fail+=1
        if fail<=5:
            print(f'FAIL {chart}: {e}')
    if (i+1)%500==0:
        print(f'进度: {i+1}/{len(lines)}, ok={ok}, fail={fail}')

print(f'完成: ok={ok}, fail={fail}')

with open('scripts/all_cases_output.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['book','id','chart','day_stem','root_class','queries','judgment','wangshuai_kw'])
    w.writeheader()
    w.writerows(results)
print(f'导出: scripts/all_cases_output.csv ({len(results)}条)')
