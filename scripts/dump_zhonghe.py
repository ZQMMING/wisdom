# -*- coding: utf-8 -*-
import sys,csv,re;sys.path.insert(0,'.')
from engines.common.l0_fact_builder import build
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes,WUXING
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.daymaster_power_network import build_power_network
from engines.common.wuxing_power import build_wuxing_power,build_spectrum_topology
lines=open(r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt',encoding='utf-8').readlines()
rows=list(csv.DictReader(open('scripts/dts_513_output.csv',encoding='utf-8-sig')))
GZ=r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]'
BZ_RE=re.compile(rf'^{GZ}\s+{GZ}\s+{GZ}\s+{GZ}\s*$')
def case_text(ln):
    e=ln+1
    while e<len(lines):
        l=lines[e].strip()
        if l.startswith('八字：') or l.startswith('====') or l.startswith('【') or BZ_RE.match(l): break
        e+=1
    return ''.join(lines[ln+1:e])
def spec_of(p):
    f=build(p);pa=build_power_structure(p)
    hst={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
    rc=build_root_classes(p,hst);tc=build_tou_cang(f);wx=build_wang_xiang(f,f['day_stem'])
    rr=build_root_relations(rc,f['combination_facts']);ts=build_two_side(rc,tc,rr)
    bt=build_branch_tiers(p,f);th=build_tian_he(p,f)
    net=build_power_network(pa,rc,tc,wx,rr,ts,branch_tier=bt,tian_he=th,facts=f)
    net.setdefault('facts',{})['daymaster_element']=WUXING[f['day_stem']]
    wpo=build_wuxing_power(p,f,th);return build_spectrum_topology(net,wpo)
for kw in ['中和']:
    print(f'=== 原文"{kw}" ===')
    for r in rows:
        ch=r['chart'];text=case_text(int(r['line']))
        for m in re.finditer(kw,text):
            ctx=text[max(0,m.start()-12):m.start()+10]
            if any(x in ctx for x in ['运','流年','若','设使','假如','凡','如','假','似','论中和','贵乎','要','须','不可','太过不及']):
                continue
            p={'year':list(ch[0:2]),'month':list(ch[2:4]),'day':list(ch[4:6]),'hour':list(ch[6:8])}
            sp=spec_of(p)
            print(f'{ch} ratio={sp["daymaster_ratio"]:.2f} {sp["self_factors"]["支持档"]} 根{sp["self_factors"]["R"]} -> {sp["spectrum"]} | {ctx}')
            break
