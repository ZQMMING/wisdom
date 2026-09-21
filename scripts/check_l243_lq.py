#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查L243的lq变量值"""
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

for li, fp, dy, txt in cases:
    if li == 243:
        try: p, f, ye, tp0 = engine(fp)
        except Exception as e:
            print(f"引擎错误: {e}")
            break
        
        print("L243 Facts层special完整结构:")
        import json
        sp = f.get('special') or {}
        print(json.dumps(sp, ensure_ascii=False, indent=2))
        print()
        print(f"  cong_type: {sp.get('cong_type')}")
        print(f"  zhuanwang: {sp.get('zhuanwang')}")
        print(f"  hua_qi: {sp.get('hua_qi')}")
        print(f"  liangqi: {sp.get('liangqi')}")
        print()
        print(f"  ye.special: {ye.get('special')}")
        print(f"  ye.paths: {ye.get('yongshen_paths')}")
        print(f"  ye.primary: {ye.get('yongshen_primary')}")
        break
