#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查special字段完整结构"""
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

# 检查L243的special完整结构
for li, fp, dy, txt in cases:
    if li == 243:
        try: p, f, ye, tp0 = engine(fp)
        except Exception as e:
            print(f"引擎错误: {e}")
            break
        
        print("L243 special完整结构:")
        import json
        print(json.dumps(f.get('special'), ensure_ascii=False, indent=2))
        print()
        print(f"  zhuanwang字段: {f.get('zhuanwang')}")
        print(f"  zhuanwang_state字段: {f.get('zhuanwang_state')}")
        break

print()
print("=== 检查所有special包含'格'的案例 ===")
ge_cases = []
for li, fp, dy, txt in cases:
    try: p, f, ye, tp0 = engine(fp)
    except Exception: continue
    sp = f.get('special') or {}
    sp_str = str(sp)
    if '格' in sp_str:
        ge_cases.append({
            'li': li, 'special': sp,
            'zhuanwang': f.get('zhuanwang'),
            'paths': ye.get('yongshen_paths')
        })

print(f"包含'格'的案例总数: {len(ge_cases)}")
print()

# 统计zhuanwang字段设置情况
zw_set = sum(1 for c in ge_cases if c['zhuanwang'])
zw_none = sum(1 for c in ge_cases if not c['zhuanwang'])
print(f"zhuanwang字段已设置: {zw_set}例")
print(f"zhuanwang字段为None: {zw_none}例")
print()

print("zhuanwang为None的案例:")
for c in ge_cases:
    if not c['zhuanwang']:
        print(f"  L{c['li']} special={c['special']} paths={c['paths']}")
