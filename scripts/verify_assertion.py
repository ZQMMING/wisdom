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

p = {'year': '甲子', 'month': '辛未', 'day': '戊午', 'hour': '己未'}
f = l0build(p)
ds = f['day_stem']
hst = {p[k][1]: f['hidden_stems'][k] for k in ('year','month','day','hour')}
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

print('=== 稼穑格(甲子辛未戊午己未) ===')
print('special:', ye.get('special'))
print()
print('qtbj_stem_assertions:')
for a in ye.get('qtbj_stem_assertions', []):
    print('  ' + a['assertion_id'] + ': ' + a['stem'] + '(' + a['element'] + ') P' + str(a['priority']))
    print('    applicability: ' + a['applicability'])
    print('    condition: ' + a['condition'])
    print('    valid: ' + str(a['valid']))
    print('    provenance: ' + a['provenance'])
    print()
