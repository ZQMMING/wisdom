# -*- coding: utf-8 -*-
"""DTS 513命例: 四柱+后续断语 配对, 标注意旺弱关键词, 跑引擎对照."""
import re, sys, json, collections
sys.path.insert(0, '.')

path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
GZ = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')

KW = ['身旺','身弱','日主旺','日主弱','得地','得时','得令','失令','得势','身强','身衰','衰弱','强旺','旺衰','旺','衰','强','弱']
records = []
for i, ln in enumerate(lines):
    s = ln.strip()
    four_pairs = None
    if s.startswith('八字'):
        body = s.split('：',1)[-1].split(':',1)[-1].strip()
        pp = GZ.findall(body)
        if len(pp)==4: four_pairs = pp
    else:
        pp = GZ.findall(s)
        if len(pp)==4 and len(s)<60:
            cleaned = GZ.sub('',s).replace(' ','').replace('\u3000','')
            if cleaned=='': four_pairs = pp
    if four_pairs:
        # 后续5行断语
        tail = '\n'.join(lines[i+2:i+8])
        hit = [k for k in ['身旺','身弱','日主旺','日主弱','得地','得时','得令','失令','得势','身强','身衰'] if k in tail]
        records.append({'line':i+1,'pillars':four_pairs,'tags':hit,'tail':tail[:200]})

print(f'命例: {len(records)}')
tagged = [r for r in records if r['tags']]
print(f'含旺弱断语: {len(tagged)}')
for r in tagged[:15]:
    s=''.join(r['pillars'][0]+r['pillars'][1]+r['pillars'][2]+r['pillars'][3])
    print(f"  L{r['line']} {s} {r['tags']}")

# 跑引擎
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

# 对照: 任氏说"身旺/旺/强"的盘, 引擎 root 是否 HEAVY?
# 任氏说"身弱/衰/弱"的盘, 引擎 root 是否 LIGHT/NONE?
match_heavy = 0; match_light = 0; mismatches = []
for r in tagged:
    p = {'year':list(r['pillars'][0]),'month':list(r['pillars'][1]),'day':list(r['pillars'][2]),'hour':list(r['pillars'][3])}
    try:
        f=build(p);pa=build_power_structure(p)
        hst={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
        rc=build_root_classes(p,hst);tc=build_tou_cang(f);wx=build_wang_xiang(f,f['day_stem'])
        rr=build_root_relations(rc,f['combination_facts']);ts=build_two_side(rc,tc,rr)
        bt=build_branch_tiers(p,f);th=build_tian_he(p,f)
        net=build_power_network(pa,rc,tc,wx,rr,ts,branch_tier=bt,tian_he=th)
        rw=net['dimensions']['ROOT']['root_weight_class']
        s=''.join(r['pillars'][0]+r['pillars'][1]+r['pillars'][2]+r['pillars'][3])
        tags=r['tags']
        # 任氏判旺
        if any(t in tags for t in ['身旺','日主旺','得地','得时','得令','得势','身强']):
            if rw=='HEAVY': match_heavy+=1
            else: mismatches.append((s,tags,rw,'任氏旺'))
        if any(t in tags for t in ['身弱','日主弱','失令','身衰']):
            if rw in ('LIGHT','NONE'): match_light+=1
            else: mismatches.append((s,tags,rw,'任氏弱'))
    except: pass

print(f'\n=== 对照 ===')
print(f'任氏旺 -> 引擎HEAVY: {match_heavy}')
print(f'任氏弱 -> 引擎LIGHT/NONE: {match_light}')
print(f'不一致: {len(mismatches)}')
for m in mismatches[:15]: print('  ',m)
