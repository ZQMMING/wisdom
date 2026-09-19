# -*- coding: utf-8 -*-
"""调试用神引擎: 输出不匹配案例的命局结构和决策路径."""
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
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology
from engines.common.special_pattern import build_special_patterns
from engines.common.climate_structure import build_climate_structure
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine, _ten_wx

WX={'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}

def run_case(chart_str, name=''):
    pillars = {
        'year': (chart_str[0], chart_str[1]),
        'month': (chart_str[2], chart_str[3]),
        'day': (chart_str[4], chart_str[5]),
        'hour': (chart_str[6], chart_str[7]),
    }
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
    spt = build_spectrum_topology(net, wpo)
    cl = build_climate_structure(pillars, f, th)
    spc = build_special_patterns(pillars, f, wpo, th, cl)
    clc = build_climate_candidates(f)
    ye = build_yongshen_engine(pillars, f, wpo, spt, spc, clc)

    dm = f['day_stem']
    dmw = _ten_wx(dm)
    tier = spt.get('spectrum')
    t = f['ten_god_members']
    print('=== %s %s ===' % (name, chart_str))
    print('日主: %s(%s), 月令: %s' % (dm, dmw, pillars['month'][1]))
    print('天干: %s %s %s %s' % (pillars['year'][0], pillars['month'][0], pillars['day'][0], pillars['hour'][0]))
    print('地支: %s %s %s %s' % (pillars['year'][1], pillars['month'][1], pillars['day'][1], pillars['hour'][1]))
    print('旺衰谱: %s' % tier)
    # 统计十神
    for god_name, god_list in [('官杀', ['正官','七杀']), ('印星', ['正印','偏印']), ('比劫', ['比肩','劫财']), ('食伤', ['食神','伤官']), ('财星', ['正财','偏财'])]:
        stem_n = sum(1 for x in t if x['type']=='stem' and x['ten_god'] in god_list)
        ben_n = sum(1 for x in t if x['type']=='hidden' and x['qi_position']=='本气' and x['ten_god'] in god_list)
        zhong_n = sum(1 for x in t if x['type']=='hidden' and x['qi_position']=='中气' and x['ten_god'] in god_list)
        yu_n = sum(1 for x in t if x['type']=='hidden' and x['qi_position']=='余气' and x['ten_god'] in god_list)
        print('%s: 透干=%d, 本气根=%d, 中气根=%d, 余气根=%d' % (god_name, stem_n, ben_n, zhong_n, yu_n))
    print('用神: primary=%s, secondary=%s, avoid=%s' % (ye.get('yongshen_primary'), ye.get('yongshen_secondary'), ye.get('yongshen_avoid')))
    print('路径: %s' % ye.get('yongshen_paths'))
    print('theory_source: %s' % ye.get('theory_source'))
    print()

cases = [
    ('己亥丁卯庚申庚辰', '案例: 原文"支坐禄旺，时逢印比，足以用官"→用神应为火(官)'),
]

for chart, name in cases:
    run_case(chart, name)
