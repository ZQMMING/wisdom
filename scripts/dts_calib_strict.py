# -*- coding: utf-8 -*-
"""DTS 513命例 严格段内配对: 四柱行->下一四柱行之间为该命例断语段."""
import re, sys, json, collections
sys.path.insert(0, '.')

path = r'D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓阐微_任铁樵注_全文.txt'
lines = open(path, encoding='utf-8').read().splitlines()
GZ = re.compile(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])')

# 找所有四柱行位置
pillars_lines = []
for i, ln in enumerate(lines):
    s = ln.strip()
    fp = None
    if s.startswith('八字'):
        b = s.split('：',1)[-1].split(':',1)[-1].strip(); pp = GZ.findall(b)
        if len(pp)==4: fp = pp
    else:
        pp = GZ.findall(s)
        if len(pp)==4 and len(s)<60:
            c = GZ.sub('',s).replace(' ','').replace('\u3000','')
            if c=='': fp = pp
    if fp: pillars_lines.append((i, fp))

print(f'四柱行: {len(pillars_lines)}')

# 每个命例段 = 从该行到下一个四柱行
KW_STRONG = ['身旺','日主旺','身强','强旺']
KW_WEAK = ['身弱','日主弱','身衰','衰弱']
KW_SEASON = ['得时','得令','得地','得势','失令']

cases = []
for idx, (li, fp) in enumerate(pillars_lines):
    end = pillars_lines[idx+1][0] if idx+1 < len(pillars_lines) else min(li+30, len(lines))
    segment = '\n'.join(lines[li:end])
    strong = [k for k in KW_STRONG if k in segment]
    weak = [k for k in KW_WEAK if k in segment]
    season = [k for k in KW_SEASON if k in segment]
    cases.append({'line':li+1, 'pillars':fp, 'strong':strong, 'weak':weak, 'season':season})

# 跑引擎
from engines.common.l0_fact_builder import build
from engines.common.daymaster_root_class import build_root_classes
results = []
for c in cases:
    p = {'year':list(c['pillars'][0]),'month':list(c['pillars'][1]),'day':list(c['pillars'][2]),'hour':list(c['pillars'][3])}
    try:
        f = build(p)
        hst = {p[k][1]:f['hidden_stems'][k] for k in ('year','month','day','hour')}
        rc = build_root_classes(p, hst)
        rw = rc['root_weight_class']
        s = ''.join(c['pillars'][0]+c['pillars'][1]+c['pillars'][2]+c['pillars'][3])
        results.append({'line':c['line'],'pillars':s,'root':rw,'strong':c['strong'],'weak':c['weak'],'season':c['season']})
    except Exception as e:
        results.append({'line':c['line'],'pillars':'ERR','root':'ERR','strong':[],'weak':[],'season':[]})

# 对照统计
both = [r for r in results if r['strong'] and r['weak']]
pure_strong = [r for r in results if r['strong'] and not r['weak']]
pure_weak = [r for r in results if r['weak'] and not r['strong']]
print(f'\n含旺弱断语段: {len(pure_strong)+len(pure_weak)+len(both)}')
print(f'  纯旺: {len(pure_strong)}  纯弱: {len(pure_weak)}  旺弱同段: {len(both)}')

print(f'\n=== 纯旺 {len(pure_strong)} 例: 任氏说旺 -> 引擎root ===')
c1 = collections.Counter(r['root'] for r in pure_strong)
for k,v in c1.most_common(): print(f'  {k:10s} {v}')
print('\n  不一致(任氏旺但非HEAVY):')
for r in pure_strong:
    if r['root']!='HEAVY':
        print(f"    L{r['line']} {r['pillars']} root={r['root']} strong={r['strong']}")

print(f'\n=== 纯弱 {len(pure_weak)} 例: 任氏说弱 -> 引擎root ===')
c2 = collections.Counter(r['root'] for r in pure_weak)
for k,v in c2.most_common(): print(f'  {k:10s} {v}')
print('\n  不一致(任氏弱但HEAVY):')
for r in pure_weak:
    if r['root']=='HEAVY':
        print(f"    L{r['line']} {r['pillars']} root={r['root']} weak={r['weak']}")

# 保存
json.dump(results, open('scripts/dts_calib_results.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n保存: scripts/dts_calib_results.json')
