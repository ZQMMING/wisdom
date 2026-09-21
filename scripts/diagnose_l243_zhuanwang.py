#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断L243专旺格识别失败原因"""
import sys; sys.path.insert(0, '.')
from engines.common.special_pattern import build_special_patterns
from engines.common.wuxing_power import build_wuxing_power
from engines.common.climate_structure import build_climate_structure
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.l0build import l0build

p = {'year': ['戊', '子'], 'month': ['戊', '午'], 'day': ['戊', '戌'], 'hour': ['戊', '午']}
f = l0build(p)
ds = f['day_stem']
hst = {p[k][1]: f['hidden_stems'][k] for k in ('year', 'month', 'day', 'hour')}
th = build_tian_he(p, f)
wp = build_wuxing_power(p, f, th)
cls = build_climate_structure(p, f, th)

print("=== L243 戊子戊午戊戌戊午 ===")
print(f"日主: {ds}")
print(f"藏干: {hst}")
print()

# 检查wuxing_power中的关键指标
wp_data = wp.get('wuxing_power', {})
print("=== wuxing_power 关键指标 ===")
for wx in '木火土金水':
    d = wp_data.get(wx, {})
    print(f"  {wx}: ben_n={d.get('ben_n')}, zhong_n={d.get('zhong_n')}, yu_n={d.get('yu_n')}, stem_n={d.get('stem_n')}, ju_n={d.get('ju_n')}")
print()

# 检查special_patterns
spp = build_special_patterns(p, f, wp, th, cls)
print("=== special_patterns 输出 ===")
print(f"  zhuanwang: {spp.get('zhuanwang')}")
print(f"  zhuanwang_state: {spp.get('zhuanwang_state')}")
print(f"  cong_type: {spp.get('cong_type')}")
print(f"  cong_state: {spp.get('cong_state')}")
print(f"  hua_qi: {spp.get('hua_qi')}")
print(f"  liangqi: {spp.get('liangqi')}")
print(f"  patterns: {spp.get('patterns')}")
print()

# 手动检查专旺格识别条件
print("=== 手动检查专旺格识别条件 ===")
dm_wuxing = '土'  # 戊土
# 本方本气根
dm_ben = sum(wp_data.get(wx, {}).get('ben_n', 0) for wx in [dm_wuxing])
yin_wuxing = '火'  # 火生土
yin_ben = sum(wp_data.get(wx, {}).get('ben_n', 0) for wx in [yin_wuxing])
print(f"  日主本气根(土ben_n): {dm_ben}")
print(f"  印本气根(火ben_n): {yin_ben}")
print(f"  半合本方(banhe_n): {wp_data.get(dm_wuxing, {}).get('banhe_n', 0)}")
party = dm_ben + yin_ben + wp_data.get(dm_wuxing, {}).get('banhe_n', 0)
print(f"  party(专旺党众): {party}")
print()

# 官杀/财检查
guan_sha = '木'  # 木克土
cai = '水'  # 土克水
gs_ben = wp_data.get(guan_sha, {}).get('ben_n', 0)
cai_ben = wp_data.get(cai, {}).get('ben_n', 0)
gs_stem = wp_data.get(guan_sha, {}).get('stem_n', 0)
cai_stem = wp_data.get(cai, {}).get('stem_n', 0)
print(f"  官杀(木)本气根: {gs_ben}, 透干: {gs_stem}")
print(f"  财(水)本气根: {cai_ben}, 透干: {cai_stem}")
print()

# 食伤检查
shi_shang = '金'  # 土生金
ss_ben = wp_data.get(shi_shang, {}).get('ben_n', 0)
ss_stem = wp_data.get(shi_shang, {}).get('stem_n', 0)
print(f"  食伤(金)本气根: {ss_ben}, 透干: {ss_stem}")
print()

# 三合/三会检查
print(f"  土ju_n(三合三会): {wp_data.get('土', {}).get('ju_n', 0)}")
print()

# 检查是否会合成方局
print("=== 地支组合检查 ===")
print(f"  年支子, 月支午, 日支戌, 时支午")
print(f"  午午戌: 午戌半合火局(印局), 不是土局")
print(f"  土的三合局: 辰戌丑未(四库全), 但这里只有戌一个土支")
print(f"  土的三会局: 辰巳午(南方火), 不是土局")
print()
print("结论: L243虽然戊土透干×4, 但地支只有戌一个土本气根, 午午是火(印), 子是水(财)")
print("土的本气根只有1个(戌), 不满足专旺格'本方成局/本气重'的条件")
print("但yongshen_engine从liangqi.name获取到了'稼穑格', 说明liangqi的识别逻辑更宽松")
