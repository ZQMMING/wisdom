# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
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
from engines.common.wuxing_power import build_wuxing_power
from engines.common.special_pattern import build_special_patterns
from engines.common.climate_structure import build_climate_structure

# 案例2: 润下格
pillars = {'year': '壬申', 'month': '壬子', 'day': '辛亥', 'hour': '癸巳'}
f = build(pillars)
pa = build_power_structure(pillars)
hst = {pillars[k][1]: f['hidden_stems'][k] for k in ('year', 'month', 'day', 'hour')}
rc = build_root_classes(pillars, hst)
tc = build_tou_cang(f)
wx = build_wang_xiang(f, f['day_stem'])
rr = build_root_relations(rc, f['combination_facts'])
ts = build_two_side(rc, tc, rr)
bt = build_branch_tiers(pillars, f)
th = build_tian_he(pillars, f)
net = build_power_network(pa, rc, tc, wx, rr, ts, branch_tier=bt, tian_he=th, facts=f)
wpo = build_wuxing_power(pillars, f, th)
cl = build_climate_structure(pillars, f, th)
spc = build_special_patterns(pillars, f, wpo, th, cl)

print('=== 润下格调试 ===')
print('day_stem:', f['day_stem'])
wp = wpo['wuxing_power']
for elem in ['水', '金', '木', '火', '土']:
    d = wp[elem]
    print('%s: ben_n=%s, ju_n=%s, stem_n=%s, total=%s' % (elem, d.get('ben_n'), d.get('ju_n'), d.get('stem_n'), d.get('total')))
print()
print('month_element:', wpo.get('month_element'))
print('patterns:', [p.get('pattern_name') for p in spc.get('patterns', [])])
print('zhuanwang:', spc.get('zhuanwang'), spc.get('zhuanwang_state'))
print('cong_type:', spc.get('cong_type'))
print('hua_qi:', spc.get('hua_qi'))

# 手动计算专旺格条件
print()
print('=== 专旺格条件手动计算 ===')
dm_wx = '水'
dm = wp[dm_wx]
yin = wp['金']  # 金生水
gs = wp['土']   # 土克水
cai = wp['火']  # 水克火
ss = wp['木']   # 水生木

dm_ben = dm.get('ben_n', 0)
dm_ju = dm.get('ju_n', 0)
yin_ben = yin.get('ben_n', 0)
gs_ben = gs.get('ben_n', 0)
gs_stem = gs.get('stem_n', 0)
gs_ju = gs.get('ju_n', 0)
cai_ben = cai.get('ben_n', 0)
cai_stem = cai.get('stem_n', 0)
cai_ju = cai.get('ju_n', 0)
ss_stem = ss.get('stem_n', 0)
ss_ben = ss.get('ben_n', 0)

party = dm_ben + yin_ben + dm.get('banhe_n', 0)
print('dm_ben(水本气):', dm_ben)
print('dm_ju(水局):', dm_ju)
print('yin_ben(金本气):', yin_ben)
print('gs_ben(土本气):', gs_ben)
print('gs_stem(土透干):', gs_stem)
print('cai_ben(火本气):', cai_ben)
print('cai_stem(火透干):', cai_stem)
print('ss_stem(木透干):', ss_stem)
print('party:', party)
print()
print('CONFIRMED条件: gs_ben==0 and gs_stem==0 and gs_ju==0 and cai_ben==0 and cai_stem==0 and cai_ju==0 and (dm_ju>=1 or (party>=4 and dm_ben>=2))')
print('  => gs_ben==0:', gs_ben==0, ', gs_stem==0:', gs_stem==0, ', cai_ben==0:', cai_ben==0, ', cai_stem==0:', cai_stem==0)
print('  => (dm_ju>=1 or (party>=4 and dm_ben>=2)):', (dm_ju>=1 or (party>=4 and dm_ben>=2)))
print()
print('CANDIDATE条件: gs_ben<=1 and gs_ju==0 and cai_ben<=1 and party>=3 and (dm_ju>=1 or dm_ben>=2)')
print('  => gs_ben<=1:', gs_ben<=1, ', cai_ben<=1:', cai_ben<=1, ', party>=3:', party>=3)
print('  => (dm_ju>=1 or dm_ben>=2):', (dm_ju>=1 or dm_ben>=2))
