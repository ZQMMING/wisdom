# -*- coding: utf-8 -*-
import sys,csv,re,collections;sys.path.insert(0,'.')
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
from engines.common.wuxing_power import build_spectrum_topology,build_wuxing_power
from engines.common.daymaster_root_class import WUXING

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
    ht={p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
    rc=build_root_classes(p,ht);tc=build_tou_cang(f)
    wx=build_wang_xiang(f,f['day_stem']);rr=build_root_relations(rc,f['combination_facts'])
    ts=build_two_side(rc,tc,rr);bt=build_branch_tiers(p,f);th=build_tian_he(p,f)
    net=build_power_network(pa,rc,tc,wx,rr,ts,branch_tier=bt,tian_he=th,facts=f)
    net.setdefault('facts',{})['daymaster_element']=WUXING[f['day_stem']]
    wpo=build_wuxing_power(p,f,th)
    return build_spectrum_topology(net,wpo)['spectrum']

dist=collections.Counter();cross=collections.defaultdict(collections.Counter);specmap={}
for r in rows:
    ch=r['chart'];p={'year':list(ch[0:2]),'month':list(ch[2:4]),'day':list(ch[4:6]),'hour':list(ch[6:8])}
    try: sp=spec_of(p)
    except Exception as ex: sp='ERR'
    dist[sp]+=1;specmap[ch]=sp
print('=== 拓扑七档分布 ===')
for k in ['旺极','太旺','旺','中和','衰','太衰','衰极','ERR']:
    print(f'{k}: {dist[k]}')
print('\n=== 原文关键词 × 拓扑档 ===')
for kw in ['旺极','太旺','中和','衰极','身旺','身强','日主旺','身弱','身衰','日主弱','衰弱']:
    c=collections.Counter();n=0
    for r in rows:
        text=case_text(int(r['line']))
        if kw in text:
            c[specmap[r['chart']]]+=1;n+=1
    print(f'{kw} (原文{n}): {dict(c)}')
