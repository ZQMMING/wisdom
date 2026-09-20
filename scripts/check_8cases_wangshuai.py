#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""确认8例冲原局案例的身旺身弱状态"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')

# 只导入函数, 不运行主逻辑
import importlib.util
spec = importlib.util.spec_from_file_location("dayun_align_mod", "scripts/dayun_align.py")
mod = importlib.util.module_from_spec(spec)
# 阻止主逻辑运行
import unittest.mock
with unittest.mock.patch('sys.argv', ['dayun_align.py']):
    try:
        spec.loader.exec_module(mod)
    except SystemExit:
        pass

cases = mod.cases
engine = mod.engine

targets = [326, 620, 852, 911, 1045, 2044, 2198]

for li, fp, dy, txt in cases:
    if li+1 not in targets: continue
    try: p, f, ye, tp0 = engine(fp)
    except: continue
    dm = f['day_stem']
    # 获取身旺身弱信息
    ws = ye.get('wang_shuai') or {}
    qr = ye.get('qiang_ruo') or {}
    spec_val = ye.get('wangshuai_spectrum') or ye.get('spectrum') or 'N/A'
    print(f"L{li+1} {''.join(a+b for a,b in fp)} 日主{dm}")
    print(f"  spectrum={spec_val}")
    print(f"  wang_shuai={ws}")
    print(f"  qiang_ruo={qr}")
    print(f"  primary={ye.get('yongshen_primary')}")
    print(f"  paths={ye.get('yongshen_paths')}")
    print()
