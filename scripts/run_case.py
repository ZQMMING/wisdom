# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build, WUXING
from engines.common.daymaster_power_structure import build_power_structure
from engines.common.daymaster_root_class import build_root_classes
from engines.common.daymaster_tou_cang import build_tou_cang
from engines.common.daymaster_wang_xiang import build_wang_xiang
from engines.common.daymaster_root_relations import build_root_relations
from engines.common.daymaster_two_side import build_two_side
from engines.common.daymaster_branch_tier import build_branch_tiers
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology, build_spectrum_from_power
from engines.common.daymaster_power_network import build_power_network
from engines.common.climate_structure import build_climate_structure
from engines.common.special_pattern import build_special_patterns
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine
from engines.common.dayun_xiji import build_dayun_xiji

K = ('year', 'month', 'day', 'hour')
p = {'year': ['甲', '子'], 'month': ['辛', '未'], 'day': ['戊', '午'], 'hour': ['己', '未']}
f = l0build(p)
ds = f['day_stem']
hst = {p[k][1]: f['hidden_stems'][k] for k in K}
pa = build_power_structure(p)
rc = build_root_classes(p, hst)
tc = build_tou_cang(f)
wxo = build_wang_xiang(f, ds)
rr = build_root_relations(rc, f['combination_facts'])
ts = build_two_side(rc, tc, rr)
bt = build_branch_tiers(p, f)
th = build_tian_he(p, f)
wp = build_wuxing_power(p, f, th)
net = build_power_network(pa, rc, tc, wxo, rr, ts, branch_tier=bt, tian_he=th, facts=f)
net.setdefault('facts', {})['daymaster_element'] = WUXING[ds]
sp = build_spectrum_topology(net, wp)
_spd = build_spectrum_from_power(wp, p)
sp['wang_shuai'] = _spd.get('wang_shuai')
sp['qiang_ruo'] = _spd.get('qiang_ruo')
clc = build_climate_candidates(f)
cls = build_climate_structure(p, f, th)
spp = build_special_patterns(p, f, wp, th, cls)
ye = build_yongshen_engine(p, f, wp, sp, spp, clc)

print('=== climate_stem_candidates ===')
for c in ye.get('climate_stem_candidates', []):
    print(' ', c)
print()

dayun_list = ['壬申', '癸酉', '甲戌', '乙亥', '丙子', '丁丑', '戊寅', '己卯']
dx = build_dayun_xiji(p, ye, dayun_list, {'wuxing_power': wp})
per_step = dx.get('per_step', [])

print('=== 大运喜忌 + stem_match_type ===')
for i, step in enumerate(per_step):
    gan = step.get('gan', '?')
    zhi = step.get('zhi', '?')
    ej = step.get('element_judgment', {})
    smt = step.get('stem_match_type', '?')
    age_start = 5 + i * 10
    age_end = age_start + 9
    print('%s%s (%d-%d岁): 元素级=%s | stem_match=%s' % (gan, zhi, age_start, age_end, ej.get('result','?'), smt))
