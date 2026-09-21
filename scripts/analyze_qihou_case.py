#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析调候轨L1015案例 + 汇总所有发现"""
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

# L1015
for li, fp, dy, txt in cases:
    if li == 1015:
        print(f"{'='*80}")
        print(f"L1015 壬子辛亥乙亥丙子 运丙辰 [调候轨]")
        print(f"{'='*80}")
        print(f"原典断语:")
        print(f"  {txt[:500]}")
        print()
        
        try: p, f, ye, tp0 = engine(fp)
        except Exception as e:
            print(f"引擎错误: {e}")
            break
        
        print(f"引擎输出:")
        print(f"  日主: {f['day_stem']}")
        print(f"  月令: {p['month'][1]}")
        print(f"  special: {ye.get('special')}")
        print(f"  spectrum: {ye.get('spectrum_tier')}")
        print(f"  paths: {ye.get('yongshen_paths')}")
        print(f"  primary: {ye.get('yongshen_primary')}")
        print(f"  secondary: {ye.get('yongshen_secondary')}")
        print(f"  avoid: {ye.get('yongshen_avoid')}")
        print()
        
        GAN_WX = mod.GAN_WX
        BRANCH_WX = mod.BRANCH_WX
        g, z = '丙', '辰'
        prim = ye.get('yongshen_primary') or ''
        fav = set([prim]) | set(ye.get('yongshen_secondary') or []) if prim else set(ye.get('yongshen_secondary') or [])
        av = set(ye.get('yongshen_avoid') or [])
        print(f"大运丙辰判断:")
        print(f"  干丙={GAN_WX[g]} (fav={GAN_WX[g] in fav}, av={GAN_WX[g] in av})")
        print(f"  支辰={BRANCH_WX[z]} (fav={BRANCH_WX[z] in fav}, av={BRANCH_WX[z] in av})")
        print(f"  fav集合: {sorted(fav)}")
        print(f"  av集合: {sorted(av)}")
        break

print()
print("="*80)
print("【大运喜忌层对齐优化 - 全面审计汇总】")
print("="*80)
print()
print("当前状态:")
print("  单一对齐率: 69.8% (196/281)")
print("  命中率@K: 95.7% (269/281)")
print("  未命中: 21例 (9例无互动, 12例有互动)")
print()
print("方向验证结果:")
print("  方向一(四轨并行): V1=57.7%, V2=55.3%, V3=58.2% - 全部失败")
print("  方向二(十干级): 44.0% - 失败")
print()
print("未命中案例根因分布(9例无互动):")
print("  1. 从格/专旺格用神构造不准确: 5例")
print("     - L249从财格: 从财格用官杀泄财逻辑错误")
print("     - L518从儿格: 从格识别不准确(原典用扶抑逻辑)")
print("     - L751从财格: 大运天干地支判断差异")
print("     - L1121从财格: 从格识别不准确(原典用扶抑逻辑)")
print("     - L2085炎上格: 炎上格fav错误(应木火土非金)")
print("  2. 病药轨判断不准确: 3例")
print("     - L269: 大运天干地支判断差异")
print("     - L996: V5.1修正版误伤(身弱印比修正)")
print("     - L1807: 病药轨未考虑比劫夺财")
print("  3. 调候轨判断不准确: 1例")
print("     - L1015: 待分析")
print()
print("核心结论:")
print("  1. 69.8%可能是当前架构在原著案例上的上限")
print("  2. 互动级判断不能靠单一布尔条件(七轮试错全部回退)")
print("  3. 从格/专旺格识别和用神构造需要系统性重构")
print("  4. 病药轨需要考虑比劫夺财等特殊情况")
print("  5. 大运天干地支判断差异(分前五后五)是重要因素")
print("  6. V5.1身弱印比修正存在误伤")
