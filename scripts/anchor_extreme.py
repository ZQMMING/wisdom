# -*- coding: utf-8 -*-
# 干净锚点: 日主太旺(X太旺者似, X=日主五行) / 日主衰极(X衰极, X=日主五行), 排除他神
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
from engines.common.wuxing_power import build_spectrum_topology,build_wuxing_power
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
    return build_spectrum_topology(net,wpo)
wxmap={'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
taiwang=[];shuaiji=[]
for r in rows:
    ch=r['chart'];text=case_text(int(r['line']));dwx=wxmap[ch[4]]
    p={'year':list(ch[0:2]),'month':list(ch[2:4]),'day':list(ch[4:6]),'hour':list(ch[6:8])}
    sp=spec_of(p);sf=sp['self_factors'];of=sp['opposing_factors']
    for m in re.finditer(r'([金木水火土])太旺',text):
        if m.group(1)==dwx:
            taiwang.append((ch,dwx,sp['spectrum'],sf['支持档'],of.get('财官杀真党类数'),text[max(0,m.start()-6):m.start()+10]))
    for m in re.finditer(r'([金木水火土])衰极',text):
        if m.group(1)==dwx:
            shuaiji.append((ch,dwx,sp['spectrum'],sf['支持档'],of.get('财官杀真党类数'),text[max(0,m.start()-6):m.start()+10]))
print('=== 日主太旺 干净锚点 (期望 太旺/旺极) ===')
for x in taiwang: print(f'{x[0]} {x[1]} -> {x[2]} ({x[3]},财官党{x[4]})  {x[5]}')
print('=== 日主衰极 干净锚点 (期望 太衰/衰极) ===')
for x in shuaiji: print(f'{x[0]} {x[1]} -> {x[2]} ({x[3]},财官党{x[4]})  {x[5]}')
def rate(lst,good):
    return sum(1 for x in lst if x[2] in good),len(lst)
tw=rate(taiwang,{'太旺','旺极'});sj=rate(shuaiji,{'太衰','衰极'})
print(f'\n太旺锚点 {tw[0]}/{tw[1]}   衰极锚点 {sj[0]}/{sj[1]}')
