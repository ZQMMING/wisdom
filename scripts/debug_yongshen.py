# -*- coding: utf-8 -*-
"""调试用神引擎: 输出不匹配案例的命局结构和决策路径."""
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_topology
from engines.common.special_pattern import build_special_patterns
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine

WX={'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
BRANCH_WX={'子':'水','亥':'水','寅':'木','卯':'木','巳':'火','午':'火','申':'金','酉':'金','辰':'土','戌':'土','丑':'土','未':'土'}

def run_case(chart_str, name=''):
    pillars = {
        'year': (chart_str[0], chart_str[1]),
        'month': (chart_str[2], chart_str[3]),
        'day': (chart_str[4], chart_str[5]),
        'hour': (chart_str[6], chart_str[7]),
    }
    facts = build(pillars)
    wpo = build_wuxing_power(pillars, facts)
    # spt = build_spectrum_topology(wpo)  # 有bug, 先用占位
    spt = {'spectrum': '中和'}
    spc = build_special_patterns(pillars, facts, wpo)
    clc = build_climate_candidates(facts)
    ys = build_yongshen_engine(pillars, facts, wpo, spt, spc, clc)

    dm = facts['day_stem']
    dmw = WX[dm]
    tier = spt.get('spectrum') if isinstance(spt, dict) else spt
    print('=== %s %s ===' % (name, chart_str))
    print('日主: %s(%s), 月令: %s(%s)' % (dm, dmw, pillars['month'][1], BRANCH_WX.get(pillars['month'][1])))
    print('天干: %s %s %s %s' % (pillars['year'][0], pillars['month'][0], pillars['day'][0], pillars['hour'][0]))
    print('地支: %s %s %s %s' % (pillars['year'][1], pillars['month'][1], pillars['day'][1], pillars['hour'][1]))
    print('旺衰谱: %s' % tier)
    print('特殊格局: cong=%s(%s), zw=%s(%s), hua=%s(%s)' % (
        spc.get('cong_type',''), spc.get('cong_state',''),
        spc.get('zhuanwang',''), spc.get('zhuanwang_state',''),
        spc.get('hua_qi',''), spc.get('hua_qi_state','')))
    print('五行力量:')
    wpd = wpo.get('wuxing_power', {}) if isinstance(wpo, dict) else {}
    for w in '木火土金水':
        wp = wpd.get(w, {}) if isinstance(wpd, dict) else {}
        print('  %s: ben=%d, stem=%d, ling=%s, ju=%d, zhong=%d, yu=%d' % (
            w, wp.get('ben_n',0), wp.get('stem_n',0), wp.get('ling_state',''),
            wp.get('ju_n',0), wp.get('zhong_n',0), wp.get('yu_n',0)))
    print('调候候选: %s' % [c.get('stem') for c in (clc.get('climate_candidates') or []) if isinstance(c, dict)])
    print('用神: primary=%s, secondary=%s, avoid=%s' % (ys.get('yongshen_primary'), ys.get('yongshen_secondary'), ys.get('yongshen_avoid')))
    print('路径: %s' % ys.get('yongshen_paths'))
    print()

cases = [
    ('丁巳壬子辛巳丁酉', '案例1: 原文用神必在酉金, 引擎输出火'),
    ('丁亥壬子庚子辛巳', '案例2: 原文用神在土不在火, 引擎输出木'),
    ('戊子壬戌庚寅癸未', '案例3: 原文用神在水不在火, 引擎输出木'),
    ('庚申戊寅壬子甲辰', '案例4: 原文透金为用神, 引擎输出木'),
    ('己丑丙子辛酉壬辰', '案例5: 原文必以水为用神, 引擎输出火'),
]

for chart, name in cases:
    run_case(chart, name)
