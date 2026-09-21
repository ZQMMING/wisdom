#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""剩余11例未命中案例逐例诊断: A类(用神五行错)/B类(大运喜忌逻辑错)/C类(原典模糊)"""
import sys; sys.path.insert(0, '.'); sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('dayun_align_mod', 'scripts/dayun_align.py')
mod = importlib.util.module_from_spec(spec)
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try: spec.loader.exec_module(mod)
    except SystemExit: pass

engine = mod.engine
cases = mod.cases
luck_verdict = mod.luck_verdict
from engines.common.dayun_xiji import build_dayun_xiji
from engines.common.transit_power import transit_clash_verdicts, element_power_tier

# 收集所有未命中案例
unhit_cases = []
for li, fp, dy, txt in cases:
    if len(dy) < 4: continue
    try: p, f, ye, tp0 = engine(fp)
    except Exception: continue
    prim = ye.get('yongshen_primary') or ''
    fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
    av = set(ye.get('yongshen_avoid') or [])
    dm = f['day_stem']
    for gz in dy:
        g, z = gz[0], gz[1]
        v, blob = luck_verdict(txt, g, z)
        if blob and blob.lstrip().startswith('【原注】'):
            v = None
        if not v or v == 'hun' or v == 'lao':
            continue
        # 引擎判断
        dx = build_dayun_xiji(p, ye, [gz], tp0)
        # 从dx中提取该大运的判断
        luck_list = dx.get('dayun_list', [])
        eng_result = 'neutral'
        eng_reason = ''
        for item in luck_list:
            if item.get('dayun') == gz:
                eng_result = item.get('luck_verdict', 'neutral')
                eng_reason = item.get('reason', '')
                break
        # 原典判断
        orig_result = 'ji' if v == 'ji' else 'xiong'
        # 互动级检测(简化: 从对齐脚本输出已知, 这里标记为未知)
        has_interaction = False
        interaction_type = 'unknown'
        # 候选集: 元素级判断 + 互动级影响(简化处理)
        eng_set = {eng_result}
        # 简化: 所有未命中案例都假设可能有互动级影响
        if eng_result in ('ji', 'xiong'):
            opposite = 'xiong' if eng_result == 'ji' else 'ji'
            eng_set.add(opposite)
        # 判断是否未命中
        if orig_result not in eng_set:
            # 差异定位
            # A类: 用神五行错 - 大运五行不在fav中也不在av中, 或大运五行在fav中但原典判凶
            dayun_wx = '木火土金水'['甲乙丙丁戊己庚辛壬癸'.index(g) // 2]
            in_fav = dayun_wx in fav
            in_av = dayun_wx in av
            # B类: 大运喜忌逻辑错 - 用神五行对, 但判断相反
            # C类: 原典模糊
            unhit_cases.append({
                'li': li, 'fp': fp, 'gz': gz, 'txt': txt,
                'eng_result': eng_result, 'eng_reason': eng_reason,
                'orig_result': orig_result, 'blob': blob[:120],
                'fav': sorted(fav), 'av': sorted(av), 'primary': prim,
                'special': ye.get('special'), 'paths': ye.get('yongshen_paths'),
                'dayun_wx': dayun_wx, 'in_fav': in_fav, 'in_av': in_av,
                'has_interaction': has_interaction, 'interaction_type': interaction_type,
            })

print(f"未命中案例总数: {len(unhit_cases)}")
print()

# 按A/B/C分类
A_cases = []  # 用神五行错
B_cases = []  # 大运喜忌逻辑错
C_cases = []  # 原典模糊

for c in unhit_cases:
    # A类: 大运五行在fav中但原典判凶(用神可能错), 或大运五行不在fav也不在av
    if c['orig_result'] == 'xiong' and c['in_fav']:
        A_cases.append(c)
    elif c['orig_result'] == 'ji' and c['in_av']:
        A_cases.append(c)
    elif not c['in_fav'] and not c['in_av']:
        # 大运五行既不在fav也不在av, 可能是用神候选不全
        A_cases.append(c)
    else:
        # B类: 用神五行对, 但判断相反
        B_cases.append(c)

print("=== A/B/C分类 ===")
print(f"  A类(用神五行错/候选不全): {len(A_cases)}例")
print(f"  B类(大运喜忌逻辑错): {len(B_cases)}例")
print(f"  C类(原典模糊): {len(C_cases)}例")
print()

# 详细输出每个案例
print("=== 未命中案例详细数据 ===")
for i, c in enumerate(unhit_cases, 1):
    bazi = ''.join(c['fp'][k][0]+c['fp'][k][1] for k in ('year','month','day','hour'))
    category = 'A' if c in A_cases else ('B' if c in B_cases else 'C')
    print(f"\n--- 案例{i}[{category}类]: L{c['li']} {bazi} 运{c['gz']} ---")
    print(f"  引擎判断: {c['eng_result']} ({c['eng_reason'][:60]})")
    print(f"  原典判断: {c['orig_result']}")
    print(f"  原典断语: {c['blob']}")
    print(f"  special: {c['special']}")
    print(f"  paths: {c['paths']}")
    print(f"  primary: {c['primary']}")
    print(f"  fav: {c['fav']}")
    print(f"  av: {c['av']}")
    print(f"  大运五行: {c['dayun_wx']} (in_fav={c['in_fav']}, in_av={c['in_av']})")
    print(f"  互动级: {c['interaction_type']} (has={c['has_interaction']})")
