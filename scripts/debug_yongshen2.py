# -*- coding: utf-8 -*-
"""深度调试用神引擎决策路径."""
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.wuxing_power import build_wuxing_power
from engines.common.special_pattern import build_special_patterns
from engines.common.qtbj_climate_candidates import build_climate_candidates

# 案例1: 丁巳壬子辛巳丁酉 (原文用神必在酉金)
pillars = {
    'year': ['丁', '巳'],
    'month': ['壬', '子'],
    'day': ['辛', '巳'],
    'hour': ['丁', '酉'],
}

facts = build(pillars)
wpo = build_wuxing_power(pillars, facts)
spc = build_special_patterns(pillars, facts, wpo)
clc = build_climate_candidates(facts)

print('=== 案例1: 丁巳壬子辛巳丁酉 ===')
print('日主: 辛(金), 月令: 子(水)')
print('特殊格局: cong=%s(%s), zw=%s(%s)' % (
    spc.get('cong_type'), spc.get('cong_state'),
    spc.get('zhuanwang'), spc.get('zhuanwang_state')))
print('调候候选:', clc.get('climate_candidates'))

# 手动模拟用神引擎决策
WX = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
SHENG = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
KE = {'木':'土','土':'水','水':'火','火':'金','金':'木'}

dm = '辛'
dmw = '金'
mz = '子'

# 五行力量
t = wpo['wuxing_power']
print('\n五行力量:')
for wx in ['木','火','土','金','水']:
    print('  %s: ben=%d, stem=%d, ling=%s, cs=%s' % (
        wx, t[wx]['ben'], t[wx]['stem'], t[wx]['ling'], t[wx]['cheng_shi']))

# 关键变量
cs = lambda wx: t[wx]['cheng_shi']
ben = lambda wx: t[wx]['ben']
stem = lambda wx: t[wx]['stem']
ling = lambda wx: t[wx]['ling']

print('\n关键判断:')
print('  cs(食伤=水):', cs('水'))
print('  cs(官杀=火):', cs('火'))
print('  cs(印=土):', cs('土'))
print('  cs(比劫=金):', cs('金'))
print('  stem(官杀=火):', stem('火'))
print('  ben(官杀=火):', ben('火'))
print('  ling(食伤=水):', ling('水'))

# 官杀制化判断
gs_rooted = cs('火') or (stem('火')>=1 and ben('火')>=1)
gs_bing = gs_rooted or (stem('火')>=2) or (ling('火')=='旺' and stem('火')>=1)
print('\n  gs_rooted:', gs_rooted)
print('  gs_bing:', gs_bing)

# 调候
hou = set()
for c in (clc.get('climate_candidates') or []):
    s = c.get('stem')
    if s in WX:
        hou.add(WX[s])
print('  hou(调候五行):', hou)
print('  sorted(hou):', sorted(hou))
