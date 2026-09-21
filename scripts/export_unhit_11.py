#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""剩余11例未命中案例完整数据导出"""
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
        from engines.common.dayun_xiji import build_dayun_xiji
        dx = build_dayun_xiji(p, ye, [gz], tp0)
        eng_result = dx.get('luck_verdict') or 'neutral'
        # 原典判断
        orig_result = 'ji' if v == 'ji' else 'xiong'
        # 判断是否命中
        eng_set = {eng_result}
        if dx.get('interaction_note'):
            # 有互动级影响，候选集包含相反结论
            if eng_result == 'ji':
                eng_set.add('xiong')
            else:
                eng_set.add('ji')
        if orig_result not in eng_set:
            unhit_cases.append({
                'li': li, 'fp': fp, 'gz': gz, 'txt': txt,
                'eng_result': eng_result, 'orig_result': orig_result,
                'fav': sorted(fav), 'av': sorted(av),
                'primary': prim, 'special': ye.get('special'),
                'paths': ye.get('yongshen_paths'),
                'blob': blob[:100],
                'interaction': dx.get('interaction_note', ''),
            })

print(f"未命中案例总数: {len(unhit_cases)}")
print()

# 按special分类
from collections import defaultdict
by_special = defaultdict(list)
for c in unhit_cases:
    by_special[c['special'] or '正格'].append(c)

print("=== 按special分类 ===")
for sp, cases in sorted(by_special.items(), key=lambda x: -len(x[1])):
    print(f"  {sp}: {len(cases)}例")
print()

# 详细输出每个案例
print("=== 未命中案例详细数据 ===")
for i, c in enumerate(unhit_cases, 1):
    print(f"\n--- 案例{i}: L{c['li']} {''.join(c['fp'][k][0]+c['fp'][k][1] for k in ('year','month','day','hour'))} 运{c['gz']} ---")
    print(f"  引擎判断: {c['eng_result']}")
    print(f"  原典判断: {c['orig_result']}")
    print(f"  special: {c['special']}")
    print(f"  paths: {c['paths']}")
    print(f"  primary: {c['primary']}")
    print(f"  fav: {c['fav']}")
    print(f"  av: {c['av']}")
    print(f"  互动级: {c['interaction']}")
    print(f"  原典断语: {c['blob']}")
