# -*- coding: utf-8 -*-
"""测试大运应期喜忌结构层, 并与DTS断语对齐."""
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.wuxing_power import build_wuxing_power
from engines.common.special_pattern import build_special_patterns
from engines.common.qtbj_climate_candidates import build_climate_candidates
from engines.common.yongshen_engine import build_yongshen_engine
from engines.common.dayun_xiji import build_dayun_xiji

# 案例: 辛卯丁酉庚午丙子 (董中堂造之前的命例)
pillars = {
    'year': ['辛', '卯'],
    'month': ['丁', '酉'],
    'day': ['庚', '午'],
    'hour': ['丙', '子'],
}
dayun = ['丙申','乙未','癸巳','壬辰','庚寅','己丑','戊子','丁亥']

facts = build(pillars)
wpo = build_wuxing_power(pillars, facts)
spt = {'spectrum': '中和'}
spc = build_special_patterns(pillars, facts, wpo)
clc = build_climate_candidates(facts)
ys = build_yongshen_engine(pillars, facts, wpo, spt, spc, clc)

print('=== 原局用神 ===')
print('primary: %s' % ys.get('yongshen_primary'))
print('secondary: %s' % ys.get('yongshen_secondary'))
print('avoid: %s' % ys.get('yongshen_avoid'))
print()

dx = build_dayun_xiji(pillars, ys, dayun)
print('=== 大运喜忌结构 ===')
for step in dx['per_step']:
    print('%s: 十神=%s, 干五行=%s, 支五行=%s, 标签=%s, 关系=%s' % (
        step['ganzhi'], step['ten_god'], step['gan_wuxing'], step['zhi_wuxing'],
        step['xiji_label'], step['relations']))

print()
print('DTS原文断语: "天干庚辛丙丁，正配火炼秋金...最喜子午逢冲..."')
print('大运: 丙申 乙未 癸巳 壬辰 庚寅 己丑 戊子 丁亥')
